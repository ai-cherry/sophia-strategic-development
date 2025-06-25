#!/usr/bin/env python3
"""
Sophia AI Phase 1 API Routes
Unified API for Enhanced Knowledge Base, Interactive Sales Coach, and Memory Preservation
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field

from backend.services.sophia_ai_orchestrator import (
    SophiaAIOrchestrator, 
    OrchestrationRequest, 
    RequestType, 
    OrchestrationMode
)

logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(prefix="/api/v1/sophia-ai", tags=["Sophia AI Phase 1"])

# Global orchestrator instance
orchestrator: Optional[SophiaAIOrchestrator] = None


# Pydantic Models
class KnowledgeQueryRequest(BaseModel):
    """Request model for knowledge queries"""
    query: str = Field(..., description="Knowledge query text")
    context: Dict[str, Any] = Field(default_factory=dict, description="Query context")
    user_id: str = Field(..., description="User ID making the request")
    limit: int = Field(default=5, description="Maximum number of results")


class KnowledgeIngestionRequest(BaseModel):
    """Request model for knowledge ingestion"""
    content: str = Field(..., description="Knowledge content to ingest")
    source: str = Field(default="manual", description="Source of the knowledge")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    user_id: str = Field(..., description="User ID ingesting the knowledge")


class SalesCoachingRequest(BaseModel):
    """Request model for sales coaching"""
    sales_rep_id: str = Field(..., description="Sales representative ID")
    context: Dict[str, Any] = Field(..., description="Coaching context")
    query: Optional[str] = Field(None, description="Specific coaching query")
    coaching_type: Optional[str] = Field(None, description="Type of coaching needed")


class TeachingSessionRequest(BaseModel):
    """Request model for teaching sessions"""
    teaching_data: Dict[str, Any] = Field(..., description="Teaching session data")
    user_id: str = Field(..., description="User ID conducting the teaching")
    knowledge_id: Optional[str] = Field(None, description="Knowledge ID being taught")


class MemoryPreservationRequest(BaseModel):
    """Request model for memory preservation"""
    operation: str = Field(..., description="Preservation operation type")
    source_systems: Optional[List[str]] = Field(None, description="Source systems to preserve from")
    context: Dict[str, Any] = Field(default_factory=dict, description="Operation context")


class SlackEventRequest(BaseModel):
    """Request model for Slack events"""
    event_type: str = Field(..., description="Type of Slack event")
    user: str = Field(..., description="Slack user ID")
    channel: str = Field(..., description="Slack channel ID")
    text: Optional[str] = Field(None, description="Message text")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional event metadata")


class UnifiedIntelligenceRequest(BaseModel):
    """Request model for unified intelligence queries"""
    query: str = Field(..., description="Intelligence query")
    user_id: str = Field(..., description="User ID making the request")
    context: Dict[str, Any] = Field(default_factory=dict, description="Query context")
    mode: str = Field(default="unified_intelligence", description="Orchestration mode")
    priority: int = Field(default=1, description="Request priority (1=high, 3=low)")


# Dependency to get initialized orchestrator
async def get_orchestrator() -> SophiaAIOrchestrator:
    """Get initialized orchestrator instance"""
    global orchestrator
    
    if orchestrator is None:
        orchestrator = SophiaAIOrchestrator()
        await orchestrator.initialize()
    
    return orchestrator


# API Routes

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        orch = await get_orchestrator()
        
        request = OrchestrationRequest(
            request_id=f"health_{int(datetime.now().timestamp())}",
            request_type=RequestType.HEALTH_CHECK,
            user_id="system",
            context={"source": "api_health_check"}
        )
        
        response = await orch.process_request(request)
        
        return {
            "status": "healthy" if response.success else "degraded",
            "timestamp": datetime.now().isoformat(),
            "services": response.primary_response.get("service_health", {}),
            "orchestrator_ready": True
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")


@router.post("/knowledge/query")
async def query_knowledge(request: KnowledgeQueryRequest):
    """Query the enhanced knowledge base"""
    try:
        orch = await get_orchestrator()
        
        orchestration_request = OrchestrationRequest(
            request_id=f"kb_query_{int(datetime.now().timestamp())}_{request.user_id}",
            request_type=RequestType.KNOWLEDGE_QUERY,
            user_id=request.user_id,
            query=request.query,
            context={
                **request.context,
                "limit": request.limit,
                "source": "api_knowledge_query"
            }
        )
        
        response = await orch.process_request(orchestration_request)
        
        if not response.success:
            raise HTTPException(status_code=400, detail=response.error or "Knowledge query failed")
        
        return {
            "success": True,
            "query": request.query,
            "results": response.primary_response.get("knowledge_items", []),
            "results_count": response.knowledge_items_accessed,
            "confidence_score": response.confidence_score,
            "processing_time_ms": response.processing_time_ms,
            "suggested_actions": response.suggested_actions,
            "related_queries": response.related_queries,
            "services_used": response.services_used
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Knowledge query failed: {e}")
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@router.post("/knowledge/ingest")
async def ingest_knowledge(request: KnowledgeIngestionRequest):
    """Ingest new knowledge into the system"""
    try:
        orch = await get_orchestrator()
        
        orchestration_request = OrchestrationRequest(
            request_id=f"kb_ingest_{int(datetime.now().timestamp())}_{request.user_id}",
            request_type=RequestType.KNOWLEDGE_INGESTION,
            user_id=request.user_id,
            content=request.content,
            metadata=request.metadata,
            context={
                "source": request.source,
                "ingestion_timestamp": datetime.now().isoformat()
            }
        )
        
        response = await orch.process_request(orchestration_request)
        
        if not response.success:
            raise HTTPException(status_code=400, detail=response.error or "Knowledge ingestion failed")
        
        return {
            "success": True,
            "knowledge_id": response.primary_response.get("knowledge_id"),
            "title": response.primary_response.get("title"),
            "knowledge_type": response.primary_response.get("knowledge_type"),
            "confidence_score": response.confidence_score,
            "tags": response.primary_response.get("tags", []),
            "enhancement_suggestions": response.primary_response.get("enhancement_suggestions", []),
            "processing_time_ms": response.processing_time_ms
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Knowledge ingestion failed: {e}")
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@router.post("/sales/coaching")
async def provide_sales_coaching(request: SalesCoachingRequest):
    """Provide AI-powered sales coaching"""
    try:
        orch = await get_orchestrator()
        
        orchestration_request = OrchestrationRequest(
            request_id=f"sales_coach_{int(datetime.now().timestamp())}_{request.sales_rep_id}",
            request_type=RequestType.SALES_COACHING_REQUEST,
            user_id=request.sales_rep_id,
            query=request.query,
            context={
                **request.context,
                "coaching_type": request.coaching_type,
                "source": "api_sales_coaching"
            }
        )
        
        response = await orch.process_request(orchestration_request)
        
        if not response.success:
            raise HTTPException(status_code=400, detail=response.error or "Sales coaching failed")
        
        return {
            "success": True,
            "sales_rep_id": request.sales_rep_id,
            "coaching_insights": response.primary_response.get("immediate_insights", []),
            "insights_generated": response.coaching_insights_generated,
            "knowledge_context": response.supporting_responses,
            "confidence_score": response.confidence_score,
            "suggested_actions": response.suggested_actions,
            "processing_time_ms": response.processing_time_ms
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Sales coaching failed: {e}")
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@router.post("/sales/slack-integration")
async def handle_slack_event(request: SlackEventRequest):
    """Handle Slack events for sales coaching integration"""
    try:
        orch = await get_orchestrator()
        
        # Convert Slack event to sales coaching context
        slack_event = {
            "type": request.event_type,
            "user": request.user,
            "channel": request.channel,
            "text": request.text,
            **request.metadata
        }
        
        # Use sales coach's Slack interface
        sales_coach = orch.sales_coach
        if not sales_coach:
            raise HTTPException(status_code=503, detail="Sales coach service not available")
        
        response = await sales_coach.slack_coaching_interface(slack_event)
        
        return {
            "success": response.get("success", False),
            "event_type": request.event_type,
            "user_id": request.user,
            "response": response.get("response", {}),
            "coaching_action": response.get("response", {}).get("type", "none")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Slack event handling failed: {e}")
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@router.post("/teaching/session")
async def conduct_teaching_session(request: TeachingSessionRequest):
    """Conduct interactive teaching session"""
    try:
        orch = await get_orchestrator()
        
        orchestration_request = OrchestrationRequest(
            request_id=f"teaching_{int(datetime.now().timestamp())}_{request.user_id}",
            request_type=RequestType.TEACHING_SESSION,
            user_id=request.user_id,
            context={
                "teaching_data": request.teaching_data,
                "knowledge_id": request.knowledge_id,
                "source": "api_teaching_session"
            }
        )
        
        response = await orch.process_request(orchestration_request)
        
        if not response.success:
            raise HTTPException(status_code=400, detail=response.error or "Teaching session failed")
        
        return {
            "success": True,
            "session_id": response.primary_response.get("session_id"),
            "session_type": response.primary_response.get("session_type"),
            "effectiveness_score": response.primary_response.get("effectiveness_score"),
            "improvements_made": response.primary_response.get("improvements_made", {}),
            "processing_time_ms": response.processing_time_ms,
            "suggested_actions": response.suggested_actions
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Teaching session failed: {e}")
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@router.post("/memory/preserve")
async def preserve_memories(request: MemoryPreservationRequest, background_tasks: BackgroundTasks):
    """Preserve memories during Cortex migration"""
    try:
        orch = await get_orchestrator()
        
        orchestration_request = OrchestrationRequest(
            request_id=f"memory_preserve_{int(datetime.now().timestamp())}",
            request_type=RequestType.MEMORY_PRESERVATION,
            user_id="system",
            context={
                "operation": request.operation,
                "source_systems": request.source_systems,
                **request.context,
                "source": "api_memory_preservation"
            }
        )
        
        # For long-running operations, process in background
        if request.operation in ["preserve_all", "full_migration"]:
            background_tasks.add_task(_background_memory_preservation, orch, orchestration_request)
            
            return {
                "success": True,
                "operation": request.operation,
                "status": "started",
                "request_id": orchestration_request.request_id,
                "message": "Memory preservation started in background",
                "estimated_duration": "5-30 minutes depending on data volume"
            }
        else:
            # Process synchronously for quick operations
            response = await orch.process_request(orchestration_request)
            
            if not response.success:
                raise HTTPException(status_code=400, detail=response.error or "Memory preservation failed")
            
            return {
                "success": True,
                "operation": request.operation,
                "memories_processed": response.memories_processed,
                "preservation_results": response.primary_response,
                "processing_time_ms": response.processing_time_ms
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Memory preservation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@router.post("/intelligence/unified")
async def unified_intelligence_query(request: UnifiedIntelligenceRequest):
    """Unified intelligence query coordinating all services"""
    try:
        orch = await get_orchestrator()
        
        orchestration_request = OrchestrationRequest(
            request_id=f"unified_{int(datetime.now().timestamp())}_{request.user_id}",
            request_type=RequestType.KNOWLEDGE_QUERY,  # Will be routed to unified processing
            user_id=request.user_id,
            query=request.query,
            context={
                **request.context,
                "source": "api_unified_intelligence"
            },
            mode=OrchestrationMode(request.mode),
            priority=request.priority
        )
        
        response = await orch.process_request(orchestration_request)
        
        if not response.success:
            raise HTTPException(status_code=400, detail=response.error or "Unified intelligence query failed")
        
        return {
            "success": True,
            "query": request.query,
            "unified_response": response.primary_response,
            "supporting_insights": response.supporting_responses,
            "services_coordinated": response.services_used,
            "confidence_score": response.confidence_score,
            "knowledge_items_accessed": response.knowledge_items_accessed,
            "coaching_insights_generated": response.coaching_insights_generated,
            "suggested_actions": response.suggested_actions,
            "related_queries": response.related_queries,
            "processing_time_ms": response.processing_time_ms,
            "intelligence_quality": {
                "comprehensive": len(response.services_used) > 1,
                "confidence_level": "high" if response.confidence_score > 0.8 else "medium" if response.confidence_score > 0.6 else "low",
                "data_sources": len(response.supporting_responses)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unified intelligence query failed: {e}")
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@router.get("/analytics")
async def get_analytics(analytics_type: str = "comprehensive"):
    """Get comprehensive analytics for all services"""
    try:
        orch = await get_orchestrator()
        
        orchestration_request = OrchestrationRequest(
            request_id=f"analytics_{int(datetime.now().timestamp())}",
            request_type=RequestType.ANALYTICS_REQUEST,
            user_id="system",
            context={
                "analytics_type": analytics_type,
                "source": "api_analytics"
            }
        )
        
        response = await orch.process_request(orchestration_request)
        
        if not response.success:
            raise HTTPException(status_code=400, detail=response.error or "Analytics retrieval failed")
        
        return {
            "success": True,
            "analytics_type": analytics_type,
            "analytics_data": response.primary_response,
            "generated_at": datetime.now().isoformat(),
            "processing_time_ms": response.processing_time_ms
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analytics retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@router.get("/status")
async def get_system_status():
    """Get detailed system status"""
    try:
        orch = await get_orchestrator()
        
        # Get orchestration analytics
        orchestration_analytics = await orch.get_orchestration_analytics()
        
        # Get individual service status
        service_status = {
            "knowledge_base": {
                "initialized": orch.knowledge_base.initialized if orch.knowledge_base else False,
                "analytics": await orch.knowledge_base.get_knowledge_analytics() if orch.knowledge_base and orch.knowledge_base.initialized else {}
            },
            "sales_coach": {
                "initialized": orch.sales_coach.initialized if orch.sales_coach else False,
                "analytics": orch.sales_coach.coaching_analytics if orch.sales_coach and orch.sales_coach.initialized else {}
            },
            "memory_preservation": {
                "initialized": orch.memory_preservation.initialized if orch.memory_preservation else False,
                "analytics": await orch.memory_preservation.get_migration_analytics() if orch.memory_preservation and orch.memory_preservation.initialized else {}
            }
        }
        
        return {
            "system_status": "operational",
            "orchestrator_analytics": orchestration_analytics,
            "service_status": service_status,
            "api_version": "1.0.0",
            "phase": "Phase 1 - Core Intelligence Services",
            "capabilities": [
                "Enhanced Knowledge Base with Interactive Teaching",
                "Interactive Sales Coach with Slack Integration",
                "Memory Preservation for Cortex Migration",
                "Unified Intelligence Orchestration"
            ],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"System status retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


# Background task functions
async def _background_memory_preservation(orchestrator: SophiaAIOrchestrator, request: OrchestrationRequest):
    """Background task for memory preservation"""
    try:
        logger.info(f"Starting background memory preservation: {request.request_id}")
        
        response = await orchestrator.process_request(request)
        
        if response.success:
            logger.info(f"Background memory preservation completed: {request.request_id}")
        else:
            logger.error(f"Background memory preservation failed: {request.request_id} - {response.error}")
            
    except Exception as e:
        logger.error(f"Background memory preservation error: {e}")


# WebSocket endpoint for real-time updates (future enhancement)
@router.get("/ws/status")
async def websocket_status():
    """WebSocket endpoint for real-time status updates"""
    return {
        "message": "WebSocket real-time status updates will be available in Phase 2",
        "current_capabilities": "REST API with comprehensive status endpoints",
        "future_enhancements": [
            "Real-time coaching notifications",
            "Live knowledge base updates",
            "Memory preservation progress tracking",
            "System health monitoring"
        ]
    }


# Export router for FastAPI app integration
__all__ = ["router"]
