"""
Smart AI Service API Routes

Provides comprehensive API endpoints for:
- LLM request routing and management
- Usage analytics and cost tracking
- Strategic model assignments (CEO-configurable)
- Gateway health monitoring
- Performance optimization
"""

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
import logging

from backend.services.smart_ai_service import (
    smart_ai_service,
    LLMRequest,
    TaskType,
    PerformanceTier,
    generate_executive_insight,
    generate_competitive_analysis,
    generate_code,
    experimental_query
)
from backend.utils.snowflake_cortex_service import SnowflakeCortexService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/smart-ai", tags=["Smart AI Service"])


# Pydantic models for API
class LLMRequestModel(BaseModel):
    """API model for LLM requests"""
    messages: List[Dict[str, str]]
    task_type: TaskType
    model_preference: Optional[str] = None
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=2000, ge=1, le=8000)
    cost_sensitivity: float = Field(default=0.5, ge=0.0, le=1.0)
    performance_priority: bool = True
    is_experimental: bool = False
    user_id: str = "api_user"
    session_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class StrategicAssignmentModel(BaseModel):
    """API model for strategic model assignments"""
    task_type: TaskType
    model: str


class ExecutiveInsightRequest(BaseModel):
    """API model for executive insight requests"""
    query: str
    context: Optional[str] = None
    user_id: str = "executive"


class CompetitiveAnalysisRequest(BaseModel):
    """API model for competitive analysis requests"""
    prompt: str
    user_id: str = "analyst"


class CodeGenerationRequest(BaseModel):
    """API model for code generation requests"""
    prompt: str
    language: str = "python"
    user_id: str = "developer"


class ExperimentalQueryRequest(BaseModel):
    """API model for experimental queries"""
    prompt: str
    model: str = "llama-3-70b"
    user_id: str = "researcher"


