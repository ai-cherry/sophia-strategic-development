"""
Tests for LLM Router
Ensures router functionality, fallback, and performance
"""

import asyncio
import time
from unittest.mock import AsyncMock, patch

import pytest

from infrastructure.services.llm_router import TaskComplexity, TaskType
from infrastructure.services.llm_router.config_schema import LLMRouterConfig
from infrastructure.services.llm_router.router import LLMRouter

@pytest.fixture
def mock_config():
    """Mock configuration for testing"""
    return LLMRouterConfig.from_defaults()

@pytest.fixture
def router(mock_config):
    """Create router instance for testing"""
    router = LLMRouter()
    router._config = mock_config
    router._initialized = True
    return router

@pytest.fixture(autouse=True)
def mock_external_calls():
    """Mock all external API calls"""
    with patch(
        "infrastructure.services.llm_router.gateway.aiohttp.ClientSession"
    ) as mock_session:
        # Mock successful response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(
            return_value={
                "choices": [
                    {
                        "message": {"content": "Test response"},
                        "delta": {"content": "Test"},
                    }
                ],
                "usage": {
                    "prompt_tokens": 10,
                    "completion_tokens": 20,
                    "total_tokens": 30,
                },
            }
        )
        mock_response.content = AsyncMock()

        mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = (
            mock_response
        )

        yield mock_session

class TestLLMRouter:
    """Test LLM Router core functionality"""

    @pytest.mark.asyncio
    async def test_router_initialization(self):
        """Test router initializes correctly"""
        router = LLMRouter()
        assert not router._initialized

        await router._ensure_initialized()
        assert router._initialized
        assert router._config is not None
        assert router._gateway is not None
        assert router._cortex is not None

    @pytest.mark.asyncio
    async def test_complete_basic(self, router):
        """Test basic completion"""
        response = []
        async for chunk in router.complete(
            prompt="Test prompt",
            task=TaskType.CODE_GENERATION,
            complexity=TaskComplexity.SIMPLE,
        ):
            response.append(chunk)

        assert len(response) > 0
        assert "Test" in "".join(response)

    @pytest.mark.asyncio
    async def test_task_routing(self, router):
        """Test different tasks route to appropriate providers"""
        # SQL task should route to Qdrant
        with patch.object(router._cortex, "complete") as mock_cortex:
            mock_cortex.return_value = self._async_generator(["SQL result"])

            response = []
            async for chunk in router.complete(
                prompt="SELECT * FROM users", task=TaskType.SQL_GENERATION
            ):
                response.append(chunk)

            mock_cortex.assert_called_once()
            assert "SQL result" in "".join(response)

        # Code task should route to gateway
        with patch.object(router._gateway, "route_and_complete") as mock_gateway:
            mock_gateway.return_value = self._async_generator(["Code result"])

            response = []
            async for chunk in router.complete(
                prompt="Write a function", task=TaskType.CODE_GENERATION
            ):
                response.append(chunk)

            mock_gateway.assert_called_once()
            assert "Code result" in "".join(response)

    @pytest.mark.asyncio
    async def test_complexity_routing(self, router):
        """Test complexity affects model selection"""
        with patch.object(router._gateway, "route_and_complete") as mock_gateway:
            mock_gateway.return_value = self._async_generator(["Response"])

            # Simple task
            await self._consume_generator(
                router.complete(
                    prompt="Hello",
                    task=TaskType.CHAT_CONVERSATION,
                    complexity=TaskComplexity.SIMPLE,
                )
            )

            # Complex task
            await self._consume_generator(
                router.complete(
                    prompt="Design a system",
                    task=TaskType.ARCHITECTURE_DESIGN,
                    complexity=TaskComplexity.ARCHITECTURE,
                )
            )

            # Verify different complexity levels were passed
            assert mock_gateway.call_count == 2
            calls = mock_gateway.call_args_list
            assert calls[0][1]["complexity"] == TaskComplexity.SIMPLE
            assert calls[1][1]["complexity"] == TaskComplexity.ARCHITECTURE

    @pytest.mark.asyncio
    async def test_cache_functionality(self, router):
        """Test caching works correctly"""
        # Enable cache
        router._cache = AsyncMock()
        router._cache.get = AsyncMock(return_value="Cached response")
        router._cache.set = AsyncMock(return_value=True)

        # First call - cache hit
        response = []
        async for chunk in router.complete(
            prompt="Test prompt",
            task=TaskType.CODE_GENERATION,
            stream=False,  # Cache only works for non-streaming
        ):
            response.append(chunk)

        assert "Cached response" in "".join(response)
        router._cache.get.assert_called_once()

    @pytest.mark.asyncio
    async def test_error_handling(self, router):
        """Test error handling and fallback"""
        # Mock gateway to fail
        router._gateway.route_and_complete = AsyncMock(
            side_effect=Exception("Gateway failed")
        )

        # Mock fallback to succeed
        router._fallback = AsyncMock()
        router._fallback.complete = AsyncMock(
            return_value=self._async_generator(["Fallback response"])
        )

        response = []
        async for chunk in router.complete(
            prompt="Test prompt", task=TaskType.CODE_GENERATION
        ):
            response.append(chunk)

        assert "Fallback response" in "".join(response)
        router._fallback.complete.assert_called_once()

    @pytest.mark.asyncio
    async def test_performance_latency(self, router):
        """Test response latency is within bounds"""
        start_time = time.time()

        response = []
        async for chunk in router.complete(
            prompt="Test prompt",
            task=TaskType.CODE_GENERATION,
            complexity=TaskComplexity.SIMPLE,
        ):
            response.append(chunk)

        duration = time.time() - start_time

        # Should complete within 2 seconds (p95 target)
        assert duration < 2.0

    @pytest.mark.asyncio
    async def test_cost_estimation(self, router):
        """Test cost estimation functionality"""
        estimate = await router.estimate_cost(
            prompt="Test prompt",
            task=TaskType.CODE_GENERATION,
            complexity=TaskComplexity.SIMPLE,
        )

        assert "provider" in estimate
        assert "model" in estimate
        assert "estimated_cost" in estimate
        assert estimate["estimated_cost"] >= 0

    @pytest.mark.asyncio
    async def test_health_check(self, router):
        """Test health check functionality"""
        health = await router.health_check()

        assert health["router"] == "healthy"
        assert health["version"] == "v2"
        assert "providers" in health

    @pytest.mark.asyncio
    async def test_model_override(self, router):
        """Test model override functionality"""
        with patch.object(router._gateway, "route_and_complete") as mock_gateway:
            mock_gateway.return_value = self._async_generator(["Response"])

            await self._consume_generator(
                router.complete(
                    prompt="Test",
                    task=TaskType.CODE_GENERATION,
                    model_override="gpt-3.5-turbo",
                )
            )

            # Verify model override was passed
            mock_gateway.assert_called_once()
            assert mock_gateway.call_args[1]["model_override"] == "gpt-3.5-turbo"

    @pytest.mark.asyncio
    async def test_streaming_vs_non_streaming(self, router):
        """Test both streaming and non-streaming modes"""
        # Streaming mode
        response = []
        async for chunk in router.complete(
            prompt="Test", task=TaskType.CODE_GENERATION, stream=True
        ):
            response.append(chunk)

        assert len(response) > 0

        # Non-streaming mode
        response = []
        async for chunk in router.complete(
            prompt="Test", task=TaskType.CODE_GENERATION, stream=False
        ):
            response.append(chunk)

        assert len(response) > 0

    # Helper methods
    async def _async_generator(self, items):
        """Create async generator for testing"""
        for item in items:
            yield item

    async def _consume_generator(self, generator):
        """Consume all items from async generator"""
        async for _ in generator:
            pass

