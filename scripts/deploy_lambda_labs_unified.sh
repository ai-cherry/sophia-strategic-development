#!/bin/bash
# 🚀 UNIFIED SOPHIA AI DEPLOYMENT TO LAMBDA LABS K3S
# Deploys the complete enterprise-grade cloud-native platform to sophia-intel.ai

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
LAMBDA_K3S_IP="192.222.58.232"
KUBECONFIG_PATH="$HOME/.kube/k3s-lambda-labs-tunnel"
DEPLOYMENT_LOG="deployment-$(date +%Y%m%d-%H%M%S).log"

echo -e "${BLUE}🚀 SOPHIA AI UNIFIED DEPLOYMENT${NC}"
echo -e "${BLUE}=================================${NC}"
echo "Target: Lambda Labs K3s Cluster (${LAMBDA_K3S_IP})"
echo "Domain: sophia-intel.ai"
echo "Log: ${DEPLOYMENT_LOG}"
echo ""

# Function to log messages
log() {
    echo -e "$1" | tee -a "${DEPLOYMENT_LOG}"
}

# Function to check command success
check_success() {
    if [ $? -eq 0 ]; then
        log "${GREEN}✅ $1${NC}"
    else
        log "${RED}❌ $1 FAILED${NC}"
        exit 1
    fi
}

# Step 1: Verify kubeconfig access
log "${BLUE}📋 Step 1: Verifying K3s Cluster Access${NC}"
export KUBECONFIG="${KUBECONFIG_PATH}"

if kubectl cluster-info &>/dev/null; then
    log "${GREEN}✅ K3s cluster accessible at ${LAMBDA_K3S_IP}${NC}"
    kubectl get nodes -o wide
else
    log "${RED}❌ Cannot access K3s cluster. Check kubeconfig: ${KUBECONFIG_PATH}${NC}"
    log "${YELLOW}💡 Run: scp root@${LAMBDA_K3S_IP}:/etc/rancher/k3s/k3s.yaml ${KUBECONFIG_PATH}${NC}"
    exit 1
fi

# Step 2: Deploy cert-manager (if not already installed)
log "\n${BLUE}📋 Step 2: Installing cert-manager${NC}"
if ! kubectl get namespace cert-manager &>/dev/null; then
    log "${YELLOW}🔧 Installing cert-manager...${NC}"
    kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml
    check_success "cert-manager installation"
    
    log "${YELLOW}⏳ Waiting for cert-manager pods...${NC}"
    kubectl wait --for=condition=Ready pods --all -n cert-manager --timeout=300s
    check_success "cert-manager pods ready"
else
    log "${GREEN}✅ cert-manager already installed${NC}"
fi

# Step 3: Create namespaces
log "\n${BLUE}📋 Step 3: Creating Namespaces${NC}"
kubectl apply -f - <<EOF
apiVersion: v1
kind: Namespace
metadata:
  name: sophia-ai-prod
  labels:
    app.kubernetes.io/name: sophia-ai-prod
    app.kubernetes.io/part-of: sophia-ai
---
apiVersion: v1
kind: Namespace
metadata:
  name: mcp-servers
  labels:
    app.kubernetes.io/name: mcp-servers
    app.kubernetes.io/part-of: sophia-ai
---
apiVersion: v1
kind: Namespace
metadata:
  name: monitoring
  labels:
    app.kubernetes.io/name: monitoring
    app.kubernetes.io/part-of: sophia-ai
EOF
check_success "namespace creation"

# Step 4: Deploy Sophia AI Platform
log "\n${BLUE}📋 Step 4: Deploying Sophia AI Platform${NC}"
log "${YELLOW}🔧 Applying base infrastructure...${NC}"
kubectl apply -k k8s/overlays/production
check_success "Sophia AI platform deployment"

# Step 5: Deploy monitoring
log "\n${BLUE}📋 Step 5: Deploying Monitoring Stack${NC}"
if [ -f k8s/monitoring/service-monitors.yaml ]; then
    kubectl apply -f k8s/monitoring/service-monitors.yaml
    check_success "monitoring deployment"
else
    log "${YELLOW}⚠️  Monitoring file not found, skipping${NC}"
fi

# Step 6: Wait for deployment rollout
log "\n${BLUE}📋 Step 6: Waiting for Deployment Rollout${NC}"
log "${YELLOW}⏳ Waiting for sophia-backend deployment...${NC}"
if kubectl rollout status deployment/sophia-backend -n sophia-ai-prod --timeout=300s; then
    log "${GREEN}✅ sophia-backend deployment ready${NC}"
else
    log "${YELLOW}⚠️  sophia-backend deployment timeout, checking status...${NC}"
    kubectl get pods -n sophia-ai-prod
fi

# Step 7: Verify services
log "\n${BLUE}📋 Step 7: Verifying Services${NC}"
log "${YELLOW}🔍 Checking service status...${NC}"
kubectl get services -n sophia-ai-prod
kubectl get pods -n sophia-ai-prod -o wide
kubectl get ingress -n sophia-ai-prod

# Step 8: Check SSL certificate status
log "\n${BLUE}📋 Step 8: Checking SSL Certificates${NC}"
if kubectl get certificateissuers.cert-manager.io &>/dev/null; then
    kubectl get certificates -A
    kubectl get certificateissuers -A
else
    log "${YELLOW}⚠️  cert-manager CRDs not ready yet${NC}"
fi

# Step 9: Display access information
log "\n${GREEN}🎉 DEPLOYMENT COMPLETE!${NC}"
log "${GREEN}========================${NC}"
log "${BLUE}📊 Access URLs:${NC}"
log "  Frontend:   https://sophia-intel.ai"
log "  API:        https://api.sophia-intel.ai"
log "  Monitoring: https://grafana.sophia-intel.ai"
log ""
log "${BLUE}📊 Service Status:${NC}"
kubectl get pods -n sophia-ai-prod --no-headers | while read line; do
    pod_name=$(echo $line | awk '{print $1}')
    status=$(echo $line | awk '{print $3}')
    if [[ "$status" == "Running" ]]; then
        log "${GREEN}✅ $pod_name: $status${NC}"
    else
        log "${YELLOW}⏳ $pod_name: $status${NC}"
    fi
done

log "\n${BLUE}📋 Next Steps:${NC}"
log "1. Configure DNS: Point sophia-intel.ai to ${LAMBDA_K3S_IP}"
log "2. Wait for SSL certificates to provision (5-10 minutes)"
log "3. Test endpoints: curl -I https://api.sophia-intel.ai/health"
log "4. Monitor logs: kubectl logs -f deployment/sophia-backend -n sophia-ai-prod"

log "\n${GREEN}🚀 Sophia AI Platform deployed successfully to Lambda Labs K3s!${NC}"
echo "Full deployment log saved to: ${DEPLOYMENT_LOG}" 