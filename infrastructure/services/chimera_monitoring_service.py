"""
Comprehensive Monitoring Service for Project Chimera
Provides real-time monitoring, metrics collection, and performance tracking
"""

import asyncio
import logging
import time
from collections import defaultdict, deque
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from typing import Any

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetric:
    """Performance metric data point"""

    metric_name: str
    value: float
    timestamp: datetime
    tags: dict[str, str] = None

@dataclass
class SystemHealth:
    """System health status"""

    component: str
    status: str  # 'healthy', 'degraded', 'unhealthy'
    last_check: datetime
    response_time: float
    error_rate: float
    details: dict[str, Any] = None

class ChimeraMonitoringService:
    """Comprehensive monitoring service for Project Chimera"""

    def __init__(self):
        self.metrics_buffer = defaultdict(deque)
        self.health_status = {}
        self.alert_thresholds = {
            "response_time_p99": 3000,  # 3 seconds
            "error_rate": 0.05,  # 5%
            "availability": 0.999,  # 99.9%
        }
        self.performance_targets = {
            "query_success_rate": 0.95,
            "average_response_time": 1500,
            "system_availability": 0.999,
        }
        self.monitoring_active = False

    async def start_monitoring(self):
        """Start the monitoring system"""
        self.monitoring_active = True
        logger.info("🚀 Starting Chimera monitoring system...")

        # Start monitoring tasks
        monitoring_tasks = [
            asyncio.create_task(self.monitor_performance_metrics()),
            asyncio.create_task(self.monitor_system_health()),
            asyncio.create_task(self.monitor_business_metrics()),
            asyncio.create_task(self.generate_alerts()),
        ]

        await asyncio.gather(*monitoring_tasks)

    async def stop_monitoring(self):
        """Stop the monitoring system"""
        self.monitoring_active = False
        logger.info("🛑 Stopping Chimera monitoring system...")

    async def monitor_performance_metrics(self):
        """Monitor performance metrics continuously"""
        while self.monitoring_active:
            try:
                # Collect performance metrics
                metrics = await self.collect_performance_metrics()

                for metric in metrics:
                    self.record_metric(metric)

                await asyncio.sleep(10)  # Collect every 10 seconds

            except Exception as e:
                logger.exception(f"Performance monitoring error: {e!s}")
                await asyncio.sleep(30)

    async def monitor_system_health(self):
        """Monitor system health continuously"""
        while self.monitoring_active:
            try:
                # Check health of all components
                components = [
                    "federated_query_layer",
                    "dynamic_orchestration",
                    "cortex_integration",
                    "action_framework",
                    "streaming_service",
                ]

                for component in components:
                    health = await self.check_component_health(component)
                    self.health_status[component] = health

                await asyncio.sleep(30)  # Check every 30 seconds

            except Exception as e:
                logger.exception(f"Health monitoring error: {e!s}")
                await asyncio.sleep(60)

    async def monitor_business_metrics(self):
        """Monitor business-level metrics"""
        while self.monitoring_active:
            try:
                # Collect business metrics
                business_metrics = await self.collect_business_metrics()

                for metric in business_metrics:
                    self.record_metric(metric)

                await asyncio.sleep(60)  # Collect every minute

            except Exception as e:
                logger.exception(f"Business monitoring error: {e!s}")
                await asyncio.sleep(120)

    async def generate_alerts(self):
        """Generate alerts based on thresholds"""
        while self.monitoring_active:
            try:
                alerts = await self.check_alert_conditions()

                for alert in alerts:
                    await self.send_alert(alert)

                await asyncio.sleep(60)  # Check every minute

            except Exception as e:
                logger.exception(f"Alert generation error: {e!s}")
                await asyncio.sleep(120)

    async def collect_performance_metrics(self) -> list[PerformanceMetric]:
        """Collect current performance metrics"""
        metrics = []
        current_time = datetime.utcnow()

        # Simulate metric collection
        metrics.extend(
            [
                PerformanceMetric(
                    metric_name="response_time_p99",
                    value=2500 + (time.time() % 1000),  # Simulated response time
                    timestamp=current_time,
                    tags={"component": "unified_chat"},
                ),
                PerformanceMetric(
                    metric_name="query_success_rate",
                    value=0.96,
                    timestamp=current_time,
                    tags={"component": "federated_query"},
                ),
                PerformanceMetric(
                    metric_name="active_users",
                    value=45,
                    timestamp=current_time,
                    tags={"component": "chat_interface"},
                ),
                PerformanceMetric(
                    metric_name="ai_model_cost",
                    value=0.12,
                    timestamp=current_time,
                    tags={"provider": "portkey"},
                ),
            ]
        )

        return metrics

    async def check_component_health(self, component: str) -> SystemHealth:
        """Check health of a specific component"""
        start_time = time.time()

        # Simulate health check
        await asyncio.sleep(0.1)  # Simulate check time

        response_time = (time.time() - start_time) * 1000  # Convert to ms

        # Simulate health status
        status = "healthy"
        error_rate = 0.02

        if response_time > 1000:
            status = "degraded"
        if error_rate > 0.1:
            status = "unhealthy"

        return SystemHealth(
            component=component,
            status=status,
            last_check=datetime.utcnow(),
            response_time=response_time,
            error_rate=error_rate,
            details={
                "version": "1.0.0",
                "uptime": "99.9%",
                "last_restart": "2025-01-01T00:00:00Z",
            },
        )

    async def collect_business_metrics(self) -> list[PerformanceMetric]:
        """Collect business-level metrics"""
        metrics = []
        current_time = datetime.utcnow()

        # Simulate business metric collection
        metrics.extend(
            [
                PerformanceMetric(
                    metric_name="executive_queries_per_hour",
                    value=25,
                    timestamp=current_time,
                    tags={"user_type": "executive"},
                ),
                PerformanceMetric(
                    metric_name="insights_generated",
                    value=180,
                    timestamp=current_time,
                    tags={"type": "automated"},
                ),
                PerformanceMetric(
                    metric_name="actions_executed",
                    value=12,
                    timestamp=current_time,
                    tags={"risk_level": "all"},
                ),
                PerformanceMetric(
                    metric_name="user_satisfaction_score",
                    value=4.7,
                    timestamp=current_time,
                    tags={"scale": "1-5"},
                ),
            ]
        )

        return metrics

    def record_metric(self, metric: PerformanceMetric):
        """Record a metric in the buffer"""
        metric_buffer = self.metrics_buffer[metric.metric_name]
        metric_buffer.append(metric)

        # Keep only last 1000 metrics per type
        while len(metric_buffer) > 1000:
            metric_buffer.popleft()

    async def check_alert_conditions(self) -> list[dict[str, Any]]:
        """Check for alert conditions"""
        alerts = []

        # Check response time threshold
        response_times = [m.value for m in self.metrics_buffer["response_time_p99"]]
        if (
            response_times
            and max(response_times[-10:]) > self.alert_thresholds["response_time_p99"]
        ):
            alerts.append(
                {
                    "type": "performance",
                    "severity": "warning",
                    "message": "Response time exceeding threshold",
                    "metric": "response_time_p99",
                    "current_value": max(response_times[-10:]),
                    "threshold": self.alert_thresholds["response_time_p99"],
                }
            )

        # Check system health
        unhealthy_components = [
            comp
            for comp, health in self.health_status.items()
            if health.status == "unhealthy"
        ]

        if unhealthy_components:
            alerts.append(
                {
                    "type": "health",
                    "severity": "critical",
                    "message": f'Unhealthy components detected: {", ".join(unhealthy_components)}',
                    "components": unhealthy_components,
                }
            )

        return alerts

    async def send_alert(self, alert: dict[str, Any]):
        """Send an alert notification"""
        logger.warning(f"🚨 ALERT: {alert['message']}")

        # This would integrate with actual alerting systems
        # For now, just log the alert
        {"timestamp": datetime.utcnow().isoformat(), "alert": alert}

        # Could send to Slack, email, PagerDuty, etc.

    async def get_dashboard_data(self) -> dict[str, Any]:
        """Get data for monitoring dashboard"""
        current_time = datetime.utcnow()

        # Calculate summary metrics
        response_times = [m.value for m in self.metrics_buffer["response_time_p99"]]
        success_rates = [m.value for m in self.metrics_buffer["query_success_rate"]]

        dashboard_data = {
            "timestamp": current_time.isoformat(),
            "summary": {
                "avg_response_time": (
                    sum(response_times[-10:]) / len(response_times[-10:])
                    if response_times
                    else 0
                ),
                "current_success_rate": success_rates[-1].value if success_rates else 0,
                "healthy_components": len(
                    [h for h in self.health_status.values() if h.status == "healthy"]
                ),
                "total_components": len(self.health_status),
                "active_alerts": len(await self.check_alert_conditions()),
            },
            "performance_metrics": {
                name: [asdict(m) for m in list(buffer)[-20:]]  # Last 20 metrics
                for name, buffer in self.metrics_buffer.items()
            },
            "health_status": {
                name: asdict(health) for name, health in self.health_status.items()
            },
            "targets": self.performance_targets,
        }

        return dashboard_data

    async def generate_performance_report(self, hours: int = 24) -> dict[str, Any]:
        """Generate performance report for specified time period"""
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours)

        # Filter metrics by time range
        filtered_metrics = {}
        for metric_name, buffer in self.metrics_buffer.items():
            filtered_metrics[metric_name] = [
                m for m in buffer if start_time <= m.timestamp <= end_time
            ]

        # Calculate statistics
        report = {
            "report_period": {
                "start": start_time.isoformat(),
                "end": end_time.isoformat(),
                "duration_hours": hours,
            },
            "performance_summary": {},
            "health_summary": {},
            "recommendations": [],
        }

        # Add performance statistics
        for metric_name, metrics in filtered_metrics.items():
            if metrics:
                values = [m.value for m in metrics]
                report["performance_summary"][metric_name] = {
                    "count": len(values),
                    "average": sum(values) / len(values),
                    "min": min(values),
                    "max": max(values),
                    "latest": values[-1],
                }

        # Add health summary
        report["health_summary"] = {
            "healthy_components": len(
                [h for h in self.health_status.values() if h.status == "healthy"]
            ),
            "degraded_components": len(
                [h for h in self.health_status.values() if h.status == "degraded"]
            ),
            "unhealthy_components": len(
                [h for h in self.health_status.values() if h.status == "unhealthy"]
            ),
        }

        # Add recommendations
        avg_response_time = (
            report["performance_summary"].get("response_time_p99", {}).get("average", 0)
        )
        if avg_response_time > 2000:
            report["recommendations"].append(
                "Consider optimizing query performance - average response time is above target"
            )

        success_rate = (
            report["performance_summary"]
            .get("query_success_rate", {})
            .get("average", 1.0)
        )
        if success_rate < 0.95:
            report["recommendations"].append(
                "Investigate query failures - success rate is below target"
            )

        return report
