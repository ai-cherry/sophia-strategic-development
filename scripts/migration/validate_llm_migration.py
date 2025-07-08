#!/usr/bin/env python3
"""
Validate LLM Router Migration
Checks for remaining direct LLM client usage and migration status
"""

import ast
import json
import re
from collections import defaultdict
from pathlib import Path


class LLMUsageValidator:
    """Validates LLM usage patterns in the codebase"""

    def __init__(self):
        self.issues = defaultdict(list)
        self.stats = {
            "total_files": 0,
            "files_with_issues": 0,
            "direct_openai_calls": 0,
            "direct_portkey_calls": 0,
            "direct_anthropic_calls": 0,
            "hardcoded_keys": 0,
            "old_imports": 0,
            "router_usage": 0,
        }

    def validate_file(self, file_path: Path) -> list[dict]:
        """Validate a single file for LLM usage patterns"""
        issues = []
        self.stats["total_files"] += 1

        try:
            content = file_path.read_text()

            # Check for direct SDK imports
            if re.search(r"^\s*import\s+openai\b", content, re.MULTILINE):
                issues.append(
                    {
                        "type": "direct_import",
                        "provider": "openai",
                        "line": self._find_line_number(content, r"import\s+openai"),
                    }
                )
                self.stats["old_imports"] += 1

            if re.search(r"^\s*from\s+openai\s+import", content, re.MULTILINE):
                issues.append(
                    {
                        "type": "direct_import",
                        "provider": "openai",
                        "line": self._find_line_number(
                            content, r"from\s+openai\s+import"
                        ),
                    }
                )
                self.stats["old_imports"] += 1

            if re.search(r"^\s*import\s+portkey_ai\b", content, re.MULTILINE):
                issues.append(
                    {
                        "type": "direct_import",
                        "provider": "portkey",
                        "line": self._find_line_number(content, r"import\s+portkey_ai"),
                    }
                )
                self.stats["old_imports"] += 1

            # Check for direct API calls
            if re.search(r"openai\.(ChatCompletion|Completion)\.create", content):
                issues.append(
                    {
                        "type": "direct_api_call",
                        "provider": "openai",
                        "pattern": "openai.*.create",
                    }
                )
                self.stats["direct_openai_calls"] += 1

            if re.search(r"AsyncOpenAI\s*\(", content):
                issues.append(
                    {
                        "type": "direct_client_init",
                        "provider": "openai",
                        "pattern": "AsyncOpenAI()",
                    }
                )
                self.stats["direct_openai_calls"] += 1

            if re.search(r"AsyncPortkey\s*\(", content):
                issues.append(
                    {
                        "type": "direct_client_init",
                        "provider": "portkey",
                        "pattern": "AsyncPortkey()",
                    }
                )
                self.stats["direct_portkey_calls"] += 1

            # Check for hardcoded API keys - exclude validation script itself
            if "validate_llm_migration" not in str(file_path):
                # Look for actual hardcoded keys, not patterns
                if re.search(
                    r'(api_key|API_KEY)\s*=\s*["\'][sS][kK]-[a-zA-Z0-9]{20,}["\']',
                    content,
                ):
                    issues.append(
                        {
                            "type": "hardcoded_key",
                            "severity": "critical",
                            "pattern": "api_key=hardcoded_value",
                        }
                    )
                    self.stats["hardcoded_keys"] += 1

            # Check for router usage (positive validation)
            if re.search(
                r"from\s+infrastructure\.services\.llm_router\s+import", content
            ):
                self.stats["router_usage"] += 1

            if re.search(r"llm_router\.complete\s*\(", content):
                self.stats["router_usage"] += 1

            # Parse AST for deeper analysis
            try:
                tree = ast.parse(content)
                self._analyze_ast(tree, issues)
            except SyntaxError:
                pass  # Skip files with syntax errors

            if issues:
                self.stats["files_with_issues"] += 1
                self.issues[str(file_path)] = issues

        except Exception as e:
            issues.append({"type": "error", "message": str(e)})

        return issues

    def _find_line_number(self, content: str, pattern: str) -> int:
        """Find line number of pattern in content"""
        lines = content.split("\n")
        for i, line in enumerate(lines, 1):
            if re.search(pattern, line):
                return i
        return 0

    def _analyze_ast(self, tree: ast.AST, issues: list[dict]):
        """Analyze AST for LLM usage patterns"""
        for node in ast.walk(tree):
            # Check for OpenAI client initialization
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id in [
                    "OpenAI",
                    "AsyncOpenAI",
                ]:
                    issues.append(
                        {
                            "type": "direct_client_init",
                            "provider": "openai",
                            "line": node.lineno,
                        }
                    )

            # Check for old unified_llm_service usage
            if isinstance(node, ast.ImportFrom):
                if node.module == "infrastructure.services.unified_llm_service":
                    issues.append(
                        {
                            "type": "old_service_import",
                            "severity": "warning",
                            "line": node.lineno,
                        }
                    )

    def generate_report(self) -> dict:
        """Generate validation report"""
        return {
            "summary": {
                "total_files_scanned": self.stats["total_files"],
                "files_with_issues": self.stats["files_with_issues"],
                "migration_progress": self._calculate_progress(),
                "critical_issues": self.stats["hardcoded_keys"],
                "router_adoption": self.stats["router_usage"],
            },
            "statistics": self.stats,
            "issues_by_file": dict(self.issues),
            "recommendations": self._generate_recommendations(),
        }

    def _calculate_progress(self) -> float:
        """Calculate migration progress percentage"""
        if self.stats["total_files"] == 0:
            return 100.0

        migrated_files = self.stats["total_files"] - self.stats["files_with_issues"]
        return round((migrated_files / self.stats["total_files"]) * 100, 2)

    def _generate_recommendations(self) -> list[str]:
        """Generate recommendations based on findings"""
        recommendations = []

        if self.stats["hardcoded_keys"] > 0:
            recommendations.append(
                f"CRITICAL: Found {self.stats['hardcoded_keys']} hardcoded API keys. "
                "These must be removed immediately and replaced with get_config_value() calls."
            )

        if self.stats["direct_openai_calls"] > 0:
            recommendations.append(
                f"Found {self.stats['direct_openai_calls']} direct OpenAI API calls. "
                "Run 'python scripts/codemod/replace_llm_clients.py --write' to migrate."
            )

        if self.stats["old_imports"] > 0:
            recommendations.append(
                f"Found {self.stats['old_imports']} old LLM client imports. "
                "These should be replaced with 'from infrastructure.services.llm_router import llm_router'."
            )

        if self.stats["router_usage"] < self.stats["total_files"] * 0.1:
            recommendations.append(
                "Low router adoption detected. Consider running the codemod script "
                "to accelerate migration to the unified LLM router."
            )

        return recommendations


