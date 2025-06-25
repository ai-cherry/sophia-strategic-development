#!/usr/bin/env python3
"""
Notion MCP Server for Sophia AI
Provides knowledge base access, document management, and strategic planning features.
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

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
logger = logging.getLogger("notion-mcp-server")


class NotionMCPServer:
    """Notion MCP Server for knowledge base and document management."""

    def __init__(self):
        self.server = Server("notion-mcp-server")
        self.base_url = "https://api.notion.com/v1"
        self.access_token = os.getenv("NOTION_ACCESS_TOKEN")
        self.notion_version = "2022-06-28"

        if not self.access_token:
            logger.error("NOTION_ACCESS_TOKEN environment variable not set")
            sys.exit(1)

        # Setup MCP server handlers
        self.setup_handlers()

    def setup_handlers(self):
        """Setup MCP server request handlers."""

        @self.server.list_tools()
        async def handle_list_tools() -> ListToolsResult:
            """List available Notion tools."""
            return ListToolsResult(
                tools=[
                    Tool(
                        name="search_pages",
                        description="Search for pages in Notion workspace",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "query": {
                                    "type": "string",
                                    "description": "Search query text",
                                },
                                "filter": {
                                    "type": "object",
                                    "description": "Filter criteria for search",
                                    "properties": {
                                        "property": {
                                            "type": "string",
                                            "description": "Property name to filter by",
                                        },
                                        "value": {
                                            "type": "string",
                                            "description": "Value to filter for",
                                        },
                                    },
                                },
                                "sort": {
                                    "type": "object",
                                    "description": "Sort criteria",
                                    "properties": {
                                        "direction": {
                                            "type": "string",
                                            "enum": ["ascending", "descending"],
                                            "description": "Sort direction",
                                        },
                                        "timestamp": {
                                            "type": "string",
                                            "enum": [
                                                "created_time",
                                                "last_edited_time",
                                            ],
                                            "description": "Timestamp to sort by",
                                        },
                                    },
                                },
                                "page_size": {
                                    "type": "integer",
                                    "description": "Number of results to return (max 100)",
                                },
                            },
                        },
                    ),
                    Tool(
                        name="get_page",
                        description="Get detailed information about a specific page",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "page_id": {
                                    "type": "string",
                                    "description": "Page ID to retrieve",
                                    "required": True,
                                }
                            },
                            "required": ["page_id"],
                        },
                    ),
                    Tool(
                        name="get_page_content",
                        description="Get the content blocks of a page",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "page_id": {
                                    "type": "string",
                                    "description": "Page ID to get content for",
                                    "required": True,
                                },
                                "page_size": {
                                    "type": "integer",
                                    "description": "Number of blocks to return (max 100)",
                                },
                            },
                            "required": ["page_id"],
                        },
                    ),
                    Tool(
                        name="get_database",
                        description="Get information about a database",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "database_id": {
                                    "type": "string",
                                    "description": "Database ID to retrieve",
                                    "required": True,
                                }
                            },
                            "required": ["database_id"],
                        },
                    ),
                    Tool(
                        name="query_database",
                        description="Query a database with filters and sorting",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "database_id": {
                                    "type": "string",
                                    "description": "Database ID to query",
                                    "required": True,
                                },
                                "filter": {
                                    "type": "object",
                                    "description": "Filter criteria for database query",
                                },
                                "sorts": {
                                    "type": "array",
                                    "description": "Sort criteria for database query",
                                },
                                "page_size": {
                                    "type": "integer",
                                    "description": "Number of results to return (max 100)",
                                },
                            },
                            "required": ["database_id"],
                        },
                    ),
                    Tool(
                        name="get_users",
                        description="Get list of users in the workspace",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "page_size": {
                                    "type": "integer",
                                    "description": "Number of users to return (max 100)",
                                }
                            },
                        },
                    ),
                    Tool(
                        name="get_user",
                        description="Get information about a specific user",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "user_id": {
                                    "type": "string",
                                    "description": "User ID to retrieve",
                                    "required": True,
                                }
                            },
                            "required": ["user_id"],
                        },
                    ),
                    Tool(
                        name="search_by_title",
                        description="Search pages by title text",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "title": {
                                    "type": "string",
                                    "description": "Title text to search for",
                                    "required": True,
                                },
                                "exact_match": {
                                    "type": "boolean",
                                    "description": "Whether to match exact title (default: false)",
                                },
                            },
                            "required": ["title"],
                        },
                    ),
                    Tool(
                        name="get_recent_pages",
                        description="Get recently edited pages",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "days": {
                                    "type": "integer",
                                    "description": "Number of days to look back (default: 7)",
                                },
                                "page_size": {
                                    "type": "integer",
                                    "description": "Number of pages to return (max 100)",
                                },
                            },
                        },
                    ),
                    Tool(
                        name="get_page_analytics",
                        description="Get analytics and metadata for a page",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "page_id": {
                                    "type": "string",
                                    "description": "Page ID to analyze",
                                    "required": True,
                                }
                            },
                            "required": ["page_id"],
                        },
                    ),
                    Tool(
                        name="search_strategic_content",
                        description="Search for strategic planning and OKR-related content",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "content_type": {
                                    "type": "string",
                                    "enum": [
                                        "okr",
                                        "strategy",
                                        "planning",
                                        "goals",
                                        "metrics",
                                    ],
                                    "description": "Type of strategic content to search for",
                                },
                                "quarter": {
                                    "type": "string",
                                    "description": "Quarter to filter by (e.g., 'Q3 2024')",
                                },
                            },
                        },
                    ),
                ]
            )

        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict) -> CallToolResult:
            """Handle tool calls."""
            try:
                if name == "search_pages":
                    result = await self.search_pages(**arguments)
                elif name == "get_page":
                    result = await self.get_page(**arguments)
                elif name == "get_page_content":
                    result = await self.get_page_content(**arguments)
                elif name == "get_database":
                    result = await self.get_database(**arguments)
                elif name == "query_database":
                    result = await self.query_database(**arguments)
                elif name == "get_users":
                    result = await self.get_users(**arguments)
                elif name == "get_user":
                    result = await self.get_user(**arguments)
                elif name == "search_by_title":
                    result = await self.search_by_title(**arguments)
                elif name == "get_recent_pages":
                    result = await self.get_recent_pages(**arguments)
                elif name == "get_page_analytics":
                    result = await self.get_page_analytics(**arguments)
                elif name == "search_strategic_content":
                    result = await self.search_strategic_content(**arguments)
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

    async def make_request(
        self, method: str, endpoint: str, data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make authenticated request to Notion API."""
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "Notion-Version": self.notion_version,
        }

        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        async with aiohttp.ClientSession() as session:
            if method.upper() == "GET":
                async with session.get(url, headers=headers, params=data) as response:
                    return await self._handle_response(response)
            elif method.upper() == "POST":
                async with session.post(url, headers=headers, json=data) as response:
                    return await self._handle_response(response)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

    async def _handle_response(self, response) -> Dict[str, Any]:
        """Handle API response."""
        if response.status == 200:
            return await response.json()
        else:
            error_text = await response.text()
            raise Exception(f"Notion API error {response.status}: {error_text}")

    async def search_pages(
        self,
        query: Optional[str] = None,
        filter: Optional[Dict] = None,
        sort: Optional[Dict] = None,
        page_size: int = 100,
    ) -> Dict[str, Any]:
        """Search for pages in Notion."""
        search_data = {"page_size": min(page_size, 100)}

        if query:
            search_data["query"] = query

        if filter:
            search_data["filter"] = filter

        if sort:
            search_data["sort"] = sort

        result = await self.make_request("POST", "search", search_data)

        # Enhance results with additional metadata
        enhanced_results = []
        for page in result.get("results", []):
            try:
                enhanced_page = await self._enhance_page_data(page)
                enhanced_results.append(enhanced_page)
            except Exception as e:
                logger.warning(
                    f"Could not enhance page {page.get('id', 'unknown')}: {e}"
                )
                enhanced_results.append(page)

        return {
            "results": enhanced_results,
            "has_more": result.get("has_more", False),
            "next_cursor": result.get("next_cursor"),
            "total_results": len(enhanced_results),
            "search_criteria": {"query": query, "filter": filter, "sort": sort},
            "sync_time": datetime.now().isoformat(),
        }

    async def get_page(self, page_id: str) -> Dict[str, Any]:
        """Get detailed page information."""
        page = await self.make_request("GET", f"pages/{page_id}")
        enhanced_page = await self._enhance_page_data(page)

        return {"page": enhanced_page, "sync_time": datetime.now().isoformat()}

    async def get_page_content(
        self, page_id: str, page_size: int = 100
    ) -> Dict[str, Any]:
        """Get page content blocks."""
        params = {"page_size": min(page_size, 100)}

        result = await self.make_request("GET", f"blocks/{page_id}/children", params)

        # Analyze content structure
        content_analysis = self._analyze_content_blocks(result.get("results", []))

        return {
            "page_id": page_id,
            "blocks": result.get("results", []),
            "has_more": result.get("has_more", False),
            "next_cursor": result.get("next_cursor"),
            "content_analysis": content_analysis,
            "sync_time": datetime.now().isoformat(),
        }

    async def get_database(self, database_id: str) -> Dict[str, Any]:
        """Get database information."""
        database = await self.make_request("GET", f"databases/{database_id}")

        return {"database": database, "sync_time": datetime.now().isoformat()}

    async def query_database(
        self,
        database_id: str,
        filter: Optional[Dict] = None,
        sorts: Optional[List] = None,
        page_size: int = 100,
    ) -> Dict[str, Any]:
        """Query database with filters and sorting."""
        query_data = {"page_size": min(page_size, 100)}

        if filter:
            query_data["filter"] = filter

        if sorts:
            query_data["sorts"] = sorts

        result = await self.make_request(
            "POST", f"databases/{database_id}/query", query_data
        )

        # Enhance database results
        enhanced_results = []
        for page in result.get("results", []):
            try:
                enhanced_page = await self._enhance_database_page(page)
                enhanced_results.append(enhanced_page)
            except Exception as e:
                logger.warning(
                    f"Could not enhance database page {page.get('id', 'unknown')}: {e}"
                )
                enhanced_results.append(page)

        return {
            "database_id": database_id,
            "results": enhanced_results,
            "has_more": result.get("has_more", False),
            "next_cursor": result.get("next_cursor"),
            "result_count": len(enhanced_results),
            "query_criteria": {"filter": filter, "sorts": sorts},
            "sync_time": datetime.now().isoformat(),
        }

    async def get_users(self, page_size: int = 100) -> Dict[str, Any]:
        """Get workspace users."""
        params = {"page_size": min(page_size, 100)}

        result = await self.make_request("GET", "users", params)

        return {
            "users": result.get("results", []),
            "has_more": result.get("has_more", False),
            "next_cursor": result.get("next_cursor"),
            "user_count": len(result.get("results", [])),
            "sync_time": datetime.now().isoformat(),
        }

    async def get_user(self, user_id: str) -> Dict[str, Any]:
        """Get specific user information."""
        user = await self.make_request("GET", f"users/{user_id}")

        return {"user": user, "sync_time": datetime.now().isoformat()}

    async def search_by_title(
        self, title: str, exact_match: bool = False
    ) -> Dict[str, Any]:
        """Search pages by title."""
        if exact_match:
            filter_criteria = {"property": "object", "value": "page"}
        else:
            filter_criteria = None

        result = await self.search_pages(query=title, filter=filter_criteria)

        # Filter results by title match
        if exact_match:
            filtered_results = [
                page
                for page in result["results"]
                if self._extract_title(page).lower() == title.lower()
            ]
        else:
            title_lower = title.lower()
            filtered_results = [
                page
                for page in result["results"]
                if title_lower in self._extract_title(page).lower()
            ]

        return {
            "search_title": title,
            "exact_match": exact_match,
            "results": filtered_results,
            "result_count": len(filtered_results),
            "sync_time": datetime.now().isoformat(),
        }

    async def get_recent_pages(
        self, days: int = 7, page_size: int = 100
    ) -> Dict[str, Any]:
        """Get recently edited pages."""
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()

        sort_criteria = {"direction": "descending", "timestamp": "last_edited_time"}

        filter_criteria = {"property": "object", "value": "page"}

        result = await self.search_pages(
            filter=filter_criteria, sort=sort_criteria, page_size=page_size
        )

        # Filter by date
        recent_pages = [
            page
            for page in result["results"]
            if page.get("last_edited_time", "") >= cutoff_date
        ]

        return {
            "days_back": days,
            "cutoff_date": cutoff_date,
            "recent_pages": recent_pages,
            "page_count": len(recent_pages),
            "sync_time": datetime.now().isoformat(),
        }

    async def get_page_analytics(self, page_id: str) -> Dict[str, Any]:
        """Get analytics and metadata for a page."""
        page = await self.get_page(page_id)
        content = await self.get_page_content(page_id)

        page_data = page["page"]
        content_data = content["content_analysis"]

        # Calculate page metrics
        analytics = {
            "page_id": page_id,
            "title": self._extract_title(page_data),
            "created_time": page_data.get("created_time"),
            "last_edited_time": page_data.get("last_edited_time"),
            "created_by": page_data.get("created_by", {}).get("id"),
            "last_edited_by": page_data.get("last_edited_by", {}).get("id"),
            "content_metrics": content_data,
            "properties": self._extract_properties(page_data),
            "url": page_data.get("url"),
            "sync_time": datetime.now().isoformat(),
        }

        return analytics

    async def search_strategic_content(
        self, content_type: Optional[str] = None, quarter: Optional[str] = None
    ) -> Dict[str, Any]:
        """Search for strategic planning content."""
        search_terms = {
            "okr": ["OKR", "objective", "key result", "goal"],
            "strategy": ["strategy", "strategic", "vision", "mission"],
            "planning": ["plan", "planning", "roadmap", "timeline"],
            "goals": ["goal", "target", "objective", "achievement"],
            "metrics": ["metric", "KPI", "measurement", "performance"],
        }

        query_terms = []
        if content_type and content_type in search_terms:
            query_terms.extend(search_terms[content_type])
        else:
            # Search all strategic content
            for terms in search_terms.values():
                query_terms.extend(terms)

        if quarter:
            query_terms.append(quarter)

        query = " OR ".join(query_terms[:10])  # Limit query complexity

        result = await self.search_pages(query=query)

        # Categorize results
        categorized_results = {
            "okr_pages": [],
            "strategy_pages": [],
            "planning_pages": [],
            "goal_pages": [],
            "metric_pages": [],
        }

        for page in result["results"]:
            title = self._extract_title(page).lower()
            content = str(page.get("properties", {})).lower()

            if any(
                term in title or term in content for term in search_terms.get("okr", [])
            ):
                categorized_results["okr_pages"].append(page)
            elif any(
                term in title or term in content
                for term in search_terms.get("strategy", [])
            ):
                categorized_results["strategy_pages"].append(page)
            elif any(
                term in title or term in content
                for term in search_terms.get("planning", [])
            ):
                categorized_results["planning_pages"].append(page)
            elif any(
                term in title or term in content
                for term in search_terms.get("goals", [])
            ):
                categorized_results["goal_pages"].append(page)
            elif any(
                term in title or term in content
                for term in search_terms.get("metrics", [])
            ):
                categorized_results["metric_pages"].append(page)

        return {
            "search_criteria": {
                "content_type": content_type,
                "quarter": quarter,
                "query": query,
            },
            "all_results": result["results"],
            "categorized_results": categorized_results,
            "summary": {
                "total_pages": len(result["results"]),
                "okr_pages": len(categorized_results["okr_pages"]),
                "strategy_pages": len(categorized_results["strategy_pages"]),
                "planning_pages": len(categorized_results["planning_pages"]),
                "goal_pages": len(categorized_results["goal_pages"]),
                "metric_pages": len(categorized_results["metric_pages"]),
            },
            "sync_time": datetime.now().isoformat(),
        }

    async def _enhance_page_data(self, page: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance page data with additional metadata."""
        enhanced = page.copy()

        # Extract and normalize title
        enhanced["extracted_title"] = self._extract_title(page)

        # Extract properties in a normalized format
        enhanced["extracted_properties"] = self._extract_properties(page)

        # Add content preview if it's a page
        if page.get("object") == "page":
            try:
                content_preview = await self._get_content_preview(page["id"])
                enhanced["content_preview"] = content_preview
            except Exception as e:
                logger.debug(
                    f"Could not get content preview for page {page['id']}: {e}"
                )
                enhanced["content_preview"] = None

        return enhanced

    async def _enhance_database_page(self, page: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance database page with extracted property values."""
        enhanced = page.copy()

        # Extract property values in a more usable format
        properties = page.get("properties", {})
        extracted_props = {}

        for prop_name, prop_data in properties.items():
            prop_type = prop_data.get("type")

            if prop_type == "title":
                extracted_props[prop_name] = self._extract_title_property(prop_data)
            elif prop_type == "rich_text":
                extracted_props[prop_name] = self._extract_rich_text(prop_data)
            elif prop_type == "number":
                extracted_props[prop_name] = prop_data.get("number")
            elif prop_type == "select":
                extracted_props[prop_name] = prop_data.get("select", {}).get("name")
            elif prop_type == "multi_select":
                extracted_props[prop_name] = [
                    item.get("name") for item in prop_data.get("multi_select", [])
                ]
            elif prop_type == "date":
                extracted_props[prop_name] = prop_data.get("date", {}).get("start")
            elif prop_type == "checkbox":
                extracted_props[prop_name] = prop_data.get("checkbox")
            elif prop_type == "url":
                extracted_props[prop_name] = prop_data.get("url")
            elif prop_type == "email":
                extracted_props[prop_name] = prop_data.get("email")
            elif prop_type == "phone_number":
                extracted_props[prop_name] = prop_data.get("phone_number")
            elif prop_type == "people":
                extracted_props[prop_name] = [
                    person.get("name") for person in prop_data.get("people", [])
                ]

        enhanced["extracted_properties"] = extracted_props
        return enhanced

    async def _get_content_preview(self, page_id: str, max_blocks: int = 3) -> str:
        """Get a preview of page content."""
        try:
            content = await self.get_page_content(page_id, page_size=max_blocks)
            blocks = content.get("blocks", [])

            preview_text = []
            for block in blocks[:max_blocks]:
                block_text = self._extract_block_text(block)
                if block_text:
                    preview_text.append(block_text)

            return " ".join(preview_text)[:200] + "..." if preview_text else ""
        except Exception:
            return ""

    def _extract_title(self, page: Dict[str, Any]) -> str:
        """Extract title from page object."""
        if "properties" in page:
            # Database page
            for prop_name, prop_data in page["properties"].items():
                if prop_data.get("type") == "title":
                    return self._extract_title_property(prop_data)

        # Regular page
        if "title" in page:
            title_blocks = page["title"]
            if title_blocks:
                return "".join(block.get("plain_text", "") for block in title_blocks)

        return "Untitled"

    def _extract_title_property(self, title_prop: Dict[str, Any]) -> str:
        """Extract text from title property."""
        title_blocks = title_prop.get("title", [])
        return "".join(block.get("plain_text", "") for block in title_blocks)

    def _extract_rich_text(self, rich_text_prop: Dict[str, Any]) -> str:
        """Extract text from rich text property."""
        rich_text_blocks = rich_text_prop.get("rich_text", [])
        return "".join(block.get("plain_text", "") for block in rich_text_blocks)

    def _extract_properties(self, page: Dict[str, Any]) -> Dict[str, Any]:
        """Extract properties in a normalized format."""
        if "properties" not in page:
            return {}

        return {
            prop_name: self._normalize_property_value(prop_data)
            for prop_name, prop_data in page["properties"].items()
        }

    def _normalize_property_value(self, prop_data: Dict[str, Any]) -> Any:
        """Normalize property value based on type."""
        prop_type = prop_data.get("type")

        if prop_type == "title":
            return self._extract_title_property(prop_data)
        elif prop_type == "rich_text":
            return self._extract_rich_text(prop_data)
        elif prop_type == "number":
            return prop_data.get("number")
        elif prop_type == "select":
            return prop_data.get("select", {}).get("name")
        elif prop_type == "multi_select":
            return [item.get("name") for item in prop_data.get("multi_select", [])]
        elif prop_type == "date":
            return prop_data.get("date", {}).get("start")
        elif prop_type == "checkbox":
            return prop_data.get("checkbox")
        elif prop_type == "url":
            return prop_data.get("url")
        elif prop_type == "email":
            return prop_data.get("email")
        elif prop_type == "phone_number":
            return prop_data.get("phone_number")
        elif prop_type == "people":
            return [person.get("name") for person in prop_data.get("people", [])]
        else:
            return str(prop_data)

    def _analyze_content_blocks(self, blocks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze content blocks for structure and metrics."""
        analysis = {
            "total_blocks": len(blocks),
            "block_types": {},
            "text_length": 0,
            "has_images": False,
            "has_links": False,
            "has_tables": False,
            "has_code": False,
        }

        for block in blocks:
            block_type = block.get("type", "unknown")
            analysis["block_types"][block_type] = (
                analysis["block_types"].get(block_type, 0) + 1
            )

            # Extract text and analyze content
            block_text = self._extract_block_text(block)
            if block_text:
                analysis["text_length"] += len(block_text)

                if "http" in block_text:
                    analysis["has_links"] = True

            # Check for specific content types
            if block_type == "image":
                analysis["has_images"] = True
            elif block_type == "table":
                analysis["has_tables"] = True
            elif block_type == "code":
                analysis["has_code"] = True

        return analysis

    def _extract_block_text(self, block: Dict[str, Any]) -> str:
        """Extract text content from a block."""
        block_type = block.get("type")

        if block_type in [
            "paragraph",
            "heading_1",
            "heading_2",
            "heading_3",
            "bulleted_list_item",
            "numbered_list_item",
        ]:
            rich_text = block.get(block_type, {}).get("rich_text", [])
            return "".join(item.get("plain_text", "") for item in rich_text)
        elif block_type == "quote":
            rich_text = block.get("quote", {}).get("rich_text", [])
            return "".join(item.get("plain_text", "") for item in rich_text)
        elif block_type == "callout":
            rich_text = block.get("callout", {}).get("rich_text", [])
            return "".join(item.get("plain_text", "") for item in rich_text)
        elif block_type == "code":
            rich_text = block.get("code", {}).get("rich_text", [])
            return "".join(item.get("plain_text", "") for item in rich_text)

        return ""


async def main():
    """Main entry point for the Notion MCP server."""
    notion_server = NotionMCPServer()

    # Initialize and run the server
    async with stdio_server() as (read_stream, write_stream):
        await notion_server.server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="notion-mcp-server",
                server_version="1.0.0",
                capabilities=notion_server.server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
