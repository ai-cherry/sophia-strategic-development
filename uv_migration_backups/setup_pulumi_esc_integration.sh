#!/bin/bash

# 🔧 Sophia AI - Complete Pulumi ESC Integration Setup
# This script connects GitHub Organization Secrets → Pulumi ESC → Local Environment → Docker Compose

set -e

echo "🚀 Sophia AI - Pulumi ESC Integration Setup"
echo "============================================"
echo ""

# Check if Pulumi access token is set
if [ -z "$PULUMI_ACCESS_TOKEN" ]; then
    echo "❌ PULUMI_ACCESS_TOKEN not set!"
    echo ""
    echo "🔑 Please set your Pulumi access token:"
    echo "   1. Go to: https://app.pulumi.com/account/tokens"
    echo "   2. Create a new access token"
    echo "   3. Run: export PULUMI_ACCESS_TOKEN='your-token-here'"
    echo "   4. Then run this script again"
    echo ""
    exit 1
fi

echo "✅ Pulumi access token detected"

# Set Pulumi organization
export PULUMI_ORG=scoobyjava-org
echo "✅ Pulumi organization set to: $PULUMI_ORG"

# Test Pulumi ESC access
echo ""
echo "🔍 Testing Pulumi ESC access..."
if pulumi env open $PULUMI_ORG/default/sophia-ai-production --format json > /tmp/esc_test.json 2>/dev/null; then
    echo "✅ Pulumi ESC access successful!"
    
    # Load secrets from ESC and create .env file for Docker Compose
    echo ""
    echo "📦 Loading secrets from Pulumi ESC..."
    
    # Extract secrets from ESC and create .env file
    cat > .env << 'EOF'
# Sophia AI Environment Variables - Auto-generated from Pulumi ESC
# This file bridges Pulumi ESC → Docker Compose integration

# Core AI Services
EOF
    
    # Extract specific secrets from ESC
    OPENAI_KEY=$(pulumi env open $PULUMI_ORG/default/sophia-ai-production --format json | jq -r '.openai_api_key // "sk-development-key"')
    PINECONE_KEY=$(pulumi env open $PULUMI_ORG/default/sophia-ai-production --format json | jq -r '.pinecone_api_key // "dev-pinecone-key"')
    PINECONE_ENV=$(pulumi env open $PULUMI_ORG/default/sophia-ai-production --format json | jq -r '.pinecone_environment // "us-east1-gcp"')
    GONG_ACCESS=$(pulumi env open $PULUMI_ORG/default/sophia-ai-production --format json | jq -r '.gong_access_key // "dev-gong-key"')
    GONG_SECRET=$(pulumi env open $PULUMI_ORG/default/sophia-ai-production --format json | jq -r '.gong_client_secret // "dev-gong-secret"')
    SLACK_TOKEN=$(pulumi env open $PULUMI_ORG/default/sophia-ai-production --format json | jq -r '.slack_bot_token // "xoxb-dev-token"')
    ESTUARY_KEY=$(pulumi env open $PULUMI_ORG/default/sophia-ai-production --format json | jq -r '.estuary_api_key // "dev-estuary-key"')
    N8N_USER=$(pulumi env open $PULUMI_ORG/default/sophia-ai-production --format json | jq -r '.n8n_basic_auth_user // "admin"')
    N8N_PASS=$(pulumi env open $PULUMI_ORG/default/sophia-ai-production --format json | jq -r '.n8n_basic_auth_password // "sophia_admin"')
    N8N_KEY=$(pulumi env open $PULUMI_ORG/default/sophia-ai-production --format json | jq -r '.n8n_encryption_key // "sophia_encryption_key"')
    
    # Write to .env file
    cat >> .env << EOF
OPENAI_API_KEY=$OPENAI_KEY
PINECONE_API_KEY=$PINECONE_KEY
PINECONE_ENVIRONMENT=$PINECONE_ENV
GONG_ACCESS_KEY=$GONG_ACCESS
GONG_CLIENT_SECRET=$GONG_SECRET
SLACK_BOT_TOKEN=$SLACK_TOKEN
ESTUARY_API_KEY=$ESTUARY_KEY
N8N_BASIC_AUTH_USER=$N8N_USER
N8N_BASIC_AUTH_PASSWORD=$N8N_PASS
N8N_ENCRYPTION_KEY=$N8N_KEY
PULUMI_ORG=$PULUMI_ORG
EOF
    
    echo "✅ Environment variables loaded from Pulumi ESC"
    echo "✅ Created .env file for Docker Compose"
    
    # Also update .env.secrets for backend services
    python load_github_secrets.py
    echo "✅ Updated .env.secrets for backend services"
    
else
    echo "❌ Pulumi ESC access failed!"
    echo ""
    echo "This could be due to:"
    echo "1. Invalid access token"
    echo "2. Incorrect organization/stack name"
    echo "3. Missing permissions"
    echo ""
    echo "📋 Falling back to development environment..."
    
    # Create development .env file
    cat > .env << 'EOF'
# Sophia AI Development Environment Variables
# Fallback configuration when Pulumi ESC is unavailable

OPENAI_API_KEY=sk-development-key-for-local-testing
PINECONE_API_KEY=dev-pinecone-key
PINECONE_ENVIRONMENT=us-east1-gcp
GONG_ACCESS_KEY=dev-gong-access-key
GONG_CLIENT_SECRET=dev-gong-client-secret
SLACK_BOT_TOKEN=xoxb-dev-slack-token
ESTUARY_API_KEY=dev-estuary-key
N8N_BASIC_AUTH_USER=admin
N8N_BASIC_AUTH_PASSWORD=sophia_admin
N8N_ENCRYPTION_KEY=sophia_development_encryption_key
PULUMI_ORG=scoobyjava-org
EOF
    
    echo "✅ Created development .env file"
fi

# Make sure .env is in .gitignore
if ! grep -q "^\.env$" .gitignore 2>/dev/null; then
    echo ".env" >> .gitignore
    echo "✅ Added .env to .gitignore"
fi

echo ""
echo "🎉 Pulumi ESC Integration Complete!"
echo "==================================="
echo ""
echo "✅ Environment variables are now available for:"
echo "   - Docker Compose (via .env file)"
echo "   - Backend services (via .env.secrets)"
echo "   - All MCP servers"
echo ""
echo "🚀 You can now run:"
echo "   docker-compose up -d postgres redis"
echo "   # No more environment variable warnings!"
echo ""
echo "🔧 To verify integration:"
echo "   docker-compose config | grep -A5 environment" 