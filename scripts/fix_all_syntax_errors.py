#!/usr/bin/env python3
"""Fix all syntax errors in Python files, focusing on docstring issues."""

import ast
import os
import re
from pathlib import Path
from typing import List, Tuple


def fix_docstring_syntax(content: str) -> str:
    """Fix various docstring syntax issues."""
    lines = content.split("\n")
    fixed_lines = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # Fix standalone periods after docstrings
        if i > 0 and line.strip() == "." and i < len(lines) - 1:
            prev_line = lines[i - 1].strip()
            next_line = lines[i + 1].strip() if i + 1 < len(lines) else ""

            # Check if previous line ends with quotes and next line doesn't start with quotes
            if (
                prev_line.endswith('"""') or prev_line.endswith("'''")
            ) and not next_line.startswith(('"""', "'''")):
                # Skip this line (remove the standalone period)
                i += 1
                continue

        # Fix "def" or "class" statements with periods
        if re.match(r"^(\s*)(def|class)\s+\w+.*:\s*\.$", line):
            line = line.rstrip(".")

        # Fix docstrings that have been split incorrectly
        if '"""' in line or "'''" in line:
            # Check if this is a malformed docstring
            if line.strip().endswith(('."""', ".'''")) and not line.strip().startswith(
                ('"""', "'''")
            ):
                # This might be the end of a docstring that was split
                line = line.replace('."""', '"""').replace(".'''", "'''")

        fixed_lines.append(line)
        i += 1

    return "\n".join(fixed_lines)


def fix_multiline_docstrings(content: str) -> str:
    """Fix multiline docstrings that have been incorrectly formatted."""
    # Pattern to find docstrings with standalone periods
    pattern = r'("""[^"]*?"""\s*\n\s*\.(?:\s*\n|$))'

    def replace_func(match):
        # Remove the standalone period line
        return match.group(1).rstrip() + "\n"

    content = re.sub(pattern, replace_func, content, flags=re.MULTILINE | re.DOTALL)

    # Also handle single quotes
    pattern = r"('''[^']*?'''\s*\n\s*\.(?:\s*\n|$))"
    content = re.sub(pattern, replace_func, content, flags=re.MULTILINE | re.DOTALL)

    return content


def fix_class_and_function_definitions(content: str) -> str:
    """Fix class and function definitions with syntax errors."""
    lines = content.split("\n")
    fixed_lines = []

    for i, line in enumerate(lines):
        # Fix class definitions with periods
        if re.match(r"^\s*class\s+\w+.*:\s*\.$", line):
            line = line.rstrip(".")

        # Fix function definitions with periods
        if re.match(r"^\s*def\s+\w+.*:\s*\.$", line):
            line = line.rstrip(".")

        # Fix docstrings that start with a period on the next line
        if line.strip().startswith(('"""', "'''")):
            # Check if next line is just a period
            if i + 1 < len(lines) and lines[i + 1].strip() == ".":
                # Skip the period line
                continue

        fixed_lines.append(line)

    return "\n".join(fixed_lines)


def validate_python_syntax(filepath: Path) -> List[str]:
    """Validate Python syntax and return list of errors."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        ast.parse(content)
        return []
    except SyntaxError as e:
        return [f"Line {e.lineno}: {e.msg}"]
    except Exception as e:
        return [str(e)]


def fix_file(filepath: Path) -> Tuple[bool, List[str]]:
    """Fix syntax errors in a single file."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        original_content = content

        # Apply fixes
        content = fix_docstring_syntax(content)
        content = fix_multiline_docstrings(content)
        content = fix_class_and_function_definitions(content)

        # Additional specific fixes for known patterns
        # Fix "name: str." pattern
        content = re.sub(r"(\w+:\s*\w+)\.\s*$", r"\1", content, flags=re.MULTILINE)

        # Fix "def function()." pattern
        content = re.sub(
            r"(def\s+\w+\([^)]*\)):\s*\.\s*$", r"\1:", content, flags=re.MULTILINE
        )

        # Fix "class ClassName." pattern
        content = re.sub(
            r"(class\s+\w+[^:]*?):\s*\.\s*$", r"\1:", content, flags=re.MULTILINE
        )

        # Remove standalone periods after docstrings
        content = re.sub(r'("""\s*\n)\s*\.\s*\n', r"\1", content, flags=re.MULTILINE)
        content = re.sub(r"('''\s*\n)\s*\.\s*\n", r"\1", content, flags=re.MULTILINE)

        if content != original_content:
            # Validate the fixed content
            try:
                ast.parse(content)
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(content)
                return True, []
            except SyntaxError as e:
                return False, [f"Failed to fix: Line {e.lineno}: {e.msg}"]

        return False, []

    except Exception as e:
        return False, [f"Error processing file: {str(e)}"]


def main():
    """Main function to fix all Python files."""
    # Priority files that were mentioned in the error output
    priority_files = [
        "backend/agents/core/agent_router.py",
        "backend/agents/docker_agent.py",
        "backend/agents/pulumi_agent.py",
        "backend/core/context_manager.py",
        "backend/integrations/pulumi_mcp_client.py",
        "backend/integrations/portkey_client.py",
    ]

    # Fix priority files first
    print("Fixing priority files...")
    for filepath in priority_files:
        path = Path(filepath)
        if path.exists():
            print(f"Checking {filepath}...")
            errors = validate_python_syntax(path)
            if errors:
                print(f"  Found errors: {errors}")
                fixed, fix_errors = fix_file(path)
                if fixed:
                    print("  ✓ Fixed successfully")
                else:
                    print(f"  ✗ Failed to fix: {fix_errors}")

    # Then fix all Python files
    print("\nFixing all Python files...")
    python_files = []
    for root, dirs, files in os.walk("."):
        # Skip virtual environments and other non-source directories
        dirs[:] = [
            d
            for d in dirs
            if d not in {".git", "__pycache__", "venv", ".venv", "node_modules"}
        ]

        for file in files:
            if file.endswith(".py"):
                python_files.append(Path(root) / file)

    fixed_count = 0
    error_count = 0

    for filepath in python_files:
        errors = validate_python_syntax(filepath)
        if errors:
            print(f"Found syntax errors in {filepath}: {errors}")
            fixed, fix_errors = fix_file(filepath)
            if fixed:
                print(f"  ✓ Fixed {filepath}")
                fixed_count += 1
            else:
                print(f"  ✗ Failed to fix {filepath}: {fix_errors}")
                error_count += 1

    print("\nSummary:")
    print(f"  Files fixed: {fixed_count}")
    print(f"  Files with unfixed errors: {error_count}")

    # Validate all priority files again
    print("\nValidating priority files...")
    all_valid = True
    for filepath in priority_files:
        path = Path(filepath)
        if path.exists():
            errors = validate_python_syntax(path)
            if errors:
                print(f"  ✗ {filepath} still has errors: {errors}")
                all_valid = False
            else:
                print(f"  ✓ {filepath} is valid")

    return 0 if all_valid else 1


if __name__ == "__main__":
    exit(main())
