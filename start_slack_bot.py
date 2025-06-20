#!/usr/bin/env python3
"""Slack Bot Launcher
Starts the Sophia Slack bot with proper configuration
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.integrations.slack.sophia_slack_bot import sophia_slack_bot

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def main():
    """Main entry point for Slack bot"""
    try:
        # Check required environment variables
        required_vars = ["SLACK_BOT_TOKEN", "SLACK_APP_TOKEN", "SLACK_SIGNING_SECRET"]

        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            logger.error(f"Missing required environment variables: {missing_vars}")
            logger.error("Please set the following environment variables:")
            for var in missing_vars:
                logger.error(f"  export {var}=your_value_here")
            return

        logger.info("Starting Sophia Slack Bot...")
        await sophia_slack_bot.start()

    except KeyboardInterrupt:
        logger.info("Received interrupt signal, shutting down...")
        await sophia_slack_bot.stop()
    except Exception as e:
        logger.error(f"Error starting Slack bot: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
