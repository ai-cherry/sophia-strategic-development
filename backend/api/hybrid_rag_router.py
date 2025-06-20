"""Enhanced FastAPI Router for Hybrid RAG with AG-UI Protocol
Provides REST and WebSocket endpoints for the complete hybrid RAG system
"""

import asyncio
import json
import logging
import time
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from backend.api.agui_protocol import EventType, agui_protocol
from backend.core.hybrid_rag_router import hybrid_rag_router
from backend.integrations.enhanced_agno_integration import enhanced_agno_integration
from backend.mcp.enhanced_mcp_federation import mcp_federation

logger = logging.getLogger(__name__)


# Pydantic models for request/response
class QueryRequest(BaseModel):
    """Request model for hybrid RAG queries."""

    query: str = Field(..., description="The query string")
    context: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Additional context"
    )
    stream: bool = Field(default=False, description="Whether to stream the response")
    user_id: Optional[str] = Field(None, description="User ID for personalization")


class QueryResponse(BaseModel):
    """Response model for hybrid RAG queries."""

    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    routing_metadata: Optional[Dict[str, Any]] = None
    execution_time_ms: float
    session_id: Optional[str] = None


class AgentPoolRequest(BaseModel):
    """Request model for agent pool operations."""

    pool_name: str = Field(..., description="Name of the agent pool")
    instructions: Optional[List[str]] = Field(None, description="Agent instructions")
    model: Optional[str] = Field(None, description="Model to use")


class AgentRequest(BaseModel):
    """Request model for agent operations."""

    request: str = Field(..., description="Request to process")
    pool_name: str = Field(default="general_assistant", description="Agent pool to use")
    stream: bool = Field(default=False, description="Whether to stream the response")
    context: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Additional context"
    )


class MCPQueryRequest(BaseModel):
    """Request model for MCP federation queries."""

    query: str = Field(..., description="The query string")
    context: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Additional context"
    )
    target_servers: Optional[List[str]] = Field(
        None, description="Specific servers to query"
    )
    stream: bool = Field(default=False, description="Whether to stream the response")


class SessionRequest(BaseModel):
    """Request model for AG-UI session creation."""

    user_id: Optional[str] = Field(None, description="User ID")
    context: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Initial context"
    )


class EventRequest(BaseModel):
    """Request model for AG-UI events."""

    event_type: str = Field(..., description="Event type")
    payload: Dict[str, Any] = Field(..., description="Event payload")


# Create router
router = APIRouter(prefix="/api/v1/hybrid-rag", tags=["Hybrid RAG"])


@router.post("/query", response_model=QueryResponse)
async def query_hybrid_rag(request: QueryRequest):
    """Process a query through the hybrid RAG system.

    This endpoint routes queries intelligently between:
    - Vector search for semantic similarity
    - MCP federation for structured data
    - Agno orchestration for complex workflows
    - LlamaIndex for document intelligence
    """
    start_time = time.perf_counter()

    try:
        # Ensure router is initialized
        if not hybrid_rag_router.initialized:
            await hybrid_rag_router.initialize()

        # Create session if user_id provided
        session_id = None
        if request.user_id:
            session_id = await agui_protocol.create_session(
                request.user_id, request.context
            )

        # Process query
        result = await hybrid_rag_router.route_query(
            query=request.query, context=request.context, stream=False
        )

        execution_time = (time.perf_counter() - start_time) * 1000

        return QueryResponse(
            success=result.get("success", False),
            data=result.get("data"),
            error=result.get("error"),
            routing_metadata=result.get("routing_metadata"),
            execution_time_ms=execution_time,
            session_id=session_id,
        )

    except Exception as e:
        execution_time = (time.perf_counter() - start_time) * 1000
        logger.error(f"Hybrid RAG query failed: {e}")

        return QueryResponse(
            success=False, error=str(e), execution_time_ms=execution_time
        )


@router.post("/query/stream")
async def stream_hybrid_rag_query(request: QueryRequest):
    """Stream a query through the hybrid RAG system with real-time results.
    """
    try:
        # Ensure router is initialized
        if not hybrid_rag_router.initialized:
            await hybrid_rag_router.initialize()

        async def generate_stream():
            try:
                async for chunk in hybrid_rag_router.route_query(
                    query=request.query, context=request.context, stream=True
                ):
                    yield f"data: {json.dumps(chunk)}\n\n"
            except Exception as e:
                error_chunk = {"type": "error", "error": str(e)}
                yield f"data: {json.dumps(error_chunk)}\n\n"

        return StreamingResponse(
            generate_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "*",
            },
        )

    except Exception as e:
        logger.error(f"Streaming query failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/agents/process")
