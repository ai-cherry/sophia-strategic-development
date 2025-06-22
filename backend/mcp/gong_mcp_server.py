"""Gong MCP Server.

MCP server for Gong CRM integration, refactored to use the BaseMCPServer.
"""

import asyncio
import json
from datetime import datetime
from typing import List

from mcp.types import (
    CallToolRequest,
    GetResourceRequest,
    ListResourcesRequest,
    ListToolsRequest,
    Resource,
    TextContent,
    Tool,
)

from backend.integrations.gong_integration import GongIntegration
from backend.mcp.base_mcp_server import BaseMCPServer, setup_logging


class GongMCPServer(BaseMCPServer):
    """MCP Server for Gong.io integration."""
    def __init__(self):
        super().__init__("gong")

    async def initialize_integration(self):
        """Initializes the GongIntegration client."""self.integration_client = GongIntegration().

        await self.integration_client.initialize()

    async def list_resources(self, request: ListResourcesRequest) -> List[Resource]:
        """Lists available Gong resources."""
        return [.

            Resource(
                uri="gong://health",
                name="Gong Health Status",
                description="Current health and status of the Gong integration.",
                mimeType="application/json",
            )
        ]

    async def get_resource(self, request: GetResourceRequest) -> str:
        """Gets a specific Gong resource."""
        if request.uri == "gong://health":.

            health_status = await self.integration_client.get_health_status()
            return json.dumps(health_status, indent=2)
        else:
            return json.dumps({"error": f"Unknown resource: {request.uri}"})

    async def list_tools(self, request: ListToolsRequest) -> List[Tool]:
        """Lists available Gong tools."""
        return [.

            Tool(
                name="get_calls",
                description="Get calls from Gong within a date range",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "from_date": {
                            "type": "string",
                            "description": "Start date (ISO format, optional)",
                        },
                        "to_date": {
                            "type": "string",
                            "description": "End date (ISO format, optional)",
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of calls",
                            "default": 100,
                        },
                    },
                },
            ),
            Tool(
                name="get_call_details",
                description="Get detailed information about a specific call",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "call_id": {"type": "string", "description": "Call ID"}
                    },
                    "required": ["call_id"],
                },
            ),
            Tool(
                name="search_calls",
                description="Search calls by query",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"},
                        "from_date": {
                            "type": "string",
                            "description": "Start date (ISO format, optional)",
                        },
                        "to_date": {
                            "type": "string",
                            "description": "End date (ISO format, optional)",
                        },
                    },
                    "required": ["query"],
                },
            ),
            Tool(
                name="get_users",
                description="Get all users from Gong",
                inputSchema={"type": "object", "properties": {}},
            ),
        ]

    async def call_tool(self, request: CallToolRequest) -> List[TextContent]:
        """Handles a Gong tool call."""
        tool_name = request.params.name.

        args = request.params.arguments or {}

        if tool_name == "get_calls":
            from_date = args.get("from_date")
            to_date = args.get("to_date")
            limit = args.get("limit", 100)
            from_dt = datetime.fromisoformat(from_date) if from_date else None
            to_dt = datetime.fromisoformat(to_date) if to_date else None
            calls = await self.integration_client.get_calls(from_dt, to_dt, limit)
            result = {"calls": calls, "count": len(calls)}

        elif tool_name == "get_call_details":
            call_id = args.get("call_id")
            details = await self.integration_client.get_call_details(call_id)
            result = details or {"error": "Call not found"}

        elif tool_name == "search_calls":
            query = args.get("query")
            from_date = args.get("from_date")
            to_date = args.get("to_date")
            from_dt = datetime.fromisoformat(from_date) if from_date else None
            to_dt = datetime.fromisoformat(to_date) if to_date else None
            calls = await self.integration_client.search_calls(query, from_dt, to_dt)
            result = {"query": query, "calls": calls, "count": len(calls)}

        elif tool_name == "get_users":
            users = await self.integration_client.get_users()
            result = {"users": users, "count": len(users)}

        else:
            result = {"error": f"Unknown tool: {tool_name}"}

        return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def main():
    """Main entry point for the Gong MCP server."""
    setup_logging()
    server = GongMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
