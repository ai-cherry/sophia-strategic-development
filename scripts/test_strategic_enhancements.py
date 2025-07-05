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

    try:
        ProjectIntelligenceService()

        # Note: These will fail without actual Snowflake data
        # but we can test the service structure

        return True

    except Exception:
        return False


async def test_structured_output():
    """Test Structured Output Service."""

    try:
        StructuredOutputService()

        # Test the service structure

        # Test schema classes
        from backend.services.structured_output_service import (
            CallInsights,
            DealAnalysis,
            ExecutiveSummary,
        )

        # Create test instances
        ExecutiveSummary(
            title="Test Summary",
            key_points=["Point 1", "Point 2", "Point 3"],
            metrics={"revenue": 100000, "growth": 15},
            recommendations=["Recommendation 1"],
            risk_level="low",
            confidence_score=0.85,
        )

        DealAnalysis(
            deal_id="test-123",
            deal_name="Test Deal",
            probability=75.0,
            risk_factors=["Risk 1"],
            opportunities=["Opportunity 1"],
            next_steps=["Step 1"],
            estimated_close_date=datetime.now(),
            competitor_threats=["Competitor 1"],
        )

        CallInsights(
            call_id="call-123",
            sentiment_score=0.7,
            key_topics=["Topic 1"],
            action_items=[{"task": "Follow up", "owner": "Sales Rep"}],
            customer_concerns=["Concern 1"],
            positive_signals=["Signal 1"],
            follow_up_required=True,
            urgency_level="medium",
        )

        return True

    except Exception:
        return False


async def test_fast_document_processor():
    """Test Fast Document Processor."""

    try:
        processor = FastDocumentProcessor(max_workers=4)

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

        results = await processor.process_documents_batch(test_docs)

        for _result in results:
            pass

        # Get metrics
        processor.get_metrics()

        return True

    except Exception:
        return False


async def main():
    """Run all tests."""

    results = {
        "project_intelligence": await test_project_intelligence(),
        "structured_output": await test_structured_output(),
        "fast_document_processor": await test_fast_document_processor(),
    }

    for _service, _passed in results.items():
        pass

    total_passed = sum(results.values())

    return total_passed == len(results)


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
