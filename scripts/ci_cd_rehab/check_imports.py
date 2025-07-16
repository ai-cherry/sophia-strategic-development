#!/usr/bin/env python3
"""
Import Health Check Script
Validates all Python imports are resolvable and reports issues
"""

import ast
import importlib
import importlib.util
import logging
import sys
from collections import defaultdict
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

class ImportChecker:
    """Check health of Python imports across the project"""

    def __init__(self, project_root: Path | None = None):
        self.project_root = project_root or Path.cwd()
        self.import_issues: list[dict] = []
        self.checked_files: set[Path] = set()
        self.module_cache: dict[str, bool] = {}

    def find_python_files(self) -> list[Path]:
        """Find all Python files in the project"""
        python_files = []

        for pattern in ["**/*.py"]:
            for file_path in self.project_root.rglob(pattern):
                # Skip certain directories
                skip_dirs = {
                    "__pycache__",
                    ".git",
                    "venv",
                    ".venv",
                    ".env",
                    "node_modules",
                    "build",
                    "dist",
                    ".techdebt",
                    ".pytest_cache",
                    ".mypy_cache",
                    "htmlcov",
                }

                if any(skip in str(file_path) for skip in skip_dirs):
                    continue

                python_files.append(file_path)

        return sorted(python_files)

    def extract_imports(self, file_path: Path) -> list[tuple[str, int, str]]:
        """Extract all imports from a Python file"""
        imports = []

        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content, filename=str(file_path))

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(
                            (alias.name, node.lineno, f"import {alias.name}")
                        )

                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    level = node.level  # Number of dots (relative import)

                    if level > 0:
                        # Relative import
                        base_module = self.resolve_relative_import(
                            file_path, module, level
                        )
                        if base_module:
                            module = base_module

                    for alias in node.names:
                        if alias.name == "*":
                            import_str = f"from {module} import *"
                        else:
                            import_str = f"from {module} import {alias.name}"

                        imports.append((module, node.lineno, import_str))

        except SyntaxError as e:
            logger.warning(f"Syntax error in {file_path}: {e}")
        except Exception as e:
            logger.warning(f"Error parsing {file_path}: {e}")

        return imports

    def resolve_relative_import(
        self, file_path: Path, module: str, level: int
    ) -> str | None:
        """Resolve relative import to absolute module path"""
        try:
            # Get the package hierarchy
            parts = file_path.relative_to(self.project_root).parts[:-1]

            # Go up 'level' directories
            if level > len(parts):
                return None

            base_parts = parts[:-level] if level > 0 else parts

            # Combine with module
            if module:
                full_parts = list(base_parts) + module.split(".")
            else:
                full_parts = list(base_parts)

            return ".".join(full_parts)

        except Exception:
            return None

    def can_import_module(self, module_name: str) -> bool:
        """Check if a module can be imported"""
        # Check cache first
        if module_name in self.module_cache:
            return self.module_cache[module_name]

        # Special handling for known problematic modules
        if module_name.startswith("anthropic_mcp_python_sdk"):
            self.module_cache[module_name] = False
            return False

        # Try to find the module spec
        try:
            spec = importlib.util.find_spec(module_name)
            result = spec is not None
        except (ImportError, ModuleNotFoundError, ValueError):
            result = False
        except Exception:
            # Some modules cause other exceptions
            result = False

        self.module_cache[module_name] = result
        return result

    def check_file_imports(self, file_path: Path) -> list[dict]:
        """Check all imports in a single file"""
        issues = []
        imports = self.extract_imports(file_path)

        for module_name, line_no, import_stmt in imports:
            if not module_name:
                continue

            # Check if module can be imported
            if not self.can_import_module(module_name):
                # Check if it's a local module
                local_module_path = (
                    self.project_root / module_name.replace(".", "/") / "__init__.py"
                )
                local_file_path = self.project_root / (
                    module_name.replace(".", "/") + ".py"
                )

                if not (local_module_path.exists() or local_file_path.exists()):
                    issues.append(
                        {
                            "file": str(file_path.relative_to(self.project_root)),
                            "line": line_no,
                            "module": module_name,
                            "import_statement": import_stmt,
                            "issue_type": "module_not_found",
                        }
                    )

        return issues

    def check_all_imports(self) -> list[dict]:
        """Check imports across all Python files"""
        python_files = self.find_python_files()
        logger.info(f"Checking imports in {len(python_files)} Python files...")

        for file_path in python_files:
            self.checked_files.add(file_path)
            file_issues = self.check_file_imports(file_path)
            self.import_issues.extend(file_issues)

        return self.import_issues

    def analyze_issues(self) -> dict:
        """Analyze import issues and generate summary"""
        # Group issues by type
        issues_by_type = defaultdict(list)
        for issue in self.import_issues:
            issues_by_type[issue["issue_type"]].append(issue)

        # Group issues by module
        issues_by_module = defaultdict(list)
        for issue in self.import_issues:
            issues_by_module[issue["module"]].append(issue)

        # Find most problematic files
        issues_by_file = defaultdict(list)
        for issue in self.import_issues:
            issues_by_file[issue["file"]].append(issue)

        problematic_files = sorted(
            issues_by_file.items(), key=lambda x: len(x[1]), reverse=True
        )[:10]

        # Find most common missing modules
        module_counts = defaultdict(int)
        for issue in self.import_issues:
            module_counts[issue["module"]] += 1

        common_missing = sorted(
            module_counts.items(), key=lambda x: x[1], reverse=True
        )[:10]

        return {
            "total_files_checked": len(self.checked_files),
            "total_issues": len(self.import_issues),
            "issues_by_type": dict(issues_by_type),
            "most_problematic_files": problematic_files,
            "most_common_missing_modules": common_missing,
            "unique_missing_modules": len(issues_by_module),
        }

    def generate_report(self) -> str:
        """Generate human-readable report"""
        analysis = self.analyze_issues()

        report = []
        report.append("=" * 60)
        report.append("IMPORT HEALTH CHECK REPORT")
        report.append("=" * 60)
        report.append(f"\nFiles checked: {analysis['total_files_checked']}")
        report.append(f"Total issues found: {analysis['total_issues']}")

        if analysis["total_issues"] == 0:
            report.append("\n✅ All imports are healthy!")
            return "\n".join(report)

        # Most common missing modules
        report.append("\n## Most Common Missing Modules:")
        for module, count in analysis["most_common_missing_modules"]:
            report.append(f"  - {module}: {count} occurrences")

        # Most problematic files
        report.append("\n## Most Problematic Files:")
        for file, issues in analysis["most_problematic_files"]:
            report.append(f"  - {file}: {len(issues)} issues")

        # Detailed issues
        report.append("\n## Detailed Issues:")
        for i, issue in enumerate(self.import_issues[:20], 1):
            report.append(f"\n{i}. {issue['file']}:{issue['line']}")
            report.append(f"   {issue['import_statement']}")
            report.append(f"   Issue: {issue['issue_type']}")

        if len(self.import_issues) > 20:
            report.append(f"\n... and {len(self.import_issues) - 20} more issues")

        # Recommendations
        report.append("\n## Recommendations:")

        if any(
            "anthropic_mcp_python_sdk" in issue["module"]
            for issue in self.import_issues
        ):
            report.append(
                "- Replace anthropic_mcp_python_sdk imports with backend.mcp.shim"
            )

        if analysis["unique_missing_modules"] > 10:
            report.append("- Review and consolidate dependencies in requirements.txt")

        report.append(
            "- Run 'pip install -r requirements.txt' to install missing packages"
        )
        report.append("- Check for typos in import statements")

        return "\n".join(report)

    def write_github_annotations(self):
        """Write GitHub Actions annotations for issues"""
        for issue in self.import_issues:
            print(
                f"::error file={issue['file']},line={issue['line']}::"
                f"Import error: {issue['import_statement']} - {issue['issue_type']}"
            )

def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Check health of Python imports")
    parser.add_argument(
        "--root", type=Path, default=Path.cwd(), help="Project root directory"
    )
    parser.add_argument(
        "--github-annotations",
        action="store_true",
        help="Output GitHub Actions annotations",
    )
    parser.add_argument("--json", action="store_true", help="Output JSON report")
    parser.add_argument(
        "--fail-on-issues",
        action="store_true",
        help="Exit with error code if issues found",
    )

    args = parser.parse_args()

    # Create checker
    checker = ImportChecker(project_root=args.root)

    # Run checks
    issues = checker.check_all_imports()

    # Output results
    if args.json:
        import json

        analysis = checker.analyze_issues()
        print(json.dumps(analysis, indent=2))
    elif args.github_annotations and issues:
        checker.write_github_annotations()
    else:
        report = checker.generate_report()
        print(report)

    # Exit code
    if args.fail_on_issues and issues:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
