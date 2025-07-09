#!/usr/bin/env python3
"""
Start Individual MCP Server
Utility to start and test individual MCP servers
"""

import asyncio
import json
import logging
import os
import signal
import subprocess
import sys
from pathlib import Path
from typing import Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MCPServerStarter:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.config_dir = self.project_root / "config"

        # Load configurations
        self.cursor_config = self._load_json(
            self.config_dir / "cursor_enhanced_mcp_config.json"
        )
        self.unified_ports = self._load_json(self.config_dir / "unified_mcp_ports.json")

        # Track running processes
        self.processes = {}

    def _load_json(self, file_path: Path) -> dict[str, Any]:
        """Load JSON configuration file"""
        if file_path.exists():
            with open(file_path) as f:
                return json.load(f)
        return {}

    def list_available_servers(self):
        """List all available MCP servers"""
        logger.info("📋 Available MCP Servers:\n")

        servers = self.cursor_config.get("mcpServers", {})
        active_ports = self.unified_ports.get("active_servers", {})

        for i, (server_name, config) in enumerate(servers.items(), 1):
            port = active_ports.get(server_name, "N/A")
            args = config.get("args", [])
            file_path = None

            for arg in args:
                if arg.endswith(".py"):
                    file_path = arg
                    break

            logger.info(f"{i}. {server_name}")
            logger.info(f"   Port: {port}")
            logger.info(f"   File: {file_path or 'N/A'}")
            logger.info("")

        return list(servers.keys())

    def start_server(
        self, server_name: str, detached: bool = False
    ) -> subprocess.Popen | None:
        """Start a specific MCP server"""
        servers = self.cursor_config.get("mcpServers", {})

        if server_name not in servers:
            logger.error(f"❌ Server '{server_name}' not found in configuration")
            return None

        config = servers[server_name]
        command = config.get("command", "python")
        args = config.get("args", [])
        env = config.get("env", {})

        # Build full command
        full_command = [command, *args]

        # Set up environment
        full_env = os.environ.copy()
        full_env.update(env)

        # Ensure Lambda Labs host is set
        full_env["LAMBDA_LABS_HOST"] = "165.1.69.44"
        full_env["ENVIRONMENT"] = "prod"
        full_env["PULUMI_ORG"] = "scoobyjava-org"

        logger.info(f"🚀 Starting {server_name}...")
        logger.info(f"   Command: {' '.join(full_command)}")
        logger.info(f"   Environment: {json.dumps(env, indent=2)}")

        try:
            if detached:
                # Start in background
                process = subprocess.Popen(
                    full_command,
                    env=full_env,
                    cwd=self.project_root,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                self.processes[server_name] = process
                logger.info(
                    f"✅ {server_name} started in background (PID: {process.pid})"
                )
                return process
            else:
                # Start in foreground
                process = subprocess.Popen(
                    full_command, env=full_env, cwd=self.project_root
                )
                logger.info(f"✅ {server_name} started in foreground")
                return process

        except Exception as e:
            logger.exception(f"❌ Failed to start {server_name}: {e}")
            return None

    def stop_server(self, server_name: str):
        """Stop a running MCP server"""
        if server_name in self.processes:
            process = self.processes[server_name]
            if process.poll() is None:  # Still running
                logger.info(f"🛑 Stopping {server_name} (PID: {process.pid})...")
                process.terminate()
                try:
                    process.wait(timeout=5)
                    logger.info(f"✅ {server_name} stopped")
                except subprocess.TimeoutExpired:
                    logger.warning(f"⚠️  Force killing {server_name}")
                    process.kill()
                    process.wait()

            del self.processes[server_name]
        else:
            logger.warning(f"⚠️  {server_name} is not running")

    def stop_all_servers(self):
        """Stop all running MCP servers"""
        logger.info("🛑 Stopping all servers...")

        for server_name in list(self.processes.keys()):
            self.stop_server(server_name)

    def check_server_status(self, server_name: str) -> bool:
        """Check if a server is running"""
        if server_name in self.processes:
            process = self.processes[server_name]
            if process.poll() is None:
                return True
        return False

    def start_all_servers(self):
        """Start all configured MCP servers"""
        logger.info("🚀 Starting all MCP servers...\n")

        servers = self.cursor_config.get("mcpServers", {})

        for server_name in servers:
            self.start_server(server_name, detached=True)
            # Small delay between starts
            asyncio.run(asyncio.sleep(1))

        logger.info(f"\n✅ Started {len(self.processes)} servers")

    def monitor_servers(self):
        """Monitor running servers and restart if needed"""
        logger.info("👀 Monitoring servers (Ctrl+C to stop)...\n")

        try:
            while True:
                for server_name, process in list(self.processes.items()):
                    if process.poll() is not None:
                        # Process died
                        logger.warning(
                            f"⚠️  {server_name} died (exit code: {process.returncode})"
                        )
                        logger.info(f"🔄 Restarting {server_name}...")
                        del self.processes[server_name]
                        self.start_server(server_name, detached=True)

                asyncio.run(asyncio.sleep(5))  # Check every 5 seconds

        except KeyboardInterrupt:
            logger.info("\n⏹️  Stopping monitoring...")
            self.stop_all_servers()


def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info("\n🛑 Received shutdown signal")
    sys.exit(0)


def main():
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    starter = MCPServerStarter()

    if len(sys.argv) < 2:
        logger.info("Usage: python start_mcp_server.py <command> [server_name]")
        logger.info("\nCommands:")
        logger.info("  list     - List all available servers")
        logger.info("  start    - Start a specific server")
        logger.info("  stop     - Stop a specific server")
        logger.info("  restart  - Restart a specific server")
        logger.info("  all      - Start all servers")
        logger.info("  monitor  - Start all servers and monitor")
        logger.info("\nExamples:")
        logger.info("  python start_mcp_server.py list")
        logger.info("  python start_mcp_server.py start ai_memory")
        logger.info("  python start_mcp_server.py all")
        logger.info("  python start_mcp_server.py monitor")
        sys.exit(1)

    command = sys.argv[1]

    if command == "list":
        starter.list_available_servers()

    elif command == "start":
        if len(sys.argv) < 3:
            logger.error("Please specify a server name")
            starter.list_available_servers()
            sys.exit(1)

        server_name = sys.argv[2]
        process = starter.start_server(server_name)

        if process and not starter.check_server_status(server_name):
            # Running in foreground
            try:
                process.wait()
            except KeyboardInterrupt:
                logger.info("\n🛑 Stopping server...")
                process.terminate()
                process.wait()

    elif command == "stop":
        if len(sys.argv) < 3:
            logger.error("Please specify a server name")
            sys.exit(1)

        server_name = sys.argv[2]
        starter.stop_server(server_name)

    elif command == "restart":
        if len(sys.argv) < 3:
            logger.error("Please specify a server name")
            sys.exit(1)

        server_name = sys.argv[2]
        starter.stop_server(server_name)
        asyncio.run(asyncio.sleep(1))
        starter.start_server(server_name)

    elif command == "all":
        starter.start_all_servers()
        logger.info(
            "\n✅ All servers started. Use 'monitor' command to keep them running."
        )

    elif command == "monitor":
        starter.start_all_servers()
        starter.monitor_servers()

    else:
        logger.error(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
