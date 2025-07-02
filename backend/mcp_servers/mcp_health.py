"""
MCP Services Health Monitoring
Comprehensive health checks and monitoring for all MCP servers
"""

import asyncio
import logging
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class ServiceHealth:
    """Health status for a service"""

    name: str
    status: str  # healthy, degraded, unhealthy
    response_time_ms: float
    last_check: datetime
    error_message: str | None = None
    uptime_percentage: float = 100.0


@dataclass
class SystemHealth:
    """Overall system health"""

    overall_status: str
    total_services: int
    healthy_services: int
    degraded_services: int
    unhealthy_services: int
    last_updated: datetime
    services: list[ServiceHealth]


class MCPHealthMonitor:
    """Health monitoring for all MCP services"""

    def __init__(self):
        self.health_history: dict[str, list[ServiceHealth]] = {}
        self.services = ["snowflake", "hubspot", "slack", "github", "notion"]

    async def check_service_health(self, service_name: str) -> ServiceHealth:
        """Check health of a specific service"""
        start_time = datetime.now()

        try:
            # Import and test the service
            if service_name == "snowflake":
                from backend.core.snowflake_override import (
                    get_snowflake_connection_params,
                )

                params = get_snowflake_connection_params()
                status = "healthy" if params["account"] == "ZNB04675.us-east-1" else "unhealthy"
                error_msg = None if status == "healthy" else "Wrong account configured"

            elif service_name == "hubspot":
                from backend.mcp_servers.mcp_auth import mcp_auth

                configured = mcp_auth.is_service_configured("hubspot")
                status = "healthy" if configured else "degraded"
                error_msg = None if configured else "API key not configured"

            elif service_name == "slack":
                from backend.mcp_servers.mcp_auth import mcp_auth

                configured = mcp_auth.is_service_configured("slack")
                status = "healthy" if configured else "degraded"
                error_msg = None if configured else "Bot token not configured"

            elif service_name == "github":
                from backend.mcp_servers.mcp_auth import mcp_auth

                configured = mcp_auth.is_service_configured("github")
                status = "healthy" if configured else "degraded"
                error_msg = None if configured else "Access token not configured"

            elif service_name == "notion":
                from backend.mcp_servers.mcp_auth import mcp_auth

                configured = mcp_auth.is_service_configured("notion")
                status = "healthy" if configured else "degraded"
                error_msg = None if configured else "API token not configured"

            else:
                status = "unhealthy"
                error_msg = f"Unknown service: {service_name}"

            # Calculate response time
            response_time = (datetime.now() - start_time).total_seconds() * 1000

            return ServiceHealth(
                name=service_name,
                status=status,
                response_time_ms=response_time,
                last_check=datetime.now(),
                error_message=error_msg,
            )

        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            return ServiceHealth(
                name=service_name,
                status="unhealthy",
                response_time_ms=response_time,
                last_check=datetime.now(),
                error_message=str(e),
            )

    async def check_all_services(self) -> SystemHealth:
        """Check health of all services"""
        logger.info("🔍 Checking health of all MCP services...")

        # Check all services concurrently
        health_checks = [
            self.check_service_health(service) for service in self.services
        ]

        service_healths = await asyncio.gather(*health_checks)

        # Store in history
        for health in service_healths:
            if health.name not in self.health_history:
                self.health_history[health.name] = []
            self.health_history[health.name].append(health)

            # Keep only last 100 checks
            if len(self.health_history[health.name]) > 100:
                self.health_history[health.name] = self.health_history[health.name][
                    -100:
                ]

        # Calculate overall status
        healthy = sum(1 for h in service_healths if h.status == "healthy")
        degraded = sum(1 for h in service_healths if h.status == "degraded")
        unhealthy = sum(1 for h in service_healths if h.status == "unhealthy")

        if unhealthy > 0:
            overall_status = "unhealthy"
        elif degraded > 0:
            overall_status = "degraded"
        else:
            overall_status = "healthy"

        system_health = SystemHealth(
            overall_status=overall_status,
            total_services=len(service_healths),
            healthy_services=healthy,
            degraded_services=degraded,
            unhealthy_services=unhealthy,
            last_updated=datetime.now(),
            services=service_healths,
        )

        # Log summary
        logger.info(f"   Overall Status: {overall_status}")
        logger.info(
            f"   Services: {healthy} healthy, {degraded} degraded, {unhealthy} unhealthy"
        )

        return system_health

    def get_health_report(self) -> dict[str, Any]:
        """Get comprehensive health report"""
        return {
            "timestamp": datetime.now().isoformat(),
            "services": {
                name: [asdict(h) for h in history[-10:]]  # Last 10 checks
                for name, history in self.health_history.items()
            },
        }


# Global health monitor instance
health_monitor = MCPHealthMonitor()
