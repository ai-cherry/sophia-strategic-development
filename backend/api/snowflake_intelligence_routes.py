# File: backend/api/snowflake_intelligence_routes.py

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import Dict, List, Any, Optional
from pydantic import BaseModel
from datetime import datetime
from backend.services.snowflake_intelligence_service import SnowflakeIntelligenceService, IntelligenceQuery
from backend.services.automated_insights_service import AutomatedInsightsService
from backend.services.predictive_analytics_service import PredictiveAnalyticsService
# A mock for auth dependency, in a real app this would be more robust
from backend.core.auth import get_current_user
from backend.utils.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/intelligence", tags=["snowflake-intelligence"])

# Pydantic models for request/response
class NaturalLanguageQueryRequest(BaseModel):
    query: str
    context: Dict[str, Any] = {}
    include_visualizations: bool = True
    response_format: str = "comprehensive"

class DashboardMetricsRequest(BaseModel):
    timeRange: str = "30d"
    metrics: List[str] = []
    include_predictions: bool = True

class InsightGenerationRequest(BaseModel):
    force_refresh: bool = False
    priority_filter: Optional[str] = None

# Initialize services
intelligence_service = SnowflakeIntelligenceService()
insights_service = AutomatedInsightsService()
predictive_service = PredictiveAnalyticsService()

@router.on_event("startup")
async def startup_event():
    logger.info("Initializing Snowflake Intelligence services...")
    await insights_service.initialize_insight_generation()
    await predictive_service.initialize_prediction_models()
    logger.info("Snowflake Intelligence services initialized.")

@router.post("/query")
async def process_natural_language_query(
    request: NaturalLanguageQueryRequest,
    current_user: dict = Depends(get_current_user)
):
    """Process natural language query using Snowflake Intelligence"""
    try:
        query = IntelligenceQuery(
            query_text=request.query,
            user_context={**request.context, 'user_id': current_user.get('id'), 'user_role': current_user.get('role', 'user')},
            required_sources=[],
            response_format=request.response_format,
            include_visualizations=request.include_visualizations
        )
        response = await intelligence_service.process_natural_language_query(query)
        logger.info(f"Natural language query processed for user {current_user.get('id')}: {request.query}")
        return response.__dict__
    except Exception as e:
        logger.error(f"Failed to process natural language query: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/dashboard/enhanced-metrics")
async def get_enhanced_dashboard_metrics(
    request: DashboardMetricsRequest,
    current_user: dict = Depends(get_current_user)
):
    """Get enhanced dashboard metrics with AI insights"""
    try:
        base_metrics = await intelligence_service.semantic_service.get_dashboard_metrics(
            time_range=request.timeRange,
            metrics=request.metrics
        )
        insights = await insights_service.get_insights_for_metrics(request.metrics or list(base_metrics.keys()))
        predictions = {}
        if request.include_predictions:
            for metric in request.metrics or ['revenue', 'satisfaction', 'pipeline']:
                try:
                    prediction = await predictive_service.generate_prediction(
                        f"{metric}_prediction",
                        {'time_range': request.timeRange}
                    )
                    predictions[metric] = prediction.__dict__
                except Exception:
                    predictions[metric] = None
        
        return {
            "success": True,
            "metrics": base_metrics,
            "insights": [i.__dict__ for i in insights],
            "predictions": predictions,
            "last_updated": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get enhanced dashboard metrics: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/insights/automated")
async def get_automated_insights(
    priority_filter: Optional[str] = None,
    limit: int = 20,
    current_user: dict = Depends(get_current_user)
):
    """Get automated insights with optional filtering"""
    try:
        insights = await insights_service.get_active_insights(priority_filter=priority_filter, limit=limit)
        return {
            "success": True,
            "insights": [i.__dict__ for i in insights],
            "total_count": len(insights)
        }
    except Exception as e:
        logger.error(f"Failed to get automated insights: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/insights/generate")
async def generate_insights_batch(
    background_tasks: BackgroundTasks,
    request: InsightGenerationRequest,
    current_user: dict = Depends(get_current_user)
):
    """Trigger batch insight generation"""
    if request.force_refresh:
        background_tasks.add_task(insights_service.generate_insights_batch)
        return {"success": True, "message": "Insight generation started in background"}
    else:
        insights = await insights_service.get_active_insights(priority_filter=request.priority_filter)
        return {"success": True, "insights": [i.__dict__ for i in insights], "message": "Returned cached insights."}

@router.get("/predictions/dashboard")
async def get_dashboard_predictions(current_user: dict = Depends(get_current_user)):
    """Get predictions for dashboard display"""
    prediction_models = ['customer_churn_prediction', 'revenue_forecasting', 'sales_conversion_prediction']
    predictions = {}
    for model_id in prediction_models:
        try:
            prediction = await predictive_service.generate_prediction(model_id, {'current_date': datetime.now().isoformat()})
            predictions[model_id] = prediction.__dict__
        except Exception as e:
            logger.warning(f"Failed to get prediction for {model_id}: {e}")
            predictions[model_id] = None
    return {"success": True, "predictions": predictions, "generated_at": datetime.now().isoformat()}

@router.get("/health")
async def health_check():
    """Health check endpoint for Snowflake Intelligence services"""
    try:
        service_health = await intelligence_service.health_check()
        if service_health.get("status") == "healthy":
            return {"success": True, "services": service_health, "timestamp": datetime.now().isoformat()}
        else:
            raise HTTPException(status_code=503, detail=service_health)
    except Exception as e:
        logger.error(f"Health check failed: {e}", exc_info=True)
        return {"success": False, "error": str(e), "timestamp": datetime.now().isoformat()} 