#!/bin/bash
# Fix missing secrets in Pulumi ESC

set -e

echo "🔧 Fixing missing secrets in Pulumi ESC..."


# openai_api_key
if [ -n "${OPENAI_API_KEY}" ]; then
    echo "Setting openai_api_key..."
    pulumi env set scoobyjava-org/default/sophia-ai-production values.sophia.openai_api_key "${OPENAI_API_KEY}"
else
    echo "⚠️  OPENAI_API_KEY not set in environment"
fi

# anthropic_api_key
if [ -n "${ANTHROPIC_API_KEY}" ]; then
    echo "Setting anthropic_api_key..."
    pulumi env set scoobyjava-org/default/sophia-ai-production values.sophia.anthropic_api_key "${ANTHROPIC_API_KEY}"
else
    echo "⚠️  ANTHROPIC_API_KEY not set in environment"
fi

# perplexity_api_key
if [ -n "${PERPLEXITY_API_KEY}" ]; then
    echo "Setting perplexity_api_key..."
    pulumi env set scoobyjava-org/default/sophia-ai-production values.sophia.perplexity_api_key "${PERPLEXITY_API_KEY}"
else
    echo "⚠️  PERPLEXITY_API_KEY not set in environment"
fi

# gong_access_key
if [ -n "${GONG_ACCESS_KEY}" ]; then
    echo "Setting gong_access_key..."
    pulumi env set scoobyjava-org/default/sophia-ai-production values.sophia.gong_access_key "${GONG_ACCESS_KEY}"
else
    echo "⚠️  GONG_ACCESS_KEY not set in environment"
fi

# gong_instance_url
if [ -n "${GONG_INSTANCE_URL}" ]; then
    echo "Setting gong_instance_url..."
    pulumi env set scoobyjava-org/default/sophia-ai-production values.sophia.gong_instance_url "${GONG_INSTANCE_URL}"
else
    echo "⚠️  GONG_INSTANCE_URL not set in environment"
fi

# hubspot_access_token
if [ -n "${HUBSPOT_ACCESS_TOKEN}" ]; then
    echo "Setting hubspot_access_token..."
    pulumi env set scoobyjava-org/default/sophia-ai-production values.sophia.hubspot_access_token "${HUBSPOT_ACCESS_TOKEN}"
else
    echo "⚠️  HUBSPOT_ACCESS_TOKEN not set in environment"
fi

# hubspot_api_key
if [ -n "${HUBSPOT_API_KEY}" ]; then
    echo "Setting hubspot_api_key..."
    pulumi env set scoobyjava-org/default/sophia-ai-production values.sophia.hubspot_api_key "${HUBSPOT_API_KEY}"
else
    echo "⚠️  HUBSPOT_API_KEY not set in environment"
fi

# slack_bot_token
if [ -n "${SLACK_BOT_TOKEN}" ]; then
    echo "Setting slack_bot_token..."
    pulumi env set scoobyjava-org/default/sophia-ai-production values.sophia.slack_bot_token "${SLACK_BOT_TOKEN}"
else
    echo "⚠️  SLACK_BOT_TOKEN not set in environment"
fi

# slack_app_token
if [ -n "${SLACK_APP_TOKEN}" ]; then
    echo "Setting slack_app_token..."
    pulumi env set scoobyjava-org/default/sophia-ai-production values.sophia.slack_app_token "${SLACK_APP_TOKEN}"
else
    echo "⚠️  SLACK_APP_TOKEN not set in environment"
fi

# slack_signing_secret
if [ -n "${SLACK_SIGNING_SECRET}" ]; then
    echo "Setting slack_signing_secret..."
    pulumi env set scoobyjava-org/default/sophia-ai-production values.sophia.slack_signing_secret "${SLACK_SIGNING_SECRET}"
else
    echo "⚠️  SLACK_SIGNING_SECRET not set in environment"
fi

# linear_api_key
if [ -n "${LINEAR_API_KEY}" ]; then
    echo "Setting linear_api_key..."
    pulumi env set scoobyjava-org/default/sophia-ai-production values.sophia.linear_api_key "${LINEAR_API_KEY}"
