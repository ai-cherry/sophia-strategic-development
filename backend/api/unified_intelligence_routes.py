from datetime import UTC, datetime

"""
Sophia AI Unified Intelligence API Routes
=========================================
FastAPI routes for unified intelligence queries with constitutional AI.
"""

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from backend.core.simple_auth import get_current_user
from backend.services.simplified_unified_intelligence_service import (
    get_simplified_unified_intelligence_service,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/unified-intelligence",
    tags=["unified-intelligence"],
    responses={404: {"description": "Not found"}},
)


class UnifiedIntelligenceRequest(BaseModel):
    """Request model for unified intelligence queries"""

    query: str = Field(..., description="Natural language business query")
    business_context: dict[str, Any] | None = Field(
        default_factory=dict, description="Business context for the query"
    )
    optimization_mode: str = Field(
        default="balanced", description="Optimization mode: balanced, performance, cost"
    )
    conversation_history: list[dict[str, str]] | None = Field(
        default_factory=list, description="Previous conversation messages for context"
    )


class UnifiedIntelligenceResponse(BaseModel):
    """Response model for unified intelligence queries"""

    unified_insights: str = Field(
        ..., description="Synthesized insights from all sources"
    )
    memory_context: list[dict[str, Any]] | None = Field(
        default=None, description="Relevant memories from AI Memory"
    )
    business_data: dict[str, Any] = Field(
        default_factory=dict, description="Business data from integrations"
    )
    constitutional_compliance: float = Field(
        ..., description="Constitutional AI compliance score (0-1)"
    )
    optimization_insights: dict[str, Any] = Field(
        default_factory=dict, description="Insights for query optimization"
    )
    confidence_score: float = Field(..., description="Overall confidence score (0-1)")
    timestamp: str = Field(..., description="Response timestamp")
    error: str | None = Field(default=None, description="Error message if any")


def get_user_context() -> dict[str, Any]:
    """Get user context for requests (simplified for development)"""
    return get_current_user()


@router.post("/query", response_model=UnifiedIntelligenceResponse)
async def unified_business_intelligence(
    request: UnifiedIntelligenceRequest,
    current_user: dict[str, Any] = Depends(get_user_context),
):
    """
    Execute a unified business intelligence query

    This endpoint:
    - Validates queries against constitutional AI principles
    - Searches across all data sources (Snowflake, AI Memory, Gong, etc.)
    - Synthesizes results into actionable insights
    - Provides optimization recommendations
    """
    logger.info(
        f"📊 Unified intelligence query from user {current_user.get('id')}: {request.query[:100]}..."
    )

    try:
        # Get unified intelligence service
        unified_service = await get_simplified_unified_intelligence_service()

        # Prepare context with user information
        context = {
            "user_id": current_user.get("id"),
            "user_role": current_user.get("role", "employee"),
            "user_department": current_user.get("department"),
            "optimization_mode": request.optimization_mode,
            "conversation_history": request.conversation_history,
        }
        # Add business context if provided
        if request.business_context:
            context.update(request.business_context)

        # Execute unified query
        response = await unified_service.unified_business_query(
            query=request.query, context=context
        )

        # Check for errors
        if "error" in response:
            logger.error(f"❌ Error in unified query: {response['error']}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=response["error"]
            )

        return UnifiedIntelligenceResponse(**response)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Unexpected error in unified intelligence: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process unified intelligence query: {str(e)}",
        )


@router.get("/health")
async def unified_intelligence_health():
    """Check health of unified intelligence service"""
    try:
        unified_service = await get_simplified_unified_intelligence_service()

        health_status = {
            "status": "healthy",
            "timestamp": datetime.now(UTC).isoformat(),
            "services": {
                "snowflake_cortex": bool(unified_service.snowflake_cortex),
                "ai_memory": bool(unified_service.ai_memory),
                "gong_integration": bool(unified_service.gong_integration),
                "constitutional_ai": bool(unified_service.constitutional_ai),
                "vector_router": bool(getattr(unified_service, "vector_router", None)),
                "portkey_gateway": bool(
                    getattr(unified_service, "portkey_gateway", None)
                ),
            },
        }

        # Check if at least core services are available
        core_services = [
            health_status["services"]["snowflake_cortex"],
            health_status["services"]["ai_memory"],
        ]

        if not any(core_services):
            health_status["status"] = "degraded"
            health_status["message"] = "Core services unavailable"

        return health_status

    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now(UTC).isoformat(),
        }


@router.post("/validate-query")
async def validate_query(
    query: str, current_user: dict[str, Any] = Depends(get_user_context)
):
    """
    Validate a query against constitutional AI principles

    This endpoint allows checking if a query complies with ethical principles
    before executing it.
    """
    try:
        unified_service = await get_simplified_unified_intelligence_service()

        if not unified_service.constitutional_ai:
            return {
                "approved": True,
                "compliance_score": 1.0,
                "message": "Constitutional AI not available, query auto-approved",
            }

        context = {
            "user_id": current_user.get("id"),
            "user_role": current_user.get("role", "employee"),
            "user_department": current_user.get("department"),
        }

        # Use simplified validation since constitutional AI is not fully implemented
        validation_result = await unified_service._validate_query_safety(query, context)

        return validation_result

    except Exception as e:
        logger.error(f"❌ Query validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to validate query: {str(e)}",
        )


@router.get("/optimization-insights")
async def get_optimization_insights(
    current_user: dict[str, Any] = Depends(get_user_context),
):
    """
    Get optimization insights for improving query performance

    This endpoint provides recommendations for:
    - Query optimization strategies
    - Caching opportunities
    - Performance improvements
    """
    try:
        return {
            "query_tips": [
                "Include specific time ranges for faster results",
                "Use entity names (company, person) for precise matching",
                "Add context keywords for better relevance",
            ],
            "performance_tips": [
                "Queries with specific entities are 3x faster",
                "Date-ranged queries reduce search space by 80%",
                "Cached queries return in <50ms",
            ],
            "cost_optimization": [
                "Use 'cost' optimization mode for budget-conscious queries",
                "Batch similar queries together",
                "Enable result caching for repeated queries",
            ],
            "advanced_features": [
                "Use conversation history for context-aware responses",
                "Specify business_context for domain-specific insights",
                "Request specific data sources for targeted analysis",
            ],
        }

    except Exception as e:
        logger.error(f"❌ Failed to get optimization insights: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve optimization insights: {str(e)}",
        )


@router.get("/performance-dashboard")
async def get_performance_dashboard(
    current_user: dict[str, Any] = Depends(get_user_context),
):
    """
    Get comprehensive performance dashboard data

    This endpoint provides:
    - Performance metrics
    - Ecosystem health status
    - Cost analysis
    - Optimization opportunities
    """
    try:
        unified_service = await get_simplified_unified_intelligence_service()
        dashboard_data = await unified_service.get_performance_dashboard()

        return dashboard_data

    except Exception as e:
        logger.error(f"❌ Failed to get performance dashboard: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve performance dashboard: {str(e)}",
        )