def find_python_files(root_path: Path, exclude_patterns: list[str]) -> list[Path]:
    """Find all Python files to validate"""
    files = []

    for file_path in root_path.rglob("*.py"):
        # Skip excluded patterns
        if any(pattern in str(file_path) for pattern in exclude_patterns):
            continue
        files.append(file_path)

    return files


def main():
    """Main validation function"""
    print("🔍 Validating LLM Router Migration Status...\n")

    # Configuration
    root_path = Path.cwd()
    exclude_patterns = [
        "__pycache__",
        ".venv",
        "venv",
        "test_",
        "/tests/",
        "/migrations/",
        "scripts/codemod",  # Don't validate the codemod itself
        "llm_router",  # Don't validate the router module itself
        "validate_llm_migration.py",  # Don't validate the old validation script
    ]

    # Find files
    files = find_python_files(root_path, exclude_patterns)
    print(f"Found {len(files)} Python files to validate\n")

    # Validate files
    validator = LLMUsageValidator()

    for file_path in files:
        issues = validator.validate_file(file_path)
        if issues:
            print(f"❌ {file_path}: {len(issues)} issues")
            for issue in issues[:3]:  # Show first 3 issues
                print(
                    f"   - {issue['type']}: {issue.get('pattern', issue.get('provider', ''))}"
                )

    # Generate report
    report = validator.generate_report()

    # Print summary
    print("\n" + "=" * 60)
    print("📊 VALIDATION SUMMARY")
    print("=" * 60)
    print(f"Total files scanned: {report['summary']['total_files_scanned']}")
    print(f"Files with issues: {report['summary']['files_with_issues']}")
    print(f"Migration progress: {report['summary']['migration_progress']}%")
    print(f"Critical issues: {report['summary']['critical_issues']}")
    print(f"Router adoption: {report['summary']['router_adoption']} files")

    # Print statistics
    print("\n📈 STATISTICS:")
    for key, value in report["statistics"].items():
        if value > 0:
            print(f"  {key}: {value}")

    # Print recommendations
    if report["recommendations"]:
        print("\n💡 RECOMMENDATIONS:")
        for i, rec in enumerate(report["recommendations"], 1):
            print(f"{i}. {rec}")

    # Save detailed report
    report_path = Path("reports/llm_migration_validation.json")
    report_path.parent.mkdir(exist_ok=True)

    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    print(f"\n📄 Detailed report saved to: {report_path}")

    # Exit code based on critical issues
    if report["summary"]["critical_issues"] > 0:
        print("\n❌ Validation failed due to critical issues")
        return 1
    elif report["summary"]["files_with_issues"] > 0:
        print("\n⚠️  Validation completed with warnings")
        return 0
    else:
        print("\n✅ Validation passed - migration complete!")
        return 0


if __name__ == "__main__":
    exit(main())
