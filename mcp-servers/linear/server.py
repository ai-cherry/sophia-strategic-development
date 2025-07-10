#!/usr/bin/env python3
"""
Sophia AI Linear MCP Server
Provides project management and issue tracking
Using official Anthropic MCP SDK

Date: July 10, 2025
"""

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


class IssueState(str, Enum):
    """Linear issue states"""

    BACKLOG = "backlog"
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    IN_REVIEW = "in_review"
    DONE = "done"
    CANCELED = "canceled"


class LinearMCPServer(StandardizedMCPServer):
    """Linear MCP Server for project management"""

    def __init__(self):
        config = ServerConfig(
            name="linear",
            version="2.0.0",
            port=9002,
            capabilities=["PROJECT_MANAGEMENT", "ISSUE_TRACKING", "ANALYTICS"],
            tier="SECONDARY",
        )
        super().__init__(config)

        # Linear configuration
        self.api_key = get_config_value("linear_api_key")
        self.api_url = "https://api.linear.app/graphql"
        self.headers = {
            "Authorization": self.api_key,
            "Content-Type": "application/json",
        }

    def get_tool_definitions(self) -> list[ToolDefinition]:
        """Define Linear tools"""
        return [
            ToolDefinition(
                name="list_issues",
                description="List Linear issues with optional filters",
                parameters=[
                    ToolParameter(
                        name="state",
                        type="string",
                        description="Filter by state (backlog, todo, in_progress, in_review, done, canceled)",
                        required=False,
                    ),
                    ToolParameter(
                        name="assignee",
                        type="string",
                        description="Filter by assignee email",
                        required=False,
                    ),
                    ToolParameter(
                        name="limit",
                        type="number",
                        description="Maximum number of issues to return",
                        required=False,
                    ),
                ],
            ),
            ToolDefinition(
                name="create_issue",
                description="Create a new Linear issue",
                parameters=[
                    ToolParameter(
                        name="title",
                        type="string",
                        description="Issue title",
                        required=True,
                    ),
                    ToolParameter(
                        name="description",
                        type="string",
                        description="Issue description",
                        required=False,
                    ),
                    ToolParameter(
                        name="team_key",
                        type="string",
                        description="Team key (e.g., 'ENG')",
                        required=True,
                    ),
                    ToolParameter(
                        name="priority",
                        type="number",
                        description="Priority (0-4, where 0 is urgent)",
                        required=False,
                    ),
                ],
            ),
            ToolDefinition(
                name="update_issue",
                description="Update an existing Linear issue",
                parameters=[
                    ToolParameter(
                        name="issue_id",
                        type="string",
                        description="Issue ID",
                        required=True,
                    ),
                    ToolParameter(
                        name="state",
                        type="string",
                        description="New state",
                        required=False,
                    ),
                    ToolParameter(
                        name="title",
                        type="string",
                        description="New title",
                        required=False,
                    ),
                    ToolParameter(
                        name="description",
                        type="string",
                        description="New description",
                        required=False,
                    ),
                ],
            ),
            ToolDefinition(
                name="get_issue",
                description="Get details of a specific Linear issue",
                parameters=[
                    ToolParameter(
                        name="issue_id",
                        type="string",
                        description="Issue ID or identifier (e.g., 'ENG-123')",
                        required=True,
                    ),
                ],
            ),
            ToolDefinition(
                name="get_team_analytics",
                description="Get team analytics and velocity",
                parameters=[
                    ToolParameter(
                        name="team_key",
                        type="string",
                        description="Team key (e.g., 'ENG')",
                        required=True,
                    ),
                    ToolParameter(
                        name="days",
                        type="number",
                        description="Number of days to analyze",
                        required=False,
                    ),
                ],
            ),
            ToolDefinition(
                name="search_issues",
                description="Search issues by query",
                parameters=[
                    ToolParameter(
                        name="query",
                        type="string",
                        description="Search query",
                        required=True,
                    ),
                ],
            ),
            ToolDefinition(
                name="add_comment",
                description="Add a comment to an issue",
                parameters=[
                    ToolParameter(
                        name="issue_id",
                        type="string",
                        description="Issue ID",
                        required=True,
                    ),
                    ToolParameter(
                        name="body",
                        type="string",
                        description="Comment text",
                        required=True,
                    ),
                ],
            ),
        ]

    async def handle_tool_call(
        self, tool_name: str, arguments: dict[str, Any]
    ) -> dict[str, Any]:
        """Handle Linear tool calls"""

        if tool_name == "list_issues":
            return await self._list_issues(**arguments)
        elif tool_name == "create_issue":
            return await self._create_issue(**arguments)
        elif tool_name == "update_issue":
            return await self._update_issue(**arguments)
        elif tool_name == "get_issue":
            return await self._get_issue(**arguments)
        elif tool_name == "get_team_analytics":
            return await self._get_team_analytics(**arguments)
        elif tool_name == "search_issues":
            return await self._search_issues(**arguments)
        elif tool_name == "add_comment":
            return await self._add_comment(**arguments)
        else:
            raise ValueError(f"Unknown tool: {tool_name}")

    async def _make_graphql_request(
        self, query: str, variables: Optional[dict[str, Any]] = None
    ) -> dict[str, Any]:
        """Make a GraphQL request to Linear API"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.api_url,
                headers=self.headers,
                json={"query": query, "variables": variables or {}},
            )
            response.raise_for_status()
            return response.json()

    async def _list_issues(
        self,
        state: Optional[str] = None,
        assignee: Optional[str] = None,
        limit: int = 50,
    ) -> dict[str, Any]:
        """List Linear issues"""

        # Build filter
        filters = []
        if state:
            filters.append(f'state: {{name: {{eq: "{state}"}}}}')
        if assignee:
            filters.append(f'assignee: {{email: {{eq: "{assignee}"}}}}')

        filter_str = f"filter: {{{', '.join(filters)}}}" if filters else ""

        query = f"""
        query ListIssues {{
            issues({filter_str}, first: {limit}) {{
                nodes {{
                    id
                    identifier
                    title
                    description
                    state {{
                        name
                        color
                    }}
                    priority
                    assignee {{
                        name
                        email
                    }}
                    createdAt
                    updatedAt
                    completedAt
                }}
            }}
        }}
        """

        result = await self._make_graphql_request(query)
        issues = result.get("data", {}).get("issues", {}).get("nodes", [])

        return {
            "issues": issues,
            "count": len(issues),
            "filters": {
                "state": state,
                "assignee": assignee,
                "limit": limit,
            },
        }

    async def _create_issue(
        self,
        title: str,
        team_key: str,
        description: Optional[str] = None,
        priority: Optional[int] = None,
    ) -> dict[str, Any]:
        """Create a new Linear issue"""

        # First, get the team ID
        team_query = """
        query GetTeam($key: String!) {
            teams(filter: {key: {eq: $key}}) {
                nodes {
                    id
                    name
                }
            }
        }
        """

        team_result = await self._make_graphql_request(team_query, {"key": team_key})
        teams = team_result.get("data", {}).get("teams", {}).get("nodes", [])

        if not teams:
            raise ValueError(f"Team with key '{team_key}' not found")

        team_id = teams[0]["id"]

        # Create the issue
        mutation = """
        mutation CreateIssue($input: IssueCreateInput!) {
            issueCreate(input: $input) {
                success
                issue {
                    id
                    identifier
                    title
                    description
                    url
                }
            }
        }
        """

        variables = {
            "input": {
                "title": title,
                "teamId": team_id,
            }
        }

        if description:
            variables["input"]["description"] = description
        if priority is not None:
            variables["input"]["priority"] = priority

        result = await self._make_graphql_request(mutation, variables)

        create_result = result.get("data", {}).get("issueCreate", {})
        if not create_result.get("success"):
            raise Exception("Failed to create issue")

        return {
            "issue": create_result.get("issue"),
            "success": True,
        }

    async def _update_issue(
        self,
        issue_id: str,
        state: Optional[str] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
    ) -> dict[str, Any]:
        """Update an existing Linear issue"""

        mutation = """
        mutation UpdateIssue($id: String!, $input: IssueUpdateInput!) {
            issueUpdate(id: $id, input: $input) {
                success
                issue {
                    id
                    identifier
                    title
                    description
                    state {
                        name
                    }
                }
            }
        }
        """

        input_data = {}

        if state:
            # Get state ID
            state_query = """
            query GetState($name: String!) {
                workflowStates(filter: {name: {eq: $name}}) {
                    nodes {
                        id
                        name
                    }
                }
            }
            """
            state_result = await self._make_graphql_request(
                state_query, {"name": state}
            )
            states = (
                state_result.get("data", {}).get("workflowStates", {}).get("nodes", [])
            )
            if states:
                input_data["stateId"] = states[0]["id"]

        if title:
            input_data["title"] = title
        if description:
            input_data["description"] = description

        result = await self._make_graphql_request(
            mutation, {"id": issue_id, "input": input_data}
        )

        update_result = result.get("data", {}).get("issueUpdate", {})
        if not update_result.get("success"):
            raise Exception("Failed to update issue")

        return {
            "issue": update_result.get("issue"),
            "success": True,
        }

    async def _get_issue(self, issue_id: str) -> dict[str, Any]:
        """Get details of a specific Linear issue"""

        query = """
        query GetIssue($id: String!) {
            issue(id: $id) {
                id
                identifier
                title
                description
                state {
                    name
                    color
                }
                priority
                assignee {
                    name
                    email
                }
                team {
                    name
                    key
                }
                parent {
                    identifier
                    title
                }
                children {
                    nodes {
                        identifier
                        title
                    }
                }
                comments {
                    nodes {
                        body
                        user {
                            name
                        }
                        createdAt
                    }
                }
                createdAt
                updatedAt
                completedAt
                url
            }
        }
        """

        result = await self._make_graphql_request(query, {"id": issue_id})
        issue = result.get("data", {}).get("issue")

        if not issue:
            raise ValueError(f"Issue '{issue_id}' not found")

        return {"issue": issue}

    async def _get_team_analytics(
        self, team_key: str, days: int = 30
    ) -> dict[str, Any]:
        """Get team analytics and velocity"""

        # Calculate date range
        end_date = datetime.now(UTC)
        start_date = end_date - timedelta(days=days)

        query = """
        query GetTeamAnalytics($teamKey: String!, $startDate: DateTime!, $endDate: DateTime!) {
            team(key: $teamKey) {
                name
                issues(
                    filter: {
                        completedAt: {gte: $startDate, lte: $endDate}
                    }
                ) {
                    nodes {
                        id
                        estimate
                        completedAt
                    }
                }
                members {
                    nodes {
                        name
                        email
                    }
                }
            }
        }
        """

        result = await self._make_graphql_request(
            query,
            {
                "teamKey": team_key,
                "startDate": start_date.isoformat(),
                "endDate": end_date.isoformat(),
            },
        )

        team = result.get("data", {}).get("team")
        if not team:
            raise ValueError(f"Team '{team_key}' not found")

        # Calculate velocity
        completed_issues = team.get("issues", {}).get("nodes", [])
        total_points = sum(issue.get("estimate", 0) for issue in completed_issues)

        return {
            "team": team.get("name"),
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
                "days": days,
            },
            "velocity": {
                "total_points": total_points,
                "issues_completed": len(completed_issues),
                "average_points_per_day": total_points / days if days > 0 else 0,
            },
            "members": team.get("members", {}).get("nodes", []),
        }

    async def _search_issues(self, query: str) -> dict[str, Any]:
        """Search issues by query"""

        graphql_query = """
        query SearchIssues($query: String!) {
            issueSearch(query: $query, first: 50) {
                nodes {
                    ... on Issue {
                        id
                        identifier
                        title
                        description
                        state {
                            name
                        }
                        assignee {
                            name
                            email
                        }
                        team {
                            name
                            key
                        }
                    }
                }
            }
        }
        """

        result = await self._make_graphql_request(graphql_query, {"query": query})

        issues = result.get("data", {}).get("issueSearch", {}).get("nodes", [])

        return {
            "query": query,
            "results": issues,
            "count": len(issues),
        }

    async def _add_comment(self, issue_id: str, body: str) -> dict[str, Any]:
        """Add a comment to an issue"""

        mutation = """
        mutation AddComment($issueId: String!, $body: String!) {
            commentCreate(input: {issueId: $issueId, body: $body}) {
                success
                comment {
                    id
                    body
                    user {
                        name
                    }
                    createdAt
                }
            }
        }
        """

        result = await self._make_graphql_request(
            mutation, {"issueId": issue_id, "body": body}
        )

        create_result = result.get("data", {}).get("commentCreate", {})
        if not create_result.get("success"):
            raise Exception("Failed to add comment")

        return {
            "comment": create_result.get("comment"),
            "success": True,
        }


# Create and run server
if __name__ == "__main__":
    server = LinearMCPServer()
    server.run()
