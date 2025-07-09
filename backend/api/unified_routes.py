"""
Enhanced Unified API Routes for Sophia AI v3.0

Provides complete ecosystem access through natural language queries including:
- Gong conversation intelligence (integrated with business systems)
- Slack team communication
- Linear engineering tasks  
- Asana project management
- Notion documentation
- HubSpot CRM data
- Complete project management assessment across ALL data sources

Date: July 9, 2025
"""

import json
import logging
from datetime import datetime
from typing import Any

from fastapi import APIRouter, BackgroundTasks, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from backend.services.enhanced_multi_agent_orchestrator import (
    EnhancedMultiAgentOrchestrator,
)
from backend.services.project_management_service import ProjectManagementService
from backend.services.unified_chat_service_enhanced import (
    ECOSYSTEM_QUERY_EXAMPLES,
    EnhancedUnifiedChatService,
)

logger = logging.getLogger(__name__)

# Initialize services
enhanced_chat_service = EnhancedUnifiedChatService()
enhanced_orchestrator = EnhancedMultiAgentOrchestrator()
project_service = ProjectManagementService()

router = APIRouter(prefix="/api/v3", tags=["Enhanced Unified Chat"])


class EcosystemQueryRequest(BaseModel):
    """Request model for ecosystem queries"""
    query: str = Field(..., description="Natural language query for the complete ecosystem")
    user_id: str = Field(default="user", description="User identifier")
    session_id: str = Field(default="session", description="Session identifier")
    context: dict[str, Any] | None = Field(default=None, description="Additional context")
    stream: bool = Field(default=False, description="Enable streaming response")
    include_ecosystem_analysis: bool = Field(default=True, description="Include ecosystem analysis")
    include_project_health: bool = Field(default=True, description="Include project health assessment")


class EcosystemQueryResponse(BaseModel):
    """Response model for ecosystem queries"""
    response: str
    confidence: float
    processing_time: float

    # Ecosystem intelligence
    ecosystem_sources_used: list[str]
    ecosystem_patterns: list[str]
    cross_system_correlations: dict[str, Any]

    # Business intelligence
    project_health_insights: dict[str, Any]
    risk_indicators: list[str]
    opportunities: list[str]

    # Metadata
    citations: list[dict[str, Any]]
    metadata: dict[str, Any]
    current_date: str
    date_validated: bool

    # Query context
    query_intent: str
    complexity_level: str
    requires_cross_system_analysis: bool


class ProjectHealthRequest(BaseModel):
    """Request model for project health assessment"""
    project_context: str | None = Field(default=None, description="Specific project context")
    include_gong_intelligence: bool = Field(default=True, description="Include Gong conversation intelligence")
    include_slack_discussions: bool = Field(default=True, description="Include Slack team discussions")
    include_linear_velocity: bool = Field(default=True, description="Include Linear engineering velocity")
    include_asana_progress: bool = Field(default=True, description="Include Asana project progress")
    time_range_days: int = Field(default=30, description="Time range for analysis in days")


@router.post("/chat/ecosystem", response_model=EcosystemQueryResponse)
async def process_ecosystem_query(request: EcosystemQueryRequest):
    """
    Process natural language query with complete ecosystem access
    
    Examples:
    - "What project risks were mentioned in Gong calls this week?"
    - "Show me Linear tasks related to customer feedback from Gong"
    - "Cross-reference Slack discussions with Asana project status"
    - "How is our engineering velocity compared to customer requests?"
    """

    try:
        logger.info(f"Processing ecosystem query: {request.query}")

        # Process through enhanced unified chat service
        result = await enhanced_chat_service.process_ecosystem_query(
            query=request.query,
            user_id=request.user_id,
            session_id=request.session_id,
            context=request.context or {}
        )

        return EcosystemQueryResponse(**result)

    except Exception as e:
        logger.error(f"Ecosystem query error: {e}")
        raise HTTPException(status_code=500, detail=f"Ecosystem query processing failed: {e!s}")


@router.post("/chat/ecosystem/stream")
async def stream_ecosystem_query(request: EcosystemQueryRequest):
    """
    Stream ecosystem query processing with real-time updates
    
    Provides real-time progress updates as the query is processed across
    multiple ecosystem services including Gong, Slack, Linear, Asana, etc.
    """

    async def generate_stream():
        try:
            async for update in enhanced_chat_service.stream_ecosystem_query(
                query=request.query,
                user_id=request.user_id,
                session_id=request.session_id,
                context=request.context or {}
            ):
                yield f"data: {json.dumps(update)}\n\n"

        except Exception as e:
            error_update = {
                "type": "error",
                "data": {"error": str(e)}
            }
            yield f"data: {json.dumps(error_update)}\n\n"

    return StreamingResponse(
        generate_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream"
        }
    )


