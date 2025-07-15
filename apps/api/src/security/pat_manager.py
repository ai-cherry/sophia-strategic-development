"""
Qdrant PAT (Programmatic Access Token) Manager
Handles secure PAT lifecycle management with rotation alerts.
"""

import json
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

import structlog
from prometheus_client import Gauge

from backend.core.auto_esc_config import get_config_value, set_config_value

logger = structlog.get_logger(__name__)

# Prometheus metrics
pat_days_until_expiry = Gauge(
    "QDRANT_pat_days_until_expiry", "Days until PAT expiration", ["environment"]
)

pat_rotation_alerts = Gauge(
    "QDRANT_pat_rotation_alerts", "Number of PATs needing rotation", ["severity"]
)


class AlertSeverity(Enum):
    """Alert severity levels"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class PATMetadata:
    """PAT metadata for tracking"""

    environment: str
    created_at: datetime
    expires_at: datetime
    last_rotated: datetime | None = None
    rotation_count: int = 0
    created_by: str = "system"


@dataclass
class RotationAlert:
    """PAT rotation alert"""

    environment: str
    days_remaining: int
    severity: AlertSeverity
    pat_id: str | None = None
    message: str | None = None


class SecurityError(Exception):
    """Security-related errors"""

    pass


class QdrantPATManager:
    """
    Manages Qdrant PAT lifecycle including validation, rotation tracking, and alerts.
    """

    def __init__(self):
        self.rotation_days = 90  # Qdrant PAT expires after 90 days
        self.alert_days_before = 7  # Alert 7 days before expiry
        self.critical_days = 1  # Critical alert 1 day before expiry

        # Load PAT metadata from configuration
        self._pat_metadata: dict[str, PATMetadata] = self._load_pat_metadata()

        logger.info(
            "QdrantPATManager initialized",
            rotation_days=self.rotation_days,
            alert_threshold=self.alert_days_before,
        )

    async def get_current_pat(self, environment: str = None) -> str:
        """
        Retrieve current PAT with validation

        Args:
            environment: Environment name (prod, staging). Defaults to current.

        Returns:
            PAT string

        Raises:
            SecurityError: If PAT is invalid or not configured
        """
        if not environment:
            environment = get_config_value("environment", "prod")

        # Get PAT using auto_esc_config helper
        from backend.core.auto_esc_config import get_QDRANT_pat

        try:
            pat = get_QDRANT_pat(environment)
        except ValueError as e:
            raise SecurityError(f"PAT not configured: {e}")

        # Validate PAT format
        if not self._validate_pat_format(pat):
            raise SecurityError("Invalid PAT format")

        # Check if PAT is expired or needs rotation
        alerts = await self.check_rotation_needed()
        critical_alerts = [a for a in alerts if a.severity == AlertSeverity.CRITICAL]

        if critical_alerts:
            logger.error(
                "Critical PAT rotation needed",
                environment=environment,
                alerts=len(critical_alerts),
            )
            # In production, this might trigger automatic rotation

        return pat

    def _validate_pat_format(self, pat: str) -> bool:
        """
        Validate PAT format

        Qdrant PATs typically:
        - Start with specific prefix
        - Have minimum length
        - Contain only valid characters
        """
        if not pat:
            return False

        # Basic validation - adjust based on actual Qdrant PAT format
        if len(pat) < 32:
            return False

        # Check for valid characters (alphanumeric + some special chars)
        import re

        if not re.match(r"^[a-zA-Z0-9_\-\.]+$", pat):
            return False

        return True

    async def check_rotation_needed(self) -> list[RotationAlert]:
        """
        Check all PATs for rotation requirements

        Returns:
            List of rotation alerts
        """
        alerts = []
        now = datetime.now()

        for env in ["prod", "staging"]:
            metadata = self._pat_metadata.get(env)

            if not metadata:
                # No metadata - assume PAT needs rotation
                alerts.append(
                    RotationAlert(
                        environment=env,
                        days_remaining=0,
                        severity=AlertSeverity.CRITICAL,
                        message="No PAT metadata found - rotation required",
                    )
                )
                continue

            days_until_expiry = (metadata.expires_at - now).days

            # Update metrics
            pat_days_until_expiry.labels(environment=env).set(days_until_expiry)

            # Determine severity and create alert if needed
            if days_until_expiry <= 0:
                severity = AlertSeverity.CRITICAL
                message = "PAT has expired"
            elif days_until_expiry <= self.critical_days:
                severity = AlertSeverity.CRITICAL
                message = f"PAT expires in {days_until_expiry} days"
            elif days_until_expiry <= self.alert_days_before:
                severity = AlertSeverity.HIGH
                message = f"PAT expires in {days_until_expiry} days"
            elif days_until_expiry <= self.alert_days_before * 2:
                severity = AlertSeverity.MEDIUM
                message = f"PAT expires in {days_until_expiry} days"
            else:
                # No alert needed
                continue

            alerts.append(
                RotationAlert(
                    environment=env,
                    days_remaining=days_until_expiry,
                    severity=severity,
                    message=message,
                )
            )

        # Update alert metrics
        for severity in AlertSeverity:
            count = len([a for a in alerts if a.severity == severity])
            pat_rotation_alerts.labels(severity=severity.value).set(count)

        if alerts:
            logger.warning(
                "PAT rotation alerts generated",
                total_alerts=len(alerts),
                critical=len(
                    [a for a in alerts if a.severity == AlertSeverity.CRITICAL]
                ),
            )

        return alerts

    async def rotate_pat(self, environment: str, new_pat: str) -> dict[str, str]:
        """
        Rotate PAT for an environment

        Args:
            environment: Environment name
            new_pat: New PAT value

        Returns:
            Rotation confirmation with metadata
        """
        # Validate new PAT
        if not self._validate_pat_format(new_pat):
            raise SecurityError("Invalid new PAT format")

        # Store in configuration (would be Pulumi ESC in production)
        pat_key = f"QDRANT_pat_{environment}"
        set_config_value(pat_key, new_pat)

        # Update metadata
        now = datetime.now()
        metadata = PATMetadata(
            environment=environment,
            created_at=now,
            expires_at=now + timedelta(days=self.rotation_days),
            last_rotated=now,
            rotation_count=self._pat_metadata.get(
                environment,
                PATMetadata(environment=environment, created_at=now, expires_at=now),
            ).rotation_count
            + 1,
        )

        self._pat_metadata[environment] = metadata
        self._save_pat_metadata()

        logger.info(
            "PAT rotated successfully",
            environment=environment,
            expires_at=metadata.expires_at.isoformat(),
            rotation_count=metadata.rotation_count,
        )

        return {
            "environment": environment,
            "rotated_at": now.isoformat(),
            "expires_at": metadata.expires_at.isoformat(),
            "rotation_count": str(metadata.rotation_count),
        }

    def get_rotation_schedule(self) -> dict[str, dict[str, str]]:
        """
        Get rotation schedule for all PATs

        Returns:
            Schedule with next rotation dates
        """
        schedule = {}

        for env, metadata in self._pat_metadata.items():
            rotation_date = metadata.expires_at - timedelta(days=self.alert_days_before)

            schedule[env] = {
                "created_at": metadata.created_at.isoformat(),
                "expires_at": metadata.expires_at.isoformat(),
                "rotation_recommended": rotation_date.isoformat(),
                "days_until_expiry": str((metadata.expires_at - datetime.now()).days),
                "rotation_count": str(metadata.rotation_count),
            }

        return schedule

    def _load_pat_metadata(self) -> dict[str, PATMetadata]:
        """Load PAT metadata from configuration"""
        metadata = {}

        # Try to load from configuration
        metadata_json = get_config_value("QDRANT_pat_metadata")

        if metadata_json:
            try:
                data = json.loads(metadata_json)
                for env, env_data in data.items():
                    metadata[env] = PATMetadata(
                        environment=env,
                        created_at=datetime.fromisoformat(env_data["created_at"]),
                        expires_at=datetime.fromisoformat(env_data["expires_at"]),
                        last_rotated=(
                            datetime.fromisoformat(env_data["last_rotated"])
                            if env_data.get("last_rotated")
                            else None
                        ),
                        rotation_count=env_data.get("rotation_count", 0),
                    )
            except Exception as e:
                logger.error(f"Failed to load PAT metadata: {e}")

        # If no metadata, create default entries
        if not metadata:
            now = datetime.now()
            for env in ["prod", "staging"]:
                # Check if PAT exists
                try:
                    from backend.core.auto_esc_config import get_QDRANT_pat

                    pat = get_QDRANT_pat(env)
                    if pat:
                        # Assume PAT was created today (conservative)
                        metadata[env] = PATMetadata(
                            environment=env,
                            created_at=now,
                            expires_at=now + timedelta(days=self.rotation_days),
                        )
                except:
                    pass

        return metadata

    def _save_pat_metadata(self):
        """Save PAT metadata to configuration"""
        data = {}

        for env, metadata in self._pat_metadata.items():
            data[env] = {
                "created_at": metadata.created_at.isoformat(),
                "expires_at": metadata.expires_at.isoformat(),
                "last_rotated": (
                    metadata.last_rotated.isoformat() if metadata.last_rotated else None
                ),
                "rotation_count": metadata.rotation_count,
                "created_by": metadata.created_by,
            }

        set_config_value("QDRANT_pat_metadata", json.dumps(data))

    async def generate_rotation_report(self) -> dict[str, Any]:
        """
        Generate comprehensive PAT rotation report

        Returns:
            Report with rotation status and recommendations
        """
        alerts = await self.check_rotation_needed()
        schedule = self.get_rotation_schedule()

        report = {
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "total_pats": len(self._pat_metadata),
                "alerts": len(alerts),
                "critical_alerts": len(
                    [a for a in alerts if a.severity == AlertSeverity.CRITICAL]
                ),
                "high_alerts": len(
                    [a for a in alerts if a.severity == AlertSeverity.HIGH]
                ),
            },
            "alerts": [
                {
                    "environment": alert.environment,
                    "severity": alert.severity.value,
                    "days_remaining": alert.days_remaining,
                    "message": alert.message,
                }
                for alert in alerts
            ],
            "schedule": schedule,
            "recommendations": [],
        }

        # Add recommendations
        if report["summary"]["critical_alerts"] > 0:
            report["recommendations"].append(
                "URGENT: Rotate PATs with critical alerts immediately"
            )

        if report["summary"]["high_alerts"] > 0:
            report["recommendations"].append(
                "Schedule PAT rotation for high severity alerts within 24 hours"
            )

        # Check for PATs that haven't been rotated in a while
        for env, metadata in self._pat_metadata.items():
            if metadata.rotation_count == 0:
                report["recommendations"].append(
                    f"Consider rotating {env} PAT - never been rotated"
                )

        return report


# Singleton instance
_pat_manager: QdrantPATManager | None = None


def get_pat_manager() -> QdrantPATManager:
    """Get or create PAT manager instance"""
    global _pat_manager
    if _pat_manager is None:
        _pat_manager = QdrantPATManager()
    return _pat_manager
