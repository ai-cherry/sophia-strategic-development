"""
Sophia AI - Unified Standardized MCP Server Base Class
The definitive base class for all MCP servers in the Sophia AI ecosystem
Using official Anthropic MCP SDK

Date: July 9, 2025
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from collections.abc import Sequence
from datetime import UTC, datetime
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool
from pydantic import BaseModel

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ServerConfig(BaseModel):
    """Configuration for MCP servers"""

    name: str
    version: str = "1.0.0"
    description: str = ""


class StandardizedMCPServer(ABC):
    """
    Standardized base class for all MCP servers
    Uses official Anthropic MCP SDK
    """

    def __init__(self, config: ServerConfig):
        self.config = config
        self.server = Server(config.name)
        self.start_time = datetime.now(UTC)
        self.request_count = 0
        self.error_count = 0

        # Set up logging
        self.logger = logging.getLogger(f"mcp.{config.name}")

        # Register handlers
        self._register_handlers()

    def _register_handlers(self):
        """Register MCP handlers"""

        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """List all available tools"""
            base_tools = [
                Tool(
                    name="health_check",
                    description="Check server health and status",
                    inputSchema={"type": "object", "properties": {}, "required": []},
                ),
                Tool(
                    name="get_server_info",
                    description="Get information about this server",
                    inputSchema={"type": "object", "properties": {}, "required": []},
                ),
            ]

            # Add custom tools from subclass
            custom_tools = await self.get_custom_tools()
            return base_tools + custom_tools

        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict) -> Sequence[TextContent]:
            """Handle tool calls"""
            self.request_count += 1

            try:
                # Handle base tools
                if name == "health_check":
                    result = await self._health_check()
                elif name == "get_server_info":
                    result = await self._get_server_info()
                else:
                    # Delegate to subclass
                    result = await self.handle_custom_tool(name, arguments)

                # Convert dict result to JSON text
                import json

                return [TextContent(type="text", text=json.dumps(result, indent=2))]

            except Exception as e:
                self.error_count += 1
                self.logger.error(f"Tool error: {e}")
                raise

    async def _health_check(self) -> dict[str, Any]:
        """Check server health"""
        uptime = (datetime.now(UTC) - self.start_time).total_seconds()

        return {
            "status": "healthy",
            "server": self.config.name,
            "version": self.config.version,
            "uptime_seconds": uptime,
            "request_count": self.request_count,
            "error_count": self.error_count,
            "timestamp": datetime.now(UTC).isoformat(),
        }

    async def _get_server_info(self) -> dict[str, Any]:
        """Get server information"""
        return {
            "name": self.config.name,
            "version": self.config.version,
            "description": self.config.description,
            "start_time": self.start_time.isoformat(),
        }

    @abstractmethod
    async def get_custom_tools(self) -> list[Tool]:
        """
        Return list of custom tools for this server
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
        """Run the server"""
        self.logger.info(
            f"Starting {self.config.name} MCP server v{self.config.version}"
        )

        try:
            options = self.server.create_initialization_options()
            async with stdio_server() as (read_stream, write_stream):
                await self.server.run(read_stream, write_stream, options)
        except Exception as e:
            self.logger.error(f"Server error: {e}")
            raise


# Example implementation for reference
class ExampleMCPServer(StandardizedMCPServer):
    """Example implementation showing how to use the base class"""

    def __init__(self):
        config = ServerConfig(
            name="example_server",
            version="1.0.0",
            description="Example MCP server implementation",
        )
        super().__init__(config)

    async def get_custom_tools(self) -> list[Tool]:
        """Define custom tools"""
        return [
            Tool(
                name="example_tool",
                description="Example tool that processes a query",
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
                "result": f"Processed: {query}",
                "timestamp": datetime.now(UTC).isoformat(),
            }
        else:
            raise ValueError(f"Unknown tool: {name}")


async def main():
    """Main entry point"""
    server = ExampleMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
