#!/bin/bash

# Sophia AI - Pulumi ESC Setup Script
# This script sets up Pulumi ESC environments for secure secret management

set -e

echo "🚀 Setting up Pulumi ESC for Sophia AI..."

# Check if Pulumi CLI is available
if ! command -v pulumi &> /dev/null; then
    echo "❌ Pulumi CLI not found. Please install Pulumi first."
    exit 1
fi

# Set up PATH for Pulumi
export PATH=$PATH:/home/ubuntu/.pulumi/bin

# Check if user is logged in to Pulumi
if ! pulumi whoami &> /dev/null; then
    echo "⚠️  Not logged in to Pulumi. Please run 'pulumi login' first."
    echo "   You can use your Pulumi access token: your-pulumi-access-token"
    exit 1
fi

# Set organization and project
PULUMI_ORG="scoobyjava-org"
PULUMI_PROJECT="sophia-ai"

echo "📋 Organization: $PULUMI_ORG"
echo "📋 Project: $PULUMI_PROJECT"

# Create ESC environments
echo "🔧 Creating Pulumi ESC environments..."

# Create base environment
echo "📝 Creating base environment..."
pulumi env init $PULUMI_ORG/sophia-ai-base || echo "Base environment already exists"

# Create production environment  
echo "📝 Creating production environment..."
pulumi env init $PULUMI_ORG/sophia-ai-production || echo "Production environment already exists"

# Create development environment
echo "📝 Creating development environment..."
pulumi env init $PULUMI_ORG/sophia-ai-development || echo "Development environment already exists"

# Update environments with configuration
echo "🔄 Updating environment configurations..."

# Update base environment
echo "📤 Updating base environment..."
pulumi env set $PULUMI_ORG/sophia-ai-base --file infrastructure/esc/sophia-ai-base.yaml

# Update production environment
echo "📤 Updating production environment..."
pulumi env set $PULUMI_ORG/sophia-ai-production --file infrastructure/esc/sophia-ai-production.yaml

echo "✅ Pulumi ESC environments created successfully!"
echo ""
echo "🔑 Next steps:"
echo "1. Set your secrets in the Pulumi ESC environments"
echo "2. Configure GitHub OIDC for secure CI/CD"
echo "3. Update your application to use ESC environment variables"
echo ""
echo "🌐 Access your environments at:"
echo "   https://app.pulumi.com/$PULUMI_ORG/environments"

