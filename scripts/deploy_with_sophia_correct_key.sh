#!/bin/bash
# Sophia AI Unified Deployment Script
# Uses ONLY sophia_correct_key for all SSH operations

set -euo pipefail

# Configuration
LAMBDA_IP="${LAMBDA_IP:-192.222.58.232}"
SSH_KEY="$HOME/.ssh/sophia_correct_key"
DOCKER_REGISTRY="scoobyjava15"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}🚀 Sophia AI Unified Deployment${NC}"
echo "================================="
echo "SSH Key: $SSH_KEY"
echo "Target: $LAMBDA_IP"
echo ""

# Validate SSH key exists
if [[ ! -f "$SSH_KEY" ]]; then
    echo -e "${RED}❌ SSH key not found at $SSH_KEY${NC}"
    echo "Run: python scripts/ssh_key_manager.py --setup"
    exit 1
fi

# Test SSH connection
echo -e "${YELLOW}🔗 Testing SSH connection...${NC}"
if ssh -i "$SSH_KEY" -o ConnectTimeout=10 -o BatchMode=yes ubuntu@$LAMBDA_IP exit; then
    echo -e "${GREEN}✅ SSH connection successful${NC}"
else
    echo -e "${RED}❌ SSH connection failed${NC}"
    echo "Run: python scripts/ssh_key_manager.py --validate"
    exit 1
fi

# Deploy Sophia AI
echo -e "${YELLOW}🚀 Deploying Sophia AI...${NC}"
export KUBECONFIG=~/.kube/config-lambda-labs-tunnel
kubectl apply -f k8s/production/

echo -e "${GREEN}✅ Deployment complete!${NC}"
echo "🌐 Access: https://$LAMBDA_IP"
echo "🔑 SSH: ssh -i $SSH_KEY ubuntu@$LAMBDA_IP" 