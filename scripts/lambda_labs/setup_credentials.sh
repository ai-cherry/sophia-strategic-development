#!/bin/bash
# Lambda Labs Credential Setup Script
# Retrieves credentials from GitHub Organization Secrets via Pulumi ESC

set -euo pipefail

echo "=== Lambda Labs Credential Setup ==="

# Check GitHub CLI authentication
if ! gh auth status &>/dev/null; then
    echo "❌ Error: GitHub CLI not authenticated. Run 'gh auth login' first."
    exit 1
fi

# Check organization access
if ! gh api user/orgs | grep -q "ai-cherry"; then
    echo "❌ Error: No access to ai-cherry organization"
    exit 1
fi

# Create .env file for local development
cat > .env.lambda-labs << EOF
# Lambda Labs Configuration - Generated $(date)
# DO NOT COMMIT THIS FILE
LAMBDA_API_KEY=$(gh secret get LAMBDA_API_KEY --org ai-cherry)
LAMBDA_SSH_KEY=$(gh secret get LAMBDA_SSH_KEY --org ai-cherry)
LAMBDA_PRIVATE_SSH_KEY=$(gh secret get LAMBDA_PRIVATE_SSH_KEY --org ai-cherry)
EOF

# Setup SSH key
mkdir -p ~/.ssh
gh secret get LAMBDA_PRIVATE_SSH_KEY --org ai-cherry > ~/.ssh/sophia2025
chmod 600 ~/.ssh/sophia2025

# Add to SSH agent
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/sophia2025

# Validate Lambda Labs API access
LAMBDA_API_KEY=$(gh secret get LAMBDA_API_KEY --org ai-cherry)
if curl -s -H "Authorization: Bearer $LAMBDA_API_KEY" https://cloud.lambdalabs.com/api/v1/instances | jq -e '.data' >/dev/null; then
    echo "✅ Lambda Labs API access validated"
else
    echo "❌ Lambda Labs API access failed"
    exit 1
fi

# Test SSH connectivity to instances
instances=(
    "192.222.58.232:sophia-ai-core"
    "104.171.202.117:sophia-mcp-orchestrator"
    "104.171.202.134:sophia-data-pipeline"
    "155.248.194.183:sophia-development"
)

echo ""
echo "Testing SSH connectivity:"
for instance in "${instances[@]}"; do
    ip=$(echo $instance | cut -d: -f1)
    name=$(echo $instance | cut -d: -f2)
    if ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no ubuntu@$ip "echo 'Connected'" &>/dev/null; then
        echo "✅ $name ($ip)"
    else
        echo "❌ $name ($ip)"
    fi
done

echo ""
echo "✅ Credential setup complete"
echo "📝 Environment file created: .env.lambda-labs"
echo "🔑 SSH key configured: ~/.ssh/sophia2025"
