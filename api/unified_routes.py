"""
Unified API Routes - THE ONLY ROUTES FILE
Consolidates all chat and API functionality into a single, clean implementation
"""

import logging
import uuid
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field

from infrastructure.services.unified_sophia_service import (
    SophiaResponse,
    UnifiedSophiaService,
    get_unified_sophia_service,
)

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1", tags=["Unified API"])

# Request/Response Models
class ChatAPIRequest(BaseModel):
    """API request model for chat"""

    message: str = Field(..., description="User message")
    session_id: str | None = Field(default=None, description="Session ID")
    user_id: str = Field(default="user", description="User ID")
    context: dict[str, Any] | None = Field(
        default=None, description="Additional chat context"
    )

class ChatAPIResponse(BaseModel):
    """API response model for chat"""

    content: str
    suggestions: list[str]
    metadata: dict[str, Any]
    workflow_id: str
    session_id: str

# WebSocket Connection Manager
class ConnectionManager:
    """Manage WebSocket connections for real-time chat"""

    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, session_id: str):
        """Accept new WebSocket connection"""
        await websocket.accept()
        self.active_connections[session_id] = websocket
        logger.info(f"WebSocket connected: {session_id}")

    def disconnect(self, session_id: str):
        """Remove WebSocket connection"""
        if session_id in self.active_connections:
            del self.active_connections[session_id]
            logger.info(f"WebSocket disconnected: {session_id}")

    async def send_message(self, session_id: str, message: dict):
        """Send message to specific session"""
        if session_id in self.active_connections:
            try:
                await self.active_connections[session_id].send_json(message)
            except Exception as e:
                logger.exception(f"Error sending message to {session_id}: {e}")
                self.disconnect(session_id)

    async def broadcast(self, message: dict):
        """Broadcast message to all connections"""
        disconnected = []
        for session_id, websocket in self.active_connections.items():
            try:
                await websocket.send_json(message)
            except Exception:
                disconnected.append(session_id)

        # Clean up disconnected sessions
        for session_id in disconnected:
            self.disconnect(session_id)

# Global connection manager
manager = ConnectionManager()

# Health check endpoint
@router.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

# Unified chat endpoint (REST)
@router.post("/chat", response_model=ChatAPIResponse)
async def chat(
    request: ChatAPIRequest,
    sophia_service: UnifiedSophiaService = Depends(get_unified_sophia_service),
):
    """
    Main chat endpoint using the intelligent orchestrator.
    Processes a user message and returns a comprehensive AI response.
    """
    try:
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())

        # Process message through the unified service
        response: SophiaResponse = await sophia_service.process_message(
            message=request.message,
            user_id=request.user_id,
            session_id=session_id,
            context=request.context,
        )

        # Send response via WebSocket if a connection for this session exists
        await manager.send_message(
            session_id,
            {
                "type": "response",
                "data": {
                    "content": response.content,
                    "suggestions": response.suggestions,
                    "metadata": response.metadata,
                    "workflow_id": response.workflow_id,
                },
            },
        )

        return ChatAPIResponse(
            content=response.content,
            suggestions=response.suggestions,
            metadata=response.metadata,
            workflow_id=response.workflow_id,
            session_id=session_id,
        )

    except Exception as e:
        logger.exception(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# WebSocket endpoint for real-time chat
@router.websocket("/ws/chat/{session_id}")
async def websocket_chat(
    websocket: WebSocket,
    session_id: str,
    sophia_service: UnifiedSophiaService = Depends(get_unified_sophia_service),
):
    """WebSocket endpoint for real-time chat with the intelligent orchestrator"""
    await manager.connect(websocket, session_id)

    try:
        while True:
            # Receive message
            data = await websocket.receive_json()

            # Extract message data
            message = data.get("message", "")
            user_id = data.get("user_id", "anonymous_ws_user")
            context = data.get("context")

            if not message:
                await websocket.send_json(
                    {"type": "error", "message": "Message cannot be empty"}
                )
                continue

            # Send typing indicator
            await websocket.send_json(
                {"type": "typing", "timestamp": datetime.now().isoformat()}
            )

            # Process chat
            try:
                response: SophiaResponse = await sophia_service.process_message(
                    message=message,
                    user_id=user_id,
                    session_id=session_id,
                    context=context,
                )

                # Send response
                await websocket.send_json(
                    {
                        "type": "response",
                        "data": {
                            "content": response.content,
                            "suggestions": response.suggestions,
                            "metadata": response.metadata,
                            "workflow_id": response.workflow_id,
                        },
                    }
                )

            except Exception as e:
                logger.exception(f"Chat processing error: {e}")
                await websocket.send_json(
                    {"type": "error", "message": f"Error processing message: {e!s}"}
                )

    except WebSocketDisconnect:
        manager.disconnect(session_id)
    except Exception as e:
        logger.exception(f"WebSocket error in session {session_id}: {e}")
    finally:
        manager.disconnect(session_id)
