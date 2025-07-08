#!/usr/bin/env bash
# Infrastructure Deployment Script
# Deploys Sophia AI infrastructure using Pulumi

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PULUMI_STACK="${PULUMI_STACK:-scoobyjava-org/sophia-prod-on-lambda}"
PULUMI_DIR="infrastructure/pulumi"
MAX_RETRIES=3
RETRY_DELAY=5

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_prerequisites() {
    log_info "Checking prerequisites..."

    # Check Pulumi CLI
    if ! command -v pulumi &> /dev/null; then
        log_error "Pulumi CLI not found. Installing..."
        curl -fsSL https://get.pulumi.com | sh
        export PATH="$HOME/.pulumi/bin:$PATH"
    fi

    # Check Node.js
    if ! command -v node &> /dev/null; then
        log_error "Node.js not found. Please install Node.js 18+"
        exit 1
    fi

    # Check environment variables
    if [ -z "${PULUMI_ACCESS_TOKEN:-}" ]; then
        log_error "PULUMI_ACCESS_TOKEN not set"
        exit 1
    fi

    log_info "Prerequisites check passed"
}

login_pulumi() {
    log_info "Logging into Pulumi..."

    # Login to Pulumi Cloud
    pulumi login

    # Select or create stack
    pulumi stack select "$PULUMI_STACK" 2>/dev/null || {
        log_warn "Stack not found, creating..."
        pulumi stack init "$PULUMI_STACK"
    }

    log_info "Pulumi stack: $(pulumi stack)"
}

install_dependencies() {
    log_info "Installing dependencies..."

    cd "$PULUMI_DIR"

    # Install npm dependencies
    if [ -f "package.json" ]; then
        npm ci
    fi

    # Install Python dependencies if needed
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
    fi

    cd - > /dev/null
}

preview_changes() {
    log_info "Previewing infrastructure changes..."

    cd "$PULUMI_DIR"
    pulumi preview --diff
    cd - > /dev/null

    # Ask for confirmation in interactive mode
    if [ -t 0 ]; then
        read -p "Do you want to apply these changes? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_warn "Deployment cancelled"
            exit 0
        fi
    fi
}

deploy_infrastructure() {
    log_info "Deploying infrastructure..."

    cd "$PULUMI_DIR"

    # Deploy with retries
    local attempt=1
    while [ $attempt -le $MAX_RETRIES ]; do
        if pulumi up --yes --suppress-outputs; then
            log_info "Infrastructure deployed successfully"
            break
        else
            log_warn "Deployment attempt $attempt failed"
            if [ $attempt -lt $MAX_RETRIES ]; then
                log_info "Retrying in $RETRY_DELAY seconds..."
                sleep $RETRY_DELAY
            else
                log_error "Deployment failed after $MAX_RETRIES attempts"
                exit 1
            fi
        fi
        ((attempt++))
    done

    cd - > /dev/null
}

export_outputs() {
    log_info "Exporting stack outputs..."

    cd "$PULUMI_DIR"

    # Export outputs to file
    pulumi stack output --json > stack-outputs.json

    # Export key outputs as environment variables
    export BACKEND_URL=$(pulumi stack output backendUrl 2>/dev/null || echo "")
    export MCP_GATEWAY_URL=$(pulumi stack output mcpGatewayUrl 2>/dev/null || echo "")
    export FRONTEND_URL=$(pulumi stack output frontendUrl 2>/dev/null || echo "")

    cd - > /dev/null

    log_info "Stack outputs exported"
}

smoke_test() {
    log_info "Running smoke tests..."

    # Test backend health
    if [ -n "$BACKEND_URL" ]; then
        log_info "Testing backend health endpoint..."
        if curl -sf "${BACKEND_URL}/health" | grep -q '"status":"healthy"'; then
            log_info "Backend health check passed"
        else
            log_error "Backend health check failed"
            exit 1
        fi
    fi

    # Test MCP gateway
    if [ -n "$MCP_GATEWAY_URL" ]; then
        log_info "Testing MCP gateway..."
        if curl -sf "${MCP_GATEWAY_URL}/mcp/tools" > /dev/null; then
            log_info "MCP gateway check passed"
        else
            log_warn "MCP gateway check failed (non-critical)"
        fi
    fi

    log_info "Smoke tests completed"
}

update_monitoring() {
    log_info "Updating monitoring dashboards..."

    # Update Grafana annotation
    if [ -n "${GRAFANA_URL:-}" ] && [ -n "${GRAFANA_API_KEY:-}" ]; then
        curl -X POST "${GRAFANA_URL}/api/annotations" \
            -H "Authorization: Bearer ${GRAFANA_API_KEY}" \
            -H "Content-Type: application/json" \
            -d '{
                "dashboardUID": "sophia-infra",
                "tags": ["deployment", "infrastructure"],
                "text": "Infrastructure deployment completed",
                "time": '$(date +%s000)'
            }' 2>/dev/null || log_warn "Failed to update Grafana"
    fi
}

main() {
    log_info "Starting infrastructure deployment..."

    # Record start time
    START_TIME=$(date +%s)

    # Run deployment steps
    check_prerequisites
    login_pulumi
    install_dependencies
    preview_changes
    deploy_infrastructure
    export_outputs
    smoke_test
    update_monitoring

    # Calculate duration
    END_TIME=$(date +%s)
    DURATION=$((END_TIME - START_TIME))

    log_info "Infrastructure deployment completed in ${DURATION} seconds"

    # Output summary
    echo
    echo "=== Deployment Summary ==="
    echo "Stack: $PULUMI_STACK"
    echo "Backend URL: ${BACKEND_URL:-Not available}"
    echo "MCP Gateway URL: ${MCP_GATEWAY_URL:-Not available}"
    echo "Frontend URL: ${FRONTEND_URL:-Not available}"
    echo "========================="
}

# Handle errors
trap 'log_error "Script failed on line $LINENO"' ERR

# Run main function
main "$@"
