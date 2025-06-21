"""Claude MCP Server
MCP server for Claude/Anthropic API integration with "Claude as Code" functionality,
refactored to use the BaseMCPServer.
"""

import asyncio
import json
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

from backend.integrations.claude_integration import claude_integration
from backend.mcp.base_mcp_server import BaseMCPServer, setup_logging
from infrastructure.esc.claude_secrets import claude_secret_manager


class ClaudeMCPServer(BaseMCPServer):
    """MCP Server for Claude/Anthropic API integration."""

    def __init__(self):
        super().__init__("claude")
        # The claude_integration is a singleton-like module, so we'll use it directly
        self.claude = claude_integration
        self.secret_manager = claude_secret_manager

    async def initialize_integration(self):
        """Initializes the Claude integration."""
        # The integration is initialized on first use, but we can check its status.
        if not self.claude._authenticated:
            await self.claude.initialize()
        self.integration_client = self.claude  # for compatibility with BaseMCPServer

    async def list_resources(self, request: ListResourcesRequest) -> List[Resource]:
        """Lists available Claude resources."""
        return [
            Resource(
                uri="claude://health", name="Claude Health", mimeType="application/json"
            ),
            Resource(
                uri="claude://config", name="Claude Config", mimeType="application/json"
            ),
            Resource(
                uri="claude://models", name="Claude Models", mimeType="application/json"
            ),
        ]

    async def get_resource(self, request: GetResourceRequest) -> str:
        """Gets a specific Claude resource."""
        uri = request.uri
        if uri == "claude://health":
            data = await self.claude.get_health_status()
        elif uri == "claude://config":
            config = await self.secret_manager.get_claude_config()
            if config and "api_key" in config:
                config["api_key"] = (
                    f"{config['api_key'][:8]}..." if config["api_key"] else None
                )
            data = config or {}
        elif uri == "claude://models":
            data = {
                "available_models": [
                    "claude-3-5-sonnet-20241022",
                    "claude-3-haiku-20240307",
                    "claude-3-opus-20240229",
                ],
                "default_model": self.claude.default_model,
            }
        else:
            data = {"error": f"Unknown resource: {uri}"}
        return json.dumps(data, indent=2)

    async def list_tools(self, request: ListToolsRequest) -> List[Tool]:
        """Lists available Claude tools for code generation and analysis."""
        return [
            Tool(
                name="generate_code",
                description="Generate code using Claude.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "prompt": {
                            "type": "string",
                            "description": "Description of code to generate",
                        },
                        "language": {
                            "type": "string",
                            "description": "Programming language",
                            "default": "python",
                        },
                    },
                    "required": ["prompt"],
                },
            ),
            Tool(
                name="analyze_code",
                description="Analyze code for review, explanation, or optimization.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "code": {"type": "string", "description": "Code to analyze"},
                        "analysis_type": {
                            "type": "string",
                            "enum": ["review", "explain", "optimize"],
                            "default": "review",
                        },
                    },
                    "required": ["code"],
                },
            ),
            Tool(
                name="refactor_code",
                description="Refactor code to meet a specific goal.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "code": {"type": "string", "description": "Code to refactor"},
                        "refactor_goal": {
                            "type": "string",
                            "description": "Goal of refactoring",
                            "default": "improve readability",
                        },
                    },
                    "required": ["code"],
                },
            ),
        ]

    async def call_tool(self, request: CallToolRequest) -> List[TextContent]:
        """Handles a Claude tool call."""
        tool_name = request.params.name
        args = request.params.arguments or {}
        result = None

        if tool_name == "generate_code":
            result = await self.claude.generate_code(
                prompt=args["prompt"], language=args.get("language", "python")
            )
        elif tool_name == "analyze_code":
            result = await self.claude.analyze_code(
                code=args["code"], analysis_type=args.get("analysis_type", "review")
            )
        elif tool_name == "refactor_code":
            result = await self.claude.refactor_code(
                code=args["code"],
                refactor_goal=args.get("refactor_goal", "improve readability"),
            )
        else:
            result = {"error": f"Unknown tool: {tool_name}"}

        # Convert dataclass to dict for JSON serialization if needed
        if hasattr(result, "__dict__"):
            result = result.__dict__

        return [
            TextContent(type="text", text=json.dumps(result, indent=2, default=str))
        ]


async def main():
    """Main entry point for the Claude MCP server."""
    setup_logging()
    server = ClaudeMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
