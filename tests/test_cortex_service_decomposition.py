#!/usr/bin/env python3
"""
Tests for Snowflake Cortex Service decomposition
Verifies that decomposed modules work correctly together
"""

import pytest
from backend.utils.optimized_snowflake_cortex_service_models import (
    CortexOperation,
    ProcessingMode,
    CortexResult,
    CortexConfig,
    CortexPerformanceMetrics
)
from backend.utils.optimized_snowflake_cortex_service_utils import CortexUtils


class TestCortexServiceDecomposition:
    """Test suite for decomposed Cortex service modules"""

    def test_models_import_successfully(self):
        """Test that all models can be imported and instantiated"""
        # Test enum values
        assert CortexOperation.SENTIMENT_ANALYSIS == "sentiment_analysis"
        assert ProcessingMode.BATCH == "batch"
        
        # Test dataclass instantiation
        result = CortexResult(
            operation=CortexOperation.SENTIMENT_ANALYSIS,
            success=True,
            result={"score": 0.8}
        )
        assert result.operation == CortexOperation.SENTIMENT_ANALYSIS
        assert result.success is True
        
        # Test config with defaults
        config = CortexConfig()
        assert config.max_batch_size == 50
        assert config.optimal_batch_size == 10


if __name__ == "__main__":
    pytest.main([__file__])
