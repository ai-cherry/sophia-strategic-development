#!/bin/bash
# Deploy Sophia AI with automated image updates
# Combines manual deployment with automation setup

set -euo pipefail

# Configuration
SSH_KEY="${SSH_KEY:-~/.ssh/sophia2025.pem}"
CONTROL_PLANE_IP="104.171.202.103"
DOCKER_REGISTRY="${DOCKER_REGISTRY:-scoobyjava15}"
DEPLOY_METHOD="${1:-keel}"  # keel, gitops, or manual

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🚀 Deploying Sophia AI with Automation${NC}"
echo -e "${BLUE}Method: ${DEPLOY_METHOD}${NC}"

# Setup kubectl
echo -e "${YELLOW}Setting up kubectl...${NC}"
scp -i ${SSH_KEY} ubuntu@${CONTROL_PLANE_IP}:~/.kube/config /tmp/kubeconfig
export KUBECONFIG=/tmp/kubeconfig

# Function for Keel deployment
deploy_with_keel() {
    echo -e "${YELLOW}Deploying with Keel automation...${NC}"
    
    # Apply Keel-annotated deployments
    kubectl apply -f kubernetes/production/sophia-backend-deployment-keel.yaml
    kubectl apply -f kubernetes/production/sophia-frontend-deployment-keel.yaml
    
    # Apply other resources
    kubectl apply -f kubernetes/production/namespace.yaml
    kubectl apply -f kubernetes/production/storage.yaml
    kubectl apply -f kubernetes/production/postgres-deployment.yaml
    kubectl apply -f kubernetes/production/redis-deployment.yaml
    kubectl apply -f kubernetes/production/sophia-service.yaml
    kubectl apply -f kubernetes/production/ingress.yaml
    
    echo -e "${GREEN}✅ Deployed with Keel automation${NC}"
    echo -e "${YELLOW}Images will auto-update when new tags are pushed${NC}"
}

# Function for GitOps deployment
deploy_with_gitops() {
    echo -e "${YELLOW}Deploying with GitOps (Kustomize)...${NC}"
    
    # Apply Kustomization
    kubectl apply -k kubernetes/gitops/
    
    echo -e "${GREEN}✅ Deployed with GitOps${NC}"
    echo -e "${YELLOW}Update kubernetes/gitops/kustomization.yaml to trigger updates${NC}"
}

# Function for manual deployment
deploy_manual() {
    echo -e "${YELLOW}Deploying manually...${NC}"
    
    # Apply all manifests
    kubectl apply -f kubernetes/production/
    
    echo -e "${GREEN}✅ Manual deployment complete${NC}"
}

# Function to show status
show_status() {
    echo -e "${YELLOW}Deployment status:${NC}"
    
    # Wait for deployments
    kubectl -n sophia-ai-prod wait --for=condition=available --timeout=300s deployment --all || true
    
    # Show pods
    kubectl -n sophia-ai-prod get pods
    
    # Show services
    kubectl -n sophia-ai-prod get services
    
    # Get IPs
    BACKEND_IP=$(kubectl -n sophia-ai-prod get svc sophia-backend -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "pending")
    FRONTEND_IP=$(kubectl -n sophia-ai-prod get svc sophia-frontend -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "pending")
    
    echo -e "${GREEN}Access URLs:${NC}"
    echo -e "${BLUE}Backend: http://${BACKEND_IP}:8000${NC}"
    echo -e "${BLUE}Frontend: http://${FRONTEND_IP}${NC}"
}

# Main deployment
case $DEPLOY_METHOD in
    keel)
        deploy_with_keel
        ;;
    gitops)
        deploy_with_gitops
        ;;
    manual)
        deploy_manual
        ;;
    *)
        echo -e "${RED}Unknown deployment method: $DEPLOY_METHOD${NC}"
        echo "Usage: $0 [keel|gitops|manual]"
        exit 1
        ;;
esac

# Show status
show_status

echo -e "${GREEN}✅ Deployment complete!${NC}"

# Show next steps
echo -e "${YELLOW}Next steps:${NC}"
case $DEPLOY_METHOD in
    keel)
        echo -e "${BLUE}1. Push new Docker images to trigger automatic updates${NC}"
        echo -e "${BLUE}2. Monitor updates: kubectl -n keel logs deployment/keel -f${NC}"
        ;;
    gitops)
        echo -e "${BLUE}1. Update image tags in kubernetes/gitops/kustomization.yaml${NC}"
        echo -e "${BLUE}2. Commit and push to trigger deployment${NC}"
        ;;
    manual)
        echo -e "${BLUE}1. To update: kubectl set image deployment/sophia-backend sophia-backend=\$IMAGE${NC}"
        echo -e "${BLUE}2. Consider setting up automation with: ./scripts/setup_k8s_automation.sh${NC}"
        ;;
esac 