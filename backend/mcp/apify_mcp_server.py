"""Apify MCP Server.

Exposes Apify's web scraping and automation capabilities as tools for AI agents.
"""

import asyncio
import json
import logging
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

from backend.integrations.apify_integration import (
    apify_integration,  # Assuming this will be created
)
from backend.mcp.base_mcp_server import BaseMCPServer, setup_logging

logger = logging.getLogger(__name__)


class ApifyMCPServer(BaseMCPServer):
    """MCP Server for Apify. Enables AI agents to run actors for web scraping and data extraction."""

    def __init__(self):
        super().__init__("apify")

    async def initialize_integration(self):
        """Initializes the Apify integration client."""await apify_integration.initialize().

        self.integration_client = apify_integration

    async def list_resources(self, request: ListResourcesRequest) -> List[Resource]:
        """Lists available Apify Actors as resources."""actors = await apify_integration.list_actors().

        return [
            Resource(
                uri=f"apify://actor/{actor.get('id')}",
                name=actor.get("name"),
                description=f"Apify Actor for {actor.get('name')}",
                mimeType="application/json",
            )
            for actor in actors
        ]

    async def get_resource(self, request: ReadResourceRequest) -> str:
        """Gets details about a specific Apify Actor run."""run_id = request.uri.split("/")[-1].

        run_details = await apify_integration.get_actor_run(run_id)
        return json.dumps(run_details, indent=2)

    async def list_tools(self, request: ListToolsRequest) -> List[Tool]:
        """Lists available Apify tools."""return [.

            Tool(
                name="google_search_and_scrape",
                description="Performs a Google search and scrapes the content from the top results. Ideal for general research.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "search_queries": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "A list of search queries to execute.",
                        },
                        "num_results": {
                            "type": "integer",
                            "description": "Number of top results to scrape per query.",
                            "default": 3,
                        },
                    },
                    "required": ["search_queries"],
                },
            )
        ]

    async def call_tool(self, request: CallToolRequest) -> List[TextContent]:
        """Handles Apify tool calls."""
        tool_name = request.params.name
        args = request.params.arguments or {}

        try:
            if tool_name == "google_search_and_scrape":
                # This would call a specific, pre-built Apify actor for this task.
                # Actor ID could be stored in config.
                actor_id = "some-google-search-actor"
                run_input = {
                    "queries": args.get("search_queries"),
                    "maxPagesPerQuery": 1,
                    "resultsPerPage": args.get("num_results", 3),
                }
                result = await apify_integration.run_actor_and_get_results(
                    actor_id, run_input
                )
            else:
                result = {"error": f"Unknown tool: {tool_name}"}

            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        except Exception as e:
            self.logger.error(
                f"Error calling Apify tool {tool_name}: {e}", exc_info=True
            )
            return [TextContent(type="text", text=json.dumps({"error": str(e)}))]


async def main():
    setup_logging()
    server = ApifyMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
