"""
Sophia AI - Main MCP Server
Comprehensive MCP server for Sophia AI platform integration
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel
)

from ..core.integration_registry import integration_registry
from ..core.integration_config import integration_config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create MCP server
server = Server("sophia-ai")

@server.list_resources()
async def handle_list_resources() -> List[Resource]:
    """List available resources"""
    resources = []
    
    # Add integration status resource
    resources.append(
        Resource(
            uri="sophia://integrations/status",
            name="Integration Status",
            description="Status of all Sophia AI integrations",
            mimeType="application/json"
        )
    )
    
    # Add service configuration resources
    services = await integration_config.list_services()
    for service in services:
        resources.append(
            Resource(
                uri=f"sophia://services/{service}/config",
                name=f"{service.title()} Configuration",
                description=f"Configuration for {service} service",
                mimeType="application/json"
            )
        )
    
    return resources

@server.read_resource()
async def handle_read_resource(uri: str) -> str:
    """Read a specific resource"""
    if uri == "sophia://integrations/status":
        # Get integration status
        stats = integration_registry.get_integration_stats()
        health_status = await integration_registry.health_check_all()
        
        status = {
            "stats": stats,
            "health": health_status,
            "timestamp": asyncio.get_event_loop().time()
        }
        
        return json.dumps(status, indent=2)
    
    elif uri.startswith("sophia://services/"):
        # Extract service name
        parts = uri.split("/")
        if len(parts) >= 3:
            service_name = parts[2]
            
            if parts[3] == "config":
                # Get service configuration
                config = await integration_config.get_service_config(service_name)
                if config:
                    return json.dumps({
                        "service_name": config.service_name,
                        "config": config.config,
                        "metadata": config.metadata
                    }, indent=2)
                else:
                    return json.dumps({"error": f"Service {service_name} not found"})
    
    return json.dumps({"error": "Resource not found"})

@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """List available tools"""
    tools = [
        Tool(
            name="health_check",
            description="Check health of all integrations or a specific service",
            inputSchema={
                "type": "object",
                "properties": {
                    "service": {
                        "type": "string",
                        "description": "Optional service name to check (if not provided, checks all)"
                    }
                }
            }
        ),
        Tool(
            name="list_services",
            description="List all available services",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="get_service_config",
            description="Get configuration for a specific service",
            inputSchema={
                "type": "object",
                "properties": {
                    "service": {
                        "type": "string",
                        "description": "Service name"
                    }
                },
                "required": ["service"]
            }
        ),
        Tool(
            name="validate_service",
            description="Validate a service configuration",
            inputSchema={
                "type": "object",
                "properties": {
                    "service": {
                        "type": "string",
                        "description": "Service name"
                    }
                },
                "required": ["service"]
            }
        ),
        Tool(
            name="refresh_cache",
            description="Refresh configuration cache for a service or all services",
            inputSchema={
                "type": "object",
                "properties": {
                    "service": {
                        "type": "string",
                        "description": "Optional service name (if not provided, refreshes all)"
                    }
                }
            }
        ),
        Tool(
            name="get_integration_stats",
            description="Get statistics about the integration registry",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]
    
    return tools

@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls"""
    try:
        if name == "health_check":
            service = arguments.get("service")
            
            if service:
                # Check specific service
                is_healthy = await integration_registry.health_check(service)
                result = {
                    "service": service,
                    "healthy": is_healthy,
                    "timestamp": asyncio.get_event_loop().time()
                }
            else:
                # Check all services
                health_status = await integration_registry.health_check_all()
                result = {
                    "all_services": health_status,
                    "timestamp": asyncio.get_event_loop().time()
                }
            
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "list_services":
            services = await integration_config.list_services()
            result = {
                "services": services,
                "count": len(services)
            }
            
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "get_service_config":
            service = arguments.get("service")
            if not service:
                return [TextContent(type="text", text=json.dumps({"error": "Service name required"}))]
            
            config = await integration_config.get_service_config(service)
            if config:
                result = {
                    "service_name": config.service_name,
                    "config": config.config,
                    "metadata": config.metadata
                }
            else:
                result = {"error": f"Service {service} not found"}
            
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "validate_service":
            service = arguments.get("service")
            if not service:
                return [TextContent(type="text", text=json.dumps({"error": "Service name required"}))]
            
            is_valid = await integration_registry.validate_integration(service)
            result = {
                "service": service,
                "valid": is_valid,
                "timestamp": asyncio.get_event_loop().time()
            }
            
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "refresh_cache":
            service = arguments.get("service")
            
            await integration_config.refresh_cache(service)
            
            result = {
                "action": "cache_refreshed",
                "service": service or "all",
                "timestamp": asyncio.get_event_loop().time()
            }
            
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "get_integration_stats":
            stats = integration_registry.get_integration_stats()
            
            return [TextContent(type="text", text=json.dumps(stats, indent=2))]
        
        else:
            return [TextContent(type="text", text=json.dumps({"error": f"Unknown tool: {name}"}))]
    
    except Exception as e:
        logger.error(f"Error handling tool call {name}: {e}")
        return [TextContent(type="text", text=json.dumps({"error": str(e)}))]

async def main():
    """Main entry point for the MCP server"""
    # Initialize integration registry
    await integration_registry.initialize()
    
    # Run the server
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="sophia-ai",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=None,
                    experimental_capabilities=None
                )
            )
        )

if __name__ == "__main__":
    asyncio.run(main())

