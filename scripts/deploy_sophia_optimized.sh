#!/bin/bash
# Sophia AI Optimized Deployment Script
# Generated: 2025-07-04 18:04:56

# Configuration
GITHUB_TOKEN="${GITHUB_TOKEN:-}"  # Set via environment variable
PLATFORM_IP="146.235.200.1"  # sophia-platform-prod
AI_IP="137.131.6.213"        # sophia-ai-prod (A100)
MCP_IP="165.1.69.44"         # sophia-mcp-prod

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo "🚀 Sophia AI Production Deployment"
echo "=================================="

# Function to setup instance
setup_instance() {
    local IP=$1
    local ROLE=$2

    echo -e "${GREEN}Setting up $ROLE on $IP${NC}"

    ssh -i ~/.ssh/lambda_labs_key ubuntu@$IP << 'SETUP'
        # Update system
        sudo apt-get update
        sudo apt-get upgrade -y

        # Install Docker
        curl -fsSL https://get.docker.com -o get-docker.sh
        sudo sh get-docker.sh
        sudo usermod -aG docker ubuntu

        # Install dependencies
        sudo apt-get install -y python3-pip git nginx certbot

        # Clone repository
        git clone https://github.com/ai-cherry/sophia-main.git
        cd sophia-main

        # Set environment
        echo "export ENVIRONMENT=prod" >> ~/.bashrc
        echo "export PULUMI_ORG=scoobyjava-org" >> ~/.bashrc
        echo "export GITHUB_TOKEN=$GITHUB_TOKEN" >> ~/.bashrc
        source ~/.bashrc

        # Install Python dependencies
        pip install uv
        uv venv
        source .venv/bin/activate
        uv sync
SETUP
}

# Main deployment
echo "Waiting for instances to be ready..."
sleep 30

# Deploy to each instance
setup_instance $PLATFORM_IP "Platform Server"
setup_instance $AI_IP "AI Server"
setup_instance $MCP_IP "MCP Server"

echo -e "${GREEN}✅ Deployment preparation complete!${NC}"
