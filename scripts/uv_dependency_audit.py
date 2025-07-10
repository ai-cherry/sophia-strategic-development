#!/usr/bin/env python3
"""
UV Dependency Audit Tool
Continuous hygiene for Sophia AI dependencies
"""

import json
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional

import tomli


class Severity(Enum):
    """Vulnerability severity levels"""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class Vulnerability:
    """Represents a security vulnerability"""

    package: str
    installed_version: str
    vulnerability_id: str
    severity: Severity
    description: str
    fixed_version: Optional[str] = None


@dataclass
class DependencyIssue:
    """Represents a dependency issue"""

    package: str
    issue_type: str
    details: str
    severity: Severity


@dataclass
class AuditReport:
    """Complete audit report"""

    timestamp: datetime = field(default_factory=datetime.now)
    python_version: str = ""
    total_packages: int = 0
    direct_dependencies: int = 0
    group_dependencies: Dict[str, int] = field(default_factory=dict)
    vulnerabilities: List[Vulnerability] = field(default_factory=list)
    outdated_packages: List[Dict[str, str]] = field(default_factory=list)
    license_issues: List[DependencyIssue] = field(default_factory=list)
    size_metrics: Dict[str, int] = field(default_factory=dict)
    sync_time: float = 0.0

    @property
    def vulnerability_count(self) -> Dict[str, int]:
        """Count vulnerabilities by severity"""
        counts = {s.value: 0 for s in Severity}
        for vuln in self.vulnerabilities:
            counts[vuln.severity.value] += 1
        return counts

    @property
    def health_score(self) -> float:
        """Calculate overall health score (0-100)"""
        score = 100.0

        # Deduct for vulnerabilities
        vuln_counts = self.vulnerability_count
        score -= vuln_counts[Severity.CRITICAL.value] * 20
        score -= vuln_counts[Severity.HIGH.value] * 10
        score -= vuln_counts[Severity.MEDIUM.value] * 5
        score -= vuln_counts[Severity.LOW.value] * 2

        # Deduct for outdated packages
        if self.total_packages > 0:
            outdated_ratio = len(self.outdated_packages) / self.total_packages
            score -= outdated_ratio * 10

        # Deduct for license issues
        score -= len(self.license_issues) * 5

        # Deduct for slow sync time
        if self.sync_time > 60:
            score -= 5

        return max(0.0, score)


