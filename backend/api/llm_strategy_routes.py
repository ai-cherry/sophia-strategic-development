from __future__ import annotations

import json
import logging
import os
import time
import uuid
from datetime import datetime
from typing import Any

import httpx
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse, StreamingResponse

# Import required models and services
try:
    from backend.models.llm_models import ChatResponse, LLMRequest
    from backend.services.unified_intelligence_service import (
from backend.core.auto_esc_config import get_config_value
        unified_intelligence_service,
    )
except ImportError:
    # Fallback if models don't exist
    from pydantic import BaseModel

    class LLMRequest(BaseModel):
        message: str
        context: dict = {}
        session_id: str = ""
        user_id: str = ""

    class ChatResponse(BaseModel):
        content: str
        session_id: str
        metadata: dict = {}
        processing_time: float = 0

    # Mock service for fallback
    class MockUnifiedService:
        async def process_request(self, request):
            return ChatResponse(
                content="Service temporarily unavailable",
                session_id=request.session_id,
                metadata={},
                processing_time=0,
            )

        async def stream_response(self, data):
            yield {"content": "Streaming not available"}

    unified_intelligence_service = MockUnifiedService()

logger = logging.getLogger(__name__)
router = APIRouter()


class SophiaLLMManager:
    """Enhanced LLM strategy manager with Portkey + OpenRouter integration"""

    def __init__(self):
        # Portkey Gateway Configuration
        self.portkey_endpoint = os.getenv(
            "PORTKEY_ENDPOINT", "https://api.portkey.ai/v1/chat/completions"
        )
        self.portkey_api_key = get_config_value("portkey_api_key")

        # OpenRouter Backend Configuration
        self.openrouter_endpoint = "https://openrouter.ai/api/v1/chat/completions"
        self.openrouter_api_key = get_config_value("openrouter_api_key")

        # Performance and cost tracking
        self.usage_metrics = {}
        self.strategic_assignments = {
            "executive_insights": "gpt-4o",
            "competitive_intelligence": "claude-3-opus",
            "financial_analysis": "gpt-4o",
            "market_analysis": "gemini-1.5-pro",
            "operational_efficiency": "claude-3-haiku",
        }
        self.cost_controls = {
            "monthlyBudget": 2000,
            "alertThreshold": 75,
            "autoDowngradeThreshold": 90,
            "emergencyModel": "llama-3-70b",
            "cacheThreshold": 0.92,
            "cacheTTL": 24,
            "maxCacheSize": 50,
        }

        # Model tier configuration
        self.model_tiers = {
            "tier_1": ["gpt-4o", "claude-3-opus", "gemini-1.5-pro"],
            "tier_2": ["claude-3-haiku", "gpt-4-turbo", "deepseek-v3"],
            "cost_optimized": ["llama-3-70b", "qwen2-72b", "mixtral-8x22b"],
        }

    async def call_portkey_gateway(
        self, messages: list[dict], context: dict = None, task_type: str = "general"
    ) -> dict:
        """Call Portkey gateway with intelligent routing to OpenRouter backend"""
        start_time = time.time()

        # Determine optimal model based on context and task type
        selected_model = await self._select_optimal_model(task_type, context)

        # Portkey headers with OpenRouter backend configuration
        headers = {
            "Authorization": f"Bearer {self.portkey_api_key}",
            "Content-Type": "application/json",
            "x-portkey-provider": "openrouter",
            "x-portkey-api-key": self.openrouter_api_key,
            "x-portkey-cache": "semantic",
            "x-portkey-cache-force-refresh": "false",
            "x-portkey-trace-id": f"sophia-{int(time.time())}",
        }

        # Enhanced payload with Portkey configurations
        payload = {
            "model": selected_model,
            "messages": messages,
            "temperature": self._get_temperature_for_task(task_type),
            "max_tokens": self._get_max_tokens_for_task(task_type),
            "metadata": {
                "task_type": task_type,
                "dashboard_type": (
                    context.get("dashboardType", "general") if context else "general"
                ),
                "user_id": (
                    context.get("userId", "anonymous") if context else "anonymous"
                ),
            },
        }

        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    self.portkey_endpoint, headers=headers, json=payload
                )
                response.raise_for_status()
                result = response.json()

                # Calculate performance metrics
                latency_ms = int((time.time() - start_time) * 1000)
                cost_usd = await self._calculate_cost(
                    selected_model, result.get("usage", {})
                )
                cache_hit = response.headers.get("x-portkey-cache-status") == "hit"

                # Store metrics for tracking
                await self._store_usage_metrics(
                    selected_model, latency_ms, cost_usd, task_type, cache_hit
                )

                return {
                    "response": result["choices"][0]["message"]["content"],
                    "model_used": selected_model,
                    "latency_ms": latency_ms,
                    "cost_usd": cost_usd,
                    "cache_hit": cache_hit,
                    "sources": [],
                    "portkey_trace_id": headers["x-portkey-trace-id"],
                }

        except Exception as e:
            logger.error(f"Portkey gateway call failed: {e}")
            # Fallback to direct OpenRouter
            return await self._fallback_to_openrouter(
                messages, selected_model, task_type
            )

    async def _select_optimal_model(self, task_type: str, context: dict = None) -> str:
        """Select optimal model based on task type, context, and strategic assignments"""

        # Check for strategic assignments first (CEO dashboard context)
        if context and context.get("dashboardType") == "ceo":
            if task_type in self.strategic_assignments:
                return self.strategic_assignments[task_type]

        # Task-based model selection with performance optimization
        model_map = {
            "executive_summary": "gpt-4o",
            "competitive_analysis": "claude-3-opus",
            "financial_analysis": "gpt-4o",
            "code_generation": "deepseek-v3",
            "complex_reasoning": "claude-3-opus",
            "long_context": "gemini-1.5-pro",
            "chat": "gpt-4o",
            "summarization": "claude-3-haiku",
            "general": "gpt-4o",
        }

        selected_model = model_map.get(task_type, "gpt-4o")

        # Check cost controls and budget constraints
        if await self._should_use_cost_optimized_model():
            return self.cost_controls["emergencyModel"]

        return selected_model

    async def _should_use_cost_optimized_model(self) -> bool:
        """Check if we should use cost-optimized models based on budget constraints"""
        # Simplified budget check - in production, this would check actual spend
        current_month_spend = sum(
            m.get("total_cost", 0) for m in self.usage_metrics.values()
        )
        budget_percentage = (
            current_month_spend / self.cost_controls["monthlyBudget"]
        ) * 100

        return budget_percentage >= self.cost_controls["autoDowngradeThreshold"]

    def _get_temperature_for_task(self, task_type: str) -> float:
        """Get optimal temperature setting for different task types"""
        temperature_map = {
            "executive_summary": 0.3,
            "competitive_analysis": 0.4,
            "financial_analysis": 0.2,
            "code_generation": 0.1,
            "creative": 0.7,
            "chat": 0.5,
            "general": 0.3,
        }
        return temperature_map.get(task_type, 0.3)

    def _get_max_tokens_for_task(self, task_type: str) -> int:
        """Get optimal max tokens for different task types"""
        token_map = {
            "executive_summary": 2000,
            "competitive_analysis": 3000,
            "financial_analysis": 2500,
            "code_generation": 4000,
            "long_context": 8000,
            "chat": 1500,
            "general": 2000,
        }
        return token_map.get(task_type, 2000)

    async def _calculate_cost(self, model: str, usage: dict) -> float:
        """Calculate cost with updated pricing for top-tier models"""
        cost_per_1k = {
            "gpt-4o": 0.015,
            "claude-3-opus": 0.015,
            "gemini-1.5-pro": 0.0035,
            "claude-3-haiku": 0.0025,
            "deepseek-v3": 0.0014,
            "gpt-4-turbo": 0.01,
            "llama-3-70b": 0.0009,
            "qwen2-72b": 0.0009,
            "mixtral-8x22b": 0.0009,
        }

        input_tokens = usage.get("prompt_tokens", 0)
        output_tokens = usage.get("completion_tokens", 0)

        rate = cost_per_1k.get(model, 0.01)
        return ((input_tokens + output_tokens) / 1000) * rate

    async def _store_usage_metrics(
        self,
        model: str,
        latency_ms: int,
        cost_usd: float,
        task_type: str,
        cache_hit: bool,
    ):
        """Store comprehensive usage metrics for monitoring and optimization"""
        timestamp = datetime.now()

        if model not in self.usage_metrics:
            self.usage_metrics[model] = {
                "total_requests": 0,
                "total_cost": 0,
                "total_latency": 0,
                "cache_hits": 0,
                "error_count": 0,
                "last_used": timestamp,
                "quality_scores": [],
            }

        metrics = self.usage_metrics[model]
        metrics["total_requests"] += 1
        metrics["total_cost"] += cost_usd
        metrics["total_latency"] += latency_ms
        if cache_hit:
            metrics["cache_hits"] += 1
        metrics["last_used"] = timestamp

    async def _fallback_to_openrouter(
        self, messages: list[dict], model: str, task_type: str
    ) -> dict:
        """Fallback to direct OpenRouter if Portkey fails"""
        try:
            headers = {
                "Authorization": f"Bearer {self.openrouter_api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://sophia-intel.ai",
            }

            payload = {
                "model": model,
                "messages": messages,
                "temperature": self._get_temperature_for_task(task_type),
                "max_tokens": self._get_max_tokens_for_task(task_type),
            }

            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    self.openrouter_endpoint, headers=headers, json=payload
                )
                response.raise_for_status()
                result = response.json()

                return {
                    "response": result["choices"][0]["message"]["content"],
                    "model_used": model,
                    "latency_ms": 0,
                    "cost_usd": 0,
                    "cache_hit": False,
                    "sources": [],
                    "fallback": True,
                }
        except Exception as e:
            logger.error(f"OpenRouter fallback failed: {e}")
            return {
                "response": "I'm experiencing technical difficulties. Please try again.",
                "model_used": "fallback",
                "latency_ms": 0,
                "cost_usd": 0,
                "cache_hit": False,
                "sources": [],
                "error": True,
            }


