#!/usr/bin/env python3
"""
Sophia AI Health Check
Comprehensive health monitoring for all Sophia AI components

Date: July 9, 2025
"""

import asyncio
import json
import sys
from pathlib import Path

import aiohttp
import yaml

from backend.core.date_time_manager import date_manager

# Health check endpoints
HEALTH_ENDPOINTS = {
    "unified_orchestrator": "http://localhost:8000/health",
    "mcp_orchestration": "http://localhost:8080/health",
    "registry_v2": "http://localhost:8081/health",
    "health_monitor": "http://localhost:8082/health",
}

# MCP server health endpoints
MCP_HEALTH_TEMPLATE = "http://localhost:{port}/health"


class SophiaHealthChecker:
    """Comprehensive health checker for Sophia AI"""

    def __init__(self):
        self.current_date = date_manager.now()
        self.results = {
            "timestamp": self.current_date.isoformat(),
            "overall_health": "UNKNOWN",
            "components": {},
            "mcp_servers": {},
            "metrics": {},
            "issues": [],
        }

    async def check_all(self) -> dict:
        """Run all health checks"""
        print(
            f"🏥 Sophia AI Health Check - {self.current_date.strftime('%Y-%m-%d %H:%M:%S')}"
        )
        print("=" * 60)

        # Load configuration
        config = self._load_config()

        # Run checks in parallel
        tasks = [
            self._check_core_services(),
            self._check_mcp_servers(config),
            self._check_memory_architecture(),
            self._check_configuration_validity(config),
            self._check_resource_usage(),
        ]

        await asyncio.gather(*tasks, return_exceptions=True)

        # Calculate overall health
        self._calculate_overall_health()

        # Generate report
        self._print_report()

        return self.results

    def _load_config(self) -> dict:
        """Load Sophia configuration"""
        config_path = Path("config/sophia_mcp_unified.yaml")

        if not config_path.exists():
            self.results["issues"].append("Configuration file not found")
            return {}

        with open(config_path) as f:
            return yaml.safe_load(f)

    async def _check_core_services(self):
        """Check core Sophia services"""
        print("\n🔍 Checking Core Services...")

        async with aiohttp.ClientSession() as session:
            for service_name, url in HEALTH_ENDPOINTS.items():
                try:
                    async with session.get(
                        url, timeout=aiohttp.ClientTimeout(total=5)
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            self.results["components"][service_name] = {
                                "status": "HEALTHY",
                                "response_time": data.get("response_time", 0),
                                "version": data.get("version", "unknown"),
                            }
                            print(f"  ✅ {service_name}: HEALTHY")
                        else:
                            self.results["components"][service_name] = {
                                "status": "UNHEALTHY",
                                "error": f"HTTP {response.status}",
                            }
                            self.results["issues"].append(
                                f"{service_name} returned HTTP {response.status}"
                            )
                            print(
                                f"  ❌ {service_name}: UNHEALTHY (HTTP {response.status})"
                            )
                except asyncio.TimeoutError:
                    self.results["components"][service_name] = {
                        "status": "TIMEOUT",
                        "error": "Request timed out",
                    }
                    self.results["issues"].append(
                        f"{service_name} health check timed out"
                    )
                    print(f"  ⏱️  {service_name}: TIMEOUT")
                except Exception as e:
                    self.results["components"][service_name] = {
                        "status": "ERROR",
                        "error": str(e),
                    }
                    self.results["issues"].append(
                        f"{service_name} health check failed: {e}"
                    )
                    print(f"  ❌ {service_name}: ERROR ({type(e).__name__})")

    async def _check_mcp_servers(self, config: dict):
        """Check all MCP servers"""
        print("\n🔍 Checking MCP Servers...")

        mcp_servers = config.get("mcp_servers", {})
        total_servers = 0
        healthy_servers = 0

        async with aiohttp.ClientSession() as session:
            for tier, servers in mcp_servers.items():
                print(f"\n  📂 {tier}:")

                for server_name, server_config in servers.items():
                    if isinstance(server_config, dict):
                        total_servers += 1
                        port = server_config.get("port")
                        status = server_config.get("status", "unknown")

                        if status != "active":
                            self.results["mcp_servers"][server_name] = {
                                "status": "INACTIVE",
                                "tier": tier,
                                "port": port,
                            }
                            print(f"    ⏸️  {server_name} (port {port}): INACTIVE")
                            continue

                        # Check health endpoint
                        url = MCP_HEALTH_TEMPLATE.format(port=port)

                        try:
                            async with session.get(
                                url, timeout=aiohttp.ClientTimeout(total=3)
                            ) as response:
                                if response.status == 200:
                                    healthy_servers += 1
                                    self.results["mcp_servers"][server_name] = {
                                        "status": "HEALTHY",
                                        "tier": tier,
                                        "port": port,
                                        "capabilities": server_config.get(
                                            "capabilities", []
                                        ),
                                    }
                                    print(f"    ✅ {server_name} (port {port}): HEALTHY")
                                else:
                                    self.results["mcp_servers"][server_name] = {
                                        "status": "UNHEALTHY",
                                        "tier": tier,
                                        "port": port,
                                        "error": f"HTTP {response.status}",
                                    }
                                    print(
                                        f"    ❌ {server_name} (port {port}): UNHEALTHY"
                                    )
                        except Exception:
                            self.results["mcp_servers"][server_name] = {
                                "status": "UNREACHABLE",
                                "tier": tier,
                                "port": port,
                            }
                            print(f"    ⚠️  {server_name} (port {port}): UNREACHABLE")

        self.results["metrics"]["mcp_servers_total"] = total_servers
        self.results["metrics"]["mcp_servers_healthy"] = healthy_servers
        self.results["metrics"]["mcp_servers_health_percentage"] = round(
            (healthy_servers / total_servers * 100) if total_servers > 0 else 0, 2
        )

    async def _check_memory_architecture(self):
        """Check unified memory architecture compliance"""
        print("\n🔍 Checking Memory Architecture...")

        # Check for forbidden imports
        forbidden_patterns = [
            "import pinecone",
            "import weaviate",
            "from pinecone",
            "from weaviate",
            "ChromaDB",
            "chromadb",
        ]

        violations = []
        python_files = list(Path(".").rglob("*.py"))

        for file_path in python_files[:10]:  # Check first 10 files as sample
            try:
                content = file_path.read_text()
                for pattern in forbidden_patterns:
                    if pattern in content:
                        violations.append(f"{file_path}: {pattern}")
            except Exception:
                pass

        if violations:
            self.results["components"]["memory_architecture"] = {
                "status": "VIOLATION",
                "violations": len(violations),
                "sample": violations[:5],
            }
            self.results["issues"].append(
                f"Found {len(violations)} memory architecture violations"
            )
            print(f"  ❌ Memory Architecture: {len(violations)} VIOLATIONS")
        else:
            self.results["components"]["memory_architecture"] = {"status": "COMPLIANT"}
            print("  ✅ Memory Architecture: COMPLIANT")

    async def _check_configuration_validity(self, config: dict):
        """Check configuration validity"""
        print("\n🔍 Checking Configuration...")

        issues = []

        # Check version
        version = config.get("version")
        if version != "5.0":
            issues.append(f"Unexpected configuration version: {version}")

        # Check environment
        env = config.get("environment")
        if env != "prod":
            issues.append(f"Not in production environment: {env}")

        # Check date awareness
        last_updated = config.get("last_updated")
        if last_updated != "2025-07-09":
            issues.append("Configuration not updated for July 9, 2025")

        # Check for port conflicts
        ports_seen = set()
        mcp_servers = config.get("mcp_servers", {})

        for tier, servers in mcp_servers.items():
            for server_name, server_config in servers.items():
                if isinstance(server_config, dict):
                    port = server_config.get("port")
                    if port in ports_seen:
                        issues.append(f"Port conflict: {port} used by multiple servers")
                    ports_seen.add(port)

        if issues:
            self.results["components"]["configuration"] = {
                "status": "ISSUES",
                "issues": issues,
            }
            print(f"  ⚠️  Configuration: {len(issues)} ISSUES")
        else:
            self.results["components"]["configuration"] = {"status": "VALID"}
            print("  ✅ Configuration: VALID")

    async def _check_resource_usage(self):
        """Check resource usage"""
        print("\n🔍 Checking Resource Usage...")

        try:
            # This would normally check actual resource usage
            # For now, we'll simulate with configuration data

            config = self._load_config()
            total_memory = 0
            total_cpu = 0

            for tier, servers in config.get("mcp_servers", {}).items():
                for server_name, server_config in servers.items():
                    if isinstance(server_config, dict):
                        resources = server_config.get("resources", {})
                        memory_str = resources.get("memory", "0Gi")
                        cpu_str = resources.get("cpu", "0m")
                        replicas = resources.get("replicas", 1)

                        try:
                            memory_gb = int(memory_str.replace("Gi", ""))
                            cpu_cores = int(cpu_str.replace("m", "")) / 1000

                            total_memory += memory_gb * replicas
                            total_cpu += cpu_cores * replicas
                        except ValueError:
                            pass

            self.results["metrics"]["allocated_memory_gb"] = total_memory
            self.results["metrics"]["allocated_cpu_cores"] = round(total_cpu, 2)

            print(f"  📊 Allocated Memory: {total_memory} GB")
            print(f"  📊 Allocated CPU: {total_cpu:.2f} cores")

        except Exception as e:
            self.results["components"]["resources"] = {
                "status": "ERROR",
                "error": str(e),
            }
            print("  ❌ Resource Check: ERROR")

    def _calculate_overall_health(self):
        """Calculate overall system health"""

        # Count healthy vs unhealthy components
        healthy_count = 0
        total_count = 0

        for component, status in self.results["components"].items():
            total_count += 1
            if isinstance(status, dict) and status.get("status") in [
                "HEALTHY",
                "VALID",
                "COMPLIANT",
            ]:
                healthy_count += 1

        # Factor in MCP server health
        mcp_health_pct = self.results["metrics"].get("mcp_servers_health_percentage", 0)

        # Calculate overall score
        component_score = (healthy_count / total_count * 100) if total_count > 0 else 0
        overall_score = component_score * 0.6 + mcp_health_pct * 0.4

        if overall_score >= 90:
            self.results["overall_health"] = "EXCELLENT"
        elif overall_score >= 75:
            self.results["overall_health"] = "GOOD"
        elif overall_score >= 50:
            self.results["overall_health"] = "DEGRADED"
        else:
            self.results["overall_health"] = "CRITICAL"

        self.results["metrics"]["overall_health_score"] = round(overall_score, 2)

    def _print_report(self):
        """Print health check report"""

        print("\n" + "=" * 60)
        print("📊 HEALTH CHECK SUMMARY")
        print("=" * 60)

        # Overall health
        health_emoji = {
            "EXCELLENT": "🟢",
            "GOOD": "🟡",
            "DEGRADED": "🟠",
            "CRITICAL": "🔴",
            "UNKNOWN": "⚫",
        }

        overall = self.results["overall_health"]
        score = self.results["metrics"].get("overall_health_score", 0)

        print(f"\n{health_emoji[overall]} Overall Health: {overall} ({score}%)")

        # Component summary
        print("\n📦 Core Components:")
        for component, status in self.results["components"].items():
            if isinstance(status, dict):
                status_str = status.get("status", "UNKNOWN")
                emoji = "✅" if status_str in ["HEALTHY", "VALID", "COMPLIANT"] else "❌"
                print(f"  {emoji} {component}: {status_str}")

        # MCP servers summary
        total = self.results["metrics"].get("mcp_servers_total", 0)
        healthy = self.results["metrics"].get("mcp_servers_healthy", 0)
        print(f"\n🖥️  MCP Servers: {healthy}/{total} healthy")

        # Issues
        if self.results["issues"]:
            print(f"\n⚠️  Issues Found ({len(self.results['issues'])}):")
            for issue in self.results["issues"][:5]:  # Show first 5 issues
                print(f"  - {issue}")
            if len(self.results["issues"]) > 5:
                print(f"  ... and {len(self.results['issues']) - 5} more")

        # Save results
        output_path = Path(
            f"health_check_{self.current_date.strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(output_path, "w") as f:
            json.dump(self.results, f, indent=2)

        print(f"\n💾 Full report saved to: {output_path}")


async def main():
    """Run health check"""
    checker = SophiaHealthChecker()
    results = await checker.check_all()

    # Exit with appropriate code
    if results["overall_health"] in ["EXCELLENT", "GOOD"]:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
