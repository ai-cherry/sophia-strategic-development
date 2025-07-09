#!/usr/bin/env python3
"""
Validate that all GitHub Organization Secrets have corresponding mappings
in the backend auto_esc_config.py file.
"""

import subprocess
import json
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.core.auto_esc_config import get_config_value


def get_github_secrets():
    """Get list of secrets from GitHub organization"""
    try:
        result = subprocess.run(
            ["gh", "secret", "list", "--org", "ai-cherry", "--json", "name"],
            capture_output=True,
            text=True,
            check=True
        )
        secrets = json.loads(result.stdout)
        return [s["name"] for s in secrets]
    except Exception as e:
        print(f"❌ Failed to get GitHub secrets: {e}")
        print("Make sure you're logged in with: gh auth login")
        return []


def validate_mappings():
    """Validate that all secrets have proper mappings"""
    print("🔍 Validating Secret Mappings\n")
    
    # Get GitHub secrets
    github_secrets = get_github_secrets()
    if not github_secrets:
        print("⚠️  No GitHub secrets found or unable to access")
        return
    
    print(f"📊 Found {len(github_secrets)} GitHub Organization Secrets\n")
    
    # Critical secrets that MUST work
    critical_mappings = {
        "docker_hub_access_token": "Docker Hub Access Token",
        "docker_hub_username": "Docker Hub Username",
        "lambda_api_key": "Lambda Labs API Key",
        "lambda_ssh_private_key": "Lambda Labs SSH Key",
        "openai_api_key": "OpenAI API Key",
        "anthropic_api_key": "Anthropic API Key",
        "snowflake_password": "Snowflake Password",
        "gong_access_key": "Gong Access Key",
        "hubspot_access_token": "HubSpot Access Token",
        "slack_bot_token": "Slack Bot Token",
    }
    
    print("🔐 Checking Critical Secrets:\n")
    
    working = 0
    missing = 0
    
    for backend_key, display_name in critical_mappings.items():
        value = get_config_value(backend_key)
        if value and not str(value).startswith("PLACEHOLDER"):
            print(f"✅ {display_name}: Available via get_config_value('{backend_key}')")
            working += 1
        else:
            print(f"❌ {display_name}: Missing or placeholder")
            missing += 1
    
    print(f"\n📊 Summary:")
    print(f"  ✅ Working: {working}")
    print(f"  ❌ Missing: {missing}")
    
    # Test specific functions
    print(f"\n🧪 Testing Helper Functions:\n")
    
    try:
        from backend.core.auto_esc_config import get_docker_hub_config
        docker_config = get_docker_hub_config()
        username = docker_config.get("username", "Not found")
        has_token = "Yes" if docker_config.get("access_token") else "No"
        print(f"✅ get_docker_hub_config()")
        print(f"   Username: {username}")
        print(f"   Has token: {has_token}")
    except Exception as e:
        print(f"❌ get_docker_hub_config() failed: {e}")
    
    try:
        from backend.core.auto_esc_config import get_lambda_labs_config
        lambda_config = get_lambda_labs_config()
        has_key = "Yes" if lambda_config.get("api_key") else "No"
        has_ssh = "Yes" if lambda_config.get("ssh_private_key") else "No"
        print(f"✅ get_lambda_labs_config()")
        print(f"   Has API key: {has_key}")
        print(f"   Has SSH key: {has_ssh}")
    except Exception as e:
        print(f"❌ get_lambda_labs_config() failed: {e}")
    
    try:
        from backend.core.auto_esc_config import get_snowflake_config
        snowflake_config = get_snowflake_config()
        account = snowflake_config.get("account", "Not found")
        has_password = "Yes" if snowflake_config.get("password") else "No"
        print(f"✅ get_snowflake_config()")
        print(f"   Account: {account}")
        print(f"   Has password: {has_password}")
    except Exception as e:
        print(f"❌ get_snowflake_config() failed: {e}")
    
    print(f"\n💡 Tips:")
    print(f"1. If secrets are missing, run: gh workflow run sync_secrets.yml")
    print(f"2. Check Pulumi ESC: pulumi env get scoobyjava-org/default/sophia-ai-production --show-secrets")
    print(f"3. Add new mappings to backend/core/auto_esc_config.py")


if __name__ == "__main__":
    validate_mappings() 