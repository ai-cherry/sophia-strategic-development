#!/usr/bin/env python3
"""
Fix Secret Sync Issues for Sophia AI Platform
This script validates and fixes secret synchronization between GitHub and Pulumi ESC
"""

import json
import logging
import os
import subprocess
from pathlib import Path

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class SecretSyncFixer:
    def __init__(self):
        self.pulumi_org = "scoobyjava-org"
        self.pulumi_env = "sophia-ai-production"
        self.env_path = f"{self.pulumi_org}/default/{self.pulumi_env}"

        # Critical secrets that must be present
        self.critical_secrets = {
            # AI Services
            "OPENAI_API_KEY": "openai_api_key",
            "ANTHROPIC_API_KEY": "anthropic_api_key",
            "GONG_ACCESS_KEY": "gong_access_key",
            "PINECONE_API_KEY": "pinecone_api_key",
            # Business Intelligence
            "HUBSPOT_ACCESS_TOKEN": "hubspot_access_token",
            "SLACK_BOT_TOKEN": "slack_bot_token",
            # Infrastructure
            "SNOWFLAKE_ACCOUNT": "snowflake_account",
            "SNOWFLAKE_USER": "snowflake_user",
            "SNOWFLAKE_PASSWORD": "snowflake_password",
            "LAMBDA_API_KEY": "lambda_api_key",
            "PULUMI_ACCESS_TOKEN": "pulumi_access_token",
        }

        # Known mapping issues to fix
        self.mapping_fixes = {
            "ASANA_API_TOKEN": "asana_access_token",
            "GH_API_TOKEN": "github_token",
            "NOTION_API_KEY": "notion_api_token",
            "LAMBDA_LABS_API_KEY": "lambda_api_key",  # Fix common naming confusion
        }

    def check_pulumi_login(self) -> bool:
        """Check if Pulumi is logged in"""
        try:
            result = subprocess.run(
                ["pulumi", "whoami"], capture_output=True, text=True, check=True
            )
            logger.info(f"✅ Pulumi logged in as: {result.stdout.strip()}")
            return True
        except subprocess.CalledProcessError:
            logger.error("❌ Not logged in to Pulumi")
            return False

    def get_current_esc_secrets(self) -> dict[str, bool]:
        """Get current secrets from Pulumi ESC"""
        try:
            result = subprocess.run(
                ["pulumi", "env", "get", self.env_path],
                capture_output=True,
                text=True,
                check=True,
            )

            # Parse the YAML output to find which secrets exist
            secrets = {}
            for line in result.stdout.split("\n"):
                if ":" in line and not line.strip().startswith("#"):
                    key = line.split(":")[0].strip()
                    if key:
                        secrets[key] = True

            return secrets
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to get ESC secrets: {e}")
            return {}

    def validate_critical_secrets(self) -> tuple[list[str], list[str]]:
        """Validate that critical secrets are present"""
        logger.info("\n🔍 Validating critical secrets...")

        esc_secrets = self.get_current_esc_secrets()
        present = []
        missing = []

        for _github_name, pulumi_name in self.critical_secrets.items():
            if pulumi_name in esc_secrets:
                present.append(pulumi_name)
                logger.info(f"✅ {pulumi_name} - Present in ESC")
            else:
                missing.append(pulumi_name)
                logger.warning(f"❌ {pulumi_name} - Missing from ESC")

        return present, missing

    def check_environment_variables(self) -> dict[str, str]:
        """Check which GitHub secrets are available as environment variables"""
        logger.info("\n🔍 Checking available environment variables...")

        available = {}
        for github_name in self.critical_secrets.keys():
            value = os.getenv(github_name)
            if value:
                available[github_name] = (
                    value[:10] + "..." if len(value) > 10 else value
                )
                logger.info(f"✅ {github_name} - Available in environment")
            else:
                logger.warning(f"❌ {github_name} - Not in environment")

        return available

    def sync_missing_secrets(self, missing: list[str]) -> int:
        """Attempt to sync missing secrets from environment variables"""
        logger.info("\n🔄 Attempting to sync missing secrets...")

        synced = 0
        for pulumi_name in missing:
            # Find the GitHub name for this Pulumi name
            github_name = None
            for gn, pn in self.critical_secrets.items():
                if pn == pulumi_name:
                    github_name = gn
                    break

            if not github_name:
                continue

            value = os.getenv(github_name)
            if not value:
                # Check mapping fixes
                for alt_name, mapped_name in self.mapping_fixes.items():
                    if mapped_name == pulumi_name:
                        value = os.getenv(alt_name)
                        if value:
                            github_name = alt_name
                            break

            if value:
                try:
                    cmd = [
                        "pulumi",
                        "env",
                        "set",
                        self.env_path,
                        pulumi_name,
                        value,
                        "--secret",
                    ]
                    subprocess.run(cmd, capture_output=True, text=True, check=True)
                    logger.info(f"✅ Synced {github_name} → {pulumi_name}")
                    synced += 1
                except subprocess.CalledProcessError as e:
                    logger.error(f"❌ Failed to sync {github_name}: {e}")

        return synced

    def create_fallback_env_file(self, missing: list[str]):
        """Create a fallback .env file for local development"""
        logger.info("\n📝 Creating fallback .env.template for missing secrets...")

        env_template = Path("backend/.env.template")

        with open(env_template, "w") as f:
            f.write("# Sophia AI Platform - Environment Variables Template\n")
            f.write("# Copy this to .env and fill in the values\n")
            f.write("# Generated by fix_secret_sync.py\n\n")

            f.write("# Critical Secrets (Required)\n")
            for github_name, pulumi_name in self.critical_secrets.items():
                if pulumi_name in missing:
                    f.write(f"{github_name}=your_{pulumi_name}_here\n")

            f.write("\n# Additional Secrets (Optional)\n")
            for github_name, pulumi_name in self.mapping_fixes.items():
                f.write(f"{github_name}=your_{pulumi_name}_here\n")

        logger.info(f"✅ Created {env_template}")

    def generate_report(
        self,
        present: list[str],
        missing: list[str],
        available_env: dict[str, str],
        synced: int,
    ):
        """Generate a comprehensive report"""
        report = {
            "timestamp": subprocess.run(
                ["date", "-u", "+%Y-%m-%dT%H:%M:%SZ"], capture_output=True, text=True
            ).stdout.strip(),
            "pulumi_environment": self.env_path,
            "critical_secrets": {
                "total": len(self.critical_secrets),
                "present": len(present),
                "missing": len(missing),
                "synced": synced,
            },
            "present_secrets": present,
            "missing_secrets": missing,
            "environment_variables": {
                "available": len(available_env),
                "names": list(available_env.keys()),
            },
            "recommendations": [],
        }

        # Add recommendations
        if missing:
            report["recommendations"].append(
                "Run GitHub Actions 'Sync Secrets to Pulumi ESC' workflow"
            )
            report["recommendations"].append(
                "Or manually add missing secrets to Pulumi ESC"
            )

        if len(available_env) < len(self.critical_secrets):
            report["recommendations"].append(
                "Ensure all GitHub secrets are available as environment variables"
            )

        # Save report
        with open("secret_sync_report.json", "w") as f:
            json.dump(report, f, indent=2)

        logger.info("\n📊 Secret Sync Report Summary:")
        logger.info(f"Total Critical Secrets: {report['critical_secrets']['total']}")
        logger.info(f"Present in ESC: {report['critical_secrets']['present']}")
        logger.info(f"Missing from ESC: {report['critical_secrets']['missing']}")
        logger.info(f"Successfully Synced: {report['critical_secrets']['synced']}")

        return report

    def run(self):
        """Run the secret sync fixer"""
        logger.info("🚀 Sophia AI Secret Sync Fixer")
        logger.info("=" * 60)

        # Check Pulumi login
        if not self.check_pulumi_login():
            logger.error("Please run: pulumi login")
            return False

        # Check environment variables
        available_env = self.check_environment_variables()

        # Validate critical secrets
        present, missing = self.validate_critical_secrets()

        # Sync missing secrets
        synced = 0
        if missing:
            synced = self.sync_missing_secrets(missing)

        # Create fallback env file
        if missing:
            self.create_fallback_env_file(missing)

        # Generate report
        self.generate_report(present, missing, available_env, synced)

        # Final status
        if not missing:
            logger.info("\n✅ All critical secrets are present in Pulumi ESC!")
            return True
        else:
            logger.warning(f"\n⚠️  {len(missing)} critical secrets still missing")
            logger.info("See secret_sync_report.json for details")
            return False


def main():
    fixer = SecretSyncFixer()
    success = fixer.run()
    exit(0 if success else 1)


if __name__ == "__main__":
    main()
