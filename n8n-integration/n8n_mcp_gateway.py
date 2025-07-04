import asyncio
import logging
import sys
from pathlib import Path

import httpx
import uvicorn
from fastapi import FastAPI

# Add backend to path to enable imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.mcp_servers.server.fastmcp import FastMCP

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- MCP Server Definition ---
mcp = FastMCP(
    "n8n_gateway",
    "N8N Orchestration Gateway",
    "The central MCP gateway powered by N8N workflows.",
)

# --- N8N Configuration ---
N8N_BASE_URL = "http://localhost:5678"
CODACY_WORKFLOW_URL = f"{N8N_BASE_URL}/webhook/codacy-mcp-tool"
AI_MEMORY_STORE_URL = f"{N8N_BASE_URL}/webhook/ai-memory-store"
AI_MEMORY_RECALL_URL = f"{N8N_BASE_URL}/webhook/ai-memory-recall"
SNOWFLAKE_QUERY_URL = f"{N8N_BASE_URL}/webhook/snowflake-query"
LINEAR_CREATE_ISSUE_URL = f"{N8N_BASE_URL}/webhook/linear-create-issue"
ASANA_CREATE_TASK_URL = f"{N8N_BASE_URL}/webhook/asana-create-task"
NOTION_CREATE_PAGE_URL = f"{N8N_BASE_URL}/webhook/notion-create-page"
SLACK_POST_MESSAGE_URL = f"{N8N_BASE_URL}/webhook/slack-post-message"
RECOMMEND_PATTERN_URL = f"{N8N_BASE_URL}/webhook/recommend-pattern"
SUBMIT_TRAINING_DATA_URL = f"{N8N_BASE_URL}/webhook/submit-training-data"


# --- Tool Definitions ---


@mcp.tool()
async def analyze_code(code: str, filename: str = "snippet.py") -> dict:
    """Analyzes a snippet of code for quality, security, and complexity."""
    logger.info(f"Gateway: Analyzing code for {filename}")
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                CODACY_WORKFLOW_URL, json={"code": code, "filename": filename}
            )
            response.raise_for_status()
            return response.json().get("data", {})
    except Exception as e:
        logger.error(f"Error in analyze_code: {e}")
        return {"error": str(e)}


@mcp.tool()
async def store_memory(
    content: str,
    category: str = "general",
    tags: list = [],
    importance_score: float = 0.5,
) -> dict:
    """Stores a memory (a piece of text) for later recall."""
    logger.info(f"Gateway: Storing memory in category '{category}'")
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            payload = {
                "content": content,
                "category": category,
                "tags": tags,
                "importance_score": importance_score,
            }
            response = await client.post(AI_MEMORY_STORE_URL, json=payload)
            response.raise_for_status()
            return response.json().get("data", {})
    except Exception as e:
        logger.error(f"Error in store_memory: {e}")
        return {"error": str(e)}


@mcp.tool()
async def recall_memory(query: str, category: str = None, limit: int = 5) -> dict:
    """Recalls memories that match a specific query."""
    logger.info(f"Gateway: Recalling memories with query '{query}'")
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            payload = {"query": query, "category": category, "limit": limit}
            response = await client.post(AI_MEMORY_RECALL_URL, json=payload)
            response.raise_for_status()
            return response.json().get("data", {})
    except Exception as e:
        logger.error(f"Error in recall_memory: {e}")
        return {"error": str(e)}


@mcp.tool()
async def execute_snowflake_query(query: str) -> dict:
    """Executes a SQL query against the Snowflake data warehouse."""
    logger.info("Gateway: Executing Snowflake query.")
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(SNOWFLAKE_QUERY_URL, json={"query": query})
            response.raise_for_status()
            result = response.json().get("data", [])
            return {"status": "success", "row_count": len(result), "results": result}
    except Exception as e:
        logger.error(f"Error in execute_snowflake_query: {e}")
        return {"error": str(e)}


