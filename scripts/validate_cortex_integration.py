#!/usr/bin/env python3
"""
Validate Snowflake Cortex MCP Integration
Comprehensive validation of all components after deployment.
"""

import asyncio
import json
import sys
import time
from datetime import datetime

# Add backend to path
sys.path.append(".")

from prometheus_client import generate_latest

from backend.core.services.snowflake_cortex_adapter import (
    CortexAdapter,
    CortexQuery,
    CortexTask,
    ExecutionMode,
)
from backend.integrations.snowflake_mcp_client import SnowflakeMCPClient
from backend.monitoring.cortex_metrics import cortex_registry
from backend.security.pat_manager import get_pat_manager


class CortexIntegrationValidator:
    """Validates Cortex integration deployment"""

    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "checks": {},
            "summary": {"total": 0, "passed": 0, "failed": 0, "warnings": 0},
        }
        self.adapter = None
        self.mcp_client = None

    async def run_all_validations(self):
        """Run all validation checks"""
        print("🔍 Snowflake Cortex Integration Validation")
        print("=" * 60)

        # 1. Configuration validation
        await self.validate_configuration()

        # 2. PAT validation
        await self.validate_pat_management()

        # 3. Connection pool validation
        await self.validate_connection_pools()

        # 4. MCP server validation
        await self.validate_mcp_servers()

        # 5. Adapter functionality
        await self.validate_adapter_functionality()

        # 6. Metrics validation
        await self.validate_metrics()

        # 7. End-to-end tests
        await self.validate_end_to_end()

        # Summary
        self.print_summary()

        return self.results["summary"]["failed"] == 0

    async def validate_configuration(self):
        """Validate configuration is properly loaded"""
        print("\n📋 Validating Configuration...")

        try:
            from backend.core.auto_esc_config import (
                get_config_value,
                get_snowflake_config,
                get_snowflake_mcp_config,
            )

            # Check Snowflake config
            sf_config = get_snowflake_config()
            required_keys = ["account", "user", "password", "warehouse", "database"]
            missing = [k for k in required_keys if not sf_config.get(k)]

            if missing:
                self._record_result(
                    "snowflake_config", False, f"Missing keys: {missing}"
                )
            else:
                self._record_result(
                    "snowflake_config", True, "All required keys present"
                )

            # Check MCP config
            mcp_config = get_snowflake_mcp_config()
            if not mcp_config.get("pat"):
                self._record_result("mcp_config", False, "No PAT configured")
            else:
                self._record_result("mcp_config", True, "MCP configuration valid")

            # Check environment
            env = get_config_value("environment", "unknown")
            if env == "prod":
                self._record_result("environment", True, f"Environment: {env}")
            else:
                self._record_result(
                    "environment", False, f"Not in production: {env}", is_warning=True
                )

        except Exception as e:
            self._record_result("configuration", False, f"Error: {e!s}")

    async def validate_pat_management(self):
        """Validate PAT manager functionality"""
        print("\n🔐 Validating PAT Management...")

        try:
            pat_manager = get_pat_manager()

            # Check current PAT
            try:
                pat = await pat_manager.get_current_pat()
                self._record_result(
                    "pat_retrieval", True, f"PAT retrieved (length: {len(pat)})"
                )
            except Exception as e:
                self._record_result("pat_retrieval", False, f"Failed to get PAT: {e}")
                return

            # Check rotation status
            alerts = await pat_manager.check_rotation_needed()
            if alerts:
                critical = [a for a in alerts if a.severity.value == "critical"]
                if critical:
                    self._record_result(
                        "pat_rotation", False, f"{len(critical)} critical alerts"
                    )
                else:
                    self._record_result(
                        "pat_rotation",
                        True,
                        f"{len(alerts)} non-critical alerts",
                        is_warning=True,
                    )
            else:
                self._record_result("pat_rotation", True, "No rotation needed")

            # Generate report
            report = await pat_manager.generate_rotation_report()
            self._record_result(
                "pat_report",
                True,
                f"Report generated with {len(report['alerts'])} alerts",
            )

        except Exception as e:
            self._record_result("pat_management", False, f"Error: {e!s}")

    async def validate_connection_pools(self):
        """Validate connection pool functionality"""
        print("\n🏊 Validating Connection Pools...")

        try:
            from backend.core.services.snowflake_pool import SnowflakePoolManager

            pool_manager = SnowflakePoolManager()
            await pool_manager.initialize()

            # Check pool health
            health = await pool_manager.get_health()

            # Direct pool
            direct_health = health.get("direct", {})
            if direct_health.get("size", 0) > 0:
                self._record_result(
                    "direct_pool",
                    True,
                    f"Size: {direct_health['size']}, In use: {direct_health['in_use']}",
                )
            else:
                self._record_result("direct_pool", False, "No connections in pool")

            # MCP pool
            mcp_health = health.get("mcp", {})
            if mcp_health.get("client_healthy"):
                self._record_result(
                    "mcp_pool",
                    True,
                    f"Size: {mcp_health['size']}, In use: {mcp_health['in_use']}",
                )
            else:
                self._record_result(
                    "mcp_pool", False, "MCP client not healthy", is_warning=True
                )

            await pool_manager.close()

        except Exception as e:
            self._record_result("connection_pools", False, f"Error: {e!s}")

    async def validate_mcp_servers(self):
        """Validate MCP server connectivity"""
        print("\n🖥️  Validating MCP Servers...")

        try:
            # Create MCP client
            self.mcp_client = SnowflakeMCPClient()

            # Check health
            health = await self.mcp_client.health_check()
            if health["status"] == "healthy":
                self._record_result(
                    "mcp_health",
                    True,
                    f"Healthy (latency: {health.get('latency_ms', 'N/A')}ms)",
                )
            else:
                self._record_result(
                    "mcp_health", False, f"Unhealthy: {health.get('error', 'Unknown')}"
                )
                return

            # Check capabilities
            try:
                capabilities = await self.mcp_client.get_capabilities()
                cap_count = len(capabilities.get("tools", []))
                self._record_result(
                    "mcp_capabilities", True, f"{cap_count} capabilities available"
                )
            except Exception as e:
                self._record_result("mcp_capabilities", False, f"Error: {e!s}")

        except Exception as e:
            self._record_result("mcp_servers", False, f"Error: {e!s}")
            # MCP might not be deployed yet
            print("  ⚠️  MCP servers may not be deployed yet")

    async def validate_adapter_functionality(self):
        """Validate CortexAdapter functionality"""
        print("\n🔧 Validating Adapter Functionality...")

        try:
            # Create adapter
            self.adapter = CortexAdapter(
                execution_mode=ExecutionMode.AUTO, mcp_client=self.mcp_client
            )

            # Check health
            health = await self.adapter.health_check()
            self._record_result(
                "adapter_health",
                health["status"] in ["healthy", "degraded"],
                f"Status: {health['status']}",
            )

            # Test mode determination
            small_query = CortexQuery(
                text="Test", task=CortexTask(type="complete", max_tokens=10)
            )

            mode = await self.adapter._determine_execution_mode(small_query)
            self._record_result("mode_selection", True, f"Selected mode: {mode.value}")

        except Exception as e:
            self._record_result("adapter", False, f"Error: {e!s}")

    async def validate_metrics(self):
        """Validate metrics are being collected"""
        print("\n📊 Validating Metrics...")

        try:
            # Generate metrics
            metrics_output = generate_latest(cortex_registry).decode("utf-8")

            # Check for key metrics
            key_metrics = [
                "cortex_calls_total",
                "cortex_latency_seconds",
                "snowflake_pool_size",
                "cortex_info",
            ]

            found_metrics = []
            for metric in key_metrics:
                if metric in metrics_output:
                    found_metrics.append(metric)

            if len(found_metrics) == len(key_metrics):
                self._record_result(
                    "metrics", True, f"All {len(key_metrics)} metrics present"
                )
            else:
                missing = set(key_metrics) - set(found_metrics)
                self._record_result("metrics", False, f"Missing metrics: {missing}")

        except Exception as e:
            self._record_result("metrics", False, f"Error: {e!s}")

    async def validate_end_to_end(self):
        """Run end-to-end tests"""
        print("\n🚀 Running End-to-End Tests...")

        if not self.adapter:
            self._record_result("e2e_tests", False, "Adapter not initialized")
            return

        # Test 1: Simple completion
        try:
            query = CortexQuery(
                text="What is the capital of France?",
                task=CortexTask(type="complete", model="mistral-7b", max_tokens=20),
            )

            start_time = time.time()
            result = await self.adapter.run(query)
            latency = (time.time() - start_time) * 1000

            if "Paris" in result.response:
                self._record_result(
                    "e2e_complete",
                    True,
                    f"Correct response in {latency:.0f}ms via {result.execution_mode.value}",
                )
            else:
                self._record_result(
                    "e2e_complete",
                    False,
                    f"Unexpected response: {result.response[:50]}...",
                )

        except Exception as e:
            self._record_result("e2e_complete", False, f"Error: {e!s}")

        # Test 2: SQL generation (analyst)
        try:
            query = CortexQuery(
                text="Show me total revenue by month",
                task=CortexTask(type="analyst", model="arctic"),
                metadata={"context_tables": ["orders", "customers"]},
            )

            result = await self.adapter.run(query)

            if "SELECT" in result.response.upper():
                self._record_result(
                    "e2e_analyst",
                    True,
                    f"SQL generated via {result.execution_mode.value}",
                )
            else:
                self._record_result("e2e_analyst", False, "No SQL in response")

        except Exception as e:
            self._record_result("e2e_analyst", False, f"Error: {e!s}")

    def _record_result(
        self, check_name: str, success: bool, message: str, is_warning: bool = False
    ):
        """Record validation result"""
        status = "passed" if success else ("warning" if is_warning else "failed")

        self.results["checks"][check_name] = {
            "status": status,
            "message": message,
            "timestamp": datetime.now().isoformat(),
        }

        self.results["summary"]["total"] += 1
        if success and not is_warning:
            self.results["summary"]["passed"] += 1
            print(f"  ✅ {check_name}: {message}")
        elif is_warning:
            self.results["summary"]["warnings"] += 1
            print(f"  ⚠️  {check_name}: {message}")
        else:
            self.results["summary"]["failed"] += 1
            print(f"  ❌ {check_name}: {message}")

    def print_summary(self):
        """Print validation summary"""
        summary = self.results["summary"]

        print("\n" + "=" * 60)
        print("📈 Validation Summary")
        print("=" * 60)
        print(f"Total Checks: {summary['total']}")
        print(f"✅ Passed: {summary['passed']}")
        print(f"⚠️  Warnings: {summary['warnings']}")
        print(f"❌ Failed: {summary['failed']}")

        success_rate = (
            (summary["passed"] / summary["total"] * 100) if summary["total"] > 0 else 0
        )
        print(f"\nSuccess Rate: {success_rate:.1f}%")

        if summary["failed"] == 0:
            print("\n🎉 All critical checks passed! Cortex integration is ready.")
        else:
            print("\n⚠️  Some checks failed. Review the output above for details.")

        # Save results
        with open("cortex_validation_results.json", "w") as f:
            json.dump(self.results, f, indent=2)
        print("\nDetailed results saved to: cortex_validation_results.json")


async def main():
    """Main validation entry point"""
    validator = CortexIntegrationValidator()
    success = await validator.run_all_validations()

    # Cleanup
    if validator.adapter:
        await validator.adapter.pool_manager.close()
    if validator.mcp_client:
        await validator.mcp_client.close()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
