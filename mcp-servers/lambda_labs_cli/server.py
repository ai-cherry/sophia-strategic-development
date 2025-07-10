#!/usr/bin/env python3
"""
Sophia AI Lambda Labs CLI MCP Server
Provides GPU instance management and monitoring
Using official Anthropic MCP SDK

Date: July 10, 2025
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Optional

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

import logging

import httpx
from base.unified_standardized_base import (
    ServerConfig,
    ToolDefinition,
    ToolParameter,
)
from base.unified_standardized_base import (
    UnifiedStandardizedMCPServer as StandardizedMCPServer,
)

from backend.core.auto_esc_config import get_config_value

logger = logging.getLogger(__name__)


class LambdaLabsCLIMCPServer(StandardizedMCPServer):
    """Lambda Labs CLI MCP Server for GPU management"""

    def __init__(self):
        config = ServerConfig(
            name="lambda_labs_cli",
            version="1.0.0",
            port=9016,
            capabilities=["GPU_MANAGEMENT", "INSTANCE_CONTROL", "MONITORING"],
            tier="PRIMARY",
        )
        super().__init__(config)

        # Lambda Labs configuration
        self.api_key = get_config_value("lambda_api_key")
        self.api_url = "https://cloud.lambdalabs.com/api/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def get_tool_definitions(self) -> list[ToolDefinition]:
        """Define Lambda Labs CLI tools"""
        return [
            ToolDefinition(
                name="list_instances",
                description="List all Lambda Labs GPU instances",
                parameters=[
                    ToolParameter(
                        name="status",
                        type="string",
                        description="Filter by status (active, stopped, all)",
                        required=False,
                    ),
                ],
            ),
            ToolDefinition(
                name="create_instance",
                description="Create a new GPU instance",
                parameters=[
                    ToolParameter(
                        name="instance_type",
                        type="string",
                        description="Instance type (e.g., gpu_1x_a100)",
                        required=True,
                    ),
                    ToolParameter(
                        name="name",
                        type="string",
                        description="Instance name",
                        required=True,
                    ),
                    ToolParameter(
                        name="region",
                        type="string",
                        description="Region for deployment",
                        required=False,
                    ),
                ],
            ),
            ToolDefinition(
                name="stop_instance",
                description="Stop a running instance",
                parameters=[
                    ToolParameter(
                        name="instance_id",
                        type="string",
                        description="Instance ID to stop",
                        required=True,
                    ),
                ],
            ),
            ToolDefinition(
                name="start_instance",
                description="Start a stopped instance",
                parameters=[
                    ToolParameter(
                        name="instance_id",
                        type="string",
                        description="Instance ID to start",
                        required=True,
                    ),
                ],
            ),
            ToolDefinition(
                name="get_instance_details",
                description="Get detailed information about an instance",
                parameters=[
                    ToolParameter(
                        name="instance_id",
                        type="string",
                        description="Instance ID",
                        required=True,
                    ),
                ],
            ),
            ToolDefinition(
                name="execute_command",
                description="Execute a command on an instance via SSH",
                parameters=[
                    ToolParameter(
                        name="instance_id",
                        type="string",
                        description="Instance ID",
                        required=True,
                    ),
                    ToolParameter(
                        name="command",
                        type="string",
                        description="Command to execute",
                        required=True,
                    ),
                ],
            ),
        ]

    async def handle_tool_call(
        self, tool_name: str, arguments: dict[str, Any]
    ) -> dict[str, Any]:
        """Handle Lambda Labs CLI tool calls"""

        if tool_name == "list_instances":
            return await self._list_instances(**arguments)
        elif tool_name == "create_instance":
            return await self._create_instance(**arguments)
        elif tool_name == "stop_instance":
            return await self._stop_instance(**arguments)
        elif tool_name == "start_instance":
            return await self._start_instance(**arguments)
        elif tool_name == "get_instance_details":
            return await self._get_instance_details(**arguments)
        elif tool_name == "execute_command":
            return await self._execute_command(**arguments)
        else:
            raise ValueError(f"Unknown tool: {tool_name}")

    async def _make_api_request(
        self, method: str, endpoint: str, data: Optional[dict[str, Any]] = None
    ) -> dict[str, Any]:
        """Make a request to Lambda Labs API"""
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method,
                f"{self.api_url}{endpoint}",
                headers=self.headers,
                json=data,
            )
            response.raise_for_status()
            return response.json()

    def _run_cli_command(self, args: list[str]) -> dict[str, Any]:
        """Run Lambda Labs CLI command"""
        cmd = ["lambda-cloud"] + args

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                env={**os.environ, "LAMBDA_API_KEY": self.api_key},
            )

            # Try to parse JSON output
            try:
                return json.loads(result.stdout)
            except json.JSONDecodeError:
                return {"output": result.stdout, "success": True}

        except subprocess.CalledProcessError as e:
            return {
                "error": e.stderr or str(e),
                "success": False,
                "return_code": e.returncode,
            }

    async def _list_instances(self, status: str = "all") -> dict[str, Any]:
        """List Lambda Labs instances"""

        # Get instances via API
        instances_data = await self._make_api_request("GET", "/instances")
        instances = instances_data.get("data", [])

        # Filter by status if requested
        if status != "all":
            instances = [
                i for i in instances if i.get("status", "").lower() == status.lower()
            ]

        # Format instance data
        formatted_instances = []
        for instance in instances:
            formatted_instances.append(
                {
                    "id": instance.get("id"),
                    "name": instance.get("name"),
                    "type": instance.get("instance_type", {}).get("name", ""),
                    "status": instance.get("status"),
                    "ip": instance.get("ip", ""),
                    "region": instance.get("region", {}).get("name", ""),
                    "created_at": instance.get("created_at"),
                    "gpu_type": instance.get("instance_type", {}).get("gpu_type", ""),
                    "gpu_count": instance.get("instance_type", {}).get("gpu_count", 0),
                }
            )

        return {
            "instances": formatted_instances,
            "count": len(formatted_instances),
            "filter": {"status": status},
        }

    async def _create_instance(
        self, instance_type: str, name: str, region: Optional[str] = None
    ) -> dict[str, Any]:
        """Create a new GPU instance"""

        data = {
            "instance_type_name": instance_type,
            "name": name,
            "ssh_key_names": ["sophia-ai-key"],  # Should be configured
        }

        if region:
            data["region_name"] = region

        # Create instance via API
        result = await self._make_api_request(
            "POST", "/instance-operations/launch", data
        )

        instance_id = result.get("data", {}).get("instance_ids", [None])[0]

        if instance_id:
            return {
                "created": True,
                "instance_id": instance_id,
                "name": name,
                "type": instance_type,
                "message": f"Instance '{name}' created successfully",
            }
        else:
            return {
                "created": False,
                "error": "Failed to create instance",
                "details": result,
            }

    async def _stop_instance(self, instance_id: str) -> dict[str, Any]:
        """Stop a running instance"""

        # Stop instance via API
        result = await self._make_api_request(
            "POST", "/instance-operations/terminate", {"instance_ids": [instance_id]}
        )

        terminated = result.get("data", {}).get("terminated_instances", [])

        if instance_id in terminated:
            return {
                "stopped": True,
                "instance_id": instance_id,
                "message": f"Instance {instance_id} stopped successfully",
            }
        else:
            return {
                "stopped": False,
                "instance_id": instance_id,
                "error": "Failed to stop instance",
                "details": result,
            }

    async def _start_instance(self, instance_id: str) -> dict[str, Any]:
        """Start a stopped instance"""

        # Lambda Labs doesn't support starting stopped instances
        # Instances are terminated, not stopped
        return {
            "started": False,
            "instance_id": instance_id,
            "error": "Lambda Labs instances cannot be restarted after termination",
            "suggestion": "Create a new instance instead",
        }

    async def _get_instance_details(self, instance_id: str) -> dict[str, Any]:
        """Get detailed instance information"""

        # Get instance details via API
        instances_data = await self._make_api_request("GET", "/instances")
        instances = instances_data.get("data", [])

        # Find the specific instance
        instance = None
        for i in instances:
            if i.get("id") == instance_id:
                instance = i
                break

        if not instance:
            return {"error": f"Instance {instance_id} not found"}

        # Format detailed information
        details = {
            "id": instance.get("id"),
            "name": instance.get("name"),
            "status": instance.get("status"),
            "instance_type": {
                "name": instance.get("instance_type", {}).get("name"),
                "gpu_type": instance.get("instance_type", {}).get("gpu_type"),
                "gpu_count": instance.get("instance_type", {}).get("gpu_count"),
                "cpu_count": instance.get("instance_type", {}).get("cpu_count"),
                "ram_gb": instance.get("instance_type", {}).get("ram_gb"),
            },
            "network": {
                "ip": instance.get("ip"),
                "private_ip": instance.get("private_ip"),
                "hostname": instance.get("hostname"),
            },
            "region": instance.get("region", {}).get("name"),
            "created_at": instance.get("created_at"),
            "ssh_keys": instance.get("ssh_key_names", []),
            "pricing": {
                "price_per_hour": instance.get("instance_type", {}).get(
                    "price_cents_per_hour", 0
                )
                / 100,
                "currency": "USD",
            },
        }

        return details

    async def _execute_command(self, instance_id: str, command: str) -> dict[str, Any]:
        """Execute command on instance via SSH"""

        # First get instance details to get IP
        details = await self._get_instance_details(instance_id)

        if "error" in details:
            return details

        ip = details.get("network", {}).get("ip")
        if not ip:
            return {"error": "No IP address found for instance"}

        # Execute SSH command
        ssh_key = get_config_value("lambda_ssh_key_path", "~/.ssh/lambda_rsa")
        ssh_cmd = [
            "ssh",
            "-i",
            ssh_key,
            "-o",
            "StrictHostKeyChecking=no",
            "-o",
            "UserKnownHostsFile=/dev/null",
            f"ubuntu@{ip}",
            command,
        ]

        try:
            result = subprocess.run(
                ssh_cmd,
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )

            return {
                "instance_id": instance_id,
                "command": command,
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode,
            }

        except subprocess.TimeoutExpired:
            return {
                "instance_id": instance_id,
                "command": command,
                "success": False,
                "error": "Command timed out after 30 seconds",
            }
        except Exception as e:
            return {
                "instance_id": instance_id,
                "command": command,
                "success": False,
                "error": str(e),
            }


# Create and run server
if __name__ == "__main__":
    server = LambdaLabsCLIMCPServer()
    server.run()
