"""
Lambda Labs Serverless AI Service
==================================
Revolutionary serverless AI infrastructure using Lambda Labs Inference API
with intelligent model routing, cost optimization, and enterprise-grade monitoring.
"""

from backend.services.unified_memory_service_v3 import UnifiedMemoryServiceV3
import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

import aiohttp
import backoff
from openai import AsyncOpenAI

from backend.core.auto_esc_config import get_config_value
from backend.services.unified_memory_service_v2 import UnifiedMemoryServiceV2

logger = logging.getLogger(__name__)


class ModelTier(Enum):
    """Model performance tiers"""

    TIER1_PREMIUM = "tier1"
    TIER2_SPECIALIZED = "tier2"
    TIER3_BUDGET = "tier3"


class RoutingStrategy(Enum):
    """Routing strategy options"""

    PERFORMANCE_FIRST = "performance_first"
    COST_FIRST = "cost_first"
    BALANCED = "balanced"


@dataclass
class ModelConfig:
    """Configuration for a Lambda Labs model"""

    name: str
    context_window: int
    price_input: float
    price_output: float
    use_cases: list[str]
    priority: int
    tier: ModelTier


@dataclass
class RequestMetrics:
    """Metrics for a single request"""

    model_used: str
    input_tokens: int
    output_tokens: int
    cost: float
    response_time: float
    timestamp: datetime
    success: bool
    error_message: str | None = None


@dataclass
class UsageStats:
    """Usage statistics tracking"""

    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_cost: float = 0.0
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    average_response_time: float = 0.0
    model_usage: dict[str, int] = field(default_factory=dict)
    hourly_cost: dict[str, float] = field(default_factory=dict)
    daily_cost: dict[str, float] = field(default_factory=dict)