else
    echo "⚠️  LINEAR_API_KEY not set in environment"
fi

# snowflake_account
if [ -n "${SNOWFLAKE_ACCOUNT}" ]; then
    echo "Setting snowflake_account..."
    pulumi env set scoobyjava-org/default/sophia-ai-production values.sophia.snowflake_account "${SNOWFLAKE_ACCOUNT}"
else
    echo "⚠️  SNOWFLAKE_ACCOUNT not set in environment"
fi

# snowflake_user
if [ -n "${SNOWFLAKE_USER}" ]; then
    echo "Setting snowflake_user..."
    pulumi env set scoobyjava-org/default/sophia-ai-production values.sophia.snowflake_user "${SNOWFLAKE_USER}"
else
    echo "⚠️  SNOWFLAKE_USER not set in environment"
fi

# snowflake_password
if [ -n "${SNOWFLAKE_PASSWORD}" ]; then
    echo "Setting snowflake_password..."
    pulumi env set scoobyjava-org/default/sophia-ai-production values.sophia.snowflake_password "${SNOWFLAKE_PASSWORD}"
else
    echo "⚠️  SNOWFLAKE_PASSWORD not set in environment"
fi

# snowflake_database
if [ -n "${SNOWFLAKE_DATABASE}" ]; then
    echo "Setting snowflake_database..."
    pulumi env set scoobyjava-org/default/sophia-ai-production values.sophia.snowflake_database "${SNOWFLAKE_DATABASE}"
else
    echo "⚠️  SNOWFLAKE_DATABASE not set in environment"
fi

# snowflake_warehouse
if [ -n "${SNOWFLAKE_WAREHOUSE}" ]; then
    echo "Setting snowflake_warehouse..."
    pulumi env set scoobyjava-org/default/sophia-ai-production values.sophia.snowflake_warehouse "${SNOWFLAKE_WAREHOUSE}"
else
    echo "⚠️  SNOWFLAKE_WAREHOUSE not set in environment"
fi

# snowflake_role
if [ -n "${SNOWFLAKE_ROLE}" ]; then
    echo "Setting snowflake_role..."
    pulumi env set scoobyjava-org/default/sophia-ai-production values.sophia.snowflake_role "${SNOWFLAKE_ROLE}"
else
    echo "⚠️  SNOWFLAKE_ROLE not set in environment"
fi

# pinecone_api_key
if [ -n "${PINECONE_API_KEY}" ]; then
    echo "Setting pinecone_api_key..."
    pulumi env set scoobyjava-org/default/sophia-ai-production values.sophia.pinecone_api_key "${PINECONE_API_KEY}"
else
    echo "⚠️  PINECONE_API_KEY not set in environment"
fi

# pinecone_environment
if [ -n "${PINECONE_ENVIRONMENT}" ]; then
    echo "Setting pinecone_environment..."
    pulumi env set scoobyjava-org/default/sophia-ai-production values.sophia.pinecone_environment "${PINECONE_ENVIRONMENT}"
else
    echo "⚠️  PINECONE_ENVIRONMENT not set in environment"
fi

# weaviate_api_key
if [ -n "${WEAVIATE_API_KEY}" ]; then
    echo "Setting weaviate_api_key..."
    pulumi env set scoobyjava-org/default/sophia-ai-production values.sophia.weaviate_api_key "${WEAVIATE_API_KEY}"
else
    echo "⚠️  WEAVIATE_API_KEY not set in environment"
fi

# weaviate_url
if [ -n "${WEAVIATE_URL}" ]; then
    echo "Setting weaviate_url..."
    pulumi env set scoobyjava-org/default/sophia-ai-production values.sophia.weaviate_url "${WEAVIATE_URL}"
else
    echo "⚠️  WEAVIATE_URL not set in environment"
fi

