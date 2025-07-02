#!/usr/bin/env python3
"""
🎯 Group Health Monitoring for Sophia AI
=======================================

Enhanced monitoring with group-aware intelligence that extends
the existing monitoring infrastructure.

Business Value:
- Group-specific health checks with different intervals
- Business impact assessment for group failures
- Predictive failure detection using group patterns
- Performance optimization suggestions based on group characteristics
"""

import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from enum import Enum
from typing import Any

from backend.monitoring.mcp_metrics_collector import MCPMetricsCollector
from backend.services.mcp_orchestration_service import (
    MCPOrchestrationService,
    ServerStatus,
)

logger = logging.getLogger(__name__)


class GroupMonitoringInterval(Enum):
    """Monitoring intervals for different groups"""

    REAL_TIME = 30  # seconds
    HIGH_FREQUENCY = 60  # 1 minute
    STANDARD = 300  # 5 minutes
    LOW_FREQUENCY = 900  # 15 minutes


@dataclass
class GroupHealthMetrics:
    """Health metrics for a server group"""

    group_name: str
    timestamp: datetime
    health_percentage: float
    response_time_avg: float
    error_rate: float
    availability: float
    server_metrics: dict[str, dict[str, Any]]
    business_impact_score: float = 0.0
    predicted_failure_risk: float = 0.0
    optimization_opportunities: list[str] = field(default_factory=list)


@dataclass
class GroupRiskAssessment:
    """Risk assessment for a server group"""

    group_name: str
    risk_level: str  # low, medium, high, critical
    risk_factors: list[str]
    predicted_failure_window: str | None
    mitigation_actions: list[str]
    business_impact: str
    confidence_score: float


@dataclass
class OptimizationRecommendation:
    """Performance optimization recommendation"""

    group_name: str
    recommendation_type: str
    description: str
    expected_improvement: float
    implementation_effort: str  # low, medium, high
    priority: int  # 1-5, 1 being highest


