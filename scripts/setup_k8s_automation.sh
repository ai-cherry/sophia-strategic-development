#!/bin/bash
# Setup Kubernetes automation for Lambda Labs deployment
# Includes Keel for image updates and GitOps preparation

set -euo pipefail

# Configuration
SSH_KEY="${SSH_KEY:-~/.ssh/sophia2025.pem}"
CONTROL_PLANE_IP="104.171.202.103"
DOCKER_REGISTRY="${DOCKER_REGISTRY:-scoobyjava15}"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}🚀 Setting up Kubernetes Automation${NC}"

# Function to setup kubectl
setup_kubectl() {
    echo -e "${YELLOW}Setting up kubectl access...${NC}"
    
    # Get kubeconfig from control plane
    scp -i ${SSH_KEY} ubuntu@${CONTROL_PLANE_IP}:~/.kube/config /tmp/kubeconfig
    export KUBECONFIG=/tmp/kubeconfig
    
    # Test connection
    if kubectl get nodes &>/dev/null; then
        echo -e "${GREEN}✅ kubectl configured successfully${NC}"
    else
        echo -e "${RED}❌ Failed to connect to cluster${NC}"
        exit 1
    fi
}

# Function to install Keel
install_keel() {
    echo -e "${YELLOW}Installing Keel for automatic image updates...${NC}"
    
    # Create Docker registry secret for Keel
    kubectl create namespace keel --dry-run=client -o yaml | kubectl apply -f -
    
    # Create Docker registry secret
    kubectl create secret docker-registry docker-registry-secret \
        --docker-server=docker.io \
        --docker-username=${DOCKER_REGISTRY} \
        --docker-password="${DOCKER_HUB_ACCESS_TOKEN}" \
        --namespace=keel \
        --dry-run=client -o yaml | kubectl apply -f -
    
    # Create basic auth secret for Keel
    KEEL_PASSWORD=$(openssl rand -base64 32)
    kubectl create secret generic keel-basic-auth \
        --from-literal=password="${KEEL_PASSWORD}" \
        --namespace=keel \
        --dry-run=client -o yaml | kubectl apply -f -
    
    # Apply Keel deployment
    kubectl apply -f kubernetes/keel/keel-deployment.yaml
    
    # Wait for Keel to be ready
    kubectl -n keel wait --for=condition=available --timeout=300s deployment/keel
    
    echo -e "${GREEN}✅ Keel installed successfully${NC}"
    echo -e "${YELLOW}Keel credentials:${NC}"
    echo -e "${BLUE}Username: admin${NC}"
    echo -e "${BLUE}Password: ${KEEL_PASSWORD}${NC}"
}

# Function to update deployments with Keel annotations
update_deployments_for_keel() {
    echo -e "${YELLOW}Updating deployments with Keel annotations...${NC}"
    
    # Apply Keel-annotated deployments
    kubectl apply -f kubernetes/production/sophia-backend-deployment-keel.yaml
    kubectl apply -f kubernetes/production/sophia-frontend-deployment-keel.yaml
    
    echo -e "${GREEN}✅ Deployments updated for automatic image updates${NC}"
}

# Function to setup GitOps structure
setup_gitops() {
    echo -e "${YELLOW}Setting up GitOps structure...${NC}"
    
    # Create namespace
    kubectl create namespace sophia-ai-prod --dry-run=client -o yaml | kubectl apply -f -
    
    # Apply Kustomization
    kubectl apply -k kubernetes/gitops/
    
    echo -e "${GREEN}✅ GitOps structure applied${NC}"
}

