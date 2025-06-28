#!/usr/bin/env python3
"""
Sophia Universal Chat API Routes
RESTful and WebSocket endpoints for the ultimate conversational AI experience
"""

import logging
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Depends
from pydantic import BaseModel

from backend.services.sophia_universal_chat_service import (
    SophiaUniversalChatService, 
    SophiaPersonality,
    UserAccessLevel,
    SearchContext
)

logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(prefix="/api/v1/sophia", tags=["sophia-universal-chat"])

# Global service instance
sophia_service: Optional[SophiaUniversalChatService] = None

# Pydantic models for API
class ChatMessageRequest(BaseModel):
    message: str
    user_id: str = "ceo"
    context: Optional[Dict[str, Any]] = None
    personality_override: Optional[str] = None

class ChatMessageResponse(BaseModel):
    content: str
    sources: List[Dict[str, Any]]
    confidence_score: float
    search_time_ms: int
    personality_applied: str
    internal_results_count: int
    internet_results_count: int
    synthesis_quality: float

class UserProfileRequest(BaseModel):
    user_id: str
    name: str
    email: str
    access_level: str
    department: str
    search_permissions: Optional[List[str]] = ["internal_only"]
    preferred_personality: Optional[str] = "friendly_assistant"
    api_quota_daily: Optional[int] = 1000

class UserPermissionUpdate(BaseModel):
    access_level: Optional[str] = None
    search_permissions: Optional[List[str]] = None
    api_quota_daily: Optional[int] = None
    preferred_personality: Optional[str] = None

class WebSocketMessage(BaseModel):
    type: str
    message: Optional[str] = None
    user_id: Optional[str] = "ceo"
    context: Optional[Dict[str, Any]] = None

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.user_sessions: Dict[str, str] = {}  # user_id -> connection_id

    async def connect(self, websocket: WebSocket, connection_id: str, user_id: str = "ceo"):
        await websocket.accept()
        self.active_connections[connection_id] = websocket
        self.user_sessions[user_id] = connection_id
        logger.info(f"WebSocket connected: {connection_id} for user {user_id}")

    def disconnect(self, connection_id: str, user_id: str = "ceo"):
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]
        if user_id in self.user_sessions:
            del self.user_sessions[user_id]
        logger.info(f"WebSocket disconnected: {connection_id}")

    async def send_personal_message(self, message: dict, connection_id: str):
        if connection_id in self.active_connections:
            try:
                await self.active_connections[connection_id].send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Failed to send message to {connection_id}: {e}")
                self.active_connections.pop(connection_id, None)

    async def send_to_user(self, message: dict, user_id: str):
        connection_id = self.user_sessions.get(user_id)
        if connection_id:
            await self.send_personal_message(message, connection_id)

manager = ConnectionManager()

async def get_sophia_service() -> SophiaUniversalChatService:
    """Get or initialize Sophia service"""
    global sophia_service
    if sophia_service is None:
        sophia_service = SophiaUniversalChatService()
        await sophia_service.initialize()
    return sophia_service

# REST API Endpoints

@router.post("/chat/message", response_model=ChatMessageResponse)
async def send_chat_message(
    request: ChatMessageRequest,
    service: SophiaUniversalChatService = Depends(get_sophia_service)
) -> ChatMessageResponse:
    """
    Send a message to Sophia AI and get intelligent response
    
    Features:
    - Blended internal/internet search
    - Personality-driven responses
    - User access level awareness
    - Source attribution
    """
    try:
        # Apply personality override if provided
        if request.personality_override:
            user_profile = service.user_profiles.get(request.user_id)
            if user_profile:
                original_personality = user_profile.preferred_personality
                user_profile.preferred_personality = SophiaPersonality(request.personality_override)
        
        # Process message
        result = await service.process_chat_message(
            message=request.message,
            user_id=request.user_id,
            context=request.context or {}
        )
        
        # Restore original personality if overridden
        if request.personality_override:
            user_profile = service.user_profiles.get(request.user_id)
            if user_profile:
                user_profile.preferred_personality = original_personality
        
        return ChatMessageResponse(
            content=result.content,
            sources=result.sources,
            confidence_score=result.confidence_score,
            search_time_ms=result.search_time_ms,
            personality_applied=result.personality_applied.value,
            internal_results_count=len(result.internal_results),
            internet_results_count=len(result.internet_results),
            synthesis_quality=result.synthesis_quality
        )
        
    except Exception as e:
        logger.error(f"Chat message processing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process message: {str(e)}")

@router.get("/chat/personalities")
async def get_available_personalities() -> Dict[str, Any]:
    """Get all available Sophia personalities with descriptions"""
    service = await get_sophia_service()
    
    personalities = {}
    for personality in SophiaPersonality:
        template = service.personality_templates[personality]
        personalities[personality.value] = {
            "name": personality.value.replace("_", " ").title(),
            "tone": template["tone"],
            "style": template["style"],
            "focus": template["focus"],
            "greeting": template["greeting"]
        }
    
    return {"personalities": personalities}

