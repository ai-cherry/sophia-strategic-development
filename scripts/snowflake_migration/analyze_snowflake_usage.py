#!/usr/bin/env python3
"""
Analyze Snowflake usage patterns across the codebase to support migration to CortexGateway.
Identifies direct connections, Cortex function calls, and connection patterns.
"""

import ast
import json
import re
from collections import defaultdict
from pathlib import Path

# Patterns to identify Snowflake usage
SNOWFLAKE_PATTERNS = {
    "direct_connect": re.compile(r"snowflake\.connector\.connect\s*\("),
    "cortex_complete": re.compile(r"SNOWFLAKE\.CORTEX\.COMPLETE"),
    "cortex_embed": re.compile(r"SNOWFLAKE\.CORTEX\.EMBED_TEXT"),
    "cortex_search": re.compile(r"SNOWFLAKE\.CORTEX\.SEARCH"),
    "cortex_sentiment": re.compile(r"SNOWFLAKE\.CORTEX\.SENTIMENT"),
    "execute_query": re.compile(r"execute_query\s*\("),
    "cursor_execute": re.compile(r"cursor\.execute\s*\("),
    "connection_manager": re.compile(r"ConnectionManager|connection_manager"),
    "cortex_service": re.compile(r"SnowflakeCortexService|CortexService"),
}

# Files to skip
SKIP_PATTERNS = {
    "__pycache__",
    ".git",
    "node_modules",
    ".venv",
    "test_env",
    "venv",
    "env",
    ".pytest_cache",
    "build",
    "dist",
}


