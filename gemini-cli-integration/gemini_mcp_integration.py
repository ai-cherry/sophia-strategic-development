"""
Sophia AI - Gemini CLI MCP Integration Module
Provides advanced integration between Google Gemini CLI and Sophia AI MCP servers
"""

import asyncio
import contextlib
import json
import logging
import os
import subprocess
import time
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

import aiohttp
import psutil

logger = logging.getLogger(__name__)


class MCPServerStatus(Enum):
    """MCP Server status enumeration."""

    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"
    STARTING = "starting"
    STOPPING = "stopping"


@dataclass
class MCPServerInfo:
    """MCP Server information."""

    name: str
    port: int
    pid: int | None = None
    status: MCPServerStatus = MCPServerStatus.STOPPED
    last_health_check: float | None = None
    error_message: str | None = None
    capabilities: list[str] = None
    auto_start: bool = True


class GeminiMCPIntegration:
    """
    Advanced Gemini CLI integration with Sophia AI MCP servers.

    Provides:
    - MCP server lifecycle management
    - Health monitoring and auto-recovery
    - Intelligent routing and load balancing
    - Performance metrics and logging
    - Security and access control
    """

    def __init__(self, config_path: str = ".gemini/settings.json"):
        """Initialize Gemini MCP Integration."""
        self.config_path = Path(config_path)
        self.config: dict[str, Any] = {}
        self.servers: dict[str, MCPServerInfo] = {}
        self.session: aiohttp.ClientSession | None = None
        self.monitoring_task: asyncio.Task | None = None

        # Load configuration
        self._load_config()
        self._initialize_servers()

    def _load_config(self) -> None:
        """Load MCP configuration from JSON file."""
        try:
            if self.config_path.exists():
                with open(self.config_path) as f:
                    self.config = json.load(f)
                logger.info(f"Loaded configuration from {self.config_path}")
            else:
                logger.error(f"Configuration file not found: {self.config_path}")
                raise FileNotFoundError(
                    f"Configuration file not found: {self.config_path}"
                )
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in configuration file: {e}")
            raise
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            raise

    def _initialize_servers(self) -> None:
        """Initialize MCP server information from configuration."""
        mcp_servers = self.config.get("mcpServers", {})

        for server_name, server_config in mcp_servers.items():
            # Extract port from environment or default
            port = int(server_config.get("env", {}).get("MCP_SERVER_PORT", 8091))
            capabilities = server_config.get("capabilities", [])
            auto_start = server_config.get("auto_start", True)

            self.servers[server_name] = MCPServerInfo(
                name=server_name,
                port=port,
                capabilities=capabilities,
                auto_start=auto_start,
            )

        logger.info(f"Initialized {len(self.servers)} MCP servers")

    async def start_session(self) -> None:
        """Start HTTP session for health checks."""
        if not self.session:
            timeout = aiohttp.ClientTimeout(total=10)
            self.session = aiohttp.ClientSession(timeout=timeout)

    async def close_session(self) -> None:
        """Close HTTP session."""
        if self.session:
            await self.session.close()
            self.session = None

    async def start_server(self, server_name: str) -> bool:
        """Start a specific MCP server."""
        if server_name not in self.servers:
            logger.error(f"Unknown server: {server_name}")
            return False

        server_info = self.servers[server_name]
        server_config = self.config["mcpServers"][server_name]

        # Check if already running
        if await self._is_server_running(server_name):
            logger.info(f"Server {server_name} is already running")
            return True

        try:
            # Update status
            server_info.status = MCPServerStatus.STARTING

            # Prepare command
            command = server_config["command"]
            args = server_config.get("args", [])
            env = os.environ.copy()
            env.update(server_config.get("env", {}))

            # Start process
            full_command = [command] + args
            logger.info(f"Starting server {server_name}: {' '.join(full_command)}")

            process = subprocess.Popen(
                full_command,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                preexec_fn=os.setsid,  # Create new process group
            )

            # Store PID
            server_info.pid = process.pid
            server_info.status = MCPServerStatus.RUNNING

            # Wait a moment for server to start
            await asyncio.sleep(2)

            # Verify server is responding
            if await self._health_check(server_name):
                logger.info(
                    f"Server {server_name} started successfully (PID: {process.pid})"
                )
                return True
            else:
                logger.error(f"Server {server_name} failed health check after startup")
                server_info.status = MCPServerStatus.ERROR
                return False

        except Exception as e:
            logger.error(f"Error starting server {server_name}: {e}")
            server_info.status = MCPServerStatus.ERROR
            server_info.error_message = str(e)
            return False

    async def stop_server(self, server_name: str) -> bool:
        """Stop a specific MCP server."""
        if server_name not in self.servers:
            logger.error(f"Unknown server: {server_name}")
            return False

        server_info = self.servers[server_name]

        try:
            server_info.status = MCPServerStatus.STOPPING

            if server_info.pid:
                # Try graceful shutdown first
                try:
                    process = psutil.Process(server_info.pid)
                    process.terminate()

                    # Wait for graceful shutdown
                    try:
                        process.wait(timeout=10)
                    except psutil.TimeoutExpired:
                        # Force kill if graceful shutdown fails
                        process.kill()
                        process.wait(timeout=5)

                    logger.info(
                        f"Server {server_name} stopped (PID: {server_info.pid})"
                    )

                except psutil.NoSuchProcess:
                    logger.info(
                        f"Server {server_name} process not found (already stopped)"
                    )

                server_info.pid = None

            # Also try to kill by port
            await self._kill_process_by_port(server_info.port)

            server_info.status = MCPServerStatus.STOPPED
            return True

        except Exception as e:
            logger.error(f"Error stopping server {server_name}: {e}")
            server_info.status = MCPServerStatus.ERROR
            server_info.error_message = str(e)
            return False

    async def start_all_servers(self) -> dict[str, bool]:
        """Start all auto-start MCP servers."""
        results = {}

        for server_name, server_info in self.servers.items():
            if server_info.auto_start:
                results[server_name] = await self.start_server(server_name)
            else:
                logger.info(f"Skipping {server_name} (auto_start=False)")
                results[server_name] = True

        return results

    async def stop_all_servers(self) -> dict[str, bool]:
        """Stop all MCP servers."""
        results = {}

        for server_name in self.servers:
            results[server_name] = await self.stop_server(server_name)

        return results

    async def _is_server_running(self, server_name: str) -> bool:
        """Check if server is running by port."""
        server_info = self.servers[server_name]

        # Check by PID first
        if server_info.pid:
            try:
                process = psutil.Process(server_info.pid)
                if process.is_running():
                    return True
            except psutil.NoSuchProcess:
                server_info.pid = None

        # Check by port
        for conn in psutil.net_connections():
            if (
                conn.laddr.port == server_info.port
                and conn.status == psutil.CONN_LISTEN
            ):
                return True

        return False

    async def _health_check(self, server_name: str) -> bool:
        """Perform health check on MCP server."""
        if not self.session:
            await self.start_session()

        server_info = self.servers[server_name]

        try:
            # Try to connect to server
            url = f"http://localhost:{server_info.port}/health"
            async with self.session.get(url) as response:
                if response.status == 200:
                    server_info.last_health_check = time.time()
                    server_info.status = MCPServerStatus.RUNNING
                    return True
                else:
                    logger.warning(
                        f"Health check failed for {server_name}: HTTP {response.status}"
                    )
                    return False

        except Exception as e:
            logger.warning(f"Health check failed for {server_name}: {e}")
            return False

    async def _kill_process_by_port(self, port: int) -> None:
        """Kill process listening on specific port."""
        try:
            for conn in psutil.net_connections():
                if conn.laddr.port == port and conn.status == psutil.CONN_LISTEN:
                    try:
                        process = psutil.Process(conn.pid)
                        process.terminate()
                        logger.info(f"Terminated process {conn.pid} on port {port}")
                    except psutil.NoSuchProcess:
                        pass
        except Exception as e:
            logger.warning(f"Error killing process on port {port}: {e}")

    async def get_server_status(self, server_name: str) -> dict[str, Any]:
        """Get detailed status of MCP server."""
        if server_name not in self.servers:
            return {"error": f"Unknown server: {server_name}"}

        server_info = self.servers[server_name]

        # Perform health check
        is_healthy = await self._health_check(server_name)

        return {
            "name": server_info.name,
            "port": server_info.port,
            "pid": server_info.pid,
            "status": server_info.status.value,
            "healthy": is_healthy,
            "last_health_check": server_info.last_health_check,
            "error_message": server_info.error_message,
            "capabilities": server_info.capabilities,
            "auto_start": server_info.auto_start,
        }

    async def get_all_server_status(self) -> dict[str, dict[str, Any]]:
        """Get status of all MCP servers."""
        status = {}

        for server_name in self.servers:
            status[server_name] = await self.get_server_status(server_name)

        return status

    async def start_monitoring(self, interval: int = 60) -> None:
        """Start continuous health monitoring."""
        if self.monitoring_task and not self.monitoring_task.done():
            logger.warning("Monitoring already running")
            return

        self.monitoring_task = asyncio.create_task(self._monitoring_loop(interval))
        logger.info(f"Started health monitoring (interval: {interval}s)")

    async def stop_monitoring(self) -> None:
        """Stop health monitoring."""
        if self.monitoring_task:
            self.monitoring_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self.monitoring_task
            self.monitoring_task = None
            logger.info("Stopped health monitoring")

    async def _monitoring_loop(self, interval: int) -> None:
        """Continuous monitoring loop."""
        while True:
            try:
                for server_name, server_info in self.servers.items():
                    if server_info.status == MCPServerStatus.RUNNING:
                        is_healthy = await self._health_check(server_name)

                        if not is_healthy and server_info.auto_start:
                            logger.warning(
                                f"Server {server_name} failed health check, attempting restart"
                            )
                            await self.start_server(server_name)

                await asyncio.sleep(interval)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(interval)

    async def route_request(self, query: str) -> str:
        """Route request to appropriate MCP server based on content."""
        routing_rules = self.config.get("routing", {}).get("rules", [])
        fallback_server = self.config.get("routing", {}).get(
            "fallback", "sophia-ai-intelligence"
        )

        # Apply routing rules
        for rule in routing_rules:
            pattern = rule.get("pattern", "")
            server = rule.get("server", "")

            # Simple pattern matching (can be enhanced with regex)
            if any(keyword in query.lower() for keyword in pattern.split("|")):
                if server in self.servers:
                    logger.info(
                        f"Routing query to {server} based on pattern: {pattern}"
                    )
                    return server

        # Use fallback server
        logger.info(f"Using fallback server: {fallback_server}")
        return fallback_server

    def get_gemini_cli_config(self) -> dict[str, Any]:
        """Get Gemini CLI compatible configuration."""
        return {
            "mcpServers": self.config.get("mcpServers", {}),
            "globalSettings": self.config.get("globalSettings", {}),
            "routing": self.config.get("routing", {}),
            "workflows": self.config.get("workflows", {}),
            "security": self.config.get("security", {}),
            "performance": self.config.get("performance", {}),
        }

    async def __aenter__(self):
        """Async context manager entry."""
        await self.start_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.stop_monitoring()
        await self.close_session()