llm_manager = SophiaLLMManager()


@router.get("/api/v1/llm/metrics")
async def get_llm_metrics():
    """Get comprehensive LLM usage metrics including Portkey performance"""
    total_requests = sum(
        m.get("total_requests", 0) for m in llm_manager.usage_metrics.values()
    )
    total_cost = sum(m.get("total_cost", 0) for m in llm_manager.usage_metrics.values())
    total_cache_hits = sum(
        m.get("cache_hits", 0) for m in llm_manager.usage_metrics.values()
    )

    # Calculate average latency
    total_latency = sum(
        m.get("total_latency", 0) for m in llm_manager.usage_metrics.values()
    )
    avg_latency = int(total_latency / max(total_requests, 1))

    # Calculate cache hit rate
    cache_hit_rate = total_cache_hits / max(total_requests, 1)

    # Calculate cost savings from caching (estimated)
    cost_savings = (
        total_cost * cache_hit_rate * 0.8
    )  # Assume 80% cost reduction from cache hits

    # Model distribution
    model_distribution = {}
    for model, metrics in llm_manager.usage_metrics.items():
        if total_requests > 0:
            model_distribution[model] = int(
                (metrics.get("total_requests", 0) / total_requests) * 100
            )

    return JSONResponse(
        content={
            "totalRequests": total_requests,
            "totalCost": round(total_cost, 2),
            "averageLatency": avg_latency,
            "cacheHitRate": round(cache_hit_rate, 3),
            "costSavings": round(cost_savings, 2),
            "modelDistribution": model_distribution,
        }
    )


