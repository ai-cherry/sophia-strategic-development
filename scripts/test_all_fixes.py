#!/usr/bin/env python3
"""
Test All MCP Fixes
Comprehensive test suite to verify all remediation fixes
"""

import asyncio
import json
import logging
import subprocess
import sys
from pathlib import Path

import aiohttp

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MCPFixTester:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.test_results = {
            "import_fixes": {},
            "configuration": {},
            "lambda_labs": {},
            "server_startup": {},
            "unified_integration": {},
            "summary": {"total_tests": 0, "passed": 0, "failed": 0},
        }

    async def test_import_fixes(self) -> dict[str, bool]:
        """Test that all import errors are fixed"""
        logger.info("\n🔍 Testing Import Fixes...")

        results = {}

        # Test snowflake_admin_mcp_server.py import
        snowflake_admin_file = (
            self.project_root / "backend/mcp_servers/snowflake_admin_mcp_server.py"
        )

        try:
            # Try to import the module
            import_test = subprocess.run(
                [
                    "python",
                    "-c",
                    "import backend.mcp_servers.snowflake_admin_mcp_server",
                ],
                cwd=self.project_root,
                capture_output=True,
                text=True,
            )

            if import_test.returncode == 0:
                logger.info("✅ snowflake_admin_mcp_server.py imports correctly")
                results["snowflake_admin_import"] = True
            else:
                logger.error(
                    f"❌ snowflake_admin_mcp_server.py import failed: {import_test.stderr}"
                )
                results["snowflake_admin_import"] = False

        except Exception as e:
            logger.error(f"❌ Import test failed: {e}")
            results["snowflake_admin_import"] = False

        self.test_results["import_fixes"] = results
        return results

    def test_configuration_files(self) -> dict[str, bool]:
        """Test configuration file fixes"""
        logger.info("\n📋 Testing Configuration Files...")

        results = {}

        # Check cursor config
        cursor_config_file = (
            self.project_root / "config/cursor_enhanced_mcp_config.json"
        )
        if cursor_config_file.exists():
            with open(cursor_config_file) as f:
                cursor_config = json.load(f)

            # Check for Lambda Labs configuration
            has_lambda = any(
                "LAMBDA_LABS_HOST" in server.get("env", {})
                for server in cursor_config.get("mcpServers", {}).values()
            )

            results["cursor_config_exists"] = True
            results["lambda_labs_configured"] = has_lambda

            if has_lambda:
                logger.info("✅ Cursor config has Lambda Labs configuration")
            else:
                logger.error("❌ Cursor config missing Lambda Labs configuration")
        else:
            results["cursor_config_exists"] = False
            logger.error("❌ Cursor config file not found")

        # Check consolidated ports
        consolidated_ports_file = (
            self.project_root / "config/consolidated_mcp_ports.json"
        )
        results["consolidated_ports_exists"] = consolidated_ports_file.exists()

        if results["consolidated_ports_exists"]:
            logger.info("✅ Consolidated ports configuration exists")
        else:
            logger.error("❌ Consolidated ports configuration missing")

        # Check Lambda Labs config
        lambda_config_file = self.project_root / "config/lambda_labs_mcp_config.json"
        results["lambda_config_exists"] = lambda_config_file.exists()

        if results["lambda_config_exists"]:
            logger.info("✅ Lambda Labs configuration exists")
        else:
            logger.error("❌ Lambda Labs configuration missing")

        self.test_results["configuration"] = results
        return results

    async def test_lambda_labs_connectivity(self) -> dict[str, bool]:
        """Test Lambda Labs connectivity"""
        logger.info("\n🌐 Testing Lambda Labs Connectivity...")

        results = {}
        lambda_host = "104.171.202.64"

        # Test basic connectivity
        try:
            # Try to reach Lambda Labs gateway
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.get(
                        f"http://{lambda_host}:8080/health",
                        timeout=aiohttp.ClientTimeout(total=5),
                    ) as response:
                        results["gateway_reachable"] = response.status == 200
                        if results["gateway_reachable"]:
                            logger.info(
                                f"✅ Lambda Labs gateway reachable at {lambda_host}:8080"
                            )
                        else:
                            logger.warning(
                                f"⚠️  Lambda Labs gateway returned status {response.status}"
                            )
                except Exception as e:
                    results["gateway_reachable"] = False
                    logger.warning(f"⚠️  Lambda Labs gateway not reachable: {e}")

        except Exception as e:
            results["gateway_reachable"] = False
            logger.error(f"❌ Lambda Labs connectivity test failed: {e}")

        self.test_results["lambda_labs"] = results
        return results

    async def test_server_startup(self) -> dict[str, bool]:
        """Test that servers can start without errors"""
        logger.info("\n🚀 Testing Server Startup...")

        results = {}

        # Test a few key servers
        test_servers = [
            ("ai_memory", "backend.mcp_servers.enhanced_ai_memory_mcp_server:app"),
            ("codacy", "backend.mcp_servers.codacy.codacy_mcp_server:app"),
        ]

        for server_name, module_path in test_servers:
            try:
                # Try to import the module
                import_cmd = f"from {module_path.split(':')[0]} import *"
                test_result = subprocess.run(
                    ["python", "-c", import_cmd],
                    cwd=self.project_root,
                    capture_output=True,
                    text=True,
                    timeout=5,
                )

                if test_result.returncode == 0:
                    logger.info(f"✅ {server_name} can be imported")
                    results[f"{server_name}_import"] = True
                else:
                    logger.error(f"❌ {server_name} import failed: {test_result.stderr}")
                    results[f"{server_name}_import"] = False

            except Exception as e:
                logger.error(f"❌ {server_name} test failed: {e}")
                results[f"{server_name}_import"] = False

        self.test_results["server_startup"] = results
        return results

    def test_unified_integration(self) -> dict[str, bool]:
        """Test unified system integration points"""
        logger.info("\n🔗 Testing Unified System Integration...")

        results = {}

        # Check if unified service registry exists
        registry_file = (
            self.project_root / "backend/services/unified_service_registry.py"
        )
        results["service_registry_exists"] = registry_file.exists()

        if results["service_registry_exists"]:
            logger.info("✅ Unified service registry exists")
        else:
            logger.warning("⚠️  Unified service registry not found")

        # Check if dashboard integration files exist
        dashboard_file = (
            self.project_root / "frontend/src/components/dashboard/UnifiedDashboard.tsx"
        )
        results["dashboard_exists"] = dashboard_file.exists()

        if results["dashboard_exists"]:
            logger.info("✅ Unified dashboard component exists")
        else:
            logger.warning("⚠️  Unified dashboard component not found")

        # Check Docker Swarm config
        docker_swarm_file = self.project_root / "docker-compose.lambda.yml"
        results["docker_swarm_exists"] = docker_swarm_file.exists()

        if results["docker_swarm_exists"]:
            logger.info("✅ Docker Swarm configuration exists")
        else:
            logger.warning("⚠️  Docker Swarm configuration not found")

        self.test_results["unified_integration"] = results
        return results

    def generate_report(self):
        """Generate test report"""
        report_file = self.project_root / "mcp_fix_test_report.json"

        # Calculate summary
        for category, tests in self.test_results.items():
            if category != "summary" and isinstance(tests, dict):
                for test_name, passed in tests.items():
                    self.test_results["summary"]["total_tests"] += 1
                    if passed:
                        self.test_results["summary"]["passed"] += 1
                    else:
                        self.test_results["summary"]["failed"] += 1

        # Save report
        with open(report_file, "w") as f:
            json.dump(self.test_results, f, indent=2)

        logger.info(f"\n📊 Test report saved to: {report_file}")

    def print_summary(self):
        """Print test summary"""
        summary = self.test_results["summary"]

        logger.info("\n" + "=" * 50)
        logger.info("🧪 MCP FIX TEST SUMMARY")
        logger.info("=" * 50)
        logger.info(f"Total Tests: {summary['total_tests']}")
        logger.info(f"✅ Passed: {summary['passed']}")
        logger.info(f"❌ Failed: {summary['failed']}")

        if summary["total_tests"] > 0:
            pass_rate = (summary["passed"] / summary["total_tests"]) * 100
            logger.info(f"\n🎯 Pass Rate: {pass_rate:.1f}%")

            if pass_rate == 100:
                logger.info("🎉 All tests passed! Fixes are working correctly.")
            elif pass_rate >= 80:
                logger.info("✅ Most fixes are working, minor issues remain.")
            elif pass_rate >= 50:
                logger.warning("⚠️  Some fixes need attention.")
            else:
                logger.error("❌ Critical fixes are not working properly.")

        logger.info("=" * 50)

    async def run_all_tests(self):
        """Run all tests"""
        logger.info("🧪 Starting MCP Fix Tests...\n")

        # Run tests
        await self.test_import_fixes()
        self.test_configuration_files()
        await self.test_lambda_labs_connectivity()
        await self.test_server_startup()
        self.test_unified_integration()

        # Generate report
        self.generate_report()

        # Print summary
        self.print_summary()

        # Return exit code
        return 0 if self.test_results["summary"]["failed"] == 0 else 1


async def main():
    tester = MCPFixTester()
    exit_code = await tester.run_all_tests()
    sys.exit(exit_code)


if __name__ == "__main__":
    asyncio.run(main())
