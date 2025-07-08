#!/usr/bin/env python3
"""
MCP Server Health Monitor
Monitors all MCP servers and reports status
"""

import asyncio
import json
from datetime import datetime
from typing import Any, Dict, List

import aiohttp
from aiohttp import ClientTimeout  # Import ClientTimeout


class MCPHealthMonitor:
    def __init__(self, host: str):
        self.host = host
        self.mcp_servers = self._get_mcp_server_list()

    def _get_mcp_server_list(self) -> list[dict[str, Any]]:
        """Get list of all MCP servers with their ports"""
        return [
            {"name": "ai-memory", "port": 9001},
            {"name": "codacy", "port": 3008},
            {"name": "linear", "port": 9004},
            {"name": "github-agent", "port": 9010},
            {"name": "pulumi-agent", "port": 9011},
            {"name": "apollo", "port": 9020},
            {"name": "asana", "port": 9021},
            {"name": "figma_context", "port": 9030},
            # Add all 34 servers
        ]

    async def check_server_health(
        self, session: aiohttp.ClientSession, server: dict[str, Any]
    ) -> dict[str, Any]:  # Made async
        """Check health of individual MCP server"""
        url = f"http://{self.host}:{server['port']}/health"

        try:
            async with session.get(url, timeout=ClientTimeout(total=10)) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "name": server["name"],
                        "status": "healthy",
                        "response_time": data.get("response_time", 0),
                        "version": data.get("version", "unknown"),
                    }
                else:
                    return {
                        "name": server["name"],
                        "status": "unhealthy",
                        "error": f"HTTP {response.status}",
                    }
        except Exception as e:
            return {"name": server["name"], "status": "unreachable", "error": str(e)}

    async def monitor_all_servers(self) -> dict[str, Any]:
        """Monitor all MCP servers"""
        async with aiohttp.ClientSession() as session:
            tasks = [
                self.check_server_health(session, server) for server in self.mcp_servers
            ]

            results = await asyncio.gather(*tasks)  # tasks are now coroutines

            healthy_count = sum(1 for r in results if r["status"] == "healthy")
            total_count = len(results)

            return {
                "timestamp": datetime.utcnow().isoformat(),
                "host": self.host,
                "summary": {
                    "total_servers": total_count,
                    "healthy_servers": healthy_count,
                    "unhealthy_servers": total_count - healthy_count,
                    "health_percentage": (healthy_count / total_count) * 100,
                },
                "servers": results,
            }


async def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--host", required=True)
    parser.add_argument("--output", default="mcp-health-report.json")
    args = parser.parse_args()

    monitor = MCPHealthMonitor(args.host)
    report = await monitor.monitor_all_servers()

    with open(args.output, "w") as f:
        json.dump(report, f, indent=2)



if __name__ == "__main__":
    asyncio.run(main())
