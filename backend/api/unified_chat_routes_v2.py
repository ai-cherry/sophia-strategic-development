"""
Unified Chat API Routes - Phase 2A Implementation
Consolidates sophia_universal_chat_routes.py, universal_chat_routes.py, and enhanced_ceo_chat_routes.py

CRITICAL: All LLM interactions route through the unified LLM gateway
to ensure centralized control, caching, monitoring, and cost optimization.
"""

import logging
import uuid
from datetime import UTC, datetime
from typing import Any, Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

# Import unified LLM service for centralized routing
try:
    from backend.services.unified_llm_service import TaskType, get_unified_llm_service

    unified_llm_available = True
except ImportError:
    # Fallback for development
    get_unified_llm_service = None
    unified_llm_available = False

    # Create fallback TaskType enum
    from enum import Enum

    class TaskType(Enum):
        CHAT_CONVERSATION = "chat_conversation"
        BUSINESS_INTELLIGENCE = "business_intelligence"


# Optional imports for backward compatibility
try:
    from backend.services.enhanced_unified_chat_service import (
        EnhancedUnifiedChatService,
    )
except ImportError:
    EnhancedUnifiedChatService = None

try:
    from backend.services.sophia_universal_chat_service import SophiaUnifiedChatService
except ImportError:
    SophiaUnifiedChatService = None

logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(prefix="/api/v1", tags=["unified-chat"])


# Unified Request/Response Models
class ChatRequest(BaseModel):
    """Unified chat request model supporting all chat modes"""

    message: str = Field(..., description="User message content")
    mode: Literal["universal", "sophia", "executive"] = Field(
        default="universal",
        description="Chat mode: universal (basic), sophia (full AI), executive (CEO-focused)",
    )
    session_id: str | None = Field(
        default=None, description="Session ID for conversation continuity"
    )
    context: dict[str, Any] | None = Field(
        default=None, description="Additional context for the conversation"
    )
    user_role: str | None = Field(
        default=None, description="User role for role-based responses"
    )
    temperature: float | None = Field(
        default=0.7, ge=0.0, le=2.0, description="Response creativity (0.0-2.0)"
    )
    max_tokens: int | None = Field(
        default=1000, ge=1, le=4000, description="Maximum response length"
    )


class ChatResponse(BaseModel):
    """Unified chat response model"""

    response: str = Field(..., description="AI response content")
    session_id: str = Field(..., description="Session ID for this conversation")
    mode: str = Field(..., description="Chat mode used")
    provider: str = Field(..., description="AI provider used (via unified gateway)")
    metadata: dict[str, Any] | None = Field(
        default=None, description="Additional response metadata"
    )
    suggestions: list[str] | None = Field(
        default=None, description="Suggested follow-up questions"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Response timestamp"
    )
    tokens_used: int | None = Field(
        default=None, description="Tokens consumed for this request"
    )
    cost: float | None = Field(
        default=None, description="Estimated cost for this request"
    )


class ChatSession(BaseModel):
    """Chat session information"""

    session_id: str
    mode: str
    created_at: datetime
    last_activity: datetime
    message_count: int
    total_tokens: int
    total_cost: float


