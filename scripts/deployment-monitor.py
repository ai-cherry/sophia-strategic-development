#!/usr/bin/env python3
"""
Sophia AI Deployment Monitor
Monitors deployment health and sends alerts when issues are detected.
"""

import json
import logging
import os
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timedelta

import requests


@dataclass
class HealthCheck:
    name: str
    url: str
    expected_status: int = 200
    timeout: int = 30
    critical: bool = True

@dataclass
class MonitoringResult:
    timestamp: datetime
    checks: list[tuple[str, bool, str]]  # (name, success, message)
    overall_health: bool
    response_times: dict[str, float]

class DeploymentMonitor:
    def __init__(self, base_url: str, webhook_url: str | None = None):
        self.base_url = base_url.rstrip('/')
        self.webhook_url = webhook_url
        self.logger = self._setup_logging()

        # Define health checks
        self.health_checks = [
            HealthCheck("Frontend", f"{self.base_url}/", critical=True),
            HealthCheck("API Health", f"{self.base_url}/api/health", critical=True),
            HealthCheck("n8n Webhook", f"{self.base_url}/api/n8n/health", critical=False),
            HealthCheck("MCP Server", f"{self.base_url}/api/mcp/health", critical=False),
        ]

    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('deployment-monitor.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        return logging.getLogger(__name__)

    def check_endpoint(self, check: HealthCheck) -> tuple[bool, str, float]:
        """Check a single endpoint."""
        start_time = time.time()

        try:
            response = requests.get(
                check.url,
                timeout=check.timeout,
                headers={'User-Agent': 'Sophia-AI-Monitor/1.0'}
            )

            response_time = time.time() - start_time

            if response.status_code == check.expected_status:
                return True, f"OK ({response.status_code})", response_time
            else:
                return False, f"HTTP {response.status_code}", response_time

        except requests.exceptions.Timeout:
            response_time = time.time() - start_time
            return False, f"Timeout after {check.timeout}s", response_time

        except requests.exceptions.ConnectionError:
            response_time = time.time() - start_time
            return False, "Connection failed", response_time

        except Exception as e:
            response_time = time.time() - start_time
            return False, f"Error: {str(e)}", response_time

    def run_health_checks(self) -> MonitoringResult:
        """Run all health checks."""
        self.logger.info(f"🔍 Running health checks for {self.base_url}")

        checks = []
        response_times = {}
        critical_failures = 0

        for health_check in self.health_checks:
            success, message, response_time = self.check_endpoint(health_check)

            checks.append((health_check.name, success, message))
            response_times[health_check.name] = response_time

            status_icon = "✅" if success else "❌"
            criticality = " (CRITICAL)" if health_check.critical else ""

            self.logger.info(
                f"{status_icon} {health_check.name}{criticality}: {message} "
                f"({response_time:.2f}s)"
            )

            if not success and health_check.critical:
                critical_failures += 1

        overall_health = critical_failures == 0

        return MonitoringResult(
            timestamp=datetime.utcnow(),
            checks=checks,
            overall_health=overall_health,
            response_times=response_times
        )

    def send_alert(self, result: MonitoringResult, alert_type: str = "failure"):
        """Send alert notification."""
        if not self.webhook_url:
            self.logger.warning("No webhook URL configured for alerts")
            return

        # Prepare alert message
        if alert_type == "failure":
            title = "🚨 Sophia AI Deployment Alert - Service Down"
            color = "#ff0000"
        elif alert_type == "recovery":
            title = "✅ Sophia AI Deployment Recovery - Service Restored"
            color = "#00ff00"
        else:
            title = "📊 Sophia AI Deployment Status"
            color = "#ffaa00"

        # Build status summary
        failed_checks = [name for name, success, _ in result.checks if not success]

        if failed_checks:
            status_text = f"Failed services: {', '.join(failed_checks)}"
        else:
            status_text = "All services operational"

        # Create alert payload (Slack format)
        payload = {
            "text": title,
            "attachments": [
                {
                    "color": color,
                    "fields": [
                        {
                            "title": "Status",
                            "value": status_text,
                            "short": True
                        },
                        {
                            "title": "Timestamp",
                            "value": result.timestamp.strftime("%Y-%m-%d %H:%M:%S UTC"),
                            "short": True
                        },
                        {
                            "title": "Base URL",
                            "value": self.base_url,
                            "short": False
                        }
                    ]
                }
            ]
        }

        # Add detailed check results
        check_details = []
        for name, success, message in result.checks:
            icon = "✅" if success else "❌"
            response_time = result.response_times.get(name, 0)
            check_details.append(f"{icon} {name}: {message} ({response_time:.2f}s)")

        payload["attachments"][0]["fields"].append({
            "title": "Detailed Results",
            "value": "\n".join(check_details),
            "short": False
        })

        try:
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=10
            )

            if response.status_code == 200:
                self.logger.info("📤 Alert sent successfully")
            else:
                self.logger.error(f"Failed to send alert: {response.status_code}")

        except Exception as e:
            self.logger.error(f"Error sending alert: {e}")

    def save_metrics(self, result: MonitoringResult):
        """Save monitoring metrics to file."""
        metrics_file = "deployment-metrics.jsonl"

        metric_data = {
            "timestamp": result.timestamp.isoformat(),
            "overall_health": result.overall_health,
            "response_times": result.response_times,
            "checks": {name: success for name, success, _ in result.checks}
        }

        try:
            with open(metrics_file, "a") as f:
                f.write(json.dumps(metric_data) + "\n")
        except Exception as e:
            self.logger.error(f"Failed to save metrics: {e}")

    def generate_report(self, hours: int = 24) -> str:
        """Generate a health report for the last N hours."""
        try:
            with open("deployment-metrics.jsonl") as f:
                lines = f.readlines()
        except FileNotFoundError:
            return "No metrics data available"

        # Parse recent metrics
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        recent_metrics = []

        for line in lines:
            try:
                data = json.loads(line.strip())
                timestamp = datetime.fromisoformat(data["timestamp"])
                if timestamp >= cutoff_time:
                    recent_metrics.append(data)
            except:
                continue

        if not recent_metrics:
            return f"No metrics data available for the last {hours} hours"

        # Calculate statistics
        total_checks = len(recent_metrics)
        healthy_checks = sum(1 for m in recent_metrics if m["overall_health"])
        uptime_percentage = (healthy_checks / total_checks) * 100 if total_checks > 0 else 0

        # Average response times
        avg_response_times = {}
        for service in ["Frontend", "API Health", "n8n Webhook", "MCP Server"]:
            times = [m["response_times"].get(service, 0) for m in recent_metrics if service in m["response_times"]]
            avg_response_times[service] = sum(times) / len(times) if times else 0

        # Generate report
        report = f"""
# 📊 Sophia AI Deployment Health Report

## Summary (Last {hours} Hours)
- **Total Checks:** {total_checks}
- **Uptime:** {uptime_percentage:.1f}%
- **Healthy Checks:** {healthy_checks}/{total_checks}

## Average Response Times
"""

        for service, avg_time in avg_response_times.items():
            report += f"- **{service}:** {avg_time:.2f}s\n"

        report += f"""
## Recent Status
- **Last Check:** {recent_metrics[-1]['timestamp'] if recent_metrics else 'N/A'}
- **Current Health:** {'✅ Healthy' if recent_metrics[-1]['overall_health'] else '❌ Issues Detected'}

## Recommendations
"""

        if uptime_percentage < 95:
            report += "- ⚠️  Uptime below 95% - investigate deployment issues\n"

        if any(time > 5.0 for time in avg_response_times.values()):
            report += "- ⚠️  High response times detected - consider performance optimization\n"

        if uptime_percentage >= 99:
            report += "- ✅ Excellent uptime - deployment is stable\n"

        return report.strip()

