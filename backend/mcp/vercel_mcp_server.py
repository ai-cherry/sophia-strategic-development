"""Vercel MCP Server.

MCP server for Vercel deployment integration
"""

import asyncio
import json
import logging
from typing import Any, Dict, List

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from ..integrations.vercel_integration import VercelIntegration

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create MCP server
server = Server("vercel")

# Global integration instance
vercel_integration = None


@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """List available Vercel tools."""
        return [
        Tool(
            name="get_projects",
            description="Get all Vercel projects",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="get_project",
            description="Get specific project details",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {"type": "string", "description": "Project ID"}
                },
                "required": ["project_id"],
            },
        ),
        Tool(
            name="get_deployments",
            description="Get deployments for a project or all deployments",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "Optional project ID",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of deployments to return",
                        "default": 20,
                    },
                },
            },
        ),
        Tool(
            name="get_deployment",
            description="Get specific deployment details",
            inputSchema={
                "type": "object",
                "properties": {
                    "deployment_id": {"type": "string", "description": "Deployment ID"}
                },
                "required": ["deployment_id"],
            },
        ),
        Tool(
            name="create_deployment",
            description="Create a new deployment",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Deployment name"},
                    "files": {
                        "type": "object",
                        "description": "Files to deploy (filename -> content mapping)",
                    },
                    "project_settings": {
                        "type": "object",
                        "description": "Optional project settings",
                    },
                },
                "required": ["name", "files"],
            },
        ),
        Tool(
            name="delete_deployment",
            description="Delete a deployment",
            inputSchema={
                "type": "object",
                "properties": {
                    "deployment_id": {"type": "string", "description": "Deployment ID"}
                },
                "required": ["deployment_id"],
            },
        ),
        Tool(
            name="get_domains",
            description="Get domains for a project or all domains",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "Optional project ID",
                    }
                },
            },
        ),
        Tool(
            name="add_domain",
            description="Add a domain to a project",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Domain name"},
                    "project_id": {"type": "string", "description": "Project ID"},
                },
                "required": ["name", "project_id"],
            },
        ),
        Tool(
            name="get_environment_variables",
            description="Get environment variables for a project",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {"type": "string", "description": "Project ID"}
                },
                "required": ["project_id"],
            },
        ),
        Tool(
            name="set_environment_variable",
            description="Set an environment variable for a project",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {"type": "string", "description": "Project ID"},
                    "key": {
                        "type": "string",
                        "description": "Environment variable key",
                    },
                    "value": {
                        "type": "string",
                        "description": "Environment variable value",
                    },
                    "target": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Target environments (production, preview, development)",
                    },
                },
                "required": ["project_id", "key", "value"],
            },
        ),
        Tool(
            name="get_logs",
            description="Get deployment logs",
            inputSchema={
                "type": "object",
                "properties": {
                    "deployment_id": {"type": "string", "description": "Deployment ID"}
                },
                "required": ["deployment_id"],
            },
        ),
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle Vercel tool calls."""global vercel_integration.

    try:
        # Initialize integration if needed
        if not vercel_integration:
            vercel_integration = VercelIntegration()
            await vercel_integration.initialize()

        if name == "get_projects":
            projects = await vercel_integration.get_projects()

            return [
                TextContent(
                    type="text",
                    text=json.dumps(
                        {"projects": projects, "count": len(projects)}, indent=2
                    ),
                )
            ]

        elif name == "get_project":
            project_id = arguments.get("project_id")
            if not project_id:
                return [
                    TextContent(
                        type="text", text=json.dumps({"error": "Project ID required"})
                    )
                ]

            project = await vercel_integration.get_project(project_id)

            return [
                TextContent(
                    type="text",
                    text=json.dumps(
                        project or {"error": "Project not found"}, indent=2
                    ),
                )
            ]

        elif name == "get_deployments":
            project_id = arguments.get("project_id")
            limit = arguments.get("limit", 20)

            deployments = await vercel_integration.get_deployments(project_id, limit)

            return [
                TextContent(
                    type="text",
                    text=json.dumps(
                        {"deployments": deployments, "count": len(deployments)},
                        indent=2,
                    ),
                )
            ]

        elif name == "get_deployment":
            deployment_id = arguments.get("deployment_id")
            if not deployment_id:
                return [
                    TextContent(
                        type="text",
                        text=json.dumps({"error": "Deployment ID required"}),
                    )
                ]

            deployment = await vercel_integration.get_deployment(deployment_id)

            return [
                TextContent(
                    type="text",
                    text=json.dumps(
                        deployment or {"error": "Deployment not found"}, indent=2
                    ),
                )
            ]

        elif name == "create_deployment":
            name = arguments.get("name")
            files = arguments.get("files")
            project_settings = arguments.get("project_settings")

            if not name or not files:
                return [
                    TextContent(
                        type="text",
                        text=json.dumps({"error": "Name and files required"}),
                    )
                ]

            deployment = await vercel_integration.create_deployment(
                name, files, project_settings
            )

            return [
                TextContent(
                    type="text",
                    text=json.dumps(
                        deployment or {"error": "Failed to create deployment"}, indent=2
                    ),
                )
            ]

        elif name == "delete_deployment":
            deployment_id = arguments.get("deployment_id")
            if not deployment_id:
                return [
                    TextContent(
                        type="text",
                        text=json.dumps({"error": "Deployment ID required"}),
                    )
                ]

            success = await vercel_integration.delete_deployment(deployment_id)

            return [
                TextContent(
                    type="text",
                    text=json.dumps(
                        {"success": success, "deployment_id": deployment_id}, indent=2
                    ),
                )
            ]

        elif name == "get_domains":
            project_id = arguments.get("project_id")
            domains = await vercel_integration.get_domains(project_id)

            return [
                TextContent(
                    type="text",
                    text=json.dumps(
                        {"domains": domains, "count": len(domains)}, indent=2
                    ),
                )
            ]

        elif name == "add_domain":
            name = arguments.get("name")
            project_id = arguments.get("project_id")

            if not name or not project_id:
                return [
                    TextContent(
                        type="text",
                        text=json.dumps({"error": "Name and project ID required"}),
                    )
                ]

            domain = await vercel_integration.add_domain(name, project_id)

            return [
                TextContent(
                    type="text",
                    text=json.dumps(
                        domain or {"error": "Failed to add domain"}, indent=2
                    ),
                )
            ]

        elif name == "get_environment_variables":
            project_id = arguments.get("project_id")
            if not project_id:
                return [
                    TextContent(
                        type="text", text=json.dumps({"error": "Project ID required"})
                    )
                ]

            env_vars = await vercel_integration.get_environment_variables(project_id)

            return [
                TextContent(
                    type="text",
                    text=json.dumps(
                        {"environment_variables": env_vars, "count": len(env_vars)},
                        indent=2,
                    ),
                )
            ]

        elif name == "set_environment_variable":
            project_id = arguments.get("project_id")
            key = arguments.get("key")
            value = arguments.get("value")
            target = arguments.get("target")

            if not project_id or not key or not value:
                return [
                    TextContent(
                        type="text",
                        text=json.dumps(
                            {"error": "Project ID, key, and value required"}
                        ),
                    )
                ]

            env_var = await vercel_integration.set_environment_variable(
                project_id, key, value, target
            )

            return [
                TextContent(
                    type="text",
                    text=json.dumps(
                        env_var or {"error": "Failed to set environment variable"},
                        indent=2,
                    ),
                )
            ]

        elif name == "get_logs":
            deployment_id = arguments.get("deployment_id")
            if not deployment_id:
                return [
                    TextContent(
                        type="text",
                        text=json.dumps({"error": "Deployment ID required"}),
                    )
                ]

            logs = await vercel_integration.get_logs(deployment_id)

            return [
                TextContent(
                    type="text",
                    text=json.dumps(
                        {"logs": logs, "deployment_id": deployment_id}, indent=2
                    ),
                )
            ]

        else:
            return [
                TextContent(
                    type="text", text=json.dumps({"error": f"Unknown tool: {name}"})
                )
            ]

    except Exception as e:
        logger.error(f"Error handling Vercel tool call {name}: {e}")
        return [TextContent(type="text", text=json.dumps({"error": str(e)}))]


async def main():
    """Main entry point for the Vercel MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="vercel",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=None, experimental_capabilities=None
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