class GroupHealthMonitor:
    """
    Enhanced monitoring with group-aware intelligence.
    Extends existing monitoring infrastructure with group-specific capabilities.
    """

    def __init__(
        self,
        orchestrator: MCPOrchestrationService,
        metrics_collector: MCPMetricsCollector | None = None,
    ):
        self.orchestrator = orchestrator
        self.metrics_collector = metrics_collector or MCPMetricsCollector(
            "group_health"
        )
        self.monitoring_intervals = self._initialize_monitoring_intervals()
        self.health_history: dict[str, list[GroupHealthMetrics]] = {}
        self.alert_thresholds = self._initialize_alert_thresholds()
        self.business_impact_weights = self._initialize_business_impact_weights()

    def _initialize_monitoring_intervals(self) -> dict[str, GroupMonitoringInterval]:
        """Initialize monitoring intervals for each group"""
        return {
            "core_ai": GroupMonitoringInterval.HIGH_FREQUENCY,
            "business_intelligence": GroupMonitoringInterval.HIGH_FREQUENCY,
            "data_infrastructure": GroupMonitoringInterval.STANDARD,
            "integrations": GroupMonitoringInterval.STANDARD,
            "quality_security": GroupMonitoringInterval.LOW_FREQUENCY,
        }

    def _initialize_alert_thresholds(self) -> dict[str, dict[str, float]]:
        """Initialize alert thresholds for each group"""
        return {
            "core_ai": {
                "health_percentage": 80.0,
                "response_time_ms": 200.0,
                "error_rate": 0.01,
                "availability": 0.99,
            },
            "business_intelligence": {
                "health_percentage": 75.0,
                "response_time_ms": 500.0,
                "error_rate": 0.02,
                "availability": 0.98,
            },
            "data_infrastructure": {
                "health_percentage": 70.0,
                "response_time_ms": 1000.0,
                "error_rate": 0.05,
                "availability": 0.95,
            },
            "integrations": {
                "health_percentage": 70.0,
                "response_time_ms": 800.0,
                "error_rate": 0.03,
                "availability": 0.97,
            },
            "quality_security": {
                "health_percentage": 60.0,
                "response_time_ms": 2000.0,
                "error_rate": 0.1,
                "availability": 0.90,
            },
        }

    def _initialize_business_impact_weights(self) -> dict[str, float]:
        """Initialize business impact weights for each group"""
        return {
            "core_ai": 1.0,  # Critical - AI functionality
            "business_intelligence": 0.9,  # Very High - Executive decisions
            "data_infrastructure": 0.8,  # High - Data operations
            "integrations": 0.7,  # Medium-High - External systems
            "quality_security": 0.5,  # Medium - Development support
        }

    async def monitor_group_health(self, group_name: str) -> GroupHealthMetrics:
        """
        Monitor health of a specific server group.
        Collects metrics from all servers in the group.
        """
        servers_in_group = self._get_servers_in_group(group_name)

        if not servers_in_group:
            logger.warning(f"No servers found in group {group_name}")
            return self._create_empty_metrics(group_name)

        # Collect metrics from each server
        server_metrics = {}
        total_response_time = 0.0
        total_errors = 0
        total_requests = 0
        healthy_servers = 0

        for server_name in servers_in_group:
            if server_name in self.orchestrator.servers:
                server = self.orchestrator.servers[server_name]

                # Get server metrics
                metrics = await self._collect_server_metrics(server_name, server)
                server_metrics[server_name] = metrics

                # Aggregate metrics
                if metrics["status"] == ServerStatus.HEALTHY.value:
                    healthy_servers += 1

                total_response_time += metrics.get("response_time_ms", 0)
                total_errors += metrics.get("error_count", 0)
                total_requests += metrics.get("request_count", 1)

        # Calculate group metrics
        health_percentage = (
            (healthy_servers / len(servers_in_group) * 100) if servers_in_group else 0
        )
        avg_response_time = (
            total_response_time / len(servers_in_group) if servers_in_group else 0
        )
        error_rate = total_errors / total_requests if total_requests > 0 else 0
        availability = 1 - error_rate

        # Calculate business impact score
        business_impact_score = self._calculate_business_impact(
            group_name, health_percentage, availability
        )

        # Predict failure risk
        predicted_failure_risk = await self._predict_failure_risk(
            group_name, health_percentage, error_rate
        )

        # Generate optimization opportunities
        optimization_opportunities = self._identify_optimization_opportunities(
            group_name, avg_response_time, error_rate
        )

        metrics = GroupHealthMetrics(
            group_name=group_name,
            timestamp=datetime.now(UTC),
            health_percentage=health_percentage,
            response_time_avg=avg_response_time,
            error_rate=error_rate,
            availability=availability,
            server_metrics=server_metrics,
            business_impact_score=business_impact_score,
            predicted_failure_risk=predicted_failure_risk,
            optimization_opportunities=optimization_opportunities,
        )

        # Store in history
        if group_name not in self.health_history:
            self.health_history[group_name] = []

        self.health_history[group_name].append(metrics)

        # Keep only last 24 hours of data
        cutoff_time = datetime.now(UTC) - timedelta(hours=24)
        self.health_history[group_name] = [
            m for m in self.health_history[group_name] if m.timestamp > cutoff_time
        ]

        # Record metrics
        if self.metrics_collector:
            self.metrics_collector.record_group_health_metrics(
                group_name,
                health_percentage,
                avg_response_time,
                error_rate,
                availability,
            )

        return metrics

    def _get_servers_in_group(self, group_name: str) -> list[str]:
        """Get list of servers in a group"""
        # This would be loaded from configuration
        group_mappings = {
            "core_ai": ["ai_memory", "sophia_ai_intelligence"],
            "business_intelligence": [
                "sophia_business_intelligence",
                "sophia_data_intelligence",
                "hubspot",
            ],
            "data_infrastructure": [
                "snowflake_admin",
                "snowflake_cli_enhanced",
                "postgres",
                "pulumi",
            ],
            "integrations": ["asana", "linear", "notion", "slack", "github"],
            "quality_security": ["codacy"],
        }

        return group_mappings.get(group_name, [])

    async def _collect_server_metrics(
        self, server_name: str, server: Any
    ) -> dict[str, Any]:
        """Collect metrics from a specific server"""
        return {
            "status": server.status.value,
            "response_time_ms": server.response_time_ms,
            "last_health_check": (
                server.last_health_check.isoformat()
                if server.last_health_check
                else None
            ),
            "error_count": 0,  # Would be tracked over time
            "request_count": 1,  # Would be tracked over time
            "capabilities": server.capabilities,
        }

    def _create_empty_metrics(self, group_name: str) -> GroupHealthMetrics:
        """Create empty metrics for a group with no servers"""
        return GroupHealthMetrics(
            group_name=group_name,
            timestamp=datetime.now(UTC),
            health_percentage=0.0,
            response_time_avg=0.0,
            error_rate=1.0,
            availability=0.0,
            server_metrics={},
            business_impact_score=self.business_impact_weights.get(group_name, 0.5),
            predicted_failure_risk=1.0,
            optimization_opportunities=["No servers available in group"],
        )

    def _calculate_business_impact(
        self, group_name: str, health_percentage: float, availability: float
    ) -> float:
        """Calculate business impact score for a group"""
        base_weight = self.business_impact_weights.get(group_name, 0.5)

        # Impact increases as health decreases
        health_impact = (100 - health_percentage) / 100

        # Availability has direct impact
        availability_impact = 1 - availability

        # Combined impact score (0-1 scale)
        impact_score = base_weight * (health_impact * 0.6 + availability_impact * 0.4)

        return min(impact_score, 1.0)

    async def _predict_failure_risk(
        self, group_name: str, current_health: float, error_rate: float
    ) -> float:
        """Predict failure risk based on trends and current metrics"""
        if (
            group_name not in self.health_history
            or len(self.health_history[group_name]) < 5
        ):
            # Not enough history, use current metrics
            if current_health < 50 or error_rate > 0.1:
                return 0.8  # High risk
            elif current_health < 70 or error_rate > 0.05:
                return 0.5  # Medium risk
            else:
                return 0.2  # Low risk

        # Analyze trends
        recent_metrics = self.health_history[group_name][-10:]
        health_trend = self._calculate_trend(
            [m.health_percentage for m in recent_metrics]
        )
        error_trend = self._calculate_trend([m.error_rate for m in recent_metrics])

        risk_score = 0.0

        # Declining health increases risk
        if health_trend < -5:  # Health declining by 5% or more
            risk_score += 0.3

        # Increasing errors increase risk
        if error_trend > 0.02:  # Error rate increasing
            risk_score += 0.3

        # Current state factors
        if current_health < 60:
            risk_score += 0.2
        if error_rate > 0.05:
            risk_score += 0.2

        return min(risk_score, 1.0)

    def _calculate_trend(self, values: list[float]) -> float:
        """Calculate trend from a list of values (positive = increasing)"""
        if len(values) < 2:
            return 0.0

        # Simple linear regression
        n = len(values)
        x_mean = (n - 1) / 2
        y_mean = sum(values) / n

        numerator = sum((i - x_mean) * (y - y_mean) for i, y in enumerate(values))
        denominator = sum((i - x_mean) ** 2 for i in range(n))

        if denominator == 0:
            return 0.0

        return numerator / denominator

    def _identify_optimization_opportunities(
        self, group_name: str, avg_response_time: float, error_rate: float
    ) -> list[str]:
        """Identify optimization opportunities for a group"""
        opportunities = []

        thresholds = self.alert_thresholds.get(group_name, {})

        # Response time optimization
        if avg_response_time > thresholds.get("response_time_ms", 1000):
            opportunities.append(
                f"Response time ({avg_response_time:.0f}ms) exceeds threshold. "
                "Consider caching or query optimization."
            )

        # Error rate optimization
        if error_rate > thresholds.get("error_rate", 0.05):
            opportunities.append(
                f"Error rate ({error_rate:.2%}) is high. "
                "Review error logs and implement retry logic."
            )

        # Group-specific recommendations
        if group_name == "data_infrastructure" and avg_response_time > 500:
            opportunities.append(
                "Consider implementing connection pooling for database operations."
            )

        if group_name == "integrations" and error_rate > 0.02:
            opportunities.append(
                "External API errors detected. Implement circuit breakers."
            )

        if not opportunities:
            opportunities.append("Group performing optimally.")

        return opportunities

    async def predict_group_failures(self) -> list[GroupRiskAssessment]:
        """
        Predict potential group failures based on trends and patterns.
        Returns risk assessments for groups at risk.
        """
        risk_assessments = []

        for group_name, metrics_history in self.health_history.items():
            if len(metrics_history) < 5:
                continue  # Not enough data

            # Get recent metrics
            recent_metrics = metrics_history[-10:]
            current_metrics = recent_metrics[-1]

            # Analyze trends
            health_trend = self._calculate_trend(
                [m.health_percentage for m in recent_metrics]
            )
            error_trend = self._calculate_trend([m.error_rate for m in recent_metrics])
            response_trend = self._calculate_trend(
                [m.response_time_avg for m in recent_metrics]
            )

            # Determine risk level
            risk_factors = []
            risk_score = 0.0

            if health_trend < -10:
                risk_factors.append("Rapidly declining health")
                risk_score += 0.4
            elif health_trend < -5:
                risk_factors.append("Declining health trend")
                risk_score += 0.2

            if current_metrics.health_percentage < 50:
                risk_factors.append("Critical health level")
                risk_score += 0.3
            elif current_metrics.health_percentage < 70:
                risk_factors.append("Low health level")
                risk_score += 0.1

            if error_trend > 0.05:
                risk_factors.append("Increasing error rate")
                risk_score += 0.2

            if response_trend > 100:
                risk_factors.append("Degrading performance")
                risk_score += 0.1

            if risk_score > 0.2:  # Threshold for creating risk assessment
                # Determine risk level
                if risk_score > 0.7:
                    risk_level = "critical"
                    failure_window = "1-2 hours"
                elif risk_score > 0.5:
                    risk_level = "high"
                    failure_window = "2-4 hours"
                elif risk_score > 0.3:
                    risk_level = "medium"
                    failure_window = "4-8 hours"
                else:
                    risk_level = "low"
                    failure_window = "8-24 hours"

                # Generate mitigation actions
                mitigation_actions = self._generate_mitigation_actions(
                    group_name, risk_factors, current_metrics
                )

                # Assess business impact
                business_impact = self._assess_business_impact(group_name, risk_level)

                assessment = GroupRiskAssessment(
                    group_name=group_name,
                    risk_level=risk_level,
                    risk_factors=risk_factors,
                    predicted_failure_window=failure_window,
                    mitigation_actions=mitigation_actions,
                    business_impact=business_impact,
                    confidence_score=min(
                        len(recent_metrics) / 20, 1.0
                    ),  # More data = higher confidence
                )

                risk_assessments.append(assessment)

        # Sort by risk level (critical first)
        risk_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        risk_assessments.sort(key=lambda x: risk_order.get(x.risk_level, 4))

        return risk_assessments

    def _generate_mitigation_actions(
        self,
        group_name: str,
        risk_factors: list[str],
        current_metrics: GroupHealthMetrics,
    ) -> list[str]:
        """Generate mitigation actions based on risk factors"""
        actions = []

        if "Critical health level" in risk_factors:
            actions.append(
                f"Immediately investigate and restart failed servers in {group_name}"
            )
            actions.append("Enable emergency fallback procedures")

        if "Rapidly declining health" in risk_factors:
            actions.append("Review recent changes and rollback if necessary")
            actions.append("Increase monitoring frequency")

        if "Increasing error rate" in risk_factors:
            actions.append("Review error logs and identify root causes")
            actions.append("Implement additional error handling and retry logic")

        if "Degrading performance" in risk_factors:
            actions.append("Analyze performance bottlenecks")
            actions.append("Scale resources or optimize queries")

        # Group-specific actions
        if group_name == "core_ai":
            actions.append("Ensure AI model resources are adequate")
        elif group_name == "business_intelligence":
            actions.append("Verify data pipeline integrity")
        elif group_name == "integrations":
            actions.append("Check external API status and rate limits")

        return actions

    def _assess_business_impact(self, group_name: str, risk_level: str) -> str:
        """Assess business impact of potential group failure"""
        impact_weight = self.business_impact_weights.get(group_name, 0.5)

        if impact_weight > 0.8:
            if risk_level in ["critical", "high"]:
                return "Severe business impact - Core functionality at risk"
            else:
                return "Moderate business impact - Performance degradation expected"
        elif impact_weight > 0.6:
            if risk_level in ["critical", "high"]:
                return "High business impact - Key features may be unavailable"
            else:
                return "Low to moderate business impact"
        else:
            return "Limited business impact - Non-critical features affected"

    async def optimize_group_performance(self) -> list[OptimizationRecommendation]:
        """
        Generate performance optimization recommendations for groups.
        Analyzes current performance and suggests improvements.
        """
        recommendations = []

        for group_name in self.monitoring_intervals.keys():
            # Get current metrics
            current_metrics = await self.monitor_group_health(group_name)

            # Analyze performance gaps
            thresholds = self.alert_thresholds.get(group_name, {})

            # Response time optimization
            if (
                current_metrics.response_time_avg
                > thresholds.get("response_time_ms", 1000) * 0.8
            ):
                improvement = (
                    (current_metrics.response_time_avg - thresholds["response_time_ms"])
                    / current_metrics.response_time_avg
                    * 100
                )

                recommendations.append(
                    OptimizationRecommendation(
                        group_name=group_name,
                        recommendation_type="performance",
                        description=f"Optimize {group_name} response time through caching and query optimization",
                        expected_improvement=improvement,
                        implementation_effort="medium",
                        priority=2 if improvement > 20 else 3,
                    )
                )

            # Error rate optimization
            if current_metrics.error_rate > thresholds.get("error_rate", 0.05) * 0.5:
                recommendations.append(
                    OptimizationRecommendation(
                        group_name=group_name,
                        recommendation_type="reliability",
                        description=f"Implement robust error handling and retry mechanisms for {group_name}",
                        expected_improvement=50.0,  # Target 50% error reduction
                        implementation_effort="low",
                        priority=1 if current_metrics.error_rate > 0.05 else 2,
                    )
                )

            # Availability optimization
            if current_metrics.availability < thresholds.get("availability", 0.95):
                recommendations.append(
                    OptimizationRecommendation(
                        group_name=group_name,
                        recommendation_type="availability",
                        description=f"Implement redundancy and failover for {group_name} servers",
                        expected_improvement=(0.99 - current_metrics.availability)
                        * 100,
                        implementation_effort="high",
                        priority=1 if current_metrics.availability < 0.9 else 2,
                    )
                )

            # Group-specific optimizations
            if (
                group_name == "data_infrastructure"
                and len(current_metrics.server_metrics) > 3
            ):
                recommendations.append(
                    OptimizationRecommendation(
                        group_name=group_name,
                        recommendation_type="architecture",
                        description="Implement connection pooling and query result caching",
                        expected_improvement=30.0,
                        implementation_effort="medium",
                        priority=3,
                    )
                )

            if group_name == "integrations" and current_metrics.response_time_avg > 500:
                recommendations.append(
                    OptimizationRecommendation(
                        group_name=group_name,
                        recommendation_type="integration",
                        description="Implement asynchronous processing for external API calls",
                        expected_improvement=40.0,
                        implementation_effort="medium",
                        priority=2,
                    )
                )

        # Sort by priority
        recommendations.sort(key=lambda x: x.priority)

        return recommendations

    async def get_monitoring_dashboard(self) -> dict[str, Any]:
        """
        Get comprehensive monitoring dashboard data.
        Provides overview of all groups with key metrics.
        """
        dashboard = {
            "timestamp": datetime.now(UTC).isoformat(),
            "groups": {},
            "overall_health": "healthy",
            "active_alerts": [],
            "risk_assessments": [],
            "optimization_opportunities": [],
        }

        total_health = 0.0
        group_count = 0

        # Collect metrics for each group
        for group_name in self.monitoring_intervals.keys():
            metrics = await self.monitor_group_health(group_name)

            dashboard["groups"][group_name] = {
                "health_percentage": metrics.health_percentage,
                "response_time_avg": metrics.response_time_avg,
                "error_rate": metrics.error_rate,
                "availability": metrics.availability,
                "business_impact_score": metrics.business_impact_score,
                "server_count": len(metrics.server_metrics),
                "optimization_opportunities": metrics.optimization_opportunities,
            }

            total_health += metrics.health_percentage
            group_count += 1

            # Check for alerts
            thresholds = self.alert_thresholds.get(group_name, {})
            if metrics.health_percentage < thresholds.get("health_percentage", 70):
                dashboard["active_alerts"].append(
                    {
                        "group": group_name,
                        "type": "health",
                        "severity": (
                            "critical" if metrics.health_percentage < 50 else "warning"
                        ),
                        "message": f"{group_name} health at {metrics.health_percentage:.1f}%",
                    }
                )

        # Calculate overall health
        avg_health = total_health / group_count if group_count > 0 else 0
        if avg_health >= 80:
            dashboard["overall_health"] = "healthy"
        elif avg_health >= 60:
            dashboard["overall_health"] = "degraded"
        else:
            dashboard["overall_health"] = "critical"

        # Get risk assessments
        risk_assessments = await self.predict_group_failures()
        dashboard["risk_assessments"] = [
            {
                "group": ra.group_name,
                "risk_level": ra.risk_level,
                "predicted_failure_window": ra.predicted_failure_window,
                "business_impact": ra.business_impact,
            }
            for ra in risk_assessments[:5]  # Top 5 risks
        ]

        # Get optimization opportunities
        optimizations = await self.optimize_group_performance()
        dashboard["optimization_opportunities"] = [
            {
                "group": opt.group_name,
                "type": opt.recommendation_type,
                "description": opt.description,
                "expected_improvement": f"{opt.expected_improvement:.0f}%",
            }
            for opt in optimizations[:5]  # Top 5 opportunities
        ]

        return dashboard
