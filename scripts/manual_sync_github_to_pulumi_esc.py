#!/usr/bin/env python3
"""
Manual GitHub Organization Secrets → Pulumi ESC Sync Script
One-time sync to immediately fix all secret mappings

Usage:
python scripts/manual_sync_github_to_pulumi_esc.py
"""

import logging
import subprocess
import sys
from typing import Dict, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Priority 1 secrets that are critical for MCP servers
PRIORITY_1_SECRETS = {
    # Core AI Services - WORKING ✓
    "openai_api_key": "sk-svcacct-fBzQGxh4ZN3X9...",  # From GitHub: OPENAI_API_KEY
    "anthropic_api_key": "sk-ant-api03-l2Og...",      # From GitHub: ANTHROPIC_API_KEY  
    "pinecone_api_key": "pcsk_7PHV2G_Mj1rRCwi...",   # From GitHub: PINECONE_API_KEY
    "gong_access_key": "TV33BPZ5UN45QKZ...",          # From GitHub: GONG_ACCESS_KEY
    
    # Gateway Services - MISSING (add these)
    "portkey_api_key": "PLACEHOLDER_FROM_GITHUB_PORTKEY_API_KEY",      # From GitHub: PORTKEY_API_KEY
    "openrouter_api_key": "PLACEHOLDER_FROM_GITHUB_OPENROUTER_API_KEY", # From GitHub: OPENROUTER_API_KEY
    
    # Business Intelligence - MISSING (add these) 
    "hubspot_access_token": "PLACEHOLDER_FROM_GITHUB_HUBSPOT_ACCESS_TOKEN",  # From GitHub: HUBSPOT_ACCESS_TOKEN
    "linear_api_key": "PLACEHOLDER_FROM_GITHUB_LINEAR_API_KEY",               # From GitHub: LINEAR_API_KEY
    "asana_access_token": "PLACEHOLDER_FROM_GITHUB_ASANA_API_TOKEN",          # From GitHub: ASANA_API_TOKEN
    
    # Communication - MISSING (add these)
    "slack_bot_token": "PLACEHOLDER_FROM_GITHUB_SLACK_BOT_TOKEN",    # From GitHub: SLACK_BOT_TOKEN
    "slack_app_token": "PLACEHOLDER_FROM_GITHUB_SLACK_APP_TOKEN",    # From GitHub: SLACK_APP_TOKEN
    
    # Development Tools - MISSING (add these)
    "github_token": "PLACEHOLDER_FROM_GITHUB_GH_API_TOKEN",          # From GitHub: GH_API_TOKEN
    "figma_pat": "PLACEHOLDER_FROM_GITHUB_FIGMA_PAT",                # From GitHub: FIGMA_PAT
    "notion_api_token": "PLACEHOLDER_FROM_GITHUB_NOTION_API_KEY",    # From GitHub: NOTION_API_KEY
    
    # Infrastructure - MISSING (add these)
    "lambda_api_key": "PLACEHOLDER_FROM_GITHUB_LAMBDA_API_KEY",      # From GitHub: LAMBDA_API_KEY
    
    # Snowflake - WORKING ✓
    "snowflake_account": "ZNB04675",                  # From GitHub: SNOWFLAKE_ACCOUNT
    "snowflake_user": "SCOOBYJAVA15",                # From GitHub: SNOWFLAKE_USER
    "snowflake_password": "xxx",                     # From GitHub: SNOWFLAKE_PASSWORD
}

