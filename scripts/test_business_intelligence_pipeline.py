#!/usr/bin/env python3
"""Run the business intelligence portion of the comprehensive integration test."""
import asyncio
from scripts.test_agno_arize_integration import ComprehensiveIntegrationTest

async def main() -> None:
    test_suite = ComprehensiveIntegrationTest()
    await test_suite.test_business_intelligence()

if __name__ == "__main__":
    asyncio.run(main())
