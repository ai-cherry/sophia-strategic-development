#!/usr/bin/env python3
"""
Script to automatically add type annotations to Python files.
"""

import ast
import json
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


class TypeAnnotationAdder(ast.NodeTransformer):
    """AST transformer to add type annotations to functions."""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.changes_made = 0

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
        """Add type annotations to function definitions."""
        self.generic_visit(node)

        # Add return type annotation if missing
        if not node.returns and not node.name.startswith("__"):
            # Infer return type based on function name and content
            return_type = self._infer_return_type(node)
            if return_type:
                node.returns = ast.Name(id=return_type, ctx=ast.Load())
                self.changes_made += 1

        # Add parameter type annotations if missing
        for arg in node.args.args:
            if not arg.annotation and arg.arg != "self" and arg.arg != "cls":
                # Infer parameter type based on name and usage
                param_type = self._infer_param_type(arg.arg, node)
                if param_type:
                    arg.annotation = ast.Name(id=param_type, ctx=ast.Load())
                    self.changes_made += 1

        return node

    def visit_AsyncFunctionDef(
        self, node: ast.AsyncFunctionDef
    ) -> ast.AsyncFunctionDef:
        """Add type annotations to async function definitions."""
        # Treat async functions the same as regular functions
        return self.visit_FunctionDef(node)

    def _infer_return_type(self, node: ast.FunctionDef) -> str | None:
        """Infer return type based on function name and body."""
        # Test functions typically return None
        if node.name.startswith("test_"):
            return "None"

        # Main functions typically return None
        if node.name == "main":
            return "None"

        # Check for explicit return statements
        for stmt in ast.walk(node):
            if isinstance(stmt, ast.Return):
                if stmt.value is None:
                    return "None"
                elif isinstance(stmt.value, ast.Constant):
                    if isinstance(stmt.value.value, bool):
                        return "bool"
                    elif isinstance(stmt.value.value, int):
                        return "int"
                    elif isinstance(stmt.value.value, str):
                        return "str"
                    elif isinstance(stmt.value.value, float):
                        return "float"
                elif isinstance(stmt.value, ast.Dict):
                    return "Dict[str, Any]"
                elif isinstance(stmt.value, ast.List):
                    return "List[Any]"
                elif isinstance(stmt.value, ast.Tuple):
                    return "Tuple[Any, ...]"

        # Default to Any for complex functions
        return "Any"

    def _infer_param_type(self, param_name: str, node: ast.FunctionDef) -> str | None:
        """Infer parameter type based on name and usage."""
        # Common parameter patterns
        if param_name in ["file_path", "path", "directory", "folder"]:
            return "Path"
        elif param_name in ["content", "text", "message", "query"]:
            return "str"
        elif param_name in ["limit", "count", "index", "port"]:
            return "int"
        elif param_name in ["verbose", "recursive", "enabled"]:
            return "bool"
        elif param_name in ["config", "data", "params", "kwargs"]:
            return "Dict[str, Any]"
        elif param_name in ["items", "values", "results"]:
            return "List[Any]"
        elif param_name.endswith("_id"):
            return "str"
        elif param_name.endswith("_name"):
            return "str"
        elif param_name in ["exclude_dirs", "tags"]:
            return "Optional[List[str]]"

        # FastAPI specific
        if "file" in param_name.lower() and "UploadFile" in str(node):
            return "UploadFile"

        # Default to Any for unknown parameters
        return "Any"


