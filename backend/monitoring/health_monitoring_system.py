#!/usr/bin/env python3
"""
Health Monitoring System for Sophia AI
Comprehensive health checks with predictive alerting
"""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class AlertSeverity(str, Enum):
    """Alert severity levels"""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class HealthAlert:
    """Health monitoring alert"""

    service: str
    severity: AlertSeverity
    message: str
    timestamp: datetime
    resolved: bool = False


class HealthMonitoringSystem:
    """Comprehensive health monitoring with alerting"""

    def __init__(self):
        self.health_checkers = {}
        self.alerts: list[HealthAlert] = []
        self.monitoring_active = False

    async def start_monitoring(self):
        """Start health monitoring loops"""
        self.monitoring_active = True
        logger.info("🏥 Starting health monitoring system...")

        # Start monitoring tasks for each registered service
        for service_name in self.health_checkers.keys():
            asyncio.create_task(self._monitor_service(service_name))

        logger.info("✅ Health monitoring system started")

    def register_service(self, service_name: str, health_checker):
        """Register a service for health monitoring"""
        self.health_checkers[service_name] = health_checker
        logger.info(f"📋 Registered {service_name} for health monitoring")

    async def _monitor_service(self, service_name: str):
        """Monitor a specific service"""
        health_checker = self.health_checkers[service_name]

        while self.monitoring_active:
            try:
                # Perform health check
                health_result = await health_checker.check_health()

                # Check for alerts
                if health_result.status == "unhealthy":
                    await self._create_alert(
                        service_name,
                        AlertSeverity.CRITICAL,
                        f"Service {service_name} is unhealthy: {health_result.error_message}",
                    )
                elif health_result.response_time_ms > 5000:  # 5 second threshold
                    await self._create_alert(
                        service_name,
                        AlertSeverity.WARNING,
                        f"Service {service_name} response time is high: {health_result.response_time_ms}ms",
                    )

                # Wait for next check
                await asyncio.sleep(30)  # Check every 30 seconds

            except Exception as e:
                logger.error(f"Health monitoring error for {service_name}: {e}")
                await asyncio.sleep(60)  # Back off on errors

    async def _create_alert(self, service: str, severity: AlertSeverity, message: str):
        """Create and process alert"""
        alert = HealthAlert(
            service=service,
            severity=severity,
            message=message,
            timestamp=datetime.now(UTC),
        )

        self.alerts.append(alert)
        logger.warning(f"🚨 {severity.value.upper()}: {message}")

        # Here you would integrate with external alerting systems
        # (Slack, email, PagerDuty, etc.)

    async def get_system_health_summary(self) -> dict[str, Any]:
        """Get comprehensive system health summary"""
        health_results = {}

        for service_name, health_checker in self.health_checkers.items():
            try:
                result = await health_checker.check_health()
                health_results[service_name] = {
                    "status": result.status,
                    "response_time_ms": result.response_time_ms,
                    "last_check": result.timestamp.isoformat(),
                    "error_message": result.error_message,
                }
            except Exception as e:
                health_results[service_name] = {
                    "status": "error",
                    "error_message": str(e),
                }

        # Get recent alerts
        recent_alerts = [
            {
                "service": alert.service,
                "severity": alert.severity.value,
                "message": alert.message,
                "timestamp": alert.timestamp.isoformat(),
                "resolved": alert.resolved,
            }
            for alert in self.alerts[-10:]  # Last 10 alerts
        ]

        return {
            "timestamp": datetime.now(UTC).isoformat(),
            "overall_status": self._calculate_overall_status(health_results),
            "service_health": health_results,
            "recent_alerts": recent_alerts,
            "alert_summary": {
                "total_alerts": len(self.alerts),
                "critical_alerts": len(
                    [
                        a
                        for a in self.alerts
                        if a.severity == AlertSeverity.CRITICAL and not a.resolved
                    ]
                ),
                "warning_alerts": len(
                    [
                        a
                        for a in self.alerts
                        if a.severity == AlertSeverity.WARNING and not a.resolved
                    ]
                ),
            },
        }

    def _calculate_overall_status(self, health_results: dict[str, Any]) -> str:
        """Calculate overall system status"""
        if not health_results:
            return "unknown"

        statuses = [
            result.get("status", "unknown") for result in health_results.values()
        ]

        if any(status == "unhealthy" for status in statuses):
            return "critical"
        elif any(status == "degraded" for status in statuses):
            return "degraded"
        elif all(status == "healthy" for status in statuses):
            return "healthy"
        else:
            return "unknown"


# Global instance
health_monitoring_system = HealthMonitoringSystem()
