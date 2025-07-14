"""
Lambda Labs Cost Monitor
========================
Comprehensive cost monitoring and alerting system for Lambda Labs Serverless
with Qdrant integration, real-time alerts, and predictive cost analysis.
"""

import asyncio
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

import aiohttp

from backend.core.auto_esc_config import get_config_value
from backend.services.unified_memory_service_primary import UnifiedMemoryService

logger = logging.getLogger(__name__)


class AlertLevel(Enum):
    """Alert severity levels"""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class CostCategory(Enum):
    """Cost categorization"""

    INFERENCE = "inference"
    COMPUTE = "compute"
    STORAGE = "storage"
    BANDWIDTH = "bandwidth"
    OTHER = "other"


@dataclass
class CostAlert:
    """Cost alert data structure"""

    id: str
    level: AlertLevel
    category: CostCategory
    message: str
    current_value: float
    threshold: float
    timestamp: datetime
    resolved: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class CostPrediction:
    """Cost prediction data structure"""

    predicted_daily_cost: float
    predicted_monthly_cost: float
    confidence: float
    factors: list[str]
    timestamp: datetime
    trend_direction: str  # "increasing", "decreasing", "stable"


@dataclass
class ModelCostAnalysis:
    """Cost analysis per model"""

    model_name: str
    total_cost: float
    request_count: int
    avg_cost_per_request: float
    avg_input_tokens: int
    avg_output_tokens: int
    cost_efficiency_score: float
    usage_trend: str


