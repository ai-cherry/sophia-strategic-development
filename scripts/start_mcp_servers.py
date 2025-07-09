#!/usr/bin/env python3
"""
Start all MCP servers with proper configuration
"""

import asyncio
import json
import logging
import os
import subprocess
from pathlib import Path

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class MCPServerManager:
    """Manages MCP server startup and monitoring"""

    def __init__(self):
        self.servers = self.load_server_config()
        self.processes = {}

    def load_server_config(self):
        """Load server configuration from unified config"""
        config_path = Path("config/unified_mcp_config.json")
        if config_path.exists():
            with open(config_path) as f:
                config = json.load(f)
                return config.get("mcpServers", {})
        return {}

    async def start_server(self, name: str, config: dict):
        """Start a single MCP server"""
        try:
            # Skip if already running
            port = config.get("port")
            if self.check_port_in_use(port):
                logger.info(f"✅ {name} already running on port {port}")
                return True

            logger.info(f"🚀 Starting {name} on port {port}...")

            # Set up environment
            env = os.environ.copy()
            env.update(config.get("env", {}))

            # Prepare command
            cmd = [config.get("command", "python")]
            cmd.extend(config.get("args", []))

            # Start the process
            process = subprocess.Popen(
                cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )

            self.processes[name] = process

            # Wait a moment for startup
            await asyncio.sleep(2)

            # Check if process is still running
            if process.poll() is None:
                logger.info(f"✅ {name} started successfully (PID: {process.pid})")
                return True
            else:
                # Process died, get error
                stdout, stderr = process.communicate()
                logger.error(f"❌ {name} failed to start")
                if stderr:
                    logger.error(f"   Error: {stderr}")
                return False

        except Exception as e:
            logger.exception(f"❌ Error starting {name}: {e}")
            return False

    def check_port_in_use(self, port: int) -> bool:
        """Check if a port is already in use"""
        try:
            result = subprocess.run(
                ["lsof", "-i", f":{port}"], check=False, capture_output=True, text=True
            )
            return result.returncode == 0
        except:
            return False

    async def start_all_servers(self):
        """Start all configured servers"""
        logger.info("🚀 Starting all MCP servers...")

        # Get startup order if defined
        startup_order = [
            "snowflake_admin",
            "ai_memory",
            "codacy",
            "linear",
            "github",
            "asana",
            "notion",
            "ui_ux_agent",
            "portkey_admin",
            "lambda_labs_cli",
        ]

        # Start servers in order
        success_count = 0
        for server_name in startup_order:
            if server_name in self.servers:
                config = self.servers[server_name]
                if await self.start_server(server_name, config):
                    success_count += 1
                await asyncio.sleep(1)  # Small delay between starts

        # Start any remaining servers not in order
        for server_name, config in self.servers.items():
            if server_name not in startup_order:
                if await self.start_server(server_name, config):
                    success_count += 1
                await asyncio.sleep(1)

        logger.info(f"\n✅ Started {success_count}/{len(self.servers)} servers")

    async def stop_all_servers(self):
        """Stop all running servers"""
        logger.info("🛑 Stopping all MCP servers...")

        for name, process in self.processes.items():
            if process.poll() is None:
                logger.info(f"  Stopping {name} (PID: {process.pid})")
                process.terminate()
                await asyncio.sleep(0.5)
                if process.poll() is None:
                    process.kill()

        logger.info("✅ All servers stopped")

    async def monitor_servers(self):
        """Monitor server health"""
        while True:
            await asyncio.sleep(30)  # Check every 30 seconds

            for name, process in self.processes.items():
                if process.poll() is not None:
                    logger.warning(f"⚠️  {name} has stopped unexpectedly")
                    # Optionally restart
                    if name in self.servers:
                        await self.start_server(name, self.servers[name])


async def main():
    """Main execution"""
    manager = MCPServerManager()

    try:
        # Start all servers
        await manager.start_all_servers()

        # Keep running and monitor
        logger.info("\n📊 Monitoring servers... Press Ctrl+C to stop")
        await manager.monitor_servers()

    except KeyboardInterrupt:
        logger.info("\n🛑 Shutting down...")
        await manager.stop_all_servers()


if __name__ == "__main__":
    asyncio.run(main())