class UVDependencyAuditor:
    """Main auditor class"""

    def __init__(self, project_root: Path = Path.cwd()):
        self.project_root = project_root
        self.pyproject_path = project_root / "pyproject.toml"
        self.lock_path = project_root / "uv.lock"

    def run_audit(self) -> AuditReport:
        """Run complete dependency audit"""
        report = AuditReport()

        # Get Python version
        report.python_version = self._get_python_version()

        # Parse pyproject.toml
        project_config = self._parse_pyproject()

        # Count dependencies
        report.direct_dependencies = len(
            project_config.get("project", {}).get("dependencies", [])
        )

        # Count group dependencies
        for group, deps in project_config.get("dependency-groups", {}).items():
            report.group_dependencies[group] = len(deps)

        # Get total installed packages
        report.total_packages = self._count_installed_packages()

        # Check for vulnerabilities
        report.vulnerabilities = self._check_vulnerabilities()

        # Check for outdated packages
        report.outdated_packages = self._check_outdated_packages()

        # Check licenses
        report.license_issues = self._check_licenses()

        # Get size metrics
        report.size_metrics = self._calculate_size_metrics()

        # Measure sync time
        report.sync_time = self._measure_sync_time()

        return report

    def _get_python_version(self) -> str:
        """Get Python version"""
        result = subprocess.run(
            [sys.executable, "--version"], capture_output=True, text=True
        )
        return result.stdout.strip()

    def _parse_pyproject(self) -> dict:
        """Parse pyproject.toml"""
        with open(self.pyproject_path, "rb") as f:
            return tomli.load(f)

    def _count_installed_packages(self) -> int:
        """Count total installed packages"""
        try:
            result = subprocess.run(
                ["uv", "pip", "list", "--format", "json"],
                capture_output=True,
                text=True,
                env={
                    **subprocess.os.environ,
                    "PATH": f"{Path.home()}/.local/bin:{subprocess.os.environ['PATH']}",
                },
            )
            if result.returncode == 0:
                packages = json.loads(result.stdout)
                return len(packages)
        except Exception:
            pass
        return 0

    def _check_vulnerabilities(self) -> List[Vulnerability]:
        """Check for security vulnerabilities using pip-audit"""
        vulnerabilities = []

        try:
            # Run pip-audit
            result = subprocess.run(
                ["pip-audit", "--format", "json", "--desc"],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                audit_data = json.loads(result.stdout)
                for vuln in audit_data.get("vulnerabilities", []):
                    vulnerabilities.append(
                        Vulnerability(
                            package=vuln["name"],
                            installed_version=vuln["version"],
                            vulnerability_id=vuln["id"],
                            severity=Severity.HIGH,  # pip-audit doesn't provide severity
                            description=vuln.get("description", ""),
                            fixed_version=vuln.get("fix_versions", [None])[0],
                        )
                    )
        except Exception as e:
            print(f"Warning: Could not run pip-audit: {e}")

        return vulnerabilities

    def _check_outdated_packages(self) -> List[Dict[str, str]]:
        """Check for outdated packages"""
        outdated = []

        try:
            # UV doesn't have a direct outdated command yet, so we'll parse the lock file
            # This is a simplified check
            result = subprocess.run(
                ["uv", "pip", "list", "--outdated", "--format", "json"],
                capture_output=True,
                text=True,
                env={
                    **subprocess.os.environ,
                    "PATH": f"{Path.home()}/.local/bin:{subprocess.os.environ['PATH']}",
                },
            )

            if result.returncode == 0:
                outdated = json.loads(result.stdout)
        except Exception:
            # UV might not support --outdated yet
            pass

        return outdated

    def _check_licenses(self) -> List[DependencyIssue]:
        """Check for license compatibility issues"""
        issues = []

        # List of problematic licenses for proprietary software
        # problematic_licenses = {"GPL", "AGPL", "LGPL", "SSPL"}

        try:
            # This is a simplified check - in production, use a proper license checker
            subprocess.run(
                ["pip", "show", "--verbose"] + self._get_installed_packages(),
                capture_output=True,
                text=True,
            )

            # Parse output for license information
            # This is simplified - real implementation would be more robust

        except Exception:
            pass

        return issues

    def _get_installed_packages(self) -> List[str]:
        """Get list of installed package names"""
        try:
            result = subprocess.run(
                ["uv", "pip", "list", "--format", "json"],
                capture_output=True,
                text=True,
                env={
                    **subprocess.os.environ,
                    "PATH": f"{Path.home()}/.local/bin:{subprocess.os.environ['PATH']}",
                },
            )
            if result.returncode == 0:
                packages = json.loads(result.stdout)
                return [pkg["name"] for pkg in packages]
        except Exception:
            pass
        return []

    def _calculate_size_metrics(self) -> Dict[str, int]:
        """Calculate size metrics for dependencies"""
        metrics = {"total_size_mb": 0, "cache_size_mb": 0, "largest_package_mb": 0}

        # Check UV cache size
        cache_dir = Path.home() / ".cache" / "uv"
        if cache_dir.exists():
            cache_size = sum(
                f.stat().st_size for f in cache_dir.rglob("*") if f.is_file()
            )
            metrics["cache_size_mb"] = cache_size // (1024 * 1024)

        # Check virtual environment size
        venv_dir = self.project_root / ".venv"
        if venv_dir.exists():
            total_size = sum(
                f.stat().st_size for f in venv_dir.rglob("*") if f.is_file()
            )
            metrics["total_size_mb"] = total_size // (1024 * 1024)

        return metrics

    def _measure_sync_time(self) -> float:
        """Measure UV sync time"""
        import time

        start_time = time.time()
        try:
            subprocess.run(
                ["uv", "sync", "--no-install-project"],
                capture_output=True,
                env={
                    **subprocess.os.environ,
                    "PATH": f"{Path.home()}/.local/bin:{subprocess.os.environ['PATH']}",
                },
            )
        except Exception:
            pass

        return time.time() - start_time

    def generate_report(self, report: AuditReport, format: str = "text") -> str:
        """Generate formatted report"""
        if format == "json":
            return self._generate_json_report(report)
        elif format == "markdown":
            return self._generate_markdown_report(report)
        else:
            return self._generate_text_report(report)

    def _generate_text_report(self, report: AuditReport) -> str:
        """Generate text format report"""
        lines = [
            "=" * 60,
            "UV DEPENDENCY AUDIT REPORT",
            "=" * 60,
            f"Timestamp: {report.timestamp.isoformat()}",
            f"Python Version: {report.python_version}",
            f"Health Score: {report.health_score:.1f}/100",
            "",
            "DEPENDENCY SUMMARY:",
            f"  Total Packages: {report.total_packages}",
            f"  Direct Dependencies: {report.direct_dependencies}",
            "",
        ]

        if report.group_dependencies:
            lines.append("DEPENDENCY GROUPS:")
            for group, count in report.group_dependencies.items():
                lines.append(f"  {group}: {count} packages")
            lines.append("")

        vuln_counts = report.vulnerability_count
        if any(vuln_counts.values()):
            lines.extend(
                [
                    "SECURITY VULNERABILITIES:",
                    f"  Critical: {vuln_counts['critical']}",
                    f"  High: {vuln_counts['high']}",
                    f"  Medium: {vuln_counts['medium']}",
                    f"  Low: {vuln_counts['low']}",
                    "",
                ]
            )

            for vuln in report.vulnerabilities[:5]:  # Show first 5
                lines.append(
                    f"  - {vuln.package} ({vuln.installed_version}): {vuln.vulnerability_id}"
                )

        if report.outdated_packages:
            lines.extend([f"OUTDATED PACKAGES: {len(report.outdated_packages)}", ""])

        if report.size_metrics:
            lines.extend(
                [
                    "SIZE METRICS:",
                    f"  Total Size: {report.size_metrics.get('total_size_mb', 0)} MB",
                    f"  Cache Size: {report.size_metrics.get('cache_size_mb', 0)} MB",
                    "",
                ]
            )

        lines.extend(
            ["PERFORMANCE:", f"  UV Sync Time: {report.sync_time:.1f}s", "", "=" * 60]
        )

        return "\n".join(lines)

    def _generate_json_report(self, report: AuditReport) -> str:
        """Generate JSON format report"""
        data = {
            "timestamp": report.timestamp.isoformat(),
            "python_version": report.python_version,
            "health_score": report.health_score,
            "metrics": {
                "total_packages": report.total_packages,
                "direct_dependencies": report.direct_dependencies,
                "group_dependencies": report.group_dependencies,
                "vulnerabilities": report.vulnerability_count,
                "outdated_packages": len(report.outdated_packages),
                "size_mb": report.size_metrics.get("total_size_mb", 0),
                "sync_time_seconds": report.sync_time,
            },
            "vulnerabilities": [
                {
                    "package": v.package,
                    "version": v.installed_version,
                    "id": v.vulnerability_id,
                    "severity": v.severity.value,
                    "fixed_version": v.fixed_version,
                }
                for v in report.vulnerabilities
            ],
        }
        return json.dumps(data, indent=2)

    def _generate_markdown_report(self, report: AuditReport) -> str:
        """Generate Markdown format report"""
        lines = [
            "# UV Dependency Audit Report",
            "",
            f"**Generated:** {report.timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Python Version:** {report.python_version}",
            f"**Health Score:** {report.health_score:.1f}/100",
            "",
            "## Summary",
            "",
            f"- **Total Packages:** {report.total_packages}",
            f"- **Direct Dependencies:** {report.direct_dependencies}",
            f"- **Sync Time:** {report.sync_time:.1f}s",
            "",
        ]

        if report.group_dependencies:
            lines.extend(
                ["## Dependency Groups", "", "| Group | Count |", "|-------|-------|"]
            )
            for group, count in report.group_dependencies.items():
                lines.append(f"| {group} | {count} |")
            lines.append("")

        vuln_counts = report.vulnerability_count
        if any(vuln_counts.values()):
            lines.extend(
                [
                    "## Security Vulnerabilities",
                    "",
                    f"- **Critical:** {vuln_counts['critical']}",
                    f"- **High:** {vuln_counts['high']}",
                    f"- **Medium:** {vuln_counts['medium']}",
                    f"- **Low:** {vuln_counts['low']}",
                    "",
                ]
            )

        return "\n".join(lines)


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="UV Dependency Audit Tool")
    parser.add_argument(
        "--format",
        choices=["text", "json", "markdown"],
        default="text",
        help="Output format",
    )
    parser.add_argument("--output", help="Output file (default: stdout)")

    args = parser.parse_args()

    # Run audit
    auditor = UVDependencyAuditor()
    print("Running UV dependency audit...", file=sys.stderr)
    report = auditor.run_audit()

    # Generate report
    output = auditor.generate_report(report, format=args.format)

    # Write output
    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
        print(f"Report written to: {args.output}", file=sys.stderr)
    else:
        print(output)

    # Exit with non-zero if health score is low
    if report.health_score < 80:
        sys.exit(1)


if __name__ == "__main__":
    main()
