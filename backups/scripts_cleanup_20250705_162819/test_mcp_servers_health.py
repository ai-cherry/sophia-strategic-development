#!/usr/bin/env python3
"""
Test MCP Servers Health
Comprehensive health check for all MCP servers
"""

import asyncio
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import aiohttp

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MCPHealthChecker:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.config_dir = self.project_root / "config"

        # Load configurations
        self.unified_ports = self._load_json(self.config_dir / "unified_mcp_ports.json")
        self.cursor_config = self._load_json(
            self.config_dir / "cursor_enhanced_mcp_config.json"
        )
        self.lambda_config = self._load_json(
            self.config_dir / "lambda_labs_mcp_config.json"
        )

        self.results = {
            "timestamp": datetime.now().isoformat(),
            "servers": {},
            "summary": {"total": 0, "healthy": 0, "unhealthy": 0, "unreachable": 0},
        }

    def _load_json(self, file_path: Path) -> dict[str, Any]:
        """Load JSON configuration file"""
        if file_path.exists():
            with open(file_path) as f:
                return json.load(f)
        return {}

    async def check_server_health(
        self, server_name: str, port: int, host: str = "localhost"
    ) -> dict[str, Any]:
        """Check health of a single MCP server"""
        url = f"http://{host}:{port}/health"

        try:
            async with aiohttp.ClientSession() as session, session.get(
                url, timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "status": "healthy",
                        "response_time_ms": response.headers.get(
                            "X-Response-Time", "N/A"
                        ),
                        "data": data,
                        "url": url,
                    }
                else:
                    return {
                        "status": "unhealthy",
                        "http_status": response.status,
                        "url": url,
                    }
        except TimeoutError:
            return {"status": "timeout", "error": "Connection timeout", "url": url}
        except Exception as e:
            return {"status": "unreachable", "error": str(e), "url": url}

    async def check_lambda_labs_connectivity(self):
        """Check connectivity to Lambda Labs host"""
        logger.info("\n🔍 Checking Lambda Labs connectivity...")

        lambda_host = self.lambda_config.get("host", "165.1.69.44")
        gateway_port = (
            self.lambda_config.get("services", {})
            .get("mcp_gateway", {})
            .get("port", 8080)
        )

        result = await self.check_server_health(
            "lambda_labs_gateway", gateway_port, lambda_host
        )

        if result["status"] == "healthy":
            logger.info(
                f"✅ Lambda Labs gateway reachable at {lambda_host}:{gateway_port}"
            )
        else:
            logger.warning(
                f"❌ Lambda Labs gateway unreachable: {result.get('error', 'Unknown error')}"
            )

        return result

    async def check_all_servers(self):
        """Check health of all configured MCP servers"""
        logger.info("🏥 Starting MCP Server Health Checks...\n")

        # Get active servers from unified ports
        active_servers = self.unified_ports.get("active_servers", {})

        # Check each server
        tasks = []
        for server_name, port in active_servers.items():
            if isinstance(port, int):  # Skip non-port entries
                logger.info(f"Checking {server_name} on port {port}...")
                task = self.check_server_health(server_name, port)
                tasks.append((server_name, task))

        # Wait for all checks to complete
        for server_name, task in tasks:
            result = await task
            self.results["servers"][server_name] = result
            self.results["summary"]["total"] += 1

            if result["status"] == "healthy":
                self.results["summary"]["healthy"] += 1
                logger.info(f"✅ {server_name}: HEALTHY")
            elif result["status"] == "unreachable":
                self.results["summary"]["unreachable"] += 1
                logger.warning(
                    f"❌ {server_name}: UNREACHABLE - {result.get('error', '')}"
                )
            else:
                self.results["summary"]["unhealthy"] += 1
                logger.warning(
                    f"⚠️  {server_name}: UNHEALTHY - Status: {result.get('status', 'unknown')}"
                )

    def check_server_files(self):
        """Check if server implementation files exist"""
        logger.info("\n📁 Checking server implementation files...\n")

        file_status = {}

        # Check cursor config for file paths
        mcp_servers = self.cursor_config.get("mcpServers", {})

        for server_name, config in mcp_servers.items():
            args = config.get("args", [])
            for arg in args:
                if arg.endswith(".py"):
                    file_path = self.project_root / arg
                    exists = file_path.exists()
                    file_status[server_name] = {
                        "file": arg,
                        "exists": exists,
                        "full_path": str(file_path),
                    }

                    if exists:
                        logger.info(f"✅ {server_name}: {arg}")
                    else:
                        logger.error(f"❌ {server_name}: {arg} NOT FOUND")

        return file_status

    def generate_report(self):
        """Generate comprehensive health report"""
        report = {
            **self.results,
            "lambda_labs": {
                "configured": True,
                "host": self.lambda_config.get("host", "165.1.69.44"),
                "services": self.lambda_config.get("services", {}),
            },
            "configuration": {
                "unified_ports": len(self.unified_ports.get("active_servers", {})),
                "cursor_servers": len(self.cursor_config.get("mcpServers", {})),
                "version": self.cursor_config.get("version", "unknown"),
            },
        }

        # Save report
        report_file = self.project_root / "mcp_health_report.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        logger.info(f"\n📊 Report saved to: {report_file}")

        return report

    def print_summary(self):
        """Print health check summary"""
        summary = self.results["summary"]
        total = summary["total"]
        healthy = summary["healthy"]

        logger.info("\n" + "=" * 50)
        logger.info("📊 MCP SERVER HEALTH SUMMARY")
        logger.info("=" * 50)
        logger.info(f"Total Servers: {total}")
        logger.info(f"✅ Healthy: {healthy}")
        logger.info(f"⚠️  Unhealthy: {summary['unhealthy']}")
        logger.info(f"❌ Unreachable: {summary['unreachable']}")

        if total > 0:
            health_percentage = (healthy / total) * 100
            logger.info(f"\n🎯 Overall Health: {health_percentage:.1f}%")

            if health_percentage == 100:
                logger.info("🎉 All servers are healthy!")
            elif health_percentage >= 80:
                logger.info("✅ System is operational with minor issues")
            elif health_percentage >= 50:
                logger.warning("⚠️  System is degraded - attention needed")
            else:
                logger.error("❌ System is critically impaired")

        logger.info("\n" + "=" * 50)

    async def run(self):
        """Run all health checks"""
        # Check server files
        self.check_server_files()

        # Check server health
        await self.check_all_servers()

        # Check Lambda Labs
        lambda_result = await self.check_lambda_labs_connectivity()
        self.results["lambda_labs"] = lambda_result

        # Generate report
        self.generate_report()

        # Print summary
        self.print_summary()

        # Return exit code based on health
        healthy_percentage = (
            self.results["summary"]["healthy"]
            / max(1, self.results["summary"]["total"])
        ) * 100
        return 0 if healthy_percentage >= 50 else 1


async def main():
    checker = MCPHealthChecker()
    exit_code = await checker.run()
    sys.exit(exit_code)


if __name__ == "__main__":
    asyncio.run(main())
