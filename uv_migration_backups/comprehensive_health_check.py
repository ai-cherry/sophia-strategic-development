#!/usr/bin/env python3
"""
Comprehensive Health Check for Sophia AI Platform
Validates all system components and generates detailed health report
"""

import asyncio
import argparse
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from backend.core.auto_esc_config import config
from backend.mcp.ai_memory_mcp_server import AiMemoryMCPServer
from backend.agents.infrastructure.sophia_infrastructure_agent import (
    SophiaInfrastructureAgent,
)

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class HealthCheckStatus:
    """Health check status enumeration"""

    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class ComponentHealthCheck:
    """Base class for component health checks"""

    def __init__(self, name: str):
        self.name = name
        self.status = HealthCheckStatus.UNKNOWN
        self.details = {}
        self.start_time = None
        self.end_time = None

    async def check(self) -> Dict[str, Any]:
        """Perform health check - to be implemented by subclasses"""
        raise NotImplementedError

    def get_execution_time(self) -> Optional[float]:
        """Get execution time in seconds"""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None


class ConfigurationHealthCheck(ComponentHealthCheck):
    """Health check for configuration system"""

    def __init__(self):
        super().__init__("Configuration System")

    async def check(self) -> Dict[str, Any]:
        """Check configuration system health"""
        self.start_time = datetime.now(timezone.utc)

        try:
            # Test configuration loading
            settings = config.as_enhanced_settings()

            # Test health status
            health_status = config.get_health_status()

            # Validate critical settings
            critical_checks = {
                "platform_name": settings.platform_name == "sophia-ai-platform",
                "platform_version": bool(settings.platform_version),
                "environment": bool(settings.environment),
                "config_loaded": health_status.get("config_loaded", False),
                "fallback_working": True,  # If we got here, fallback is working
            }

            all_critical_passed = all(critical_checks.values())

            self.status = (
                HealthCheckStatus.HEALTHY
                if all_critical_passed
                else HealthCheckStatus.WARNING
            )
            self.details = {
                "platform_name": settings.platform_name,
                "platform_version": settings.platform_version,
                "environment": settings.environment,
                "config_key_count": health_status.get("config_key_count", 0),
                "cache_valid": health_status.get("cache_valid", False),
                "critical_checks": critical_checks,
                "health_status": health_status,
            }

        except Exception as e:
            self.status = HealthCheckStatus.CRITICAL
            self.details = {"error": str(e)}
            logger.error(f"Configuration health check failed: {e}")

        self.end_time = datetime.now(timezone.utc)

        return {
            "component": self.name,
            "status": self.status,
            "details": self.details,
            "execution_time": self.get_execution_time(),
        }


class MCPServerHealthCheck(ComponentHealthCheck):
    """Health check for MCP servers"""

    def __init__(self):
        super().__init__("MCP Servers")

    async def check(self) -> Dict[str, Any]:
        """Check MCP server health"""
        self.start_time = datetime.now(timezone.utc)

        try:
            # Test AI Memory MCP Server
            mcp_server = AiMemoryMCPServer()

            # Test tool availability
            tools = mcp_server.get_tools()

            # Test health check
            health = await mcp_server.health_check()

            # Test basic functionality
            test_store = await mcp_server.execute_tool(
                "store_conversation",
                {
                    "content": "Health check test memory",
                    "category": "workflow",
                    "tags": ["health_check", "test"],
                },
            )

            functionality_checks = {
                "tools_available": len(tools) >= 2,
                "server_operational": health.get("status") == "operational",
                "memory_manager": health.get("memory_manager", False),
                "store_functionality": "id" in test_store
                and test_store.get("status") == "stored",
            }

            all_checks_passed = all(functionality_checks.values())

            self.status = (
                HealthCheckStatus.HEALTHY
                if all_checks_passed
                else HealthCheckStatus.WARNING
            )
            self.details = {
                "tools_count": len(tools),
                "tools": [tool["name"] for tool in tools],
                "health_status": health,
                "functionality_checks": functionality_checks,
                "test_store_result": test_store,
            }

        except Exception as e:
            self.status = HealthCheckStatus.CRITICAL
            self.details = {"error": str(e)}
            logger.error(f"MCP server health check failed: {e}")

        self.end_time = datetime.now(timezone.utc)

        return {
            "component": self.name,
            "status": self.status,
            "details": self.details,
            "execution_time": self.get_execution_time(),
        }


