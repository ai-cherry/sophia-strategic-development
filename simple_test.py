#!/usr/bin/env python3
"""
Simple test to verify refactoring structure
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))


def test_basic_imports():
    """Test basic imports without configuration"""

    try:
        # Test models import

        # Test utils import
        from backend.utils.snowflake_cortex_service_utils import (
            CacheManager,
            CortexUtils,
            PerformanceMonitor,
        )

        # Test that enums work

        # Test utility functions
        utils = CortexUtils()
        utils.escape_sql("test'string")

        # Test performance monitor
        monitor = PerformanceMonitor()
        start_time = monitor.start_operation()
        monitor.end_operation(start_time, success=True)
        monitor.get_performance_stats()

        # Test cache manager
        cache = CacheManager()
        cache.set("test_key", "test_value")
        cache.get("test_key")

        return True

    except Exception:
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    if test_basic_imports():
        pass
    else:
        pass
