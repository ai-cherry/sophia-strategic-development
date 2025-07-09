#!/usr/bin/env python3
"""
Fix the fucking secret sync once and for all.
Maps GitHub secret names to Pulumi ESC with CORRECT names.
"""

import os
import subprocess
import json
import yaml
from typing import Dict, Any

# THE ACTUAL GITHUB SECRET NAMES - THIS IS THE SOURCE OF TRUTH
GITHUB_TO_ESC_MAPPING = {
    # Docker Hub - THE MAIN PROBLEM
    "DOCKER_USERNAME": "docker_username",
    "DOCKER_TOKEN": "docker_token",  # NOT docker_hub_access_token!
    
    # Snowflake
    "SNOWFLAKE_ACCOUNT": "snowflake_account",
    "SNOWFLAKE_USER": "snowflake_user", 
    "SNOWFLAKE_PASSWORD": "snowflake_password",  # This is the PAT
    "SNOWFLAKE_WAREHOUSE": "snowflake_warehouse",
    "SNOWFLAKE_DATABASE": "snowflake_database",
    "SNOWFLAKE_SCHEMA": "snowflake_schema",
    "SNOWFLAKE_ROLE": "snowflake_role",
    
    # Lambda Labs
    "LAMBDA_API_KEY": "lambda_api_key",
    "LAMBDA_SSH_PRIVATE_KEY": "lambda_ssh_private_key",
    
    # AI Services
    "OPENAI_API_KEY": "openai_api_key",
    "ANTHROPIC_API_KEY": "anthropic_api_key",
    "PINECONE_API_KEY": "pinecone_api_key",
    
    # Dev Tools
    "GH_API_TOKEN": "github_token",
    "LINEAR_API_KEY": "linear_api_key",
    "NOTION_API_KEY": "notion_api_key",
    "FIGMA_PAT": "figma_pat",
    "VERCEL_TOKEN": "vercel_token",
    
    # Business Tools
    "GONG_ACCESS_KEY": "gong_access_key",
    "GONG_ACCESS_KEY_SECRET": "gong_access_key_secret",
    "HUBSPOT_API_KEY": "hubspot_api_key",
    "SLACK_WEBHOOK": "slack_webhook_url",
    "SLACK_BOT_TOKEN": "slack_bot_token",
}

def get_github_secret(secret_name: str) -> str:
    """Get secret from environment (set by GitHub Actions)"""
    value = os.environ.get(secret_name)
    if not value:
        print(f"⚠️  Warning: {secret_name} not found in environment")
        return f"PLACEHOLDER_{secret_name}"
    return value

def update_pulumi_esc(secrets: Dict[str, Any]) -> None:
    """Update Pulumi ESC with the secrets"""
    print("🔄 Updating Pulumi ESC...")
    
    # Get current ESC config
    result = subprocess.run(
        ["pulumi", "env", "get", "default/sophia-ai-production"],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"❌ Failed to get current ESC config: {result.stderr}")
        return
    
    try:
        current_config = json.loads(result.stdout)
    except json.JSONDecodeError:
        current_config = {}
    
    # Update with new secrets
    for github_name, esc_name in GITHUB_TO_ESC_MAPPING.items():
        value = get_github_secret(github_name)
        if value and not value.startswith("PLACEHOLDER_"):
            current_config[esc_name] = {"fn::secret": value}
            print(f"✅ Mapped {github_name} -> {esc_name}")
    
    # Write updated config
    config_file = "/tmp/esc_config.json"
    with open(config_file, "w") as f:
        json.dump(current_config, f, indent=2)
    
    # Update ESC
    result = subprocess.run(
        ["pulumi", "env", "set", "default/sophia-ai-production", "-f", config_file],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("✅ Pulumi ESC updated successfully")
    else:
        print(f"❌ Failed to update ESC: {result.stderr}")

def verify_sync() -> None:
    """Verify the sync worked"""
    print("\n🔍 Verifying sync...")
    
    # Check Docker credentials specifically
    result = subprocess.run(
        ["pulumi", "env", "get", "default/sophia-ai-production", "--show-secrets"],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        try:
            config = json.loads(result.stdout)
            
            # Check critical secrets
            critical = ["docker_token", "docker_username", "snowflake_password"]
            for key in critical:
                if key in config and not str(config[key]).startswith("PLACEHOLDER"):
                    print(f"✅ {key}: Found (hidden)")
                else:
                    print(f"❌ {key}: Missing or placeholder")
                    
        except json.JSONDecodeError:
            print("❌ Could not parse ESC config")

def main():
    print("🚀 Fixing secret sync...")
    print(f"📋 Mapping {len(GITHUB_TO_ESC_MAPPING)} secrets")
    
    # Update Pulumi ESC
    update_pulumi_esc(GITHUB_TO_ESC_MAPPING)
    
    # Verify
    verify_sync()
    
    print("\n📝 Next steps:")
    print("1. Run this in GitHub Actions with all secrets in environment")
    print("2. Or manually set DOCKER_TOKEN and DOCKER_USERNAME env vars and run locally")
    print("3. Test with: python3 test_docker_config.py")

if __name__ == "__main__":
    main() 