class TestRouterIntegration:
    """Integration tests for LLM Router"""

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_full_request_flow(self):
        """Test complete request flow with real components"""
        # This test would run against real services in integration environment
        # Skipped in unit tests
        pytest.skip("Integration test - requires real services")

    @pytest.mark.asyncio
    async def test_concurrent_requests(self, router):
        """Test router handles concurrent requests"""
        tasks = []

        # Create 10 concurrent requests
        for i in range(10):
            task = router.complete(
                prompt=f"Test prompt {i}",
                task=TaskType.CODE_GENERATION,
                complexity=TaskComplexity.SIMPLE,
            )
            tasks.append(self._consume_generator(task))

        # All should complete successfully
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # No exceptions
        for result in results:
            assert not isinstance(result, Exception)

class TestMetrics:
    """Test metrics collection"""

    @pytest.mark.asyncio
    async def test_metrics_collection(self, router):
        """Test that metrics are collected properly"""
        from infrastructure.services.llm_router.metrics import (
            llm_requests_total,
            llm_router_version,
        )

        # Check router version metric
        # This is set during router initialization
        # We can't easily test the actual value, but we can verify the metric exists

        # Make a request to trigger metrics
        await self._consume_generator(
            router.complete(prompt="Test", task=TaskType.CODE_GENERATION)
        )

        # Metrics should be updated (testing the structure, not values)
        assert llm_requests_total._name == "llm_requests_total"
        assert llm_router_version._name == "llm_router_version_total"

    async def _consume_generator(self, generator):
        """Consume all items from async generator"""
        async for _ in generator:
            pass
