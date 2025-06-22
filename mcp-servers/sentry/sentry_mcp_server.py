"""
Sentry MCP Server for Sophia AI
Provides error tracking, monitoring, and automated debugging capabilities
"""

import os
import json
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime
import asyncio
import subprocess
import sys

import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, Resource
from dotenv import load_dotenv
import structlog

# Load environment variables
load_dotenv()

# Configure structured logging
logger = structlog.get_logger()

def get_pulumi_esc_value(key: str, default: str = None) -> str:
    """Get value from Pulumi ESC using CLI."""
    try:
        # Try to get from Pulumi ESC
        result = subprocess.run(
            ["pulumi", "env", "get", "scoobyjava-org/default/sophia-ai-production", key],
            capture_output=True,
            text=True,
            check=True
        )
        value = result.stdout.strip()
        if value:
            return value
    except subprocess.CalledProcessError:
        logger.warning(f"Failed to get {key} from Pulumi ESC, falling back to environment")
    except FileNotFoundError:
        logger.warning("Pulumi CLI not found, falling back to environment variables")
    
    # Fall back to environment variable
    return os.getenv(key, default)

class SentryMCPServer:
    """MCP Server for Sentry integration with Pulumi ESC support."""
    
    def __init__(self):
        self.server = Server("sentry-mcp")
        
        # Get configuration from Pulumi ESC or environment
        self.api_token = get_pulumi_esc_value("SENTRY_API_TOKEN")
        self.organization_slug = get_pulumi_esc_value("SENTRY_ORGANIZATION_SLUG", "pay-ready")
        self.base_url = "https://sentry.io/api/0"
        
        if not self.api_token:
            logger.error("SENTRY_API_TOKEN not found in Pulumi ESC or environment")
            sys.exit(1)
        self.client = httpx.AsyncClient(
            headers={
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json"
            },
            timeout=30.0
        )
        
        # Register handlers
        self.server.list_tools.add_handler(self.handle_list_tools)
        self.server.call_tool.add_handler(self.handle_call_tool)
        self.server.list_resources.add_handler(self.handle_list_resources)
        self.server.read_resource.add_handler(self.handle_read_resource)
        
        logger.info("Sentry MCP Server initialized", 
                   organization=self.organization_slug)
    
    async def handle_list_tools(self) -> List[Tool]:
        """List available Sentry tools."""
        return [
            Tool(
                name="get_sentry_issue",
                description="Fetch detailed information about a Sentry issue",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "project_slug": {
                            "type": "string",
                            "description": "The project slug (e.g., 'pay-ready')"
                        },
                        "issue_id": {
                            "type": "string",
                            "description": "The Sentry issue ID"
                        }
                    },
                    "required": ["project_slug", "issue_id"]
                }
            ),
            Tool(
                name="list_sentry_issues",
                description="List recent issues from a Sentry project",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "project_slug": {
                            "type": "string",
                            "description": "The project slug"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Number of issues to return (default: 10)",
                            "default": 10
                        },
                        "status": {
                            "type": "string",
                            "description": "Filter by status: unresolved, resolved, ignored",
                            "enum": ["unresolved", "resolved", "ignored"],
                            "default": "unresolved"
                        }
                    },
                    "required": ["project_slug"]
                }
            ),
            Tool(
                name="get_issue_events",
                description="Get events associated with a Sentry issue",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "issue_id": {
                            "type": "string",
                            "description": "The Sentry issue ID"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Number of events to return",
                            "default": 5
                        }
                    },
                    "required": ["issue_id"]
                }
            ),
            Tool(
                name="create_sentry_alert",
                description="Create an alert rule for a Sentry project",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "project_slug": {
                            "type": "string",
                            "description": "The project slug"
                        },
                        "name": {
                            "type": "string",
                            "description": "Alert rule name"
                        },
                        "conditions": {
                            "type": "object",
                            "description": "Alert conditions"
                        },
                        "actions": {
                            "type": "array",
                            "description": "Actions to take when alert triggers"
                        }
                    },
                    "required": ["project_slug", "name", "conditions", "actions"]
                }
            ),
            Tool(
                name="resolve_issue",
                description="Mark a Sentry issue as resolved",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "issue_id": {
                            "type": "string",
                            "description": "The Sentry issue ID to resolve"
                        }
                    },
                    "required": ["issue_id"]
                }
            )
        ]
    
    async def handle_call_tool(self, name: str, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle tool execution."""
        try:
            if name == "get_sentry_issue":
                result = await self.get_issue(
                    arguments["project_slug"],
                    arguments["issue_id"]
                )
            elif name == "list_sentry_issues":
                result = await self.list_issues(
                    arguments["project_slug"],
                    arguments.get("limit", 10),
                    arguments.get("status", "unresolved")
                )
            elif name == "get_issue_events":
                result = await self.get_issue_events(
                    arguments["issue_id"],
                    arguments.get("limit", 5)
                )
            elif name == "create_sentry_alert":
                result = await self.create_alert(
                    arguments["project_slug"],
                    arguments["name"],
                    arguments["conditions"],
                    arguments["actions"]
                )
            elif name == "resolve_issue":
                result = await self.resolve_issue(arguments["issue_id"])
            else:
                result = {"error": f"Unknown tool: {name}"}
            
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
            
        except Exception as e:
            logger.error("Tool execution failed", 
                        tool=name, 
                        error=str(e),
                        arguments=arguments)
            return [TextContent(
                type="text",
                text=json.dumps({
                    "error": str(e),
                    "tool": name,
                    "arguments": arguments
                }, indent=2)
            )]
    
    async def handle_list_resources(self) -> List[Resource]:
        """List available Sentry resources."""
        return [
            Resource(
                uri=f"sentry://organizations/{self.organization_slug}",
                name=f"Sentry Organization: {self.organization_slug}",
                description="Organization overview and settings",
                mimeType="application/json"
            ),
            Resource(
                uri=f"sentry://organizations/{self.organization_slug}/projects",
                name="Sentry Projects",
                description="List of all projects in the organization",
                mimeType="application/json"
            ),
            Resource(
                uri=f"sentry://organizations/{self.organization_slug}/stats",
                name="Organization Statistics",
                description="Error rates, performance metrics, and trends",
                mimeType="application/json"
            )
        ]
    
    async def handle_read_resource(self, uri: str) -> TextContent:
        """Read a Sentry resource."""
        try:
            if uri == f"sentry://organizations/{self.organization_slug}":
                result = await self.get_organization_info()
            elif uri == f"sentry://organizations/{self.organization_slug}/projects":
                result = await self.list_projects()
            elif uri == f"sentry://organizations/{self.organization_slug}/stats":
                result = await self.get_organization_stats()
            else:
                result = {"error": f"Unknown resource: {uri}"}
            
            return TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )
            
        except Exception as e:
            logger.error("Resource read failed", uri=uri, error=str(e))
            return TextContent(
                type="text",
                text=json.dumps({"error": str(e), "uri": uri}, indent=2)
            )
    
    async def get_issue(self, project_slug: str, issue_id: str) -> Dict[str, Any]:
        """Fetch detailed information about a Sentry issue."""
        url = f"{self.base_url}/issues/{issue_id}/"
        response = await self.client.get(url)
        response.raise_for_status()
        
        data = response.json()
        
        # Extract relevant information
        return {
            "id": data["id"],
            "title": data["title"],
            "culprit": data.get("culprit", "Unknown"),
            "permalink": data["permalink"],
            "firstSeen": data["firstSeen"],
            "lastSeen": data["lastSeen"],
            "count": data["count"],
            "userCount": data["userCount"],
            "level": data["level"],
            "status": data["status"],
            "statusDetails": data.get("statusDetails", {}),
            "project": {
                "id": data["project"]["id"],
                "name": data["project"]["name"],
                "slug": data["project"]["slug"]
            },
            "type": data.get("type", "error"),
            "metadata": data.get("metadata", {}),
            "tags": [{"key": tag["key"], "value": tag["value"]} for tag in data.get("tags", [])]
        }
    
    async def list_issues(self, project_slug: str, limit: int = 10, status: str = "unresolved") -> Dict[str, Any]:
        """List recent issues from a Sentry project."""
        url = f"{self.base_url}/projects/{self.organization_slug}/{project_slug}/issues/"
        params = {
            "limit": limit,
            "query": f"is:{status}"
        }
        
        response = await self.client.get(url, params=params)
        response.raise_for_status()
        
        issues = response.json()
        
        return {
            "project": project_slug,
            "status_filter": status,
            "count": len(issues),
            "issues": [
                {
                    "id": issue["id"],
                    "title": issue["title"],
                    "culprit": issue.get("culprit", "Unknown"),
                    "permalink": issue["permalink"],
                    "level": issue["level"],
                    "status": issue["status"],
                    "count": issue["count"],
                    "userCount": issue["userCount"],
                    "firstSeen": issue["firstSeen"],
                    "lastSeen": issue["lastSeen"]
                }
                for issue in issues
            ]
        }
    
    async def get_issue_events(self, issue_id: str, limit: int = 5) -> Dict[str, Any]:
        """Get events associated with a Sentry issue."""
        url = f"{self.base_url}/issues/{issue_id}/events/"
        params = {"limit": limit}
        
        response = await self.client.get(url, params=params)
        response.raise_for_status()
        
        events = response.json()
        
        return {
            "issue_id": issue_id,
            "event_count": len(events),
            "events": [
                {
                    "id": event["id"],
                    "eventID": event["eventID"],
                    "dateCreated": event["dateCreated"],
                    "message": event.get("message", ""),
                    "title": event.get("title", ""),
                    "platform": event.get("platform", "unknown"),
                    "environment": event.get("environment", ""),
                    "release": event.get("release", {}).get("version", "") if event.get("release") else "",
                    "user": event.get("user", {}),
                    "contexts": event.get("contexts", {}),
                    "tags": event.get("tags", [])
                }
                for event in events
            ]
        }
    
    async def create_alert(self, project_slug: str, name: str, conditions: Dict, actions: List) -> Dict[str, Any]:
        """Create an alert rule for a Sentry project."""
        url = f"{self.base_url}/projects/{self.organization_slug}/{project_slug}/rules/"
        
        data = {
            "name": name,
            "conditions": conditions,
            "actions": actions,
            "frequency": 30,  # Check every 30 minutes
            "environment": None  # All environments
        }
        
        response = await self.client.post(url, json=data)
        response.raise_for_status()
        
        alert = response.json()
        
        return {
            "id": alert["id"],
            "name": alert["name"],
            "dateCreated": alert["dateCreated"],
            "project": project_slug,
            "conditions": alert["conditions"],
            "actions": alert["actions"],
            "status": "created"
        }
    
    async def resolve_issue(self, issue_id: str) -> Dict[str, Any]:
        """Mark a Sentry issue as resolved."""
        url = f"{self.base_url}/issues/{issue_id}/"
        data = {"status": "resolved"}
        
        response = await self.client.put(url, json=data)
        response.raise_for_status()
        
        return {
            "issue_id": issue_id,
            "status": "resolved",
            "resolved_at": datetime.utcnow().isoformat(),
            "success": True
        }
    
    async def get_organization_info(self) -> Dict[str, Any]:
        """Get organization information."""
        url = f"{self.base_url}/organizations/{self.organization_slug}/"
        response = await self.client.get(url)
        response.raise_for_status()
        
        org = response.json()
        
        return {
            "id": org["id"],
            "slug": org["slug"],
            "name": org["name"],
            "dateCreated": org["dateCreated"],
            "status": org["status"],
            "features": org.get("features", []),
            "quota": org.get("quota", {}),
            "access": org.get("access", [])
        }
    
    async def list_projects(self) -> Dict[str, Any]:
        """List all projects in the organization."""
        url = f"{self.base_url}/organizations/{self.organization_slug}/projects/"
        response = await self.client.get(url)
        response.raise_for_status()
        
        projects = response.json()
        
        return {
            "organization": self.organization_slug,
            "project_count": len(projects),
            "projects": [
                {
                    "id": project["id"],
                    "name": project["name"],
                    "slug": project["slug"],
                    "platform": project.get("platform", "unknown"),
                    "dateCreated": project["dateCreated"],
                    "firstEvent": project.get("firstEvent"),
                    "features": project.get("features", []),
                    "status": project["status"]
                }
                for project in projects
            ]
        }
    
    async def get_organization_stats(self) -> Dict[str, Any]:
        """Get organization statistics."""
        url = f"{self.base_url}/organizations/{self.organization_slug}/stats/"
        params = {
            "stat": "received,rejected,blacklisted",
            "since": "1d"  # Last 24 hours
        }
        
        response = await self.client.get(url, params=params)
        response.raise_for_status()
        
        stats = response.json()
        
        return {
            "organization": self.organization_slug,
            "period": "last_24_hours",
            "stats": stats
        }
    
    async def run(self):
        """Run the MCP server."""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(read_stream, write_stream)

async def main():
    """Main entry point."""
    server = SentryMCPServer()
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())
