"""
UNIFIED CHAT ROUTES - CONSOLIDATED IMPLEMENTATION

This module consolidates ALL existing chat API routes into a single,
unified, role-aware chat API for Sophia AI Platform.
"""

import logging
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

# Import the enhanced chat service
from infrastructure.services.unified_chat_service import (
    ChatResponse,
    EnhancedUnifiedChatService,
    universal_chat_service,
)

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/chat", tags=["Unified Chat"])


# Request/Response Models
class ChatRequest(BaseModel):
    message: str = Field(..., description="User message")
    session_id: str | None = Field(default=None, description="Session ID")
    user_id: str = Field(default="user", description="User ID")
    context: dict[str, Any] = Field(default={}, description="Additional context")


class HealthResponse(BaseModel):
    status: str
    initialized: bool
    components: dict[str, bool]
    metrics: dict[str, Any]
    timestamp: str


# Helper Functions
async def get_chat_service() -> EnhancedUnifiedChatService:
    """Get the chat service instance"""
    if not universal_chat_service.initialized:
        await universal_chat_service.initialize()
    return universal_chat_service


# API Endpoints
@router.post("/message", response_model=ChatResponse)
async def send_chat_message(
    request: ChatRequest,
    chat_service: EnhancedUnifiedChatService = Depends(get_chat_service),
):
    """Send a chat message and get AI response"""
    try:
        response = await chat_service.process_chat_message(
            message=request.message,
            user_id=request.user_id,
            session_id=request.session_id,
            context=request.context,
        )
        return response

    except Exception as e:
        logger.exception(f"Error processing chat message: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing message: {e!s}")


@router.get("/health", response_model=HealthResponse)
async def chat_health_check(
    chat_service: EnhancedUnifiedChatService = Depends(get_chat_service),
):
    """Get chat service health status"""
    try:
        health_status = chat_service.get_health_status()
        return HealthResponse(**health_status)

    except Exception as e:
        logger.exception(f"Error getting health status: {e}")
        return HealthResponse(
            status="unhealthy",
            initialized=False,
            components={},
            metrics={},
            timestamp=datetime.now().isoformat(),
        )


@router.get("/capabilities")
async def get_chat_capabilities():
    """Get chat service capabilities"""
    return {
        "universal_chat": True,
        "role_based_access": True,
        "ai_personalities": [
            "executive_advisor",
            "business_intelligence",
            "friendly_assistant",
            "technical_expert",
            "project_manager",
        ],
        "search_contexts": [
            "universal",
            "internal_only",
            "business_intelligence",
            "strategic_research",
        ],
        "supported_roles": ["Unified", "Executive", "Manager", "Employee"],
        "features": [
            "universal_search",
            "business_intelligence",
            "source_attribution",
            "recommended_actions",
            "session_management",
        ],
    }
