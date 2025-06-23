#!/usr/bin/env python3
"""
Script to validate current syntax status of Python files in the codebase.
"""

import ast
import json
from pathlib import Path
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def check_python_syntax(file_path):
    """Check if a Python file has valid syntax."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        ast.parse(content)
        return True, None
    except SyntaxError as e:
        return False, f"SyntaxError: {e.msg} at line {e.lineno}"
    except Exception as e:
        return False, f"Error: {str(e)}"


def scan_directory(directory, exclude_dirs=None):
    """Scan directory for Python files and check their syntax."""
    if exclude_dirs is None:
        exclude_dirs = {
            ".venv",
            "venv",
            "__pycache__",
            ".git",
            "node_modules",
            ".pytest_cache",
        }

    valid_files = []
    error_files = {}

    for py_file in Path(directory).rglob("*.py"):
        # Skip excluded directories
        if any(excluded in py_file.parts for excluded in exclude_dirs):
            continue

        relative_path = py_file.relative_to(directory)
        is_valid, error_msg = check_python_syntax(py_file)

        if is_valid:
            valid_files.append(str(relative_path))
        else:
            error_files[str(relative_path)] = error_msg

    return valid_files, error_files


def main():
    """Main function to validate syntax."""
    logger.info("Starting syntax validation...")

    # Scan the entire project
    project_root = Path.cwd()
    valid_files, error_files = scan_directory(project_root)

    # Calculate statistics
    total_files = len(valid_files) + len(error_files)
    success_rate = (len(valid_files) / total_files * 100) if total_files > 0 else 0

    # Create report
    report = {
        "timestamp": datetime.now().isoformat(),
        "total_files": total_files,
        "valid_files": len(valid_files),
        "error_count": len(error_files),
        "success_rate": f"{success_rate:.2f}%",
        "errors": error_files,
    }

    # Save report
    report_path = "current_syntax_validation_report.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    # Print summary
    logger.info(f"\n{'='*50}")
    logger.info("Syntax Validation Summary")
    logger.info(f"{'='*50}")
    logger.info(f"Total Python files: {total_files}")
    logger.info(f"Valid files: {len(valid_files)}")
    logger.info(f"Files with errors: {len(error_files)}")
    logger.info(f"Success rate: {success_rate:.2f}%")
    logger.info(f"\nReport saved to: {report_path}")

    # Print files with errors
    if error_files:
        logger.info(f"\n{'='*50}")
        logger.info("Files with syntax errors:")
        logger.info(f"{'='*50}")
        for file_path, error_msg in sorted(error_files.items()):
            logger.error(f"\n{file_path}:")
            logger.error(f"  {error_msg}")
    else:
        logger.info("\n✅ No syntax errors found!")


if __name__ == "__main__":
    main()