@router.get("/search/contexts")
async def get_search_contexts() -> Dict[str, Any]:
    """Get all available search contexts with descriptions"""
    contexts = {}
    for context in SearchContext:
        descriptions = {
            SearchContext.INTERNAL_ONLY: "Search only internal company data and schemas",
            SearchContext.INTERNET_ONLY: "Search only internet sources and external intelligence",
            SearchContext.BLENDED_INTELLIGENCE: "Combine internal data with internet intelligence",
            SearchContext.CEO_DEEP_RESEARCH: "Comprehensive research with advanced scraping (CEO only)"
        }
        
        contexts[context.value] = {
            "name": context.value.replace("_", " ").title(),
            "description": descriptions.get(context, "Advanced search capability"),
            "requires_permission": context in [SearchContext.CEO_DEEP_RESEARCH]
        }
    
    return {"search_contexts": contexts}

# User Management Endpoints (CEO Dashboard Integration)

@router.post("/users", response_model=Dict[str, Any])
async def create_user_profile(
    request: UserProfileRequest,
    creator_id: str = "ceo",
    service: SophiaUniversalChatService = Depends(get_sophia_service)
) -> Dict[str, Any]:
    """Create new user profile (CEO dashboard functionality)"""
    try:
        user_data = request.dict()
        user_profile = await service.create_user_profile(user_data, creator_id)
        
        return {
            "success": True,
            "user_id": user_profile.user_id,
            "message": f"User profile created for {user_profile.name}",
            "profile": {
                "user_id": user_profile.user_id,
                "name": user_profile.name,
                "email": user_profile.email,
                "access_level": user_profile.access_level.value,
                "department": user_profile.department,
                "accessible_schemas": user_profile.accessible_schemas,
                "search_permissions": [perm.value for perm in user_profile.search_permissions],
                "preferred_personality": user_profile.preferred_personality.value,
                "api_quota_daily": user_profile.api_quota_daily
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to create user profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/users")
async def list_users(
    service: SophiaUniversalChatService = Depends(get_sophia_service)
) -> Dict[str, Any]:
    """Get all user profiles"""
    try:
        users = []
        for user_profile in service.user_profiles.values():
            users.append({
                "user_id": user_profile.user_id,
                "name": user_profile.name,
                "email": user_profile.email,
                "access_level": user_profile.access_level.value,
                "department": user_profile.department,
                "api_usage_today": user_profile.api_usage_today,
                "api_quota_daily": user_profile.api_quota_daily,
                "last_active": user_profile.last_active.isoformat(),
                "preferred_personality": user_profile.preferred_personality.value
            })
        
        return {"users": users, "total_count": len(users)}
        
    except Exception as e:
        logger.error(f"Failed to list users: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/users/{user_id}")
async def get_user_profile(
    user_id: str,
    service: SophiaUniversalChatService = Depends(get_sophia_service)
) -> Dict[str, Any]:
    """Get specific user profile"""
    try:
        user_profile = service.user_profiles.get(user_id)
        if not user_profile:
            raise HTTPException(status_code=404, detail=f"User {user_id} not found")
        
        return {
            "user_id": user_profile.user_id,
            "name": user_profile.name,
            "email": user_profile.email,
            "access_level": user_profile.access_level.value,
            "department": user_profile.department,
            "accessible_schemas": user_profile.accessible_schemas,
            "search_permissions": [perm.value for perm in user_profile.search_permissions],
            "preferred_personality": user_profile.preferred_personality.value,
            "api_quota_daily": user_profile.api_quota_daily,
            "api_usage_today": user_profile.api_usage_today,
            "usage_percentage": (user_profile.api_usage_today / user_profile.api_quota_daily) * 100,
            "created_at": user_profile.created_at.isoformat(),
            "last_active": user_profile.last_active.isoformat(),
            "custom_context": user_profile.custom_context
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get user profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/users/{user_id}/permissions")
async def update_user_permissions(
    user_id: str,
    request: UserPermissionUpdate,
    updater_id: str = "ceo",
    service: SophiaUniversalChatService = Depends(get_sophia_service)
) -> Dict[str, Any]:
    """Update user permissions (CEO only)"""
    try:
        # Verify updater has CEO access
        updater = service.user_profiles.get(updater_id)
        if not updater or updater.access_level != UserAccessLevel.CEO:
            raise HTTPException(status_code=403, detail="Only CEO can update user permissions")
        
        user_profile = service.user_profiles.get(user_id)
        if not user_profile:
            raise HTTPException(status_code=404, detail=f"User {user_id} not found")
        
        # Update permissions
        updates = request.dict(exclude_unset=True)
        
        if "access_level" in updates:
            new_level = UserAccessLevel(updates["access_level"])
            user_profile.access_level = new_level
            user_profile.accessible_schemas = service.schema_access_map[new_level]
        
        if "search_permissions" in updates:
            user_profile.search_permissions = [
                SearchContext(perm) for perm in updates["search_permissions"]
            ]
        
        if "api_quota_daily" in updates:
            user_profile.api_quota_daily = updates["api_quota_daily"]
        
        if "preferred_personality" in updates:
            user_profile.preferred_personality = SophiaPersonality(updates["preferred_personality"])
        
        # Save changes
        await service._save_user_profile(user_profile)
        
        return {
            "success": True,
            "message": f"Updated permissions for {user_profile.name}",
            "updated_fields": list(updates.keys())
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update user permissions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/users")
async def get_user_analytics(
    user_id: Optional[str] = None,
    service: SophiaUniversalChatService = Depends(get_sophia_service)
) -> Dict[str, Any]:
    """Get user analytics for CEO dashboard"""
    try:
        analytics = await service.get_user_analytics(user_id)
        return {
            "success": True,
            "analytics": analytics,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get user analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check(
    service: SophiaUniversalChatService = Depends(get_sophia_service)
) -> Dict[str, Any]:
    """Health check for Sophia Universal Chat Service"""
    try:
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "service_initialized": service is not None,
            "total_users": len(service.user_profiles) if service else 0,
        }
        
        return health_status
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# WebSocket Endpoint for Real-time Chat

@router.websocket("/chat/ws/{connection_id}")
async def websocket_chat_endpoint(
    websocket: WebSocket, 
    connection_id: str,
    user_id: str = "ceo"
):
    """
    WebSocket endpoint for real-time chat with Sophia AI
    
    Message Types:
    - init: Initialize connection
    - chat_message: Send message to Sophia
    - personality_change: Change Sophia's personality
    - search_context_change: Change search context
    """
    try:
        await manager.connect(websocket, connection_id, user_id)
        service = await get_sophia_service()
        
        # Send welcome message
        await manager.send_personal_message({
            "type": "connected",
            "message": "Connected to Sophia AI Universal Chat",
            "user_id": user_id,
            "available_personalities": [p.value for p in SophiaPersonality],
            "available_search_contexts": [c.value for c in SearchContext],
            "timestamp": datetime.now().isoformat()
        }, connection_id)
        
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            message_type = message_data.get("type")
            
            if message_type == "chat_message":
                # Send typing indicator
                await manager.send_personal_message({
                    "type": "typing",
                    "is_typing": True
                }, connection_id)
                
                try:
                    # Process chat message
                    result = await service.process_chat_message(
                        message=message_data.get("message", ""),
                        user_id=user_id,
                        context=message_data.get("context", {})
                    )
                    
                    # Send response
                    await manager.send_personal_message({
                        "type": "chat_response",
                        "content": result.content,
                        "sources": result.sources,
                        "confidence_score": result.confidence_score,
                        "search_time_ms": result.search_time_ms,
                        "personality_applied": result.personality_applied.value,
                        "internal_results_count": len(result.internal_results),
                        "internet_results_count": len(result.internet_results),
                        "synthesis_quality": result.synthesis_quality,
                        "timestamp": datetime.now().isoformat()
                    }, connection_id)
                    
                except Exception as e:
                    await manager.send_personal_message({
                        "type": "error",
                        "message": f"Failed to process message: {str(e)}",
                        "timestamp": datetime.now().isoformat()
                    }, connection_id)
                
                finally:
                    # Stop typing indicator
                    await manager.send_personal_message({
                        "type": "typing",
                        "is_typing": False
                    }, connection_id)
            
            elif message_type == "personality_change":
                try:
                    new_personality = SophiaPersonality(message_data.get("personality"))
                    user_profile = service.user_profiles.get(user_id)
                    if user_profile:
                        user_profile.preferred_personality = new_personality
                    
                    await manager.send_personal_message({
                        "type": "personality_changed",
                        "personality": new_personality.value,
                        "message": f"Sophia's personality changed to {new_personality.value.replace('_', ' ').title()}",
                        "timestamp": datetime.now().isoformat()
                    }, connection_id)
                    
                except Exception as e:
                    await manager.send_personal_message({
                        "type": "error",
                        "message": f"Failed to change personality: {str(e)}",
                        "timestamp": datetime.now().isoformat()
                    }, connection_id)
            
            elif message_type == "ping":
                await manager.send_personal_message({
                    "type": "pong",
                    "timestamp": datetime.now().isoformat()
                }, connection_id)
            
            else:
                await manager.send_personal_message({
                    "type": "error",
                    "message": f"Unknown message type: {message_type}",
                    "timestamp": datetime.now().isoformat()
                }, connection_id)
                
    except WebSocketDisconnect:
        manager.disconnect(connection_id, user_id)
        logger.info(f"WebSocket disconnected: {connection_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(connection_id, user_id)

# Startup event to initialize service
@router.on_event("startup")
async def startup_event():
    """Initialize Sophia service on startup"""
    try:
        global sophia_service
        sophia_service = SophiaUniversalChatService()
        await sophia_service.initialize()
        logger.info("✅ Sophia Universal Chat Service started")
    except Exception as e:
        logger.error(f"❌ Failed to start Sophia Universal Chat Service: {e}")

# Shutdown event to cleanup
@router.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    try:
        global sophia_service
        if sophia_service:
            await sophia_service.close()
        logger.info("✅ Sophia Universal Chat Service stopped")
    except Exception as e:
        logger.error(f"❌ Failed to stop Sophia Universal Chat Service: {e}") 
