"""
Enhanced Sophia MCP Base Class
Using official Anthropic MCP Python SDK with FastMCP
"""

import asyncio
import logging
import time
from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from backend.core.auto_esc_config import get_config_value
from backend.mcp_servers.server.fastmcp import FastMCP

logger = logging.getLogger(__name__)


@dataclass
class MCPServerHealth:
    """Health status for MCP servers"""

    status: str  # healthy, degraded, unhealthy
    uptime_seconds: float
    total_requests: int
    successful_requests: int
    failed_requests: int
    last_request_time: datetime | None
    error_rate: float


@dataclass
class SophiaContext:
    """Sophia AI context for MCP servers"""

    config: dict[str, Any]
    connection_manager: Any | None = None
    health_metrics: dict[str, Any] | None = None


class EnhancedSophiaMCPServer(ABC):
    """
    Enhanced base class for all Sophia AI MCP servers using official SDK
    Provides enterprise-grade patterns with FastMCP integration
    """

    def __init__(self, name: str, version: str = "1.0.0", port: int | None = None):
        self.name = name
        self.version = version
        self.port = port
        self.start_time = time.time()

        # Setup logging
        self.logger = logging.getLogger(f"sophia.mcp.{name}")
        self.logger.setLevel(logging.INFO)

        # Load configuration
        self.config = self._load_config()

        # Initialize metrics
        self.metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "last_request_time": None,
        }

        # Create FastMCP server with lifespan management
        self.mcp = FastMCP(
            name=name, dependencies=self.get_dependencies(), lifespan=self.app_lifespan
        )

        # Register tools and resources
        self._register_tools()
        self._register_resources()
        self._register_prompts()

        self.logger.info(f"🚀 Initialized {name} Enhanced MCP Server v{version}")

    def _load_config(self) -> dict[str, Any]:
        """Load configuration from Pulumi ESC and environment"""
        return {
            "environment": get_config_value("environment", "prod"),
            "log_level": get_config_value("log_level", "INFO"),
            "debug_mode": get_config_value("debug_mode", "false").lower() == "true",
            "max_retries": int(get_config_value("mcp_max_retries", "3")),
            "timeout_seconds": int(get_config_value("mcp_timeout", "30")),
        }

    @asynccontextmanager
    async def app_lifespan(self, server: FastMCP) -> AsyncIterator[SophiaContext]:
        """Manage application lifecycle with type-safe context"""
        self.logger.info(f"🚀 Starting {self.name} MCP Server lifecycle")

        # Initialize resources
        context = SophiaContext(config=self.config, health_metrics=self.metrics)

        # Initialize server-specific resources
        await self.initialize_resources(context)

        try:
            yield context
        finally:
            # Cleanup on shutdown
            await self.cleanup_resources(context)
            self.logger.info(f"🛑 {self.name} MCP Server lifecycle ended")

    @abstractmethod
    async def initialize_resources(self, context: SophiaContext):
        """Initialize server-specific resources - implement in subclasses"""
        pass

    @abstractmethod
    async def cleanup_resources(self, context: SophiaContext):
        """Cleanup server-specific resources - implement in subclasses"""
        pass

    @abstractmethod
    def get_dependencies(self) -> list[str]:
        """Return list of dependencies for this server"""
        return []

    @abstractmethod
    def _register_tools(self):
        """Register MCP tools - implement in subclasses"""
        pass

    @abstractmethod
    def _register_resources(self):
        """Register MCP resources - implement in subclasses"""
        pass

    def _register_prompts(self):
        """Register MCP prompts - override in subclasses if needed"""

        # Default health check prompt
        @self.mcp.prompt(title="Health Check")
        def health_prompt() -> str:
            return f"Check the health status of the {self.name} MCP server"

    def get_context(self) -> SophiaContext:
        """Get the current lifespan context"""
        return self.mcp.get_context().request_context.lifespan_context

    async def health_check(self) -> MCPServerHealth:
        """Standard health check for all servers"""
        uptime = time.time() - self.start_time
        total_requests = self.metrics["total_requests"]
        failed_requests = self.metrics["failed_requests"]

        error_rate = (failed_requests / max(total_requests, 1)) * 100

        # Determine health status
        if error_rate > 50:
            status = "unhealthy"
        elif error_rate > 10:
            status = "degraded"
        else:
            status = "healthy"

        return MCPServerHealth(
            status=status,
            uptime_seconds=uptime,
            total_requests=total_requests,
            successful_requests=self.metrics["successful_requests"],
            failed_requests=failed_requests,
            last_request_time=self.metrics["last_request_time"],
            error_rate=error_rate,
        )

    def track_request(self, success: bool = True):
        """Track request metrics"""
        self.metrics["total_requests"] += 1
        self.metrics["last_request_time"] = datetime.now()

        if success:
            self.metrics["successful_requests"] += 1
        else:
            self.metrics["failed_requests"] += 1

    async def run_server(self):
        """Run the MCP server"""
        self.logger.info(f"🚀 Starting {self.name} Enhanced MCP Server")

        if self.port:
            self.logger.info(f"   Listening on port {self.port}")

        # The FastMCP server handles the actual serving
        # This method can be used for additional server logic
        health = await self.health_check()
        self.logger.info(f"   Health status: {health.status}")

        return self.mcp


# Factory function for creating enhanced MCP servers
def create_enhanced_mcp_server(server_type: str, **kwargs) -> EnhancedSophiaMCPServer:
    """Factory function to create enhanced MCP servers"""
    servers = {
        # Add server types here
    }

    if server_type not in servers:
        raise ValueError(f"Unknown server type: {server_type}")

    return servers[server_type](**kwargs)


# Main function for running servers standalone
async def main():
    """Main function for testing servers"""
    logger.info("Enhanced MCP server framework ready")


if __name__ == "__main__":
    asyncio.run(main())