# Core LLM endpoints
@router.post("/generate", response_model=Dict[str, Any])
async def generate_llm_response(request: LLMRequestModel):
    """
    Generate LLM response using intelligent routing
    
    Uses SmartAIService to route requests to optimal provider/model
    based on task type, performance requirements, and cost sensitivity.
    """
    try:
        # Convert API model to internal request
        llm_request = LLMRequest(
            messages=request.messages,
            task_type=request.task_type,
            model_preference=request.model_preference,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            cost_sensitivity=request.cost_sensitivity,
            performance_priority=request.performance_priority,
            is_experimental=request.is_experimental,
            user_id=request.user_id,
            session_id=request.session_id,
            metadata=request.metadata or {}
        )

        # Generate response
        response = await smart_ai_service.generate_response(llm_request)

        return {
            "content": response.content,
            "provider": response.provider.value,
            "model": response.model,
            "cost_usd": response.cost_usd,
            "latency_ms": response.latency_ms,
            "tokens_used": response.tokens_used,
            "cache_hit": response.cache_hit,
            "quality_score": response.quality_score,
            "request_id": response.request_id,
            "timestamp": response.timestamp.isoformat(),
            "error": response.error
        }

    except Exception as e:
        logger.error(f"Error generating LLM response: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Convenience endpoints for common use cases
@router.post("/executive-insight")
async def generate_executive_insight_endpoint(request: ExecutiveInsightRequest):
    """Generate executive-level insights with premium models"""
    try:
        content = await generate_executive_insight(
            query=request.query,
            context=request.context,
            user_id=request.user_id
        )

        return {
            "content": content,
            "task_type": "executive_insights",
            "generated_at": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error generating executive insight: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/competitive-analysis")
async def generate_competitive_analysis_endpoint(request: CompetitiveAnalysisRequest):
    """Generate competitive analysis with specialized models"""
    try:
        content = await generate_competitive_analysis(
            prompt=request.prompt,
            user_id=request.user_id
        )

        return {
            "content": content,
            "task_type": "competitive_analysis",
            "generated_at": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error generating competitive analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-code")
async def generate_code_endpoint(request: CodeGenerationRequest):
    """Generate code with specialized coding models"""
    try:
        content = await generate_code(
            prompt=request.prompt,
            language=request.language,
            user_id=request.user_id
        )

        return {
            "content": content,
            "language": request.language,
            "task_type": "code_generation",
            "generated_at": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error generating code: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/experimental-query")
async def experimental_query_endpoint(request: ExperimentalQueryRequest):
    """Run experimental queries on OpenRouter"""
    try:
        content = await experimental_query(
            prompt=request.prompt,
            model=request.model,
            user_id=request.user_id
        )

        return {
            "content": content,
            "model": request.model,
            "task_type": "experimental",
            "generated_at": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error running experimental query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Analytics and monitoring endpoints
@router.get("/analytics")
async def get_usage_analytics(time_period_hours: int = 24):
    """
    Get comprehensive usage analytics
    
    Provides insights into:
    - Cost breakdown by provider/model
    - Performance metrics
    - Cache hit rates
    - Error rates
    - Gateway health
    """
    try:
        analytics = await smart_ai_service.get_usage_analytics(time_period_hours)
        return analytics

    except Exception as e:
        logger.error(f"Error getting usage analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/cost-optimization")
async def get_cost_optimization_insights():
    """
    Get cost optimization insights from Snowflake analytics
    
    Identifies opportunities to reduce costs while maintaining quality.
    """
    try:
        cortex_service = SnowflakeCortexService()
        
        async with cortex_service as cortex:
            # Query cost optimization view
            optimization_data = await cortex.query_structured_data(
                table="OPS_MONITORING.V_AI_COST_OPTIMIZATION",
                limit=20
            )

            if not optimization_data:
                return {"opportunities": [], "message": "No optimization data available"}

            # Format optimization opportunities
            opportunities = []
            for record in optimization_data:
                opportunities.append({
                    "task_type": record.get("TASK_TYPE"),
                    "model": record.get("MODEL"),
                    "provider": record.get("PROVIDER"),
                    "current_cost": record.get("AVG_COST"),
                    "potential_savings": record.get("POTENTIAL_SAVINGS", 0),
                    "optimization_level": record.get("OPTIMIZATION_OPPORTUNITY"),
                    "recommendation": f"Consider switching to lower-cost model for {record.get('TASK_TYPE')} tasks"
                })

            return {
                "opportunities": opportunities,
                "total_potential_savings": sum(op["potential_savings"] for op in opportunities),
                "generated_at": datetime.now().isoformat()
            }

    except Exception as e:
        logger.error(f"Error getting cost optimization insights: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/performance")
async def get_performance_analytics():
    """Get performance analytics from Snowflake"""
    try:
        cortex_service = SnowflakeCortexService()
        
        async with cortex_service as cortex:
            performance_data = await cortex.query_structured_data(
                table="OPS_MONITORING.V_AI_PERFORMANCE_ANALYTICS",
                limit=20
            )

            if not performance_data:
                return {"performance_metrics": [], "message": "No performance data available"}

            metrics = []
            for record in performance_data:
                metrics.append({
                    "provider": record.get("PROVIDER"),
                    "model": record.get("MODEL"),
                    "total_requests": record.get("TOTAL_REQUESTS"),
                    "avg_latency_ms": record.get("AVG_LATENCY_MS"),
                    "p95_latency_ms": record.get("P95_LATENCY_MS"),
                    "avg_quality_score": record.get("AVG_QUALITY_SCORE"),
                    "error_rate": record.get("ERROR_RATE"),
                    "cache_hit_rate": record.get("CACHE_HIT_RATE"),
                    "avg_cost_per_request": record.get("AVG_COST_PER_REQUEST")
                })

            return {
                "performance_metrics": metrics,
                "generated_at": datetime.now().isoformat()
            }

    except Exception as e:
        logger.error(f"Error getting performance analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def get_gateway_health():
    """Get real-time gateway health status"""
    try:
        cortex_service = SnowflakeCortexService()
        
        async with cortex_service as cortex:
            health_data = await cortex.query_structured_data(
                table="OPS_MONITORING.V_AI_GATEWAY_HEALTH",
                limit=10
            )

            if not health_data:
                return {"gateways": [], "overall_status": "UNKNOWN"}

            gateways = []
            healthy_count = 0
            
            for record in health_data:
                status = record.get("HEALTH_STATUS", "UNKNOWN")
                if status == "HEALTHY":
                    healthy_count += 1
                    
                gateways.append({
                    "provider": record.get("PROVIDER"),
                    "status": status,
                    "total_requests": record.get("TOTAL_REQUESTS"),
                    "error_rate": record.get("ERROR_RATE"),
                    "avg_latency": record.get("AVG_LATENCY"),
                    "last_request": record.get("LAST_REQUEST_TIME")
                })

            overall_status = "HEALTHY" if healthy_count == len(gateways) else "DEGRADED"

            return {
                "overall_status": overall_status,
                "gateways": gateways,
                "checked_at": datetime.now().isoformat()
            }

    except Exception as e:
        logger.error(f"Error getting gateway health: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Strategic management endpoints (CEO dashboard)
@router.get("/strategic-assignments")
async def get_strategic_assignments():
    """Get current strategic model assignments (CEO-configurable)"""
    try:
        assignments = {
            task_type.value: model 
            for task_type, model in smart_ai_service.strategic_assignments.items()
        }
        
        return {
            "assignments": assignments,
            "available_models": smart_ai_service.get_available_models(),
            "last_updated": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error getting strategic assignments: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/strategic-assignments")
async def update_strategic_assignment(request: StrategicAssignmentModel):
    """Update strategic model assignment (CEO-configurable)"""
    try:
        success = await smart_ai_service.update_strategic_assignment(
            task_type=request.task_type,
            model=request.model
        )

        if success:
            return {
                "success": True,
                "message": f"Updated {request.task_type.value} to use {request.model}",
                "updated_at": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to update assignment")

    except Exception as e:
        logger.error(f"Error updating strategic assignment: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models")
async def get_available_models():
    """Get available models by performance tier"""
    try:
        models = smart_ai_service.get_available_models()
        
        # Add model metadata
        model_info = {}
        for tier, model_list in models.items():
            model_info[tier] = []
            for model in model_list:
                model_info[tier].append({
                    "name": model,
                    "provider": smart_ai_service._get_provider_for_model(model).value,
                    "estimated_cost_per_1k_tokens": smart_ai_service._calculate_cost(model, {"total_tokens": 1000}),
                    "recommended_use_cases": smart_ai_service.model_tiers[PerformanceTier(tier)]["use_cases"]
                })

        return {
            "models_by_tier": model_info,
            "tier_descriptions": {
                "tier_1": "Premium models for critical tasks (highest quality)",
                "tier_2": "Balanced performance/cost models",
                "cost_optimized": "Cost-focused models for bulk processing"
            }
        }

    except Exception as e:
        logger.error(f"Error getting available models: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cost-summary")
async def get_cost_summary(days: int = 7):
    """Get cost summary for specified period"""
    try:
        cortex_service = SnowflakeCortexService()
        
        async with cortex_service as cortex:
            # Call stored procedure for cost summary
            cost_data = await cortex.execute_procedure(
                "OPS_MONITORING.SP_GET_AI_COST_SUMMARY",
                [
                    (datetime.now() - timedelta(days=days)).date(),
                    datetime.now().date()
                ]
            )

            if not cost_data:
                return {"cost_summary": [], "total_cost": 0, "period_days": days}

            total_cost = sum(record.get("TOTAL_COST", 0) for record in cost_data)
            
            summary = []
            for record in cost_data:
                summary.append({
                    "provider": record.get("PROVIDER"),
                    "model": record.get("MODEL"),
                    "total_requests": record.get("TOTAL_REQUESTS"),
                    "total_cost": record.get("TOTAL_COST"),
                    "avg_cost_per_request": record.get("AVG_COST_PER_REQUEST"),
                    "total_tokens": record.get("TOTAL_TOKENS"),
                    "avg_quality": record.get("AVG_QUALITY"),
                    "cache_hit_rate": record.get("CACHE_HIT_RATE")
                })

            return {
                "cost_summary": summary,
                "total_cost": total_cost,
                "period_days": days,
                "avg_cost_per_day": total_cost / max(days, 1),
                "generated_at": datetime.now().isoformat()
            }

    except Exception as e:
        logger.error(f"Error getting cost summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Configuration endpoints
@router.get("/config")
async def get_service_config():
    """Get current SmartAIService configuration"""
    try:
        return {
            "portkey_configured": bool(smart_ai_service.portkey_config["api_key"]),
            "openrouter_configured": bool(smart_ai_service.openrouter_config["api_key"]),
            "model_tiers": {
                tier.value: {
                    "models": config["models"],
                    "use_cases": config["use_cases"],
                    "preferred_provider": config["preferred_provider"].value
                }
                for tier, config in smart_ai_service.model_tiers.items()
            },
            "strategic_assignments": {
                task.value: model 
                for task, model in smart_ai_service.strategic_assignments.items()
            },
            "service_initialized": smart_ai_service.initialized
        }

    except Exception as e:
        logger.error(f"Error getting service config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/initialize")
async def initialize_service():
    """Initialize SmartAIService (if not already initialized)"""
    try:
        if not smart_ai_service.initialized:
            await smart_ai_service.initialize()
        
        return {
            "success": True,
            "message": "SmartAIService initialized successfully",
            "initialized_at": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error initializing service: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# CEO Dashboard specific endpoints
@router.get("/ceo-dashboard/summary")
async def get_ceo_dashboard_summary():
    """Get high-level summary for CEO dashboard"""
    try:
        # Get recent analytics
        analytics = await smart_ai_service.get_usage_analytics(24)
        
        # Get cost trends
        cortex_service = SnowflakeCortexService()
        async with cortex_service as cortex:
            cost_trend_data = await cortex.query_structured_data(
                table="OPS_MONITORING.V_AI_COST_ANALYTICS",
                filters={"USAGE_DATE": f">= '{(datetime.now() - timedelta(days=7)).date()}'"},
                limit=7
            )

        daily_costs = [record.get("TOTAL_COST", 0) for record in cost_trend_data] if cost_trend_data else []
        
        return {
            "summary": {
                "total_requests_24h": analytics["summary"]["total_requests"],
                "total_cost_24h": analytics["summary"]["total_cost_usd"],
                "avg_cost_per_request": analytics["summary"]["avg_cost_per_request"],
                "cache_hit_rate": analytics["summary"]["cache_hit_rate"],
                "cost_savings_from_cache": analytics["summary"]["cost_savings_from_cache"]
            },
            "gateway_health": analytics["gateway_health"],
            "cost_trend_7d": daily_costs,
            "top_models": list(analytics["model_performance"].keys())[:5],
            "strategic_assignments": analytics["strategic_assignments"],
            "generated_at": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error getting CEO dashboard summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Error handling
@router.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.now().isoformat()
        }
    ) 