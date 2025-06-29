#!/usr/bin/env python3
"""
Comprehensive Syntax Scanner for Sophia AI Platform
Validates Python, SQL, JSON, YAML, and configuration files
"""

import ast
import json
import logging
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml


class ComprehensiveSyntaxScanner:
    """Comprehensive syntax validation for all file types"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.results = {
            "scan_timestamp": datetime.now().isoformat(),
            "python_files": {"total": 0, "valid": 0, "errors": []},
            "sql_files": {"total": 0, "valid": 0, "errors": []},
            "json_files": {"total": 0, "valid": 0, "errors": []},
            "yaml_files": {"total": 0, "valid": 0, "errors": []},
            "config_files": {"total": 0, "valid": 0, "errors": []},
            "summary": {},
        }

        # Configure logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def scan_python_files(self) -> dict[str, Any]:
        """Scan all Python files for syntax errors"""
        self.logger.info("🐍 Scanning Python files...")

        python_files = list(self.project_root.rglob("*.py"))
        self.results["python_files"]["total"] = len(python_files)

        for py_file in python_files:
            try:
                with open(py_file, encoding="utf-8") as f:
                    content = f.read()

                # Parse with AST
                ast.parse(content, filename=str(py_file))
                self.results["python_files"]["valid"] += 1

            except SyntaxError as e:
                error_info = {
                    "file": str(py_file.relative_to(self.project_root)),
                    "line": e.lineno,
                    "column": e.offset,
                    "error": str(e),
                    "type": "SyntaxError",
                }
                self.results["python_files"]["errors"].append(error_info)
                self.logger.error(f"❌ {py_file.name}: {e}")

            except UnicodeDecodeError as e:
                error_info = {
                    "file": str(py_file.relative_to(self.project_root)),
                    "error": f"Unicode decode error: {e}",
                    "type": "UnicodeError",
                }
                self.results["python_files"]["errors"].append(error_info)

            except Exception as e:
                error_info = {
                    "file": str(py_file.relative_to(self.project_root)),
                    "error": str(e),
                    "type": "UnknownError",
                }
                self.results["python_files"]["errors"].append(error_info)

        success_rate = (
            (
                self.results["python_files"]["valid"]
                / self.results["python_files"]["total"]
                * 100
            )
            if self.results["python_files"]["total"] > 0
            else 0
        )

        self.logger.info(
            f"✅ Python files: {self.results['python_files']['valid']}/{self.results['python_files']['total']} valid ({success_rate:.1f}%)"
        )
        return self.results["python_files"]

    def scan_sql_files(self) -> dict[str, Any]:
        """Scan SQL files for basic syntax validation"""
        self.logger.info("🗄️ Scanning SQL files...")

        sql_files = list(self.project_root.rglob("*.sql"))
        self.results["sql_files"]["total"] = len(sql_files)

        for sql_file in sql_files:
            try:
                with open(sql_file, encoding="utf-8") as f:
                    content = f.read()

                # Basic SQL validation (check for common syntax issues)
                if self._validate_basic_sql_syntax(content, sql_file):
                    self.results["sql_files"]["valid"] += 1

            except Exception as e:
                error_info = {
                    "file": str(sql_file.relative_to(self.project_root)),
                    "error": str(e),
                    "type": "ReadError",
                }
                self.results["sql_files"]["errors"].append(error_info)

        success_rate = (
            (
                self.results["sql_files"]["valid"]
                / self.results["sql_files"]["total"]
                * 100
            )
            if self.results["sql_files"]["total"] > 0
            else 0
        )

        self.logger.info(
            f"✅ SQL files: {self.results['sql_files']['valid']}/{self.results['sql_files']['total']} valid ({success_rate:.1f}%)"
        )
        return self.results["sql_files"]

    def _validate_basic_sql_syntax(self, content: str, file_path: Path) -> bool:
        """Basic SQL syntax validation"""
        try:
            # Check for balanced parentheses
            paren_count = content.count("(") - content.count(")")
            if paren_count != 0:
                error_info = {
                    "file": str(file_path.relative_to(self.project_root)),
                    "error": f"Unbalanced parentheses: {paren_count}",
                    "type": "SyntaxError",
                }
                self.results["sql_files"]["errors"].append(error_info)
                return False

            # Check for basic SQL keywords structure
            content_upper = content.upper()

            # Check for incomplete statements
            statements = [stmt.strip() for stmt in content.split(";") if stmt.strip()]
            for i, stmt in enumerate(statements):
                if stmt and not any(
                    keyword in stmt.upper()
                    for keyword in [
                        "SELECT",
                        "INSERT",
                        "UPDATE",
                        "DELETE",
                        "CREATE",
                        "DROP",
                        "ALTER",
                        "USE",
                        "SET",
                    ]
                ):
                    if len(stmt) > 10:  # Ignore very short statements
                        error_info = {
                            "file": str(file_path.relative_to(self.project_root)),
                            "error": f"Statement {i+1} doesn't contain recognized SQL keywords",
                            "type": "SyntaxWarning",
                        }
                        self.results["sql_files"]["errors"].append(error_info)

            return True

        except Exception as e:
            error_info = {
                "file": str(file_path.relative_to(self.project_root)),
                "error": f"SQL validation error: {e}",
                "type": "ValidationError",
            }
            self.results["sql_files"]["errors"].append(error_info)
            return False

    def scan_json_files(self) -> dict[str, Any]:
        """Scan JSON files for syntax validation"""
        self.logger.info("📄 Scanning JSON files...")

        json_files = list(self.project_root.rglob("*.json"))
        self.results["json_files"]["total"] = len(json_files)

        for json_file in json_files:
            try:
                with open(json_file, encoding="utf-8") as f:
                    json.load(f)
                self.results["json_files"]["valid"] += 1

            except json.JSONDecodeError as e:
                error_info = {
                    "file": str(json_file.relative_to(self.project_root)),
                    "line": e.lineno,
                    "column": e.colno,
                    "error": str(e),
                    "type": "JSONDecodeError",
                }
                self.results["json_files"]["errors"].append(error_info)
                self.logger.error(f"❌ {json_file.name}: {e}")

            except Exception as e:
                error_info = {
                    "file": str(json_file.relative_to(self.project_root)),
                    "error": str(e),
                    "type": "UnknownError",
                }
                self.results["json_files"]["errors"].append(error_info)

        success_rate = (
            (
                self.results["json_files"]["valid"]
                / self.results["json_files"]["total"]
                * 100
            )
            if self.results["json_files"]["total"] > 0
            else 0
        )

        self.logger.info(
            f"✅ JSON files: {self.results['json_files']['valid']}/{self.results['json_files']['total']} valid ({success_rate:.1f}%)"
        )
        return self.results["json_files"]

    def scan_yaml_files(self) -> dict[str, Any]:
        """Scan YAML files for syntax validation"""
        self.logger.info("📋 Scanning YAML files...")

        yaml_files = list(self.project_root.rglob("*.yaml")) + list(
            self.project_root.rglob("*.yml")
        )
        self.results["yaml_files"]["total"] = len(yaml_files)

        for yaml_file in yaml_files:
            try:
                with open(yaml_file, encoding="utf-8") as f:
                    yaml.safe_load(f)
                self.results["yaml_files"]["valid"] += 1

            except yaml.YAMLError as e:
                error_info = {
                    "file": str(yaml_file.relative_to(self.project_root)),
                    "error": str(e),
                    "type": "YAMLError",
                }
                self.results["yaml_files"]["errors"].append(error_info)
                self.logger.error(f"❌ {yaml_file.name}: {e}")

            except Exception as e:
                error_info = {
                    "file": str(yaml_file.relative_to(self.project_root)),
                    "error": str(e),
                    "type": "UnknownError",
                }
                self.results["yaml_files"]["errors"].append(error_info)

        success_rate = (
            (
                self.results["yaml_files"]["valid"]
                / self.results["yaml_files"]["total"]
                * 100
            )
            if self.results["yaml_files"]["total"] > 0
            else 0
        )

        self.logger.info(
            f"✅ YAML files: {self.results['yaml_files']['valid']}/{self.results['yaml_files']['total']} valid ({success_rate:.1f}%)"
        )
        return self.results["yaml_files"]

    def run_ruff_validation(self) -> dict[str, Any]:
        """Run ruff for comprehensive Python code quality"""
        self.logger.info("🔍 Running Ruff validation...")

        try:
            # Run ruff check
            result = subprocess.run(
                ["uv", "run", "ruff", "check", ".", "--output-format", "json"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=120,
            )

            if result.stdout:
                ruff_issues = json.loads(result.stdout)
                return {
                    "total_issues": len(ruff_issues),
                    "issues": ruff_issues[:50],  # Limit to first 50 for readability
                    "status": "completed",
                }
            else:
                return {"total_issues": 0, "issues": [], "status": "no_issues"}

        except subprocess.TimeoutExpired:
            return {"total_issues": -1, "issues": [], "status": "timeout"}
        except Exception as e:
            return {"total_issues": -1, "issues": [], "status": f"error: {e}"}

    def run_comprehensive_scan(self) -> dict[str, Any]:
        """Run comprehensive syntax scan across all file types"""
        self.logger.info("🚀 Starting Comprehensive Syntax Scan")
        self.logger.info("=" * 50)

        # Scan all file types
        self.scan_python_files()
        self.scan_sql_files()
        self.scan_json_files()
        self.scan_yaml_files()

        # Run additional validations
        ruff_results = self.run_ruff_validation()

        # Calculate summary
        total_files = (
            self.results["python_files"]["total"]
            + self.results["sql_files"]["total"]
            + self.results["json_files"]["total"]
            + self.results["yaml_files"]["total"]
        )

        total_valid = (
            self.results["python_files"]["valid"]
            + self.results["sql_files"]["valid"]
            + self.results["json_files"]["valid"]
            + self.results["yaml_files"]["valid"]
        )

        total_errors = (
            len(self.results["python_files"]["errors"])
            + len(self.results["sql_files"]["errors"])
            + len(self.results["json_files"]["errors"])
            + len(self.results["yaml_files"]["errors"])
        )

        self.results["summary"] = {
            "total_files_scanned": total_files,
            "total_valid_files": total_valid,
            "total_syntax_errors": total_errors,
            "overall_success_rate": (
                (total_valid / total_files * 100) if total_files > 0 else 0
            ),
            "ruff_validation": ruff_results,
        }

        # Log summary
        self.logger.info("=" * 50)
        self.logger.info("📊 SCAN SUMMARY")
        self.logger.info("=" * 50)
        self.logger.info(f"📁 Total files scanned: {total_files}")
        self.logger.info(f"✅ Valid files: {total_valid}")
        self.logger.info(f"❌ Files with errors: {total_errors}")
        self.logger.info(
            f"🎯 Success rate: {self.results['summary']['overall_success_rate']:.1f}%"
        )
        self.logger.info(f"🔍 Ruff issues: {ruff_results.get('total_issues', 'N/A')}")

        return self.results

    def save_results(self, output_file: str = "syntax_scan_results.json"):
        """Save scan results to JSON file"""
        output_path = self.project_root / output_file
        with open(output_path, "w") as f:
            json.dump(self.results, f, indent=2)

        self.logger.info(f"💾 Results saved to: {output_path}")
        return output_path


def main():
    """Main function"""
    project_root = Path("/home/ubuntu/sophia-main")
    scanner = ComprehensiveSyntaxScanner(project_root)

    # Run comprehensive scan
    results = scanner.run_comprehensive_scan()

    # Save results
    output_file = scanner.save_results()

    # Determine exit code based on results
    if results["summary"]["overall_success_rate"] >= 95.0:
        print("\n🎉 EXCELLENT: Syntax validation passed with flying colors!")
        return 0
    elif results["summary"]["overall_success_rate"] >= 85.0:
        print("\n✅ GOOD: Syntax validation passed with minor issues")
        return 0
    elif results["summary"]["overall_success_rate"] >= 70.0:
        print("\n⚠️ WARNING: Syntax validation passed but needs attention")
        return 1
    else:
        print("\n❌ CRITICAL: Syntax validation failed - immediate attention required")
        return 2


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
