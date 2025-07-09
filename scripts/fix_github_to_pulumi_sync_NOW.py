#!/usr/bin/env python3
"""
FIX THE FUCKING GITHUB TO PULUMI ESC SYNC ONCE AND FOR ALL
This manually syncs ALL secrets and eliminates ALL placeholders
"""

import os
import subprocess
import json
import sys

# ALL THE FUCKING SECRETS THAT SHOULD BE IN GITHUB
GITHUB_SECRETS = {
    # Docker Hub - THE MAIN PROBLEM
    "DOCKER_USERNAME": "docker_username",
    "DOCKER_TOKEN": "docker_token",
    
    # Snowflake
    "SNOWFLAKE_ACCOUNT": "snowflake_account",
    "SNOWFLAKE_USER": "snowflake_user",
    "SNOWFLAKE_PASSWORD": "snowflake_password",
    "SNOWFLAKE_WAREHOUSE": "snowflake_warehouse", 
    "SNOWFLAKE_DATABASE": "snowflake_database",
    "SNOWFLAKE_SCHEMA": "snowflake_schema",
    "SNOWFLAKE_ROLE": "snowflake_role",
    
    # Lambda Labs
    "LAMBDA_API_KEY": "lambda_api_key",
    "LAMBDA_SSH_PRIVATE_KEY": "lambda_ssh_private_key",
    "LAMBDA_API_ENDPOINT": "lambda_api_endpoint",
    
    # AI Services
    "OPENAI_API_KEY": "openai_api_key",
    "ANTHROPIC_API_KEY": "anthropic_api_key",
    "PINECONE_API_KEY": "pinecone_api_key",
    "WEAVIATE_API_KEY": "weaviate_api_key",
    "WEAVIATE_URL": "weaviate_url",
    
    # Dev Tools
    "GH_API_TOKEN": "github_token",
    "LINEAR_API_KEY": "linear_api_key",
    "NOTION_API_KEY": "notion_api_key",
    "FIGMA_PAT": "figma_pat",
    "FIGMA_PROJECT_ID": "figma_project_id",
    "VERCEL_TOKEN": "vercel_token",
    "VERCEL_ORG_ID": "vercel_org_id",
    "VERCEL_PROJECT_ID": "vercel_project_id",
    
    # Business Tools
    "GONG_ACCESS_KEY": "gong_access_key",
    "GONG_ACCESS_KEY_SECRET": "gong_access_key_secret",
    "HUBSPOT_API_KEY": "hubspot_api_key",
    "SLACK_WEBHOOK": "slack_webhook_url",
    "SLACK_BOT_TOKEN": "slack_bot_token",
    "ASANA_API_TOKEN": "asana_api_token",
    
    # Infrastructure
    "POSTGRES_USER": "postgres_user",
    "POSTGRES_PASSWORD": "postgres_password", 
    "POSTGRES_DB": "postgres_db",
    "REDIS_PASSWORD": "redis_password",
    
    # Monitoring
    "GRAFANA_API_KEY": "grafana_api_key",
    "GRAFANA_URL": "grafana_url",
    
    # Additional
    "PORTKEY_API_KEY": "portkey_api_key",
    "OPENROUTER_API_KEY": "openrouter_api_key",
    "CODACY_API_TOKEN": "codacy_api_token",
    "ESTUARY_ACCESS_TOKEN": "estuary_access_token",
    "NPM_API_TOKEN": "npm_api_token",
    "AWS_DEPLOY_ROLE_ARN": "aws_deploy_role_arn",
}

def get_github_secrets():
    """Get ALL secrets from GitHub organization"""
    print("🔍 Getting secrets from GitHub organization...")
    
    secrets = {}
    for github_name, pulumi_name in GITHUB_SECRETS.items():
        # Try to get from GitHub CLI
        result = subprocess.run(
            ["gh", "secret", "list", "--org", "ai-cherry"],
            capture_output=True,
            text=True
        )
        
        if github_name in result.stdout:
            print(f"✅ Found {github_name} in GitHub")
            secrets[github_name] = pulumi_name
        else:
            print(f"❌ Missing {github_name} in GitHub")
    
    return secrets