class LambdaLabsCostMonitor:
    """
    Comprehensive cost monitoring system for Lambda Labs Serverless

    Features:
    - Real-time cost tracking and alerting
    - Predictive cost analysis
    - Model-specific cost optimization
    - Budget enforcement and recommendations
    - Qdrant integration for historical analysis
    - Slack/email notifications
    """

    def __init__(self):
        """Initialize the cost monitor"""
        # Configuration
        self.daily_budget = float(get_config_value("LAMBDA_DAILY_BUDGET", "100.0"))
        self.monthly_budget = float(get_config_value("LAMBDA_MONTHLY_BUDGET", "2500.0"))
        self.alert_email = get_config_value("ALERT_EMAIL", "admin@sophia-ai.com")
        self.slack_webhook = get_config_value("SLACK_WEBHOOK_URL")

        # Alert thresholds
        self.thresholds = {
            "daily_warning": self.daily_budget * 0.8,  # 80% of daily budget
            "daily_critical": self.daily_budget * 0.95,  # 95% of daily budget
            "hourly_warning": 10.0,  # $10/hour
            "hourly_critical": 25.0,  # $25/hour
            "cost_per_request_warning": 0.50,  # $0.50 per request
            "cost_per_request_critical": 1.00,  # $1.00 per request
            "efficiency_warning": 0.3,  # 30% efficiency score
            "efficiency_critical": 0.1,  # 10% efficiency score
        }

        # Monitoring state
        self.active_alerts: list[CostAlert] = []
        self.cost_history: list[dict[str, Any]] = []
        self.model_analytics: dict[str, ModelCostAnalysis] = {}

        # Qdrant integration
        self.qdrant_service = UnifiedMemoryService()

        # Monitoring task
        self.monitoring_task: asyncio.Task | None = None
        self.monitoring_interval = 300  # 5 minutes

        logger.info("🔍 Lambda Labs Cost Monitor initialized")

    async def start_monitoring(self) -> None:
        """Start the cost monitoring background task"""
        if self.monitoring_task and not self.monitoring_task.done():
            logger.warning("Cost monitoring already running")
            return

        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        logger.info("✅ Cost monitoring started")

    async def stop_monitoring(self) -> None:
        """Stop the cost monitoring background task"""
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
            self.monitoring_task = None

        logger.info("🛑 Cost monitoring stopped")

    async def _monitoring_loop(self) -> None:
        """Main monitoring loop"""
        while True:
            try:
                await self._perform_cost_check()
                await asyncio.sleep(self.monitoring_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Cost monitoring error: {e}")
                await asyncio.sleep(60)  # Wait 1 minute on error

    async def _perform_cost_check(self) -> None:
        """Perform comprehensive cost check"""
        try:
            # Get current costs
            current_costs = await self._get_current_costs()

            # Check thresholds
            await self._check_cost_thresholds(current_costs)

            # Update model analytics
            await self._update_model_analytics()

            # Generate predictions
            prediction = await self._generate_cost_prediction()

            # Store in Qdrant
            await self._store_cost_data(current_costs, prediction)

            # Check for anomalies
            await self._detect_cost_anomalies(current_costs)

        except Exception as e:
            logger.error(f"Cost check failed: {e}")

    async def _get_current_costs(self) -> dict[str, Any]:
        """Get current cost information"""
        from backend.services.lambda_labs_serverless_service import get_lambda_service

        try:
            service = await get_lambda_service()
            stats = await service.get_usage_stats()

            return {
                "daily_cost": stats["daily_cost"],
                "hourly_cost": stats["hourly_cost"],
                "total_cost": stats["total_cost"],
                "total_requests": stats["total_requests"],
                "successful_requests": stats["successful_requests"],
                "failed_requests": stats["failed_requests"],
                "model_usage": stats["model_usage"],
                "average_response_time": stats["average_response_time"],
                "budget_remaining": stats["budget_remaining"],
                "timestamp": datetime.now(),
            }
        except Exception as e:
            logger.error(f"Failed to get current costs: {e}")
            return {}

    async def _check_cost_thresholds(self, costs: dict[str, Any]) -> None:
        """Check cost thresholds and generate alerts"""
        if not costs:
            return

        daily_cost = costs.get("daily_cost", 0.0)
        hourly_cost = costs.get("hourly_cost", 0.0)
        total_requests = costs.get("total_requests", 0)

        # Calculate cost per request
        cost_per_request = daily_cost / total_requests if total_requests > 0 else 0.0

        # Check daily budget
        if daily_cost >= self.thresholds["daily_critical"]:
            await self._create_alert(
                AlertLevel.CRITICAL,
                CostCategory.INFERENCE,
                f"Daily budget critical: ${daily_cost:.2f} >= ${self.thresholds['daily_critical']:.2f}",
                daily_cost,
                self.thresholds["daily_critical"],
            )
        elif daily_cost >= self.thresholds["daily_warning"]:
            await self._create_alert(
                AlertLevel.WARNING,
                CostCategory.INFERENCE,
                f"Daily budget warning: ${daily_cost:.2f} >= ${self.thresholds['daily_warning']:.2f}",
                daily_cost,
                self.thresholds["daily_warning"],
            )

        # Check hourly costs
        if hourly_cost >= self.thresholds["hourly_critical"]:
            await self._create_alert(
                AlertLevel.CRITICAL,
                CostCategory.INFERENCE,
                f"Hourly cost critical: ${hourly_cost:.2f} >= ${self.thresholds['hourly_critical']:.2f}",
                hourly_cost,
                self.thresholds["hourly_critical"],
            )
        elif hourly_cost >= self.thresholds["hourly_warning"]:
            await self._create_alert(
                AlertLevel.WARNING,
                CostCategory.INFERENCE,
                f"Hourly cost warning: ${hourly_cost:.2f} >= ${self.thresholds['hourly_warning']:.2f}",
                hourly_cost,
                self.thresholds["hourly_warning"],
            )

        # Check cost per request
        if cost_per_request >= self.thresholds["cost_per_request_critical"]:
            await self._create_alert(
                AlertLevel.CRITICAL,
                CostCategory.INFERENCE,
                f"Cost per request critical: ${cost_per_request:.3f} >= ${self.thresholds['cost_per_request_critical']:.3f}",
                cost_per_request,
                self.thresholds["cost_per_request_critical"],
            )
        elif cost_per_request >= self.thresholds["cost_per_request_warning"]:
            await self._create_alert(
                AlertLevel.WARNING,
                CostCategory.INFERENCE,
                f"Cost per request warning: ${cost_per_request:.3f} >= ${self.thresholds['cost_per_request_warning']:.3f}",
                cost_per_request,
                self.thresholds["cost_per_request_warning"],
            )

    async def _create_alert(
        self,
        level: AlertLevel,
        category: CostCategory,
        message: str,
        current_value: float,
        threshold: float,
    ) -> None:
        """Create and process a cost alert"""
        alert = CostAlert(
            id=f"{category.value}_{level.value}_{datetime.now().timestamp()}",
            level=level,
            category=category,
            message=message,
            current_value=current_value,
            threshold=threshold,
            timestamp=datetime.now(),
        )

        # Check if similar alert already exists
        existing_alert = next(
            (
                a
                for a in self.active_alerts
                if a.category == category and a.level == level and not a.resolved
            ),
            None,
        )

        if existing_alert:
            # Update existing alert
            existing_alert.current_value = current_value
            existing_alert.timestamp = datetime.now()
            existing_alert.message = message
        else:
            # Add new alert
            self.active_alerts.append(alert)

        # Send notifications
        await self._send_alert_notification(alert)

        logger.warning(f"🚨 Cost Alert [{level.value.upper()}]: {message}")

    async def _send_alert_notification(self, alert: CostAlert) -> None:
        """Send alert notification via Slack/email"""
        try:
            # Prepare notification message
            message = f"""
🚨 **Lambda Labs Cost Alert**

**Level:** {alert.level.value.upper()}
**Category:** {alert.category.value}
**Message:** {alert.message}
**Current Value:** ${alert.current_value:.2f}
**Threshold:** ${alert.threshold:.2f}
**Time:** {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')}

**Recommendations:**
- Review current usage patterns
- Consider switching to more cost-effective models
- Implement request batching
- Enable response caching
            """

            # Send Slack notification
            if self.slack_webhook:
                await self._send_slack_notification(message, alert.level)

            # Send email notification (placeholder)
            # await self._send_email_notification(message, alert.level)

        except Exception as e:
            logger.error(f"Failed to send alert notification: {e}")

    async def _send_slack_notification(self, message: str, level: AlertLevel) -> None:
        """Send Slack notification"""
        try:
            color_map = {
                AlertLevel.INFO: "#36a64f",
                AlertLevel.WARNING: "#ff9500",
                AlertLevel.CRITICAL: "#ff0000",
                AlertLevel.EMERGENCY: "#8B0000",
            }

            payload = {
                "text": "Lambda Labs Cost Alert",
                "attachments": [
                    {
                        "color": color_map.get(level, "#36a64f"),
                        "text": message,
                        "ts": datetime.now().timestamp(),
                    }
                ],
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(self.slack_webhook, json=payload) as response:
                    if response.status == 200:
                        logger.info("Slack notification sent successfully")
                    else:
                        logger.error(f"Slack notification failed: {response.status}")

        except Exception as e:
            logger.error(f"Slack notification error: {e}")

    async def _update_model_analytics(self) -> None:
        """Update model-specific cost analytics"""
        try:
            from backend.services.lambda_labs_serverless_service import (
                get_lambda_service,
            )

            service = await get_lambda_service()

            # Analyze each model
            for model_name in service.models.keys():
                model_requests = [
                    r
                    for r in service.request_history
                    if r.model_used == model_name and r.success
                ]

                if not model_requests:
                    continue

                # Calculate analytics
                total_cost = sum(r.cost for r in model_requests)
                request_count = len(model_requests)
                avg_cost_per_request = total_cost / request_count
                avg_input_tokens = (
                    sum(r.input_tokens for r in model_requests) / request_count
                )
                avg_output_tokens = (
                    sum(r.output_tokens for r in model_requests) / request_count
                )
                avg_response_time = (
                    sum(r.response_time for r in model_requests) / request_count
                )

                # Calculate efficiency score (lower is better)
                cost_efficiency_score = (
                    avg_response_time / avg_cost_per_request
                    if avg_cost_per_request > 0
                    else 0
                )

                # Determine usage trend
                recent_requests = [
                    r
                    for r in model_requests
                    if r.timestamp > datetime.now() - timedelta(hours=24)
                ]
                older_requests = [
                    r
                    for r in model_requests
                    if r.timestamp <= datetime.now() - timedelta(hours=24)
                ]

                if len(recent_requests) > len(older_requests):
                    usage_trend = "increasing"
                elif len(recent_requests) < len(older_requests):
                    usage_trend = "decreasing"
                else:
                    usage_trend = "stable"

                # Store analytics
                self.model_analytics[model_name] = ModelCostAnalysis(
                    model_name=model_name,
                    total_cost=total_cost,
                    request_count=request_count,
                    avg_cost_per_request=avg_cost_per_request,
                    avg_input_tokens=int(avg_input_tokens),
                    avg_output_tokens=int(avg_output_tokens),
                    cost_efficiency_score=cost_efficiency_score,
                    usage_trend=usage_trend,
                )

        except Exception as e:
            logger.error(f"Failed to update model analytics: {e}")

    async def _generate_cost_prediction(self) -> CostPrediction:
        """Generate cost predictions based on usage patterns"""
        try:
            from backend.services.lambda_labs_serverless_service import (
                get_lambda_service,
            )

            service = await get_lambda_service()

            # Get recent usage data
            recent_hours = 24
            cutoff_time = datetime.now() - timedelta(hours=recent_hours)
            recent_requests = [
                r
                for r in service.request_history
                if r.timestamp > cutoff_time and r.success
            ]

            if not recent_requests:
                return CostPrediction(
                    predicted_daily_cost=0.0,
                    predicted_monthly_cost=0.0,
                    confidence=0.0,
                    factors=["No recent data"],
                    timestamp=datetime.now(),
                    trend_direction="stable",
                )

            # Calculate hourly average
            hourly_costs = {}
            for request in recent_requests:
                hour_key = request.timestamp.strftime("%Y-%m-%d %H:00")
                if hour_key not in hourly_costs:
                    hourly_costs[hour_key] = 0.0
                hourly_costs[hour_key] += request.cost

            avg_hourly_cost = sum(hourly_costs.values()) / len(hourly_costs)

            # Predict daily cost
            predicted_daily_cost = avg_hourly_cost * 24

            # Predict monthly cost
            predicted_monthly_cost = predicted_daily_cost * 30

            # Calculate confidence based on data consistency
            cost_variance = sum(
                (cost - avg_hourly_cost) ** 2 for cost in hourly_costs.values()
            ) / len(hourly_costs)
            confidence = max(
                0.0,
                min(
                    1.0,
                    (
                        1.0 - (cost_variance / avg_hourly_cost)
                        if avg_hourly_cost > 0
                        else 0.0
                    ),
                ),
            )

            # Determine trend
            if len(hourly_costs) >= 2:
                recent_half = list(hourly_costs.values())[len(hourly_costs) // 2 :]
                older_half = list(hourly_costs.values())[: len(hourly_costs) // 2]

                recent_avg = sum(recent_half) / len(recent_half)
                older_avg = sum(older_half) / len(older_half)

                if recent_avg > older_avg * 1.1:
                    trend_direction = "increasing"
                elif recent_avg < older_avg * 0.9:
                    trend_direction = "decreasing"
                else:
                    trend_direction = "stable"
            else:
                trend_direction = "stable"

            # Identify factors
            factors = []
            if predicted_daily_cost > self.daily_budget:
                factors.append("Predicted to exceed daily budget")
            if predicted_monthly_cost > self.monthly_budget:
                factors.append("Predicted to exceed monthly budget")
            if trend_direction == "increasing":
                factors.append("Usage trend is increasing")

            return CostPrediction(
                predicted_daily_cost=predicted_daily_cost,
                predicted_monthly_cost=predicted_monthly_cost,
                confidence=confidence,
                factors=factors,
                timestamp=datetime.now(),
                trend_direction=trend_direction,
            )

        except Exception as e:
            logger.error(f"Failed to generate cost prediction: {e}")
            return CostPrediction(
                predicted_daily_cost=0.0,
                predicted_monthly_cost=0.0,
                confidence=0.0,
                factors=[f"Prediction error: {e!s}"],
                timestamp=datetime.now(),
                trend_direction="stable",
            )

    async def _store_cost_data(
        self, costs: dict[str, Any], prediction: CostPrediction
    ) -> None:
        """Store cost data in Qdrant for historical analysis"""
        try:
            # Prepare cost record
            cost_record = {
                "timestamp": costs.get("timestamp", datetime.now()).isoformat(),
                "daily_cost": costs.get("daily_cost", 0.0),
                "hourly_cost": costs.get("hourly_cost", 0.0),
                "total_cost": costs.get("total_cost", 0.0),
                "total_requests": costs.get("total_requests", 0),
                "successful_requests": costs.get("successful_requests", 0),
                "failed_requests": costs.get("failed_requests", 0),
                "average_response_time": costs.get("average_response_time", 0.0),
                "budget_remaining": costs.get("budget_remaining", 0.0),
                "predicted_daily_cost": prediction.predicted_daily_cost,
                "predicted_monthly_cost": prediction.predicted_monthly_cost,
                "prediction_confidence": prediction.confidence,
                "trend_direction": prediction.trend_direction,
                "model_usage": json.dumps(costs.get("model_usage", {})),
            }

            # Insert into Qdrant
            insert_query = """
            INSERT INTO SOPHIA_AI.AI_INSIGHTS.LAMBDA_LABS_COST_MONITORING
            (timestamp, daily_cost, hourly_cost, total_cost, total_requests,
             successful_requests, failed_requests, average_response_time,
             budget_remaining, predicted_daily_cost, predicted_monthly_cost,
             prediction_confidence, trend_direction, model_usage)
            VALUES (%(timestamp)s, %(daily_cost)s, %(hourly_cost)s, %(total_cost)s,
                    %(total_requests)s, %(successful_requests)s, %(failed_requests)s,
                    %(average_response_time)s, %(budget_remaining)s, %(predicted_daily_cost)s,
                    %(predicted_monthly_cost)s, %(prediction_confidence)s, %(trend_direction)s,
                    %(model_usage)s)
            """

            await self.qdrant_service.execute_query(insert_query, cost_record)

        except Exception as e:
            logger.error(f"Failed to store cost data in Qdrant: {e}")

    async def _detect_cost_anomalies(self, costs: dict[str, Any]) -> None:
        """Detect cost anomalies using historical data"""
        try:
            # Get historical data from Qdrant
            historical_query = """
            SELECT daily_cost, hourly_cost, total_requests, average_response_time
            FROM SOPHIA_AI.AI_INSIGHTS.LAMBDA_LABS_COST_MONITORING
            WHERE timestamp > CURRENT_TIMESTAMP - INTERVAL '7 days'
            ORDER BY timestamp DESC
            """

            historical_data = await self.qdrant_service.execute_query(historical_query)

            if not historical_data or len(historical_data) < 10:
                return  # Not enough data for anomaly detection

            # Calculate statistics
            daily_costs = [row[0] for row in historical_data]
            hourly_costs = [row[1] for row in historical_data]

            daily_avg = sum(daily_costs) / len(daily_costs)
            daily_std = (
                sum((x - daily_avg) ** 2 for x in daily_costs) / len(daily_costs)
            ) ** 0.5

            hourly_avg = sum(hourly_costs) / len(hourly_costs)
            hourly_std = (
                sum((x - hourly_avg) ** 2 for x in hourly_costs) / len(hourly_costs)
            ) ** 0.5

            # Check for anomalies (2 standard deviations)
            current_daily = costs.get("daily_cost", 0.0)
            current_hourly = costs.get("hourly_cost", 0.0)

            if abs(current_daily - daily_avg) > 2 * daily_std:
                await self._create_alert(
                    AlertLevel.WARNING,
                    CostCategory.INFERENCE,
                    f"Daily cost anomaly detected: ${current_daily:.2f} vs avg ${daily_avg:.2f}",
                    current_daily,
                    daily_avg + 2 * daily_std,
                )

            if abs(current_hourly - hourly_avg) > 2 * hourly_std:
                await self._create_alert(
                    AlertLevel.WARNING,
                    CostCategory.INFERENCE,
                    f"Hourly cost anomaly detected: ${current_hourly:.2f} vs avg ${hourly_avg:.2f}",
                    current_hourly,
                    hourly_avg + 2 * hourly_std,
                )

        except Exception as e:
            logger.error(f"Failed to detect cost anomalies: {e}")

    async def get_cost_report(self) -> dict[str, Any]:
        """Generate comprehensive cost report"""
        try:
            # Get current costs
            current_costs = await self._get_current_costs()

            # Generate prediction
            prediction = await self._generate_cost_prediction()

            # Get model analytics
            model_analytics = {
                name: {
                    "total_cost": analytics.total_cost,
                    "request_count": analytics.request_count,
                    "avg_cost_per_request": analytics.avg_cost_per_request,
                    "avg_input_tokens": analytics.avg_input_tokens,
                    "avg_output_tokens": analytics.avg_output_tokens,
                    "cost_efficiency_score": analytics.cost_efficiency_score,
                    "usage_trend": analytics.usage_trend,
                }
                for name, analytics in self.model_analytics.items()
            }

            # Get active alerts
            active_alerts = [
                {
                    "id": alert.id,
                    "level": alert.level.value,
                    "category": alert.category.value,
                    "message": alert.message,
                    "current_value": alert.current_value,
                    "threshold": alert.threshold,
                    "timestamp": alert.timestamp.isoformat(),
                    "resolved": alert.resolved,
                }
                for alert in self.active_alerts
                if not alert.resolved
            ]

            return {
                "current_costs": current_costs,
                "prediction": {
                    "predicted_daily_cost": prediction.predicted_daily_cost,
                    "predicted_monthly_cost": prediction.predicted_monthly_cost,
                    "confidence": prediction.confidence,
                    "factors": prediction.factors,
                    "trend_direction": prediction.trend_direction,
                },
                "model_analytics": model_analytics,
                "active_alerts": active_alerts,
                "budget_status": {
                    "daily_budget": self.daily_budget,
                    "monthly_budget": self.monthly_budget,
                    "daily_utilization": (
                        current_costs.get("daily_cost", 0.0) / self.daily_budget
                    )
                    * 100,
                    "budget_remaining": current_costs.get("budget_remaining", 0.0),
                },
                "thresholds": self.thresholds,
                "monitoring_status": {
                    "active": self.monitoring_task is not None
                    and not self.monitoring_task.done(),
                    "interval": self.monitoring_interval,
                    "last_check": datetime.now().isoformat(),
                },
            }

        except Exception as e:
            logger.error(f"Failed to generate cost report: {e}")
            return {"error": str(e)}

    async def resolve_alert(self, alert_id: str) -> bool:
        """Resolve an active alert"""
        try:
            alert = next((a for a in self.active_alerts if a.id == alert_id), None)
            if alert:
                alert.resolved = True
                logger.info(f"Alert {alert_id} resolved")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to resolve alert {alert_id}: {e}")
            return False

    async def update_thresholds(self, new_thresholds: dict[str, float]) -> None:
        """Update alert thresholds"""
        try:
            self.thresholds.update(new_thresholds)
            logger.info(f"Thresholds updated: {new_thresholds}")
        except Exception as e:
            logger.error(f"Failed to update thresholds: {e}")

    async def cleanup_old_data(self, days_to_keep: int = 30) -> None:
        """Clean up old monitoring data"""
        try:
            # Remove old alerts
            cutoff_time = datetime.now() - timedelta(days=days_to_keep)
            self.active_alerts = [
                alert for alert in self.active_alerts if alert.timestamp > cutoff_time
            ]

            # Clean up Qdrant data
            cleanup_query = (
                """
            DELETE FROM SOPHIA_AI.AI_INSIGHTS.LAMBDA_LABS_COST_MONITORING
            WHERE timestamp < CURRENT_TIMESTAMP - INTERVAL '%s days'
            """
                % days_to_keep
            )

            await self.qdrant_service.execute_query(cleanup_query)

            logger.info(f"Cleaned up data older than {days_to_keep} days")

        except Exception as e:
            logger.error(f"Failed to cleanup old data: {e}")


# Global monitor instance
_cost_monitor: LambdaLabsCostMonitor | None = None


async def get_cost_monitor() -> LambdaLabsCostMonitor:
    """Get or create the global cost monitor instance"""
    global _cost_monitor
    if _cost_monitor is None:
        _cost_monitor = LambdaLabsCostMonitor()
    return _cost_monitor


# Convenience functions
async def start_cost_monitoring() -> None:
    """Start cost monitoring"""
    monitor = await get_cost_monitor()
    await monitor.start_monitoring()


async def stop_cost_monitoring() -> None:
    """Stop cost monitoring"""
    monitor = await get_cost_monitor()
    await monitor.stop_monitoring()


async def get_cost_report() -> dict[str, Any]:
    """Get comprehensive cost report"""
    monitor = await get_cost_monitor()
    return await monitor.get_cost_report()
