#!/usr/bin/env python3
"""
Sophia AI Phase 1 Integration Test
Validates all core services and orchestration
"""

import asyncio
import json
import sys
from datetime import datetime

# Add backend to path
sys.path.append("backend")

from backend.services.sophia_ai_orchestrator import (
    SophiaAIOrchestrator,
    OrchestrationRequest,
    RequestType,
    OrchestrationMode,
)


async def test_knowledge_base_integration():
    """Test Enhanced Knowledge Base Service"""
    print("🧠 Testing Enhanced Knowledge Base Service...")

    try:
        orchestrator = SophiaAIOrchestrator()
        await orchestrator.initialize()

        # Test knowledge ingestion
        ingestion_request = OrchestrationRequest(
            request_id="test_ingest_001",
            request_type=RequestType.KNOWLEDGE_INGESTION,
            user_id="test_user",
            content="Our sales process involves initial contact, needs assessment, proposal, and closing.",
            context={"source": "test", "category": "sales_process"},
        )

        ingestion_response = await orchestrator.process_request(ingestion_request)

        if ingestion_response.success:
            print("  ✅ Knowledge ingestion successful")
            knowledge_id = ingestion_response.primary_response.get("knowledge_id")
            print(f"     Knowledge ID: {knowledge_id}")
        else:
            print(f"  ❌ Knowledge ingestion failed: {ingestion_response.error}")
            return False

        # Test knowledge query
        query_request = OrchestrationRequest(
            request_id="test_query_001",
            request_type=RequestType.KNOWLEDGE_QUERY,
            user_id="test_user",
            query="What is our sales process?",
            context={"source": "test"},
        )

        query_response = await orchestrator.process_request(query_request)

        if query_response.success:
            print("  ✅ Knowledge query successful")
            print(f"     Results found: {query_response.knowledge_items_accessed}")
        else:
            print(f"  ❌ Knowledge query failed: {query_response.error}")
            return False

        # Test teaching interface
        teaching_request = OrchestrationRequest(
            request_id="test_teaching_001",
            request_type=RequestType.TEACHING_SESSION,
            user_id="test_user",
            context={
                "teaching_data": {
                    "knowledge_id": knowledge_id,
                    "feedback": "This is very helpful sales process information",
                    "session_type": "validation",
                }
            },
        )

        teaching_response = await orchestrator.process_request(teaching_request)

        if teaching_response.success:
            print("  ✅ Teaching session successful")
        else:
            print(f"  ❌ Teaching session failed: {teaching_response.error}")
            return False

        return True

    except Exception as e:
        print(f"  ❌ Knowledge Base integration error: {e}")
        return False


async def test_sales_coach_integration():
    """Test Interactive Sales Coach Agent"""
    print("🎯 Testing Interactive Sales Coach Agent...")

    try:
        orchestrator = SophiaAIOrchestrator()
        await orchestrator.initialize()

        # Test real-time coaching
        coaching_request = OrchestrationRequest(
            request_id="test_coaching_001",
            request_type=RequestType.SALES_COACHING_REQUEST,
            user_id="sales_rep_001",
            query="How can I improve my follow-up strategy?",
            context={
                "type": "performance_improvement",
                "recent_calls": 5,
                "close_rate": 0.15,
            },
        )

        coaching_response = await orchestrator.process_request(coaching_request)

        if coaching_response.success:
            print("  ✅ Sales coaching successful")
            print(
                f"     Insights generated: {coaching_response.coaching_insights_generated}"
            )
        else:
            print(f"  ❌ Sales coaching failed: {coaching_response.error}")
            return False

        # Test Slack integration
        if orchestrator.sales_coach:
            slack_event = {
                "type": "message",
                "user": "sales_rep_001",
                "channel": "sales-coaching",
                "text": "@coach help with objection handling",
            }

            slack_response = await orchestrator.sales_coach.slack_coaching_interface(
                slack_event
            )

            if slack_response.get("success"):
                print("  ✅ Slack integration successful")
            else:
                print(f"  ❌ Slack integration failed: {slack_response.get('error')}")
                return False

        return True

    except Exception as e:
        print(f"  ❌ Sales Coach integration error: {e}")
        return False


async def test_memory_preservation_integration():
    """Test Memory Preservation Service"""
    print("💾 Testing Memory Preservation Service...")

    try:
        orchestrator = SophiaAIOrchestrator()
        await orchestrator.initialize()

        # Test memory validation
        validation_request = OrchestrationRequest(
            request_id="test_memory_001",
            request_type=RequestType.MEMORY_PRESERVATION,
            user_id="system",
            context={
                "operation": "validate_integrity",
                "source_system": "ai_memory_mcp",
            },
        )

        validation_response = await orchestrator.process_request(validation_request)

        if validation_response.success:
            print("  ✅ Memory validation successful")
        else:
            print(f"  ❌ Memory validation failed: {validation_response.error}")
            return False

        # Test incremental sync
        sync_request = OrchestrationRequest(
            request_id="test_sync_001",
            request_type=RequestType.MEMORY_PRESERVATION,
            user_id="system",
            context={"operation": "incremental_sync", "source_system": "ai_memory_mcp"},
        )

        sync_response = await orchestrator.process_request(sync_request)

        if sync_response.success:
            print("  ✅ Memory sync successful")
            print(f"     Memories processed: {sync_response.memories_processed}")
        else:
            print(f"  ❌ Memory sync failed: {sync_response.error}")
            return False

        return True

    except Exception as e:
        print(f"  ❌ Memory Preservation integration error: {e}")
        return False


