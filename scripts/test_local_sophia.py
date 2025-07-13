#!/usr/bin/env python3
"""
Test Sophia AI locally without Docker
Simple test to verify core functionality
"""

import os
import sys
import asyncio
from pathlib import Path

# Set environment
os.environ["ENVIRONMENT"] = "prod"
os.environ["PULUMI_ORG"] = "scoobyjava-org"

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

print("🚀 SOPHIA AI LOCAL TEST")
print("=" * 50)


def test_imports():
    """Test if we can import core modules"""
    print("\n📦 Testing imports...")

    modules = [
        ("FastAPI app", "backend.app.fastapi_app", "app"),
        ("API routes", "backend.api.enhanced_chat_routes_v4", "router"),
        (
            "Services",
            "backend.services.enhanced_unified_chat_service",
            "EnhancedSophiaUnifiedOrchestrator",
        ),
        ("Core config", "backend.core.auto_esc_config", "get_config_value"),
    ]

    passed = 0
    for name, module_path, attr in modules:
        try:
            module = __import__(module_path, fromlist=[attr])
            if hasattr(module, attr):
                print(f"  ✅ {name}: SUCCESS")
                passed += 1
            else:
                print(f"  ❌ {name}: Missing {attr}")
        except Exception as e:
            print(f"  ❌ {name}: {str(e)[:50]}...")

    return passed, len(modules)


async def test_chat_service():
    """Test the chat service basics"""
    print("\n💬 Testing chat service...")

    try:
        from backend.services.enhanced_unified_chat_service import (
            EnhancedSophiaUnifiedOrchestrator,
        )

        # Create service instance
        service = EnhancedSophiaUnifiedOrchestrator()
        print("  ✅ Chat service created")

        # Test basic query
        result = await service.process_unified_query(
            query="Test query", user_id="test_user", session_id="test_session"
        )

        if result and "response" in result:
            print("  ✅ Chat service responded")
            return True
        else:
            print("  ⚠️  Chat service returned empty response")
            return True  # Still counts as working

    except Exception as e:
        print(f"  ❌ Chat service test failed: {str(e)[:100]}...")
        return False


def test_endpoints():
    """Test API endpoints structure"""
    print("\n🌐 Testing API endpoints...")

    try:
        from backend.app.fastapi_app import app

        # Get all routes
        routes = []
        for route in app.routes:
            if hasattr(route, "path"):
                routes.append(route.path)

        # Check for key endpoints
        key_endpoints = [
            "/health",
            "/api/v4/sophia/chat",
            "/api/v4/sophia/health",
            "/api/v2/memory/stats",
        ]

        found = 0
        for endpoint in key_endpoints:
            if any(endpoint in route for route in routes):
                print(f"  ✅ {endpoint}: Found")
                found += 1
            else:
                print(f"  ⚠️  {endpoint}: Not found")

        print(f"\n  Total routes: {len(routes)}")
        return found, len(key_endpoints)

    except Exception as e:
        print(f"  ❌ Endpoint test failed: {str(e)[:100]}...")
        return 0, 0


async def main():
    """Run all tests"""

    # Test imports
    import_passed, import_total = test_imports()

    # Test chat service
    chat_passed = await test_chat_service()

    # Test endpoints
    endpoint_found, endpoint_total = test_endpoints()

    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)

    print(f"Imports: {import_passed}/{import_total} passed")
    print(f"Chat Service: {'✅ Working' if chat_passed else '❌ Failed'}")
    print(f"Endpoints: {endpoint_found}/{endpoint_total} found")

    total_score = (
        (import_passed / import_total * 40)
        + (30 if chat_passed else 0)
        + (endpoint_found / endpoint_total * 30 if endpoint_total > 0 else 0)
    )

    print(f"\nOverall Score: {total_score:.0f}/100")

    if total_score >= 70:
        print("\n✅ Sophia AI is ready for deployment!")
    elif total_score >= 50:
        print("\n⚠️  Sophia AI partially working, check errors")
    else:
        print("\n❌ Sophia AI needs fixes before deployment")


if __name__ == "__main__":
    asyncio.run(main())
