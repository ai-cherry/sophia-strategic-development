#!/usr/bin/env python3
"""
Comprehensive MCP Server Debugging Tool
Sophia AI Platform - Complete MCP Ecosystem Health Check

This script systematically debugs all MCP servers configured in the Sophia AI platform,
identifying connectivity issues, configuration problems, and operational status.

Usage:
    python scripts/debug_all_mcp_servers.py
    python scripts/debug_all_mcp_servers.py --verbose
    python scripts/debug_all_mcp_servers.py --fix-issues
    python scripts/debug_all_mcp_servers.py --report-only
"""

import argparse
import concurrent.futures
import json
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

import requests


@dataclass
class MCPServerStatus:
    """MCP server status information."""

    name: str
    port: int
    expected_path: str
    host: str = "165.1.69.44"
    status: str = "unknown"  # unknown, healthy, degraded, failed, unreachable
    response_time: Optional[float] = None
    error_message: Optional[str] = None
    capabilities: list[str] = field(default_factory=list)
    health_data: Optional[dict] = None
    file_exists: bool = False
    config_issues: list[str] = field(default_factory=list)


@dataclass
class MCPEcosystemReport:
    """Complete MCP ecosystem health report."""

    timestamp: str
    total_servers: int
    healthy_servers: int
    degraded_servers: int
    failed_servers: int
    unreachable_servers: int
    config_issues: list[str]
    port_conflicts: list[dict]
    missing_files: list[str]
    server_details: list[MCPServerStatus]


