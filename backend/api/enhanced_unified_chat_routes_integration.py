"""
Enhanced Unified Chat Routes with Service Integration
=====================================================

This module extends the existing enhanced_unified_chat_routes.py
to integrate with the unified service registry and orchestrators.
"""

import logging
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import Field

from backend.api.enhanced_unified_chat_routes import (
    ChatRequest,
    ChatResponse,
)
from backend.api.enhanced_unified_chat_routes import (
    manager as websocket_manager,
)
from backend.core.dependencies import get_current_user
from backend.services.sophia_ai_orchestrator import (
    OrchestrationMode,
    OrchestrationRequest,
    RequestType,
)
from backend.services.unified_service_registry import (
    get_business_intelligence,
    get_cache_service,
    get_sophia_orchestrator,
    registry,
)

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/chat", tags=["Enhanced Chat Integration"])


class IntegratedChatRequest(ChatRequest):
    """Extended chat request with orchestration hints"""

    orchestration_mode: str | None = Field(
        default="unified_intelligence", description="Orchestration mode hint"
    )
    require_business_intelligence: bool = Field(
        default=False, description="Force business intelligence processing"
    )
    require_ui_generation: bool = Field(
        default=False, description="Force UI/UX generation"
    )


class IntegratedChatResponse(ChatResponse):
    """Extended chat response with orchestration details"""

    services_used: list[str] = Field(
        default_factory=list, description="Services that processed this request"
    )
    orchestration_details: dict[str, Any] | None = Field(
        default=None, description="Details from orchestration"
    )
    cache_hit: bool = Field(
        default=False, description="Whether response was from cache"
    )


async def determine_intent(message: str, context: dict[str, Any]) -> dict[str, Any]:
    """
    Determine the intent and required services for a message

    Returns:
        Dict with intent classification and service requirements
    """
    message_lower = message.lower()

    intent = {
        "is_business_query": any(
            term in message_lower
            for term in [
                "revenue",
                "sales",
                "customer",
                "roi",
                "profit",
                "market",
                "competitor",
                "prospect",
                "deal",
                "pipeline",
                "forecast",
            ]
        ),
        "is_ui_request": any(
            term in message_lower
            for term in [
                "design",
                "ui",
                "ux",
                "component",
                "interface",
                "mockup",
                "prototype",
                "figma",
                "create ui",
                "generate design",
            ]
        ),
        "is_knowledge_query": any(
            term in message_lower
            for term in [
                "what is",
                "how does",
                "explain",
                "tell me about",
                "define",
                "documentation",
                "knowledge",
                "information",
            ]
        ),
        "is_project_query": any(
            term in message_lower
            for term in [
                "project",
                "task",
                "asana",
                "linear",
                "status",
                "progress",
                "deadline",
                "milestone",
                "okr",
            ]
        ),
        "requires_search": any(
            term in message_lower
            for term in ["search", "find", "look up", "latest", "recent", "news"]
        ),
    }

    # Determine primary intent
    if intent["is_business_query"]:
        intent["primary"] = "business_intelligence"
    elif intent["is_ui_request"]:
        intent["primary"] = "ui_generation"
    elif intent["is_project_query"]:
        intent["primary"] = "project_management"
    elif intent["is_knowledge_query"]:
        intent["primary"] = "knowledge_retrieval"
    else:
        intent["primary"] = "general_assistance"

    return intent


