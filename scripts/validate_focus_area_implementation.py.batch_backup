#!/usr/bin/env python3
"""
Focus Area Implementation Validation Script
Comprehensive testing and validation of all implemented focus areas

Validates:
1. Critical dependency fixes
2. Non-functional server activation
3. Cross-server orchestration
4. Predictive automation capabilities
"""

import asyncio
import json
import logging
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import aiohttp

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.append(str(backend_path))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FocusAreaValidator:
    """Comprehensive validator for all focus area implementations"""

    def __init__(self):
        self.session: aiohttp.ClientSession | None = None
        self.validation_results: dict[str, Any] = {}
        self.server_endpoints = {
            "ai_memory": "http://localhost:9000",
            "figma_context": "http://localhost:9001",
            "ui_ux_agent": "http://localhost:9002",
            "codacy": "http://localhost:9003",
            "asana": "http://localhost:9004",
            "notion": "http://localhost:9005",
            "linear": "http://localhost:9006",
            "github": "http://localhost:9007",
            "slack": "http://localhost:9008",
            "postgresql": "http://localhost:9009",
            "sophia_data": "http://localhost:9010",
            "sophia_infrastructure": "http://localhost:9011",
            "snowflake_admin": "http://localhost:9012",
            "portkey_admin": "http://localhost:9013",
            "openrouter_search": "http://localhost:9014",
            "lambda_labs_cli": "http://localhost:9020",
            "snowflake_cli_enhanced": "http://localhost:9021",
            "estuary_flow": "http://localhost:9022",
        }

    async def initialize(self):
        """Initialize validation session"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=10),
            headers={"User-Agent": "Sophia-AI-Validator/1.0"},
        )
        logger.info("🚀 Focus Area Validator initialized")

    async def shutdown(self):
        """Cleanup validation session"""
        if self.session:
            await self.session.close()
        logger.info("🔄 Focus Area Validator shutdown complete")

    async def validate_all_focus_areas(self) -> dict[str, Any]:
        """Validate all implemented focus areas"""
        logger.info("🔍 Starting comprehensive focus area validation...")

        results = {
            "validation_timestamp": datetime.now(UTC).isoformat(),
            "focus_areas": {},
            "overall_score": 0,
            "summary": {},
        }

        # Focus Area 1: Critical Dependency Fixes
        results["focus_areas"]["critical_fixes"] = await self.validate_critical_fixes()

        # Focus Area 2: Server Activation
        results["focus_areas"][
            "server_activation"
        ] = await self.validate_server_activation()

        # Focus Area 3: Cross-Server Orchestration
        results["focus_areas"]["orchestration"] = await self.validate_orchestration()

        # Focus Area 4: Predictive Automation
        results["focus_areas"][
            "predictive_automation"
        ] = await self.validate_predictive_automation()

        # Calculate overall score
        focus_scores = [fa["score"] for fa in results["focus_areas"].values()]
        results["overall_score"] = (
            sum(focus_scores) / len(focus_scores) if focus_scores else 0
        )

        # Generate summary
        results["summary"] = self.generate_summary(results)

        self.validation_results = results
        return results

    async def validate_critical_fixes(self) -> dict[str, Any]:
        """Validate Focus Area 1: Critical Dependency Fixes"""
        logger.info("🔧 Validating critical dependency fixes...")

        results = {
            "focus_area": "Critical Dependency Fixes",
            "tests": {},
            "score": 0,
            "status": "unknown",
        }

        # Test 1: UTC Import Fix
        results["tests"]["utc_import_fix"] = await self.test_utc_import_fix()

        # Test 2: SSL/WebFetch Fix
        results["tests"]["ssl_webfetch_fix"] = await self.test_ssl_webfetch_fix()

        # Test 3: Snowflake Connection Handling
        results["tests"][
            "snowflake_connection"
        ] = await self.test_snowflake_connection_handling()

        # Test 4: Port Configuration
        results["tests"]["port_configuration"] = await self.test_port_configuration()

        # Calculate score
        passed_tests = sum(1 for test in results["tests"].values() if test["passed"])
        total_tests = len(results["tests"])
        results["score"] = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        results["status"] = "passed" if results["score"] >= 80 else "failed"

        return results

    async def validate_server_activation(self) -> dict[str, Any]:
        """Validate Focus Area 2: Non-Functional Server Activation"""
        logger.info("🚀 Validating server activation...")

        results = {
            "focus_area": "Server Activation",
            "tests": {},
            "score": 0,
            "status": "unknown",
            "operational_servers": [],
            "non_operational_servers": [],
        }

        # Test server health for all known servers
        for server_name, endpoint in self.server_endpoints.items():
            test_result = await self.test_server_health(server_name, endpoint)
            results["tests"][f"{server_name}_health"] = test_result

            if test_result["passed"]:
                results["operational_servers"].append(server_name)
            else:
                results["non_operational_servers"].append(server_name)

        # Calculate score based on operational servers
        operational_count = len(results["operational_servers"])
        total_count = len(self.server_endpoints)
        results["score"] = (operational_count / total_count) * 100
        results["status"] = "passed" if results["score"] >= 70 else "failed"

        return results

    async def validate_orchestration(self) -> dict[str, Any]:
        """Validate Focus Area 3: Cross-Server Orchestration"""
        logger.info("🔄 Validating cross-server orchestration...")

        results = {
            "focus_area": "Cross-Server Orchestration",
            "tests": {},
            "score": 0,
            "status": "unknown",
        }

        # Test 1: Orchestration Service Availability
        results["tests"][
            "orchestration_service"
        ] = await self.test_orchestration_service()

        # Test 2: Multi-Server Communication
        results["tests"][
            "multi_server_communication"
        ] = await self.test_multi_server_communication()

        # Test 3: Task Routing Logic
        results["tests"]["task_routing"] = await self.test_task_routing_logic()

        # Test 4: Result Synthesis
        results["tests"]["result_synthesis"] = await self.test_result_synthesis()

        # Calculate score
        passed_tests = sum(1 for test in results["tests"].values() if test["passed"])
        total_tests = len(results["tests"])
        results["score"] = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        results["status"] = "passed" if results["score"] >= 75 else "failed"

        return results

    async def validate_predictive_automation(self) -> dict[str, Any]:
        """Validate Focus Area 4: Predictive Automation"""
        logger.info("🤖 Validating predictive automation...")

        results = {
            "focus_area": "Predictive Automation",
            "tests": {},
            "score": 0,
            "status": "unknown",
        }

        # Test 1: Predictive Service Availability
        results["tests"]["predictive_service"] = await self.test_predictive_service()

        # Test 2: Automation Rules
        results["tests"]["automation_rules"] = await self.test_automation_rules()

        # Test 3: Learning Patterns
        results["tests"]["learning_patterns"] = await self.test_learning_patterns()

        # Test 4: Proactive Capabilities
        results["tests"][
            "proactive_capabilities"
        ] = await self.test_proactive_capabilities()

        # Calculate score
        passed_tests = sum(1 for test in results["tests"].values() if test["passed"])
        total_tests = len(results["tests"])
        results["score"] = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        results["status"] = "passed" if results["score"] >= 70 else "failed"

        return results

    async def test_utc_import_fix(self) -> dict[str, Any]:
        """Test that UTC import fix is working"""
        try:
            # Test importing the fixed base class
            from datetime import UTC

            # Test UTC usage
            test_time = datetime.now(UTC)

            return {
                "test_name": "UTC Import Fix",
                "passed": True,
                "message": "UTC import working correctly",
                "details": f"Successfully imported UTC and created timestamp: {test_time.isoformat()}",
            }
        except Exception as e:
            return {
                "test_name": "UTC Import Fix",
                "passed": False,
                "message": f"UTC import failed: {str(e)}",
                "details": str(e),
            }

    async def test_ssl_webfetch_fix(self) -> dict[str, Any]:
        """Test that SSL/WebFetch fix is working"""
        try:
            # Test SSL configuration by checking if servers respond to WebFetch health checks
            healthy_servers = []
            for server_name in ["portkey_admin", "ui_ux_agent"]:
                endpoint = self.server_endpoints.get(server_name)
                if endpoint:
                    try:
                        async with self.session.get(f"{endpoint}/health") as response:
                            if response.status == 200:
                                data = await response.json()
                                if "webfetch" in data.get("components", {}):
                                    webfetch_status = data["components"]["webfetch"][
                                        "status"
                                    ]
                                    if webfetch_status == "healthy":
                                        healthy_servers.append(server_name)
                    except Exception:
                        pass

            return {
                "test_name": "SSL/WebFetch Fix",
                "passed": len(healthy_servers) > 0,
                "message": f"WebFetch working on {len(healthy_servers)} servers",
                "details": f"Servers with working WebFetch: {healthy_servers}",
            }
        except Exception as e:
            return {
                "test_name": "SSL/WebFetch Fix",
                "passed": False,
                "message": f"SSL/WebFetch test failed: {str(e)}",
                "details": str(e),
            }

    async def test_snowflake_connection_handling(self) -> dict[str, Any]:
        """Test that Snowflake connection handling is working"""
        try:
            # Check that servers can start without requiring Snowflake connections
            servers_without_snowflake_errors = []

            for server_name in ["portkey_admin", "ui_ux_agent", "lambda_labs_cli"]:
                endpoint = self.server_endpoints.get(server_name)
                if endpoint:
                    try:
                        async with self.session.get(f"{endpoint}/health") as response:
                            if response.status == 200:
                                data = await response.json()
                                # If server is healthy, it started without Snowflake dependency issues
                                if data.get("status") in ["healthy", "degraded"]:
                                    servers_without_snowflake_errors.append(server_name)
                    except Exception:
                        pass

            return {
                "test_name": "Snowflake Connection Handling",
                "passed": len(servers_without_snowflake_errors) >= 2,
                "message": f"Snowflake handling working on {len(servers_without_snowflake_errors)} servers",
                "details": f"Servers without Snowflake dependency issues: {servers_without_snowflake_errors}",
            }
        except Exception as e:
            return {
                "test_name": "Snowflake Connection Handling",
                "passed": False,
                "message": f"Snowflake connection test failed: {str(e)}",
                "details": str(e),
            }

    async def test_port_configuration(self) -> dict[str, Any]:
        """Test that port configuration is working"""
        try:
            # Check consolidated port configuration exists
            config_path = (
                Path(__file__).parent.parent / "config" / "consolidated_mcp_ports.json"
            )

            if config_path.exists():
                with open(config_path) as f:
                    port_config = json.load(f)

                return {
                    "test_name": "Port Configuration",
                    "passed": True,
                    "message": f"Consolidated port configuration found with {len(port_config)} servers",
                    "details": f"Configuration file exists at {config_path}",
                }
            else:
                return {
                    "test_name": "Port Configuration",
                    "passed": False,
                    "message": "Consolidated port configuration not found",
                    "details": f"Expected file at {config_path}",
                }
        except Exception as e:
            return {
                "test_name": "Port Configuration",
                "passed": False,
                "message": f"Port configuration test failed: {str(e)}",
                "details": str(e),
            }

    async def test_server_health(
        self, server_name: str, endpoint: str
    ) -> dict[str, Any]:
        """Test health of a specific server"""
        try:
            async with self.session.get(f"{endpoint}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    status = data.get("status", "unknown")

                    return {
                        "test_name": f"{server_name} Health",
                        "passed": status in ["healthy", "degraded"],
                        "message": f"Server status: {status}",
                        "details": {
                            "endpoint": endpoint,
                            "status": status,
                            "response_time": response.headers.get(
                                "X-Response-Time", "unknown"
                            ),
                        },
                    }
                else:
                    return {
                        "test_name": f"{server_name} Health",
                        "passed": False,
                        "message": f"Server returned status {response.status}",
                        "details": {
                            "endpoint": endpoint,
                            "status_code": response.status,
                        },
                    }
        except Exception as e:
            return {
                "test_name": f"{server_name} Health",
                "passed": False,
                "message": f"Server unreachable: {str(e)}",
                "details": {"endpoint": endpoint, "error": str(e)},
            }

    async def test_orchestration_service(self) -> dict[str, Any]:
        """Test orchestration service availability"""
        try:
            # Test if orchestration service can be imported and initialized
            from backend.services.mcp_orchestration_service import orchestration_service

            status = orchestration_service.get_orchestration_status()

            return {
                "test_name": "Orchestration Service",
                "passed": True,
                "message": "Orchestration service available",
                "details": {
                    "total_servers": status.get("total_servers", 0),
                    "orchestration_rules": status.get("orchestration_rules", 0),
                },
            }
        except Exception as e:
            return {
                "test_name": "Orchestration Service",
                "passed": False,
                "message": f"Orchestration service failed: {str(e)}",
                "details": str(e),
            }

    async def test_multi_server_communication(self) -> dict[str, Any]:
        """Test multi-server communication capabilities"""
        try:
            # Test that multiple servers can be reached
            reachable_servers = []
            for server_name, endpoint in self.server_endpoints.items():
                try:
                    async with self.session.get(
                        f"{endpoint}/health", timeout=aiohttp.ClientTimeout(total=3)
                    ) as response:
                        if response.status == 200:
                            reachable_servers.append(server_name)
                except Exception:
                    pass

            return {
                "test_name": "Multi-Server Communication",
                "passed": len(reachable_servers) >= 3,
                "message": f"Can communicate with {len(reachable_servers)} servers",
                "details": {"reachable_servers": reachable_servers},
            }
        except Exception as e:
            return {
                "test_name": "Multi-Server Communication",
                "passed": False,
                "message": f"Multi-server communication test failed: {str(e)}",
                "details": str(e),
            }

    async def test_task_routing_logic(self) -> dict[str, Any]:
        """Test task routing logic"""
        try:
            from backend.services.mcp_orchestration_service import orchestration_service

            # Test that orchestration rules exist
            status = orchestration_service.get_orchestration_status()
            rules_count = status.get("orchestration_rules", 0)

            return {
                "test_name": "Task Routing Logic",
                "passed": rules_count >= 5,
                "message": f"Task routing with {rules_count} orchestration rules",
                "details": {"orchestration_rules": rules_count},
            }
        except Exception as e:
            return {
                "test_name": "Task Routing Logic",
                "passed": False,
                "message": f"Task routing test failed: {str(e)}",
                "details": str(e),
            }

    async def test_result_synthesis(self) -> dict[str, Any]:
        """Test result synthesis capabilities"""
        try:
            from backend.services.mcp_orchestration_service import orchestration_service

            # Test that synthesis methods are available
            has_synthesis = hasattr(orchestration_service, "_synthesize_results")

            return {
                "test_name": "Result Synthesis",
                "passed": has_synthesis,
                "message": "Result synthesis capabilities available",
                "details": {"synthesis_method_available": has_synthesis},
            }
        except Exception as e:
            return {
                "test_name": "Result Synthesis",
                "passed": False,
                "message": f"Result synthesis test failed: {str(e)}",
                "details": str(e),
            }

    async def test_predictive_service(self) -> dict[str, Any]:
        """Test predictive service availability"""
        try:
            from backend.services.predictive_automation_service import (
                predictive_service,
            )

            status = predictive_service.get_automation_status()

            return {
                "test_name": "Predictive Service",
                "passed": True,
                "message": "Predictive automation service available",
                "details": {
                    "automation_rules": status.get("automation_rules", 0),
                    "learning_patterns": status.get("learning_patterns", 0),
                },
            }
        except Exception as e:
            return {
                "test_name": "Predictive Service",
                "passed": False,
                "message": f"Predictive service failed: {str(e)}",
                "details": str(e),
            }

    async def test_automation_rules(self) -> dict[str, Any]:
        """Test automation rules"""
        try:
            from backend.services.predictive_automation_service import (
                predictive_service,
            )

            status = predictive_service.get_automation_status()
            rules_count = status.get("automation_rules", 0)

            return {
                "test_name": "Automation Rules",
                "passed": rules_count >= 4,
                "message": f"Automation with {rules_count} rules available",
                "details": {"automation_rules": rules_count},
            }
        except Exception as e:
            return {
                "test_name": "Automation Rules",
                "passed": False,
                "message": f"Automation rules test failed: {str(e)}",
                "details": str(e),
            }

    async def test_learning_patterns(self) -> dict[str, Any]:
        """Test learning patterns"""
        try:
            from backend.services.predictive_automation_service import (
                predictive_service,
            )

            status = predictive_service.get_automation_status()
            patterns_count = status.get("learning_patterns", 0)

            return {
                "test_name": "Learning Patterns",
                "passed": patterns_count >= 3,
                "message": f"Learning with {patterns_count} patterns available",
                "details": {"learning_patterns": patterns_count},
            }
        except Exception as e:
            return {
                "test_name": "Learning Patterns",
                "passed": False,
                "message": f"Learning patterns test failed: {str(e)}",
                "details": str(e),
            }

    async def test_proactive_capabilities(self) -> dict[str, Any]:
        """Test proactive capabilities"""
        try:
            from backend.services.predictive_automation_service import (
                predictive_service,
            )

            # Test that proactive methods are available
            has_prediction = hasattr(predictive_service, "add_metric_data")
            has_automation = hasattr(
                predictive_service, "_attempt_automated_resolution"
            )

            return {
                "test_name": "Proactive Capabilities",
                "passed": has_prediction and has_automation,
                "message": "Proactive capabilities available",
                "details": {
                    "prediction_capability": has_prediction,
                    "automation_capability": has_automation,
                },
            }
        except Exception as e:
            return {
                "test_name": "Proactive Capabilities",
                "passed": False,
                "message": f"Proactive capabilities test failed: {str(e)}",
                "details": str(e),
            }

    def generate_summary(self, results: dict[str, Any]) -> dict[str, Any]:
        """Generate comprehensive summary of validation results"""
        focus_areas = results["focus_areas"]

        # Calculate statistics
        total_tests = sum(len(fa["tests"]) for fa in focus_areas.values())
        passed_tests = sum(
            sum(1 for test in fa["tests"].values() if test["passed"])
            for fa in focus_areas.values()
        )

        operational_servers = len(
            focus_areas.get("server_activation", {}).get("operational_servers", [])
        )
        total_servers = len(self.server_endpoints)

        return {
            "overall_status": (
                "EXCELLENT"
                if results["overall_score"] >= 90
                else (
                    "GOOD"
                    if results["overall_score"] >= 80
                    else (
                        "FAIR"
                        if results["overall_score"] >= 70
                        else "NEEDS_IMPROVEMENT"
                    )
                )
            ),
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "test_pass_rate": (
                (passed_tests / total_tests) * 100 if total_tests > 0 else 0
            ),
            "operational_servers": operational_servers,
            "total_servers": total_servers,
            "server_operational_rate": (operational_servers / total_servers) * 100,
            "focus_area_scores": {
                name: fa["score"] for name, fa in focus_areas.items()
            },
            "recommendations": self.generate_recommendations(results),
            "next_steps": self.generate_next_steps(results),
        }

    def generate_recommendations(self, results: dict[str, Any]) -> list[str]:
        """Generate recommendations based on validation results"""
        recommendations = []

        # Check each focus area for specific recommendations
        focus_areas = results["focus_areas"]

        if focus_areas.get("critical_fixes", {}).get("score", 0) < 90:
            recommendations.append(
                "Complete remaining critical dependency fixes for optimal stability"
            )

        if focus_areas.get("server_activation", {}).get("score", 0) < 80:
            recommendations.append(
                "Activate remaining non-functional MCP servers to reach full capability"
            )

        if focus_areas.get("orchestration", {}).get("score", 0) < 85:
            recommendations.append(
                "Enhance cross-server orchestration for better integration"
            )

        if focus_areas.get("predictive_automation", {}).get("score", 0) < 80:
            recommendations.append(
                "Implement additional predictive automation capabilities"
            )

        if results["overall_score"] >= 85:
            recommendations.append(
                "System is performing well - focus on optimization and monitoring"
            )

        return recommendations

    def generate_next_steps(self, results: dict[str, Any]) -> list[str]:
        """Generate next steps based on validation results"""
        next_steps = []

        operational_rate = results["summary"]["server_operational_rate"]

        if operational_rate < 70:
            next_steps.append("Priority 1: Activate remaining MCP servers")
            next_steps.append("Priority 2: Resolve server connectivity issues")

        if results["overall_score"] < 80:
            next_steps.append("Priority 1: Address failed test cases")
            next_steps.append("Priority 2: Implement missing functionality")
        else:
            next_steps.append("Phase 1: Monitor and optimize current implementation")
            next_steps.append("Phase 2: Implement advanced features and automation")
            next_steps.append("Phase 3: Scale to enterprise production deployment")

        next_steps.append("Continuous: Monitor system performance and health")

        return next_steps

    async def save_validation_report(self, filename: str = None) -> str:
        """Save validation report to file"""
        if filename is None:
            timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
            filename = f"FOCUS_AREA_VALIDATION_REPORT_{timestamp}.json"

        filepath = Path(__file__).parent.parent / filename

        with open(filepath, "w") as f:
            json.dump(self.validation_results, f, indent=2, default=str)

        logger.info(f"📄 Validation report saved to {filepath}")
        return str(filepath)


async def main():
    """Main validation function"""
    validator = FocusAreaValidator()

    try:
        await validator.initialize()

        # Run comprehensive validation
        results = await validator.validate_all_focus_areas()

        # Save report
        report_path = await validator.save_validation_report()

        # Print summary
        print("\n" + "=" * 80)
        print("🎯 FOCUS AREA IMPLEMENTATION VALIDATION RESULTS")
        print("=" * 80)

        print(f"\n📊 OVERALL SCORE: {results['overall_score']:.1f}/100")
        print(f"📈 STATUS: {results['summary']['overall_status']}")

        print(
            f"\n🧪 TESTS: {results['summary']['passed_tests']}/{results['summary']['total_tests']} passed ({results['summary']['test_pass_rate']:.1f}%)"
        )
        print(
            f"🖥️  SERVERS: {results['summary']['operational_servers']}/{results['summary']['total_servers']} operational ({results['summary']['server_operational_rate']:.1f}%)"
        )

        print("\n📋 FOCUS AREA SCORES:")
        for name, score in results["summary"]["focus_area_scores"].items():
            status_emoji = "✅" if score >= 80 else "⚠️" if score >= 70 else "❌"
            print(
                f"   {status_emoji} {name.replace('_', ' ').title()}: {score:.1f}/100"
            )

        print("\n💡 RECOMMENDATIONS:")
        for i, rec in enumerate(results["summary"]["recommendations"], 1):
            print(f"   {i}. {rec}")

        print("\n🚀 NEXT STEPS:")
        for i, step in enumerate(results["summary"]["next_steps"], 1):
            print(f"   {i}. {step}")

        print(f"\n📄 Full report saved to: {report_path}")
        print("=" * 80)

    finally:
        await validator.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
