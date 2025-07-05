#!/usr/bin/env python3
"""
Enhanced Monitoring Integration for Sophia AI
Unifies existing monitoring systems into a cohesive, comprehensive monitoring platform

Building on existing systems:
- backend.core.integrated_performance_monitoring
- backend.core.self_optimization
- backend.core.performance_monitor
- backend.monitoring.prometheus_config
- scripts.performance_optimizer
- backend.agents.infrastructure.sophia_infrastructure_agent

Features:
- Unified monitoring dashboard
- Cross-system performance correlation
- Intelligent alerting with context
- Performance optimization recommendations
- Health status aggregation
- Real-time monitoring with minimal overhead
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Any

import psutil

# Import existing monitoring systems
from backend.core.integrated_performance_monitoring import (
    PerformanceMonitoringIntegration,
)
from backend.core.self_optimization import SophiaSelfOptimizer
from backend.monitoring.prometheus_config import SophiaMetrics

logger = logging.getLogger(__name__)


class EnhancedSophiaMonitoring:
    """
    Enhanced monitoring that builds on existing performance tracking systems
    Provides unified interface and intelligent correlation without duplication
    """

    def __init__(self):
        # Initialize existing monitoring systems
        self.performance_integration = PerformanceMonitoringIntegration()
        self.self_optimizer = SophiaSelfOptimizer()
        self.prometheus_metrics = SophiaMetrics()

        # Enhanced features
        self.monitoring_dashboard = SophiaMonitoringDashboard()
        self.intelligent_correlator = PerformanceCorrelator()
        self.unified_alerting = UnifiedAlertingSystem()

        # State tracking
        self.last_health_check = None
        self.health_trends = []
        self.performance_baseline = {}
        self.alert_history = []

        # Configuration
        self.config = {
            "health_check_interval": 60,  # 1 minute
            "trend_analysis_window": 3600,  # 1 hour
            "baseline_calculation_period": 86400,  # 24 hours
            "alert_cooldown": 300,  # 5 minutes
            "correlation_threshold": 0.7,
        }

    async def initialize(self):
        """Initialize enhanced monitoring system"""
        try:
            logger.info("🔄 Initializing Enhanced Sophia Monitoring...")

            # Initialize existing systems
            await self.performance_integration.initialize()
            await self.self_optimizer.start_optimization_loop()

            # Initialize enhanced features
            await self.monitoring_dashboard.initialize()
            await self.intelligent_correlator.initialize()
            await self.unified_alerting.initialize()

            # Start monitoring loops
            asyncio.create_task(self._health_monitoring_loop())
            asyncio.create_task(self._trend_analysis_loop())
            asyncio.create_task(self._correlation_analysis_loop())

            logger.info("✅ Enhanced Sophia Monitoring initialized successfully")

        except Exception as e:
            logger.error(f"❌ Failed to initialize Enhanced Monitoring: {e}")
            raise

    async def get_unified_health_status(self) -> dict[str, Any]:
        """Get comprehensive health status from all monitoring systems"""
        try:
            # Collect from existing systems
            performance_status = await self.performance_integration.get_system_health()
            optimization_status = await self.self_optimizer.get_optimization_status()

            # Add system metrics
            system_metrics = await self._collect_system_metrics()

            # Correlate and analyze
            correlated_insights = (
                await self.intelligent_correlator.analyze_performance_patterns(
                    performance_status, optimization_status, system_metrics
                )
            )

            # Generate unified status
            unified_status = {
                "timestamp": datetime.now().isoformat(),
                "overall_health": self._calculate_overall_health(
                    performance_status, optimization_status, system_metrics
                ),
                "component_health": {
                    "performance_monitoring": performance_status,
                    "self_optimization": optimization_status,
                    "system_metrics": system_metrics,
                },
                "insights": correlated_insights,
                "recommendations": await self._generate_actionable_recommendations(
                    performance_status, optimization_status, correlated_insights
                ),
                "trends": self._get_recent_trends(),
                "alerts": await self.unified_alerting.get_active_alerts(),
            }

            # Store for trend analysis
            self.health_trends.append(
                {
                    "timestamp": datetime.now(),
                    "health_score": unified_status["overall_health"]["score"],
                    "key_metrics": unified_status["overall_health"]["key_metrics"],
                }
            )

            # Trim old trends
            cutoff_time = datetime.now() - timedelta(
                seconds=self.config["trend_analysis_window"]
            )
            self.health_trends = [
                trend
                for trend in self.health_trends
                if trend["timestamp"] > cutoff_time
            ]

            self.last_health_check = unified_status
            return unified_status

        except Exception as e:
            logger.error(f"Error getting unified health status: {e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "overall_health": {"score": 0, "status": "error"},
            }

    async def _collect_system_metrics(self) -> dict[str, Any]:
        """Collect system-level metrics"""
        try:
            # CPU and Memory
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("/")

            # Network I/O
            network = psutil.net_io_counters()

            # Process information
            process_count = len(psutil.pids())

            return {
                "cpu": {"percent": cpu_percent, "count": psutil.cpu_count()},
                "memory": {
                    "percent": memory.percent,
                    "total": memory.total,
                    "available": memory.available,
                    "used": memory.used,
                },
                "disk": {
                    "percent": disk.percent,
                    "total": disk.total,
                    "used": disk.used,
                    "free": disk.free,
                },
                "network": {
                    "bytes_sent": network.bytes_sent,
                    "bytes_recv": network.bytes_recv,
                    "packets_sent": network.packets_sent,
                    "packets_recv": network.packets_recv,
                },
                "processes": {"count": process_count},
            }

        except Exception as e:
            logger.warning(f"Error collecting system metrics: {e}")
            return {"error": str(e)}

    def _calculate_overall_health(
        self, performance_status, optimization_status, system_metrics
    ) -> dict[str, Any]:
        """Calculate overall system health score"""
        try:
            scores = []
            details = {}

            # Performance score (40% weight)
            if performance_status.get("overall_health_score"):
                perf_score = performance_status["overall_health_score"]
                scores.append(("performance", perf_score, 0.4))
                details["performance"] = perf_score

            # Optimization score (20% weight)
            if optimization_status.get("is_running"):
                opt_score = 100 if optimization_status["is_running"] else 50
                scores.append(("optimization", opt_score, 0.2))
                details["optimization"] = opt_score

            # System metrics score (40% weight)
            if "error" not in system_metrics:
                cpu_score = max(0, 100 - system_metrics["cpu"]["percent"])
                memory_score = max(0, 100 - system_metrics["memory"]["percent"])
                disk_score = max(0, 100 - system_metrics["disk"]["percent"])

                system_score = (cpu_score + memory_score + disk_score) / 3
                scores.append(("system", system_score, 0.4))
                details["system"] = system_score

            # Calculate weighted average
            if scores:
                weighted_sum = sum(score * weight for _, score, weight in scores)
                total_weight = sum(weight for _, _, weight in scores)
                overall_score = weighted_sum / total_weight if total_weight > 0 else 0
            else:
                overall_score = 0

            # Determine status
            if overall_score >= 90:
                status = "excellent"
            elif overall_score >= 75:
                status = "good"
            elif overall_score >= 60:
                status = "fair"
            elif overall_score >= 40:
                status = "poor"
            else:
                status = "critical"

            return {
                "score": round(overall_score, 1),
                "status": status,
                "key_metrics": details,
                "components_evaluated": len(scores),
            }

        except Exception as e:
            logger.error(f"Error calculating overall health: {e}")
            return {"score": 0, "status": "error", "error": str(e)}

    async def _generate_actionable_recommendations(
        self, performance_status, optimization_status, insights
    ) -> list[str]:
        """Generate actionable recommendations based on current status"""
        recommendations = []

        try:
            # Performance recommendations
            if performance_status.get("overall_health_score", 100) < 80:
                recommendations.append("🔧 Consider restarting underperforming services")
                recommendations.append(
                    "📊 Review performance metrics for optimization opportunities"
                )

            # Optimization recommendations
            if not optimization_status.get("is_running", False):
                recommendations.append("🚀 Start the self-optimization engine")

            # System resource recommendations
            system_metrics = await self._collect_system_metrics()
            if "error" not in system_metrics:
                if system_metrics["cpu"]["percent"] > 80:
                    recommendations.append(
                        "⚡ High CPU usage detected - consider scaling resources"
                    )

                if system_metrics["memory"]["percent"] > 85:
                    recommendations.append(
                        "💾 High memory usage detected - review memory leaks"
                    )

                if system_metrics["disk"]["percent"] > 90:
                    recommendations.append(
                        "💽 Disk space running low - clean up logs and temporary files"
                    )

            # Insights-based recommendations
            if insights.get("patterns"):
                for pattern in insights["patterns"]:
                    if pattern.get("recommendation"):
                        recommendations.append(f"🔍 {pattern['recommendation']}")

            if not recommendations:
                recommendations.append(
                    "✅ System operating optimally - no immediate actions required"
                )

            return recommendations

        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return ["❌ Unable to generate recommendations due to system error"]

    def _get_recent_trends(self) -> dict[str, Any]:
        """Get recent performance trends"""
        if len(self.health_trends) < 2:
            return {"status": "insufficient_data"}

        try:
            recent_scores = [
                trend["health_score"] for trend in self.health_trends[-10:]
            ]

            # Calculate trend
            if len(recent_scores) >= 2:
                trend_direction = (
                    "improving" if recent_scores[-1] > recent_scores[0] else "declining"
                )
                trend_magnitude = abs(recent_scores[-1] - recent_scores[0])
            else:
                trend_direction = "stable"
                trend_magnitude = 0

            return {
                "direction": trend_direction,
                "magnitude": round(trend_magnitude, 1),
                "current_score": recent_scores[-1],
                "average_score": round(sum(recent_scores) / len(recent_scores), 1),
                "data_points": len(recent_scores),
            }

        except Exception as e:
            logger.error(f"Error calculating trends: {e}")
            return {"status": "error", "error": str(e)}

    async def _health_monitoring_loop(self):
        """Continuous health monitoring loop"""
        while True:
            try:
                await self.get_unified_health_status()
                await asyncio.sleep(self.config["health_check_interval"])
            except Exception as e:
                logger.error(f"Error in health monitoring loop: {e}")
                await asyncio.sleep(60)  # Wait 1 minute on error

    async def _trend_analysis_loop(self):
        """Continuous trend analysis loop"""
        while True:
            try:
                await self._analyze_performance_trends()
                await asyncio.sleep(
                    self.config["trend_analysis_window"] // 4
                )  # 15 minutes
            except Exception as e:
                logger.error(f"Error in trend analysis loop: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes on error

    async def _correlation_analysis_loop(self):
        """Continuous correlation analysis loop"""
        while True:
            try:
                await self.intelligent_correlator.analyze_system_correlations()
                await asyncio.sleep(300)  # 5 minutes
            except Exception as e:
                logger.error(f"Error in correlation analysis loop: {e}")
                await asyncio.sleep(300)

    async def _analyze_performance_trends(self):
        """Analyze performance trends and detect anomalies"""
        if len(self.health_trends) < 10:
            return  # Need more data

        try:
            # Calculate baseline if needed
            if not self.performance_baseline:
                await self._calculate_performance_baseline()

            # Detect anomalies
            recent_scores = [
                trend["health_score"] for trend in self.health_trends[-10:]
            ]
            current_score = recent_scores[-1]
            baseline_score = self.performance_baseline.get(
                "average_score", current_score
            )

            # Check for significant deviation
            if abs(current_score - baseline_score) > 20:
                await self.unified_alerting.trigger_alert(
                    {
                        "type": "performance_anomaly",
                        "severity": "warning",
                        "message": f"Performance deviation detected: {current_score:.1f} vs baseline {baseline_score:.1f}",
                        "current_score": current_score,
                        "baseline_score": baseline_score,
                    }
                )

        except Exception as e:
            logger.error(f"Error analyzing performance trends: {e}")

    async def _calculate_performance_baseline(self):
        """Calculate performance baseline from historical data"""
        if len(self.health_trends) < 50:  # Need sufficient data
            return

        try:
            # Use last 24 hours of data
            cutoff_time = datetime.now() - timedelta(
                seconds=self.config["baseline_calculation_period"]
            )
            baseline_data = [
                trend
                for trend in self.health_trends
                if trend["timestamp"] > cutoff_time
            ]

            if baseline_data:
                scores = [trend["health_score"] for trend in baseline_data]
                self.performance_baseline = {
                    "average_score": sum(scores) / len(scores),
                    "min_score": min(scores),
                    "max_score": max(scores),
                    "data_points": len(scores),
                    "calculated_at": datetime.now().isoformat(),
                }

                logger.info(
                    f"Updated performance baseline: {self.performance_baseline['average_score']:.1f}"
                )

        except Exception as e:
            logger.error(f"Error calculating performance baseline: {e}")

    async def get_monitoring_api_data(self) -> dict[str, Any]:
        """Get formatted data for monitoring API endpoints"""
        try:
            unified_status = await self.get_unified_health_status()

            return {
                "status": "operational",
                "timestamp": datetime.now().isoformat(),
                "health": unified_status["overall_health"],
                "components": {
                    name: {
                        "status": status.get("status", "unknown"),
                        "score": status.get("health_score", 0),
                    }
                    for name, status in unified_status["component_health"].items()
                },
                "metrics": {
                    "response_time": await self._get_average_response_time(),
                    "error_rate": await self._get_current_error_rate(),
                    "uptime": await self._get_system_uptime(),
                    "active_alerts": len(unified_status.get("alerts", [])),
                },
                "trends": unified_status.get("trends", {}),
                "recommendations": unified_status.get("recommendations", [])[
                    :3
                ],  # Top 3
            }

        except Exception as e:
            logger.error(f"Error getting monitoring API data: {e}")
            return {
                "status": "error",
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
            }

    async def _get_average_response_time(self) -> float:
        """Get current average response time across services"""
        try:
            # Get from performance monitoring
            metrics = await self.performance_integration.get_performance_dashboard()
            return metrics.get("average_response_time", 0.0)
        except Exception:
            return 0.0

    async def _get_current_error_rate(self) -> float:
        """Get current error rate across services"""
        try:
            metrics = await self.performance_integration.get_performance_dashboard()
            return metrics.get("error_rate", 0.0)
        except Exception:
            return 0.0

    async def _get_system_uptime(self) -> float:
        """Get system uptime in seconds"""
        try:
            return time.time() - psutil.boot_time()
        except Exception:
            return 0.0


class SophiaMonitoringDashboard:
    """Enhanced monitoring dashboard"""

    def __init__(self):
        self.dashboard_data = {}
        self.update_interval = 60  # 1 minute

    async def initialize(self):
        """Initialize dashboard"""
        logger.info("📊 Monitoring dashboard initialized")

    async def get_dashboard_data(self) -> dict[str, Any]:
        """Get formatted dashboard data"""
        return {"timestamp": datetime.now().isoformat(), "status": "operational"}


class PerformanceCorrelator:
    """Intelligent performance correlation analysis"""

    def __init__(self):
        self.correlation_data = {}

    async def initialize(self):
        """Initialize correlator"""
        logger.info("🔗 Performance correlator initialized")

    async def analyze_performance_patterns(
        self, performance_status, optimization_status, system_metrics
    ) -> dict[str, Any]:
        """Analyze patterns across monitoring systems"""
        return {"patterns": [], "correlations": {}, "insights": []}

    async def analyze_system_correlations(self):
        """Analyze correlations between system components"""
        pass


class UnifiedAlertingSystem:
    """Unified alerting across all monitoring systems"""

    def __init__(self):
        self.active_alerts = []
        self.alert_history = []

    async def initialize(self):
        """Initialize alerting system"""
        logger.info("🚨 Unified alerting system initialized")

    async def get_active_alerts(self) -> list[dict[str, Any]]:
        """Get currently active alerts"""
        return self.active_alerts

    async def trigger_alert(self, alert_data: dict[str, Any]):
        """Trigger a new alert"""
        alert = {
            "timestamp": datetime.now().isoformat(),
            "id": f"alert_{int(time.time())}",
            **alert_data,
        }

        self.active_alerts.append(alert)
        self.alert_history.append(alert)

        logger.warning(f"🚨 Alert triggered: {alert['message']}")


# Global instance for easy access
enhanced_monitoring = EnhancedSophiaMonitoring()


async def initialize_enhanced_monitoring():
    """Initialize the global enhanced monitoring system"""
    await enhanced_monitoring.initialize()
    return True


async def get_unified_health_status():
    """Get unified health status"""
    return await enhanced_monitoring.get_unified_health_status()


async def get_monitoring_dashboard_data():
    """Get monitoring dashboard data"""
    return await enhanced_monitoring.get_monitoring_api_data()
