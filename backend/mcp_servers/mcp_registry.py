"""
Sophia AI MCP Server Registry
Central registry for managing all MCP servers
"""

import asyncio
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

from .sophia_mcp_base import SophiaMCPServer, MCPServerHealth, create_mcp_server

logger = logging.getLogger(__name__)


@dataclass
class MCPServerConfig:
    """Configuration for an MCP server"""

    name: str
    type: str
    port: int
    enabled: bool = True
    auto_start: bool = True
    health_check_interval: int = 60


class MCPServerRegistry:
    """Registry for managing all MCP servers"""

    def __init__(self):
        self.servers: Dict[str, SophiaMCPServer] = {}
        self.configs: Dict[str, MCPServerConfig] = {}
        self.health_status: Dict[str, MCPServerHealth] = {}

        # Load default configurations
        self._load_default_configs()

    def _load_default_configs(self):
        """Load default server configurations"""
        default_configs = [
            MCPServerConfig("snowflake", "snowflake", 9100),
            MCPServerConfig("hubspot", "hubspot", 9101),
            MCPServerConfig("slack", "slack", 9102),
            MCPServerConfig("github", "github", 9103),
            MCPServerConfig("notion", "notion", 9104),
        ]

        for config in default_configs:
            self.configs[config.name] = config

    async def register_server(self, config: MCPServerConfig):
        """Register a new MCP server"""
        logger.info(f"📋 Registering MCP server: {config.name}")

        try:
            # Create server instance
            server = create_mcp_server(config.type, port=config.port)
            self.servers[config.name] = server
            self.configs[config.name] = config

            # Start server if auto_start is enabled
            if config.auto_start and config.enabled:
                await server.start()

            logger.info(f"✅ Registered {config.name} MCP server")

        except Exception as e:
            logger.error(f"❌ Failed to register {config.name}: {e}")
            raise

    async def start_server(self, name: str):
        """Start a specific MCP server"""
        if name not in self.servers:
            raise ValueError(f"Server {name} not found in registry")

        server = self.servers[name]
        await server.start()
        logger.info(f"🚀 Started {name} MCP server")

    async def stop_server(self, name: str):
        """Stop a specific MCP server"""
        if name not in self.servers:
            raise ValueError(f"Server {name} not found in registry")

        server = self.servers[name]
        await server.stop()
        logger.info(f"🛑 Stopped {name} MCP server")

    async def start_all_servers(self):
        """Start all enabled MCP servers"""
        logger.info("🚀 Starting all enabled MCP servers")

        for name, config in self.configs.items():
            if config.enabled and config.auto_start:
                try:
                    if name not in self.servers:
                        await self.register_server(config)
                    else:
                        await self.start_server(name)
                except Exception as e:
                    logger.error(f"❌ Failed to start {name}: {e}")

    async def stop_all_servers(self):
        """Stop all MCP servers"""
        logger.info("🛑 Stopping all MCP servers")

        for name in self.servers:
            try:
                await self.stop_server(name)
            except Exception as e:
                logger.error(f"❌ Failed to stop {name}: {e}")

    async def health_check_all(self):
        """Perform health check on all servers"""
        logger.info("🔍 Performing health check on all MCP servers")

        for name, server in self.servers.items():
            try:
                health = await server.health_check()
                self.health_status[name] = health
                logger.info(f"   {name}: {health.status}")
            except Exception as e:
                logger.error(f"❌ Health check failed for {name}: {e}")

    def get_server_status(self) -> Dict[str, Dict]:
        """Get status of all servers"""
        status = {}

        for name, config in self.configs.items():
            server_info = {
                "config": asdict(config),
                "registered": name in self.servers,
                "health": (
                    asdict(self.health_status.get(name))
                    if name in self.health_status
                    else None
                ),
            }
            status[name] = server_info

        return status

    async def start_health_monitoring(self):
        """Start background health monitoring"""
        logger.info("🔍 Starting MCP server health monitoring")

        async def health_monitor():
            while True:
                try:
                    await self.health_check_all()
                    await asyncio.sleep(60)  # Check every minute
                except Exception as e:
                    logger.error(f"Health monitoring error: {e}")
                    await asyncio.sleep(60)

        # Start monitoring task
        asyncio.create_task(health_monitor())


# Global registry instance
mcp_registry = MCPServerRegistry()
