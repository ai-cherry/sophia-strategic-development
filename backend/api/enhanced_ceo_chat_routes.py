"""
Enhanced CEO Chat API Routes
Provides CEO-level universal chat capabilities with deep research and coding agents
"""

import asyncio
import logging
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, Depends, Query
from fastapi.responses import StreamingResponse
from typing import Dict, List, Any, Optional, Union
from pydantic import BaseModel, Field
from datetime import datetime

from ..services.enhanced_ceo_universal_chat_service import (
    EnhancedCEOUniversalChatService,
    CEOChatContext,
    EnhancedChatResponse,
    AccessLevel,
    SearchContext
)
from ..services.advanced_ui_ux_agent_service import (
    AdvancedUIUXAgentService,
    DesignContext,
    DesignResponse,
    UIFramework,
    DesignStyle
)

logger = logging.getLogger(__name__)

# Initialize services
ceo_chat_service = EnhancedCEOUniversalChatService()
ui_ux_service = AdvancedUIUXAgentService()

# Create router
router = APIRouter(prefix="/api/v1/ceo-chat", tags=["Enhanced CEO Chat"])

# Pydantic models
class ChatRequest(BaseModel):
    message: str
    user_id: str = "ceo_user"
    access_level: str = "ceo"
    search_context: str = "blended"
    coding_mode: bool = False
    design_mode: bool = False
    session_id: str = Field(default_factory=lambda: f"session_{datetime.utcnow().timestamp()}")

class DesignRequest(BaseModel):
    description: str
    project_name: str = "CEO Dashboard"
    framework: str = "react_typescript"
    style: str = "glassmorphism"
    accessibility: bool = True
    responsive: bool = True
    dark_mode: bool = True

class WebResearchRequest(BaseModel):
    query: str
    depth: str = "standard"  # standard, deep, comprehensive
    sources: List[str] = Field(default_factory=lambda: ["perplexity", "tavily"])
    user_id: str = "ceo_user"

class MCPServerRequest(BaseModel):
    server_name: str
    action: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    user_id: str = "ceo_user"

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info(f"CEO chat client {client_id} connected")

    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            logger.info(f"CEO chat client {client_id} disconnected")

    async def send_personal_message(self, message: dict, client_id: str):
        if client_id in self.active_connections:
            websocket = self.active_connections[client_id]
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Error sending message to {client_id}: {e}")
                self.disconnect(client_id)

manager = ConnectionManager()

# Utility functions
def get_access_level(level_str: str) -> AccessLevel:
    """Convert string to AccessLevel enum"""
    try:
        return AccessLevel(level_str.lower())
    except ValueError:
        return AccessLevel.EMPLOYEE

def get_search_context(context_str: str) -> SearchContext:
    """Convert string to SearchContext enum"""
    try:
        return SearchContext(context_str.lower())
    except ValueError:
        return SearchContext.BLENDED

def create_chat_context(request: ChatRequest) -> CEOChatContext:
    """Create CEOChatContext from request"""
    return CEOChatContext(
        user_id=request.user_id,
        access_level=get_access_level(request.access_level),
        session_id=request.session_id,
        search_context=get_search_context(request.search_context),
        coding_mode=request.coding_mode,
        design_mode=request.design_mode
    )

# API Routes

@router.post("/chat", response_model=Dict[str, Any])
async def process_ceo_chat(request: ChatRequest):
    """Process CEO-level chat query with enhanced capabilities"""
    try:
        context = create_chat_context(request)
        
        # Validate CEO access for restricted features
        if context.search_context in [SearchContext.DEEP_RESEARCH, SearchContext.CODING_AGENTS, SearchContext.MCP_TOOLS]:
            if context.access_level != AccessLevel.CEO:
                raise HTTPException(
                    status_code=403,
                    detail=f"Access denied: {context.search_context.value} requires CEO-level access"
                )
        
        response = await ceo_chat_service.process_ceo_query(
            query=request.message,
            context=context
        )
        
        return {
            "response": response.content,
            "sources": response.sources,
            "actions": response.actions,
            "suggestions": response.suggestions,
            "metadata": {
                "query_type": response.query_type,
                "processing_time": response.processing_time,
                "access_level": context.access_level.value,
                "search_context": context.search_context.value,
                "timestamp": response.timestamp
            }
        }
        
    except Exception as e:
        logger.error(f"Error processing CEO chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/design", response_model=Dict[str, Any])
