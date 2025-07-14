#!/usr/bin/env python3
"""
Start Essential Project Management MCP Servers
"""
import asyncio
import logging
import os
import subprocess

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProjectMCPManager:
    def __init__(self):
        self.servers = {
            "asana": {
                "path": "mcp-servers/asana/asana_mcp_server.py",
                "port": 9004,
                "priority": 1,
            },
            "linear": {
                "path": "mcp-servers/linear/linear_mcp_server.py",
                "port": 9006,
                "priority": 1,
            },
            "notion": {
                "path": "mcp-servers/notion/enhanced_notion_mcp_server.py",
                "port": 9005,
                "priority": 1,
            },
            "slack_unified": {
                "path": "mcp-servers/slack_unified/simple_slack_integration_server.py",
                "port": 9008,
                "priority": 2,
            },
            "ai_memory": {
                "path": "mcp-servers/ai_memory/enhanced_ai_memory_mcp_server.py",
                "port": 9000,
                "priority": 3,
            },
        }
        self.processes = {}

    async def start_server(self, name: str, config: dict) -> bool:
        """Start individual MCP server"""
        try:
            # Check if file exists
            if not os.path.exists(config["path"]):
                logger.error(f"❌ {name} server file not found: {config['path']}")
                return False

            cmd = ["python3", config["path"]]

            # Set environment variables
            env = os.environ.copy()
            env.update(
                {
                    "PORT": str(config["port"]),
                    "ENVIRONMENT": "prod",
                    "PULUMI_ORG": "scoobyjava-org",
                }
            )

            logger.info(f"🚀 Starting {name} on port {config['port']}")

            process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env
            )

            # Wait for startup
            await asyncio.sleep(3)

            # Check if process is still running
            if process.poll() is None:
                self.processes[name] = process
                logger.info(f"✅ {name} started successfully (PID: {process.pid})")
                return True
            else:
                stdout, stderr = process.communicate()
                logger.error(f"❌ {name} failed to start")
                if stderr:
                    logger.error(f"   Error: {stderr[:200]}")
                if stdout:
                    logger.info(f"   Output: {stdout[:200]}")
                return False

        except Exception as e:
            logger.error(f"❌ Failed to start {name}: {e}")
            return False

    async def start_all(self):
        """Start all servers in priority order"""
        # Sort by priority
        sorted_servers = sorted(self.servers.items(), key=lambda x: x[1]["priority"])

        started_count = 0
        total_count = len(self.servers)

        logger.info(f"🎯 Starting {total_count} Project Management MCP Servers")

        for name, config in sorted_servers:
            if await self.start_server(name, config):
                started_count += 1

            # Small delay between starts
            await asyncio.sleep(2)

        logger.info(f"📊 Started {started_count}/{total_count} servers")
        return started_count

    async def health_check(self):
        """Check health of all running servers"""
        import aiohttp

        results = {}
        async with aiohttp.ClientSession() as session:
            for name, config in self.servers.items():
                try:
                    url = f"http://localhost:{config['port']}/health"
                    async with session.get(url, timeout=3) as response:
                        if response.status == 200:
                            data = await response.json()
                            results[name] = {"status": "healthy", "data": data}
                        else:
                            results[name] = {
                                "status": "unhealthy",
                                "error": f"HTTP {response.status}",
                            }
                except Exception as e:
                    results[name] = {"status": "offline", "error": str(e)[:50]}

        return results

    def stop_all(self):
        """Stop all running servers"""
        logger.info("🛑 Stopping all MCP servers...")

        for name, process in self.processes.items():
            try:
                if process.poll() is None:
                    logger.info(f"   Stopping {name} (PID: {process.pid})")
                    process.terminate()

                    # Wait up to 5 seconds for graceful shutdown
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        logger.warning(f"   Force killing {name}")
                        process.kill()
                        process.wait()

            except Exception as e:
                logger.error(f"   Failed to stop {name}: {e}")

        self.processes.clear()
        logger.info("✅ All servers stopped")


async def main():
    manager = ProjectMCPManager()

    try:
        logger.info("🎯 Starting Project Management MCP Servers")
        started = await manager.start_all()

        if started > 0:
            logger.info("⏳ Waiting 10 seconds for full initialization...")
            await asyncio.sleep(10)

            logger.info("🔍 Running health checks...")
            health = await manager.health_check()

            healthy_count = sum(1 for r in health.values() if r["status"] == "healthy")
            logger.info(
                f"📊 Health Check: {healthy_count}/{len(health)} servers healthy"
            )

            for name, result in health.items():
                status_emoji = "✅" if result["status"] == "healthy" else "❌"
                logger.info(f"{status_emoji} {name}: {result['status']}")

                if result["status"] == "healthy" and "data" in result:
                    data = result["data"]
                    if "port" in data:
                        logger.info(f"   Port: {data['port']}")

            if healthy_count > 0:
                logger.info(
                    "\n🎉 MCP servers are running! Press Ctrl+C to stop all servers."
                )

                # Keep running until interrupted
                try:
                    while True:
                        await asyncio.sleep(30)

                        # Quick health check every 30 seconds
                        health = await manager.health_check()
                        healthy_now = sum(
                            1 for r in health.values() if r["status"] == "healthy"
                        )

                        if healthy_now != healthy_count:
                            logger.info(
                                f"📊 Health status changed: {healthy_now}/{len(health)} servers healthy"
                            )
                            healthy_count = healthy_now

                except KeyboardInterrupt:
                    logger.info("\n🛑 Shutdown requested")
            else:
                logger.error("❌ No servers started successfully")
        else:
            logger.error("❌ Failed to start any servers")

    except KeyboardInterrupt:
        logger.info("\n🛑 Shutdown requested")
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
    finally:
        manager.stop_all()


if __name__ == "__main__":
    asyncio.run(main())