class LambdaLabsServerlessService:
    """
    Revolutionary Lambda Labs Serverless AI Service

    Features:
    - Intelligent model routing based on context and cost
    - Real-time cost monitoring and budget enforcement
    - Performance optimization with caching and batching
    - Enterprise-grade monitoring and alerting
    - Seamless integration with existing Sophia AI infrastructure
    """

    def __init__(self):
        """Initialize the Lambda Labs Serverless Service"""
        # API Configuration
        self.cloud_api_key = get_config_value("LAMBDA_CLOUD_API_KEY")
        self.inference_api_key = get_config_value("LAMBDA_API_KEY")
        self.inference_endpoint = get_config_value(
            "LAMBDA_INFERENCE_ENDPOINT", "https://api.lambdalabs.com/v1"
        )

        # Validate credentials
        if not self.inference_api_key:
            raise ValueError("LAMBDA_API_KEY not configured in Pulumi ESC")

        # Initialize OpenAI-compatible client
        self.client = AsyncOpenAI(
            api_key=self.inference_api_key, base_url=self.inference_endpoint
        )

        # Model configurations (July 2025 Top 5 Endpoints)
        self.models = {
            "llama-4-maverick-17b-128e-instruct": ModelConfig(
                name="llama-4-maverick-17b-128e-instruct",
                context_window=1000000,
                price_input=0.18,
                price_output=0.60,
                use_cases=[
                    "long-document-rag",
                    "multi-step-agents",
                    "executive-analysis",
                ],
                priority=1,
                tier=ModelTier.TIER1_PREMIUM,
            ),
            "llama-4-scout-17b-16e-instruct": ModelConfig(
                name="llama-4-scout-17b-16e-instruct",
                context_window=1000000,
                price_input=0.08,
                price_output=0.30,
                use_cases=[
                    "high-volume-chat",
                    "customer-support",
                    "business-intelligence",
                ],
                priority=2,
                tier=ModelTier.TIER1_PREMIUM,
            ),
            "deepseek-v3-0324": ModelConfig(
                name="deepseek-v3-0324",
                context_window=164000,
                price_input=0.34,
                price_output=0.88,
                use_cases=["coding-copilots", "data-analysis", "math-reasoning"],
                priority=3,
                tier=ModelTier.TIER2_SPECIALIZED,
            ),
            "llama-3.1-405b-instruct": ModelConfig(
                name="llama-3.1-405b-instruct",
                context_window=131000,
                price_input=0.80,
                price_output=0.80,
                use_cases=["premium-content", "creative-tasks", "complex-reasoning"],
                priority=4,
                tier=ModelTier.TIER2_SPECIALIZED,
            ),
            "qwen-3-32b": ModelConfig(
                name="qwen-3-32b",
                context_window=41000,
                price_input=0.10,
                price_output=0.30,
                use_cases=["code-review", "pr-comments", "documentation"],
                priority=5,
                tier=ModelTier.TIER3_BUDGET,
            ),
        }

        # Configuration
        self.routing_strategy = RoutingStrategy(
            get_config_value("LAMBDA_ROUTING_STRATEGY", "performance_first")
        )
        self.daily_budget = float(get_config_value("LAMBDA_DAILY_BUDGET", "100.0"))
        self.monthly_budget = float(get_config_value("LAMBDA_MONTHLY_BUDGET", "2500.0"))

        # Usage tracking
        self.usage_stats = UsageStats()
        self.request_history: list[RequestMetrics] = []

        # Performance cache
        self.response_cache: dict[str, tuple[Any, datetime]] = {}
        self.cache_ttl = timedelta(hours=1)

        # Fallback chain for high availability
        self.fallback_chain = [
            "llama-4-scout-17b-16e-instruct",
            "deepseek-v3-0324",
            "qwen-3-32b",
        ]

        # Integration with Lambda GPU
        self.# REMOVED: ModernStack dependency UnifiedMemoryServiceV2()

        logger.info(
            "🚀 Lambda Labs Serverless Service initialized with 5 premium models"
        )

    def _calculate_cost(
        self, model_name: str, input_tokens: int, output_tokens: int
    ) -> float:
        """Calculate cost for a request"""
        model = self.models.get(model_name)
        if not model:
            return 0.0

        input_cost = (input_tokens / 1000000) * model.price_input
        output_cost = (output_tokens / 1000000) * model.price_output

        return input_cost + output_cost

    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count for text"""
        # Rough estimation: 1 token ≈ 4 characters
        return len(text) // 4

    def _select_model(
        self, messages: list[dict[str, str]], context_hints: list[str] | None = None
    ) -> str:
        """
        Intelligent model selection based on context and routing strategy

        Args:
            messages: Chat messages
            context_hints: Additional context hints for routing

        Returns:
            Selected model name
        """
        # Analyze input
        full_text = " ".join([msg.get("content", "") for msg in messages])
        estimated_tokens = self._estimate_tokens(full_text)
        context_hints = context_hints or []

        # Add content-based hints
        text_lower = full_text.lower()
        if any(
            keyword in text_lower
            for keyword in ["code", "programming", "debug", "review"]
        ):
            context_hints.append("code_tasks")
        elif any(
            keyword in text_lower
            for keyword in ["creative", "story", "marketing", "content"]
        ):
            context_hints.append("creative_tasks")
        elif any(
            keyword in text_lower
            for keyword in ["analysis", "report", "dashboard", "metrics"]
        ):
            context_hints.append("business_intelligence")

        # Check budget constraints
        current_daily_cost = self._get_daily_cost()
        budget_remaining = self.daily_budget - current_daily_cost

        if budget_remaining < 5.0:  # Less than $5 remaining
            logger.warning(
                f"Budget constraint: ${budget_remaining:.2f} remaining, using budget model"
            )
            return "qwen-3-32b"

        # Context-based routing
        if "code_tasks" in context_hints:
            return "deepseek-v3-0324"
        elif "creative_tasks" in context_hints:
            return "llama-3.1-405b-instruct"
        elif "business_intelligence" in context_hints:
            return "llama-4-scout-17b-16e-instruct"
        elif estimated_tokens > 50000:  # Long document
            return "llama-4-maverick-17b-128e-instruct"

        # Strategy-based routing
        if self.routing_strategy == RoutingStrategy.PERFORMANCE_FIRST:
            return (
                "llama-4-scout-17b-16e-instruct"  # Best balance of performance and cost
            )
        elif self.routing_strategy == RoutingStrategy.COST_FIRST:
            return "qwen-3-32b"
        else:  # BALANCED
            return "llama-4-scout-17b-16e-instruct"

    def _get_daily_cost(self) -> float:
        """Get today's total cost"""
        today = datetime.now().date()
        return sum(
            metric.cost
            for metric in self.request_history
            if metric.timestamp.date() == today
        )

    def _get_hourly_cost(self) -> float:
        """Get current hour's cost"""
        current_hour = datetime.now().replace(minute=0, second=0, microsecond=0)
        return sum(
            metric.cost
            for metric in self.request_history
            if metric.timestamp >= current_hour
        )

    def _check_budget_limits(self) -> bool:
        """Check if within budget limits"""
        daily_cost = self._get_daily_cost()
        hourly_cost = self._get_hourly_cost()

        if daily_cost >= self.daily_budget:
            logger.error(
                f"Daily budget exceeded: ${daily_cost:.2f} >= ${self.daily_budget:.2f}"
            )
            return False

        if hourly_cost >= 10.0:  # $10/hour limit
            logger.warning(f"Hourly budget high: ${hourly_cost:.2f}")
            return False

        return True

    def _get_cache_key(self, messages: list[dict[str, str]], model: str) -> str:
        """Generate cache key for request"""
        content = json.dumps(messages, sort_keys=True)
        return f"{model}:{hash(content)}"

    def _get_cached_response(self, cache_key: str) -> Any | None:
        """Get cached response if available and not expired"""
        if cache_key in self.response_cache:
            response, timestamp = self.response_cache[cache_key]
            if datetime.now() - timestamp < self.cache_ttl:
                logger.info("Cache hit for request")
                return response
            else:
                del self.response_cache[cache_key]
        return None

    def _cache_response(self, cache_key: str, response: Any) -> None:
        """Cache response"""
        self.response_cache[cache_key] = (response, datetime.now())

    @backoff.on_exception(
        backoff.expo,
        (aiohttp.ClientError, asyncio.TimeoutError),
        max_tries=3,
        max_time=30,
    )
    async def _make_request(
        self, messages: list[dict[str, str]], model: str, **kwargs
    ) -> Any:
        """Make request to Lambda Labs API with retry logic"""
        try:
            response = await self.client.chat.completions.create(
                model=model, messages=messages, **kwargs
            )
            return response
        except Exception as e:
            logger.error(f"Request failed for model {model}: {e}")
            raise

    async def chat_completion(
        self,
        messages: list[dict[str, str]],
        context_hints: list[str] | None = None,
        **kwargs,
    ) -> dict[str, Any]:
        """
        Generate chat completion using Lambda Labs Serverless API

        Args:
            messages: Chat messages
            context_hints: Context hints for model selection
            **kwargs: Additional parameters for the API

        Returns:
            Chat completion response with metadata
        """
        start_time = time.time()

        # Check budget limits
        if not self._check_budget_limits():
            raise ValueError("Budget limits exceeded")

        # Select optimal model
        selected_model = self._select_model(messages, context_hints)

        # Check cache
        cache_key = self._get_cache_key(messages, selected_model)
        cached_response = self._get_cached_response(cache_key)
        if cached_response:
            return {
                "response": cached_response,
                "model_used": selected_model,
                "cached": True,
                "cost": 0.0,
                "response_time": time.time() - start_time,
            }

        # Try primary model with fallback
        last_error = None
        for attempt, model_name in enumerate([selected_model] + self.fallback_chain):
            if model_name == selected_model and attempt > 0:
                continue  # Skip duplicate

            try:
                logger.info(f"Attempting request with model: {model_name}")
                response = await self._make_request(messages, model_name, **kwargs)

                # Calculate metrics
                input_tokens = response.usage.prompt_tokens
                output_tokens = response.usage.completion_tokens
                cost = self._calculate_cost(model_name, input_tokens, output_tokens)
                response_time = time.time() - start_time

                # Record metrics
                metrics = RequestMetrics(
                    model_used=model_name,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    cost=cost,
                    response_time=response_time,
                    timestamp=datetime.now(),
                    success=True,
                )
                self.request_history.append(metrics)
                self._update_usage_stats(metrics)

                # Cache response
                self._cache_response(cache_key, response)

                logger.info(
                    f"✅ Request successful: {model_name}, cost: ${cost:.4f}, time: {response_time:.2f}s"
                )

                return {
                    "response": response,
                    "model_used": model_name,
                    "cached": False,
                    "cost": cost,
                    "response_time": response_time,
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                }

            except Exception as e:
                last_error = e
                logger.warning(f"Model {model_name} failed: {e}")
                continue

        # All models failed
        error_metrics = RequestMetrics(
            model_used=selected_model,
            input_tokens=0,
            output_tokens=0,
            cost=0.0,
            response_time=time.time() - start_time,
            timestamp=datetime.now(),
            success=False,
            error_message=str(last_error),
        )
        self.request_history.append(error_metrics)
        self._update_usage_stats(error_metrics)

        raise RuntimeError(f"All models failed. Last error: {last_error}")

    def _update_usage_stats(self, metrics: RequestMetrics) -> None:
        """Update usage statistics"""
        self.usage_stats.total_requests += 1

        if metrics.success:
            self.usage_stats.successful_requests += 1
            self.usage_stats.total_cost += metrics.cost
            self.usage_stats.total_input_tokens += metrics.input_tokens
            self.usage_stats.total_output_tokens += metrics.output_tokens

            # Update model usage
            if metrics.model_used not in self.usage_stats.model_usage:
                self.usage_stats.model_usage[metrics.model_used] = 0
            self.usage_stats.model_usage[metrics.model_used] += 1

            # Update hourly/daily cost tracking
            hour_key = metrics.timestamp.strftime("%Y-%m-%d %H:00")
            day_key = metrics.timestamp.strftime("%Y-%m-%d")

            if hour_key not in self.usage_stats.hourly_cost:
                self.usage_stats.hourly_cost[hour_key] = 0.0
            self.usage_stats.hourly_cost[hour_key] += metrics.cost

            if day_key not in self.usage_stats.daily_cost:
                self.usage_stats.daily_cost[day_key] = 0.0
            self.usage_stats.daily_cost[day_key] += metrics.cost
        else:
            self.usage_stats.failed_requests += 1

        # Update average response time
        if self.usage_stats.total_requests > 0:
            total_time = sum(m.response_time for m in self.request_history)
            self.usage_stats.average_response_time = (
                total_time / self.usage_stats.total_requests
            )

    async def get_usage_stats(self) -> dict[str, Any]:
        """Get comprehensive usage statistics"""
        return {
            "total_requests": self.usage_stats.total_requests,
            "successful_requests": self.usage_stats.successful_requests,
            "failed_requests": self.usage_stats.failed_requests,
            "success_rate": (
                self.usage_stats.successful_requests / self.usage_stats.total_requests
                if self.usage_stats.total_requests > 0
                else 0
            ),
            "total_cost": self.usage_stats.total_cost,
            "daily_cost": self._get_daily_cost(),
            "hourly_cost": self._get_hourly_cost(),
            "budget_remaining": self.daily_budget - self._get_daily_cost(),
            "total_input_tokens": self.usage_stats.total_input_tokens,
            "total_output_tokens": self.usage_stats.total_output_tokens,
            "average_response_time": self.usage_stats.average_response_time,
            "model_usage": self.usage_stats.model_usage,
            "available_models": list(self.models.keys()),
            "routing_strategy": self.routing_strategy.value,
            "cache_hits": len(self.response_cache),
            "recent_requests": [
                {
                    "model": m.model_used,
                    "cost": m.cost,
                    "response_time": m.response_time,
                    "success": m.success,
                    "timestamp": m.timestamp.isoformat(),
                }
                for m in self.request_history[-10:]  # Last 10 requests
            ],
        }

    async def get_model_recommendations(
        self, task_type: str, context_size: int = 0
    ) -> list[str]:
        """
        Get model recommendations for a specific task type

        Args:
            task_type: Type of task (e.g., "code", "creative", "analysis")
            context_size: Estimated context size in tokens

        Returns:
            List of recommended model names
        """
        recommendations = []

        # Filter by context window
        suitable_models = [
            model
            for model in self.models.values()
            if model.context_window >= context_size
        ]

        # Filter by use case
        task_keywords = {
            "code": ["coding-copilots", "code-review", "data-analysis"],
            "creative": ["creative-tasks", "premium-content"],
            "analysis": [
                "business-intelligence",
                "data-analysis",
                "executive-analysis",
            ],
            "chat": ["high-volume-chat", "customer-support"],
            "long_document": ["long-document-rag", "multi-step-agents"],
        }

        keywords = task_keywords.get(task_type, [])
        if keywords:
            suitable_models = [
                model
                for model in suitable_models
                if any(keyword in model.use_cases for keyword in keywords)
            ]

        # Sort by priority (lower number = higher priority)
        suitable_models.sort(key=lambda x: x.priority)

        return [model.name for model in suitable_models[:3]]  # Top 3 recommendations

    async def health_check(self) -> dict[str, Any]:
        """Perform health check of the service"""
        try:
            # Test a simple request
            test_messages = [{"role": "user", "content": "Hello"}]
            start_time = time.time()

            response = await self.chat_completion(messages=test_messages, max_tokens=10)

            response_time = time.time() - start_time

            return {
                "status": "healthy",
                "response_time": response_time,
                "api_accessible": True,
                "models_available": len(self.models),
                "budget_status": "ok" if self._check_budget_limits() else "warning",
                "daily_cost": self._get_daily_cost(),
                "cache_size": len(self.response_cache),
                "last_request_time": (
                    self.request_history[-1].timestamp.isoformat()
                    if self.request_history
                    else None
                ),
            }

        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "api_accessible": False,
                "models_available": 0,
                "budget_status": "unknown",
            }

    async def optimize_costs(self) -> dict[str, Any]:
        """Analyze and optimize costs"""
        if not self.request_history:
            return {"message": "No request history available"}

        # Analyze model performance vs cost
        model_stats = {}
        for model_name in self.models.keys():
            model_requests = [
                m
                for m in self.request_history
                if m.model_used == model_name and m.success
            ]

            if model_requests:
                avg_cost = sum(m.cost for m in model_requests) / len(model_requests)
                avg_response_time = sum(m.response_time for m in model_requests) / len(
                    model_requests
                )

                model_stats[model_name] = {
                    "requests": len(model_requests),
                    "avg_cost": avg_cost,
                    "avg_response_time": avg_response_time,
                    "efficiency_score": (
                        avg_response_time / avg_cost if avg_cost > 0 else 0
                    ),
                }

        # Find most efficient model
        best_model = (
            min(model_stats.items(), key=lambda x: x[1]["efficiency_score"])[0]
            if model_stats
            else None
        )

        # Calculate potential savings
        current_daily_cost = self._get_daily_cost()
        potential_savings = 0.0

        if best_model and current_daily_cost > 0:
            best_model_cost = model_stats[best_model]["avg_cost"]
            current_avg_cost = (
                current_daily_cost / self.usage_stats.successful_requests
                if self.usage_stats.successful_requests > 0
                else 0
            )

            if current_avg_cost > best_model_cost:
                potential_savings = (
                    current_avg_cost - best_model_cost
                ) * self.usage_stats.successful_requests

        return {
            "current_daily_cost": current_daily_cost,
            "budget_utilization": (current_daily_cost / self.daily_budget) * 100,
            "model_stats": model_stats,
            "most_efficient_model": best_model,
            "potential_daily_savings": potential_savings,
            "recommendations": [
                "Use Scout model for most business intelligence tasks",
                "Use Qwen for simple code reviews",
                "Cache responses for repeated queries",
                "Batch similar requests when possible",
            ],
        }

    async def close(self) -> None:
        """Clean up resources"""
        await self.client.aclose()
        logger.info("Lambda Labs Serverless Service closed")