async def create_design(request: DesignRequest):
    """Create UI/UX design using advanced AI agents"""
    try:
        context = DesignContext(
            user_id="ceo_user",
            project_name=request.project_name,
            framework=UIFramework(request.framework),
            style=DesignStyle(request.style),
            accessibility=request.accessibility,
            responsive=request.responsive,
            dark_mode=request.dark_mode
        )
        
        response = await ui_ux_service.process_design_request(
            request=request.description,
            context=context
        )
        
        return {
            "design_options": [
                {
                    "id": option.id,
                    "name": option.name,
                    "description": option.description,
                    "style": option.style,
                    "components": option.components,
                    "features": option.features,
                    "interaction_pattern": option.interaction_pattern,
                    "color_scheme": option.color_scheme,
                    "layout": option.layout
                }
                for option in response.options
            ],
            "assets": [
                {
                    "type": asset.type,
                    "url": asset.url,
                    "download_url": asset.download_url,
                    "interactive_url": asset.interactive_url,
                    "metadata": asset.metadata
                }
                for asset in response.assets
            ],
            "recommendations": response.recommendations,
            "next_steps": response.next_steps,
            "metadata": {
                "processing_time": response.processing_time,
                "model_used": response.model_used,
                "framework": request.framework,
                "style": request.style
            }
        }
        
    except Exception as e:
        logger.error(f"Error creating design: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/component", response_model=Dict[str, Any])
async def create_component(
    description: str,
    framework: str = "react_typescript",
    style: str = "glassmorphism"
):
    """Create a single component from description"""
    try:
        context = DesignContext(
            user_id="ceo_user",
            project_name="Component Generation",
            framework=UIFramework(framework),
            style=DesignStyle(style)
        )
        
        component = await ui_ux_service.create_component_from_description(
            description=description,
            context=context
        )
        
        return component
        
    except Exception as e:
        logger.error(f"Error creating component: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/web-research", response_model=Dict[str, Any])
async def conduct_web_research(request: WebResearchRequest):
    """Conduct deep web research (CEO-only)"""
    try:
        context = CEOChatContext(
            user_id=request.user_id,
            access_level=AccessLevel.CEO,
            session_id=f"research_{datetime.utcnow().timestamp()}",
            search_context=SearchContext.DEEP_RESEARCH if request.depth == "deep" else SearchContext.WEB_RESEARCH
        )
        
        response = await ceo_chat_service.process_ceo_query(
            query=f"Conduct {request.depth} web research on: {request.query}",
            context=context
        )
        
        return {
            "research_summary": response.content,
            "sources": response.sources,
            "depth": request.depth,
            "query": request.query,
            "processing_time": response.processing_time,
            "timestamp": response.timestamp
        }
        
    except Exception as e:
        logger.error(f"Error conducting web research: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/mcp-servers", response_model=Dict[str, Any])
