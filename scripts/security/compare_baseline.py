#!/usr/bin/env python3
"""
Compare current vulnerabilities with baseline to identify new vulnerabilities.
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


class VulnerabilityComparator:
    """Compare vulnerability scan results with baseline."""

    def __init__(self, current_file: Path, baseline_file: Path):
        self.current_file = current_file
        self.baseline_file = baseline_file
        self.current_vulns = self._load_vulnerabilities(current_file)
        self.baseline_vulns = (
            self._load_vulnerabilities(baseline_file) if baseline_file.exists() else {}
        )

    def _load_vulnerabilities(self, file_path: Path) -> dict[str, Any]:
        """Load vulnerabilities from JSON file."""
        try:
            with open(file_path) as f:
                data = json.load(f)
                # Create a dict keyed by vulnerability ID for easy comparison
                vulns = {}
                for vuln in data.get("vulnerabilities", []):
                    # Create unique key from package name, version, and vulnerability ID
                    key = f"{vuln.get('name', 'unknown')}|{vuln.get('version', 'unknown')}|{vuln.get('id', 'unknown')}"
                    vulns[key] = vuln
                return vulns
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError as e:
            print(f"Error reading {file_path}: {e}")
            return {}

    def compare(self) -> dict[str, Any]:
        """Compare current vulnerabilities with baseline."""
        # Find new vulnerabilities
        new_vulns = []
        for key, vuln in self.current_vulns.items():
            if key not in self.baseline_vulns:
                new_vulns.append(vuln)

        # Find resolved vulnerabilities
        resolved_vulns = []
        for key, vuln in self.baseline_vulns.items():
            if key not in self.current_vulns:
                resolved_vulns.append(vuln)

        # Find persisting vulnerabilities
        persisting_vulns = []
        for key, vuln in self.current_vulns.items():
            if key in self.baseline_vulns:
                persisting_vulns.append(vuln)

        # Categorize by severity
        def categorize_by_severity(
            vulns: list[dict[str, Any]]
        ) -> dict[str, list[dict[str, Any]]]:
            by_severity = {
                "critical": [],
                "high": [],
                "medium": [],
                "low": [],
                "unknown": [],
            }
            for vuln in vulns:
                severity = vuln.get("severity", "unknown").lower()
                if severity in by_severity:
                    by_severity[severity].append(vuln)
                else:
                    by_severity["unknown"].append(vuln)
            return by_severity

        return {
            "scan_timestamp": datetime.utcnow().isoformat(),
            "total_current_vulnerabilities": len(self.current_vulns),
            "total_baseline_vulnerabilities": len(self.baseline_vulns),
            "new_vulnerabilities": new_vulns,
            "new_vulnerabilities_count": len(new_vulns),
            "new_by_severity": categorize_by_severity(new_vulns),
            "resolved_vulnerabilities": resolved_vulns,
            "resolved_vulnerabilities_count": len(resolved_vulns),
            "resolved_by_severity": categorize_by_severity(resolved_vulns),
            "persisting_vulnerabilities": persisting_vulns,
            "persisting_vulnerabilities_count": len(persisting_vulns),
            "persisting_by_severity": categorize_by_severity(persisting_vulns),
            "high_priority_new": [
                v
                for v in new_vulns
                if v.get("severity", "").lower() in ["critical", "high"]
            ],
            "high_priority_new_count": len(
                [
                    v
                    for v in new_vulns
                    if v.get("severity", "").lower() in ["critical", "high"]
                ]
            ),
        }

    def generate_summary(self, comparison: dict[str, Any]) -> str:
        """Generate a human-readable summary of the comparison."""
        summary = []
        summary.append(
            f"Vulnerability Scan Comparison - {comparison['scan_timestamp']}"
        )
        summary.append("=" * 60)
        summary.append(
            f"Total vulnerabilities in current scan: {comparison['total_current_vulnerabilities']}"
        )
        summary.append(
            f"Total vulnerabilities in baseline: {comparison['total_baseline_vulnerabilities']}"
        )
        summary.append("")

        # New vulnerabilities
        if comparison["new_vulnerabilities_count"] > 0:
            summary.append(
                f"🚨 NEW VULNERABILITIES: {comparison['new_vulnerabilities_count']}"
            )
            for severity in ["critical", "high", "medium", "low", "unknown"]:
                count = len(comparison["new_by_severity"][severity])
                if count > 0:
                    summary.append(f"  - {severity.upper()}: {count}")
            summary.append("")

        # Resolved vulnerabilities
        if comparison["resolved_vulnerabilities_count"] > 0:
            summary.append(
                f"✅ RESOLVED VULNERABILITIES: {comparison['resolved_vulnerabilities_count']}"
            )
            for severity in ["critical", "high", "medium", "low", "unknown"]:
                count = len(comparison["resolved_by_severity"][severity])
                if count > 0:
                    summary.append(f"  - {severity.upper()}: {count}")
            summary.append("")

        # Persisting vulnerabilities
        if comparison["persisting_vulnerabilities_count"] > 0:
            summary.append(
                f"⚠️  PERSISTING VULNERABILITIES: {comparison['persisting_vulnerabilities_count']}"
            )
            for severity in ["critical", "high", "medium", "low", "unknown"]:
                count = len(comparison["persisting_by_severity"][severity])
                if count > 0:
                    summary.append(f"  - {severity.upper()}: {count}")
            summary.append("")

        # High priority new vulnerabilities
        if comparison["high_priority_new_count"] > 0:
            summary.append("🔴 HIGH PRIORITY NEW VULNERABILITIES:")
            for vuln in comparison["high_priority_new"]:
                summary.append(
                    f"  - {vuln.get('name')} {vuln.get('version')}: {vuln.get('id')}"
                )
                if vuln.get("fix_versions"):
                    summary.append(
                        f"    Fix available: {', '.join(vuln.get('fix_versions', []))}"
                    )

        return "\n".join(summary)


def main():
    parser = argparse.ArgumentParser(
        description="Compare vulnerability scan results with baseline"
    )
    parser.add_argument(
        "--current", required=True, help="Path to current vulnerability scan JSON"
    )
    parser.add_argument(
        "--baseline", required=True, help="Path to baseline vulnerability scan JSON"
    )
    parser.add_argument(
        "--output", required=True, help="Path to output comparison JSON"
    )
    parser.add_argument(
        "--summary", action="store_true", help="Print human-readable summary"
    )

    args = parser.parse_args()

    current_path = Path(args.current)
    baseline_path = Path(args.baseline)
    output_path = Path(args.output)

    if not current_path.exists():
        print(f"Error: Current scan file not found: {current_path}")
        sys.exit(1)

    comparator = VulnerabilityComparator(current_path, baseline_path)
    comparison = comparator.compare()

    # Write comparison results
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(comparison, f, indent=2)

    # Print summary if requested
    if args.summary:
        print(comparator.generate_summary(comparison))

    # Exit with non-zero code if high priority vulnerabilities found
    if comparison["high_priority_new_count"] > 0:
        sys.exit(1)

    return 0


if __name__ == "__main__":
    main()
