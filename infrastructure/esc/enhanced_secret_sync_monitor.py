#!/usr/bin/env python3
"""
Enhanced Secret Synchronization Monitor for Sophia AI
Building on existing github_sync_bidirectional.py with advanced monitoring, alerting, and health checks

Features:
- Real-time sync health monitoring
- Automated drift detection
- Performance metrics tracking
- Alert generation for sync failures
- Continuous validation loop
- Health dashboard integration
- Proactive maintenance recommendations

Usage:
    python infrastructure/esc/enhanced_secret_sync_monitor.py --monitor
    python infrastructure/esc/enhanced_secret_sync_monitor.py --health-check
    python infrastructure/esc/enhanced_secret_sync_monitor.py --auto-heal
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import aiohttp
import yaml

# Import existing sync manager
from github_sync_bidirectional import GitHubESCSyncManager

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class EnhancedSecretSyncMonitor:
    """
    Enhanced monitoring system for GitHub ↔ Pulumi ESC secret synchronization
    Builds on existing infrastructure with advanced monitoring capabilities
    """

    def __init__(self, config_file: str = "infrastructure/esc/monitor_config.yaml"):
        self.config = self._load_config(config_file)
        self.sync_manager = GitHubESCSyncManager(
            org=self.config["github"]["org"],
            github_token=self.config["github"]["token"],
            pulumi_org=self.config["pulumi"]["org"],
            environment=self.config["pulumi"]["environment"],
        )

        # Monitoring state
        self.health_history = []
        self.performance_metrics = {
            "sync_duration_history": [],
            "validation_duration_history": [],
            "error_count": 0,
            "success_count": 0,
            "last_sync_time": None,
            "average_sync_duration": 0.0,
        }

        # Alert thresholds
        self.alert_thresholds = {
            "sync_health_percentage": 85.0,
            "max_sync_duration": 300.0,  # 5 minutes
            "max_drift_percentage": 10.0,
            "max_consecutive_failures": 3,
        }

        self.consecutive_failures = 0
        self.is_monitoring = False

    def _load_config(self, config_file: str) -> dict[str, Any]:
        """Load monitoring configuration"""
        try:
            if Path(config_file).exists():
                with open(config_file) as f:
                    return yaml.safe_load(f)
            else:
                logger.warning(f"Config file {config_file} not found, using defaults")
                return self._get_default_config()
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return self._get_default_config()

    def _get_default_config(self) -> dict[str, Any]:
        """Get default configuration"""
        import os

        return {
            "github": {"org": "ai-cherry", "token": os.getenv("GITHUB_TOKEN", "")},
            "pulumi": {
                "org": "scoobyjava-org",
                "environment": "default/sophia-ai-production",
            },
            "monitoring": {
                "check_interval": 300,  # 5 minutes
                "health_retention_days": 30,
                "enable_alerts": True,
                "enable_auto_healing": False,
            },
            "alerts": {
                "webhook_url": "",
                "slack_channel": "#sophia-ai-alerts",
                "email_recipients": [],
            },
        }

    async def start_continuous_monitoring(self):
        """Start continuous monitoring loop"""
        logger.info("🔄 Starting enhanced secret sync monitoring...")
        self.is_monitoring = True

        while self.is_monitoring:
            try:
                await self._perform_health_check()
                await self._update_performance_metrics()
                await self._check_alert_conditions()

                # Wait for next check interval
                await asyncio.sleep(self.config["monitoring"]["check_interval"])

            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(60)  # Wait 1 minute on error

    async def stop_monitoring(self):
        """Stop monitoring loop"""
        logger.info("🛑 Stopping secret sync monitoring...")
        self.is_monitoring = False

    async def _perform_health_check(self) -> dict[str, Any]:
        """Perform comprehensive health check"""
        start_time = time.time()
        logger.info("🏥 Performing secret sync health check...")

        try:
            # Use existing validation from sync manager
            validation_result = self.sync_manager.validate_sync_status()

            # Enhance with additional metrics
            health_check = {
                "timestamp": datetime.now().isoformat(),
                "sync_health": validation_result,
                "performance": {
                    "validation_duration": time.time() - start_time,
                    "github_api_latency": await self._measure_github_api_latency(),
                    "pulumi_esc_latency": await self._measure_pulumi_esc_latency(),
                },
                "connectivity": {
                    "github_accessible": await self._test_github_connectivity(),
                    "pulumi_accessible": await self._test_pulumi_connectivity(),
                },
                "recommendations": self._generate_health_recommendations(
                    validation_result
                ),
            }

            # Store in history
            self.health_history.append(health_check)
            self._trim_health_history()

            # Update success counter
            self.performance_metrics["success_count"] += 1
            self.consecutive_failures = 0

            logger.info(
                f"✅ Health check completed in {health_check['performance']['validation_duration']:.2f}s"
            )
            return health_check

        except Exception as e:
            logger.error(f"❌ Health check failed: {e}")
            self.performance_metrics["error_count"] += 1
            self.consecutive_failures += 1

            error_health_check = {
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "consecutive_failures": self.consecutive_failures,
            }
            self.health_history.append(error_health_check)
            return error_health_check

    async def _measure_github_api_latency(self) -> float:
        """Measure GitHub API response latency"""
        try:
            start_time = time.time()
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"token {self.config['github']['token']}",
                    "Accept": "application/vnd.github+json",
                }
                async with session.get(
                    f"https://api.github.com/orgs/{self.config['github']['org']}",
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as response:
                    await response.read()
                    return time.time() - start_time
        except Exception as e:
            logger.warning(f"Failed to measure GitHub API latency: {e}")
            return -1.0

    async def _measure_pulumi_esc_latency(self) -> float:
        """Measure Pulumi ESC response latency"""
        try:
            start_time = time.time()
            # Use Pulumi CLI to test connectivity

            result = await asyncio.create_subprocess_exec(
                "pulumi",
                "whoami",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            await result.communicate()
            return time.time() - start_time
        except Exception as e:
            logger.warning(f"Failed to measure Pulumi ESC latency: {e}")
            return -1.0

    async def _test_github_connectivity(self) -> bool:
        """Test GitHub API connectivity"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"token {self.config['github']['token']}",
                    "Accept": "application/vnd.github+json",
                }
                async with session.get(
                    f"https://api.github.com/orgs/{self.config['github']['org']}",
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as response:
                    return response.status == 200
        except Exception:
            return False

    async def _test_pulumi_connectivity(self) -> bool:
        """Test Pulumi ESC connectivity"""
        try:
            result = await asyncio.create_subprocess_exec(
                "pulumi",
                "whoami",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            returncode = await result.wait()
            return returncode == 0
        except Exception:
            return False

    def _generate_health_recommendations(
        self, validation_result: dict[str, Any]
    ) -> list[str]:
        """Generate actionable health recommendations"""
        recommendations = []

        if "sync_health" in validation_result:
            sync_health = validation_result["sync_health"]

            if (
                sync_health.get("percentage", 0)
                < self.alert_thresholds["sync_health_percentage"]
            ):
                recommendations.append(
                    f"🔧 Sync health at {sync_health.get('percentage', 0):.1f}% - run sync operation"
                )

            if validation_result.get("esc_values", {}).get("missing"):
                missing_count = len(validation_result["esc_values"]["missing"])
                recommendations.append(
                    f"📋 {missing_count} ESC values missing - execute GitHub→ESC sync"
                )

            if validation_result.get("github_secrets", {}).get("not_mapped"):
                unmapped_count = len(validation_result["github_secrets"]["not_mapped"])
                recommendations.append(
                    f"🗺️ {unmapped_count} GitHub secrets not mapped - update mapping configuration"
                )

        # Performance recommendations
        avg_duration = self.performance_metrics.get("average_sync_duration", 0)
        if avg_duration > self.alert_thresholds["max_sync_duration"]:
            recommendations.append(
                f"⚡ Average sync duration {avg_duration:.1f}s exceeds threshold - investigate performance"
            )

        if not recommendations:
            recommendations.append("✅ All systems operating optimally")

        return recommendations

    async def _update_performance_metrics(self):
        """Update performance tracking metrics"""
        if len(self.performance_metrics["sync_duration_history"]) > 0:
            self.performance_metrics["average_sync_duration"] = sum(
                self.performance_metrics["sync_duration_history"]
            ) / len(self.performance_metrics["sync_duration_history"])

        # Trim old metrics
        max_history = 100
        if len(self.performance_metrics["sync_duration_history"]) > max_history:
            self.performance_metrics[
                "sync_duration_history"
            ] = self.performance_metrics["sync_duration_history"][-max_history:]

    async def _check_alert_conditions(self):
        """Check for alert conditions and trigger notifications"""
        if not self.config["monitoring"]["enable_alerts"]:
            return

        alerts = []

        # Check consecutive failures
        if (
            self.consecutive_failures
            >= self.alert_thresholds["max_consecutive_failures"]
        ):
            alerts.append(
                {
                    "severity": "critical",
                    "message": f"Secret sync has failed {self.consecutive_failures} consecutive times",
                    "action": "Immediate investigation required",
                }
            )

        # Check sync health from latest check
        if self.health_history:
            latest_health = self.health_history[-1]
            if "sync_health" in latest_health:
                sync_percentage = (
                    latest_health["sync_health"]
                    .get("sync_health", {})
                    .get("percentage", 100)
                )
                if sync_percentage < self.alert_thresholds["sync_health_percentage"]:
                    alerts.append(
                        {
                            "severity": "warning",
                            "message": f"Sync health degraded to {sync_percentage:.1f}%",
                            "action": "Run sync operation to restore health",
                        }
                    )

        # Send alerts if any exist
        for alert in alerts:
            await self._send_alert(alert)

    async def _send_alert(self, alert: dict[str, Any]):
        """Send alert notification"""
        logger.warning(f"🚨 ALERT [{alert['severity'].upper()}]: {alert['message']}")

        # In a full implementation, this would send to Slack, email, etc.
        # For now, we'll log and optionally write to a file
        alert_record = {"timestamp": datetime.now().isoformat(), **alert}

        try:
            alerts_file = Path("logs/secret_sync_alerts.json")
            alerts_file.parent.mkdir(exist_ok=True)

            # Append to alerts file
            alerts_history = []
            if alerts_file.exists():
                with open(alerts_file) as f:
                    alerts_history = json.load(f)

            alerts_history.append(alert_record)

            # Keep only last 1000 alerts
            if len(alerts_history) > 1000:
                alerts_history = alerts_history[-1000:]

            with open(alerts_file, "w") as f:
                json.dump(alerts_history, f, indent=2)

        except Exception as e:
            logger.error(f"Failed to write alert to file: {e}")

    def _trim_health_history(self):
        """Trim old health check records"""
        retention_days = self.config["monitoring"]["health_retention_days"]
        cutoff_date = datetime.now() - timedelta(days=retention_days)

        self.health_history = [
            check
            for check in self.health_history
            if datetime.fromisoformat(check["timestamp"]) > cutoff_date
        ]

    async def run_auto_healing(self) -> dict[str, Any]:
        """Run automated healing procedures for detected issues"""
        logger.info("🔧 Running automated secret sync healing...")

        if not self.config["monitoring"]["enable_auto_healing"]:
            logger.info("Auto-healing disabled in configuration")
            return {"status": "disabled"}

        try:
            # Perform health check first
            health_check = await self._perform_health_check()

            if "error" in health_check:
                logger.error("Cannot run auto-healing due to health check failure")
                return {"status": "failed", "reason": "health_check_failed"}

            # Determine healing actions based on health
            sync_health = health_check.get("sync_health", {})
            sync_percentage = sync_health.get("sync_health", {}).get("percentage", 100)

            healing_actions = []

            if sync_percentage < self.alert_thresholds["sync_health_percentage"]:
                logger.info("🔄 Auto-healing: Running GitHub→ESC sync due to low health")

                # Load secret mapping
                mapping = self.sync_manager.load_secret_mapping()

                # Run sync operation
                sync_result = self.sync_manager.sync_github_to_esc(
                    secret_mapping=mapping, dry_run=False
                )

                healing_actions.append(
                    {
                        "action": "github_to_esc_sync",
                        "result": sync_result,
                        "success": sync_result.get("successful_syncs", 0) > 0,
                    }
                )

            # Validate healing results
            post_healing_health = await self._perform_health_check()

            healing_result = {
                "status": "completed",
                "timestamp": datetime.now().isoformat(),
                "actions_taken": healing_actions,
                "pre_healing_health": sync_percentage,
                "post_healing_health": post_healing_health.get("sync_health", {})
                .get("sync_health", {})
                .get("percentage", 0),
                "improvement": 0.0,
            }

            # Calculate improvement
            post_percentage = healing_result["post_healing_health"]
            healing_result["improvement"] = post_percentage - sync_percentage

            logger.info(
                f"✅ Auto-healing completed. Health improved by {healing_result['improvement']:.1f}%"
            )
            return healing_result

        except Exception as e:
            logger.error(f"❌ Auto-healing failed: {e}")
            return {"status": "failed", "error": str(e)}

    def get_monitoring_dashboard_data(self) -> dict[str, Any]:
        """Get formatted data for monitoring dashboard"""
        latest_health = self.health_history[-1] if self.health_history else {}

        return {
            "timestamp": datetime.now().isoformat(),
            "current_health": {
                "sync_percentage": latest_health.get("sync_health", {})
                .get("sync_health", {})
                .get("percentage", 0),
                "status": latest_health.get("sync_health", {})
                .get("sync_health", {})
                .get("status", "unknown"),
                "connectivity": latest_health.get("connectivity", {}),
                "performance": latest_health.get("performance", {}),
            },
            "historical_metrics": {
                "total_checks": len(self.health_history),
                "success_rate": (
                    self.performance_metrics["success_count"]
                    / max(
                        self.performance_metrics["success_count"]
                        + self.performance_metrics["error_count"],
                        1,
                    )
                )
                * 100,
                "average_sync_duration": self.performance_metrics[
                    "average_sync_duration"
                ],
                "consecutive_failures": self.consecutive_failures,
            },
            "recommendations": latest_health.get("recommendations", []),
            "alert_summary": {
                "active_alerts": self.consecutive_failures > 0,
                "alert_level": "critical"
                if self.consecutive_failures >= 3
                else "warning"
                if self.consecutive_failures > 0
                else "none",
            },
        }


async def main():
    """Main entry point for enhanced secret sync monitoring"""
    import argparse

    parser = argparse.ArgumentParser(description="Enhanced Secret Sync Monitor")
    parser.add_argument(
        "--monitor", action="store_true", help="Start continuous monitoring"
    )
    parser.add_argument(
        "--health-check", action="store_true", help="Run single health check"
    )
    parser.add_argument(
        "--auto-heal", action="store_true", help="Run auto-healing procedures"
    )
    parser.add_argument("--dashboard", action="store_true", help="Show dashboard data")
    parser.add_argument(
        "--config",
        default="infrastructure/esc/monitor_config.yaml",
        help="Config file path",
    )

    args = parser.parse_args()

    monitor = EnhancedSecretSyncMonitor(config_file=args.config)

    try:
        if args.monitor:
            await monitor.start_continuous_monitoring()
        elif args.health_check:
            result = await monitor._perform_health_check()
            print(json.dumps(result, indent=2))
        elif args.auto_heal:
            result = await monitor.run_auto_healing()
            print(json.dumps(result, indent=2))
        elif args.dashboard:
            result = monitor.get_monitoring_dashboard_data()
            print(json.dumps(result, indent=2))
        else:
            parser.print_help()

    except KeyboardInterrupt:
        logger.info("🛑 Monitoring stopped by user")
        await monitor.stop_monitoring()
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    import sys

    sys.exit(asyncio.run(main()))
