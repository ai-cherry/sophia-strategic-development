"""Base MCP Server
Provides a standardized, class-based implementation for all MCP servers in Sophia AI.
"""

import logging
from abc import ABC, abstractmethod
from typing import List

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    ListResourcesRequest,
    ListToolsRequest,
    ReadResourceRequest,
    Resource,
    TextContent,
    Tool,
)


class BaseMCPServer(ABC):
    """Abstract base class for all Sophia AI MCP servers.

    This class provides a standardized structure for:
    - Initialization
    - Handler registration
    - State management (for integration clients)
    - Error handling
    - Consistent server startup logic
    """

    def __init__(self, server_name: str, server_version: str = "1.0.0"):
        self.server_name = server_name
        self.server_version = server_version
        self.server = Server(server_name)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.integration_client = None
        self._setup_handlers()

    @abstractmethod
    async def initialize_integration(self):
        """Abstract method to initialize the specific integration client for the server.
        This method should create and assign the client to self.integration_client.
        """
        pass

    @abstractmethod
    async def list_resources(self, request: ListResourcesRequest) -> List[Resource]:
        """Abstract method to list available resources for this server."""
        pass

    @abstractmethod
    async def get_resource(self, request: ReadResourceRequest) -> str:
        """Abstract method to get a specific resource.
        Should return a JSON string of the resource content.
        """
        pass

    @abstractmethod
    async def list_tools(self, request: ListToolsRequest) -> List[Tool]:
        """Abstract method to list available tools for this server."""
        pass

    @abstractmethod
    async def call_tool(self, request: CallToolRequest) -> List[TextContent]:
        """Abstract method to handle tool calls.
        Should return a list of TextContent objects.
        """
        pass

    def _setup_handlers(self):
        """Sets up the standard MCP handlers for this server.
        """

        # Register handlers using the server's handler decorators
        @self.server.list_resources()
        async def handle_list_resources(
            request: ListResourcesRequest,
        ) -> List[Resource]:
            return await self.list_resources(request)

        @self.server.read_resource()
        async def handle_get_resource(request: ReadResourceRequest) -> str:
            return await self.get_resource(request)

        @self.server.list_tools()
        async def handle_list_tools(request: ListToolsRequest) -> List[Tool]:
            return await self.list_tools(request)

        @self.server.call_tool()
        async def handle_call_tool(request: CallToolRequest) -> List[TextContent]:
            return await self.call_tool(request)

    async def run(self):
        """Initializes the integration and runs the MCP server.
        """
        self.logger.info(f"Starting {self.server_name} MCP Server...")

        try:
            await self.initialize_integration()
            self.logger.info("Integration initialized successfully.")
        except Exception as e:
            self.logger.error(f"Failed to initialize integration: {e}", exc_info=True)
            # Depending on the severity, you might want to exit
            # For now, we'll allow the server to start but tool calls will fail
            # until the integration is manually initialized or the server restarts.

        self.logger.info(
            f"{self.server_name} MCP Server running. Waiting for requests."
        )

        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name=self.server_name,
                    server_version=self.server_version,
                    capabilities=self.server.get_capabilities(
                        notification_options=None, experimental_capabilities=None
                    ),
                ),
            )


def setup_logging(level: int = logging.INFO):
    """Sets up logging for MCP servers.
    """
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()],
    )
