"""
Lambda Labs Serverless API Routes
=================================
FastAPI routes for Lambda Labs Serverless AI infrastructure with
comprehensive endpoints for chat, analysis, monitoring, and cost optimization.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from backend.services.lambda_labs_serverless_service import (
    LambdaLabsServerlessService,
    analyze_with_lambda,
    ask_lambda,
    get_lambda_service,
)

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/api/v1/lambda-labs-serverless", tags=["Lambda Labs Serverless"]
)

# Pydantic models
class ChatMessage(BaseModel):
    """Chat message model"""

    role: str = Field(..., description="Message role (user, assistant, system)")
    content: str = Field(..., description="Message content")

class ChatCompletionRequest(BaseModel):
    """Chat completion request model"""

    messages: list[ChatMessage] = Field(..., description="List of chat messages")
    context_hints: list[str] | None = Field(
        None, description="Context hints for model selection"
    )
    max_tokens: int | None = Field(None, description="Maximum tokens to generate")
    temperature: float | None = Field(None, description="Temperature for generation")
    stream: bool | None = Field(False, description="Enable streaming response")

class ChatCompletionResponse(BaseModel):
    """Chat completion response model"""

    response: str = Field(..., description="AI response")
    model_used: str = Field(..., description="Model used for generation")
    cached: bool = Field(..., description="Whether response was cached")
    cost: float = Field(..., description="Cost of the request")
    response_time: float = Field(..., description="Response time in seconds")
    input_tokens: int = Field(..., description="Number of input tokens")
    output_tokens: int = Field(..., description="Number of output tokens")

class AnalysisRequest(BaseModel):
    """Analysis request model"""

    data: str = Field(..., description="Data to analyze")
    analysis_type: str = Field("general", description="Type of analysis")
    context_hints: list[str] | None = Field(None, description="Context hints")

class AnalysisResponse(BaseModel):
    """Analysis response model"""

    analysis: str = Field(..., description="Analysis results")
    model_used: str = Field(..., description="Model used")
    cost: float = Field(..., description="Cost of analysis")
    recommended_models: list[str] = Field(..., description="Recommended models")
    metadata: dict[str, Any] = Field(..., description="Additional metadata")

class ModelRecommendationRequest(BaseModel):
    """Model recommendation request"""

    task_type: str = Field(..., description="Type of task")
    context_size: int = Field(0, description="Estimated context size")

class UsageStatsResponse(BaseModel):
    """Usage statistics response"""

    total_requests: int
    successful_requests: int
    failed_requests: int
    success_rate: float
    total_cost: float
    daily_cost: float
    hourly_cost: float
    budget_remaining: float
    total_input_tokens: int
    total_output_tokens: int
    average_response_time: float
    model_usage: dict[str, int]
    available_models: list[str]
    routing_strategy: str
    cache_hits: int
    recent_requests: list[dict[str, Any]]

class HealthCheckResponse(BaseModel):
    """Health check response"""

    status: str
    response_time: float | None = None
    api_accessible: bool
    models_available: int
    budget_status: str
    daily_cost: float
    cache_size: int
    last_request_time: str | None = None
    error: str | None = None

class CostOptimizationResponse(BaseModel):
    """Cost optimization response"""

    current_daily_cost: float
    budget_utilization: float
    model_stats: dict[str, Any]
    most_efficient_model: str | None
    potential_daily_savings: float
    recommendations: list[str]

# Dependency to get service
async def get_service() -> LambdaLabsServerlessService:
    """Get Lambda Labs service instance"""
    return await get_lambda_service()

# Routes
@router.post("/chat/completions", response_model=ChatCompletionResponse)
async def chat_completion(
    request: ChatCompletionRequest,
    service: LambdaLabsServerlessService = Depends(get_service),
):
    """
    Generate chat completion using Lambda Labs Serverless API

    This endpoint provides access to Lambda Labs' top 5 serverless models
    with intelligent routing based on context and cost optimization.
    """
    try:
        # Convert Pydantic models to dict
        messages = [msg.dict() for msg in request.messages]

        # Prepare kwargs
        kwargs = {}
        if request.max_tokens:
            kwargs["max_tokens"] = request.max_tokens
        if request.temperature:
            kwargs["temperature"] = request.temperature

        # Handle streaming
        if request.stream:
            # For streaming, we'll need to implement server-sent events
            # This is a placeholder for now
            raise HTTPException(status_code=501, detail="Streaming not yet implemented")

        # Make request
        result = await service.chat_completion(
            messages=messages, context_hints=request.context_hints, **kwargs
        )

        # Extract response content
        response_content = result["response"].choices[0].message.content

        return ChatCompletionResponse(
            response=response_content,
            model_used=result["model_used"],
            cached=result["cached"],
            cost=result["cost"],
            response_time=result["response_time"],
            input_tokens=result["input_tokens"],
            output_tokens=result["output_tokens"],
        )

    except Exception as e:
        logger.error(f"Chat completion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat/stream")
async def chat_completion_stream(
    request: ChatCompletionRequest,
    service: LambdaLabsServerlessService = Depends(get_service),
):
    """
    Stream chat completion response

    Returns a streaming response with server-sent events for real-time
    chat completion generation.
    """

    async def generate():
        try:
            # Convert messages
            messages = [msg.dict() for msg in request.messages]

            # For now, we'll simulate streaming by yielding the complete response
            # In a full implementation, this would use the streaming API
            result = await service.chat_completion(
                messages=messages,
                context_hints=request.context_hints,
                stream=True,  # This would need to be implemented in the service
            )

            # Yield the response
            yield f"data: {json.dumps({'content': result['response'].choices[0].message.content})}\n\n"
            yield f"data: {json.dumps({'done': True, 'metadata': {'model': result['model_used'], 'cost': result['cost']}})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
        },
    )

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_data(
    request: AnalysisRequest,
    service: LambdaLabsServerlessService = Depends(get_service),
):
    """
    Analyze data using Lambda Labs with optimal model selection

    Automatically selects the best model based on the analysis type
    and data characteristics.
    """
    try:
        result = await analyze_with_lambda(
            data=request.data, analysis_type=request.analysis_type
        )

        return AnalysisResponse(**result)

    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/models/recommendations")
async def get_model_recommendations(
    task_type: str,
    context_size: int = 0,
    service: LambdaLabsServerlessService = Depends(get_service),
):
    """
    Get model recommendations for a specific task type

    Returns recommended models based on task type and context size.
    """
    try:
        recommendations = await service.get_model_recommendations(
            task_type=task_type, context_size=context_size
        )

        return {
            "task_type": task_type,
            "context_size": context_size,
            "recommended_models": recommendations,
            "available_models": list(service.models.keys()),
        }

    except Exception as e:
        logger.error(f"Model recommendations failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/models/list")
async def list_models(service: LambdaLabsServerlessService = Depends(get_service)):
    """
    List all available Lambda Labs models with their specifications

    Returns detailed information about each model including pricing,
    context windows, and use cases.
    """
    try:
        models_info = []

        for model_name, model_config in service.models.items():
            models_info.append(
                {
                    "name": model_config.name,
                    "context_window": model_config.context_window,
                    "price_input": model_config.price_input,
                    "price_output": model_config.price_output,
                    "use_cases": model_config.use_cases,
                    "priority": model_config.priority,
                    "tier": model_config.tier.value,
                }
            )

        # Sort by priority
        models_info.sort(key=lambda x: x["priority"])

        return {
            "models": models_info,
            "total_models": len(models_info),
            "routing_strategy": service.routing_strategy.value,
            "fallback_chain": service.fallback_chain,
        }

    except Exception as e:
        logger.error(f"List models failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/usage/stats", response_model=UsageStatsResponse)
async def get_usage_stats(service: LambdaLabsServerlessService = Depends(get_service)):
    """
    Get comprehensive usage statistics

    Returns detailed statistics about requests, costs, performance,
    and model usage patterns.
    """
    try:
        stats = await service.get_usage_stats()
        return UsageStatsResponse(**stats)

    except Exception as e:
        logger.error(f"Usage stats failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/usage/cost-breakdown")
async def get_cost_breakdown(
    service: LambdaLabsServerlessService = Depends(get_service),
):
    """
    Get detailed cost breakdown by model, time period, and usage patterns
    """
    try:
        stats = await service.get_usage_stats()

        # Calculate cost per model
        model_costs = {}
        for request in service.request_history:
            if request.success:
                if request.model_used not in model_costs:
                    model_costs[request.model_used] = 0.0
                model_costs[request.model_used] += request.cost

        # Calculate hourly trends
        hourly_trends = {}
        for request in service.request_history:
            if request.success:
                hour_key = request.timestamp.strftime("%H:00")
                if hour_key not in hourly_trends:
                    hourly_trends[hour_key] = 0.0
                hourly_trends[hour_key] += request.cost

        return {
            "total_cost": stats["total_cost"],
            "daily_cost": stats["daily_cost"],
            "budget_remaining": stats["budget_remaining"],
            "budget_utilization": (stats["daily_cost"] / service.daily_budget) * 100,
            "cost_per_model": model_costs,
            "hourly_trends": hourly_trends,
            "cost_per_request": (
                stats["total_cost"] / stats["total_requests"]
                if stats["total_requests"] > 0
                else 0
            ),
            "cost_per_token": {
                "input": (
                    stats["total_cost"] / stats["total_input_tokens"]
                    if stats["total_input_tokens"] > 0
                    else 0
                ),
                "output": (
                    stats["total_cost"] / stats["total_output_tokens"]
                    if stats["total_output_tokens"] > 0
                    else 0
                ),
            },
        }

    except Exception as e:
        logger.error(f"Cost breakdown failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health", response_model=HealthCheckResponse)
async def health_check(service: LambdaLabsServerlessService = Depends(get_service)):
    """
    Perform health check of Lambda Labs Serverless service

    Tests API connectivity, model availability, and budget status.
    """
    try:
        health_result = await service.health_check()
        return HealthCheckResponse(**health_result)

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthCheckResponse(
            status="unhealthy",
            api_accessible=False,
            models_available=0,
            budget_status="unknown",
            daily_cost=0.0,
            cache_size=0,
            error=str(e),
        )

@router.get("/optimize/costs", response_model=CostOptimizationResponse)
async def optimize_costs(service: LambdaLabsServerlessService = Depends(get_service)):
    """
    Analyze and optimize costs

    Provides recommendations for cost optimization based on usage patterns
    and model performance analysis.
    """
    try:
        optimization_result = await service.optimize_costs()
        return CostOptimizationResponse(**optimization_result)

    except Exception as e:
        logger.error(f"Cost optimization failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/optimize/clear-cache")
async def clear_cache(service: LambdaLabsServerlessService = Depends(get_service)):
    """
    Clear response cache

    Clears all cached responses to force fresh API calls.
    """
    try:
        cache_size = len(service.response_cache)
        service.response_cache.clear()

        return {
            "message": "Cache cleared successfully",
            "cleared_entries": cache_size,
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Clear cache failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/config/routing-strategy")
async def set_routing_strategy(
    strategy: str, service: LambdaLabsServerlessService = Depends(get_service)
):
    """
    Set routing strategy for model selection

    Available strategies: performance_first, cost_first, balanced
    """
    try:
        from backend.services.lambda_labs_serverless_service import RoutingStrategy

        # Validate strategy
        try:
            new_strategy = RoutingStrategy(strategy)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid strategy. Must be one of: {[s.value for s in RoutingStrategy]}",
            )

        old_strategy = service.routing_strategy
        service.routing_strategy = new_strategy

        return {
            "message": "Routing strategy updated successfully",
            "old_strategy": old_strategy.value,
            "new_strategy": new_strategy.value,
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Set routing strategy failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/config/budget")
async def set_budget(
    daily_budget: float,
    monthly_budget: float | None = None,
    service: LambdaLabsServerlessService = Depends(get_service),
):
    """
    Set budget limits for Lambda Labs usage

    Updates daily and optionally monthly budget limits.
    """
    try:
        if daily_budget <= 0:
            raise HTTPException(status_code=400, detail="Daily budget must be positive")

        old_daily = service.daily_budget
        service.daily_budget = daily_budget

        if monthly_budget:
            if monthly_budget <= 0:
                raise HTTPException(
                    status_code=400, detail="Monthly budget must be positive"
                )
            old_monthly = service.monthly_budget
            service.monthly_budget = monthly_budget

        return {
            "message": "Budget updated successfully",
            "old_daily_budget": old_daily,
            "new_daily_budget": daily_budget,
            "old_monthly_budget": old_monthly if monthly_budget else None,
            "new_monthly_budget": monthly_budget,
            "current_daily_cost": service._get_daily_cost(),
            "budget_remaining": daily_budget - service._get_daily_cost(),
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Set budget failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/admin/reset-stats")
async def reset_stats(service: LambdaLabsServerlessService = Depends(get_service)):
    """
    Reset usage statistics (admin only)

    Clears all usage statistics and request history.
    """
    try:
        from backend.services.lambda_labs_serverless_service import UsageStats

        old_stats = await service.get_usage_stats()

        # Reset statistics
        service.usage_stats = UsageStats()
        service.request_history.clear()

        return {
            "message": "Statistics reset successfully",
            "old_stats": {
                "total_requests": old_stats["total_requests"],
                "total_cost": old_stats["total_cost"],
                "successful_requests": old_stats["successful_requests"],
            },
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Reset stats failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Natural language endpoints
@router.post("/ask")
async def ask_question(question: str, context_hints: list[str] | None = None):
    """
    Ask a question using natural language interface

    Simple endpoint for asking questions with automatic model selection.
    """
    try:
        response = await ask_lambda(question, context_hints)

        return {
            "question": question,
            "response": response,
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Ask question failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Background task endpoints
@router.post("/tasks/cost-monitoring")
async def start_cost_monitoring(
    background_tasks: BackgroundTasks,
    service: LambdaLabsServerlessService = Depends(get_service),
):
    """
    Start background cost monitoring task

    Monitors costs and sends alerts when thresholds are exceeded.
    """

    async def monitor_costs():
        """Background task to monitor costs"""
        while True:
            try:
                daily_cost = service._get_daily_cost()
                hourly_cost = service._get_hourly_cost()

                # Check thresholds
                if daily_cost >= service.daily_budget * 0.9:
                    logger.warning(f"Daily budget 90% exceeded: ${daily_cost:.2f}")

                if hourly_cost >= 10.0:
                    logger.warning(f"Hourly cost high: ${hourly_cost:.2f}")

                # Wait 5 minutes before next check
                await asyncio.sleep(300)

            except Exception as e:
                logger.error(f"Cost monitoring error: {e}")
                await asyncio.sleep(60)  # Wait 1 minute on error

    background_tasks.add_task(monitor_costs)

    return {
        "message": "Cost monitoring started",
        "monitoring_interval": "5 minutes",
        "timestamp": datetime.now().isoformat(),
    }

# Export router
__all__ = ["router"]
