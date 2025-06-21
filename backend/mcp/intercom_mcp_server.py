"""Intercom MCP Server - Placeholder"""

import json
from typing import List

from mcp.types import CallToolRequest, ListToolsRequest, Resource, TextContent, Tool

from backend.mcp.base_mcp_server import BaseMCPServer, setup_logging


class IntercomMCPServer(BaseMCPServer):
    def __init__(self):
        super().__init__("intercom")

    async def initialize_integration(self):
        self.integration_client = "intercom_placeholder"
        self.logger.info(
            "Intercom MCP Server initialized with placeholder integration."
        )

    async def list_resources(self, request: any) -> List[Resource]:
        return []

    async def get_resource(self, request: any) -> str:
        return json.dumps({"error": "Not implemented."})

    async def list_tools(self, request: ListToolsRequest) -> List[Tool]:
        return [
            Tool(
                name="get_conversation",
                description="Get a support conversation by ID (placeholder).",
                inputSchema={},
            ),
            Tool(
                name="create_ticket",
                description="Create a new support ticket (placeholder).",
                inputSchema={},
            ),
        ]

    async def call_tool(self, request: CallToolRequest) -> List[TextContent]:
        return [
            TextContent(
                type="text",
                text=json.dumps(
                    {"status": "placeholder", "message": "Not implemented."}
                ),
            )
        ]


async def main():
    setup_logging()
    server = IntercomMCPServer()
    await server.run()


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