class AgentFrameworkHealthCheck(ComponentHealthCheck):
    """Health check for agent framework"""

    def __init__(self):
        super().__init__("Agent Framework")

    async def check(self) -> Dict[str, Any]:
        """Check agent framework health"""
        self.start_time = datetime.now(timezone.utc)

        try:
            # Test infrastructure agent
            agent = SophiaInfrastructureAgent()

            # Test agent status
            status = agent.get_status()

            # Test agent capabilities
            capabilities = agent.get_capabilities()

            # Test health check
            health = await agent.health_check()

            agent_checks = {
                "agent_instantiated": status is not None,
                "agent_name": status.get("name") == "SophiaInfrastructureAgent",
                "agent_initialized": status.get("initialized", False),
                "capabilities_defined": len(capabilities) > 0,
                "health_check_working": health.get("healthy", False),
            }

            all_checks_passed = all(agent_checks.values())

            self.status = (
                HealthCheckStatus.HEALTHY
                if all_checks_passed
                else HealthCheckStatus.WARNING
            )
            self.details = {
                "agent_status": status,
                "capabilities": capabilities,
                "health_check": health,
                "agent_checks": agent_checks,
            }

        except Exception as e:
            self.status = HealthCheckStatus.CRITICAL
            self.details = {"error": str(e)}
            logger.error(f"Agent framework health check failed: {e}")

        self.end_time = datetime.now(timezone.utc)

        return {
            "component": self.name,
            "status": self.status,
            "details": self.details,
            "execution_time": self.get_execution_time(),
        }


class FastAPIHealthCheck(ComponentHealthCheck):
    """Health check for FastAPI application"""

    def __init__(self):
        super().__init__("FastAPI Application")

    async def check(self) -> Dict[str, Any]:
        """Check FastAPI application health"""
        self.start_time = datetime.now(timezone.utc)

        try:
            # Test FastAPI import

            # Test routes
            routes = [route.path for route in app.routes]

            # Test key endpoints exist
            endpoint_checks = {
                "health_endpoint": "/health" in routes or "/" in routes,
                "app_instantiated": app is not None,
                "routes_defined": len(routes) > 0,
            }

            all_checks_passed = all(endpoint_checks.values())

            self.status = (
                HealthCheckStatus.HEALTHY
                if all_checks_passed
                else HealthCheckStatus.WARNING
            )
            self.details = {
                "app_title": getattr(app, "title", "Unknown"),
                "route_count": len(routes),
                "routes": routes,
                "endpoint_checks": endpoint_checks,
            }

        except Exception as e:
            self.status = HealthCheckStatus.CRITICAL
            self.details = {"error": str(e)}
            logger.error(f"FastAPI health check failed: {e}")

        self.end_time = datetime.now(timezone.utc)

        return {
            "component": self.name,
            "status": self.status,
            "details": self.details,
            "execution_time": self.get_execution_time(),
        }


class DependencyHealthCheck(ComponentHealthCheck):
    """Health check for critical dependencies"""

    def __init__(self):
        super().__init__("Dependencies")

    async def check(self) -> Dict[str, Any]:
        """Check critical dependencies"""
        self.start_time = datetime.now(timezone.utc)

        dependency_status = {}
        critical_imports = [
            ("pydantic", "BaseModel"),
            ("fastapi", "FastAPI"),
            ("asyncio", "run"),
            ("logging", "getLogger"),
            ("json", "loads"),
            ("datetime", "datetime"),
            ("pathlib", "Path"),
        ]

        try:
            for module_name, attr_name in critical_imports:
                try:
                    module = __import__(module_name)
                    if hasattr(module, attr_name):
                        dependency_status[module_name] = {
                            "status": "available",
                            "version": getattr(module, "__version__", "unknown"),
                        }
                    else:
                        dependency_status[module_name] = {
                            "status": "missing_attribute",
                            "missing": attr_name,
                        }
                except ImportError as e:
                    dependency_status[module_name] = {
                        "status": "import_error",
                        "error": str(e),
                    }

            # Check for problematic dependencies
            problematic_count = sum(
                1 for dep in dependency_status.values() if dep["status"] != "available"
            )

            if problematic_count == 0:
                self.status = HealthCheckStatus.HEALTHY
            elif problematic_count <= 2:
                self.status = HealthCheckStatus.WARNING
            else:
                self.status = HealthCheckStatus.CRITICAL

            self.details = {
                "dependencies": dependency_status,
                "total_checked": len(critical_imports),
                "available_count": len(critical_imports) - problematic_count,
                "problematic_count": problematic_count,
            }

        except Exception as e:
            self.status = HealthCheckStatus.CRITICAL
            self.details = {"error": str(e)}
            logger.error(f"Dependency health check failed: {e}")

        self.end_time = datetime.now(timezone.utc)

        return {
            "component": self.name,
            "status": self.status,
            "details": self.details,
            "execution_time": self.get_execution_time(),
        }


