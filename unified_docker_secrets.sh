#!/bin/bash
# Create Docker Secrets from Pulumi ESC using direct value extraction
# This approach directly extracts secrets and creates Docker secrets

set -euo pipefail

ESC_ENV="default/sophia-ai-production"
MASTER_IP="192.222.51.151"
SSH_KEY="$HOME/.ssh/lynn_sophia_h200_key"

echo "🔐 Creating Docker Secrets from Pulumi ESC Environment: $ESC_ENV"
echo "Target Docker Swarm Manager: $MASTER_IP"
echo ""

echo "📁 Extracting secrets from ESC environment..."

# Function to extract secret value from ESC
get_secret() {
    local key_path="$1"
    esc env open $ESC_ENV | jq -r "$key_path" 2>/dev/null || echo ""
}

# Function to create Docker secret safely
create_secret() {
    local secret_name="$1"
    local secret_value="$2"

    if [ -n "$secret_value" ] && [ "$secret_value" != "null" ] && [ "$secret_value" != "" ]; then
        echo "Creating Docker secret: $secret_name"
        echo "$secret_value" | ssh -i "$SSH_KEY" ubuntu@$MASTER_IP "sudo docker secret rm $secret_name 2>/dev/null || true && sudo docker secret create $secret_name -"
        if [ $? -eq 0 ]; then
            echo "✅ Successfully created: $secret_name"
        else
            echo "❌ Failed to create: $secret_name"
        fi
    else
        echo "⚠️ Skipping $secret_name - value not found or placeholder"
    fi
}

echo "🚀 Creating Docker secrets..."

# Extract and create core secrets (use real values, not placeholders)
create_secret "pulumi_access_token" "$(get_secret '.pulumi_access_token')"
create_secret "openai_api_key" "$(get_secret '.openai_api_key')"
create_secret "anthropic_api_key" "$(get_secret '.anthropic_api_key')"

# Snowflake secrets
create_secret "snowflake_account" "$(get_secret '.snowflake_account')"
create_secret "snowflake_user" "$(get_secret '.snowflake_user')"
create_secret "snowflake_password" "$(get_secret '.snowflake_password')"
create_secret "snowflake_database" "$(get_secret '.snowflake_database')"
create_secret "snowflake_warehouse" "$(get_secret '.snowflake_warehouse')"
create_secret "snowflake_role" "$(get_secret '.snowflake_role')"

# Database secrets
create_secret "postgres_password" "$(get_secret '.snowflake_password')"  # Use Snowflake password for PostgreSQL
create_secret "redis_password" "$(get_secret '.redis_password')"
create_secret "redis_url" "$(get_secret '.redis_url')"

# Other API secrets
create_secret "mem0_api_key" "$(get_secret '.mem0_api_key')"
create_secret "github_token" "$(get_secret '.github_token')"
create_secret "lambda_api_key" "$(get_secret '.lambda_api_key')"
create_secret "VERCEL_ACCESS_TOKEN" "$(get_secret '.vercel_api_token')"

# Gong secrets (real values)
create_secret "gong_access_key" "$(get_secret '.gong_access_key')"
create_secret "gong_client_secret" "$(get_secret '.gong_client_secret')"

# Linear and other business tools
create_secret "linear_api_key" "$(get_secret '.linear_api_key')"
create_secret "hubspot_access_token" "$(get_secret '.hubspot_access_token')"

# Slack tokens (real values)
create_secret "slack_bot_token" "$(get_secret '.slack_bot_token')"
create_secret "slack_app_token" "$(get_secret '.slack_app_token')"

echo ""
echo "🔍 Verifying Docker secrets on Swarm manager..."
ssh -i "$SSH_KEY" ubuntu@$MASTER_IP "sudo docker secret ls"

echo ""
echo "✅ Docker secrets created successfully from Pulumi ESC!"
echo "🚀 Ready to deploy the stack with real production secrets."
