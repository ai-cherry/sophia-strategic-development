#!/usr/bin/env python3
"""
Update GitHub Organization Secrets using GitHub API
This script reads from local.env and updates all secrets in GitHub
"""

import base64
import os
import sys

import requests
from nacl import public
from backend.core.auto_esc_config import get_config_value

# GitHub configuration
GITHUB_ORG = "ai-cherry"
GITHUB_REPO = "sophia-main"


def get_github_public_key(token: str) -> dict[str, str]:
    """Get the public key for encrypting secrets"""
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    }

    # Try organization secrets first
    url = f"https://api.github.com/orgs/{GITHUB_ORG}/actions/secrets/public-key"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()

    # Fallback to repository secrets
    url = f"https://api.github.com/repos/{GITHUB_ORG}/{GITHUB_REPO}/actions/secrets/public-key"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to get public key: {response.status_code} - {response.text}")
        sys.exit(1)


def encrypt_secret(public_key: str, secret_value: str) -> str:
    """Encrypt a secret using the public key"""
    public_key_bytes = base64.b64decode(public_key)
    public_key_obj = public.PublicKey(public_key_bytes)
    sealed_box = public.SealedBox(public_key_obj)
    encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))
    return base64.b64encode(encrypted).decode("utf-8")


def update_secret(
    token: str, secret_name: str, secret_value: str, key_data: dict[str, str]
):
    """Update or create a secret in GitHub"""
    encrypted_value = encrypt_secret(key_data["key"], secret_value)

    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    }

    data = {"encrypted_value": encrypted_value, "key_id": key_data["key_id"]}

    # Try organization secrets first
    url = f"https://api.github.com/orgs/{GITHUB_ORG}/actions/secrets/{secret_name}"
    response = requests.put(url, headers=headers, json=data)

    if response.status_code in [201, 204]:
        print(f"✅ Updated organization secret: {secret_name}")
        return

    # Fallback to repository secrets
    url = f"https://api.github.com/repos/{GITHUB_ORG}/{GITHUB_REPO}/actions/secrets/{secret_name}"
    response = requests.put(url, headers=headers, json=data)

    if response.status_code in [201, 204]:
        print(f"✅ Updated repository secret: {secret_name}")
    else:
        print(
            f"❌ Failed to update secret {secret_name}: {response.status_code} - {response.text}"
        )


def load_env_file(file_path: str) -> dict[str, str]:
    """Load environment variables from a file"""
    env_vars = {}

    if not os.path.exists(file_path):
        print(f"❌ Environment file not found: {file_path}")
        return env_vars

    with open(file_path) as f:
        for line in f:
            line = line.strip()
            # Skip comments and empty lines
            if line.startswith("#") or not line:
                continue

            # Parse key=value
            if "=" in line:
                key, value = line.split("=", 1)
                env_vars[key.strip()] = value.strip()

    return env_vars


def main():
    """Update GitHub organization secrets"""
    print("📝 Updating GitHub Organization Secrets")

    # Get GitHub PAT
    github_token = get_config_value("GITHUB_PAT") or get_config_value("GITHUB_TOKEN")
    if not github_token:
        print("❌ GitHub PAT not found in environment")
        print("Please set GITHUB_PAT or GITHUB_TOKEN environment variable")
        sys.exit(1)

    # Load environment
    load_env_file("local.env")

    # Get public key
    public_key_data = get_github_public_key(github_token)
    if not public_key_data:
        print("❌ Failed to get GitHub public key")
        sys.exit(1)

    # Secrets to update
    secrets_mapping = {
        # Qdrant
        "QDRANT_ACCOUNT": get_config_value("QDRANT_ACCOUNT"),
        "QDRANT_USER": get_config_value("QDRANT_USER"),
        "QDRANT_PASSWORD": get_config_value("QDRANT_PASSWORD"),
        "QDRANT_PAT": get_config_value("QDRANT_PAT"),
        "QDRANT_MASTER_TOKEN": get_config_value("QDRANT_MASTER_TOKEN"),
        # Docker Hub
        "DOCKER_HUB_USERNAME": get_config_value("DOCKER_USERNAME"),
        "DOCKER_HUB_ACCESS_TOKEN": get_config_value("DOCKER_PERSONAL_ACCESS_TOKEN"),
        # Lambda Labs
        "LAMBDA_API_KEY": get_config_value("LAMBDA_API_KEY"),
        "LAMBDA_PRIVATE_SSH_KEY": get_config_value("LAMBDA_SSH_KEY"),
        # AI Services
        "OPENAI_API_KEY": get_config_value("OPENAI_API_KEY"),
        "ANTHROPIC_API_KEY": get_config_value("ANTHROPIC_API_KEY"),
        # Business Tools
        "GONG_ACCESS_KEY": get_config_value("GONG_ACCESS_KEY"),
        "GONG_ACCESS_KEY_SECRET": get_config_value("GONG_ACCESS_KEY_SECRET"),
        "HUBSPOT_API_KEY": get_config_value("HUBSPOT_API_KEY"),
        "SLACK_APP_TOKEN": get_config_value("SLACK_APP_TOKEN"),
        "SLACK_BOT_TOKEN": get_config_value("SLACK_BOT_TOKEN"),
        # Other Services
        "VERCEL_API_TOKEN": get_config_value("VERCEL_API_TOKEN"),
        "LINEAR_API_KEY": get_config_value("LINEAR_API_KEY"),
        "ESTUARY_API_KEY": get_config_value("ESTUARY_API_KEY"),
        "SENTRY_API_TOKEN": get_config_value("SENTRY_API_TOKEN"),
        "ARIZE_API_KEY": get_config_value("ARIZE_API_KEY"),
        "OPENROUTER_API_KEY": get_config_value("OPENROUTER_API_KEY"),
        "PORTKEY_API_KEY": get_config_value("PORTKEY_API_KEY"),
        # Pulumi
        "PULUMI_ORG": "scoobyjava-org",
        "PULUMI_ACCESS_TOKEN": get_config_value("PULUMI_ACCESS_TOKEN"),
    }

    # Update secrets
    success_count = 0
    for secret_name, secret_value in secrets_mapping.items():
        if secret_value:
            if update_secret(github_token, secret_name, secret_value, public_key_data):
                success_count += 1
        else:
            print(f"⚠️ Skipping {secret_name} (not found in environment)")

    print(f"\n✅ Updated {success_count}/{len(secrets_mapping)} secrets")

    # Trigger sync workflow
    if success_count > 0:
        print("\n🔄 Triggering secrets sync workflow...")
        os.system("gh workflow run sync_secrets.yml")


if __name__ == "__main__":
    main()
