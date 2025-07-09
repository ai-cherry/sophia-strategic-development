"""
Portkey/OpenRouter Gateway
Handles routing through Portkey with OpenRouter fallback
"""

import json
import time
from collections.abc import AsyncGenerator
from typing import Any, Optional

import aiohttp

from backend.core.auto_esc_config import get_config_value
from shared.utils.custom_logger import logger

from .config_schema import LLMRouterConfig, ModelConfig
from .enums import TaskComplexity, TaskType
from .metrics import (
    llm_cost_usd_total,
    llm_errors_total,
    llm_routing_decisions,
    llm_tokens_total,
)


class PortkeyGateway:
    """
    Gateway for Portkey and OpenRouter integration
    Implements intelligent routing with cost optimization
    """

    def __init__(self, config: LLMRouterConfig):
        self.config = config
        self.portkey_api_key = get_config_value("portkey_api_key")
        self.openrouter_api_key = get_config_value("openrouter_api_key")
        self.openai_api_key = get_config_value("openai_api_key")
        self.anthropic_api_key = get_config_value("anthropic_api_key")

        self.portkey_base_url = "https://api.portkey.ai/v1"
        self.openrouter_base_url = "https://openrouter.ai/api/v1"

        # Circuit breaker state
        self._circuit_breaker = {
            "portkey": {"failures": 0, "last_failure": 0, "is_open": False},
            "openrouter": {"failures": 0, "last_failure": 0, "is_open": False},
        }

        # Performance tracking
        self._model_performance = {}

    async def route_and_complete(
        self,
        prompt: str,
        task: TaskType,
        complexity: TaskComplexity,
        stream: bool = True,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        model_override: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
        **kwargs,
    ) -> AsyncGenerator[str, None]:
        """
        Route request to optimal model and complete
        """
        # Select model based on routing rules
        selected_model = await self._select_model(
            task, complexity, model_override, len(prompt)
        )

        # Track routing decision
        llm_routing_decisions.labels(
            task_type=task.value,
            complexity=complexity.value,
            selected_model=selected_model.name,
        ).inc()

        # Determine provider and complete
        if self._should_use_portkey(selected_model):
            async for chunk in self._complete_via_portkey(
                selected_model,
                prompt,
                stream,
                temperature,
                max_tokens,
                metadata,
                **kwargs,
            ):
                yield chunk
        else:
            async for chunk in self._complete_via_openrouter(
                selected_model,
                prompt,
                stream,
                temperature,
                max_tokens,
                metadata,
                **kwargs,
            ):
                yield chunk

    async def _select_model(
        self,
        task: TaskType,
        complexity: TaskComplexity,
        model_override: Optional[str],
        context_size: int,
    ) -> ModelConfig:
        """Select optimal model based on task and complexity"""
        if model_override and model_override in self.config.models:
            return self.config.models[model_override]

        # Get candidate models from routing rules
        task_candidates = self.config.routing.task_routing.get(task.value, [])
        complexity_candidates = self.config.routing.complexity_routing.get(
            complexity.value, []
        )

        # Find intersection
        candidates = set(task_candidates) & set(complexity_candidates)

        if not candidates:
            # Fallback to complexity-based selection
            candidates = set(complexity_candidates)

        if not candidates:
            # Ultimate fallback
            candidates = {"gpt-4o"}

        # Score and select best model
        best_model = None
        best_score = -1

        for model_name in candidates:
            if model_name not in self.config.models:
                continue

            model = self.config.models[model_name]
            score = self._score_model(model, task, complexity, context_size)

            if score > best_score:
                best_score = score
                best_model = model

        return best_model or self.config.models["gpt-4o"]

    def _score_model(
        self,
        model: ModelConfig,
        task: TaskType,
        complexity: TaskComplexity,
        context_size: int,
    ) -> float:
        """Score model for given task"""
        score = 0.0

        # Task alignment
        if task.value in model.use_cases:
            score += 30

        # Complexity alignment
        complexity_scores = {
            TaskComplexity.SIMPLE: {"simple": 20, "cost_efficient": 15},
            TaskComplexity.MODERATE: {"balanced": 20, "technical": 15},
            TaskComplexity.COMPLEX: {"complex_reasoning": 20, "analysis": 15},
            TaskComplexity.ARCHITECTURE: {"architecture": 25, "creative": 20},
        }

        for strength in model.strengths:
            score += complexity_scores.get(complexity, {}).get(strength, 0)

        # Context window check
        if model.context_window >= context_size * 2:
            score += 15
        elif model.context_window >= context_size:
            score += 10
        else:
            score -= 20

        # Cost efficiency (inverse)
        score += max(0, 20 - (model.cost_per_1k_tokens * 5))

        # Performance history
        perf = self._model_performance.get(model.name, {})
        success_rate = perf.get("success_rate", 0.5)
        score += success_rate * 10

        return score

    def _should_use_portkey(self, model: ModelConfig) -> bool:
        """Determine if model should be routed through Portkey"""
        # Check circuit breaker
        if self._circuit_breaker["portkey"]["is_open"]:
            return False

        # OpenAI and Anthropic models go through Portkey
        return model.provider in ["openai", "anthropic"]

    async def _complete_via_portkey(
        self,
        model: ModelConfig,
        prompt: str,
        stream: bool,
        temperature: float,
        max_tokens: int,
        metadata: Optional[dict[str, Any]],
        **kwargs,
    ) -> AsyncGenerator[str, None]:
        """Complete request via Portkey"""
        headers = {
            "x-portkey-api-key": self.portkey_api_key,
            "x-portkey-provider": model.provider,
            "Content-Type": "application/json",
        }

        # Add virtual key based on provider
        if model.provider == "openai":
            headers["x-portkey-virtual-key"] = get_config_value(
                "portkey_virtual_key_openai", ""
            )
        elif model.provider == "anthropic":
            headers["x-portkey-virtual-key"] = get_config_value(
                "portkey_virtual_key_anthropic", ""
            )

        payload = {
            "model": model.name,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream,
            "metadata": metadata or {},
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.portkey_base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=self.config.request_timeout),
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(
                            f"Portkey error: {response.status} - {error_text}"
                        )

                    if stream:
                        async for line in response.content:
                            if line:
                                line_str = line.decode("utf-8").strip()
                                if line_str.startswith("data: "):
                                    data_str = line_str[6:]
                                    if data_str == "[DONE]":
                                        break
                                    try:
                                        data = json.loads(data_str)
                                        if data.get("choices") and data["choices"][
                                            0
                                        ].get("delta", {}).get("content"):
                                            yield data["choices"][0]["delta"]["content"]
                                    except json.JSONDecodeError:
                                        continue
                    else:
                        data = await response.json()
                        if data.get("choices") and data["choices"][0].get(
                            "message", {}
                        ).get("content"):
                            yield data["choices"][0]["message"]["content"]

                    # Track metrics
                    if "usage" in data:
                        self._track_usage(model, data["usage"])

                    # Update circuit breaker
                    self._circuit_breaker["portkey"]["failures"] = 0

        except Exception as e:
            logger.error(f"Portkey error: {e}")
            self._handle_provider_error("portkey", e)
            raise

    async def _complete_via_openrouter(
        self,
        model: ModelConfig,
        prompt: str,
        stream: bool,
        temperature: float,
        max_tokens: int,
        metadata: Optional[dict[str, Any]],
        **kwargs,
    ) -> AsyncGenerator[str, None]:
        """Complete request via OpenRouter"""
        headers = {
            "Authorization": f"Bearer {self.openrouter_api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://sophia-intel.ai",
            "X-Title": "Sophia AI",
        }

        # Map model name for OpenRouter
        openrouter_model = self._map_to_openrouter_model(model.name)

        payload = {
            "model": openrouter_model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream,
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.openrouter_base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=self.config.request_timeout),
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(
                            f"OpenRouter error: {response.status} - {error_text}"
                        )

                    if stream:
                        async for line in response.content:
                            if line:
                                line_str = line.decode("utf-8").strip()
                                if line_str.startswith("data: "):
                                    data_str = line_str[6:]
                                    if data_str == "[DONE]":
                                        break
                                    try:
                                        data = json.loads(data_str)
                                        if data.get("choices") and data["choices"][
                                            0
                                        ].get("delta", {}).get("content"):
                                            yield data["choices"][0]["delta"]["content"]
                                    except json.JSONDecodeError:
                                        continue
                    else:
                        data = await response.json()
                        if data.get("choices") and data["choices"][0].get(
                            "message", {}
                        ).get("content"):
                            yield data["choices"][0]["message"]["content"]

                    # Track metrics
                    if "usage" in data:
                        self._track_usage(model, data["usage"])

                    # Update circuit breaker
                    self._circuit_breaker["openrouter"]["failures"] = 0

        except Exception as e:
            logger.error(f"OpenRouter error: {e}")
            self._handle_provider_error("openrouter", e)
            raise

    def _map_to_openrouter_model(self, model_name: str) -> str:
        """Map model name to OpenRouter format"""
        mappings = {
            "gpt-4o": "openai/gpt-4o",
            "gpt-3.5-turbo": "openai/gpt-3.5-turbo",
            "claude-3-5-sonnet": "anthropic/claude-3.5-sonnet",
            "deepseek-v3": "deepseek/deepseek-chat",
            "mixtral-8x7b": "mistralai/mixtral-8x7b-instruct",
        }
        return mappings.get(model_name, model_name)

    def _track_usage(self, model: ModelConfig, usage: dict[str, Any]):
        """Track token usage and cost"""
        input_tokens = usage.get("prompt_tokens", 0)
        output_tokens = usage.get("completion_tokens", 0)
        total_tokens = usage.get("total_tokens", 0)

        # Track tokens
        llm_tokens_total.labels(
            provider=model.provider, model=model.name, direction="input"
        ).inc(input_tokens)

        llm_tokens_total.labels(
            provider=model.provider, model=model.name, direction="output"
        ).inc(output_tokens)

        # Calculate and track cost
        cost = (total_tokens / 1000) * model.cost_per_1k_tokens
        llm_cost_usd_total.labels(
            provider=model.provider, model=model.name, task_type="general"
        ).inc(cost)

    def _handle_provider_error(self, provider: str, error: Exception):
        """Handle provider errors and update circuit breaker"""
        cb = self._circuit_breaker[provider]
        cb["failures"] += 1
        cb["last_failure"] = time.time()

        # Open circuit breaker after 3 failures
        if cb["failures"] >= 3:
            cb["is_open"] = True
            logger.warning(f"Circuit breaker opened for {provider}")

        # Track error
        llm_errors_total.labels(
            provider=provider, model="unknown", error_type=type(error).__name__
        ).inc()

    async def estimate_cost(
        self,
        prompt: str,
        task: TaskType,
        complexity: TaskComplexity,
        model_override: Optional[str] = None,
    ) -> dict[str, Any]:
        """Estimate cost for completion"""
        model = await self._select_model(task, complexity, model_override, len(prompt))

        # Rough token estimation (1 token ≈ 4 characters)
        estimated_tokens = (len(prompt) / 4) + 500  # Add estimated response
        estimated_cost = (estimated_tokens / 1000) * model.cost_per_1k_tokens

        return {
            "provider": model.provider,
            "model": model.name,
            "estimated_tokens": int(estimated_tokens),
            "estimated_cost": round(estimated_cost, 4),
            "cost_per_1k_tokens": model.cost_per_1k_tokens,
            "reasoning": f"Selected {model.name} for {task.value} with {complexity.value} complexity",
        }

    async def get_available_models(self) -> list[dict[str, Any]]:
        """Get list of available models"""
        models = []
        for name, config in self.config.models.items():
            models.append(
                {
                    "name": name,
                    "provider": config.provider,
                    "cost_per_1k_tokens": config.cost_per_1k_tokens,
                    "context_window": config.context_window,
                    "strengths": config.strengths,
                }
            )
        return models

    async def health_check(self) -> dict[str, Any]:
        """Check gateway health"""
        return {
            "portkey": {
                "configured": bool(self.portkey_api_key),
                "circuit_breaker": self._circuit_breaker["portkey"],
            },
            "openrouter": {
                "configured": bool(self.openrouter_api_key),
                "circuit_breaker": self._circuit_breaker["openrouter"],
            },
        }

    async def close(self):
        """Clean up resources"""
        pass  # No persistent connections to close
