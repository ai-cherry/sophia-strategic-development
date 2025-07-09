#!/usr/bin/env python3
"""
Comprehensive secret mapping script that fixes ALL secret name mismatches.
This is the DEFINITIVE mapping between GitHub secrets and Pulumi ESC.
"""

import os
import subprocess
import json
import sys
from typing import Dict, List, Tuple, Any

# COMPREHENSIVE SECRET MAPPING - THE COMPLETE LIST
# GitHub Secret Name -> (Pulumi ESC Path, Description)
COMPLETE_SECRET_MAPPING: Dict[str, Tuple[str, str]] = {
    # Docker Hub - THE FUCKING PROBLEM
    "DOCKER_USERNAME": ("docker_username", "Docker Hub username"),
    "DOCKER_TOKEN": ("docker_token", "Docker Hub access token"),
    
    # Snowflake
    "SNOWFLAKE_ACCOUNT": ("snowflake_account", "Snowflake account identifier"),
    "SNOWFLAKE_USER": ("snowflake_user", "Snowflake username"),
    "SNOWFLAKE_PASSWORD": ("snowflake_password", "Snowflake password/PAT"),
    "SNOWFLAKE_WAREHOUSE": ("snowflake_warehouse", "Snowflake warehouse name"),
    "SNOWFLAKE_DATABASE": ("snowflake_database", "Snowflake database name"),
    "SNOWFLAKE_SCHEMA": ("snowflake_schema", "Snowflake schema name"),
    "SNOWFLAKE_ROLE": ("snowflake_role", "Snowflake role"),
    
    # Lambda Labs
    "LAMBDA_API_KEY": ("lambda_api_key", "Lambda Labs API key"),
    "LAMBDA_SSH_KEY": ("lambda_ssh_key", "Lambda Labs SSH public key"),
    "LAMBDA_SSH_PRIVATE_KEY": ("lambda_ssh_private_key", "Lambda Labs SSH private key"),
    "LAMBDA_API_ENDPOINT": ("lambda_api_endpoint", "Lambda Labs API endpoint"),
    
    # AI Services
    "OPENAI_API_KEY": ("openai_api_key", "OpenAI API key"),
    "ANTHROPIC_API_KEY": ("anthropic_api_key", "Anthropic API key"),
    "PINECONE_API_KEY": ("pinecone_api_key", "Pinecone API key"),
    "WEAVIATE_API_KEY": ("weaviate_api_key", "Weaviate API key"),
    "WEAVIATE_URL": ("weaviate_url", "Weaviate URL"),
    
    # Development Tools
    "GH_API_TOKEN": ("github_token", "GitHub API token"),
    "LINEAR_API_KEY": ("linear_api_key", "Linear API key"),
    "NOTION_API_KEY": ("notion_api_key", "Notion API key"),
    "FIGMA_PAT": ("figma_pat", "Figma personal access token"),
    "FIGMA_PROJECT_ID": ("figma_project_id", "Figma project ID"),
    "VERCEL_TOKEN": ("vercel_token", "Vercel deployment token"),
    "VERCEL_ORG_ID": ("vercel_org_id", "Vercel organization ID"),
    "VERCEL_PROJECT_ID": ("vercel_project_id", "Vercel project ID"),
    
    # Business Tools
    "GONG_ACCESS_KEY": ("gong_access_key", "Gong API access key"),
    "GONG_ACCESS_KEY_SECRET": ("gong_access_key_secret", "Gong API secret"),
    "HUBSPOT_API_KEY": ("hubspot_api_key", "HubSpot API key"),
    "SLACK_WEBHOOK": ("slack_webhook_url", "Slack webhook URL"),
    "SLACK_BOT_TOKEN": ("slack_bot_token", "Slack bot token"),
    "ASANA_API_TOKEN": ("asana_api_token", "Asana API token"),
    
    # Infrastructure
    "POSTGRES_USER": ("postgres_user", "PostgreSQL username"),
    "POSTGRES_PASSWORD": ("postgres_password", "PostgreSQL password"),
    "POSTGRES_DB": ("postgres_db", "PostgreSQL database name"),
    "REDIS_PASSWORD": ("redis_password", "Redis password"),
    
    # Monitoring
    "GRAFANA_API_KEY": ("grafana_api_key", "Grafana API key"),
    "GRAFANA_URL": ("grafana_url", "Grafana URL"),
    
    # Additional Services
    "PORTKEY_API_KEY": ("portkey_api_key", "Portkey API key"),
    "OPENROUTER_API_KEY": ("openrouter_api_key", "OpenRouter API key"),
    "CODACY_API_TOKEN": ("codacy_api_token", "Codacy API token"),
    "ESTUARY_ACCESS_TOKEN": ("estuary_access_token", "Estuary Flow token"),
    "NPM_API_TOKEN": ("npm_api_token", "NPM registry token"),
    
    # AWS (if needed)
    "AWS_DEPLOY_ROLE_ARN": ("aws_deploy_role_arn", "AWS deployment role ARN"),
    
    # Pulumi itself
    "PULUMI_ACCESS_TOKEN": ("pulumi_access_token", "Pulumi access token"),
}