class MCPServerDebugger:
    """Comprehensive MCP server debugging and health checking system."""

    def __init__(self, config_path: str = "config/unified_mcp_config.json"):
        self.config_path = config_path
        self.config = self._load_config()
        self.lambda_labs_host = self.config.get("lambda_labs", {}).get(
            "host", "165.1.69.44"
        )
        self.server_statuses: list[MCPServerStatus] = []

    def _load_config(self) -> dict:
        """Load MCP configuration."""
        try:
            with open(self.config_path) as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Error loading config from {self.config_path}: {e}")
            return {"mcpServers": {}}

    def _check_file_exists(
        self, server_name: str, server_config: dict
    ) -> tuple[bool, str]:
        """Check if MCP server file exists."""
        args = server_config.get("args", [])
        if not args:
            return False, "No args specified in config"

        server_path = args[0]  # First arg is usually the server file
        full_path = Path(server_path)

        return full_path.exists(), str(full_path)

    def _check_health_endpoint(
        self, host: str, port: int, timeout: int = 10
    ) -> tuple[str, Optional[float], Optional[str], Optional[dict]]:
        """Check MCP server health endpoint."""
        url = f"http://{host}:{port}/health"
        start_time = time.time()

        try:
            response = requests.get(url, timeout=timeout)
            response_time = (time.time() - start_time) * 1000  # Convert to milliseconds

            if response.status_code == 200:
                try:
                    health_data = response.json()
                    status = health_data.get("status", "unknown")
                    if status in ["healthy", "ok", "running"]:
                        return "healthy", response_time, None, health_data
                    else:
                        return (
                            "degraded",
                            response_time,
                            f"Status: {status}",
                            health_data,
                        )
                except json.JSONDecodeError:
                    return "degraded", response_time, "Invalid JSON response", None
            else:
                return "failed", response_time, f"HTTP {response.status_code}", None

        except requests.exceptions.ConnectTimeout:
            response_time = (time.time() - start_time) * 1000
            return "unreachable", response_time, "Connection timeout", None
        except requests.exceptions.ConnectionError:
            response_time = (time.time() - start_time) * 1000
            return "unreachable", response_time, "Connection refused", None
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return "failed", response_time, str(e), None

    def _check_port_conflicts(self) -> list[dict]:
        """Check for port conflicts between servers."""
        port_map = {}
        conflicts = []

        for server_name, server_config in self.config.get("mcpServers", {}).items():
            port = server_config.get("port")
            if port:
                if port in port_map:
                    conflicts.append(
                        {
                            "port": port,
                            "servers": [port_map[port], server_name],
                            "severity": "critical",
                        }
                    )
                    # Update to show multiple servers on same port
                    if isinstance(port_map[port], list):
                        port_map[port].append(server_name)
                    else:
                        port_map[port] = [port_map[port], server_name]
                else:
                    port_map[port] = server_name

        return conflicts

    def _validate_server_config(
        self, server_name: str, server_config: dict
    ) -> list[str]:
        """Validate individual server configuration."""
        issues = []

        # Check required fields
        required_fields = ["command", "args", "port"]
        for field in required_fields:
            if field not in server_config:
                issues.append(f"Missing required field: {field}")

        # Check port range
        port = server_config.get("port")
        if port and (port < 1024 or port > 65535):
            issues.append(f"Invalid port range: {port}")

        # Check command
        command = server_config.get("command")
        if command and command != "python":
            issues.append(f"Unexpected command: {command} (expected: python)")

        # Check health endpoint
        if "health_endpoint" not in server_config:
            issues.append("Missing health_endpoint configuration")

        return issues

    def debug_single_server(
        self, server_name: str, server_config: dict
    ) -> MCPServerStatus:
        """Debug a single MCP server."""
        print(f"🔍 Debugging {server_name}...")

        # Initialize status
        port = server_config.get("port", 0)
        args = server_config.get("args", [])
        expected_path = args[0] if args else "unknown"

        status = MCPServerStatus(
            name=server_name,
            port=port,
            expected_path=expected_path,
            host=self.lambda_labs_host,
            capabilities=server_config.get("capabilities", []),
            config_issues=[],
        )

        # Check file exists
        file_exists, full_path = self._check_file_exists(server_name, server_config)
        status.file_exists = file_exists
        status.expected_path = full_path

        if not file_exists:
            status.status = "failed"
            status.error_message = f"Server file not found: {full_path}"
            print(f"   ❌ File missing: {full_path}")
            return status

        # Check configuration
        config_issues = self._validate_server_config(server_name, server_config)
        status.config_issues = config_issues

        if config_issues:
            print(f"   ⚠️  Config issues: {', '.join(config_issues)}")

        # Check health endpoint
        (
            health_status,
            response_time,
            error_msg,
            health_data,
        ) = self._check_health_endpoint(self.lambda_labs_host, port)

        status.status = health_status
        status.response_time = response_time
        status.error_message = error_msg
        status.health_data = health_data

        # Print status
        status_emoji = {
            "healthy": "✅",
            "degraded": "⚠️",
            "failed": "❌",
            "unreachable": "🔌",
        }.get(health_status, "❓")

        print(f"   {status_emoji} Status: {health_status}")
        if response_time:
            print(f"   ⏱️  Response time: {response_time:.2f}ms")
        if error_msg:
            print(f"   📝 Details: {error_msg}")
        if health_data:
            version = health_data.get("version", "unknown")
            uptime = health_data.get("uptime", "unknown")
            print(f"   📊 Version: {version}, Uptime: {uptime}")

        return status

    def debug_all_servers(self) -> MCPEcosystemReport:
        """Debug all configured MCP servers."""
        print("🚀 **COMPREHENSIVE MCP SERVER DEBUGGING**")
        print(f"🎯 Target Host: {self.lambda_labs_host}")
        print(f"📋 Config: {self.config_path}")
        print("=" * 60)

        # Check for port conflicts first
        port_conflicts = self._check_port_conflicts()
        if port_conflicts:
            print("\n🚨 **PORT CONFLICTS DETECTED:**")
            for conflict in port_conflicts:
                servers = conflict["servers"]
                port = conflict["port"]
                print(f"   ❌ Port {port}: {', '.join(servers)}")

        # Debug each server
        servers = self.config.get("mcpServers", {})
        print(f"\n🔍 **DEBUGGING {len(servers)} MCP SERVERS:**")

        # Use ThreadPoolExecutor for parallel health checks
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = {}
            for server_name, server_config in servers.items():
                future = executor.submit(
                    self.debug_single_server, server_name, server_config
                )
                futures[future] = server_name

            # Collect results
            for future in concurrent.futures.as_completed(futures):
                server_name = futures[future]
                try:
                    status = future.result()
                    self.server_statuses.append(status)
                except Exception as e:
                    print(f"❌ Error debugging {server_name}: {e}")

        # Generate report
        report = self._generate_report(port_conflicts)
        self._print_summary(report)

        return report

    def _generate_report(self, port_conflicts: list[dict]) -> MCPEcosystemReport:
        """Generate comprehensive ecosystem report."""
        healthy = len([s for s in self.server_statuses if s.status == "healthy"])
        degraded = len([s for s in self.server_statuses if s.status == "degraded"])
        failed = len([s for s in self.server_statuses if s.status == "failed"])
        unreachable = len(
            [s for s in self.server_statuses if s.status == "unreachable"]
        )

        config_issues = []
        missing_files = []

        for status in self.server_statuses:
            if status.config_issues:
                config_issues.extend(
                    [f"{status.name}: {issue}" for issue in status.config_issues]
                )
            if not status.file_exists:
                missing_files.append(status.expected_path)

        return MCPEcosystemReport(
            timestamp=datetime.now().isoformat(),
            total_servers=len(self.server_statuses),
            healthy_servers=healthy,
            degraded_servers=degraded,
            failed_servers=failed,
            unreachable_servers=unreachable,
            config_issues=config_issues,
            port_conflicts=port_conflicts,
            missing_files=missing_files,
            server_details=self.server_statuses,
        )

    def _print_summary(self, report: MCPEcosystemReport):
        """Print debugging summary."""
        print("\n" + "=" * 60)
        print("📊 **MCP ECOSYSTEM HEALTH SUMMARY**")
        print("=" * 60)

        total = report.total_servers
        healthy_pct = (report.healthy_servers / total * 100) if total > 0 else 0

        print(f"🎯 **OVERALL HEALTH: {healthy_pct:.1f}%**")
        print(f"📊 Total Servers: {total}")
        print(f"✅ Healthy: {report.healthy_servers}")
        print(f"⚠️  Degraded: {report.degraded_servers}")
        print(f"❌ Failed: {report.failed_servers}")
        print(f"🔌 Unreachable: {report.unreachable_servers}")

        if report.port_conflicts:
            print("\n🚨 **CRITICAL ISSUES:**")
            print(f"   📍 Port Conflicts: {len(report.port_conflicts)}")
            for conflict in report.port_conflicts:
                print(
                    f"      Port {conflict['port']}: {', '.join(conflict['servers'])}"
                )

        if report.missing_files:
            print(f"   📂 Missing Files: {len(report.missing_files)}")
            for file_path in report.missing_files[:3]:  # Show first 3
                print(f"      {file_path}")
            if len(report.missing_files) > 3:
                print(f"      ... and {len(report.missing_files) - 3} more")

        if report.config_issues:
            print(f"   ⚙️  Config Issues: {len(report.config_issues)}")
            for issue in report.config_issues[:3]:  # Show first 3
                print(f"      {issue}")
            if len(report.config_issues) > 3:
                print(f"      ... and {len(report.config_issues) - 3} more")

        # Recommendations
        print("\n💡 **RECOMMENDATIONS:**")
        if report.port_conflicts:
            print("   1. Resolve port conflicts immediately (critical)")
        if report.missing_files:
            print("   2. Install missing MCP server files")
        if report.unreachable_servers > 0:
            print("   3. Check Lambda Labs instance connectivity")
        if report.failed_servers > 0:
            print("   4. Review server logs for startup issues")
        if healthy_pct < 80:
            print("   5. Consider phased server restart")

    def save_report(self, report: MCPEcosystemReport, filename: Optional[str] = None):
        """Save debugging report to file."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"mcp_debug_report_{timestamp}.json"

        with open(filename, "w") as f:
            json.dump(asdict(report), f, indent=2, default=str)

        print(f"📊 Debug report saved: {filename}")
        return filename


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Debug All MCP Servers - Comprehensive Health Check"
    )
    parser.add_argument(
        "--config",
        default="config/unified_mcp_config.json",
        help="MCP configuration file path",
    )
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument(
        "--report-only", action="store_true", help="Generate report only without fixes"
    )
    parser.add_argument(
        "--save-report", action="store_true", help="Save report to JSON file"
    )
    parser.add_argument(
        "--fix-issues",
        action="store_true",
        help="Attempt to fix common issues (not implemented yet)",
    )

    args = parser.parse_args()

    # Initialize debugger
    debugger = MCPServerDebugger(config_path=args.config)

    # Run debugging
    report = debugger.debug_all_servers()

    # Save report if requested
    if args.save_report:
        debugger.save_report(report)

    # Return appropriate exit code
    if report.healthy_servers == report.total_servers:
        print("\n🎉 All MCP servers are healthy!")
        return 0
    elif report.healthy_servers > 0:
        print(
            f"\n⚠️  {report.healthy_servers}/{report.total_servers} servers healthy - issues detected"
        )
        return 1
    else:
        print("\n❌ Critical ecosystem issues - immediate attention required")
        return 2


if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
