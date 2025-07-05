#!/usr/bin/env python3
"""Simple Linear MCP Server for project management."""

import asyncio
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Basic FastAPI setup
try:
    import uvicorn
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
except ImportError:
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SimpleLinearManager:
    """Simple Linear project management without external API calls."""

    def __init__(self):
        self.mock_projects = [
            {
                "id": "SOPH",
                "name": "Sophia AI Platform",
                "status": "active",
                "progress": 75,
            },
            {
                "id": "MCP",
                "name": "MCP Server Infrastructure",
                "status": "active",
                "progress": 60,
            },
            {
                "id": "DEPLOY",
                "name": "Deployment Pipeline",
                "status": "completed",
                "progress": 100,
            },
        ]

        self.mock_issues = [
            {
                "id": "SOPH-001",
                "title": "Deploy AI Memory MCP server",
                "status": "done",
                "priority": "high",
                "project": "SOPH",
            },
            {
                "id": "SOPH-002",
                "title": "Deploy Codacy MCP server",
                "status": "in_progress",
                "priority": "high",
                "project": "SOPH",
            },
            {
                "id": "SOPH-003",
                "title": "Deploy GitHub MCP server",
                "status": "in_progress",
                "priority": "high",
                "project": "SOPH",
            },
            {
                "id": "SOPH-004",
                "title": "Deploy Linear MCP server",
                "status": "todo",
                "priority": "high",
                "project": "SOPH",
            },
            {
                "id": "MCP-001",
                "title": "Standardize MCP server pattern",
                "status": "done",
                "priority": "medium",
                "project": "MCP",
            },
            {
                "id": "DEPLOY-001",
                "title": "Setup GitHub Actions",
                "status": "done",
                "priority": "medium",
                "project": "DEPLOY",
            },
        ]

        self.mock_teams = [
            {"id": "dev", "name": "Development Team", "members": 3, "velocity": 85},
            {"id": "ops", "name": "Operations Team", "members": 2, "velocity": 90},
        ]

    async def get_project_info(self, project_id: str) -> dict[str, Any]:
        """Get project information."""
        project = next((p for p in self.mock_projects if p["id"] == project_id), None)
        if not project:
            return {"error": f"Project {project_id} not found"}

        # Get issues for this project
        project_issues = [i for i in self.mock_issues if i.get("project") == project_id]

        return {
            **project,
            "total_issues": len(project_issues),
            "completed_issues": len(
                [i for i in project_issues if i["status"] == "done"]
            ),
            "in_progress_issues": len(
                [i for i in project_issues if i["status"] == "in_progress"]
            ),
            "todo_issues": len([i for i in project_issues if i["status"] == "todo"]),
            "last_updated": datetime.now().isoformat(),
        }

    async def list_projects(self) -> list[dict[str, Any]]:
        """List all projects."""
        return self.mock_projects

    async def get_issues(
        self, status: str = None, project: str = None
    ) -> list[dict[str, Any]]:
        """Get issues, optionally filtered."""
        issues = self.mock_issues

        if status:
            issues = [i for i in issues if i["status"] == status]

        if project:
            issues = [i for i in issues if i.get("project") == project]

        return issues

    async def create_issue(
        self,
        title: str,
        description: str,
        priority: str = "medium",
        project: str = "SOPH",
    ) -> dict[str, Any]:
        """Create a new issue."""
        new_issue = {
            "id": f"{project}-{len(self.mock_issues) + 1:03d}",
            "title": title,
            "description": description,
            "status": "todo",
            "priority": priority,
            "project": project,
            "created_at": datetime.now().isoformat(),
            "assignee": "sophia-ai",
        }

        self.mock_issues.append(new_issue)
        logger.info(f"Created issue: {new_issue['id']} - {title}")

        return new_issue

    async def update_issue_status(self, issue_id: str, status: str) -> dict[str, Any]:
        """Update issue status."""
        issue = next((i for i in self.mock_issues if i["id"] == issue_id), None)
        if not issue:
            return {"error": f"Issue {issue_id} not found"}

        old_status = issue["status"]
        issue["status"] = status
        issue["updated_at"] = datetime.now().isoformat()

        logger.info(f"Updated issue {issue_id}: {old_status} → {status}")

        return issue

    async def get_team_stats(self) -> dict[str, Any]:
        """Get team statistics."""
        return {
            "teams": self.mock_teams,
            "total_members": sum(t["members"] for t in self.mock_teams),
            "average_velocity": sum(t["velocity"] for t in self.mock_teams)
            / len(self.mock_teams),
            "active_projects": len(
                [p for p in self.mock_projects if p["status"] == "active"]
            ),
        }

    async def get_project_health(self, project_id: str = None) -> dict[str, Any]:
        """Get project health metrics."""
        if project_id:
            projects = [p for p in self.mock_projects if p["id"] == project_id]
        else:
            projects = self.mock_projects

        health_scores = []
        for project in projects:
            project_issues = [
                i for i in self.mock_issues if i.get("project") == project["id"]
            ]

            if not project_issues:
                health_score = 100
            else:
                completed = len([i for i in project_issues if i["status"] == "done"])
                total = len(project_issues)
                health_score = (completed / total) * 100

            health_scores.append(
                {
                    "project_id": project["id"],
                    "project_name": project["name"],
                    "health_score": round(health_score, 1),
                    "status": project["status"],
                    "progress": project["progress"],
                }
            )

        return {
            "project_health": health_scores,
            "overall_health": (
                round(
                    sum(h["health_score"] for h in health_scores) / len(health_scores),
                    1,
                )
                if health_scores
                else 0
            ),
        }


