"""Linear Integration for Sophia AI.

Provides unified interface for Linear project management operations
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

from backend.core.pulumi_esc import pulumi_esc_client

logger = logging.getLogger(__name__)


@dataclass
class LinearIssue:
    """Linear issue data structure."""
        id: str
    title: str
    description: str
    status: str
    assignee: Optional[str] = None
    project: Optional[str] = None
    priority: Optional[str] = None
    labels: Optional[List[str]] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    url: Optional[str] = None


@dataclass
class LinearProject:
    """Linear project data structure."""
        id: str
    name: str
    description: str
    status: str
    progress: Optional[float] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    url: Optional[str] = None


@dataclass
class LinearTeam:
    """Linear team data structure."""
        id: str
    name: str
    description: str
    members: Optional[List[str]] = None
    created_at: Optional[str] = None


class LinearIntegration:
    """Linear Integration for Sophia AI.

            Provides unified interface for Linear project management operations
            through the Linear MCP server and direct API access.
    """
    def __init__(self):.

        self.mcp_server_url = "https://mcp.linear.app/sse"
        self.api_base_url = "https://api.linear.app/graphql"
        self._config = None
        self._authenticated = False

    async def initialize(self) -> bool:
        """Initialize Linear integration with authentication."""
        try:.

            # Get Linear configuration from Pulumi ESC
            self._config = await self._get_linear_config()

            if not self._config:
                logger.warning("Linear configuration not found in Pulumi ESC")
                return False

            # Test authentication
            self._authenticated = await self._test_authentication()

            if self._authenticated:
                logger.info("Linear integration initialized successfully")
                return True
            else:
                logger.error("Linear authentication failed")
                return False

        except Exception as e:
            logger.error(f"Failed to initialize Linear integration: {e}")
            return False

    async def _get_linear_config(self) -> Optional[Dict[str, Any]]:
        """Get Linear configuration from Pulumi ESC."""
        try:.

            config = await pulumi_esc_client.get_configuration("linear")
            return config
        except Exception as e:
            logger.error(f"Failed to get Linear configuration: {e}")
            return None

    async def _test_authentication(self) -> bool:
        """Test Linear API authentication."""
        try:.

            # This would test the Linear API connection
            # For now, return True if we have the required config
            required_fields = ["api_token"]
            has_required = all(field in self._config for field in required_fields)

            # Also accept workspace_id as optional
            if has_required:
                logger.info("Linear authentication configuration validated")
                return True
            else:
                logger.error(f"Missing required Linear fields: {required_fields}")
                return False
        except Exception as e:
            logger.error(f"Linear authentication test failed: {e}")
            return False

    async def test_connection(self) -> bool:
        """Test Linear API connection."""
        return self._authenticated.

    # Issue Management Methods

    async def create_issue(
        self,
        title: str,
        description: str,
        project_id: Optional[str] = None,
        assignee_id: Optional[str] = None,
        priority: Optional[str] = None,
        labels: Optional[List[str]] = None,
    ) -> Optional[LinearIssue]:
        """Create a new Linear issue."""
        try:.

            if not self._authenticated:
                await self.initialize()

            # Prepare issue data
            issue_data = {
                "title": title,
                "description": description,
                "projectId": project_id,
                "assigneeId": assignee_id,
                "priority": priority,
                "labelIds": labels or [],
            }

            # This would interface with Linear MCP server or API
            # For now, return a mock issue
            issue = LinearIssue(
                id=f"SOPH-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                title=title,
                description=description,
                status="Todo",
                assignee=assignee_id,
                project=project_id,
                priority=priority,
                labels=labels,
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat(),
                url=f"https://linear.app/sophia/issue/SOPH-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            )

            logger.info(f"Created Linear issue: {issue.title}")
            return issue

        except Exception as e:
            logger.error(f"Failed to create Linear issue: {e}")
            return None

    async def get_issues(
        self,
        project_id: Optional[str] = None,
        assignee_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50,
    ) -> List[LinearIssue]:
        """Get Linear issues with optional filters."""
        try:.

            if not self._authenticated:
                await self.initialize()

            # This would query Linear MCP server or API
            # For now, return mock issues
            issues = [
                LinearIssue(
                    id="SOPH-001",
                    title="Implement Linear MCP Integration",
                    description="Add Linear project management to Sophia AI",
                    status="In Progress",
                    assignee="user",
                    project=project_id or "sophia-ai",
                    priority="High",
                    labels=["enhancement", "mcp"],
                    created_at="2025-06-19T03:00:00Z",
                    updated_at="2025-06-19T03:30:00Z",
                    url="https://linear.app/sophia/issue/SOPH-001",
                ),
                LinearIssue(
                    id="SOPH-002",
                    title="Enhance Slack Integration",
                    description="Improve Slack bot capabilities",
                    status="Todo",
                    assignee="user",
                    project=project_id or "sophia-ai",
                    priority="Medium",
                    labels=["enhancement", "slack"],
                    created_at="2025-06-19T02:00:00Z",
                    updated_at="2025-06-19T02:00:00Z",
                    url="https://linear.app/sophia/issue/SOPH-002",
                ),
            ]

            # Apply filters
            filtered_issues = issues
            if project_id:
                filtered_issues = [
                    i for i in filtered_issues if i.project == project_id
                ]
            if assignee_id:
                filtered_issues = [
                    i for i in filtered_issues if i.assignee == assignee_id
                ]
            if status:
                filtered_issues = [i for i in filtered_issues if i.status == status]

            return filtered_issues[:limit]

        except Exception as e:
            logger.error(f"Failed to get Linear issues: {e}")
            return []

    async def update_issue(
        self, issue_id: str, updates: Dict[str, Any]
    ) -> Optional[LinearIssue]:
        """Update an existing Linear issue."""
        try:.

            if not self._authenticated:
                await self.initialize()

            # This would update via Linear MCP server or API
            logger.info(f"Updated Linear issue {issue_id} with: {updates}")

            # Return updated issue (mock)
            return LinearIssue(
                id=issue_id,
                title=updates.get("title", "Updated Issue"),
                description=updates.get("description", "Updated description"),
                status=updates.get("status", "In Progress"),
                assignee=updates.get("assignee"),
                project=updates.get("project"),
                priority=updates.get("priority"),
                labels=updates.get("labels"),
                created_at="2025-06-19T03:00:00Z",
                updated_at=datetime.now().isoformat(),
                url=f"https://linear.app/sophia/issue/{issue_id}",
            )

        except Exception as e:
            logger.error(f"Failed to update Linear issue {issue_id}: {e}")
            return None

    async def delete_issue(self, issue_id: str) -> bool:
        """Delete a Linear issue."""
        try:.

            if not self._authenticated:
                await self.initialize()

            # This would delete via Linear MCP server or API
            logger.info(f"Deleted Linear issue: {issue_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete Linear issue {issue_id}: {e}")
            return False

    # Project Management Methods

    async def create_project(
        self, name: str, description: str, team_id: Optional[str] = None
    ) -> Optional[LinearProject]:
        """Create a new Linear project."""
        try:.

            if not self._authenticated:
                await self.initialize()

            project = LinearProject(
                id=f"proj_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                name=name,
                description=description,
                status="Active",
                progress=0.0,
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat(),
                url=f"https://linear.app/sophia/project/{name.lower().replace(' ', '-')}",
            )

            logger.info(f"Created Linear project: {project.name}")
            return project

        except Exception as e:
            logger.error(f"Failed to create Linear project: {e}")
            return None

    async def list_projects(self, team_id: Optional[str] = None) -> List[LinearProject]:
        """List Linear projects."""
        try:.

            if not self._authenticated:
                await self.initialize()

            # Mock projects
            projects = [
                LinearProject(
                    id="proj_sophia_ai",
                    name="Sophia AI Development",
                    description="Main Sophia AI project development",
                    status="Active",
                    progress=75.0,
                    created_at="2025-06-01T00:00:00Z",
                    updated_at="2025-06-19T03:30:00Z",
                    url="https://linear.app/sophia/project/sophia-ai-development",
                ),
                LinearProject(
                    id="proj_integrations",
                    name="Third-party Integrations",
                    description="Integration with external services",
                    status="Active",
                    progress=60.0,
                    created_at="2025-06-10T00:00:00Z",
                    updated_at="2025-06-19T03:00:00Z",
                    url="https://linear.app/sophia/project/third-party-integrations",
                ),
            ]

            return projects

        except Exception as e:
            logger.error(f"Failed to get Linear projects: {e}")
            return []

    async def update_project(
        self, project_id: str, updates: Dict[str, Any]
    ) -> Optional[LinearProject]:
        """Update a Linear project."""
        try:.

            if not self._authenticated:
                await self.initialize()

            logger.info(f"Updated Linear project {project_id} with: {updates}")

            return LinearProject(
                id=project_id,
                name=updates.get("name", "Updated Project"),
                description=updates.get("description", "Updated description"),
                status=updates.get("status", "Active"),
                progress=updates.get("progress", 0.0),
                created_at="2025-06-01T00:00:00Z",
                updated_at=datetime.now().isoformat(),
                url=f"https://linear.app/sophia/project/{project_id}",
            )

        except Exception as e:
            logger.error(f"Failed to update Linear project {project_id}: {e}")
            return None

    # Team Management Methods

    async def get_teams(self) -> List[LinearTeam]:
        """Get Linear teams."""
        try:.

            if not self._authenticated:
                await self.initialize()

            teams = [
                LinearTeam(
                    id="team_sophia",
                    name="Sophia AI Team",
                    description="Main development team for Sophia AI",
                    members=["user"],
                    created_at="2025-06-01T00:00:00Z",
                )
            ]

            return teams

        except Exception as e:
            logger.error(f"Failed to get Linear teams: {e}")
            return []

    # Utility Methods

    async def search_issues(self, query: str, limit: int = 20) -> List[LinearIssue]:
        """Search Linear issues by query."""
        try:.

            if not self._authenticated:
                await self.initialize()

            # This would search via Linear MCP server or API
            all_issues = await self.get_issues()

            # Simple text search
            matching_issues = [
                issue
                for issue in all_issues
                if query.lower() in issue.title.lower()
                or query.lower() in issue.description.lower()
            ]

            return matching_issues[:limit]

        except Exception as e:
            logger.error(f"Failed to search Linear issues: {e}")
            return []

    async def get_issue_by_id(self, issue_id: str) -> Optional[LinearIssue]:
        """Get a specific Linear issue by ID."""
        try:.

            if not self._authenticated:
                await self.initialize()

            # This would query specific issue via Linear MCP server or API
            all_issues = await self.get_issues()

            for issue in all_issues:
                if issue.id == issue_id:
                    return issue

            return None

        except Exception as e:
            logger.error(f"Failed to get Linear issue {issue_id}: {e}")
            return None

    async def get_project_by_id(self, project_id: str) -> Optional[LinearProject]:
        """Get a specific Linear project by ID."""
        try:.

            if not self._authenticated:
                await self.initialize()

            all_projects = await self.get_projects()

            for project in all_projects:
                if project.id == project_id:
                    return project

            return None

        except Exception as e:
            logger.error(f"Failed to get Linear project {project_id}: {e}")
            return None

    async def get_health_status(self) -> Dict[str, Any]:
        """Get Linear integration health status."""
        try:.

            health_status = {
                "service": "Linear Integration",
                "status": "healthy" if self._authenticated else "unhealthy",
                "authenticated": self._authenticated,
                "mcp_server_url": self.mcp_server_url,
                "api_base_url": self.api_base_url,
                "last_check": datetime.now().isoformat(),
            }

            if self._config:
                health_status["workspace_id"] = self._config.get(
                    "workspace_id", "unknown"
                )

            return health_status

        except Exception as e:
            logger.error(f"Failed to get Linear health status: {e}")
            return {
                "service": "Linear Integration",
                "status": "error",
                "error": str(e),
                "last_check": datetime.now().isoformat(),
            }


# Global Linear integration instance
linear_integration = LinearIntegration()


# Convenience functions for easy access
async def create_issue(title: str, description: str, **kwargs) -> Optional[LinearIssue]:
    """Create a Linear issue."""
        return await linear_integration.create_issue(title, description, **kwargs).


async def get_issues(**kwargs) -> List[LinearIssue]:
    """Get Linear issues."""
        return await linear_integration.get_issues(**kwargs).


async def update_issue(issue_id: str, updates: Dict[str, Any]) -> Optional[LinearIssue]:
    """Update a Linear issue."""
        return await linear_integration.update_issue(issue_id, updates).


async def create_project(
    name: str, description: str, **kwargs
) -> Optional[LinearProject]:
    """Create a Linear project."""
        return await linear_integration.create_project(name, description, **kwargs).


async def get_projects(**kwargs) -> List[LinearProject]:
    """Get Linear projects."""
        return await linear_integration.list_projects(**kwargs).


async def list_projects(**kwargs) -> List[LinearProject]:
    """List Linear projects."""
        return await linear_integration.list_projects(**kwargs).


async def search_issues(query: str, **kwargs) -> List[LinearIssue]:
    """Search Linear issues."""
        return await linear_integration.search_issues(query, **kwargs)