@router.get("/ecosystem/status")
async def get_ecosystem_status():
    """
    Get status of all ecosystem services
    
    Returns the current status of:
    - Gong conversation intelligence
    - Slack team communication
    - Linear engineering tasks
    - Asana project management
    - Notion documentation
    - HubSpot CRM data
    - And all other ecosystem services
    """

    try:
        status = await enhanced_chat_service.get_ecosystem_status()
        return status

    except Exception as e:
        logger.error(f"Ecosystem status error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get ecosystem status: {e!s}")


@router.post("/project/health/comprehensive")
async def get_comprehensive_project_health(request: ProjectHealthRequest):
    """
    Get comprehensive project health assessment across ALL ecosystem data sources
    
    Analyzes project health using:
    - Gong customer conversations and feedback
    - Slack team discussions and decision points
    - Linear engineering velocity and task completion
    - Asana project progress and timeline adherence
    - Notion documentation updates
    - HubSpot deal progress and customer satisfaction
    """

    try:
        # Build comprehensive project health query
        health_query = f"""
        Provide a comprehensive project health assessment as of July 9, 2025.
        
        Include analysis from:
        1. Gong conversation intelligence - customer feedback, project mentions, risk indicators
        2. Slack team communication - project discussions, decision points, team sentiment
        3. Linear engineering tasks - velocity, completion rates, backlog health
        4. Asana project management - timeline adherence, task completion, resource allocation
        5. Notion documentation - recent updates, knowledge gaps
        6. HubSpot CRM data - customer satisfaction, deal progress
        
        Focus on: {request.project_context or 'overall platform health'}
        Time range: Last {request.time_range_days} days
        
        Provide:
        - Overall health score (1-100)
        - Key risk indicators across all systems
        - Opportunities for improvement
        - Cross-system patterns and correlations
        - Actionable recommendations
        """

        # Process through ecosystem
        result = await enhanced_chat_service.process_ecosystem_query(
            query=health_query,
            user_id="project_health_assessment",
            session_id="comprehensive_health",
            context={
                "assessment_type": "comprehensive_project_health",
                "time_range_days": request.time_range_days,
                "include_gong": request.include_gong_intelligence,
                "include_slack": request.include_slack_discussions,
                "include_linear": request.include_linear_velocity,
                "include_asana": request.include_asana_progress
            }
        )

        # Enhance with specific project metrics
        project_metrics = await project_service.get_project_summary()

        # Combine ecosystem analysis with project metrics
        comprehensive_health = {
            "ecosystem_analysis": result,
            "project_metrics": project_metrics,
            "assessment_timestamp": datetime.now().isoformat(),
            "current_date": "July 9, 2025",
            "assessment_scope": {
                "gong_intelligence": request.include_gong_intelligence,
                "slack_discussions": request.include_slack_discussions,
                "linear_velocity": request.include_linear_velocity,
                "asana_progress": request.include_asana_progress,
                "time_range_days": request.time_range_days
            }
        }

        return comprehensive_health

    except Exception as e:
        logger.error(f"Comprehensive project health error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to assess comprehensive project health: {e!s}")


@router.get("/gong/intelligence")
async def get_gong_intelligence_integrated():
    """
    Get Gong conversation intelligence as part of integrated business intelligence
    
    NOTE: This endpoint provides Gong data as part of the complete ecosystem,
    not as a standalone service. Use /api/v3/chat/ecosystem for natural language
    queries that include Gong data along with other business systems.
    """

    try:
        # Process Gong intelligence as part of ecosystem
        gong_query = """
        Provide comprehensive Gong conversation intelligence for the past 30 days including:
        1. Customer feedback and sentiment analysis
        2. Project mentions and feature requests
        3. Risk indicators and concerns raised
        4. Competitive mentions and market insights
        5. Action items and follow-ups
        
        Integrate this with other business intelligence sources for complete context.
        """

        result = await enhanced_chat_service.process_ecosystem_query(
            query=gong_query,
            user_id="gong_intelligence",
            session_id="integrated_gong",
            context={
                "focus": "gong_conversation_intelligence",
                "integration_mode": "business_intelligence"
            }
        )

        return {
            "gong_intelligence": result,
            "integration_note": "Gong data is integrated with complete business ecosystem",
            "recommended_usage": "Use /api/v3/chat/ecosystem for natural language queries",
            "current_date": "July 9, 2025"
        }

    except Exception as e:
        logger.error(f"Gong intelligence error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get Gong intelligence: {e!s}")


