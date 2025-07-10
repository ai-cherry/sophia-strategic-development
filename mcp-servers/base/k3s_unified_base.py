"""
Sophia AI - K3s-Aware Unified MCP Server Base Class
Enhanced base class for MCP servers running on K3s
Using official Anthropic MCP SDK

Date: July 10, 2025
"""

import asyncio
import logging
import os
import signal
import socket
from abc import ABC, abstractmethod
from collections.abc import Sequence
from datetime import UTC, datetime
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool
from pydantic import BaseModel, Field

# Configure logging for K3s
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - [K3s] %(message)s",
    handlers=[logging.StreamHandler()],  # Ensure logs go to stdout for K3s
)
logger = logging.getLogger(__name__)


class ServerConfig(BaseModel):
    """Configuration for K3s MCP servers"""

    name: str
    version: str = "1.0.0"
    port: int = 9000
    description: str = ""
    tier: str = "SECONDARY"  # PRIMARY, SECONDARY, TERTIARY
    capabilities: list[str] = Field(default_factory=list)
    gpu_enabled: bool = False


class K3sUnifiedMCPServer(ABC):
    """
    K3s-aware base class for all MCP servers
    Enhanced with Kubernetes features and best practices
    """

    def __init__(self, config: ServerConfig):
        self.config = config
        self.server = Server(config.name)
        self.start_time = datetime.now(UTC)
        self.request_count = 0
        self.error_count = 0
        self.is_ready = False
        self.is_healthy = True

        # K3s specific configuration
        self.k3s_namespace = os.getenv("K3S_NAMESPACE", "sophia-mcp")
        self.k3s_pod_name = os.getenv("HOSTNAME", socket.gethostname())
        self.k3s_node_name = os.getenv("K3S_NODE_NAME", "unknown")
        self.k3s_deployment = os.getenv("K3S_DEPLOYMENT", "false").lower() == "true"

        # Service discovery
        self.service_dns_suffix = f".{self.k3s_namespace}.svc.cluster.local"

        # Set up logging
        self.logger = logging.getLogger(f"mcp.{config.name}")

        # Register handlers
        self._register_handlers()

        # Setup graceful shutdown
        self._setup_graceful_shutdown()

        # Log startup information
        self._log_startup_info()

    def _log_startup_info(self):
        """Log K3s deployment information"""
        self.logger.info(
            f"Starting {self.config.name} MCP server v{self.config.version}"
        )
        self.logger.info(f"K3s Deployment: {self.k3s_deployment}")
        self.logger.info(f"Namespace: {self.k3s_namespace}")
        self.logger.info(f"Pod Name: {self.k3s_pod_name}")
        self.logger.info(f"Node Name: {self.k3s_node_name}")
        self.logger.info(f"Service Tier: {self.config.tier}")
        self.logger.info(f"GPU Enabled: {self.config.gpu_enabled}")
        self.logger.info(f"Port: {self.config.port}")

    def _setup_graceful_shutdown(self):
        """Setup SIGTERM handler for K3s graceful shutdown"""

        def sigterm_handler(signum, frame):
            self.logger.info("Received SIGTERM, initiating graceful shutdown...")
            self.is_healthy = False  # Mark as unhealthy to stop receiving traffic
            asyncio.create_task(self._graceful_shutdown())

        signal.signal(signal.SIGTERM, sigterm_handler)

    async def _graceful_shutdown(self):
        """Perform graceful shutdown"""
        try:
            # Give K3s time to stop routing traffic
            await asyncio.sleep(5)

            # Custom cleanup
            await self.cleanup()

            # Log final metrics
            self.logger.info(
                f"Shutdown metrics - Requests: {self.request_count}, Errors: {self.error_count}"
            )

            # Exit
            os._exit(0)
        except Exception as e:
            self.logger.error(f"Error during graceful shutdown: {e}")
            os._exit(1)

    def _register_handlers(self):
        """Register MCP handlers with K3s enhancements"""

        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """List all available tools"""
            base_tools = [
                Tool(
                    name="health_check",
                    description="Check server health (K3s health probe)",
                    inputSchema={"type": "object", "properties": {}, "required": []},
                ),
                Tool(
                    name="readiness_check",
                    description="Check server readiness (K3s readiness probe)",
                    inputSchema={"type": "object", "properties": {}, "required": []},
                ),
                Tool(
                    name="get_server_info",
                    description="Get server and K3s deployment information",
                    inputSchema={"type": "object", "properties": {}, "required": []},
                ),
                Tool(
                    name="get_metrics",
                    description="Get Prometheus-compatible metrics",
                    inputSchema={"type": "object", "properties": {}, "required": []},
                ),
            ]

            # Add custom tools from subclass
            custom_tools = await self.get_custom_tools()
            return base_tools + custom_tools

        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict) -> Sequence[TextContent]:
            """Handle tool calls with K3s awareness"""
            self.request_count += 1

            try:
                # Handle base tools
                if name == "health_check":
                    result = await self._health_check()
                elif name == "readiness_check":
                    result = await self._readiness_check()
                elif name == "get_server_info":
                    result = await self._get_server_info()
                elif name == "get_metrics":
                    result = await self._get_metrics()
                else:
                    # Delegate to subclass
                    result = await self.handle_custom_tool(name, arguments)

                # Convert dict result to JSON text
                import json

                return [TextContent(type="text", text=json.dumps(result, indent=2))]

            except Exception as e:
                self.error_count += 1
                self.logger.error(f"Tool error in {name}: {e}")
                raise

    async def _health_check(self) -> dict[str, Any]:
        """K3s liveness probe compatible health check"""
        # Subclasses can override is_healthy based on their logic
        status = "healthy" if self.is_healthy else "unhealthy"

        return {
            "status": status,
            "timestamp": datetime.now(UTC).isoformat(),
            "pod": self.k3s_pod_name,
            "errors": self.error_count,
            "uptime_seconds": (datetime.now(UTC) - self.start_time).total_seconds(),
        }

    async def _readiness_check(self) -> dict[str, Any]:
        """K3s readiness probe compatible check"""
        # Subclasses should set is_ready when they're ready to serve
        status = "ready" if self.is_ready else "not_ready"

        return {
            "status": status,
            "timestamp": datetime.now(UTC).isoformat(),
            "pod": self.k3s_pod_name,
            "service": f"mcp-{self.config.name}",
            "port": self.config.port,
        }

    async def _get_server_info(self) -> dict[str, Any]:
        """Get enhanced server information for K3s"""
        uptime = (datetime.now(UTC) - self.start_time).total_seconds()

        return {
            "name": self.config.name,
            "version": self.config.version,
            "description": self.config.description,
            "tier": self.config.tier,
            "capabilities": self.config.capabilities,
            "gpu_enabled": self.config.gpu_enabled,
            "uptime_seconds": uptime,
            "request_count": self.request_count,
            "error_count": self.error_count,
            "error_rate": self.error_count / max(self.request_count, 1),
            "k3s_info": {
                "deployed": self.k3s_deployment,
                "namespace": self.k3s_namespace,
                "pod_name": self.k3s_pod_name,
                "node_name": self.k3s_node_name,
                "service_dns": f"mcp-{self.config.name}{self.service_dns_suffix}",
            },
        }

    async def _get_metrics(self) -> dict[str, Any]:
        """Get Prometheus-compatible metrics"""
        uptime = (datetime.now(UTC) - self.start_time).total_seconds()

        # Format as Prometheus text format
        metrics_text = f"""# HELP mcp_server_uptime_seconds Server uptime in seconds
# TYPE mcp_server_uptime_seconds gauge
mcp_server_uptime_seconds{{server="{self.config.name}",tier="{self.config.tier}"}} {uptime}

# HELP mcp_server_requests_total Total number of requests
# TYPE mcp_server_requests_total counter
mcp_server_requests_total{{server="{self.config.name}",tier="{self.config.tier}"}} {self.request_count}

# HELP mcp_server_errors_total Total number of errors
# TYPE mcp_server_errors_total counter
mcp_server_errors_total{{server="{self.config.name}",tier="{self.config.tier}"}} {self.error_count}

# HELP mcp_server_info Server information
# TYPE mcp_server_info gauge
mcp_server_info{{server="{self.config.name}",version="{self.config.version}",tier="{self.config.tier}",gpu="{self.config.gpu_enabled}"}} 1
"""

        return {
            "format": "prometheus",
            "metrics": metrics_text,
            "endpoint": "/metrics",
        }

    def get_service_url(self, service_name: str, port: int) -> str:
        """Get K3s service URL for inter-MCP communication"""
        if self.k3s_deployment:
            # Use K3s service discovery
            return f"http://{service_name}{self.service_dns_suffix}:{port}"
        else:
            # Local development fallback
            return f"http://localhost:{port}"

    async def startup(self):
        """
        Perform startup tasks
        Subclasses should override this to initialize resources
        """
        self.logger.info("Performing startup tasks...")
        self.is_ready = True

    async def cleanup(self):
        """
        Perform cleanup tasks
        Subclasses should override this to cleanup resources
        """
        self.logger.info("Performing cleanup tasks...")

    @abstractmethod
    async def get_custom_tools(self) -> list[Tool]:
        """
        Define custom tools for this server
        Must be implemented by subclasses
        """
        pass

    @abstractmethod
    async def handle_custom_tool(self, name: str, arguments: dict) -> dict[str, Any]:
        """
        Handle custom tool calls
        Must be implemented by subclasses
        """
        pass

    async def run(self):
        """Run the server with K3s enhancements"""
        try:
            # Perform startup tasks
            await self.startup()

            self.logger.info(
                f"{self.config.name} MCP server ready on port {self.config.port}"
            )

            # Run the MCP server
            options = self.server.create_initialization_options()
            async with stdio_server() as (read_stream, write_stream):
                await self.server.run(read_stream, write_stream, options)

        except Exception as e:
            self.logger.error(f"Server error: {e}")
            self.is_healthy = False
            raise
        finally:
            await self.cleanup()


