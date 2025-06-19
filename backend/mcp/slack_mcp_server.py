"""
Slack MCP Server
MCP server for Slack integration, refactored to use the BaseMCPServer.
"""

import asyncio
import json
import logging
from typing import Any, Dict, List
from datetime import datetime

import aiohttp
from mcp.types import Resource, Tool, TextContent, CallToolRequest, GetResourceRequest, ListResourcesRequest, ListToolsRequest

from backend.mcp.base_mcp_server import BaseMCPServer, setup_logging
from backend.integrations.slack.sophia_slack_bot import sophia_slack_bot
from backend.core.integration_registry import integration_registry

class SlackMCPServer(BaseMCPServer):
    """
    MCP Server for Slack integration.
    """

    def __init__(self):
        super().__init__("slack")
        self.slack_bot = sophia_slack_bot
        self.http_session = None

    async def initialize_integration(self):
        """Initializes the Slack bot and HTTP session."""
        self.integration_client = self.slack_bot # For base class compatibility
        if not self.slack_bot.socket_client:
            # The bot is designed to be run separately, so we just check for its client.
            self.logger.warning("Sophia Slack Bot client not running. Some tools may fail.")
        self.http_session = aiohttp.ClientSession()

    async def list_resources(self, request: ListResourcesRequest) -> List[Resource]:
        """Lists available Slack resources."""
        return [
            Resource(uri="slack://channels", name="Slack Channels", mimeType="application/json"),
            Resource(uri="slack://bot/status", name="Slack Bot Status", mimeType="application/json"),
        ]

    async def get_resource(self, request: GetResourceRequest) -> str:
        """Gets a specific Slack resource."""
        uri = request.uri
        if uri == "slack://channels":
            channels = await self.slack_bot.client.conversations_list()
            data = {"channels": channels.get("channels", []), "timestamp": datetime.now().isoformat()}
        elif uri == "slack://bot/status":
            data = {
                "bot_active": self.slack_bot.socket_client is not None,
                "mcp_integration": self.slack_bot.mcp_integration,
                "timestamp": datetime.now().isoformat()
            }
        else:
            data = {"error": f"Unknown resource: {uri}"}
        return json.dumps(data, indent=2)

    async def list_tools(self, request: ListToolsRequest) -> List[Tool]:
        """Lists available Slack tools."""
        return [
            Tool(
                name="send_message",
                description="Send a message to a Slack channel.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "channel": {"type": "string"},
                        "message": {"type": "string"},
                        "blocks": {"type": "array"}
                    }, "required": ["channel", "message"]}
            ),
            Tool(
                name="check_system_health",
                description="Check system health and format for Slack.",
                inputSchema={
                    "type": "object",
                    "properties": {"detailed": {"type": "boolean", "default": False}}
                }
            ),
        ]

    async def call_tool(self, request: CallToolRequest) -> List[TextContent]:
        """Handles a Slack tool call."""
        tool_name = request.params.name
        args = request.params.arguments or {}
        result = None

        if tool_name == "send_message":
            response = await self.slack_bot.client.chat_postMessage(
                channel=args["channel"], text=args["message"], blocks=args.get("blocks")
            )
            result = {"success": True, "message_ts": response.get("ts"), "channel": response.get("channel")}
        
        elif tool_name == "check_system_health":
            health_status = await integration_registry.health_check_all()
            if args.get("detailed", False):
                result = {"health_status": health_status, "timestamp": datetime.now().isoformat()}
            else:
                result = {
                    "overall_health": all(health_status.values()),
                    "healthy_services": sum(1 for v in health_status.values() if v),
                    "total_services": len(health_status)
                }
        else:
            result = {"error": f"Unknown tool: {tool_name}"}

        return [TextContent(type="text", text=json.dumps(result, indent=2))]

async def main():
    """Main entry point for the Slack MCP server."""
    setup_logging()
    server = SlackMCPServer()
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())

