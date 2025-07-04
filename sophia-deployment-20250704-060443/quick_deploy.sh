#!/bin/bash
# Quick deployment script for Lambda Labs

set -euo pipefail

echo "🚀 Starting Sophia AI deployment..."

# Check if we're on a manager node
if ! docker node ls &>/dev/null; then
    echo "❌ ERROR: Not on a Docker Swarm manager node"
    echo "Initialize swarm with: docker swarm init"
    exit 1
fi

# Check for required environment variables
required_vars=(
    "POSTGRES_PASSWORD"
    "PULUMI_ACCESS_TOKEN"
)

for var in "${required_vars[@]}"; do
    if [ -z "${!var:-}" ]; then
        echo "❌ ERROR: $var is not set"
        echo "Set it with: export $var='your-value'"
        exit 1
    fi
done

# Run the main deployment
./deploy_sophia_stack.sh

echo "✅ Deployment initiated! Monitor with:"
echo "   docker stack ps sophia-ai"
echo "   ./monitor_swarm_performance.sh"
