#!/bin/bash

# Sophia AI - Pulumi ESC Configuration Script
# This script configures Pulumi ESC environments with proper YAML structure

set -e

echo "🚀 Configuring Pulumi ESC for Sophia AI..."

# Set up environment variables
export PATH=$PATH:/home/ubuntu/.pulumi/bin
export PULUMI_ACCESS_TOKEN="your-pulumi-access-token"
export PULUMI_ORG="scoobyjava-org"

# Configure base environment
echo "📝 Configuring base environment..."
pulumi env set $PULUMI_ORG/sophia-ai-base values.organization "scoobyjava-org" --string
pulumi env set $PULUMI_ORG/sophia-ai-base values.project "sophia-ai" --string
pulumi env set $PULUMI_ORG/sophia-ai-base values.infrastructure.region "us-east-1" --string
pulumi env set $PULUMI_ORG/sophia-ai-base values.tags.Project "Sophia AI" --string
pulumi env set $PULUMI_ORG/sophia-ai-base values.tags.ManagedBy "Pulumi" --string

# Configure production environment with imports
echo "📝 Configuring production environment..."
pulumi env set $PULUMI_ORG/sophia-ai-production import "[\"scoobyjava-org/sophia-ai-base\"]"

# Set up environment variables for the application
echo "🔧 Setting up environment variables..."
export PULUMI_ORG="scoobyjava-org"

echo "✅ Pulumi ESC environments configured successfully!"
echo ""
echo "🔑 Environment variables set:"
echo "   PULUMI_ORG=$PULUMI_ORG"
echo "   PULUMI_ACCESS_TOKEN=***"
echo ""
echo "🌐 Access your environments at:"
echo "   https://app.pulumi.com/$PULUMI_ORG/environments"

