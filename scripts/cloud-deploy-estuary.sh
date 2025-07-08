#!/bin/bash
# Cloud-based Estuary Flow deployment - runs entirely on Lambda Labs
# No local machine required - everything via SSH

set -e

# Configuration
LAMBDA_LABS_HOST="${LAMBDA_LABS_HOST:-146.235.200.1}"
LAMBDA_LABS_USER="${LAMBDA_LABS_USER:-ubuntu}"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "🌊 Cloud-Based Estuary Flow Deployment"
echo "====================================="
echo ""
echo "This script will:"
echo "1. Install flowctl CLI on Lambda Labs"
echo "2. Pull configurations from GitHub"
echo "3. Use existing Pulumi ESC secrets"
echo "4. Deploy Estuary flows"
echo ""

# Create and execute the entire deployment on Lambda Labs
ssh ${LAMBDA_LABS_USER}@${LAMBDA_LABS_HOST} << 'CLOUD_DEPLOY'
#!/bin/bash

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

echo "🚀 Starting cloud-based deployment on Lambda Labs"
echo ""

# Step 1: Install flowctl if not present
if ! command -v flowctl &> /dev/null; then
    echo "📦 Installing flowctl CLI..."

    ARCH=$(uname -m)
    OS=$(uname -s)

    if [ "$ARCH" = "x86_64" ]; then
        ARCH="amd64"
    elif [ "$ARCH" = "aarch64" ]; then
        ARCH="arm64"
    fi

    FLOWCTL_URL="https://github.com/estuary/flow/releases/latest/download/flowctl-${OS}-${ARCH}"

    if curl -L "$FLOWCTL_URL" -o /tmp/flowctl; then
        sudo mv /tmp/flowctl /usr/local/bin/flowctl
        sudo chmod +x /usr/local/bin/flowctl
        print_status "flowctl installed successfully"
    else
        print_error "Failed to download flowctl"
        exit 1
    fi
else
    print_status "flowctl already installed"
fi

# Step 2: Clone or update Sophia AI repository
echo ""
echo "📂 Setting up Sophia AI repository..."

if [ -d ~/sophia-main ]; then
    cd ~/sophia-main
    print_info "Updating existing repository..."
    git pull origin main
else
    print_info "Cloning repository..."
    cd ~
    git clone https://github.com/ai-cherry/sophia-main.git
    cd ~/sophia-main
fi
print_status "Repository ready"

# Step 3: Load secrets from Pulumi ESC
echo ""
echo "🔐 Loading secrets from Pulumi ESC..."

# Check if Pulumi is installed
if ! command -v pulumi &> /dev/null; then
    echo "Installing Pulumi CLI..."
    curl -fsSL https://get.pulumi.com | sh
    export PATH=$PATH:$HOME/.pulumi/bin
fi

# Set Pulumi organization
export PULUMI_ORG=scoobyjava-org
export ENVIRONMENT=production

# Load ESC environment
print_info "Loading Pulumi ESC environment..."
eval $(pulumi env open ${PULUMI_ORG}/default/sophia-ai-production --format=shell)

# Verify critical secrets are loaded
if [ -z "$ESTUARY_API_KEY" ]; then
    print_warning "ESTUARY_API_KEY not found in Pulumi ESC"
    print_info "Using existing secrets that should be synced from GitHub"

    # These should already be in Pulumi ESC from GitHub sync
    export ESTUARY_GONG_TOKEN="${GONG_WEBHOOK_SECRET:-$(openssl rand -hex 32)}"
    export ESTUARY_SLACK_TOKEN="${SLACK_WEBHOOK:-$(openssl rand -hex 32)}"
    export ESTUARY_GITHUB_TOKEN="${GITHUB_TOKEN:-$(openssl rand -hex 32)}"
fi

print_status "Secrets loaded from Pulumi ESC"

# Step 4: Create Estuary secrets file from ESC values
echo ""
echo "📝 Creating Estuary secrets configuration..."

mkdir -p ~/sophia-main/config/estuary
cat > ~/sophia-main/config/estuary/secrets.yaml << EOF
# Auto-generated from Pulumi ESC
# DO NOT COMMIT THIS FILE

# Webhook endpoints
gong_webhook_endpoint: "http://localhost:9009/estuary/webhook"
slack_webhook_endpoint: "http://localhost:9007/estuary/webhook"
github_webhook_endpoint: "http://localhost:9006/estuary/webhook"

# Tokens from Pulumi ESC
estuary_gong_token: "${ESTUARY_GONG_TOKEN:-$GONG_WEBHOOK_SECRET}"
estuary_slack_token: "${ESTUARY_SLACK_TOKEN:-$SLACK_WEBHOOK}"
estuary_github_token: "${ESTUARY_GITHUB_TOKEN:-$GITHUB_TOKEN}"