def add_imports_if_needed(content: str) -> str:
    """Add necessary imports for type annotations if not present."""
    lines = content.split("\n")

    # Check if typing imports are needed
    needs_typing = False
    needs_pathlib = False

    if (
        "Dict[" in content
        or "List[" in content
        or "Optional[" in content
        or "Any" in content
        or "Tuple[" in content
    ):
        needs_typing = True
    if "Path" in content and "from pathlib import" not in content:
        needs_pathlib = True

    # Find the right place to insert imports (after module docstring and before other imports)
    insert_index = 0
    in_docstring = False
    docstring_delimiter = None

    for i, line in enumerate(lines):
        if i == 0 and (line.startswith('"""') or line.startswith("'''")):
            in_docstring = True
            docstring_delimiter = '"""' if line.startswith('"""') else "'''"
            if line.count(docstring_delimiter) == 2:  # Single line docstring
                in_docstring = False
            insert_index = i + 1
            continue

        if in_docstring and docstring_delimiter in line:
            in_docstring = False
            insert_index = i + 1
            continue

        if not in_docstring and (
            line.startswith("import ") or line.startswith("from ")
        ):
            insert_index = i
            break
        elif not in_docstring and line.strip() and not line.startswith("#"):
            insert_index = i
            break

    # Add imports if needed
    imports_to_add = []
    if needs_typing and "from typing import" not in content:
        imports_to_add.append("from typing import Dict, List, Optional, Any, Tuple")
    if needs_pathlib and "from pathlib import" not in content:
        imports_to_add.append("from pathlib import Path")

    if imports_to_add:
        for imp in reversed(imports_to_add):
            lines.insert(insert_index, imp)
        # Add empty line after imports if needed
        if (
            insert_index < len(lines) - 1
            and lines[insert_index + len(imports_to_add)].strip()
        ):
            lines.insert(insert_index + len(imports_to_add), "")

    return "\n".join(lines)


def process_file(file_path: Path) -> bool:
    """Process a single file to add type annotations."""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        # Parse the AST
        tree = ast.parse(content)

        # Transform the AST
        transformer = TypeAnnotationAdder(str(file_path))
        new_tree = transformer.visit(tree)

        if transformer.changes_made > 0:
            # Convert AST back to code
            import astor

            new_content = astor.to_source(new_tree)

            # Add imports if needed
            new_content = add_imports_if_needed(new_content)

            # Create backup
            backup_path = file_path.with_suffix(file_path.suffix + ".backup_types")
            with open(backup_path, "w", encoding="utf-8") as f:
                f.write(content)

            # Write updated content
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_content)

            logger.info(
                f"✓ Added {transformer.changes_made} type annotations to {file_path}"
            )
            return True
        else:
            logger.info(f"✓ No changes needed for {file_path}")
            return False

    except Exception as e:
        logger.error(f"✗ Error processing {file_path}: {e}")
        return False


def main() -> None:
    """Main function to add type annotations."""
    # Load the type safety audit report
    report_path = Path("type_safety_audit_report.json")
    if not report_path.exists():
        logger.error(
            "type_safety_audit_report.json not found. Run type_safety_audit.py first."
        )
        return

    with open(report_path) as f:
        audit_data = json.load(f)

    # Process files with low type coverage
    files_to_process = []
    for file_data in audit_data["files"]:
        if file_data.get("type_coverage", 100) < 100 and "error" not in file_data:
            files_to_process.append(
                {
                    "path": Path(file_data["file"]),
                    "coverage": file_data["type_coverage"],
                    "missing_count": len(file_data.get("missing_annotations", [])),
                }
            )

    # Sort by coverage (lowest first)
    files_to_process.sort(key=lambda x: x["coverage"])

    logger.info(f"Found {len(files_to_process)} files that need type annotations")

    # Check if astor is available
    try:
        import astor
    except ImportError:
        logger.error("astor package is required for AST to code conversion")
        logger.info("Install it with: pip install astor")
        return

    # Process each file
    updated_count = 0
    for file_info in files_to_process:
        if process_file(file_info["path"]):
            updated_count += 1

    logger.info(f"\n{'=' * 60}")
    logger.info("Type annotation addition complete!")
    logger.info(f"Files updated: {updated_count}")
    logger.info(f"Files unchanged: {len(files_to_process) - updated_count}")
    logger.info("\nRun type_safety_audit.py again to see the improved coverage.")


if __name__ == "__main__":
    main()
