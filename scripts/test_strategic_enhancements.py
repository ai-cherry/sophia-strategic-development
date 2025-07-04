#!/usr/bin/env python3
"""
Test script for strategic enhancement services.
"""

import asyncio
import sys
from datetime import datetime

# Add parent directory to path
sys.path.append("/Users/lynnmusil/sophia-main")

from backend.services.fast_document_processor import FastDocumentProcessor
from backend.services.project_intelligence_service import ProjectIntelligenceService
from backend.services.structured_output_service import StructuredOutputService


async def test_project_intelligence():
    """Test Project Intelligence Service."""
    print("\n=== Testing Project Intelligence Service ===")

    try:
        service = ProjectIntelligenceService()
        print("✅ Service initialized")

        # Note: These will fail without actual Snowflake data
        # but we can test the service structure
        print(
            "- Service has get_project_summary method:",
            hasattr(service, "get_project_summary"),
        )
        print(
            "- Service has get_team_performance method:",
            hasattr(service, "get_team_performance"),
        )
        print(
            "- Service has get_milestone_tracking method:",
            hasattr(service, "get_milestone_tracking"),
        )

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


async def test_structured_output():
    """Test Structured Output Service."""
    print("\n=== Testing Structured Output Service ===")

    try:
        service = StructuredOutputService()
        print("✅ Service initialized")

        # Test the service structure
        print(
            "- Service has get_structured_output method:",
            hasattr(service, "get_structured_output"),
        )
        print(
            "- Service has get_executive_summary method:",
            hasattr(service, "get_executive_summary"),
        )
        print("- Service has analyze_deal method:", hasattr(service, "analyze_deal"))
        print("- Service has analyze_call method:", hasattr(service, "analyze_call"))

        # Test schema classes
        from backend.services.structured_output_service import (
            CallInsights,
            DealAnalysis,
            ExecutiveSummary,
        )

        # Create test instances
        exec_summary = ExecutiveSummary(
            title="Test Summary",
            key_points=["Point 1", "Point 2", "Point 3"],
            metrics={"revenue": 100000, "growth": 15},
            recommendations=["Recommendation 1"],
            risk_level="low",
            confidence_score=0.85,
        )
        print("✅ ExecutiveSummary schema working")

        deal = DealAnalysis(
            deal_id="test-123",
            deal_name="Test Deal",
            probability=75.0,
            risk_factors=["Risk 1"],
            opportunities=["Opportunity 1"],
            next_steps=["Step 1"],
            estimated_close_date=datetime.now(),
            competitor_threats=["Competitor 1"],
        )
        print("✅ DealAnalysis schema working")

        call = CallInsights(
            call_id="call-123",
            sentiment_score=0.7,
            key_topics=["Topic 1"],
            action_items=[{"task": "Follow up", "owner": "Sales Rep"}],
            customer_concerns=["Concern 1"],
            positive_signals=["Signal 1"],
            follow_up_required=True,
            urgency_level="medium",
        )
        print("✅ CallInsights schema working")

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


async def test_fast_document_processor():
    """Test Fast Document Processor."""
    print("\n=== Testing Fast Document Processor ===")

    try:
        processor = FastDocumentProcessor(max_workers=4)
        print("✅ Processor initialized")

        # Test processing a sample document
        test_docs = [
            {
                "id": "doc1",
                "content": "This is a test document with some content that needs to be processed and chunked intelligently.",
                "type": "text",
            },
            {
                "id": "doc2",
                "content": "# Test Markdown\n\nThis is a markdown document.\n\n## Section 1\n\nSome content here.\n\n## Section 2\n\nMore content here.",
                "type": "markdown",
            },
        ]

        print("\nProcessing test documents...")
        results = await processor.process_documents_batch(test_docs)

        print(f"✅ Processed {len(results)} documents")
        for result in results:
            print(
                f"  - Document {result.document_id}: {result.status}, {result.chunks_processed} chunks"
            )

        # Get metrics
        metrics = processor.get_metrics()
        print("\nMetrics:")
        print(f"  - Documents per second: {metrics.documents_per_second:.2f}")
        print(f"  - Average chunk time: {metrics.average_chunk_time_ms:.2f}ms")
        print(f"  - Cache hit rate: {metrics.cache_hit_rate:.2%}")

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


async def main():
    """Run all tests."""
    print("Testing Strategic Enhancement Services")
    print("=" * 50)

    results = {
        "project_intelligence": await test_project_intelligence(),
        "structured_output": await test_structured_output(),
        "fast_document_processor": await test_fast_document_processor(),
    }

    print("\n" + "=" * 50)
    print("Test Results Summary:")
    for service, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"  {service}: {status}")

    total_passed = sum(results.values())
    print(f"\nTotal: {total_passed}/{len(results)} services working")

    return total_passed == len(results)


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