# Function to install ArgoCD (optional)
install_argocd() {
    echo -e "${YELLOW}Would you like to install ArgoCD for full GitOps? (y/n)${NC}"
    read -r response
    
    if [[ "$response" == "y" ]]; then
        echo -e "${YELLOW}Installing ArgoCD...${NC}"
        
        # Create namespace
        kubectl create namespace argocd --dry-run=client -o yaml | kubectl apply -f -
        
        # Install ArgoCD
        kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
        
        # Wait for ArgoCD to be ready
        kubectl -n argocd wait --for=condition=available --timeout=300s deployment/argocd-server
        
        # Apply Sophia application
        kubectl apply -f kubernetes/gitops/argocd/sophia-app.yaml
        
        # Get admin password
        ARGOCD_PASSWORD=$(kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d)
        
        echo -e "${GREEN}✅ ArgoCD installed successfully${NC}"
        echo -e "${YELLOW}ArgoCD credentials:${NC}"
        echo -e "${BLUE}Username: admin${NC}"
        echo -e "${BLUE}Password: ${ARGOCD_PASSWORD}${NC}"
    fi
}

# Function to setup monitoring
setup_monitoring() {
    echo -e "${YELLOW}Setting up deployment monitoring...${NC}"
    
    # Apply monitoring manifests
    kubectl apply -f kubernetes/monitoring/
    
    echo -e "${GREEN}✅ Monitoring configured${NC}"
}

# Function to verify automation
verify_automation() {
    echo -e "${YELLOW}Verifying automation setup...${NC}"
    
    # Check Keel
    echo -e "${YELLOW}Keel status:${NC}"
    kubectl -n keel get pods
    kubectl -n keel logs deployment/keel --tail=20
    
    # Check deployments
    echo -e "${YELLOW}Deployment status:${NC}"
    kubectl -n sophia-ai-prod get deployments
    
    # Show annotations
    echo -e "${YELLOW}Keel annotations on deployments:${NC}"
    kubectl -n sophia-ai-prod get deployment sophia-backend -o jsonpath='{.metadata.annotations}' | jq .
    
    echo -e "${GREEN}✅ Automation verification complete${NC}"
}

# Function to create update script
create_update_script() {
    cat > trigger_image_update.sh << 'EOF'
#!/bin/bash
# Trigger image update by pushing new tags

DOCKER_REGISTRY="${DOCKER_REGISTRY:-scoobyjava15}"
NEW_TAG="${1:-$(date +%Y%m%d-%H%M%S)}"

echo "Tagging and pushing images with tag: ${NEW_TAG}"

# Tag images
docker tag ${DOCKER_REGISTRY}/sophia-backend:latest ${DOCKER_REGISTRY}/sophia-backend:${NEW_TAG}
docker tag ${DOCKER_REGISTRY}/sophia-frontend:latest ${DOCKER_REGISTRY}/sophia-frontend:${NEW_TAG}

# Push new tags
docker push ${DOCKER_REGISTRY}/sophia-backend:${NEW_TAG}
docker push ${DOCKER_REGISTRY}/sophia-frontend:${NEW_TAG}

echo "New images pushed. Keel will detect and update within 1 minute."
EOF
    
    chmod +x trigger_image_update.sh
    
    echo -e "${GREEN}✅ Created trigger_image_update.sh for manual updates${NC}"
}

# Main execution
main() {
    echo -e "${BLUE}Starting Kubernetes automation setup...${NC}"
    
    setup_kubectl
    install_keel
    update_deployments_for_keel
    setup_gitops
    install_argocd
    setup_monitoring
    verify_automation
    create_update_script
    
    echo -e "${GREEN}✅ Automation setup complete!${NC}"
    echo -e "${GREEN}Your deployments will now automatically update when new images are pushed${NC}"
    echo -e "${YELLOW}To manually trigger an update:${NC}"
    echo -e "${BLUE}./trigger_image_update.sh [tag]${NC}"
}

# Get Docker Hub token from environment or Pulumi ESC
if [ -z "${DOCKER_HUB_ACCESS_TOKEN}" ]; then
    echo -e "${YELLOW}Loading Docker Hub credentials from Pulumi ESC...${NC}"
    source backend/core/auto_esc_config.py
    export DOCKER_TOKEN=$(python -c "from backend.core.auto_esc_config import get_docker_hub_config; print(get_docker_hub_config()['access_token'])")
fi

# Run main
main "$@" 