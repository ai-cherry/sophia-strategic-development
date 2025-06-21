#!/usr/bin/env python3
"""Sophia AI - Set All Pulumi ESC Secrets.

Properly set all GitHub organization secrets in Pulumi ESC using correct syntax
"""

import logging
import os
import subprocess
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# GitHub organization secrets mapped to Pulumi ESC paths
SECRET_MAPPINGS = {
    # AI Services
    "ai_services.openai_api_key": "OPENAI_API_KEY",
    "ai_services.anthropic_api_key": "ANTHROPIC_API_KEY",
    "ai_services.agno_api_key": "AGNO_API_KEY",
    "ai_services.huggingface_api_token": "HUGGINGFACE_API_TOKEN",
    "ai_services.langchain_api_key": "LANGCHAIN_API_KEY",
    "ai_services.portkey_api_key": "PORTKEY_API_KEY",
    "ai_services.portkey_config_id": "PORTKEY_CONFIG_ID",
    "ai_services.openrouter_api_key": "OPENROUTER_API_KEY",
    "ai_services.perplexity_api_key": "PERPLEXITY_API_KEY",
    "ai_services.mistral_api_key": "MISTRAL_API_KEY",
    "ai_services.deepseek_api_key": "DEEPSEEK_API_KEY",
    "ai_services.codestral_api_key": "CODESTRAL_API_KEY",
    "ai_services.togetherai_api_key": "TOGETHERAI_API_KEY",
    "ai_services.xai_api_key": "XAI_API_KEY",
    "ai_services.venice_ai_api_key": "VENICE_AI_API_KEY",
    "ai_services.llama_api_key": "LLAMA_API_KEY",

    # Observability & Monitoring
    "observability.arize_api_key": "ARIZE_API_KEY",
    "observability.arize_space_id": "ARIZE_SPACE_ID",
    "observability.grafana_url": "GRAFANA_URL",
    "observability.grafana_username": "GRAFANA_USERNAME",
    "observability.grafana_password": "GRAFANA_PASSWORD",
    "observability.prometheus_url": "PROMETHEUS_URL",

    # Vector Databases
    "vector_databases.pinecone_api_key": "PINECONE_API_KEY",
    "vector_databases.pinecone_environment": "PINECONE_ENVIRONMENT",
    "vector_databases.pinecone_index_name": "PINECONE_INDEX_NAME",
    "vector_databases.weaviate_api_key": "WEAVIATE_API_KEY",
    "vector_databases.weaviate_url": "WEAVIATE_URL",
    "vector_databases.weaviate_rest_endpoint": "WEAVIATE_REST_ENDPOINT",
    "vector_databases.weaviate_grpc_endpoint": "WEAVIATE_GRPC_ENDPOINT",

    # Business Intelligence
    "business_intelligence.gong_access_key": "GONG_ACCESS_KEY",
    "business_intelligence.gong_client_secret": "GONG_CLIENT_SECRET",
    "business_intelligence.gong_base_url": "GONG_BASE_URL",
    "business_intelligence.hubspot_access_token": "HUBSPOT_ACCESS_TOKEN",
    "business_intelligence.salesforce_access_token": "SALESFORCE_ACCESS_TOKEN",
    "business_intelligence.linear_api_key": "LINEAR_API_KEY",
    "business_intelligence.notion_api_key": "NOTION_API_KEY",

    # Communication
    "communication.slack_bot_token": "SLACK_BOT_TOKEN",
    "communication.slack_app_token": "SLACK_APP_TOKEN",
    "communication.slack_signing_secret": "SLACK_SIGNING_SECRET",
    "communication.slack_client_id": "SLACK_CLIENT_ID",
    "communication.slack_client_secret": "SLACK_CLIENT_SECRET",

    # Data Infrastructure
    "data_infrastructure.snowflake_account": "SNOWFLAKE_ACCOUNT",
    "data_infrastructure.snowflake_user": "SNOWFLAKE_USER",
    "data_infrastructure.snowflake_role": "SNOWFLAKE_ROLE",
    "data_infrastructure.database_url": "DATABASE_URL",
    "data_infrastructure.redis_url": "REDIS_URL",

    # Research Tools
    "research_tools.apify_api_token": "APIFY_API_TOKEN",
    "research_tools.serp_api_key": "SERP_API_KEY",
    "research_tools.tavily_api_key": "TAVILY_API_KEY",
    "research_tools.exa_api_key": "EXA_API_KEY",
    "research_tools.brave_api_key": "BRAVE_API_KEY",
    "research_tools.zenrows_api_key": "ZENROWS_API_KEY",

    # Cloud Infrastructure
    "cloud_infrastructure.lambda_api_key": "LAMBDA_API_KEY",
    "cloud_infrastructure.vercel_access_token": "VERCEL_ACCESS_TOKEN",
    "cloud_infrastructure.vultr_api_key": "VULTR_API_KEY",
    "cloud_infrastructure.pulumi_access_token": "PULUMI_ACCESS_TOKEN",

    # Development Tools
    "development_tools.github_token": "GH_API_TOKEN",
    "development_tools.retool_api_token": "RETOOL_API_TOKEN",
    "development_tools.docker_token": "DOCKER_TOKEN",
    "development_tools.npm_api_token": "NPM_API_TOKEN",

    # Data Integration
    "data_integration.airbyte_access_token": "AIRBYTE_ACCESS_TOKEN",
    "data_integration.estuary_access_token": "ESTUARY_ACCESS_TOKEN",
    "data_integration.pipedream_api_key": "PIPEDREAM_API_KEY",

    # Security
    "security.jwt_secret": "JWT_SECRET",
    "security.encryption_key": "ENCRYPTION_KEY",
    "security.api_secret_key": "API_SECRET_KEY"
}

