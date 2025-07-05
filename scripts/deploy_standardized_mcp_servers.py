#!/usr/bin/env python3
"""
Deploy and manage StandardizedMCPServer implementations
Handles server startup, health monitoring, and graceful shutdown
"""

import asyncio
import signal
import subprocess
import sys
import time
from pathlib import Path

import psutil

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from backend.utils.custom_logger import setup_logger

logger = setup_logger("mcp_deploy")


class MCPServerDeployer:
    """Deploy and manage StandardizedMCPServer instances"""

    def __init__(self):
        self.servers = [
            {
                "name": "linear",
                "path": "mcp-servers/linear/linear_mcp_server.py",
                "port": 9004,
                "env": {"LINEAR_API_KEY": "demo_mode"},
            },
            {
                "name": "asana",
                "path": "mcp-servers/asana/asana_mcp_server.py",
                "port": 9012,
                "env": {"ASANA_API_TOKEN": "demo_mode"},
            },
            {
                "name": "github",
                "path": "mcp-servers/github/github_mcp_server.py",
                "port": 9003,
                "env": {"GITHUB_TOKEN": "demo_mode"},
            },
            {
                "name": "hubspot",
                "path": "mcp-servers/hubspot_unified/hubspot_mcp_server.py",
                "port": 9006,
                "env": {"HUBSPOT_API_KEY": "demo_mode"},
            },
        ]
        self.processes: dict[str, subprocess.Popen] = {}
        self.running = True

    def check_port_availability(self, port: int) -> bool:
        """Check if a port is available"""
        for conn in psutil.net_connections():
            if conn.laddr.port == port:
                return False
        return True

    def kill_process_on_port(self, port: int):
        """Kill any process using the specified port"""
        for proc in psutil.process_iter(["pid", "name"]):
            try:
                for conn in proc.connections():
                    if conn.laddr.port == port:
                        logger.warning(f"Killing process {proc.pid} using port {port}")
                        proc.kill()
                        time.sleep(1)
                        return
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

    async def start_server(self, server: dict) -> bool:
        """Start a single MCP server"""
        try:
            # Check port availability
            if not self.check_port_availability(server["port"]):
                logger.warning(
                    f"Port {server['port']} is in use, attempting to free it..."
                )
                self.kill_process_on_port(server["port"])
                await asyncio.sleep(2)

            # Prepare environment
            env = {
                **os.environ,
                "PYTHONPATH": str(Path(__file__).parent.parent),
                "ENVIRONMENT": "prod",
                "PULUMI_ORG": "scoobyjava-org",
                **server.get("env", {}),
            }

            # Start the server
            logger.info(
                f"🚀 Starting {server['name']} server on port {server['port']}..."
            )

            process = subprocess.Popen(
                [sys.executable, server["path"]],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
            )

            self.processes[server["name"]] = process

            # Wait for startup
            await asyncio.sleep(3)

            # Check if process is still running
            if process.poll() is None:
                logger.info(
                    f"✅ {server['name']} server started successfully (PID: {process.pid})"
                )
                return True
            else:
                logger.error(f"❌ {server['name']} server failed to start")
                # Read error output
                if process.stderr:
                    stderr = process.stderr.read()
                    if stderr:
                        logger.error(f"Error output: {stderr}")
                return False

        except Exception as e:
            logger.error(f"Failed to start {server['name']}: {e}")
            return False

    async def monitor_servers(self):
        """Monitor server health and restart if needed"""
        while self.running:
            for server in self.servers:
                if server["name"] in self.processes:
                    process = self.processes[server["name"]]
                    if process.poll() is not None:
                        logger.warning(
                            f"⚠️  {server['name']} server crashed, restarting..."
                        )
                        await self.start_server(server)

            await asyncio.sleep(10)

    async def start_all_servers(self):
        """Start all configured servers"""
        logger.info("🚀 Starting StandardizedMCPServer deployment...")

        # Start servers concurrently
        tasks = [self.start_server(server) for server in self.servers]
        results = await asyncio.gather(*tasks)

        successful = sum(1 for r in results if r)
        logger.info(
            f"\n📊 Deployment Summary: {successful}/{len(self.servers)} servers started successfully"
        )

        if successful > 0:
            logger.info("\n✅ Servers are running. Press Ctrl+C to stop all servers.")

            # Start monitoring
            monitor_task = asyncio.create_task(self.monitor_servers())

            try:
                await asyncio.Event().wait()
            except asyncio.CancelledError:
                monitor_task.cancel()

    def stop_all_servers(self):
        """Stop all running servers"""
        logger.info("\n🛑 Stopping all servers...")
        self.running = False

        for name, process in self.processes.items():
            if process.poll() is None:
                logger.info(f"  Stopping {name}...")
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    logger.warning(f"  Force killing {name}...")
                    process.kill()

        logger.info("✅ All servers stopped")

    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info("\n📍 Received shutdown signal")
        self.stop_all_servers()
        sys.exit(0)


async def main():
    """Main entry point"""
    deployer = MCPServerDeployer()

    # Set up signal handlers
    signal.signal(signal.SIGINT, deployer.signal_handler)
    signal.signal(signal.SIGTERM, deployer.signal_handler)

    try:
        await deployer.start_all_servers()
    except KeyboardInterrupt:
        deployer.stop_all_servers()
    except Exception as e:
        logger.error(f"Deployment failed: {e}")
        deployer.stop_all_servers()
        sys.exit(1)


if __name__ == "__main__":
    import os

    asyncio.run(main())