async def process_agent_request(request: AgentRequest):
    """Process a request through ultra-fast Agno agents.
    """
    try:
        # Ensure Agno integration is initialized
        if not enhanced_agno_integration.initialized:
            await enhanced_agno_integration.initialize()

        # Process request
        result = await enhanced_agno_integration.process_ultra_fast_request(
            request=request.request, pool_name=request.pool_name, stream=request.stream
        )

        if request.stream:
            # Convert async generator to streaming response
            async def generate_agent_stream():
                async for chunk in result:
                    yield f"data: {json.dumps(chunk)}\n\n"

            return StreamingResponse(
                generate_agent_stream(), media_type="text/event-stream"
            )
        else:
            return result

    except Exception as e:
        logger.error(f"Agent request failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agents/stats")
async def get_agent_stats():
    """Get comprehensive statistics about Agno agent performance.
    """
    try:
        if not enhanced_agno_integration.initialized:
            await enhanced_agno_integration.initialize()

        stats = enhanced_agno_integration.get_performance_stats()
        validation = await enhanced_agno_integration.validate_performance_targets()

        return {
            "performance_stats": stats,
            "validation": validation,
            "timestamp": time.time(),
        }

    except Exception as e:
        logger.error(f"Failed to get agent stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/mcp/query")
async def query_mcp_federation(request: MCPQueryRequest):
    """Query the MCP federation directly.
    """
    try:
        # Ensure MCP federation is initialized
        if not mcp_federation.initialized:
            await mcp_federation.initialize()

        # Process query
        result = await mcp_federation.federated_query(
            query=request.query, context=request.context, stream=request.stream
        )

        if request.stream:
            # Convert async generator to streaming response
            async def generate_mcp_stream():
                async for chunk in result:
                    yield f"data: {json.dumps(chunk)}\n\n"

            return StreamingResponse(
                generate_mcp_stream(), media_type="text/event-stream"
            )
        else:
            return result

    except Exception as e:
        logger.error(f"MCP query failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/mcp/stats")
async def get_mcp_stats():
    """Get comprehensive statistics about MCP federation.
    """
    try:
        if not mcp_federation.initialized:
            await mcp_federation.initialize()

        stats = mcp_federation.get_federation_stats()
        return {"federation_stats": stats, "timestamp": time.time()}

    except Exception as e:
        logger.error(f"Failed to get MCP stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sessions")
