#!/usr/bin/env python3
"""
Linear MCP Server for Sophia AI
Provides project management data, issue tracking, and team collaboration features.
"""

import asyncio
import json
import logging
import os
import sys
from typing import Any, Dict, Optional

import aiohttp
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolResult,
    ListToolsResult,
    TextContent,
    Tool,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("linear-mcp-server")


class LinearMCPServer:
    """Linear MCP Server for project management integration."""

    def __init__(self):
        self.server = Server("linear-mcp-server")
        self.base_url = "https://api.linear.app/graphql"
        self.access_token = os.getenv("LINEAR_API_KEY")
        self.team_id = os.getenv("LINEAR_TEAM_ID")

        if not self.access_token:
            logger.error("LINEAR_API_KEY environment variable not set")
            sys.exit(1)

        if not self.team_id:
            logger.warning(
                "LINEAR_TEAM_ID not set, will use first available team"
            )

        # Setup MCP server handlers
        self.setup_handlers()

    def setup_handlers(self):
        """Setup MCP server request handlers."""

        @self.server.list_tools()
        async def handle_list_tools() -> ListToolsResult:
            """List available Linear tools."""
            return ListToolsResult(
                tools=[
                    Tool(
                        name="get_projects",
                        description="Get projects from Linear workspace with filtering options",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "team_id": {
                                    "type": "string",
                                    "description": "Filter projects by team ID",
                                },
                                "state": {
                                    "type": "string",
                                    "description": "Filter by project state (planned, started, completed, canceled)",
                                },
                                "limit": {
                                    "type": "integer",
                                    "description": "Maximum number of projects to return (default: 50)",
                                },
                            },
                        },
                    ),
                    Tool(
                        name="get_project_details",
                        description="Get detailed information about a specific project",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "project_id": {
                                    "type": "string",
                                    "description": "Project ID to get details for",
                                    "required": True,
                                }
                            },
                            "required": ["project_id"],
                        },
                    ),
                    Tool(
                        name="get_issues",
                        description="Get issues from Linear with filtering options",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "team_id": {
                                    "type": "string",
                                    "description": "Filter issues by team ID",
                                },
                                "project_id": {
                                    "type": "string",
                                    "description": "Filter issues by project ID",
                                },
                                "assignee_id": {
                                    "type": "string",
                                    "description": "Filter issues by assignee ID",
                                },
                                "state": {
                                    "type": "string",
                                    "description": "Filter by issue state (backlog, unstarted, started, completed, canceled)",
                                },
                                "priority": {
                                    "type": "integer",
                                    "description": "Filter by priority (0=No priority, 1=Urgent, 2=High, 3=Normal, 4=Low)",
                                },
                                "limit": {
                                    "type": "integer",
                                    "description": "Maximum number of issues to return (default: 100)",
                                },
                            },
                        },
                    ),
                    Tool(
                        name="get_issue_details",
                        description="Get detailed information about a specific issue",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "issue_id": {
                                    "type": "string",
                                    "description": "Issue ID to get details for",
                                    "required": True,
                                }
                            },
                            "required": ["issue_id"],
                        },
                    ),
                    Tool(
                        name="get_teams",
                        description="Get teams in the workspace",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "include_archived": {
                                    "type": "boolean",
                                    "description": "Include archived teams (default: false)",
                                }
                            },
                        },
                    ),
                    Tool(
                        name="get_team_members",
                        description="Get members of a specific team",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "team_id": {
                                    "type": "string",
                                    "description": "Team ID to get members for",
                                    "required": True,
                                }
                            },
                            "required": ["team_id"],
                        },
                    ),
                    Tool(
                        name="get_milestones",
                        description="Get milestones for a project or team",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "project_id": {
                                    "type": "string",
                                    "description": "Project ID to get milestones for",
                                },
                                "team_id": {
                                    "type": "string",
                                    "description": "Team ID to get milestones for",
                                },
                                "limit": {
                                    "type": "integer",
                                    "description": "Maximum number of milestones to return (default: 20)",
                                },
                            },
                        },
                    ),
                    Tool(
                        name="search_issues",
                        description="Search for issues across the workspace",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "query": {
                                    "type": "string",
                                    "description": "Search query for issue titles and descriptions",
                                },
                                "team_id": {
                                    "type": "string",
                                    "description": "Limit search to specific team",
                                },
                                "assignee_id": {
                                    "type": "string",
                                    "description": "Filter by assignee ID",
                                },
                                "state": {
                                    "type": "string",
                                    "description": "Filter by issue state",
                                },
                                "limit": {
                                    "type": "integer",
                                    "description": "Maximum number of issues to return (default: 50)",
                                },
                            },
                        },
                    ),
                    Tool(
                        name="get_user_issues",
                        description="Get issues assigned to a specific user",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "user_id": {
                                    "type": "string",
                                    "description": "User ID to get issues for",
                                    "required": True,
                                },
                                "state": {
                                    "type": "string",
                                    "description": "Filter by issue state",
                                },
                                "team_id": {
                                    "type": "string",
                                    "description": "Filter by team ID",
                                },
                            },
                            "required": ["user_id"],
                        },
                    ),
                    Tool(
                        name="get_workspace_users",
                        description="Get users in the workspace",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "include_guests": {
                                    "type": "boolean",
                                    "description": "Include guest users (default: false)",
                                }
                            },
                        },
                    ),
                ]
            )

        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict) -> CallToolResult:
            """Handle tool calls."""
            try:
                if name == "get_projects":
                    result = await self.get_projects(**arguments)
                elif name == "get_project_details":
                    result = await self.get_project_details(**arguments)
                elif name == "get_issues":
                    result = await self.get_issues(**arguments)
                elif name == "get_issue_details":
                    result = await self.get_issue_details(**arguments)
                elif name == "get_teams":
                    result = await self.get_teams(**arguments)
                elif name == "get_team_members":
                    result = await self.get_team_members(**arguments)
                elif name == "get_milestones":
                    result = await self.get_milestones(**arguments)
                elif name == "search_issues":
                    result = await self.search_issues(**arguments)
                elif name == "get_user_issues":
                    result = await self.get_user_issues(**arguments)
                elif name == "get_workspace_users":
                    result = await self.get_workspace_users(**arguments)
                else:
                    raise ValueError(f"Unknown tool: {name}")

                return CallToolResult(
                    content=[
                        TextContent(type="text", text=json.dumps(result, indent=2))
                    ]
                )
            except Exception as e:
                logger.error(f"Error calling tool {name}: {str(e)}")
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Error: {str(e)}")]
                )

    async def make_request(self, query: str, variables: Optional[Dict] = None) -> Dict[str, Any]:
        """Make authenticated GraphQL request to Linear API."""
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

        payload = {
            "query": query,
            "variables": variables or {}
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(self.base_url, headers=headers, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    if "errors" in data:
                        raise Exception(f"Linear API errors: {data['errors']}")
                    return data.get("data", {})
                else:
                    error_text = await response.text()
                    raise Exception(f"Linear API error {response.status}: {error_text}")

    async def get_team_id(self) -> str:
        """Get team ID, using default or first available."""
        if self.team_id:
            return self.team_id

        query = """
        query {
            teams {
                nodes {
                    id
                    name
                }
            }
        }
        """
        
        result = await self.make_request(query)
        teams = result.get("teams", {}).get("nodes", [])
        
        if not teams:
            raise Exception("No teams found")

        return teams[0]["id"]

    async def get_projects(
        self,
        team_id: Optional[str] = None,
        state: Optional[str] = None,
        limit: int = 50,
    ) -> Dict[str, Any]:
        """Get projects from workspace."""
        if not team_id:
            team_id = await self.get_team_id()

        # Build filter conditions
        filter_conditions = []
        if team_id:
            filter_conditions.append(f'team: {{ id: {{ eq: "{team_id}" }} }}')
        if state:
            filter_conditions.append(f'state: {{ name: {{ eq: "{state}" }} }}')

        filter_clause = ""
        if filter_conditions:
            filter_clause = f"filter: {{ {', '.join(filter_conditions)} }}"

        query = f"""
        query {{
            projects({filter_clause}, first: {min(limit, 100)}) {{
                nodes {{
                    id
                    name
                    description
                    state {{
                        name
                        type
                    }}
                    progress
                    startDate
                    targetDate
                    completedAt
                    createdAt
                    updatedAt
                    lead {{
                        id
                        name
                        email
                    }}
                    team {{
                        id
                        name
                    }}
                    members {{
                        nodes {{
                            id
                            name
                            email
                        }}
                    }}
                    issues {{
                        nodes {{
                            id
                            state {{
                                name
                                type
                            }}
                        }}
                    }}
                }}
                pageInfo {{
                    hasNextPage
                    endCursor
                }}
            }}
        }}
        """

        result = await self.make_request(query)
        projects_data = result.get("projects", {})
        projects = projects_data.get("nodes", [])

        # Enhance project data with metrics
        enhanced_projects = []
        for project in projects:
            issues = project.get("issues", {}).get("nodes", [])
            total_issues = len(issues)
            completed_issues = len([i for i in issues if i.get("state", {}).get("type") == "completed"])
            
            project["metrics"] = {
                "total_issues": total_issues,
                "completed_issues": completed_issues,
                "completion_rate": (completed_issues / total_issues * 100) if total_issues > 0 else 0,
                "progress_percentage": project.get("progress", 0) * 100
            }
            
            enhanced_projects.append(project)

        return {
            "projects": enhanced_projects,
            "total_count": len(enhanced_projects),
            "has_next_page": projects_data.get("pageInfo", {}).get("hasNextPage", False)
        }

    async def get_project_details(self, project_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific project."""
        query = f"""
        query {{
            project(id: "{project_id}") {{
                id
                name
                description
                state {{
                    name
                    type
                }}
                progress
                startDate
                targetDate
                completedAt
                createdAt
                updatedAt
                lead {{
                    id
                    name
                    email
                }}
                team {{
                    id
                    name
                }}
                members {{
                    nodes {{
                        id
                        name
                        email
                    }}
                }}
                issues {{
                    nodes {{
                        id
                        title
                        state {{
                            name
                            type
                        }}
                        priority
                        assignee {{
                            id
                            name
                        }}
                        createdAt
                        updatedAt
                    }}
                }}
                projectMilestones {{
                    nodes {{
                        id
                        name
                        targetDate
                    }}
                }}
            }}
        }}
        """

        result = await self.make_request(query)
        return result.get("project", {})

    async def get_issues(
        self,
        team_id: Optional[str] = None,
        project_id: Optional[str] = None,
        assignee_id: Optional[str] = None,
        state: Optional[str] = None,
        priority: Optional[int] = None,
        limit: int = 100,
    ) -> Dict[str, Any]:
        """Get issues with filtering options."""
        # Build filter conditions
        filter_conditions = []
        if team_id:
            filter_conditions.append(f'team: {{ id: {{ eq: "{team_id}" }} }}')
        if project_id:
            filter_conditions.append(f'project: {{ id: {{ eq: "{project_id}" }} }}')
        if assignee_id:
            filter_conditions.append(f'assignee: {{ id: {{ eq: "{assignee_id}" }} }}')
        if state:
            filter_conditions.append(f'state: {{ name: {{ eq: "{state}" }} }}')
        if priority is not None:
            filter_conditions.append(f'priority: {{ eq: {priority} }}')

        filter_clause = ""
        if filter_conditions:
            filter_clause = f"filter: {{ {', '.join(filter_conditions)} }}"

        query = f"""
        query {{
            issues({filter_clause}, first: {min(limit, 100)}) {{
                nodes {{
                    id
                    title
                    description
                    state {{
                        name
                        type
                    }}
                    priority
                    estimate
                    assignee {{
                        id
                        name
                        email
                    }}
                    creator {{
                        id
                        name
                    }}
                    team {{
                        id
                        name
                    }}
                    project {{
                        id
                        name
                    }}
                    createdAt
                    updatedAt
                    dueDate
                    completedAt
                    labels {{
                        nodes {{
                            id
                            name
                            color
                        }}
                    }}
                }}
                pageInfo {{
                    hasNextPage
                    endCursor
                }}
            }}
        }}
        """

        result = await self.make_request(query)
        issues_data = result.get("issues", {})

        return {
            "issues": issues_data.get("nodes", []),
            "total_count": len(issues_data.get("nodes", [])),
            "has_next_page": issues_data.get("pageInfo", {}).get("hasNextPage", False)
        }

    async def get_issue_details(self, issue_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific issue."""
        query = f"""
        query {{
            issue(id: "{issue_id}") {{
                id
                title
                description
                state {{
                    name
                    type
                }}
                priority
                estimate
                assignee {{
                    id
                    name
                    email
                }}
                creator {{
                    id
                    name
                }}
                team {{
                    id
                    name
                }}
                project {{
                    id
                    name
                }}
                createdAt
                updatedAt
                dueDate
                completedAt
                labels {{
                    nodes {{
                        id
                        name
                        color
                    }}
                }}
                comments {{
                    nodes {{
                        id
                        body
                        user {{
                            name
                        }}
                        createdAt
                    }}
                }}
                attachments {{
                    nodes {{
                        id
                        title
                        url
                    }}
                }}
            }}
        }}
        """

        result = await self.make_request(query)
        return result.get("issue", {})

    async def get_teams(self, include_archived: bool = False) -> Dict[str, Any]:
        """Get teams in the workspace."""
        filter_clause = ""
        if not include_archived:
            filter_clause = 'filter: { isArchived: { eq: false } }'

        query = f"""
        query {{
            teams({filter_clause}) {{
                nodes {{
                    id
                    name
                    description
                    key
                    isArchived
                    createdAt
                    updatedAt
                    members {{
                        nodes {{
                            id
                            name
                            email
                        }}
                    }}
                    projects {{
                        nodes {{
                            id
                            name
                            state {{
                                name
                            }}
                        }}
                    }}
                    issues {{
                        nodes {{
                            id
                            state {{
                                type
                            }}
                        }}
                    }}
                }}
            }}
        }}
        """

        result = await self.make_request(query)
        teams_data = result.get("teams", {})
        teams = teams_data.get("nodes", [])

        # Enhance team data with metrics
        enhanced_teams = []
        for team in teams:
            issues = team.get("issues", {}).get("nodes", [])
            projects = team.get("projects", {}).get("nodes", [])
            
            team["metrics"] = {
                "member_count": len(team.get("members", {}).get("nodes", [])),
                "project_count": len(projects),
                "total_issues": len(issues),
                "active_projects": len([p for p in projects if p.get("state", {}).get("name") not in ["completed", "canceled"]])
            }
            
            enhanced_teams.append(team)

        return {
            "teams": enhanced_teams,
            "total_count": len(enhanced_teams)
        }

    async def get_team_members(self, team_id: str) -> Dict[str, Any]:
        """Get members of a specific team."""
        query = f"""
        query {{
            team(id: "{team_id}") {{
                id
                name
                members {{
                    nodes {{
                        id
                        name
                        email
                        isActive
                        createdAt
                        assignedIssues {{
                            nodes {{
                                id
                                state {{
                                    type
                                }}
                            }}
                        }}
                    }}
                }}
            }}
        }}
        """

        result = await self.make_request(query)
        team_data = result.get("team", {})
        members = team_data.get("members", {}).get("nodes", [])

        # Enhance member data with metrics
        enhanced_members = []
        for member in members:
            assigned_issues = member.get("assignedIssues", {}).get("nodes", [])
            active_issues = len([i for i in assigned_issues if i.get("state", {}).get("type") != "completed"])
            
            member["metrics"] = {
                "total_assigned_issues": len(assigned_issues),
                "active_issues": active_issues
            }
            
            enhanced_members.append(member)

        return {
            "team": team_data,
            "members": enhanced_members,
            "member_count": len(enhanced_members)
        }

    async def get_milestones(
        self,
        project_id: Optional[str] = None,
        team_id: Optional[str] = None,
        limit: int = 20,
    ) -> Dict[str, Any]:
        """Get milestones for a project or team."""
        filter_conditions = []
        if project_id:
            filter_conditions.append(f'project: {{ id: {{ eq: "{project_id}" }} }}')
        if team_id:
            filter_conditions.append(f'team: {{ id: {{ eq: "{team_id}" }} }}')

        filter_clause = ""
        if filter_conditions:
            filter_clause = f"filter: {{ {', '.join(filter_conditions)} }}"

        query = f"""
        query {{
            projectMilestones({filter_clause}, first: {min(limit, 50)}) {{
                nodes {{
                    id
                    name
                    description
                    targetDate
                    createdAt
                    updatedAt
                    project {{
                        id
                        name
                    }}
                }}
            }}
        }}
        """

        result = await self.make_request(query)
        milestones_data = result.get("projectMilestones", {})

        return {
            "milestones": milestones_data.get("nodes", []),
            "total_count": len(milestones_data.get("nodes", []))
        }

    async def search_issues(
        self,
        query: Optional[str] = None,
        team_id: Optional[str] = None,
        assignee_id: Optional[str] = None,
        state: Optional[str] = None,
        limit: int = 50,
    ) -> Dict[str, Any]:
        """Search for issues across the workspace."""
        filter_conditions = []
        if team_id:
            filter_conditions.append(f'team: {{ id: {{ eq: "{team_id}" }} }}')
        if assignee_id:
            filter_conditions.append(f'assignee: {{ id: {{ eq: "{assignee_id}" }} }}')
        if state:
            filter_conditions.append(f'state: {{ name: {{ eq: "{state}" }} }}')

        filter_clause = ""
        if filter_conditions:
            filter_clause = f"filter: {{ {', '.join(filter_conditions)} }}"

        # If query is provided, use search endpoint
        if query:
            search_query = f"""
            query {{
                issueSearch(query: "{query}", {filter_clause}, first: {min(limit, 50)}) {{
                    nodes {{
                        id
                        title
                        description
                        state {{
                            name
                            type
                        }}
                        priority
                        assignee {{
                            id
                            name
                        }}
                        team {{
                            id
                            name
                        }}
                        project {{
                            id
                            name
                        }}
                        createdAt
                        updatedAt
                    }}
                }}
            }}
            """
        else:
            search_query = f"""
            query {{
                issues({filter_clause}, first: {min(limit, 50)}) {{
                    nodes {{
                        id
                        title
                        description
                        state {{
                            name
                            type
                        }}
                        priority
                        assignee {{
                            id
                            name
                        }}
                        team {{
                            id
                            name
                        }}
                        project {{
                            id
                            name
                        }}
                        createdAt
                        updatedAt
                    }}
                }}
            }}
            """

        result = await self.make_request(search_query)
        
        if query:
            issues_data = result.get("issueSearch", {})
        else:
            issues_data = result.get("issues", {})

        return {
            "issues": issues_data.get("nodes", []),
            "total_count": len(issues_data.get("nodes", [])),
            "search_query": query
        }

    async def get_user_issues(
        self,
        user_id: str,
        state: Optional[str] = None,
        team_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get issues assigned to a specific user."""
        filter_conditions = [f'assignee: {{ id: {{ eq: "{user_id}" }} }}']
        
        if state:
            filter_conditions.append(f'state: {{ name: {{ eq: "{state}" }} }}')
        if team_id:
            filter_conditions.append(f'team: {{ id: {{ eq: "{team_id}" }} }}')

        filter_clause = f"filter: {{ {', '.join(filter_conditions)} }}"

        query = f"""
        query {{
            issues({filter_clause}, first: 100) {{
                nodes {{
                    id
                    title
                    state {{
                        name
                        type
                    }}
                    priority
                    team {{
                        id
                        name
                    }}
                    project {{
                        id
                        name
                    }}
                    createdAt
                    updatedAt
                    dueDate
                }}
            }}
        }}
        """

        result = await self.make_request(query)
        issues_data = result.get("issues", {})

        return {
            "user_id": user_id,
            "issues": issues_data.get("nodes", []),
            "total_count": len(issues_data.get("nodes", []))
        }

    async def get_workspace_users(self, include_guests: bool = False) -> Dict[str, Any]:
        """Get users in the workspace."""
        filter_clause = ""
        if not include_guests:
            filter_clause = 'filter: { isGuest: { eq: false } }'

        query = f"""
        query {{
            users({filter_clause}) {{
                nodes {{
                    id
                    name
                    email
                    isActive
                    isGuest
                    createdAt
                    assignedIssues {{
                        nodes {{
                            id
                            state {{
                                type
                            }}
                        }}
                    }}
                    teamMemberships {{
                        nodes {{
                            team {{
                                id
                                name
                            }}
                        }}
                    }}
                }}
            }}
        }}
        """

        result = await self.make_request(query)
        users_data = result.get("users", {})
        users = users_data.get("nodes", [])

        # Enhance user data with metrics
        enhanced_users = []
        for user in users:
            assigned_issues = user.get("assignedIssues", {}).get("nodes", [])
            active_issues = len([i for i in assigned_issues if i.get("state", {}).get("type") != "completed"])
            teams = user.get("teamMemberships", {}).get("nodes", [])
            
            user["metrics"] = {
                "total_assigned_issues": len(assigned_issues),
                "active_issues": active_issues,
                "team_count": len(teams)
            }
            
            enhanced_users.append(user)

        return {
            "users": enhanced_users,
            "total_count": len(enhanced_users)
        }


async def main():
    """Main entry point for the Linear MCP server."""
    server = LinearMCPServer()
    
    async with stdio_server() as (read_stream, write_stream):
        await server.server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="linear-mcp-server",
                server_version="1.0.0",
                capabilities=server.server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())