# Application key variations that should all map to the same secret
APP_KEY_MAPPINGS = {
    # Docker variations
    "docker_hub_access_token": "docker_token",
    "docker_hub_token": "docker_token",
    "docker_password": "docker_token",
    "DOCKER_PASSWORD": "docker_token",
    "DOCKER_HUB_ACCESS_TOKEN": "docker_token",
    "DOCKER_PERSONAL_ACCESS_TOKEN": "docker_token",
    "docker_hub_username": "docker_username",
    "DOCKERHUB_USERNAME": "docker_username",
    "DOCKER_USER_NAME": "docker_username",
    
    # GitHub variations
    "gh_api_token": "github_token",
    "GITHUB_TOKEN": "github_token",
    "GH_TOKEN": "github_token",
    
    # Notion variations
    "notion_api_token": "notion_api_key",
    "NOTION_API_TOKEN": "notion_api_key",
    
    # HubSpot variations
    "hubspot_access_token": "hubspot_api_key",
    "HUBSPOT_ACCESS_TOKEN": "hubspot_api_key",
    
    # Asana variations
    "asana_access_token": "asana_api_token",
    "ASANA_ACCESS_TOKEN": "asana_api_token",
}

def get_github_secret(secret_name: str) -> str:
    """Get secret from environment (set by GitHub Actions)"""
    value = os.environ.get(secret_name)
    if not value:
        print(f"⚠️  {secret_name}: Not found in environment")
        return None
    return value

def get_pulumi_org() -> str:
    """Get Pulumi organization"""
    org = os.environ.get("PULUMI_ORG", "scoobyjava-org")
    print(f"📋 Using Pulumi org: {org}")
    return org

