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
        # CRITICAL: These GitHub secret names must match exactly what's in GitHub Organization Secrets
        # CRITICAL: Pulumi paths must match what backend/core/auto_esc_config.py expects
        # Updated June 30, 2025 to match actual GitHub Organization Secrets
        self.secret_mappings = {
            # Core AI Services (Priority 1)
            "ANTHROPIC_API_KEY": "anthropic_api_key",
            "GONG_ACCESS_KEY": "gong_access_key", 
            "OPENAI_API_KEY": "openai_api_key",
            "PINECONE_API_KEY": "pinecone_api_key",
            
            # Gateway Services (Priority 1)
            "PORTKEY_API_KEY": "portkey_api_key",
            "OPENROUTER_API_KEY": "openrouter_api_key",
            
            # Business Intelligence (Priority 1)
            "HUBSPOT_ACCESS_TOKEN": "hubspot_access_token",
            "LINEAR_API_KEY": "linear_api_key",
            "ASANA_API_TOKEN": "asana_access_token",  # Note: GitHub has ASANA_API_TOKEN
            
            # Communication (Priority 1) 
            "SLACK_APP_TOKEN": "slack_app_token",
            "SLACK_BOT_TOKEN": "slack_bot_token",
            "SLACK_CLIENT_ID": "slack_client_id",
            "SLACK_CLIENT_SECRET": "slack_client_secret",
            "SLACK_SIGNING_SECRET": "slack_signing_secret",
            
            # Development Tools (Priority 1)
            "GH_API_TOKEN": "github_token",  # Note: mapping GH_API_TOKEN → github_token
            "FIGMA_PAT": "figma_pat",
            "NOTION_API_KEY": "notion_api_token",  # Note: mapping NOTION_API_KEY → notion_api_token
            
            # Infrastructure (Priority 1)
            "LAMBDA_API_KEY": "lambda_api_key",
            "LAMBDA_IP_ADDRESS": "lambda_ip_address", 
            "LAMBDA_SSH_PRIVATE_KEY": "lambda_ssh_private_key",
            
            # Snowflake Infrastructure (Complete)
            "SNOWFLAKE_ACCOUNT": "snowflake_account",
            "SNOWFLAKE_PASSWORD": "snowflake_password",
            "SNOWFLAKE_USER": "snowflake_user",
            "SNOWFLAKE_DATABASE_PROD": "snowflake_database",
            "SNOWFLAKE_WAREHOUSE_ANALYTICS": "snowflake_warehouse",
            "SNOWFLAKE_ROLE_PROD": "snowflake_role",
            
            # Extended AI Services
            "CODESTRAL_API_KEY": "codestral_api_key",
            "DEEPSEEK_API_KEY": "deepseek_api_key", 
            "HUGGINGFACE_API_TOKEN": "huggingface_api_token",
            "LANGCHAIN_API_KEY": "langchain_api_key",
            "LLAMA_API_KEY": "llama_api_key",
            "MISTRAL_API_KEY": "mistral_api_key",
            "PERPLEXITY_API_KEY": "perplexity_api_key",
            "TOGETHER_AI_API_KEY": "together_ai_api_key",
            "VENICE_AI_API_KEY": "venice_ai_api_key",
            "XAI_API_KEY": "xai_api_key",
            "GROQ_API_KEY": "groq_api_key",
            "COHERE_API_KEY": "cohere_api_key",
            "QWEN_API_KEY": "qwen_api_key",
            
            # Vector Databases
            "PINECONE_ENVIRONMENT": "pinecone_environment",
            "PINECONE_INDEX_NAME": "pinecone_index_name",
            "WEAVIATE_API_KEY": "weaviate_api_key",
            "WEAVIATE_GRPC_ENDPOINT": "weaviate_grpc_endpoint", 
            "WEAVIATE_REST_ENDPOINT": "weaviate_rest_endpoint",
            "WEAVIATE_URL": "weaviate_url",
            
            # Data Infrastructure
            "DATABASE_URL": "database_url",
            "REDIS_URL": "redis_url",
            "ESTUARY_ACCESS_TOKEN": "estuary_access_token",
            "AIRBYTE_ACCESS_TOKEN": "airbyte_access_token",
            
            # Cloud Infrastructure
            "PULUMI_ACCESS_TOKEN": "pulumi_access_token",
            "VERCEL_ACCESS_TOKEN": "vercel_access_token",
            "VERCEL_API_TOKEN": "vercel_api_token",
            
            # Observability & Monitoring
            "ARIZE_API_KEY": "arize_api_key",
            "ARIZE_SPACE_ID": "arize_space_id",
            "GRAFANA_PASSWORD": "grafana_password",
            "GRAFANA_URL": "grafana_url", 
            "GRAFANA_USERNAME": "grafana_username",
            "PROMETHEUS_URL": "prometheus_url",
            "SENTRY_DSN": "sentry_dsn",
            
            # Research & Data Collection
            "APIFY_API_TOKEN": "apify_api_token",
            "BRAVE_API_KEY": "brave_api_key",
            "EXA_API_KEY": "exa_api_key",
            "SERP_API_KEY": "serp_api_key",
            "TAVILY_API_KEY": "tavily_api_key",
            "ZENROWS_API_KEY": "zenrows_api_key",
            "TWINGLY_API_KEY": "twingly_api_key",
            
            # Development & CI/CD
            "DOCKER_TOKEN": "docker_token",
            "DOCKER_PERSONAL_ACCESS_TOKEN": "docker_personal_access_token",
            "NPM_API_TOKEN": "npm_api_token",
            "RETOOL_API_TOKEN": "retool_api_token",
            "CODACY_API_TOKEN": "codacy_api_token",
            
            # Integration Platforms
            "PIPEDREAM_API_KEY": "pipedream_api_key",
            "N8N_API_KEY": "n8n_api_key",
            "KONG_ACCESS_TOKEN": "kong_access_token",
            
            # Business Tools
            "SALESFORCE_ACCESS_TOKEN": "salesforce_access_token",
            "APOLLO_API_KEY": "apollo_api_key",
            "PHANTOMBUSTER_API_KEY": "phantombuster_api_key",
            
            # Security & Encryption
            "API_SECRET_KEY": "api_secret_key",
            "ENCRYPTION_KEY": "encryption_key", 
            "JWT_SECRET": "jwt_secret",
            "BACKUP_ENCRYPTION_KEY": "backup_encryption_key",
            
            # Content & Media
            "ELEVENLABS_API_KEY": "elevenlabs_api_key",
            "STABILITY_API_KEY": "stability_api_key",
            "RECRAFT_API_KEY": "recraft_api_key",
            
            # Additional Services (Present in GitHub)
            "CREW_API_TOKEN": "crew_api_token",
            "BARDEEN_ID": "bardeen_id",
            "BROWSER_USE_API_KEY": "browser_use_api_key",
            "CONTINUE_API_KEY": "continue_api_key",
            "EDEN_API_KEY": "eden_api_key",
            "KONG_ORG_ID": "kong_org_id",
            "LANGSMITH_API_KEY": "langsmith_api_key",
            "MUREKA_API_KEY": "mureka_api_key",
            "NAMECHEAP_API_KEY": "namecheap_api_key",
            "PATRONUS_API_KEY": "patronus_api_key",
            "PRISMA_API_KEY": "prisma_api_key",
            "RAILWAY_API_TOKEN": "railway_api_token",
            "RESEMBLE_API_KEY": "resemble_api_key",
            "SLIDESPEAK_API_KEY": "slidespeak_api_key",
            "SOPHIA_AI_TOKEN": "sophia_ai_token",
            "SOURCEGRAPH_API_TOKEN": "sourcegraph_api_token",
            "TERRAFORM_API_TOKEN": "terraform_api_token",
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
