#!/bin/bash
# Deploy Estuary Flow configuration for Sophia AI V2

set -e

# Configuration
ESTUARY_ENDPOINT="${ESTUARY_ENDPOINT:-https://api.estuary.dev}"
ESTUARY_ORG="${ESTUARY_ORG:-sophia-ai}"
CONFIG_DIR="config/estuary"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Function to print colored output
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

echo "🌊 Estuary Flow Deployment for Sophia AI V2"
echo "=========================================="
echo ""

# Check prerequisites
echo "📋 Checking prerequisites..."

# Check flowctl CLI
if ! command -v flowctl &> /dev/null; then
    print_error "flowctl CLI is not installed"
    print_info "Install with: curl -L https://github.com/estuary/flow/releases/latest/download/flowctl-$(uname -s)-$(uname -m) -o /usr/local/bin/flowctl"
    exit 1
fi
print_status "flowctl CLI installed"

# Check authentication
if ! flowctl auth test &> /dev/null; then
    print_warning "Not authenticated to Estuary Flow"
    echo "Authenticating..."
    flowctl auth login
fi
print_status "Authenticated to Estuary Flow"

# Validate configuration files
echo ""
echo "🔍 Validating configuration files..."

CONFIGS=(
    "gong_v2_collection.yaml"
    "slack_v2_collection.yaml"
    "github_v2_collection.yaml"
    "derivations/enrich_gong_calls.yaml"
    "derivations/enrich_slack_messages.yaml"
    "materializations/redis_cache.yaml"
    "materializations/snowflake_analytics.yaml"
    "materializations/postgresql_staging.yaml"
)

VALIDATION_FAILED=false

for config in "${CONFIGS[@]}"; do
    if [ -f "$CONFIG_DIR/$config" ]; then
        echo -n "Validating $config... "
        if flowctl catalog test --source "$CONFIG_DIR/$config" 2>/dev/null; then
            echo "✓"
        else
            echo "✗"
            print_error "Validation failed for $config"
            VALIDATION_FAILED=true
        fi
    else
        print_warning "Config not found: $CONFIG_DIR/$config"
    fi
done

if [ "$VALIDATION_FAILED" = true ]; then
    print_error "Some configurations failed validation. Please fix before deploying."
    exit 1
fi

print_status "All configurations validated successfully"

# Deploy collections
echo ""
echo "📦 Deploying Collections..."

deploy_collection() {
    local collection=$1
    local file=$2
    
    echo -n "Deploying $collection... "
    
    if flowctl catalog publish \
        --source "$CONFIG_DIR/$file" \
        --collection "$ESTUARY_ORG/$collection" \
        2>/dev/null; then
        echo "✓"
        return 0
    else
        echo "✗"
        return 1
    fi
}

# Deploy primary collections
deploy_collection "gong-calls" "gong_v2_collection.yaml" || print_error "Failed to deploy Gong collection"
deploy_collection "slack-messages" "slack_v2_collection.yaml" || print_error "Failed to deploy Slack collection"
deploy_collection "github-events" "github_v2_collection.yaml" || print_error "Failed to deploy GitHub collection"

# Deploy derivations
echo ""
echo "🔄 Deploying Derivations..."

deploy_collection "gong-calls-enriched" "derivations/enrich_gong_calls.yaml" || print_error "Failed to deploy Gong derivation"
deploy_collection "slack-messages-enriched" "derivations/enrich_slack_messages.yaml" || print_error "Failed to deploy Slack derivation"

# Deploy materializations
echo ""
echo "💾 Deploying Materializations..."

deploy_materialization() {
    local name=$1
    local file=$2
    
    echo -n "Deploying $name materialization... "
    
    if flowctl catalog publish \
        --source "$CONFIG_DIR/$file" \
        --materialization "$ESTUARY_ORG/$name" \
        2>/dev/null; then
        echo "✓"
        return 0
    else
        echo "✗"
        return 1
    fi
}