def sync_all_secrets() -> Dict[str, Any]:
    """Sync all secrets from GitHub to Pulumi ESC"""
    print("🚀 Starting comprehensive secret sync...")
    print(f"📊 Total secrets to sync: {len(COMPLETE_SECRET_MAPPING)}")
    
    org = get_pulumi_org()
    env_name = f"{org}/default/sophia-ai-production"
    
    # Get current ESC config
    print(f"\n📥 Getting current ESC config from {env_name}...")
    result = subprocess.run(
        ["pulumi", "env", "get", env_name],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"❌ Failed to get current ESC config: {result.stderr}")
        return {}
    
    try:
        current_config = json.loads(result.stdout)
    except json.JSONDecodeError:
        current_config = {}
    
    # Sync each secret
    synced = 0
    failed = 0
    skipped = 0
    
    print("\n🔄 Syncing secrets...")
    for github_name, (esc_name, description) in COMPLETE_SECRET_MAPPING.items():
        value = get_github_secret(github_name)
        
        if value:
            # Update config
            current_config[esc_name] = {"fn::secret": value}
            print(f"✅ {github_name} → {esc_name}: Synced")
            synced += 1
        else:
            # Check if we have a placeholder
            if esc_name in current_config and str(current_config[esc_name]).startswith("PLACEHOLDER"):
                print(f"⚠️  {github_name} → {esc_name}: Still placeholder")
                failed += 1
            else:
                print(f"⏭️  {github_name} → {esc_name}: Skipped (not in env)")
                skipped += 1
    
    # Write updated config
    print("\n📤 Updating Pulumi ESC...")
    config_file = "/tmp/esc_config.json"
    with open(config_file, "w") as f:
        json.dump(current_config, f, indent=2)
    
    result = subprocess.run(
        ["pulumi", "env", "set", env_name, "-f", config_file],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("✅ Pulumi ESC updated successfully")
    else:
        print(f"❌ Failed to update ESC: {result.stderr}")
    
    # Summary
    print("\n📊 Sync Summary:")
    print(f"  ✅ Synced: {synced}")
    print(f"  ⚠️  Failed: {failed}")
    print(f"  ⏭️  Skipped: {skipped}")
    print(f"  📋 Total: {len(COMPLETE_SECRET_MAPPING)}")
    
    return current_config

def verify_critical_secrets() -> None:
    """Verify critical secrets are properly synced"""
    print("\n🔍 Verifying critical secrets...")
    
    critical_secrets = [
        ("docker_token", "Docker Hub access"),
        ("docker_username", "Docker Hub username"),
        ("snowflake_password", "Snowflake access"),
        ("openai_api_key", "OpenAI access"),
        ("anthropic_api_key", "Anthropic access"),
        ("lambda_api_key", "Lambda Labs access"),
    ]
    
    org = get_pulumi_org()
    env_name = f"{org}/default/sophia-ai-production"
    
    # Get config with secrets shown
    result = subprocess.run(
        ["pulumi", "env", "get", env_name, "--show-secrets"],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        try:
            config = json.loads(result.stdout)
            
            for key, description in critical_secrets:
                if key in config:
                    value = str(config[key])
                    if not value.startswith("PLACEHOLDER"):
                        print(f"✅ {key}: Found ({description})")
                    else:
                        print(f"❌ {key}: Still placeholder!")
                else:
                    print(f"❌ {key}: Missing!")
                    
        except json.JSONDecodeError:
            print("❌ Could not parse ESC config")

def generate_mapping_report() -> None:
    """Generate a comprehensive mapping report"""
    print("\n📝 Generating mapping report...")
    
    report_file = "SECRET_MAPPING_REPORT.md"
    with open(report_file, "w") as f:
        f.write("# Secret Mapping Report\n\n")
        f.write(f"Total secrets: {len(COMPLETE_SECRET_MAPPING)}\n\n")
        
        f.write("## GitHub → Pulumi ESC Mapping\n\n")
        f.write("| GitHub Secret | Pulumi ESC Key | Description |\n")
        f.write("|---------------|----------------|-------------|\n")
        
        for github_name, (esc_name, description) in sorted(COMPLETE_SECRET_MAPPING.items()):
            f.write(f"| `{github_name}` | `{esc_name}` | {description} |\n")
        
        f.write("\n## Application Key Variations\n\n")
        f.write("| Application Key | Maps To |\n")
        f.write("|-----------------|----------|\n")
        
        for app_key, maps_to in sorted(APP_KEY_MAPPINGS.items()):
            f.write(f"| `{app_key}` | `{maps_to}` |\n")
    
    print(f"✅ Report written to {report_file}")

def main():
    print("🔧 Comprehensive Secret Mapping Fix")
    print("=" * 50)
    
    # Check if we have Pulumi access token
    if not os.environ.get("PULUMI_ACCESS_TOKEN"):
        print("❌ PULUMI_ACCESS_TOKEN not set!")
        print("💡 Set it first: export PULUMI_ACCESS_TOKEN=pul-...")
        sys.exit(1)
    
    # Sync all secrets
    sync_all_secrets()
    
    # Verify critical ones
    verify_critical_secrets()
    
    # Generate report
    generate_mapping_report()
    
    print("\n✅ Comprehensive secret mapping complete!")
    print("\n📝 Next steps:")
    print("1. Run this in GitHub Actions with all secrets")
    print("2. Or set critical env vars locally and run")
    print("3. Test with: python3 test_docker_config.py")
    print("4. Deploy with confidence!")

if __name__ == "__main__":
    main() 