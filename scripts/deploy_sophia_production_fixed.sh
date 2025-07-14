#!/bin/bash

# SOPHIA AI PRODUCTION DEPLOYMENT - FIXED VERSION
# This version properly handles SSH keys from Pulumi ESC

set -e  # Exit on any error

# Configuration
SERVER_IP="104.171.202.103"
DOMAIN="sophia-intel.ai"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}======================================"
echo "   SOPHIA AI DEPLOYMENT (FIXED)"
echo "   Using Pulumi ESC for secrets"
echo "======================================${NC}"
echo ""

# Check if we have Python and Pulumi
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 is required but not installed${NC}"
    exit 1
fi

if ! command -v pulumi &> /dev/null; then
    echo -e "${RED}Pulumi is required but not installed${NC}"
    exit 1
fi

# Create temporary SSH key from Pulumi ESC
echo -e "${YELLOW}Retrieving SSH key from Pulumi ESC...${NC}"
TEMP_SSH_KEY=$(mktemp)
chmod 600 "$TEMP_SSH_KEY"

# Get SSH key from Pulumi ESC
python3 << 'EOF' > "$TEMP_SSH_KEY"
import os
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from backend.core.auto_esc_config import get_config_value

try:
    ssh_key = get_config_value("lambda_private_ssh_key")
    if not ssh_key:
        print("ERROR: Could not retrieve SSH key from Pulumi ESC", file=sys.stderr)
        sys.exit(1)
    print(ssh_key.strip())
except Exception as e:
    print(f"ERROR: {e}", file=sys.stderr)
    sys.exit(1)
EOF

if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to retrieve SSH key from Pulumi ESC${NC}"
    rm -f "$TEMP_SSH_KEY"
    exit 1
fi

echo -e "${GREEN}✓ SSH key retrieved${NC}"

# Function to execute commands on server
remote_exec() {
    ssh -i "$TEMP_SSH_KEY" -o StrictHostKeyChecking=no -o ConnectTimeout=10 ubuntu@$SERVER_IP "$@"
}

# Function to copy files to server
remote_copy() {
    scp -i "$TEMP_SSH_KEY" -o StrictHostKeyChecking=no -r "$1" ubuntu@$SERVER_IP:"$2"
}

# Cleanup function
cleanup() {
    rm -f "$TEMP_SSH_KEY"
}
trap cleanup EXIT

# Test SSH connection
echo -e "${YELLOW}Testing SSH connection to $SERVER_IP...${NC}"
if ! remote_exec "echo 'SSH OK'" 2>/dev/null; then
    echo -e "${RED}Cannot connect to server at $SERVER_IP${NC}"
    echo -e "${YELLOW}Possible issues:${NC}"
    echo "  1. Server might be stopped - check Lambda Labs dashboard"
    echo "  2. SSH key might be incorrect"
    echo "  3. Network/firewall issues"
    echo ""
    echo "Try running: python3 scripts/lambda_labs_manager.py --status"
    exit 1
fi
echo -e "${GREEN}✓ SSH connection successful${NC}"

# Get server info
echo -e "\n${BLUE}Server Information:${NC}"
remote_exec "hostname && uname -a && df -h / | tail -1"

# Option to just test connection
if [ "$1" == "test" ]; then
    echo -e "\n${GREEN}Connection test successful!${NC}"
    exit 0
fi

# Continue with deployment...
echo -e "\n${BLUE}Would you like to continue with deployment? (y/n)${NC}"
read -r response
if [[ ! "$response" =~ ^[Yy]$ ]]; then
    echo "Deployment cancelled"
    exit 0
fi

# Phase 1: Prepare server environment
echo -e "\n${BLUE}Phase 1: Preparing server environment...${NC}"
remote_exec << 'REMOTE_SCRIPT'
# Update system
sudo apt-get update -qq

# Install required packages
PACKAGES="docker.io docker-compose nginx certbot python3-certbot-nginx python3-pip python3-venv git"
for pkg in $PACKAGES; do
    if ! dpkg -l | grep -q "^ii  $pkg"; then
        echo "Installing $pkg..."
        sudo apt-get install -y $pkg
    fi
done

# Ensure docker is running
sudo systemctl start docker
sudo systemctl enable docker

# Add ubuntu user to docker group if needed
if ! groups | grep -q docker; then
    sudo usermod -aG docker ubuntu
    echo "Added to docker group - may need to reconnect"
fi

# Create directories
mkdir -p ~/sophia-deployment
mkdir -p ~/sophia-logs
mkdir -p ~/sophia-data/{postgres,redis,weaviate}

echo "Server environment ready"
REMOTE_SCRIPT

echo -e "${GREEN}✓ Server environment prepared${NC}"

# Phase 2: Check what's already running
echo -e "\n${BLUE}Phase 2: Checking existing services...${NC}"
remote_exec "docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'"

echo -e "\n${GREEN}Deployment script ready!${NC}"
echo "Next steps:"
echo "  1. Run './scripts/deploy_sophia_production_fixed.sh test' to test connection"
echo "  2. Run './scripts/deploy_sophia_production_fixed.sh' to start deployment"
echo "  3. Use './scripts/quick_backend_deploy.sh' for backend only"
echo "  4. Use './scripts/quick_frontend_deploy.sh' for frontend only" 