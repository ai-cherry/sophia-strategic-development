"""Sophia AI - Intelligent GitHub to Pulumi ESC Sync.

This script is designed to be run within a GitHub Actions environment. It uses
the GitHub API to dynamically discover ALL organization-level secrets and
syncs them to a specified Pulumi ESC environment.

This removes the need to manually list secrets in the workflow file.
"""import logging

import os
import subprocess

import requests

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# --- Configuration ---
PULUMI_ESC_ENV = "scoobyjava-org/default/sophia-ai-production"
GITHUB_ORG = os.getenv("GITHUB_REPOSITORY_OWNER")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")  # Provided automatically by GitHub Actions


def get_all_org_secrets() -> list[str]:
    """Fetches the names of all secrets available in the GitHub organization."""

    if not GITHUB_ORG or not GITHUB_TOKEN:
        logger.error(
            "Missing GITHUB_REPOSITORY_OWNER or GITHUB_TOKEN environment variables."
        )
        return []

    url = f"https://api.github.com/orgs/{GITHUB_ORG}/actions/secrets"
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {GITHUB_TOKEN}",
    }

    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        secrets = response.json().get("secrets", [])
        secret_names = [secret["name"] for secret in secrets]
        logger.info(
            f"Discovered {len(secret_names)} secrets in the '{GITHUB_ORG}' organization."
        )
        return secret_names
    except requests.RequestException as e:
        logger.error(f"Failed to fetch secrets from GitHub API: {e}")
        return []


def sync_secret_to_pulumi_esc(secret_name: str):
    """Syncs a single secret from the environment to Pulumi ESC."""secret_value = os.getenv(secret_name).

    if not secret_value:
        logger.warning(
            f"Secret '{secret_name}' is in GitHub but not in the environment. Skipping."
        )
        return False

    logger.info(f"Syncing secret '{secret_name}' to Pulumi ESC...")
    try:
        command = [
            "pulumi",
            "env",
            "set",
            PULUMI_ESC_ENV,
            secret_name,
            "--secret",
            "--non-interactive",
        ]
        subprocess.run(
            command, input=secret_value, text=True, check=True, capture_output=True
        )
        logger.info(f"✅ Successfully synced '{secret_name}'.")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Failed to sync secret '{secret_name}': {e.stderr}")
        return False


def main():
    """Main execution function."""
    logger.info("Starting intelligent secret synchronization...")

    secret_names = get_all_org_secrets()
    if not secret_names:
        logger.error("No secrets found or failed to query GitHub API. Aborting.")
        return

    synced_count = 0
    failed_count = 0

    for name in secret_names:
        if sync_secret_to_pulumi_esc(name):
            synced_count += 1
        else:
            failed_count += 1

    logger.info("--- Sync Summary ---")
    logger.info(f"Total secrets discovered: {len(secret_names)}")
    logger.info(f"✅ Successfully synced: {synced_count}")
    logger.info(f"❌ Failed to sync: {failed_count}")

    if failed_count > 0:
        logger.error("One or more secrets failed to sync. Check the logs above.")
        exit(1)

    logger.info("🎉 Intelligent secret synchronization complete!")


if __name__ == "__main__":
    main()
