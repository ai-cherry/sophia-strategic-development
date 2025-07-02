"""
Notion MCP Server Implementation
Provides knowledge management functionality
"""

import asyncio
import logging
from datetime import datetime
from backend.mcp_servers.base.enhanced_standardized_mcp_server import (
    EnhancedStandardizedMCPServer,
    MCPServerConfig,
    HealthCheckLevel
)

from typing import Any

from mcp import Server

from backend.core.auto_esc_config import get_config_value

logger = logging.getLogger(__name__)


class NotionMCPServer:
    """Notion MCP Server for knowledge management"""

    def __init__(self, port: int = 9104):
        self.name = "notion"
        self.version = "1.0.0"

        # Initialize MCP server
        self.mcp_server = Server(self.name, self.version)

        # Load API token
        self.api_token = get_config_value("notion.api_token", "")

        # Register tools and resources
        self._register_tools()
        self._register_resources()

    def _register_tools(self):
        """Register Notion MCP tools"""

        @self.mcp_server.tool("get_pages")
        async def get_pages(database_id: str = "") -> dict[str, Any]:
            """Get Notion pages"""
            try:
                # Mock implementation for now
                return {
                    "success": True,
                    "pages": [
                        {
                            "id": "page1",
                            "title": "Sophia AI Documentation",
                            "created_time": "2024-06-01T00:00:00Z",
                        }
                    ],
                }

            except Exception as e:
                logger.error(f"Get pages failed: {e}")
                return {"error": str(e)}

        @self.mcp_server.tool("create_page")
        async def create_page(
            title: str, content: str, parent_id: str = ""
        ) -> dict[str, Any]:
            """Create a new Notion page"""
            try:
                # Mock implementation for now
                return {
                    "success": True,
                    "page_id": "new_page_123",
                    "title": title,
                    "url": "https://notion.so/new_page_123",
                }

            except Exception as e:
                logger.error(f"Create page failed: {e}")
                return {"error": str(e)}

        @self.mcp_server.tool("health_check")
        async def health_check() -> dict[str, Any]:
            """Check Notion connection health"""
            try:
                has_token = bool(self.api_token)

                return {
                    "healthy": has_token,
                    "api_token_configured": has_token,
                    "timestamp": datetime.now().isoformat(),
                }

            except Exception as e:
                logger.error(f"Health check failed: {e}")
                return {"healthy": False, "error": str(e)}

    def _register_resources(self):
        """Register Notion MCP resources"""

        @self.mcp_server.resource("databases")
        async def get_databases() -> list[dict[str, Any]]:
            """Get Notion databases"""
            try:
                # Mock implementation
                return [
                    {"id": "db1", "title": "Projects"},
                    {"id": "db2", "title": "Tasks"},
                ]

            except Exception as e:
                logger.error(f"Get databases failed: {e}")
                return []

    async def start(self):
        """Start the Notion MCP server"""
        logger.info(f"🚀 Starting Notion MCP Server on port {self.port}")

        # Test connection
        health = await self.mcp_server.call_tool("health_check", {})
        logger.info(f"   Health check: {health}")

        logger.info("✅ Notion MCP Server started successfully")

    async def stop(self):
        """Stop the Notion MCP server"""
        logger.info("🛑 Stopping Notion MCP Server")


# Create server instance
notion_server = NotionMCPServer()

if __name__ == "__main__":
    asyncio.run(notion_server.start())


# --- Auto-inserted health endpoint ---
try:
    from fastapi import APIRouter
    router = APIRouter()
    @router.get("/health")
    async def health():
        return {"status": "ok"}
except ImportError:
    pass

    async def server_specific_init(self):
        """Server-specific initialization"""
        # TODO: Add server-specific initialization
        pass
        
    def _setup_server_routes(self):
        """Setup server-specific routes"""
        # Existing routes should be moved here
        pass
        
    async def check_server_health(self) -> bool:
        """Check server health"""
        # TODO: Implement health check
        return True
        
    async def server_specific_shutdown(self):
        """Server-specific shutdown"""
        # TODO: Add cleanup logic
        pass

