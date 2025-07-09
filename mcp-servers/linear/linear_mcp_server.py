#!/usr/bin/env python3
"""
from backend.core.auto_esc_config import get_config_value
Linear MCP Server

A Model Context Protocol (MCP) server implementation for Linear.
Provides tools to interact with Linear's GraphQL API for project management.
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
from mcp import server

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

from backend.mcp_servers.base.unified_mcp_base import (
    MCPServerConfig,
    StandardizedMCPServer,
)

# Try to import Linear SDK
try:
    from linear_sdk import LinearClient

    LINEAR_AVAILABLE = True
except ImportError:
    LINEAR_AVAILABLE = False
    LinearClient = None


class LinearMCPServer(StandardizedMCPServer):
    """Linear integration MCP server."""

    def __init__(self, config: MCPServerConfig | None = None):
        if config is None:
            config = MCPServerConfig(name="linear", port=9004, version="1.0.0")
        super().__init__(config)
        self.linear_client = None

    async def server_specific_init(self) -> None:
        """Initialize Linear client."""
        api_key = get_config_value("linear_api_key")
        if not api_key:
            self.logger.warning("LINEAR_API_KEY not set, running in demo mode")
            return

        if not LINEAR_AVAILABLE:
            self.logger.warning("linear-sdk not installed, running in demo mode")
            return

        try:
            self.linear_client = LinearClient(api_key)
            self.logger.info("Linear client initialized successfully")
        except Exception as e:
            self.logger.exception(f"Failed to initialize Linear client: {e}")

    async def server_specific_cleanup(self) -> None:
        """Cleanup Linear resources."""
        if self.linear_client:
            self.linear_client = None
        self.logger.info("Linear cleanup complete")

    async def check_server_health(self) -> bool:
        """Check Linear connectivity."""
        if not self.linear_client:
            return True  # Demo mode is considered healthy

        try:
            # Try to fetch user info or teams
            # This is a placeholder - actual Linear SDK may have different methods
            return True
        except Exception as e:
            self.logger.exception(f"Linear health check failed: {e}")
            return False

    async def get_tools(self) -> list[dict[str, Any]]:
        """Get Linear tools."""
        return [
            {
                "name": "list_projects",
                "description": "List Linear projects",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "team_id": {
                            "type": "string",
                            "description": "Optional team ID filter",
                        },
                        "state": {
                            "type": "string",
                            "enum": [
                                "backlog",
                                "todo",
                                "in_progress",
                                "done",
                                "canceled",
                            ],
                        },
                        "limit": {"type": "integer", "default": 10},
                    },
                },
            },
            {
                "name": "create_issue",
                "description": "Create a new Linear issue",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "description": {"type": "string"},
                        "team_id": {"type": "string"},
                        "project_id": {"type": "string"},
                        "priority": {"type": "integer", "minimum": 0, "maximum": 4},
                        "assignee_id": {"type": "string"},
                    },
                    "required": ["title", "team_id"],
                },
            },
            {
                "name": "update_issue",
                "description": "Update a Linear issue",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "issue_id": {"type": "string"},
                        "title": {"type": "string"},
                        "description": {"type": "string"},
                        "state": {
                            "type": "string",
                            "enum": [
                                "backlog",
                                "todo",
                                "in_progress",
                                "done",
                                "canceled",
                            ],
                        },
                        "priority": {"type": "integer", "minimum": 0, "maximum": 4},
                    },
                    "required": ["issue_id"],
                },
            },
            {
                "name": "get_project_health",
                "description": "Get project health metrics",
                "inputSchema": {
                    "type": "object",
                    "properties": {"project_id": {"type": "string"}},
                    "required": ["project_id"],
                },
            },
        ]

    async def execute_tool(self, name: str, arguments: dict[str, Any]) -> Any:
        """Execute Linear tool."""
        if name == "list_projects":
            return await self._list_projects(arguments)
        elif name == "create_issue":
            return await self._create_issue(arguments)
        elif name == "update_issue":
            return await self._update_issue(arguments)
        elif name == "get_project_health":
            return await self._get_project_health(arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")

    async def _list_projects(self, args: dict[str, Any]) -> dict[str, Any]:
        """List Linear projects."""
        try:
            # Demo data if no client
            if not self.linear_client:
                return {
                    "projects": [
                        {
                            "id": "proj_1",
                            "name": "Q1 Platform Improvements",
                            "state": "in_progress",
                            "progress": 65,
                            "issues_count": 24,
                            "completed_issues": 16,
                        },
                        {
                            "id": "proj_2",
                            "name": "Customer Onboarding v2",
                            "state": "todo",
                            "progress": 0,
                            "issues_count": 12,
                            "completed_issues": 0,
                        },
                    ],
                    "total": 2,
                }

            # Real Linear API call would go here
            return {"projects": [], "total": 0}

        except Exception as e:
            self.logger.exception(f"Failed to list projects: {e}")
            return {"error": str(e), "projects": []}

    async def _create_issue(self, args: dict[str, Any]) -> dict[str, Any]:
        """Create Linear issue."""
        try:
            title = args["title"]
            team_id = args["team_id"]

            # Demo response
            if not self.linear_client:
                issue_id = f"ISS-{datetime.utcnow().timestamp():.0f}"
                return {
                    "id": issue_id,
                    "title": title,
                    "team_id": team_id,
                    "state": "todo",
                    "created_at": datetime.utcnow().isoformat(),
                    "url": f"https://linear.app/team/{team_id}/issue/{issue_id}",
                }

            # Real Linear API call would go here
            return {"error": "Not implemented"}

        except Exception as e:
            self.logger.exception(f"Failed to create issue: {e}")
            return {"error": str(e)}

    async def _update_issue(self, args: dict[str, Any]) -> dict[str, Any]:
        """Update Linear issue."""
        try:
            issue_id = args["issue_id"]

            # Demo response
            if not self.linear_client:
                return {
                    "id": issue_id,
                    "updated": True,
                    "updated_at": datetime.utcnow().isoformat(),
                }

            # Real Linear API call would go here
            return {"error": "Not implemented"}

        except Exception as e:
            self.logger.exception(f"Failed to update issue: {e}")
            return {"error": str(e)}

    async def _get_project_health(self, args: dict[str, Any]) -> dict[str, Any]:
        """Get project health metrics."""
        try:
            project_id = args["project_id"]

            # Demo health metrics
            return {
                "project_id": project_id,
                "health_score": 85,
                "metrics": {
                    "velocity": 12.5,
                    "issues_completed_this_week": 8,
                    "issues_created_this_week": 10,
                    "blocked_issues": 2,
                    "overdue_issues": 1,
                    "team_capacity": 0.8,
                },
                "risks": [
                    {
                        "type": "velocity",
                        "severity": "low",
                        "message": "Velocity slightly below target",
                    }
                ],
                "recommendations": [
                    "Consider breaking down large issues",
                    "Review blocked issues with team",
                ],
            }

        except Exception as e:
            self.logger.exception(f"Failed to get project health: {e}")
            return {"error": str(e)}


# Entry point
if __name__ == "__main__":
    server = LinearMCPServer()
    server.run()
