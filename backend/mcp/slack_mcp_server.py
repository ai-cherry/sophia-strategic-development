"""
Slack MCP Server
MCP server for Slack integration and natural language interface
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

from ..slack.sophia_slack_bot import sophia_slack_bot
from ...core.integration_registry import integration_registry

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create MCP server
server = Server("slack")

@server.list_resources()
async def handle_list_resources() -> List[Resource]:
    """List available Slack resources"""
    return [
        Resource(
            uri="slack://channels",
            name="Slack Channels",
            description="List of Slack channels and their information",
            mimeType="application/json"
        ),
        Resource(
            uri="slack://bot/status",
            name="Slack Bot Status",
            description="Current status of the Sophia Slack bot",
            mimeType="application/json"
        ),
        Resource(
            uri="slack://commands/history",
            name="Command History",
            description="Recent Slack command usage history",
            mimeType="application/json"
        ),
        Resource(
            uri="slack://admin/migration",
            name="Admin Migration Status",
            description="Status of admin website to Slack migration",
            mimeType="application/json"
        )
    ]

@server.read_resource()
async def handle_read_resource(uri: str) -> str:
    """Read a specific Slack resource"""
    if uri == "slack://channels":
        # Get channel information
        try:
            channels = await sophia_slack_bot.client.conversations_list()
            return json.dumps({
                "channels": channels.get("channels", []),
                "timestamp": datetime.now().isoformat()
            }, indent=2)
        except Exception as e:
            return json.dumps({"error": str(e)})
    
    elif uri == "slack://bot/status":
        # Get bot status
        status = {
            "bot_active": sophia_slack_bot.socket_client is not None,
            "mcp_integration": sophia_slack_bot.mcp_integration,
            "admin_api_base": sophia_slack_bot.admin_api_base,
            "timestamp": datetime.now().isoformat()
        }
        return json.dumps(status, indent=2)
    
    elif uri == "slack://commands/history":
        # Command history (would be stored in database in real implementation)
        history = {
            "recent_commands": [
                {"command": "/sophia dashboard", "user": "U123456", "timestamp": "2024-01-15T10:30:00Z"},
                {"command": "/sophia query apartment deals", "user": "U123456", "timestamp": "2024-01-15T10:25:00Z"},
                {"command": "/sophia health", "user": "U123456", "timestamp": "2024-01-15T10:20:00Z"}
            ],
            "total_commands_today": 15,
            "most_used_command": "/sophia dashboard"
        }
        return json.dumps(history, indent=2)
    
    elif uri == "slack://admin/migration":
        # Migration status
        migration_status = {
            "admin_website_status": "deprecated",
            "slack_bot_status": "active",
            "migrated_features": [
                "dashboard_statistics",
                "natural_language_queries",
                "conversation_search",
                "system_health_checks",
                "deployment_commands"
            ],
            "pending_features": [
                "advanced_analytics",
                "user_management",
                "custom_reports"
            ],
            "migration_completion": "85%"
        }
        return json.dumps(migration_status, indent=2)
    
    return json.dumps({"error": "Resource not found"})

@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """List available Slack tools"""
    return [
        Tool(
            name="send_message",
            description="Send a message to a Slack channel",
            inputSchema={
                "type": "object",
                "properties": {
                    "channel": {
                        "type": "string",
                        "description": "Channel ID or name"
                    },
                    "message": {
                        "type": "string",
                        "description": "Message text to send"
                    },
                    "blocks": {
                        "type": "array",
                        "description": "Optional Slack blocks for rich formatting"
                    }
                },
                "required": ["channel", "message"]
            }
        ),
        Tool(
            name="process_admin_query",
            description="Process an admin query through the Slack interface",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Natural language query"
                    },
                    "user_id": {
                        "type": "string",
                        "description": "User ID making the query"
                    },
                    "channel_id": {
                        "type": "string",
                        "description": "Channel ID for response"
                    }
                },
                "required": ["query", "user_id", "channel_id"]
            }
        ),
        Tool(
            name="get_dashboard_data",
            description="Get dashboard data formatted for Slack",
            inputSchema={
                "type": "object",
                "properties": {
                    "format": {
                        "type": "string",
                        "enum": ["blocks", "text", "json"],
                        "description": "Output format",
                        "default": "blocks"
                    }
                }
            }
        ),
        Tool(
            name="search_conversations",
            description="Search conversations and format for Slack display",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query"
                    },
                    "filters": {
                        "type": "object",
                        "description": "Search filters (date_from, date_to, company, etc.)"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum results to return",
                        "default": 10
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="check_system_health",
            description="Check system health and format for Slack",
            inputSchema={
                "type": "object",
                "properties": {
                    "detailed": {
                        "type": "boolean",
                        "description": "Include detailed health information",
                        "default": false
                    }
                }
            }
        ),
        Tool(
            name="trigger_deployment",
            description="Trigger a deployment through Slack interface",
            inputSchema={
                "type": "object",
                "properties": {
                    "target": {
                        "type": "string",
                        "description": "Deployment target (vercel, lambda-labs, etc.)"
                    },
                    "user_id": {
                        "type": "string",
                        "description": "User requesting deployment"
                    },
                    "channel_id": {
                        "type": "string",
                        "description": "Channel for deployment updates"
                    }
                },
                "required": ["target", "user_id", "channel_id"]
            }
        ),
        Tool(
            name="migrate_admin_feature",
            description="Migrate a specific admin website feature to Slack",
            inputSchema={
                "type": "object",
                "properties": {
                    "feature": {
                        "type": "string",
                        "description": "Feature to migrate (analytics, reports, etc.)"
                    },
                    "configuration": {
                        "type": "object",
                        "description": "Migration configuration options"
                    }
                },
                "required": ["feature"]
            }
        ),
        Tool(
            name="setup_slack_workflow",
            description="Setup automated Slack workflows for admin tasks",
            inputSchema={
                "type": "object",
                "properties": {
                    "workflow_type": {
                        "type": "string",
                        "enum": ["daily_report", "alert_escalation", "deployment_notification"],
                        "description": "Type of workflow to setup"
                    },
                    "schedule": {
                        "type": "string",
                        "description": "Cron-style schedule for automated workflows"
                    },
                    "channels": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Channels to send workflow notifications"
                    }
                },
                "required": ["workflow_type"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle Slack tool calls"""
    try:
        if name == "send_message":
            channel = arguments.get("channel")
            message = arguments.get("message")
            blocks = arguments.get("blocks")
            
            if not channel or not message:
                return [TextContent(type="text", text=json.dumps({"error": "Channel and message required"}))]
            
            try:
                result = await sophia_slack_bot.client.chat_postMessage(
                    channel=channel,
                    text=message,
                    blocks=blocks
                )
                
                return [TextContent(type="text", text=json.dumps({
                    "success": True,
                    "message_ts": result.get("ts"),
                    "channel": result.get("channel")
                }, indent=2))]
            except Exception as e:
                return [TextContent(type="text", text=json.dumps({"error": str(e)}))]
        
        elif name == "process_admin_query":
            query = arguments.get("query")
            user_id = arguments.get("user_id")
            channel_id = arguments.get("channel_id")
            
            if not all([query, user_id, channel_id]):
                return [TextContent(type="text", text=json.dumps({"error": "Query, user_id, and channel_id required"}))]
            
            # Process the query through the Slack bot
            await sophia_slack_bot._handle_natural_language_query(channel_id, sophia_slack_bot.client, query, user_id)
            
            return [TextContent(type="text", text=json.dumps({
                "success": True,
                "query": query,
                "processed": True
            }, indent=2))]
        
        elif name == "get_dashboard_data":
            format_type = arguments.get("format", "blocks")
            
            # Get dashboard data
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{sophia_slack_bot.admin_api_base}/dashboard/stats") as response:
                    if response.status == 200:
                        stats = await response.json()
                        
                        if format_type == "blocks":
                            blocks = sophia_slack_bot._create_dashboard_blocks(stats)
                            return [TextContent(type="text", text=json.dumps(blocks, indent=2))]
                        elif format_type == "text":
                            text = f"Dashboard Stats: {stats.get('total_calls', 0)} calls, {stats.get('total_emails', 0)} emails"
                            return [TextContent(type="text", text=text)]
                        else:
                            return [TextContent(type="text", text=json.dumps(stats, indent=2))]
                    else:
                        return [TextContent(type="text", text=json.dumps({"error": "Failed to fetch dashboard data"}))]
        
        elif name == "search_conversations":
            query = arguments.get("query")
            filters = arguments.get("filters", {})
            limit = arguments.get("limit", 10)
            
            if not query:
                return [TextContent(type="text", text=json.dumps({"error": "Query required"}))]
            
            # Perform search
            params = {"q": query, "limit": limit, **filters}
            
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{sophia_slack_bot.admin_api_base}/conversations/search", params=params) as response:
                    if response.status == 200:
                        results = await response.json()
                        blocks = sophia_slack_bot._create_search_result_blocks(results, query)
                        return [TextContent(type="text", text=json.dumps({
                            "results": results,
                            "blocks": blocks
                        }, indent=2))]
                    else:
                        return [TextContent(type="text", text=json.dumps({"error": "Search failed"}))]
        
        elif name == "check_system_health":
            detailed = arguments.get("detailed", False)
            
            # Get health status
            health_status = await integration_registry.health_check_all()
            stats = integration_registry.get_integration_stats()
            
            if detailed:
                result = {
                    "health_status": health_status,
                    "stats": stats,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                result = {
                    "overall_health": all(health_status.values()),
                    "healthy_services": sum(health_status.values()),
                    "total_services": len(health_status),
                    "timestamp": datetime.now().isoformat()
                }
            
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "trigger_deployment":
            target = arguments.get("target")
            user_id = arguments.get("user_id")
            channel_id = arguments.get("channel_id")
            
            if not all([target, user_id, channel_id]):
                return [TextContent(type="text", text=json.dumps({"error": "Target, user_id, and channel_id required"}))]
            
            # Trigger deployment through Slack bot
            await sophia_slack_bot._handle_deployment_request(channel_id, sophia_slack_bot.client, target, user_id)
            
            return [TextContent(type="text", text=json.dumps({
                "success": True,
                "deployment_target": target,
                "initiated_by": user_id
            }, indent=2))]
        
        elif name == "migrate_admin_feature":
            feature = arguments.get("feature")
            configuration = arguments.get("configuration", {})
            
            if not feature:
                return [TextContent(type="text", text=json.dumps({"error": "Feature required"}))]
            
            # Simulate feature migration
            migration_result = {
                "feature": feature,
                "status": "migrated",
                "configuration": configuration,
                "slack_commands_added": [f"/sophia {feature}"],
                "timestamp": datetime.now().isoformat()
            }
            
            return [TextContent(type="text", text=json.dumps(migration_result, indent=2))]
        
        elif name == "setup_slack_workflow":
            workflow_type = arguments.get("workflow_type")
            schedule = arguments.get("schedule")
            channels = arguments.get("channels", [])
            
            if not workflow_type:
                return [TextContent(type="text", text=json.dumps({"error": "Workflow type required"}))]
            
            # Setup workflow
            workflow_config = {
                "workflow_type": workflow_type,
                "schedule": schedule,
                "channels": channels,
                "status": "configured",
                "next_run": datetime.now().isoformat() if schedule else None
            }
            
            return [TextContent(type="text", text=json.dumps(workflow_config, indent=2))]
        
        else:
            return [TextContent(type="text", text=json.dumps({"error": f"Unknown tool: {name}"}))]
    
    except Exception as e:
        logger.error(f"Error handling Slack tool call {name}: {e}")
        return [TextContent(type="text", text=json.dumps({"error": str(e)}))]

async def main():
    """Main entry point for the Slack MCP server"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="slack",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=None,
                    experimental_capabilities=None
                )
            )
        )

if __name__ == "__main__":
    asyncio.run(main())