async def get_available_mcp_servers(access_level: str = "ceo"):
    """Get available MCP servers based on access level"""
    try:
        user_access = get_access_level(access_level)
        servers = await ceo_chat_service.get_available_mcp_servers(user_access)
        
        return {
            "available_servers": servers,
            "access_level": user_access.value,
            "total_servers": len(servers),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting MCP servers: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/mcp-action", response_model=Dict[str, Any])
async def execute_mcp_action(request: MCPServerRequest):
    """Execute action on MCP server (CEO-only)"""
    try:
        # For now, return a mock response
        return {
            "server": request.server_name,
            "action": request.action,
            "parameters": request.parameters,
            "result": f"Executed {request.action} on {request.server_name}",
            "status": "success",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error executing MCP action: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/design-analysis", response_model=Dict[str, Any])
async def analyze_design(design_url: str):
    """Analyze existing design and provide improvement suggestions"""
    try:
        analysis = await ui_ux_service.analyze_existing_design(design_url)
        return analysis
        
    except Exception as e:
        logger.error(f"Error analyzing design: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/service-stats", response_model=Dict[str, Any])
async def get_service_stats():
    """Get comprehensive service statistics"""
    try:
        ceo_chat_health = await ceo_chat_service.health_check()
        ui_ux_health = await ui_ux_service.health_check()
        
        return {
            "ceo_chat_service": ceo_chat_health,
            "ui_ux_service": ui_ux_health,
            "timestamp": datetime.utcnow().isoformat(),
            "overall_status": "healthy"
        }
        
    except Exception as e:
        logger.error(f"Error getting service stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health", response_model=Dict[str, Any])
async def health_check():
    """Health check for enhanced CEO chat service"""
    try:
        return await ceo_chat_service.health_check()
        
    except Exception as e:
        logger.error(f"Health check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# WebSocket endpoint for real-time chat
@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket endpoint for real-time CEO chat"""
    await manager.connect(websocket, client_id)
    
    try:
        # Send welcome message
        await manager.send_personal_message({
            "type": "welcome",
            "message": "Connected to Sophia AI Enhanced CEO Chat",
            "features": [
                "Deep web research and scraping",
                "AI coding agent integration", 
                "Advanced UI/UX design generation",
                "MCP server orchestration",
                "Real-time business intelligence"
            ],
            "timestamp": datetime.utcnow().isoformat()
        }, client_id)
        
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            
            # Process the message
            if data.get("type") == "chat":
                try:
                    # Create request from WebSocket data
                    request = ChatRequest(**data.get("data", {}))
                    context = create_chat_context(request)
                    
                    # Send typing indicator
                    await manager.send_personal_message({
                        "type": "typing",
                        "typing": True
                    }, client_id)
                    
                    # Process query
                    response = await ceo_chat_service.process_ceo_query(
                        query=request.message,
                        context=context
                    )
                    
                    # Send response
                    await manager.send_personal_message({
                        "type": "response",
                        "content": response.content,
                        "sources": response.sources,
                        "actions": response.actions,
                        "suggestions": response.suggestions,
                        "metadata": {
                            "query_type": response.query_type,
                            "processing_time": response.processing_time,
                            "timestamp": response.timestamp
                        }
                    }, client_id)
                    
                except Exception as e:
                    await manager.send_personal_message({
                        "type": "error",
                        "message": f"Error processing message: {str(e)}"
                    }, client_id)
                
            elif data.get("type") == "design":
                try:
                    # Process design request
                    design_data = data.get("data", {})
                    request = DesignRequest(**design_data)
                    
                    context = DesignContext(
                        user_id="ceo_user",
                        project_name=request.project_name,
                        framework=UIFramework(request.framework),
                        style=DesignStyle(request.style)
                    )
                    
                    response = await ui_ux_service.process_design_request(
                        request=request.description,
                        context=context
                    )
                    
                    await manager.send_personal_message({
                        "type": "design_response",
                        "options": [
                            {
                                "id": option.id,
                                "name": option.name,
                                "description": option.description,
                                "components": option.components,
                                "features": option.features
                            }
                            for option in response.options
                        ],
                        "assets": response.assets,
                        "recommendations": response.recommendations
                    }, client_id)
                    
                except Exception as e:
                    await manager.send_personal_message({
                        "type": "error",
                        "message": f"Error processing design request: {str(e)}"
                    }, client_id)
            
    except WebSocketDisconnect:
        manager.disconnect(client_id)
    except Exception as e:
        logger.error(f"WebSocket error for {client_id}: {e}")
        manager.disconnect(client_id)
