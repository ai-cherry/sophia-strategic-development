#!/usr/bin/env python3
"""
Comprehensive MCP Server Connection Testing
Tests all MCP servers and remediates issues found
"""

import asyncio
import json
import logging
import os
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import aiohttp

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class TestResult:
    """Test result for a single server"""

    server_name: str
    port: int
    status: str  # healthy, unhealthy, not_running, error
    response_time_ms: float | None = None
    error: str | None = None
    tools_available: list[str] = None
    lambda_labs_connected: bool = False
    details: dict[str, Any] = None


@dataclass
class RemediationAction:
    """Action to fix an issue"""

    server_name: str
    issue: str
    action: str
    command: str | None = None
    success: bool = False
    error: str | None = None


class MCPConnectionTester:
    """Test all MCP server connections"""

    def __init__(self):
        self.test_results: dict[str, TestResult] = {}
        self.remediation_actions: list[RemediationAction] = []
        self.lambda_labs_host = os.getenv("LAMBDA_LABS_HOST", "104.171.202.64")

    async def test_all_servers(self):
        """Test all configured servers"""
        logger.info("🧪 Starting comprehensive MCP server testing...")

        # Load server configuration
        servers = self.load_server_config()

        # Test each server
        async with aiohttp.ClientSession() as session:
            tasks = []
            for server_name, config in servers.items():
                task = self.test_server(session, server_name, config)
                tasks.append(task)

            results = await asyncio.gather(*tasks)

        # Store results
        for result in results:
            if result:
                self.test_results[result.server_name] = result

        # Generate report
        self.generate_report()

        # Perform remediation
        await self.remediate_issues()

    def load_server_config(self) -> dict[str, Any]:
        """Load server configuration"""
        servers = {}

        # Load from unified config
        config_path = Path("config/unified_mcp_config.json")
        if config_path.exists():
            with open(config_path) as f:
                config = json.load(f)
                servers.update(config.get("mcpServers", {}))

        # Also check cursor config
        cursor_config_path = Path("config/cursor_enhanced_mcp_config.json")
        if cursor_config_path.exists():
            with open(cursor_config_path) as f:
                cursor_config = json.load(f)
                # Merge any missing servers
                for name, cfg in cursor_config.get("mcpServers", {}).items():
                    if name not in servers:
                        servers[name] = cfg

        return servers

    async def test_server(
        self, session: aiohttp.ClientSession, server_name: str, config: dict[str, Any]
    ) -> TestResult:
        """Test a single server"""
        port = config.get("port", 9000)

        logger.info(f"Testing {server_name} on port {port}...")

        # First check if port is in use
        import subprocess

        try:
            result = subprocess.run(
                ["lsof", "-i", f":{port}"], capture_output=True, text=True
            )

            if result.returncode != 0:
                return TestResult(
                    server_name=server_name,
                    port=port,
                    status="not_running",
                    error="Port not in use",
                )
        except Exception as e:
            logger.error(f"Error checking port: {e}")

        # Test health endpoint
        start_time = time.time()
        try:
            url = f"http://localhost:{port}/health"
            async with session.get(url, timeout=5) as response:
                response_time_ms = (time.time() - start_time) * 1000

                if response.status == 200:
                    data = await response.json()

                    # Test tools endpoint
                    tools = await self.test_tools_endpoint(session, port)

                    # Check Lambda Labs connection
                    lambda_labs_connected = data.get("details", {}).get(
                        "lambda_labs_connected", False
                    )

                    return TestResult(
                        server_name=server_name,
                        port=port,
                        status="healthy",
                        response_time_ms=response_time_ms,
                        tools_available=tools,
                        lambda_labs_connected=lambda_labs_connected,
                        details=data,
                    )
                else:
                    return TestResult(
                        server_name=server_name,
                        port=port,
                        status="unhealthy",
                        response_time_ms=response_time_ms,
                        error=f"HTTP {response.status}",
                    )

        except TimeoutError:
            return TestResult(
                server_name=server_name,
                port=port,
                status="timeout",
                error="Connection timeout",
            )
        except Exception as e:
            return TestResult(
                server_name=server_name, port=port, status="error", error=str(e)
            )

    async def test_tools_endpoint(
        self, session: aiohttp.ClientSession, port: int
    ) -> list[str]:
        """Test tools endpoint"""
        try:
            url = f"http://localhost:{port}/tools"
            async with session.get(url, timeout=3) as response:
                if response.status == 200:
                    data = await response.json()
                    if isinstance(data, list):
                        return [tool.get("name", "unknown") for tool in data]
                    return []
        except:
            return []

    def generate_report(self):
        """Generate test report"""
        logger.info("\n" + "=" * 80)
        logger.info("📊 MCP Server Test Report")
        logger.info("=" * 80)

        # Summary statistics
        total = len(self.test_results)
        healthy = sum(1 for r in self.test_results.values() if r.status == "healthy")
        not_running = sum(
            1 for r in self.test_results.values() if r.status == "not_running"
        )
        unhealthy = sum(
            1
            for r in self.test_results.values()
            if r.status in ["unhealthy", "timeout", "error"]
        )

        logger.info("\n📈 Summary:")
        logger.info(f"  Total Servers: {total}")
        logger.info(f"  ✅ Healthy: {healthy} ({healthy/total*100:.1f}%)")
        logger.info(f"  ⚠️  Not Running: {not_running} ({not_running/total*100:.1f}%)")
        logger.info(f"  ❌ Unhealthy: {unhealthy} ({unhealthy/total*100:.1f}%)")

        # Lambda Labs integration
        lambda_connected = sum(
            1 for r in self.test_results.values() if r.lambda_labs_connected
        )
        logger.info("\n🖥️  Lambda Labs Integration:")
        logger.info(f"  Connected: {lambda_connected}/{healthy} healthy servers")
        logger.info(f"  Host: {self.lambda_labs_host}")

        # Detailed results
        logger.info("\n📋 Detailed Results:")
        for server_name, result in sorted(self.test_results.items()):
            status_icon = {
                "healthy": "✅",
                "not_running": "⚠️",
                "unhealthy": "❌",
                "timeout": "⏱️",
                "error": "💥",
            }.get(result.status, "❓")

            logger.info(f"\n{status_icon} {server_name} (port {result.port}):")
            logger.info(f"   Status: {result.status}")

            if result.response_time_ms:
                logger.info(f"   Response Time: {result.response_time_ms:.1f}ms")

            if result.tools_available:
                logger.info(f"   Tools: {', '.join(result.tools_available)}")

            if result.lambda_labs_connected:
                logger.info("   Lambda Labs: ✅ Connected")

            if result.error:
                logger.info(f"   Error: {result.error}")

    async def remediate_issues(self):
        """Attempt to fix identified issues"""
        logger.info("\n" + "=" * 80)
        logger.info("🔧 Starting Remediation")
        logger.info("=" * 80)

        # Identify servers that need to be started
        not_running = [
            name
            for name, result in self.test_results.items()
            if result.status == "not_running"
        ]

        if not_running:
            logger.info(f"\n🚀 Starting {len(not_running)} servers...")
            for server_name in not_running:
                await self.start_server(server_name)

        # Re-test after remediation
        logger.info("\n🔄 Re-testing after remediation...")
        await asyncio.sleep(5)  # Give servers time to start

        # Re-test not running servers
        async with aiohttp.ClientSession() as session:
            servers = self.load_server_config()
            for server_name in not_running:
                if server_name in servers:
                    result = await self.test_server(
                        session, server_name, servers[server_name]
                    )
                    if result:
                        self.test_results[server_name] = result

        # Final report
        self.generate_final_report()

    async def start_server(self, server_name: str):
        """Attempt to start a server"""
        servers = self.load_server_config()
        if server_name not in servers:
            logger.error(f"No configuration found for {server_name}")
            return

        config = servers[server_name]

        # Build command
        cmd = [config.get("command", "python")]
        cmd.extend(config.get("args", []))

        # Set environment
        env = os.environ.copy()
        env.update(config.get("env", {}))

        logger.info(f"  Starting {server_name}...")

        try:
            import subprocess

            process = subprocess.Popen(
                cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )

            # Wait a moment
            await asyncio.sleep(2)

            # Check if still running
            if process.poll() is None:
                logger.info(f"  ✅ {server_name} started (PID: {process.pid})")
                self.remediation_actions.append(
                    RemediationAction(
                        server_name=server_name,
                        issue="not_running",
                        action="start_server",
                        command=" ".join(cmd),
                        success=True,
                    )
                )
            else:
                stdout, stderr = process.communicate()
                logger.error(f"  ❌ {server_name} failed to start")
                if stderr:
                    logger.error(f"     Error: {stderr}")
                self.remediation_actions.append(
                    RemediationAction(
                        server_name=server_name,
                        issue="not_running",
                        action="start_server",
                        command=" ".join(cmd),
                        success=False,
                        error=stderr,
                    )
                )

        except Exception as e:
            logger.error(f"  ❌ Failed to start {server_name}: {e}")
            self.remediation_actions.append(
                RemediationAction(
                    server_name=server_name,
                    issue="not_running",
                    action="start_server",
                    success=False,
                    error=str(e),
                )
            )

    def generate_final_report(self):
        """Generate final report after remediation"""
        logger.info("\n" + "=" * 80)
        logger.info("📊 Final Report After Remediation")
        logger.info("=" * 80)

        # Summary
        total = len(self.test_results)
        healthy = sum(1 for r in self.test_results.values() if r.status == "healthy")

        logger.info(
            f"\n✅ Final Status: {healthy}/{total} servers healthy ({healthy/total*100:.1f}%)"
        )

        # Remediation summary
        if self.remediation_actions:
            logger.info("\n🔧 Remediation Actions:")
            successful = sum(1 for a in self.remediation_actions if a.success)
            logger.info(f"  Total Actions: {len(self.remediation_actions)}")
            logger.info(f"  Successful: {successful}")
            logger.info(f"  Failed: {len(self.remediation_actions) - successful}")

        # Save detailed report
        self.save_report()

    def save_report(self):
        """Save detailed report to file"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_servers": len(self.test_results),
                "healthy": sum(
                    1 for r in self.test_results.values() if r.status == "healthy"
                ),
                "not_running": sum(
                    1 for r in self.test_results.values() if r.status == "not_running"
                ),
                "unhealthy": sum(
                    1
                    for r in self.test_results.values()
                    if r.status in ["unhealthy", "timeout", "error"]
                ),
            },
            "lambda_labs": {
                "host": self.lambda_labs_host,
                "connected_servers": sum(
                    1 for r in self.test_results.values() if r.lambda_labs_connected
                ),
            },
            "servers": {
                name: {
                    "port": result.port,
                    "status": result.status,
                    "response_time_ms": result.response_time_ms,
                    "tools": result.tools_available,
                    "lambda_labs_connected": result.lambda_labs_connected,
                    "error": result.error,
                }
                for name, result in self.test_results.items()
            },
            "remediation": [
                {
                    "server": action.server_name,
                    "issue": action.issue,
                    "action": action.action,
                    "success": action.success,
                    "error": action.error,
                }
                for action in self.remediation_actions
            ],
        }

        with open("mcp_test_report.json", "w") as f:
            json.dump(report, f, indent=2)

        logger.info("\n📄 Detailed report saved to mcp_test_report.json")


async def main():
    """Main execution"""
    tester = MCPConnectionTester()
    await tester.test_all_servers()


if __name__ == "__main__":
    asyncio.run(main())
