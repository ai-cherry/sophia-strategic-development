"""Agno Router
FastAPI router for Agno integration endpoints
"""

import json
import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from backend.integrations.agno_integration import agno_integration
from backend.mcp.agno_bridge import MCPToAgnoBridge
from backend.mcp.mcp_client import MCPClient

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/agno", tags=["agno"])


# Models
class AgentRequest(BaseModel):
    """Request to create an agent."""

    agent_id: str = Field(..., description="The unique identifier for this agent")
    instructions: Optional[List[str]] = Field(
        None, description="The instructions for the agent"
    )
    model: Optional[str] = Field(None, description="The model to use for this agent")


class ProcessRequest(BaseModel):
    """Request to process a request with an agent."""

    agent_id: str = Field(..., description="The unique identifier for the agent")
    request: str = Field(..., description="The request to process")
    stream: bool = Field(False, description="Whether to stream the response")
    use_mcp_tools: bool = Field(True, description="Whether to use MCP tools")


class ToolRequest(BaseModel):
    """Request to register a tool."""

    name: str = Field(..., description="The name of the tool")
    description: str = Field(..., description="The description of the tool")
    parameters: Dict[str, Any] = Field(..., description="The parameters for the tool")


# Dependencies
async def get_mcp_client():
    """Get an initialized MCP client."""
    client = MCPClient()
    await client.initialize()
    return client


async def get_agno_bridge(mcp_client: MCPClient = Depends(get_mcp_client)):
    """Get an initialized Agno bridge."""
    bridge = MCPToAgnoBridge(mcp_client)
    return bridge


# Routes
@router.get("/health")
async def health_check():
    """Health check endpoint for Agno integration.

    Returns:
        Dict[str, Any]: The health check result
    """
    try:
        # Initialize Agno integration if needed
        if not agno_integration.initialized:
            await agno_integration.initialize()

        # Get pool stats
        stats = agno_integration.get_pool_stats()

        # Return health check result
        return {
            "status": "healthy",
            "integration_initialized": agno_integration.initialized,
            "agent_count": stats["pool_size"],
            "max_agent_count": stats["max_pool_size"],
            "default_model": agno_integration.default_model,
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")


@router.post("/agents")
async def create_agent(request: AgentRequest):
    """Create a new agent in the Agno platform.

    Args:
        request: The request to create an agent

    Returns:
        Dict[str, Any]: The created agent
    """
    try:
        # Initialize Agno integration if needed
        if not agno_integration.initialized:
            await agno_integration.initialize()

        # Create agent
        agent = await agno_integration.get_agent(
            agent_id=request.agent_id,
            instructions=request.instructions,
            model=request.model,
        )

        # Return agent data
        return {
            "success": True,
            "agent_id": agent.agent_id,
            "created_at": agent.created_at,
            "model": agent.agent_data.get("model", "unknown"),
        }
    except Exception as e:
        logger.error(f"Failed to create agent {request.agent_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create agent: {str(e)}")


@router.post("/process")
async def process_request(
    request: ProcessRequest, bridge: MCPToAgnoBridge = Depends(get_agno_bridge)
):
    """Process a request with an agent.

    Args:
        request: The request to process
        bridge: The Agno bridge

    Returns:
        Dict[str, Any]: The response
    """
    try:
        # Initialize Agno integration if needed
        if not agno_integration.initialized:
            await agno_integration.initialize()

        # Get MCP tools if requested
        tools = None
        if request.use_mcp_tools:
            tools = await bridge.convert_all_mcp_tools()

        # Process request
        if request.stream:
            # For streaming, we need to return a StreamingResponse
            async def stream_generator():
                async for chunk in agno_integration.process_request(
                    agent_id=request.agent_id,
                    request=request.request,
                    tools=tools,
                    stream=True,
                ):
                    # Convert chunk to JSON and yield
                    yield json.dumps(chunk) + "\n"

            return StreamingResponse(
                stream_generator(), media_type="application/x-ndjson"
            )
        else:
            # For non-streaming, we get a single response
            response = await agno_integration.process_request(
                agent_id=request.agent_id,
                request=request.request,
                tools=tools,
                stream=False,
            )

            # Return response
            return {"success": True, "agent_id": request.agent_id, "response": response}
    except Exception as e:
        logger.error(f"Failed to process request for agent {request.agent_id}: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to process request: {str(e)}"
        )


@router.get("/stats")
async def get_pool_stats():
    """Get statistics about the agent pool.

    Returns:
        Dict[str, Any]: Statistics about the agent pool
    """
    try:
        # Initialize Agno integration if needed
        if not agno_integration.initialized:
            await agno_integration.initialize()

        # Get pool stats
        stats = agno_integration.get_pool_stats()

        # Return stats
        return {"success": True, "stats": stats}
    except Exception as e:
        logger.error(f"Failed to get pool stats: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get pool stats: {str(e)}"
        )


@router.post("/tools")
async def register_tool(request: ToolRequest):
    """Register a new tool for Agno agents.

    Args:
        request: The request to register a tool

    Returns:
        Dict[str, Any]: The result of the registration
    """
    try:
        # This is a placeholder for registering custom tools
        # In a real implementation, we would register the tool with Agno

        # Return success
        return {
            "success": True,
            "name": request.name,
            "description": request.description,
            "parameters": request.parameters,
        }
    except Exception as e:
        logger.error(f"Failed to register tool {request.name}: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to register tool: {str(e)}"
        )


@router.get("/bridge/stats")
async def get_bridge_stats(bridge: MCPToAgnoBridge = Depends(get_agno_bridge)):
    """Get statistics about the Agno bridge.

    Args:
        bridge: The Agno bridge

    Returns:
        Dict[str, Any]: Statistics about the bridge
    """
    try:
        # Get bridge stats
        stats = bridge.get_cache_stats()

        # Return stats
        return {"success": True, "stats": stats}
    except Exception as e:
        logger.error(f"Failed to get bridge stats: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get bridge stats: {str(e)}"
        )


@router.post("/bridge/clear-cache")
async def clear_bridge_cache(bridge: MCPToAgnoBridge = Depends(get_agno_bridge)):
    """Clear the Agno bridge cache.

    Args:
        bridge: The Agno bridge

    Returns:
        Dict[str, Any]: The result of the operation
    """
    try:
        # Clear cache
        bridge.clear_cache()

        # Return success
        return {"success": True, "message": "Cache cleared successfully"}
    except Exception as e:
        logger.error(f"Failed to clear bridge cache: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to clear bridge cache: {str(e)}"
        )