async def create_agui_session(request: SessionRequest):
    """Create a new AG-UI session for real-time interaction.
    """
    try:
        session_id = await agui_protocol.create_session(
            user_id=request.user_id, context=request.context
        )

        return {
            "session_id": session_id,
            "created_at": time.time(),
            "websocket_url": f"/api/v1/hybrid-rag/sessions/{session_id}/ws",
            "stream_url": f"/api/v1/hybrid-rag/sessions/{session_id}/stream",
        }

    except Exception as e:
        logger.error(f"Failed to create session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.websocket("/sessions/{session_id}/ws")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time AG-UI communication.
    """
    try:
        await agui_protocol.connect_websocket(websocket, session_id)
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for session {session_id}")
    except Exception as e:
        logger.error(f"WebSocket error for session {session_id}: {e}")


@router.get("/sessions/{session_id}/stream")
async def stream_session_events(session_id: str):
    """HTTP Server-Sent Events endpoint for AG-UI communication.
    """
    try:
        return StreamingResponse(
            agui_protocol.stream_events(session_id),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "*",
            },
        )

    except Exception as e:
        logger.error(f"Failed to stream events for session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sessions/{session_id}/events")
async def send_event_to_session(session_id: str, request: EventRequest):
    """Send an event to a specific AG-UI session.
    """
    try:
        # Create and process event
        from backend.api.agui_protocol import AGUIEvent

        event = AGUIEvent(
            type=EventType(request.event_type),
            payload=request.payload,
            session_id=session_id,
            timestamp=time.time(),
        )

        await agui_protocol.process_event(event)

        return {
            "success": True,
            "event_id": event.event_id,
            "timestamp": event.timestamp,
        }

    except Exception as e:
        logger.error(f"Failed to send event to session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_system_stats():
    """Get comprehensive statistics about the entire hybrid RAG system.
    """
    try:
        # Initialize components if needed
        if not hybrid_rag_router.initialized:
            await hybrid_rag_router.initialize()
        if not enhanced_agno_integration.initialized:
            await enhanced_agno_integration.initialize()
        if not mcp_federation.initialized:
            await mcp_federation.initialize()

        # Collect stats from all components
        router_stats = hybrid_rag_router.get_router_stats()
        agno_stats = enhanced_agno_integration.get_performance_stats()
        mcp_stats = mcp_federation.get_federation_stats()
        agui_stats = agui_protocol.get_protocol_stats()

        return {
            "system_overview": {
                "status": "operational",
                "timestamp": time.time(),
                "components": {
                    "hybrid_rag_router": "initialized"
                    if hybrid_rag_router.initialized
                    else "not_initialized",
                    "agno_integration": "initialized"
                    if enhanced_agno_integration.initialized
                    else "not_initialized",
                    "mcp_federation": "initialized"
                    if mcp_federation.initialized
                    else "not_initialized",
                    "agui_protocol": "operational",
                },
            },
            "performance_summary": {
                "total_queries": router_stats["routing_metrics"]["total_queries"],
                "success_rate": router_stats["routing_metrics"]["success_rate"],
                "avg_routing_time_ms": router_stats["routing_metrics"][
                    "avg_routing_time_ms"
                ],
                "avg_agno_instantiation_us": agno_stats["overall"][
                    "avg_instantiation_us"
                ],
                "active_agui_sessions": agui_stats["sessions"]["active"],
                "mcp_federation_health": mcp_stats["federation_health"][
                    "overall_success_rate"
                ],
            },
            "detailed_stats": {
                "router": router_stats,
                "agno": agno_stats,
                "mcp": mcp_stats,
                "agui": agui_stats,
            },
        }

    except Exception as e:
        logger.error(f"Failed to get system stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/health")
async def health_check():
    """Comprehensive health check for the hybrid RAG system.
    """
    try:
        health_status = {
            "status": "healthy",
            "timestamp": time.time(),
            "components": {},
        }

        # Check hybrid RAG router
        try:
            if not hybrid_rag_router.initialized:
                await hybrid_rag_router.initialize()
            health_status["components"]["hybrid_rag_router"] = "healthy"
        except Exception as e:
            health_status["components"]["hybrid_rag_router"] = f"unhealthy: {str(e)}"
            health_status["status"] = "degraded"

        # Check Agno integration
        try:
            if not enhanced_agno_integration.initialized:
                await enhanced_agno_integration.initialize()
            validation = await enhanced_agno_integration.validate_performance_targets()
            health_status["components"]["agno_integration"] = (
                "healthy"
                if validation["validation"]["overall_performance"] == "excellent"
                else "degraded"
            )
        except Exception as e:
            health_status["components"]["agno_integration"] = f"unhealthy: {str(e)}"
            health_status["status"] = "degraded"

        # Check MCP federation
        try:
            if not mcp_federation.initialized:
                await mcp_federation.initialize()
            mcp_stats = mcp_federation.get_federation_stats()
            healthy_servers = mcp_stats["federation_health"]["healthy_servers"]
            total_servers = mcp_stats["federation_health"]["total_servers"]
            if healthy_servers >= total_servers * 0.7:  # 70% of servers healthy
                health_status["components"]["mcp_federation"] = "healthy"
            else:
                health_status["components"]["mcp_federation"] = "degraded"
                health_status["status"] = "degraded"
        except Exception as e:
            health_status["components"]["mcp_federation"] = f"unhealthy: {str(e)}"
            health_status["status"] = "degraded"

        # Check AG-UI protocol
        try:
            agui_stats = agui_protocol.get_protocol_stats()
            health_status["components"]["agui_protocol"] = "healthy"
        except Exception as e:
            health_status["components"]["agui_protocol"] = f"unhealthy: {str(e)}"
            health_status["status"] = "degraded"

        return health_status

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"status": "unhealthy", "error": str(e), "timestamp": time.time()}


# Background task to cleanup inactive sessions
@router.on_event("startup")
async def startup_cleanup_task():
    """Start background cleanup task."""

    async def cleanup_loop():
        while True:
            try:
                await agui_protocol.cleanup_inactive_sessions()
                await asyncio.sleep(3600)  # Run every hour
            except Exception as e:
                logger.error(f"Cleanup task error: {e}")
                await asyncio.sleep(3600)

    asyncio.create_task(cleanup_loop())
