
# REAL_NOTION_API_INTEGRATION - Added by implementation script

import httpx
from typing import Dict, List, Optional

class RealNotionClient:
    """Real Notion API client"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.notion.com/v1"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }
    
    async def make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """Make API request to Notion"""
        try:
            url = f"{self.base_url}/{endpoint}"
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                if method.upper() == "GET":
                    response = await client.get(url, headers=self.headers, params=data)
                elif method.upper() == "POST":
                    response = await client.post(url, headers=self.headers, json=data)
                else:
                    raise ValueError(f"Unsupported method: {method}")
                
                if response.status_code in [200, 201]:
                    return response.json()
                else:
                    print(f"Notion API error: {response.status_code} - {response.text}")
                    return {"error": f"API error: {response.status_code}"}
                    
        except Exception as e:
            print(f"Notion API exception: {e}")
            return {"error": str(e)}
    
    async def search_pages(self, query: str = "") -> List[Dict]:
        """Search pages in Notion"""
        data = {
            "filter": {
                "property": "object",
                "value": "page"
            }
        }
        
        if query:
            data["query"] = query
        
        result = await self.make_request("POST", "search", data)
        return result.get("results", []) if "results" in result else []
    
    async def get_databases(self) -> List[Dict]:
        """Get all databases"""
        data = {
            "filter": {
                "property": "object",
                "value": "database"
            }
        }
        
        result = await self.make_request("POST", "search", data)
        return result.get("results", []) if "results" in result else []
    
    async def query_database(self, database_id: str, filter_data: Optional[Dict] = None) -> List[Dict]:
        """Query database"""
        data = {}
        if filter_data:
            data["filter"] = filter_data
        
        result = await self.make_request("POST", f"databases/{database_id}/query", data)
        return result.get("results", []) if "results" in result else []

# Initialize real Notion client
real_notion_client = None

def get_real_notion_client():
    """Get or create real Notion client"""
    global real_notion_client
    
    if real_notion_client is None:
        api_key = os.getenv("NOTION_API_KEY")
        
        if not api_key:
            try:
                result = subprocess.run(
                    ["pulumi", "env", "get", "scoobyjava-org/default/sophia-ai-production", "notion_api_key", "--show-secrets"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0 and result.stdout.strip():
                    api_key = result.stdout.strip().replace('"', '')
            except:
                pass
        
        if api_key and api_key not in ["FROM_GITHUB", "PLACEHOLDER_NOTION_API_KEY", "[secret]"]:
            real_notion_client = RealNotionClient(api_key)
            print(f"✅ Real Notion client initialized")
        else:
            print(f"⚠️  Notion API key not found, using mock data")
    
    return real_notion_client


#!/usr/bin/env python3
"""
Sophia AI Notion MCP Server
Provides knowledge base and documentation management
Using official Anthropic MCP SDK

