#!/usr/bin/env python3
"""
Lambda Labs CLI MCP Server for Sophia AI
Direct GPU instance management with Lambda Labs CLI integration
Complements existing Kubernetes orchestration with direct hardware control
"""

import asyncio
import json
import logging
import os
import subprocess
from datetime import datetime
from typing import Any, Dict, List, Optional

from mcp.server import Server
from mcp.types import Tool, TextContent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LambdaLabsCLIMCPServer:
    """Lambda Labs CLI MCP Server for direct GPU management"""
    
    def __init__(self, port: int = 9020):
        self.port = port
        self.server = Server("lambda-labs-cli")
        self.api_key = os.getenv("LAMBDA_LABS_API_KEY", "")
        
        # Instance type configurations optimized for Sophia AI
        self.instance_configs = {
            "dev": {
                "instance_type": "gpu_1x_rtx4090",
                "region": "us-west-2",
                "description": "Development and testing environment"
            },
            "staging": {
                "instance_type": "gpu_1x_a10",
                "region": "us-west-2", 
                "description": "Staging environment with production parity"
            },
            "production": {
                "instance_type": "gpu_1x_a10",
                "region": "us-west-2",
                "description": "Production environment with high availability"
            },
            "training": {
                "instance_type": "gpu_8x_a100",
                "region": "us-west-2",
                "description": "ML model training with maximum GPU power"
            }
        }
        
        self._register_tools()

    def _register_tools(self):
        """Register MCP tools for Lambda Labs CLI operations"""
        
        @self.server.call_tool()
        async def list_instances(arguments: Dict[str, Any]) -> List[TextContent]:
            """List all Lambda Labs instances"""
            status_filter = arguments.get("status", "all")  # all, running, stopped, terminated
            
            logger.info(f"🔍 Listing Lambda Labs instances (filter: {status_filter})")
            
            try:
                result = await self._run_lambda_cli_command(["list", "instances"])
                
                if result["success"]:
                    instances_data = json.loads(result["output"])
                    instances = instances_data.get("data", [])
                    
                    # Filter by status if specified
                    if status_filter != "all":
                        instances = [inst for inst in instances if inst.get("status") == status_filter]
                    
                    response = f"🖥️ **Lambda Labs Instances ({len(instances)} found):**\n\n"
                    
                    for instance in instances:
                        response += f"**{instance.get('name', 'Unnamed')}** (ID: {instance.get('id')})\n"
                        response += f"  Status: {instance.get('status', 'unknown')}\n"
                        response += f"  Type: {instance.get('instance_type', {}).get('name', 'unknown')}\n"
                        response += f"  Region: {instance.get('region', {}).get('name', 'unknown')}\n"
                        response += f"  IP: {instance.get('ip', 'not assigned')}\n"
                        response += f"  Cost/hour: ${instance.get('instance_type', {}).get('price_cents_per_hour', 0) / 100:.2f}\n\n"
                    
                    return [TextContent(type="text", text=response)]
                else:
                    return [TextContent(
                        type="text",
                        text=f"❌ Failed to list instances: {result['error']}"
                    )]
                    
            except Exception as e:
                logger.error(f"❌ Error listing instances: {e}")
                return [TextContent(
                    type="text",
                    text=f"❌ Error listing instances: {str(e)}"
                )]

        @self.server.call_tool()
        async def launch_instance(arguments: Dict[str, Any]) -> List[TextContent]:
            """Launch a new Lambda Labs instance"""
            environment = arguments.get("environment", "dev")  # dev, staging, production, training
            instance_name = arguments.get("name", f"sophia-ai-{environment}-{datetime.now().strftime('%m%d-%H%M')}")
            ssh_key_name = arguments.get("ssh_key", "sophia-ai-key")
            
            if environment not in self.instance_configs:
                return [TextContent(
                    type="text",
                    text=f"❌ Invalid environment. Choose from: {list(self.instance_configs.keys())}"
                )]
            
            config = self.instance_configs[environment]
            
            logger.info(f"🚀 Launching {environment} instance: {instance_name}")
            
            try:
                launch_args = [
                    "launch", "instance",
                    "--instance-type", config["instance_type"],
                    "--region", config["region"],
                    "--ssh-key", ssh_key_name,
                    "--name", instance_name
                ]
                
                result = await self._run_lambda_cli_command(launch_args)
                
                if result["success"]:
                    launch_data = json.loads(result["output"])
                    instance_id = launch_data.get("data", {}).get("instance_ids", [None])[0]
                    
                    response = f"🚀 **Instance Launch Initiated:**\n\n"
                    response += f"**Name:** {instance_name}\n"
                    response += f"**Environment:** {environment}\n"
                    response += f"**Instance ID:** {instance_id}\n"
                    response += f"**Type:** {config['instance_type']}\n"
                    response += f"**Region:** {config['region']}\n"
                    response += f"**Description:** {config['description']}\n\n"
                    response += f"⏳ Instance is being provisioned. Use `get_instance_status` to monitor progress.\n"
                    response += f"💰 Estimated cost: ${self._get_hourly_cost(config['instance_type']):.2f}/hour"
                    
                    return [TextContent(type="text", text=response)]
                else:
                    return [TextContent(
                        type="text",
                        text=f"❌ Failed to launch instance: {result['error']}"
                    )]
                    
            except Exception as e:
                logger.error(f"❌ Error launching instance: {e}")
                return [TextContent(
                    type="text",
                    text=f"❌ Error launching instance: {str(e)}"
                )]

        @self.server.call_tool()
        async def terminate_instance(arguments: Dict[str, Any]) -> List[TextContent]:
            """Terminate a Lambda Labs instance"""
            instance_id = arguments.get("instance_id", "")
            confirm = arguments.get("confirm", False)
            
            if not instance_id:
                return [TextContent(
                    type="text",
                    text="❌ Error: instance_id is required"
                )]
            
            if not confirm:
                return [TextContent(
                    type="text",
                    text="⚠️ Warning: Instance termination is permanent and will result in data loss.\nSet 'confirm': true to proceed."
                )]
            
            logger.info(f"🛑 Terminating instance: {instance_id}")
            
            try:
                result = await self._run_lambda_cli_command(["terminate", "instance", instance_id])
                
                if result["success"]:
                    response = f"🛑 **Instance Termination Initiated:**\n\n"
                    response += f"**Instance ID:** {instance_id}\n"
                    response += f"**Status:** Termination in progress\n"
                    response += f"**Note:** Instance will be permanently deleted\n\n"
                    response += f"💡 Billing will stop once termination is complete."
                    
                    return [TextContent(type="text", text=response)]
                else:
                    return [TextContent(
                        type="text",
                        text=f"❌ Failed to terminate instance: {result['error']}"
                    )]
                    
            except Exception as e:
                logger.error(f"❌ Error terminating instance: {e}")
                return [TextContent(
                    type="text",
                    text=f"❌ Error terminating instance: {str(e)}"
                )]

        @self.server.call_tool()
        async def get_instance_status(arguments: Dict[str, Any]) -> List[TextContent]:
            """Get detailed status of a specific instance"""
            instance_id = arguments.get("instance_id", "")
            
            if not instance_id:
                return [TextContent(
                    type="text",
                    text="❌ Error: instance_id is required"
                )]
            
            logger.info(f"📊 Getting status for instance: {instance_id}")
            
            try:
                result = await self._run_lambda_cli_command(["get", "instance", instance_id])
                
                if result["success"]:
                    instance_data = json.loads(result["output"])
                    instance = instance_data.get("data", {})
                    
                    response = f"📊 **Instance Status Details:**\n\n"
                    response += f"**Name:** {instance.get('name', 'Unnamed')}\n"
                    response += f"**ID:** {instance.get('id')}\n"
                    response += f"**Status:** {instance.get('status', 'unknown')}\n"
                    response += f"**IP Address:** {instance.get('ip', 'not assigned')}\n"
                    response += f"**SSH User:** ubuntu\n\n"
                    
                    # Instance type details
                    instance_type = instance.get('instance_type', {})
                    response += f"**Hardware Configuration:**\n"
                    response += f"  Type: {instance_type.get('name', 'unknown')}\n"
                    response += f"  GPUs: {instance_type.get('specs', {}).get('gpu_count', 'unknown')}\n"
                    response += f"  GPU Type: {instance_type.get('specs', {}).get('gpu_type', 'unknown')}\n"
                    response += f"  Memory: {instance_type.get('specs', {}).get('memory_gb', 'unknown')} GB\n"
                    response += f"  Storage: {instance_type.get('specs', {}).get('storage_gb', 'unknown')} GB\n\n"
                    
                    # Cost information
                    response += f"**Cost Information:**\n"
                    response += f"  Rate: ${instance_type.get('price_cents_per_hour', 0) / 100:.2f}/hour\n"
                    
                    # Connection information
                    if instance.get('ip') and instance.get('status') == 'running':
                        response += f"\n**Connection Information:**\n"
                        response += f"  SSH: `ssh ubuntu@{instance.get('ip')}`\n"
                        response += f"  Sophia AI API: `http://{instance.get('ip')}:8000`\n"
                    
                    return [TextContent(type="text", text=response)]
                else:
                    return [TextContent(
                        type="text",
                        text=f"❌ Failed to get instance status: {result['error']}"
                    )]
                    
            except Exception as e:
                logger.error(f"❌ Error getting instance status: {e}")
                return [TextContent(
                    type="text",
                    text=f"❌ Error getting instance status: {str(e)}"
                )]

        @self.server.call_tool()
        async def list_instance_types(arguments: Dict[str, Any]) -> List[TextContent]:
            """List available Lambda Labs instance types"""
            region_filter = arguments.get("region", "")
            
            logger.info(f"💻 Listing available instance types")
            
            try:
                result = await self._run_lambda_cli_command(["list", "instance-types"])
                
                if result["success"]:
                    types_data = json.loads(result["output"])
                    instance_types = types_data.get("data", [])
                    
                    response = f"💻 **Available Instance Types:**\n\n"
                    
                    for inst_type in instance_types:
                        name = inst_type.get("name", "unknown")
                        specs = inst_type.get("specs", {})
                        price = inst_type.get("price_cents_per_hour", 0) / 100
                        
                        response += f"**{name}**\n"
                        response += f"  GPUs: {specs.get('gpu_count', 'unknown')} x {specs.get('gpu_type', 'unknown')}\n"
                        response += f"  Memory: {specs.get('memory_gb', 'unknown')} GB\n"
                        response += f"  Storage: {specs.get('storage_gb', 'unknown')} GB\n"
                        response += f"  Price: ${price:.2f}/hour\n\n"
                    
                    return [TextContent(type="text", text=response)]
                else:
                    return [TextContent(
                        type="text",
                        text=f"❌ Failed to list instance types: {result['error']}"
                    )]
                    
            except Exception as e:
                logger.error(f"❌ Error listing instance types: {e}")
                return [TextContent(
                    type="text",
                    text=f"❌ Error listing instance types: {str(e)}"
                )]

        @self.server.call_tool()
        async def estimate_costs(arguments: Dict[str, Any]) -> List[TextContent]:
            """Estimate costs for Lambda Labs usage"""
            environment = arguments.get("environment", "dev")
            hours_per_day = arguments.get("hours_per_day", 8)
            days_per_month = arguments.get("days_per_month", 22)
            
            if environment not in self.instance_configs:
                return [TextContent(
                    type="text",
                    text=f"❌ Invalid environment. Choose from: {list(self.instance_configs.keys())}"
                )]
            
            config = self.instance_configs[environment]
            hourly_cost = self._get_hourly_cost(config["instance_type"])
            
            daily_cost = hourly_cost * hours_per_day
            monthly_cost = daily_cost * days_per_month
            
            response = f"💰 **Cost Estimation for {environment.title()} Environment:**\n\n"
            response += f"**Instance Type:** {config['instance_type']}\n"
            response += f"**Usage Pattern:**\n"
            response += f"  Hours per day: {hours_per_day}\n"
            response += f"  Days per month: {days_per_month}\n\n"
            response += f"**Cost Breakdown:**\n"
            response += f"  Hourly: ${hourly_cost:.2f}\n"
            response += f"  Daily: ${daily_cost:.2f}\n"
            response += f"  Monthly: ${monthly_cost:.2f}\n\n"
            response += f"**Annual Estimate:** ${monthly_cost * 12:.2f}\n\n"
            response += f"💡 **Cost Optimization Tips:**\n"
            response += f"  - Use spot instances for non-critical workloads\n"
            response += f"  - Terminate instances when not in use\n"
            response += f"  - Consider smaller instance types for development"
            
            return [TextContent(type="text", text=response)]

    async def _run_lambda_cli_command(self, args: List[str]) -> Dict[str, Any]:
        """Run Lambda Labs CLI command"""
        try:
            # Check if lambda-cli is available
            cli_check = subprocess.run(["which", "lambda-cli"], capture_output=True, text=True)
            if cli_check.returncode != 0:
                return {
                    "success": False,
                    "error": "lambda-cli not found. Install with: pip install lambda-cli"
                }
            
            # Set API key in environment
            env = os.environ.copy()
            env["LAMBDA_API_KEY"] = self.api_key
            
            # Run the lambda-cli command
            cmd = ["lambda-cli"] + args + ["--output", "json"]
            result = subprocess.run(
                cmd,
                env=env,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return {
                    "success": True,
                    "output": result.stdout,
                    "command": " ".join(cmd)
                }
            else:
                return {
                    "success": False,
                    "error": result.stderr or result.stdout,
                    "command": " ".join(cmd)
                }
                
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Command timed out after 30 seconds"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def _get_hourly_cost(self, instance_type: str) -> float:
        """Get hourly cost for instance type (approximate)"""
        cost_mapping = {
            "gpu_1x_rtx4090": 1.50,
            "gpu_1x_a10": 0.75,
            "gpu_1x_a100": 1.10,
            "gpu_8x_a100": 8.80,
            "gpu_1x_h100": 2.50
        }
        return cost_mapping.get(instance_type, 1.00)

    async def start_server(self):
        """Start the Lambda Labs CLI MCP server"""
        logger.info(f"🚀 Starting Lambda Labs CLI MCP Server on port {self.port}")
        
        # Add health check endpoint
        @self.server.call_tool()
        async def health_check(arguments: Dict[str, Any]) -> List[TextContent]:
            """Health check for Lambda Labs CLI MCP server"""
            cli_available = subprocess.run(["which", "lambda-cli"], capture_output=True).returncode == 0
            api_key_set = bool(self.api_key)
            
            status = "healthy" if cli_available and api_key_set else "degraded"
            
            response = f"✅ **Lambda Labs CLI MCP Server Status:**\n\n"
            response += f"**Overall Status:** {status}\n"
            response += f"**Port:** {self.port}\n"
            response += f"**CLI Available:** {'✅' if cli_available else '❌'}\n"
            response += f"**API Key Set:** {'✅' if api_key_set else '❌'}\n\n"
            
            if not cli_available:
                response += f"⚠️ Install lambda-cli: `pip install lambda-cli`\n"
            if not api_key_set:
                response += f"⚠️ Set LAMBDA_LABS_API_KEY environment variable\n"
            
            return [TextContent(type="text", text=response)]
        
        # Register tools as MCP tools
        tools = [
            Tool(
                name="list_instances",
                description="List Lambda Labs instances with optional status filter",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "status": {"type": "string", "enum": ["all", "running", "stopped", "terminated"], "default": "all"}
                    }
                }
            ),
            Tool(
                name="launch_instance",
                description="Launch a new Lambda Labs instance for specific environment",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "environment": {"type": "string", "enum": ["dev", "staging", "production", "training"], "default": "dev"},
                        "name": {"type": "string"},
                        "ssh_key": {"type": "string", "default": "sophia-ai-key"}
                    }
                }
            ),
            Tool(
                name="terminate_instance",
                description="Terminate a Lambda Labs instance (permanent deletion)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "instance_id": {"type": "string"},
                        "confirm": {"type": "boolean", "default": False}
                    },
                    "required": ["instance_id"]
                }
            ),
            Tool(
                name="get_instance_status",
                description="Get detailed status of a specific instance",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "instance_id": {"type": "string"}
                    },
                    "required": ["instance_id"]
                }
            ),
            Tool(
                name="list_instance_types",
                description="List available Lambda Labs instance types and specifications",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "region": {"type": "string"}
                    }
                }
            ),
            Tool(
                name="estimate_costs",
                description="Estimate Lambda Labs costs for different usage patterns",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "environment": {"type": "string", "enum": ["dev", "staging", "production", "training"], "default": "dev"},
                        "hours_per_day": {"type": "number", "default": 8},
                        "days_per_month": {"type": "number", "default": 22}
                    }
                }
            ),
            Tool(
                name="health_check",
                description="Check Lambda Labs CLI MCP server health and configuration",
                inputSchema={"type": "object", "properties": {}}
            )
        ]
        
        # Set tools on server
        self.server.tools = tools
        
        # Start the server
        await self.server.run(port=self.port)

# Main execution
async def main():
    server = LambdaLabsCLIMCPServer()
    
    try:
        await server.start_server()
    except KeyboardInterrupt:
        logger.info("🛑 Shutting down Lambda Labs CLI MCP Server")

if __name__ == "__main__":
    asyncio.run(main()) 