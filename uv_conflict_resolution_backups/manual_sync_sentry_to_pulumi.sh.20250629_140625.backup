#!/bin/bash

echo "🔄 Manual Sync: GitHub Secrets → Pulumi ESC"
echo "==========================================="
echo ""

# Check if we have the required environment variables
if [ -z "$SENTRY_API_TOKEN" ] || [ -z "$SENTRY_CLIENT_SECRET" ]; then
    echo "❌ Missing required environment variables!"
    echo ""
    echo "Please export these from your GitHub secrets:"
    echo "  export SENTRY_API_TOKEN='your-token-here'"
    echo "  export SENTRY_CLIENT_SECRET='your-secret-here'"
    echo ""
    echo "You can also set optional ones:"
    echo "  export SENTRY_DSN='your-dsn-here'"
    echo "  export SENTRY_ORGANIZATION_SLUG='pay-ready'"
    echo "  export SENTRY_PROJECT_SLUG='pay-ready'"
    exit 1
fi

# Set Pulumi organization
export PULUMI_ORG=scoobyjava-org

# Check if logged in to Pulumi
if ! pulumi whoami &>/dev/null; then
    echo "📝 Logging in to Pulumi..."
    pulumi login
fi

echo "✅ Logged in as: $(pulumi whoami)"
echo ""

echo "🚀 Syncing Sentry secrets to Pulumi ESC..."
echo "-----------------------------------------"

# Sync SENTRY_API_TOKEN
echo -n "Syncing SENTRY_API_TOKEN... "
if pulumi env set scoobyjava-org/default/sophia-ai-production SENTRY_API_TOKEN "$SENTRY_API_TOKEN" --secret; then
    echo "✅"
else
    echo "❌ Failed"
fi

# Sync SENTRY_CLIENT_SECRET
echo -n "Syncing SENTRY_CLIENT_SECRET... "
if pulumi env set scoobyjava-org/default/sophia-ai-production SENTRY_CLIENT_SECRET "$SENTRY_CLIENT_SECRET" --secret; then
    echo "✅"
else
    echo "❌ Failed"
fi

# Sync optional secrets if they exist
if [ ! -z "$SENTRY_DSN" ]; then
    echo -n "Syncing SENTRY_DSN... "
    if pulumi env set scoobyjava-org/default/sophia-ai-production SENTRY_DSN "$SENTRY_DSN" --secret; then
        echo "✅"
    else
        echo "❌ Failed"
    fi
fi

if [ ! -z "$SENTRY_ORGANIZATION_SLUG" ]; then
    echo -n "Syncing SENTRY_ORGANIZATION_SLUG... "
    if pulumi env set scoobyjava-org/default/sophia-ai-production SENTRY_ORGANIZATION_SLUG "$SENTRY_ORGANIZATION_SLUG"; then
        echo "✅"
    else
        echo "❌ Failed"
    fi
fi

if [ ! -z "$SENTRY_PROJECT_SLUG" ]; then
    echo -n "Syncing SENTRY_PROJECT_SLUG... "
    if pulumi env set scoobyjava-org/default/sophia-ai-production SENTRY_PROJECT_SLUG "$SENTRY_PROJECT_SLUG"; then
        echo "✅"
    else
        echo "❌ Failed"
    fi
fi

echo ""
echo "📋 Verifying synced secrets:"
echo "----------------------------"

# Verify what's now in Pulumi ESC
pulumi env get scoobyjava-org/default/sophia-ai-production --show-secrets=false | grep -i sentry

echo ""
echo "✅ Manual sync complete!"
echo ""
echo "To view the actual secret values, run:"
echo "  pulumi env get scoobyjava-org/default/sophia-ai-production --show-secrets"
