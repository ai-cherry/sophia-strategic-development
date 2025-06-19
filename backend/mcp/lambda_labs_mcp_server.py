"""
Lambda Labs MCP Server
MCP server for Lambda Labs GPU cloud integration
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import Resource, Tool, TextContent

from ..integrations.lambda_labs_integration import LambdaLabsIntegration

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create MCP server
server = Server("lambda-labs")

# Global integration instance
lambda_labs_integration = None

@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """List available Lambda Labs tools"""
    return [
        Tool(
            name="get_instance_types",
            description="Get available GPU instance types",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="get_instances",
            description="Get all instances",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="get_instance",
            description="Get specific instance details",
            inputSchema={
                "type": "object",
                "properties": {
                    "instance_id": {
                        "type": "string",
                        "description": "Instance ID"
                    }
                },
                "required": ["instance_id"]
            }
        ),
        Tool(
            name="launch_instance",
            description="Launch a new GPU instance",
            inputSchema={
                "type": "object",
                "properties": {
                    "instance_type": {
                        "type": "string",
                        "description": "Instance type name"
                    },
                    "region": {
                        "type": "string",
                        "description": "Region name"
                    },
                    "ssh_key_names": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "SSH key names"
                    },
                    "name": {
                        "type": "string",
                        "description": "Optional instance name"
                    }
                },
                "required": ["instance_type", "region", "ssh_key_names"]
            }
        ),
        Tool(
            name="terminate_instance",
            description="Terminate an instance",
            inputSchema={
                "type": "object",
                "properties": {
                    "instance_id": {
                        "type": "string",
                        "description": "Instance ID"
                    }
                },
                "required": ["instance_id"]
            }
        ),
        Tool(
            name="restart_instance",
            description="Restart an instance",
            inputSchema={
                "type": "object",
                "properties": {
                    "instance_id": {
                        "type": "string",
                        "description": "Instance ID"
                    }
                },
                "required": ["instance_id"]
            }
        ),
        Tool(
            name="get_ssh_keys",
            description="Get SSH keys",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="add_ssh_key",
            description="Add an SSH key",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "SSH key name"
                    },
                    "public_key": {
                        "type": "string",
                        "description": "SSH public key content"
                    }
                },
                "required": ["name", "public_key"]
            }
        ),
        Tool(
            name="delete_ssh_key",
            description="Delete an SSH key",
            inputSchema={
                "type": "object",
                "properties": {
                    "ssh_key_id": {
                        "type": "string",
                        "description": "SSH key ID"
                    }
                },
                "required": ["ssh_key_id"]
            }
        ),
        Tool(
            name="get_filesystems",
            description="Get persistent filesystems",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="create_filesystem",
            description="Create a persistent filesystem",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Filesystem name"
                    },
                    "region": {
                        "type": "string",
                        "description": "Region name"
                    },
                    "size_gib": {
                        "type": "integer",
                        "description": "Size in GiB"
                    }
                },
                "required": ["name", "region", "size_gib"]
            }
        ),
        Tool(
            name="delete_filesystem",
            description="Delete a persistent filesystem",
            inputSchema={
                "type": "object",
                "properties": {
                    "filesystem_id": {
                        "type": "string",
                        "description": "Filesystem ID"
                    }
                },
                "required": ["filesystem_id"]
            }
        ),
        Tool(
            name="get_regions",
            description="Get available regions",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle Lambda Labs tool calls"""
    global lambda_labs_integration
    
    try:
        # Initialize integration if needed
        if not lambda_labs_integration:
            lambda_labs_integration = LambdaLabsIntegration()
            await lambda_labs_integration.initialize()
        
        if name == "get_instance_types":
            instance_types = await lambda_labs_integration.get_instance_types()
            
            return [TextContent(type="text", text=json.dumps({
                "instance_types": instance_types,
                "count": len(instance_types)
            }, indent=2))]
        
        elif name == "get_instances":
            instances = await lambda_labs_integration.get_instances()
            
            return [TextContent(type="text", text=json.dumps({
                "instances": instances,
                "count": len(instances)
            }, indent=2))]
        
        elif name == "get_instance":
            instance_id = arguments.get("instance_id")
            if not instance_id:
                return [TextContent(type="text", text=json.dumps({"error": "Instance ID required"}))]
            
            instance = await lambda_labs_integration.get_instance(instance_id)
            
            return [TextContent(type="text", text=json.dumps(instance or {"error": "Instance not found"}, indent=2))]
        
        elif name == "launch_instance":
            instance_type = arguments.get("instance_type")
            region = arguments.get("region")
            ssh_key_names = arguments.get("ssh_key_names")
            name = arguments.get("name")
            
            if not instance_type or not region or not ssh_key_names:
                return [TextContent(type="text", text=json.dumps({"error": "Instance type, region, and SSH key names required"}))]
            
            instance = await lambda_labs_integration.launch_instance(instance_type, region, ssh_key_names, name)
            
            return [TextContent(type="text", text=json.dumps(instance or {"error": "Failed to launch instance"}, indent=2))]
        
        elif name == "terminate_instance":
            instance_id = arguments.get("instance_id")
            if not instance_id:
                return [TextContent(type="text", text=json.dumps({"error": "Instance ID required"}))]
            
            success = await lambda_labs_integration.terminate_instance(instance_id)
            
            return [TextContent(type="text", text=json.dumps({
                "success": success,
                "instance_id": instance_id
            }, indent=2))]
        
        elif name == "restart_instance":
            instance_id = arguments.get("instance_id")
            if not instance_id:
                return [TextContent(type="text", text=json.dumps({"error": "Instance ID required"}))]
            
            success = await lambda_labs_integration.restart_instance(instance_id)
            
            return [TextContent(type="text", text=json.dumps({
                "success": success,
                "instance_id": instance_id
            }, indent=2))]
        
        elif name == "get_ssh_keys":
            ssh_keys = await lambda_labs_integration.get_ssh_keys()
            
            return [TextContent(type="text", text=json.dumps({
                "ssh_keys": ssh_keys,
                "count": len(ssh_keys)
            }, indent=2))]
        
        elif name == "add_ssh_key":
            name = arguments.get("name")
            public_key = arguments.get("public_key")
            
            if not name or not public_key:
                return [TextContent(type="text", text=json.dumps({"error": "Name and public key required"}))]
            
            ssh_key = await lambda_labs_integration.add_ssh_key(name, public_key)
            
            return [TextContent(type="text", text=json.dumps(ssh_key or {"error": "Failed to add SSH key"}, indent=2))]
        
        elif name == "delete_ssh_key":
            ssh_key_id = arguments.get("ssh_key_id")
            if not ssh_key_id:
                return [TextContent(type="text", text=json.dumps({"error": "SSH key ID required"}))]
            
            success = await lambda_labs_integration.delete_ssh_key(ssh_key_id)
            
            return [TextContent(type="text", text=json.dumps({
                "success": success,
                "ssh_key_id": ssh_key_id
            }, indent=2))]
        
        elif name == "get_filesystems":
            filesystems = await lambda_labs_integration.get_filesystems()
            
            return [TextContent(type="text", text=json.dumps({
                "filesystems": filesystems,
                "count": len(filesystems)
            }, indent=2))]
        
        elif name == "create_filesystem":
            name = arguments.get("name")
            region = arguments.get("region")
            size_gib = arguments.get("size_gib")
            
            if not name or not region or not size_gib:
                return [TextContent(type="text", text=json.dumps({"error": "Name, region, and size required"}))]
            
            filesystem = await lambda_labs_integration.create_filesystem(name, region, size_gib)
            
            return [TextContent(type="text", text=json.dumps(filesystem or {"error": "Failed to create filesystem"}, indent=2))]
        
        elif name == "delete_filesystem":
            filesystem_id = arguments.get("filesystem_id")
            if not filesystem_id:
                return [TextContent(type="text", text=json.dumps({"error": "Filesystem ID required"}))]
            
            success = await lambda_labs_integration.delete_filesystem(filesystem_id)
            
            return [TextContent(type="text", text=json.dumps({
                "success": success,
                "filesystem_id": filesystem_id
            }, indent=2))]
        
        elif name == "get_regions":
            regions = await lambda_labs_integration.get_regions()
            
            return [TextContent(type="text", text=json.dumps({
                "regions": regions,
                "count": len(regions)
            }, indent=2))]
        
        else:
            return [TextContent(type="text", text=json.dumps({"error": f"Unknown tool: {name}"}))]
    
    except Exception as e:
        logger.error(f"Error handling Lambda Labs tool call {name}: {e}")
        return [TextContent(type="text", text=json.dumps({"error": str(e)}))]

async def main():
    """Main entry point for the Lambda Labs MCP server"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="lambda-labs",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=None,
                    experimental_capabilities=None
                )
            )
        )

if __name__ == "__main__":
    asyncio.run(main())

