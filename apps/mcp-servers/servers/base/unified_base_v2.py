"""
Sophia AI Unified MCP Server Base v2
Enhanced with health checks and port standardization

Date: July 12, 2025
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from datetime import UTC, datetime
from typing import Any, Optional

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class ServerConfig(BaseModel):
    """Enhanced server configuration"""
    name: str
    version: str = "2.0.0"
    port: int
    description: str = ""
    capabilities: list[str] = []
    tier: str = "SECONDARY"
    health_check_interval: int = 30
    

class UnifiedMCPServerV2(ABC):
    """Enhanced unified base class for all MCP servers"""
    
    def __init__(self, config: ServerConfig):
        self.config = config
        self.server = Server(config.name)
        self.start_time = datetime.now(UTC)
        self.request_count = 0
        self.error_count = 0
        self.last_health_check = None
        self.is_healthy = True
        
        # Set up logging
        self.logger = logging.getLogger(f"mcp.{config.name}")
        
        # Register handlers
        self._register_handlers()
        
        # Start health check loop
        asyncio.create_task(self._health_check_loop())
    
    def _register_handlers(self):
        """Register MCP handlers with health checks"""
        
        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """List all available tools"""
            base_tools = [
                Tool(
                    name="health",
                    description="Get server health status",
                    inputSchema={"type": "object", "properties": {}, "required": []},
                ),
                Tool(
                    name="ready",
                    description="Check if server is ready",
                    inputSchema={"type": "object", "properties": {}, "required": []},
                ),
                Tool(
                    name="metrics",
                    description="Get server metrics",
                    inputSchema={"type": "object", "properties": {}, "required": []},
                ),
            ]
            
            custom_tools = await self.get_custom_tools()
            return base_tools + custom_tools
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict) -> Sequence[TextContent]:
            """Handle tool calls with error tracking"""
            try:
                self.request_count += 1
                
                # Handle base tools
                if name == "health":
                    return [TextContent(
                        type="text",
                        text=json.dumps(await self.get_health())
                    )]
                elif name == "ready":
                    return [TextContent(
                        type="text",
                        text=json.dumps({"ready": self.is_healthy})
                    )]
                elif name == "metrics":
                    return [TextContent(
                        type="text",
                        text=json.dumps(await self.get_metrics())
                    )]
                
                # Handle custom tools
                result = await self.handle_custom_tool(name, arguments)
                return [TextContent(type="text", text=json.dumps(result))]
                
            except Exception as e:
                self.error_count += 1
                self.logger.error(f"Tool error: {e}")
                raise
    
    async def _health_check_loop(self):
        """Periodic health check loop"""
        while True:
            try:
                await asyncio.sleep(self.config.health_check_interval)
                self.is_healthy = await self.check_health()
                self.last_health_check = datetime.now(UTC)
            except Exception as e:
                self.logger.error(f"Health check error: {e}")
                self.is_healthy = False
    
    async def get_health(self) -> dict[str, Any]:
        """Get health status"""
        uptime = (datetime.now(UTC) - self.start_time).total_seconds()
        
        return {
            "status": "healthy" if self.is_healthy else "unhealthy",
            "uptime_seconds": uptime,
            "request_count": self.request_count,
            "error_count": self.error_count,
            "error_rate": self.error_count / max(1, self.request_count),
            "last_health_check": self.last_health_check.isoformat() if self.last_health_check else None,
            "port": self.config.port,
            "version": self.config.version
        }
    
    async def get_metrics(self) -> dict[str, Any]:
        """Get server metrics"""
        return {
            "server": self.config.name,
            "port": self.config.port,
            "capabilities": self.config.capabilities,
            "tier": self.config.tier,
            "requests": {
                "total": self.request_count,
                "errors": self.error_count,
                "success_rate": 1 - (self.error_count / max(1, self.request_count))
            },
            "health": await self.get_health()
        }
    
    @abstractmethod
    async def get_custom_tools(self) -> list[Tool]:
        """Get custom tools for this server"""
        pass
    
    @abstractmethod
    async def handle_custom_tool(self, name: str, arguments: dict) -> dict[str, Any]:
        """Handle custom tool calls"""
        pass
    
    @abstractmethod
    async def check_health(self) -> bool:
        """Check if server is healthy"""
        pass
    
    async def run(self):
        """Run the server"""
        self.logger.info(f"Starting {self.config.name} on port {self.config.port}")
        self.logger.info(f"Capabilities: {', '.join(self.config.capabilities)}")
        
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )
