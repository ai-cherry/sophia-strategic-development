#!/usr/bin/env python3
"""
Type Safety Audit Script for Sophia AI

This script analyzes the codebase for type annotations and generates a report
on type coverage and missing annotations.
"""

import ast
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


class TypeAnnotationAnalyzer(ast.NodeVisitor):
    """AST visitor to analyze type annotations in Python code."""

    def __init__(self):
        self.functions: list[dict[str, Any]] = []
        self.classes: list[dict[str, Any]] = []
        self.current_class: str | None = None

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Analyze function definitions for type annotations."""
        func_info = {
            "name": node.name,
            "line": node.lineno,
            "class": self.current_class,
            "has_return_type": node.returns is not None,
            "parameters": [],
            "missing_annotations": [],
        }

        # Check parameters
        for arg in node.args.args:
            param_info = {"name": arg.arg, "has_type": arg.annotation is not None}
            func_info["parameters"].append(param_info)
            if not arg.annotation and arg.arg != "self":
                func_info["missing_annotations"].append(f"parameter '{arg.arg}'")

        # Check return type
        if not node.returns and not node.name.startswith("__"):
            func_info["missing_annotations"].append("return type")

        self.functions.append(func_info)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Analyze async function definitions for type annotations."""
        # Treat async functions the same as regular functions
        self.visit_FunctionDef(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Track class definitions."""
        self.current_class = node.name
        self.classes.append({"name": node.name, "line": node.lineno})
        self.generic_visit(node)
        self.current_class = None


def analyze_file(file_path: Path) -> dict[str, Any]:
    """Analyze a single Python file for type annotations."""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        tree = ast.parse(content)
        analyzer = TypeAnnotationAnalyzer()
        analyzer.visit(tree)

        return _calculate_file_stats(file_path, analyzer)

    except Exception as e:
        logger.exception(f"Error analyzing {file_path}: {e}")
        return {"file": str(file_path), "error": str(e)}


def _calculate_file_stats(
    file_path: Path, analyzer: TypeAnnotationAnalyzer
) -> dict[str, Any]:
    """Calculates type coverage statistics for a file."""
    total_functions = len(analyzer.functions)
    functions_with_complete_types = sum(
        1
        for f in analyzer.functions
        if f["has_return_type"]
        and all(p["has_type"] or p["name"] == "self" for p in f["parameters"])
    )

    return {
        "file": str(file_path),
        "total_functions": total_functions,
        "functions_with_complete_types": functions_with_complete_types,
        "type_coverage": (
            (functions_with_complete_types / total_functions * 100)
            if total_functions > 0
            else 100
        ),
        "functions": analyzer.functions,
        "classes": analyzer.classes,
        "missing_annotations": [
            f for f in analyzer.functions if f["missing_annotations"]
        ],
    }


def generate_mypy_config() -> None:
    """Generate mypy configuration file."""
    mypy_config = """[mypy]
python_version = 3.11
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
disallow_incomplete_defs = True
check_untyped_defs = True
disallow_untyped_decorators = True
no_implicit_optional = True
warn_redundant_casts = True
warn_unused_ignores = True
warn_no_return = True
warn_unreachable = True
strict_equality = True

# Per-module options:
[mypy-tests.*]
ignore_errors = True

[mypy-pinecone.*]
ignore_missing_imports = True

[mypy-asyncpg.*]
ignore_missing_imports = True

[mypy-pandas.*]
ignore_missing_imports = True
"""

    with open("mypy.ini", "w") as f:
        f.write(mypy_config)
    logger.info("Generated mypy.ini configuration file")


def scan_codebase(
    root_dir: Path, exclude_dirs: list[str] | None = None
) -> dict[str, Any]:
    """Scan the entire codebase for type annotation coverage."""
    if exclude_dirs is None:
        exclude_dirs = [".venv", "venv", "__pycache__", ".git", "node_modules"]

    results = []
    total_functions = 0
    total_with_types = 0

    for py_file in root_dir.rglob("*.py"):
        # Skip excluded directories
        if any(excluded in py_file.parts for excluded in exclude_dirs):
            continue

        file_analysis = analyze_file(py_file)
        if "error" not in file_analysis:
            results.append(file_analysis)
            total_functions += file_analysis["total_functions"]
            total_with_types += file_analysis["functions_with_complete_types"]

    return {
        "timestamp": datetime.now().isoformat(),
        "total_files": len(results),
        "total_functions": total_functions,
        "functions_with_complete_types": total_with_types,
        "overall_type_coverage": (
            (total_with_types / total_functions * 100) if total_functions > 0 else 100
        ),
        "files": results,
    }


def generate_type_stub_template(file_analysis: dict[str, Any]) -> str:
    """Generate type stub template for functions missing annotations."""
    stub_content = f'"""Type stubs for {file_analysis["file"]}"""\n\n'
    stub_content += "from typing import Any, Dict, List, Optional, Union\n\n"

    for func in file_analysis.get("missing_annotations", []):
        if func["class"]:
            stub_content += f"\nclass {func['class']}:\n"
            stub_content += f"    def {func['name']}("
        else:
            stub_content += f"\ndef {func['name']}("

        # Add parameters
        params = []
        for param in func["parameters"]:
            if param["name"] == "self":
                params.append("self")
            else:
                params.append(f"{param['name']}: Any")

        stub_content += ", ".join(params)
        stub_content += ") -> Any:\n"
        stub_content += "    ...\n"

    return stub_content


def main():
    """Main function to run type safety audit."""
    logger.info("Starting Type Safety Audit for Sophia AI...")

    # Generate mypy config
    generate_mypy_config()

    # Scan codebase
    project_root = Path.cwd()
    analysis = scan_codebase(project_root)

    # Save detailed report
    report_path = "type_safety_audit_report.json"
    with open(report_path, "w") as f:
        json.dump(analysis, f, indent=2)

    # Print summary
    logger.info(f"\n{'=' * 60}")
    logger.info("Type Safety Audit Summary")
    logger.info(f"{'=' * 60}")
    logger.info(f"Total files analyzed: {analysis['total_files']}")
    logger.info(f"Total functions: {analysis['total_functions']}")
    logger.info(
        f"Functions with complete types: {analysis['functions_with_complete_types']}"
    )
    logger.info(f"Overall type coverage: {analysis['overall_type_coverage']:.2f}%")
    logger.info(f"\nDetailed report saved to: {report_path}")

    # Generate priority fix list
    priority_files = []
    for file_data in analysis["files"]:
        if file_data.get("type_coverage", 100) < 50:
            priority_files.append(
                {
                    "file": file_data["file"],
                    "coverage": file_data["type_coverage"],
                    "missing_count": len(file_data.get("missing_annotations", [])),
                }
            )

    if priority_files:
        logger.info(f"\n{'=' * 60}")
        logger.info("Priority Files for Type Annotation (< 50% coverage):")
        logger.info(f"{'=' * 60}")
        for pf in sorted(priority_files, key=lambda x: x["coverage"]):
            logger.info(
                f"{pf['file']}: {pf['coverage']:.1f}% coverage, "
                f"{pf['missing_count']} functions need annotations"
            )


if __name__ == "__main__":
    main()
