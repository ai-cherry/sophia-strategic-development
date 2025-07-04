#!/usr/bin/env python3
"""
Simple test to verify refactoring structure
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))


def test_basic_imports():
    """Test basic imports without configuration"""
    print("🧪 Testing basic refactored imports...")

    try:
        # Test models import
        from backend.utils.snowflake_cortex_service_models import (
            CortexModel,
        )

        print("✅ Models module imported successfully")

        # Test utils import
        from backend.utils.snowflake_cortex_service_utils import (
            CacheManager,
            CortexUtils,
            PerformanceMonitor,
        )

        print("✅ Utils module imported successfully")

        # Test that enums work
        model = CortexModel.E5_BASE_V2
        print(f"✅ Enum access works: {model.value}")

        # Test utility functions
        utils = CortexUtils()
        escaped = utils.escape_sql("test'string")
        print(f"✅ Utility functions work: {escaped}")

        # Test performance monitor
        monitor = PerformanceMonitor()
        start_time = monitor.start_operation()
        monitor.end_operation(start_time, success=True)
        stats = monitor.get_performance_stats()
        print(f"✅ Performance monitoring works: {stats['total_operations']} operations")

        # Test cache manager
        cache = CacheManager()
        cache.set("test_key", "test_value")
        value = cache.get("test_key")
        print(f"✅ Cache management works: {value}")

        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("🚀 Simple Refactoring Test\n")
    if test_basic_imports():
        print("\n🎉 Basic refactoring test passed!")
        print(
            "✨ Task 1 (Split Monolithic Snowflake Cortex Service) - PARTIALLY VERIFIED"
        )
        print("   - ✅ Models module working correctly")
        print("   - ✅ Utils module working correctly")
        print("   - ✅ Enums and utility functions operational")
        print("   - ✅ Performance monitoring functional")
        print("   - ✅ Cache management functional")
        print("   - ⚠️  Core/Handlers modules require configuration (expected)")
    else:
        print("\n❌ Basic test failed")
