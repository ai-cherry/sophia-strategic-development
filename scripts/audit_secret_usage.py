#!/usr/bin/env python3
"""
Audit all secret usage patterns in the Sophia AI codebase
"""

import json
import re
from collections import defaultdict
from pathlib import Path


class SecretUsageAuditor:
    def __init__(self):
        self.patterns = {
            "get_config_value": r'get_config_value\(["\']([^"\']+)["\']\)',
            "os_getenv": r'os\.getenv\(["\']([^"\']+)["\']\)',
            "os_environ": r'os\.environ\[["\']([^"\']+)["\']\]',
            "os_environ_get": r'os\.environ\.get\(["\']([^"\']+)["\']\)',
            "env_var_ref": r"\$\{?([A-Z_]+(?:_KEY|_TOKEN|_SECRET|_PASSWORD|_ID|_URL))\}?",
            "secrets_ref": r"secrets\.([A-Z_]+)",
            "process_env": r"process\.env\.([A-Z_]+)",
        }

        self.results = {
            "by_pattern": defaultdict(list),
            "by_file": defaultdict(list),
            "unique_secrets": set(),
            "secret_access_methods": defaultdict(int),
            "potential_issues": [],
        }

    def audit_file(self, file_path: Path) -> dict[str, list[str]]:
        """Audit a single file for secret usage"""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            self.results["potential_issues"].append(
                {"file": str(file_path), "error": str(e)}
            )
            return {}

        file_results = defaultdict(list)

        for pattern_name, pattern in self.patterns.items():
            matches = re.findall(pattern, content)
            if matches:
                for match in matches:
                    file_results[pattern_name].append(match)
                    self.results["by_pattern"][pattern_name].append(
                        {"file": str(file_path), "secret": match}
                    )
                    self.results["unique_secrets"].add(match)
                    self.results["secret_access_methods"][pattern_name] += 1

        if file_results:
            self.results["by_file"][str(file_path)] = dict(file_results)

        return file_results

    def check_for_hardcoded_secrets(self, file_path: Path):
        """Check for potential hardcoded secrets"""
        hardcoded_patterns = [
            (r"sk-[a-zA-Z0-9_-]{20,}", "OpenAI-style key"),
            (r"ghp_[a-zA-Z0-9_-]{20,}", "GitHub personal access token"),
            (r"pk_[a-zA-Z0-9_-]{20,}", "Stripe/Payment key"),
            (r"pul-[a-zA-Z0-9_-]{20,}", "Pulumi access token"),
            (r'["\'][a-zA-Z0-9]{32,}["\']', "Potential API key"),
        ]

        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            for pattern, key_type in hardcoded_patterns:
                matches = re.findall(pattern, content)
                if matches:
                    for match in matches:
                        # Skip if it's in a comment or documentation
                        if not any(
                            skip in str(file_path)
                            for skip in ["test", "example", "docs", "README"]
                        ):
                            self.results["potential_issues"].append(
                                {
                                    "file": str(file_path),
                                    "type": "hardcoded_secret",
                                    "key_type": key_type,
                                    "value": (
                                        match[:20] + "..." if len(match) > 20 else match
                                    ),
                                }
                            )
        except Exception:
            pass

    def audit_directory(self, directory: Path = Path(".")):
        """Audit all files in a directory"""
        extensions = [
            ".py",
            ".js",
            ".ts",
            ".jsx",
            ".tsx",
            ".yml",
            ".yaml",
            ".json",
            ".env",
        ]
        exclude_dirs = {
            ".git",
            "node_modules",
            "__pycache__",
            ".pytest_cache",
            "venv",
            ".venv",
        }

        for file_path in directory.rglob("*"):
            if any(excluded in str(file_path) for excluded in exclude_dirs):
                continue

            if file_path.is_file() and (
                file_path.suffix in extensions or ".env" in file_path.name
            ):
                self.audit_file(file_path)
                self.check_for_hardcoded_secrets(file_path)

    def analyze_naming_conventions(self):
        """Analyze secret naming conventions"""
        naming_analysis = {
            "uppercase_underscore": [],
            "lowercase_underscore": [],
            "camelCase": [],
            "mixed_conventions": [],
        }

        for secret in self.results["unique_secrets"]:
            if secret.isupper() or (
                secret.replace("_", "").isupper() and "_" in secret
            ):
                naming_analysis["uppercase_underscore"].append(secret)
            elif secret.islower() or (
                secret.replace("_", "").islower() and "_" in secret
            ):
                naming_analysis["lowercase_underscore"].append(secret)
            elif not secret.startswith(secret[0].lower()) and "_" not in secret:
                naming_analysis["camelCase"].append(secret)
            else:
                naming_analysis["mixed_conventions"].append(secret)

        return naming_analysis

    def generate_report(self):
        """Generate comprehensive audit report"""
        naming_analysis = self.analyze_naming_conventions()

        report = {
            "summary": {
                "total_files_scanned": len(self.results["by_file"]),
                "unique_secrets_found": len(self.results["unique_secrets"]),
                "access_patterns": dict(self.results["secret_access_methods"]),
                "potential_issues": len(self.results["potential_issues"]),
            },
            "naming_conventions": {
                "uppercase_underscore": len(naming_analysis["uppercase_underscore"]),
                "lowercase_underscore": len(naming_analysis["lowercase_underscore"]),
                "camelCase": len(naming_analysis["camelCase"]),
                "mixed": len(naming_analysis["mixed_conventions"]),
            },
            "top_secrets": sorted(
                [
                    (
                        secret,
                        sum(
                            1
                            for p in self.results["by_pattern"].values()
                            for item in p
                            if item["secret"] == secret
                        ),
                    )
                    for secret in self.results["unique_secrets"]
                ],
                key=lambda x: x[1],
                reverse=True,
            )[:20],
            "access_pattern_details": self.results["by_pattern"],
            "files_with_secrets": self.results["by_file"],
            "potential_issues": self.results["potential_issues"],
            "all_unique_secrets": sorted(self.results["unique_secrets"]),
        }

        return report


def main():
    auditor = SecretUsageAuditor()
    auditor.audit_directory()

    report = auditor.generate_report()

    # Save detailed report
    with open("secret_usage_audit_report.json", "w") as f:
        json.dump(report, f, indent=2)

    # Print summary

    for _pattern, count in report["summary"]["access_patterns"].items():
        pass

    for _convention, count in report["naming_conventions"].items():
        if count > 0:
            pass

    for _issue in report["potential_issues"][:5]:
        pass


if __name__ == "__main__":
    main()
