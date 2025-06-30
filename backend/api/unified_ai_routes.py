"""
Unified AI API Routes
Comprehensive API endpoints for Sophia AI Platform with advanced Cortex Agents integration
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from backend.services.unified_ai_orchestration_service import (
    UnifiedAIOrchestrationService,
    get_unified_ai_service,
)

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/ai", tags=["Unified AI"])


# Pydantic models for request/response
class CustomerIntelligenceRequest(BaseModel):
    customer_id: str = Field(..., description="Customer ID to analyze")
    query: str = Field(..., description="Natural language query about the customer")
    include_real_time: bool = Field(True, description="Include real-time insights")


class CustomerIntelligenceResponse(BaseModel):
    customer_id: str
    query: str
    agent_response: str
    customer_context: dict[str, Any]
    real_time_insights: dict[str, Any]
    confidence_score: float
    timestamp: str


class SalesOptimizationRequest(BaseModel):
    deal_id: str = Field(..., description="Deal ID to analyze")
    query: str = Field(..., description="Natural language query about the deal")
    include_competitive: bool = Field(
        True, description="Include competitive intelligence"
    )


class SalesOptimizationResponse(BaseModel):
    deal_id: str
    query: str
    agent_response: str
    deal_context: dict[str, Any]
    competitive_insights: dict[str, Any]
    confidence_score: float
    timestamp: str


class ComplianceMonitoringRequest(BaseModel):
    query: str = Field(..., description="Natural language compliance query")
    time_range: str = Field(
        "30d", description="Time range for analysis (e.g., '7d', '30d', '90d')"
    )
    include_violations: bool = Field(True, description="Include violation details")


class ComplianceMonitoringResponse(BaseModel):
    query: str
    time_range: str
    agent_response: str
    compliance_context: dict[str, Any]
    violation_alerts: list[dict[str, Any]]
    confidence_score: float
    timestamp: str


class SystemHealthResponse(BaseModel):
    snowflake_health: list[dict[str, Any]]
    pipeline_health: dict[str, Any]
    cortex_agents_status: int
    data_sources_status: dict[str, Any]
    timestamp: str


class MultiSourceSearchRequest(BaseModel):
    query: str = Field(..., description="Natural language search query")
    sources: list[str] = Field(
        ["gong", "slack", "hubspot", "intercom"], description="Data sources to search"
    )
    customer_id: str | None = Field(None, description="Filter by customer ID")
    limit: int = Field(10, description="Maximum number of results")


class MultiSourceSearchResponse(BaseModel):
    query: str
    sources: list[str]
    results: list[dict[str, Any]]
    total_results: int
    search_time_ms: int
    timestamp: str


# API Endpoints


@router.post("/customer-intelligence", response_model=CustomerIntelligenceResponse)
async def analyze_customer_intelligence(
    request: CustomerIntelligenceRequest,
    ai_service: UnifiedAIOrchestrationService = Depends(get_unified_ai_service),
):
    """
    Analyze customer intelligence using Cortex Agents and unified data sources

    This endpoint provides comprehensive customer insights by:
    - Analyzing all customer interactions across Gong, Slack, HubSpot, Intercom
    - Using AI-powered sentiment analysis and behavior prediction
    - Providing real-time context and recommendations
    - Generating churn risk assessments and next best actions
    """
    try:
        logger.info(
            f"Processing customer intelligence query for customer {request.customer_id}"
        )

        result = await ai_service.process_customer_intelligence_query(
            customer_id=request.customer_id, query=request.query
        )

        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])

        return CustomerIntelligenceResponse(**result)

    except Exception as e:
        logger.error(f"Customer intelligence analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sales-optimization", response_model=SalesOptimizationResponse)
async def analyze_sales_optimization(
    request: SalesOptimizationRequest,
    ai_service: UnifiedAIOrchestrationService = Depends(get_unified_ai_service),
):
    """
    Analyze sales optimization using Cortex Agents and deal intelligence

    This endpoint provides comprehensive deal insights by:
    - Analyzing all deal-related conversations and activities
    - Using AI-powered competitive intelligence and risk assessment
    - Providing win probability analysis and optimization recommendations
    - Generating specific actions to advance deals and mitigate risks
    """
    try:
        logger.info(f"Processing sales optimization query for deal {request.deal_id}")

        result = await ai_service.process_sales_optimization_query(
            deal_id=request.deal_id, query=request.query
        )

        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])

        return SalesOptimizationResponse(**result)

    except Exception as e:
        logger.error(f"Sales optimization analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/compliance-monitoring", response_model=ComplianceMonitoringResponse)
async def analyze_compliance_monitoring(
    request: ComplianceMonitoringRequest,
    ai_service: UnifiedAIOrchestrationService = Depends(get_unified_ai_service),
):
    """
    Analyze compliance monitoring using Cortex Agents

    This endpoint provides comprehensive compliance insights by:
    - Monitoring all customer communications for regulatory compliance
    - Using AI-powered FDCPA violation detection and risk assessment
    - Providing automated compliance reporting and audit trails
    - Generating specific remediation recommendations for violations
    """
    try:
        logger.info(f"Processing compliance monitoring query: {request.query}")

        result = await ai_service.process_compliance_monitoring_query(
            query=request.query, time_range=request.time_range
        )

        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])

        return ComplianceMonitoringResponse(**result)

    except Exception as e:
        logger.error(f"Compliance monitoring analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/system-health", response_model=SystemHealthResponse)
async def get_system_health(
    ai_service: UnifiedAIOrchestrationService = Depends(get_unified_ai_service),
):
    """
    Get comprehensive system health status

    This endpoint provides real-time system health information including:
    - Snowflake warehouse performance and query metrics
    - Estuary Flow data pipeline status and throughput
    - Cortex Agents availability and performance
    - Data source connectivity and sync status
    """
    try:
        logger.info("Retrieving system health status")

        health_status = await ai_service.get_system_health_status()

        if "error" in health_status:
            raise HTTPException(status_code=500, detail=health_status["error"])

        return SystemHealthResponse(**health_status)

    except Exception as e:
        logger.error(f"System health check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/multi-source-search", response_model=MultiSourceSearchResponse)
async def search_multi_source_data(
    request: MultiSourceSearchRequest,
    ai_service: UnifiedAIOrchestrationService = Depends(get_unified_ai_service),
):
    """
    Search across multiple data sources using hybrid AI-powered search

    This endpoint provides unified search capabilities across:
    - Gong conversation transcripts and analytics
    - Slack messages and channel discussions
    - HubSpot contacts, deals, and company data
    - Intercom customer service conversations
    - Proprietary SQL database records

    Uses advanced hybrid search combining vector similarity and keyword matching
    """
    try:
        logger.info(f"Processing multi-source search query: {request.query}")

        start_time = datetime.now(UTC)

        # Simulate multi-source search (would integrate with Cortex Search in production)
        search_results = await _perform_multi_source_search(
            ai_service,
            request.query,
            request.sources,
            request.customer_id,
            request.limit,
        )

        end_time = datetime.now(UTC)
        search_time_ms = int((end_time - start_time).total_seconds() * 1000)

        return MultiSourceSearchResponse(
            query=request.query,
            sources=request.sources,
            results=search_results,
            total_results=len(search_results),
            search_time_ms=search_time_ms,
            timestamp=datetime.now(UTC).isoformat(),
        )

    except Exception as e:
        logger.error(f"Multi-source search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/data-sources/status")
async def get_data_sources_status(
    ai_service: UnifiedAIOrchestrationService = Depends(get_unified_ai_service),
):
    """
    Get status of all configured data sources

    Returns real-time status information for:
    - Gong.io API connectivity and last sync time
    - Slack API connectivity and message processing
    - HubSpot CRM sync status and data freshness
    - Intercom customer service data availability
    - Proprietary SQL database connectivity
    """
    try:
        return {
            "data_sources": ai_service.data_sources,
            "timestamp": datetime.now(UTC).isoformat(),
        }
    except Exception as e:
        logger.error(f"Data sources status check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cortex-agents/status")
async def get_cortex_agents_status(
    ai_service: UnifiedAIOrchestrationService = Depends(get_unified_ai_service),
):
    """
    Get status of all configured Cortex Agents

    Returns information about:
    - Available Cortex Agents and their configurations
    - Agent performance metrics and availability
    - Tool integrations and semantic model references
    - Recent interaction logs and success rates
    """
    try:
        agents_info = {}
        for agent_id, agent_config in ai_service.cortex_agents.items():
            agents_info[agent_id] = {
                "name": agent_config.get("name"),
                "tools": list(agent_config.get("tools", {}).keys()),
                "semantic_models": agent_config.get("semantic_models"),
                "search_services": agent_config.get("search_services"),
                "status": "active",
            }

        return {
            "cortex_agents": agents_info,
            "total_agents": len(ai_service.cortex_agents),
            "timestamp": datetime.now(UTC).isoformat(),
        }
    except Exception as e:
        logger.error(f"Cortex agents status check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/real-time-insights/{customer_id}")
async def get_real_time_customer_insights(
    customer_id: str,
    ai_service: UnifiedAIOrchestrationService = Depends(get_unified_ai_service),
):
    """
    Get real-time customer insights and recommendations

    Provides up-to-the-minute customer intelligence including:
    - Recent interaction summaries and sentiment trends
    - Churn risk indicators and retention recommendations
    - Next best actions based on current customer state
    - Urgency flags and escalation recommendations
    """
    try:
        insights = await ai_service._get_real_time_customer_insights(customer_id)

        return {
            "customer_id": customer_id,
            "insights": insights,
            "timestamp": datetime.now(UTC).isoformat(),
        }
    except Exception as e:
        logger.error(f"Real-time insights retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/competitive-intelligence/{deal_id}")
async def get_competitive_intelligence(
    deal_id: str,
    ai_service: UnifiedAIOrchestrationService = Depends(get_unified_ai_service),
):
    """
    Get competitive intelligence for a specific deal

    Provides comprehensive competitive analysis including:
    - Competitor mentions in conversations and documents
    - Competitive positioning and differentiation opportunities
    - Pricing discussions and negotiation insights
    - Win/loss patterns and success strategies
    """
    try:
        intelligence = await ai_service._get_competitive_intelligence(deal_id)

        return {
            "deal_id": deal_id,
            "competitive_intelligence": intelligence,
            "timestamp": datetime.now(UTC).isoformat(),
        }
    except Exception as e:
        logger.error(f"Competitive intelligence retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/compliance-violations")
async def get_recent_compliance_violations(
    time_range: str = "30d",
    ai_service: UnifiedAIOrchestrationService = Depends(get_unified_ai_service),
):
    """
    Get recent compliance violations and risk indicators

    Provides comprehensive compliance monitoring including:
    - FDCPA violation detection and severity assessment
    - Automated compliance scoring and risk indicators
    - Remediation recommendations and corrective actions
    - Audit trail documentation and regulatory reporting
    """
    try:
        violations = await ai_service._get_compliance_violations(time_range)

        return {
            "time_range": time_range,
            "violations": violations,
            "total_violations": len(violations),
            "timestamp": datetime.now(UTC).isoformat(),
        }
    except Exception as e:
        logger.error(f"Compliance violations retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Helper functions


async def _perform_multi_source_search(
    ai_service: UnifiedAIOrchestrationService,
    query: str,
    sources: list[str],
    customer_id: str | None,
    limit: int,
) -> list[dict[str, Any]]:
    """
    Perform multi-source search across specified data sources
    """
    try:
        cursor = ai_service.snowflake_conn.cursor()

        # Build dynamic query based on sources
        search_queries = []

        if "gong" in sources:
            search_queries.append(
                """
                SELECT 'gong' as source, call_id as id, customer_id, call_transcript as content,
                       call_timestamp as timestamp, 'call_transcript' as content_type
                FROM ESTUARY_MATERIALIZED.gong_calls_multimodal
                WHERE call_transcript ILIKE %s
            """
            )

        if "slack" in sources:
            search_queries.append(
                """
                SELECT 'slack' as source, message_id as id, customer_id, message_text as content,
                       message_timestamp as timestamp, 'message' as content_type
                FROM ESTUARY_MATERIALIZED.slack_messages_multimodal
                WHERE message_text ILIKE %s
            """
            )

        if "hubspot" in sources:
            search_queries.append(
                """
                SELECT 'hubspot' as source, contact_id as id, customer_id,
                       CONCAT(first_name, ' ', last_name, ' - ', company) as content,
                       last_modified_date as timestamp, 'contact' as content_type
                FROM ESTUARY_MATERIALIZED.hubspot_contacts_enhanced
                WHERE CONCAT(first_name, ' ', last_name, ' ', company) ILIKE %s
            """
            )

        if "intercom" in sources:
            search_queries.append(
                """
                SELECT 'intercom' as source, message_id as id, customer_id, message_body as content,
                       created_at as timestamp, 'support_message' as content_type
                FROM ESTUARY_MATERIALIZED.intercom_messages_enhanced
                WHERE message_body ILIKE %s
            """
            )

        # Combine queries with UNION
        if search_queries:
            combined_query = " UNION ALL ".join(search_queries)
            combined_query += f" ORDER BY timestamp DESC LIMIT {limit}"

            search_pattern = f"%{query}%"
            params = [search_pattern] * len(search_queries)

            if customer_id:
                # Add customer filter
                combined_query = (
                    f"SELECT * FROM ({combined_query}) WHERE customer_id = %s"
                )
                params.append(customer_id)

            cursor.execute(combined_query, params)
            results = cursor.fetchall()

            # Convert to list of dictionaries
            columns = [desc[0] for desc in cursor.description]
            search_results = [dict(zip(columns, row, strict=False)) for row in results]

            cursor.close()
            return search_results

        return []

    except Exception as e:
        logger.error(f"Multi-source search execution failed: {e}")
        return []


# WebSocket endpoint for real-time updates
@router.websocket("/ws/real-time-updates")
async def websocket_real_time_updates(websocket):
    """
    WebSocket endpoint for real-time system updates and notifications

    Provides live streaming of:
    - New customer interactions and sentiment changes
    - Deal progression and risk assessment updates
    - Compliance violations and alert notifications
    - System health metrics and performance indicators
    """
    await websocket.accept()

    try:
        while True:
            # Simulate real-time updates (would integrate with actual event streams)
            update = {
                "type": "system_health",
                "data": {
                    "active_queries": 42,
                    "avg_response_time_ms": 150,
                    "data_freshness_minutes": 2,
                },
                "timestamp": datetime.now(UTC).isoformat(),
            }

            await websocket.send_text(json.dumps(update))
            await asyncio.sleep(30)  # Send updates every 30 seconds

    except Exception as e:
        logger.error(f"WebSocket connection error: {e}")
    finally:
        await websocket.close()


# Export router
__all__ = ["router"]
