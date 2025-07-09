#!/usr/bin/env python3
"""
Placeholder Secret Detector and CI Enforcer
Fails CI/CD if any placeholder secrets are detected in the codebase
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

# Patterns that indicate placeholder secrets
PLACEHOLDER_PATTERNS = [
    r"PLACEHOLDER_[A-Z_]+",
    r"your_[a-z_]*(?:key|token|secret|password|api)(?:_here)?",
    r"YOUR_[A-Z_]*(?:KEY|TOKEN|SECRET|PASSWORD|API)(?:_HERE)?",
    r"REPLACE_ME(?:_WITH_SECRET)?",
    r"<YOUR_[A-Z_]+>",
    r"xxx+",  # xxxxx patterns
    r"dummy_(?:key|token|secret)",
    r"test_(?:key|token|secret)_\d+",
]

# File patterns to check
INCLUDE_PATTERNS = [
    "*.py",
    "*.js",
    "*.ts",
    "*.tsx",
    "*.jsx",
    "*.yaml",
    "*.yml",
    "*.json",
    "*.env*",
    "*.sh",
    "*.bash",
    "Dockerfile*",
    "*.md",
    "*.toml",
    "*.ini",
    "*.conf",
    "*.config",
]

# Directories to skip
EXCLUDE_DIRS = {
    ".git",
    "node_modules",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    "dist",
    "build",
    ".next",
    "coverage",
    "test_data",
    "mock_data",
    ".tox",
    "htmlcov",
}

# Files that are allowed to have placeholders (templates, examples)
ALLOWED_FILES = {
    "estuary.env.template",
    "scaffold_mcp_server.py",  # Template generator
    ".env.example",
    ".env.template",
    "example.env",
    "sample.env",
}


class PlaceholderDetector:
    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir)
        self.violations: list[dict] = []
        self.patterns = [re.compile(p, re.IGNORECASE) for p in PLACEHOLDER_PATTERNS]

    def should_check_file(self, file_path: Path) -> bool:
        """Determine if a file should be checked"""
        # Skip if in excluded directory
        for part in file_path.parts:
            if part in EXCLUDE_DIRS:
                return False

        # Skip if in allowed files
        if file_path.name in ALLOWED_FILES:
            return False

        # Check if matches include patterns
        return any(file_path.match(pattern) for pattern in INCLUDE_PATTERNS)

    def check_file(self, file_path: Path) -> list[tuple[int, str, str]]:
        """Check a single file for placeholder patterns"""
        violations = []

        try:
            with open(file_path, encoding="utf-8", errors="ignore") as f:
                for line_num, line in enumerate(f, 1):
                    for pattern in self.patterns:
                        matches = pattern.finditer(line)
                        for match in matches:
                            violations.append((line_num, match.group(), line.strip()))
        except Exception as e:
            print(f"Warning: Could not read {file_path}: {e}", file=sys.stderr)

        return violations

    def scan_directory(self) -> None:
        """Scan the entire directory tree"""
        for file_path in self.root_dir.rglob("*"):
            if file_path.is_file() and self.should_check_file(file_path):
                violations = self.check_file(file_path)
                if violations:
                    for line_num, match, context in violations:
                        self.violations.append(
                            {
                                "file": str(file_path.relative_to(self.root_dir)),
                                "line": line_num,
                                "match": match,
                                "context": context,
                            }
                        )

    def generate_report(self) -> dict:
        """Generate a comprehensive report"""
        # Group by file
        by_file = {}
        for v in self.violations:
            if v["file"] not in by_file:
                by_file[v["file"]] = []
            by_file[v["file"]].append(v)

        # Count by pattern type
        pattern_counts = {}
        for v in self.violations:
            pattern = (
                "PLACEHOLDER_"
                if "PLACEHOLDER_" in v["match"]
                else "your_*_key"
                if "your_" in v["match"].lower()
                else "YOUR_*_KEY"
                if "YOUR_" in v["match"]
                else "REPLACE_ME"
                if "REPLACE_ME" in v["match"]
                else "other"
            )
            pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1

        return {
            "total_violations": len(self.violations),
            "affected_files": len(by_file),
            "pattern_counts": pattern_counts,
            "violations_by_file": by_file,
        }

    def print_report(self, report: dict) -> None:
        """Print a human-readable report"""
        print("\n" + "=" * 80)
        print("🔍 PLACEHOLDER SECRET DETECTION REPORT")
        print("=" * 80)

        if report["total_violations"] == 0:
            print("✅ SUCCESS: No placeholder secrets detected!")
            return

        print(
            f"\n❌ FOUND {report['total_violations']} PLACEHOLDER SECRETS IN {report['affected_files']} FILES\n"
        )

        # Pattern summary
        print("Pattern Summary:")
        for pattern, count in sorted(
            report["pattern_counts"].items(), key=lambda x: x[1], reverse=True
        ):
            print(f"  - {pattern}: {count} occurrences")

        # File details
        print("\nViolations by File:")
        for file, violations in sorted(report["violations_by_file"].items()):
            print(f"\n📄 {file} ({len(violations)} violations):")
            for v in violations[:5]:  # Show first 5
                print(f"   Line {v['line']}: {v['match']}")
                print(f"   Context: {v['context'][:80]}...")
            if len(violations) > 5:
                print(f"   ... and {len(violations) - 5} more")

    def save_json_report(self, report: dict, output_file: str) -> None:
        """Save report as JSON for CI artifact"""
        with open(output_file, "w") as f:
            json.dump(report, f, indent=2)
        print(f"\n📊 Detailed report saved to: {output_file}")

    def generate_fix_script(self, report: dict) -> None:
        """Generate a script to help fix violations"""
        if report["total_violations"] == 0:
            return

        script_content = """#!/bin/bash
