#!/usr/bin/env python3
"""
Codemod to replace direct LLM client usage with unified LLM Router
Handles OpenAI, Portkey, OpenRouter, and other direct SDK calls
"""

import argparse
import ast
from pathlib import Path


class LLMClientRewriter(ast.NodeTransformer):
    """AST transformer to replace LLM client calls with router calls"""

    def __init__(self):
        self.imports_to_add = set()
        self.imports_to_remove = set()
        self.modified = False

    def visit_Import(self, node):
        """Handle import statements"""
        new_names = []
        for alias in node.names:
            if alias.name in ["openai", "portkey_ai", "anthropic"]:
                self.imports_to_remove.add(alias.name)
                self.imports_to_add.add("llm_router")
                self.modified = True
            else:
                new_names.append(alias)

        if new_names:
            node.names = new_names
            return node
        return None

    def visit_ImportFrom(self, node):
        """Handle from imports"""
        if node.module in ["openai", "portkey_ai", "anthropic"]:
            self.imports_to_remove.add(node.module)
            self.imports_to_add.add("llm_router")
            self.modified = True
            return None

        # Replace unified_llm_service imports
        if node.module == "infrastructure.services.unified_llm_service":
            self.modified = True
            return ast.ImportFrom(
                module="infrastructure.services.llm_router",
                names=[ast.alias(name="llm_router", asname=None)],
                level=0,
            )

        return node

    def visit_Call(self, node):
        """Replace LLM client calls"""
        self.generic_visit(node)

        # OpenAI completion calls
        if self._is_openai_completion(node):
            self.modified = True
            return self._create_router_call(node)

        # Portkey completion calls
        if self._is_portkey_completion(node):
            self.modified = True
            return self._create_router_call(node)

        return node

    def _is_openai_completion(self, node):
        """Check if node is an OpenAI completion call"""
        if isinstance(node.func, ast.Attribute):
            # openai.ChatCompletion.create or client.chat.completions.create
            if (
                node.func.attr == "create"
                and isinstance(node.func.value, ast.Attribute)
                and node.func.value.attr in ["completions", "ChatCompletion"]
            ):
                return True
        return False

    def _is_portkey_completion(self, node):
        """Check if node is a Portkey completion call"""
        if isinstance(node.func, ast.Attribute):
            if (
                node.func.attr == "create"
                and isinstance(node.func.value, ast.Attribute)
                and "portkey" in ast.unparse(node.func.value).lower()
            ):
                return True
        return False

    def _create_router_call(self, node):
        """Create llm_router.complete call"""
        # Extract arguments
        prompt = None
        kwargs = {}

        for keyword in node.keywords:
            if keyword.arg == "messages":
                # Extract prompt from messages
                if isinstance(keyword.value, ast.List) and keyword.value.elts:
                    last_msg = keyword.value.elts[-1]
                    if isinstance(last_msg, ast.Dict):
                        for i, key in enumerate(last_msg.keys):
                            if isinstance(key, ast.Constant) and key.value == "content":
                                prompt = last_msg.values[i]
            elif keyword.arg == "prompt":
                prompt = keyword.value
            else:
                kwargs[keyword.arg] = keyword.value

        if not prompt:
            # Default prompt if not found
            prompt = ast.Constant(value="")

        # Create router call
        router_call = ast.Call(
            func=ast.Attribute(
                value=ast.Name(id="llm_router", ctx=ast.Load()),
                attr="complete",
                ctx=ast.Load(),
            ),
            args=[],
            keywords=[
                ast.keyword(arg="prompt", value=prompt),
                ast.keyword(
                    arg="task",
                    value=ast.Attribute(
                        value=ast.Name(id="TaskType", ctx=ast.Load()),
                        attr="CODE_GENERATION",
                        ctx=ast.Load(),
                    ),
                ),
                *[ast.keyword(arg=k, value=v) for k, v in kwargs.items()],
            ],
        )

        # Wrap in await if needed
        if isinstance(node.func.value, ast.Await):
            return ast.Await(value=router_call)

        return router_call


def process_file(file_path: Path, dry_run: bool = True) -> tuple[bool, str]:
    """Process a single Python file"""
    try:
        content = file_path.read_text()
        tree = ast.parse(content, filename=str(file_path))

        # Apply transformations
        rewriter = LLMClientRewriter()
        new_tree = rewriter.visit(tree)

        if not rewriter.modified:
            return False, "No changes needed"

        # Add necessary imports
        if rewriter.imports_to_add:
            import_nodes = []
            if "llm_router" in rewriter.imports_to_add:
                import_nodes.append(
                    ast.ImportFrom(
                        module="infrastructure.services.llm_router",
                        names=[
                            ast.alias(name="llm_router", asname=None),
                            ast.alias(name="TaskType", asname=None),
                            ast.alias(name="TaskComplexity", asname=None),
                        ],
                        level=0,
                    )
                )

            # Insert imports after module docstring and other imports
            insert_pos = 0
            for i, node in enumerate(new_tree.body):
                if not isinstance(node, (ast.Expr, ast.Import, ast.ImportFrom)):
                    insert_pos = i
                    break

            for import_node in reversed(import_nodes):
                new_tree.body.insert(insert_pos, import_node)

        # Generate new code
        new_content = ast.unparse(new_tree)

        if not dry_run:
            file_path.write_text(new_content)
            return True, "File updated"
        else:
            return True, f"Would update file:\n{new_content[:200]}..."

    except Exception as e:
        return False, f"Error: {e}"


def find_python_files(root_path: Path, pattern: str = "**/*.py") -> list[Path]:
    """Find Python files matching pattern"""
    files = []
    for file_path in root_path.glob(pattern):
        # Skip test files and migrations
        if any(
            part in file_path.parts
            for part in ["test", "tests", "migrations", "__pycache__"]
        ):
            continue
        files.append(file_path)
    return files


def main():
    parser = argparse.ArgumentParser(description="Replace LLM client calls with router")
    parser.add_argument(
        "--glob", default="**/*.py", help="Glob pattern for files to process"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Show what would be changed without modifying files",
    )
    parser.add_argument(
        "--write", action="store_true", help="Actually modify files (disables dry-run)"
    )

    args = parser.parse_args()

    if args.write:
        args.dry_run = False

    # Find files
    root = Path.cwd()
    files = find_python_files(root, args.glob)

    print(f"Found {len(files)} Python files to process")

    # Process files
    modified_count = 0
    for file_path in files:
        modified, message = process_file(file_path, args.dry_run)
        if modified:
            modified_count += 1
            print(f"✓ {file_path}: {message}")

    print(
        f"\nSummary: {modified_count} files {'would be' if args.dry_run else 'were'} modified"
    )

    if args.dry_run:
        print("\nRun with --write to apply changes")


if __name__ == "__main__":
    main()
