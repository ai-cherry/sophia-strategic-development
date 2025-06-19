"""
Gong MCP Server
MCP server for Gong CRM integration
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import Resource, Tool, TextContent

from ..integrations.gong_integration import GongIntegration

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create MCP server
server = Server("gong")

# Global integration instance
gong_integration = None

@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """List available Gong tools"""
    return [
        Tool(
            name="get_calls",
            description="Get calls from Gong within a date range",
            inputSchema={
                "type": "object",
                "properties": {
                    "from_date": {
                        "type": "string",
                        "description": "Start date (ISO format, optional)"
                    },
                    "to_date": {
                        "type": "string",
                        "description": "End date (ISO format, optional)"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of calls to return",
                        "default": 100
                    }
                }
            }
        ),
        Tool(
            name="get_call_details",
            description="Get detailed information about a specific call",
            inputSchema={
                "type": "object",
                "properties": {
                    "call_id": {
                        "type": "string",
                        "description": "Call ID"
                    }
                },
                "required": ["call_id"]
            }
        ),
        Tool(
            name="get_call_transcript",
            description="Get transcript for a specific call",
            inputSchema={
                "type": "object",
                "properties": {
                    "call_id": {
                        "type": "string",
                        "description": "Call ID"
                    }
                },
                "required": ["call_id"]
            }
        ),
        Tool(
            name="search_calls",
            description="Search calls by query",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query"
                    },
                    "from_date": {
                        "type": "string",
                        "description": "Start date (ISO format, optional)"
                    },
                    "to_date": {
                        "type": "string",
                        "description": "End date (ISO format, optional)"
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="get_users",
            description="Get all users from Gong",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="get_deals",
            description="Get deals from Gong",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of deals to return",
                        "default": 100
                    }
                }
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle Gong tool calls"""
    global gong_integration
    
    try:
        # Initialize integration if needed
        if not gong_integration:
            gong_integration = GongIntegration()
            await gong_integration.initialize()
        
        if name == "get_calls":
            from_date = arguments.get("from_date")
            to_date = arguments.get("to_date")
            limit = arguments.get("limit", 100)
            
            # Parse dates if provided
            from_dt = datetime.fromisoformat(from_date) if from_date else None
            to_dt = datetime.fromisoformat(to_date) if to_date else None
            
            calls = await gong_integration.get_calls(from_dt, to_dt, limit)
            
            return [TextContent(type="text", text=json.dumps({
                "calls": calls,
                "count": len(calls)
            }, indent=2))]
        
        elif name == "get_call_details":
            call_id = arguments.get("call_id")
            if not call_id:
                return [TextContent(type="text", text=json.dumps({"error": "Call ID required"}))]
            
            details = await gong_integration.get_call_details(call_id)
            
            return [TextContent(type="text", text=json.dumps(details or {"error": "Call not found"}, indent=2))]
        
        elif name == "get_call_transcript":
            call_id = arguments.get("call_id")
            if not call_id:
                return [TextContent(type="text", text=json.dumps({"error": "Call ID required"}))]
            
            transcript = await gong_integration.get_call_transcript(call_id)
            
            return [TextContent(type="text", text=json.dumps({
                "call_id": call_id,
                "transcript": transcript or "No transcript available"
            }, indent=2))]
        
        elif name == "search_calls":
            query = arguments.get("query")
            if not query:
                return [TextContent(type="text", text=json.dumps({"error": "Query required"}))]
            
            from_date = arguments.get("from_date")
            to_date = arguments.get("to_date")
            
            # Parse dates if provided
            from_dt = datetime.fromisoformat(from_date) if from_date else None
            to_dt = datetime.fromisoformat(to_date) if to_date else None
            
            calls = await gong_integration.search_calls(query, from_dt, to_dt)
            
            return [TextContent(type="text", text=json.dumps({
                "query": query,
                "calls": calls,
                "count": len(calls)
            }, indent=2))]
        
        elif name == "get_users":
            users = await gong_integration.get_users()
            
            return [TextContent(type="text", text=json.dumps({
                "users": users,
                "count": len(users)
            }, indent=2))]
        
        elif name == "get_deals":
            limit = arguments.get("limit", 100)
            deals = await gong_integration.get_deals(limit)
            
            return [TextContent(type="text", text=json.dumps({
                "deals": deals,
                "count": len(deals)
            }, indent=2))]
        
        else:
            return [TextContent(type="text", text=json.dumps({"error": f"Unknown tool: {name}"}))]
    
    except Exception as e:
        logger.error(f"Error handling Gong tool call {name}: {e}")
        return [TextContent(type="text", text=json.dumps({"error": str(e)}))]

async def main():
    """Main entry point for the Gong MCP server"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="gong",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=None,
                    experimental_capabilities=None
                )
            )
        )

if __name__ == "__main__":
    asyncio.run(main())