# Auto-generated script to help fix placeholder secrets
# Review each change before committing!

echo "🔧 Placeholder Secret Fix Helper"
echo "================================"
echo "This script will help you identify files with placeholders."
echo "You must manually update each secret with real values."
echo ""

"""
        for file in sorted(report["violations_by_file"].keys()):
            script_content += f'echo "\\n📝 Edit: {file}"\n'
            script_content += (
                f'echo "   Violations: {len(report["violations_by_file"][file])}"\n'
            )
            script_content += f'# $EDITOR "{file}"\n'

        script_content += """
echo ""
echo "After fixing all placeholders:"
echo "1. Run: python scripts/security/purge_placeholders.py"
echo "2. Commit your changes"
echo "3. Push to trigger CI validation"
"""

        with open("fix_placeholders.sh", "w") as f:
            f.write(script_content)
        os.chmod("fix_placeholders.sh", 0o755)
        print("\n🛠️  Fix helper script generated: ./fix_placeholders.sh")


def main():
    parser = argparse.ArgumentParser(
        description="Detect placeholder secrets in codebase"
    )
    parser.add_argument("--root", default=".", help="Root directory to scan")
    parser.add_argument("--json", help="Output JSON report to file")
    parser.add_argument(
        "--fix-script", action="store_true", help="Generate fix helper script"
    )
    parser.add_argument(
        "--ci", action="store_true", help="CI mode - exit 1 if violations found"
    )

    args = parser.parse_args()

    # Run detection
    detector = PlaceholderDetector(args.root)
    print(f"🔍 Scanning directory: {os.path.abspath(args.root)}")
    detector.scan_directory()

    # Generate report
    report = detector.generate_report()
    detector.print_report(report)

    # Save JSON if requested
    if args.json:
        detector.save_json_report(report, args.json)

    # Generate fix script if requested
    if args.fix_script:
        detector.generate_fix_script(report)

    # CI mode - exit with error if violations found
    if args.ci and report["total_violations"] > 0:
        print("\n❌ CI FAILED: Placeholder secrets detected!")
        print("Fix all placeholders before deployment.")
        sys.exit(1)
    elif args.ci:
        print("\n✅ CI PASSED: No placeholder secrets detected!")
        sys.exit(0)


if __name__ == "__main__":
    main()
