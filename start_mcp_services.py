#!/usr/bin/env python3
"""
Sophia AI MCP Services Startup Script
Starts all MCP servers in the correct order
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from mcp_servers.github.github_mcp_server import github_server
from mcp_servers.hubspot.hubspot_mcp_server import hubspot_server
from mcp_servers.notion.notion_mcp_server import notion_server
from mcp_servers.slack.slack_mcp_server import slack_server
from mcp_servers.snowflake.snowflake_mcp_server import snowflake_server

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def start_all_services():
    """Start all MCP services"""
    logger.info("🚀 Starting Sophia AI MCP Services")

    services = [
        ("Snowflake", snowflake_server),
        ("HubSpot", hubspot_server),
        ("Slack", slack_server),
        ("GitHub", github_server),
        ("Notion", notion_server),
    ]

    for name, server in services:
        try:
            await server.start()
        except Exception as e:
            logger.exception(f"❌ Failed to start {name}: {e}")

    logger.info("✅ All MCP services started")

    # Keep running
    try:
        while True:
            await asyncio.sleep(60)
    except KeyboardInterrupt:
        logger.info("🛑 Shutting down services...")

        for name, server in services:
            try:
                await server.stop()
            except Exception as e:
                logger.exception(f"❌ Failed to stop {name}: {e}")


if __name__ == "__main__":
    asyncio.run(start_all_services())