# lambda_labs_api_key
if [ -n "${LAMBDA_API_KEY}" ]; then
    echo "Setting lambda_labs_api_key..."
    pulumi env set scoobyjava-org/default/sophia-ai-production values.sophia.lambda_labs_api_key "${LAMBDA_API_KEY}"
else
    echo "⚠️  LAMBDA_API_KEY not set in environment"
fi

# lambda_labs_api_key
if [ -n "${LAMBDA_API_KEY}" ]; then
    echo "Setting lambda_labs_api_key..."
    pulumi env set scoobyjava-org/default/sophia-ai-production values.sophia.lambda_labs_api_key "${LAMBDA_API_KEY}"
else
    echo "⚠️  LAMBDA_API_KEY not set in environment"
fi

# vercel_api_token
if [ -n "${VERCEL_API_TOKEN}" ]; then
    echo "Setting vercel_api_token..."
    pulumi env set scoobyjava-org/default/sophia-ai-production values.sophia.vercel_api_token "${VERCEL_API_TOKEN}"
else
    echo "⚠️  VERCEL_API_TOKEN not set in environment"
fi

# vercel_project_id
if [ -n "${VERCEL_PROJECT_ID}" ]; then
    echo "Setting vercel_project_id..."
    pulumi env set scoobyjava-org/default/sophia-ai-production values.sophia.vercel_project_id "${VERCEL_PROJECT_ID}"
else
    echo "⚠️  VERCEL_PROJECT_ID not set in environment"
fi

# pulumi_access_token
if [ -n "${PULUMI_ACCESS_TOKEN}" ]; then
    echo "Setting pulumi_access_token..."
    pulumi env set scoobyjava-org/default/sophia-ai-production values.sophia.pulumi_access_token "${PULUMI_ACCESS_TOKEN}"
else
    echo "⚠️  PULUMI_ACCESS_TOKEN not set in environment"
fi

# github_token
if [ -n "${GITHUB_TOKEN}" ]; then
    echo "Setting github_token..."
    pulumi env set scoobyjava-org/default/sophia-ai-production values.sophia.github_token "${GITHUB_TOKEN}"
else
    echo "⚠️  GITHUB_TOKEN not set in environment"
fi

# github_token
if [ -n "${GITHUB_TOKEN}" ]; then
    echo "Setting github_token..."
    pulumi env set scoobyjava-org/default/sophia-ai-production values.sophia.github_token "${GITHUB_TOKEN}"
else
    echo "⚠️  GITHUB_TOKEN not set in environment"
fi

# codacy_api_token
if [ -n "${CODACY_API_TOKEN}" ]; then
    echo "Setting codacy_api_token..."
    pulumi env set scoobyjava-org/default/sophia-ai-production values.sophia.codacy_api_token "${CODACY_API_TOKEN}"
else
    echo "⚠️  CODACY_API_TOKEN not set in environment"
fi

# notion_api_token
if [ -n "${NOTION_API_KEY}" ]; then
    echo "Setting notion_api_token..."
    pulumi env set scoobyjava-org/default/sophia-ai-production values.sophia.notion_api_token "${NOTION_API_KEY}"
else
    echo "⚠️  NOTION_API_KEY not set in environment"
fi

# notion_api_token
if [ -n "${NOTION_API_KEY}" ]; then
    echo "Setting notion_api_token..."
    pulumi env set scoobyjava-org/default/sophia-ai-production values.sophia.notion_api_token "${NOTION_API_KEY}"
else
    echo "⚠️  NOTION_API_KEY not set in environment"
fi

# asana_access_token
if [ -n "${ASANA_API_TOKEN}" ]; then
    echo "Setting asana_access_token..."
    pulumi env set scoobyjava-org/default/sophia-ai-production values.sophia.asana_access_token "${ASANA_API_TOKEN}"
else
    echo "⚠️  ASANA_API_TOKEN not set in environment"
fi

# asana_access_token
if [ -n "${ASANA_API_TOKEN}" ]; then
    echo "Setting asana_access_token..."
    pulumi env set scoobyjava-org/default/sophia-ai-production values.sophia.asana_access_token "${ASANA_API_TOKEN}"
