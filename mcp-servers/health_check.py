#!/usr/bin/env python3
"""
MCP Servers Health Check Aggregator
Monitors all MCP servers and provides consolidated health status
"""

import asyncio
import json
from datetime import datetime

import aiohttp


class MCPHealthMonitor:
    def __init__(self):
        self.servers = {
            "ai_memory": {"port": 9000, "url": "http://localhost:9000/health"},
            "ai_orchestrator": {"port": 9001, "url": "http://localhost:9001/health"},
            "sophia_business_intelligence": {"port": 9002, "url": "http://localhost:9002/health"},
            "sophia_data_intelligence": {"port": 9003, "url": "http://localhost:9003/health"},
            "code_intelligence": {"port": 9004, "url": "http://localhost:9004/health"},
            "sophia_ai_intelligence": {"port": 9005, "url": "http://localhost:9005/health"},
            "asana": {"port": 9100, "url": "http://localhost:9100/health"},
            "linear": {"port": 9101, "url": "http://localhost:9101/health"},
            "notion": {"port": 9102, "url": "http://localhost:9102/health"},
            "slack": {"port": 9103, "url": "http://localhost:9103/health"},
            "github": {"port": 9104, "url": "http://localhost:9104/health"},
            "bright_data": {"port": 9105, "url": "http://localhost:9105/health"},
            "ag_ui": {"port": 9106, "url": "http://localhost:9106/health"},
            "snowflake": {"port": 9200, "url": "http://localhost:9200/health"},
            "snowflake_admin": {"port": 9201, "url": "http://localhost:9201/health"},
            "postgres": {"port": 9202, "url": "http://localhost:9202/health"},
            "pulumi": {"port": 9203, "url": "http://localhost:9203/health"},
            "sophia_infrastructure": {"port": 9204, "url": "http://localhost:9204/health"},
            "docker": {"port": 9205, "url": "http://localhost:9205/health"},
            "codacy": {"port": 9300, "url": "http://localhost:9300/health"},
        }

    async def check_server_health(self, session: aiohttp.ClientSession, name: str, config: dict) -> dict:
        """Check health of individual server"""
        try:
            async with session.get(config["url"], timeout=5) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "name": name,
                        "status": "healthy",
                        "port": config["port"],
                        "response_time": data.get("response_time", 0),
                        "details": data
                    }
                else:
                    return {
                        "name": name,
                        "status": "unhealthy",
                        "port": config["port"],
                        "error": f"HTTP {response.status}"
                    }
        except Exception as e:
            return {
                "name": name,
                "status": "error",
                "port": config["port"],
                "error": str(e)
            }

    async def check_all_servers(self) -> dict:
        """Check health of all MCP servers"""
        async with aiohttp.ClientSession() as session:
            tasks = [
                self.check_server_health(session, name, config)
                for name, config in self.servers.items()
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Process results
            healthy_count = sum(1 for r in results if isinstance(r, dict) and r.get("status") == "healthy")
            total_count = len(results)

            return {
                "timestamp": datetime.now().isoformat(),
                "summary": {
                    "total_servers": total_count,
                    "healthy_servers": healthy_count,
                    "unhealthy_servers": total_count - healthy_count,
                    "health_percentage": round((healthy_count / total_count) * 100, 1) if total_count > 0 else 0
                },
                "servers": [r for r in results if isinstance(r, dict)]
            }

async def main():
    monitor = MCPHealthMonitor()
    health_status = await monitor.check_all_servers()

    print(json.dumps(health_status, indent=2))

    # Exit with error code if any servers are unhealthy
    if health_status["summary"]["unhealthy_servers"] > 0:
        exit(1)

if __name__ == "__main__":
    asyncio.run(main())
