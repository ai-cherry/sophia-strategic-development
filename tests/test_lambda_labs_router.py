"""Tests for Lambda Labs hybrid router."""

from unittest.mock import AsyncMock, patch

import pytest  # type: ignore[import-not-found]

from infrastructure.services.lambda_labs_hybrid_router import LambdaLabsHybridRouter

@pytest.fixture
def router():
    """Create router instance with mocked dependencies."""
    with patch(
        "infrastructure.services.lambda_labs_hybrid_router.LambdaLabsServerlessService"
    ):
        return LambdaLabsHybridRouter(serverless_ratio=0.8)

@pytest.mark.asyncio
async def test_force_serverless_backend(router):
    """Test forcing serverless backend."""
    router.serverless.generate = AsyncMock(
        return_value={
            "choices": [{"message": {"content": "Serverless response"}}],
            "backend": "serverless",
            "model": "llama3.1-70b-instruct-fp8",
        }
    )

    result = await router.generate(
        messages=[{"role": "user", "content": "Test"}], force_backend="serverless"
    )

    assert result["backend"] == "serverless"
    assert result["choices"][0]["message"]["content"] == "Serverless response"
    router.serverless.generate.assert_called_once()

@pytest.mark.asyncio
async def test_force_gpu_backend(router):
    """Test forcing GPU backend."""
    gpu_callback = AsyncMock(
        return_value={
            "choices": [{"message": {"content": "GPU response"}}],
            "backend": "gpu",
        }
    )
    router.gpu_callback = gpu_callback

    result = await router.generate(
        messages=[{"role": "user", "content": "Test"}], force_backend="gpu"
    )

    assert result["backend"] == "gpu"
    assert result["choices"][0]["message"]["content"] == "GPU response"
    gpu_callback.assert_called_once()

@pytest.mark.asyncio
async def test_model_selection_low_cost(router):
    """Test model selection for low cost priority."""
    router.serverless.generate = AsyncMock(
        return_value={
            "choices": [{"message": {"content": "Response"}}],
            "model": "llama3.1-8b-instruct",
        }
    )

    # Low cost should always use serverless
    await router.generate(
        messages=[{"role": "user", "content": "Test"}], cost_priority="low_cost"
    )

    # Should select small model for low cost
    call_args = router.serverless.generate.call_args
    assert call_args[1]["model"] == "llama3.1-8b-instruct"

@pytest.mark.asyncio
async def test_model_selection_latency_critical(router):
    """Test model selection for latency critical priority."""
    gpu_callback = AsyncMock(
        return_value={
            "choices": [{"message": {"content": "GPU response"}}],
            "backend": "gpu",
        }
    )
    router.gpu_callback = gpu_callback

    result = await router.generate(
        messages=[{"role": "user", "content": "Test"}], cost_priority="latency_critical"
    )

    # Should use GPU for latency critical
    assert result["backend"] == "gpu"
    gpu_callback.assert_called_once()

@pytest.mark.asyncio
async def test_fallback_on_serverless_failure(router):
    """Test fallback to GPU when serverless fails."""
    router.serverless.generate = AsyncMock(side_effect=Exception("Serverless failed"))
    gpu_callback = AsyncMock(
        return_value={
            "choices": [{"message": {"content": "GPU fallback"}}],
            "backend": "gpu",
        }
    )
    router.gpu_callback = gpu_callback

    result = await router.generate(
        messages=[{"role": "user", "content": "Test"}], cost_priority="balanced"
    )

    assert result["backend"] == "gpu"
    assert result["choices"][0]["message"]["content"] == "GPU fallback"

@pytest.mark.asyncio
async def test_fallback_on_gpu_failure(router):
    """Test fallback to serverless when GPU fails."""
    # Mock to force GPU selection
    router._should_use_serverless = lambda *args: False

    gpu_callback = AsyncMock(side_effect=Exception("GPU failed"))
    router.gpu_callback = gpu_callback

    router.serverless.generate = AsyncMock(
        return_value={
            "choices": [{"message": {"content": "Serverless fallback"}}],
            "backend": "serverless",
            "model": "llama3.1-70b-instruct-fp8",
        }
    )

    result = await router.generate(
        messages=[{"role": "user", "content": "Test"}], cost_priority="performance"
    )

    assert result["backend"] == "serverless"
    assert result["choices"][0]["message"]["content"] == "Serverless fallback"

@pytest.mark.asyncio
async def test_no_gpu_callback_error(router):
    """Test error when GPU is selected but no callback configured."""
    router.gpu_callback = None
    router._should_use_serverless = lambda *args: False

    with pytest.raises(RuntimeError, match="GPU callback not configured"):
        await router.generate(messages=[{"role": "user", "content": "Test"}])