@mcp.tool()
async def create_linear_issue(title: str, description: str, teamId: str) -> dict:
    """Creates a new issue in Linear."""
    logger.info(f"Gateway: Creating Linear issue '{title}'")
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            payload = {"title": title, "description": description, "teamId": teamId}
            response = await client.post(LINEAR_CREATE_ISSUE_URL, json=payload)
            response.raise_for_status()
            return response.json().get("data", {})
    except Exception as e:
        logger.error(f"Error in create_linear_issue: {e}")
        return {"error": str(e)}


@mcp.tool()
async def create_asana_task(
    name: str, notes: str, workspaceId: str, projectId: str
) -> dict:
    """Creates a new task in Asana."""
    logger.info(f"Gateway: Creating Asana task '{name}'")
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            payload = {
                "name": name,
                "notes": notes,
                "workspaceId": workspaceId,
                "projectId": projectId,
            }
            response = await client.post(ASANA_CREATE_TASK_URL, json=payload)
            response.raise_for_status()
            return response.json().get("data", {})
    except Exception as e:
        logger.error(f"Error in create_asana_task: {e}")
        return {"error": str(e)}


@mcp.tool()
async def create_notion_page(databaseId: str, title: str, content: str) -> dict:
    """Creates a new page in a Notion database."""
    logger.info(f"Gateway: Creating Notion page '{title}'")
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            payload = {"databaseId": databaseId, "title": title, "content": content}
            response = await client.post(NOTION_CREATE_PAGE_URL, json=payload)
            response.raise_for_status()
            return response.json().get("data", {})
    except Exception as e:
        logger.error(f"Error in create_notion_page: {e}")
        return {"error": str(e)}


@mcp.tool()
async def post_slack_message(channel: str, text: str) -> dict:
    """Posts a message to a Slack channel."""
    logger.info(f"Gateway: Posting to Slack channel '{channel}'")
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            payload = {"channel": channel, "text": text}
            response = await client.post(SLACK_POST_MESSAGE_URL, json=payload)
            response.raise_for_status()
            return response.json().get("data", {})
    except Exception as e:
        logger.error(f"Error in post_slack_message: {e}")
        return {"error": str(e)}


@mcp.tool()
async def recommend_repository_pattern(query: str) -> dict:
    """Recommends a repository from the external collection based on a query."""
    logger.info(
        f"Gateway: Received request for repository pattern recommendation with query '{query}'"
    )
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            payload = {"query": query}
            response = await client.post(RECOMMEND_PATTERN_URL, json=payload)
            response.raise_for_status()
            result = response.json().get("data", [])
            return {
                "status": "success",
                "recommendation_count": len(result),
                "recommendations": result,
            }
    except Exception as e:
        logger.error(f"Error in recommend_repository_pattern: {e}")
        return {"error": str(e)}


@mcp.tool()
async def submit_training_data(user_id: str, topic: str, content: str) -> dict:
    """Submits an authoritative piece of knowledge to the AI's memory."""
    logger.info(
        f"Gateway: Received request to submit training data for topic '{topic}' from user '{user_id}'"
    )
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            payload = {"user_id": user_id, "topic": topic, "content": content}
            response = await client.post(SUBMIT_TRAINING_DATA_URL, json=payload)
            response.raise_for_status()
            return response.json().get("data", {})
    except Exception as e:
        logger.error(f"Error in submit_training_data: {e}")
        return {"error": str(e)}


# --- FastAPI App for Health Check ---
app = FastAPI(title="N8N MCP Gateway", version="1.0.0")


@app.get("/health")
async def health_check():
    return {"status": "healthy", "name": "N8N MCP Gateway"}


@app.get("/mcp-tools")
async def list_mcp_tools():
    return {
        "tools": [
            {"name": tool.name, "description": tool.description}
            for tool in mcp.tools.values()
        ]
    }


# --- Main execution logic ---
async def main():
    """Starts the MCP server and the health check API."""
    logger.info("🚀 Starting the N8N MCP Gateway...")
    config = uvicorn.Config(app, host="0.0.0.0", port=8100, log_level="info")
    server = uvicorn.Server(config)

    # Run the health check server in the background
    asyncio.create_task(server.serve())
    logger.info("✅ Health check API running on http://localhost:8100")

    # Run the MCP server in the foreground
    logger.info("🤖 MCP Gateway listening for AI tool requests...")
    await mcp.run_async()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Gateway shutting down.")
