"""
MCP Version Compatibility Layer
Handles version differences between MCP SDK versions
"""

import importlib
import logging
from typing import Protocol, Any, Optional

logger = logging.getLogger(__name__)


class MCPServerProtocol(Protocol):
    """Protocol for MCP server interface"""
    async def handle_request(self, request: Any) -> Any: ...
    async def list_tools(self) -> list: ...


def get_mcp_server_class():
    """Dynamic MCP server class based on available version"""
    try:
        # Try newer version first (if available)
        from mcp.server import Server as MCPServer
        logger.info("Using MCP SDK (newer version)")
        return MCPServer
    except ImportError:
        try:
            # Fallback to older version
            from mcp_python.server import Server as MCPServer
            logger.info("Using mcp-python SDK (older version)")
            return MCPServer
        except ImportError:
            logger.error("No MCP SDK found. Please install mcp-python.")
            raise ImportError("No compatible MCP SDK available")


def get_mcp_types():
    """Get MCP types based on available version"""
    try:
        # Try newer version first
        from mcp import types
        return types
    except ImportError:
        try:
            # Fallback to older version
            from mcp_python import types
            return types
        except ImportError:
            logger.error("No MCP types found.")
            return None


class CompatibilityMCPServer:
    """Compatibility wrapper for MCP servers"""
    
    def __init__(self, name: str):
        self.name = name
        self.server_class = get_mcp_server_class()
        self.server = self.server_class(name)
        logger.info(f"Initialized MCP server: {name}")
    
    async def handle_request(self, request: Any) -> Any:
        """Handle request with compatibility layer"""
        try:
            return await self.server.handle_request(request)
        except AttributeError:
            # Handle version differences
            if hasattr(self.server, 'handle'):
                return await self.server.handle(request)
            else:
                raise NotImplementedError("Request handling not supported")
    
    async def list_tools(self) -> list:
        """List available tools with compatibility layer"""
        try:
            return await self.server.list_tools()
        except AttributeError:
            # Handle version differences
            if hasattr(self.server, 'get_tools'):
                return await self.server.get_tools()
            else:
                return []


# Export for use in MCP servers
MCPServer = get_mcp_server_class()
mcp_types = get_mcp_types()