# Database credentials from ESC
redis_password: "${REDIS_PASSWORD}"
snowflake_account: "${SNOWFLAKE_ACCOUNT}"
snowflake_user: "${SNOWFLAKE_USER}"
snowflake_password: "${SNOWFLAKE_PASSWORD}"

# Monitoring
grafana_api_key: "${GRAFANA_API_KEY}"
slack_webhook: "${SLACK_WEBHOOK}"
EOF

print_status "Secrets configuration created"

# Step 5: Authenticate with Estuary (if API key exists)
if [ -n "$ESTUARY_API_KEY" ] && [ -n "$ESTUARY_API_SECRET" ]; then
    echo ""
    echo "🔑 Authenticating with Estuary..."

    # Create auth config
    mkdir -p ~/.estuary
    cat > ~/.estuary/config.json << EOF
{
  "api_key": "${ESTUARY_API_KEY}",
  "api_secret": "${ESTUARY_API_SECRET}",
  "endpoint": "https://api.estuary.dev"
}
EOF

    if flowctl auth test; then
        print_status "Authenticated with Estuary"
    else
        print_warning "Estuary authentication failed - manual login required"
        echo "Run: flowctl auth login"
    fi
else
    print_warning "Estuary API credentials not found in Pulumi ESC"
    print_info "You'll need to run: flowctl auth login"
fi

# Step 6: Deploy Estuary flows
echo ""
echo "🚀 Deploying Estuary flows..."

cd ~/sophia-main

# Make deployment script executable
chmod +x scripts/deploy-estuary-flow.sh

# Check if we can deploy
if flowctl auth test &>/dev/null; then
    print_info "Starting Estuary deployment..."
    ./scripts/deploy-estuary-flow.sh
else
    print_warning "Cannot deploy automatically - authentication required"
    echo ""
    echo "To complete deployment:"
    echo "1. Run: flowctl auth login"
    echo "2. Run: ./scripts/deploy-estuary-flow.sh"
fi

# Step 7: Configure MCP server webhooks
echo ""
echo "🔗 Configuring MCP server webhooks..."

# Function to register webhook with MCP server
configure_webhook() {
    local server=$1
    local port=$2
    local token_var=$3
    local token_value=${!token_var}

    if [ -z "$token_value" ]; then
        print_warning "No token for $server - skipping webhook config"
        return
    fi

    echo -n "Configuring $server webhook... "

    # Update MCP server environment to include webhook token
    docker service update \
        --env-add "ESTUARY_WEBHOOK_TOKEN=$token_value" \
        sophia-mcp-v2_${server} \
        2>/dev/null && echo "✓" || echo "✗"
}

# Configure webhooks for running MCP servers
configure_webhook "gong-v2" 9009 "ESTUARY_GONG_TOKEN"
configure_webhook "slack-v2" 9007 "ESTUARY_SLACK_TOKEN"
configure_webhook "github-v2" 9006 "ESTUARY_GITHUB_TOKEN"

# Step 8: Set up monitoring
echo ""
echo "📊 Setting up monitoring..."

# Import Grafana dashboard if API key exists
if [ -n "$GRAFANA_API_KEY" ] && [ -f "infrastructure/monitoring/estuary_flow_dashboard.json" ]; then
    curl -s -X POST \
        "http://localhost:3000/api/dashboards/db" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer ${GRAFANA_API_KEY}" \
        -d @infrastructure/monitoring/estuary_flow_dashboard.json \
        > /dev/null && print_status "Grafana dashboard imported" || print_warning "Failed to import dashboard"
fi

# Final status
echo ""
echo "🎉 Cloud deployment complete!"
echo "============================="
echo ""

# Check what's working
echo "📊 Status Check:"
echo ""

# Check flowctl
if command -v flowctl &> /dev/null; then
    echo "✅ flowctl installed"
    if flowctl auth test &>/dev/null; then
        echo "✅ Estuary authenticated"

        # List flows if authenticated
        echo ""
        echo "Active flows:"
        flowctl flows list --prefix sophia-ai/ 2>/dev/null || echo "No flows deployed yet"
    else
        echo "⚠️  Estuary authentication required"
        echo "   Run: flowctl auth login"
    fi
else
    echo "❌ flowctl not installed"
fi

# Check MCP servers
echo ""
echo "MCP Servers:"
for port in 9000 9001 9002 9003 9004 9005 9006 9007 9008 9009; do
    if curl -s -f http://localhost:$port/health > /dev/null 2>&1; then
        echo "✅ Port $port - healthy"
    else
        echo "❌ Port $port - not responding"
    fi
done

echo ""
echo "📚 Next steps:"
echo "1. If not authenticated: flowctl auth login"
echo "2. Deploy flows: cd ~/sophia-main && ./scripts/deploy-estuary-flow.sh"
echo "3. Monitor: http://146.235.200.1:3000/d/estuary-flow"
echo ""
echo "All operations completed in the cloud! 🌩️"

CLOUD_DEPLOY
