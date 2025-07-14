"""
Unified AI Orchestrator
Intelligent routing between Lambda GPU and Lambda Labs with cost optimization
"""

from backend.services.unified_memory_service_v3 import UnifiedMemoryServiceV3
import logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any

from backend.services.lambda_labs_service import LambdaLabsService
from infrastructure.services.llm_router import TaskComplexity, TaskType
from infrastructure.services.modern_stack_pat_service import ModernStackPATService

logger = logging.getLogger(__name__)


class AIProvider(Enum):
    """AI provider options"""

    # REMOVED: ModernStack dependency "modern_stack_cortex"
    LAMBDA_LABS = "lambda_labs"
    AUTO = "auto"


@dataclass
class AIRequest:
    """Unified AI request structure"""

    prompt: str
    provider: AIProvider = AIProvider.AUTO
    model: str | None = None
    max_tokens: int | None = None
    temperature: float | None = None
    task_type: TaskType | None = None
    complexity: TaskComplexity | None = None
    cost_priority: str = "balanced"  # "cost", "performance", "balanced"
    use_case: str = "general"  # "embedding", "completion", "analysis", "sql"
    context: dict[str, Any] | None = None


@dataclass
class AIResponse:
    """Unified AI response structure"""

    response: str
    provider: str
    model: str
    duration: float
    cost_estimate: float
    usage: dict[str, Any]
    success: bool
    error: str | None = None
    metadata: dict[str, Any] | None = None


class IntelligentRouter:
    """Intelligent routing logic for AI requests"""

    def __init__(self):
        self.routing_rules = {
            # Use case routing
            "embedding": AIProvider.SNOWFLAKE_CORTEX,
            "sql": AIProvider.SNOWFLAKE_CORTEX,
            "data_analysis": AIProvider.SNOWFLAKE_CORTEX,
            "code_generation": AIProvider.LAMBDA_LABS,
            "creative": AIProvider.LAMBDA_LABS,
            "reasoning": AIProvider.LAMBDA_LABS,
        }

        self.cost_thresholds = {
            "simple": 100,  # tokens
            "medium": 1000,  # tokens
            "complex": 10000,  # tokens
        }

    def route_request(self, request: AIRequest) -> AIProvider:
        """Route request to optimal provider"""

        # Explicit provider override
        if request.provider != AIProvider.AUTO:
            return request.provider

        # Use case based routing
        if request.use_case in self.routing_rules:
            return self.routing_rules[request.use_case]

        # Analyze request characteristics
        prompt_tokens = len(request.prompt.split())

        # Data-local operations prefer ModernStack
        data_keywords = [
            "sql",
            "query",
            "data",
            "analytics",
            "table",
            "database",
            "warehouse",
        ]
        if any(kw in request.prompt.lower() for kw in data_keywords):
            return AIProvider.SNOWFLAKE_CORTEX

        # Complex reasoning prefers Lambda Labs
        if request.complexity == TaskComplexity.COMPLEX:
            return AIProvider.LAMBDA_LABS

        # Cost optimization
        if request.cost_priority == "cost":
            # Small requests to ModernStack, large to Lambda
            if prompt_tokens < self.cost_thresholds["medium"]:
                return AIProvider.SNOWFLAKE_CORTEX
            else:
                return AIProvider.LAMBDA_LABS

        elif request.cost_priority == "performance":
            # Performance critical to Lambda Labs
            return AIProvider.LAMBDA_LABS

        # Default balanced routing
        if prompt_tokens < self.cost_thresholds["simple"]:
            return AIProvider.LAMBDA_LABS  # Fast for simple
        elif prompt_tokens > self.cost_thresholds["complex"]:
            return AIProvider.SNOWFLAKE_CORTEX  # Better for large context
        else:
            return AIProvider.LAMBDA_LABS  # Default


