#!/bin/bash

echo "🔍 Verifying Sentry secrets in Pulumi ESC..."
echo "================================================"

# Set Pulumi organization
export PULUMI_ORG=scoobyjava-org

# Check if Pulumi is logged in
if ! pulumi whoami &>/dev/null; then
    echo "❌ Not logged in to Pulumi. Please run: pulumi login"
    exit 1
fi

echo "✅ Logged in to Pulumi as: $(pulumi whoami)"
echo ""

# Check Sentry secrets in Pulumi ESC
echo "📋 Checking Sentry secrets in Pulumi ESC:"
echo "-----------------------------------------"

# List all Sentry-related secrets (without showing values)
echo "🔐 Sentry configuration in sophia-ai-production environment:"
pulumi env get scoobyjava-org/default/sophia-ai-production --show-secrets=false | grep -i sentry || echo "❌ No Sentry secrets found!"

echo ""
echo "📊 Detailed check for each secret:"
echo "---------------------------------"

# Check individual secrets
secrets=(
    "SENTRY_API_TOKEN"
    "SENTRY_CLIENT_SECRET"
    "SENTRY_DSN"
    "SENTRY_ORGANIZATION_SLUG"
    "SENTRY_PROJECT_SLUG"
)

for secret in "${secrets[@]}"; do
    if pulumi env get scoobyjava-org/default/sophia-ai-production "$secret" &>/dev/null; then
        echo "✅ $secret - Found in Pulumi ESC"
    else
        echo "❌ $secret - NOT found in Pulumi ESC"
    fi
done

echo ""
echo "🔄 To manually sync from GitHub Actions secrets, run:"
echo "-----------------------------------------------------"
echo "1. Go to GitHub Actions"
echo "2. Run 'Sync Sentry Secrets to Pulumi ESC' workflow"
echo ""
echo "Or run this command to check with secrets visible:"
echo "pulumi env get scoobyjava-org/default/sophia-ai-production --show-secrets"
