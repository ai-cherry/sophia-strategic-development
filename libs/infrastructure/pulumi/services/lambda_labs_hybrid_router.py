"""Intelligent routing between serverless and GPU backends."""

import logging
import random
from collections.abc import Callable
from typing import Any

from infrastructure.services.lambda_labs_serverless_service import (
    LambdaLabsServerlessService,
)

logger = logging.getLogger(__name__)


class LambdaLabsHybridRouter:
    """Routes requests between serverless and GPU with 80/20 split.

    This router implements intelligent traffic distribution between
    Lambda Labs serverless API and dedicated GPU instances based on:
    - Configured traffic ratio (default 80% serverless)
    - Query complexity analysis
    - Cost optimization priorities
    - Automatic fallback on failures

    Attributes:
        serverless: Lambda Labs serverless service instance
        serverless_ratio: Percentage of traffic to route to serverless
        gpu_callback: Optional callback for GPU inference
        complexity_analyzer: Optional function to analyze query complexity
    """

    def __init__(
        self,
        serverless_ratio: float = 0.8,
        gpu_callback: Callable | None = None,
        complexity_analyzer: Callable | None = None,
    ):
        """Initialize router with configurable split ratio.

        Args:
            serverless_ratio: Percentage (0-1) of traffic for serverless
            gpu_callback: Optional async function for GPU inference
            complexity_analyzer: Optional async function to analyze complexity
        """
        self.serverless = LambdaLabsServerlessService()
        self.serverless_ratio = serverless_ratio
        self.gpu_callback = gpu_callback
        self.complexity_analyzer = complexity_analyzer

    async def generate(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
        cost_priority: str = "balanced",
        force_backend: str | None = None,
        **kwargs,
    ) -> dict[str, Any]:
        """Route to appropriate backend based on strategy.

        Args:
            messages: OpenAI-format messages
            model: Optional specific model to use
            cost_priority: One of "low_cost", "balanced", "performance", "latency_critical"
            force_backend: Optional override to force "serverless" or "gpu"
            **kwargs: Additional arguments passed to backend

        Returns:
            Generation result with backend metadata

        Raises:
            RuntimeError: If no backend is available
        """
        # Allow force override for testing
        if force_backend == "serverless":
            return await self._serverless_generate(messages, model, **kwargs)
        elif force_backend == "gpu":
            return await self._gpu_generate(messages, **kwargs)

        # Analyze complexity if analyzer provided
        complexity = "medium"
        if self.complexity_analyzer:
            complexity = await self.complexity_analyzer(messages)

        # Select model based on complexity and cost priority
        if not model:
            model = self._select_model(complexity, cost_priority)

        # Route based on ratio and complexity
        use_serverless = self._should_use_serverless(complexity, cost_priority)

        try:
            if use_serverless:
                logger.info(f"Routing to serverless (model: {model})")
                return await self._serverless_generate(messages, model, **kwargs)
            else:
                logger.info("Routing to GPU backend")
                return await self._gpu_generate(messages, **kwargs)
        except Exception as e:
            logger.error(f"Primary backend failed: {e}")
            # Fallback to other backend
            if use_serverless and self.gpu_callback:
                logger.info("Falling back to GPU")
                return await self._gpu_generate(messages, **kwargs)
            elif not use_serverless:
                logger.info("Falling back to serverless")
                return await self._serverless_generate(messages, model, **kwargs)
            raise

    def _should_use_serverless(self, complexity: str, cost_priority: str) -> bool:
        """Determine if request should use serverless.

        Args:
            complexity: Query complexity ("low", "medium", "high")
            cost_priority: Cost optimization priority

        Returns:
            True if serverless should be used
        """
        # Always use serverless for low complexity or high cost priority
        if complexity == "low" or cost_priority == "low_cost":
            return True

        # Never use serverless for ultra-low latency requirements
        if cost_priority == "latency_critical":
            return False

        # Use ratio for medium complexity
        return random.random() < self.serverless_ratio

    def _select_model(self, complexity: str, cost_priority: str) -> str:
        """Select optimal model based on complexity and cost priority.

        Args:
            complexity: Query complexity
            cost_priority: Cost optimization priority

        Returns:
            Model name
        """
        if cost_priority == "low_cost" or complexity == "low":
            return "llama3.1-8b-instruct"
        elif complexity == "high" and cost_priority != "low_cost":
            return "llama-4-maverick-17b-128e-instruct-fp8"
        else:
            return "llama3.1-70b-instruct-fp8"

    async def _serverless_generate(
        self, messages: list[dict[str, str]], model: str, **kwargs
    ) -> dict[str, Any]:
        """Generate using serverless backend.

        Args:
            messages: Input messages
            model: Model to use
            **kwargs: Additional arguments

        Returns:
            Generation result with backend metadata
        """
        result = await self.serverless.generate(messages, model=model, **kwargs)
        result["backend"] = "serverless"
        result["model"] = model
        return result

    async def _gpu_generate(
        self, messages: list[dict[str, str]], **kwargs
    ) -> dict[str, Any]:
        """Generate using GPU backend.

        Args:
            messages: Input messages
            **kwargs: Additional arguments

        Returns:
            Generation result with backend metadata

        Raises:
            RuntimeError: If GPU callback not configured
        """
        if not self.gpu_callback:
            raise RuntimeError("GPU callback not configured")
        result = await self.gpu_callback(messages, **kwargs)
        result["backend"] = "gpu"
        return result
