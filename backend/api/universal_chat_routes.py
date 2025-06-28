"""
Universal Chat Routes for Sophia AI

Fixed to eliminate circular imports by using proper dependency injection
and accessing the chat service from FastAPI app state.
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import logging

# Import dependency function
from backend.core.dependencies import get_request_chat_service

logger = logging.getLogger(__name__)

router = APIRouter()


class ChatRequest(BaseModel):
    """Chat request model"""

    message: str = Field(..., description="The user's message")
    user_id: str = Field(default="default_user", description="User identifier")
    context: Optional[Dict[str, Any]] = Field(
        default={}, description="Additional context"
    )

    class Config:
        # Avoid Pydantic model_ namespace conflicts
        protected_namespaces = ()


class ChatResponse(BaseModel):
    """Chat response model"""

    response: str = Field(..., description="AI response")
    user_id: str = Field(..., description="User identifier")
    model_used: Optional[str] = Field(None, description="AI model used")
    processing_time: Optional[float] = Field(
        None, description="Processing time in seconds"
    )

    class Config:
        # Avoid Pydantic model_ namespace conflicts
        protected_namespaces = ()


@router.post("/message", response_model=ChatResponse)
async def process_chat_message(
    chat_request: ChatRequest,
    request: Request,
    chat_service=Depends(get_request_chat_service),
):
    """
    Process a chat message through the Sophia AI system

    This endpoint provides universal chat functionality with proper
    dependency injection and no circular imports.
    """
    try:
        # Get the chat service from app state
        if hasattr(request.app.state, "chat_service_instance"):
            chat_service = request.app.state.chat_service_instance
        else:
            raise HTTPException(status_code=503, detail="Chat service not available")

        # Process the message
        if hasattr(chat_service, "process_chat_message"):
            response = await chat_service.process_chat_message(
                message=chat_request.message,
                user_id=chat_request.user_id,
                context=chat_request.context,
            )
        else:
            # Fallback response
            response = {
                "response": f"Received message: {chat_request.message}",
                "user_id": chat_request.user_id,
                "model_used": "fallback",
                "processing_time": 0.1,
            }

        return ChatResponse(**response)

    except Exception as e:
        logger.error(f"Error processing chat message: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Error processing message: {str(e)}"
        )


@router.get("/health")
async def chat_health_check(request: Request):
    """Health check for chat service"""
    try:
        chat_available = hasattr(request.app.state, "chat_service_instance")
        return {
            "status": "healthy" if chat_available else "degraded",
            "chat_service_available": chat_available,
            "service": "Universal Chat",
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e), "service": "Universal Chat"}


@router.get("/capabilities")
async def get_chat_capabilities(request: Request):
    """Get chat service capabilities"""
    try:
        if hasattr(request.app.state, "chat_service_instance"):
            chat_service = request.app.state.chat_service_instance

            # Extract capabilities if available
            capabilities = {
                "universal_chat": True,
                "context_aware": True,
                "multi_user": True,
                "available_methods": [],
            }

            # Add method names if available
            if hasattr(chat_service, "__dict__"):
                methods = [
                    method
                    for method in dir(chat_service)
                    if not method.startswith("_")
                    and callable(getattr(chat_service, method))
                ]
                capabilities["available_methods"] = methods[:10]  # Limit output

            return capabilities
        else:
            return {"universal_chat": False, "error": "Chat service not initialized"}

    except Exception as e:
        return {"error": str(e), "universal_chat": False}
