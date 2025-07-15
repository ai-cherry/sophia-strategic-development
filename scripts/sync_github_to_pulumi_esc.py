#!/usr/bin/env python3
"""
🔄 GitHub Organization Secrets → Pulumi ESC Synchronization

This script synchronizes all 135+ GitHub Organization Secrets 
to Pulumi ESC for runtime access.

Usage:
    python scripts/sync_github_to_pulumi_esc.py
    python scripts/sync_github_to_pulumi_esc.py --dry-run
    python scripts/sync_github_to_pulumi_esc.py --environment staging
"""

import os
import asyncio
from typing import Dict, List, Optional
import subprocess
import sys
import argparse
from datetime import datetime

# Complete mapping of all 135+ GitHub secrets to ESC keys
GITHUB_TO_ESC_MAPPING = {
    # Core Platform Infrastructure
    "API_SECRET_KEY": "api_secret_key",
    "JWT_SECRET": "jwt_secret",
    "ENCRYPTION_KEY": "encryption_key",
    "BACKUP_ENCRYPTION_KEY": "backup_encryption_key",
    
    # Authentication & Security
    "GH_API_TOKEN": "gh_api_token",
    "GH_CLASSIC_PAT_TOKEN": "gh_classic_pat_token",
    "GH_FINE_GRAINED_TOKEN": "gh_fine_grained_token",
    "GH_IP_ADDRESS": "gh_ip_address",
    "SSH_PRIVATE_KEY": "ssh_private_key",
    "SSH_PUBLIC_KEY": "ssh_public_key",
    "PRODUCTION_SSH_KEY": "production_ssh_key",
    "STAGING_SSH_KEY": "staging_ssh_key",
    "DATABASE_SSH_KEY": "database_ssh_key",
    
    # AI Model Providers (Primary Stack)
    "OPENAI_API_KEY": "openai_api_key",
    "ANTHROPIC_API_KEY": "anthropic_api_key",
    "PORTKEY_API_KEY": "portkey_api_key",
    "PORTKEY_CONFIG": "portkey_config",
    "PORTKEY_CONFIG_ID": "portkey_config_id",
    "OPENROUTER_API_KEY": "openrouter_api_key",
    "LANGCHAIN_API_KEY": "langchain_api_key",
    "LANGGRAPH_API_KEY": "langgraph_api_key",
    "LANGSMITH_API_KEY": "langsmith_api_key",
    "LANGSMITH_ORG_ID": "langsmith_org_id",
    "MEM0_API_KEY": "mem0_api_key",
    
    # Alternative AI Providers
    "MISTRAL_API_KEY": "mistral_api_key",
    "MISTRAL_VIRTUAL_KEY": "mistral_virtual_key",
    "CODESTRAL_API_KEY": "codestral_api_key",
    "CODESTRAL_ORG_ID": "codestral_org_id",
    "CODESTRAL_ORG_NAME": "codestral_org_name",
    "GROQ_API_KEY": "groq_api_key",
    "GROQ_VIRTUAL_KEY": "groq_virtual_key",
    "DEEPSEEK_API_KEY": "deepseek_api_key",
    "COHERE_API_KEY": "cohere_api_key",
    "COHERE_VIRTUAL_KEY": "cohere_virtual_key",
    "LLAMA_API_KEY": "llama_api_key",
    "PERPLEXITY_API_KEY": "perplexity_api_key",
    "XAI_API_KEY": "xai_api_key",
    "QWEN_API_KEY": "qwen_api_key",
    "QWEN_VIRTUAL_KEY": "qwen_virtual_key",
    "VENICE_AI_API_KEY": "venice_ai_api_key",
    "VENICE_API_KEY": "venice_api_key",
    "TOGETHER_AI_API_KEY": "together_ai_api_key",
    "TOGETHERAI_API_KEY": "togetherai_api_key",
    "CONTINUE_API_KEY": "continue_api_key",
    
    # Database & Storage Infrastructure
    "DATABASE_URL": "database_url",
    "DATABASE_HOST": "database_host",
    "QDRANT_API_KEY": "QDRANT_api_key",
    "QDRANT_CLUSTER": "QDRANT_cluster",
    "QDRANT_CLUSTER_URL": "QDRANT_cluster_url",
    "QDRANT_URL": "QDRANT_URL",
    "REDIS_URL": "redis_url",
    "REDIS_PASSWORD": "redis_password",
    "REDIS_DATABASE_NAME": "redis_database_name",
    "REDIS_API_ACCOUNTKEY": "redis_api_accountkey",
    "REDIS_API_USERKEY": "redis_api_userkey",
    "REDIT_DATABASE_ENDPOINT": "redit_database_endpoint",
    
    # Infrastructure & Deployment
    "PULUMI_ACCESS_TOKEN": "pulumi_access_token",
    "PULUMI_CONFIGURE_PASSPHRASE": "pulumi_configure_passphrase",
    "PULUMI_IP_ADDRESS": "pulumi_ip_address",
    "LAMBDA_API_KEY": "lambda_api_key",
    "LAMBDA_CLOUD_API_KEY": "lambda_cloud_api_key",
    "LAMBDA_LABS_API_KEY": "lambda_labs_api_key",
    "LAMBDA_SSH_HOST": "lambda_ssh_host",
    "LAMBDA_SSH_USER": "lambda_ssh_user",
    "DOCKER_USER_NAME": "docker_user_name",
    "DOCKER_PERSONAL_ACCESS_TOKEN": "docker_personal_access_token",
    "DOCKER_TOKEN": "docker_token",
    "DOCKERHUB_USERNAME": "dockerhub_username",
    "KUBERNETES_CLUSTER_ID": "kubernetes_cluster_id",
    "PRODUCTION_HOST": "production_host",
    "STAGING_HOST": "staging_host",
    "LOAD_BALANCER_HOST": "load_balancer_host",
    
    # Business Intelligence Integrations
    "HUBSPOT_ACCESS_TOKEN": "hubspot_access_token",
    "HUBSPOT_API_KEY": "hubspot_api_key",
    "HUBSPOT_CLIENT_SECRET": "hubspot_client_secret",
    "GONG_ACCESS_KEY": "gong_access_key",
    "GONG_ACCESS_KEY_SECRET": "gong_access_key_secret",
    "GONG_CLIENT_ACCESS_KEY": "gong_client_access_key",
    "GONG_CLIENT_SECRET": "gong_client_secret",
    "SLACK_BOT_TOKEN": "slack_bot_token",
    "SLACK_APP_TOKEN": "slack_app_token",
    "SLACK_APP_TOKEN_2": "slack_app_token_2",
    "SLACK_CLIENT_ID": "slack_client_id",
    "SLACK_CLIENT_SECRET": "slack_client_secret",
    "SLACK_SIGNING_SECRET": "slack_signing_secret",
    "SLACK_SOCKET_TOKEN": "slack_socket_token",
    "SLACK_REFRESH_TOKEN": "slack_refresh_token",
    "LINEAR_API_KEY": "linear_api_key",
    "ASANA_API_TOKEN": "asana_api_token",
    "NOTION_API_KEY": "notion_api_key",
    "NOTION_API_TOKEN": "notion_api_token",
    "SALESFORCE_ACCESS_TOKEN": "salesforce_access_token",
    
    # Workflow Automation & ETL
    "ESTUARY_ACCESS_TOKEN": "estuary_access_token",
    "ESTUARY_REFRESH_TOKEN": "estuary_refresh_token",
    "ESTUARY_TENANT": "estuary_tenant",
    "N8N_API_KEY": "n8n_api_key",
    "TERRAFORM_API_TOKEN": "terraform_api_token",
    "TERRAFORM_ORGANIZATION_TOKEN": "terraform_organization_token",
    
    # Development & Code Quality
    "CODACY_API_TOKEN": "codacy_api_token",
    "FIGMA_PAT": "figma_pat",
    "FIGMA_PROJECT_ID": "figma_project_id",
    "NPM_API_TOKEN": "npm_api_token",
    "ARIZE_API_KEY": "arize_api_key",
    "ARIZE_SPACE_ID": "arize_space_id",
    
    # Web Services & APIs
    "EXA_API_KEY": "exa_api_key",
    "SERP_API_KEY": "serp_api_key",
    "TAVILY_API_KEY": "tavily_api_key",
    "BRAVE_API_KEY": "brave_api_key",
    "APIFY_API_TOKEN": "apify_api_token",
    "PHANTOMBUSTER_API_KEY": "phantombuster_api_key",
    "PHANTOM_BUSTER_API_KEY": "phantom_buster_api_key",
    "PIPEDREAM_API_KEY": "pipedream_api_key",
    "PIPEDREAM_OAUTH_CLIENT_ID": "pipedream_oauth_client_id",
    "PIPEDREAM_OAUTH_CLIENT_NAME": "pipedream_oauth_client_name",
    "PIPEDREAM_OAUTH_CLIENT_SECRET": "pipedream_oauth_client_secret",
    "PIPEDREAM_WORKPLACE_ID": "pipedream_workplace_id",
    "ELEVEN_LABS_API_KEY": "eleven_labs_api_key",
    "STABILITY_API_KEY": "stability_api_key",
    "RECRAFT_API_KEY": "recraft_api_key",
    "RESEMBLE_API_KEY": "resemble_api_key",
    "RESEMBLE_STREAMING_ENDPOINT": "resemble_streaming_endpoint",
    "RESEMBLE_SYNTHESIS_ENDPOINT": "resemble_synthesis_endpoint",
    "APOLLO_API_KEY": "apollo_api_key",
    "LATTICE_API_KEY": "lattice_api_key",
    
    # Specialized Services
    "SOURCEGRAPH_API_TOKEN": "sourcegraph_api_token",
    "CREW_API_TOKEN": "crew_api_token",
    "KONG_ACCESS_TOKEN": "kong_access_token",
    "KONG_ORG_ID": "kong_org_id",
    "NGROK_AUTHTOKEN": "ngrok_authtoken",
    "NORDVPN_USERNAME": "nordvpn_username",
    "NORDVPN_PASSWORD": "nordvpn_password",
    "NAMECHEAP_API_KEY": "namecheap_api_key",
    "NAMECHEAP_USERNAME": "namecheap_username",
    "REDDIT_API_KEY": "reddit_api_key",
    "REDDIT_CLIENT_ID": "reddit_client_id",
    "STACKAPPS_CLIENT_SECRET": "stackapps_client_secret",
    "STACKAPP_API_KEY": "stackapp_api_key",
    "SLIDESPEAK_API_KEY": "slidespeak_api_key",
    "TWINGLY_API_KEY": "twingly_api_key",
    "ZENROWS_API_KEY": "zenrows_api_key",
    "EDEN_API_KEY": "eden_api_key",
    "BROWSER_USE_API_KEY": "browser_use_api_key",
    "MUREKA_API_KEY": "mureka_api_key",
    "PATRONUS_API_KEY": "patronus_api_key",
    "BARDEEN_ID": "bardeen_id",
    "MIDJOURNEY_ID": "midjourney_id",
    "PRISMA_API_KEY": "prisma_api_key",
    
    # Sophia AI Specific
    "SOPHIA_AI_TOKEN": "sophia_ai_token",
    "SOPHIA_DEPLOYMENT_KEY_2025": "sophia_deployment_key_2025",
}

