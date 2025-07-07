#!/bin/bash

# GitHub Secrets Setup Script for Sentry Integration
# This script helps set up the required GitHub organization secrets for Sentry integration

set -e

echo "🔧 Setting up GitHub Secrets for Sentry Integration"
echo "=================================================="

# Check if GitHub CLI is available
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) is not installed. Please install it first:"
    echo "   https://cli.github.com/"
    exit 1
fi

# Check if user is authenticated
if ! gh auth status &> /dev/null; then
    echo "❌ Not authenticated with GitHub CLI. Please run 'gh auth login' first."
    exit 1
fi

# Organization and repository details
ORG="ai-cherry"
REPO="sophia-main"

echo "📋 Setting up secrets for organization: $ORG"
echo ""

# Sentry configuration values
SENTRY_AUTH_TOKEN="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"
SENTRY_API_TOKEN="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"
SENTRY_CLIENT_SECRET="42c8dc1fbabb7668e5e2abf5a1bcd1ac94c2df91bb4450411f906571352c3f65"
SENTRY_ORGANIZATION_SLUG="pay-ready"
SENTRY_PROJECT_SLUG="sophia-ai"

# Note: SENTRY_DSN will need to be set after creating the Sentry project
echo "⚠️  Note: SENTRY_DSN will need to be set manually after creating the Sentry project"
echo ""

# Function to set organization secret
set_org_secret() {
    local secret_name=$1
    local secret_value=$2

    echo "Setting $secret_name..."
    if echo "$secret_value" | gh secret set "$secret_name" --org "$ORG" --visibility all; then
        echo "✅ $secret_name set successfully"
    else
        echo "❌ Failed to set $secret_name"
        return 1
    fi
}

# Set all the secrets
echo "🔐 Setting organization secrets..."
echo ""

set_org_secret "SENTRY_AUTH_TOKEN" "$SENTRY_AUTH_TOKEN"
set_org_secret "SENTRY_API_TOKEN" "$SENTRY_API_TOKEN"
set_org_secret "SENTRY_CLIENT_SECRET" "$SENTRY_CLIENT_SECRET"
set_org_secret "SENTRY_ORGANIZATION_SLUG" "$SENTRY_ORGANIZATION_SLUG"
set_org_secret "SENTRY_PROJECT_SLUG" "$SENTRY_PROJECT_SLUG"

echo ""
echo "✅ All Sentry secrets have been set in the GitHub organization!"
echo ""
echo "📝 Next Steps:"
echo "1. Create a Sentry project named 'sophia-ai' in the 'pay-ready' organization"
echo "2. Get the DSN from the project settings"
echo "3. Set the SENTRY_DSN secret: gh secret set SENTRY_DSN --org $ORG --visibility all"
echo "4. Run the sync workflow to push secrets to Pulumi ESC"
echo ""
echo "🚀 To trigger the sync workflow:"
echo "   gh workflow run sync-sentry-secrets.yml --repo $ORG/$REPO"
echo ""
echo "🔍 To verify secrets were set:"
echo "   gh secret list --org $ORG"
