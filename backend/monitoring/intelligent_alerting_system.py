#!/usr/bin/env python3
"""
Intelligent Alerting System for Sophia AI
Smart alerting with escalation, noise reduction, and context-aware notifications
"""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Alert severity levels"""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class AlertStatus(Enum):
    """Alert status"""

    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"


@dataclass
class Alert:
    """Alert definition"""

    id: str
    title: str
    description: str
    severity: AlertSeverity
    source: str
    timestamp: datetime
    status: AlertStatus = AlertStatus.ACTIVE
    acknowledged_by: str | None = None
    acknowledged_at: datetime | None = None
    resolved_at: datetime | None = None
    escalation_count: int = 0

    @property
    def age_minutes(self) -> int:
        return int((datetime.now() - self.timestamp).total_seconds() / 60)


class IntelligentAlertingSystem:
    """Production-grade alerting with intelligent features"""

    def __init__(self):
        self.active_alerts: dict[str, Alert] = {}
        self.alert_history: list[Alert] = []
        self.escalation_rules = {
            AlertSeverity.CRITICAL: {
                "escalate_after_minutes": 15,
                "max_escalations": 3,
            },
            AlertSeverity.WARNING: {"escalate_after_minutes": 60, "max_escalations": 2},
            AlertSeverity.INFO: {"escalate_after_minutes": 240, "max_escalations": 1},
        }
        self.noise_reduction_enabled = True

    async def create_alert(
        self,
        title: str,
        description: str,
        severity: AlertSeverity,
        source: str,
        context: dict[str, Any] = None,
    ) -> Alert:
        """Create new alert with intelligent deduplication"""

        # Check for duplicate alerts (noise reduction)
        if self.noise_reduction_enabled:
            existing_alert = self._find_similar_alert(title, source)
            if existing_alert:
                logger.info(f"Suppressing duplicate alert: {title}")
                return existing_alert

        # Create new alert
        alert_id = f"{source}_{int(datetime.now().timestamp())}"
        alert = Alert(
            id=alert_id,
            title=title,
            description=description,
            severity=severity,
            source=source,
            timestamp=datetime.now(),
        )

        self.active_alerts[alert_id] = alert

        # Send immediate notification for critical/emergency alerts
        if severity in [AlertSeverity.CRITICAL, AlertSeverity.EMERGENCY]:
            await self._send_immediate_notification(alert)

        logger.info(f"Created {severity.value} alert: {title}")
        return alert

    def _find_similar_alert(self, title: str, source: str) -> Alert | None:
        """Find similar active alert for deduplication"""
        for alert in self.active_alerts.values():
            if (
                alert.source == source
                and alert.status == AlertStatus.ACTIVE
                and self._calculate_similarity(alert.title, title) > 0.8
            ):
                return alert
        return None

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate text similarity (simplified)"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        if not words1 or not words2:
            return 0.0

        intersection = words1.intersection(words2)
        union = words1.union(words2)

        return len(intersection) / len(union)

    async def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> bool:
        """Acknowledge an alert"""
        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]
            alert.status = AlertStatus.ACKNOWLEDGED
            alert.acknowledged_by = acknowledged_by
            alert.acknowledged_at = datetime.now()

            logger.info(f"Alert acknowledged by {acknowledged_by}: {alert.title}")
            return True

        return False

    async def resolve_alert(self, alert_id: str, resolved_by: str = None) -> bool:
        """Resolve an alert"""
        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]
            alert.status = AlertStatus.RESOLVED
            alert.resolved_at = datetime.now()

            # Move to history
            self.alert_history.append(alert)
            del self.active_alerts[alert_id]

            logger.info(f"Alert resolved: {alert.title}")
            return True

        return False

    async def check_escalations(self):
        """Check for alerts that need escalation"""
        current_time = datetime.now()

        for alert in self.active_alerts.values():
            if alert.status != AlertStatus.ACTIVE:
                continue

            escalation_rule = self.escalation_rules.get(alert.severity)
            if not escalation_rule:
                continue

            # Check if escalation is needed
            minutes_since_created = (
                current_time - alert.timestamp
            ).total_seconds() / 60
            escalate_after = escalation_rule["escalate_after_minutes"]
            max_escalations = escalation_rule["max_escalations"]

            if (
                minutes_since_created >= escalate_after
                and alert.escalation_count < max_escalations
            ):
                await self._escalate_alert(alert)

    async def _escalate_alert(self, alert: Alert):
        """Escalate an alert"""
        alert.escalation_count += 1

        logger.warning(f"Escalating alert (#{alert.escalation_count}): {alert.title}")

        # Send escalation notification
        await self._send_escalation_notification(alert)

    async def _send_immediate_notification(self, alert: Alert):
        """Send immediate notification for critical alerts"""
        logger.critical(f"🚨 IMMEDIATE ALERT: {alert.title}")
        logger.critical(f"   Severity: {alert.severity.value}")
        logger.critical(f"   Source: {alert.source}")
        logger.critical(f"   Description: {alert.description}")

        # In production, this would send to Slack, email, PagerDuty, etc.

    async def _send_escalation_notification(self, alert: Alert):
        """Send escalation notification"""
        logger.error(f"⬆️ ESCALATION #{alert.escalation_count}: {alert.title}")
        logger.error(f"   Alert has been active for {alert.age_minutes} minutes")
        logger.error(f"   Severity: {alert.severity.value}")

        # In production, this would escalate to higher-level contacts

    async def generate_alert_summary(self) -> dict[str, Any]:
        """Generate comprehensive alert summary"""

        # Count alerts by severity
        severity_counts = {}
        for severity in AlertSeverity:
            severity_counts[severity.value] = sum(
                1
                for alert in self.active_alerts.values()
                if alert.severity == severity and alert.status == AlertStatus.ACTIVE
            )

        # Calculate alert trends
        recent_alerts = [
            alert
            for alert in self.alert_history
            if alert.timestamp > datetime.now() - timedelta(hours=24)
        ]

        # Top alert sources
        source_counts = {}
        for alert in list(self.active_alerts.values()) + recent_alerts:
            source_counts[alert.source] = source_counts.get(alert.source, 0) + 1

        top_sources = sorted(source_counts.items(), key=lambda x: x[1], reverse=True)[
            :5
        ]

        return {
            "timestamp": datetime.now().isoformat(),
            "active_alerts": {
                "total": len(self.active_alerts),
                "by_severity": severity_counts,
                "unacknowledged": sum(
                    1
                    for alert in self.active_alerts.values()
                    if alert.status == AlertStatus.ACTIVE
                ),
            },
            "alert_trends": {
                "last_24h": len(recent_alerts),
                "avg_resolution_time_minutes": self._calculate_avg_resolution_time(),
                "escalation_rate": self._calculate_escalation_rate(),
            },
            "top_alert_sources": top_sources,
            "system_health": {
                "alerting_system_status": "operational",
                "noise_reduction_enabled": self.noise_reduction_enabled,
                "total_escalations_today": sum(
                    alert.escalation_count for alert in self.active_alerts.values()
                ),
            },
        }

    def _calculate_avg_resolution_time(self) -> float:
        """Calculate average alert resolution time"""
        resolved_alerts = [
            alert
            for alert in self.alert_history
            if alert.resolved_at
            and alert.timestamp > datetime.now() - timedelta(days=7)
        ]

        if not resolved_alerts:
            return 0.0

        total_time = sum(
            (alert.resolved_at - alert.timestamp).total_seconds() / 60
            for alert in resolved_alerts
        )

        return total_time / len(resolved_alerts)

    def _calculate_escalation_rate(self) -> float:
        """Calculate escalation rate percentage"""
        recent_alerts = [
            alert
            for alert in self.alert_history + list(self.active_alerts.values())
            if alert.timestamp > datetime.now() - timedelta(days=7)
        ]

        if not recent_alerts:
            return 0.0

        escalated_alerts = sum(
            1 for alert in recent_alerts if alert.escalation_count > 0
        )
        return (escalated_alerts / len(recent_alerts)) * 100


# Global instance
intelligent_alerting_system = IntelligentAlertingSystem()


# Background escalation check task
async def escalation_check_task():
    """Background task for checking escalations"""
    while True:
        try:
            await intelligent_alerting_system.check_escalations()
            await asyncio.sleep(300)  # Check every 5 minutes
        except Exception as e:
            logger.error(f"Escalation check error: {e}")
            await asyncio.sleep(60)


# Start escalation check task
asyncio.create_task(escalation_check_task())