class UnifiedAIOrchestrator:
    """
    Orchestrates AI requests between Lambda GPU and Lambda Labs
    Provides intelligent routing, cost optimization, and unified interface
    """

    def __init__(self):
        self.lambda_service = LambdaLabsService()
        self.memory_service_v3 = ModernStackPATService()
        self.router = IntelligentRouter()

        # Performance tracking
        self.request_history = []
        self.provider_metrics = {
            AIProvider.SNOWFLAKE_CORTEX: {
                "requests": 0,
                "total_duration": 0,
                "total_cost": 0,
                "success_rate": 0,
            },
            AIProvider.LAMBDA_LABS: {
                "requests": 0,
                "total_duration": 0,
                "total_cost": 0,
                "success_rate": 0,
            },
        }

    async def process_request(self, request: AIRequest) -> AIResponse:
        """Process unified AI request with intelligent routing"""

        start_time = time.time()

        # Route request
        provider = self.router.route_request(request)

        try:
            # Process based on provider
            if provider == AIProvider.LAMBDA_LABS:
                response = await self._process_lambda(request)
            else:
                response = await self._process_modern_stack(request)

            # Update metrics
            self._update_metrics(provider, response, success=True)

            return response

        except Exception as e:
            duration = time.time() - start_time
            error_response = AIResponse(
                response="",
                provider=provider.value,
                model=request.model or "unknown",
                duration=duration,
                cost_estimate=0,
                usage={},
                success=False,
                error=str(e),
            )

            # Update metrics
            self._update_metrics(provider, error_response, success=False)

            logger.error(f"AI request failed: {e!s}")
            return error_response

    async def _process_lambda(self, request: AIRequest) -> AIResponse:
        """Process request using Lambda Labs"""

        start_time = time.time()

        # Prepare messages
        messages = []
        if request.context:
            system_msg = f"Context: {request.context}"
            messages.append({"role": "system", "content": system_msg})
        messages.append({"role": "user", "content": request.prompt})

        # Select model
        if not request.model:
            complexity = request.complexity or TaskComplexity.MODERATE
            if complexity == TaskComplexity.SIMPLE:
                model = "llama3.1-8b-instruct"
            elif complexity == TaskComplexity.COMPLEX:
                model = "llama-4-maverick-17b-128e-instruct-fp8"
            else:
                model = "llama3.1-70b-instruct-fp8"
        else:
            model = request.model

        # Execute request
        result = await self.lambda_service.chat_completion(
            messages=messages,
            model=model,
            max_tokens=request.max_tokens or 1000,
            temperature=request.temperature or 0.7,
        )

        duration = time.time() - start_time

        # Extract response
        response_text = result["choices"][0]["message"]["content"]
        usage = result.get("usage", {})

        # Calculate cost
        cost_estimate = self._calculate_lambda_cost(model, usage)

        return AIResponse(
            response=response_text,
            provider=AIProvider.LAMBDA_LABS.value,
            model=model,
            duration=duration,
            cost_estimate=cost_estimate,
            usage=usage,
            success=True,
            metadata={"backend": "serverless", "cost_priority": request.cost_priority},
        )

    async def _process_modern_stack(self, request: AIRequest) -> AIResponse:
        """Process request using Lambda GPU"""

        start_time = time.time()

        # Handle different use cases
        if request.use_case == "embedding":
            response_data = await self.memory_service_v3.execute_cortex_embed(
                text=request.prompt, model=request.model or "e5-base-v2"
            )
            response_text = str(response_data)  # Embedding vector

        elif request.use_case == "sql":
            result = await self.memory_service_v3.natural_language_to_sql(
                query=request.prompt,
                schema_context=(
                    request.context.get("schema") if request.context else None
                ),
            )
            response_text = result.get("generated_sql", "")

        else:
            # General completion
            response_text = await self.memory_service_v3.execute_cortex_complete(
                prompt=request.prompt,
                model=request.model or "mistral-large",
                temperature=request.temperature or 0.7,
                max_tokens=request.max_tokens or 1000,
            )

        duration = time.time() - start_time

        # Estimate usage and cost
        usage = {
            "prompt_tokens": len(request.prompt.split()),
            "completion_tokens": len(response_text.split()),
            "total_tokens": len(request.prompt.split()) + len(response_text.split()),
        }

        cost_estimate = self._calculate_modern_stack_cost(usage)

        return AIResponse(
            response=response_text,
            provider=AIProvider.SNOWFLAKE_CORTEX.value,
            model=request.model or "mistral-large",
            duration=duration,
            cost_estimate=cost_estimate,
            usage=usage,
            success=True,
            metadata={"backend": "data-local", "use_case": request.use_case},
        )

    def _calculate_lambda_cost(self, model: str, usage: dict[str, Any]) -> float:
        """Calculate Lambda Labs cost"""

        # Cost per million tokens (from Lambda Labs config)
        cost_map = {
            "llama3.1-8b-instruct": 0.07,
            "llama3.1-70b-instruct-fp8": 0.35,
            "llama-4-maverick-17b-128e-instruct-fp8": 0.88,
        }

        cost_per_million = cost_map.get(model, 0.35)
        total_tokens = usage.get("total_tokens", 0)

        return (total_tokens / 1_000_000) * cost_per_million

    def _calculate_modern_stack_cost(self, usage: dict[str, Any]) -> float:
        """Calculate Lambda GPU cost"""

        # Lambda GPU pricing (approximate)
        # Typically included in compute costs
        total_tokens = usage.get("total_tokens", 0)

        # Rough estimate: $0.0001 per 1K tokens
        return (total_tokens / 1000) * 0.0001

    def _update_metrics(
        self, provider: AIProvider, response: AIResponse, success: bool
    ):
        """Update provider metrics"""

        metrics = self.provider_metrics[provider]
        metrics["requests"] += 1
        metrics["total_duration"] += response.duration
        metrics["total_cost"] += response.cost_estimate

        # Update success rate
        if success:
            current_rate = metrics["success_rate"]
            metrics["success_rate"] = (
                current_rate * (metrics["requests"] - 1) + 1
            ) / metrics["requests"]
        else:
            current_rate = metrics["success_rate"]
            metrics["success_rate"] = (
                current_rate * (metrics["requests"] - 1)
            ) / metrics["requests"]

    async def natural_language_optimization(self, command: str) -> dict[str, Any]:
        """Process natural language infrastructure optimization commands"""

        optimization_request = AIRequest(
            prompt=f"""Analyze this infrastructure optimization command and provide specific actions:

Command: {command}

Current System State:
- Providers: Lambda GPU (data-local), Lambda Labs (serverless)
- Cost Priority: Balanced
- Performance Metrics: {self.get_performance_summary()}

Available Optimization Actions:
1. Adjust routing preferences
2. Modify cost thresholds
3. Change model selection criteria
4. Update provider priorities
5. Generate performance recommendations

Provide specific, actionable recommendations in JSON format with:
- action: specific action to take
- impact: expected impact
- implementation: how to implement
- priority: high/medium/low
""",
            provider=AIProvider.LAMBDA_LABS,
            cost_priority="performance",
            use_case="analysis",
        )

        response = await self.process_request(optimization_request)

        return {
            "command": command,
            "analysis": response.response,
            "provider_used": response.provider,
            "optimization_actions": "Parse and implement based on AI response",
        }

    async def health_check(self) -> dict[str, Any]:
        """Check health of all AI services"""

        health_status = {"orchestrator": "healthy", "providers": {}}

        # Check Lambda Labs
        try:
            lambda_health = await self.lambda_service.health_check()
            health_status["providers"]["lambda_labs"] = {
                "status": "healthy" if lambda_health else "unhealthy",
                "available": lambda_health,
            }
        except Exception as e:
            health_status["providers"]["lambda_labs"] = {
                "status": "unhealthy",
                "error": str(e),
            }

        # Check ModernStack
        try:
            # REMOVED: ModernStack dependency await self.memory_service_v3.test_connection()
            health_status["providers"]["# REMOVED: ModernStack dependency {
                "status": "healthy" if modern_stack_health["connected"] else "unhealthy",
                "details": modern_stack_health,
            }
        except Exception as e:
            health_status["providers"]["# REMOVED: ModernStack dependency {
                "status": "unhealthy",
                "error": str(e),
            }

        # Overall health
        provider_statuses = [
            p.get("status", "unhealthy") for p in health_status["providers"].values()
        ]

        if all(status == "healthy" for status in provider_statuses):
            health_status["orchestrator"] = "healthy"
        elif any(status == "healthy" for status in provider_statuses):
            health_status["orchestrator"] = "degraded"
        else:
            health_status["orchestrator"] = "unhealthy"

        return health_status

    def get_performance_summary(self) -> dict[str, Any]:
        """Get performance summary across providers"""

        summary = {}

        for provider, metrics in self.provider_metrics.items():
            if metrics["requests"] > 0:
                summary[provider.value] = {
                    "total_requests": metrics["requests"],
                    "avg_duration": metrics["total_duration"] / metrics["requests"],
                    "total_cost": metrics["total_cost"],
                    "avg_cost_per_request": metrics["total_cost"] / metrics["requests"],
                    "success_rate": metrics["success_rate"],
                }

        return summary

    async def get_usage_analytics(self) -> dict[str, Any]:
        """Get comprehensive usage analytics"""

        # Get Lambda Labs usage
        lambda_usage = await self.lambda_service.get_usage_analytics()

        # Get performance summary
        performance = self.get_performance_summary()

        # Calculate cost savings
        total_requests = sum(m["requests"] for m in self.provider_metrics.values())

        if total_requests > 0:
            avg_cost = (
                sum(m["total_cost"] for m in self.provider_metrics.values())
                / total_requests
            )

            # Compare to GPU-only baseline ($6,444/month)
            monthly_projection = avg_cost * total_requests * 30  # Daily to monthly
            gpu_baseline = 6444
            savings_percentage = (
                (gpu_baseline - monthly_projection) / gpu_baseline
            ) * 100
        else:
            savings_percentage = 0

        return {
            "lambda_usage": lambda_usage,
            "performance_by_provider": performance,
            "total_requests": total_requests,
            "cost_savings": {
                "percentage": savings_percentage,
                "monthly_savings": (
                    6444 - (avg_cost * total_requests * 30) if total_requests > 0 else 0
                ),
            },
            "routing_distribution": {
                provider.value: (
                    metrics["requests"] / total_requests if total_requests > 0 else 0
                )
                for provider, metrics in self.provider_metrics.items()
            },
        }
