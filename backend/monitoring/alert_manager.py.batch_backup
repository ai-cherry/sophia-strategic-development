"""
Alert Manager for Gong Data Quality Monitoring.

Handles intelligent alert routing, escalation, and notification
for data quality issues detected in the Gong webhook pipeline.
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional
from collections import defaultdict, deque
from enum import Enum

import httpx
import structlog
from pydantic import BaseModel, Field

from .gong_data_quality import AlertSeverity, AlertType, QualityReport, QualityDimension

logger = structlog.get_logger()


class NotificationChannel(str, Enum):
    """Available notification channels."""

    SLACK = "slack"
    EMAIL = "email"
    WEBHOOK = "webhook"
    PROMETHEUS = "prometheus"
    PAGERDUTY = "pagerduty"


class AlertStatus(str, Enum):
    """Alert lifecycle status."""

    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"
    ESCALATED = "escalated"


class AlertPolicy(BaseModel):
    """Alert policy configuration."""

    name: str
    description: str
    conditions: Dict[str, Any]
    severity_threshold: AlertSeverity
    channels: List[NotificationChannel]
    cooldown_minutes: int = 15
    escalation_after_minutes: int = 30
    max_alerts_per_hour: int = 10
    enabled: bool = True


class Alert(BaseModel):
    """Data quality alert."""

    alert_id: str
    alert_type: AlertType
    severity: AlertSeverity
    status: AlertStatus = AlertStatus.ACTIVE
    call_id: str
    webhook_id: Optional[str] = None
    quality_score: float
    dimensions: Dict[QualityDimension, float]
    title: str
    description: str
    details: Dict[str, Any]
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None
    resolution_notes: Optional[str] = None
    notification_history: List[Dict[str, Any]] = Field(default_factory=list)
    escalation_level: int = 0


class AlertGroup(BaseModel):
    """Group of related alerts."""

    group_id: str
    group_type: str  # e.g., "quality_degradation", "api_failures"
    alerts: List[Alert]
    first_seen: datetime
    last_seen: datetime
    total_count: int
    active_count: int


class QualityAlertManager:
    """
    Intelligent alert routing and escalation for data quality issues.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logger.bind(component="quality_alert_manager")

        # Alert tracking
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history = deque(maxlen=10000)
        self.alert_groups: Dict[str, AlertGroup] = {}

        # Rate limiting
        self.notification_history = defaultdict(lambda: deque(maxlen=100))
        self.channel_cooldowns: Dict[str, datetime] = {}

        # Alert policies
        self.policies = self._load_default_policies()

        # Notification clients
        self.notification_clients = self._initialize_notification_clients()

    def _load_default_policies(self) -> List[AlertPolicy]:
        """Load default alert policies."""
        return [
            AlertPolicy(
                name="critical_quality_degradation",
                description="Alert on critical quality score drops",
                conditions={
                    "quality_score_below": 0.5,
                    "severity": AlertSeverity.CRITICAL,
                },
                severity_threshold=AlertSeverity.CRITICAL,
                channels=[NotificationChannel.SLACK, NotificationChannel.PAGERDUTY],
                cooldown_minutes=5,
                escalation_after_minutes=15,
            ),
            AlertPolicy(
                name="sustained_quality_issues",
                description="Alert on sustained quality problems",
                conditions={
                    "quality_score_below": 0.8,
                    "duration_minutes": 30,
                    "affected_calls": 10,
                },
                severity_threshold=AlertSeverity.HIGH,
                channels=[NotificationChannel.SLACK, NotificationChannel.EMAIL],
                cooldown_minutes=60,
            ),
            AlertPolicy(
                name="api_enhancement_failures",
                description="Alert on API enhancement failures",
                conditions={"api_failure_rate_above": 0.1, "consecutive_failures": 5},
                severity_threshold=AlertSeverity.HIGH,
                channels=[NotificationChannel.SLACK, NotificationChannel.WEBHOOK],
                cooldown_minutes=30,
            ),
            AlertPolicy(
                name="processing_latency_spike",
                description="Alert on processing latency spikes",
                conditions={"latency_p95_above_seconds": 60, "duration_minutes": 15},
                severity_threshold=AlertSeverity.MEDIUM,
                channels=[NotificationChannel.SLACK],
                cooldown_minutes=30,
            ),
            AlertPolicy(
                name="data_completeness_degradation",
                description="Alert on data completeness issues",
                conditions={"completeness_below": 0.9, "missing_required_fields": True},
                severity_threshold=AlertSeverity.MEDIUM,
                channels=[NotificationChannel.SLACK, NotificationChannel.EMAIL],
                cooldown_minutes=60,
            ),
        ]

    def _initialize_notification_clients(self) -> Dict[NotificationChannel, Any]:
        """Initialize notification channel clients."""
        clients = {}

        # Initialize Slack client if configured
        if self.config.get("slack_webhook_url"):
            clients[NotificationChannel.SLACK] = SlackNotificationClient(
                webhook_url=self.config["slack_webhook_url"]
            )

        # Initialize email client if configured
        if self.config.get("email_config"):
            clients[NotificationChannel.EMAIL] = EmailNotificationClient(
                config=self.config["email_config"]
            )

        # Initialize webhook client
        if self.config.get("webhook_url"):
            clients[NotificationChannel.WEBHOOK] = WebhookNotificationClient(
                webhook_url=self.config["webhook_url"]
            )

        # Initialize PagerDuty client if configured
        if self.config.get("pagerduty_key"):
            clients[NotificationChannel.PAGERDUTY] = PagerDutyNotificationClient(
                integration_key=self.config["pagerduty_key"]
            )

        return clients

    async def trigger_quality_alert(
        self,
        alert_type: AlertType,
        severity: AlertSeverity,
        title: str,
        description: str,
        quality_report: QualityReport,
        details: Optional[Dict[str, Any]] = None,
    ) -> Optional[Alert]:
        """
        Trigger a quality alert with intelligent routing.

        Args:
            alert_type: Type of alert
            severity: Alert severity
            title: Alert title
            description: Alert description
            quality_report: Associated quality report
            details: Additional alert details

        Returns:
            Created alert or None if suppressed
        """
        # Check if alert should be suppressed
        if self._should_suppress_alert(alert_type, quality_report.call_id):
            self.logger.info(
                "Alert suppressed due to rate limiting",
                alert_type=alert_type.value,
                call_id=quality_report.call_id,
            )
            return None

        # Create alert
        alert = Alert(
            alert_id=f"alert_{quality_report.webhook_id}_{int(datetime.now().timestamp())}",
            alert_type=alert_type,
            severity=severity,
            call_id=quality_report.call_id,
            webhook_id=quality_report.webhook_id,
            quality_score=quality_report.overall_score,
            dimensions=quality_report.dimensions,
            title=title,
            description=description,
            details=details or {},
        )

        # Store alert
        self.active_alerts[alert.alert_id] = alert
        self.alert_history.append(alert)

        # Check for alert grouping
        group = self._find_or_create_alert_group(alert)
        if group:
            group.alerts.append(alert)
            group.last_seen = alert.created_at
            group.total_count += 1
            group.active_count += 1

        # Route alert based on policies
        await self._route_alert(alert, quality_report)

        # Schedule escalation if needed
        asyncio.create_task(self._schedule_escalation(alert))

        self.logger.warning(
            "Quality alert triggered",
            alert_id=alert.alert_id,
            alert_type=alert_type.value,
            severity=severity.value,
            call_id=quality_report.call_id,
        )

        return alert

    async def _route_alert(self, alert: Alert, quality_report: QualityReport):
        """Route alert to appropriate channels based on policies."""
        applicable_policies = self._get_applicable_policies(alert, quality_report)

        channels_notified = set()

        for policy in applicable_policies:
            for channel in policy.channels:
                if channel not in channels_notified:
                    if await self._send_notification(channel, alert, quality_report):
                        channels_notified.add(channel)

        # Record notification history
        alert.notification_history.append(
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "channels": list(channels_notified),
                "policies": [p.name for p in applicable_policies],
            }
        )

    def _get_applicable_policies(
        self, alert: Alert, quality_report: QualityReport
    ) -> List[AlertPolicy]:
        """Get policies that apply to this alert."""
        applicable = []

        for policy in self.policies:
            if not policy.enabled:
                continue

            # Check severity threshold
            if self._compare_severity(alert.severity, policy.severity_threshold) >= 0:
                # Check additional conditions
                if self._check_policy_conditions(policy, alert, quality_report):
                    applicable.append(policy)

        return applicable

    def _check_policy_conditions(
        self, policy: AlertPolicy, alert: Alert, quality_report: QualityReport
    ) -> bool:
        """Check if policy conditions are met."""
        conditions = policy.conditions

        # Check quality score condition
        if "quality_score_below" in conditions:
            if quality_report.overall_score >= conditions["quality_score_below"]:
                return False

        # Check API failure rate
        if "api_failure_rate_above" in conditions:
            # This would need to be calculated from recent history
            # For now, check if this is an API failure alert
            if alert.alert_type != AlertType.API_FAILURE:
                return False

        # Add more condition checks as needed

        return True

    async def _send_notification(
        self, channel: NotificationChannel, alert: Alert, quality_report: QualityReport
    ) -> bool:
        """Send notification through specified channel."""
        if channel not in self.notification_clients:
            self.logger.warning(f"Notification channel {channel} not configured")
            return False

        # Check channel cooldown
        if self._is_channel_in_cooldown(channel, alert.call_id):
            return False

        try:
            client = self.notification_clients[channel]

            if channel == NotificationChannel.SLACK:
                await client.send_alert(alert, quality_report)
            elif channel == NotificationChannel.EMAIL:
                await client.send_alert_email(alert, quality_report)
            elif channel == NotificationChannel.WEBHOOK:
                await client.send_webhook(alert, quality_report)
            elif channel == NotificationChannel.PAGERDUTY:
                await client.create_incident(alert, quality_report)

            # Record notification
            self.notification_history[channel].append(
                {
                    "timestamp": datetime.now(timezone.utc),
                    "alert_id": alert.alert_id,
                    "call_id": alert.call_id,
                }
            )

            return True

        except Exception as e:
            self.logger.error(f"Failed to send {channel} notification: {str(e)}")
            return False

    def _should_suppress_alert(self, alert_type: AlertType, call_id: str) -> bool:
        """Check if alert should be suppressed due to rate limiting."""
        # Check recent alerts for this call
        recent_alerts = [
            a
            for a in self.alert_history
            if a.call_id == call_id
            and a.alert_type == alert_type
            and (datetime.now(timezone.utc) - a.created_at).total_seconds() < 3600
        ]

        # Suppress if too many recent alerts
        if len(recent_alerts) >= 5:
            return True

        # Check global rate limits
        hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)
        recent_global_alerts = [
            a for a in self.alert_history if a.created_at > hour_ago
        ]

        if len(recent_global_alerts) >= 50:  # Max 50 alerts per hour globally
            return True

        return False

    def _is_channel_in_cooldown(
        self, channel: NotificationChannel, call_id: str
    ) -> bool:
        """Check if channel is in cooldown for this call."""
        cooldown_key = f"{channel}:{call_id}"

        if cooldown_key in self.channel_cooldowns:
            cooldown_until = self.channel_cooldowns[cooldown_key]
            if datetime.now(timezone.utc) < cooldown_until:
                return True

        return False

    def _find_or_create_alert_group(self, alert: Alert) -> Optional[AlertGroup]:
        """Find existing alert group or create new one."""
        # Group by alert type and severity
        group_key = f"{alert.alert_type}:{alert.severity}"

        if group_key in self.alert_groups:
            group = self.alert_groups[group_key]

            # Check if group is still active (within last hour)
            if (datetime.now(timezone.utc) - group.last_seen).total_seconds() < 3600:
                return group

        # Create new group
        group = AlertGroup(
            group_id=f"group_{group_key}_{int(datetime.now().timestamp())}",
            group_type=alert.alert_type.value,
            alerts=[],
            first_seen=alert.created_at,
            last_seen=alert.created_at,
            total_count=0,
            active_count=0,
        )

        self.alert_groups[group_key] = group
        return group

    async def _schedule_escalation(self, alert: Alert):
        """Schedule alert escalation if not resolved."""
        # Find applicable escalation policies
        policies = self._get_applicable_policies(alert, None)  # Need to refactor this

        if not policies:
            return

        # Get shortest escalation time
        escalation_minutes = min(p.escalation_after_minutes for p in policies)

        # Wait for escalation period
        await asyncio.sleep(escalation_minutes * 60)

        # Check if alert is still active
        if alert.alert_id in self.active_alerts and alert.status == AlertStatus.ACTIVE:
            await self._escalate_alert(alert)

    async def _escalate_alert(self, alert: Alert):
        """Escalate an unresolved alert."""
        alert.escalation_level += 1
        alert.status = AlertStatus.ESCALATED
        alert.updated_at = datetime.now(timezone.utc)

        self.logger.warning(
            "Alert escalated",
            alert_id=alert.alert_id,
            escalation_level=alert.escalation_level,
        )

        # Send escalation notifications
        # This would typically notify managers or on-call personnel
        if NotificationChannel.PAGERDUTY in self.notification_clients:
            await self.notification_clients[
                NotificationChannel.PAGERDUTY
            ].escalate_incident(alert)

    async def acknowledge_alert(
        self, alert_id: str, acknowledged_by: str, notes: Optional[str] = None
    ):
        """Acknowledge an alert."""
        if alert_id not in self.active_alerts:
            raise ValueError(f"Alert {alert_id} not found")

        alert = self.active_alerts[alert_id]
        alert.status = AlertStatus.ACKNOWLEDGED
        alert.acknowledged_at = datetime.now(timezone.utc)
        alert.acknowledged_by = acknowledged_by
        alert.updated_at = datetime.now(timezone.utc)

        if notes:
            alert.resolution_notes = notes

        self.logger.info(
            "Alert acknowledged", alert_id=alert_id, acknowledged_by=acknowledged_by
        )

    async def resolve_alert(self, alert_id: str, resolution_notes: str):
        """Resolve an alert."""
        if alert_id not in self.active_alerts:
            raise ValueError(f"Alert {alert_id} not found")

        alert = self.active_alerts[alert_id]
        alert.status = AlertStatus.RESOLVED
        alert.resolved_at = datetime.now(timezone.utc)
        alert.resolution_notes = resolution_notes
        alert.updated_at = datetime.now(timezone.utc)

        # Update group
        for group in self.alert_groups.values():
            if alert in group.alerts:
                group.active_count -= 1
                break

        # Remove from active alerts
        del self.active_alerts[alert_id]

        self.logger.info("Alert resolved", alert_id=alert_id)

    def _compare_severity(self, sev1: AlertSeverity, sev2: AlertSeverity) -> int:
        """Compare severity levels. Returns -1, 0, or 1."""
        severity_order = {
            AlertSeverity.INFO: 0,
            AlertSeverity.LOW: 1,
            AlertSeverity.MEDIUM: 2,
            AlertSeverity.HIGH: 3,
            AlertSeverity.CRITICAL: 4,
        }

        return severity_order[sev1] - severity_order[sev2]

    def get_active_alerts(
        self, call_id: Optional[str] = None, severity: Optional[AlertSeverity] = None
    ) -> List[Alert]:
        """Get active alerts with optional filtering."""
        alerts = list(self.active_alerts.values())

        if call_id:
            alerts = [a for a in alerts if a.call_id == call_id]

        if severity:
            alerts = [a for a in alerts if a.severity == severity]

        return sorted(alerts, key=lambda a: a.created_at, reverse=True)

    def get_alert_statistics(self) -> Dict[str, Any]:
        """Get alert statistics."""
        now = datetime.now(timezone.utc)
        hour_ago = now - timedelta(hours=1)
        day_ago = now - timedelta(days=1)

        recent_alerts = [a for a in self.alert_history if a.created_at > hour_ago]
        daily_alerts = [a for a in self.alert_history if a.created_at > day_ago]

        # Calculate statistics
        stats = {
            "active_alerts": len(self.active_alerts),
            "alerts_last_hour": len(recent_alerts),
            "alerts_last_24h": len(daily_alerts),
            "alerts_by_severity": defaultdict(int),
            "alerts_by_type": defaultdict(int),
            "average_resolution_time": None,
            "escalation_rate": 0.0,
        }

        # Count by severity and type
        for alert in daily_alerts:
            stats["alerts_by_severity"][alert.severity.value] += 1
            stats["alerts_by_type"][alert.alert_type.value] += 1

        # Calculate resolution time
        resolved_alerts = [
            a
            for a in self.alert_history
            if a.status == AlertStatus.RESOLVED and a.resolved_at
        ]
        if resolved_alerts:
            resolution_times = [
                (a.resolved_at - a.created_at).total_seconds() for a in resolved_alerts
            ]
            stats["average_resolution_time"] = sum(resolution_times) / len(
                resolution_times
            )

        # Calculate escalation rate
        if daily_alerts:
            escalated = sum(1 for a in daily_alerts if a.escalation_level > 0)
            stats["escalation_rate"] = escalated / len(daily_alerts)

        return stats


