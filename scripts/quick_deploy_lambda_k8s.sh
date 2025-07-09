#!/bin/bash
# Quick deployment script for Lambda Labs Kubernetes
# Uses existing manifests and pre-built images

set -euo pipefail

# Configuration
DOCKER_REGISTRY="${DOCKER_REGISTRY:-scoobyjava15}"
SSH_KEY="${SSH_KEY:-~/.ssh/sophia2025.pem}"
CONTROL_PLANE_IP="104.171.202.103"
NAMESPACE="sophia-ai-prod"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🚀 Quick Deploy to Lambda Labs Kubernetes${NC}"

# Step 1: Setup kubectl access
echo -e "${YELLOW}Setting up kubectl access...${NC}"
scp -i ${SSH_KEY} ubuntu@${CONTROL_PLANE_IP}:~/.kube/config /tmp/kubeconfig
export KUBECONFIG=/tmp/kubeconfig

# Step 2: Create namespace
echo -e "${YELLOW}Creating namespace...${NC}"
kubectl create namespace ${NAMESPACE} --dry-run=client -o yaml | kubectl apply -f -

# Step 3: Apply existing manifests
echo -e "${YELLOW}Deploying applications...${NC}"

# Core infrastructure
kubectl apply -f kubernetes/production/namespace.yaml
kubectl apply -f kubernetes/production/storage.yaml
kubectl apply -f kubernetes/production/postgres-deployment.yaml
kubectl apply -f kubernetes/production/redis-deployment.yaml

# Backend and frontend
kubectl apply -f kubernetes/production/sophia-backend-deployment.yaml
kubectl apply -f kubernetes/production/frontend-deployment.yaml

# MCP servers
for mcp in kubernetes/production/mcp-*.yaml; do
    echo "Applying $mcp..."
    kubectl apply -f $mcp
done

# Services and ingress
kubectl apply -f kubernetes/production/sophia-service.yaml
kubectl apply -f kubernetes/production/ingress.yaml

# Monitoring
kubectl apply -f kubernetes/monitoring/

# Step 4: Wait for deployments
echo -e "${YELLOW}Waiting for deployments to be ready...${NC}"
kubectl -n ${NAMESPACE} wait --for=condition=available --timeout=300s deployment --all || true

# Step 5: Show status
echo -e "${YELLOW}Deployment status:${NC}"
kubectl -n ${NAMESPACE} get pods
kubectl -n ${NAMESPACE} get services

echo -e "${GREEN}✅ Quick deployment complete!${NC}"
echo -e "${GREEN}Access via: http://${CONTROL_PLANE_IP}${NC}" 