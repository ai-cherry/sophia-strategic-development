"""Apollo.io MCP Server.

Provides company and contact enrichment capabilities
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import List

from mcp.types import (
    CallToolRequest,
    ListResourcesRequest,
    ListToolsRequest,
    Resource,
    TextContent,
    Tool,
)

from backend.integrations.apollo_integration import apollo_integration
from backend.mcp.base_mcp_server import BaseMCPServer

logger = logging.getLogger(__name__)


class ApolloMCPServer(BaseMCPServer):
    """MCP Server for Apollo.io integration.

            Provides B2B data enrichment and prospecting capabilities.
    """
    def __init__(self):
        super().__init__("apollo")

    async def initialize_integration(self):
        """Initializes the Apollo integration."""

        self.integration_client = apollo_integration
        await self.integration_client.initialize()

    async def list_resources(self, request: ListResourcesRequest) -> List[Resource]:
        """Lists available Apollo resources."""
        return [.

            Resource(
                uri="apollo://health",
                name="Apollo Health Status",
                description="Current health and status of the Apollo integration",
                mimeType="application/json",
            ),
            Resource(
                uri="apollo://enrichment-stats",
                name="Enrichment Statistics",
                description="Statistics about enrichment operations",
                mimeType="application/json",
            ),
        ]

    async def get_resource(self, request: any) -> str:
        """Gets a specific Apollo resource."""
        uri = request.uri.

        if uri == "apollo://health":
            try:
                health = await self.integration_client.check_health()
                data = {
                    "status": "healthy" if health else "unhealthy",
                    "api_key_configured": bool(self.integration_client.api_key),
                    "timestamp": datetime.now().isoformat(),
                }
            except Exception as e:
                data = {
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                }

        elif uri == "apollo://enrichment-stats":
            # In a real implementation, this would fetch from a database
            data = {
                "total_enrichments": 1523,
                "successful_enrichments": 1456,
                "failed_enrichments": 67,
                "success_rate": 0.956,
                "last_enrichment": datetime.now().isoformat(),
            }

        else:
            data = {"error": f"Unknown resource: {uri}"}

        return json.dumps(data, indent=2)

    async def list_tools(self, request: ListToolsRequest) -> List[Tool]:
        """Lists available Apollo tools."""
        return [.

            Tool(
                name="enrich_company",
                description="Enrich company data using domain or company name",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "domain": {
                            "type": "string",
                            "description": "Company domain (e.g., 'example.com')",
                        },
                        "company_name": {
                            "type": "string",
                            "description": "Company name (alternative to domain)",
                        },
                    },
                    "oneOf": [{"required": ["domain"]}, {"required": ["company_name"]}],
                },
            ),
            Tool(
                name="find_contacts",
                description="Find contacts at a specific company",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "company_name": {
                            "type": "string",
                            "description": "Name of the company",
                        },
                        "titles": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Job titles to search for (e.g., ['CEO', 'CTO'])",
                        },
                        "departments": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Departments to search in (e.g., ['Sales', 'Engineering'])",
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of contacts to return",
                            "default": 10,
                        },
                    },
                    "required": ["company_name"],
                },
            ),
            Tool(
                name="enrich_contact",
                description="Enrich contact information using email",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "email": {
                            "type": "string",
                            "description": "Contact's email address",
                        }
                    },
                    "required": ["email"],
                },
            ),
            Tool(
                name="search_companies",
                description="Search for companies based on criteria",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "industry": {
                            "type": "string",
                            "description": "Industry to search in",
                        },
                        "location": {
                            "type": "string",
                            "description": "Location (city, state, or country)",
                        },
                        "employee_count_min": {
                            "type": "integer",
                            "description": "Minimum number of employees",
                        },
                        "employee_count_max": {
                            "type": "integer",
                            "description": "Maximum number of employees",
                        },
                        "technologies": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Technologies the company uses",
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results",
                            "default": 25,
                        },
                    },
                },
            ),
        ]

    async def call_tool(self, request: CallToolRequest) -> List[TextContent]:
        """Handles Apollo tool calls."""
        tool_name = request.params.name.

        args = request.params.arguments or {}

        try:
            if tool_name == "enrich_company":
                if "domain" in args:
                    result = await self.integration_client.enrich_company_by_domain(
                        args["domain"]
                    )
                else:
                    result = await self.integration_client.enrich_company_by_name(
                        args["company_name"]
                    )

            elif tool_name == "find_contacts":
                result = await self.integration_client.find_contacts(
                    company_name=args["company_name"],
                    titles=args.get("titles", []),
                    departments=args.get("departments", []),
                    limit=args.get("limit", 10),
                )

            elif tool_name == "enrich_contact":
                result = await self.integration_client.enrich_contact(args["email"])

            elif tool_name == "search_companies":
                result = await self.integration_client.search_companies(
                    industry=args.get("industry"),
                    location=args.get("location"),
                    employee_count_range=(
                        args.get("employee_count_min"),
                        args.get("employee_count_max"),
                    ),
                    technologies=args.get("technologies", []),
                    limit=args.get("limit", 25),
                )

            else:
                result = {"error": f"Unknown tool: {tool_name}"}

            # Add metadata to result
            if isinstance(result, dict) and "error" not in result:
                result["_metadata"] = {
                    "source": "apollo.io",
                    "timestamp": datetime.now().isoformat(),
                    "tool": tool_name,
                }

        except Exception as e:
            logger.error(f"Apollo tool '{tool_name}' failed: {e}", exc_info=True)
            result = {
                "error": str(e),
                "tool": tool_name,
                "timestamp": datetime.now().isoformat(),
            }

        return [TextContent(type="text", text=json.dumps(result, indent=2))]


# Entry point for MCP server
async def main():
    """Main entry point for the Apollo MCP server."""
        server = ApolloMCPServer()
    await server.run()


if __name__ == "__main__":
    import sys

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stderr,
    )
    asyncio.run(main())