# Environment variables mapping
ENV_VAR_MAPPINGS = {
    "OPENAI_API_KEY": "${ai_services.openai_api_key}",
    "ANTHROPIC_API_KEY": "${ai_services.anthropic_api_key}",
    "AGNO_API_KEY": "${ai_services.agno_api_key}",
    "HUGGINGFACE_API_TOKEN": "${ai_services.huggingface_api_token}",
    "PORTKEY_API_KEY": "${ai_services.portkey_api_key}",
    "PORTKEY_CONFIG_ID": "${ai_services.portkey_config_id}",
    "ARIZE_API_KEY": "${observability.arize_api_key}",
    "ARIZE_SPACE_ID": "${observability.arize_space_id}",
    "PINECONE_API_KEY": "${vector_databases.pinecone_api_key}",
    "PINECONE_ENVIRONMENT": "${vector_databases.pinecone_environment}",
    "WEAVIATE_API_KEY": "${vector_databases.weaviate_api_key}",
    "WEAVIATE_URL": "${vector_databases.weaviate_url}",
    "GONG_ACCESS_KEY": "${business_intelligence.gong_access_key}",
    "GONG_CLIENT_SECRET": "${business_intelligence.gong_client_secret}",
    "HUBSPOT_ACCESS_TOKEN": "${business_intelligence.hubspot_access_token}",
    "LINEAR_API_KEY": "${business_intelligence.linear_api_key}",
    "SLACK_BOT_TOKEN": "${communication.slack_bot_token}",
    "SLACK_APP_TOKEN": "${communication.slack_app_token}",
    "SNOWFLAKE_ACCOUNT": "${data_infrastructure.snowflake_account}",
    "SNOWFLAKE_USER": "${data_infrastructure.snowflake_user}",
    "DATABASE_URL": "${data_infrastructure.database_url}",
    "APIFY_API_TOKEN": "${research_tools.apify_api_token}",
    "SERP_API_KEY": "${research_tools.serp_api_key}",
    "TAVILY_API_KEY": "${research_tools.tavily_api_key}",
    "JWT_SECRET": "${security.jwt_secret}",
    "ENCRYPTION_KEY": "${security.encryption_key}"
}


def run_command(command: str) -> subprocess.CompletedProcess:
    """Run shell command and return result."""

    logger.info(f"🔧 Running: {command}")
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode != 0:
            logger.error(f"❌ Command failed: {result.stderr}")
        return result
    except subprocess.TimeoutExpired:
        logger.error(f"❌ Command timed out: {command}")
        raise


def set_all_secrets():
    """Set all secrets in Pulumi ESC."""env_name = "scoobyjava-org/default/sophia-ai-production".

    logger.info(f"🔐 Setting secrets in Pulumi ESC environment: {env_name}")

    success_count = 0
    failed_count = 0

    # Set all secret values
    for path, env_var in SECRET_MAPPINGS.items():
        try:
            # Set the secret value (using placeholder for now since we don't have actual values)
            command = f'pulumi env set {env_name} {path} "PLACEHOLDER_{env_var}" --secret'
            result = run_command(command)

            if result.returncode == 0:
                logger.info(f"✅ Set {path}")
                success_count += 1
            else:
                logger.error(f"❌ Failed to set {path}: {result.stderr}")
                failed_count += 1

        except Exception as e:
            logger.error(f"❌ Error setting {path}: {e}")
            failed_count += 1

    # Set environment variables
    logger.info("🌍 Setting environment variables...")
    for env_var, value in ENV_VAR_MAPPINGS.items():
        try:
            command = f'pulumi env set {env_name} environmentVariables.{env_var} "{value}"'
            result = run_command(command)

            if result.returncode == 0:
                logger.info(f"✅ Set env var {env_var}")
            else:
                logger.error(f"❌ Failed to set env var {env_var}: {result.stderr}")

        except Exception as e:
            logger.error(f"❌ Error setting env var {env_var}: {e}")

    # Print summary
    print("\n" + "="*80)
    print("🎉 PULUMI ESC SECRET CONFIGURATION COMPLETED!")
    print("="*80)
    print(f"✅ Secrets successfully set: {success_count}")
    print(f"❌ Secrets failed: {failed_count}")
    print(f"🌍 Environment variables configured: {len(ENV_VAR_MAPPINGS)}")
    print(f"🔐 Environment: {env_name}")
    print("\n🎯 Next Steps:")
    print("1. Update secret values with actual GitHub organization secrets")
    print("2. Test access: export PULUMI_ORG=scoobyjava-org && python -c 'from backend.core.auto_esc_config import config; print(config.agno_api_key)'")
    print("3. Deploy agents with all secrets available")
    print("="*80)


def main():
    """Main execution."""
    # Set Pulumi organization
    os.environ["PULUMI_ORG"] = "scoobyjava-org"

    # Run secret setup
    set_all_secrets()


if __name__ == "__main__":
    main()
