"""
Linear MCP Server
MCP server for Linear project management integration
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Sequence
from datetime import datetime

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource, Tool, TextContent, ImageContent, EmbeddedResource,
    CallToolRequest, CallToolResult, GetResourceRequest, GetResourceResult,
    ListResourcesRequest, ListResourcesResult, ListToolsRequest, ListToolsResult
)

from backend.integrations.linear_integration import linear_integration

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create MCP server instance
server = Server("linear-mcp-server")

@server.list_resources()
async def list_resources() -> List[Resource]:
    """List available Linear resources"""
    return [
        Resource(
            uri="linear://issues",
            name="Linear Issues",
            description="Access to Linear issues and their details",
            mimeType="application/json"
        ),
        Resource(
            uri="linear://projects",
            name="Linear Projects", 
            description="Access to Linear projects and their status",
            mimeType="application/json"
        ),
        Resource(
            uri="linear://teams",
            name="Linear Teams",
            description="Access to Linear teams and members",
            mimeType="application/json"
        ),
        Resource(
            uri="linear://health",
            name="Linear Health Status",
            description="Linear integration health and status information",
            mimeType="application/json"
        )
    ]

@server.get_resource()
async def get_resource(request: GetResourceRequest) -> GetResourceResult:
    """Get specific Linear resource"""
    try:
        uri = request.uri
        
        if uri == "linear://issues":
            issues = await linear_integration.get_issues()
            issues_data = [
                {
                    "id": issue.id,
                    "title": issue.title,
                    "description": issue.description,
                    "status": issue.status,
                    "assignee": issue.assignee,
                    "project": issue.project,
                    "priority": issue.priority,
                    "labels": issue.labels,
                    "created_at": issue.created_at,
                    "updated_at": issue.updated_at,
                    "url": issue.url
                }
                for issue in issues
            ]
            
            return GetResourceResult(
                contents=[
                    TextContent(
                        type="text",
                        text=json.dumps(issues_data, indent=2)
                    )
                ]
            )
        
        elif uri == "linear://projects":
            projects = await linear_integration.get_projects()
            projects_data = [
                {
                    "id": project.id,
                    "name": project.name,
                    "description": project.description,
                    "status": project.status,
                    "progress": project.progress,
                    "created_at": project.created_at,
                    "updated_at": project.updated_at,
                    "url": project.url
                }
                for project in projects
            ]
            
            return GetResourceResult(
                contents=[
                    TextContent(
                        type="text",
                        text=json.dumps(projects_data, indent=2)
                    )
                ]
            )
        
        elif uri == "linear://teams":
            teams = await linear_integration.get_teams()
            teams_data = [
                {
                    "id": team.id,
                    "name": team.name,
                    "description": team.description,
                    "members": team.members,
                    "created_at": team.created_at
                }
                for team in teams
            ]
            
            return GetResourceResult(
                contents=[
                    TextContent(
                        type="text",
                        text=json.dumps(teams_data, indent=2)
                    )
                ]
            )
        
        elif uri == "linear://health":
            health_status = await linear_integration.get_health_status()
            
            return GetResourceResult(
                contents=[
                    TextContent(
                        type="text",
                        text=json.dumps(health_status, indent=2)
                    )
                ]
            )
        
        else:
            raise ValueError(f"Unknown resource URI: {uri}")
    
    except Exception as e:
        logger.error(f"Error getting resource {request.uri}: {e}")
        return GetResourceResult(
            contents=[
                TextContent(
                    type="text",
                    text=f"Error: {str(e)}"
                )
            ]
        )

@server.list_tools()
async def list_tools() -> List[Tool]:
    """List available Linear tools"""
    return [
        Tool(
            name="create_linear_issue",
            description="Create a new Linear issue",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Issue title"
                    },
                    "description": {
                        "type": "string", 
                        "description": "Issue description"
                    },
                    "project_id": {
                        "type": "string",
                        "description": "Project ID (optional)"
                    },
                    "assignee_id": {
                        "type": "string",
                        "description": "Assignee ID (optional)"
                    },
                    "priority": {
                        "type": "string",
                        "description": "Issue priority (Low, Medium, High, Urgent)",
                        "enum": ["Low", "Medium", "High", "Urgent"]
                    },
                    "labels": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Issue labels (optional)"
                    }
                },
                "required": ["title", "description"]
            }
        ),
        Tool(
            name="get_linear_issues",
            description="Get Linear issues with optional filters",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "Filter by project ID (optional)"
                    },
                    "assignee_id": {
                        "type": "string",
                        "description": "Filter by assignee ID (optional)"
                    },
                    "status": {
                        "type": "string",
                        "description": "Filter by status (optional)"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of issues to return",
                        "default": 50
                    }
                }
            }
        ),
        Tool(
            name="update_linear_issue",
            description="Update an existing Linear issue",
            inputSchema={
                "type": "object",
                "properties": {
                    "issue_id": {
                        "type": "string",
                        "description": "Issue ID to update"
                    },
                    "title": {
                        "type": "string",
                        "description": "New title (optional)"
                    },
                    "description": {
                        "type": "string",
                        "description": "New description (optional)"
                    },
                    "status": {
                        "type": "string",
                        "description": "New status (optional)"
                    },
                    "assignee_id": {
                        "type": "string",
                        "description": "New assignee ID (optional)"
                    },
                    "priority": {
                        "type": "string",
                        "description": "New priority (optional)"
                    },
                    "labels": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "New labels (optional)"
                    }
                },
                "required": ["issue_id"]
            }
        ),
        Tool(
            name="search_linear_issues",
            description="Search Linear issues by query",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results",
                        "default": 20
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="create_linear_project",
            description="Create a new Linear project",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Project name"
                    },
                    "description": {
                        "type": "string",
                        "description": "Project description"
                    },
                    "team_id": {
                        "type": "string",
                        "description": "Team ID (optional)"
                    }
                },
                "required": ["name", "description"]
            }
        ),
        Tool(
            name="get_linear_projects",
            description="Get Linear projects",
            inputSchema={
                "type": "object",
                "properties": {
                    "team_id": {
                        "type": "string",
                        "description": "Filter by team ID (optional)"
                    }
                }
            }
        ),
        Tool(
            name="get_linear_teams",
            description="Get Linear teams",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="get_linear_health",
            description="Get Linear integration health status",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]

@server.call_tool()
async def call_tool(request: CallToolRequest) -> CallToolResult:
    """Handle Linear tool calls"""
    try:
        tool_name = request.name
        arguments = request.arguments or {}
        
        if tool_name == "create_linear_issue":
            issue = await linear_integration.create_issue(
                title=arguments["title"],
                description=arguments["description"],
                project_id=arguments.get("project_id"),
                assignee_id=arguments.get("assignee_id"),
                priority=arguments.get("priority"),
                labels=arguments.get("labels")
            )
            
            if issue:
                result = {
                    "success": True,
                    "issue": {
                        "id": issue.id,
                        "title": issue.title,
                        "description": issue.description,
                        "status": issue.status,
                        "assignee": issue.assignee,
                        "project": issue.project,
                        "priority": issue.priority,
                        "labels": issue.labels,
                        "url": issue.url,
                        "created_at": issue.created_at
                    }
                }
            else:
                result = {"success": False, "error": "Failed to create issue"}
        
        elif tool_name == "get_linear_issues":
            issues = await linear_integration.get_issues(
                project_id=arguments.get("project_id"),
                assignee_id=arguments.get("assignee_id"),
                status=arguments.get("status"),
                limit=arguments.get("limit", 50)
            )
            
            result = {
                "success": True,
                "issues": [
                    {
                        "id": issue.id,
                        "title": issue.title,
                        "description": issue.description,
                        "status": issue.status,
                        "assignee": issue.assignee,
                        "project": issue.project,
                        "priority": issue.priority,
                        "labels": issue.labels,
                        "url": issue.url,
                        "created_at": issue.created_at,
                        "updated_at": issue.updated_at
                    }
                    for issue in issues
                ],
                "count": len(issues)
            }
        
        elif tool_name == "update_linear_issue":
            issue_id = arguments["issue_id"]
            updates = {k: v for k, v in arguments.items() if k != "issue_id" and v is not None}
            
            updated_issue = await linear_integration.update_issue(issue_id, updates)
            
            if updated_issue:
                result = {
                    "success": True,
                    "issue": {
                        "id": updated_issue.id,
                        "title": updated_issue.title,
                        "description": updated_issue.description,
                        "status": updated_issue.status,
                        "assignee": updated_issue.assignee,
                        "project": updated_issue.project,
                        "priority": updated_issue.priority,
                        "labels": updated_issue.labels,
                        "url": updated_issue.url,
                        "updated_at": updated_issue.updated_at
                    }
                }
            else:
                result = {"success": False, "error": f"Failed to update issue {issue_id}"}
        
        elif tool_name == "search_linear_issues":
            issues = await linear_integration.search_issues(
                query=arguments["query"],
                limit=arguments.get("limit", 20)
            )
            
            result = {
                "success": True,
                "query": arguments["query"],
                "issues": [
                    {
                        "id": issue.id,
                        "title": issue.title,
                        "description": issue.description,
                        "status": issue.status,
                        "assignee": issue.assignee,
                        "project": issue.project,
                        "priority": issue.priority,
                        "url": issue.url
                    }
                    for issue in issues
                ],
                "count": len(issues)
            }
        
        elif tool_name == "create_linear_project":
            project = await linear_integration.create_project(
                name=arguments["name"],
                description=arguments["description"],
                team_id=arguments.get("team_id")
            )
            
            if project:
                result = {
                    "success": True,
                    "project": {
                        "id": project.id,
                        "name": project.name,
                        "description": project.description,
                        "status": project.status,
                        "progress": project.progress,
                        "url": project.url,
                        "created_at": project.created_at
                    }
                }
            else:
                result = {"success": False, "error": "Failed to create project"}
        
        elif tool_name == "get_linear_projects":
            projects = await linear_integration.get_projects(
                team_id=arguments.get("team_id")
            )
            
            result = {
                "success": True,
                "projects": [
                    {
                        "id": project.id,
                        "name": project.name,
                        "description": project.description,
                        "status": project.status,
                        "progress": project.progress,
                        "url": project.url,
                        "created_at": project.created_at,
                        "updated_at": project.updated_at
                    }
                    for project in projects
                ],
                "count": len(projects)
            }
        
        elif tool_name == "get_linear_teams":
            teams = await linear_integration.get_teams()
            
            result = {
                "success": True,
                "teams": [
                    {
                        "id": team.id,
                        "name": team.name,
                        "description": team.description,
                        "members": team.members,
                        "created_at": team.created_at
                    }
                    for team in teams
                ],
                "count": len(teams)
            }
        
        elif tool_name == "get_linear_health":
            health_status = await linear_integration.get_health_status()
            result = {
                "success": True,
                "health": health_status
            }
        
        else:
            result = {"success": False, "error": f"Unknown tool: {tool_name}"}
        
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )
            ]
        )
    
    except Exception as e:
        logger.error(f"Error calling tool {request.name}: {e}")
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=json.dumps({
                        "success": False,
                        "error": str(e),
                        "tool": request.name
                    }, indent=2)
                )
            ]
        )

async def main():
    """Main entry point for Linear MCP server"""
    # Initialize Linear integration
    await linear_integration.initialize()
    
    # Run the server
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="linear-mcp-server",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=None,
                    experimental_capabilities=None
                )
            )
        )

if __name__ == "__main__":
    asyncio.run(main())

