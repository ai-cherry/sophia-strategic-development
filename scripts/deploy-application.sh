#!/usr/bin/env bash
# Application Deployment Script
# Deploys Sophia AI application to Lambda Labs instances

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
HOSTS=(
    "192.222.58.232"
    "104.171.202.117"
    "192.222.58.232"
    "192.222.58.67"
)
SSH_KEY="${SSH_KEY:-$HOME/.ssh/sophia2025}"
SSH_USER="${SSH_USER:-ubuntu}"
APP_DIR="/home/ubuntu/sophia-ai"
PARALLEL_DEPLOY="${PARALLEL_DEPLOY:-false}"

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

log_host() {
    echo -e "${BLUE}[$1]${NC} $2"
}

check_prerequisites() {
    log_info "Checking prerequisites..."

    # Check SSH key
    if [ ! -f "$SSH_KEY" ]; then
        log_error "SSH key not found: $SSH_KEY"
        exit 1
    fi

    # Check SSH key permissions
    if [ "$(stat -f %A "$SSH_KEY" 2>/dev/null || stat -c %a "$SSH_KEY")" != "600" ]; then
        log_warn "Fixing SSH key permissions..."
        chmod 600 "$SSH_KEY"
    fi

    # Test SSH connectivity
    log_info "Testing SSH connectivity..."
    for host in "${HOSTS[@]}"; do
        if ssh -i "$SSH_KEY" -o ConnectTimeout=5 -o StrictHostKeyChecking=no \
            "$SSH_USER@$host" "echo 'SSH OK'" &>/dev/null; then
            log_host "$host" "SSH connection OK"
        else
            log_error "Cannot connect to $host"
            exit 1
        fi
    done

    log_info "Prerequisites check passed"
}

deploy_to_host() {
    local host=$1

    log_host "$host" "Starting deployment..."

    # Create deployment script
    local deploy_script=$(cat <<'ENDDEPLOY'
#!/bin/bash
set -euo pipefail

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}Deploying Sophia AI...${NC}"

# Navigate to app directory
cd /home/ubuntu/sophia-ai || {
    echo -e "${RED}App directory not found${NC}"
    exit 1
}

# Store current version
PREV_VERSION=$(git rev-parse HEAD 2>/dev/null || echo "unknown")

# Pull latest code
echo "Pulling latest code..."
git fetch origin
git reset --hard origin/main
NEW_VERSION=$(git rev-parse HEAD)

echo "Version: ${PREV_VERSION:0:7} -> ${NEW_VERSION:0:7}"

# Update Python dependencies
echo "Updating dependencies..."
source venv/bin/activate || {
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3.12 -m venv venv
    source venv/bin/activate
}

# Use UV for fast dependency installation
if command -v uv &> /dev/null; then
    uv pip sync requirements.txt
else
    pip install --no-cache-dir -r requirements.txt
fi

# Run database migrations
if [ -d "alembic" ] || [ -d "migrations" ]; then
    echo "Running database migrations..."
    alembic upgrade head || python -m alembic upgrade head || true
fi

# Update systemd services
echo "Updating services..."

# Backend service
sudo tee /etc/systemd/system/sophia-ai-backend.service > /dev/null <<EOF
[Unit]
Description=Sophia AI Backend
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/sophia-ai
Environment="PATH=/home/ubuntu/sophia-ai/venv/bin:/usr/local/bin:/usr/bin:/bin"
Environment="PYTHONPATH=/home/ubuntu/sophia-ai"
ExecStart=/home/ubuntu/sophia-ai/venv/bin/uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# MCP Gateway service
sudo tee /etc/systemd/system/sophia-ai-mcp-gateway.service > /dev/null <<EOF
[Unit]
Description=Sophia AI MCP Gateway
After=network.target sophia-ai-backend.service

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/sophia-ai
Environment="PATH=/home/ubuntu/sophia-ai/venv/bin:/usr/local/bin:/usr/bin:/bin"
Environment="PYTHONPATH=/home/ubuntu/sophia-ai"
ExecStart=/home/ubuntu/sophia-ai/venv/bin/python -m mcp_gateway.main
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd
sudo systemctl daemon-reload

# Restart services
echo "Restarting services..."
sudo systemctl restart sophia-ai-backend
sleep 3
sudo systemctl restart sophia-ai-mcp-gateway

# Enable services
sudo systemctl enable sophia-ai-backend
sudo systemctl enable sophia-ai-mcp-gateway

# Health check
echo "Running health checks..."
sleep 5

# Check backend
if curl -sf http://localhost:8000/health | grep -q '"status":"healthy"'; then
    echo -e "${GREEN}Backend health check passed${NC}"
else
    echo -e "${RED}Backend health check failed${NC}"
    sudo journalctl -u sophia-ai-backend -n 50
    exit 1
fi

# Check MCP gateway
if curl -sf http://localhost:9000/health 2>/dev/null | grep -q "ok"; then
    echo -e "${GREEN}MCP gateway health check passed${NC}"
else
    echo -e "${YELLOW}MCP gateway health check failed (non-critical)${NC}"
fi

# Check service status
echo ""
echo "Service Status:"
sudo systemctl status sophia-ai-backend --no-pager | grep "Active:"
sudo systemctl status sophia-ai-mcp-gateway --no-pager | grep "Active:" || true

echo -e "${GREEN}Deployment completed successfully!${NC}"
ENDDEPLOY
)

    # Execute deployment
    if ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$SSH_USER@$host" "$deploy_script"; then
        log_host "$host" "Deployment successful"
        return 0
    else
        log_host "$host" "Deployment failed"
        return 1
    fi
}

