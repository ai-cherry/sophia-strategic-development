#!/usr/bin/env python3
"""Sophia AI - Sync GitHub Secrets to Pulumi ESC
This script is designed to be run within a GitHub Actions environment.
It reads secrets from environment variables and sets them in Pulumi ESC.
"""

import logging
import os
import subprocess
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# This mapping should be kept in sync with the desired ESC structure
# It maps the Pulumi ESC path to the GitHub Secret name (which becomes the env var)
SECRET_MAPPINGS = {
    # AI Services
    "ai_services.openai_api_key": "OPENAI_API_KEY",
    "ai_services.anthropic_api_key": "ANTHROPIC_API_KEY",
    "ai_services.agno_api_key": "AGNO_API_KEY",
    "ai_services.huggingface_api_token": "HUGGINGFACE_API_TOKEN",
    "ai_services.langchain_api_key": "LANGCHAIN_API_KEY",
    "ai_services.portkey_api_key": "PORTKEY_API_KEY",
    # Add all other mappings here...
    "observability.arize_api_key": "ARIZE_API_KEY",
    "observability.arize_space_id": "ARIZE_SPACE_ID",
    "vector_databases.pinecone_api_key": "PINECONE_API_KEY",
    "business_intelligence.gong_access_key": "GONG_ACCESS_KEY",
    "communication.slack_bot_token": "SLACK_BOT_TOKEN",
    "data_infrastructure.snowflake_account": "SNOWFLAKE_ACCOUNT",
    "security.jwt_secret": "JWT_SECRET",
}


def run_command(command: list):
    """Run a shell command and handle errors."""
    logger.info(f"🔧 Running: {' '.join(command)} ...")
    try:
        process = subprocess.run(command, check=True, capture_output=True, text=True)
        if process.stdout:
            logger.info(process.stdout)
        if process.stderr:
            logger.warning(process.stderr)
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Command failed: {' '.join(command)}")
        logger.error(f"Exit Code: {e.returncode}")
        logger.error(f"Stderr: {e.stderr}")
        logger.error(f"Stdout: {e.stdout}")
        sys.exit(1)


def sync_secrets():
    """Reads secrets from env vars and syncs them to Pulumi ESC."""
    env_name = "scoobyjava-org/default/sophia-ai-production"
    logger.info(f"Starting sync for Pulumi ESC environment: {env_name}")

    secrets_synced = 0
    secrets_missing = 0

    for esc_path, secret_name in SECRET_MAPPINGS.items():
        secret_value = os.getenv(secret_name)

        if secret_value:
            logger.info(f"Found secret for '{secret_name}'. Syncing to '{esc_path}'.")
            # The secret value is passed via stdin for security
            command = ["pulumi", "env", "set", env_name, esc_path, "--secret"]
            try:
                subprocess.run(
                    command,
                    input=secret_value,
                    text=True,
                    check=True,
                    capture_output=True,
                )
                logger.info(f"✅ Successfully synced '{esc_path}'")
                secrets_synced += 1
            except subprocess.CalledProcessError as e:
                logger.error(f"❌ Failed to sync secret for {esc_path}: {e.stderr}")

        else:
            logger.warning(
                f"⚠️ Secret '{secret_name}' not found in environment. Skipping."
            )
            secrets_missing += 1

    print("\n" + "=" * 60)
    logger.info("🎉 Pulumi ESC Sync Complete!")
    print("=" * 60)
    logger.info(f"✅ Secrets Synced: {secrets_synced}")
    logger.info(f"⚠️ Secrets Missing in Environment: {secrets_missing}")
    print("=" * 60)

    if secrets_missing > 0:
        logger.warning("Some secrets were not found in the GitHub Actions environment.")
        logger.warning("Please ensure they are configured as organization secrets.")


if __name__ == "__main__":
    sync_secrets()
