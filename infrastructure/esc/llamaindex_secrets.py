#!/usr/bin/env python
"""LlamaIndex Secrets Management for Sophia AI.

This script manages LlamaIndex API keys and other secrets using Pulumi ESC.
It syncs secrets between GitHub and Pulumi ESC, and provides utilities for
accessing these secrets in the application.

Usage:
    python infrastructure/esc/llamaindex_secrets.py [--sync-secrets]
"""import argparse

import logging
import os
import sys
from typing import Dict

# Add the project root to the Python path
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Import shared ESC utilities
from infrastructure.pulumi_esc import (
    check_secret_exists,
    get_secret,
    sync_github_to_esc,
)

# LlamaIndex secret names
LLAMAINDEX_SECRETS = [
    "LLAMA_API_KEY",
    "LLAMAINDEX_PINECONE_API_KEY",
    "LLAMAINDEX_WEAVIATE_API_KEY",
    "LLAMAINDEX_OPENAI_API_KEY",
]


def setup_llamaindex_secrets():
    """Set up LlamaIndex secrets in Pulumi ESC."""

    logger.info("Setting up LlamaIndex secrets in Pulumi ESC")

    # Check if secrets exist
    missing_secrets = []
    for secret_name in LLAMAINDEX_SECRETS:
        if not check_secret_exists(secret_name):
            missing_secrets.append(secret_name)

    if missing_secrets:
        logger.warning(f"Missing LlamaIndex secrets: {', '.join(missing_secrets)}")
        logger.info("Attempting to sync from GitHub secrets")

        # Sync from GitHub secrets
        sync_github_to_esc(missing_secrets)

        # Check again
        still_missing = []
        for secret_name in missing_secrets:
            if not check_secret_exists(secret_name):
                still_missing.append(secret_name)

        if still_missing:
            logger.error(f"Failed to sync secrets: {', '.join(still_missing)}")
            logger.info(
                "Please add these secrets manually or ensure they exist in GitHub"
            )
            return False

    logger.info("LlamaIndex secrets are set up in Pulumi ESC")
    return True


def get_llamaindex_secrets() -> Dict[str, str]:
    """Get all LlamaIndex secrets from Pulumi ESC."""logger.info("Getting LlamaIndex secrets from Pulumi ESC").

    secrets = {}
    for secret_name in LLAMAINDEX_SECRETS:
        secret_value = get_secret(secret_name)
        if secret_value:
            secrets[secret_name] = secret_value
        else:
            logger.warning(f"Secret {secret_name} not found in Pulumi ESC")

    return secrets


def update_env_file():
    """Update the .env file with LlamaIndex secrets."""logger.info("Updating .env file with LlamaIndex secrets").

    # Get secrets
    secrets = get_llamaindex_secrets()
    if not secrets:
        logger.error("No LlamaIndex secrets found")
        return False

    # Read existing .env file
    env_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        ".env",
    )
    env_content = ""
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            env_content = f.read()

    # Update or add secrets
    for secret_name, secret_value in secrets.items():
        if f"{secret_name}=" in env_content:
            # Update existing secret
            env_content = "\n".join(
                [
                    (
                        line
                        if not line.startswith(f"{secret_name}=")
                        else f"{secret_name}={secret_value}"
                    )
                    for line in env_content.split("\n")
                ]
            )
        else:
            # Add new secret
            env_content += f"\n{secret_name}={secret_value}"

    # Write updated .env file
    with open(env_path, "w") as f:
        f.write(env_content)

    logger.info("Updated .env file with LlamaIndex secrets")
    return True


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="LlamaIndex Secrets Management")
    parser.add_argument(
        "--sync-secrets",
        action="store_true",
        help="Sync secrets between GitHub and Pulumi ESC",
    )
    parser.add_argument(
        "--update-env",
        action="store_true",
        help="Update .env file with LlamaIndex secrets",
    )
    parser.add_argument(
        "--list-secrets", action="store_true", help="List available LlamaIndex secrets"
    )
    args = parser.parse_args()

    if args.sync_secrets:
        logger.info("Syncing LlamaIndex secrets between GitHub and Pulumi ESC")
        setup_llamaindex_secrets()

    if args.update_env:
        logger.info("Updating .env file with LlamaIndex secrets")
        update_env_file()

    if args.list_secrets:
        logger.info("Listing available LlamaIndex secrets")
        secrets = get_llamaindex_secrets()
        for secret_name in secrets:
            logger.info(f"Secret {secret_name} is available")

    if not any([args.sync_secrets, args.update_env, args.list_secrets]):
        logger.info("No action specified, running setup")
        setup_llamaindex_secrets()
        update_env_file()


if __name__ == "__main__":
    main()
