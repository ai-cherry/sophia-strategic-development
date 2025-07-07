#!/usr/bin/env python3
"""
MCP Server Issues Fix Script
Sophia AI Platform - Automated MCP Server Management

This script fixes common MCP server issues including:
- Port conflicts resolution
- Configuration fixes
- Local server startup for testing
- Missing file detection

Usage:
    python scripts/fix_mcp_server_issues.py --fix-ports
    python scripts/fix_mcp_server_issues.py --start-local
    python scripts/fix_mcp_server_issues.py --fix-all
"""

import argparse
import json
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional

import requests

# NOTE: This script now supports all 48+ MCP servers dynamically
# Complete server list loaded from configuration files


class MCPServerManager:
    """Comprehensive MCP server management and fixing system."""

    def __init__(self, config_path: str = "config/unified_mcp_config.json"):
        self.config_path = config_path
        self.config = self._load_config()
        self.running_processes: dict[str, subprocess.Popen] = {}
        self.shutdown_requested = False

        # Register signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _load_config(self) -> dict:
        """Load MCP configuration."""
        try:
            with open(self.config_path) as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Error loading config from {self.config_path}: {e}")
            return {"mcpServers": {}}

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        print(f"\n🛑 Received signal {signum}, shutting down gracefully...")
        self.shutdown_requested = True
        self.stop_all_servers()
        sys.exit(0)

    def fix_port_conflicts(self) -> bool:
        """Fix port conflicts in the configuration."""
        print("🔧 **FIXING PORT CONFLICTS**")

        servers = self.config.get("mcpServers", {})
        port_assignments = {}
        conflicts_found = []

        # Detect conflicts
        for server_name, server_config in servers.items():
            port = server_config.get("port")
            if port in port_assignments:
                conflicts_found.append((port, port_assignments[port], server_name))
            else:
                port_assignments[port] = server_name

        if not conflicts_found:
            print("✅ No port conflicts detected")
            return True

        print(f"🚨 Found {len(conflicts_found)} port conflicts:")

        # Fix conflicts by reassigning ports
        next_available_port = 9040  # Start from a high port

        for port, server1, server2 in conflicts_found:
            print(f"   Conflict on port {port}: {server1} vs {server2}")

            # Keep the first server on the original port, move the second
            new_port = next_available_port
            while new_port in port_assignments.values():
                new_port += 1

            print(f"   → Moving {server2} from port {port} to {new_port}")

            # Update configuration
            servers[server2]["port"] = new_port
            if "env" in servers[server2]:
                servers[server2]["env"]["PORT"] = str(new_port)

            port_assignments[new_port] = server2
            next_available_port = new_port + 1

        # Save updated configuration
        try:
            with open(self.config_path, "w") as f:
                json.dump(self.config, f, indent=2)
            print("✅ Port conflicts resolved and configuration saved")
            return True
        except Exception as e:
            print(f"❌ Error saving configuration: {e}")
            return False

    def validate_server_files(self) -> dict[str, bool]:
        """Validate that all server files exist."""
        print("📂 **VALIDATING SERVER FILES**")

        results = {}
        servers = self.config.get("mcpServers", {})

        for server_name, server_config in servers.items():
            args = server_config.get("args", [])
            if not args:
                print(f"   ❌ {server_name}: No args specified")
                results[server_name] = False
                continue

            server_path = Path(args[0])
            if server_path.exists():
                print(f"   ✅ {server_name}: {server_path}")
                results[server_name] = True
            else:
                print(f"   ❌ {server_name}: Missing file {server_path}")
                results[server_name] = False

        valid_count = sum(1 for v in results.values() if v)
        print(f"📊 {valid_count}/{len(results)} server files found")

        return results

    def start_server_locally(
        self, server_name: str, server_config: dict
    ) -> subprocess.Popen | None:
        """Start a single MCP server locally."""
        if server_name in self.running_processes:
            print(f"   ⚠️  {server_name} already running")
            return self.running_processes[server_name]

        # Prepare command
        command = server_config.get("command", "python")
        args = server_config.get("args", [])
        port = server_config.get("port", 8000)

        if not args:
            print(f"   ❌ {server_name}: No args specified")
            return None

        server_path = Path(args[0])
        if not server_path.exists():
            print(f"   ❌ {server_name}: File not found: {server_path}")
            return None

        # Prepare environment
        env = {
            "PYTHONPATH": str(Path.cwd()),
            "ENVIRONMENT": "dev",
            "PORT": str(port),
            **server_config.get("env", {}),
        }

        # Start server
        try:
            full_command = [command] + args
            print(f"   🚀 Starting {server_name} on port {port}")
            print(f"      Command: {' '.join(full_command)}")

            process = subprocess.Popen(
                full_command,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=str(Path.cwd()),
            )

            self.running_processes[server_name] = process

            # Give it a moment to start
            time.sleep(2)

            # Check if it's still running
            if process.poll() is None:
                print(f"   ✅ {server_name} started successfully (PID: {process.pid})")
                return process
            else:
                stdout, stderr = process.communicate()
                print(f"   ❌ {server_name} failed to start")
                print(f"      stdout: {stdout[:200]}...")
                print(f"      stderr: {stderr[:200]}...")
                return None

        except Exception as e:
            print(f"   ❌ {server_name}: Error starting server: {e}")
            return None

    def start_all_servers_locally(self) -> dict[str, bool]:
        """Start all MCP servers locally for testing."""
        print("🚀 **STARTING ALL MCP SERVERS LOCALLY**")

        servers = self.config.get("mcpServers", {})
        results = {}

        # Start servers in dependency order if specified
        startup_order = self.config.get("orchestration", {}).get("startup_order", [])

        # If no startup order, use all servers
        if not startup_order:
            startup_order = list(servers.keys())

        for server_name in startup_order:
            if server_name not in servers:
                print(f"   ⚠️  Server {server_name} in startup order but not in config")
                continue

            server_config = servers[server_name]
            process = self.start_server_locally(server_name, server_config)
            results[server_name] = process is not None

            # Brief pause between startups
            time.sleep(1)

        # Summary
        successful = sum(1 for v in results.values() if v)
        print(f"\n📊 Started {successful}/{len(results)} servers successfully")

        if successful > 0:
            print("💡 Servers are running locally. Use Ctrl+C to stop all servers.")

        return results

    def health_check_servers(self, timeout: int = 5) -> dict[str, dict]:
        """Check health of running servers."""
        print("🏥 **HEALTH CHECKING SERVERS**")

        results = {}
        servers = self.config.get("mcpServers", {})

        for server_name, server_config in servers.items():
            port = server_config.get("port", 8000)
            url = f"http://localhost:{port}/health"

            try:
                response = requests.get(url, timeout=timeout)
                if response.status_code == 200:
                    try:
                        health_data = response.json()
                        results[server_name] = {
                            "status": "healthy",
                            "response_time": response.elapsed.total_seconds() * 1000,
                            "data": health_data,
                        }
                        print(
                            f"   ✅ {server_name}: Healthy ({response.elapsed.total_seconds()*1000:.1f}ms)"
                        )
                    except:
                        results[server_name] = {
                            "status": "responding",
                            "response_time": response.elapsed.total_seconds() * 1000,
                            "data": None,
                        }
                        print(f"   ⚠️  {server_name}: Responding but invalid JSON")
                else:
                    results[server_name] = {
                        "status": "error",
                        "response_time": response.elapsed.total_seconds() * 1000,
                        "error": f"HTTP {response.status_code}",
                    }
                    print(f"   ❌ {server_name}: HTTP {response.status_code}")
            except requests.exceptions.ConnectTimeout:
                results[server_name] = {
                    "status": "timeout",
                    "error": "Connection timeout",
                }
                print(f"   🔌 {server_name}: Connection timeout")
            except requests.exceptions.ConnectionError:
                results[server_name] = {
                    "status": "unreachable",
                    "error": "Connection refused",
                }
                print(f"   🔌 {server_name}: Connection refused")
            except Exception as e:
                results[server_name] = {"status": "error", "error": str(e)}
                print(f"   ❌ {server_name}: {e}")

        # Summary
        healthy_count = sum(1 for r in results.values() if r.get("status") == "healthy")
        print(f"📊 {healthy_count}/{len(results)} servers healthy")

        return results

    def stop_all_servers(self):
        """Stop all running servers."""
        if not self.running_processes:
            return

        print("🛑 **STOPPING ALL SERVERS**")

        for server_name, process in self.running_processes.items():
            try:
                print(f"   🛑 Stopping {server_name} (PID: {process.pid})")
                process.terminate()

                # Wait for graceful shutdown
                try:
                    process.wait(timeout=5)
                    print(f"   ✅ {server_name} stopped gracefully")
                except subprocess.TimeoutExpired:
                    print(f"   ⚡ Force killing {server_name}")
                    process.kill()
                    process.wait()

            except Exception as e:
                print(f"   ❌ Error stopping {server_name}: {e}")

        self.running_processes.clear()
        print("✅ All servers stopped")

    def monitor_servers(self, interval: int = 30):
        """Monitor running servers and restart if needed."""
        print(f"👁️  **MONITORING SERVERS** (checking every {interval}s)")
        print("Press Ctrl+C to stop monitoring")

        try:
            while not self.shutdown_requested:
                # Check process health
                dead_servers = []
                for server_name, process in self.running_processes.items():
                    if process.poll() is not None:
                        dead_servers.append(server_name)

                # Restart dead servers
                if dead_servers:
                    print(f"💀 Dead servers detected: {', '.join(dead_servers)}")
                    servers = self.config.get("mcpServers", {})
                    for server_name in dead_servers:
                        if server_name in servers:
                            print(f"🔄 Restarting {server_name}")
                            del self.running_processes[server_name]
                            self.start_server_locally(server_name, servers[server_name])

                # Health check
                if self.running_processes:
                    health_results = self.health_check_servers()
                    healthy_count = sum(
                        1
                        for r in health_results.values()
                        if r.get("status") == "healthy"
                    )
                    print(
                        f"📊 Health Status: {healthy_count}/{len(health_results)} servers healthy"
                    )

                # Wait for next check
                time.sleep(interval)

        except KeyboardInterrupt:
            print("\n👋 Monitoring stopped by user")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Fix MCP Server Issues - Comprehensive Management Tool"
    )
    parser.add_argument(
        "--config",
        default="config/unified_mcp_config.json",
        help="MCP configuration file path",
    )
    parser.add_argument(
        "--fix-ports", action="store_true", help="Fix port conflicts in configuration"
    )
    parser.add_argument(
        "--validate-files",
        action="store_true",
        help="Validate that all server files exist",
    )
    parser.add_argument(
        "--start-local",
        action="store_true",
        help="Start all servers locally for testing",
    )
    parser.add_argument(
        "--health-check", action="store_true", help="Perform health check on servers"
    )
    parser.add_argument(
        "--monitor", action="store_true", help="Monitor servers and restart if needed"
    )
    parser.add_argument(
        "--fix-all",
        action="store_true",
        help="Fix all issues and start servers locally",
    )

    args = parser.parse_args()

    # Initialize manager
    manager = MCPServerManager(config_path=args.config)

    try:
        if args.fix_all:
            print("🔧 **COMPREHENSIVE MCP SERVER FIX**")
            print("=" * 50)

            # Step 1: Fix port conflicts
            manager.fix_port_conflicts()

            # Step 2: Validate files
            file_results = manager.validate_server_files()

            # Step 3: Start servers locally
            if any(file_results.values()):
                startup_results = manager.start_all_servers_locally()

                # Step 4: Health check
                time.sleep(3)  # Give servers time to start
                health_results = manager.health_check_servers()

                # Step 5: Monitor if any servers started
                if any(startup_results.values()):
                    manager.monitor_servers()
            else:
                print("❌ No valid server files found - cannot start servers")

        elif args.fix_ports:
            manager.fix_port_conflicts()

        elif args.validate_files:
            manager.validate_server_files()

        elif args.start_local:
            manager.start_all_servers_locally()
            if manager.running_processes:
                manager.monitor_servers()

        elif args.health_check:
            manager.health_check_servers()

        elif args.monitor:
            manager.monitor_servers()

        else:
            # Default: show current status
            print("📊 **MCP SERVER STATUS CHECK**")
            file_results = manager.validate_server_files()
            health_results = manager.health_check_servers()

    except KeyboardInterrupt:
        print("\n👋 Interrupted by user")

    finally:
        manager.stop_all_servers()


if __name__ == "__main__":
    main()
