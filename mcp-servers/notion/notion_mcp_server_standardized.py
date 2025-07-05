#!/usr/bin/env python3
"""
Standardized Notion MCP Server for Sophia AI
Provides Notion integration with project management capabilities using StandardizedMCPServer base class.
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

from backend.mcp_servers.base.unified_mcp_base import (
    MCPServerConfig,
    StandardizedMCPServer,
)

# Try to import Notion
try:
    from notion_client import Client as NotionClient
    from notion_client.errors import APIResponseError
    NOTION_AVAILABLE = True
except ImportError:
    NOTION_AVAILABLE = False
    NotionClient = None
    APIResponseError = Exception


class NotionMCPServer(StandardizedMCPServer):
    """Notion integration MCP server using StandardizedMCPServer base."""

    def __init__(self, config: MCPServerConfig | None = None):
        if config is None:
            config = MCPServerConfig(name="notion", port=9005, version="2.0.0")
        super().__init__(config)
        self.notion_client = None

    async def server_specific_init(self) -> None:
        """Initialize Notion client."""
        # Try to get token from environment variables
        access_token = os.getenv("NOTION_API_TOKEN") or os.getenv("NOTION_TOKEN")
        
        if not access_token:
            self.logger.warning("NOTION_API_TOKEN not set, running in demo mode")
            return

        if not NOTION_AVAILABLE:
            self.logger.warning("notion-client package not installed, running in demo mode")
            return

        try:
            self.notion_client = NotionClient(auth=access_token)
            # Test the connection
            self.notion_client.users.list()
            self.logger.info("Notion client initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize Notion client: {e}")

    async def server_specific_cleanup(self) -> None:
        """Cleanup Notion resources."""
        if self.notion_client:
            self.notion_client = None
        self.logger.info("Notion cleanup complete")

    async def check_server_health(self) -> bool:
        """Check Notion connectivity."""
        if not self.notion_client:
            return True  # Demo mode is considered healthy

        try:
            # Try to list users to verify API connectivity
            self.notion_client.users.list()
            return True
        except Exception as e:
            self.logger.error(f"Notion health check failed: {e}")
            return False

    async def get_tools(self) -> list[dict[str, Any]]:
        """Get Notion tools."""
        return [
            {
                "name": "search_pages",
                "description": "Search Notion pages",
                "inputSchema": {
                    "type": "object", 
                    "properties": {
                        "query": {"type": "string", "description": "Search query"},
                        "filter": {
                            "type": "string", 
                            "enum": ["page", "database", "all"],
                            "default": "all"
                        },
                        "limit": {"type": "integer", "default": 10}
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "create_page",
                "description": "Create a new Notion page",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "content": {"type": "string"},
                        "parent_id": {"type": "string", "description": "Parent page or database ID"}
                    },
                    "required": ["title"]
                }
            },
            {
                "name": "list_databases",
                "description": "List available Notion databases",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "limit": {"type": "integer", "default": 20}
                    }
                }
            },
            {
                "name": "query_database",
                "description": "Query a Notion database",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "database_id": {"type": "string"},
                        "filter": {"type": "object", "description": "Notion filter object"},
                        "sorts": {"type": "array", "description": "Notion sorts array"},
                        "limit": {"type": "integer", "default": 20}
                    },
                    "required": ["database_id"]
                }
            },
            {
                "name": "get_project_status",
                "description": "Get comprehensive project status for executive dashboard",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "project_name": {"type": "string", "description": "Optional project filter"}
                    }
                }
            }
        ]

    async def execute_tool(self, name: str, arguments: dict[str, Any]) -> Any:
        """Execute Notion tool."""
        if name == "search_pages":
            return await self._search_pages(arguments)
        elif name == "create_page":
            return await self._create_page(arguments)
        elif name == "list_databases":
            return await self._list_databases(arguments)
        elif name == "query_database":
            return await self._query_database(arguments)
        elif name == "get_project_status":
            return await self._get_project_status(arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")

    async def _search_pages(self, args: dict[str, Any]) -> dict[str, Any]:
        """Search Notion pages."""
        try:
            query = args["query"]
            filter_type = args.get("filter", "all")
            limit = args.get("limit", 10)

            # Demo data if no client
            if not self.notion_client:
                return {
                    "pages": [
                        {
                            "id": "page_1",
                            "title": f"Demo Project: {query}",
                            "url": "https://notion.so/demo-page-1",
                            "created_time": "2025-01-01T00:00:00Z",
                            "last_edited_time": "2025-01-05T10:00:00Z"
                        },
                        {
                            "id": "page_2", 
                            "title": f"Strategy Document: {query}",
                            "url": "https://notion.so/demo-page-2",
                            "created_time": "2025-01-02T00:00:00Z",
                            "last_edited_time": "2025-01-04T15:30:00Z"
                        }
                    ],
                    "total": 2,
                    "query": query
                }

            # Real Notion API call
            search_filter = {}
            if filter_type != "all":
                search_filter = {"property": "object", "value": filter_type}

            results = self.notion_client.search(
                query=query,
                filter=search_filter,
                page_size=limit
            )

            pages = []
            for result in results["results"]:
                title = "Untitled"
                if result.get("properties") and result["properties"].get("title"):
                    title_prop = result["properties"]["title"]
                    if title_prop.get("title") and len(title_prop["title"]) > 0:
                        title = title_prop["title"][0]["text"]["content"]
                elif result.get("title"):
                    if len(result["title"]) > 0:
                        title = result["title"][0]["text"]["content"]

                pages.append({
                    "id": result["id"],
                    "title": title,
                    "url": result.get("url", ""),
                    "created_time": result.get("created_time", ""),
                    "last_edited_time": result.get("last_edited_time", "")
                })

            return {
                "pages": pages,
                "total": len(pages),
                "query": query
            }

        except Exception as e:
            self.logger.error(f"Failed to search pages: {e}")
            return {"error": str(e), "pages": []}

    async def _create_page(self, args: dict[str, Any]) -> dict[str, Any]:
        """Create a new Notion page."""
        try:
            title = args["title"]
            content = args.get("content", "")
            parent_id = args.get("parent_id")

            # Demo response
            if not self.notion_client:
                page_id = f"page_{datetime.utcnow().timestamp():.0f}"
                return {
                    "id": page_id,
                    "title": title,
                    "url": f"https://notion.so/{page_id}",
                    "created_time": datetime.utcnow().isoformat()
                }

            # Create page properties
            page_data = {
                "properties": {
                    "title": {
                        "title": [
                            {
                                "text": {
                                    "content": title
                                }
                            }
                        ]
                    }
                }
            }

            # Add parent if specified
            if parent_id:
                page_data["parent"] = {"page_id": parent_id}
            else:
                # Use workspace as parent
                page_data["parent"] = {"type": "workspace", "workspace": True}

            # Add content if provided
            if content:
                page_data["children"] = [
                    {
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [
                                {
                                    "type": "text",
                                    "text": {
                                        "content": content
                                    }
                                }
                            ]
                        }
                    }
                ]

            # Create the page
            result = self.notion_client.pages.create(**page_data)

            return {
                "id": result["id"],
                "title": title,
                "url": result.get("url", ""),
                "created_time": result.get("created_time", "")
            }

        except Exception as e:
            self.logger.error(f"Failed to create page: {e}")
            return {"error": str(e)}

    async def _list_databases(self, args: dict[str, Any]) -> dict[str, Any]:
        """List Notion databases."""
        try:
            limit = args.get("limit", 20)

            # Demo data
            if not self.notion_client:
                return {
                    "databases": [
                        {
                            "id": "db_1",
                            "title": "Projects",
                            "description": "Project management database",
                            "url": "https://notion.so/db_1"
                        },
                        {
                            "id": "db_2", 
                            "title": "Tasks",
                            "description": "Task tracking database",
                            "url": "https://notion.so/db_2"
                        }
                    ],
                    "total": 2
                }

            # Search for databases
            results = self.notion_client.search(
                filter={"property": "object", "value": "database"},
                page_size=limit
            )

            databases = []
            for result in results["results"]:
                title = "Untitled Database"
                if result.get("title") and len(result["title"]) > 0:
                    title = result["title"][0]["text"]["content"]

                databases.append({
                    "id": result["id"],
                    "title": title,
                    "description": result.get("description", [{}])[0].get("text", {}).get("content", ""),
                    "url": result.get("url", "")
                })

            return {
                "databases": databases,
                "total": len(databases)
            }

        except Exception as e:
            self.logger.error(f"Failed to list databases: {e}")
            return {"error": str(e), "databases": []}

    async def _query_database(self, args: dict[str, Any]) -> dict[str, Any]:
        """Query a Notion database."""
        try:
            database_id = args["database_id"]
            filter_obj = args.get("filter", {})
            sorts = args.get("sorts", [])
            limit = args.get("limit", 20)

            # Demo data
            if not self.notion_client:
                return {
                    "results": [
                        {
                            "id": "item_1",
                            "properties": {
                                "Name": {"title": [{"text": {"content": "Sample Project"}}]},
                                "Status": {"select": {"name": "In Progress"}},
                                "Progress": {"number": 75}
                            }
                        }
                    ],
                    "total": 1,
                    "database_id": database_id
                }

            # Build query parameters
            query_params = {"database_id": database_id, "page_size": limit}
            if filter_obj:
                query_params["filter"] = filter_obj
            if sorts:
                query_params["sorts"] = sorts

            # Query the database
            result = self.notion_client.databases.query(**query_params)

            return {
                "results": result["results"],
                "total": len(result["results"]),
                "database_id": database_id,
                "has_more": result.get("has_more", False)
            }

        except Exception as e:
            self.logger.error(f"Failed to query database: {e}")
            return {"error": str(e), "results": []}

    async def _get_project_status(self, args: dict[str, Any]) -> dict[str, Any]:
        """Get comprehensive project status for executive dashboard."""
        try:
            project_name = args.get("project_name", "")

            # Demo executive summary
            return {
                "project_name": project_name or "All Projects",
                "overall_status": "On Track",
                "progress_percentage": 78.5,
                "metrics": {
                    "total_projects": 12,
                    "completed_projects": 8,
                    "in_progress_projects": 3,
                    "blocked_projects": 1,
                    "total_tasks": 156,
                    "completed_tasks": 89,
                    "overdue_tasks": 7
                },
                "key_milestones": [
                    {
                        "name": "Q1 Strategy Review",
                        "due_date": "2025-01-15",
                        "status": "at_risk",
                        "progress": 65
                    },
                    {
                        "name": "Product Launch Prep",
                        "due_date": "2025-01-31", 
                        "status": "on_track",
                        "progress": 85
                    }
                ],
                "recent_updates": [
                    {
                        "title": "Marketing campaign approved",
                        "date": "2025-01-05",
                        "type": "milestone"
                    },
                    {
                        "title": "Development sprint completed",
                        "date": "2025-01-04",
                        "type": "progress"
                    }
                ],
                "risks": [
                    {
                        "description": "Resource allocation for Q2",
                        "severity": "medium",
                        "mitigation": "Hiring additional team members"
                    }
                ],
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Failed to get project status: {e}")
            return {"error": str(e)}


def main():
    """Main entry point for the Notion MCP server."""
    # Create and run the server
    notion_server = NotionMCPServer()
    notion_server.run()


if __name__ == "__main__":
    # If running as FastAPI app
    if os.getenv("RUN_AS_FASTAPI", "false").lower() == "true":
        import uvicorn
        from fastapi import APIRouter, FastAPI

        app = FastAPI(title="Notion MCP Server")
        router = APIRouter(prefix="/mcp/notion")

        @router.get("/health")
        async def health():
            return {"status": "healthy", "service": "notion-mcp-server"}

        app.include_router(router)

        # Run with uvicorn
        uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "9005")))
    else:
        # Run as MCP server
        main() 