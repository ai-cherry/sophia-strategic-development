"""
Enhanced Portkey LLM Gateway with OpenRouter Integration
Implements Claude-Code-Development-Kit routing patterns with intelligent model selection
"""

import json
import time
from collections.abc import AsyncGenerator
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

import aiohttp

from backend.core.auto_esc_config import get_config_value
from backend.utils.custom_logger import logger


class ModelProvider(Enum):
    """Supported model providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    DEEPSEEK = "deepseek"
    MISTRAL = "mistral"
    META = "meta"
    OPENROUTER = "openrouter"


class TaskComplexity(Enum):
    """Task complexity for intelligent routing"""
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    ARCHITECTURE = "architecture"


@dataclass
class ModelTarget:
    """Model target configuration for routing"""
    name: str
    provider: ModelProvider
    model: str
    cost_per_1k_tokens: float
    max_tokens: int
    context_window: int
    strengths: list[str]
    use_cases: list[str]


@dataclass
class RoutingDecision:
    """Result of routing decision"""
    selected_model: ModelTarget
    reasoning: str
    confidence: float
    fallback_models: list[ModelTarget]


class EnhancedPortkeyLLMGateway:
    """
    Enhanced Portkey LLM Gateway with OpenRouter Integration
    Implements Claude-Code-Development-Kit routing patterns
    """

    def __init__(self):
        self.portkey_api_key = get_config_value("portkey_api_key")
        self.openrouter_api_key = get_config_value("openrouter_api_key")
        self.base_url = "https://api.portkey.ai/v1"
        self.openrouter_base_url = "https://openrouter.ai/api/v1"

        # Performance tracking
        self.performance_metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_tokens": 0,
            "total_cost": 0.0,
            "average_latency": 0.0,
            "model_usage": {}
        }

        # Model targets optimized for different task types
        self.model_targets = self._init_model_targets()

        # Routing rules for Claude-Code-Development-Kit patterns
        self.routing_rules = self._init_routing_rules()

    def _init_model_targets(self) -> dict[str, ModelTarget]:
        """Initialize model targets with cost and capability optimization"""
        return {
            # Premium models for complex tasks
            "claude-3-5-sonnet": ModelTarget(
                name="claude-3-5-sonnet",
                provider=ModelProvider.ANTHROPIC,
                model="claude-3-5-sonnet-20241022",
                cost_per_1k_tokens=3.0,
                max_tokens=8192,
                context_window=200000,
                strengths=["creative_writing", "complex_reasoning", "code_analysis", "architecture_design"],
                use_cases=["architecture", "complex_code_generation", "strategic_analysis"]
            ),

            "gpt-4o": ModelTarget(
                name="gpt-4o",
                provider=ModelProvider.OPENAI,
                model="gpt-4o",
                cost_per_1k_tokens=2.5,
                max_tokens=16384,
                context_window=128000,
                strengths=["balanced_performance", "code_generation", "analysis"],
                use_cases=["general_tasks", "code_development", "business_intelligence"]
            ),

            # Cost-effective models for routine tasks
            "deepseek-v3": ModelTarget(
                name="deepseek-v3",
                provider=ModelProvider.DEEPSEEK,
                model="deepseek-chat",
                cost_per_1k_tokens=0.14,
                max_tokens=8192,
                context_window=64000,
                strengths=["code_generation", "technical_tasks", "cost_efficiency"],
                use_cases=["code_generation", "technical_documentation", "simple_analysis"]
            ),

            "gpt-3.5-turbo": ModelTarget(
                name="gpt-3.5-turbo",
                provider=ModelProvider.OPENAI,
                model="gpt-3.5-turbo",
                cost_per_1k_tokens=0.5,
                max_tokens=4096,
                context_window=16385,
                strengths=["speed", "cost_efficiency", "simple_tasks"],
                use_cases=["simple_queries", "chat", "basic_analysis"]
            ),

            # Specialized models for specific tasks
            "gemini-1.5-pro": ModelTarget(
                name="gemini-1.5-pro",
                provider=ModelProvider.GOOGLE,
                model="gemini-1.5-pro-latest",
                cost_per_1k_tokens=1.25,
                max_tokens=8192,
                context_window=1000000,
                strengths=["large_context", "document_analysis", "research"],
                use_cases=["large_document_analysis", "research", "context_heavy_tasks"]
            ),

            "mixtral-8x7b": ModelTarget(
                name="mixtral-8x7b",
                provider=ModelProvider.MISTRAL,
                model="mistralai/mixtral-8x7b-instruct",
                cost_per_1k_tokens=0.3,
                max_tokens=4096,
                context_window=32768,
                strengths=["multilingual", "reasoning", "cost_efficiency"],
                use_cases=["analysis", "moderate_complexity", "international_tasks"]
            )
        }

    def _init_routing_rules(self) -> dict[str, Any]:
        """Initialize routing rules following Claude-Code-Development-Kit patterns"""
        return {
            # Task type based routing
            "task_routing": {
                "architecture_design": ["claude-3-5-sonnet", "gpt-4o"],
                "code_generation": ["deepseek-v3", "gpt-4o", "claude-3-5-sonnet"],
                "business_intelligence": ["gpt-4o", "claude-3-5-sonnet", "gemini-1.5-pro"],
                "research": ["gemini-1.5-pro", "claude-3-5-sonnet", "gpt-4o"],
                "simple_chat": ["gpt-3.5-turbo", "mixtral-8x7b"],
                "document_analysis": ["gemini-1.5-pro", "claude-3-5-sonnet"],
                "infrastructure": ["gpt-4o", "deepseek-v3", "claude-3-5-sonnet"]
            },

            # Complexity based routing
            "complexity_routing": {
                TaskComplexity.SIMPLE: ["gpt-3.5-turbo", "mixtral-8x7b", "deepseek-v3"],
                TaskComplexity.MODERATE: ["deepseek-v3", "gpt-4o", "mixtral-8x7b"],
                TaskComplexity.COMPLEX: ["gpt-4o", "claude-3-5-sonnet", "gemini-1.5-pro"],
                TaskComplexity.ARCHITECTURE: ["claude-3-5-sonnet", "gpt-4o", "gemini-1.5-pro"]
            },

            # Context size routing
            "context_routing": {
                "small": ["gpt-3.5-turbo", "deepseek-v3", "mixtral-8x7b"],
                "medium": ["gpt-4o", "claude-3-5-sonnet", "deepseek-v3"],
                "large": ["gemini-1.5-pro", "claude-3-5-sonnet"],
                "extra_large": ["gemini-1.5-pro"]
            },

            # Cost optimization thresholds
            "cost_optimization": {
                "budget_mode": ["gpt-3.5-turbo", "deepseek-v3", "mixtral-8x7b"],
                "balanced_mode": ["deepseek-v3", "gpt-4o", "mixtral-8x7b"],
                "premium_mode": ["claude-3-5-sonnet", "gpt-4o", "gemini-1.5-pro"]
            }
        }

    async def route_request(
        self,
        messages: list[dict[str, str]],
        task_type: str = "general",
        complexity: TaskComplexity = TaskComplexity.MODERATE,
        cost_preference: str = "balanced_mode",
        model_override: str | None = None
    ) -> RoutingDecision:
        """
        Intelligent model routing based on Claude-Code-Development-Kit patterns
        
        Args:
            messages: Chat messages
            task_type: Type of task for routing
            complexity: Task complexity level
            cost_preference: Cost optimization preference
            model_override: Override automatic selection
            
        Returns:
            RoutingDecision with selected model and reasoning
        """
        # Override selection if specified
        if model_override and model_override in self.model_targets:
            selected_model = self.model_targets[model_override]
            return RoutingDecision(
                selected_model=selected_model,
                reasoning=f"Model override: {model_override}",
                confidence=1.0,
                fallback_models=[]
            )

        # Calculate context size
        context_size = sum(len(msg["content"]) for msg in messages)
        context_category = self._categorize_context_size(context_size)

        # Get candidate models from different routing strategies
        task_candidates = self.routing_rules["task_routing"].get(task_type, [])
        complexity_candidates = self.routing_rules["complexity_routing"].get(complexity, [])
        context_candidates = self.routing_rules["context_routing"].get(context_category, [])
        cost_candidates = self.routing_rules["cost_optimization"].get(cost_preference, [])

        # Find intersection of candidates (models that satisfy all criteria)
        all_candidates = set(task_candidates) & set(complexity_candidates) & set(context_candidates) & set(cost_candidates)

        # If no intersection, prioritize by importance
        if not all_candidates:
            all_candidates = set(complexity_candidates) & set(cost_candidates)

        if not all_candidates:
            all_candidates = set(complexity_candidates)

        if not all_candidates:
            all_candidates = ["gpt-4o"]  # Fallback

        # Select best model based on scoring
        selected_model = await self._score_and_select_model(
            list(all_candidates), task_type, complexity, context_size
        )

        # Prepare fallback models
        fallback_models = [
            self.model_targets[model_name]
            for model_name in all_candidates
            if model_name != selected_model.name
        ][:2]  # Top 2 fallbacks

        reasoning = self._generate_routing_reasoning(
            selected_model, task_type, complexity, context_category, cost_preference
        )

        return RoutingDecision(
            selected_model=selected_model,
            reasoning=reasoning,
            confidence=0.85,  # High confidence in our routing logic
            fallback_models=fallback_models
        )

    def _categorize_context_size(self, context_size: int) -> str:
        """Categorize context size for routing"""
        if context_size < 1000:
            return "small"
        elif context_size < 10000:
            return "medium"
        elif context_size < 50000:
            return "large"
        else:
            return "extra_large"

    async def _score_and_select_model(
        self,
        candidates: list[str],
        task_type: str,
        complexity: TaskComplexity,
        context_size: int
    ) -> ModelTarget:
        """Score candidate models and select the best one"""
        scored_models = []

        for model_name in candidates:
            if model_name not in self.model_targets:
                continue

            model = self.model_targets[model_name]
            score = 0.0

            # Task type alignment score
            if task_type in [use_case for use_case in model.use_cases]:
                score += 30

            # Complexity alignment score
            if complexity == TaskComplexity.ARCHITECTURE and "architecture_design" in model.strengths:
                score += 25
            elif complexity == TaskComplexity.COMPLEX and "complex_reasoning" in model.strengths:
                score += 20
            elif complexity == TaskComplexity.MODERATE and "balanced_performance" in model.strengths:
                score += 15
            elif complexity == TaskComplexity.SIMPLE and "speed" in model.strengths:
                score += 10

            # Context window adequacy
            if model.context_window >= context_size * 2:  # Good buffer
                score += 15
            elif model.context_window >= context_size:
                score += 10
            else:
                score -= 20  # Penalize insufficient context

            # Cost efficiency (inverse relationship)
            cost_efficiency_score = max(0, 20 - (model.cost_per_1k_tokens * 5))
            score += cost_efficiency_score

            # Performance history (if available)
            model_stats = self.performance_metrics["model_usage"].get(model_name, {})
            success_rate = model_stats.get("success_rate", 0.5)  # Default 50%
            score += success_rate * 10

            scored_models.append((score, model))

        # Sort by score and return best model
        scored_models.sort(key=lambda x: x[0], reverse=True)
        return scored_models[0][1] if scored_models else self.model_targets["gpt-4o"]

    def _generate_routing_reasoning(
        self,
        selected_model: ModelTarget,
        task_type: str,
        complexity: TaskComplexity,
        context_category: str,
        cost_preference: str
    ) -> str:
        """Generate human-readable reasoning for model selection"""
        return f"""