deploy_materialization "redis-hot-cache" "materializations/redis_cache.yaml" || print_error "Failed to deploy Redis materialization"
deploy_materialization "snowflake-analytics" "materializations/snowflake_analytics.yaml" || print_error "Failed to deploy Snowflake materialization"
deploy_materialization "postgresql-staging" "materializations/postgresql_staging.yaml" || print_error "Failed to deploy PostgreSQL materialization"

# Start flows
echo ""
echo "▶️  Starting Flows..."

start_flow() {
    local flow=$1
    local type=$2
    
    echo -n "Starting $flow... "
    
    if flowctl flows activate \
        --$type "$ESTUARY_ORG/$flow" \
        2>/dev/null; then
        echo "✓"
        return 0
    else
        echo "✗"
        return 1
    fi
}

# Start collections
start_flow "gong-calls" "collection" || print_warning "Failed to start Gong collection"
start_flow "slack-messages" "collection" || print_warning "Failed to start Slack collection"
start_flow "github-events" "collection" || print_warning "Failed to start GitHub collection"

# Start derivations
start_flow "gong-calls-enriched" "derivation" || print_warning "Failed to start Gong derivation"
start_flow "slack-messages-enriched" "derivation" || print_warning "Failed to start Slack derivation"

# Start materializations
start_flow "redis-hot-cache" "materialization" || print_warning "Failed to start Redis materialization"
start_flow "snowflake-analytics" "materialization" || print_warning "Failed to start Snowflake materialization"

# Check flow status
echo ""
echo "📊 Flow Status:"
flowctl flows list --prefix "$ESTUARY_ORG/" | grep -E "(gong|slack|github|redis|snowflake)"

# Configure webhooks on MCP servers
echo ""
echo "🔗 Configuring MCP Server Webhooks..."

configure_webhook() {
    local server=$1
    local port=$2
    local webhook_url="https://api.estuary.dev/webhooks/$ESTUARY_ORG/$server"
    
    echo -n "Configuring $server webhook... "
    
    # Call MCP server to register Estuary webhook
    if curl -s -X POST \
        "http://146.235.200.1:$port/admin/configure-webhook" \
        -H "Content-Type: application/json" \
        -d "{\"webhook_url\": \"$webhook_url\", \"events\": [\"all\"]}" \
        > /dev/null; then
        echo "✓"
    else
        echo "✗"
        print_warning "Failed to configure $server webhook"
    fi
}

configure_webhook "gong-v2" 9009
configure_webhook "slack-v2" 9007
configure_webhook "github-v2" 9006

# Create monitoring dashboard
echo ""
echo "📈 Setting up Monitoring..."

# Create Grafana dashboard
if [ -f "infrastructure/monitoring/estuary_flow_dashboard.json" ]; then
    echo "Importing Grafana dashboard..."
    curl -s -X POST \
        "http://146.235.200.1:3000/api/dashboards/db" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer ${GRAFANA_API_KEY}" \
        -d @infrastructure/monitoring/estuary_flow_dashboard.json \
        > /dev/null && print_status "Grafana dashboard imported"
fi

# Final status check
echo ""
echo "🎉 Estuary Flow Deployment Complete!"
echo "===================================="
echo ""
echo "📊 Active Flows:"
flowctl flows list --prefix "$ESTUARY_ORG/" --status active | tail -n +2

echo ""
echo "🔍 Next Steps:"
echo "  1. Monitor flows: flowctl flows logs --follow"
echo "  2. Check metrics: http://146.235.200.1:3000/d/estuary-flow"
echo "  3. Test webhooks: curl -X POST http://146.235.200.1:9009/test/webhook"
echo ""
echo "📚 Documentation: docs/05-integrations/ESTUARY_FLOW_GUIDE.md"
echo ""
echo "⚠️  Note: Ensure all required secrets are configured in Pulumi ESC" 