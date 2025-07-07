#!/usr/bin/env python3
"""
Docker Swarm Secrets Creation from Pulumi ESC
Creates all required Docker secrets for Sophia AI deployment
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional


def run_command(
    cmd: list[str], capture_output: bool = True
) -> subprocess.CompletedProcess:
    """Run a command and return the result"""
    try:
        result = subprocess.run(
            cmd, capture_output=capture_output, text=True, check=True
        )
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed: {' '.join(cmd)}")
        print(f"Error: {e.stderr}")
        sys.exit(1)


def get_pulumi_esc_secrets(environment: str) -> dict[str, str]:
    """Get all secrets from Pulumi ESC"""
    print(f"🔐 Fetching secrets from Pulumi ESC environment: {environment}")

    try:
        # Get all environment values
        cmd = ["pulumi", "env", "get", f"scoobyjava-org/default/{environment}"]
        result = run_command(cmd)

        # Parse the environment values
        env_data = json.loads(result.stdout)

        # Extract secrets from the nested structure
        secrets = {}
        if "values" in env_data and "sophia" in env_data["values"]:
            sophia_values = env_data["values"]["sophia"]

            # Flatten the nested structure
            def flatten_dict(d, parent_key="", sep="_"):
                items = []
                for k, v in d.items():
                    new_key = f"{parent_key}{sep}{k}" if parent_key else k
                    if isinstance(v, dict):
                        items.extend(flatten_dict(v, new_key, sep=sep).items())
                    else:
                        items.append((new_key, v))
                return dict(items)

            secrets = flatten_dict(sophia_values)

        print(f"✅ Retrieved {len(secrets)} secrets from Pulumi ESC")
        return secrets

    except Exception as e:
        print(f"❌ Failed to fetch secrets from Pulumi ESC: {e}")
        sys.exit(1)


def create_docker_secret(
    host: str, ssh_key: str, secret_name: str, secret_value: str
) -> bool:
    """Create a Docker secret on the remote host"""
    try:
        # Check if secret already exists
        check_cmd = [
            "ssh",
            "-i",
            ssh_key,
            "-o",
            "StrictHostKeyChecking=no",
            f"ubuntu@{host}",
            f"sudo docker secret ls --filter name={secret_name} --format '{{{{.Name}}}}'",
        ]

        result = run_command(check_cmd)
        if secret_name in result.stdout:
            print(f"🔄 Secret {secret_name} already exists, removing...")
            remove_cmd = [
                "ssh",
                "-i",
                ssh_key,
                "-o",
                "StrictHostKeyChecking=no",
                f"ubuntu@{host}",
                f"sudo docker secret rm {secret_name}",
            ]
            run_command(remove_cmd)

        # Create the secret
        create_cmd = [
            "ssh",
            "-i",
            ssh_key,
            "-o",
            "StrictHostKeyChecking=no",
            f"ubuntu@{host}",
            f"echo '{secret_value}' | sudo docker secret create {secret_name} -",
        ]

        run_command(create_cmd)
        print(f"✅ Created Docker secret: {secret_name}")
        return True

    except Exception as e:
        print(f"❌ Failed to create secret {secret_name}: {e}")
        return False


def get_required_secrets() -> dict[str, str]:
    """Get the mapping of Pulumi ESC keys to Docker secret names"""
    return {
        # Core platform secrets
        "ai_openai_api_key": "openai_api_key",
        "ai_anthropic_api_key": "anthropic_api_key",
        "infrastructure_pulumi_access_token": "pulumi_access_token",
        # Database secrets
        "data_postgres_password": "postgres_password",
        "data_redis_password": "redis_password",
        "data_redis_url": "redis_url",
        # Snowflake secrets
        "data_snowflake_account": "snowflake_account",
        "data_snowflake_user": "snowflake_user",
        "data_snowflake_password": "snowflake_password",
        "data_snowflake_database": "snowflake_database",
        "data_snowflake_role": "snowflake_role",
        "data_snowflake_warehouse": "snowflake_warehouse",
        # Business tool secrets
        "business_gong_access_key": "gong_access_key",
        "business_gong_client_secret": "gong_client_secret",
        "business_hubspot_access_token": "hubspot_access_token",
        "business_linear_api_key": "linear_api_key",
        "business_slack_app_token": "slack_app_token",
        "business_slack_bot_token": "slack_bot_token",
        # Infrastructure secrets
        "infrastructure_lambda_labs_api_key": "lambda_api_key",
        "infrastructure_vercel_access_token": "VERCEL_ACCESS_TOKEN",
        "infrastructure_github_token": "github_token",
        # MCP server secrets
        "ai_mem0_api_key": "mem0_api_key",
        # Monitoring secrets
        "monitoring_grafana_password": "grafana_password",
    }


def main():
    parser = argparse.ArgumentParser(
        description="Create Docker Swarm secrets from Pulumi ESC"
    )
    parser.add_argument("--host", required=True, help="Lambda Labs host IP")
    parser.add_argument("--ssh-key", required=True, help="SSH key file path")
    parser.add_argument(
        "--environment", default="sophia-ai-production", help="Pulumi ESC environment"
    )

    args = parser.parse_args()

    print("🚀 Creating Docker Swarm Secrets for Sophia AI")
    print("=" * 50)
    print(f"Host: {args.host}")
    print(f"Environment: {args.environment}")
    print()

    # Get secrets from Pulumi ESC
    esc_secrets = get_pulumi_esc_secrets(args.environment)

    # Get required secret mappings
    secret_mappings = get_required_secrets()

    # Create Docker secrets
    created_count = 0
    failed_count = 0

    for esc_key, docker_name in secret_mappings.items():
        if esc_key in esc_secrets:
            success = create_docker_secret(
                args.host, args.ssh_key, docker_name, esc_secrets[esc_key]
            )
            if success:
                created_count += 1
            else:
                failed_count += 1
        else:
            print(f"⚠️  Warning: Secret {esc_key} not found in Pulumi ESC")
            failed_count += 1

    print()
    print("📊 Secret Creation Summary")
    print("=" * 30)
    print(f"✅ Created: {created_count}")
    print(f"❌ Failed: {failed_count}")
    print(f"📋 Total: {len(secret_mappings)}")

    if failed_count > 0:
        print(f"⚠️  {failed_count} secrets failed to create")
        sys.exit(1)

    print("🎉 All Docker Swarm secrets created successfully!")


if __name__ == "__main__":
    main()