deploy_parallel() {
    log_info "Deploying to all hosts in parallel..."

    local pids=()
    local failed=0

    # Start deployments in background
    for host in "${HOSTS[@]}"; do
        deploy_to_host "$host" &
        pids+=($!)
    done

    # Wait for all deployments
    for pid in "${pids[@]}"; do
        if ! wait "$pid"; then
            ((failed++))
        fi
    done

    if [ $failed -gt 0 ]; then
        log_error "$failed deployments failed"
        return 1
    fi

    return 0
}

deploy_sequential() {
    log_info "Deploying to hosts sequentially..."

    local failed=0

    for host in "${HOSTS[@]}"; do
        if ! deploy_to_host "$host"; then
            ((failed++))
            log_error "Deployment to $host failed, continuing..."
        fi
    done

    if [ $failed -gt 0 ]; then
        log_error "$failed deployments failed"
        return 1
    fi

    return 0
}

verify_deployments() {
    log_info "Verifying deployments..."

    local failed=0

    for host in "${HOSTS[@]}"; do
        log_host "$host" "Verifying..."

        # Test external connectivity
        if curl -sf "http://$host:8000/health" | grep -q '"status":"healthy"'; then
            log_host "$host" "External health check passed"
        else
            log_host "$host" "External health check failed"
            ((failed++))
        fi
    done

    if [ $failed -gt 0 ]; then
        log_warn "$failed hosts failed verification"
        return 1
    fi

    log_info "All deployments verified successfully"
    return 0
}

update_monitoring() {
    log_info "Updating monitoring..."

    # Send deployment metrics
    for host in "${HOSTS[@]}"; do
        # This would send metrics to your monitoring system
        # Example: Prometheus pushgateway, Grafana annotation, etc.
        :
    done
}

main() {
    log_info "Starting application deployment..."

    # Record start time
    START_TIME=$(date +%s)

    # Run deployment steps
    check_prerequisites

    # Deploy based on mode
    if [ "$PARALLEL_DEPLOY" == "true" ]; then
        deploy_parallel
    else
        deploy_sequential
    fi

    # Verify deployments
    verify_deployments

    # Update monitoring
    update_monitoring

    # Calculate duration
    END_TIME=$(date +%s)
    DURATION=$((END_TIME - START_TIME))

    log_info "Application deployment completed in ${DURATION} seconds"

    # Output summary
    echo
    echo "=== Deployment Summary ==="
    echo "Hosts deployed: ${#HOSTS[@]}"
    echo "Duration: ${DURATION}s"
    echo "Status: SUCCESS"
    echo "========================="
}

# Handle errors
trap 'log_error "Script failed on line $LINENO"' ERR

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --parallel)
            PARALLEL_DEPLOY=true
            shift
            ;;
        --hosts)
            IFS=',' read -ra HOSTS <<< "$2"
            shift 2
            ;;
        --ssh-key)
            SSH_KEY="$2"
            shift 2
            ;;
        *)
            log_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Run main function
main
