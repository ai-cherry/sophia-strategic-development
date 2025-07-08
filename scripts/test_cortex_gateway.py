#!/usr/bin/env python3
"""
Test script to verify CortexGateway functionality.
Tests basic operations and ensures the gateway is working correctly.
"""

import asyncio
import json
import logging
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.infra.cortex_gateway import get_gateway
from infrastructure.adapters.enhanced_snowflake_adapter import get_adapter

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


async def test_gateway_health():
    """Test gateway health check"""
    logger.info("🔍 Testing gateway health check...")

    gateway = get_gateway()
    health = await gateway.health_check()

    logger.info(f"Health status: {health['status']}")
    if health.get("details"):
        logger.info(f"Details: {json.dumps(health['details'], indent=2)}")

    return health["status"] == "healthy"


async def test_sql_execution():
    """Test basic SQL execution"""
    logger.info("🔍 Testing SQL execution...")

    gateway = get_gateway()

    # Simple query to test connection
    query = "SELECT CURRENT_TIMESTAMP() as timestamp, CURRENT_USER() as user, CURRENT_DATABASE() as database"

    try:
        result = await gateway.execute_sql(query)
        logger.info("✅ SQL execution successful")
        logger.info(f"Result: {json.dumps(result, indent=2, default=str)}")
        return True
    except Exception as e:
        logger.error(f"❌ SQL execution failed: {e}")
        return False


async def test_cortex_complete():
    """Test Cortex COMPLETE function"""
    logger.info("🔍 Testing Cortex COMPLETE function...")

    gateway = get_gateway()

    prompt = "What is Snowflake Cortex? Provide a brief explanation in one sentence."

    try:
        result = await gateway.complete(prompt, model="mixtral-8x7b")
        logger.info("✅ Cortex COMPLETE successful")
        logger.info(f"Response: {result}")
        return True
    except Exception as e:
        logger.error(f"❌ Cortex COMPLETE failed: {e}")
        return False


async def test_cortex_embed():
    """Test Cortex embedding function"""
    logger.info("🔍 Testing Cortex embedding function...")

    gateway = get_gateway()

    text = "Snowflake Cortex provides AI capabilities within the data cloud."

    try:
        embedding = await gateway.embed(text)
        logger.info("✅ Cortex embedding successful")
        logger.info(f"Embedding dimensions: {len(embedding)}")
        logger.info(f"First 5 values: {embedding[:5]}")
        return True
    except Exception as e:
        logger.error(f"❌ Cortex embedding failed: {e}")
        return False


async def test_cortex_sentiment():
    """Test Cortex sentiment analysis"""
    logger.info("🔍 Testing Cortex sentiment analysis...")

    gateway = get_gateway()

    texts = [
        "I love using Snowflake for data analytics!",
        "The performance is terrible and costs too much.",
        "It's an okay platform with some good features.",
    ]

    try:
        for text in texts:
            sentiment = await gateway.sentiment(text)
            logger.info(f"Text: '{text}'")
            logger.info(f"Sentiment: {sentiment}")

        logger.info("✅ Cortex sentiment analysis successful")
        return True
    except Exception as e:
        logger.error(f"❌ Cortex sentiment analysis failed: {e}")
        return False


async def test_adapter_credit_usage():
    """Test adapter credit usage tracking"""
    logger.info("🔍 Testing credit usage tracking...")

    adapter = get_adapter()
    await adapter.initialize()

    try:
        usage = await adapter.get_credit_usage_summary()
        logger.info("✅ Credit usage tracking successful")
        logger.info(f"Daily limit: {usage['daily_limit']} credits")
        logger.info(f"Credits used: {usage['credits_used']:.2f}")
        logger.info(f"Credits remaining: {usage['credits_remaining']:.2f}")
        logger.info(f"Usage: {usage['usage_percentage']:.1f}%")
        return True
    except Exception as e:
        logger.error(f"❌ Credit usage tracking failed: {e}")
        return False


async def test_warehouse_optimization():
    """Test warehouse optimization recommendations"""
    logger.info("🔍 Testing warehouse optimization...")

    adapter = get_adapter()
    await adapter.initialize()

    try:
        optimization = await adapter.optimize_warehouse_usage()
        logger.info("✅ Warehouse optimization analysis successful")
        logger.info(f"Recommendations: {len(optimization['recommendations'])}")

        if optimization["recommendations"]:
            for rec in optimization["recommendations"][:3]:
                logger.info(f"  - {rec}")

        return True
    except Exception as e:
        logger.error(f"❌ Warehouse optimization failed: {e}")
        return False


async def run_all_tests():
    """Run all tests"""
    logger.info("🚀 Starting CortexGateway tests...")
    logger.info("=" * 60)

    tests = [
        ("Gateway Health", test_gateway_health),
        ("SQL Execution", test_sql_execution),
        ("Cortex COMPLETE", test_cortex_complete),
        ("Cortex Embeddings", test_cortex_embed),
        ("Cortex Sentiment", test_cortex_sentiment),
        ("Credit Usage", test_adapter_credit_usage),
        ("Warehouse Optimization", test_warehouse_optimization),
    ]

    results = {}

    for test_name, test_func in tests:
        logger.info(f"\n📋 Running test: {test_name}")
        logger.info("-" * 40)

        try:
            success = await test_func()
            results[test_name] = "PASSED" if success else "FAILED"
        except Exception as e:
            logger.error(f"Test crashed: {e}")
            results[test_name] = "ERROR"

        logger.info("")

    # Summary
    logger.info("=" * 60)
    logger.info("📊 Test Summary:")
    logger.info("-" * 40)

    passed = sum(1 for r in results.values() if r == "PASSED")
    total = len(results)

    for test_name, result in results.items():
        emoji = "✅" if result == "PASSED" else "❌"
        logger.info(f"{emoji} {test_name}: {result}")

    logger.info("-" * 40)
    logger.info(f"Total: {passed}/{total} tests passed ({passed/total*100:.0f}%)")

    return passed == total


async def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Test CortexGateway functionality")
    parser.add_argument(
        "--test",
        help="Run specific test",
        choices=[
            "health",
            "sql",
            "complete",
            "embed",
            "sentiment",
            "credit",
            "optimize",
        ],
    )
    args = parser.parse_args()

    if args.test:
        # Run specific test
        test_map = {
            "health": test_gateway_health,
            "sql": test_sql_execution,
            "complete": test_cortex_complete,
            "embed": test_cortex_embed,
            "sentiment": test_cortex_sentiment,
            "credit": test_adapter_credit_usage,
            "optimize": test_warehouse_optimization,
        }

        test_func = test_map[args.test]
        success = await test_func()
        sys.exit(0 if success else 1)
    else:
        # Run all tests
        success = await run_all_tests()
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
