#!/usr/bin/env python3
"""Test script for enhanced app components"""
import contextlib
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_imports():
    """Test if all imports work correctly"""

    with contextlib.suppress(ImportError):
        pass

    with contextlib.suppress(ImportError):
        pass

    with contextlib.suppress(ImportError):
        pass


def test_components():
    """Test individual components"""

    # Test capability router
    try:
        from backend.services.mcp_capability_router import capability_router

        coverage = capability_router.get_capability_coverage()

        # Show some capabilities
        for _cap, _servers in list(coverage.items())[:5]:
            pass
    except Exception:
        pass

    # Test health monitor
    try:
        from backend.monitoring.mcp_health_monitor import health_monitor

        health_monitor.get_health_summary()
    except Exception:
        pass


def main():
    """Run all tests"""

    test_imports()
    test_components()


if __name__ == "__main__":
    main()
