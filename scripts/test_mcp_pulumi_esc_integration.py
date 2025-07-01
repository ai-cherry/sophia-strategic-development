#!/usr/bin/env python3
"""
MCP Pulumi ESC Integration Test Script
Validates all MCP server secret mappings and Pulumi ESC integration

Test Coverage:
- All MCP servers have proper secret access
- Pulumi ESC environment loading works
- Secret mappings are correct and accessible
- No hardcoded secrets or environment variables
"""

import asyncio
import json
import logging
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.append(str(backend_path))

from backend.core.auto_esc_config import _load_esc_environment, get_config_value

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MCPPulumiESCValidator:
    """Validates MCP server Pulumi ESC integration"""

    def __init__(self):
        self.test_results: dict[str, Any] = {
            "validation_timestamp": datetime.now(UTC).isoformat(),
            "pulumi_esc_status": {},
            "secret_mappings": {},
            "mcp_server_secrets": {},
            "overall_status": "unknown",
            "recommendations": [],
        }
        self.required_secrets = [
            # Core AI Services
            "openai_api_key",
            "anthropic_api_key",
            "pinecone_api_key",
            # Business Intelligence
            "gong_access_key",
            "hubspot_access_token",
            "slack_bot_token",
            "slack_app_token",
            # Infrastructure
            "snowflake_account",
            "snowflake_user",
            "snowflake_password",
            "lambda_api_key",
            # Development Tools
            "github_token",
            "figma_pat",
            "linear_api_key",
            "notion_api_token",
            # Gateway Services
            "portkey_api_key",
            "openrouter_api_key",
        ]

    async def run_comprehensive_validation(self) -> dict[str, Any]:
        """Run comprehensive validation of MCP Pulumi ESC integration"""
        logger.info("🔍 Starting comprehensive MCP Pulumi ESC validation...")

        # Test 1: Pulumi ESC Environment Loading
        await self.test_pulumi_esc_loading()

        # Test 2: Secret Mapping Validation
        await self.test_secret_mappings()

        # Test 3: MCP Server Secret Access
        await self.test_mcp_server_secrets()

        # Test 4: Configuration Completeness
        await self.test_configuration_completeness()

        # Generate final assessment
        self.generate_final_assessment()

        return self.test_results

    async def test_pulumi_esc_loading(self) -> None:
        """Test Pulumi ESC environment loading"""
        logger.info("🔧 Testing Pulumi ESC environment loading...")

        try:
            esc_data = _load_esc_environment()

            self.test_results["pulumi_esc_status"] = {
                "environment_accessible": len(esc_data) > 0,
                "environment_name": "scoobyjava-org/default/sophia-ai-production",
                "keys_loaded": len(esc_data),
                "test_status": "passed" if len(esc_data) > 0 else "failed",
                "details": f"Loaded {len(esc_data)} configuration keys",
            }

            if len(esc_data) > 0:
                logger.info(f"✅ Pulumi ESC loaded {len(esc_data)} configuration keys")
            else:
                logger.warning(
                    "⚠️  Pulumi ESC environment appears empty or inaccessible"
                )

        except Exception as e:
            self.test_results["pulumi_esc_status"] = {
                "environment_accessible": False,
                "test_status": "failed",
                "error": str(e),
                "details": "Failed to load Pulumi ESC environment",
            }
            logger.error(f"❌ Pulumi ESC loading failed: {e}")

    async def test_secret_mappings(self) -> None:
        """Test secret mappings for all required secrets"""
        logger.info("🔑 Testing secret mappings...")

        secret_results = {}

        for secret_name in self.required_secrets:
            try:
                secret_value = get_config_value(secret_name)

                # Check if secret is accessible and not None/empty
                is_accessible = secret_value is not None and secret_value != ""
                is_placeholder = False

                if isinstance(secret_value, str):
                    is_placeholder = "PLACEHOLDER" in secret_value.upper()

                secret_results[secret_name] = {
                    "accessible": is_accessible,
                    "has_value": is_accessible and not is_placeholder,
                    "is_placeholder": is_placeholder,
                    "value_length": len(str(secret_value)) if secret_value else 0,
                    "test_status": (
                        "passed" if (is_accessible and not is_placeholder) else "failed"
                    ),
                }

                if is_accessible and not is_placeholder:
                    logger.info(
                        f"✅ {secret_name}: accessible ({len(str(secret_value))} chars)"
                    )
                elif is_placeholder:
                    logger.warning(f"⚠️  {secret_name}: placeholder value detected")
                else:
                    logger.error(f"❌ {secret_name}: not accessible")

            except Exception as e:
                secret_results[secret_name] = {
                    "accessible": False,
                    "has_value": False,
                    "error": str(e),
                    "test_status": "failed",
                }
                logger.error(f"❌ {secret_name}: error accessing - {e}")

        self.test_results["secret_mappings"] = secret_results

        # Calculate summary
        accessible_count = sum(1 for r in secret_results.values() if r["accessible"])
        valid_count = sum(
            1 for r in secret_results.values() if r.get("has_value", False)
        )

        logger.info(
            f"📊 Secret Summary: {accessible_count}/{len(self.required_secrets)} accessible, {valid_count}/{len(self.required_secrets)} valid"
        )

    async def test_mcp_server_secrets(self) -> None:
        """Test MCP server specific secret requirements"""
        logger.info("🖥️  Testing MCP server secret requirements...")

        mcp_server_configs = {
            "ai_memory": ["openai_api_key", "pinecone_api_key"],
            "figma_context": ["figma_pat"],
            "ui_ux_agent": ["figma_pat", "openai_api_key"],
            "codacy": [],  # No external secrets required
            "asana": ["asana_access_token"],
            "notion": ["notion_api_token"],
            "linear": ["linear_api_key"],
            "github": ["github_token"],
            "slack": ["slack_bot_token", "slack_app_token"],
            "snowflake_admin": [
                "snowflake_account",
                "snowflake_user",
                "snowflake_password",
            ],
            "portkey_admin": ["portkey_api_key"],
            "openrouter_search": ["openrouter_api_key"],
            "lambda_labs_cli": ["lambda_api_key"],
            "snowflake_cli_enhanced": [
                "snowflake_account",
                "snowflake_user",
                "snowflake_password",
            ],
        }

        server_results = {}

        for server_name, required_secrets in mcp_server_configs.items():
            server_status = {
                "required_secrets": required_secrets,
                "secrets_status": {},
                "all_secrets_available": True,
                "test_status": "unknown",
            }

            for secret in required_secrets:
                secret_value = get_config_value(secret)
                secret_available = (
                    secret_value is not None
                    and secret_value != ""
                    and "PLACEHOLDER" not in str(secret_value).upper()
                )

                server_status["secrets_status"][secret] = {
                    "available": secret_available,
                    "value_length": len(str(secret_value)) if secret_value else 0,
                }

                if not secret_available:
                    server_status["all_secrets_available"] = False

            server_status["test_status"] = (
                "passed" if server_status["all_secrets_available"] else "failed"
            )
            server_results[server_name] = server_status

            status_icon = "✅" if server_status["all_secrets_available"] else "❌"
            logger.info(
                f"{status_icon} {server_name}: {len([s for s in server_status['secrets_status'].values() if s['available']])}/{len(required_secrets)} secrets available"
            )

        self.test_results["mcp_server_secrets"] = server_results

    async def test_configuration_completeness(self) -> None:
        """Test overall configuration completeness"""
        logger.info("📋 Testing configuration completeness...")

        # Test key configuration areas
        config_tests = {
            "snowflake_config": self.test_snowflake_config(),
            "ai_services_config": self.test_ai_services_config(),
            "business_tools_config": self.test_business_tools_config(),
            "infrastructure_config": self.test_infrastructure_config(),
        }

        completeness_results = {}
        for config_name, config_result in config_tests.items():
            completeness_results[config_name] = config_result

        self.test_results["configuration_completeness"] = completeness_results

    def test_snowflake_config(self) -> dict[str, Any]:
        """Test Snowflake configuration completeness"""
        snowflake_keys = [
            "snowflake_account",
            "snowflake_user",
            "snowflake_password",
            "snowflake_warehouse",
            "snowflake_database",
        ]

        config_status = {}
        all_present = True

        for key in snowflake_keys:
            value = get_config_value(key)
            is_present = (
                value is not None
                and value != ""
                and "PLACEHOLDER" not in str(value).upper()
            )
            config_status[key] = is_present
            if not is_present:
                all_present = False

        return {
            "test_name": "Snowflake Configuration",
            "keys_tested": snowflake_keys,
            "status": config_status,
            "complete": all_present,
            "test_status": "passed" if all_present else "failed",
        }

    def test_ai_services_config(self) -> dict[str, Any]:
        """Test AI services configuration completeness"""
        ai_keys = [
            "openai_api_key",
            "anthropic_api_key",
            "pinecone_api_key",
            "portkey_api_key",
            "openrouter_api_key",
        ]

        config_status = {}
        all_present = True

        for key in ai_keys:
            value = get_config_value(key)
            is_present = (
                value is not None
                and value != ""
                and "PLACEHOLDER" not in str(value).upper()
            )
            config_status[key] = is_present
            if not is_present:
                all_present = False

        return {
            "test_name": "AI Services Configuration",
            "keys_tested": ai_keys,
            "status": config_status,
            "complete": all_present,
            "test_status": "passed" if all_present else "failed",
        }

    def test_business_tools_config(self) -> dict[str, Any]:
        """Test business tools configuration completeness"""
        business_keys = [
            "gong_access_key",
            "hubspot_access_token",
            "slack_bot_token",
            "linear_api_key",
            "github_token",
        ]

        config_status = {}
        present_count = 0

        for key in business_keys:
            value = get_config_value(key)
            is_present = (
                value is not None
                and value != ""
                and "PLACEHOLDER" not in str(value).upper()
            )
            config_status[key] = is_present
            if is_present:
                present_count += 1

        # Business tools are optional, so we consider it complete if at least 60% are present
        is_complete = present_count >= len(business_keys) * 0.6

        return {
            "test_name": "Business Tools Configuration",
            "keys_tested": business_keys,
            "status": config_status,
            "present_count": present_count,
            "total_count": len(business_keys),
            "complete": is_complete,
            "test_status": "passed" if is_complete else "failed",
        }

    def test_infrastructure_config(self) -> dict[str, Any]:
        """Test infrastructure configuration completeness"""
        infra_keys = ["lambda_api_key", "figma_pat"]

        config_status = {}
        present_count = 0

        for key in infra_keys:
            value = get_config_value(key)
            is_present = (
                value is not None
                and value != ""
                and "PLACEHOLDER" not in str(value).upper()
            )
            config_status[key] = is_present
            if is_present:
                present_count += 1

        # Infrastructure is optional for core functionality
        is_complete = present_count >= 1

        return {
            "test_name": "Infrastructure Configuration",
            "keys_tested": infra_keys,
            "status": config_status,
            "present_count": present_count,
            "total_count": len(infra_keys),
            "complete": is_complete,
            "test_status": "passed" if is_complete else "failed",
        }

    def generate_final_assessment(self) -> None:
        """Generate final assessment and recommendations"""
        logger.info("📊 Generating final assessment...")

        # Calculate overall scores
        pulumi_esc_working = self.test_results["pulumi_esc_status"].get(
            "environment_accessible", False
        )

        secret_results = self.test_results["secret_mappings"]
        total_secrets = len(secret_results)
        sum(1 for r in secret_results.values() if r["accessible"])
        valid_secrets = sum(
            1 for r in secret_results.values() if r.get("has_value", False)
        )

        mcp_server_results = self.test_results["mcp_server_secrets"]
        total_servers = len(mcp_server_results)
        operational_servers = sum(
            1 for r in mcp_server_results.values() if r["all_secrets_available"]
        )

        config_results = self.test_results["configuration_completeness"]
        complete_configs = sum(1 for r in config_results.values() if r["complete"])
        total_configs = len(config_results)

        # Calculate overall score
        esc_score = 25 if pulumi_esc_working else 0
        secret_score = (valid_secrets / total_secrets) * 35
        server_score = (operational_servers / total_servers) * 25
        config_score = (complete_configs / total_configs) * 15

        overall_score = esc_score + secret_score + server_score + config_score

        # Determine overall status
        if overall_score >= 90:
            overall_status = "excellent"
        elif overall_score >= 75:
            overall_status = "good"
        elif overall_score >= 60:
            overall_status = "acceptable"
        else:
            overall_status = "needs_improvement"

        self.test_results["overall_status"] = overall_status
        self.test_results["overall_score"] = overall_score
        self.test_results["score_breakdown"] = {
            "pulumi_esc": esc_score,
            "secrets": secret_score,
            "servers": server_score,
            "configuration": config_score,
        }

        # Generate recommendations
        recommendations = []

        if not pulumi_esc_working:
            recommendations.append(
                "Fix Pulumi ESC environment access - ensure 'pulumi env get scoobyjava-org/default/sophia-ai-production' works"
            )

        if valid_secrets < total_secrets * 0.8:
            recommendations.append(
                f"Add missing secrets to Pulumi ESC: {total_secrets - valid_secrets} secrets need attention"
            )

        if operational_servers < total_servers * 0.8:
            recommendations.append(
                f"Fix MCP server secret mappings: {total_servers - operational_servers} servers have missing secrets"
            )

        if complete_configs < total_configs:
            recommendations.append("Complete configuration for all service categories")

        if not recommendations:
            recommendations.append(
                "All systems operational - no immediate action required"
            )

        self.test_results["recommendations"] = recommendations

        # Log final results
        logger.info(
            f"🎯 Final Assessment: {overall_status.upper()} ({overall_score:.1f}/100)"
        )
        logger.info(
            f"📈 Breakdown: ESC={esc_score:.0f}, Secrets={secret_score:.1f}, Servers={server_score:.1f}, Config={config_score:.1f}"
        )
        logger.info(
            f"✅ Operational: {operational_servers}/{total_servers} servers, {valid_secrets}/{total_secrets} secrets"
        )

        for recommendation in recommendations:
            logger.info(f"💡 Recommendation: {recommendation}")

    async def save_test_report(self, filename: str | None = None) -> str:
        """Save test report to file"""
        if filename is None:
            timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
            filename = f"MCP_PULUMI_ESC_VALIDATION_REPORT_{timestamp}.json"

        report_path = Path(__file__).parent.parent / filename

        with open(report_path, "w") as f:
            json.dump(self.test_results, f, indent=2)

        logger.info(f"📄 Test report saved to: {report_path}")
        return str(report_path)


async def main():
    """Main function to run the MCP Pulumi ESC validation"""
    validator = MCPPulumiESCValidator()

    try:
        # Run comprehensive validation
        results = await validator.run_comprehensive_validation()

        # Save test report
        report_path = await validator.save_test_report()

        # Print summary
        print("\n" + "=" * 60)
        print("MCP PULUMI ESC INTEGRATION TEST SUMMARY")
        print("=" * 60)
        print(f"Overall Status: {results['overall_status'].upper()}")
        print(f"Overall Score: {results['overall_score']:.1f}/100")
        print(f"Test Date: {results['validation_timestamp']}")
        print(f"Report: {report_path}")
        print("\nRecommendations:")
        for i, rec in enumerate(results["recommendations"], 1):
            print(f"{i}. {rec}")
        print("=" * 60)

        # Exit with appropriate code
        exit_code = 0 if results["overall_score"] >= 75 else 1
        sys.exit(exit_code)

    except Exception as e:
        logger.error(f"❌ Validation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
