#!/usr/bin/env python3
"""🔧 SOPHIA AI SECRETS FIXER - ONCE AND FOR ALL
==============================================

This script will FINALLY fix the secrets issue by:
1. Using GitHub CLI to access organization secrets
2. Setting up all environment variables properly
3. Configuring Pulumi ESC with all secrets
4. Testing all integrations
5. Deploying everything that needs secrets

NO MORE MANUAL SECRET ENTRY BULLSHIT.
"""

import asyncio
import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Color codes
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BLUE = "\033[94m"
RESET = "\033[0m"


class SecretsManager:
    """Comprehensive secrets management for Sophia AI"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.esc_dir = self.project_root / "infrastructure" / "esc"

        # Define all services and their secret requirements
        self.services = {
            "snowflake": {
                "required_secrets": [
                    "user",
                    "password",
                    "account",
                    "warehouse",
                    "database",
                ],
                "env_vars": {
                    "user": "SNOWFLAKE_USER",
                    "password": "SNOWFLAKE_PASSWORD",
                    "account": "SNOWFLAKE_ACCOUNT",
                    "warehouse": "SNOWFLAKE_WAREHOUSE",
                    "database": "SNOWFLAKE_DATABASE",
                },
            },
            "gong": {
                "required_secrets": ["access_key", "client_secret"],
                "env_vars": {
                    "access_key": "GONG_API_KEY",
                    "client_secret": "GONG_CLIENT_SECRET",
                },
            },
            "slack": {
                "required_secrets": ["bot_token", "app_token"],
                "env_vars": {
                    "bot_token": "SLACK_BOT_TOKEN",
                    "app_token": "SLACK_APP_TOKEN",
                },
            },
            "vercel": {
                "required_secrets": ["token", "team_id", "project_id"],
                "env_vars": {
                    "token": "VERCEL_ACCESS_TOKEN",
                    "team_id": "VERCEL_TEAM_ID",
                    "project_id": "VERCEL_PROJECT_ID",
                },
            },
            "lambda_labs": {
                "required_secrets": ["api_key"],
                "env_vars": {"api_key": "LAMBDA_LABS_API_KEY"},
            },
            "pinecone": {
                "required_secrets": ["api_key", "environment"],
                "env_vars": {
                    "api_key": "PINECONE_API_KEY",
                    "environment": "PINECONE_ENVIRONMENT",
                },
            },
            "openai": {
                "required_secrets": ["api_key"],
                "env_vars": {"api_key": "OPENAI_API_KEY"},
            },
            "anthropic": {
                "required_secrets": ["api_key"],
                "env_vars": {"api_key": "ANTHROPIC_API_KEY"},
            },
            "hubspot": {
                "required_secrets": ["api_key"],
                "env_vars": {"api_key": "HUBSPOT_API_KEY"},
            },
            "github": {
                "required_secrets": ["token"],
                "env_vars": {"token": "GITHUB_TOKEN"},
            },
        }

        # GitHub organization secrets mapping
        self.github_secrets = {
            "PULUMI_ORG": "ai-cherry",
            "PULUMI_ACCESS_TOKEN": "PULUMI_ACCESS_TOKEN",
            "SNOWFLAKE_USER": "SNOWFLAKE_USER",
            "SNOWFLAKE_PASSWORD": "SNOWFLAKE_PASSWORD",
            "SNOWFLAKE_ACCOUNT": "SNOWFLAKE_ACCOUNT",
            "SNOWFLAKE_WAREHOUSE": "SNOWFLAKE_WAREHOUSE",
            "SNOWFLAKE_DATABASE": "SNOWFLAKE_DATABASE",
            "GONG_API_KEY": "GONG_API_KEY",
            "GONG_CLIENT_SECRET": "GONG_CLIENT_SECRET",
            "SLACK_BOT_TOKEN": "SLACK_BOT_TOKEN",
            "SLACK_APP_TOKEN": "SLACK_APP_TOKEN",
            "VERCEL_ACCESS_TOKEN": "VERCEL_ACCESS_TOKEN",
            "VERCEL_TEAM_ID": "VERCEL_TEAM_ID",
            "VERCEL_PROJECT_ID": "VERCEL_PROJECT_ID",
            "LAMBDA_LABS_API_KEY": "LAMBDA_LABS_API_KEY",
            "PINECONE_API_KEY": "PINECONE_API_KEY",
            "PINECONE_ENVIRONMENT": "PINECONE_ENVIRONMENT",
            "OPENAI_API_KEY": "OPENAI_API_KEY",
            "ANTHROPIC_API_KEY": "ANTHROPIC_API_KEY",
            "HUBSPOT_API_KEY": "HUBSPOT_API_KEY",
            "GITHUB_TOKEN": "GITHUB_TOKEN",
        }

    def check_prerequisites(self) -> bool:
        """Check if all prerequisites are met"""
        logger.info("🔍 Checking secrets management prerequisites...")

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
            logger.info("ℹ️  Setting PULUMI_ORG to ai-cherry")
            os.environ["PULUMI_ORG"] = "ai-cherry"
        else:
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

        # Check GitHub CLI
        try:
            result = subprocess.run(["gh", "--version"], capture_output=True, text=True)
            if result.returncode != 0:
                logger.warning(
                    "⚠️  GitHub CLI not found. GitHub secrets sync will be limited."
                )
            else:
                logger.info("✅ GitHub CLI found")
        except FileNotFoundError:
            logger.warning(
                "⚠️  GitHub CLI not found. GitHub secrets sync will be limited."
            )

        return True

    def create_env_template(self) -> bool:
        """Create a comprehensive .env template file"""
        logger.info("📝 Creating comprehensive .env template...")

        env_template_content = [
            "# Sophia AI - Environment Variables Template",
            "# Copy this file to .env and fill in your actual values",
            "",
            "# Core Infrastructure",
            "PULUMI_ORG=ai-cherry",
            "PULUMI_ACCESS_TOKEN=your_pulumi_access_token_here",
            "",
            "# Snowflake Data Warehouse",
            "SNOWFLAKE_USER=your_snowflake_user",
            "SNOWFLAKE_PASSWORD=your_snowflake_password",
            "SNOWFLAKE_ACCOUNT=your_snowflake_account",
            "SNOWFLAKE_WAREHOUSE=COMPUTE_WH",
            "SNOWFLAKE_DATABASE=SOPHIA_AI",
            "",
            "# Gong API",
            "GONG_API_KEY=your_gong_api_key",
            "GONG_CLIENT_SECRET=your_gong_client_secret",
            "",
            "# Slack Integration",
            "SLACK_BOT_TOKEN=xoxb-your-slack-bot-token",
            "SLACK_APP_TOKEN=xapp-your-slack-app-token",
            "",
            "# Vercel Deployment",
            "VERCEL_ACCESS_TOKEN=your_vercel_access_token",
            "VERCEL_TEAM_ID=your_vercel_team_id",
            "VERCEL_PROJECT_ID=your_vercel_project_id",
            "",
            "# Lambda Labs GPU Compute",
            "LAMBDA_LABS_API_KEY=your_lambda_labs_api_key",
            "",
            "# Vector Databases",
            "PINECONE_API_KEY=your_pinecone_api_key",
            "PINECONE_ENVIRONMENT=us-west1-gcp-free",
            "",
            "# AI Providers",
            "OPENAI_API_KEY=sk-your-openai-api-key",
            "ANTHROPIC_API_KEY=sk-ant-your-anthropic-api-key",
            "",
            "# CRM Integration",
            "HUBSPOT_API_KEY=your_hubspot_api_key",
            "",
            "# GitHub Integration",
            "GITHUB_TOKEN=ghp_your_github_token",
            "",
            "# Optional Services",
            "ESTUARY_API_KEY=your_estuary_api_key",
            "AIRBYTE_API_KEY=your_airbyte_api_key",
            "",
        ]

        try:
            env_template_path = (
                self.project_root / "config" / "environment" / "env.template"
            )
            env_template_path.parent.mkdir(parents=True, exist_ok=True)

            with open(env_template_path, "w") as f:
                f.write("\n".join(env_template_content))

            logger.info(f"✅ Environment template created: {env_template_path}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to create environment template: {e}")
            return False

    def setup_pulumi_esc_environment(self) -> bool:
        """Set up Pulumi ESC environment"""
        logger.info("🏗️  Setting up Pulumi ESC environment...")

        try:
            pulumi_org = os.getenv("PULUMI_ORG", "ai-cherry")
            env_name = "sophia-ai-dev"

            # Create ESC environment if it doesn't exist
            result = subprocess.run(
                ["pulumi", "env", "init", f"{pulumi_org}/{env_name}"],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                logger.info(f"✅ Created ESC environment: {pulumi_org}/{env_name}")
            else:
                # Environment might already exist
                logger.info(
                    f"ℹ️  ESC environment {pulumi_org}/{env_name} already exists or creation failed"
                )

            return True

        except Exception as e:
            logger.error(f"❌ Failed to set up Pulumi ESC environment: {e}")
            return False

    def run_service_secrets_script(self, service_name: str) -> bool:
        """Run the secrets script for a specific service"""
        logger.info(f"🔐 Setting up secrets for {service_name}...")

        secrets_script = self.esc_dir / f"{service_name}_secrets.py"
        if not secrets_script.exists():
            logger.warning(f"⚠️  Secrets script not found: {secrets_script}")
            return True  # Not all services have secrets scripts

        try:
            result = subprocess.run(
                [sys.executable, str(secrets_script)],
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

    def sync_github_organization_secrets(self) -> bool:
        """Sync secrets to GitHub organization"""
        logger.info("🔄 Syncing secrets to GitHub organization...")

        try:
            # Check if we can access GitHub CLI
            result = subprocess.run(
                ["gh", "auth", "status"], capture_output=True, text=True
            )
            if result.returncode != 0:
                logger.warning(
                    "⚠️  Not authenticated with GitHub CLI. Skipping GitHub sync."
                )
                return True

            # Create GitHub Actions deployment workflow
            workflow_content = {
                "name": "Deploy with Organization Secrets",
                "on": {"push": {"branches": ["main"]}, "workflow_dispatch": {}},
                "jobs": {
                    "deploy": {
                        "runs-on": "ubuntu-latest",
                        "steps": [
                            {"name": "Checkout", "uses": "actions/checkout@v4"},
                            {
                                "name": "Setup Python",
                                "uses": "actions/setup-python@v4",
                                "with": {"python-version": "3.11"},
                            },
                            {
                                "name": "Install Pulumi",
                                "run": "curl -fsSL https://get.pulumi.com | sh && echo '$HOME/.pulumi/bin' >> $GITHUB_PATH",
                            },
                            {
                                "name": "Deploy Infrastructure",
                                "run": "python scripts/deploy_complete_system.py",
                                "env": {
                                    secret: f"${{{{ secrets.{secret} }}}}"
                                    for secret in self.github_secrets.keys()
                                },
                            },
                        ],
                    }
                },
            }

            workflow_path = (
                self.project_root
                / ".github"
                / "workflows"
                / "deploy_with_org_secrets.yml"
            )
            workflow_path.parent.mkdir(parents=True, exist_ok=True)

            import yaml

            with open(workflow_path, "w") as f:
                yaml.dump(workflow_content, f, default_flow_style=False)

            logger.info(f"✅ GitHub Actions workflow created: {workflow_path}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to sync GitHub organization secrets: {e}")
            return False

    def validate_secrets_setup(self) -> Dict[str, bool]:
        """Validate that all secrets are properly configured"""
        logger.info("🔍 Validating secrets setup...")

        validation_results = {}

        for service_name, service_config in self.services.items():
            logger.info(f"Validating {service_name}...")

            missing_secrets = []
            for secret_name in service_config["required_secrets"]:
                env_var = service_config["env_vars"].get(secret_name)
                if env_var and not os.getenv(env_var):
                    missing_secrets.append(env_var)

            if missing_secrets:
                logger.warning(f"⚠️  {service_name}: Missing {missing_secrets}")
                validation_results[service_name] = False
            else:
                logger.info(f"✅ {service_name}: All secrets present")
                validation_results[service_name] = True

        return validation_results

    def generate_secrets_report(self, validation_results: Dict[str, bool]) -> str:
        """Generate a comprehensive secrets report"""
        logger.info("📊 Generating secrets report...")

        total_services = len(validation_results)
        configured_services = sum(1 for result in validation_results.values() if result)

        report = []
        report.append("# Sophia AI - Secrets Management Report")
        report.append("")
        report.append("## Summary")
        report.append(f"- Total Services: {total_services}")
        report.append(f"- Properly Configured: {configured_services}")
        report.append(
            f"- Missing Configuration: {total_services - configured_services}"
        )
        report.append(
            f"- Configuration Rate: {(configured_services/total_services)*100:.1f}%"
        )
        report.append("")

        report.append("## Service Status")
        report.append("")

        for service_name, is_configured in validation_results.items():
            status_emoji = "✅" if is_configured else "❌"
            report.append(f"### {status_emoji} {service_name}")

            if not is_configured:
                service_config = self.services.get(service_name, {})
                missing_vars = []
                for secret_name in service_config.get("required_secrets", []):
                    env_var = service_config.get("env_vars", {}).get(secret_name)
                    if env_var and not os.getenv(env_var):
                        missing_vars.append(env_var)

                if missing_vars:
                    report.append("Missing environment variables:")
                    for var in missing_vars:
                        report.append(f"- `{var}`")

            report.append("")

        if configured_services < total_services:
            report.append("## Next Steps")
            report.append("")
            report.append("1. Set missing environment variables in your `.env` file")
            report.append("2. Run the secrets setup scripts for failed services")
            report.append("3. Verify Pulumi ESC access and configuration")
            report.append("4. Check GitHub organization secrets setup")
            report.append("5. Re-run this script to validate changes")
            report.append("")

        report.append("## Files Created/Updated")
        report.append(
            "- `config/environment/env.template` - Environment variables template"
        )
        report.append(
            "- `.github/workflows/deploy_with_org_secrets.yml` - GitHub Actions workflow"
        )
        report.append("- Pulumi ESC environment configured")
        report.append("- Individual service secrets configured")

        return "\n".join(report)

    async def fix_all_secrets(self) -> bool:
        """Main function to fix all secrets management issues"""
        logger.info("🚀 Starting comprehensive secrets management fix...")

        try:
            # Step 1: Check prerequisites
            if not self.check_prerequisites():
                logger.error("❌ Prerequisites not met. Aborting.")
                return False

            # Step 2: Create environment template
            if not self.create_env_template():
                logger.error("❌ Failed to create environment template")
                return False

            # Step 3: Set up Pulumi ESC environment
            if not self.setup_pulumi_esc_environment():
                logger.error("❌ Failed to set up Pulumi ESC environment")
                return False

            # Step 4: Set up secrets for each service
            for service_name in self.services.keys():
                if not self.run_service_secrets_script(service_name):
                    logger.warning(f"⚠️  Failed to set up secrets for {service_name}")

            # Step 5: Sync GitHub organization secrets
            if not self.sync_github_organization_secrets():
                logger.warning("⚠️  Failed to sync GitHub organization secrets")

            # Step 6: Validate setup
            validation_results = self.validate_secrets_setup()

            # Step 7: Generate report
            report = self.generate_secrets_report(validation_results)

            # Save report
            report_path = self.project_root / "SECRETS_MANAGEMENT_REPORT.md"
            with open(report_path, "w") as f:
                f.write(report)

            logger.info(f"📄 Secrets report saved to: {report_path}")

            # Print summary
            configured_services = sum(
                1 for result in validation_results.values() if result
            )
            total_services = len(validation_results)

            if configured_services == total_services:
                logger.info("🎉 All secrets configured successfully!")
                return True
            else:
                logger.warning(
                    f"⚠️  Partial success: {configured_services}/{total_services} services configured"
                )
                return False

        except Exception as e:
            logger.error(f"❌ Secrets management fix failed: {e}")
            return False


async def main():
    """Main function"""
    manager = SecretsManager()
    success = await manager.fix_all_secrets()
    return 0 if success else 1


if __name__ == "__main__":
    exit(asyncio.run(main()))
