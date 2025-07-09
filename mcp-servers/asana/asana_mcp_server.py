#!/usr/bin/env python3
"""
Asana MCP Server

A Model Context Protocol (MCP) server implementation for Asana.
Provides tools to interact with Asana's REST API for project management.
"""

import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))

try:
    from backend.core.auto_esc_config import get_config_value
    # Add base directory to path
    sys.path.append(os.path.join(os.path.dirname(__file__), "..", "base"))
    from unified_mcp_base import (
        ServiceMCPServer,
        MCPServerConfig,
    )
except ImportError as e:
    logger.error(f"Failed to import dependencies: {e}")
    logger.error(f"Python path: {sys.path}")
    sys.exit(1)

# Try to import Asana
try:
    import asana
    from asana.rest import ApiException

    ASANA_AVAILABLE = True
except ImportError:
    ASANA_AVAILABLE = False
    asana = None
    ApiException = Exception


class AsanaMCPServer(ServiceMCPServer):
    """Asana integration MCP server."""

    def __init__(self):
        config = MCPServerConfig(
            name="asana",
            port=9006,
            version="2.0.0"
        )
        super().__init__(config)
        self.asana_client = None

    async def server_specific_init(self) -> None:
        """Initialize Asana client."""
        access_token = os.getenv("ASANA_ACCESS_TOKEN")
        if not access_token:
            self.logger.warning("ASANA_ACCESS_TOKEN not set, running in demo mode")
            return

        if not ASANA_AVAILABLE:
            self.logger.warning("asana package not installed, running in demo mode")
            return

        try:
            configuration = asana.Configuration()
            configuration.access_token = access_token
            self.asana_client = asana.ApiClient(configuration)
            self.logger.info("Asana client initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize Asana client: {e}")

    async def server_specific_cleanup(self) -> None:
        """Cleanup Asana resources."""
        if self.asana_client:
            self.asana_client = None
        self.logger.info("Asana cleanup complete")

    async def check_server_health(self) -> bool:
        """Check Asana connectivity."""
        if not self.asana_client:
            return True  # Demo mode is considered healthy

        try:
            # Try to get user info
            users_api = asana.UsersApi(self.asana_client)
            users_api.get_user("me")
            return True
        except Exception as e:
            self.logger.error(f"Asana health check failed: {e}")
            return False

    async def get_tools(self) -> list[dict[str, Any]]:
        """Get Asana tools."""
        return [
            {
                "name": "list_tasks",
                "description": "List Asana tasks",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "project_id": {
                            "type": "string",
                            "description": "Optional project ID filter",
                        },
                        "assignee": {
                            "type": "string",
                            "description": "Assignee email or 'me'",
                        },
                        "completed": {"type": "boolean", "default": False},
                        "limit": {"type": "integer", "default": 20},
                    },
                },
            },
            {
                "name": "create_task",
                "description": "Create a new Asana task",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "notes": {"type": "string"},
                        "project_id": {"type": "string"},
                        "assignee": {"type": "string"},
                        "due_on": {"type": "string", "format": "date"},
                        "tags": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["name"],
                },
            },
            {
                "name": "update_task",
                "description": "Update an Asana task",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "task_id": {"type": "string"},
                        "name": {"type": "string"},
                        "notes": {"type": "string"},
                        "completed": {"type": "boolean"},
                        "due_on": {"type": "string", "format": "date"},
                    },
                    "required": ["task_id"],
                },
            },
            {
                "name": "get_project_status",
                "description": "Get project status and metrics",
                "inputSchema": {
                    "type": "object",
                    "properties": {"project_id": {"type": "string"}},
                    "required": ["project_id"],
                },
            },
            {
                "name": "list_projects",
                "description": "List available Asana projects",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "workspace_id": {
                            "type": "string",
                            "description": "Optional workspace ID",
                        },
                        "limit": {"type": "integer", "default": 10},
                    },
                },
            },
        ]

    async def execute_tool(self, name: str, arguments: dict[str, Any]) -> Any:
        """Execute Asana tool."""
        if name == "list_tasks":
            return await self._list_tasks(arguments)
        elif name == "create_task":
            return await self._create_task(arguments)
        elif name == "update_task":
            return await self._update_task(arguments)
        elif name == "get_project_status":
            return await self._get_project_status(arguments)
        elif name == "list_projects":
            return await self._list_projects(arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")

    async def _list_tasks(self, args: dict[str, Any]) -> dict[str, Any]:
        """List Asana tasks."""
        try:
            # Demo data if no client
            if not self.asana_client:
                return {
                    "tasks": [
                        {
                            "gid": "task_1",
                            "name": "Review Q1 marketing strategy",
                            "completed": False,
                            "due_on": "2025-01-15",
                            "assignee": {"name": "CEO"},
                            "projects": [{"name": "Q1 Planning"}],
                        },
                        {
                            "gid": "task_2",
                            "name": "Approve new hire requisitions",
                            "completed": False,
                            "due_on": "2025-01-10",
                            "assignee": {"name": "CEO"},
                            "projects": [{"name": "HR"}],
                        },
                    ],
                    "total": 2,
                }

            # Real Asana API call would go here
            asana.TasksApi(self.asana_client)
            # Implementation would query tasks
            return {"tasks": [], "total": 0}

        except Exception as e:
            self.logger.error(f"Failed to list tasks: {e}")
            return {"error": str(e), "tasks": []}

    async def _create_task(self, args: dict[str, Any]) -> dict[str, Any]:
        """Create Asana task."""
        try:
            name = args["name"]

            # Demo response
            if not self.asana_client:
                task_id = f"task_{datetime.utcnow().timestamp():.0f}"
                return {
                    "gid": task_id,
                    "name": name,
                    "notes": args.get("notes", ""),
                    "created_at": datetime.utcnow().isoformat(),
                    "permalink_url": f"https://app.asana.com/0/0/{task_id}",
                }

            # Real Asana API call would go here
            return {"error": "Not implemented"}

        except Exception as e:
            self.logger.error(f"Failed to create task: {e}")
            return {"error": str(e)}

    async def _update_task(self, args: dict[str, Any]) -> dict[str, Any]:
        """Update Asana task."""
        try:
            task_id = args["task_id"]

            # Demo response
            if not self.asana_client:
                return {
                    "gid": task_id,
                    "updated": True,
                    "modified_at": datetime.utcnow().isoformat(),
                }

            # Real Asana API call would go here
            return {"error": "Not implemented"}

        except Exception as e:
            self.logger.error(f"Failed to update task: {e}")
            return {"error": str(e)}

    async def _get_project_status(self, args: dict[str, Any]) -> dict[str, Any]:
        """Get project status and metrics."""
        try:
            project_id = args["project_id"]

            # Demo project status
            return {
                "project_id": project_id,
                "name": "Q1 Strategic Initiatives",
                "status": {"color": "green", "text": "On Track"},
                "metrics": {
                    "total_tasks": 45,
                    "completed_tasks": 28,
                    "overdue_tasks": 3,
                    "tasks_due_this_week": 8,
                    "completion_percentage": 62.2,
                },
                "milestones": [
                    {
                        "name": "Strategy Document Complete",
                        "due_on": "2025-01-15",
                        "status": "at_risk",
                    },
                    {
                        "name": "Team Reviews Complete",
                        "due_on": "2025-01-30",
                        "status": "on_track",
                    },
                ],
                "recent_updates": [
                    {
                        "text": "Marketing plan approved",
                        "created_at": "2025-01-03T10:00:00Z",
                    }
                ],
            }

        except Exception as e:
            self.logger.error(f"Failed to get project status: {e}")
            return {"error": str(e)}

    async def _list_projects(self, args: dict[str, Any]) -> dict[str, Any]:
        """List Asana projects."""
        try:
            # Demo data
            if not self.asana_client:
                return {
                    "projects": [
                        {
                            "gid": "proj_1",
                            "name": "Q1 Strategic Initiatives",
                            "color": "light-green",
                            "notes": "Key initiatives for Q1 2025",
                        },
                        {
                            "gid": "proj_2",
                            "name": "Product Roadmap 2025",
                            "color": "light-blue",
                            "notes": "Product development roadmap",
                        },
                    ],
                    "total": 2,
                }

            # Real Asana API call would go here
            return {"projects": [], "total": 0}

        except Exception as e:
            self.logger.error(f"Failed to list projects: {e}")
            return {"error": str(e), "projects": []}


def main():
    """Main entry point for the Asana MCP server."""
    # Create and run the server
    asana_server = AsanaMCPServer()
    asana_server.run()


if __name__ == "__main__":
    # If running as FastAPI app
    if get_config_value("run_as_fastapi", "false").lower() == "true":
        import uvicorn
        from fastapi import APIRouter, FastAPI

        # FastAPI app created by unified base
        router = APIRouter(prefix="/mcp/asana")

        @router.get("/health")
        async def health():
            return {"status": "healthy", "service": "asana-mcp-server"}

        app.include_router(router)

        # Run with uvicorn
        uvicorn.run(
            app,
            host="127.0.0.1",  # Changed from 0.0.0.0 for security. Use environment variable for production
            port=int(get_config_value("port", "9100")),
            log_level="info",
        )
    else:
        # Run as MCP server
        main()
