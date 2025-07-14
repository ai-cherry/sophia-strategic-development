#!/bin/bash
# Setup Pulumi ESC secrets for Sophia AI
# Run this script to configure secrets securely

echo "🔐 Setting up Pulumi ESC for Sophia AI"
echo "======================================="

# Check if Pulumi is installed
if ! command -v pulumi &> /dev/null; then
    echo "❌ Pulumi CLI not found. Please install it first:"
    echo "   curl -fsSL https://get.pulumi.com | sh"
    exit 1
fi

# Login to Pulumi
echo "📝 Logging into Pulumi..."
pulumi login

# Create environment if it doesn't exist
echo "🌍 Creating Pulumi environment..."
pulumi env init sophia-ai/production || echo "Environment already exists"

# Set secrets
echo "🔑 Setting secrets..."

# Namecheap
pulumi env set sophia-ai/production namecheap_api_key --secret
pulumi env set sophia-ai/production namecheap_api_user "scoobyjava"

# Vercel
pulumi env set sophia-ai/production vercel_token --secret

# Domain configuration
pulumi env set sophia-ai/production domain "sophia-intel.ai"
pulumi env set sophia-ai/production api_url "https://api.sophia-intel.ai"
pulumi env set sophia-ai/production app_url "https://sophia-intel.ai"

# Lambda Labs
pulumi env set sophia-ai/production lambda_labs_host "192.222.58.232"

# Database URLs (will be updated after deployment)
pulumi env set sophia-ai/production database_url --secret
pulumi env set sophia-ai/production redis_url "redis://localhost:6379"
pulumi env set sophia-ai/production weaviate_url "http://localhost:8080"

# AI Services (optional)
echo "🤖 Setting AI service keys (press Enter to skip if not available)..."
pulumi env set sophia-ai/production openai_api_key --secret
pulumi env set sophia-ai/production anthropic_api_key --secret

# GitHub token for MCP
pulumi env set sophia-ai/production github_token --secret

# Admin settings
pulumi env set sophia-ai/production admin_email "musillynn@gmail.com"
pulumi env set sophia-ai/production grafana_admin_password --secret

echo "✅ Pulumi ESC configuration complete!"
echo ""
echo "To view your configuration:"
echo "  pulumi env open sophia-ai/production"
echo ""
echo "To use in your deployment:"
echo "  pulumi env run sophia-ai/production -- ./deploy.sh" 