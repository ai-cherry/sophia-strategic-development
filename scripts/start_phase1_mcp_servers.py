#!/usr/bin/env python3
"""
Start Phase 1 MCP Servers Script
Starts critical Phase 1 target servers with proper error handling and monitoring
"""

import asyncio
import logging
import os
import subprocess
import sys
import time
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class Phase1MCPServerStarter:
    def __init__(self):
        self.root_path = Path(__file__).parent.parent
        self.mcp_servers_path = self.root_path / "mcp-servers"

        # Phase 1 target servers in startup order (most critical first)
        self.phase1_servers = [
            {"name": "ai_memory", "port": 9000, "priority": 1, "critical": True},
            {"name": "lambda_labs_cli", "port": 9020, "priority": 1, "critical": True},
            {"name": "ui_ux_agent", "port": 9002, "priority": 2, "critical": True},
            {"name": "codacy", "port": 3008, "priority": 2, "critical": True},
            {"name": "portkey_admin", "port": 9013, "priority": 3, "critical": False},
            {"name": "snowflake_cli_enhanced", "port": 9021, "priority": 3, "critical": False},
            {"name": "ag_ui", "port": 9004, "priority": 4, "critical": False},
            {"name": "snowflake_admin", "port": 9022, "priority": 4, "critical": False},
        ]

        self.running_servers = {}
        self.failed_servers = {}

    async def start_all_phase1_servers(self) -> dict:
        """Start all Phase 1 MCP servers with proper error handling"""
        logger.info("🚀 Starting Phase 1 MCP Server Recovery...")

        results = {
            "started_servers": [],
            "failed_servers": [],
            "already_running": [],
            "health_checks": {},
            "total_started": 0,
            "critical_success": False
        }

        # Group servers by priority
        servers_by_priority = {}
        for server in self.phase1_servers:
            priority = server["priority"]
            if priority not in servers_by_priority:
                servers_by_priority[priority] = []
            servers_by_priority[priority].append(server)

        # Start servers in priority order
        for priority in sorted(servers_by_priority.keys()):
            logger.info(f"🔄 Starting Priority {priority} servers...")

            priority_servers = servers_by_priority[priority]
            priority_results = await self.start_priority_group(priority_servers)

            # Update results
            results["started_servers"].extend(priority_results["started"])
            results["failed_servers"].extend(priority_results["failed"])
            results["already_running"].extend(priority_results["already_running"])
            results["health_checks"].update(priority_results["health_checks"])

            # Short delay between priority groups
            if priority < max(servers_by_priority.keys()):
                await asyncio.sleep(2)

        # Calculate success metrics
        results["total_started"] = len(results["started_servers"])
        critical_servers = [s for s in self.phase1_servers if s["critical"]]
        critical_started = len([s for s in results["started_servers"] if any(cs["name"] == s for cs in critical_servers)])
        results["critical_success"] = critical_started >= len(critical_servers) * 0.75  # 75% success rate

        # Generate summary
        await self.generate_startup_summary(results)

        return results

    async def start_priority_group(self, servers: list[dict]) -> dict:
        """Start a group of servers with the same priority"""
        results = {
            "started": [],
            "failed": [],
            "already_running": [],
            "health_checks": {}
        }

        # Start servers in parallel within the same priority group
        startup_tasks = []
        for server in servers:
            task = asyncio.create_task(self.start_single_server(server))
            startup_tasks.append((server["name"], task))

        # Wait for all servers in this priority group
        for server_name, task in startup_tasks:
            try:
                result = await task
                if result["status"] == "started":
                    results["started"].append(server_name)
                elif result["status"] == "already_running":
                    results["already_running"].append(server_name)
                elif result["status"] == "failed":
                    results["failed"].append(f"{server_name}: {result['error']}")

                results["health_checks"][server_name] = result.get("health_check", {})

            except Exception as e:
                error_msg = f"Exception starting {server_name}: {e}"
                results["failed"].append(error_msg)
                logger.error(f"❌ {error_msg}")

        return results

    async def start_single_server(self, server: dict) -> dict:
        """Start a single MCP server"""
        server_name = server["name"]
        port = server["port"]

        logger.info(f"🔄 Starting {server_name} on port {port}...")

        # Check if already running
        if await self.check_server_running(port):
            logger.info(f"✅ {server_name} already running on port {port}")
            health_check = await self.perform_health_check(port)
            return {
                "status": "already_running",
                "health_check": health_check
            }

        # Find server file
        server_file = self.find_server_file(server_name)
        if not server_file:
            error_msg = f"Server file not found for {server_name}"
            logger.error(f"❌ {error_msg}")
            return {
                "status": "failed",
                "error": error_msg
            }

        # Start the server
        try:
            # Environment setup
            env = os.environ.copy()
            env["ENVIRONMENT"] = "prod"
            env["PULUMI_ORG"] = "scoobyjava-org"

            # Start server process
            cmd = [sys.executable, str(server_file)]
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
                cwd=str(server_file.parent)
            )

            # Wait a moment for startup
            await asyncio.sleep(3)

            # Check if process is still running
            if process.poll() is not None:
                # Process died, get error
                stdout, stderr = process.communicate()
                error_msg = f"Process died: {stderr.decode()}"
                logger.error(f"❌ {server_name}: {error_msg}")
                return {
                    "status": "failed",
                    "error": error_msg
                }

            # Check if server is responding
            if await self.check_server_running(port):
                logger.info(f"✅ {server_name} started successfully on port {port}")
                health_check = await self.perform_health_check(port)
                self.running_servers[server_name] = {
                    "process": process,
                    "port": port,
                    "started_at": time.time()
                }
                return {
                    "status": "started",
                    "health_check": health_check
                }
            else:
                # Server not responding
                process.terminate()
                error_msg = f"Server not responding on port {port}"
                logger.error(f"❌ {server_name}: {error_msg}")
                return {
                    "status": "failed",
                    "error": error_msg
                }

        except Exception as e:
            error_msg = f"Failed to start: {e}"
            logger.error(f"❌ {server_name}: {error_msg}")
            return {
                "status": "failed",
                "error": error_msg
            }

    async def check_server_running(self, port: int) -> bool:
        """Check if a server is running on the specified port"""
        try:
            import aiohttp
            timeout = aiohttp.ClientTimeout(total=5)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(f"http://localhost:{port}/health") as response:
                    return response.status == 200
        except:
            return False

    async def perform_health_check(self, port: int) -> dict:
        """Perform detailed health check on a server"""
        try:
            import aiohttp
            timeout = aiohttp.ClientTimeout(total=10)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                start_time = time.time()
                async with session.get(f"http://localhost:{port}/health") as response:
                    response_time = (time.time() - start_time) * 1000
                    if response.status == 200:
                        health_data = await response.json()
                        return {
                            "status": "healthy",
                            "response_time_ms": response_time,
                            "details": health_data
                        }
                    else:
                        return {
                            "status": "unhealthy",
                            "response_time_ms": response_time,
                            "error": f"HTTP {response.status}"
                        }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

    def find_server_file(self, server_name: str) -> Path | None:
        """Find the main server file for a given server"""
        server_path = self.mcp_servers_path / server_name
        if not server_path.exists():
            return None

        # Possible server file names
        possible_names = [
            f"{server_name}_mcp_server.py",
            "mcp_server.py",
            "server.py",
            "main.py"
        ]

        for name in possible_names:
            file_path = server_path / name
            if file_path.exists():
                return file_path

        # Look for any Python file
        python_files = list(server_path.glob("*.py"))
        if python_files:
            return python_files[0]

        return None

    async def generate_startup_summary(self, results: dict) -> None:
        """Generate comprehensive startup summary"""
        logger.info(f"\n{'='*60}")
        logger.info("🚀 PHASE 1 MCP SERVER STARTUP SUMMARY")
        logger.info(f"{'='*60}")

        total_servers = len(self.phase1_servers)
        started = len(results["started_servers"])
        already_running = len(results["already_running"])
        failed = len(results["failed_servers"])
        operational = started + already_running

        logger.info("\n📊 OVERVIEW:")
        logger.info(f"   Total Phase 1 servers: {total_servers}")
        logger.info(f"   ✅ Operational: {operational} ({operational/total_servers*100:.1f}%)")
        logger.info(f"   🔄 Started this session: {started}")
        logger.info(f"   ✅ Already running: {already_running}")
        logger.info(f"   ❌ Failed: {failed}")

        if results["started_servers"]:
            logger.info(f"\n🚀 STARTED SERVERS ({len(results['started_servers'])}):")
            for server in results["started_servers"]:
                logger.info(f"   • {server}")

        if results["already_running"]:
            logger.info(f"\n✅ ALREADY RUNNING ({len(results['already_running'])}):")
            for server in results["already_running"]:
                logger.info(f"   • {server}")

        if results["failed_servers"]:
            logger.info(f"\n❌ FAILED SERVERS ({len(results['failed_servers'])}):")
            for server in results["failed_servers"]:
                logger.info(f"   • {server}")

        # Health check summary
        healthy_servers = sum(1 for hc in results["health_checks"].values() if hc.get("status") == "healthy")
        if results["health_checks"]:
            logger.info("\n🏥 HEALTH STATUS:")
            logger.info(f"   Healthy: {healthy_servers}/{len(results['health_checks'])}")

            for server, health in results["health_checks"].items():
                status_emoji = "✅" if health.get("status") == "healthy" else "⚠️"
                response_time = health.get("response_time_ms", 0)
                logger.info(f"   {status_emoji} {server}: {health.get('status', 'unknown')} ({response_time:.1f}ms)")

        # Success assessment
        logger.info("\n🎯 PHASE 1 RECOVERY STATUS:")
        if results["critical_success"]:
            logger.info("   🎉 Critical server threshold achieved!")
            logger.info("   ✅ Ready to proceed with Phase 2")
        else:
            logger.info("   ⚠️ Critical server threshold not met")
            logger.info("   🔧 Additional remediation may be needed")

        # ROI calculation
        value_recovered = operational * 6250  # $50K / 8 servers
        logger.info("\n💰 BUSINESS IMPACT:")
        logger.info(f"   Value recovered: ${value_recovered:,}")
        logger.info(f"   Operational capacity: {operational/total_servers*100:.1f}%")

        logger.info(f"\n{'='*60}")


async def main():
    """Main execution function"""
    logger.info("🚀 Phase 1 MCP Server Starter")

    # Check environment
    env = os.getenv("ENVIRONMENT", "unknown")
    pulumi_org = os.getenv("PULUMI_ORG", "unknown")

    logger.info(f"Environment: {env}")
    logger.info(f"Pulumi Org: {pulumi_org}")

    if env != "prod":
        logger.warning("⚠️ Not in production environment!")

    if pulumi_org != "scoobyjava-org":
        logger.warning("⚠️ Pulumi org not configured!")

    # Start Phase 1 servers
    starter = Phase1MCPServerStarter()
    results = await starter.start_all_phase1_servers()

    # Final assessment
    if results["critical_success"]:
        logger.info("🎉 Phase 1 MCP Recovery: SUCCESS!")
        exit_code = 0
    else:
        logger.warning("⚠️ Phase 1 MCP Recovery: PARTIAL SUCCESS")
        exit_code = 1

    return exit_code


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
