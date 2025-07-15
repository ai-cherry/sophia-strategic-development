"""
Security Metrics Exporter for Prometheus monitoring.
Exposes vulnerability counts and trends as Prometheus metrics.
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml
from fastapi import FastAPI, Response
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    CollectorRegistry,
    Gauge,
    Histogram,
    generate_latest,
)
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)


class SecurityMetricsSettings(BaseSettings):
    """Settings for security metrics exporter."""

    reports_dir: str = Field(
        default="security/reports",
        description="Directory containing security scan reports",
    )
    allowlist_file: str = Field(
        default="security/vulnerability-allowlist.yaml",
        description="Path to vulnerability allowlist",
    )
    scan_interval_seconds: int = Field(
        default=3600, description="Interval between report scans"
    )
    port: int = Field(default=9092, description="Port to expose metrics on")

    class Config:
        env_prefix = "SECURITY_METRICS_"


class VulnerabilityMetrics(BaseModel):
    """Model for vulnerability metrics."""

    total_count: int = 0
    critical_count: int = 0
    high_count: int = 0
    medium_count: int = 0
    low_count: int = 0
    unknown_count: int = 0
    new_count: int = 0
    resolved_count: int = 0
    allowlisted_count: int = 0
    pending_review_count: int = 0
    in_progress_count: int = 0

    by_package: dict[str, int] = {}
    by_severity: dict[str, int] = {}
    age_distribution: dict[str, int] = {}  # e.g., "0-30 days", "31-90 days", etc.


class SecurityMetricsExporter:
    """Exports security vulnerability metrics for Prometheus."""

    def __init__(self, settings: SecurityMetricsSettings):
        self.settings = settings
        self.registry = CollectorRegistry()
        self._setup_metrics()
        self._last_scan_time = None
        self._vulnerability_cache = VulnerabilityMetrics()

    def _setup_metrics(self):
        """Initialize Prometheus metrics."""
        # Vulnerability counts by severity
        self.vuln_total = Gauge(
            "sophia_vulnerabilities_total",
            "Total number of vulnerabilities",
            registry=self.registry,
        )

        self.vuln_by_severity = Gauge(
            "sophia_vulnerabilities_by_severity",
            "Number of vulnerabilities by severity",
            ["severity"],
            registry=self.registry,
        )

        # Vulnerability lifecycle metrics
        self.vuln_new = Gauge(
            "sophia_vulnerabilities_new",
            "Number of new vulnerabilities in latest scan",
            registry=self.registry,
        )

        self.vuln_resolved = Gauge(
            "sophia_vulnerabilities_resolved",
            "Number of resolved vulnerabilities in latest scan",
            registry=self.registry,
        )

        self.vuln_allowlisted = Gauge(
            "sophia_vulnerabilities_allowlisted",
            "Number of allowlisted vulnerabilities",
            registry=self.registry,
        )

        self.vuln_pending_review = Gauge(
            "sophia_vulnerabilities_pending_review",
            "Number of vulnerabilities pending review",
            registry=self.registry,
        )

        self.vuln_in_progress = Gauge(
            "sophia_vulnerabilities_in_progress",
            "Number of vulnerabilities being remediated",
            registry=self.registry,
        )

        # Package metrics
        self.vuln_by_package = Gauge(
            "sophia_vulnerabilities_by_package",
            "Number of vulnerabilities by package",
            ["package"],
            registry=self.registry,
        )

        # Age distribution
        self.vuln_by_age = Gauge(
            "sophia_vulnerabilities_by_age",
            "Number of vulnerabilities by age category",
            ["age_category"],
            registry=self.registry,
        )

        # Scan metadata
        self.last_scan_timestamp = Gauge(
            "sophia_security_last_scan_timestamp",
            "Timestamp of last security scan",
            registry=self.registry,
        )

        self.scan_duration = Histogram(
            "sophia_security_scan_duration_seconds",
            "Duration of security scan in seconds",
            registry=self.registry,
        )

        # Alert thresholds
        self.critical_threshold_exceeded = Gauge(
            "sophia_security_critical_threshold_exceeded",
            "Whether critical vulnerability threshold is exceeded (0 or 1)",
            registry=self.registry,
        )

    async def update_metrics(self):
        """Update metrics from latest security reports."""
        start_time = datetime.now()

        try:
            # Load latest vulnerability report
            latest_report = self._find_latest_report()
            if not latest_report:
                logger.warning("No vulnerability reports found")
                return

            # Load vulnerability data
            with open(latest_report) as f:
                vuln_data = json.load(f)

            # Load allowlist
            allowlist_data = self._load_allowlist()

            # Calculate metrics
            metrics = self._calculate_metrics(vuln_data, allowlist_data)

            # Update Prometheus metrics
            self._update_prometheus_metrics(metrics)

            # Update cache
            self._vulnerability_cache = metrics
            self._last_scan_time = datetime.now()

            # Record scan metadata
            self.last_scan_timestamp.set(self._last_scan_time.timestamp())
            duration = (datetime.now() - start_time).total_seconds()
            self.scan_duration.observe(duration)

            logger.info(f"Updated security metrics in {duration:.2f}s")

        except Exception as e:
            logger.error(f"Error updating security metrics: {e}")

    def _find_latest_report(self) -> Path | None:
        """Find the most recent vulnerability report."""
        reports_path = Path(self.settings.reports_dir)
        if not reports_path.exists():
            return None

        # Look for all vulnerability report files
        report_files = list(reports_path.glob("*vulnerabilities*.json"))
        if not report_files:
            return None

        # Return the most recent file
        return max(report_files, key=lambda p: p.stat().st_mtime)

    def _load_allowlist(self) -> dict[str, Any]:
        """Load vulnerability allowlist configuration."""
        allowlist_path = Path(self.settings.allowlist_file)
        if not allowlist_path.exists():
            return {}

        try:
            with open(allowlist_path) as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            logger.error(f"Error loading allowlist: {e}")
            return {}

    def _calculate_metrics(
        self, vuln_data: dict, allowlist_data: dict
    ) -> VulnerabilityMetrics:
        """Calculate vulnerability metrics from raw data."""
        metrics = VulnerabilityMetrics()

        vulnerabilities = vuln_data.get("vulnerabilities", [])
        metrics.total_count = len(vulnerabilities)

        # Get allowlisted vulnerability IDs
        allowlisted_ids = {
            item.get("id") for item in allowlist_data.get("allowlist", [])
        }
        pending_ids = {
            item.get("id") for item in allowlist_data.get("pending_review", [])
        }
        in_progress_ids = {
            item.get("id") for item in allowlist_data.get("in_progress", [])
        }

        # Count by severity and package
        package_counts = {}
        severity_counts = {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
            "unknown": 0,
        }

        for vuln in vulnerabilities:
            vuln_id = vuln.get("id", "unknown")
            severity = vuln.get("severity", "unknown").lower()
            package = vuln.get("name", "unknown")

            # Skip if allowlisted
            if vuln_id in allowlisted_ids:
                metrics.allowlisted_count += 1
                continue

            # Check lifecycle status
            if vuln_id in pending_ids:
                metrics.pending_review_count += 1
            elif vuln_id in in_progress_ids:
                metrics.in_progress_count += 1

            # Count by severity
            if severity in severity_counts:
                severity_counts[severity] += 1
            else:
                severity_counts["unknown"] += 1

            # Count by package
            if package not in package_counts:
                package_counts[package] = 0
            package_counts[package] += 1

        # Update metrics
        metrics.critical_count = severity_counts["critical"]
        metrics.high_count = severity_counts["high"]
        metrics.medium_count = severity_counts["medium"]
        metrics.low_count = severity_counts["low"]
        metrics.unknown_count = severity_counts["unknown"]

        metrics.by_severity = severity_counts
        metrics.by_package = package_counts

        # Get new/resolved counts from comparison data if available
        comparison_file = self._find_latest_comparison()
        if comparison_file:
            try:
                with open(comparison_file) as f:
                    comparison = json.load(f)
                    metrics.new_count = comparison.get("new_vulnerabilities_count", 0)
                    metrics.resolved_count = comparison.get(
                        "resolved_vulnerabilities_count", 0
                    )
            except Exception as e:
                logger.error(f"Error loading comparison data: {e}")

        return metrics

    def _find_latest_comparison(self) -> Path | None:
        """Find the most recent baseline comparison report."""
        reports_path = Path(self.settings.reports_dir)
        comparison_files = list(reports_path.glob("*comparison*.json"))
        if not comparison_files:
            return None
        return max(comparison_files, key=lambda p: p.stat().st_mtime)

    def _update_prometheus_metrics(self, metrics: VulnerabilityMetrics):
        """Update Prometheus metrics with calculated values."""
        # Total count
        self.vuln_total.set(metrics.total_count)

        # By severity
        for severity in ["critical", "high", "medium", "low", "unknown"]:
            count = getattr(metrics, f"{severity}_count", 0)
            self.vuln_by_severity.labels(severity=severity).set(count)

        # Lifecycle metrics
        self.vuln_new.set(metrics.new_count)
        self.vuln_resolved.set(metrics.resolved_count)
        self.vuln_allowlisted.set(metrics.allowlisted_count)
        self.vuln_pending_review.set(metrics.pending_review_count)
        self.vuln_in_progress.set(metrics.in_progress_count)

        # By package (top 20 to avoid cardinality explosion)
        sorted_packages = sorted(
            metrics.by_package.items(), key=lambda x: x[1], reverse=True
        )[:20]

        for package, count in sorted_packages:
            self.vuln_by_package.labels(package=package).set(count)

        # Alert thresholds
        critical_threshold = metrics.critical_count > 0
        self.critical_threshold_exceeded.set(1 if critical_threshold else 0)

    async def run_periodic_updates(self):
        """Run periodic metric updates."""
        while True:
            await self.update_metrics()
            await asyncio.sleep(self.settings.scan_interval_seconds)


# FastAPI application
app = FastAPI(title="Sophia AI Security Metrics Exporter")
settings = SecurityMetricsSettings()
exporter = SecurityMetricsExporter(settings)


@app.on_event("startup")
async def startup_event():
    """Start periodic metric updates on startup."""
    asyncio.create_task(exporter.run_periodic_updates())


@app.get("/metrics")
async def metrics():
    """Expose Prometheus metrics."""
    # Generate latest metrics
    metrics_data = generate_latest(exporter.registry)
    return Response(content=metrics_data, media_type=CONTENT_TYPE_LATEST)


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "last_scan": (
            exporter._last_scan_time.isoformat() if exporter._last_scan_time else None
        ),
        "vulnerabilities": {
            "total": exporter._vulnerability_cache.total_count,
            "critical": exporter._vulnerability_cache.critical_count,
            "high": exporter._vulnerability_cache.high_count,
        },
    }


@app.get("/api/vulnerabilities/summary")
async def vulnerability_summary():
    """Get current vulnerability summary."""
    return exporter._vulnerability_cache.dict()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="127.0.0.1",  # Changed from 0.0.0.0 for security. Use environment variable for production
        port=settings.port,
        log_level="info",
    )
