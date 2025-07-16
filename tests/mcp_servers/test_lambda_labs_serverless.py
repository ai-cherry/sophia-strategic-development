import importlib.util
import json
import pathlib

import pytest  # type: ignore

# Dynamically load the server module because directory name contains a hyphen
SERVER_PATH = (
    pathlib.Path(__file__).parents[2]
    / "mcp-servers"
    / "lambda_labs_serverless"
    / "server.py"
)

spec = importlib.util.spec_from_file_location("lambda_server", SERVER_PATH)
lambda_server = importlib.util.module_from_spec(spec)  # type: ignore
assert spec and spec.loader  # guard for mypy / linters
spec.loader.exec_module(lambda_server)  # type: ignore

# Extract symbols for test usage
LambdaLabsServerlessMCP = lambda_server.LambdaLabsServerlessMCP
MCPServerConfig = lambda_server.MCPServerConfig

@pytest.mark.asyncio
async def test_server_initializes_with_api_key(monkeypatch):
    """Server should initialise when LAMBDA_LABS_API_KEY is present."""
    monkeypatch.setenv("LAMBDA_LABS_API_KEY", "fake-key")

    cfg = MCPServerConfig(name="lambda_test", port=9900)
    server = LambdaLabsServerlessMCP(cfg)
    await server.server_specific_init()
    assert server._session is not None
    await server.server_specific_cleanup()

@pytest.mark.asyncio
async def test_server_health_check_handles_missing_key(monkeypatch):
    """Health check should return critical when api key missing."""
    monkeypatch.delenv("LAMBDA_LABS_API_KEY", raising=False)

    cfg = MCPServerConfig(name="lambda_test", port=9901)

    with pytest.raises(RuntimeError):
        server = LambdaLabsServerlessMCP(cfg)
        await server.server_specific_init()

# ---------------------------------------------------------------------------
# Aioresponses-powered tests for inference behaviour
# ---------------------------------------------------------------------------

from aioresponses import aioresponses  # type: ignore

@pytest.mark.asyncio
async def test_successful_inference(monkeypatch):
    monkeypatch.setenv("LAMBDA_LABS_API_KEY", "fake-key")

    cfg = MCPServerConfig(name="lambda_test", port=9902)
    server = LambdaLabsServerlessMCP(cfg)
    await server.server_specific_init()

    endpoint = lambda_server.DEFAULT_INFERENCE_ENDPOINT

    with aioresponses() as mocked:
        mocked.post(
            endpoint,
            status=200,
            payload={"choices": [{"message": {"content": "Hello world"}}]},
        )

        content = await server.serverless_inference("Hello?")
        assert content == "Hello world"

    await server.server_specific_cleanup()

@pytest.mark.asyncio
async def test_inference_http_error(monkeypatch):
    monkeypatch.setenv("LAMBDA_LABS_API_KEY", "fake-key")

    cfg = MCPServerConfig(name="lambda_test", port=9903)
    server = LambdaLabsServerlessMCP(cfg)
    await server.server_specific_init()

    endpoint = lambda_server.DEFAULT_INFERENCE_ENDPOINT

    with aioresponses() as mocked:
        mocked.post(endpoint, status=401, payload={"error": "unauthorized"})

        with pytest.raises(RuntimeError):
            await server.serverless_inference("Hello?")

    await server.server_specific_cleanup()

# ---------------------------------------------------------------------------
# Budget exceeded / invalid-key / rate-limit tests
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_budget_exceeded(monkeypatch):
    """Ensure serverless_inference returns budget error when cost too high."""

    monkeypatch.setenv("LAMBDA_LABS_API_KEY", "fake-key")

    cfg = MCPServerConfig(name="lambda_test", port=9904)
    server = LambdaLabsServerlessMCP(cfg)
    await server.server_specific_init()

    # Craft gigantic prompt so estimated cost blows past budget ( > $50 daily )
    huge_prompt = "x" * 4 * 1_000_000  # ~1M tokens estimated

    result_json = await server._execute_optimized_inference(
        huge_prompt, complexity="premium", max_tokens=1, temperature=0
    )

    result = json.loads(result_json)
    assert result["success"] is False
    assert "Budget limit exceeded" in result["error"]

    await server.server_specific_cleanup()

@pytest.mark.asyncio
async def test_invalid_api_key(monkeypatch):
    """API returns 401 – ensure RuntimeError is raised."""

    monkeypatch.setenv("LAMBDA_LABS_API_KEY", "invalid-key")

    cfg = MCPServerConfig(name="lambda_test", port=9905)
    server = LambdaLabsServerlessMCP(cfg)
    await server.server_specific_init()

    endpoint = lambda_server.DEFAULT_INFERENCE_ENDPOINT

    with aioresponses() as mocked:
        mocked.post(endpoint, status=401, payload={"error": "unauthorized"})

        with pytest.raises(RuntimeError):
            await server.serverless_inference("Hi")

    await server.server_specific_cleanup()

@pytest.mark.asyncio
async def test_rate_limit_exceeded(monkeypatch):
    """API returns 429 rate limit – ensure RuntimeError is raised."""

    monkeypatch.setenv("LAMBDA_LABS_API_KEY", "fake-key")

    cfg = MCPServerConfig(name="lambda_test", port=9906)
    server = LambdaLabsServerlessMCP(cfg)
    await server.server_specific_init()

    endpoint = lambda_server.DEFAULT_INFERENCE_ENDPOINT

    with aioresponses() as mocked:
        mocked.post(endpoint, status=429, payload={"error": "rate limit"})

        with pytest.raises(RuntimeError):
            await server.serverless_inference("Hi again")

    await server.server_specific_cleanup()
