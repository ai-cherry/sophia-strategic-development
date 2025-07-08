"""Tests for dual-mode Snowflake Cortex adapter."""

import os
from unittest.mock import MagicMock, patch

import httpx
import pytest

from shared.utils.snowflake_cortex import (
    CortexAuthenticationError,
    CortexModel,
    MCPMode,
    SnowflakeCortexService,
)


@pytest.fixture
def mock_snowflake_connection():
    """Mock Snowflake connection."""
    conn = MagicMock()
    cursor = MagicMock()

    # Mock cursor behavior
    cursor.execute.return_value = cursor
    cursor.fetchall.return_value = []
    cursor.description = [("RESULT",)]

    conn.cursor.return_value = cursor
    conn.is_closed.return_value = False

    return conn


@pytest.fixture
def mock_mcp_response():
    """Mock MCP server response."""
    return httpx.Response(
        200, json={"completion": "Test response", "vector": [0.1] * 768}
    )


class TestSnowflakeCortexService:
    """Test SnowflakeCortexService dual-mode functionality."""

    @pytest.mark.asyncio
    async def test_auto_mode_prefers_mcp(self):
        """Test that AUTO mode prefers MCP when PAT is available."""
        with patch.dict(os.environ, {"SNOWFLAKE_MCP_PAT": "test-pat"}):
            with patch(
                "shared.utils.snowflake_cortex.service.get_config_value"
            ) as mock_config:
                mock_config.side_effect = lambda key, default=None: {
                    "snowflake_mcp_pat": "test-pat",
                    "snowflake_user": "test-user",
                    "snowflake_password": "test-pass",
                }.get(key, default)

                service = SnowflakeCortexService(mode=MCPMode.AUTO)
                assert service.mode == MCPMode.MCP

    @pytest.mark.asyncio
    async def test_auto_mode_falls_back_to_direct(self):
        """Test that AUTO mode falls back to DIRECT when no PAT."""
        with patch.dict(os.environ, {}, clear=True):
            with patch(
                "shared.utils.snowflake_cortex.service.get_config_value"
            ) as mock_config:
                mock_config.side_effect = lambda key, default=None: {
                    "snowflake_user": "test-user",
                    "snowflake_password": "test-pass",
                    "snowflake_account": "test-account",
                }.get(key, default)

                service = SnowflakeCortexService(mode=MCPMode.AUTO)
                assert service.mode == MCPMode.DIRECT

    @pytest.mark.asyncio
    async def test_no_credentials_raises_error(self):
        """Test that missing credentials raise authentication error."""
        with patch(
            "shared.utils.snowflake_cortex.service.get_config_value"
        ) as mock_config:
            mock_config.return_value = None

            with pytest.raises(CortexAuthenticationError):
                SnowflakeCortexService(mode=MCPMode.AUTO)

    @pytest.mark.asyncio
    async def test_mcp_mode_embedding(self):
        """Test embedding generation in MCP mode."""
        with patch(
            "shared.utils.snowflake_cortex.service.get_config_value"
        ) as mock_config:
            mock_config.side_effect = lambda key, default=None: {
                "snowflake_mcp_pat": "test-pat",
                "snowflake_mcp_url": "http://test-mcp:8080",
            }.get(key, default)

            service = SnowflakeCortexService(mode=MCPMode.MCP)

            # Mock MCP client
            with patch("httpx.AsyncClient.post") as mock_post:
                mock_post.return_value = httpx.Response(
                    200, json={"vector": [0.1] * 768}
                )

                async with service.session():
                    result = await service.generate_embedding("test text")
                    assert len(result) == 768
                    assert all(v == 0.1 for v in result)

    @pytest.mark.asyncio
    async def test_direct_mode_embedding(self, mock_snowflake_connection):
        """Test embedding generation in DIRECT mode."""
        with patch(
            "shared.utils.snowflake_cortex.service.get_config_value"
        ) as mock_config:
            mock_config.side_effect = lambda key, default=None: {
                "snowflake_user": "test-user",
                "snowflake_password": "test-pass",
                "snowflake_account": "test-account",
                "snowflake_warehouse": "test-wh",
                "snowflake_database": "test-db",
                "snowflake_schema": "test-schema",
            }.get(key, default)

            service = SnowflakeCortexService(mode=MCPMode.DIRECT)

            # Mock connection pool
            with patch("snowflake.connector.connect") as mock_connect:
                mock_connect.return_value = mock_snowflake_connection

                # Mock query result
                mock_snowflake_connection.cursor().fetchall.return_value = [
                    {"EMBEDDING": "[0.2, 0.2, 0.2]"}
                ]

                async with service.session():
                    result = await service.generate_embedding("test text")
                    assert result == [0.2, 0.2, 0.2]

    @pytest.mark.asyncio
    async def test_mcp_mode_completion(self):
        """Test text completion in MCP mode."""
        with patch(
            "shared.utils.snowflake_cortex.service.get_config_value"
        ) as mock_config:
            mock_config.side_effect = lambda key, default=None: {
                "snowflake_mcp_pat": "test-pat",
                "snowflake_mcp_url": "http://test-mcp:8080",
            }.get(key, default)

            service = SnowflakeCortexService(mode=MCPMode.MCP)

            # Mock MCP client
            with patch("httpx.AsyncClient.post") as mock_post:
                mock_post.return_value = httpx.Response(
                    200, json={"completion": "Generated text"}
                )

                async with service.session():
                    result = await service.complete_text_with_cortex(
                        "Test prompt", model=CortexModel.MISTRAL_7B
                    )
                    assert result == "Generated text"

    @pytest.mark.asyncio
    async def test_direct_mode_completion(self, mock_snowflake_connection):
        """Test text completion in DIRECT mode."""
        with patch(
            "shared.utils.snowflake_cortex.service.get_config_value"
        ) as mock_config:
            mock_config.side_effect = lambda key, default=None: {
                "snowflake_user": "test-user",
                "snowflake_password": "test-pass",
                "snowflake_account": "test-account",
                "snowflake_warehouse": "test-wh",
                "snowflake_database": "test-db",
                "snowflake_schema": "test-schema",
            }.get(key, default)

            service = SnowflakeCortexService(mode=MCPMode.DIRECT)

            # Mock connection pool
            with patch("snowflake.connector.connect") as mock_connect:
                mock_connect.return_value = mock_snowflake_connection

                # Mock query result
                mock_snowflake_connection.cursor().fetchall.return_value = [
                    {"COMPLETION": "SQL generated text"}
                ]

                async with service.session():
                    result = await service.complete_text_with_cortex(
                        "Test prompt", model=CortexModel.MISTRAL_7B
                    )
                    assert result == "SQL generated text"

    @pytest.mark.asyncio
    async def test_cache_hit(self):
        """Test that cache returns cached results."""
        with patch(
            "shared.utils.snowflake_cortex.service.get_config_value"
        ) as mock_config:
            mock_config.side_effect = lambda key, default=None: {
                "snowflake_mcp_pat": "test-pat",
                "snowflake_mcp_url": "http://test-mcp:8080",
            }.get(key, default)

            service = SnowflakeCortexService(mode=MCPMode.MCP, enable_cache=True)

            # Mock cache
            with patch(
                "shared.utils.snowflake_cortex.cache.CortexCache.get"
            ) as mock_get:
                mock_get.return_value = "Cached result"

                async with service.session():
                    result = await service.complete_text_with_cortex("Test prompt")
                    assert result == "Cached result"

    @pytest.mark.asyncio
    async def test_mcp_search(self):
        """Test Cortex Search (MCP mode only)."""
        with patch(
            "shared.utils.snowflake_cortex.service.get_config_value"
        ) as mock_config:
            mock_config.side_effect = lambda key, default=None: {
                "snowflake_mcp_pat": "test-pat",
                "snowflake_mcp_url": "http://test-mcp:8080",
            }.get(key, default)

            service = SnowflakeCortexService(mode=MCPMode.MCP)

            # Mock MCP client
            with patch("httpx.AsyncClient.post") as mock_post:
                mock_post.return_value = httpx.Response(
                    200, json={"results": [{"id": 1, "text": "Result 1"}]}
                )

                async with service.session():
                    results = await service.search(
                        "test query", "test_service", ["col1", "col2"]
                    )
                    assert len(results) == 1
                    assert results[0]["text"] == "Result 1"

    @pytest.mark.asyncio
    async def test_service_lifecycle(self):
        """Test service initialization and cleanup."""
        with patch(
            "shared.utils.snowflake_cortex.service.get_config_value"
        ) as mock_config:
            mock_config.side_effect = lambda key, default=None: {
                "snowflake_mcp_pat": "test-pat",
                "snowflake_mcp_url": "http://test-mcp:8080",
            }.get(key, default)

            service = SnowflakeCortexService(mode=MCPMode.MCP)

            # Test initialization
            assert not service.is_initialized
            await service.initialize()
            assert service.is_initialized

            # Test cleanup
            await service.close()

            # Test context manager
            async with service.session() as svc:
                assert svc.is_initialized
