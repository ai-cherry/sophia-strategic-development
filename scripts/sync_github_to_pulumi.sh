#!/bin/bash

# Sophia AI - GitHub Organization Secrets → Pulumi ESC Sync
# This script pulls secrets from GitHub org and pushes to Pulumi ESC
# NO MORE MANUAL SECRET MANAGEMENT!

set -e

echo "🔄 Syncing GitHub Organization Secrets to Pulumi ESC..."

# Set Pulumi configuration
export PULUMI_ORG="scoobyjava-org"
# PULUMI_ACCESS_TOKEN should be set from GitHub organization secrets
if [ -z "$PULUMI_ACCESS_TOKEN" ]; then
    echo "❌ PULUMI_ACCESS_TOKEN not set! This should come from GitHub organization secrets."
    exit 1
fi

# GitHub organization secrets to sync
declare -A GITHUB_SECRETS=(
    ["OPENAI_API_KEY"]="sophia.ai.openai.api_key"
    ["ANTHROPIC_API_KEY"]="sophia.ai.anthropic.api_key"
    ["GONG_ACCESS_KEY"]="sophia.business.gong.access_key"
    ["GONG_CLIENT_SECRET"]="sophia.business.gong.client_secret"
    ["GONG_URL"]="sophia.business.gong.url"
    ["HUBSPOT_API_TOKEN"]="sophia.business.hubspot.api_token"
    ["SLACK_BOT_TOKEN"]="sophia.business.slack.bot_token"
    ["SNOWFLAKE_ACCOUNT"]="sophia.data.snowflake.account"
    ["SNOWFLAKE_USER"]="sophia.data.snowflake.user"
    ["SNOWFLAKE_PASSWORD"]="sophia.data.snowflake.password"
    ["PINECONE_API_KEY"]="sophia.data.pinecone.api_key"
    ["LAMBDA_LABS_API_KEY"]="sophia.cloud.lambda_labs.api_key"
    ["VERCEL_ACCESS_TOKEN"]="sophia.cloud.vercel.access_token"
)

# Environment to update
ENV_NAME="scoobyjava-org/default/sophia-ai-production"

echo "📋 Syncing secrets to: $ENV_NAME"

# Sync each secret
for github_secret in "${!GITHUB_SECRETS[@]}"; do
    pulumi_path="${GITHUB_SECRETS[$github_secret]}"

    if [ ! -z "${!github_secret}" ]; then
        echo "🔑 Syncing: $github_secret → $pulumi_path"
        pulumi env set "$ENV_NAME" "values.$pulumi_path" "${!github_secret}" --secret
    else
        echo "⚠️  Missing: $github_secret (set in GitHub org secrets)"
    fi
done

echo "✅ GitHub → Pulumi ESC sync complete!"
echo "🎯 Backend will now automatically use these secrets"