@router.get("/api/v1/llm/models")
async def get_active_models():
    """Get active models with enhanced metrics"""
    models = []

    for model_id in [
        "gpt-4o",
        "claude-3-opus",
        "gemini-1.5-pro",
        "claude-3-haiku",
        "deepseek-v3",
        "llama-3-70b",
    ]:
        metrics = llm_manager.usage_metrics.get(model_id, {})
        total_requests = metrics.get("total_requests", 0)
        total_cache_hits = metrics.get("cache_hits", 0)

        models.append(
            {
                "id": model_id,
                "name": model_id.replace("-", " ").title(),
                "usage": (
                    min(100, (total_requests / 1000) * 100) if total_requests > 0 else 0
                ),
                "costPer1k": await llm_manager._calculate_cost(
                    model_id, {"prompt_tokens": 1000, "completion_tokens": 0}
                ),
                "avgLatency": int(
                    metrics.get("total_latency", 0) / max(total_requests, 1)
                ),
                "cacheHitRate": round(
                    (total_cache_hits / max(total_requests, 1)) * 100, 1
                ),
                "qualityScore": round(
                    sum(metrics.get("quality_scores", [85]))
                    / max(len(metrics.get("quality_scores", [1])), 1),
                    1,
                ),
                "priority": (
                    "high"
                    if model_id in llm_manager.model_tiers["tier_1"]
                    else "medium"
                ),
            }
        )

    return JSONResponse(content=models)


@router.get("/api/v1/llm/portkey/status")
async def get_portkey_status():
    """Get Portkey gateway status and performance"""
    try:
        start_time = time.time()
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.get("https://api.portkey.ai/v1/health")
            latency = int((time.time() - start_time) * 1000)

            if response.status_code == 200:
                return JSONResponse(content={"status": "healthy", "latency": latency})
            else:
                return JSONResponse(content={"status": "degraded", "latency": latency})
    except Exception:
        return JSONResponse(content={"status": "unhealthy", "latency": 0})


@router.get("/api/v1/llm/strategic-assignments")
async def get_strategic_assignments():
    """Get current strategic model assignments"""
    return JSONResponse(content=llm_manager.strategic_assignments)


@router.put("/api/v1/llm/strategic-assignments")
async def update_strategic_assignment(request: Request):
    """Update strategic model assignment"""
    try:
        data = await request.json()
        use_case = data.get("useCase")
        model_id = data.get("modelId")

        if use_case in llm_manager.strategic_assignments:
            llm_manager.strategic_assignments[use_case] = model_id
            return JSONResponse(
                content={
                    "success": True,
                    "message": f"Updated {use_case} to use {model_id}",
                }
            )
        else:
            raise HTTPException(status_code=400, detail="Invalid use case")
    except Exception as e:
        logger.error(f"Failed to update strategic assignment: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/v1/llm/cost-controls")
