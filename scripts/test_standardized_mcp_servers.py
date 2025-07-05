#!/usr/bin/env python3
"""
Test script for StandardizedMCPServer implementations
Tests health checks, metrics, and basic functionality
"""

import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import aiohttp

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from backend.utils.custom_logger import setup_logger

logger = setup_logger("mcp_test")


class MCPServerTester:
    """Test harness for StandardizedMCPServer implementations"""

    def __init__(self):
        self.servers = [
            {"name": "linear", "port": 9004, "health_endpoint": "/health"},
            {"name": "asana", "port": 9012, "health_endpoint": "/health"},
            {"name": "github", "port": 9003, "health_endpoint": "/health"},
            {"name": "hubspot", "port": 9006, "health_endpoint": "/health"},
        ]
        self.results = []

    async def test_health_endpoint(self, server: dict[str, Any]) -> dict[str, Any]:
        """Test server health endpoint"""
        url = f"http://localhost:{server['port']}{server['health_endpoint']}"

        try:
            async with aiohttp.ClientSession() as session, session.get(
                url, timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "server": server["name"],
                        "status": "healthy",
                        "response_time_ms": data.get("latency_ms", 0),
                        "details": data,
                    }
                else:
                    return {
                        "server": server["name"],
                        "status": "unhealthy",
                        "error": f"HTTP {response.status}",
                    }
        except TimeoutError:
            return {
                "server": server["name"],
                "status": "timeout",
                "error": "Request timed out",
            }
        except Exception as e:
            return {"server": server["name"], "status": "error", "error": str(e)}

    async def test_metrics_endpoint(self, server: dict[str, Any]) -> dict[str, Any]:
        """Test server metrics endpoint"""
        url = f"http://localhost:{server['port']}/metrics"

        try:
            async with aiohttp.ClientSession() as session, session.get(
                url, timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                if response.status == 200:
                    text = await response.text()
                    # Parse Prometheus metrics
                    metrics = {}
                    for line in text.split("\n"):
                        if line and not line.startswith("#"):
                            parts = line.split(" ")
                            if len(parts) == 2:
                                metrics[parts[0]] = float(parts[1])

                    return {
                        "server": server["name"],
                        "status": "success",
                        "metrics": metrics,
                    }
                else:
                    return {
                        "server": server["name"],
                        "status": "failed",
                        "error": f"HTTP {response.status}",
                    }
        except Exception as e:
            return {"server": server["name"], "status": "error", "error": str(e)}

    async def test_tools_endpoint(self, server: dict[str, Any]) -> dict[str, Any]:
        """Test MCP tools listing endpoint"""
        url = f"http://localhost:{server['port']}/tools/list"

        try:
            async with aiohttp.ClientSession() as session, session.post(
                url, json={}, timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "server": server["name"],
                        "status": "success",
                        "tools": data.get("tools", []),
                    }
                else:
                    return {
                        "server": server["name"],
                        "status": "failed",
                        "error": f"HTTP {response.status}",
                    }
        except Exception as e:
            return {"server": server["name"], "status": "error", "error": str(e)}

    async def run_all_tests(self):
        """Run all tests for all servers"""
        logger.info("🧪 Starting StandardizedMCPServer tests...")

        for server in self.servers:
            logger.info(f"\n📍 Testing {server['name']} server on port {server['port']}")

            # Test health endpoint
            health_result = await self.test_health_endpoint(server)
            logger.info(f"  Health: {health_result['status']}")
            if health_result["status"] == "healthy":
                logger.info(
                    f"    Response time: {health_result.get('response_time_ms', 'N/A')}ms"
                )
            else:
                logger.warning(f"    Error: {health_result.get('error', 'Unknown')}")

            # Test metrics endpoint
            metrics_result = await self.test_metrics_endpoint(server)
            logger.info(f"  Metrics: {metrics_result['status']}")
            if metrics_result["status"] == "success":
                metrics = metrics_result.get("metrics", {})
                logger.info(
                    f"    Total requests: {metrics.get('mcp_requests_total', 0)}"
                )
                logger.info(
                    f"    Active connections: {metrics.get('mcp_active_connections', 0)}"
                )

            # Test tools endpoint
            tools_result = await self.test_tools_endpoint(server)
            logger.info(f"  Tools: {tools_result['status']}")
            if tools_result["status"] == "success":
                tools = tools_result.get("tools", [])
                logger.info(f"    Available tools: {len(tools)}")
                for tool in tools[:3]:  # Show first 3 tools
                    logger.info(f"      - {tool.get('name', 'Unknown')}")

            # Store results
            self.results.append(
                {
                    "server": server["name"],
                    "health": health_result,
                    "metrics": metrics_result,
                    "tools": tools_result,
                    "timestamp": datetime.now().isoformat(),
                }
            )

        # Summary
        self.print_summary()

    def print_summary(self):
        """Print test summary"""
        logger.info("\n" + "=" * 60)
        logger.info("📊 TEST SUMMARY")
        logger.info("=" * 60)

        healthy_servers = sum(
            1 for r in self.results if r["health"]["status"] == "healthy"
        )
        total_servers = len(self.results)

        logger.info(f"Total servers tested: {total_servers}")
        logger.info(f"Healthy servers: {healthy_servers}")
        logger.info(f"Success rate: {(healthy_servers/total_servers*100):.1f}%")

        logger.info("\nServer Status:")
        for result in self.results:
            status_icon = "✅" if result["health"]["status"] == "healthy" else "❌"
            logger.info(
                f"  {status_icon} {result['server']}: {result['health']['status']}"
            )

        # Save results to file
        with open("mcp_server_test_results.json", "w") as f:
            json.dump(self.results, f, indent=2)
        logger.info("\nDetailed results saved to: mcp_server_test_results.json")


async def main():
    """Main entry point"""
    tester = MCPServerTester()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