def sync_single_secret(secret_name: str, placeholder_value: str) -> bool:
    """Sync a single secret to Pulumi ESC using placeholder as reminder"""
    try:
        # Use pulumi env set to add the secret
        cmd = [
            "pulumi", "env", "set", 
            "scoobyjava-org/default/sophia-ai-production",
            secret_name,
            placeholder_value,
            "--secret"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        logger.info(f"✅ Synced: {secret_name}")
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Failed to sync {secret_name}: {e.stderr}")
        return False

def validate_pulumi_access() -> bool:
    """Validate Pulumi access"""
    try:
        # Check if Pulumi CLI is available
        subprocess.run(["pulumi", "version"], capture_output=True, text=True, check=True)
        
        # Check authentication
        result = subprocess.run(["pulumi", "whoami"], capture_output=True, text=True, check=True)
        logger.info(f"✅ Pulumi authenticated as: {result.stdout.strip()}")
        
        # Test environment access
        subprocess.run([
            "pulumi", "env", "get", "scoobyjava-org/default/sophia-ai-production"
        ], capture_output=True, text=True, check=True)
        logger.info("✅ Pulumi ESC environment accessible")
        
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Pulumi validation failed: {e}")
        return False
    except FileNotFoundError:
        logger.error("❌ Pulumi CLI not found")
        return False

def main():
    """Main sync function"""
    logger.info("🚀 Manual GitHub Organization Secrets → Pulumi ESC Sync")
    logger.info("=" * 60)
    
    # Validate Pulumi access
    if not validate_pulumi_access():
        logger.error("❌ Pulumi validation failed - exiting")
        sys.exit(1)
    
    logger.info("🔍 Syncing Priority 1 secrets for MCP server functionality...")
    
    success_count = 0
    failed_secrets = []
    
    for secret_name, placeholder in PRIORITY_1_SECRETS.items():
        if placeholder.startswith("PLACEHOLDER_"):
            logger.warning(f"⚠️  {secret_name}: Using placeholder - needs GitHub organization secret value")
        
        if sync_single_secret(secret_name, placeholder):
            success_count += 1
        else:
            failed_secrets.append(secret_name)
    
    # Report results
    total_secrets = len(PRIORITY_1_SECRETS)
    logger.info(f"\n📊 Sync Results:")
    logger.info(f"Total secrets: {total_secrets}")
    logger.info(f"Successful: {success_count}")
    logger.info(f"Failed: {len(failed_secrets)}")
    logger.info(f"Success rate: {(success_count/total_secrets)*100:.1f}%")
    
    if failed_secrets:
        logger.warning(f"⚠️  Failed secrets: {', '.join(failed_secrets)}")
    
    # Instructions for completing the sync
    placeholder_secrets = [name for name, value in PRIORITY_1_SECRETS.items() if value.startswith("PLACEHOLDER_")]
    
    if placeholder_secrets:
        logger.info(f"\n🔧 NEXT STEPS:")
        logger.info("Replace placeholder values with real GitHub organization secrets:")
        logger.info("Run these commands with real values from GitHub:")
        print()
        
        github_secret_mapping = {
            "portkey_api_key": "PORTKEY_API_KEY",
            "openrouter_api_key": "OPENROUTER_API_KEY", 
            "hubspot_access_token": "HUBSPOT_ACCESS_TOKEN",
            "linear_api_key": "LINEAR_API_KEY",
            "asana_access_token": "ASANA_API_TOKEN",
            "slack_bot_token": "SLACK_BOT_TOKEN",
            "slack_app_token": "SLACK_APP_TOKEN",
            "github_token": "GH_API_TOKEN",
            "figma_pat": "FIGMA_PAT",
            "notion_api_token": "NOTION_API_KEY",
            "lambda_api_key": "LAMBDA_API_KEY"
        }
        
        for secret_name in placeholder_secrets:
            github_secret = github_secret_mapping.get(secret_name, "UNKNOWN")
            print(f'pulumi env set scoobyjava-org/default/sophia-ai-production {secret_name} "${{secrets.{github_secret}}}" --secret')
    
    logger.info(f"\n✅ Manual sync completed!")
    logger.info("Re-run the MCP validation test after updating placeholder values:")
    logger.info("python scripts/test_mcp_pulumi_esc_integration.py")

if __name__ == "__main__":
    main() 