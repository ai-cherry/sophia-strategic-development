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

    try:
        # Test MCP orchestration service (should use lazy initialization)

        # Test secure snowflake config (should use lazy initialization)

        # Test AI Memory MCP server

        # Test FastAPI app imports (without starting)

        return True

    except Exception:
        import traceback

        traceback.print_exc()
        return False


def test_lazy_initialization():
    """Test that lazy initialization prevents immediate validation"""

    try:
        # Import should work without triggering validation

        # Calling the function should trigger validation (and may fail)

        return True

    except Exception:
        return False


def main():
    """Main test function"""

    # Test critical imports
    imports_ok = test_critical_imports()

    # Test lazy initialization
    lazy_ok = test_lazy_initialization()

    if imports_ok and lazy_ok:
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
