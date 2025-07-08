#!/usr/bin/env python3
"""
Unified Secret Sync - GitHub Organization to Pulumi ESC
Part of the Sophia AI Unified Infrastructure

This is THE ONLY secret sync script. All others are legacy.
"""

import json
import os
import subprocess
import sys


def get_secret(secret_name: str) -> str:
    """Get a secret value from the GitHub Actions environment."""
    value = os.environ.get(secret_name, "")
    if not value:
        pass
    return value


def sync_secrets_to_pulumi_esc():
    """Sync GitHub Organization secrets to Pulumi ESC environment."""

    # The Pulumi organization and environment
    pulumi_org = os.environ.get("PULUMI_ORG", "scoobyjava-org")
    esc_environment = f"{pulumi_org}/default/sophia-ai-production"

    # Define the secret structure that matches your ACTUAL GitHub organization secrets
    # Using the EXACT names from GitHub Organization Secrets
    secrets_structure = {
        # Snowflake
        "snowflake_account": get_secret("SNOWFLAKE_ACCOUNT"),
        "snowflake_username": get_secret("SNOWFLAKE_USERNAME"),
        "snowflake_password": get_secret("SNOWFLAKE_PASSWORD"),
        "snowflake_warehouse": get_secret("SNOWFLAKE_WAREHOUSE"),
        "snowflake_database": get_secret("SNOWFLAKE_DATABASE"),
        "snowflake_role": get_secret("SNOWFLAKE_ROLE"),
        # AI Services
        "openai_api_key": get_secret("OPENAI_API_KEY"),
        "anthropic_api_key": get_secret("ANTHROPIC_API_KEY"),
        "mem0_api_key": get_secret("MEM0_API_KEY"),
        "openrouter_api_key": get_secret("OPENROUTER_API_KEY"),
        "portkey_api_key": get_secret("PORTKEY_API_KEY"),
        # Business Intelligence
        "gong_access_key": get_secret("GONG_ACCESS_KEY"),
        "gong_access_key_secret": get_secret("GONG_ACCESS_KEY_SECRET"),
        "hubspot_api_key": get_secret("HUBSPOT_API_KEY"),
        "linear_api_key": get_secret("LINEAR_API_KEY"),
        "asana_access_token": get_secret("ASANA_ACCESS_TOKEN"),
        "notion_api_token": get_secret("NOTION_API_TOKEN"),
        # Communication
        "slack_bot_token": get_secret("SLACK_BOT_TOKEN"),
        "slack_app_token": get_secret("SLACK_APP_TOKEN"),
        "slack_webhook_url": get_secret("SLACK_WEBHOOK_URL"),
        "slack_signing_secret": get_secret("SLACK_SIGNING_SECRET"),
        # Development Tools
        "github_token": get_secret("GITHUB_TOKEN"),
        "github_app_id": get_secret("GITHUB_APP_ID"),
        "github_app_private_key": get_secret("GITHUB_APP_PRIVATE_KEY"),
        "docker_token": get_secret("DOCKER_TOKEN"),
        "docker_hub_access_token": get_secret("DOCKER_HUB_ACCESS_TOKEN"),
        "codacy_api_token": get_secret("CODACY_API_TOKEN"),
        # Lambda Labs - Using ACTUAL GitHub secret names
        "lambda_labs_api_key": get_secret("LAMBDA_LABS_API_KEY"),
        "lambda_labs_ssh_key": get_secret("LAMBDA_LABS_SSH_PRIVATE_KEY"),
        "lambda_labs_ssh_key_name": get_secret("LAMBDA_LABS_SSH_KEY_NAME"),
        "lambda_labs_region": get_secret("LAMBDA_LABS_REGION"),
        "lambda_labs_instance_type": get_secret("LAMBDA_LABS_INSTANCE_TYPE"),
        "lambda_labs_cluster_size": get_secret("LAMBDA_LABS_CLUSTER_SIZE"),
        "lambda_labs_max_cluster_size": get_secret("LAMBDA_LABS_MAX_CLUSTER_SIZE"),
        "lambda_labs_shared_fs_id": get_secret("LAMBDA_LABS_SHARED_FS_ID"),
        "lambda_labs_shared_fs_mount": get_secret("LAMBDA_LABS_SHARED_FS_MOUNT"),
        "lambda_labs_asg_name": get_secret("LAMBDA_LABS_ASG_NAME"),
        # Cloud Infrastructure
        "vercel_api_token": get_secret("VERCEL_ACCESS_TOKEN"),  # Standardized name
        "namecheap_api_key": get_secret(
            "NAMECHEAP_API_KEY"
        ),  # Added for domain management
        "pulumi_access_token": get_secret("PULUMI_ACCESS_TOKEN"),
        # Data Infrastructure
        "postgres_password": get_secret("POSTGRES_PASSWORD"),
        "pinecone_api_key": get_secret("PINECONE_API_KEY"),
        "pinecone_environment": get_secret("PINECONE_ENVIRONMENT"),
        "weaviate_api_key": get_secret("WEAVIATE_API_KEY"),
        "weaviate_url": get_secret("WEAVIATE_URL"),
        "estuary_api_token": get_secret("ESTUARY_API_TOKEN"),
        # Design
        "figma_pat": get_secret("FIGMA_PAT"),
        "figma_project_id": get_secret("FIGMA_PROJECT_ID"),
        # Monitoring
        "grafana_password": get_secret("GRAFANA_PASSWORD"),
    }

    # Convert to the structured format Pulumi ESC expects
    esc_config = {"values": {"sophia": secrets_structure}}

    # Write to temporary file
    import tempfile

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(esc_config, f, indent=2)
        temp_file = f.name

    try:
        # Set the configuration in Pulumi ESC
        cmd = ["esc", "env", "set", esc_environment, "--file", temp_file]

        result = subprocess.run(cmd, check=False, capture_output=True, text=True)

        if result.returncode == 0:
            # List the secrets that were synced
            sum(1 for v in secrets_structure.values() if v)
            len(secrets_structure)

            # Show which secrets are missing
            missing = [k for k, v in secrets_structure.items() if not v]
            if missing:
                pass
        else:
            sys.exit(1)
    finally:
        # Clean up temp file
        os.unlink(temp_file)


