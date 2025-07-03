"""
Unified API Routes - THE ONLY ROUTES FILE
Consolidates all chat and API functionality into a single, clean implementation
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
import uuid

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from backend.services.unified_chat_service import (
    UnifiedChatService,
    get_unified_chat_service,
    ChatRequest,
    ChatResponse,
    ChatContext,
    AccessLevel
)

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1", tags=["Unified API"])


# Request/Response Models
class ChatAPIRequest(BaseModel):
    """API request model for chat"""
    message: str = Field(..., description="User message")
    session_id: Optional[str] = Field(default=None, description="Session ID")
    user_id: str = Field(default="user", description="User ID")
    context: str = Field(default="blended_intelligence", description="Chat context")
    access_level: str = Field(default="employee", description="User access level")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")


class SessionInfo(BaseModel):
    """Session information model"""
    session_id: str
    user_id: str
    created_at: str
    last_activity: str
    message_count: int
    context: str


class HealthStatus(BaseModel):
    """Health status model"""
    status: str
    timestamp: str
    services: Dict[str, str]
    version: str = "1.0.0"


# WebSocket Connection Manager
class ConnectionManager:
    """Manage WebSocket connections for real-time chat"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        
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
                logger.error(f"Error sending message to {session_id}: {e}")
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


# API Endpoints
@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatAPIRequest,
    chat_service: UnifiedChatService = Depends(get_unified_chat_service)
):
    """
    Main chat endpoint - handles all chat requests
    
    Contexts:
    - business_intelligence: Business analysis and insights
    - ceo_deep_research: Executive-level strategic research
    - internal_only: Internal knowledge only
    - blended_intelligence: Mix of internal and external sources
    - mcp_tools: MCP server interactions
    - coding_agents: Code generation and assistance
    - infrastructure: Infrastructure management
    
    Access Levels:
    - ceo: Full access to all features
    - executive: Strategic features access
    - manager: Team and project data access
    - employee: Basic access
    """
    try:
        # Generate session ID if not provided
        if not request.session_id:
            request.session_id = str(uuid.uuid4())
            
        # Convert string context to enum
        try:
            context = ChatContext(request.context)
        except ValueError:
            context = ChatContext.BLENDED_INTELLIGENCE
            
        # Convert string access level to enum
        try:
            access_level = AccessLevel(request.access_level)
        except ValueError:
            access_level = AccessLevel.EMPLOYEE
            
        # Create chat request
        chat_request = ChatRequest(
            message=request.message,
            user_id=request.user_id,
            session_id=request.session_id,
            context=context,
            access_level=access_level,
            metadata=request.metadata
        )
        
        # Process chat
        response = await chat_service.process_chat(chat_request)
        
        # Send via WebSocket if connected
        await manager.send_message(request.session_id, {
            "type": "response",
            "data": {
                "response": response.response,
                "sources": response.sources,
                "suggestions": response.suggestions,
                "timestamp": response.timestamp
            }
        })
        
        return response
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/chat/sessions/{session_id}")
async def get_session(
    session_id: str,
    chat_service: UnifiedChatService = Depends(get_unified_chat_service)
):
    """Get session information and history"""
    try:
        history = await chat_service.get_session_history(session_id)
        
        if not history:
            raise HTTPException(status_code=404, detail="Session not found")
            
        # Calculate session info
        session_info = SessionInfo(
            session_id=session_id,
            user_id=history[0].get("user_id", "unknown") if history else "unknown",
            created_at=history[0].get("timestamp", "") if history else datetime.now().isoformat(),
            last_activity=history[-1].get("timestamp", "") if history else datetime.now().isoformat(),
            message_count=len(history),
            context=history[0].get("context", "unknown") if history else "unknown"
        )
        
        return {
            "session": session_info,
            "history": history
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get session error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/chat/sessions/{session_id}")
async def delete_session(
    session_id: str,
    chat_service: UnifiedChatService = Depends(get_unified_chat_service)
):
    """Delete a chat session"""
    try:
        success = await chat_service.clear_session(session_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Session not found")
            
        return {"message": f"Session {session_id} deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete session error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/chat/contexts")
async def get_available_contexts():
    """Get available chat contexts"""
    return {
        "contexts": [
            {
                "id": "business_intelligence",
                "name": "Business Intelligence",
                "description": "Business analysis and insights",
                "access_level": "employee"
            },
            {
                "id": "ceo_deep_research",
                "name": "CEO Deep Research",
                "description": "Executive-level strategic research",
                "access_level": "ceo"
            },
            {
                "id": "internal_only",
                "name": "Internal Knowledge",
                "description": "Internal knowledge base only",
                "access_level": "employee"
            },
            {
                "id": "blended_intelligence",
                "name": "Blended Intelligence",
                "description": "Mix of internal and external sources",
                "access_level": "employee"
            },
            {
                "id": "mcp_tools",
                "name": "MCP Tools",
                "description": "MCP server interactions",
                "access_level": "manager"
            },
            {
                "id": "coding_agents",
                "name": "Coding Assistance",
                "description": "Code generation and assistance",
                "access_level": "employee"
            },
            {
                "id": "infrastructure",
                "name": "Infrastructure",
                "description": "Infrastructure management",
                "access_level": "executive"
            }
        ]
    }


@router.get("/health", response_model=HealthStatus)
async def health_check(
    chat_service: UnifiedChatService = Depends(get_unified_chat_service)
):
    """Health check endpoint"""
    try:
        # Check service health
        services = {
            "chat_service": "healthy",
            "websocket": "healthy" if manager.active_connections else "idle",
            "database": "healthy"  # Add actual DB check
        }
        
        return HealthStatus(
            status="healthy" if all(s == "healthy" or s == "idle" for s in services.values()) else "degraded",
            timestamp=datetime.now().isoformat(),
            services=services
        )
        
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return HealthStatus(
            status="unhealthy",
            timestamp=datetime.now().isoformat(),
            services={"error": str(e)}
        )


# WebSocket endpoint for real-time chat
@router.websocket("/ws/chat/{session_id}")
async def websocket_chat(
    websocket: WebSocket,
    session_id: str,
    chat_service: UnifiedChatService = Depends(get_unified_chat_service)
):
    """WebSocket endpoint for real-time chat"""
    await manager.connect(websocket, session_id)
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_json()
            
            # Extract message data
            message = data.get("message", "")
            user_id = data.get("user_id", "anonymous")
            context = data.get("context", "blended_intelligence")
            access_level = data.get("access_level", "employee")
            
            if not message:
                await websocket.send_json({
                    "type": "error",
                    "message": "Message cannot be empty"
                })
                continue
                
            # Create chat request
            try:
                context_enum = ChatContext(context)
            except ValueError:
                context_enum = ChatContext.BLENDED_INTELLIGENCE
                
            try:
                access_enum = AccessLevel(access_level)
            except ValueError:
                access_enum = AccessLevel.EMPLOYEE
                
            chat_request = ChatRequest(
                message=message,
                user_id=user_id,
                session_id=session_id,
                context=context_enum,
                access_level=access_enum
            )
            
            # Send typing indicator
            await websocket.send_json({
                "type": "typing",
                "timestamp": datetime.now().isoformat()
            })
            
            # Process chat
            try:
                response = await chat_service.process_chat(chat_request)
                
                # Send response
                await websocket.send_json({
                    "type": "response",
                    "data": {
                        "response": response.response,
                        "sources": response.sources,
                        "suggestions": response.suggestions,
                        "timestamp": response.timestamp
                    }
                })
                
            except Exception as e:
                logger.error(f"Chat processing error: {e}")
                await websocket.send_json({
                    "type": "error",
                    "message": f"Error processing message: {str(e)}"
                })
                
    except WebSocketDisconnect:
        manager.disconnect(session_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(session_id)


# Legacy endpoint support (redirect to new endpoints)
@router.post("/ceo/chat", deprecated=True)
async def legacy_ceo_chat(request: dict):
    """Legacy CEO chat endpoint - redirects to unified chat"""
    return await chat(ChatAPIRequest(
        message=request.get("message", ""),
        session_id=request.get("session_id"),
        user_id=request.get("user_id", "ceo"),
        context="ceo_deep_research",
        access_level="ceo"
    ))


@router.post("/universal-chat", deprecated=True)
async def legacy_universal_chat(request: dict):
    """Legacy universal chat endpoint - redirects to unified chat"""
    return await chat(ChatAPIRequest(
        message=request.get("message", ""),
        session_id=request.get("session_id"),
        user_id=request.get("user_id", "user"),
        context="blended_intelligence",
        access_level="employee"
    ))


@router.post("/sophia-chat", deprecated=True)
async def legacy_sophia_chat(request: dict):
    """Legacy Sophia chat endpoint - redirects to unified chat"""
    return await chat(ChatAPIRequest(
        message=request.get("message", ""),
        session_id=request.get("session_id"),
        user_id=request.get("user_id", "user"),
        context="business_intelligence",
        access_level="employee"
    ))


@router.post("/chat/approve/{approval_id}")
async def approve_code_changes(
    approval_id: str,
    chat_service: UnifiedChatService = Depends(get_unified_chat_service)
) -> Dict[str, Any]:
    """
    Approve pending code changes
    
    Args:
        approval_id: ID of the pending approval
        
    Returns:
        Result of applying the changes
    """
    result = await chat_service.apply_pending_changes(approval_id)
    
    return {
        "success": result["success"],
        "file_path": result.get("file_path"),
        "error": result.get("error")
    }
    

@router.post("/chat/reject/{approval_id}")
async def reject_code_changes(
    approval_id: str,
    chat_service: UnifiedChatService = Depends(get_unified_chat_service)
) -> Dict[str, Any]:
    """
    Reject pending code changes
    
    Args:
        approval_id: ID of the pending approval
        
    Returns:
        Result of rejection
    """
    result = await chat_service.reject_pending_changes(approval_id)
    
    return {
        "success": result["success"],
        "file_path": result.get("file_path"),
        "error": result.get("error")
    }


# Dependency injection helpers
def get_enhanced_chat_service() -> UnifiedChatService:
    """Get enhanced chat service instance"""
    return UnifiedChatService() 