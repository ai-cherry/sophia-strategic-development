#!/usr/bin/env python3
"""
Simple MCP Server Deployment Script
Starts essential MCP servers for Sophia AI
"""

import contextlib
import logging
import os
import subprocess
import sys
import time
from pathlib import Path

import requests

logger = logging.getLogger(__name__)

class MCPServerDeployer:
    def __init__(self):
        self.servers = []
        self.root_path = Path(__file__).parent

    def start_server(self, name: str, module: str, port: int):
        """Start an MCP server"""

        # Set environment variables
        env = os.environ.copy()
        env["PULUMI_ORG"] = "scoobyjava-org"
        env["PYTHONPATH"] = str(self.root_path)

        try:
            # Start the server as a subprocess
            proc = subprocess.Popen(
                [sys.executable, "-m", module],
                env=env,
                cwd=self.root_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            self.servers.append(
                {"name": name, "module": module, "port": port, "process": proc}
            )

            return True

        except Exception:
            return False

    def check_server_health(self, port: int):
        """Check if a server is responding"""
        try:
            response = requests.get(f"http://localhost:{port}/health", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.debug(f"Health check for port {port} failed: {e}")
            return False

    def deploy_essential_servers(self):
        """Deploy the essential MCP servers"""

        # Essential servers to deploy
        essential_servers = [
            {
                "name": "AI Memory",
                "module": "backend.mcp.ai_memory_mcp_server",
                "port": 9000,
            }
        ]

        success_count = 0
        for server in essential_servers:
            if self.start_server(server["name"], server["module"], server["port"]):
                success_count += 1
                # Give the server time to start
                time.sleep(2)

        if success_count > 0:
            for server in self.servers:
                ("🟢 Running" if server["process"].poll() is None else "🔴 Stopped")

        return success_count > 0

    def stop_all_servers(self):
        """Stop all running servers"""
        for server in self.servers:
            try:
                server["process"].terminate()
                server["process"].wait(timeout=5)
            except Exception:
                with contextlib.suppress(Exception):
                    server["process"].kill()

def main():
    deployer = MCPServerDeployer()

    try:
        success = deployer.deploy_essential_servers()

        if success:
            # Keep the script running
            while True:
                time.sleep(10)
                # Check if any servers have died
                for server in deployer.servers:
                    if server["process"].poll() is not None:
                        pass
        else:
            return 1

    except KeyboardInterrupt:
        deployer.stop_all_servers()
        return 0
    except Exception:
        deployer.stop_all_servers()
        return 1

if __name__ == "__main__":
    sys.exit(main())
