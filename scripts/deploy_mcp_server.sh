#!/bin/bash
set -e

echo "🚀 Deploying to MCP Orchestrator Server (104.171.202.117)"

# Install K3s if not present
if ! command -v k3s &> /dev/null; then
    curl -sfL https://get.k3s.io | sh -
fi

# Create MCP namespace
kubectl create namespace mcp-servers --dry-run=client -o yaml | kubectl apply -f -

# Deploy MCP servers
kubectl apply -f k8s/mcp-servers/

# Setup webhook handlers
kubectl apply -f k8s/webhooks/

echo "✅ MCP orchestrator deployment complete!"
echo "🔗 Webhooks: https://webhooks.sophia-intel.ai"
echo "🤖 MCP: https://mcp.sophia-intel.ai"