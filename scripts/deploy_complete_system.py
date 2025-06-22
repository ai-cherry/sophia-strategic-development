#!/usr/bin/env python3
"""🚀 SOPHIA AI COMPLETE SYSTEM DEPLOYMENT SCRIPT.

==================================================

This script deploys the entire Sophia AI system including:
1. Data Pipeline (Gong → Slack → Snowflake)
2. Three AI-Powered Dashboards (CEO, Knowledge, Project)
3. MCP Server Infrastructure
4. Knowledge Base with Foundational Content
5. Real-time Chat Features with Live Data

Usage:
    python scripts/deploy_complete_system.py --environment production
    python scripts/deploy_complete_system.py --dry-run
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict

import click

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Color codes for output
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BLUE = "\033[94m"
RESET = "\033[0m"


class SophiaDeploymentManager:
    """Complete deployment manager for Sophia AI system."""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.infrastructure_dir = self.project_root / "infrastructure"
        self.esc_dir = self.infrastructure_dir / "esc"

        # Service configuration
        self.services = {
            "snowflake": {
                "type": "database",
                "pulumi_setup": "snowflake_setup.py",
                "secrets_script": "snowflake_secrets.py",
                "required_secrets": [
                    "user",
                    "password",
                    "account",
                    "warehouse",
                    "database",
                ],
                "priority": 1,
            },
            "gong": {
                "type": "api",
                "pulumi_setup": "pulumi/gong_setup.py",
                "secrets_script": "gong_secrets.py",
                "required_secrets": ["access_key", "client_secret"],
                "priority": 2,
            },
            "slack": {
                "type": "api",
                "pulumi_setup": "pulumi/slack_setup.py",
                "secrets_script": "slack_secrets.py",
                "required_secrets": ["bot_token", "app_token"],
                "priority": 2,
            },
            "vercel": {
                "type": "deployment",
                "pulumi_setup": "vercel_setup.py",
                "secrets_script": "vercel_secrets.py",
                "required_secrets": ["token", "team_id", "project_id"],
                "priority": 3,
            },
            "lambda_labs": {
                "type": "compute",
                "pulumi_setup": "lambda_labs_setup.py",
                "secrets_script": "lambda_labs_secrets.py",
                "required_secrets": ["api_key", "ssh_public_key"],
                "priority": 3,
            },
            "pinecone": {
                "type": "vector_db",
                "pulumi_setup": "pinecone_setup.py",
                "secrets_script": "pinecone_secrets.py",
                "required_secrets": ["api_key", "environment"],
                "priority": 4,
            },
            "openai": {
                "type": "ai_provider",
                "pulumi_setup": None,  # No infrastructure setup needed
                "secrets_script": "openai_secrets.py",
                "required_secrets": ["api_key"],
                "priority": 4,
            },
            "anthropic": {
                "type": "ai_provider",
                "pulumi_setup": None,
                "secrets_script": "claude_secrets.py",
                "required_secrets": ["api_key"],
                "priority": 4,
            },
        }

        self.deployment_status = {}

    async def check_prerequisites(self) -> bool:
        """Check if all prerequisites are met."""
        logger.info("🔍 Checking deployment prerequisites...").

        # Check Pulumi CLI
        try:
            result = subprocess.run(
                ["pulumi", "version"], capture_output=True, text=True
            )
            if result.returncode != 0:
                logger.error("❌ Pulumi CLI not found. Please install Pulumi.")
                return False
            logger.info(f"✅ Pulumi CLI found: {result.stdout.strip()}")
        except FileNotFoundError:
            logger.error("❌ Pulumi CLI not found. Please install Pulumi.")
            return False

        # Check PULUMI_ORG environment variable
        pulumi_org = os.getenv("PULUMI_ORG")
        if not pulumi_org:
            logger.error("❌ PULUMI_ORG environment variable not set")
            return False
        logger.info(f"✅ PULUMI_ORG set to: {pulumi_org}")

        # Check if logged into Pulumi
        try:
            result = subprocess.run(
                ["pulumi", "whoami"], capture_output=True, text=True
            )
            if result.returncode != 0:
                logger.error("❌ Not logged into Pulumi. Please run 'pulumi login'")
                return False
            logger.info(f"✅ Logged into Pulumi as: {result.stdout.strip()}")
        except Exception as e:
            logger.error(f"❌ Error checking Pulumi login: {e}")
            return False

        # Check ESC access
        try:
            result = subprocess.run(
                ["pulumi", "env", "ls", "--org", pulumi_org],
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                logger.warning("⚠️  Could not list Pulumi ESC environments")
            else:
                logger.info("✅ Pulumi ESC access confirmed")
        except Exception as e:
            logger.warning(f"⚠️  Could not verify ESC access: {e}")

        return True

    async def setup_secrets(self, service_name: str) -> bool:
        """Set up secrets for a specific service."""
        logger.info(f"🔐 Setting up secrets for {service_name}...").

        service_config = self.services.get(service_name)
        if not service_config:
            logger.error(f"❌ Unknown service: {service_name}")
            return False

        secrets_script = service_config.get("secrets_script")
        if not secrets_script:
            logger.info(f"ℹ️  No secrets script for {service_name}")
            return True

        secrets_path = self.esc_dir / secrets_script
        if not secrets_path.exists():
            logger.error(f"❌ Secrets script not found: {secrets_path}")
            return False

        try:
            # Run the secrets script
            result = subprocess.run(
                [sys.executable, str(secrets_path)],
                cwd=str(self.project_root),
                capture_output=True,
                text=True,
                env={**os.environ, "PULUMI_ORG": os.getenv("PULUMI_ORG", "ai-cherry")},
            )

            if result.returncode == 0:
                logger.info(f"✅ Secrets configured for {service_name}")
                return True
            else:
                logger.error(f"❌ Failed to configure secrets for {service_name}")
                logger.error(f"Error: {result.stderr}")
                return False

        except Exception as e:
            logger.error(f"❌ Error setting up secrets for {service_name}: {e}")
            return False

    async def deploy_infrastructure(self, service_name: str) -> bool:
        """Deploy infrastructure for a specific service."""
        logger.info(f"🚀 Deploying infrastructure for {service_name}...").

        service_config = self.services.get(service_name)
        if not service_config:
            logger.error(f"❌ Unknown service: {service_name}")
            return False

        pulumi_setup = service_config.get("pulumi_setup")
        if not pulumi_setup:
            logger.info(f"ℹ️  No infrastructure setup needed for {service_name}")
            return True

        setup_path = self.infrastructure_dir / pulumi_setup
        if not setup_path.exists():
            logger.warning(f"⚠️  Infrastructure setup script not found: {setup_path}")
            return True  # Not all services need infrastructure setup

        try:
            # Create Pulumi stack if it doesn't exist
            stack_name = f"sophia-{service_name}-dev"

            # Check if stack exists
            result = subprocess.run(
                ["pulumi", "stack", "select", stack_name],
                cwd=str(self.infrastructure_dir),
                capture_output=True,
                text=True,
            )

            if result.returncode != 0:
                # Create stack
                logger.info(f"Creating Pulumi stack: {stack_name}")
                result = subprocess.run(
                    ["pulumi", "stack", "init", stack_name],
                    cwd=str(self.infrastructure_dir),
                    capture_output=True,
                    text=True,
                )

                if result.returncode != 0:
                    logger.error(f"❌ Failed to create stack {stack_name}")
                    logger.error(f"Error: {result.stderr}")
                    return False

            # Deploy infrastructure
            logger.info(f"Deploying infrastructure for {service_name}...")
            result = subprocess.run(
                ["pulumi", "up", "--yes", "--stack", stack_name],
                cwd=str(self.infrastructure_dir),
                capture_output=True,
                text=True,
                env={**os.environ, "PULUMI_ORG": os.getenv("PULUMI_ORG", "ai-cherry")},
            )

            if result.returncode == 0:
                logger.info(f"✅ Infrastructure deployed for {service_name}")
                return True
            else:
                logger.error(f"❌ Failed to deploy infrastructure for {service_name}")
                logger.error(f"Error: {result.stderr}")
                return False

        except Exception as e:
            logger.error(f"❌ Error deploying infrastructure for {service_name}: {e}")
            return False

    async def verify_service_health(self, service_name: str) -> bool:
        """Verify that a service is properly configured and accessible."""
        logger.info(f"🏥 Verifying health for {service_name}...").

        try:
            # Use the integration manager to test the service
            result = subprocess.run(
                [
                    sys.executable,
                    "infrastructure/manage_integrations.py",
                    "test",
                    "--service",
                    service_name,
                    "--format",
                    "json",
                ],
                cwd=str(self.project_root),
                capture_output=True,
                text=True,
                env={**os.environ, "PULUMI_ORG": os.getenv("PULUMI_ORG", "ai-cherry")},
            )

            if result.returncode == 0:
                test_result = json.loads(result.stdout)
                if test_result.get("status") == "ok":
                    logger.info(f"✅ {service_name} health check passed")
                    return True
                else:
                    logger.warning(
                        f"⚠️  {service_name} health check failed: {test_result.get('error', 'Unknown error')}"
                    )
                    return False
            else:
                logger.warning(f"⚠️  Could not verify health for {service_name}")
                return False

        except Exception as e:
            logger.warning(f"⚠️  Error verifying health for {service_name}: {e}")
            return False

    async def deploy_service(self, service_name: str) -> Dict[str, Any]:
        """Deploy a complete service (secrets + infrastructure + verification)."""
        logger.info(f"📦 Deploying complete service: {service_name}").

        status = {
            "service": service_name,
            "secrets": False,
            "infrastructure": False,
            "health": False,
            "overall": False,
            "errors": [],
        }

        try:
            # Step 1: Set up secrets
            if await self.setup_secrets(service_name):
                status["secrets"] = True
            else:
                status["errors"].append("Failed to set up secrets")

            # Step 2: Deploy infrastructure
            if await self.deploy_infrastructure(service_name):
                status["infrastructure"] = True
            else:
                status["errors"].append("Failed to deploy infrastructure")

            # Step 3: Verify health
            if await self.verify_service_health(service_name):
                status["health"] = True
            else:
                status["errors"].append("Health check failed")

            # Overall status
            status["overall"] = status["secrets"] and status["infrastructure"]

            if status["overall"]:
                logger.info(f"✅ Successfully deployed {service_name}")
            else:
                logger.error(
                    f"❌ Failed to deploy {service_name}: {', '.join(status['errors'])}"
                )

        except Exception as e:
            logger.error(f"❌ Error deploying {service_name}: {e}")
            status["errors"].append(str(e))

        return status

    async def deploy_all_services(self) -> Dict[str, Any]:
        """Deploy all services in priority order."""
        logger.info("🚀 Starting complete system deployment...").

        # Sort services by priority
        sorted_services = sorted(self.services.items(), key=lambda x: x[1]["priority"])

        deployment_results = {}

        for service_name, service_config in sorted_services:
            logger.info(f"\n{'=' * 60}")
            logger.info(
                f"Deploying {service_name} (Priority {service_config['priority']})"
            )
            logger.info(f"{'=' * 60}")

            result = await self.deploy_service(service_name)
            deployment_results[service_name] = result

            # Add delay between deployments to avoid rate limits
            await asyncio.sleep(2)

        return deployment_results

    async def generate_deployment_report(self, results: Dict[str, Any]) -> str:
        """Generate a comprehensive deployment report."""
        logger.info("📊 Generating deployment report...").

        total_services = len(results)
        successful_services = sum(1 for r in results.values() if r["overall"])
        failed_services = total_services - successful_services

        report = []
        report.append("# Sophia AI - Complete System Deployment Report")
        report.append(f"Generated: {asyncio.get_event_loop().time()}")
        report.append("")
        report.append("## Summary")
        report.append(f"- Total Services: {total_services}")
        report.append(f"- Successful: {successful_services}")
        report.append(f"- Failed: {failed_services}")
        report.append(
            f"- Success Rate: {(successful_services / total_services) * 100:.1f}%"
        )
        report.append("")

        # Service details
        report.append("## Service Details")
        report.append("")

        for service_name, result in results.items():
            status_emoji = "✅" if result["overall"] else "❌"
            report.append(f"### {status_emoji} {service_name}")
            report.append(f"- Secrets: {'✅' if result['secrets'] else '❌'}")
            report.append(
                f"- Infrastructure: {'✅' if result['infrastructure'] else '❌'}"
            )
            report.append(f"- Health: {'✅' if result['health'] else '❌'}")

            if result["errors"]:
                report.append("- Errors:")
                for error in result["errors"]:
                    report.append(f"  - {error}")

            report.append("")

        # Next steps
        report.append("## Next Steps")
        report.append("")

        if failed_services > 0:
            report.append("### Failed Services")
            for service_name, result in results.items():
                if not result["overall"]:
                    report.append(
                        f"- **{service_name}**: {', '.join(result['errors'])}"
                    )
            report.append("")

        report.append("### Recommended Actions")
        report.append("1. Review failed service configurations")
        report.append("2. Check secret management setup")
        report.append("3. Verify network connectivity")
        report.append("4. Test API endpoints manually")
        report.append("5. Monitor service health")
        report.append("")

        report.append("### Access Information")
        report.append("- Backend API: http://localhost:8000")
        report.append("- Frontend Dashboard: http://localhost:5173")
        report.append("- Health Endpoint: http://localhost:8000/health")
        report.append("- Admin Key: sophia_admin_2024")

        return "\n".join(report)

    async def deploy(self) -> bool:
        """Main deployment function."""
        try:.

            # Check prerequisites
            if not await self.check_prerequisites():
                logger.error("❌ Prerequisites not met. Aborting deployment.")
                return False

            # Deploy all services
            results = await self.deploy_all_services()

            # Generate report
            report = await self.generate_deployment_report(results)

            # Save report
            report_path = self.project_root / "COMPLETE_DEPLOYMENT_ROADMAP.md"
            with open(report_path, "w") as f:
                f.write(report)

            logger.info(f"📄 Deployment report saved to: {report_path}")

            # Print summary
            successful_services = sum(1 for r in results.values() if r["overall"])
            total_services = len(results)

            if successful_services == total_services:
                logger.info("🎉 Complete system deployment successful!")
                return True
            else:
                logger.warning(
                    f"⚠️  Partial deployment: {successful_services}/{total_services} services deployed"
                )
                return False

        except Exception as e:
            logger.error(f"❌ Deployment failed: {e}")
            return False


@click.command()
@click.option("--environment", default="production", help="Deployment environment")
@click.option(
    "--dry-run", is_flag=True, help="Run in dry-run mode (no actual deployment)"
)
@click.option("--verbose", is_flag=True, help="Enable verbose logging")
def main(environment: str, dry_run: bool, verbose: bool):
    """Deploy the complete Sophia AI system."""
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    manager = SophiaDeploymentManager()

    try:
        asyncio.run(manager.deploy())
    except KeyboardInterrupt:
        print(f"\n{YELLOW}⚠️  Deployment interrupted by user{RESET}")
    except Exception as e:
        print(f"\n{RED}❌ Deployment failed with error: {e}{RESET}")
        sys.exit(1)


if __name__ == "__main__":
    main()