# This mapping is for reference - showing how GitHub secrets map to Pulumi ESC keys
SECRET_MAPPING = {
    # AI Services
    "OPENAI_API_KEY": "openai_api_key",
    "ANTHROPIC_API_KEY": "anthropic_api_key",
    "MEM0_API_KEY": "mem0_api_key",
    "OPENROUTER_API_KEY": "openrouter_api_key",
    "PORTKEY_API_KEY": "portkey_api_key",
    # Data Infrastructure
    "SNOWFLAKE_ACCOUNT": "snowflake_account",
    "SNOWFLAKE_USERNAME": "snowflake_username",
    "SNOWFLAKE_PASSWORD": "snowflake_password",
    "SNOWFLAKE_WAREHOUSE": "snowflake_warehouse",
    "SNOWFLAKE_DATABASE": "snowflake_database",
    "SNOWFLAKE_ROLE": "snowflake_role",
    "POSTGRES_PASSWORD": "postgres_password",
    "PINECONE_API_KEY": "pinecone_api_key",
    "PINECONE_ENVIRONMENT": "pinecone_environment",
    "WEAVIATE_API_KEY": "weaviate_api_key",
    "WEAVIATE_URL": "weaviate_url",
    "ESTUARY_API_TOKEN": "estuary_api_token",
    # Business Intelligence
    "GONG_ACCESS_KEY": "gong_access_key",
    "GONG_ACCESS_KEY_SECRET": "gong_access_key_secret",
    "HUBSPOT_API_KEY": "hubspot_api_key",
    # Communication
    "SLACK_BOT_TOKEN": "slack_bot_token",
    "SLACK_APP_TOKEN": "slack_app_token",
    "SLACK_WEBHOOK_URL": "slack_webhook_url",
    "SLACK_SIGNING_SECRET": "slack_signing_secret",
    # Project Management
    "LINEAR_API_KEY": "linear_api_key",
    "ASANA_ACCESS_TOKEN": "asana_access_token",
    "NOTION_API_TOKEN": "notion_api_token",
    # Lambda Labs - ACTUAL GitHub secret names
    "LAMBDA_LABS_API_KEY": "lambda_labs_api_key",
    "LAMBDA_LABS_SSH_PRIVATE_KEY": "lambda_labs_ssh_key",
    "LAMBDA_LABS_SSH_KEY_NAME": "lambda_labs_ssh_key_name",
    "LAMBDA_LABS_REGION": "lambda_labs_region",
    "LAMBDA_LABS_INSTANCE_TYPE": "lambda_labs_instance_type",
    "LAMBDA_LABS_CLUSTER_SIZE": "lambda_labs_cluster_size",
    "LAMBDA_LABS_MAX_CLUSTER_SIZE": "lambda_labs_max_cluster_size",
    "LAMBDA_LABS_SHARED_FS_ID": "lambda_labs_shared_fs_id",
    "LAMBDA_LABS_SHARED_FS_MOUNT": "lambda_labs_shared_fs_mount",
    "LAMBDA_LABS_ASG_NAME": "lambda_labs_asg_name",
    # Cloud Infrastructure
    "PULUMI_ACCESS_TOKEN": "pulumi_access_token",
    "VERCEL_ACCESS_TOKEN": "vercel_api_token",
    "NAMECHEAP_API_KEY": "namecheap_api_key",  # Added for domain management
    # Development Tools
    "DOCKER_TOKEN": "docker_token",
    "DOCKER_HUB_ACCESS_TOKEN": "docker_hub_access_token",
    "GITHUB_TOKEN": "github_token",
    "GITHUB_APP_ID": "github_app_id",
    "GITHUB_APP_PRIVATE_KEY": "github_app_private_key",
    "CODACY_API_TOKEN": "codacy_api_token",
    # Monitoring
    "GRAFANA_PASSWORD": "grafana_password",
    # Design
    "FIGMA_PAT": "figma_pat",
    "FIGMA_PROJECT_ID": "figma_project_id",
}

if __name__ == "__main__":
    sync_secrets_to_pulumi_esc()
