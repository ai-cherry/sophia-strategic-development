#!/usr/bin/env python3
"""
Sophia AI - GitHub Organization Secrets → Pulumi ESC Sync Script
This script synchronizes secrets from GitHub organization to Pulumi ESC
for the Sophia AI platform.
"""

import os
import sys
import json
import subprocess
import logging
from typing import Dict, Optional, Any
from dataclasses import dataclass

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class SyncResult:
    """Result of a secret sync operation."""
    secret_name: str
    success: bool
    error_message: Optional[str] = None

class PulumiESCSync:
    """Synchronizes GitHub organization secrets to Pulumi ESC."""
    
    def __init__(self):
        self.pulumi_org = "scoobyjava-org"
        self.pulumi_env = "sophia-ai-production"
        self.env_path = f"{self.pulumi_org}/default/{self.pulumi_env}"
        
        # GitHub secrets to Pulumi ESC path mapping
        # CRITICAL: These GitHub secret names must match exactly what's in .github/workflows/sync_secrets.yml
        # CRITICAL: Pulumi paths must match what backend/core/auto_esc_config.py expects
        self.secret_mappings = {
            # AI Services - backend expects values.sophia.ai.*
            "OPENAI_API_KEY": "values.sophia.ai.openai.api_key",
            "ANTHROPIC_API_KEY": "values.sophia.ai.anthropic.api_key",
            "HUGGINGFACE_API_TOKEN": "values.sophia.ai.huggingface.api_token",
            "LANGCHAIN_API_KEY": "values.sophia.ai.langchain.api_key",
            "LANGSMITH_API_KEY": "values.sophia.ai.langsmith.api_key",
            "PORTKEY_API_KEY": "values.sophia.ai.portkey.api_key",
            "OPENROUTER_API_KEY": "values.sophia.ai.openrouter.api_key",
            "PERPLEXITY_API_KEY": "values.sophia.ai.perplexity.api_key",
            "MISTRAL_API_KEY": "values.sophia.ai.mistral.api_key",
            "DEEPSEEK_API_KEY": "values.sophia.ai.deepseek.api_key",
            "CODESTRAL_API_KEY": "values.sophia.ai.codestral.api_key",
            "TOGETHERAI_API_KEY": "values.sophia.ai.togetherai.api_key",
            "XAI_API_KEY": "values.sophia.ai.xai.api_key",
            "VENICE_AI_API_KEY": "values.sophia.ai.venice_ai.api_key",
            "LLAMA_API_KEY": "values.sophia.ai.llama.api_key",
            
            # Business Intelligence - backend expects values.sophia.business.*
            "GONG_ACCESS_KEY": "values.sophia.business.gong.access_key",
            "GONG_CLIENT_SECRET": "values.sophia.business.gong.client_secret",
            "GONG_BASE_URL": "values.sophia.business.gong.base_url",
            "HUBSPOT_ACCESS_TOKEN": "values.sophia.business.hubspot.access_token",
            "SALESFORCE_ACCESS_TOKEN": "values.sophia.business.salesforce.access_token",
            "LINEAR_API_KEY": "values.sophia.business.linear.api_key",
            "NOTION_API_KEY": "values.sophia.business.notion.api_key",
            
            # Communication - backend expects values.sophia.communication.*
            "SLACK_BOT_TOKEN": "values.sophia.communication.slack.bot_token",
            "SLACK_APP_TOKEN": "values.sophia.communication.slack.app_token",
            "SLACK_SIGNING_SECRET": "values.sophia.communication.slack.signing_secret",
            "SLACK_CLIENT_ID": "values.sophia.communication.slack.client_id",
            "SLACK_CLIENT_SECRET": "values.sophia.communication.slack.client_secret",
            
            # Data Infrastructure - backend expects values.sophia.data.*
            "SNOWFLAKE_ACCOUNT": "values.sophia.data.snowflake.account",
            "SNOWFLAKE_USER": "values.sophia.data.snowflake.user",
            "SNOWFLAKE_ROLE": "values.sophia.data.snowflake.role",
            "SNOWFLAKE_PASSWORD": "values.sophia.data.snowflake.password",
            "PINECONE_API_KEY": "values.sophia.data.pinecone.api_key",
            "PINECONE_ENVIRONMENT": "values.sophia.data.pinecone.environment",
            "PINECONE_INDEX_NAME": "values.sophia.data.pinecone.index_name",
            "WEAVIATE_API_KEY": "values.sophia.data.weaviate.api_key",
            "WEAVIATE_URL": "values.sophia.data.weaviate.url",
            "WEAVIATE_REST_ENDPOINT": "values.sophia.data.weaviate.rest_endpoint",
            "WEAVIATE_GRPC_ENDPOINT": "values.sophia.data.weaviate.grpc_endpoint",
            "DATABASE_URL": "values.sophia.data.database.url",
            "REDIS_URL": "values.sophia.data.redis.url",
            
            # Observability & Monitoring
            "ARIZE_API_KEY": "values.sophia.monitoring.arize.api_key",
            "ARIZE_SPACE_ID": "values.sophia.monitoring.arize.space_id",
            "GRAFANA_URL": "values.sophia.monitoring.grafana.url",
            "GRAFANA_USERNAME": "values.sophia.monitoring.grafana.username",
            "GRAFANA_PASSWORD": "values.sophia.monitoring.grafana.password",
            "PROMETHEUS_URL": "values.sophia.monitoring.prometheus.url",
            
            # Cloud Infrastructure - FIXED: GitHub workflow has LAMBDA_API_KEY, not LAMBDA_LABS_API_KEY
            "LAMBDA_API_KEY": "values.sophia.infrastructure.lambda_labs.api_key",
            "VERCEL_ACCESS_TOKEN": "values.sophia.infrastructure.vercel.access_token",
            "VULTR_API_KEY": "values.sophia.infrastructure.vultr.api_key",
            "PULUMI_ACCESS_TOKEN": "values.sophia.infrastructure.pulumi.access_token",
            
            # Research Tools
            "APIFY_API_TOKEN": "values.sophia.research.apify.api_token",
            "SERP_API_KEY": "values.sophia.research.serp.api_key",
            "TAVILY_API_KEY": "values.sophia.research.tavily.api_key",
            "EXA_API_KEY": "values.sophia.research.exa.api_key",
            "BRAVE_API_KEY": "values.sophia.research.brave.api_key",
            "ZENROWS_API_KEY": "values.sophia.research.zenrows.api_key",
            
            # Development Tools
            "GH_API_TOKEN": "values.sophia.development.github.api_token",
            "RETOOL_API_TOKEN": "values.sophia.development.retool.api_token",
            "DOCKER_TOKEN": "values.sophia.development.docker.token",
            "NPM_API_TOKEN": "values.sophia.development.npm.api_token",
            
            # Data Integration
            "AIRBYTE_ACCESS_TOKEN": "values.sophia.integration.airbyte.access_token",
            "ESTUARY_ACCESS_TOKEN": "values.sophia.integration.estuary.access_token",
            "PIPEDREAM_API_KEY": "values.sophia.integration.pipedream.api_key",
            
            # Security
            "JWT_SECRET": "values.sophia.security.jwt.secret",
            "ENCRYPTION_KEY": "values.sophia.security.encryption.key",
            "API_SECRET_KEY": "values.sophia.security.api.secret_key",
        }
    
    def validate_prerequisites(self) -> bool:
        """Validate that all prerequisites are met."""
        logger.info("🔍 Validating prerequisites...")
        
        # Check Pulumi access token
        if not os.getenv("PULUMI_ACCESS_TOKEN"):
            logger.error("❌ PULUMI_ACCESS_TOKEN not set")
            return False
        
        # Check if Pulumi CLI is available
        try:
            result = subprocess.run(
                ["pulumi", "version"],
                capture_output=True,
                text=True,
                check=True
            )
            logger.info(f"✅ Pulumi CLI available: {result.stdout.strip()}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.error("❌ Pulumi CLI not available")
            return False
        
        # Test Pulumi login
        try:
            subprocess.run(
                ["pulumi", "whoami"],
                capture_output=True,
                text=True,
                check=True
            )
            logger.info("✅ Pulumi authentication successful")
        except subprocess.CalledProcessError:
            logger.error("❌ Pulumi authentication failed")
            return False
        
        return True
    
    def sync_secret(self, github_secret: str, pulumi_path: str) -> SyncResult:
        """Sync a single secret from GitHub to Pulumi ESC."""
        value = os.getenv(github_secret)
        
        if not value:
            return SyncResult(
                secret_name=github_secret,
                success=False,
                error_message="Secret not found in environment variables"
            )
        
        try:
            cmd = [
                "pulumi", "env", "set",
                self.env_path,
                pulumi_path,
                value,
                "--secret"
            ]
            
            subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            logger.info(f"✅ Synced: {github_secret} → {pulumi_path}")
            return SyncResult(secret_name=github_secret, success=True)
            
        except subprocess.CalledProcessError as e:
            error_msg = f"Pulumi command failed: {e.stderr}"
            logger.error(f"❌ Failed to sync {github_secret}: {error_msg}")
            return SyncResult(
                secret_name=github_secret,
                success=False,
                error_message=error_msg
            )
    
    def sync_all_secrets(self) -> Dict[str, SyncResult]:
        """Sync all configured secrets."""
        logger.info(f"🔄 Starting sync to Pulumi ESC environment: {self.env_path}")
        
        results = {}
        success_count = 0
        total_count = len(self.secret_mappings)
        
        for github_secret, pulumi_path in self.secret_mappings.items():
            result = self.sync_secret(github_secret, pulumi_path)
            results[github_secret] = result
            
            if result.success:
                success_count += 1
        
        logger.info(f"📊 Sync completed: {success_count}/{total_count} secrets synced successfully")
        
        # Log failures
        failures = [name for name, result in results.items() if not result.success]
        if failures:
            logger.warning(f"⚠️  Failed to sync: {', '.join(failures)}")
        
        return results
    
    def generate_summary_report(self, results: Dict[str, SyncResult]) -> Dict[str, Any]:
        """Generate a summary report of the sync operation."""
        successful = [name for name, result in results.items() if result.success]
        failed = [name for name, result in results.items() if not result.success]
        
        report = {
            "sync_timestamp": subprocess.run(
                ["date", "-u", "+%Y-%m-%dT%H:%M:%SZ"],
                capture_output=True,
                text=True
            ).stdout.strip(),
            "pulumi_environment": self.env_path,
            "total_secrets": len(results),
            "successful_syncs": len(successful),
            "failed_syncs": len(failed),
            "success_rate": f"{(len(successful) / len(results) * 100):.1f}%",
            "successful_secrets": successful,
            "failed_secrets": [
                {
                    "name": name,
                    "error": results[name].error_message
                }
                for name in failed
            ]
        }
        
        return report

def main():
    """Main entry point."""
    logger.info("🚀 Sophia AI - GitHub Secrets → Pulumi ESC Sync")
    logger.info("=" * 50)
    
    sync = PulumiESCSync()
    
    # Validate prerequisites
    if not sync.validate_prerequisites():
        logger.error("❌ Prerequisites validation failed")
        sys.exit(1)
    
    # Perform sync
    results = sync.sync_all_secrets()
    
    # Generate and display report
    report = sync.generate_summary_report(results)
    
    logger.info("📋 Sync Summary Report:")
    logger.info("-" * 30)
    logger.info(f"Environment: {report['pulumi_environment']}")
    logger.info(f"Total Secrets: {report['total_secrets']}")
    logger.info(f"Successful: {report['successful_syncs']}")
    logger.info(f"Failed: {report['failed_syncs']}")
    logger.info(f"Success Rate: {report['success_rate']}")
    
    if report['failed_secrets']:
        logger.info("\n❌ Failed Secrets:")
        for failed in report['failed_secrets']:
            logger.info(f"  - {failed['name']}: {failed['error']}")
    
    # Write report to file for GitHub Actions artifact
    with open('sync_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    logger.info("\n✅ Sync completed! Report saved to sync_report.json")
    
    # Exit with error code if any secrets failed to sync
    if report['failed_syncs'] > 0:
        sys.exit(1)

if __name__ == "__main__":
    main()