Date: July 10, 2025
"""

import sys
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


class NotionMCPServer(StandardizedMCPServer):
    """Notion MCP Server for knowledge management"""

    def __init__(self):
        config = ServerConfig(
            name="notion",
            version="2.0.0",
            port=9011,
            capabilities=["KNOWLEDGE_BASE", "DOCUMENTATION", "WIKI"],
            tier="SECONDARY",
        )
        super().__init__(config)

        # Notion configuration
        self.api_key = get_config_value("notion_api_token")
        self.api_url = "https://api.notion.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28",
        }

    def get_tool_definitions(self) -> list[ToolDefinition]:
        """Define Notion tools"""
        return [
            ToolDefinition(
                name="search_pages",
                description="Search Notion pages by query",
                parameters=[
                    ToolParameter(
                        name="query",
                        type="string",
                        description="Search query",
                        required=True,
                    ),
                    ToolParameter(
                        name="filter_type",
                        type="string",
                        description="Filter by type: page or database",
                        required=False,
                    ),
                ],
            ),
            ToolDefinition(
                name="get_page",
                description="Get Notion page content",
                parameters=[
                    ToolParameter(
                        name="page_id",
                        type="string",
                        description="Notion page ID",
                        required=True,
                    ),
                ],
            ),
            ToolDefinition(
                name="create_page",
                description="Create a new Notion page",
                parameters=[
                    ToolParameter(
                        name="title",
                        type="string",
                        description="Page title",
                        required=True,
                    ),
                    ToolParameter(
                        name="content",
                        type="string",
                        description="Page content (markdown supported)",
                        required=True,
                    ),
                    ToolParameter(
                        name="parent_page_id",
                        type="string",
                        description="Parent page ID (optional)",
                        required=False,
                    ),
                ],
            ),
            ToolDefinition(
                name="update_page",
                description="Update an existing Notion page",
                parameters=[
                    ToolParameter(
                        name="page_id",
                        type="string",
                        description="Page ID to update",
                        required=True,
                    ),
                    ToolParameter(
                        name="content",
                        type="string",
                        description="New content (markdown supported)",
                        required=True,
                    ),
                ],
            ),
            ToolDefinition(
                name="query_database",
                description="Query a Notion database",
                parameters=[
                    ToolParameter(
                        name="database_id",
                        type="string",
                        description="Database ID",
                        required=True,
                    ),
                    ToolParameter(
                        name="filter",
                        type="object",
                        description="Filter object (Notion format)",
                        required=False,
                    ),
                    ToolParameter(
                        name="sorts",
                        type="array",
                        description="Sort array (Notion format)",
                        required=False,
                    ),
                ],
            ),
            ToolDefinition(
                name="add_to_database",
                description="Add a new entry to a Notion database",
                parameters=[
                    ToolParameter(
                        name="database_id",
                        type="string",
                        description="Database ID",
                        required=True,
                    ),
                    ToolParameter(
                        name="properties",
                        type="object",
                        description="Properties object matching database schema",
                        required=True,
                    ),
                ],
            ),
        ]

    async def handle_tool_call(
        self, tool_name: str, arguments: dict[str, Any]
    ) -> dict[str, Any]:
        """Handle Notion tool calls"""

        if tool_name == "search_pages":
            return await self._search_pages(**arguments)
        elif tool_name == "get_page":
            return await self._get_page(**arguments)
        elif tool_name == "create_page":
            return await self._create_page(**arguments)
        elif tool_name == "update_page":
            return await self._update_page(**arguments)
        elif tool_name == "query_database":
            return await self._query_database(**arguments)
        elif tool_name == "add_to_database":
            return await self._add_to_database(**arguments)
        else:
            raise ValueError(f"Unknown tool: {tool_name}")

    async def _make_request(
        self, method: str, endpoint: str, data: Optional[dict[str, Any]] = None
    ) -> dict[str, Any]:
        """Make a request to Notion API"""
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method,
                f"{self.api_url}{endpoint}",
                headers=self.headers,
                json=data,
            )
            response.raise_for_status()
            return response.json()

    async def _search_pages(
        self, query: str, filter_type: Optional[str] = None
    ) -> dict[str, Any]:
        """Search Notion pages"""

        data = {
            "query": query,
            "sort": {"direction": "descending", "timestamp": "last_edited_time"},
        }

        if filter_type:
            data["filter"] = {"property": "object", "value": filter_type}

        result = await self._make_request("POST", "/search", data)

        # Process results
        pages = []
        for item in result.get("results", []):
            page_info = {
                "id": item["id"],
                "type": item["object"],
                "created_time": item["created_time"],
                "last_edited_time": item["last_edited_time"],
                "url": item.get("url", ""),
            }

            # Extract title
            if item["object"] == "page":
                props = item.get("properties", {})
                title_prop = props.get("title") or props.get("Name") or {}
                if title_prop.get("title"):
                    page_info["title"] = title_prop["title"][0].get("plain_text", "")
                elif title_prop.get("type") == "title":
                    page_info["title"] = title_prop.get("title", [{}])[0].get(
                        "plain_text", ""
                    )
                else:
                    page_info["title"] = "Untitled"
            elif item["object"] == "database":
                page_info["title"] = item.get("title", [{}])[0].get("plain_text", "")

            pages.append(page_info)

        return {
            "query": query,
            "count": len(pages),
            "results": pages,
        }

    async def _get_page(self, page_id: str) -> dict[str, Any]:
        """Get Notion page content"""

        # Get page metadata
        page = await self._make_request("GET", f"/pages/{page_id}")

        # Get page blocks (content)
        blocks = await self._make_request("GET", f"/blocks/{page_id}/children")

        # Process blocks into readable content
        content = []
        for block in blocks.get("results", []):
            block_text = self._extract_block_text(block)
            if block_text:
                content.append(block_text)

        # Extract title
        props = page.get("properties", {})
        title_prop = props.get("title") or props.get("Name") or {}
        if title_prop.get("title"):
            title = title_prop["title"][0].get("plain_text", "Untitled")
        else:
            title = "Untitled"

        return {
            "id": page_id,
            "title": title,
            "content": "\n\n".join(content),
            "created_time": page["created_time"],
            "last_edited_time": page["last_edited_time"],
            "url": page.get("url", ""),
        }

    def _extract_block_text(self, block: dict[str, Any]) -> str:
        """Extract text from a Notion block"""
        block_type = block["type"]
        block_data = block.get(block_type, {})

        # Handle different block types
        if block_type in ["paragraph", "heading_1", "heading_2", "heading_3"]:
            texts = block_data.get("rich_text", [])
            return "".join(t.get("plain_text", "") for t in texts)
        elif block_type == "bulleted_list_item":
            texts = block_data.get("rich_text", [])
            text_content = "".join(t.get("plain_text", "") for t in texts)
            return f"• {text_content}"
        elif block_type == "numbered_list_item":
            texts = block_data.get("rich_text", [])
            text_content = "".join(t.get("plain_text", "") for t in texts)
            return f"1. {text_content}"
        elif block_type == "code":
            texts = block_data.get("rich_text", [])
            code = "".join(t.get("plain_text", "") for t in texts)
            language = block_data.get("language", "")
            return f"```{language}\n{code}\n```"
        elif block_type == "divider":
            return "---"
        else:
            return ""

    async def _create_page(
        self, title: str, content: str, parent_page_id: Optional[str] = None
    ) -> dict[str, Any]:
        """Create a new Notion page"""

        # Prepare page data
        page_data = {"properties": {"title": {"title": [{"text": {"content": title}}]}}}

        # Set parent
        if parent_page_id:
            page_data["parent"] = {"page_id": parent_page_id}
        else:
            # Use workspace as parent if no parent specified
            page_data["parent"] = {"type": "workspace", "workspace": True}

        # Create page
        page = await self._make_request("POST", "/pages", page_data)

        # Add content as blocks
        blocks = self._markdown_to_blocks(content)
        if blocks:
            await self._make_request(
                "PATCH", f"/blocks/{page['id']}/children", {"children": blocks}
            )

        return {
            "id": page["id"],
            "title": title,
            "url": page.get("url", ""),
            "created": True,
        }

    def _markdown_to_blocks(self, markdown: str) -> list[dict[str, Any]]:
        """Convert markdown to Notion blocks (simplified)"""
        blocks = []
        lines = markdown.split("\n")

        for line in lines:
            if not line.strip():
                continue

            if line.startswith("# "):
                blocks.append(
                    {
                        "type": "heading_1",
                        "heading_1": {"rich_text": [{"text": {"content": line[2:]}}]},
                    }
                )
            elif line.startswith("## "):
                blocks.append(
                    {
                        "type": "heading_2",
                        "heading_2": {"rich_text": [{"text": {"content": line[3:]}}]},
                    }
                )
            elif line.startswith("- ") or line.startswith("* "):
                blocks.append(
                    {
                        "type": "bulleted_list_item",
                        "bulleted_list_item": {
                            "rich_text": [{"text": {"content": line[2:]}}]
                        },
                    }
                )
            else:
                blocks.append(
                    {
                        "type": "paragraph",
                        "paragraph": {"rich_text": [{"text": {"content": line}}]},
                    }
                )

        return blocks

    async def _update_page(self, page_id: str, content: str) -> dict[str, Any]:
        """Update an existing Notion page"""

        # First, delete existing blocks
        existing_blocks = await self._make_request("GET", f"/blocks/{page_id}/children")

        for block in existing_blocks.get("results", []):
            await self._make_request("DELETE", f"/blocks/{block['id']}")

        # Add new content
        blocks = self._markdown_to_blocks(content)
        if blocks:
            await self._make_request(
                "PATCH", f"/blocks/{page_id}/children", {"children": blocks}
            )

        return {
            "id": page_id,
            "updated": True,
        }

    async def _query_database(
        self,
        database_id: str,
        filter: Optional[dict[str, Any]] = None,
        sorts: Optional[list[dict[str, Any]]] = None,
    ) -> dict[str, Any]:
        """Query a Notion database"""

        data = {}
        if filter:
            data["filter"] = filter
        if sorts:
            data["sorts"] = sorts

        result = await self._make_request(
            "POST", f"/databases/{database_id}/query", data
        )

        # Process results
        entries = []
        for page in result.get("results", []):
            entry = {
                "id": page["id"],
                "created_time": page["created_time"],
                "last_edited_time": page["last_edited_time"],
                "properties": {},
            }

            # Extract properties
            for prop_name, prop_value in page.get("properties", {}).items():
                prop_type = prop_value["type"]

                if prop_type == "title":
                    entry["properties"][prop_name] = prop_value.get("title", [{}])[
                        0
                    ].get("plain_text", "")
                elif prop_type == "rich_text":
                    entry["properties"][prop_name] = prop_value.get("rich_text", [{}])[
                        0
                    ].get("plain_text", "")
                elif prop_type == "number":
                    entry["properties"][prop_name] = prop_value.get("number")
                elif prop_type == "select":
                    entry["properties"][prop_name] = prop_value.get("select", {}).get(
                        "name", ""
                    )
                elif prop_type == "multi_select":
                    entry["properties"][prop_name] = [
                        s["name"] for s in prop_value.get("multi_select", [])
                    ]
                elif prop_type == "checkbox":
                    entry["properties"][prop_name] = prop_value.get("checkbox", False)
                elif prop_type == "date":
                    entry["properties"][prop_name] = prop_value.get("date", {}).get(
                        "start", ""
                    )

            entries.append(entry)

        return {
            "database_id": database_id,
            "count": len(entries),
            "results": entries,
        }

    async def _add_to_database(
        self, database_id: str, properties: dict[str, Any]
    ) -> dict[str, Any]:
        """Add a new entry to a Notion database"""

        # Convert properties to Notion format
        notion_properties = {}
        for prop_name, prop_value in properties.items():
            if isinstance(prop_value, str):
                # Assume it's a title if it's the first property, otherwise rich_text
                if not notion_properties:
                    notion_properties[prop_name] = {
                        "title": [{"text": {"content": prop_value}}]
                    }
                else:
                    notion_properties[prop_name] = {
                        "rich_text": [{"text": {"content": prop_value}}]
                    }
            elif isinstance(prop_value, (int, float)):
                notion_properties[prop_name] = {"number": prop_value}
            elif isinstance(prop_value, bool):
                notion_properties[prop_name] = {"checkbox": prop_value}
            elif isinstance(prop_value, list):
                notion_properties[prop_name] = {
                    "multi_select": [{"name": v} for v in prop_value]
                }

        page_data = {
            "parent": {"database_id": database_id},
            "properties": notion_properties,
        }

        result = await self._make_request("POST", "/pages", page_data)

        return {
            "id": result["id"],
            "created": True,
            "url": result.get("url", ""),
        }


# Create and run server
if __name__ == "__main__":
    server = NotionMCPServer()
    server.run()
