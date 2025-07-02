import asyncio
import logging
import uvicorn
import httpx
from fastapi import FastAPI, HTTPException, Request
import sys
from pathlib import Path

# Add backend to path to enable imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.mcp_servers.server.fastmcp import FastMCP

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- MCP Server Definition ---
# This is what Cursor will connect to.
mcp = FastMCP(
    "n8n_gateway",
    "N8N Orchestration Gateway",
    "The central MCP gateway powered by N8N workflows.",
)

# --- N8N Configuration ---
N8N_BASE_URL = "http://localhost:5678" # Default N8N port
CODACY_WORKFLOW_URL = f"{N8N_BASE_URL}/webhook/codacy-mcp-tool"
AI_MEMORY_STORE_URL = f"{N8N_BASE_URL}/webhook/ai-memory-store"
AI_MEMORY_RECALL_URL = f"{N8N_BASE_URL}/webhook/ai-memory-recall"


@mcp.tool()
async def analyze_code(code: str, filename: str = "snippet.py") -> dict:
    """
    Analyzes a snippet of code for quality, security, and complexity.
    This tool is powered by a Codacy analysis workflow in N8N.
    """
    logger.info(f"Gateway: Received request to analyze code for {filename}")
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            payload = {"code": code, "filename": filename}
            response = await client.post(CODACY_WORKFLOW_URL, json=payload)
            
            response.raise_for_status()
            
            result = response.json()
            # The N8N HTTP Request node puts the result in a 'data' key
            # We return the content of that key
            final_result = result.get('data', result)
            logger.info(f"Gateway: Received successful response from N8N for {filename}")
            return final_result

    except httpx.HTTPStatusError as e:
        error_text = e.response.text
        logger.error(f"HTTP error calling N8N workflow: {e.response.status_code} - {error_text}")
        return {"error": "N8N workflow execution failed", "status_code": e.response.status_code, "details": error_text}
    except Exception as e:
        logger.error(f"An unexpected error occurred in the gateway: {e}")
        return {"error": "Internal gateway error", "details": str(e)}


@mcp.tool()
async def store_memory(content: str, category: str = "general", tags: list = [], importance_score: float = 0.5) -> dict:
    """
    Stores a memory (a piece of text) for later recall.
    This tool is powered by an AI Memory workflow in N8N.
    """
    logger.info(f"Gateway: Received request to store memory in category '{category}'")
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            payload = {
                "content": content,
                "category": category,
                "tags": tags,
                "importance_score": importance_score
            }
            response = await client.post(AI_MEMORY_STORE_URL, json=payload)
            response.raise_for_status()
            result = response.json()
            final_result = result.get('data', result)
            logger.info(f"Gateway: Successfully stored memory.")
            return final_result

    except httpx.HTTPStatusError as e:
        error_text = e.response.text
        logger.error(f"HTTP error calling AI Memory Store workflow: {e.response.status_code} - {error_text}")
        return {"error": "N8N workflow execution failed", "status_code": e.response.status_code, "details": error_text}
    except Exception as e:
        logger.error(f"An unexpected error occurred in the gateway: {e}")
        return {"error": "Internal gateway error", "details": str(e)}


@mcp.tool()
async def recall_memory(query: str, category: str = None, limit: int = 5) -> dict:
    """
    Recalls memories that match a specific query.
    This tool is powered by an AI Memory workflow in N8N.
    """
    logger.info(f"Gateway: Received request to recall memories with query '{query}'")
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            payload = {
                "query": query,
                "category": category,
                "limit": limit
            }
            response = await client.post(AI_MEMORY_RECALL_URL, json=payload)
            response.raise_for_status()
            result = response.json()
            final_result = result.get('data', result)
            logger.info(f"Gateway: Successfully recalled {len(final_result.get('results', []))} memories.")
            return final_result

    except httpx.HTTPStatusError as e:
        error_text = e.response.text
        logger.error(f"HTTP error calling AI Memory Recall workflow: {e.response.status_code} - {error_text}")
        return {"error": "N8N workflow execution failed", "status_code": e.response.status_code, "details": error_text}
    except Exception as e:
        logger.error(f"An unexpected error occurred in the gateway: {e}")
        return {"error": "Internal gateway error", "details": str(e)}


# --- FastAPI App for Health Check ---
# This allows us to monitor the gateway itself.
app = FastAPI(title="N8N MCP Gateway", version="1.0.0")

@app.get("/health")
async def health_check():
    """Provides a simple health check endpoint for the gateway."""
    return {"status": "healthy", "name": "N8N MCP Gateway"}

@app.get("/mcp-tools")
async def list_mcp_tools():
    """Lists the tools exposed by this MCP gateway."""
    return {"tools": [
        {"name": tool.name, "description": tool.description} 
        for tool in mcp.tools.values()
    ]}


# --- Main execution logic ---
async def main():
    """Starts the MCP server and the health check API."""
    logger.info("🚀 Starting the N8N MCP Gateway...")

    # Configure and run the Uvicorn server for the health check API
    config = uvicorn.Config(app, host="0.0.0.0", port=8100, log_level="info")
    server = uvicorn.Server(config)
    
    # Run the health check server in the background
    asyncio.create_task(server.serve())
    logger.info("✅ Health check API running on http://localhost:8100")
    
    # Run the MCP server in the foreground
    # This is the primary function that listens for Cursor AI
    logger.info("🤖 MCP Gateway listening for AI tool requests...")
    await mcp.run_async()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Gateway shutting down.")
