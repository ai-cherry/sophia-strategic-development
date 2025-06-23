"""Health check for the AI Memory MCP server."""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime

import aiohttp

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def check_ai_memory_health() -> bool:
    """Check the health of the AI Memory MCP server."""
    logger.info("🧠 Checking AI Memory MCP server health...")
    gateway_url = os.getenv("MCP_GATEWAY_URL", "http://localhost:8090")
    try:
        async with aiohttp.ClientSession() as session:
            logger.info("Checking MCP Gateway registration...")
            async with session.get(f"{gateway_url}/servers") as response:
                if response.status != 200:
                    logger.error(f"Failed to get servers from gateway: {response.status}")
                    return False
                servers = await response.json()
                if "ai_memory" not in servers:
                    logger.error("AI Memory MCP server not registered with gateway")
                    return False
                logger.info("✅ AI Memory MCP server registered with gateway")

            logger.info("Checking AI Memory MCP server health...")
            async with session.get(f"{gateway_url}/servers/ai_memory/health") as response:
                if response.status != 200:
                    logger.error(f"Failed to get server health: {response.status}")
                    return False
                health = await response.json()
                logger.info("AI Memory MCP server health: %s", json.dumps(health, indent=2))
                if health.get("status") != "operational":
                    logger.warning("AI Memory MCP server not operational: %s", health.get("status"))
                    return False
                logger.info("✅ AI Memory MCP server operational")

            logger.info("Testing store_conversation tool...")
            test_content = f"Test memory created at {datetime.now().isoformat()}"
            store_payload = {
                "tool": "store_conversation",
                "parameters": {
                    "content": test_content,
                    "category": "workflow",
                    "tags": ["test", "health_check"],
                },
            }
            async with session.post(f"{gateway_url}/servers/ai_memory/tools", json=store_payload) as response:
                if response.status != 200:
                    logger.error(f"Failed to store conversation: {response.status}")
                    return False
                result = await response.json()
                if "id" not in result or result.get("status") != "stored":
                    logger.error("Failed to store conversation: %s", result)
                    return False
                memory_id = result["id"]
                logger.info("✅ Successfully stored test memory with ID: %s", memory_id)

            logger.info("Testing recall_memory tool...")
            recall_payload = {
                "tool": "recall_memory",
                "parameters": {
                    "query": "test health_check",
                    "category": "workflow",
                    "limit": 1,
                },
            }
            async with session.post(f"{gateway_url}/servers/ai_memory/tools", json=recall_payload) as response:
                if response.status != 200:
                    logger.error(f"Failed to recall memory: {response.status}")
                    return False
                result = await response.json()
                if "results" not in result or not result["results"]:
                    logger.error("Failed to recall memory: %s", result)
                    return False
                logger.info("✅ Successfully recalled test memory")
            logger.info("🎉 AI Memory MCP server health check passed!")
            return True
    except Exception as exc:
        logger.error("Error checking AI Memory MCP server health: %s", str(exc))
        return False


if __name__ == "__main__":
    result = asyncio.run(check_ai_memory_health())
    sys.exit(0 if result else 1)
