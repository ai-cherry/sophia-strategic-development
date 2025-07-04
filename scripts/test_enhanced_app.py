#!/usr/bin/env python3
"""Test script for enhanced app components"""
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_imports():
    """Test if all imports work correctly"""
    print("Testing imports...")

    try:
        from backend.monitoring.mcp_health_monitor import HealthStatus, health_monitor

        print("✅ Health monitor imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import health monitor: {e}")

    try:
        from backend.services.gptcache_service import CEO_COMMON_QUERIES, cache_service

        print("✅ Cache service imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import cache service: {e}")

    try:
        from backend.services.mcp_capability_router import Capability, capability_router

        print("✅ Capability router imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import capability router: {e}")


def test_components():
    """Test individual components"""
    print("\nTesting components...")

    # Test capability router
    try:
        from backend.services.mcp_capability_router import capability_router

        coverage = capability_router.get_capability_coverage()
        print(f"✅ Capability router working - {len(coverage)} capabilities mapped")

        # Show some capabilities
        print("\nSample capabilities:")
        for cap, servers in list(coverage.items())[:5]:
            print(f"  - {cap}: {', '.join(servers)}")
    except Exception as e:
        print(f"❌ Capability router error: {e}")

    # Test health monitor
    try:
        from backend.monitoring.mcp_health_monitor import health_monitor

        summary = health_monitor.get_health_summary()
        print(
            f"\n✅ Health monitor working - monitoring {summary['total_servers']} servers"
        )
    except Exception as e:
        print(f"❌ Health monitor error: {e}")


def main():
    """Run all tests"""
    print("Enhanced App Component Tests")
    print("=" * 50)

    test_imports()
    test_components()

    print("\n" + "=" * 50)
    print("Test complete!")


if __name__ == "__main__":
    main()
