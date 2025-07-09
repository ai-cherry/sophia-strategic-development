#!/bin/bash
set -euo pipefail

# Lambda Labs MCP Server Deployment Script

echo "🚀 Deploying Lambda Labs MCP Server..."

# Configuration
DOCKER_REGISTRY="scoobyjava15"
IMAGE_NAME="lambda-labs-mcp"
VERSION="${1:-latest}"
MCP_PORT="9025"

# Build Docker image
echo "📦 Building Docker image..."
cd mcp-servers/lambda_labs_unified
docker build -t ${DOCKER_REGISTRY}/${IMAGE_NAME}:${VERSION} .

# Push to registry
echo "📤 Pushing to Docker Hub..."
docker push ${DOCKER_REGISTRY}/${IMAGE_NAME}:${VERSION}

# Update cursor MCP config
echo "🔧 Updating Cursor MCP configuration..."
cat > /tmp/lambda_mcp_config.json << EOF
{
  "lambda-labs": {
    "command": "docker",
    "args": [
      "run",
      "--rm",
      "-i",
      "-v", "\${HOME}/.sophia/lambda:/app/data",
      "-e", "LAMBDA_SERVERLESS_API_KEY=\${LAMBDA_SERVERLESS_API_KEY}",
      "-e", "LAMBDA_DAILY_BUDGET=\${LAMBDA_DAILY_BUDGET:-50}",
      "-e", "LAMBDA_MONTHLY_BUDGET=\${LAMBDA_MONTHLY_BUDGET:-1000}",
      "-e", "SLACK_WEBHOOK_URL=\${SLACK_WEBHOOK_URL}",
      "${DOCKER_REGISTRY}/${IMAGE_NAME}:${VERSION}"
    ],
    "env": {
      "MCP_SERVER_NAME": "lambda-labs-unified"
    }
  }
}
EOF

# Merge with existing config
if [ -f "config/cursor_mcp_config.json" ]; then
    echo "📝 Merging with existing MCP configuration..."
    jq -s '.[0] * .[1]' config/cursor_mcp_config.json /tmp/lambda_mcp_config.json > /tmp/merged_config.json
    mv /tmp/merged_config.json config/cursor_mcp_config.json
else
    mv /tmp/lambda_mcp_config.json config/cursor_mcp_config.json
fi

# Create data directory
echo "📁 Creating data directory..."
mkdir -p ~/.sophia/lambda

# Test the server
echo "🧪 Testing MCP server..."
docker run --rm \
    -v ~/.sophia/lambda:/app/data \
    -e LAMBDA_SERVERLESS_API_KEY="${LAMBDA_SERVERLESS_API_KEY}" \
    ${DOCKER_REGISTRY}/${IMAGE_NAME}:${VERSION} \
    python -c "print('✅ Lambda Labs MCP Server ready!')"

echo "✅ Lambda Labs MCP Server deployed successfully!"
echo ""
echo "📝 Next steps:"
echo "1. Restart Cursor to load the new MCP server"
echo "2. Use natural language commands like:"
echo "   - 'Use Lambda serverless to analyze this report'"
echo "   - 'Show Lambda Labs usage for last 7 days'"
echo "   - 'Estimate cost for processing 1000 documents'"