async def test_unified_intelligence():
    """Test Unified Intelligence Orchestration"""
    print("🎼 Testing Unified Intelligence Orchestration...")

    try:
        orchestrator = SophiaAIOrchestrator()
        await orchestrator.initialize()

        # Test unified intelligence query
        unified_request = OrchestrationRequest(
            request_id="test_unified_001",
            request_type=RequestType.KNOWLEDGE_QUERY,
            user_id="test_user",
            query="How can I improve my sales performance using our process?",
            context={"source": "unified_test"},
            mode=OrchestrationMode.UNIFIED_INTELLIGENCE,
        )

        unified_response = await orchestrator.process_request(unified_request)

        if unified_response.success:
            print("  ✅ Unified intelligence successful")
            print(f"     Services coordinated: {len(unified_response.services_used)}")
            print(f"     Confidence score: {unified_response.confidence_score:.2f}")
            print(f"     Processing time: {unified_response.processing_time_ms:.2f}ms")
        else:
            print(f"  ❌ Unified intelligence failed: {unified_response.error}")
            return False

        return True

    except Exception as e:
        print(f"  ❌ Unified Intelligence error: {e}")
        return False


async def test_system_health():
    """Test System Health and Analytics"""
    print("🏥 Testing System Health and Analytics...")

    try:
        orchestrator = SophiaAIOrchestrator()
        await orchestrator.initialize()

        # Test health check
        health_request = OrchestrationRequest(
            request_id="test_health_001",
            request_type=RequestType.HEALTH_CHECK,
            user_id="system",
            context={"source": "integration_test"},
        )

        health_response = await orchestrator.process_request(health_request)

        if health_response.success:
            print("  ✅ Health check successful")

            # Check individual service health
            service_health = health_response.primary_response.get("service_health", {})
            for service, health in service_health.items():
                status = health.get("status", "unknown")
                print(f"     {service}: {status}")
        else:
            print(f"  ❌ Health check failed: {health_response.error}")
            return False

        # Test analytics
        analytics_request = OrchestrationRequest(
            request_id="test_analytics_001",
            request_type=RequestType.ANALYTICS_REQUEST,
            user_id="system",
            context={"analytics_type": "comprehensive"},
        )

        analytics_response = await orchestrator.process_request(analytics_request)

        if analytics_response.success:
            print("  ✅ Analytics retrieval successful")

            orchestration_analytics = analytics_response.primary_response.get(
                "orchestration_analytics", {}
            )
            total_requests = orchestration_analytics.get("total_requests", 0)
            success_rate = orchestration_analytics.get("successful_requests", 0) / max(
                total_requests, 1
            )

            print(f"     Total requests processed: {total_requests}")
            print(f"     Success rate: {success_rate:.1%}")
            print(
                f"     Average response time: {orchestration_analytics.get('average_response_time', 0):.2f}ms"
            )
        else:
            print(f"  ❌ Analytics retrieval failed: {analytics_response.error}")
            return False

        return True

    except Exception as e:
        print(f"  ❌ System Health error: {e}")
        return False


async def run_comprehensive_integration_test():
    """Run comprehensive integration test of all Phase 1 components"""
    print("🚀 SOPHIA AI PHASE 1 INTEGRATION TEST")
    print("=" * 50)

    test_start = datetime.now()
    test_results = []

    # Run all integration tests
    tests = [
        ("Knowledge Base Integration", test_knowledge_base_integration),
        ("Sales Coach Integration", test_sales_coach_integration),
        ("Memory Preservation Integration", test_memory_preservation_integration),
        ("Unified Intelligence", test_unified_intelligence),
        ("System Health & Analytics", test_system_health),
    ]

    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 30)

        try:
            test_result = await test_func()
            test_results.append((test_name, test_result))

            if test_result:
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")

        except Exception as e:
            print(f"💥 {test_name} ERROR: {e}")
            test_results.append((test_name, False))

    # Print final results
    test_duration = (datetime.now() - test_start).total_seconds()

    print("\n" + "=" * 50)
    print("📊 INTEGRATION TEST RESULTS")
    print("=" * 50)

    passed_tests = sum(1 for _, result in test_results if result)
    total_tests = len(test_results)

    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")

    print(f"\n🎯 OVERALL RESULTS:")
    print(f"   Tests Passed: {passed_tests}/{total_tests}")
    print(f"   Success Rate: {passed_tests/total_tests:.1%}")
    print(f"   Test Duration: {test_duration:.2f} seconds")

    if passed_tests == total_tests:
        print("\n�� ALL TESTS PASSED! Sophia AI Phase 1 is ready for production!")
        return True
    else:
        print(f"\n⚠️  {total_tests - passed_tests} tests failed. Review errors above.")
        return False


if __name__ == "__main__":
    success = asyncio.run(run_comprehensive_integration_test())
    sys.exit(0 if success else 1)