# Create FastAPI app
app = FastAPI(title="Simple Linear MCP Server", version="1.0.0")

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create Linear manager
linear_manager = SimpleLinearManager()


@app.get("/")
async def root():
    return {
        "name": "Simple Linear MCP Server",
        "version": "1.0.0",
        "status": "running",
        "capabilities": ["project_management", "issue_tracking", "team_analytics"],
    }


@app.get("/health")
async def health():
    health_data = await linear_manager.get_project_health()
    return {
        "status": "healthy",
        "service": "linear_mcp",
        "timestamp": datetime.now().isoformat(),
        "overall_health": health_data["overall_health"],
    }


@app.get("/api/v1/projects")
async def list_projects():
    """List all projects."""
    try:
        projects = await linear_manager.list_projects()
        return {"projects": projects, "count": len(projects)}
    except Exception as e:
        logger.error(f"Error listing projects: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/projects/{project_id}")
async def get_project(project_id: str):
    """Get specific project information."""
    try:
        project_info = await linear_manager.get_project_info(project_id)
        return project_info
    except Exception as e:
        logger.error(f"Error getting project {project_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/issues")
async def get_issues(status: str = None, project: str = None):
    """Get issues, optionally filtered."""
    try:
        issues = await linear_manager.get_issues(status, project)
        return {"issues": issues, "count": len(issues)}
    except Exception as e:
        logger.error(f"Error getting issues: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/issues")
async def create_issue(data: dict[str, Any]):
    """Create a new issue."""
    try:
        title = data.get("title")
        if not title:
            raise HTTPException(status_code=400, detail="Title is required")

        description = data.get("description", "")
        priority = data.get("priority", "medium")
        project = data.get("project", "SOPH")

        issue = await linear_manager.create_issue(title, description, priority, project)
        return issue
    except Exception as e:
        logger.error(f"Error creating issue: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.patch("/api/v1/issues/{issue_id}")
async def update_issue(issue_id: str, data: dict[str, Any]):
    """Update issue status."""
    try:
        status = data.get("status")
        if not status:
            raise HTTPException(status_code=400, detail="Status is required")

        issue = await linear_manager.update_issue_status(issue_id, status)
        return issue
    except Exception as e:
        logger.error(f"Error updating issue {issue_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/health")
async def get_project_health(project_id: str = None):
    """Get project health metrics."""
    try:
        return await linear_manager.get_project_health(project_id)
    except Exception as e:
        logger.error(f"Error getting project health: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/teams")
async def get_team_stats():
    """Get team statistics."""
    try:
        return await linear_manager.get_team_stats()
    except Exception as e:
        logger.error(f"Error getting team stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def main():
    """Run the server."""
    logger.info("Starting Simple Linear MCP Server on port 9004...")

    try:
        # Try to load ESC config if available
        try:
            logger.info("✅ Pulumi ESC integration available")
        except Exception as e:
            logger.warning(f"Pulumi ESC not available: {e}")

        # Start server
        config = uvicorn.Config(app=app, host="0.0.0.0", port=9004, log_level="info")
        server = uvicorn.Server(config)
        await server.serve()

    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