# Alias for backward compatibility
UnifiedStandardizedMCPServer = K3sUnifiedMCPServer


# Example implementation for reference
class ExampleK3sMCPServer(K3sUnifiedMCPServer):
    """Example implementation showing K3s features"""

    def __init__(self):
        config = ServerConfig(
            name="example",
            version="1.0.0",
            port=9999,
            description="Example K3s MCP server",
            tier="SECONDARY",
            capabilities=["EXAMPLE", "TEST"],
            gpu_enabled=False,
        )
        super().__init__(config)

    async def startup(self):
        """Initialize resources"""
        await super().startup()
        self.logger.info("Example server initialized")

        # Example: Connect to other MCP servers
        ai_memory_url = self.get_service_url("mcp-ai-memory", 9000)
        self.logger.info(f"AI Memory service URL: {ai_memory_url}")

    async def get_custom_tools(self) -> list[Tool]:
        """Define custom tools"""
        return [
            Tool(
                name="example_tool",
                description="Example tool for K3s deployment",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Query to process"}
                    },
                    "required": ["query"],
                },
            )
        ]

    async def handle_custom_tool(self, name: str, arguments: dict) -> dict[str, Any]:
        """Handle custom tool calls"""
        if name == "example_tool":
            query = arguments.get("query", "")
            self.logger.info(f"Processing query: {query}")

            return {
                "query": query,
                "result": f"Processed in K3s: {query}",
                "pod": self.k3s_pod_name,
                "timestamp": datetime.now(UTC).isoformat(),
            }
        else:
            raise ValueError(f"Unknown tool: {name}")


async def main():
    """Main entry point"""
    server = ExampleK3sMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