def get_current_esc_config():
    """Get current Pulumi ESC config"""
    print("\n📥 Getting current Pulumi ESC config...")
    
    result = subprocess.run(
        ["pulumi", "env", "get", "scoobyjava-org/default/sophia-ai-production"],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"❌ Failed to get ESC config: {result.stderr}")
        return {}
    
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return {}

def update_esc_with_real_secrets():
    """Update ESC with real secrets from GitHub"""
    print("\n🔄 Updating Pulumi ESC with real secrets...")
    
    # Get current config
    config = get_current_esc_config()
    
    # Count placeholders
    placeholder_count = 0
    for key, value in config.items():
        if isinstance(value, str) and value.startswith("PLACEHOLDER"):
            placeholder_count += 1
        elif isinstance(value, dict) and "fn::secret" in value:
            if str(value["fn::secret"]).startswith("PLACEHOLDER"):
                placeholder_count += 1
    
    print(f"⚠️  Found {placeholder_count} placeholders to replace")
    
    # For each secret, try to get from GitHub and update ESC
    for github_name, pulumi_name in GITHUB_SECRETS.items():
        # Try to get the secret value using gh CLI
        result = subprocess.run(
            ["gh", "secret", "get", github_name, "--org", "ai-cherry"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0 and result.stdout.strip():
            value = result.stdout.strip()
            print(f"✅ Got {github_name} from GitHub ({len(value)} chars)")
            
            # Update the config
            config[pulumi_name] = {"fn::secret": value}
        else:
            print(f"❌ Could not get {github_name} from GitHub")
    
    # Write updated config
    config_file = "/tmp/updated_esc_config.json"
    with open(config_file, "w") as f:
        json.dump(config, f, indent=2)
    
    # Update ESC
    print("\n📤 Updating Pulumi ESC...")
    result = subprocess.run(
        ["pulumi", "env", "set", "scoobyjava-org/default/sophia-ai-production", "-f", config_file],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("✅ Pulumi ESC updated successfully!")
        return True
    else:
        print(f"❌ Failed to update ESC: {result.stderr}")
        return False

def verify_no_placeholders():
    """Verify no placeholders remain"""
    print("\n🔍 Verifying no placeholders remain...")
    
    result = subprocess.run(
        ["pulumi", "env", "get", "scoobyjava-org/default/sophia-ai-production", "--show-secrets"],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        output = result.stdout
        placeholder_count = output.count("PLACEHOLDER")
        
        if placeholder_count == 0:
            print("✅ NO PLACEHOLDERS FOUND! All secrets are real!")
            return True
        else:
            print(f"❌ Still found {placeholder_count} placeholders")
            # Show which ones
            lines = output.split('\n')
            for line in lines:
                if "PLACEHOLDER" in line:
                    print(f"  {line.strip()}")
            return False
    else:
        print(f"❌ Could not verify: {result.stderr}")
        return False

def main():
    print("🚨 FIXING GITHUB → PULUMI ESC SYNC FOR ALL SECRETS")
    print("=" * 60)
    
    # Check prerequisites
    if not os.environ.get("PULUMI_ACCESS_TOKEN"):
        print("❌ PULUMI_ACCESS_TOKEN not set!")
        sys.exit(1)
    
    # Check gh CLI is authenticated
    result = subprocess.run(["gh", "auth", "status"], capture_output=True, text=True)
    if result.returncode != 0:
        print("❌ GitHub CLI not authenticated!")
        print("Run: gh auth login")
        sys.exit(1)
    
    print(f"📋 Will sync {len(GITHUB_SECRETS)} secrets")
    
    # Get secrets from GitHub
    github_secrets = get_github_secrets()
    print(f"✅ Found {len(github_secrets)} secrets in GitHub")
    
    # Update ESC
    if update_esc_with_real_secrets():
        # Verify
        if verify_no_placeholders():
            print("\n🎉 SUCCESS! All secrets synced and no placeholders remain!")
        else:
            print("\n⚠️  Some placeholders still remain")
    else:
        print("\n❌ Failed to update ESC")
    
    print("\n📝 Next steps:")
    print("1. Test Docker login: python3 scripts/use_docker_from_pulumi.py")
    print("2. Deploy to Lambda Labs")
    print("3. Never worry about placeholders again!")

if __name__ == "__main__":
    main() 