#!/usr/bin/env python3
"""
Sophia AI Unified Project Management MCP Server
Consolidates Asana, Linear, and Notion functionality
Using official Anthropic MCP SDK

Date: July 12, 2025
"""

import asyncio
import sys
from datetime import UTC, datetime, timedelta
from enum import Enum
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


class ProjectPlatform(str, Enum):
    """Supported project management platforms"""
    ASANA = "asana"
    LINEAR = "linear"
    NOTION = "notion"


class UnifiedProjectMCPServer(StandardizedMCPServer):
    """Unified Project Management MCP Server"""

    def __init__(self):
        config = ServerConfig(
            name="unified_project",
            version="2.0.0",
            port=9005,
            capabilities=["PROJECT_MANAGEMENT", "TASK_TRACKING", "KNOWLEDGE_BASE", "ANALYTICS"],
            tier="SECONDARY",
        )
        super().__init__(config)

        # Platform configurations
        self.asana_token = get_config_value("asana_access_token")
        self.linear_token = get_config_value("linear_api_key")
        self.notion_token = get_config_value("notion_api_token")
        
        # API endpoints
        self.asana_url = "https://app.asana.com/api/1.0"
        self.linear_url = "https://api.linear.app/graphql"
        self.notion_url = "https://api.notion.com/v1"

    def get_tool_definitions(self) -> list[ToolDefinition]:
        """Define unified project management tools"""
        return [
            ToolDefinition(
                name="list_projects",
                description="List projects across all platforms",
                parameters=[
                    ToolParameter(
                        name="platform",
                        type="string",
                        description="Platform to query (asana/linear/notion/all)",
                        required=False,
                    ),
                    ToolParameter(
                        name="limit",
                        type="number",
                        description="Maximum number of projects",
                        required=False,
                    ),
                ],
            ),
            ToolDefinition(
                name="create_task",
                description="Create a task in specified platform",
                parameters=[
                    ToolParameter(
                        name="platform",
                        type="string",
                        description="Platform to create task in",
                        required=True,
                    ),
                    ToolParameter(
                        name="title",
                        type="string",
                        description="Task title",
                        required=True,
                    ),
                    ToolParameter(
                        name="description",
                        type="string",
                        description="Task description",
                        required=False,
                    ),
                    ToolParameter(
                        name="project_id",
                        type="string",
                        description="Project ID",
                        required=True,
                    ),
                    ToolParameter(
                        name="assignee",
                        type="string",
                        description="Assignee email",
                        required=False,
                    ),
                    ToolParameter(
                        name="due_date",
                        type="string",
                        description="Due date (YYYY-MM-DD)",
                        required=False,
                    ),
                ],
            ),
            ToolDefinition(
                name="search_tasks",
                description="Search tasks across platforms",
                parameters=[
                    ToolParameter(
                        name="query",
                        type="string",
                        description="Search query",
                        required=True,
                    ),
                    ToolParameter(
                        name="platform",
                        type="string",
                        description="Platform to search (asana/linear/notion/all)",
                        required=False,
                    ),
                    ToolParameter(
                        name="limit",
                        type="number",
                        description="Maximum results",
                        required=False,
                    ),
                ],
            ),
            ToolDefinition(
                name="get_project_health",
                description="Get project health metrics across platforms",
                parameters=[
                    ToolParameter(
                        name="project_id",
                        type="string",
                        description="Project ID",
                        required=True,
                    ),
                    ToolParameter(
                        name="platform",
                        type="string",
                        description="Platform",
                        required=True,
                    ),
                ],
            ),
            ToolDefinition(
                name="sync_platforms",
                description="Sync data between platforms",
                parameters=[
                    ToolParameter(
                        name="source_platform",
                        type="string",
                        description="Source platform",
                        required=True,
                    ),
                    ToolParameter(
                        name="target_platform",
                        type="string",
                        description="Target platform",
                        required=True,
                    ),
                    ToolParameter(
                        name="project_id",
                        type="string",
                        description="Project to sync",
                        required=True,
                    ),
                ],
            ),
        ]

    async def handle_tool_call(
        self, tool_name: str, arguments: dict[str, Any]
    ) -> dict[str, Any]:
        """Handle unified project management tool calls"""

        if tool_name == "list_projects":
            return await self._list_projects(**arguments)
        elif tool_name == "create_task":
            return await self._create_task(**arguments)
        elif tool_name == "search_tasks":
            return await self._search_tasks(**arguments)
        elif tool_name == "get_project_health":
            return await self._get_project_health(**arguments)
        elif tool_name == "sync_platforms":
            return await self._sync_platforms(**arguments)
        else:
            raise ValueError(f"Unknown tool: {tool_name}")

    async def _list_projects(
        self, platform: Optional[str] = "all", limit: Optional[int] = 10
    ) -> dict[str, Any]:
        """List projects across platforms"""
        projects = []
        
        if platform in ["all", "asana"]:
            asana_projects = await self._get_asana_projects(limit)
            projects.extend(asana_projects)
            
        if platform in ["all", "linear"]:
            linear_projects = await self._get_linear_projects(limit)
            projects.extend(linear_projects)
            
        if platform in ["all", "notion"]:
            notion_projects = await self._get_notion_databases(limit)
            projects.extend(notion_projects)
        
        return {
            "projects": projects[:limit] if limit else projects,
            "total": len(projects),
            "platforms": ["asana", "linear", "notion"] if platform == "all" else [platform]
        }

    async def _create_task(
        self,
        platform: str,
        title: str,
        project_id: str,
        description: Optional[str] = None,
        assignee: Optional[str] = None,
        due_date: Optional[str] = None,
    ) -> dict[str, Any]:
        """Create task in specified platform"""
        if platform == ProjectPlatform.ASANA:
            return await self._create_asana_task(
                title, project_id, description, assignee, due_date
            )
        elif platform == ProjectPlatform.LINEAR:
            return await self._create_linear_issue(
                title, project_id, description, assignee, due_date
            )
        elif platform == ProjectPlatform.NOTION:
            return await self._create_notion_page(
                title, project_id, description, assignee, due_date
            )
        else:
            raise ValueError(f"Unsupported platform: {platform}")

    async def _search_tasks(
        self, query: str, platform: Optional[str] = "all", limit: Optional[int] = 10
    ) -> dict[str, Any]:
        """Search tasks across platforms"""
        results = []
        
        if platform in ["all", "asana"]:
            asana_results = await self._search_asana_tasks(query, limit)
            results.extend(asana_results)
            
        if platform in ["all", "linear"]:
            linear_results = await self._search_linear_issues(query, limit)
            results.extend(linear_results)
            
        if platform in ["all", "notion"]:
            notion_results = await self._search_notion_pages(query, limit)
            results.extend(notion_results)
        
        return {
            "results": results[:limit] if limit else results,
            "total": len(results),
            "query": query,
            "platforms": ["asana", "linear", "notion"] if platform == "all" else [platform]
        }

    async def _get_project_health(
        self, project_id: str, platform: str
    ) -> dict[str, Any]:
        """Get project health metrics"""
        # Calculate health metrics based on platform
        if platform == ProjectPlatform.ASANA:
            tasks = await self._get_asana_project_tasks(project_id)
        elif platform == ProjectPlatform.LINEAR:
            tasks = await self._get_linear_project_issues(project_id)
        elif platform == ProjectPlatform.NOTION:
            tasks = await self._get_notion_database_items(project_id)
        else:
            raise ValueError(f"Unsupported platform: {platform}")
        
        # Calculate metrics
        total_tasks = len(tasks)
        completed_tasks = sum(1 for t in tasks if t.get("completed", False))
        overdue_tasks = sum(1 for t in tasks if self._is_overdue(t))
        
        health_score = 100
        if total_tasks > 0:
            completion_rate = (completed_tasks / total_tasks) * 100
            overdue_rate = (overdue_tasks / total_tasks) * 100
            health_score = max(0, min(100, completion_rate - (overdue_rate * 2)))
        
        return {
            "project_id": project_id,
            "platform": platform,
            "health_score": round(health_score, 2),
            "metrics": {
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks,
                "overdue_tasks": overdue_tasks,
                "completion_rate": round((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0, 2),
            },
            "status": self._get_health_status(health_score),
        }

    def _is_overdue(self, task: dict[str, Any]) -> bool:
        """Check if task is overdue"""
        if task.get("completed"):
            return False
        due_date = task.get("due_date") or task.get("due_on")
        if not due_date:
            return False
        try:
            due = datetime.fromisoformat(due_date.replace("Z", "+00:00"))
            return due < datetime.now(UTC)
        except:
            return False

    def _get_health_status(self, score: float) -> str:
        """Get health status from score"""
        if score >= 80:
            return "healthy"
        elif score >= 60:
            return "at_risk"
        else:
            return "critical"

    # Platform-specific methods (simplified for brevity)
    async def _get_asana_projects(self, limit: int) -> list[dict[str, Any]]:
        """Get Asana projects"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.asana_url}/projects",
                headers={"Authorization": f"Bearer {self.asana_token}"},
                params={"limit": limit}
            )
            data = response.json()
            return [
                {
                    "id": p["gid"],
                    "name": p["name"],
                    "platform": "asana",
                    "url": f"https://app.asana.com/0/{p['gid']}"
                }
                for p in data.get("data", [])
            ]

    async def _get_linear_projects(self, limit: int) -> list[dict[str, Any]]:
        """Get Linear projects"""
        query = """
        query GetProjects($limit: Int!) {
            teams(first: $limit) {
                nodes {
                    id
                    name
                    key
                }
            }
        }
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.linear_url,
                headers={"Authorization": self.linear_token},
                json={"query": query, "variables": {"limit": limit}}
            )
            data = response.json()
            teams = data.get("data", {}).get("teams", {}).get("nodes", [])
            return [
                {
                    "id": t["id"],
                    "name": t["name"],
                    "platform": "linear",
                    "url": f"https://linear.app/team/{t['key']}"
                }
                for t in teams
            ]

    async def _get_notion_databases(self, limit: int) -> list[dict[str, Any]]:
        """Get Notion databases"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.notion_url}/search",
                headers={
                    "Authorization": f"Bearer {self.notion_token}",
                    "Notion-Version": "2022-06-28"
                },
                json={"filter": {"property": "object", "value": "database"}}
            )
            data = response.json()
            databases = data.get("results", [])[:limit]
            return [
                {
                    "id": db["id"],
                    "name": db.get("title", [{}])[0].get("plain_text", "Untitled"),
                    "platform": "notion",
                    "url": db["url"]
                }
                for db in databases
            ]

    # Additional platform-specific methods would be implemented here...


if __name__ == "__main__":
    server = UnifiedProjectMCPServer()
    asyncio.run(server.run()) 