class SlackNotificationClient:
    """Slack notification client."""

    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
        self.logger = logger.bind(component="slack_notification")

    async def send_alert(self, alert: Alert, quality_report: QualityReport):
        """Send alert to Slack."""
        # Format message
        message = self._format_slack_message(alert, quality_report)

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(self.webhook_url, json=message)
                response.raise_for_status()
                self.logger.info("Slack notification sent", alert_id=alert.alert_id)
            except Exception as e:
                self.logger.error(f"Failed to send Slack notification: {str(e)}")
                raise

    def _format_slack_message(
        self, alert: Alert, quality_report: QualityReport
    ) -> Dict[str, Any]:
        """Format alert as Slack message."""
        color = {
            AlertSeverity.CRITICAL: "#FF0000",
            AlertSeverity.HIGH: "#FF6600",
            AlertSeverity.MEDIUM: "#FFCC00",
            AlertSeverity.LOW: "#0099FF",
            AlertSeverity.INFO: "#00CC00",
        }.get(alert.severity, "#808080")

        fields = [
            {"title": "Call ID", "value": alert.call_id, "short": True},
            {
                "title": "Quality Score",
                "value": f"{alert.quality_score:.2%}",
                "short": True,
            },
            {"title": "Alert Type", "value": alert.alert_type.value, "short": True},
            {"title": "Severity", "value": alert.severity.value.upper(), "short": True},
        ]

        # Add quality dimensions
        for dimension, score in alert.dimensions.items():
            if score < 0.8:  # Only show problematic dimensions
                fields.append(
                    {
                        "title": dimension.value.title(),
                        "value": f"{score:.2%}",
                        "short": True,
                    }
                )

        return {
            "attachments": [
                {
                    "color": color,
                    "title": f":warning: {alert.title}",
                    "text": alert.description,
                    "fields": fields,
                    "footer": "Gong Data Quality Monitor",
                    "ts": int(alert.created_at.timestamp()),
                    "actions": [
                        {
                            "type": "button",
                            "text": "View Details",
                            "url": f"https://monitoring.sophia-ai.com/alerts/{alert.alert_id}",
                        },
                        {
                            "type": "button",
                            "text": "Acknowledge",
                            "url": f"https://monitoring.sophia-ai.com/alerts/{alert.alert_id}/acknowledge",
                        },
                    ],
                }
            ]
        }


