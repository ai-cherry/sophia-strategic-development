"""Model routing utilities for the Sophia platform.

This module provides thin wrappers around OpenRouter and Portkey so that the
rest of the codebase can access a unified interface.  The implementation here is
intentionally lightweight and is primarily designed to allow the module to be
imported without requiring external services.
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

# aiohttp is an optional dependency; the real implementation would make HTTP
# requests.  The simplified version merely defines the expected API.
try:  # pragma: no cover - optional dependency
    import aiohttp  # type: ignore
except Exception:  # pragma: no cover - import may fail in minimal envs
    aiohttp = None

logger = logging.getLogger(__name__)


@dataclass
class ModelConfig:
    """Configuration describing an AI model."""

    name: str
    provider: str
    cost_per_token: float
    max_tokens: int
    capabilities: List[str]
    priority: int = 1


@dataclass
class RoutingRule:
    """Rule for routing requests to specific models."""

    condition: str
    target_model: str
    weight: float = 1.0


class OpenRouterClient:
    """Minimal OpenRouter client."""

    def __init__(self) -> None:
        self.api_key = os.getenv("OPENROUTER_API_KEY", "")
        self.base_url = "https://openrouter.ai/api/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        self.models = {
            "gpt-4-turbo": ModelConfig(
                name="openai/gpt-4-turbo",
                provider="openai",
                cost_per_token=0.0,
                max_tokens=128000,
                capabilities=["chat"],
            )
        }

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Return a dummy completion response."""

        model_name = model or self._select_optimal_model(messages, [])
        return {
            "model": model_name,
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": "This is a stub response.",
                    }
                }
            ],
        }

    def _select_optimal_model(
        self, messages: List[Dict[str, str]], capabilities: List[str]
    ) -> str:
        """Select a model.  The simplified logic just picks the first one."""

        return next(iter(self.models.values())).name

    async def get_models(self) -> List[Dict[str, Any]]:
        """Return available models."""

        return [
            {
                "id": cfg.name,
                "provider": cfg.provider,
            }
            for cfg in self.models.values()
        ]


class PortkeyGateway:
    """Minimal Portkey gateway wrapper."""

    def __init__(self) -> None:
        self.api_key = os.getenv("PORTKEY_API_KEY", "")
        self.base_url = "https://api.portkey.ai/v1"
        self.headers = {"Authorization": f"Bearer {self.api_key}"}
        self.routing_rules: List[RoutingRule] = []

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        routing_strategy: str = "smart",
        cache: bool = True,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Return a dummy completion from Portkey."""

        selected_model = model or self._apply_routing_strategy(
            messages, routing_strategy, kwargs
        )
        return {
            "model": selected_model,
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": "This is a stub response from Portkey.",
                    }
                }
            ],
        }

    def _apply_routing_strategy(
        self,
        messages: List[Dict[str, str]],
        strategy: str,
        kwargs: Dict[str, Any],
    ) -> str:
        """Very small routing strategy implementation."""

        return "openai/gpt-4-turbo"


class SophiaAIModelRouter:
    """Unified router that proxies requests to OpenRouter or Portkey."""

    def __init__(self) -> None:
        self.openrouter = OpenRouterClient()
        self.portkey = PortkeyGateway()
        self.config = {
            "default_provider": "portkey",
            "fallback_provider": "openrouter",
            "enable_monitoring": False,
        }

    async def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        provider: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Route a chat completion request."""

        provider = provider or self.config["default_provider"]
        if provider == "portkey":
            result = await self.portkey.chat_completion(messages, model, **kwargs)
        else:
            result = await self.openrouter.chat_completion(messages, model, **kwargs)

        if self.config.get("enable_monitoring"):
            self._log_request(messages, result, provider, model)
        return result

    def _log_request(
        self,
        messages: List[Dict[str, str]],
        result: Dict[str, Any],
        provider: str,
        model: Optional[str],
    ) -> None:
        """Log a request for basic analytics."""

        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "provider": provider,
            "model": model,
            "input_tokens": sum(len(m.get("content", "")) for m in messages) // 4,
            "success": "error" not in result,
        }
        logger.info("Model request logged: %s", json.dumps(log_data))


sophia_router: Optional[SophiaAIModelRouter] = None


def get_sophia_router() -> SophiaAIModelRouter:
    """Get or create the global router instance."""

    global sophia_router
    if sophia_router is None:
        sophia_router = SophiaAIModelRouter()
    return sophia_router


async def sophia_chat(messages: List[Dict[str, str]], **kwargs: Any) -> Dict[str, Any]:
    """Convenience wrapper around :meth:`SophiaAIModelRouter.chat`."""

    router = get_sophia_router()
    return await router.chat(messages, **kwargs)


async def sophia_analyze(
    text: str, analysis_type: str = "general", **kwargs: Any
) -> Dict[str, Any]:
    """Perform a simple analysis request."""

    messages = [
        {
            "role": "system",
            "content": f"You are Sophia AI, an expert analyst. Perform {analysis_type} analysis.",
        },
        {"role": "user", "content": text},
    ]
    router = get_sophia_router()
    return await router.chat(messages, **kwargs)


async def sophia_code(
    prompt: str, language: str = "python", **kwargs: Any
) -> Dict[str, Any]:
    """Generate code using Sophia AI."""

    messages = [
        {
            "role": "system",
            "content": f"You are Sophia AI, an expert {language} developer.",
        },
        {"role": "user", "content": prompt},
    ]
    router = get_sophia_router()
    return await router.chat(messages, **kwargs)