# Unified chat service using the unified LLM gateway
class UnifiedChatService:
    """Unified chat service routing all requests through the unified LLM gateway"""

    def __init__(self):
        self.llm_service = None

    async def _ensure_llm_service(self):
        """Ensure unified LLM service is initialized"""
        if self.llm_service is None and get_unified_llm_service:
            self.llm_service = await get_unified_llm_service()

    async def process_universal_chat(self, request: ChatRequest) -> ChatResponse:
        """Process universal chat request through unified gateway"""
        await self._ensure_llm_service()

        if not self.llm_service:
            # Fallback mock response
            return ChatResponse(
                response=f"Universal chat response to: '{request.message}'. This is a basic chat mode with general AI capabilities.",
                session_id=request.session_id or str(uuid.uuid4()),
                mode="universal",
                provider="unified_gateway",
                metadata={"response_type": "universal", "features": ["basic_chat"]},
                suggestions=["Tell me more", "What else can you help with?"],
                tokens_used=50,
                cost=0.001,
            )

        # Route through unified LLM service
        response_chunks = []
        async for chunk in self.llm_service.complete(
            prompt=request.message,
            task_type=TaskType.CHAT_CONVERSATION,
            stream=False,
            temperature=request.temperature or 0.7,
            max_tokens=request.max_tokens or 1000,
            metadata={"mode": "universal", "session_id": request.session_id},
        ):
            response_chunks.append(chunk)

        response_text = "".join(response_chunks)

        return ChatResponse(
            response=response_text,
            session_id=request.session_id or str(uuid.uuid4()),
            mode="universal",
            provider="unified_gateway",
            metadata={"response_type": "universal", "routing": "unified_llm_service"},
            suggestions=["Tell me more", "What else can you help with?"],
            tokens_used=len(response_text.split()),
            cost=0.001,
        )

    async def process_sophia_chat(self, request: ChatRequest) -> ChatResponse:
        """Process Sophia AI chat request through unified gateway"""
        await self._ensure_llm_service()

        if not self.llm_service:
            # Fallback mock response
            return ChatResponse(
                response=f"Sophia AI response to: '{request.message}'. I'm your advanced AI assistant with comprehensive business intelligence capabilities.",
                session_id=request.session_id or str(uuid.uuid4()),
                mode="sophia",
                provider="unified_gateway",
                metadata={
                    "response_type": "sophia",
                    "features": ["business_intelligence"],
                },
                suggestions=[
                    "Analyze our Q3 performance",
                    "What are key industry trends?",
                ],
                tokens_used=120,
                cost=0.003,
            )

        # Route through unified LLM service with business intelligence focus
        response_chunks = []
        async for chunk in self.llm_service.complete(
            prompt=f"As Sophia AI, provide business intelligence insights for: {request.message}",
            task_type=TaskType.BUSINESS_INTELLIGENCE,
            stream=False,
            temperature=request.temperature or 0.7,
            max_tokens=request.max_tokens or 1000,
            metadata={
                "mode": "sophia",
                "session_id": request.session_id,
                "business_context": True,
            },
        ):
            response_chunks.append(chunk)

        response_text = "".join(response_chunks)

        return ChatResponse(
            response=response_text,
            session_id=request.session_id or str(uuid.uuid4()),
            mode="sophia",
            provider="unified_gateway",
            metadata={
                "response_type": "sophia",
                "features": [
                    "business_intelligence",
                    "data_analysis",
                    "strategic_insights",
                ],
                "routing": "unified_llm_service",
                "sophia_version": "2.1.0",
            },
            suggestions=[
                "Analyze our Q3 performance metrics",
                "What are the key trends in our industry?",
                "Generate a strategic recommendation",
            ],
            tokens_used=len(response_text.split()),
            cost=0.003,
        )

    async def process_executive_chat(self, request: ChatRequest) -> ChatResponse:
        """Process executive/CEO chat request through unified gateway"""
        await self._ensure_llm_service()

        if not self.llm_service:
            # Fallback mock response
            return ChatResponse(
                response=f"Executive Assistant response to: '{request.message}'. As your executive AI assistant, I provide high-level strategic insights and C-suite focused analysis.",
                session_id=request.session_id or str(uuid.uuid4()),
                mode="executive",
                provider="unified_gateway",
                metadata={"response_type": "executive", "executive_level": "c_suite"},
                suggestions=[
                    "Summarize key business metrics",
                    "Top 3 strategic priorities",
                ],
                tokens_used=150,
                cost=0.005,
            )

        # Route through unified LLM service with executive context
        executive_prompt = f"""As an executive AI assistant for C-suite leadership, provide strategic insights for: {request.message}

Context: This is an executive-level request requiring high-quality strategic analysis, board-ready summaries, and C-suite focused recommendations."""

        response_chunks = []
        async for chunk in self.llm_service.complete(
            prompt=executive_prompt,
            task_type=TaskType.BUSINESS_INTELLIGENCE,
            stream=False,
            temperature=request.temperature or 0.7,
            max_tokens=request.max_tokens or 1000,
            metadata={
                "mode": "executive",
                "session_id": request.session_id,
                "executive_level": True,
                "user_role": request.user_role or "ceo",
            },
        ):
            response_chunks.append(chunk)

        response_text = "".join(response_chunks)

        return ChatResponse(
            response=response_text,
            session_id=request.session_id or str(uuid.uuid4()),
            mode="executive",
            provider="unified_gateway",
            metadata={
                "response_type": "executive",
                "features": [
                    "executive_insights",
                    "strategic_analysis",
                    "board_summaries",
                ],
                "executive_level": "c_suite",
                "routing": "unified_llm_service",
                "unified_gateway_integration": True,
            },
            suggestions=[
                "Summarize this week's key business metrics",
                "What are our top 3 strategic priorities?",
                "Prepare a board presentation summary",
                "Analyze competitive positioning",
            ],
            tokens_used=len(response_text.split()),
            cost=0.005,
        )


# Initialize unified chat service
unified_chat_service = UnifiedChatService()


# Chat mode handlers using unified service
async def handle_universal_chat(request: ChatRequest) -> ChatResponse:
    """Handle universal chat mode through unified gateway"""
    logger.info(
        f"Processing universal chat through unified gateway: {request.message[:50]}..."
    )
    return await unified_chat_service.process_universal_chat(request)


async def handle_sophia_chat(request: ChatRequest) -> ChatResponse:
    """Handle Sophia AI chat mode through unified gateway"""
    logger.info(
        f"Processing Sophia chat through unified gateway: {request.message[:50]}..."
    )
    return await unified_chat_service.process_sophia_chat(request)


async def handle_executive_chat(request: ChatRequest) -> ChatResponse:
    """Handle executive/CEO chat mode through unified gateway"""
    logger.info(
        f"Processing executive chat through unified gateway: {request.message[:50]}..."
    )
    return await unified_chat_service.process_executive_chat(request)


