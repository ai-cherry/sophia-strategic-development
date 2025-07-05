#!/usr/bin/env python3
"""
Example MCP Server using Unified Base Class
"""

from typing import Any

from backend.mcp_servers.base.unified_mcp_base import (
    HealthCheckLevel,
    MCPServerConfig,
    UnifiedMCPServer,
)


class ExampleMCPServer(UnifiedMCPServer):
    """Example server implementation"""

    def __init__(self):
        config = MCPServerConfig(
            name="example",
            port=9999,
            version="1.0.0",
            enable_cortex=True,
            enable_caching=True,
        )
        super().__init__(config)

    def _setup_server_routes(self):
        """Set up server-specific routes"""

        @self.app.get("/example/test")
        async def test_endpoint():
            return {"message": "Example endpoint"}

    async def server_specific_init(self):
        """Server-specific initialization"""
        # Initialize your server components here
        pass

    async def server_specific_health_check(
        self, level: HealthCheckLevel
    ) -> dict[str, Any]:
        """Server-specific health checks"""
        return {"example_status": "operational", "custom_metric": 42}

    async def list_tools(self) -> list[dict[str, Any]]:
        """List available tools"""
        return [
            {
                "name": "example_tool",
                "description": "An example tool",
                "parameters": {"input": {"type": "string", "required": True}},
            }
        ]

    async def execute_tool(self, tool_name: str, arguments: dict[str, Any]) -> Any:
        """Execute a tool"""
        if tool_name == "example_tool":
            return {"result": f"Processed: {arguments.get('input')}"}
        else:
            raise ValueError(f"Unknown tool: {tool_name}")

    async def server_specific_cleanup(self):
        """Server-specific cleanup"""
        # Cleanup your server resources here
        pass


if __name__ == "__main__":
    import asyncio

    server = ExampleMCPServer()
    asyncio.run(server.start())
