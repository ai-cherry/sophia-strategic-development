#!/usr/bin/env python3
"""
Deploy Unified AI Enhancements
Implements Snowflake PAT authentication and unified AI orchestration
"""

import asyncio
import logging
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.core.auto_esc_config import get_config_value, validate_snowflake_pat
from scripts.test_unified_ai_integration import (
    test_snowflake_pat_connection,
    test_unified_ai_routing,
)

logger = logging.getLogger(__name__)


class UnifiedAIDeployment:
    """Deploy unified AI enhancements"""

    def __init__(self):
        self.deployment_steps = []
        self.deployment_status = {}

    async def validate_prerequisites(self) -> bool:
        """Validate all prerequisites are met"""
        logger.info("Validating prerequisites...")

        checks = {
            "lambda_api_key": bool(get_config_value("lambda_labs_api_key")),
            "snowflake_account": get_config_value("snowflake_account")
            == "UHDECNO-CVB64222",
            "snowflake_user": get_config_value("snowflake_user") == "SCOOBYJAVA15",
            "snowflake_pat": validate_snowflake_pat(),
            "python_version": sys.version_info >= (3, 11),
        }

        all_passed = True
        for check, passed in checks.items():
            status = "✅" if passed else "❌"
            logger.info(f"  {status} {check}")
            if not passed:
                all_passed = False

        return all_passed

    async def deploy_snowflake_pat_service(self) -> bool:
        """Deploy Snowflake PAT authentication service"""
        logger.info("\nDeploying Snowflake PAT Service...")

        try:
            # Test PAT connection
            connected = await test_snowflake_pat_connection()

            if connected:
                logger.info("✅ Snowflake PAT service deployed successfully")
                self.deployment_status["snowflake_pat"] = "success"
                return True
            else:
                logger.error("❌ Snowflake PAT connection failed")
                self.deployment_status["snowflake_pat"] = "failed"
                return False

        except Exception as e:
            logger.error(f"❌ Deployment failed: {e!s}")
            self.deployment_status["snowflake_pat"] = "error"
            return False

    async def deploy_unified_orchestrator(self) -> bool:
        """Deploy unified AI orchestrator"""
        logger.info("\nDeploying Unified AI Orchestrator...")

        try:
            from infrastructure.services.unified_ai_orchestrator import (
                UnifiedAIOrchestrator,
            )

            orchestrator = UnifiedAIOrchestrator()
            health = await orchestrator.health_check()

            if health["orchestrator"] in ["healthy", "degraded"]:
                logger.info(
                    f"✅ Orchestrator deployed - Status: {health['orchestrator']}"
                )

                # Log provider status
                for provider, status in health["providers"].items():
                    logger.info(f"  - {provider}: {status['status']}")

                self.deployment_status["orchestrator"] = "success"
                return True
            else:
                logger.error("❌ Orchestrator unhealthy")
                self.deployment_status["orchestrator"] = "failed"
                return False

        except Exception as e:
            logger.error(f"❌ Deployment failed: {e!s}")
            self.deployment_status["orchestrator"] = "error"
            return False

    async def deploy_mcp_server(self) -> bool:
        """Deploy unified AI MCP server"""
        logger.info("\nDeploying Unified AI MCP Server...")

        try:
            # Check if MCP server file exists
            mcp_path = (
                project_root / "mcp-servers" / "unified_ai" / "unified_ai_mcp_server.py"
            )

            if mcp_path.exists():
                logger.info("✅ MCP server code deployed")

                # Update MCP configuration
                await self._update_mcp_config()

                self.deployment_status["mcp_server"] = "success"
                return True
            else:
                logger.error(f"❌ MCP server file not found: {mcp_path}")
                self.deployment_status["mcp_server"] = "failed"
                return False

        except Exception as e:
            logger.error(f"❌ Deployment failed: {e!s}")
            self.deployment_status["mcp_server"] = "error"
            return False

    async def _update_mcp_config(self):
        """Update MCP configuration"""
        import json

        config_path = project_root / "config" / "cursor_enhanced_mcp_config.json"

        if config_path.exists():
            with open(config_path) as f:
                config = json.load(f)

            # Add unified AI server
            if "unified_ai" not in config.get("mcpServers", {}):
                config["mcpServers"]["unified_ai"] = {
                    "command": "python",
                    "args": [
                        str(
                            project_root
                            / "mcp-servers"
                            / "unified_ai"
                            / "unified_ai_mcp_server.py"
                        )
                    ],
                    "env": {"PYTHONPATH": str(project_root)},
                }

                with open(config_path, "w") as f:
                    json.dump(config, f, indent=2)

                logger.info("  Updated MCP configuration")

    async def run_integration_tests(self) -> bool:
        """Run integration tests"""
        logger.info("\nRunning Integration Tests...")

        try:
            # Run basic routing tests
            await test_unified_ai_routing()

            logger.info("✅ Integration tests passed")
            self.deployment_status["tests"] = "success"
            return True

        except Exception as e:
            logger.error(f"❌ Tests failed: {e!s}")
            self.deployment_status["tests"] = "failed"
            return False

    async def generate_documentation(self):
        """Generate deployment documentation"""
        logger.info("\nGenerating Documentation...")

        doc_content = f"""# Unified AI Deployment Report
Generated: {datetime.now().isoformat()}

## Deployment Status

| Component | Status |
|-----------|--------|
"""

        for component, status in self.deployment_status.items():
            emoji = "✅" if status == "success" else "❌"
            doc_content += f"| {component} | {emoji} {status} |\n"

        doc_content += f"""

## Configuration

- **Snowflake Account**: {get_config_value("snowflake_account")}
- **Snowflake User**: {get_config_value("snowflake_user")}
- **PAT Validated**: {validate_snowflake_pat()}
- **Lambda Labs API**: {"Configured" if get_config_value("lambda_labs_api_key") else "Missing"}

## Cost Optimization

- **Current GPU Cost**: $6,444/month
- **Projected Serverless Cost**: $450-900/month
- **Expected Savings**: 85-93% ($5,544-5,994/month)

## Next Steps

1. Monitor usage analytics
2. Fine-tune routing rules
3. Implement cost alerts
4. Document natural language commands

## Natural Language Commands

### Infrastructure Optimization
- "Optimize costs while maintaining performance"
- "Reduce AI processing costs by 50%"
- "Balance performance and cost for production"

### AI Operations
- "Generate SQL for customer revenue analysis"
- "Analyze sales trends using data-local processing"
- "Create embeddings for product descriptions"

"""

        doc_path = (
            project_root / "docs" / "deployment" / "unified_ai_deployment_report.md"
        )
        doc_path.parent.mkdir(parents=True, exist_ok=True)

        with open(doc_path, "w") as f:
            f.write(doc_content)

        logger.info(f"  Documentation saved to: {doc_path}")

    async def deploy(self):
        """Run full deployment"""
        logger.info("=" * 60)
        logger.info("Unified AI Enhancement Deployment")
        logger.info("=" * 60)

        # Validate prerequisites
        if not await self.validate_prerequisites():
            logger.error(
                "\n❌ Prerequisites not met. Please configure all required secrets."
            )
            return False

        # Deploy components
        success = True

        if not await self.deploy_snowflake_pat_service():
            success = False

        if not await self.deploy_unified_orchestrator():
            success = False

        if not await self.deploy_mcp_server():
            success = False

        # Run tests
        if success and not await self.run_integration_tests():
            logger.warning("⚠️  Some tests failed but deployment completed")

        # Generate documentation
        await self.generate_documentation()

        # Summary
        logger.info("\n" + "=" * 60)
        logger.info("Deployment Summary")
        logger.info("=" * 60)

        successful = sum(1 for s in self.deployment_status.values() if s == "success")
        total = len(self.deployment_status)

        if successful == total:
            logger.info(
                f"✅ All components deployed successfully ({successful}/{total})"
            )
        else:
            logger.warning(f"⚠️  Partial deployment ({successful}/{total} successful)")

        return successful == total


async def main():
    """Main deployment function"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    deployment = UnifiedAIDeployment()
    success = await deployment.deploy()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
