#!/bin/bash
# Sophia AI - Secure Credential Setup Script
# Configures environment variables for production deployment

echo "🔐 Sophia AI Secure Credential Setup"
echo "===================================="
echo ""

# Function to securely set environment variable
set_credential() {
    local var_name="$1"
    local description="$2"
    local current_value="${!var_name}"
    
    if [ -z "$current_value" ]; then
        echo "⚠️  Missing: $var_name"
        echo "   Description: $description"
        echo "   Please set: export $var_name=\"your_value_here\""
        echo ""
        return 1
    else
        echo "✅ Configured: $var_name"
        return 0
    fi
}

# Track missing credentials
missing_count=0

echo "🎯 CORE INFRASTRUCTURE:"
echo "----------------------"
set_credential "PULUMI_ACCESS_TOKEN" "Pulumi Cloud access token" || ((missing_count++))
set_credential "SECRET_KEY" "Application secret key (32+ chars)" || ((missing_count++))
set_credential "JWT_SECRET" "JWT signing secret (32+ chars)" || ((missing_count++))
echo ""

echo "🗄️  DATABASE & STORAGE:"
echo "----------------------"
set_credential "POSTGRES_HOST" "PostgreSQL host" || ((missing_count++))
set_credential "POSTGRES_USER" "PostgreSQL username" || ((missing_count++))
set_credential "POSTGRES_PASSWORD" "PostgreSQL password" || ((missing_count++))
set_credential "POSTGRES_DB" "PostgreSQL database name" || ((missing_count++))
echo ""

echo "🤖 AI SERVICES:"
echo "---------------"
set_credential "OPENAI_API_KEY" "OpenAI API key" || ((missing_count++))
set_credential "ANTHROPIC_API_KEY" "Anthropic Claude API key" || ((missing_count++))
echo ""

echo "📊 BUSINESS INTELLIGENCE:"
echo "-------------------------"
set_credential "GONG_ACCESS_KEY" "Gong.io API access key" || ((missing_count++))
set_credential "GONG_CLIENT_SECRET" "Gong.io client secret" || ((missing_count++))
set_credential "SLACK_BOT_TOKEN" "Slack bot token" || ((missing_count++))
set_credential "HUBSPOT_API_TOKEN" "HubSpot API token" || ((missing_count++))
echo ""

echo "❄️  SNOWFLAKE DATA WAREHOUSE:"
echo "----------------------------"
set_credential "SNOWFLAKE_ACCOUNT" "Snowflake account identifier" || ((missing_count++))
set_credential "SNOWFLAKE_USER" "Snowflake username" || ((missing_count++))
set_credential "SNOWFLAKE_PASSWORD" "Snowflake password" || ((missing_count++))
echo ""

echo "🔍 VECTOR DATABASES:"
echo "-------------------"
set_credential "PINECONE_API_KEY" "Pinecone API key" || ((missing_count++))
set_credential "WEAVIATE_API_KEY" "Weaviate API key" || ((missing_count++))
echo ""

echo "☁️  CLOUD SERVICES:"
echo "------------------"
set_credential "LAMBDA_LABS_API_KEY" "Lambda Labs API key" || ((missing_count++))
set_credential "VERCEL_ACCESS_TOKEN" "Vercel access token" || ((missing_count++))
set_credential "RETOOL_API_TOKEN" "Retool API token" || ((missing_count++))
echo ""

# Summary
echo "📋 CREDENTIAL SUMMARY:"
echo "======================"
total_credentials=18
configured_count=$((total_credentials - missing_count))

echo "✅ Configured: $configured_count/$total_credentials"
echo "❌ Missing: $missing_count/$total_credentials"
echo "📊 Completion: $(( (configured_count * 100) / total_credentials ))%"
echo ""

if [ $missing_count -eq 0 ]; then
    echo "🎉 ALL CREDENTIALS CONFIGURED!"
    echo "Ready for production deployment."
    echo ""
    echo "Next steps:"
    echo "1. Run: python3 backend/core/secure_credential_manager.py"
    echo "2. Run: ./deploy_production.sh"
    exit 0
else
    echo "⚠️  $missing_count credentials need configuration."
    echo ""
    echo "To configure credentials:"
    echo "1. Set environment variables as shown above"
    echo "2. Or add to GitHub organization secrets"
    echo "3. Re-run this script to validate"
    exit 1
fi

