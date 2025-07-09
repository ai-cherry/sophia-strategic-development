#!/usr/bin/env python3
"""
Start the Snowflake monitoring service with Prometheus metrics export.
This service monitors Snowflake usage, costs, and performance.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from infrastructure.monitoring.snowflake_monitoring import (
    snowflake_monitor,
    start_monitoring_service,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


async def run_initial_check():
    """Run initial monitoring check to verify setup"""
    logger.info("🔍 Running initial Snowflake monitoring check...")

    try:
        result = await snowflake_monitor.run_monitoring_cycle()

        if result:
            logger.info("✅ Initial monitoring check completed successfully")
            logger.info(
                f"   - Warehouses found: {result['summary']['total_warehouses']}"
            )
            logger.info(
                f"   - Daily credit usage: {result['summary']['daily_credits_used']:.2f}/{result['summary']['daily_credits_limit']}"
            )
            logger.info(f"   - Active alerts: {result['summary']['active_alerts']}")
            return True
        else:
            logger.warning("⚠️ Initial monitoring check returned no data")
            return False

    except Exception as e:
        logger.error(f"❌ Initial monitoring check failed: {e}")
        return False


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Start Snowflake monitoring service")
    parser.add_argument(
        "--port", type=int, default=8003, help="Prometheus metrics port (default: 8003)"
    )
    parser.add_argument(
        "--check-only", action="store_true", help="Run one check and exit"
    )
    args = parser.parse_args()

    if args.check_only:
        # Run single check
        success = asyncio.run(run_initial_check())
        sys.exit(0 if success else 1)
    else:
        # Start monitoring service
        logger.info(f"🚀 Starting Snowflake monitoring service on port {args.port}")
        logger.info(
            f"📊 Prometheus metrics will be available at http://localhost:{args.port}/metrics"
        )
        logger.info(
            "📈 Monitoring dashboard data will be saved to reports/snowflake_monitoring_latest.json"
        )
        logger.info("⏰ Monitoring cycles will run every 15 minutes")

        try:
            start_monitoring_service(port=args.port)
        except KeyboardInterrupt:
            logger.info("🛑 Monitoring service stopped by user")
        except Exception as e:
            logger.error(f"❌ Monitoring service failed: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()