@router.post("/integrated", response_model=IntegratedChatResponse)
async def integrated_chat_endpoint(
    request: IntegratedChatRequest, current_user: dict = Depends(get_current_user)
):
    """
    Integrated chat endpoint that orchestrates across all services

    This endpoint:
    1. Determines intent
    2. Checks cache
    3. Routes to appropriate orchestrators
    4. Synthesizes responses
    5. Updates cache
    """
    try:
        user_id = current_user.get("user_id", "anonymous")

        # Initialize critical services
        await registry.initialize_all_critical()

        # Get cache service
        cache_service = await get_cache_service()

        # Check cache first
        cache_key = f"{user_id}:{request.message}"
        if cache_service:
            cached_response = await cache_service.get(cache_key)
            if cached_response:
                logger.info(f"Cache hit for query: {request.message[:50]}...")
                return IntegratedChatResponse(**cached_response, cache_hit=True)

        # Determine intent
        intent = await determine_intent(request.message, request.metadata or {})
        logger.info(f"Determined intent: {intent['primary']}")

        # Route to appropriate orchestrator
        services_used = []
        orchestration_details = {}

        if intent["is_business_query"] or request.require_business_intelligence:
            # Use business intelligence orchestrator
            bi_service = await get_business_intelligence()
            if bi_service:
                bi_response = await bi_service.handle_conversational_query(
                    request.message,
                    {"user_id": user_id, "session_id": request.session_id},
                )
                orchestration_details["business_intelligence"] = bi_response
                services_used.append("business_intelligence")

        # Always use Sophia orchestrator for unified intelligence
        sophia_orchestrator = await get_sophia_orchestrator()
        if sophia_orchestrator:
            orch_request = OrchestrationRequest(
                request_id=f"chat_{request.session_id}_{datetime.now().timestamp()}",
                request_type=RequestType.KNOWLEDGE_QUERY,
                user_id=user_id,
                context={
                    "session_id": request.session_id,
                    "intent": intent,
                    "metadata": request.metadata,
                },
                query=request.message,
                mode=OrchestrationMode(request.orchestration_mode),
            )

            orch_response = await sophia_orchestrator.process_request(orch_request)

            # Build integrated response
            response_content = orch_response.primary_response.get(
                "response", orch_response.primary_response.get("answer", "")
            )

            # Add business intelligence insights if available
            if "business_intelligence" in orchestration_details:
                response_content += (
                    f"\n\n{orchestration_details['business_intelligence']}"
                )

            response = IntegratedChatResponse(
                message_id=orch_request.request_id,
                session_id=request.session_id,
                message_type="ai_response",
                content=response_content,
                metadata={
                    "confidence": orch_response.confidence_score,
                    "processing_time_ms": orch_response.processing_time_ms,
                    "knowledge_items_accessed": orch_response.knowledge_items_accessed,
                },
                timestamp=datetime.now(),
                intent=intent["primary"],
                confidence=orch_response.confidence_score,
                services_used=services_used + orch_response.services_used,
                orchestration_details={
                    "suggested_actions": orch_response.suggested_actions,
                    "related_queries": orch_response.related_queries,
                },
            )

            # Cache the response
            if cache_service and response.confidence > 0.8:
                await cache_service.set(cache_key, response.dict(), ttl=3600)  # 1 hour

            # Send via WebSocket if connected
            await websocket_manager.broadcast_to_user(
                {"type": "integrated_response", "data": response.dict()}, user_id
            )

            return response

        # Fallback if no orchestrator available
        raise HTTPException(
            status_code=503, detail="Orchestration services unavailable"
        )

    except Exception as e:
        logger.error(f"Integrated chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/services/status")
async def get_services_status():
    """Get status of all integrated services"""
    health_status = await registry.health_check()

    return {
        "timestamp": datetime.now().isoformat(),
        "services": health_status,
        "summary": {
            "total": len(health_status),
            "healthy": sum(
                1 for s in health_status.values() if s["status"] == "healthy"
            ),
            "unhealthy": sum(
                1 for s in health_status.values() if s["status"] == "unhealthy"
            ),
            "error": sum(1 for s in health_status.values() if s["status"] == "error"),
        },
    }


@router.websocket("/integrated/ws/{user_id}")
async def integrated_websocket_endpoint(websocket: WebSocket, user_id: str):
    """
    Integrated WebSocket endpoint with full orchestration

    Supports:
    - Real-time chat with orchestration
    - Service status updates
    - Workflow notifications
    - Dashboard data streaming
    """
    await websocket_manager.connect(websocket, user_id)

    try:
        # Initialize services
        await registry.initialize_all_critical()

        while True:
            data = await websocket.receive_json()
            message_type = data.get("type", "chat_message")

            if message_type == "chat_message":
                # Process through integrated chat
                request = IntegratedChatRequest(
                    message=data.get("message", ""),
                    session_id=data.get("session_id", f"ws_{user_id}"),
                    metadata=data.get("metadata", {}),
                    orchestration_mode=data.get(
                        "orchestration_mode", "unified_intelligence"
                    ),
                )

                # Mock current user for WebSocket
                current_user = {"user_id": user_id}

                try:
                    response = await integrated_chat_endpoint(request, current_user)
                    await websocket.send_json(
                        {"type": "integrated_response", "data": response.dict()}
                    )
                except Exception as e:
                    await websocket.send_json({"type": "error", "message": str(e)})

            elif message_type == "service_status":
                # Get service status
                status = await get_services_status()
                await websocket.send_json({"type": "service_status", "data": status})

            elif message_type == "ping":
                # Heartbeat
                await websocket.send_json(
                    {"type": "pong", "timestamp": datetime.now().isoformat()}
                )

    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket, user_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        websocket_manager.disconnect(websocket, user_id)