class SecretSynchronizer:
    """Synchronizes GitHub Organization Secrets to Pulumi ESC"""
    
    def __init__(self, org: str = "scoobyjava-org", environment: str = "sophia-ai-production"):
        self.org = org
        self.environment = environment
        self.esc_path = f"{org}/default/{environment}"
        
    async def sync_secrets(self, dry_run: bool = False) -> bool:
        """Synchronize all GitHub Organization Secrets to Pulumi ESC"""
        
        print(f"🔄 Starting GitHub → Pulumi ESC synchronization...")
        print(f"📍 Target: {self.esc_path}")
        print(f"🏃 Mode: {'DRY RUN' if dry_run else 'LIVE'}")
        print(f"📊 Total secrets to sync: {len(GITHUB_TO_ESC_MAPPING)}")
        
        if dry_run:
            print("⚠️  DRY RUN MODE - No actual changes will be made")
        
        success_count = 0
        error_count = 0
        missing_count = 0
        
        for github_secret, esc_key in GITHUB_TO_ESC_MAPPING.items():
            try:
                # Get value from GitHub Actions environment
                value = os.getenv(github_secret)
                
                if value:
                    if not dry_run:
                        # Set in Pulumi ESC
                        await self.set_esc_secret(esc_key, value)
                    
                    print(f"✅ {'[DRY RUN] ' if dry_run else ''}Synced: {github_secret} → {esc_key} ({len(value)} chars)")
                    success_count += 1
                else:
                    print(f"⚠️  Missing: {github_secret}")
                    missing_count += 1
                    
            except Exception as e:
                print(f"❌ Error syncing {github_secret}: {e}")
                error_count += 1
        
        # Generate summary
        print(f"\n📊 Synchronization Summary:")
        print(f"✅ Successfully synced: {success_count}")
        print(f"⚠️  Missing secrets: {missing_count}")
        print(f"❌ Errors: {error_count}")
        print(f"📍 Total processed: {len(GITHUB_TO_ESC_MAPPING)}")
        
        success_rate = (success_count / len(GITHUB_TO_ESC_MAPPING)) * 100
        print(f"📈 Success rate: {success_rate:.1f}%")
        
        if not dry_run:
            await self.generate_sync_report(success_count, missing_count, error_count)
        
        return error_count == 0 and success_count > 0
    
    async def set_esc_secret(self, key: str, value: str):
        """Set a secret in Pulumi ESC"""
        
        cmd = [
            "pulumi", "esc", "env", "set",
            self.esc_path,
            f"values.secrets.{key}",
            f'{{"fn::secret": "{value}"}}'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise Exception(f"Failed to set ESC secret: {result.stderr}")
    
    async def validate_esc_access(self) -> bool:
        """Validate that we can access Pulumi ESC"""
        
        print("🔍 Validating Pulumi ESC access...")
        
        try:
            # Check if we can list environments
            cmd = ["pulumi", "env", "ls"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"❌ Cannot access Pulumi ESC: {result.stderr}")
                return False
            
            # Check if our environment exists
            if self.environment not in result.stdout:
                print(f"⚠️  Environment {self.environment} does not exist")
                return False
            
            print(f"✅ Pulumi ESC access validated")
            return True
            
        except Exception as e:
            print(f"❌ ESC validation failed: {e}")
            return False
    
    async def generate_sync_report(self, success_count: int, missing_count: int, error_count: int):
        """Generate a detailed synchronization report"""
        
        report = f"""# 🔄 GitHub → Pulumi ESC Synchronization Report

**Timestamp**: {datetime.now().isoformat()}
**Environment**: {self.environment}
**ESC Path**: {self.esc_path}

## 📊 Summary
- **Total Secrets**: {len(GITHUB_TO_ESC_MAPPING)}
- **Successfully Synced**: {success_count}
- **Missing Secrets**: {missing_count}
- **Errors**: {error_count}
- **Success Rate**: {(success_count / len(GITHUB_TO_ESC_MAPPING)) * 100:.1f}%

## 🎯 Status
{"✅ SYNCHRONIZATION SUCCESSFUL" if error_count == 0 else "⚠️ SYNCHRONIZATION COMPLETED WITH ISSUES"}

## 🔧 Next Steps
1. Verify secrets are accessible in Pulumi ESC
2. Test application startup with ESC integration
3. Update any missing secrets in GitHub Organization
4. Run deployment validation

## 📋 Commands
```bash
# Verify ESC environment
pulumi esc env get {self.esc_path}

# Test secret access
pulumi esc env run {self.esc_path} -- echo "ESC integration working"

# Deploy with ESC
pulumi esc env run {self.esc_path} -- pulumi up --yes --stack {self.environment}
```
"""
        
        try:
            report_file = f"sync_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            with open(report_file, 'w') as f:
                f.write(report)
            print(f"📋 Sync report saved: {report_file}")
        except Exception as e:
            print(f"⚠️  Could not save report: {e}")

async def main():
    parser = argparse.ArgumentParser(
        description="Synchronize GitHub Organization Secrets to Pulumi ESC"
    )
    parser.add_argument(
        "--dry-run", 
        action="store_true", 
        help="Show what would be synced without making changes"
    )
    parser.add_argument(
        "--environment", 
        default="default/sophia-ai-production",
        help="Target ESC environment (default: default/sophia-ai-production)"
    )
    parser.add_argument(
        "--org", 
        default="scoobyjava-org",
        help="Pulumi organization (default: scoobyjava-org)"
    )
    
    args = parser.parse_args()
    
    # Initialize synchronizer
    synchronizer = SecretSynchronizer(
        org=args.org,
        environment=args.environment
    )
    
    # Validate ESC access
    if not await synchronizer.validate_esc_access():
        print("❌ Cannot access Pulumi ESC. Please check your configuration.")
        sys.exit(1)
    
    # Synchronize secrets
    success = await synchronizer.sync_secrets(dry_run=args.dry_run)
    
    if success:
        print("\n🎉 Secret synchronization completed successfully!")
        if not args.dry_run:
            print("🚀 Sophia AI is ready for deployment with unified secret management!")
    else:
        print("\n❌ Secret synchronization failed!")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 