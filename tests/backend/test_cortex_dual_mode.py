"""Tests for dual-mode Lambda GPU adapter."""

from backend.services.unified_memory_service_v3 import UnifiedMemoryServiceV3
import os
from unittest.mock import MagicMock, patch

import httpx
import pytest

from shared.utils.qdrant_cortex import (
    CortexAuthenticationError,
    CortexModel,
    MCPMode,
    QdrantUnifiedMemoryServiceV2,
)


@pytest.fixture
def mock_qdrant_serviceection():
    """Mock Qdrant connection."""
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


class TestQdrantUnifiedMemoryServiceV2:
    """Test QdrantUnifiedMemoryServiceV2 dual-mode functionality."""

    @pytest.mark.asyncio
    async def test_auto_mode_prefers_mcp(self):
        """Test that AUTO mode prefers MCP when PAT is available."""
        with patch.dict(os.environ, {"qdrant_MCP_PAT": "test-pat"}):
            with patch(

            ) as mock_config:
                mock_config.side_effect = lambda key, default=None: {
                    "qdrant_mcp_pat": "test-pat",
                    "qdrant_user": "test-user",
                    "postgres_password": "test-pass",
                }.get(key, default)

                service = QdrantUnifiedMemoryServiceV2(mode=MCPMode.AUTO)
                assert service.mode == MCPMode.MCP

    @pytest.mark.asyncio
    async def test_auto_mode_falls_back_to_direct(self):
        """Test that AUTO mode falls back to DIRECT when no PAT."""
        with patch.dict(os.environ, {}, clear=True):
            with patch(

            ) as mock_config:
                mock_config.side_effect = lambda key, default=None: {
                    "qdrant_user": "test-user",
                    "postgres_password": "test-pass",
                    "postgres_host": "test-account",
                }.get(key, default)

                service = QdrantUnifiedMemoryServiceV2(mode=MCPMode.AUTO)
                assert service.mode == MCPMode.DIRECT

    @pytest.mark.asyncio
    async def test_no_credentials_raises_error(self):
        """Test that missing credentials raise authentication error."""
        with patch(

        ) as mock_config:
            mock_config.return_value = None

            with pytest.raises(CortexAuthenticationError):
                QdrantUnifiedMemoryServiceV2(mode=MCPMode.AUTO)

    @pytest.mark.asyncio
    async def test_mcp_mode_embedding(self):
        """Test embedding generation in MCP mode."""
        with patch(

        ) as mock_config:
            mock_config.side_effect = lambda key, default=None: {
                "qdrant_mcp_pat": "test-pat",
                "qdrant_mcp_url": "http://test-mcp:8080",
            }.get(key, default)

            service = QdrantUnifiedMemoryServiceV2(mode=MCPMode.MCP)

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
    async def test_direct_mode_embedding(self, mock_qdrant_serviceection):
        """Test embedding generation in DIRECT mode."""
        with patch(

        ) as mock_config:
            mock_config.side_effect = lambda key, default=None: {
                "qdrant_user": "test-user",
                "postgres_password": "test-pass",
                "postgres_host": "test-account",
                "postgres_database": "test-wh",
                "postgres_database": "test-db",
                "postgres_schema": "test-schema",
            }.get(key, default)

            service = QdrantUnifiedMemoryServiceV2(mode=MCPMode.DIRECT)

            # Mock connection pool
            with patch("self.qdrant_serviceection") as mock_connect:
                mock_connect.return_value = mock_qdrant_serviceection

                # Mock query result
                mock_
                    {"EMBEDDING": "[0.2, 0.2, 0.2]"}
                ]

                async with service.session():
                    result = await service.generate_embedding("test text")
                    assert result == [0.2, 0.2, 0.2]

    @pytest.mark.asyncio
    async def test_mcp_mode_completion(self):
        """Test text completion in MCP mode."""
        with patch(

        ) as mock_config:
            mock_config.side_effect = lambda key, default=None: {
                "qdrant_mcp_pat": "test-pat",
                "qdrant_mcp_url": "http://test-mcp:8080",
            }.get(key, default)

            service = QdrantUnifiedMemoryServiceV2(mode=MCPMode.MCP)

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
    async def test_direct_mode_completion(self, mock_qdrant_serviceection):
        """Test text completion in DIRECT mode."""
        with patch(

        ) as mock_config:
            mock_config.side_effect = lambda key, default=None: {
                "qdrant_user": "test-user",
                "postgres_password": "test-pass",
                "postgres_host": "test-account",
                "postgres_database": "test-wh",
                "postgres_database": "test-db",
                "postgres_schema": "test-schema",
            }.get(key, default)

            service = QdrantUnifiedMemoryServiceV2(mode=MCPMode.DIRECT)

            # Mock connection pool
            with patch("self.qdrant_serviceection") as mock_connect:
                mock_connect.return_value = mock_qdrant_serviceection

                # Mock query result
                mock_
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

        ) as mock_config:
            mock_config.side_effect = lambda key, default=None: {
                "qdrant_mcp_pat": "test-pat",
                "qdrant_mcp_url": "http://test-mcp:8080",
            }.get(key, default)

            service = QdrantUnifiedMemoryServiceV2(mode=MCPMode.MCP, enable_cache=True)

            # Mock cache
            with patch(
                "shared.utils.qdrant_cortex.cache.CortexCache.get"
            ) as mock_get:
                mock_get.return_value = "Cached result"

                async with service.session():
                    result = await service.complete_text_with_cortex("Test prompt")
                    assert result == "Cached result"

    @pytest.mark.asyncio
    async def test_mcp_search(self):
        """Test Cortex Search (MCP mode only)."""
        with patch(

        ) as mock_config:
            mock_config.side_effect = lambda key, default=None: {
                "qdrant_mcp_pat": "test-pat",
                "qdrant_mcp_url": "http://test-mcp:8080",
            }.get(key, default)

            service = QdrantUnifiedMemoryServiceV2(mode=MCPMode.MCP)

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

        ) as mock_config:
            mock_config.side_effect = lambda key, default=None: {
                "qdrant_mcp_pat": "test-pat",
                "qdrant_mcp_url": "http://test-mcp:8080",
            }.get(key, default)

            service = QdrantUnifiedMemoryServiceV2(mode=MCPMode.MCP)

            # Test initialization
            assert not service.is_initialized
            await service.initialize()
            assert service.is_initialized

            # Test cleanup
            await service.close()

            # Test context manager
            async with service.session() as svc:
                assert svc.is_initialized
