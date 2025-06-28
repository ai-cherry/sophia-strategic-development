from typing import Any

"""
Snowflake Cortex API Routes for Sophia AI
RESTful endpoints and WebSocket support for Cortex agents
"""

from fastapi import APIRouter, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, List, Optional
import logging
from datetime import datetime

from backend.services.cortex_agent_service import (
    get_cortex_agent_service,
    CortexAgentService,
    AgentRequest,
)

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/cortex", tags=["cortex-agents"])

# Security
security = HTTPBearer()


async def verify_jwt_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    """Verify JWT token from Authorization header"""
    return credentials.credentials


@router.get("/agents")
async def list_agents(
    cortex_service: CortexAgentService = Depends(get_cortex_agent_service),
) -> Dict[str, List[Dict]]:
    """
    List all available Cortex agents

    Returns detailed information about each agent including:
    - Name and model
    - Available tools
    - JWT requirements
    """
    try:
        agents = await cortex_service.list_agents()

        return {
            "agents": agents,
            "count": len(agents),
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Failed to list agents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agents/{agent_name}")
async def get_agent_details(
    agent_name: str,
    cortex_service: CortexAgentService = Depends(get_cortex_agent_service),
) -> Dict[str, Any]:
    """Get detailed information about a specific agent"""
    try:
        agents = await cortex_service.list_agents()
        agent = next((a for a in agents if a["name"] == agent_name), None)

        if not agent:
            raise HTTPException(
                status_code=404, detail=f"Agent '{agent_name}' not found"
            )

        return {"agent": agent, "timestamp": datetime.now().isoformat()}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get agent details: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/agents/{agent_name}/invoke")
async def invoke_agent(
    agent_name: str,
    request: AgentRequest,
    jwt_token: Optional[str] = None,
    cortex_service: CortexAgentService = Depends(get_cortex_agent_service),
) -> Dict[str, Any]:
    """
    Invoke a Cortex agent with optional JWT authentication

    Parameters:
    - agent_name: Name of the agent to invoke
    - request: Agent request with prompt and optional context/tools
    - jwt_token: Optional JWT token for authenticated agents

    Returns:
    - Agent response with generated text and metadata
    """
    try:
        # Check if JWT is provided in header
        if not jwt_token:
            # Try to get from Authorization header
            try:
                credentials = await verify_jwt_token()
                jwt_token = credentials
            except:
                # JWT not provided, will fail if agent requires it
                pass

        # Invoke the agent
        response = await cortex_service.invoke_agent(
            agent_name=agent_name, request=request, jwt_token=jwt_token
        )

        return {
            "success": True,
            "agent_name": response.agent_name,
            "response": response.response,
            "tools_used": response.tools_used,
            "tokens_used": response.tokens_used,
            "execution_time": response.execution_time,
            "metadata": response.metadata,
            "timestamp": datetime.now().isoformat(),
        }

    except ValueError as e:
        # Handle specific errors (agent not found, JWT required, etc.)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to invoke agent {agent_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/agents/{agent_name}/tools/{tool_name}")
async def execute_agent_tool(
    agent_name: str,
    tool_name: str,
    parameters: Dict[str, Any],
    jwt_token: Optional[str] = None,
    cortex_service: CortexAgentService = Depends(get_cortex_agent_service),
) -> Dict[str, Any]:
    """
    Execute a specific tool for an agent

    This endpoint allows direct tool execution without going through
    the full agent conversation flow.
    """
    try:
        # Create a request that specifically asks for the tool
        tool_request = AgentRequest(
            prompt=f"Execute tool: {tool_name}", tools=[tool_name], context=parameters
        )

        # Invoke agent with tool request
        response = await cortex_service.invoke_agent(
            agent_name=agent_name, request=tool_request, jwt_token=jwt_token
        )

        # Extract tool results from metadata
        tool_results = response.metadata.get("tool_results", {})

        return {
            "success": True,
            "agent_name": agent_name,
            "tool_name": tool_name,
            "result": tool_results.get(tool_name, "Tool execution completed"),
            "execution_time": response.execution_time,
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Failed to execute tool {tool_name} for agent {agent_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.websocket("/agents/{agent_name}/stream")
async def stream_agent_response(
    websocket: WebSocket,
    agent_name: str,
    cortex_service: CortexAgentService = Depends(get_cortex_agent_service),
):
    """
    WebSocket endpoint for streaming agent responses

    Allows real-time streaming of agent responses for better UX
    with long-running generations.

    Protocol:
    1. Client connects to WebSocket
    2. Client sends request JSON with prompt and optional JWT
    3. Server streams response chunks
    4. Server sends final message with done=true
    """
    await websocket.accept()

    try:
        # Wait for initial request
        request_data = await websocket.receive_json()

        # Parse request
        agent_request = AgentRequest(
            prompt=request_data.get("prompt", ""),
            context=request_data.get("context"),
            tools=request_data.get("tools"),
            temperature=request_data.get("temperature"),
            max_tokens=request_data.get("max_tokens"),
            stream=True,
        )

        jwt_token = request_data.get("jwt_token")

        # Stream response
        async for chunk in cortex_service.handle_stream(
            websocket=websocket,
            agent_name=agent_name,
            request=agent_request,
            jwt_token=jwt_token,
        ):
            await websocket.send_text(chunk)

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for agent {agent_name}")
    except Exception as e:
        logger.error(f"WebSocket error for agent {agent_name}: {e}")
        await websocket.send_json({"error": str(e), "done": True})
    finally:
        await websocket.close()


@router.post("/agents/{agent_name}/generate-token")
async def generate_agent_token(
    agent_name: str,
    user_id: str,
    cortex_service: CortexAgentService = Depends(get_cortex_agent_service),
) -> Dict[str, str]:
    """
    Generate a JWT token for accessing a specific agent

    This endpoint should be protected and only accessible
    to authenticated users with appropriate permissions.
    """
    try:
        # In production, verify user permissions here
        # For now, generate token for any valid request

        token = cortex_service.generate_jwt(user_id, agent_name)

        return {
            "token": token,
            "agent_name": agent_name,
            "user_id": user_id,
            "expires_in_hours": 24,
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Failed to generate token: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def cortex_health_check(
    cortex_service: CortexAgentService = Depends(get_cortex_agent_service),
) -> Dict[str, Any]:
    """Check health of Cortex agent service"""
    try:
        # Check if we can list agents
        agents = await cortex_service.list_agents()

        # Check Snowflake connection
        snowflake_connected = cortex_service.snowflake_conn is not None

        return {
            "status": "healthy" if snowflake_connected else "degraded",
            "agents_available": len(agents),
            "snowflake_connected": snowflake_connected,
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
        }


# Example usage endpoints for specific business scenarios


@router.post("/analyze-gong-call")
async def analyze_gong_call(
    call_id: str,
    analysis_type: str = "summary",
    cortex_service: CortexAgentService = Depends(get_cortex_agent_service),
) -> Dict[str, Any]:
    """
    Analyze a Gong call using the business intelligence agent

    This is a convenience endpoint that wraps the agent invocation
    for a common use case.
    """
    try:
        # Prepare the analysis request
        prompt = f"""Analyze Gong call {call_id} and provide a {analysis_type}.
        
        Focus on:
        - Key discussion points
        - Action items
        - Customer sentiment
        - Next steps
        """

        request = AgentRequest(
            prompt=prompt,
            context={
                "call_id": call_id,
                "source": "gong",
                "analysis_type": analysis_type,
            },
            tools=["analyze_metrics", "generate_insights"],
        )

        # Use business intelligence agent
        response = await cortex_service.invoke_agent(
            agent_name="business_intelligence", request=request
        )

        return {
            "call_id": call_id,
            "analysis_type": analysis_type,
            "analysis": response.response,
            "insights": response.metadata.get("tool_results", {}).get(
                "generate_insights", {}
            ),
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Failed to analyze Gong call: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search-knowledge")
async def search_knowledge_base(
    query: str,
    limit: int = 10,
    filters: Optional[Dict[str, Any]] = None,
    cortex_service: CortexAgentService = Depends(get_cortex_agent_service),
) -> Dict[str, Any]:
    """
    Search the knowledge base using semantic memory agent

    Convenience endpoint for semantic search across all stored data.
    """
    try:
        request = AgentRequest(
            prompt=f"Search for: {query}",
            context={"limit": limit, "filters": filters or {}},
            tools=["recall_memory", "search_context"],
        )

        # Use semantic memory agent
        response = await cortex_service.invoke_agent(
            agent_name="semantic_memory", request=request
        )

        # Extract search results
        tool_results = response.metadata.get("tool_results", {})
        memories = tool_results.get("recall_memory", {}).get("memories", [])

        return {
            "query": query,
            "results": memories[:limit],
            "count": len(memories),
            "execution_time": response.execution_time,
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Failed to search knowledge base: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/optimize-sql")
async def optimize_sql_query(
    query: str,
    warehouse: str = "COMPUTE_WH",
    cortex_service: CortexAgentService = Depends(get_cortex_agent_service),
) -> Dict[str, Any]:
    """
    Optimize a SQL query using the Snowflake operations agent

    Returns optimization suggestions and potentially rewritten query.
    """
    try:
        request = AgentRequest(
            prompt=f"Optimize this SQL query: {query}",
            context={"warehouse": warehouse},
            tools=["optimize_query"],
        )

        # Use Snowflake ops agent
        response = await cortex_service.invoke_agent(
            agent_name="snowflake_ops", request=request
        )

        return {
            "original_query": query,
            "optimization_suggestions": response.response,
            "warehouse": warehouse,
            "execution_time": response.execution_time,
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Failed to optimize SQL query: {e}")
        raise HTTPException(status_code=500, detail=str(e))
