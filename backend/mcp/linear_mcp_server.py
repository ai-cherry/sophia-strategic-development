"""Linear MCP Server.

MCP server for Linear project management integration, refactored to use the BaseMCPServer.
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

from backend.integrations.linear_integration import linear_integration
from backend.mcp.base_mcp_server import BaseMCPServer, setup_logging


class LinearMCPServer(BaseMCPServer):
    """MCP Server for Linear project management integration."""
    def __init__(self):
        super().__init__("linear")
        # The linear_integration is a singleton-like module
        self.integration_client = linear_integration

    async def initialize_integration(self):
        """Initializes the Linear integration."""await self.integration_client.initialize().

    async def list_resources(self, request: ListResourcesRequest) -> List[Resource]:
        """Lists available Linear resources."""
        return [.

            Resource(
                uri="linear://health", name="Linear Health", mimeType="application/json"
            ),
            Resource(
                uri="linear://issues", name="Linear Issues", mimeType="application/json"
            ),
            Resource(
                uri="linear://projects",
                name="Linear Projects",
                mimeType="application/json",
            ),
            Resource(
                uri="linear://teams", name="Linear Teams", mimeType="application/json"
            ),
        ]

    async def get_resource(self, request: GetResourceRequest) -> str:
        """Gets a specific Linear resource."""
        uri = request.uri.

        data = None
        if uri == "linear://health":
            data = await self.integration_client.get_health_status()
        elif uri == "linear://issues":
            issues = await self.integration_client.get_issues()
            data = [issue.to_dict() for issue in issues]
        elif uri == "linear://projects":
            projects = await self.integration_client.get_projects()
            data = [project.to_dict() for project in projects]
        elif uri == "linear://teams":
            teams = await self.integration_client.get_teams()
            data = [team.to_dict() for team in teams]
        else:
            data = {"error": f"Unknown resource: {uri}"}

        return json.dumps(data, indent=2, default=str)

    async def list_tools(self, request: ListToolsRequest) -> List[Tool]:
        """Lists available Linear tools."""
        return [.

            Tool(
                name="create_issue",
                description="Create a new Linear issue.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "description": {"type": "string"},
                        "project_id": {"type": "string"},
                    },
                    "required": ["title", "description"],
                },
            ),
            Tool(
                name="update_issue",
                description="Update an existing Linear issue.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "issue_id": {"type": "string"},
                        "title": {"type": "string"},
                        "description": {"type": "string"},
                        "status": {"type": "string"},
                    },
                    "required": ["issue_id"],
                },
            ),
            Tool(
                name="search_issues",
                description="Search Linear issues by query.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "limit": {"type": "integer", "default": 20},
                    },
                    "required": ["query"],
                },
            ),
        ]

    async def call_tool(self, request: CallToolRequest) -> List[TextContent]:
        """Handles a Linear tool call."""
        tool_name = request.params.name.

        args = request.params.arguments or {}
        result = None

        if tool_name == "create_issue":
            issue = await self.integration_client.create_issue(
                title=args["title"],
                description=args["description"],
                project_id=args.get("project_id"),
            )
            result = issue.to_dict() if issue else {"error": "Failed to create issue"}

        elif tool_name == "update_issue":
            issue_id = args.pop("issue_id")
            updated_issue = await self.integration_client.update_issue(issue_id, args)
            result = (
                updated_issue.to_dict()
                if updated_issue
                else {"error": "Failed to update issue"}
            )

        elif tool_name == "search_issues":
            issues = await self.integration_client.search_issues(
                query=args["query"], limit=args.get("limit", 20)
            )
            result = [issue.to_dict() for issue in issues]

        else:
            result = {"error": f"Unknown tool: {tool_name}"}

        return [
            TextContent(type="text", text=json.dumps(result, indent=2, default=str))
        ]


async def main():
    """Main entry point for the Linear MCP server."""
    setup_logging()
    server = LinearMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
