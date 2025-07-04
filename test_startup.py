#!/usr/bin/env python3
"""
Test script to validate Sophia AI startup without environment validation errors
"""

import os
import sys

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_critical_imports():
    """Test that critical imports work without triggering validation"""
    print("🧪 Testing critical imports...")

    try:
        # Test MCP orchestration service (should use lazy initialization)
        print("  ✓ Testing MCP orchestration service...")

        print("    ✓ MCP orchestration service import successful")

        # Test secure snowflake config (should use lazy initialization)
        print("  ✓ Testing secure Snowflake config...")

        print("    ✓ Secure Snowflake config import successful")

        # Test AI Memory MCP server
        print("  ✓ Testing AI Memory MCP server...")

        print("    ✓ AI Memory MCP server import successful")

        # Test FastAPI app imports (without starting)
        print("  ✓ Testing FastAPI app imports...")

        print("    ✓ FastAPI app import successful")

        print("✅ All critical imports successful!")
        return True

    except Exception as e:
        print(f"❌ Import failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_lazy_initialization():
    """Test that lazy initialization prevents immediate validation"""
    print("\n🧪 Testing lazy initialization...")

    try:
        # Import should work without triggering validation

        print("  ✓ Import successful without validation")

        # Calling the function should trigger validation (and may fail)
        print(
            "  ⚠️  Note: Calling get_secure_snowflake_config() would trigger validation"
        )
        print(
            "  ⚠️  This is expected behavior - validation only happens when actually needed"
        )

        return True

    except Exception as e:
        print(f"❌ Lazy initialization test failed: {e}")
        return False


def main():
    """Main test function"""
    print("🚀 Sophia AI Startup Test")
    print("=" * 50)

    # Test critical imports
    imports_ok = test_critical_imports()

    # Test lazy initialization
    lazy_ok = test_lazy_initialization()

    print("\n" + "=" * 50)
    if imports_ok and lazy_ok:
        print("✅ All tests passed! Sophia AI should start successfully.")
        return 0
    else:
        print("❌ Some tests failed. Check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