def main():
    """Main monitoring function."""
    # Get configuration from environment
    base_url = os.getenv("SOPHIA_BASE_URL", "https://sophia-ai-frontend-dev.vercel.app")
    webhook_url = os.getenv("ALERT_WEBHOOK_URL")

    # Parse command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "report":
            hours = int(sys.argv[2]) if len(sys.argv) > 2 else 24
            monitor = DeploymentMonitor(base_url, webhook_url)
            print(monitor.generate_report(hours))
            return
        elif command == "test":
            # Test mode - single check without alerts
            monitor = DeploymentMonitor(base_url)
            result = monitor.run_health_checks()
            print(f"\n📊 Overall Health: {'✅ Healthy' if result.overall_health else '❌ Issues'}")
            return

    # Regular monitoring mode
    monitor = DeploymentMonitor(base_url, webhook_url)

    # Load previous state for alert management
    state_file = "monitor-state.json"
    previous_state = {"healthy": True}

    try:
        with open(state_file) as f:
            previous_state = json.load(f)
    except FileNotFoundError:
        pass

    # Run health checks
    result = monitor.run_health_checks()

    # Save metrics
    monitor.save_metrics(result)

    # Determine if we need to send alerts
    current_healthy = result.overall_health
    previous_healthy = previous_state.get("healthy", True)

    if not current_healthy and previous_healthy:
        # Service just went down
        monitor.send_alert(result, "failure")
    elif current_healthy and not previous_healthy:
        # Service just recovered
        monitor.send_alert(result, "recovery")

    # Save current state
    try:
        with open(state_file, "w") as f:
            json.dump({"healthy": current_healthy}, f)
    except Exception as e:
        monitor.logger.error(f"Failed to save state: {e}")

    # Exit with appropriate code
    sys.exit(0 if current_healthy else 1)

if __name__ == "__main__":
    main()

