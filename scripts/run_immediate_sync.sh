#!/bin/bash
# Immediate secret sync from GitHub to Pulumi ESC
# This script triggers the enhanced sync workflow

echo "🔐 Triggering Enhanced Secret Sync"
echo "=================================="

# Check if we're logged into GitHub CLI
if ! gh auth status &>/dev/null; then
    echo "❌ Not logged into GitHub CLI"
    echo "Run: gh auth login"
    exit 1
fi

# Trigger the enhanced sync workflow
echo "🚀 Triggering sync workflow..."
gh workflow run sync_secrets_enhanced.yml

# Wait a moment for the workflow to start
sleep 5

# Show the status
echo ""
echo "📊 Workflow Status:"
gh run list --workflow=sync_secrets_enhanced.yml --limit 3

echo ""
echo "🔍 To monitor progress:"
echo "gh run watch"
echo ""
echo "Or view in browser:"
echo "gh run list --workflow=sync_secrets_enhanced.yml --limit 1 --json databaseId | jq -r '.[0].databaseId' | xargs gh run view --web"

# Also provide a manual sync option
echo ""
echo "🛠️  For manual sync (if workflow fails):"
echo "export PULUMI_ACCESS_TOKEN='${PULUMI_ACCESS_TOKEN}'"
echo "python scripts/ci/sync_secrets_to_esc_enhanced.py"
