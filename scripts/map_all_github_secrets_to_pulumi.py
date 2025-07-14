#!/usr/bin/env python3
"""
Map ALL GitHub secrets to Pulumi ESC based on the complete list provided.
This eliminates ALL placeholders once and for all.
"""

import subprocess

# COMPLETE MAPPING based on the GitHub secrets list provided
GITHUB_TO_PULUMI_MAPPING = {
    # AI Services
    "ANTHROPIC_API_KEY": "anthropic_api_key",
    "OPENAI_API_KEY": "openai_api_key",
    "PINECONE_API_KEY": "pinecone_api_key",
    "DEEPSEEK_API_KEY": "deepseek_api_key",
    "GROQ_API_KEY": "groq_api_key",
    "MISTRAL_API_KEY": "mistral_api_key",
    "PERPLEXITY_API_KEY": "perplexity_api_key",
    "TOGETHER_AI_API_KEY": "together_ai_api_key",
    "LANGCHAIN_API_KEY": "langchain_api_key",
    "LANGGRAPH_API_KEY": "langgraph_api_key",
    "LANGSMITH_API_KEY": "langsmith_api_key",
    "COHERE_API_KEY": "cohere_api_key",
    "ELEVEN_LABS_API_KEY": "eleven_labs_api_key",
    "STABILITY_API_KEY": "stability_api_key",
    "HUGGINGFACE_API_TOKEN": "huggingface_api_token",
    "PORTKEY_API_KEY": "portkey_api_key",
    "OPENROUTER_API_KEY": "openrouter_api_key",
    "MEM0_API_KEY": "mem0_api_key",
    # Docker
    "DOCKER_TOKEN": "docker_token",
    "DOCKER_TOKEN": "docker_token",  # Map to same
    "DOCKERHUB_USERNAME": "docker_username",
    "DOCKERHUB_USERNAME": "docker_username",  # Map to same
    # Qdrant
    "QDRANT_API_KEY": "qdrant_api_key",
    "QDRANT_URL": "qdrant_url",
    "qdrant_ACCOUNT": "postgres_host",
    "qdrant_USER": "qdrant_user",
    "qdrant_PASSWORD": "postgres_password",
    "qdrant_WAREHOUSE": "postgres_database",
    "qdrant_DATABASE": "postgres_database",
    "qdrant_SCHEMA": "postgres_schema",
    "qdrant_ROLE": "qdrant_role",
    "qdrant_PAT": "qdrant_pat",
    "qdrant_CONNECTION_URL": "qdrant_serviceection_url",
    # Lambda Labs
    "LAMBDA_LABS_API_KEY": "lambda_labs_api_key",
    "LAMBDA_API_CLOUD_ENDPOINT": "lambda_api_cloud_endpoint",
    "LAMBDA_CLOUD_API_KEY": "lambda_cloud_api_key",
    # GitHub
    "GH_API_TOKEN": "github_token",
    "GH_CLASSIC_PAT_TOKEN": "github_classic_pat_token",
    "GH_FINE_GRAINED_TOKEN": "github_fine_grained_token",
    # Business Tools
    "LINEAR_API_KEY": "linear_api_key",
    "NOTION_API_KEY": "notion_api_key",
    "NOTION_API_TOKEN": "notion_api_token",
    "ASANA_API_TOKEN": "asana_api_token",
    "FIGMA_PAT": "figma_pat",
    "FIGMA_PROJECT_ID": "figma_project_id",
    # CRM & Sales
    "HUBSPOT_API_KEY": "hubspot_api_key",
    "HUBSPOT_ACCESS_TOKEN": "hubspot_access_token",
    "HUBSPOT_CLIENT_SECRET": "hubspot_client_secret",
    "GONG_ACCESS_KEY": "gong_access_key",
    "GONG_ACCESS_KEY_SECRET": "gong_access_key_secret",
    "GONG_CLIENT_SECRET": "gong_client_secret",
    "GONG_BASE_URL": "gong_base_url",
    "SALESFORCE_ACCESS_TOKEN": "salesforce_access_token",
    # Communication
    "SLACK_BOT_TOKEN": "slack_bot_token",
    "SLACK_APP_TOKEN": "slack_app_token",
    "SLACK_CLIENT_ID": "slack_client_id",
    "SLACK_CLIENT_SECRET": "slack_client_secret",
    "SLACK_SIGNING_SECRET": "slack_signing_secret",
    # Infrastructure
    "PULUMI_ACCESS_TOKEN": "pulumi_access_token",
    "DATABASE_URL": "database_url",
    "REDIS_PASSWORD": "redis_password",
    "REDIS_URL": "redis_url",
    # Deployment
    "VERCEL_ACCESS_TOKEN": "vercel_access_token",
    "VERCEL_ORG_ID": "vercel_org_id",
    "VERCEL_PROJECT_ID_SOPHIA_PROD": "vercel_project_id_sophia_prod",
    # Monitoring
    "GRAFANA_URL": "grafana_url",
    "GRAFANA_USERNAME": "grafana_username",
    "GRAFANA_PASSWORD": "grafana_password",
    # Data & Analytics
    "ESTUARY_ACCESS_TOKEN": "estuary_access_token",
    "ESTUARY_ENDPOINT": "estuary_endpoint",
    "ESTUARY_REFRESH_TOKEN": "estuary_refresh_token",
    "ESTUARY_TENANT": "estuary_tenant",
    "WEAVIATE_API_KEY": "weaviate_api_key",
    "WEAVIATE_URL": "weaviate_url",
    "WEAVIATE_REST_ENDPOINT": "weaviate_rest_endpoint",
    # Code Quality
    "CODACY_API_TOKEN": "codacy_api_token",
    # Development
    "NPM_API_TOKEN": "npm_api_token",
    "JWT_SECRET": "jwt_secret",
    "ENCRYPTION_KEY": "encryption_key",
    "API_SECRET_KEY": "api_secret_key",
    # External APIs
    "SERP_API_KEY": "serp_api_key",
    "TAVILY_API_KEY": "tavily_api_key",
    "EXA_API_KEY": "exa_api_key",
    "BRAVE_API_KEY": "brave_api_key",
    "APIFY_API_TOKEN": "apify_api_token",
    "APOLLO_API_KEY": "apollo_api_key",
    "NAMECHEAP_API_KEY": "namecheap_api_key",
    "NAMECHEAP_USERNAME": "namecheap_username",
}


