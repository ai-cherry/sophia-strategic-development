"""
Asana Integration API Routes for Sophia AI
Provides endpoints for Asana project management data via MCP server.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import aiohttp
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/integrations/asana", tags=["asana"])


# Pydantic models for request/response
class AsanaProjectSummary(BaseModel):
    gid: str
    name: str
    status: str
    progress: int
    owner: Optional[str] = None
    team: Optional[str] = None
    due_date: Optional[str] = None
    budget: Optional[float] = None
    spent: Optional[float] = None
    risk_level: Optional[str] = None


class AsanaTaskSummary(BaseModel):
    gid: str
    name: str
    completed: bool
    assignee: Optional[str] = None
    due_date: Optional[str] = None
    project: Optional[str] = None


class AsanaTeamSummary(BaseModel):
    gid: str
    name: str
    project_count: int
    member_count: Optional[int] = None


class AsanaIntegrationHealth(BaseModel):
    status: str
    last_sync: str
    api_health: bool
    total_projects: int
    total_tasks: int
    sync_errors: List[str] = []


class AsanaMCPClient:
    """Client for communicating with Asana MCP server."""

    def __init__(self):
        self.mcp_url = "http://asana-mcp:3006"
        self.timeout = 30

    async def call_tool(
        self, tool_name: str, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Call a tool on the Asana MCP server."""
        try:
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            ) as session:
                payload = {
                    "method": "tools/call",
                    "params": {"name": tool_name, "arguments": arguments},
                }

                async with session.post(
                    f"{self.mcp_url}/mcp", json=payload
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        # Parse the text content from MCP response
                        if "result" in result and "content" in result["result"]:
                            content = result["result"]["content"][0]["text"]
                            return json.loads(content)
                        return result
                    else:
                        error_text = await response.text()
                        raise Exception(
                            f"MCP server error {response.status}: {error_text}"
                        )
        except Exception as e:
            logger.error(f"Error calling Asana MCP tool {tool_name}: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"Asana integration error: {str(e)}"
            )


# Initialize MCP client
asana_client = AsanaMCPClient()


@router.get("/health", response_model=AsanaIntegrationHealth)
async def get_asana_health():
    """Get Asana integration health status."""
    try:
        # Test connection by getting projects
        projects_result = await asana_client.call_tool("get_projects", {"limit": 1})

        total_projects = projects_result.get("total_count", 0)

        # Test getting tasks for health check
        if projects_result.get("projects"):
            first_project = projects_result["projects"][0]
            tasks_result = await asana_client.call_tool(
                "get_project_tasks", {"project_gid": first_project["gid"], "limit": 1}
            )
            total_tasks = tasks_result.get("task_summary", {}).get("total", 0)
        else:
            total_tasks = 0

        return AsanaIntegrationHealth(
            status="healthy",
            last_sync=datetime.now().isoformat(),
            api_health=True,
            total_projects=total_projects,
            total_tasks=total_tasks,
            sync_errors=[],
        )
    except Exception as e:
        logger.error(f"Asana health check failed: {str(e)}")
        return AsanaIntegrationHealth(
            status="unhealthy",
            last_sync=datetime.now().isoformat(),
            api_health=False,
            total_projects=0,
            total_tasks=0,
            sync_errors=[str(e)],
        )


@router.get("/projects", response_model=List[AsanaProjectSummary])
async def get_projects(
    team_gid: Optional[str] = Query(None, description="Filter by team GID"),
    archived: bool = Query(False, description="Include archived projects"),
    limit: int = Query(50, description="Maximum number of projects to return"),
):
    """Get projects from Asana."""
    try:
        arguments = {"archived": archived, "limit": min(limit, 100)}

        if team_gid:
            arguments["team_gid"] = team_gid

        result = await asana_client.call_tool("get_projects", arguments)

        projects = []
        for project in result.get("projects", []):
            # Extract custom fields for budget and risk
            custom_fields = project.get("custom_fields", {})
            budget = (
                custom_fields.get("budget") if isinstance(custom_fields, dict) else None
            )
            spent = (
                custom_fields.get("spent") if isinstance(custom_fields, dict) else None
            )
            risk_level = (
                custom_fields.get("risk_level")
                if isinstance(custom_fields, dict)
                else None
            )

            projects.append(
                AsanaProjectSummary(
                    gid=project["gid"],
                    name=project.get("name", "Unnamed Project"),
                    status=_map_asana_status(project.get("current_status")),
                    progress=_calculate_progress(project),
                    owner=(
                        project.get("owner", {}).get("name")
                        if project.get("owner")
                        else None
                    ),
                    team=(
                        project.get("team", {}).get("name")
                        if project.get("team")
                        else None
                    ),
                    due_date=project.get("due_date"),
                    budget=budget,
                    spent=spent,
                    risk_level=risk_level,
                )
            )

        return projects
    except Exception as e:
        logger.error(f"Error getting Asana projects: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get projects: {str(e)}")


@router.get("/projects/{project_gid}")
async def get_project_details(project_gid: str):
    """Get detailed information about a specific project."""
    try:
        result = await asana_client.call_tool(
            "get_project_details", {"project_gid": project_gid}
        )
        return result
    except Exception as e:
        logger.error(f"Error getting project details for {project_gid}: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get project details: {str(e)}"
        )


@router.get("/projects/{project_gid}/tasks", response_model=List[AsanaTaskSummary])
async def get_project_tasks(
    project_gid: str,
    completed_since: Optional[str] = Query(
        None, description="ISO date string for completed tasks filter"
    ),
    limit: int = Query(100, description="Maximum number of tasks to return"),
):
    """Get tasks for a specific project."""
    try:
        arguments = {"project_gid": project_gid, "limit": min(limit, 100)}

        if completed_since:
            arguments["completed_since"] = completed_since

        result = await asana_client.call_tool("get_project_tasks", arguments)

        tasks = []
        for task in result.get("tasks", []):
            tasks.append(
                AsanaTaskSummary(
                    gid=task["gid"],
                    name=task.get("name", "Unnamed Task"),
                    completed=task.get("completed", False),
                    assignee=(
                        task.get("assignee", {}).get("name")
                        if task.get("assignee")
                        else None
                    ),
                    due_date=task.get("due_date"),
                    project=project_gid,
                )
            )

        return tasks
    except Exception as e:
        logger.error(f"Error getting tasks for project {project_gid}: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get project tasks: {str(e)}"
        )


@router.get("/teams", response_model=List[AsanaTeamSummary])
async def get_teams(
    workspace_gid: Optional[str] = Query(None, description="Workspace GID")
):
    """Get teams in the workspace."""
    try:
        arguments = {}
        if workspace_gid:
            arguments["workspace_gid"] = workspace_gid

        result = await asana_client.call_tool("get_teams", arguments)

        teams = []
        for team in result.get("teams", []):
            # Get project count for each team
            try:
                team_projects = await asana_client.call_tool(
                    "get_team_projects", {"team_gid": team["gid"]}
                )
                project_count = team_projects.get("project_count", 0)
            except Exception:
                project_count = 0

            teams.append(
                AsanaTeamSummary(
                    gid=team["gid"],
                    name=team.get("name", "Unnamed Team"),
                    project_count=project_count,
                )
            )

        return teams
    except Exception as e:
        logger.error(f"Error getting Asana teams: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get teams: {str(e)}")


@router.get("/search/tasks", response_model=List[AsanaTaskSummary])
async def search_tasks(
    text: Optional[str] = Query(None, description="Text to search for"),
    assignee: Optional[str] = Query(None, description="User GID to filter by assignee"),
    project_gid: Optional[str] = Query(None, description="Project GID to limit search"),
    completed: Optional[bool] = Query(None, description="Filter by completion status"),
    due_date_before: Optional[str] = Query(
        None, description="ISO date to filter tasks due before"
    ),
    due_date_after: Optional[str] = Query(
        None, description="ISO date to filter tasks due after"
    ),
):
    """Search for tasks with various filters."""
    try:
        arguments = {}

        if text:
            arguments["text"] = text
        if assignee:
            arguments["assignee"] = assignee
        if project_gid:
            arguments["project_gid"] = project_gid
        if completed is not None:
            arguments["completed"] = completed
        if due_date_before:
            arguments["due_date_before"] = due_date_before
        if due_date_after:
            arguments["due_date_after"] = due_date_after

        result = await asana_client.call_tool("search_tasks", arguments)

        tasks = []
        for task in result.get("tasks", []):
            # Get project name from projects array
            project_name = None
            if task.get("projects"):
                project_name = task["projects"][0].get("name")

            tasks.append(
                AsanaTaskSummary(
                    gid=task["gid"],
                    name=task.get("name", "Unnamed Task"),
                    completed=task.get("completed", False),
                    assignee=(
                        task.get("assignee", {}).get("name")
                        if task.get("assignee")
                        else None
                    ),
                    due_date=task.get("due_date"),
                    project=project_name,
                )
            )

        return tasks
    except Exception as e:
        logger.error(f"Error searching Asana tasks: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to search tasks: {str(e)}")


@router.get("/users/{user_gid}/tasks", response_model=List[AsanaTaskSummary])
async def get_user_tasks(
    user_gid: str,
    completed_since: Optional[str] = Query(
        None, description="ISO date string for completed tasks filter"
    ),
    workspace_gid: Optional[str] = Query(None, description="Workspace GID"),
):
    """Get tasks assigned to a specific user."""
    try:
        arguments = {"user_gid": user_gid}

        if completed_since:
            arguments["completed_since"] = completed_since
        if workspace_gid:
            arguments["workspace_gid"] = workspace_gid

        result = await asana_client.call_tool("get_user_tasks", arguments)

        tasks = []
        for task in result.get("tasks", []):
            # Get project name from projects array
            project_name = None
            if task.get("projects"):
                project_name = task["projects"][0].get("name")

            tasks.append(
                AsanaTaskSummary(
                    gid=task["gid"],
                    name=task.get("name", "Unnamed Task"),
                    completed=task.get("completed", False),
                    assignee=user_gid,
                    due_date=task.get("due_date"),
                    project=project_name,
                )
            )

        return tasks
    except Exception as e:
        logger.error(f"Error getting tasks for user {user_gid}: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get user tasks: {str(e)}"
        )


@router.get("/dashboard/summary")
async def get_dashboard_summary():
    """Get summary data for executive dashboard."""
    try:
        # Get projects overview
        projects_result = await asana_client.call_tool("get_projects", {"limit": 100})
        projects = projects_result.get("projects", [])

        # Calculate summary metrics
        total_projects = len(projects)
        active_projects = len([p for p in projects if not p.get("completed", False)])

        # Get recent activity (tasks completed in last 7 days)
        (datetime.now() - timedelta(days=7)).isoformat()

        # Calculate budget metrics
        total_budget = 0
        total_spent = 0

        for project in projects:
            custom_fields = project.get("custom_fields", {})
            if isinstance(custom_fields, dict):
                budget = custom_fields.get("budget", 0)
                spent = custom_fields.get("spent", 0)
                if budget:
                    total_budget += budget
                if spent:
                    total_spent += spent

        # Risk analysis
        risk_distribution = {"low": 0, "medium": 0, "high": 0}
        for project in projects:
            custom_fields = project.get("custom_fields", {})
            if isinstance(custom_fields, dict):
                risk = custom_fields.get("risk_level", "low")
                risk_distribution[risk] = risk_distribution.get(risk, 0) + 1

        return {
            "total_projects": total_projects,
            "active_projects": active_projects,
            "completed_projects": total_projects - active_projects,
            "total_budget": total_budget,
            "total_spent": total_spent,
            "budget_utilization": (
                (total_spent / total_budget * 100) if total_budget > 0 else 0
            ),
            "risk_distribution": risk_distribution,
            "sync_time": datetime.now().isoformat(),
            "health_status": "healthy",
        }
    except Exception as e:
        logger.error(f"Error getting dashboard summary: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get dashboard summary: {str(e)}"
        )


# Helper functions
def _map_asana_status(status_data: Optional[Dict]) -> str:
    """Map Asana status to simplified status."""
    if not status_data:
        return "not-started"

    status_type = status_data.get("status_type", "").lower()

    if status_type in ["complete", "approved"]:
        return "completed"
    elif status_type in ["at_risk", "off_track"]:
        return "at-risk"
    elif status_type in ["on_track", "on_hold"]:
        return "on-track"
    else:
        return "not-started"


def _calculate_progress(project: Dict[str, Any]) -> int:
    """Calculate project progress percentage."""
    # If we have task count data, use that
    task_count = project.get("task_count", 0)
    if task_count > 0:
        # Estimate progress based on task completion (simplified)
        return min(int(task_count * 10), 100)  # Rough estimation

    # Fallback to status-based progress
    status = project.get("current_status", {})
    if status:
        status_type = status.get("status_type", "").lower()
        if status_type == "complete":
            return 100
        elif status_type == "on_track":
            return 65
        elif status_type == "at_risk":
            return 45
        elif status_type == "off_track":
            return 25

    return 0