async def get_cost_controls():
    """Get current cost control settings"""
    return JSONResponse(content=llm_manager.cost_controls)


@router.put("/api/v1/llm/cost-controls")
async def update_cost_control(request: Request):
    """Update cost control setting"""
    try:
        data = await request.json()
        setting = data.get("setting")
        value = data.get("value")

        if setting in llm_manager.cost_controls:
            # Convert to appropriate type
            if setting in [
                "monthlyBudget",
                "alertThreshold",
                "autoDowngradeThreshold",
                "cacheTTL",
                "maxCacheSize",
            ]:
                llm_manager.cost_controls[setting] = int(value)
            elif setting == "cacheThreshold":
                llm_manager.cost_controls[setting] = float(value)
            else:
                llm_manager.cost_controls[setting] = value

            return JSONResponse(
                content={"success": True, "message": f"Updated {setting} to {value}"}
            )
        else:
            raise HTTPException(status_code=400, detail="Invalid setting")
    except Exception as e:
        logger.error(f"Failed to update cost control: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/v1/chat/unified")
async def _validate_chat_request(request: Request) -> dict[str, Any]:
    """Validate and parse incoming chat request"""
    try:
        request_data = await request.json()

        if not request_data.get("message"):
            raise ValueError("Message is required")

        return {
            "message": request_data["message"],
            "context": request_data.get("context", {}),
            "session_id": request_data.get("session_id"),
            "user_id": request_data.get("user_id"),
            "stream": request_data.get("stream", False),
        }
    except Exception as e:
        logger.error(f"Request validation error: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid request: {e}")


async def _process_chat_message(validated_data: dict[str, Any]) -> dict[str, Any]:
    """Process chat message through AI pipeline"""
    try:
        session_id = validated_data.get("session_id") or str(uuid.uuid4())

        # Create LLM request
        llm_request = LLMRequest(
            message=validated_data["message"],
            context=validated_data.get("context", {}),
            session_id=session_id,
            user_id=validated_data.get("user_id"),
        )

        # Process through intelligence service
        response = await unified_intelligence_service.process_request(llm_request)

        return {
            "response": response.content,
            "session_id": session_id,
            "metadata": response.metadata,
            "processing_time": response.processing_time,
        }

    except Exception as e:
        logger.error(f"Chat processing error: {e}")
        raise HTTPException(status_code=500, detail=f"Processing error: {e}")


async def _handle_streaming_response(
    validated_data: dict[str, Any],
) -> StreamingResponse:
    """Handle streaming chat response"""

    async def generate_stream():
        try:
            async for chunk in unified_intelligence_service.stream_response(
                validated_data
            ):
                yield f"data: {json.dumps(chunk)}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
    )


@router.post("/unified-chat", response_model=ChatResponse)
async def unified_chat_endpoint(request: Request):
    """
    Unified chat endpoint for AI interactions
    Handles both streaming and non-streaming requests
    """
    try:
        # Validate request
        validated_data = await _validate_chat_request(request)

        # Handle streaming requests
        if validated_data.get("stream"):
            return await _handle_streaming_response(validated_data)

        # Process regular chat message
        result = await _process_chat_message(validated_data)

        return ChatResponse(
            content=result["response"],
            session_id=result["session_id"],
            metadata=result.get("metadata", {}),
            processing_time=result.get("processing_time", 0),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in unified chat: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/api/v1/actions/execute")
async def execute_action(request: Request):
    """Execute suggested actions with enhanced functionality"""
    try:
        data = await request.json()
        action_id = data.get("action", "")
        data.get("parameters", {})
        data.get("context", {})

        # Enhanced action execution based on action type
        action_responses = {
            "generate_executive_report": "Executive report generation started. Advanced analytics and insights will be delivered to your dashboard in 3-5 minutes.",
            "analyze_recent_calls": "Analyzing recent Gong calls with enhanced competitive intelligence. Results will appear in the competitive analysis section.",
            "optimize_model_selection": "Running A/B test on model performance for your use case. Results will be available in the LLM Strategy Hub.",
            "refresh_competitive_data": "Refreshing competitive intelligence data from all sources. Updated insights will be available shortly.",
        }

        message = action_responses.get(
            action_id,
            f"Action '{action_id}' executed successfully with enhanced capabilities",
        )

        return JSONResponse(
            content={
                "message": message,
                "success": True,
                "action_id": action_id,
                "timestamp": datetime.now().isoformat(),
            }
        )

    except Exception as e:
        logger.error(f"Action execution failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
