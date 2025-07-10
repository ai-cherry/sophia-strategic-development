"""
Sophia AI Asana MCP Server
Using official Anthropic MCP SDK

Date: July 10, 2025
"""

import asyncio
import sys
from pathlib import Path
from typing import Any, Dict, List

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp.types import Tool, TextContent

from base.unified_standardized_base import StandardizedMCPServer, ServerConfig
from backend.core.auto_esc_config import get_config_value


class AsanaMCPServer(StandardizedMCPServer):
    """Asana MCP Server using official SDK"""
    
    def __init__(self):
        config = ServerConfig(
            name="asana",
            version="1.0.0",
            description="Asana project and task management server"
        )
        super().__init__(config)
        
        # Asana configuration
        self.access_token = get_config_value("asana_access_token")
        self.workspace_gid = get_config_value("asana_workspace_gid")
        
    async def get_custom_tools(self) -> List[Tool]:
        """Define custom tools for Asana operations"""
        return [
            Tool(
                name="list_projects",
                description="List projects in workspace",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "workspace": {
                            "type": "string",
                            "description": f"Workspace ID (default: {self.workspace_gid})"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum projects (default: 20)"
                        }
                    },
                    "required": []
                }
            ),
            Tool(
                name="get_project_tasks",
                description="Get tasks for a project",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "project_id": {
                            "type": "string",
                            "description": "Project ID"
                        },
                        "completed": {
                            "type": "boolean",
                            "description": "Include completed tasks (default: false)"
                        }
                    },
                    "required": ["project_id"]
                }
            ),
            Tool(
                name="create_task",
                description="Create a new task",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "project_id": {
                            "type": "string",
                            "description": "Project ID"
                        },
                        "name": {
                            "type": "string",
                            "description": "Task name"
                        },
                        "description": {
                            "type": "string",
                            "description": "Task description"
                        },
                        "assignee": {
                            "type": "string",
                            "description": "Assignee email or ID"
                        },
                        "due_date": {
                            "type": "string",
                            "description": "Due date (YYYY-MM-DD)"
                        }
                    },
                    "required": ["project_id", "name"]
                }
            ),
            Tool(
                name="update_task",
                description="Update an existing task",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "string",
                            "description": "Task ID"
                        },
                        "name": {
                            "type": "string",
                            "description": "Updated task name"
                        },
                        "description": {
                            "type": "string",
                            "description": "Updated description"
                        },
                        "completed": {
                            "type": "boolean",
                            "description": "Mark as completed"
                        },
                        "due_date": {
                            "type": "string",
                            "description": "Updated due date"
                        }
                    },
                    "required": ["task_id"]
                }
            ),
            Tool(
                name="get_task_details",
                description="Get detailed information about a task",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "string",
                            "description": "Task ID"
                        }
                    },
                    "required": ["task_id"]
                }
            ),
            Tool(
                name="add_comment",
                description="Add a comment to a task",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "string",
                            "description": "Task ID"
                        },
                        "text": {
                            "type": "string",
                            "description": "Comment text"
                        }
                    },
                    "required": ["task_id", "text"]
                }
            ),
            Tool(
                name="search_tasks",
                description="Search for tasks",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query"
                        },
                        "project_id": {
                            "type": "string",
                            "description": "Limit to specific project"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum results (default: 10)"
                        }
                    },
                    "required": ["query"]
                }
            )
        ]
    
    async def handle_custom_tool(self, name: str, arguments: dict) -> Dict[str, Any]:
        """Handle custom tool calls"""
        try:
            if name == "list_projects":
                return await self._list_projects(arguments)
            elif name == "get_project_tasks":
                return await self._get_project_tasks(arguments)
            elif name == "create_task":
                return await self._create_task(arguments)
            elif name == "update_task":
                return await self._update_task(arguments)
            elif name == "get_task_details":
                return await self._get_task_details(arguments)
            elif name == "add_comment":
                return await self._add_comment(arguments)
            elif name == "search_tasks":
                return await self._search_tasks(arguments)
            else:
                raise ValueError(f"Unknown tool: {name}")
        except Exception as e:
            self.logger.error(f"Error handling tool {name}: {e}")
            return {"status": "error", "error": str(e)}
    
    async def _list_projects(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List projects"""
        try:
            workspace = params.get("workspace", self.workspace_gid)
            limit = params.get("limit", 20)
            
            # In production, would use Asana API
            # Simulate response
            projects = [
                {
                    "gid": "1234567890",
                    "name": "Sophia AI Development",
                    "created_at": "2025-01-15T00:00:00Z",
                    "modified_at": "2025-07-10T00:00:00Z",
                    "color": "light-green",
                    "members": 12
                },
                {
                    "gid": "2345678901",
                    "name": "Q3 Marketing Campaign",
                    "created_at": "2025-06-01T00:00:00Z",
                    "modified_at": "2025-07-09T00:00:00Z",
                    "color": "light-blue",
                    "members": 8
                }
            ]
            
            return {
                "status": "success",
                "workspace": workspace,
                "projects": projects[:limit],
                "total": len(projects)
            }
            
        except Exception as e:
            self.logger.error(f"Error listing projects: {e}")
            raise
    
    async def _get_project_tasks(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get project tasks"""
        try:
            project_id = params["project_id"]
            include_completed = params.get("completed", False)
            
            # In production, would use Asana API
            # Simulate response
            tasks = [
                {
                    "gid": "3456789012",
                    "name": "Implement MCP server standardization",
                    "completed": False,
                    "assignee": {"name": "John Doe"},
                    "due_on": "2025-07-15",
                    "created_at": "2025-07-08T00:00:00Z"
                },
                {
                    "gid": "4567890123",
                    "name": "Review ETL pipeline architecture",
                    "completed": True,
                    "assignee": {"name": "Jane Smith"},
                    "due_on": "2025-07-10",
                    "created_at": "2025-07-05T00:00:00Z"
                }
            ]
            
            # Filter completed if needed
            if not include_completed:
                tasks = [t for t in tasks if not t["completed"]]
            
            return {
                "status": "success",
                "project_id": project_id,
                "tasks": tasks,
                "total": len(tasks)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting project tasks: {e}")
            raise
    
    async def _create_task(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create task"""
        try:
            project_id = params["project_id"]
            name = params["name"]
            description = params.get("description", "")
            assignee = params.get("assignee")
            due_date = params.get("due_date")
            
            # In production, would use Asana API
            # Simulate response
            task = {
                "gid": "5678901234",
                "name": name,
                "description": description,
                "completed": False,
                "assignee": {"email": assignee} if assignee else None,
                "due_on": due_date,
                "created_at": "2025-07-10T00:00:00Z",
                "project": {"gid": project_id}
            }
            
            self.logger.info(f"Created task: {name}")
            
            return {
                "status": "success",
                "task": task
            }
            
        except Exception as e:
            self.logger.error(f"Error creating task: {e}")
            raise
    
    async def _update_task(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update task"""
        try:
            task_id = params["task_id"]
            
            # In production, would use Asana API
            # Simulate response
            updated_fields = {}
            if "name" in params:
                updated_fields["name"] = params["name"]
            if "description" in params:
                updated_fields["description"] = params["description"]
            if "completed" in params:
                updated_fields["completed"] = params["completed"]
            if "due_date" in params:
                updated_fields["due_on"] = params["due_date"]
            
            self.logger.info(f"Updated task {task_id}")
            
            return {
                "status": "success",
                "task_id": task_id,
                "updated_fields": updated_fields
            }
            
        except Exception as e:
            self.logger.error(f"Error updating task: {e}")
            raise
    
    async def _get_task_details(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get task details"""
        try:
            task_id = params["task_id"]
            
            # In production, would use Asana API
            # Simulate response
            task = {
                "gid": task_id,
                "name": "Detailed task information",
                "description": "This is a detailed description of the task",
                "completed": False,
                "assignee": {
                    "gid": "6789012345",
                    "name": "John Doe",
                    "email": "john.doe@company.com"
                },
                "due_on": "2025-07-15",
                "created_at": "2025-07-08T00:00:00Z",
                "modified_at": "2025-07-10T00:00:00Z",
                "tags": ["urgent", "development"],
                "followers": [
                    {"name": "Jane Smith"},
                    {"name": "Bob Johnson"}
                ],
                "custom_fields": []
            }
            
            return {
                "status": "success",
                "task": task
            }
            
        except Exception as e:
            self.logger.error(f"Error getting task details: {e}")
            raise
    
    async def _add_comment(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Add comment to task"""
        try:
            task_id = params["task_id"]
            text = params["text"]
            
            # In production, would use Asana API
            # Simulate response
            comment = {
                "gid": "7890123456",
                "text": text,
                "created_at": "2025-07-10T00:00:00Z",
                "author": {
                    "name": "Sophia AI",
                    "email": "sophia@company.com"
                },
                "task": {"gid": task_id}
            }
            
            self.logger.info(f"Added comment to task {task_id}")
            
            return {
                "status": "success",
                "comment": comment
            }
            
        except Exception as e:
            self.logger.error(f"Error adding comment: {e}")
            raise
    
    async def _search_tasks(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search tasks"""
        try:
            query = params["query"]
            project_id = params.get("project_id")
            limit = params.get("limit", 10)
            
            # In production, would use Asana API
            # Simulate response
            tasks = [
                {
                    "gid": "8901234567",
                    "name": f"Task matching: {query}",
                    "completed": False,
                    "project": {"gid": project_id} if project_id else {"gid": "1234567890"},
                    "assignee": {"name": "Team Member"},
                    "due_on": "2025-07-20"
                }
            ]
            
            return {
                "status": "success",
                "query": query,
                "tasks": tasks[:limit],
                "total": len(tasks)
            }
            
        except Exception as e:
            self.logger.error(f"Error searching tasks: {e}")
            raise


async def main():
    """Main entry point"""
    server = AsanaMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main()) 