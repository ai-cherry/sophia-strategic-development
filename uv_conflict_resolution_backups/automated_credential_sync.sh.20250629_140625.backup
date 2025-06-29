#!/bin/bash
# Automated Credential Sync with Pulumi ESC
# This script automatically syncs credentials from GitHub Secrets to Pulumi ESC

set -e

echo "🔐 Starting Automated Credential Sync..."

# Initialize Pulumi ESC
pulumi config set --path sophia-ai:snowflake_account "${SNOWFLAKE_ACCOUNT}"
pulumi config set --path sophia-ai:snowflake_user "${SNOWFLAKE_USER}" 
pulumi config set --path sophia-ai:sophia_ai_token "${SOPHIA_AI_TOKEN}" --secret

pulumi config set --path sophia-ai:estuary_client_id "${ESTUARY_CLIENT_ID}"
pulumi config set --path sophia-ai:estuary_client_secret "${ESTUARY_CLIENT_SECRET}" --secret
pulumi config set --path sophia-ai:estuary_access_token "${ESTUARY_ACCESS_TOKEN}" --secret

pulumi config set --path sophia-ai:gong_access_key "${GONG_ACCESS_KEY}" --secret
pulumi config set --path sophia-ai:gong_client_secret "${GONG_CLIENT_SECRET}" --secret

pulumi config set --path sophia-ai:slack_bot_token "${SLACK_BOT_TOKEN}" --secret
pulumi config set --path sophia-ai:slack_app_token "${SLACK_APP_TOKEN}" --secret

pulumi config set --path sophia-ai:hubspot_access_token "${HUBSPOT_ACCESS_TOKEN}" --secret

pulumi config set --path sophia-ai:vercel_token "${VERCEL_TOKEN}" --secret
pulumi config set --path sophia-ai:lambda_labs_api_key "${LAMBDA_LABS_API_KEY}" --secret

pulumi config set --path sophia-ai:portkey_api_key "${PORTKEY_API_KEY}" --secret
pulumi config set --path sophia-ai:openrouter_api_key "${OPENROUTER_API_KEY}" --secret

pulumi config set --path sophia-ai:linear_api_key "${LINEAR_API_KEY}" --secret
pulumi config set --path sophia-ai:asana_access_token "${ASANA_ACCESS_TOKEN}" --secret

pulumi config set --path sophia-ai:usergems_api_key "${USERGEMS_API_KEY}" --secret
pulumi config set --path sophia-ai:apollo_api_key "${APOLLO_API_KEY}" --secret

pulumi config set --path sophia-ai:webhook_base_url "${SOPHIA_WEBHOOK_BASE_URL}"

echo "✅ Automated Credential Sync Complete"