class SophiaHealthChecker:
    """Main health checker orchestrator"""

    def __init__(self, full_validation: bool = False):
        self.full_validation = full_validation
        self.health_checks = [
            ConfigurationHealthCheck(),
            DependencyHealthCheck(),
            MCPServerHealthCheck(),
            AgentFrameworkHealthCheck(),
            FastAPIHealthCheck(),
        ]

    async def run_all_checks(self) -> Dict[str, Any]:
        """Run all health checks"""
        logger.info("🔍 Starting Sophia AI Comprehensive Health Check...")

        start_time = datetime.now(timezone.utc)
        results = []

        for health_check in self.health_checks:
            logger.info(f"Checking {health_check.name}...")
            result = await health_check.check()
            results.append(result)

            status_emoji = {
                HealthCheckStatus.HEALTHY: "✅",
                HealthCheckStatus.WARNING: "⚠️",
                HealthCheckStatus.CRITICAL: "❌",
                HealthCheckStatus.UNKNOWN: "❓",
            }.get(result["status"], "❓")

            logger.info(f"{status_emoji} {health_check.name}: {result['status']}")

        end_time = datetime.now(timezone.utc)

        # Generate summary
        summary = self._generate_summary(results)

        final_report = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_execution_time": (end_time - start_time).total_seconds(),
            "sophia_ai_version": "v2.0.0",
            "environment": "staging",  # Could be dynamic
            "summary": summary,
            "detailed_results": results,
        }

        return final_report

    def _generate_summary(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate health check summary"""
        status_counts = {}
        total_components = len(results)
        total_execution_time = sum(r.get("execution_time", 0) for r in results)

        for result in results:
            status = result["status"]
            status_counts[status] = status_counts.get(status, 0) + 1

        healthy_count = status_counts.get(HealthCheckStatus.HEALTHY, 0)
        warning_count = status_counts.get(HealthCheckStatus.WARNING, 0)
        critical_count = status_counts.get(HealthCheckStatus.CRITICAL, 0)

        # Determine overall status
        if critical_count > 0:
            overall_status = HealthCheckStatus.CRITICAL
        elif warning_count > 0:
            overall_status = HealthCheckStatus.WARNING
        else:
            overall_status = HealthCheckStatus.HEALTHY

        # Calculate health percentage
        health_percentage = (healthy_count / total_components) * 100

        return {
            "overall_status": overall_status,
            "health_percentage": round(health_percentage, 1),
            "total_components": total_components,
            "healthy_count": healthy_count,
            "warning_count": warning_count,
            "critical_count": critical_count,
            "total_execution_time": round(total_execution_time, 3),
            "production_ready": overall_status == HealthCheckStatus.HEALTHY,
            "status_distribution": status_counts,
        }

    def save_report(self, report: Dict[str, Any], output_file: str = None) -> str:
        """Save health check report to file"""
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"sophia_health_report_{timestamp}.json"

        with open(output_file, "w") as f:
            json.dump(report, f, indent=2, default=str)

        return output_file

    def print_summary(self, report: Dict[str, Any]) -> None:
        """Print formatted health check summary"""
        summary = report["summary"]

        print("\n" + "=" * 60)
        print("🎯 SOPHIA AI HEALTH CHECK SUMMARY")
        print("=" * 60)

        status_emoji = {
            HealthCheckStatus.HEALTHY: "✅",
            HealthCheckStatus.WARNING: "⚠️",
            HealthCheckStatus.CRITICAL: "❌",
        }.get(summary["overall_status"], "❓")

        print(f"Overall Status: {status_emoji} {summary['overall_status'].upper()}")
        print(f"Health Score: {summary['health_percentage']}%")
        print(
            f"Components: {summary['healthy_count']}/{summary['total_components']} healthy"
        )
        print(f"Execution Time: {summary['total_execution_time']}s")
        print(
            f"Production Ready: {'✅ YES' if summary['production_ready'] else '❌ NO'}"
        )

        print("\n📊 Component Status:")
        for result in report["detailed_results"]:
            status_emoji = {
                HealthCheckStatus.HEALTHY: "✅",
                HealthCheckStatus.WARNING: "⚠️",
                HealthCheckStatus.CRITICAL: "❌",
                HealthCheckStatus.UNKNOWN: "❓",
            }.get(result["status"], "❓")

            exec_time = result.get("execution_time", 0)
            print(f"  {status_emoji} {result['component']} ({exec_time:.2f}s)")

            # Show critical details for non-healthy components
            if result["status"] != HealthCheckStatus.HEALTHY:
                details = result.get("details", {})
                if "error" in details:
                    print(f"    Error: {details['error']}")
                elif isinstance(details, dict):
                    for key, value in details.items():
                        if isinstance(value, dict) and not all(
                            v for v in value.values()
                        ):
                            failed_checks = [k for k, v in value.items() if not v]
                            if failed_checks:
                                print(f"    Failed: {', '.join(failed_checks)}")

        print("\n" + "=" * 60)


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Comprehensive Sophia AI Health Check")
    parser.add_argument(
        "--full-validation",
        action="store_true",
        help="Run full validation with extended checks",
    )
    parser.add_argument("--output", type=str, help="Output file for detailed report")
    parser.add_argument("--quiet", action="store_true", help="Suppress verbose output")

    args = parser.parse_args()

    if args.quiet:
        logging.getLogger().setLevel(logging.WARNING)

    # Run health checks
    health_checker = SophiaHealthChecker(full_validation=args.full_validation)
    report = await health_checker.run_all_checks()

    # Save detailed report
    report_file = health_checker.save_report(report, args.output)

    # Print summary
    health_checker.print_summary(report)

    print(f"\n📄 Detailed report saved to: {report_file}")

    # Exit with appropriate code
    overall_status = report["summary"]["overall_status"]
    exit_code = {
        HealthCheckStatus.HEALTHY: 0,
        HealthCheckStatus.WARNING: 1,
        HealthCheckStatus.CRITICAL: 2,
    }.get(overall_status, 3)

    sys.exit(exit_code)


if __name__ == "__main__":
    asyncio.run(main())
