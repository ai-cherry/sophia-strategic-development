"""Airbyte MCP Server.

Exposes the Airbyte integration to the Sophia AI system via MCP.
"""

import asyncio
import json
from typing import List

from mcp.types import CallToolRequest, ListToolsRequest, Resource, TextContent, Tool

from backend.integrations.airbyte_integration import airbyte_integration
from backend.mcp.base_mcp_server import BaseMCPServer, setup_logging


class AirbyteMCPServer(BaseMCPServer):
    """MCP Server for Airbyte."""
    def __init__(self):
        super().__init__("airbyte")

    async def initialize_integration(self):
        """Initializes the Airbyte integration client."""self.integration_client = airbyte_integration.

        await self.integration_client.initialize()

    async def list_resources(self, request: any) -> List[Resource]:
        """Airbyte server is tool-focused."""
        return [].

    async def get_resource(self, request: any) -> str:
        """Airbyte server is tool-focused."""
        return json.dumps(.

            {"error": "This server does not provide resources, only tools."}
        )

    async def list_tools(self, request: ListToolsRequest) -> List[Tool]:
        """Lists the available Airbyte tools."""
        return [.

            Tool(
                name="trigger_sync",
                description="Triggers a data synchronization job for a specific connection.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "connection_id": {
                            "type": "string",
                            "description": "The Airbyte connection ID to sync.",
                        }
                    },
                    "required": ["connection_id"],
                },
            ),
            Tool(
                name="get_job_status",
                description="Checks the status of a specific Airbyte synchronization job.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "job_id": {
                            "type": "integer",
                            "description": "The Airbyte job ID to check.",
                        }
                    },
                    "required": ["job_id"],
                },
            ),
        ]

    async def call_tool(self, request: CallToolRequest) -> List[TextContent]:
        """Handles an Airbyte tool call."""
        tool_name = request.params.name.

        args = request.params.arguments or {}
        result = None

        if tool_name == "trigger_sync":
            result = await self.integration_client.trigger_sync(args["connection_id"])
        elif tool_name == "get_job_status":
            result = await self.integration_client.get_job_status(args["job_id"])
        else:
            result = {"error": f"Unknown tool: {tool_name}"}

        if result is None:
            result = {
                "error": f"Tool call for '{tool_name}' failed or returned no data."
            }

        return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def main():
    """Main entry point for the Airbyte MCP server."""
    setup_logging()
    server = AirbyteMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
