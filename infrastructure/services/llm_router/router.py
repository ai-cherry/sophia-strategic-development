"""
LLM Router - Core routing engine
Stateless, observable, and performance-optimized
"""

from backend.services.unified_memory_service_v3 import UnifiedMemoryServiceV3
import time
from collections.abc import AsyncGenerator
from typing import Any

from shared.utils.custom_logger import logger

from .cache import SemanticCache
from .config_schema import LLMRouterConfig
from .cortex_adapter import CortexAdapter
from .enums import Provider, TaskComplexity, TaskType
from .fallback import FallbackChain
from .gateway import PortkeyGateway
from .metrics import (
    llm_cache_hit_rate,
    llm_request_duration,
    llm_requests_total,
    llm_router_version,
)


class LLMRouter:
    """
    Single facade for all LLM interactions
    Implements intelligent routing based on task type, complexity, and cost
    """

    def __init__(self):
        self._initialized = False
        self._config: LLMRouterConfig | None = None
        self._gateway: PortkeyGateway | None = None
        self._cortex: CortexAdapter | None = None
        self._fallback: FallbackChain | None = None
        self._cache: SemanticCache | None = None

        # Track router version for metrics
        llm_router_version.labels(version="v2").inc()

    async def _ensure_initialized(self):
        """Lazy initialization of components"""
        if not self._initialized:
            await self._initialize()

    async def _initialize(self):
        """Initialize all components"""
        try:
            # Load configuration
            self._config = LLMRouterConfig.from_file()

            # Initialize components
            self._gateway = PortkeyGateway(self._config)
            self._cortex = CortexAdapter()
            self._fallback = FallbackChain(self._config)

            # Initialize cache if enabled
            if self._config.cache.enabled:
                self._cache = SemanticCache(self._config.cache)
                await self._cache.initialize()

            self._initialized = True
            logger.info("✅ LLM Router initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize LLM Router: {e}")
            raise

    async def complete(
        self,
        prompt: str,
        task: TaskType,
        complexity: TaskComplexity = TaskComplexity.SIMPLE,
        stream: bool = True,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        model_override: str | None = None,
        metadata: dict[str, Any] | None = None,
        **kwargs,
    ) -> AsyncGenerator[str, None]:
        """
        Unified completion interface with intelligent routing

        Args:
            prompt: The prompt to complete
            task: Type of task for routing
            complexity: Task complexity level
            stream: Whether to stream the response
            temperature: Generation temperature
            max_tokens: Maximum tokens to generate
            model_override: Override automatic model selection
            metadata: Additional metadata for tracking
            **kwargs: Additional provider-specific parameters

        Yields:
            Response chunks if streaming, otherwise complete response
        """
        await self._ensure_initialized()

        start_time = time.time()
        provider = None
        model = None

        try:
            # Check cache first if enabled
            if self._cache and not stream:
                cached_response = await self._cache.get(
                    prompt=prompt,
                    task=task,
                    complexity=complexity,
                    model_override=model_override,
                )
                if cached_response:
                    llm_cache_hit_rate.labels(cache_type="semantic").inc()
                    yield cached_response
                    return

            # Route to appropriate provider
            if task in {
                TaskType.SQL_GENERATION,
                TaskType.DATA_ANALYSIS,
                TaskType.EMBEDDINGS,
            }:
                # Use Lambda GPU for data operations
                provider = Provider.qdrant
                async for chunk in self._
                    prompt=prompt,
                    task=task,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    **kwargs,
                ):
                    yield chunk
            else:
                # Use gateway for all other tasks
                provider = Provider.PORTKEY
                routing_result = await self._gateway.route_and_complete(
                    prompt=prompt,
                    task=task,
                    complexity=complexity,
                    stream=stream,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    model_override=model_override,
                    metadata=metadata,
                    **kwargs,
                )

                # Collect response for caching
                response_chunks = []
                async for chunk in routing_result:
                    response_chunks.append(chunk)
                    yield chunk

                # Cache complete response if not streaming
                if self._cache and not stream and response_chunks:
                    complete_response = "".join(response_chunks)
                    await self._cache.set(
                        prompt=prompt,
                        task=task,
                        complexity=complexity,
                        model_override=model_override,
                        response=complete_response,
                    )

            # Track success metrics
            duration = time.time() - start_time
            llm_request_duration.labels(
                provider=provider.value, model=model or "default", task_type=task.value
            ).observe(duration)

            llm_requests_total.labels(
                provider=provider.value,
                model=model or "default",
                task_type=task.value,
                status="success",
            ).inc()

        except Exception as e:
            # Track error metrics
            llm_requests_total.labels(
                provider=provider.value if provider else "unknown",
                model=model or "default",
                task_type=task.value,
                status="error",
            ).inc()

            logger.error(f"LLM Router error: {e}")

            # Attempt fallback if available
            if self._fallback:
                logger.info("Attempting fallback providers...")
                async for chunk in self._fallback.complete(
                    prompt=prompt, task=task, complexity=complexity, **kwargs
                ):
                    yield chunk
            else:
                raise

    async def estimate_cost(
        self,
        prompt: str,
        task: TaskType,
        complexity: TaskComplexity = TaskComplexity.SIMPLE,
        model_override: str | None = None,
    ) -> dict[str, Any]:
        """
        Estimate cost for a completion request

        Returns:
            Dictionary with cost estimate and model selection
        """
        await self._ensure_initialized()

        # Route to determine model
        if task in {
            TaskType.SQL_GENERATION,
            TaskType.DATA_ANALYSIS,
            TaskType.EMBEDDINGS,
        }:
            return {
                "provider": Provider.self.qdrant_service.value,
                "model": "qdrant-cortex",
                "estimated_cost": 0.0,  # Lambda GPU is free within platform
                "reasoning": "Data operations use Lambda GPU (no additional cost)",
            }
        else:
            return await self._gateway.estimate_cost(
                prompt=prompt,
                task=task,
                complexity=complexity,
                model_override=model_override,
            )

    async def get_available_models(self) -> dict[str, Any]:
        """Get list of available models by provider"""
        await self._ensure_initialized()

        models = {
            "qdrant": await self._cortex.get_available_models(),
            "gateway": await self._gateway.get_available_models(),
        }

        return models

    async def health_check(self) -> dict[str, Any]:
        """Check health of all LLM providers"""
        await self._ensure_initialized()

        health = {"router": "healthy", "version": "v2", "providers": {}}

        # Check each component
        if self._cortex:
            health["providers"]["qdrant"] = await self._cortex.health_check()

        if self._gateway:
            health["providers"]["gateway"] = await self._gateway.health_check()

        if self._cache:
            health["cache"] = await self._cache.health_check()

        return health

    async def close(self):
        """Clean up resources"""
        if self._gateway:
            await self._gateway.close()

        if self._cortex:
            await self._cortex.close()

        if self._cache:
            await self._cache.close()

        self._initialized = False
        logger.info("LLM Router closed")