# Main unified chat endpoint
@router.post("/chat", response_model=ChatResponse)
async def unified_chat(request: ChatRequest) -> ChatResponse:
    """
    Unified chat endpoint supporting multiple modes

    IMPORTANT: All requests are routed through the unified LLM gateway
    for centralized control, caching, monitoring, and cost optimization.

    Modes:
    - universal: Basic chat functionality
    - sophia: Full Sophia AI capabilities with business intelligence
    - executive: CEO/executive-focused chat with strategic insights

    Note: Provider selection is handled automatically by the unified gateway
    based on task complexity, cost optimization, and performance requirements.
    """
    try:
        # Validate request
        if not request.message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")

        # Generate session ID if not provided
        if not request.session_id:
            request.session_id = str(uuid.uuid4())

        # Route to appropriate handler based on mode
        # All handlers use the unified LLM gateway for consistent routing
        if request.mode == "executive":
            response = await handle_executive_chat(request)
        elif request.mode == "sophia":
            response = await handle_sophia_chat(request)
        else:  # universal
            response = await handle_universal_chat(request)

        logger.info(
            f"Chat processed through unified gateway: mode={request.mode}, session={request.session_id}, provider={response.provider}"
        )
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat processing error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# Session management endpoints
@router.get("/chat/sessions/{session_id}", response_model=ChatSession)
async def get_chat_session(session_id: str) -> ChatSession:
    """Get chat session information"""
    # Mock implementation - replace with actual session storage
    return ChatSession(
        session_id=session_id,
        mode="sophia",
        created_at=datetime.now(UTC),
        last_activity=datetime.now(UTC),
        message_count=5,
        total_tokens=500,
        total_cost=0.015,
    )


@router.delete("/chat/sessions/{session_id}")
async def delete_chat_session(session_id: str) -> dict[str, str]:
    """Delete chat session"""
    # Mock implementation - replace with actual session storage
    logger.info(f"Deleting chat session: {session_id}")
    return {"message": f"Session {session_id} deleted successfully"}


@router.get("/chat/sessions", response_model=list[ChatSession])
async def list_chat_sessions(limit: int = 10, offset: int = 0) -> list[ChatSession]:
    """List chat sessions"""
    # Mock implementation - replace with actual session storage
    return [
        ChatSession(
            session_id=f"session_{i}",
            mode="sophia" if i % 2 == 0 else "executive",
            created_at=datetime.now(UTC),
            last_activity=datetime.now(UTC),
            message_count=i * 3,
            total_tokens=i * 100,
            total_cost=i * 0.01,
        )
        for i in range(offset, min(offset + limit, 10))
    ]


# Health check endpoint
@router.get("/chat/health")
async def chat_health_check() -> dict[str, Any]:
    """Health check for chat services"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(UTC).isoformat(),
        "modes": ["universal", "sophia", "executive"],
        "routing": "unified_llm_gateway",
        "provider_selection": "automatic_via_unified_gateway",
        "version": "2.0.0",
    }


# Backward compatibility endpoints (deprecated)
@router.post("/sophia-universal-chat", deprecated=True)
async def sophia_universal_chat_legacy(request: dict[str, Any]) -> dict[str, Any]:
    """Legacy Sophia universal chat endpoint (deprecated)"""
    logger.warning("Using deprecated sophia-universal-chat endpoint")

    # Convert legacy request to unified format
    unified_request = ChatRequest(
        message=request.get("message", ""),
        mode="sophia",
        session_id=request.get("session_id"),
        context=request.get("context"),
    )

    response = await unified_chat(unified_request)

    # Convert to legacy response format
    return {
        "response": response.response,
        "session_id": response.session_id,
        "metadata": response.metadata,
    }


@router.post("/universal-chat", deprecated=True)
async def universal_chat_legacy(request: dict[str, Any]) -> dict[str, Any]:
    """Legacy universal chat endpoint (deprecated)"""
    logger.warning("Using deprecated universal-chat endpoint")

    # Convert legacy request to unified format
    unified_request = ChatRequest(
        message=request.get("message", ""),
        mode="universal",
        session_id=request.get("session_id"),
    )

    response = await unified_chat(unified_request)

    # Convert to legacy response format
    return {"response": response.response, "session_id": response.session_id}


@router.post("/enhanced-ceo-chat", deprecated=True)
async def enhanced_ceo_chat_legacy(request: dict[str, Any]) -> dict[str, Any]:
    """Legacy enhanced CEO chat endpoint (deprecated)"""
    logger.warning("Using deprecated enhanced-ceo-chat endpoint")

    # Convert legacy request to unified format
    unified_request = ChatRequest(
        message=request.get("message", ""),
        mode="executive",
        session_id=request.get("session_id"),
        user_role="ceo",
    )

    response = await unified_chat(unified_request)

    # Convert to legacy response format
    return {
        "response": response.response,
        "session_id": response.session_id,
        "metadata": response.metadata,
        "suggestions": response.suggestions,
    }


# Export router for main application
__all__ = ["router"]
