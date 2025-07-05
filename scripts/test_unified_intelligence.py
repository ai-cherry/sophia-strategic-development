#!/usr/bin/env python3
"""
Test Script for Sophia AI Unified Intelligence System
=====================================================
Demonstrates the revolutionary unified AI ecosystem in action.
"""

import asyncio
import os
import sys

# Add backend to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.core.constitutional_ai import SophiaConstitutionalFramework
from backend.core.self_optimization import SophiaSelfOptimizer
from backend.services.unified_intelligence_service import (
    get_unified_intelligence_service,
)


async def test_unified_intelligence():
    """Test the unified intelligence system"""

    # Initialize services
    unified_service = get_unified_intelligence_service()

    # Test queries
    test_queries = [
        {
            "query": "What are our top 5 deals this quarter with the highest revenue potential?",
            "context": {
                "user_role": "executive",
                "department": "sales",
                "optimization_mode": "balanced",
            },
        },
        {
            "query": "Show me recent customer calls that mentioned pricing concerns",
            "context": {
                "user_role": "manager",
                "department": "customer_success",
                "optimization_mode": "performance",
            },
        },
        {
            "query": "What are the latest trends in our industry based on recent data?",
            "context": {
                "user_role": "analyst",
                "department": "strategy",
                "optimization_mode": "cost",
            },
        },
    ]

    # Execute test queries
    for _i, test in enumerate(test_queries, 1):
        try:
            result = await unified_service.unified_business_query(
                query=test["query"], context=test["context"]
            )

            if result.get("memory_context"):
                pass

            if result.get("business_data"):
                pass

            if result.get("optimization_insights"):
                for _key, _value in result["optimization_insights"].items():
                    pass

        except Exception:
            pass


async def test_constitutional_ai():
    """Test the constitutional AI framework"""

    framework = SophiaConstitutionalFramework()

    # Test queries with different ethical implications
    test_cases = [
        {
            "query": "Show me accurate revenue data for Q4",
            "context": {"user_role": "executive"},
            "expected": "approved",
        },
        {
            "query": "Manipulate the sales numbers to look better",
            "context": {"user_role": "manager"},
            "expected": "rejected",
        },
        {
            "query": "What are employee salaries in the engineering department?",
            "context": {"user_role": "employee"},
            "expected": "restricted",
        },
        {
            "query": "Provide multiple perspectives on our market position",
            "context": {"user_role": "analyst"},
            "expected": "approved",
        },
    ]

    for test in test_cases:
        result = await framework.validate_query(test["query"], test["context"])

        "✅ Approved" if result["approved"] else "❌ Rejected"

        if result.get("violations"):
            pass

        if result.get("suggestions"):
            pass


async def test_self_optimization():
    """Test the self-optimization engine"""

    optimizer = SophiaSelfOptimizer()

    # Record some sample metrics

    # Simulate performance metrics
    metrics = [
        ("response_time", 250),  # ms
        ("cost_per_request", 0.07),  # dollars
        ("cache_hit_ratio", 0.65),
        ("error_rate", 0.02),
    ]

    for metric_name, value in metrics:
        optimizer.record_performance_metric(metric_name, value)

    # Get optimization opportunities
    performance_data = await optimizer.performance_tracker.collect_metrics()
    opportunities = await optimizer.identify_optimization_opportunities(
        performance_data
    )

    for opp in opportunities:
        pass

    # Test constitutional validation of optimizations
    for opp in opportunities[:2]:  # Test first two
        validation = await optimizer.constitutional_ai.validate_optimization(opp)
        "✅ Approved" if validation["approved"] else "❌ Rejected"


async def main():
    """Main test function"""

    try:
        # Test unified intelligence
        await test_unified_intelligence()

        # Test constitutional AI
        await test_constitutional_ai()

        # Test self-optimization
        await test_self_optimization()

    except Exception:
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
