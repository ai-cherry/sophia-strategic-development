#!/usr/bin/env python3
"""Check for import issues in the codebase."""

import ast
import sys
from pathlib import Path


def check_python_file(filepath):
    """Check a Python file for import issues."""
    issues = []

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        # Parse the AST
        tree = ast.parse(content, filename=str(filepath))

        # Check imports
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module_name = alias.name
                    # Check if it's a relative import that might be problematic
                    if ".." in module_name:
                        issues.append(
                            f"Line {node.lineno}: Relative import with '..' - {module_name}"
                        )

            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                level = node.level

                # Check for problematic relative imports
                if level > 1:  # More than one dot
                    issues.append(
                        f"Line {node.lineno}: Deep relative import (level {level}) - from {'.' * level}{module}"
                    )

                # Check for circular import patterns
                if "backend" in str(filepath) and module:
                    # Check if importing from parent directories incorrectly
                    if module.startswith("..") and "backend" in module:
                        issues.append(
                            f"Line {node.lineno}: Potentially incorrect relative import - from {module}"
                        )

    except SyntaxError as e:
        issues.append(f"Syntax error: {e}")
    except Exception as e:
        issues.append(f"Error parsing file: {e}")

    return issues


def main():
    """Main function to check all Python files."""
    print("Checking Python files for import issues...\n")

    # Get all Python files in backend directory
    backend_dir = Path("backend")
    python_files = list(backend_dir.rglob("*.py"))

    total_issues = 0
    files_with_issues = []

    for py_file in python_files:
        issues = check_python_file(py_file)
        if issues:
            files_with_issues.append((py_file, issues))
            total_issues += len(issues)

    # Report results
    if files_with_issues:
        print(
            f"Found {total_issues} import issues in {len(files_with_issues)} files:\n"
        )

        for filepath, issues in files_with_issues:
            print(f"\n{filepath}:")
            for issue in issues:
                print(f"  - {issue}")
    else:
        print("No import issues found!")

    # Also check for specific known problematic imports
    print("\n\nChecking for specific known issues...")

    # Check comprehensive_memory_manager.py
    cmm_path = Path("backend/core/comprehensive_memory_manager.py")
    if cmm_path.exists():
        with open(cmm_path, "r") as f:
            content = f.read()
            if "from ..agents.core.persistent_memory" in content:
                print(f"WARNING: {cmm_path} has incorrect relative import")
            else:
                print(f"✓ {cmm_path} imports look correct")

    # Check persistent_memory.py
    pm_path = Path("backend/agents/core/persistent_memory.py")
    if pm_path.exists():
        with open(pm_path, "r") as f:
            content = f.read()
            if "from ...core.secret_manager" in content:
                print(f"WARNING: {pm_path} has incorrect relative import")
            else:
                print(f"✓ {pm_path} imports look correct")

    return 0 if not files_with_issues else 1


if __name__ == "__main__":
    sys.exit(main())
