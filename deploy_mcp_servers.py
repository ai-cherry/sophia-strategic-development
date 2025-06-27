#!/usr/bin/env python3
"""
Simple MCP Server Deployment Script
Starts essential MCP servers for Sophia AI
"""

import subprocess
import time
import sys
import os
from pathlib import Path
import requests
import logging

logger = logging.getLogger(__name__)


class MCPServerDeployer:
    def __init__(self):
        self.servers = []
        self.root_path = Path(__file__).parent

    def start_server(self, name: str, module: str, port: int):
        """Start an MCP server"""
        print(f"🚀 Starting {name} MCP Server on port {port}...")

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

            print(f"✅ {name} MCP Server started (PID: {proc.pid})")
            return True

        except Exception as e:
            print(f"❌ Failed to start {name} MCP Server: {e}")
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
        print("🎯 Deploying Essential Sophia AI MCP Servers")
        print("=" * 50)

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

        print("\n📊 Deployment Summary:")
        print(
            f"   ✅ Successfully started: {success_count}/{len(essential_servers)} servers"
        )

        if success_count > 0:
            print("\n🔗 Server Status:")
            for server in self.servers:
                status = (
                    "🟢 Running" if server["process"].poll() is None else "🔴 Stopped"
                )
                print(f"   {server['name']}: {status} (Port {server['port']})")

        return success_count > 0

    def stop_all_servers(self):
        """Stop all running servers"""
        print("\n🛑 Stopping all MCP servers...")
        for server in self.servers:
            try:
                server["process"].terminate()
                server["process"].wait(timeout=5)
                print(f"✅ Stopped {server['name']}")
            except Exception:
                try:
                    server["process"].kill()
                    print(f"🔴 Force killed {server['name']}")
                except Exception as e:
                    print(f"❌ Failed to stop {server['name']}: {e}")


def main():
    deployer = MCPServerDeployer()

    try:
        success = deployer.deploy_essential_servers()

        if success:
            print("\n🎉 MCP Servers deployed successfully!")
            print("\n💡 Next steps:")
            print("   1. Test server connectivity")
            print("   2. Deploy additional servers as needed")
            print("   3. Configure Cursor IDE integration")
            print("\n⚠️  Press Ctrl+C to stop all servers")

            # Keep the script running
            while True:
                time.sleep(10)
                # Check if any servers have died
                for server in deployer.servers:
                    if server["process"].poll() is not None:
                        print(f"⚠️  {server['name']} server has stopped!")
        else:
            print("\n❌ Failed to deploy MCP servers")
            return 1

    except KeyboardInterrupt:
        print("\n\n🛑 Shutdown requested...")
        deployer.stop_all_servers()
        print("✅ All servers stopped")
        return 0
    except Exception as e:
        print(f"\n❌ Deployment failed: {e}")
        deployer.stop_all_servers()
        return 1


if __name__ == "__main__":
    sys.exit(main())
