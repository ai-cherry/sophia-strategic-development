"""Pulumi MCP Server
Exposes Pulumi automation as a tool for AI agents.
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

from backend.mcp.base_mcp_server import BaseMCPServer, setup_logging

logger = logging.getLogger(__name__)


class PulumiMCPServer(BaseMCPServer):
    """MCP Server for Pulumi. Enables AI agents to deploy and manage
    infrastructure by running Pulumi scripts.
    """

    def __init__(self):
        super().__init__("pulumi")
        # The 'integration_client' for this server is the ability to run shell commands.
        self.integration_client = "subprocess"

    async def initialize_integration(self):
        """No external integration to initialize for this server."""
        logger.info(
            "Pulumi MCP Server initialized. It will execute commands in the iac-toolkit container."
        )
        pass

    async def list_resources(self, request: ListResourcesRequest) -> List[Resource]:
        """Lists available Pulumi stacks as resources."""
        # In a real scenario, this could list .py files in infrastructure/pulumi/
        return [
            Resource(uri="pulumi://stack/dev", name="dev", mimeType="application/json"),
            Resource(
                uri="pulumi://stack/prod", name="prod", mimeType="application/json"
            ),
        ]

    async def get_resource(self, request: ReadResourceRequest) -> str:
        """Gets the status of a specific Pulumi stack."""
        stack_name = request.uri.split("/")[-1]

        # This is a conceptual implementation. A real one would use `pulumi stack export`.
        return json.dumps(
            {
                "stack_name": stack_name,
                "status": "Ready to be deployed.",
                "last_deployed": "N/A",
            }
        )

    async def list_tools(self, request: ListToolsRequest) -> List[Tool]:
        """Lists available Pulumi tools."""
        return [
            Tool(
                name="run_pulumi_up",
                description="Runs 'pulumi up' for a specific IaC script to deploy or update infrastructure.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "script_path": {
                            "type": "string",
                            "description": "The path to the Pulumi script to run (e.g., 'infrastructure/pulumi/snowflake_setup.py').",
                        },
                        "stack_name": {
                            "type": "string",
                            "description": "The name of the stack to deploy to (e.g., 'dev' or 'prod').",
                            "default": "dev",
                        },
                    },
                    "required": ["script_path"],
                },
            )
        ]

    async def call_tool(self, request: CallToolRequest) -> List[TextContent]:
        """Handles Pulumi tool calls."""
        tool_name = request.params.name
        arguments = request.params.arguments or {}

        if tool_name == "run_pulumi_up":
            script_path = arguments.get("script_path")
            stack_name = arguments.get("stack_name", "dev")

            if not script_path:
                result = {"error": "script_path is required."}
                return [TextContent(type="text", text=json.dumps(result))]

            # IMPORTANT: This command is executed inside the iac-toolkit container,
            # which has Pulumi and all necessary credentials configured.
            command = f"pulumi up --yes --stack {stack_name} -f {script_path}"

            # We use asyncio's subprocess to run the command asynchronously
            process = await asyncio.create_subprocess_shell(
                command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            if process.returncode == 0:
                result = {"success": True, "output": stdout.decode()}
            else:
                result = {"success": False, "error": stderr.decode()}

            return [TextContent(type="text", text=json.dumps(result))]

        return [
            TextContent(
                type="text", text=json.dumps({"error": f"Unknown tool: {tool_name}"})
            )
        ]


async def main():
    """Main entry point for the Pulumi MCP server."""
    setup_logging()
    server = PulumiMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