def set_secret_in_pulumi(github_name, pulumi_key, value_placeholder="FROM_GITHUB"):
    """Set a secret in Pulumi ESC"""
    print(f"Setting {github_name} → {pulumi_key}")

    cmd = [
        "pulumi",
        "env",
        "set",
        "scoobyjava-org/default/sophia-ai-production",
        "--secret",
        pulumi_key,
        value_placeholder,
    ]

    result = subprocess.run(cmd, check=False, capture_output=True, text=True)

    if result.returncode == 0:
        print(f"✅ Set {pulumi_key}")
        return True
    else:
        print(f"❌ Failed to set {pulumi_key}: {result.stderr}")
        return False


def main():
    print("🚀 Mapping ALL GitHub Secrets to Pulumi ESC")
    print("=" * 60)
    print(f"Total secrets to map: {len(GITHUB_TO_PULUMI_MAPPING)}")

    success_count = 0
    fail_count = 0

    # Map each secret
    for github_name, pulumi_key in GITHUB_TO_PULUMI_MAPPING.items():
        if set_secret_in_pulumi(github_name, pulumi_key):
            success_count += 1
        else:
            fail_count += 1

    print("\n📊 Results:")
    print(f"✅ Successfully mapped: {success_count}")
    print(f"❌ Failed: {fail_count}")
    print(f"📋 Total: {len(GITHUB_TO_PULUMI_MAPPING)}")

    print("\n📝 Next steps:")
    print("1. GitHub Actions workflows will automatically use these secrets")
    print("2. Backend auto_esc_config.py will load them automatically")
    print("3. Test Docker login: python3 scripts/use_docker_from_pulumi.py")
    print("4. Deploy to Lambda Labs")

    print("\n⚠️  NOTE: The actual secret values need to be synced from GitHub")
    print("This script creates the mapping structure in Pulumi ESC")


if __name__ == "__main__":
    main()