else
    echo "⚠️  ASANA_API_TOKEN not set in environment"
fi

# portkey_api_key
if [ -n "${PORTKEY_API_KEY}" ]; then
    echo "Setting portkey_api_key..."
    pulumi env set scoobyjava-org/default/sophia-ai-production values.sophia.portkey_api_key "${PORTKEY_API_KEY}"
else
    echo "⚠️  PORTKEY_API_KEY not set in environment"
fi

# openrouter_api_key
if [ -n "${OPENROUTER_API_KEY}" ]; then
    echo "Setting openrouter_api_key..."
    pulumi env set scoobyjava-org/default/sophia-ai-production values.sophia.openrouter_api_key "${OPENROUTER_API_KEY}"
else
    echo "⚠️  OPENROUTER_API_KEY not set in environment"
fi

# estuary_api_key
if [ -n "${ESTUARY_API_KEY}" ]; then
    echo "Setting estuary_api_key..."
    pulumi env set scoobyjava-org/default/sophia-ai-production values.sophia.estuary_api_key "${ESTUARY_API_KEY}"
else
    echo "⚠️  ESTUARY_API_KEY not set in environment"
fi

# figma_pat
if [ -n "${FIGMA_PAT}" ]; then
    echo "Setting figma_pat..."
    pulumi env set scoobyjava-org/default/sophia-ai-production values.sophia.figma_pat "${FIGMA_PAT}"
else
    echo "⚠️  FIGMA_PAT not set in environment"
fi

# figma_project_id
if [ -n "${FIGMA_PROJECT_ID}" ]; then
    echo "Setting figma_project_id..."
    pulumi env set scoobyjava-org/default/sophia-ai-production values.sophia.figma_project_id "${FIGMA_PROJECT_ID}"
else
    echo "⚠️  FIGMA_PROJECT_ID not set in environment"
fi

# apify_api_token
if [ -n "${APIFY_API_TOKEN}" ]; then
    echo "Setting apify_api_token..."
    pulumi env set scoobyjava-org/default/sophia-ai-production values.sophia.apify_api_token "${APIFY_API_TOKEN}"
else
    echo "⚠️  APIFY_API_TOKEN not set in environment"
fi

# bright_data_api_key
if [ -n "${BRIGHT_DATA_API_KEY}" ]; then
    echo "Setting bright_data_api_key..."
    pulumi env set scoobyjava-org/default/sophia-ai-production values.sophia.bright_data_api_key "${BRIGHT_DATA_API_KEY}"
else
    echo "⚠️  BRIGHT_DATA_API_KEY not set in environment"
fi

# huggingface_api_key
if [ -n "${HUGGINGFACE_API_KEY}" ]; then
    echo "Setting huggingface_api_key..."
    pulumi env set scoobyjava-org/default/sophia-ai-production values.sophia.huggingface_api_key "${HUGGINGFACE_API_KEY}"
else
    echo "⚠️  HUGGINGFACE_API_KEY not set in environment"
fi

# postgres_password
if [ -n "${POSTGRES_PASSWORD}" ]; then
    echo "Setting postgres_password..."
    pulumi env set scoobyjava-org/default/sophia-ai-production values.sophia.postgres_password "${POSTGRES_PASSWORD}"
else
    echo "⚠️  POSTGRES_PASSWORD not set in environment"
fi

# redis_password
if [ -n "${REDIS_PASSWORD}" ]; then
    echo "Setting redis_password..."
    pulumi env set scoobyjava-org/default/sophia-ai-production values.sophia.redis_password "${REDIS_PASSWORD}"
else
    echo "⚠️  REDIS_PASSWORD not set in environment"
fi

# apollo_api_key
if [ -n "${APOLLO_API_KEY}" ]; then
    echo "Setting apollo_api_key..."
    pulumi env set scoobyjava-org/default/sophia-ai-production values.sophia.apollo_api_key "${APOLLO_API_KEY}"
else
    echo "⚠️  APOLLO_API_KEY not set in environment"
