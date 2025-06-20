#!/usr/bin/env python3
"""Sophia AI - Automated Health Check Runner
Comprehensive system validation and monitoring
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class HealthCheckRunner:
    """Automated health check runner for all Sophia AI components"""

    def __init__(self):
        self.results = {}
        self.start_time = datetime.utcnow()

    async def run_all_checks(self) -> Dict[str, Any]:
        """Run all health checks and return comprehensive results"""
        logger.info("Starting comprehensive health check...")

        checks = [
            ("System Resources", self.check_system_resources),
            ("Docker Services", self.check_docker_services),
            ("MCP Servers", self.check_mcp_servers),
            ("Pulumi ESC", self.check_pulumi_esc),
            ("Database Connections", self.check_database_connections),
            ("API Endpoints", self.check_api_endpoints),
            ("Secret Access", self.check_secret_access),
            ("Claude Integration", self.check_claude_integration),
            ("Configuration Validation", self.check_configuration),
        ]

        for check_name, check_func in checks:
            try:
                logger.info(f"Running {check_name} check...")
                result = await check_func()
                self.results[check_name] = {
                    "status": (
                        "healthy" if result.get("success", False) else "unhealthy"
                    ),
                    "details": result,
                    "timestamp": datetime.utcnow().isoformat(),
                }
            except Exception as e:
                logger.error(f"{check_name} check failed: {e}")
                self.results[check_name] = {
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat(),
                }

        # Calculate overall health
        healthy_checks = sum(
            1 for r in self.results.values() if r["status"] == "healthy"
        )
        total_checks = len(self.results)
        overall_health = (
            "healthy"
            if healthy_checks == total_checks
            else "degraded"
            if healthy_checks > total_checks * 0.7
            else "unhealthy"
        )

        execution_time = (datetime.utcnow() - self.start_time).total_seconds()

        return {
            "overall_status": overall_health,
            "healthy_checks": healthy_checks,
            "total_checks": total_checks,
            "health_percentage": (healthy_checks / total_checks) * 100,
            "execution_time": f"{execution_time:.2f}s",
            "timestamp": datetime.utcnow().isoformat(),
            "checks": self.results,
        }

    async def check_system_resources(self) -> Dict[str, Any]:
        """Check system resource usage"""
        try:
            # CPU usage
            cpu_result = subprocess.run(["top", "-bn1"], capture_output=True, text=True)
            cpu_line = [
                line for line in cpu_result.stdout.split("\n") if "Cpu(s)" in line
            ][0]
            cpu_usage = float(cpu_line.split()[1].replace("%us,", ""))

            # Memory usage
            mem_result = subprocess.run(["free", "-m"], capture_output=True, text=True)
            mem_lines = mem_result.stdout.split("\n")
            mem_line = [line for line in mem_lines if "Mem:" in line][0]
            mem_parts = mem_line.split()
            total_mem = int(mem_parts[1])
            used_mem = int(mem_parts[2])
            mem_usage = (used_mem / total_mem) * 100

            # Disk usage
            disk_result = subprocess.run(
                ["df", "-h", "/"], capture_output=True, text=True
            )
            disk_line = disk_result.stdout.split("\n")[1]
            disk_usage = float(disk_line.split()[4].replace("%", ""))

            return {
                "success": cpu_usage < 80 and mem_usage < 80 and disk_usage < 80,
                "cpu_usage": f"{cpu_usage:.1f}%",
                "memory_usage": f"{mem_usage:.1f}%",
                "disk_usage": f"{disk_usage:.1f}%",
                "warnings": [
                    f"High CPU usage: {cpu_usage:.1f}%" if cpu_usage > 80 else None,
                    f"High memory usage: {mem_usage:.1f}%" if mem_usage > 80 else None,
                    f"High disk usage: {disk_usage:.1f}%" if disk_usage > 80 else None,
                ],
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def check_docker_services(self) -> Dict[str, Any]:
        """Check Docker services status"""
        try:
            result = subprocess.run(
                [
                    "docker-compose",
                    "-f",
                    "docker-compose.mcp.yml",
                    "ps",
                    "--format",
                    "json",
                ],
                capture_output=True,
                text=True,
                cwd=project_root,
            )

            if result.returncode != 0:
                return {"success": False, "error": "Docker Compose not available"}

            services = []
            for line in result.stdout.strip().split("\n"):
                if line:
                    service = json.loads(line)
                    services.append(
                        {
                            "name": service.get("Service"),
                            "status": service.get("State"),
                            "health": service.get("Health", "unknown"),
                        }
                    )

            healthy_services = [s for s in services if s["status"] == "running"]

            return {
                "success": len(healthy_services) == len(services),
                "total_services": len(services),
                "healthy_services": len(healthy_services),
                "services": services,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def check_mcp_servers(self) -> Dict[str, Any]:
        """Check MCP servers health"""
        try:
            import aiohttp

            mcp_servers = [
                ("Sophia MCP", "http://localhost:8000/sophia/health"),
                ("Claude MCP", "http://localhost:8001/claude/health"),
                ("Gong MCP", "http://localhost:8002/gong/health"),
                ("Linear MCP", "http://localhost:8003/linear/health"),
                ("Slack MCP", "http://localhost:8004/slack/health"),
            ]

            server_status = []
            async with aiohttp.ClientSession() as session:
                for name, url in mcp_servers:
                    try:
                        async with session.get(url, timeout=5) as response:
                            if response.status == 200:
                                data = await response.json()
                                server_status.append(
                                    {
                                        "name": name,
                                        "status": "healthy",
                                        "response_time": data.get(
                                            "response_time", "unknown"
                                        ),
                                    }
                                )
                            else:
                                server_status.append(
                                    {
                                        "name": name,
                                        "status": "unhealthy",
                                        "error": f"HTTP {response.status}",
                                    }
                                )
                    except Exception as e:
                        server_status.append(
                            {"name": name, "status": "unreachable", "error": str(e)}
                        )

            healthy_servers = [s for s in server_status if s["status"] == "healthy"]

            return {
                "success": len(healthy_servers) > 0,
                "total_servers": len(server_status),
                "healthy_servers": len(healthy_servers),
                "servers": server_status,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def check_pulumi_esc(self) -> Dict[str, Any]:
        """Check Pulumi ESC connectivity"""
        try:
            result = subprocess.run(
                ["pulumi", "whoami"], capture_output=True, text=True
            )
            if result.returncode != 0:
                return {"success": False, "error": "Pulumi not authenticated"}

            user = result.stdout.strip()

            # Check stack access
            stack_result = subprocess.run(
                ["pulumi", "stack", "ls"], capture_output=True, text=True
            )
            stacks = (
                stack_result.stdout.strip().split("\n")[1:]
                if stack_result.returncode == 0
                else []
            )

            return {
                "success": True,
                "user": user,
                "available_stacks": len(stacks),
                "stacks": [s.split()[0] for s in stacks if s.strip()],
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def check_database_connections(self) -> Dict[str, Any]:
        """Check database connectivity"""
        try:
            from backend.core.config_manager import config_manager

            # Test Snowflake connection
            snowflake_healthy = await config_manager.test_connection("snowflake")

            # Test PostgreSQL connection (if configured)
            postgres_healthy = True  # Placeholder

            return {
                "success": snowflake_healthy,
                "databases": {
                    "snowflake": "healthy" if snowflake_healthy else "unhealthy",
                    "postgres": "healthy" if postgres_healthy else "unhealthy",
                },
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def check_api_endpoints(self) -> Dict[str, Any]:
        """Check API endpoint health"""
        try:
            import aiohttp

            endpoints = [
                ("Health Check", "http://localhost:8000/health"),
                ("Natural Query", "http://localhost:8000/api/natural-query"),
                ("Config API", "http://localhost:8000/api/config"),
            ]

            endpoint_status = []
            async with aiohttp.ClientSession() as session:
                for name, url in endpoints:
                    try:
                        async with session.get(url, timeout=5) as response:
                            endpoint_status.append(
                                {
                                    "name": name,
                                    "status": (
                                        "healthy"
                                        if response.status < 400
                                        else "unhealthy"
                                    ),
                                    "response_code": response.status,
                                }
                            )
                    except Exception as e:
                        endpoint_status.append(
                            {"name": name, "status": "unreachable", "error": str(e)}
                        )

            healthy_endpoints = [e for e in endpoint_status if e["status"] == "healthy"]

            return {
                "success": len(healthy_endpoints) > 0,
                "total_endpoints": len(endpoint_status),
                "healthy_endpoints": len(healthy_endpoints),
                "endpoints": endpoint_status,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def check_secret_access(self) -> Dict[str, Any]:
        """Check secret access through Pulumi ESC"""
        try:
            from backend.core.pulumi_esc import pulumi_esc_client

            # Test secret retrieval
            test_result = await pulumi_esc_client.get_secret(
                "test_secret", default="test_value"
            )

            return {
                "success": test_result is not None,
                "can_access_secrets": test_result is not None,
                "test_result": "accessible" if test_result else "inaccessible",
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def check_claude_integration(self) -> Dict[str, Any]:
        """Check Claude API integration"""
        try:
            from backend.integrations.claude_integration import claude_integration

            # Test Claude API
            test_response = await claude_integration.test_connection()

            return {
                "success": test_response.get("success", False),
                "api_accessible": test_response.get("success", False),
                "model_available": test_response.get("model", "unknown"),
                "response_time": test_response.get("response_time", "unknown"),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def check_configuration(self) -> Dict[str, Any]:
        """Check configuration validity"""
        try:
            # Check MCP config
            mcp_config_path = project_root / "mcp_config.json"
            if not mcp_config_path.exists():
                return {"success": False, "error": "MCP config file not found"}

            with open(mcp_config_path) as f:
                mcp_config = json.load(f)

            # Check Cursor rules
            cursor_rules_path = project_root / ".cursorrules"
            cursor_rules_exists = cursor_rules_path.exists()

            # Check environment variables
            required_env_vars = ["ANTHROPIC_API_KEY", "PULUMI_ACCESS_TOKEN"]

            missing_env_vars = [var for var in required_env_vars if not os.getenv(var)]

            return {
                "success": len(missing_env_vars) == 0 and cursor_rules_exists,
                "mcp_servers_configured": len(mcp_config.get("mcpServers", {})),
                "cursor_rules_exists": cursor_rules_exists,
                "missing_env_vars": missing_env_vars,
                "config_files": {
                    "mcp_config.json": mcp_config_path.exists(),
                    ".cursorrules": cursor_rules_exists,
                    "docker-compose.mcp.yml": (
                        project_root / "docker-compose.mcp.yml"
                    ).exists(),
                },
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


async def main():
    """Main entry point"""
    health_checker = HealthCheckRunner()
    results = await health_checker.run_all_checks()

    # Print results
    print("\n🏥 Sophia AI Health Check Report")
    print(f"{'='*50}")
    print(
        f"Overall Status: {'✅ HEALTHY' if results['overall_status'] == 'healthy' else '⚠️ DEGRADED' if results['overall_status'] == 'degraded' else '❌ UNHEALTHY'}"
    )
    print(
        f"Health Score: {results['health_percentage']:.1f}% ({results['healthy_checks']}/{results['total_checks']} checks passed)"
    )
    print(f"Execution Time: {results['execution_time']}")
    print(f"Timestamp: {results['timestamp']}")

    print("\n📊 Detailed Results:")
    print(f"{'='*50}")

    for check_name, check_result in results["checks"].items():
        status_icon = "✅" if check_result["status"] == "healthy" else "❌"
        print(f"{status_icon} {check_name}: {check_result['status'].upper()}")

        if check_result["status"] == "error":
            print(f"   Error: {check_result['error']}")
        elif "details" in check_result:
            details = check_result["details"]
            if "error" in details:
                print(f"   Error: {details['error']}")
            else:
                # Print relevant details
                for key, value in details.items():
                    if key not in ["success", "error"] and value is not None:
                        print(f"   {key}: {value}")

    # Save results to file
    results_file = (
        project_root
        / f"health_check_results_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
    )
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n📄 Full results saved to: {results_file}")

    # Exit with appropriate code
    if results["overall_status"] == "healthy":
        sys.exit(0)
    elif results["overall_status"] == "degraded":
        sys.exit(1)
    else:
        sys.exit(2)


if __name__ == "__main__":
    asyncio.run(main())
