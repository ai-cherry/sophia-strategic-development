import asyncio
from unittest.mock import AsyncMock, patch

import pandas as pd
import pytest

from backend.services.circuit_breaker import CircuitBreaker, ConnectionError
from backend.services.data_source_manager import (
    DataValidationError,
    EmptyResultError,
)
from backend.services.data_transformer import DataTransformer
from backend.services.unified_intelligence_service import UnifiedIntelligenceService


@pytest.mark.integration
class TestLiveDataPipeline:
    """Comprehensive tests for the live data pipeline."""

    @pytest.fixture
    def mock_snowflake_data(self) -> pd.DataFrame:
        """Provides a mock pandas DataFrame for Snowflake sales data."""
        return pd.DataFrame(
            {
                "deal_id": ["D001", "D002", "D003"],
                "deal_name": ["Acme Corp", "TechStart", "GlobalTech"],
                "amount": [450000, 380000, 275000],
                "stage": ["Negotiation", "Proposal", "Discovery"],
                "probability": [85, 70, 40],
                "close_date": pd.to_datetime(
                    ["2025-08-15", "2025-09-01", "2025-09-30"]
                ),
                "last_activity_date": pd.to_datetime(
                    ["2025-07-01", "2025-06-20", "2025-07-05"]
                ),
            }
        )

    @pytest.mark.asyncio
    @patch("backend.services.data_source_manager.DataSourceManager.fetch_data")
    @patch(
        "backend.services.advanced_llm_service.AdvancedLLMService.synthesize_response"
    )
    async def test_end_to_end_sales_query(
        self, mock_synthesize, mock_fetch_data, mock_snowflake_data
    ):
        """Test the complete flow from a user query to a synthesized response."""
        # Mock the data fetching to return our pandas DataFrame
        mock_fetch_data.return_value = mock_snowflake_data.to_dict("records")

        # Mock the LLM synthesis to return a predictable response
        mock_synthesize.return_value = "Synthesized response about top deals."

        # We need to patch the initializer of the service to use our mocks
        with patch(
            "backend.services.unified_intelligence_service.DataSourceManager",
            return_value=AsyncMock(fetch_data=mock_fetch_data),
        ), patch(
            "backend.services.unified_intelligence_service.AdvancedLLMService",
            return_value=AsyncMock(synthesize_response=mock_synthesize),
        ):
            service = UnifiedIntelligenceService()
            result = await service.process_query("Show me top deals")

            # Assertions
            mock_fetch_data.assert_called_once()
            mock_synthesize.assert_called_once()

            assert result["type"] == "sales"
            assert "Acme Corp" in str(result.get("results"))
            assert result["insights"] is not None
            assert result["response"] == "Synthesized response about top deals."

    def test_data_validation_error(self):
        """Test that the DataTransformer raises validation errors for invalid data."""
        invalid_data = pd.DataFrame({"deal_id": ["D001"]})  # Missing required columns

        with pytest.raises(DataValidationError, match="Missing required sales columns"):
            DataTransformer.validate_sales_data(invalid_data)

    def test_empty_result_error(self):
        """Test that the DataTransformer raises EmptyResultError for empty input."""
        with pytest.raises(EmptyResultError, match="Sales data DataFrame is empty"):
            DataTransformer.validate_sales_data(pd.DataFrame())

    @pytest.mark.asyncio
    async def test_circuit_breaker_opens_and_recovers(self):
        """Test that the circuit breaker opens after failures and recovers after timeout."""
        breaker = CircuitBreaker(
            failure_threshold=2, recovery_timeout=1
        )  # Quick timeout for test

        async def failing_function():
            raise ConnectionError("Service is unavailable")

        # Trigger failures to open the circuit
        for _ in range(2):
            with pytest.raises(ConnectionError):
                await breaker.call(failing_function)

        assert breaker.state == "open"

        # Further calls should fail immediately while the circuit is open
        with pytest.raises(ConnectionError, match="is open"):
            await breaker.call(failing_function)

        # Wait for the recovery timeout
        await asyncio.sleep(1.1)

        # The next call should be in a "half-open" state and succeed if the function works
        async def succeeding_function():
            return "Success"

        result = await breaker.call(succeeding_function)
        assert result == "Success"
        assert breaker.state == "closed"
