"""Docker MCP Server
Exposes Docker daemon management as tools for AI agents.
"""

import asyncio
import json
from typing import Any, List

import docker
from docker.errors import DockerException
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


class DockerMCPServer(BaseMCPServer):
    """MCP Server for Docker. Enables AI agents to inspect and manage
    the Docker environment they are running in.
    """

    def __init__(self):
        super().__init__("docker")
        self.docker_client = None

    async def initialize_integration(self):
        """Initializes the Docker client."""
        try:
            # Connect to the Docker daemon via the Unix socket
            self.docker_client = docker.from_env()
            # Verify the connection
            self.docker_client.ping()
            self.logger.info("Docker client initialized and connected successfully.")
        except DockerException as e:
            self.logger.error(f"Failed to connect to Docker daemon: {e}")
            self.logger.error(
                "Ensure the Docker socket is mounted correctly in the container."
            )
            raise
        self.integration_client = self.docker_client

    async def list_resources(self, request: ListResourcesRequest) -> List[Resource]:
        """Lists Docker resources like containers and images."""
        return [
            Resource(
                uri="docker://containers",
                name="Docker Containers",
                description="List of all running Docker containers.",
                mimeType="application/json",
            ),
            Resource(
                uri="docker://images",
                name="Docker Images",
                description="List of all Docker images.",
                mimeType="application/json",
            ),
        ]

    async def get_resource(self, request: ReadResourceRequest) -> str:
        """Gets a specific Docker resource."""
        uri = request.uri
        try:
            if uri == "docker://containers":
                containers = self.docker_client.containers.list()
                return json.dumps(
                    [
                        {
                            "id": c.short_id,
                            "name": c.name,
                            "image": c.image.tags,
                            "status": c.status,
                        }
                        for c in containers
                    ]
                )
            elif uri == "docker://images":
                images = self.docker_client.images.list()
                return json.dumps([{"id": i.short_id, "tags": i.tags} for i in images])
            else:
                return json.dumps({"error": f"Unknown resource: {uri}"})
        except DockerException as e:
            return json.dumps({"error": str(e)})

    async def list_tools(self, request: ListToolsRequest) -> List[Tool]:
        """Lists available Docker tools."""
        return [
            Tool(
                name="list_containers",
                description="Lists all containers, optionally including stopped ones.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "all": {
                            "type": "boolean",
                            "description": "Set to true to include stopped containers.",
                            "default": False,
                        }
                    },
                },
            ),
            Tool(
                name="inspect_container",
                description="Inspects a specific container to get detailed information.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "container_id": {
                            "type": "string",
                            "description": "The ID or name of the container to inspect.",
                        }
                    },
                    "required": ["container_id"],
                },
            ),
            Tool(
                name="get_container_logs",
                description="Retrieves logs from a specific container.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "container_id": {
                            "type": "string",
                            "description": "The ID or name of the container to get logs from.",
                        },
                        "tail": {
                            "type": "integer",
                            "description": "Number of lines to show from the end of the logs.",
                            "default": 100,
                        },
                    },
                    "required": ["container_id"],
                },
            ),
            Tool(
                name="get_container_stats",
                description="Gets real-time performance statistics for a container.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "container_id": {
                            "type": "string",
                            "description": "The ID or name of the container to get stats for.",
                        }
                    },
                    "required": ["container_id"],
                },
            ),
        ]

    async def call_tool(self, request: CallToolRequest) -> List[TextContent]:
        """Handles Docker tool calls."""
        tool_name = request.params.name
        args = request.params.arguments or {}

        try:
            if tool_name == "list_containers":
                containers = self.docker_client.containers.list(
                    all=args.get("all", False)
                )
                result = [
                    {
                        "id": c.short_id,
                        "name": c.name,
                        "image": c.image.tags,
                        "status": c.status,
                    }
                    for c in containers
                ]
            elif tool_name == "inspect_container":
                container_id = args.get("container_id")
                if not container_id:
                    result = {"error": "container_id is required"}
                else:
                    container = self.docker_client.containers.get(container_id)
                    result = container.attrs
            elif tool_name == "get_container_logs":
                container_id = args.get("container_id")
                if not container_id:
                    result = {"error": "container_id is required"}
                else:
                    container = self.docker_client.containers.get(container_id)
                    logs = container.logs(tail=args.get("tail", 100)).decode(
                        "utf-8", errors="ignore"
                    )
                    result = {"container_id": container.short_id, "logs": logs}
            elif tool_name == "get_container_stats":
                container_id = args.get("container_id")
                if not container_id:
                    result = {"error": "container_id is required"}
                else:
                    container = self.docker_client.containers.get(container_id)
                    stats = container.stats(stream=False)
                    result = {"container_id": container.short_id, "stats": stats}
            else:
                result = {"error": f"Unknown tool: {tool_name}"}

            # Use a helper to handle complex serialization
            return [TextContent(type="text", text=self._safe_json_dumps(result))]

        except DockerException as e:
            self.logger.error(f"Error calling tool {tool_name}: {e}", exc_info=True)
            return [TextContent(type="text", text=json.dumps({"error": str(e)}))]

    def _safe_json_dumps(self, data: Any) -> str:
        """Safely dumps data to JSON, handling non-serializable objects."""

        def default_serializer(o):
            if isinstance(o, (bytes, bytearray)):
                return o.decode("utf-8", errors="ignore")
            return f"<non-serializable: {type(o).__name__}>"

        return json.dumps(data, default=default_serializer, indent=2)


async def main():
    """Main entry point for the Docker MCP server."""
    setup_logging()
    server = DockerMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
