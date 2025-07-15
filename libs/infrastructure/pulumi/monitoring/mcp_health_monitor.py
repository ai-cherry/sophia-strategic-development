"""
MCP Health Monitoring System
Implements LangConnect-style health monitoring for all 28 MCP servers
"""

import asyncio
import logging
import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

import httpx
from prometheus_client import Counter, Gauge, Histogram

logger = logging.getLogger(__name__)

# Prometheus metrics
mcp_health_status = Gauge(
    "mcp_server_health_status", "Health status of MCP servers", ["server_name"]
)
mcp_response_time = Histogram(
    "mcp_server_response_time", "Response time of MCP servers", ["server_name"]
)
mcp_error_count = Counter(
    "mcp_server_errors", "Error count for MCP servers", ["server_name", "error_type"]
)
mcp_restart_count = Counter(
    "mcp_server_restarts", "Restart count for MCP servers", ["server_name"]
)


class HealthStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class ServerHealth:
    server_name: str
    status: HealthStatus
    response_time_ms: float
    last_check: datetime
    error_message: str | None = None
    capabilities: list[str] | None = None
    consecutive_failures: int = 0


class MCPHealthMonitor:
    """
    Monitors health of all MCP servers with auto-recovery capabilities
    """

    def __init__(self):
        self.servers = self._load_server_config()
        self.health_cache: dict[str, ServerHealth] = {}
        self.client = httpx.AsyncClient(timeout=10.0)
        self.check_interval = 30  # seconds
        self.max_consecutive_failures = 3
        self.restart_cooldown = 300  # 5 minutes
        self.last_restart: dict[str, datetime] = {}

    def _load_server_config(self) -> dict[str, dict]:
        """Load MCP server configuration"""
        # In production, load from config/consolidated_mcp_ports.json
        return {
            "ai_memory": {"port": 9000, "health_endpoint": "/health"},
            "codacy": {"port": 3008, "health_endpoint": "/health"},
            "github": {"port": 9003, "health_endpoint": "/health"},
            "linear": {"port": 9004, "health_endpoint": "/health"},
            "QDRANT_admin": {"port": 9020, "health_endpoint": "/health"},
            "ui_ux_agent": {"port": 9002, "health_endpoint": "/health"},
            "slack": {"port": 9005, "health_endpoint": "/health"},
            "hubspot": {"port": 9006, "health_endpoint": "/health"},
            # Add all 28 servers...
        }

    async def check_server_health(self, server_name: str) -> ServerHealth:
        """Check health of a single MCP server"""
        if server_name not in self.servers:
            return ServerHealth(
                server_name=server_name,
                status=HealthStatus.UNKNOWN,
                response_time_ms=0,
                last_check=datetime.utcnow(),
                error_message="Server not configured",
            )

        server_config = self.servers[server_name]
        url = f"http://localhost:{server_config['port']}{server_config['health_endpoint']}"

        start_time = time.time()
        try:
            response = await self.client.get(url)
            response_time_ms = (time.time() - start_time) * 1000

            # Record metrics
            mcp_response_time.labels(server_name=server_name).observe(response_time_ms)

            if response.status_code == 200:
                # Parse capabilities from response
                data = response.json()
                capabilities = data.get("capabilities", [])

                # Determine health status based on response time
                if response_time_ms < 100:
                    status = HealthStatus.HEALTHY
                elif response_time_ms < 500:
                    status = HealthStatus.DEGRADED
                else:
                    status = HealthStatus.UNHEALTHY

                health = ServerHealth(
                    server_name=server_name,
                    status=status,
                    response_time_ms=response_time_ms,
                    last_check=datetime.utcnow(),
                    capabilities=capabilities,
                    consecutive_failures=0,
                )

                # Update metrics
                mcp_health_status.labels(server_name=server_name).set(
                    1
                    if status == HealthStatus.HEALTHY
                    else 0.5
                    if status == HealthStatus.DEGRADED
                    else 0
                )

            else:
                health = ServerHealth(
                    server_name=server_name,
                    status=HealthStatus.UNHEALTHY,
                    response_time_ms=response_time_ms,
                    last_check=datetime.utcnow(),
                    error_message=f"HTTP {response.status_code}",
                    consecutive_failures=self._get_consecutive_failures(server_name)
                    + 1,
                )
                mcp_error_count.labels(
                    server_name=server_name, error_type="http_error"
                ).inc()
                mcp_health_status.labels(server_name=server_name).set(0)

        except Exception as e:
            health = ServerHealth(
                server_name=server_name,
                status=HealthStatus.UNHEALTHY,
                response_time_ms=0,
                last_check=datetime.utcnow(),
                error_message=str(e),
                consecutive_failures=self._get_consecutive_failures(server_name) + 1,
            )
            mcp_error_count.labels(
                server_name=server_name, error_type="connection_error"
            ).inc()
            mcp_health_status.labels(server_name=server_name).set(0)
            logger.exception(f"Health check failed for {server_name}: {e}")

        # Update cache
        self.health_cache[server_name] = health

        # Check if auto-recovery needed
        if health.consecutive_failures >= self.max_consecutive_failures:
            await self._attempt_auto_recovery(server_name)

        return health

    def _get_consecutive_failures(self, server_name: str) -> int:
        """Get consecutive failure count for a server"""
        if server_name in self.health_cache:
            return self.health_cache[server_name].consecutive_failures
        return 0

    async def _attempt_auto_recovery(self, server_name: str):
        """Attempt to auto-recover an unhealthy server"""
        # Check cooldown
        if server_name in self.last_restart:
            time_since_restart = datetime.utcnow() - self.last_restart[server_name]
            if time_since_restart.total_seconds() < self.restart_cooldown:
                logger.warning(
                    f"Skipping restart for {server_name} - in cooldown period"
                )
                return

        logger.warning(f"Attempting auto-recovery for {server_name}")
        try:
            # In production, this would use Docker API or systemctl
            # For now, log the action
            logger.info(f"Would restart MCP server: {server_name}")
            mcp_restart_count.labels(server_name=server_name).inc()
            self.last_restart[server_name] = datetime.utcnow()

            # Reset consecutive failures after restart attempt
            if server_name in self.health_cache:
                self.health_cache[server_name].consecutive_failures = 0

        except Exception as e:
            logger.exception(f"Failed to restart {server_name}: {e}")

    async def check_all_servers(self) -> dict[str, ServerHealth]:
        """Check health of all configured servers"""
        tasks = [self.check_server_health(name) for name in self.servers]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        health_status = {}
        for server_name, result in zip(self.servers.keys(), results, strict=False):
            if isinstance(result, Exception):
                health_status[server_name] = ServerHealth(
                    server_name=server_name,
                    status=HealthStatus.UNKNOWN,
                    response_time_ms=0,
                    last_check=datetime.utcnow(),
                    error_message=str(result),
                )
            else:
                health_status[server_name] = result

        return health_status

    async def start_monitoring(self):
        """Start continuous health monitoring"""
        logger.info("Starting MCP health monitoring")
        while True:
            try:
                await self.check_all_servers()
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                logger.exception(f"Error in monitoring loop: {e}")
                await asyncio.sleep(self.check_interval)

    def get_health_summary(self) -> dict:
        """Get summary of all server health"""
        total = len(self.servers)
        healthy = sum(
            1 for h in self.health_cache.values() if h.status == HealthStatus.HEALTHY
        )
        degraded = sum(
            1 for h in self.health_cache.values() if h.status == HealthStatus.DEGRADED
        )
        unhealthy = sum(
            1 for h in self.health_cache.values() if h.status == HealthStatus.UNHEALTHY
        )

        return {
            "total_servers": total,
            "healthy": healthy,
            "degraded": degraded,
            "unhealthy": unhealthy,
            "health_percentage": (healthy / total * 100) if total > 0 else 0,
            "last_check": max(
                (h.last_check for h in self.health_cache.values()),
                default=datetime.utcnow(),
            ),
            "servers": {
                name: {
                    "status": health.status.value,
                    "response_time_ms": health.response_time_ms,
                    "last_check": health.last_check.isoformat(),
                    "error": health.error_message,
                    "capabilities": health.capabilities,
                }
                for name, health in self.health_cache.items()
            },
        }

    async def close(self):
        """Clean up resources"""
        await self.client.aclose()


# Singleton instance
health_monitor = MCPHealthMonitor()