Selected {selected_model.name} for this request:
- Task type: {task_type} (matches {', '.join(selected_model.use_cases)})
- Complexity: {complexity.value} (strengths: {', '.join(selected_model.strengths[:3])})
- Context: {context_category} (window: {selected_model.context_window:,} tokens)
- Cost: ${selected_model.cost_per_1k_tokens}/1k tokens ({cost_preference})
- Provider: {selected_model.provider.value}
        """.strip()

    async def complete(
        self,
        messages: list[dict[str, str]],
        task_type: str = "general",
        complexity: TaskComplexity = TaskComplexity.MODERATE,
        cost_preference: str = "balanced_mode",
        model_override: str | None = None,
        stream: bool = False,
        max_tokens: int = 2000,
        temperature: float = 0.7,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """
        Complete with intelligent routing and fallback handling
        
        Args:
            messages: Chat messages
            task_type: Type of task
            complexity: Task complexity
            cost_preference: Cost optimization preference
            model_override: Override model selection
            stream: Whether to stream response
            max_tokens: Maximum tokens to generate
            temperature: Generation temperature
            **kwargs: Additional parameters
            
        Yields:
            Response chunks
        """
        start_time = time.time()
        self.performance_metrics["total_requests"] += 1

        try:
            # Route to optimal model
            routing_decision = await self.route_request(
                messages, task_type, complexity, cost_preference, model_override
            )

            logger.info(f"🎯 Routing decision: {routing_decision.reasoning}")

            # Attempt completion with selected model
            response_chunks = []
            tokens_used = 0

            try:
                async for chunk in self._complete_with_model(
                    routing_decision.selected_model,
                    messages,
                    stream,
                    max_tokens,
                    temperature,
                    **kwargs
                ):
                    response_chunks.append(chunk)
                    tokens_used += len(chunk.split())
                    yield chunk

                # Track successful completion
                self._update_performance_metrics(
                    routing_decision.selected_model.name,
                    start_time,
                    tokens_used,
                    routing_decision.selected_model.cost_per_1k_tokens,
                    True
                )

            except Exception as e:
                logger.warning(f"Primary model {routing_decision.selected_model.name} failed: {e}")

                # Try fallback models
                for fallback_model in routing_decision.fallback_models:
                    try:
                        logger.info(f"🔄 Trying fallback model: {fallback_model.name}")

                        async for chunk in self._complete_with_model(
                            fallback_model,
                            messages,
                            stream,
                            max_tokens,
                            temperature,
                            **kwargs
                        ):
                            response_chunks.append(chunk)
                            tokens_used += len(chunk.split())
                            yield chunk

                        # Track fallback success
                        self._update_performance_metrics(
                            fallback_model.name,
                            start_time,
                            tokens_used,
                            fallback_model.cost_per_1k_tokens,
                            True
                        )
                        return

                    except Exception as fallback_error:
                        logger.warning(f"Fallback model {fallback_model.name} failed: {fallback_error}")
                        continue

                # All models failed
                self.performance_metrics["failed_requests"] += 1
                yield f"Error: All models failed. Primary: {e}"

        except Exception as e:
            logger.error(f"Routing error: {e}")
            self.performance_metrics["failed_requests"] += 1
            yield f"Error: Routing failed - {str(e)}"

    async def _complete_with_model(
        self,
        model: ModelTarget,
        messages: list[dict[str, str]],
        stream: bool,
        max_tokens: int,
        temperature: float,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Complete with specific model using appropriate provider"""

        if model.provider in [ModelProvider.OPENAI, ModelProvider.ANTHROPIC] and self.portkey_api_key:
            # Use Portkey for OpenAI/Anthropic
            async for chunk in self._complete_via_portkey(
                model, messages, stream, max_tokens, temperature, **kwargs
            ):
                yield chunk

        else:
            # Use OpenRouter for other models
            async for chunk in self._complete_via_openrouter(
                model, messages, stream, max_tokens, temperature, **kwargs
            ):
                yield chunk

    async def _complete_via_portkey(
        self,
        model: ModelTarget,
        messages: list[dict[str, str]],
        stream: bool,
        max_tokens: int,
        temperature: float,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Complete via Portkey gateway"""
        headers = {
            "Authorization": f"Bearer {self.portkey_api_key}",
            "Content-Type": "application/json",
            "x-portkey-provider": model.provider.value,
            "x-portkey-config": json.dumps({
                "cache": {"mode": "semantic", "max_age": 3600},
                "retry": {"attempts": 2}
            })
        }

        payload = {
            "model": model.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": stream,
            **kwargs
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload
            ) as response:
                if stream:
                    async for line in response.content:
                        if line:
                            try:
                                data = json.loads(line.decode().replace("data: ", ""))
                                if "choices" in data and data["choices"]:
                                    content = data["choices"][0].get("delta", {}).get("content", "")
                                    if content:
                                        yield content
                            except (json.JSONDecodeError, KeyError):
                                continue
                else:
                    result = await response.json()
                    if "choices" in result and result["choices"]:
                        content = result["choices"][0].get("message", {}).get("content", "")
                        if content:
                            yield content

    async def _complete_via_openrouter(
        self,
        model: ModelTarget,
        messages: list[dict[str, str]],
        stream: bool,
        max_tokens: int,
        temperature: float,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Complete via OpenRouter"""
        headers = {
            "Authorization": f"Bearer {self.openrouter_api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://sophia-intel.ai",
            "X-Title": "Sophia AI"
        }

        payload = {
            "model": model.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": stream,
            **kwargs
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.openrouter_base_url}/chat/completions",
                headers=headers,
                json=payload
            ) as response:
                if stream:
                    async for line in response.content:
                        if line:
                            try:
                                data = json.loads(line.decode().replace("data: ", ""))
                                if "choices" in data and data["choices"]:
                                    content = data["choices"][0].get("delta", {}).get("content", "")
                                    if content:
                                        yield content
                            except (json.JSONDecodeError, KeyError):
                                continue
                else:
                    result = await response.json()
                    if "choices" in result and result["choices"]:
                        content = result["choices"][0].get("message", {}).get("content", "")
                        if content:
                            yield content

    def _update_performance_metrics(
        self,
        model_name: str,
        start_time: float,
        tokens_used: int,
        cost_per_1k: float,
        success: bool
    ):
        """Update performance metrics"""
        duration = time.time() - start_time
        cost = (tokens_used / 1000) * cost_per_1k

        if success:
            self.performance_metrics["successful_requests"] += 1

        self.performance_metrics["total_tokens"] += tokens_used
        self.performance_metrics["total_cost"] += cost

        # Update running average latency
        total_requests = self.performance_metrics["total_requests"]
        current_avg = self.performance_metrics["average_latency"]
        self.performance_metrics["average_latency"] = (
            (current_avg * (total_requests - 1) + duration) / total_requests
        )

        # Update model-specific metrics
        if model_name not in self.performance_metrics["model_usage"]:
            self.performance_metrics["model_usage"][model_name] = {
                "requests": 0,
                "successes": 0,
                "tokens": 0,
                "cost": 0.0,
                "success_rate": 0.0
            }

        model_stats = self.performance_metrics["model_usage"][model_name]
        model_stats["requests"] += 1
        model_stats["tokens"] += tokens_used
        model_stats["cost"] += cost

        if success:
            model_stats["successes"] += 1

        model_stats["success_rate"] = model_stats["successes"] / model_stats["requests"]

    async def get_performance_metrics(self) -> dict[str, Any]:
        """Get gateway performance metrics"""
        return {
            "gateway_status": "active",
            "total_requests": self.performance_metrics["total_requests"],
            "success_rate": (
                self.performance_metrics["successful_requests"] /
                max(1, self.performance_metrics["total_requests"])
            ) * 100,
            "average_latency": round(self.performance_metrics["average_latency"], 3),
            "total_cost": round(self.performance_metrics["total_cost"], 4),
            "total_tokens": self.performance_metrics["total_tokens"],
            "model_usage": self.performance_metrics["model_usage"],
            "available_models": len(self.model_targets),
            "routing_rules": len(self.routing_rules)
        }

    async def health_check(self) -> dict[str, Any]:
        """Health check for the gateway"""
        return {
            "service": "enhanced_portkey_llm_gateway",
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "providers": {
                "portkey": bool(self.portkey_api_key),
                "openrouter": bool(self.openrouter_api_key)
            },
            "capabilities": [
                "Intelligent model routing",
                "Cost optimization",
                "Automatic fallbacks",
                "Performance tracking",
                "Claude-Code-Development-Kit patterns"
            ],
            "model_targets": list(self.model_targets.keys()),
            "metrics": await self.get_performance_metrics()
        }


# Global gateway instance
_gateway_instance = None


async def get_enhanced_portkey_gateway() -> EnhancedPortkeyLLMGateway:
    """Get singleton gateway instance"""
    global _gateway_instance
    if _gateway_instance is None:
        _gateway_instance = EnhancedPortkeyLLMGateway()
    return _gateway_instance
