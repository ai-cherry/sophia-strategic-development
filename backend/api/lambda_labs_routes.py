"""API routes for Lambda Labs integration."""

from typing import Any, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from backend.services.lambda_labs_chat_integration import LambdaLabsChatIntegration
from infrastructure.monitoring.lambda_labs_cost_monitor import LambdaLabsCostMonitor
from infrastructure.services.lambda_labs_hybrid_router import LambdaLabsHybridRouter

router = APIRouter(prefix="/api/v1/lambda-labs", tags=["lambda-labs"])

# Services
lambda_integration = LambdaLabsChatIntegration()
cost_monitor = LambdaLabsCostMonitor()
router_service = LambdaLabsHybridRouter()


class GenerateRequest(BaseModel):
    """Request for text generation."""

    prompt: str = Field(..., description="Input prompt")
    model: Optional[str] = Field(None, description="Model to use")
    cost_priority: str = Field("balanced", description="Cost priority")
    max_tokens: int = Field(1000, description="Maximum tokens")
    temperature: float = Field(0.7, description="Sampling temperature")
    force_backend: Optional[str] = Field(None, description="Force specific backend")


class GenerateResponse(BaseModel):
    """Response from text generation."""

    text: str
    model: str
    backend: str
    tokens_used: int
    cost_usd: float
    latency_ms: Optional[int] = None


class UsageStatsResponse(BaseModel):
    """Usage statistics response."""

    period_days: int
    model_stats: dict[str, Any]
    total_cost: float
    total_requests: int
    budget_status: dict[str, Any]


class CostEstimateResponse(BaseModel):
    """Cost estimation response."""

    prompt_length: int
    estimated_tokens: int
    cost_estimates: dict[str, float]
    recommended_model: str


@router.post("/generate", response_model=GenerateResponse)
async def generate_text(request: GenerateRequest) -> GenerateResponse:
    """Generate text using Lambda Labs.

    Args:
        request: Generation request

    Returns:
        Generated text with metadata
    """
    try:
        # Check budget
        if not cost_monitor.is_within_budget():
            raise HTTPException(status_code=402, detail="Lambda Labs budget exceeded")

        # Generate
        result = await router_service.generate(
            messages=[{"role": "user", "content": request.prompt}],
            model=request.model,
            cost_priority=request.cost_priority,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            force_backend=request.force_backend,
        )

        # Extract response
        text = result.get("choices", [{}])[0].get("message", {}).get("content", "")
        usage = result.get("usage", {})
        tokens = usage.get("total_tokens", 0)

        # Calculate cost
        model = result.get("model", "llama3.1-70b-instruct-fp8")
        cost_per_million = {
            "llama3.1-8b-instruct": 0.07,
            "llama3.1-70b-instruct-fp8": 0.35,
            "llama-4-maverick-17b-128e-instruct-fp8": 0.88,
        }.get(model, 0.35)

        cost = (tokens / 1_000_000) * cost_per_million

        return GenerateResponse(
            text=text,
            model=model,
            backend=result.get("backend", "unknown"),
            tokens_used=tokens,
            cost_usd=cost,
            latency_ms=result.get("latency_ms"),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/usage/stats", response_model=UsageStatsResponse)
async def get_usage_stats(
    days: int = Query(7, description="Number of days to analyze")
) -> UsageStatsResponse:
    """Get Lambda Labs usage statistics.

    Args:
        days: Number of days to analyze

    Returns:
        Usage statistics and budget status
    """
    try:
        # Get usage stats
        stats = router_service.serverless.get_usage_stats(days=days)

        # Get budget status
        budget_status = await cost_monitor.check_and_alert()

        # Calculate totals
        total_cost = sum(
            model_stat["cost"] for model_stat in stats.get("model_stats", {}).values()
        )
        total_requests = sum(
            model_stat["requests"]
            for model_stat in stats.get("model_stats", {}).values()
        )

        return UsageStatsResponse(
            period_days=days,
            model_stats=stats.get("model_stats", {}),
            total_cost=total_cost,
            total_requests=total_requests,
            budget_status=budget_status,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/estimate-cost", response_model=CostEstimateResponse)
async def estimate_cost(prompt: str) -> CostEstimateResponse:
    """Estimate cost for processing a prompt.

    Args:
        prompt: Prompt to estimate cost for

    Returns:
        Cost estimates for different models
    """
    try:
        # Estimate tokens (rough approximation)
        prompt_length = len(prompt)
        estimated_tokens = prompt_length // 4 + 500  # Add some for response

        # Calculate costs
        cost_estimates = {
            "llama3.1-8b-instruct": (estimated_tokens / 1_000_000) * 0.07,
            "llama3.1-70b-instruct-fp8": (estimated_tokens / 1_000_000) * 0.35,
            "llama-4-maverick-17b-128e-instruct-fp8": (estimated_tokens / 1_000_000)
            * 0.88,
        }

        # Recommend model based on complexity
        if prompt_length < 200:
            recommended = "llama3.1-8b-instruct"
        elif prompt_length > 1000:
            recommended = "llama-4-maverick-17b-128e-instruct-fp8"
        else:
            recommended = "llama3.1-70b-instruct-fp8"

        return CostEstimateResponse(
            prompt_length=prompt_length,
            estimated_tokens=estimated_tokens,
            cost_estimates=cost_estimates,
            recommended_model=recommended,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/budget/status")
async def get_budget_status() -> dict[str, Any]:
    """Get current budget status.

    Returns:
        Budget status with alerts
    """
    try:
        return await cost_monitor.check_and_alert()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/budget/remaining")
async def get_remaining_budget() -> dict[str, float]:
    """Get remaining budget.

    Returns:
        Remaining daily and monthly budgets
    """
    try:
        return cost_monitor.get_remaining_budget()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint.

    Returns:
        Health status
    """
    return {"status": "healthy", "service": "lambda-labs-integration"}
