#!/bin/bash
# Create Docker Secrets from Pulumi ESC using proper esc run pattern
# Implements the GitHub → Pulumi ESC → Docker Swarm secret pipeline correctly

set -euo pipefail

ESC_ENV="default/sophia-ai-production"
MASTER_IP="192.222.51.151"
SSH_KEY="$HOME/.ssh/lynn_sophia_h200_key"

echo "🔐 Creating Docker Secrets from Pulumi ESC Environment: $ESC_ENV"
echo "Target Docker Swarm Manager: $MASTER_IP"
echo ""

echo "🚀 Using ESC run pattern for automatic secret injection..."

# Use esc run to execute secret creation with automatic environment variable injection
esc run $ESC_ENV -- bash -c "
echo '📝 Creating Docker secrets on Swarm manager...'

# Function to create Docker secret safely
create_secret() {
    local secret_name=\$1
    local secret_value=\$2

    if [ -n \"\$secret_value\" ]; then
        echo \"Creating Docker secret: \$secret_name\"
        echo \"\$secret_value\" | ssh -i $SSH_KEY ubuntu@$MASTER_IP \"sudo docker secret rm \$secret_name 2>/dev/null || true && sudo docker secret create \$secret_name -\"
        if [ \$? -eq 0 ]; then
            echo \"✅ Successfully created: \$secret_name\"
        else
            echo \"❌ Failed to create: \$secret_name\"
        fi
    else
        echo \"⚠️ Skipping \$secret_name - value not found\"
    fi
}

# Create Docker secrets using environment variables from ESC (corrected variable names)
create_secret 'pulumi_access_token' \"\$pulumi_access_token\"
create_secret 'postgres_password' \"\$snowflake_password\"
create_secret 'snowflake_account' \"\$snowflake_account\"
create_secret 'snowflake_user' \"\$snowflake_user\"
create_secret 'snowflake_password' \"\$snowflake_password\"
create_secret 'snowflake_database' \"\$snowflake_database\"
create_secret 'snowflake_warehouse' \"\$snowflake_warehouse\"
create_secret 'snowflake_role' \"\$snowflake_role\"
create_secret 'mem0_api_key' \"\$mem0_api_key\"
create_secret 'openai_api_key' \"\$openai_api_key\"
create_secret 'anthropic_api_key' \"\$anthropic_api_key\"
create_secret 'vercel_api_token' \"\$vercel_api_token\"
create_secret 'redis_password' \"\$redis_password\"
create_secret 'redis_url' \"\$redis_url\"
create_secret 'github_token' \"\$github_token\"
create_secret 'lambda_api_key' \"\$lambda_api_key\"

echo ''
echo '🔍 Verifying Docker secrets on Swarm manager...'
ssh -i $SSH_KEY ubuntu@$MASTER_IP 'sudo docker secret ls'

echo ''
echo '✅ Docker secrets created successfully from Pulumi ESC!'
"
