"""Lambda Labs MCP Server
MCP server for Lambda Labs GPU cloud integration, refactored to use the BaseMCPServer.
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

from backend.integrations.lambda_labs_integration import LambdaLabsIntegration
from backend.mcp.base_mcp_server import BaseMCPServer, setup_logging


class LambdaLabsMCPServer(BaseMCPServer):
    """MCP Server for Lambda Labs integration."""

    def __init__(self):
        super().__init__("lambda-labs")

    async def initialize_integration(self):
        """Initializes the LambdaLabsIntegration client."""
        self.integration_client = LambdaLabsIntegration()
        await self.integration_client.initialize()

    async def list_resources(self, request: ListResourcesRequest) -> List[Resource]:
        """Lists available Lambda Labs resources."""
        return [
            Resource(
                uri="lambdalabs://health",
                name="Lambda Labs Health Status",
                description="Current health and status of the Lambda Labs integration.",
                mimeType="application/json",
            ),
            Resource(
                uri="lambdalabs://instances",
                name="Lambda Labs Instances",
                description="List of active GPU instances.",
                mimeType="application/json",
            ),
        ]

    async def get_resource(self, request: GetResourceRequest) -> str:
        """Gets a specific Lambda Labs resource."""
        if request.uri == "lambdalabs://health":
            health_status = await self.integration_client.get_health_status()
            return json.dumps(health_status, indent=2)
        elif request.uri == "lambdalabs://instances":
            instances = await self.integration_client.get_instances()
            return json.dumps(
                {"instances": instances, "count": len(instances)}, indent=2
            )
        else:
            return json.dumps({"error": f"Unknown resource: {request.uri}"})

    async def list_tools(self, request: ListToolsRequest) -> List[Tool]:
        """Lists available Lambda Labs tools."""
        return [
            Tool(
                name="launch_instance",
                description="Launch a new GPU instance",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "instance_type": {
                            "type": "string",
                            "description": "Instance type name",
                        },
                        "region": {"type": "string", "description": "Region name"},
                        "ssh_key_names": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "SSH key names",
                        },
                        "name": {
                            "type": "string",
                            "description": "Optional instance name",
                        },
                    },
                    "required": ["instance_type", "region", "ssh_key_names"],
                },
            ),
            Tool(
                name="terminate_instance",
                description="Terminate an instance",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "instance_id": {"type": "string", "description": "Instance ID"}
                    },
                    "required": ["instance_id"],
                },
            ),
            Tool(
                name="get_instance_types",
                description="Get available GPU instance types",
                inputSchema={"type": "object", "properties": {}},
            ),
        ]

    async def call_tool(self, request: CallToolRequest) -> List[TextContent]:
        """Handles a Lambda Labs tool call."""
        tool_name = request.params.name
        args = request.params.arguments or {}

        if tool_name == "launch_instance":
            instance = await self.integration_client.launch_instance(
                instance_type=args.get("instance_type"),
                region=args.get("region"),
                ssh_key_names=args.get("ssh_key_names"),
                name=args.get("name"),
            )
            result = instance or {"error": "Failed to launch instance"}

        elif tool_name == "terminate_instance":
            success = await self.integration_client.terminate_instance(
                instance_id=args.get("instance_id")
            )
            result = {"success": success, "instance_id": args.get("instance_id")}

        elif tool_name == "get_instance_types":
            instance_types = await self.integration_client.get_instance_types()
            result = {"instance_types": instance_types, "count": len(instance_types)}

        else:
            result = {"error": f"Unknown tool: {tool_name}"}

        return [
            TextContent(type="text", text=json.dumps(result, indent=2, default=str))
        ]


async def main():
    """Main entry point for the Lambda Labs MCP server."""
    setup_logging()
    server = LambdaLabsMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