# CLI Interface
async def main():
    """Main CLI interface for Gemini MCP Integration."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Sophia AI - Gemini CLI MCP Integration"
    )
    parser.add_argument(
        "--config", default=".gemini/settings.json", help="Configuration file path"
    )
    parser.add_argument(
        "--action",
        choices=["start", "stop", "status", "monitor"],
        required=True,
        help="Action to perform",
    )
    parser.add_argument("--server", help="Specific server name (optional)")
    parser.add_argument(
        "--interval", type=int, default=60, help="Monitoring interval in seconds"
    )

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    async with GeminiMCPIntegration(args.config) as integration:
        if args.action == "start":
            if args.server:
                await integration.start_server(args.server)
            else:
                results = await integration.start_all_servers()
                for _server, _success in results.items():
                    pass

        elif args.action == "stop":
            if args.server:
                await integration.stop_server(args.server)
            else:
                results = await integration.stop_all_servers()
                for _server, _success in results.items():
                    pass

        elif args.action == "status":
            if args.server:
                await integration.get_server_status(args.server)
            else:
                await integration.get_all_server_status()

        elif args.action == "monitor":
            await integration.start_monitoring(args.interval)
            try:
                # Keep monitoring running
                while True:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                await integration.stop_monitoring()


if __name__ == "__main__":
    asyncio.run(main())
