#!/usr/bin/env python3
"""
Sophia AI - GitHub Organization Secrets → Pulumi ESC Sync Script
This script synchronizes secrets from GitHub organization to Pulumi ESC
for the Sophia AI platform.
"""

import json
import logging
import os
import subprocess
import sys
from dataclasses import dataclass
from typing import Any

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class SyncResult:
    """Result of a secret sync operation."""

    secret_name: str
    success: bool
    error_message: str | None = None


class PulumiESCSync:
    """Synchronizes GitHub organization secrets to Pulumi ESC."""

    def __init__(self):
        self.pulumi_org = "scoobyjava-org"
        self.pulumi_env = "sophia-ai-production"
        self.env_path = f"{self.pulumi_org}/default/{self.pulumi_env}"

        # GitHub secrets to Pulumi ESC path mapping
        # CRITICAL: These GitHub secret names must match exactly what's in .github/workflows/sync_secrets.yml
        # CRITICAL: Pulumi paths must match what backend/core/auto_esc_config.py expects
                # TOP-LEVEL MAPPINGS (what backend actually reads)
        # CRITICAL FIX: Use top-level ESC keys, not nested values.sophia.*
        self.secret_mappings = {
            # Core AI Services (top-level keys)
            "OPENAI_API_KEY": "openai_api_key",
            "ANTHROPIC_API_KEY": "anthropic_api_key",
            "GONG_ACCESS_KEY": "gong_access_key",
            "PINECONE_API_KEY": "pinecone_api_key",
            
            # Snowflake (top-level keys)
            "SNOWFLAKE_ACCOUNT": "snowflake_account", 
            "SNOWFLAKE_USER": "snowflake_user",
            "SNOWFLAKE_PASSWORD": "snowflake_password",
            "SNOWFLAKE_ROLE": "snowflake_role",
            "SNOWFLAKE_WAREHOUSE": "snowflake_warehouse",
            "SNOWFLAKE_DATABASE": "snowflake_database",
            
            # Lambda Labs (top-level keys) - CRITICAL FIX
            "LAMBDA_API_KEY": "lambda_api_key",
            "LAMBDA_IP_ADDRESS": "lambda_ip_address",
            "LAMBDA_SSH_PRIVATE_KEY": "lambda_ssh_private_key",
            
            # Business Intelligence (top-level keys)
            "HUBSPOT_ACCESS_TOKEN": "hubspot_access_token",
            "SLACK_BOT_TOKEN": "slack_bot_token",
            "LINEAR_API_KEY": "linear_api_key", 
            "NOTION_API_KEY": "notion_api_key",
            
            # Additional high-priority services
            "VERCEL_ACCESS_TOKEN": "vercel_access_token",
            "PORTKEY_API_KEY": "portkey_api_key",
            "OPENROUTER_API_KEY": "openrouter_api_key",
        }

    def validate_prerequisites(self) -> bool:
        """Validate that all prerequisites are met."""
        logger.info("🔍 Validating prerequisites...")

        # Check Pulumi access token
        if not os.getenv("PULUMI_ACCESS_TOKEN"):
            logger.error("❌ PULUMI_ACCESS_TOKEN not set")
            return False

        # Check if Pulumi CLI is available
        try:
            result = subprocess.run(
                ["pulumi", "version"], capture_output=True, text=True, check=True
            )
            logger.info(f"✅ Pulumi CLI available: {result.stdout.strip()}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.error("❌ Pulumi CLI not available")
            return False

        # Test Pulumi login
        try:
            subprocess.run(
                ["pulumi", "whoami"], capture_output=True, text=True, check=True
            )
            logger.info("✅ Pulumi authentication successful")
        except subprocess.CalledProcessError:
            logger.error("❌ Pulumi authentication failed")
            return False

        return True

    def sync_secret(self, github_secret: str, pulumi_path: str) -> SyncResult:
        """Sync a single secret from GitHub to Pulumi ESC."""
        value = os.getenv(github_secret)

        if not value:
            return SyncResult(
                secret_name=github_secret,
                success=False,
                error_message="Secret not found in environment variables",
            )

        try:
            cmd = [
                "pulumi",
                "env",
                "set",
                self.env_path,
                pulumi_path,
                value,
                "--secret",
            ]

            subprocess.run(cmd, capture_output=True, text=True, check=True)

            logger.info(f"✅ Synced: {github_secret} → {pulumi_path}")
            return SyncResult(secret_name=github_secret, success=True)

        except subprocess.CalledProcessError as e:
            error_msg = f"Pulumi command failed: {e.stderr}"
            logger.error(f"❌ Failed to sync {github_secret}: {error_msg}")
            return SyncResult(
                secret_name=github_secret, success=False, error_message=error_msg
            )

    def sync_all_secrets(self) -> dict[str, SyncResult]:
        """Sync all configured secrets."""
        logger.info(f"🔄 Starting sync to Pulumi ESC environment: {self.env_path}")

        results = {}
        success_count = 0
        total_count = len(self.secret_mappings)

        for github_secret, pulumi_path in self.secret_mappings.items():
            result = self.sync_secret(github_secret, pulumi_path)
            results[github_secret] = result

            if result.success:
                success_count += 1

        logger.info(
            f"📊 Sync completed: {success_count}/{total_count} secrets synced successfully"
        )

        # Log failures
        failures = [name for name, result in results.items() if not result.success]
        if failures:
            logger.warning(f"⚠️  Failed to sync: {', '.join(failures)}")

        return results

    def generate_summary_report(self, results: dict[str, SyncResult]) -> dict[str, Any]:
        """Generate a summary report of the sync operation."""
        successful = [name for name, result in results.items() if result.success]
        failed = [name for name, result in results.items() if not result.success]

        report = {
            "sync_timestamp": subprocess.run(
                ["date", "-u", "+%Y-%m-%dT%H:%M:%SZ"], capture_output=True, text=True
            ).stdout.strip(),
            "pulumi_environment": self.env_path,
            "total_secrets": len(results),
            "successful_syncs": len(successful),
            "failed_syncs": len(failed),
            "success_rate": f"{(len(successful) / len(results) * 100):.1f}%",
            "successful_secrets": successful,
            "failed_secrets": [
                {"name": name, "error": results[name].error_message} for name in failed
            ],
        }

        return report


def main():
    """Main entry point."""
    logger.info("🚀 Sophia AI - GitHub Secrets → Pulumi ESC Sync")
    logger.info("=" * 50)

    sync = PulumiESCSync()

    # Validate prerequisites
    if not sync.validate_prerequisites():
        logger.error("❌ Prerequisites validation failed")
        sys.exit(1)

    # Perform sync
    results = sync.sync_all_secrets()

    # Generate and display report
    report = sync.generate_summary_report(results)

    logger.info("📋 Sync Summary Report:")
    logger.info("-" * 30)
    logger.info(f"Environment: {report['pulumi_environment']}")
    logger.info(f"Total Secrets: {report['total_secrets']}")
    logger.info(f"Successful: {report['successful_syncs']}")
    logger.info(f"Failed: {report['failed_syncs']}")
    logger.info(f"Success Rate: {report['success_rate']}")

    if report["failed_secrets"]:
        logger.info("\n❌ Failed Secrets:")
        for failed in report["failed_secrets"]:
            logger.info(f"  - {failed['name']}: {failed['error']}")

    # Write report to file for GitHub Actions artifact
    with open("sync_report.json", "w") as f:
        json.dump(report, f, indent=2)

    logger.info("\n✅ Sync completed! Report saved to sync_report.json")

    # Exit with error code if any secrets failed to sync
    if report["failed_syncs"] > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