# Global service instance
_lambda_service: LambdaLabsServerlessService | None = None


async def get_lambda_service() -> LambdaLabsServerlessService:
    """Get or create the global Lambda Labs service instance"""
    global _lambda_service
    if _lambda_service is None:
        _lambda_service = LambdaLabsServerlessService()
    return _lambda_service


# Natural language interface functions
async def ask_lambda(question: str, context_hints: list[str] | None = None) -> str:
    """
    Simple natural language interface to Lambda Labs

    Args:
        question: Question to ask
        context_hints: Optional context hints for model selection

    Returns:
        AI response as string
    """
    service = await get_lambda_service()

    messages = [{"role": "user", "content": question}]

    result = await service.chat_completion(messages, context_hints)

    return result["response"].choices[0].message.content


async def analyze_with_lambda(
    data: str, analysis_type: str = "general"
) -> dict[str, Any]:
    """
    Analyze data using Lambda Labs with appropriate model selection

    Args:
        data: Data to analyze
        analysis_type: Type of analysis (code, creative, business, etc.)

    Returns:
        Analysis results with metadata
    """
    service = await get_lambda_service()

    # Get model recommendations
    recommendations = await service.get_model_recommendations(
        task_type=analysis_type, context_size=service._estimate_tokens(data)
    )

    messages = [
        {
            "role": "system",
            "content": f"You are an expert analyst performing {analysis_type} analysis.",
        },
        {"role": "user", "content": f"Please analyze the following data:\n\n{data}"},
    ]

    result = await service.chat_completion(messages, context_hints=[analysis_type])

    return {
        "analysis": result["response"].choices[0].message.content,
        "model_used": result["model_used"],
        "cost": result["cost"],
        "recommended_models": recommendations,
        "metadata": {
            "response_time": result["response_time"],
            "input_tokens": result["input_tokens"],
            "output_tokens": result["output_tokens"],
        },
    }