@router.get("/ecosystem/examples")
async def get_ecosystem_query_examples():
    """
    Get examples of natural language queries for the complete ecosystem
    
    Returns examples showing how to query across:
    - Gong conversation intelligence
    - Slack team communication
    - Linear engineering tasks
    - Asana project management
    - And all other ecosystem services
    """

    return {
        "ecosystem_query_examples": ECOSYSTEM_QUERY_EXAMPLES,
        "usage_instructions": [
            "Use natural language to query across all ecosystem services",
            "Gong intelligence is integrated with business systems, not standalone",
            "Cross-reference data between different systems for comprehensive insights",
            "Ask for project health assessments using data from all sources",
            "Request risk analysis across multiple communication and project channels"
        ],
        "example_categories": {
            "gong_intelligence": [
                "What project risks were mentioned in Gong calls this week?",
                "Show me customer feedback about our new feature from Gong conversations"
            ],
            "cross_system_analysis": [
                "Cross-reference Linear engineering tasks with customer requests from Gong",
                "Show me Asana project status and related Slack discussions"
            ],
            "communication_intelligence": [
                "What are the team discussing in Slack about the product launch?",
                "Find action items mentioned in Slack that relate to Linear tasks"
            ],
            "comprehensive_assessment": [
                "Give me a comprehensive project health assessment across all systems",
                "What patterns emerge when looking at Gong, Slack, Linear, and Asana together?"
            ]
        },
        "current_date": "July 9, 2025"
    }


@router.post("/chat/natural-language")
async def process_natural_language_query(
    query: str,
    user_id: str = "user",
    session_id: str = "session",
    context: dict[str, Any] | None = None
):
    """
    Simplified natural language query endpoint for complete ecosystem access
    
    This is the main endpoint for natural language queries that can access
    the complete Pay Ready ecosystem including Gong, Slack, Linear, Asana,
    Notion, HubSpot, and all other integrated services.
    
    Examples:
    - "What did customers say about our pricing in recent Gong calls?"
    - "Show me engineering velocity from Linear and customer feedback from Gong"
    - "What project risks appear in both Slack discussions and customer calls?"
    """

    try:
        result = await enhanced_chat_service.process_ecosystem_query(
            query=query,
            user_id=user_id,
            session_id=session_id,
            context=context or {}
        )

        # Simplified response for natural language interface
        return {
            "response": result["response"],
            "confidence": result["confidence"],
            "sources": result["ecosystem_sources_used"],
            "patterns": result["ecosystem_patterns"],
            "current_date": "July 9, 2025",
            "processing_time": result["processing_time"]
        }

    except Exception as e:
        logger.error(f"Natural language query error: {e}")
        raise HTTPException(status_code=500, detail=f"Query processing failed: {e!s}")


@router.get("/health")
async def health_check():
    """Health check endpoint with ecosystem status"""

    try:
        # Quick health check of core services
        ecosystem_status = await enhanced_chat_service.get_ecosystem_status()

        active_services = sum(1 for service in ecosystem_status["services"].values() if service["status"] == "active")
        total_services = len(ecosystem_status["services"])

        return {
            "status": "healthy",
            "current_date": "July 9, 2025",
            "date_validated": True,
            "ecosystem_health": {
                "active_services": active_services,
                "total_services": total_services,
                "health_percentage": round((active_services / total_services) * 100, 1)
            },
            "capabilities": ecosystem_status["capabilities"],
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {
            "status": "degraded",
            "error": str(e),
            "current_date": "July 9, 2025",
            "timestamp": datetime.now().isoformat()
        }


# Background task for ecosystem data refresh
@router.post("/ecosystem/refresh")
async def refresh_ecosystem_data(background_tasks: BackgroundTasks):
    """
    Refresh ecosystem data in the background
    
    Triggers a background refresh of data from all ecosystem services
    including Gong, Slack, Linear, Asana, etc.
    """

    async def refresh_task():
        try:
            logger.info("Starting ecosystem data refresh")

            # Refresh query to trigger data updates
            refresh_query = """
            Refresh and validate data connections across all ecosystem services:
            - Gong conversation intelligence
            - Slack team communication
            - Linear engineering tasks
            - Asana project management
            - Notion documentation
            - HubSpot CRM data
            - All other integrated services
            
            Verify data freshness and connection health.
            """

            await enhanced_chat_service.process_ecosystem_query(
                query=refresh_query,
                user_id="system_refresh",
                session_id="ecosystem_refresh",
                context={"refresh_mode": True}
            )

            logger.info("Ecosystem data refresh completed")

        except Exception as e:
            logger.error(f"Ecosystem refresh error: {e}")

    background_tasks.add_task(refresh_task)

    return {
        "status": "refresh_initiated",
        "message": "Ecosystem data refresh started in background",
        "current_date": "July 9, 2025",
        "timestamp": datetime.now().isoformat()
    }
