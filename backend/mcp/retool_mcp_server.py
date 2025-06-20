"""Retool MCP Server
Exposes Retool integration as tools for AI agents to build internal UIs.
"""

import asyncio
import json
from typing import List

from mcp.types import (
    CallToolRequest,
    ListResourcesRequest,
    ListToolsRequest,
    ReadResourceRequest,
    Resource,
    TextContent,
    Tool,
)

from backend.integrations.retool_integration import RetoolIntegration
from backend.mcp.base_mcp_server import BaseMCPServer, setup_logging


class RetoolMCPServer(BaseMCPServer):
    """MCP Server for Retool. Enables AI agents to build and manage
    Retool applications programmatically.
    """

    def __init__(self):
        super().__init__("retool")
        self.retool_integration = RetoolIntegration()

    async def initialize_integration(self):
        """Initializes the RetoolIntegration client."""
        await self.retool_integration.initialize()
        self.integration_client = self.retool_integration

    async def list_resources(self, request: ListResourcesRequest) -> List[Resource]:
        """Lists available Retool resources (conceptual)."""
        return [
            Resource(
                uri="retool://health",
                name="Retool Health Status",
                description="Health of the Retool integration.",
                mimeType="application/json",
            )
        ]

    async def get_resource(self, request: ReadResourceRequest) -> str:
        """Gets a specific Retool resource."""
        if request.uri == "retool://health":
            return json.dumps(
                {
                    "status": "healthy"
                    if self.retool_integration.initialized
                    else "degraded",
                    "initialized": self.retool_integration.initialized,
                }
            )
        return json.dumps({"error": f"Unknown resource: {request.uri}"})

    async def list_tools(self, request: ListToolsRequest) -> List[Tool]:
        """Lists available Retool tools."""
        return [
            Tool(
                name="create_admin_dashboard",
                description="Creates a new Retool application to serve as an admin dashboard.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "dashboard_name": {
                            "type": "string",
                            "description": "The name for the new dashboard (e.g., 'mcp_server_status').",
                        },
                        "description": {
                            "type": "string",
                            "description": "A brief description of the dashboard's purpose.",
                        },
                    },
                    "required": ["dashboard_name"],
                },
            ),
            Tool(
                name="add_component",
                description="Adds a pre-configured UI component (widget) to a Retool application.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "app_id": {
                            "type": "string",
                            "description": "The ID of the Retool application to modify.",
                        },
                        "component_type": {
                            "type": "string",
                            "description": "The type of component to add (e.g., 'Table', 'Chart').",
                        },
                        "name": {
                            "type": "string",
                            "description": "A name for the new component (e.g., 'mcp_status_table').",
                        },
                        "properties": {
                            "type": "object",
                            "description": "A dictionary of properties to configure the component.",
                        },
                    },
                    "required": ["app_id", "component_type", "name", "properties"],
                },
            ),
        ]

    async def call_tool(self, request: CallToolRequest) -> List[TextContent]:
        """Handles Retool tool calls."""
        tool_name = request.params.name
        arguments = request.params.arguments or {}

        try:
            if tool_name == "create_admin_dashboard":
                dashboard_name = arguments.get("dashboard_name")
                description = arguments.get(
                    "description", f"Admin dashboard for {dashboard_name}"
                )

                if not dashboard_name:
                    result = {"error": "dashboard_name is required."}
                else:
                    result = await self.retool_integration.create_app(
                        dashboard_name, description
                    )
            elif tool_name == "add_component":
                result = await self.retool_integration.add_component_to_app(
                    app_id=arguments.get("app_id"),
                    component_type=arguments.get("component_type"),
                    name=arguments.get("name"),
                    properties=arguments.get("properties", {}),
                )
            else:
                result = {"error": f"Unknown tool: {tool_name}"}

            return [TextContent(type="text", text=json.dumps(result))]

        except Exception as e:
            self.logger.error(f"Error calling tool {tool_name}: {e}", exc_info=True)
            return [TextContent(type="text", text=json.dumps({"error": str(e)}))]


async def main():
    """Main entry point for the Retool MCP server."""
    setup_logging()
    server = RetoolMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
