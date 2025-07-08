#!/usr/bin/env python3
"""
Test script for Unified AI Integration
Validates Snowflake PAT authentication and Lambda Labs routing
"""

import asyncio
import logging
from datetime import datetime

from backend.core.auto_esc_config import validate_snowflake_pat
from infrastructure.services.snowflake_pat_service import SnowflakePATService
from infrastructure.services.unified_ai_orchestrator import (
    AIRequest,
    UnifiedAIOrchestrator,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def test_snowflake_pat_connection():
    """Test Snowflake PAT authentication"""
    logger.info("=" * 60)
    logger.info("Testing Snowflake PAT Authentication")
    logger.info("=" * 60)

    # Validate PAT token format
    pat_valid = validate_snowflake_pat()
    logger.info(f"PAT Token Format Valid: {pat_valid}")

    # Test connection
    service = SnowflakePATService()
    connection_result = await service.test_connection()

    logger.info(f"Connection Status: {connection_result['connected']}")
    logger.info(f"Authentication Type: {connection_result['authentication']}")

    if connection_result["connected"]:
        logger.info("Session Info:")
        for key, value in connection_result["session_info"].items():
            logger.info(f"  {key}: {value}")
    else:
        logger.error(f"Connection Error: {connection_result.get('error')}")

    await service.close()

    return connection_result["connected"]


async def test_unified_ai_routing():
    """Test unified AI orchestrator routing"""
    logger.info("\n" + "=" * 60)
    logger.info("Testing Unified AI Orchestrator")
    logger.info("=" * 60)

    orchestrator = UnifiedAIOrchestrator()

    # Test health check
    logger.info("\n1. Health Check:")
    health = await orchestrator.health_check()
    logger.info(f"Overall Status: {health['orchestrator']}")
    for provider, status in health["providers"].items():
        logger.info(f"  {provider}: {status['status']}")

    # Test different routing scenarios
    test_cases = [
        {
            "name": "SQL Generation (Should route to Snowflake)",
            "request": AIRequest(
                prompt="Generate SQL to find top 10 customers by revenue",
                use_case="sql",
            ),
        },
        {
            "name": "Complex Reasoning (Should route to Lambda)",
            "request": AIRequest(
                prompt="Analyze the strategic implications of market trends",
                use_case="reasoning",
                cost_priority="performance",
            ),
        },
        {
            "name": "Cost-Optimized Simple Query (Auto routing)",
            "request": AIRequest(
                prompt="What is the weather today?", cost_priority="cost"
            ),
        },
        {
            "name": "Data Analytics (Should route to Snowflake)",
            "request": AIRequest(
                prompt="Analyze sales data from last quarter", use_case="data_analysis"
            ),
        },
    ]

    logger.info("\n2. Routing Tests:")
    for i, test in enumerate(test_cases, 1):
        logger.info(f"\n  Test {i}: {test['name']}")

        try:
            response = await orchestrator.process_request(test["request"])

            logger.info(f"    Provider: {response.provider}")
            logger.info(f"    Model: {response.model}")
            logger.info(f"    Duration: {response.duration:.2f}s")
            logger.info(f"    Cost Estimate: ${response.cost_estimate:.6f}")
            logger.info(f"    Success: {response.success}")

            if response.success:
                logger.info(f"    Response Preview: {response.response[:100]}...")
            else:
                logger.error(f"    Error: {response.error}")

        except Exception as e:
            logger.error(f"    Test failed: {e!s}")

    # Test natural language optimization
    logger.info("\n3. Natural Language Optimization Test:")
    optimization_result = await orchestrator.natural_language_optimization(
        "Optimize costs while maintaining performance for AI operations"
    )
    logger.info("  Command processed successfully")
    logger.info(f"  Provider used: {optimization_result['provider_used']}")

    # Get usage analytics
    logger.info("\n4. Usage Analytics:")
    analytics = await orchestrator.get_usage_analytics()
    logger.info(f"  Total Requests: {analytics['total_requests']}")

    if analytics["total_requests"] > 0:
        logger.info(f"  Cost Savings: {analytics['cost_savings']['percentage']:.1f}%")
        logger.info(
            f"  Monthly Savings: ${analytics['cost_savings']['monthly_savings']:.2f}"
        )

        logger.info("  Routing Distribution:")
        for provider, percentage in analytics["routing_distribution"].items():
            logger.info(f"    {provider}: {percentage:.1%}")

    # Get performance summary
    logger.info("\n5. Performance Summary:")
    performance = orchestrator.get_performance_summary()
    for provider, metrics in performance.items():
        logger.info(f"  {provider}:")
        logger.info(f"    Requests: {metrics['total_requests']}")
        logger.info(f"    Avg Duration: {metrics['avg_duration']:.2f}s")
        logger.info(f"    Avg Cost: ${metrics['avg_cost_per_request']:.6f}")
        logger.info(f"    Success Rate: {metrics['success_rate']:.1%}")


async def test_cost_comparison():
    """Test and display cost comparison"""
    logger.info("\n" + "=" * 60)
    logger.info("Cost Comparison Analysis")
    logger.info("=" * 60)

    # Current GPU baseline
    gpu_monthly_cost = 6444

    # Projected serverless costs
    serverless_low = 450
    serverless_high = 900

    # Calculate savings
    savings_low = gpu_monthly_cost - serverless_high
    savings_high = gpu_monthly_cost - serverless_low

    savings_pct_low = (savings_low / gpu_monthly_cost) * 100
    savings_pct_high = (savings_high / gpu_monthly_cost) * 100

    logger.info(f"Current GPU Infrastructure: ${gpu_monthly_cost}/month")
    logger.info(
        f"Projected Serverless Cost: ${serverless_low}-${serverless_high}/month"
    )
    logger.info(f"Monthly Savings: ${savings_low}-${savings_high}")
    logger.info(f"Savings Percentage: {savings_pct_low:.1f}%-{savings_pct_high:.1f}%")
    logger.info(f"Annual Savings: ${savings_low * 12:,}-${savings_high * 12:,}")


async def main():
    """Run all tests"""
    logger.info("Starting Unified AI Integration Tests")
    logger.info(f"Timestamp: {datetime.now().isoformat()}")

    # Test Snowflake PAT
    snowflake_ok = await test_snowflake_pat_connection()

    if not snowflake_ok:
        logger.warning("Snowflake PAT connection failed - some tests may not work")

    # Test unified AI routing
    await test_unified_ai_routing()

    # Show cost comparison
    await test_cost_comparison()

    logger.info("\n" + "=" * 60)
    logger.info("Test Suite Complete")
    logger.info("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
