"""Unified Chat API Routes for Sophia AI"""

from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from backend.core.auth import get_current_user
from backend.services.knowledge_service import KnowledgeService
from backend.services.okr_service import OKRService
from backend.services.project_management_service import ProjectManagementService
from backend.services.system_monitoring_service import SystemMonitoringService
from backend.services.unified_chat_service import UnifiedChatService

router = APIRouter(prefix="/api/v3", tags=["unified-chat"])

# Services
chat_service = UnifiedChatService()
knowledge_service = KnowledgeService()
project_service = ProjectManagementService()
system_service = SystemMonitoringService()
okr_service = OKRService()


class ChatRequest(BaseModel):
    message: str
    context: str = "chat"
    sessionId: str
    metadata: Optional[dict[str, Any]] = None


class ChatResponse(BaseModel):
    response: str
    citations: Optional[list[dict[str, Any]]] = None
    metadata: Optional[dict[str, Any]] = None


@router.post("/chat/unified", response_model=ChatResponse)
async def unified_chat(
    request: ChatRequest, current_user: dict = Depends(get_current_user)
):
    """
    Unified chat endpoint that routes to appropriate services based on context
    """
    try:
        # Route based on context
        if request.context == "knowledge":
            response = await knowledge_service.process_query(
                query=request.message,
                user_id=current_user["id"],
                session_id=request.sessionId,
            )
        elif request.context == "projects":
            response = await project_service.process_query(
                query=request.message,
                user_id=current_user["id"],
                session_id=request.sessionId,
            )
        elif request.context == "system":
            response = await system_service.process_query(
                query=request.message,
                user_id=current_user["id"],
                session_id=request.sessionId,
            )
        elif request.context == "okrs":
            response = await okr_service.process_query(
                query=request.message,
                user_id=current_user["id"],
                session_id=request.sessionId,
            )
        else:
            # Default unified chat across all contexts
            response = await chat_service.process_unified_query(
                query=request.message,
                user_id=current_user["id"],
                session_id=request.sessionId,
                context=request.context,
            )

        return ChatResponse(
            response=response.get("response", ""),
            citations=response.get("citations", []),
            metadata=response.get("metadata", {}),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/knowledge/stats")
async def get_knowledge_stats(current_user: dict = Depends(get_current_user)):
    """Get knowledge base statistics"""
    try:
        stats = await knowledge_service.get_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/knowledge/recent")
async def get_recent_documents(
    limit: int = 10, current_user: dict = Depends(get_current_user)
):
    """Get recent documents from knowledge base"""
    try:
        docs = await knowledge_service.get_recent_documents(limit=limit)
        return docs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/projects/summary")
async def get_project_summary(current_user: dict = Depends(get_current_user)):
    """Get project management summary across all platforms"""
    try:
        summary = await project_service.get_unified_summary()
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/projects/active")
async def get_active_projects(
    limit: int = 10, current_user: dict = Depends(get_current_user)
):
    """Get active projects across all platforms"""
    try:
        projects = await project_service.get_active_projects(limit=limit)
        return projects
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/system/health")
async def get_system_health(current_user: dict = Depends(get_current_user)):
    """Get overall system health status"""
    try:
        health = await system_service.get_overall_health()
        return health
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/system/mcp-servers")
async def get_mcp_server_status(current_user: dict = Depends(get_current_user)):
    """Get MCP server status"""
    try:
        servers = await system_service.get_mcp_server_status()
        return servers
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/system/metrics")
async def get_system_metrics(current_user: dict = Depends(get_current_user)):
    """Get system performance metrics"""
    try:
        metrics = await system_service.get_performance_metrics()
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/okrs/current")
async def get_current_okrs(current_user: dict = Depends(get_current_user)):
    """Get current quarter OKRs"""
    try:
        okrs = await okr_service.get_current_okrs()
        return okrs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/okrs/progress")
async def get_okr_progress(current_user: dict = Depends(get_current_user)):
    """Get OKR progress summary"""
    try:
        progress = await okr_service.get_progress_summary()
        return progress
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/okrs/update")
async def update_okr_progress(
    objective_id: str,
    key_result_id: str,
    current_value: float,
    current_user: dict = Depends(get_current_user),
):
    """Update OKR key result progress"""
    try:
        if current_user.get("role") not in ["admin", "executive"]:
            raise HTTPException(status_code=403, detail="Insufficient permissions")

        result = await okr_service.update_key_result(
            objective_id=objective_id,
            key_result_id=key_result_id,
            current_value=current_value,
            updated_by=current_user["id"],
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