fi

# nmhc_api_key
if [ -n "${NMHC_API_KEY}" ]; then
    echo "Setting nmhc_api_key..."
    pulumi env set scoobyjava-org/default/sophia-ai-production values.sophia.nmhc_api_key "${NMHC_API_KEY}"
else
    echo "⚠️  NMHC_API_KEY not set in environment"
fi

# sentry_dsn
if [ -n "${SENTRY_DSN}" ]; then
    echo "Setting sentry_dsn..."
    pulumi env set scoobyjava-org/default/sophia-ai-production values.sophia.sentry_dsn "${SENTRY_DSN}"
else
    echo "⚠️  SENTRY_DSN not set in environment"
fi

# graphiti_api_key
if [ -n "${GRAPHITI_API_KEY}" ]; then
    echo "Setting graphiti_api_key..."
    pulumi env set scoobyjava-org/default/sophia-ai-production values.sophia.graphiti_api_key "${GRAPHITI_API_KEY}"
else
    echo "⚠️  GRAPHITI_API_KEY not set in environment"
fi

# langfuse_api_key
if [ -n "${LANGFUSE_API_KEY}" ]; then
    echo "Setting langfuse_api_key..."
    pulumi env set scoobyjava-org/default/sophia-ai-production values.sophia.langfuse_api_key "${LANGFUSE_API_KEY}"
else
    echo "⚠️  LANGFUSE_API_KEY not set in environment"
fi

# langsmith_api_key
if [ -n "${LANGSMITH_API_KEY}" ]; then
    echo "Setting langsmith_api_key..."
    pulumi env set scoobyjava-org/default/sophia-ai-production values.sophia.langsmith_api_key "${LANGSMITH_API_KEY}"
else
    echo "⚠️  LANGSMITH_API_KEY not set in environment"
fi

# deepseek_api_key
if [ -n "${DEEPSEEK_API_KEY}" ]; then
    echo "Setting deepseek_api_key..."
    pulumi env set scoobyjava-org/default/sophia-ai-production values.sophia.deepseek_api_key "${DEEPSEEK_API_KEY}"
else
    echo "⚠️  DEEPSEEK_API_KEY not set in environment"
fi

# gemini_api_key
if [ -n "${GEMINI_API_KEY}" ]; then
    echo "Setting gemini_api_key..."
    pulumi env set scoobyjava-org/default/sophia-ai-production values.sophia.gemini_api_key "${GEMINI_API_KEY}"
else
    echo "⚠️  GEMINI_API_KEY not set in environment"
fi

# claude_api_key
if [ -n "${CLAUDE_API_KEY}" ]; then
    echo "Setting claude_api_key..."
    pulumi env set scoobyjava-org/default/sophia-ai-production values.sophia.claude_api_key "${CLAUDE_API_KEY}"
else
    echo "⚠️  CLAUDE_API_KEY not set in environment"
fi

# retool_api_key
if [ -n "${RETOOL_API_KEY}" ]; then
    echo "Setting retool_api_key..."
    pulumi env set scoobyjava-org/default/sophia-ai-production values.sophia.retool_api_key "${RETOOL_API_KEY}"
else
    echo "⚠️  RETOOL_API_KEY not set in environment"
fi

# n8n_api_key
if [ -n "${N8N_API_KEY}" ]; then
    echo "Setting n8n_api_key..."
    pulumi env set scoobyjava-org/default/sophia-ai-production values.sophia.n8n_api_key "${N8N_API_KEY}"
else
    echo "⚠️  N8N_API_KEY not set in environment"
fi

# snowflake_cortex_api_key
if [ -n "${SNOWFLAKE_CORTEX_API_KEY}" ]; then
    echo "Setting snowflake_cortex_api_key..."
    pulumi env set scoobyjava-org/default/sophia-ai-production values.sophia.snowflake_cortex_api_key "${SNOWFLAKE_CORTEX_API_KEY}"
else
    echo "⚠️  SNOWFLAKE_CORTEX_API_KEY not set in environment"
fi
