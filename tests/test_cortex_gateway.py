"""
Unit tests for CortexGateway - unified Snowflake access layer
"""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from core.infra.cortex_gateway import CortexGateway, get_gateway


@pytest.fixture
async def mock_connection_manager():
    """Mock the OptimizedConnectionManager"""
    with patch("core.infra.cortex_gateway.OptimizedConnectionManager") as mock:
        manager = AsyncMock()
        manager.initialize = AsyncMock()
        manager.get_connection = AsyncMock()
        manager._session_id = "test-session-123"
        mock.return_value = manager
        yield manager


@pytest.fixture
async def gateway(mock_connection_manager):
    """Create a test gateway instance"""
    # Reset singleton
    CortexGateway._instance = None
    gateway = CortexGateway()
    await gateway.initialize()
    return gateway


class TestCortexGateway:
    """Test suite for CortexGateway"""

    def test_singleton_pattern(self):
        """Test that CortexGateway follows singleton pattern"""
        gateway1 = get_gateway()
        gateway2 = get_gateway()
        assert gateway1 is gateway2

    @pytest.mark.asyncio
    async def test_initialize(self, mock_connection_manager):
        """Test gateway initialization"""
        gateway = CortexGateway()
        assert not gateway._initialized

        await gateway.initialize()

        assert gateway._initialized
        assert gateway._daily_credit_limit == 100
        assert gateway._credits_used_today == 0
        mock_connection_manager.initialize.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_sql(self, gateway, mock_connection_manager):
        """Test SQL execution with credit tracking"""
        # Mock connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [{"result": 1}]
        mock_conn.cursor.return_value = mock_cursor

        # Setup async context manager
        async def async_context():
            yield mock_conn

        mock_connection_manager.get_connection.return_value = async_context()

        # Execute query
        result = await gateway.execute_sql("SELECT 1", warehouse="COMPUTE_WH")

        assert result == [{"result": 1}]
        assert gateway._credits_used_today > 0
        mock_cursor.execute.assert_called_with("SELECT 1")

    @pytest.mark.asyncio
    async def test_credit_limit_enforcement(self, gateway):
        """Test that credit limit is enforced"""
        # Set credits near limit
        gateway._credits_used_today = 99.99

        # Should raise exception when limit exceeded
        with pytest.raises(Exception, match="Daily credit limit"):
            await gateway._check_credit_limit(0.02)

    @pytest.mark.asyncio
    async def test_complete_function(self, gateway, mock_connection_manager):
        """Test Cortex COMPLETE function"""
        # Mock connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = {"RESPONSE": "AI response"}
        mock_conn.cursor.return_value = mock_cursor

        # Setup async context manager
        async def async_context():
            yield mock_conn

        mock_connection_manager.get_connection.return_value = async_context()

        # Execute complete
        result = await gateway.complete("Test prompt", model="mixtral-8x7b")

        assert result == "AI response"
        assert "SNOWFLAKE.CORTEX.COMPLETE" in mock_cursor.execute.call_args[0][0]

    @pytest.mark.asyncio
    async def test_embed_function(self, gateway, mock_connection_manager):
        """Test Cortex embedding function"""
        # Mock connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = {"EMBEDDING": "[0.1, 0.2, 0.3]"}
        mock_conn.cursor.return_value = mock_cursor

        # Setup async context manager
        async def async_context():
            yield mock_conn

        mock_connection_manager.get_connection.return_value = async_context()

        # Execute embed
        result = await gateway.embed("Test text")

        assert result == [0.1, 0.2, 0.3]
        assert "SNOWFLAKE.CORTEX.EMBED_TEXT_768" in mock_cursor.execute.call_args[0][0]

    @pytest.mark.asyncio
    async def test_batch_embed_function(self, gateway, mock_connection_manager):
        """Test batch embedding function"""
        # Mock connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            {"EMBEDDING": "[0.1, 0.2]"},
            {"EMBEDDING": "[0.3, 0.4]"},
        ]
        mock_conn.cursor.return_value = mock_cursor

        # Setup async context manager
        async def async_context():
            yield mock_conn

        mock_connection_manager.get_connection.return_value = async_context()

        # Execute batch embed
        result = await gateway.batch_embed(["Text 1", "Text 2"])

        assert result == [[0.1, 0.2], [0.3, 0.4]]
        assert gateway._credits_used_today > 0

    @pytest.mark.asyncio
    async def test_sentiment_function(self, gateway, mock_connection_manager):
        """Test Cortex sentiment analysis"""
        # Mock connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = {"SENTIMENT": 0.8}
        mock_conn.cursor.return_value = mock_cursor

        # Setup async context manager
        async def async_context():
            yield mock_conn

        mock_connection_manager.get_connection.return_value = async_context()

        # Execute sentiment
        result = await gateway.sentiment("Positive text")

        assert result == 0.8
        assert "SNOWFLAKE.CORTEX.SENTIMENT" in mock_cursor.execute.call_args[0][0]

    @pytest.mark.asyncio
    async def test_health_check(self, gateway, mock_connection_manager):
        """Test gateway health check"""
        # Mock successful query
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [{"health_check": 1}]
        mock_conn.cursor.return_value = mock_cursor

        async def async_context():
            yield mock_conn

        mock_connection_manager.get_connection.return_value = async_context()

        # Check health
        health = await gateway.health_check()

        assert health["status"] == "healthy"
        assert health["credits_used_today"] >= 0
        assert health["credits_remaining"] > 0
        assert health["daily_limit"] == 100
        assert health["initialized"] is True

    @pytest.mark.asyncio
    async def test_daily_credit_reset(self, gateway):
        """Test that credits reset on new day"""
        # Set credits for yesterday
        gateway._credits_used_today = 50
        gateway._last_credit_reset = datetime(2024, 1, 1).date()

        # Mock today as next day
        with patch("core.infra.cortex_gateway.datetime") as mock_datetime:
            mock_datetime.now.return_value = datetime(2024, 1, 2)

            # Check credit limit (should reset)
            await gateway._check_credit_limit(10)

            assert gateway._credits_used_today == 0
            assert gateway._last_credit_reset == datetime(2024, 1, 2).date()

    @pytest.mark.asyncio
    async def test_metrics_tracking(self, gateway, mock_connection_manager):
        """Test Prometheus metrics are updated"""
        with patch("core.infra.cortex_gateway.snowflake_query_count") as mock_counter:
            with patch(
                "core.infra.cortex_gateway.snowflake_query_duration"
            ) as mock_histogram:
                # Mock connection
                mock_conn = MagicMock()
                mock_cursor = MagicMock()
                mock_cursor.fetchall.return_value = []
                mock_conn.cursor.return_value = mock_cursor

                async def async_context():
                    yield mock_conn

                mock_connection_manager.get_connection.return_value = async_context()

                # Execute query
                await gateway.execute_sql("SELECT 1")

                # Check metrics were updated
                mock_counter.labels.assert_called()
                mock_histogram.labels.assert_called()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