class EmailNotificationClient:
    """Email notification client (placeholder)."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logger.bind(component="email_notification")

    async def send_alert_email(self, alert: Alert, quality_report: QualityReport):
        """Send alert via email."""
        # Implementation would depend on email service
        self.logger.info("Email notification would be sent", alert_id=alert.alert_id)


class WebhookNotificationClient:
    """Generic webhook notification client."""

    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
        self.logger = logger.bind(component="webhook_notification")

    async def send_webhook(self, alert: Alert, quality_report: QualityReport):
        """Send alert to webhook."""
        payload = {
            "alert": alert.dict(),
            "quality_report": {
                "call_id": quality_report.call_id,
                "overall_score": quality_report.overall_score,
                "dimensions": quality_report.dimensions,
                "issues": [issue.dict() for issue in quality_report.issues],
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(self.webhook_url, json=payload)
                response.raise_for_status()
                self.logger.info("Webhook notification sent", alert_id=alert.alert_id)
            except Exception as e:
                self.logger.error(f"Failed to send webhook notification: {str(e)}")
                raise


class PagerDutyNotificationClient:
    """PagerDuty notification client."""

    def __init__(self, integration_key: str):
        self.integration_key = integration_key
        self.api_url = "https://events.pagerduty.com/v2/enqueue"
        self.logger = logger.bind(component="pagerduty_notification")

    async def create_incident(self, alert: Alert, quality_report: QualityReport):
        """Create PagerDuty incident."""
        payload = {
            "routing_key": self.integration_key,
            "event_action": "trigger",
            "dedup_key": alert.alert_id,
            "payload": {
                "summary": alert.title,
                "severity": self._map_severity(alert.severity),
                "source": "gong-data-quality",
                "custom_details": {
                    "call_id": alert.call_id,
                    "quality_score": alert.quality_score,
                    "alert_type": alert.alert_type.value,
                    "description": alert.description,
                    "dimensions": alert.dimensions,
                },
            },
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(self.api_url, json=payload)
                response.raise_for_status()
                self.logger.info("PagerDuty incident created", alert_id=alert.alert_id)
            except Exception as e:
                self.logger.error(f"Failed to create PagerDuty incident: {str(e)}")
                raise

    async def escalate_incident(self, alert: Alert):
        """Escalate existing PagerDuty incident."""
        payload = {
            "routing_key": self.integration_key,
            "event_action": "trigger",
            "dedup_key": alert.alert_id,
            "payload": {
                "summary": f"[ESCALATED] {alert.title}",
                "severity": "critical",  # Always critical for escalations
                "source": "gong-data-quality",
                "custom_details": {
                    "escalation_level": alert.escalation_level,
                    "original_severity": alert.severity.value,
                },
            },
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(self.api_url, json=payload)
                response.raise_for_status()
                self.logger.info(
                    "PagerDuty incident escalated", alert_id=alert.alert_id
                )
            except Exception as e:
                self.logger.error(f"Failed to escalate PagerDuty incident: {str(e)}")
                raise

    def _map_severity(self, severity: AlertSeverity) -> str:
        """Map alert severity to PagerDuty severity."""
        mapping = {
            AlertSeverity.CRITICAL: "critical",
            AlertSeverity.HIGH: "error",
            AlertSeverity.MEDIUM: "warning",
            AlertSeverity.LOW: "info",
            AlertSeverity.INFO: "info",
        }
        return mapping.get(severity, "warning")
