"""
Notion Integration API Routes for Sophia AI
Provides endpoints for Notion knowledge base and strategic planning data via MCP server.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import aiohttp
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from backend.core.auto_esc_config import get_config_value

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/integrations/notion", tags=["notion"])

# Pydantic models for request/response
class NotionPageSummary(BaseModel):
    id: str
    title: str
    url: Optional[str] = None
    created_time: str
    last_edited_time: str
    created_by: Optional[str] = None
    last_edited_by: Optional[str] = None
    properties: Dict[str, Any] = {}
    content_preview: Optional[str] = None

class NotionDatabaseSummary(BaseModel):
    id: str
    title: str
    url: Optional[str] = None
    created_time: str
    last_edited_time: str
    properties: Dict[str, Any] = {}
    page_count: Optional[int] = None

class NotionStrategicContent(BaseModel):
    content_type: str
    pages: List[NotionPageSummary]
    summary: Dict[str, int]

class NotionIntegrationHealth(BaseModel):
    status: str
    last_sync: str
    api_health: bool
    total_pages: int
    total_databases: int
    sync_errors: List[str] = []

class NotionMCPClient:
    """Client for communicating with Notion MCP server."""
    
    def __init__(self):
        self.mcp_url = "http://notion-mcp:3007"
        self.timeout = 30
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool on the Notion MCP server."""
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                payload = {
                    "method": "tools/call",
                    "params": {
                        "name": tool_name,
                        "arguments": arguments
                    }
                }
                
                async with session.post(f"{self.mcp_url}/mcp", json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        # Parse the text content from MCP response
                        if "result" in result and "content" in result["result"]:
                            content = result["result"]["content"][0]["text"]
                            return json.loads(content)
                        return result
                    else:
                        error_text = await response.text()
                        raise Exception(f"MCP server error {response.status}: {error_text}")
        except Exception as e:
            logger.error(f"Error calling Notion MCP tool {tool_name}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Notion integration error: {str(e)}")

# Initialize MCP client
notion_client = NotionMCPClient()

@router.get("/health", response_model=NotionIntegrationHealth)
async def get_notion_health():
    """Get Notion integration health status."""
    try:
        # Test connection by searching pages
        search_result = await notion_client.call_tool("search_pages", {"page_size": 1})
        total_pages = len(search_result.get("results", []))
        
        # Test getting users for health check
        users_result = await notion_client.call_tool("get_users", {"page_size": 1})
        
        return NotionIntegrationHealth(
            status="healthy",
            last_sync=datetime.now().isoformat(),
            api_health=True,
            total_pages=total_pages,
            total_databases=0,  # Will be populated when we get database count
            sync_errors=[]
        )
    except Exception as e:
        logger.error(f"Notion health check failed: {str(e)}")
        return NotionIntegrationHealth(
            status="unhealthy",
            last_sync=datetime.now().isoformat(),
            api_health=False,
            total_pages=0,
            total_databases=0,
            sync_errors=[str(e)]
        )

@router.get("/search", response_model=List[NotionPageSummary])
async def search_pages(
    query: Optional[str] = Query(None, description="Search query text"),
    page_size: int = Query(50, description="Number of results to return")
):
    """Search for pages in Notion workspace."""
    try:
        arguments = {
            "page_size": min(page_size, 100)
        }
        
        if query:
            arguments["query"] = query
        
        result = await notion_client.call_tool("search_pages", arguments)
        
        pages = []
        for page in result.get("results", []):
            pages.append(_convert_to_page_summary(page))
        
        return pages
    except Exception as e:
        logger.error(f"Error searching Notion pages: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to search pages: {str(e)}")

@router.get("/pages/{page_id}")
async def get_page(page_id: str):
    """Get detailed information about a specific page."""
    try:
        result = await notion_client.call_tool("get_page", {"page_id": page_id})
        return result
    except Exception as e:
        logger.error(f"Error getting page {page_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get page: {str(e)}")

@router.get("/pages/{page_id}/content")
async def get_page_content(
    page_id: str,
    page_size: int = Query(100, description="Number of blocks to return")
):
    """Get the content blocks of a page."""
    try:
        result = await notion_client.call_tool("get_page_content", {
            "page_id": page_id,
            "page_size": min(page_size, 100)
        })
        return result
    except Exception as e:
        logger.error(f"Error getting content for page {page_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get page content: {str(e)}")

@router.get("/pages/{page_id}/analytics")
async def get_page_analytics(page_id: str):
    """Get analytics and metadata for a page."""
    try:
        result = await notion_client.call_tool("get_page_analytics", {"page_id": page_id})
        return result
    except Exception as e:
        logger.error(f"Error getting analytics for page {page_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get page analytics: {str(e)}")

@router.get("/databases/{database_id}")
async def get_database(database_id: str):
    """Get information about a database."""
    try:
        result = await notion_client.call_tool("get_database", {"database_id": database_id})
        return result
    except Exception as e:
        logger.error(f"Error getting database {database_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get database: {str(e)}")

@router.post("/databases/{database_id}/query")
async def query_database(
    database_id: str,
    filter_criteria: Optional[Dict] = None,
    sorts: Optional[List] = None,
    page_size: int = Query(100, description="Number of results to return")
):
    """Query a database with filters and sorting."""
    try:
        arguments = {
            "database_id": database_id,
            "page_size": min(page_size, 100)
        }
        
        if filter_criteria:
            arguments["filter"] = filter_criteria
        if sorts:
            arguments["sorts"] = sorts
        
        result = await notion_client.call_tool("query_database", arguments)
        return result
    except Exception as e:
        logger.error(f"Error querying database {database_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to query database: {str(e)}")

@router.get("/search/title/{title}", response_model=List[NotionPageSummary])
async def search_by_title(
    title: str,
    exact_match: bool = Query(False, description="Whether to match exact title")
):
    """Search pages by title text."""
    try:
        result = await notion_client.call_tool("search_by_title", {
            "title": title,
            "exact_match": exact_match
        })
        
        pages = []
        for page in result.get("results", []):
            pages.append(_convert_to_page_summary(page))
        
        return pages
    except Exception as e:
        logger.error(f"Error searching by title '{title}': {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to search by title: {str(e)}")

@router.get("/recent", response_model=List[NotionPageSummary])
async def get_recent_pages(
    days: int = Query(7, description="Number of days to look back"),
    page_size: int = Query(50, description="Number of pages to return")
):
    """Get recently edited pages."""
    try:
        result = await notion_client.call_tool("get_recent_pages", {
            "days": days,
            "page_size": min(page_size, 100)
        })
        
        pages = []
        for page in result.get("recent_pages", []):
            pages.append(_convert_to_page_summary(page))
        
        return pages
    except Exception as e:
        logger.error(f"Error getting recent pages: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get recent pages: {str(e)}")

@router.get("/strategic", response_model=NotionStrategicContent)
async def get_strategic_content(
    content_type: Optional[str] = Query(None, description="Type of strategic content", enum=["okr", "strategy", "planning", "goals", "metrics"]),
    quarter: Optional[str] = Query(None, description="Quarter to filter by (e.g., 'Q3 2024')")
):
    """Search for strategic planning and OKR-related content."""
    try:
        arguments = {}
        if content_type:
            arguments["content_type"] = content_type
        if quarter:
            arguments["quarter"] = quarter
        
        result = await notion_client.call_tool("search_strategic_content", arguments)
        
        # Convert categorized results to page summaries
        categorized = result.get("categorized_results", {})
        all_pages = []
        
        for category, pages in categorized.items():
            for page in pages:
                all_pages.append(_convert_to_page_summary(page))
        
        return NotionStrategicContent(
            content_type=content_type or "all",
            pages=all_pages,
            summary=result.get("summary", {})
        )
    except Exception as e:
        logger.error(f"Error getting strategic content: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get strategic content: {str(e)}")

@router.get("/users")
async def get_users(page_size: int = Query(100, description="Number of users to return")):
    """Get workspace users."""
    try:
        result = await notion_client.call_tool("get_users", {
            "page_size": min(page_size, 100)
        })
        return result
    except Exception as e:
        logger.error(f"Error getting users: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get users: {str(e)}")

@router.get("/users/{user_id}")
async def get_user(user_id: str):
    """Get information about a specific user."""
    try:
        result = await notion_client.call_tool("get_user", {"user_id": user_id})
        return result
    except Exception as e:
        logger.error(f"Error getting user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get user: {str(e)}")

@router.get("/dashboard/summary")
async def get_dashboard_summary():
    """Get summary data for executive dashboard."""
    try:
        # Get recent pages
        recent_result = await notion_client.call_tool("get_recent_pages", {"days": 30, "page_size": 100})
        recent_pages = recent_result.get("recent_pages", [])
        
        # Get strategic content summary
        strategic_result = await notion_client.call_tool("search_strategic_content", {})
        strategic_summary = strategic_result.get("summary", {})
        
        # Calculate activity metrics
        last_week = (datetime.now() - timedelta(days=7)).isoformat()
        recent_activity = len([
            page for page in recent_pages 
            if page.get("last_edited_time", "") >= last_week
        ])
        
        # Extract project-related pages
        project_pages = []
        for page in recent_pages:
            title = _extract_title(page).lower()
            properties = page.get("extracted_properties", {})
            
            if any(keyword in title for keyword in ["project", "initiative", "roadmap", "plan"]):
                project_pages.append({
                    "id": page["id"],
                    "title": _extract_title(page),
                    "last_edited": page.get("last_edited_time"),
                    "properties": properties
                })
        
        return {
            "total_pages": len(recent_pages),
            "recent_activity": recent_activity,
            "strategic_content": strategic_summary,
            "project_pages": len(project_pages),
            "top_project_pages": project_pages[:5],
            "content_categories": {
                "okr_pages": strategic_summary.get("okr_pages", 0),
                "strategy_pages": strategic_summary.get("strategy_pages", 0),
                "planning_pages": strategic_summary.get("planning_pages", 0)
            },
            "sync_time": datetime.now().isoformat(),
            "health_status": "healthy"
        }
    except Exception as e:
        logger.error(f"Error getting dashboard summary: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard summary: {str(e)}")

# Helper functions
def _convert_to_page_summary(page: Dict[str, Any]) -> NotionPageSummary:
    """Convert Notion page data to summary model."""
    return NotionPageSummary(
        id=page["id"],
        title=_extract_title(page),
        url=page.get("url"),
        created_time=page.get("created_time", ""),
        last_edited_time=page.get("last_edited_time", ""),
        created_by=page.get("created_by", {}).get("id") if page.get("created_by") else None,
        last_edited_by=page.get("last_edited_by", {}).get("id") if page.get("last_edited_by") else None,
        properties=page.get("extracted_properties", {}),
        content_preview=page.get("content_preview")
    )

def _extract_title(page: Dict[str, Any]) -> str:
    """Extract title from page object."""
    # Try extracted title first
    if "extracted_title" in page:
        return page["extracted_title"]
    
    # Try properties for database pages
    if "properties" in page:
        for prop_name, prop_data in page["properties"].items():
            if prop_data.get("type") == "title":
                title_blocks = prop_data.get("title", [])
                if title_blocks:
                    return "".join(block.get("plain_text", "") for block in title_blocks)
    
    # Try title field for regular pages
    if "title" in page:
        title_blocks = page["title"]
        if title_blocks:
            return "".join(block.get("plain_text", "") for block in title_blocks)
    
    return "Untitled" 