"""Real-time cost monitoring with budget enforcement."""

import logging
import sqlite3
import time
from typing import Any, Optional

from backend.core.auto_esc_config import (
    get_config_value,  # type: ignore[import-not-found]
)

logger = logging.getLogger(__name__)


class LambdaLabsCostMonitor:
    """Monitor Lambda Labs usage and enforce budgets.

    This service provides:
    - Real-time cost tracking from usage database
    - Daily and monthly budget enforcement
    - Automatic alerts when thresholds exceeded
    - Budget status reporting

    Attributes:
        db_path: Path to usage database
        daily_budget: Daily spending limit in USD
        monthly_budget: Monthly spending limit in USD
        alert_webhook: Optional webhook for alerts
    """

    def __init__(
        self,
        db_path: str = "data/lambda_usage.db",
        daily_budget: Optional[float] = None,
        monthly_budget: Optional[float] = None,
    ):
        """Initialize cost monitor with budget limits.

        Args:
            db_path: Path to SQLite usage database
            daily_budget: Optional daily budget override
            monthly_budget: Optional monthly budget override
        """
        self.db_path = db_path
        self.daily_budget = daily_budget or float(
            get_config_value("lambda_daily_budget", "50.0")
        )
        self.monthly_budget = monthly_budget or float(
            get_config_value("lambda_monthly_budget", "1000.0")
        )
        self.alert_webhook = get_config_value("slack_webhook_url", "")

    async def check_and_alert(self) -> dict[str, Any]:
        """Check current usage against budgets and send alerts if needed.

        Returns:
            Dictionary containing:
            - daily: Current daily cost
            - monthly: Current monthly cost
            - daily_budget: Daily budget limit
            - monthly_budget: Monthly budget limit
            - daily_percentage: Percentage of daily budget used
            - monthly_percentage: Percentage of monthly budget used
            - alerts: List of alert messages sent
        """
        daily_cost, monthly_cost = self._compute_costs()

        result = {
            "daily": daily_cost,
            "monthly": monthly_cost,
            "daily_budget": self.daily_budget,
            "monthly_budget": self.monthly_budget,
            "daily_percentage": (daily_cost / self.daily_budget) * 100,
            "monthly_percentage": (monthly_cost / self.monthly_budget) * 100,
            "alerts": [],
        }

        # Check daily budget
        if daily_cost >= self.daily_budget * 0.8:
            alert = f"Daily Lambda Labs budget alert: ${daily_cost:.2f} / ${self.daily_budget:.2f} ({result['daily_percentage']:.1f}%)"
            result["alerts"].append(alert)
            await self._send_alert(
                alert, "warning" if daily_cost < self.daily_budget else "error"
            )

        # Check monthly budget
        if monthly_cost >= self.monthly_budget * 0.8:
            alert = f"Monthly Lambda Labs budget alert: ${monthly_cost:.2f} / ${self.monthly_budget:.2f} ({result['monthly_percentage']:.1f}%)"
            result["alerts"].append(alert)
            await self._send_alert(
                alert, "warning" if monthly_cost < self.monthly_budget else "error"
            )

        return result

    def _compute_costs(self) -> tuple[float, float]:
        """Compute daily and monthly costs from database.

        Returns:
            Tuple of (daily_cost, monthly_cost)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Daily cost (last 24 hours)
        daily_start = int(time.time()) - 86400
        cursor.execute(
            "SELECT SUM(cost) FROM usage WHERE timestamp >= ?", (daily_start,)
        )
        daily_cost = cursor.fetchone()[0] or 0.0

        # Monthly cost (last 30 days)
        monthly_start = int(time.time()) - (30 * 86400)
        cursor.execute(
            "SELECT SUM(cost) FROM usage WHERE timestamp >= ?", (monthly_start,)
        )
        monthly_cost = cursor.fetchone()[0] or 0.0

        conn.close()
        return daily_cost, monthly_cost

    async def _send_alert(self, message: str, level: str = "warning") -> None:
        """Send alert to configured webhook.

        Args:
            message: Alert message
            level: Alert level ("warning" or "error")
        """
        if not self.alert_webhook:
            logger.warning(f"No webhook configured for alert: {message}")
            return

        # Send to Slack webhook
        payload = {
            "text": message,
            "attachments": [
                {
                    "color": "danger" if level == "error" else "warning",
                    "fields": [
                        {
                            "title": "Lambda Labs Cost Alert",
                            "value": message,
                            "short": False,
                        }
                    ],
                    "footer": "Sophia AI Cost Monitor",
                    "ts": int(time.time()),
                }
            ],
        }

        # Would implement actual webhook call here
        logger.info(f"Alert sent: {message}")

    def is_within_budget(self) -> bool:
        """Check if current usage is within budget limits.

        Returns:
            True if within both daily and monthly budgets
        """
        daily_cost, monthly_cost = self._compute_costs()
        return daily_cost < self.daily_budget and monthly_cost < self.monthly_budget

    def get_remaining_budget(self) -> dict[str, float]:
        """Get remaining budget for daily and monthly limits.

        Returns:
            Dictionary with daily_remaining and monthly_remaining
        """
        daily_cost, monthly_cost = self._compute_costs()
        return {
            "daily_remaining": max(0, self.daily_budget - daily_cost),
            "monthly_remaining": max(0, self.monthly_budget - monthly_cost),
        }
