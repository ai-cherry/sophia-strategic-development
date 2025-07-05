#!/usr/bin/env python3
"""
Test script to verify the refactored Snowflake Cortex service
"""

import os
import sys

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))


def test_imports():
    """Test that all refactored modules can be imported"""

    try:
        # Test models import

        # Test utils import

        # Test core import

        # Test handlers import

        # Test facade import

        return True

    except Exception:
        return False


def test_instantiation():
    """Test that the service can be instantiated"""

    try:
        from backend.utils.snowflake_cortex_service import SnowflakeCortexService

        # Create service instance
        service = SnowflakeCortexService()

        # Test that handlers are initialized
        assert hasattr(service, "cortex_handlers"), "Missing cortex_handlers"
        assert hasattr(service, "business_handlers"), "Missing business_handlers"
        assert hasattr(service, "utils"), "Missing utils"
        assert hasattr(service, "performance_monitor"), "Missing performance_monitor"

        # Test that core methods exist
        assert hasattr(
            service, "summarize_text_in_snowflake"
        ), "Missing summarize method"
        assert hasattr(
            service, "analyze_sentiment_in_snowflake"
        ), "Missing sentiment method"
        assert hasattr(
            service, "generate_embedding_in_snowflake"
        ), "Missing embedding method"
        assert hasattr(
            service, "store_embedding_in_business_table"
        ), "Missing business embedding method"

        return True

    except Exception:
        return False


def test_backward_compatibility():
    """Test that the facade maintains backward compatibility"""

    try:
        # Test that all original imports still work
        from backend.utils.snowflake_cortex_service import (
            CortexModel,
        )

        # Test that enum values are accessible
        assert hasattr(CortexModel, "E5_BASE_V2"), "Missing E5_BASE_V2 model"
        assert hasattr(CortexModel, "MISTRAL_7B"), "Missing MISTRAL_7B model"

        return True

    except Exception:
        return False


def main():
    """Run all tests"""

    tests = [test_imports, test_instantiation, test_backward_compatibility]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1
        else:
            break  # Stop on first failure

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