class SnowflakeUsageAnalyzer:
    """Analyze Snowflake usage patterns in the codebase."""

    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir)
        self.results = {
            "total_files_scanned": 0,
            "files_with_snowflake": 0,
            "direct_connections": [],
            "cortex_functions": defaultdict(list),
            "connection_managers": [],
            "service_usage": [],
            "migration_complexity": {},
        }

    def should_skip(self, path: Path) -> bool:
        """Check if path should be skipped."""
        return any(skip in str(path) for skip in SKIP_PATTERNS)

    def analyze_file(self, file_path: Path) -> dict[str, list[tuple[int, str]]]:
        """Analyze a single Python file for Snowflake usage."""
        if self.should_skip(file_path):
            return {}

        findings = defaultdict(list)

        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()
                lines = content.splitlines()

            # Check each pattern
            for pattern_name, pattern in SNOWFLAKE_PATTERNS.items():
                for match in pattern.finditer(content):
                    line_num = content[: match.start()].count("\n") + 1
                    line_content = (
                        lines[line_num - 1].strip() if line_num <= len(lines) else ""
                    )
                    findings[pattern_name].append((line_num, line_content))

            # Try AST analysis for imports
            try:
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            if "snowflake" in alias.name:
                                findings["imports"].append(
                                    (node.lineno, f"import {alias.name}")
                                )
                    elif isinstance(node, ast.ImportFrom):
                        if node.module and "snowflake" in node.module:
                            imports = ", ".join(alias.name for alias in node.names)
                            findings["imports"].append(
                                (node.lineno, f"from {node.module} import {imports}")
                            )
            except:
                pass  # AST parsing might fail on some files

        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")

        return findings

    def calculate_complexity(self, findings: dict[str, list]) -> str:
        """Calculate migration complexity for a file."""
        score = 0

        # Direct connections are most complex
        score += len(findings.get("direct_connect", [])) * 3

        # Cortex functions are medium complexity
        for pattern in [
            "cortex_complete",
            "cortex_embed",
            "cortex_search",
            "cortex_sentiment",
        ]:
            score += len(findings.get(pattern, []))

        # Service usage is easier to migrate
        score += len(findings.get("cortex_service", [])) * 0.5

        if score == 0:
            return "none"
        elif score < 3:
            return "low"
        elif score < 10:
            return "medium"
        else:
            return "high"

    def analyze_codebase(self):
        """Analyze entire codebase for Snowflake usage."""
        python_files = list(self.root_dir.rglob("*.py"))

        for file_path in python_files:
            if self.should_skip(file_path):
                continue

            self.results["total_files_scanned"] += 1
            findings = self.analyze_file(file_path)

            if findings:
                self.results["files_with_snowflake"] += 1
                relative_path = str(file_path.relative_to(self.root_dir))

                # Record direct connections
                if "direct_connect" in findings:
                    for line_num, line in findings["direct_connect"]:
                        self.results["direct_connections"].append(
                            {"file": relative_path, "line": line_num, "code": line}
                        )

                # Record Cortex function usage
                for func_type in [
                    "cortex_complete",
                    "cortex_embed",
                    "cortex_search",
                    "cortex_sentiment",
                ]:
                    if func_type in findings:
                        for line_num, line in findings[func_type]:
                            self.results["cortex_functions"][func_type].append(
                                {"file": relative_path, "line": line_num, "code": line}
                            )

                # Record service usage
                if "cortex_service" in findings:
                    self.results["service_usage"].append(
                        {
                            "file": relative_path,
                            "instances": len(findings["cortex_service"]),
                        }
                    )

                # Calculate complexity
                complexity = self.calculate_complexity(findings)
                self.results["migration_complexity"][relative_path] = {
                    "score": complexity,
                    "findings_count": sum(len(v) for v in findings.values()),
                }

    def generate_report(self) -> dict:
        """Generate migration report."""
        report = {
            "summary": {
                "total_files_scanned": self.results["total_files_scanned"],
                "files_with_snowflake": self.results["files_with_snowflake"],
                "direct_connections_count": len(self.results["direct_connections"]),
                "cortex_function_calls": sum(
                    len(v) for v in self.results["cortex_functions"].values()
                ),
                "high_complexity_files": len(
                    [
                        f
                        for f, c in self.results["migration_complexity"].items()
                        if c["score"] == "high"
                    ]
                ),
                "medium_complexity_files": len(
                    [
                        f
                        for f, c in self.results["migration_complexity"].items()
                        if c["score"] == "medium"
                    ]
                ),
                "low_complexity_files": len(
                    [
                        f
                        for f, c in self.results["migration_complexity"].items()
                        if c["score"] == "low"
                    ]
                ),
            },
            "priority_files": [],
            "direct_connections": self.results["direct_connections"][:10],  # Top 10
            "cortex_usage_by_function": {
                func: len(calls)
                for func, calls in self.results["cortex_functions"].items()
            },
            "migration_plan": [],
        }

        # Identify priority files (high complexity or many direct connections)
        for file_path, complexity in sorted(
            self.results["migration_complexity"].items(),
            key=lambda x: (x[1]["score"] == "high", x[1]["findings_count"]),
            reverse=True,
        )[:20]:
            report["priority_files"].append(
                {
                    "file": file_path,
                    "complexity": complexity["score"],
                    "findings": complexity["findings_count"],
                }
            )

        # Generate migration plan phases
        high_priority = [
            f
            for f, c in self.results["migration_complexity"].items()
            if c["score"] == "high"
        ]
        medium_priority = [
            f
            for f, c in self.results["migration_complexity"].items()
            if c["score"] == "medium"
        ]
        low_priority = [
            f
            for f, c in self.results["migration_complexity"].items()
            if c["score"] == "low"
        ]

        report["migration_plan"] = [
            {
                "phase": 1,
                "description": "High complexity files with direct connections",
                "files": high_priority[:10],
                "estimated_effort": "High",
            },
            {
                "phase": 2,
                "description": "Medium complexity files with Cortex functions",
                "files": medium_priority[:15],
                "estimated_effort": "Medium",
            },
            {
                "phase": 3,
                "description": "Low complexity files and service refactoring",
                "files": low_priority[:20],
                "estimated_effort": "Low",
            },
        ]

        return report


def main():
    """Run the analysis."""
    print("🔍 Analyzing Snowflake usage patterns...")

    analyzer = SnowflakeUsageAnalyzer()
    analyzer.analyze_codebase()
    report = analyzer.generate_report()

    # Save detailed results
    with open("reports/snowflake_usage_analysis.json", "w") as f:
        json.dump(report, f, indent=2)

    # Print summary
    print("\n📊 Analysis Summary:")
    print(f"Total files scanned: {report['summary']['total_files_scanned']}")
    print(f"Files with Snowflake usage: {report['summary']['files_with_snowflake']}")
    print(f"Direct connections found: {report['summary']['direct_connections_count']}")
    print(f"Cortex function calls: {report['summary']['cortex_function_calls']}")
    print("\n📈 Migration Complexity:")
    print(f"High complexity files: {report['summary']['high_complexity_files']}")
    print(f"Medium complexity files: {report['summary']['medium_complexity_files']}")
    print(f"Low complexity files: {report['summary']['low_complexity_files']}")

    print("\n📋 Top Priority Files:")
    for file_info in report["priority_files"][:5]:
        print(
            f"  - {file_info['file']} (complexity: {file_info['complexity']}, findings: {file_info['findings']})"
        )

    print("\n✅ Full report saved to: reports/snowflake_usage_analysis.json")


if __name__ == "__main__":
    main()
