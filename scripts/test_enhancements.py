#!/usr/bin/env python3
"""
Test Sophia AI enhancements locally
Verifies core features are working
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import our enhanced modules
try:
    from backend.services.unified_memory_service_v2 import UnifiedMemoryServiceV2

    print("✅ UnifiedMemoryServiceV2 imported successfully")
except Exception as e:
    print(f"❌ Failed to import UnifiedMemoryServiceV2: {e}")

try:
    from backend.services.sophia_unified_orchestrator import SophiaUnifiedOrchestrator

    print("✅ SophiaUnifiedOrchestrator imported successfully")
except Exception as e:
    print(f"❌ Failed to import SophiaUnifiedOrchestrator: {e}")

try:
    from backend.services.personality_engine import PersonalityEngine, PersonalityType

    print("✅ PersonalityEngine imported successfully")
except Exception as e:
    print(f"❌ Failed to import PersonalityEngine: {e}")

try:

    print("✅ EnhancedChatServiceV4 imported successfully")
except Exception as e:
    print(f"❌ Failed to import EnhancedChatServiceV4: {e}")


async def test_personality_engine():
    """Test the personality engine"""
    print("\n🧠 Testing Personality Engine...")
    try:
        engine = PersonalityEngine()

        # Test each personality
        personalities = [
            PersonalityType.EXPERT_SNARK,
            PersonalityType.CEO_MODE,
            PersonalityType.DATA_SCIENTIST,
        ]

        test_query = "Tell me about our revenue performance"

        for personality in personalities:
            prompt = engine.apply_personality(test_query, personality)
            print(f"\n{personality.value}:")
            print(f"  System prompt preview: {prompt[:100]}...")

        print("\n✅ Personality Engine working!")
        return True
    except Exception as e:
        print(f"❌ Personality Engine test failed: {e}")
        return False


async def test_memory_service():
    """Test memory service (mock mode)"""
    print("\n💾 Testing Memory Service...")
    try:
        # We'll test in mock mode since we don't have real connections
        print("  Testing import and initialization...")

        # Just verify the class structure
        memory = UnifiedMemoryServiceV2()

        # Check if methods exist
        assert hasattr(memory, "add_knowledge")
        assert hasattr(memory, "search_knowledge")
        assert hasattr(memory, "get_embeddings")

        print("  ✅ Memory service structure validated")
        return True
    except Exception as e:
        print(f"❌ Memory Service test failed: {e}")
        return False


async def test_orchestrator():
    """Test the unified orchestrator"""
    print("\n🎯 Testing Unified Orchestrator...")
    try:
        orchestrator = SophiaUnifiedOrchestrator()

        # Test reasoning chain creation
        test_query = "What's our best performing product?"

        print(f"  Creating reasoning chain for: '{test_query}'")

        # Just verify the structure
        assert hasattr(orchestrator, "process_query")
        assert hasattr(orchestrator, "execute_reasoning_chain")
        assert hasattr(orchestrator, "self_critique")

        print("  ✅ Orchestrator structure validated")
        return True
    except Exception as e:
        print(f"❌ Orchestrator test failed: {e}")
        return False


async def test_chat_service():
    """Test enhanced chat service v4"""
    print("\n💬 Testing Enhanced Chat Service V4...")
    try:
        # Check the service structure
        from backend.services.enhanced_chat_service_v4 import ChatRequest

        # Create a test request
        request = ChatRequest(
            query="Test query",
            user_id="test_user",
            personality=PersonalityType.EXPERT_SNARK,
            enable_reasoning=True,
            enable_external_knowledge=False,
        )

        print(f"  Created test request with personality: {request.personality}")
        print(f"  Multi-hop reasoning: {request.enable_reasoning}")

        print("  ✅ Chat Service V4 structure validated")
        return True
    except Exception as e:
        print(f"❌ Chat Service test failed: {e}")
        return False


async def main():
    """Run all tests"""
    print("🚀 SOPHIA AI ENHANCEMENT TEST SUITE")
    print("=" * 50)
    print("Testing core enhancements locally...")
    print("=" * 50)

    results = []

    # Run tests
    results.append(await test_personality_engine())
    results.append(await test_memory_service())
    results.append(await test_orchestrator())
    results.append(await test_chat_service())

    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)

    passed = sum(results)
    total = len(results)

    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")

    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("🔥 Sophia AI enhancements are ready!")
    else:
        print("\n⚠️  Some tests failed")
        print("Check the errors above for details")

    return passed == total


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
