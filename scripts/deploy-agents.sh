#!/bin/bash
#
# Deploy Autonomous Agents to Production
# 
# This script builds and deploys all autonomous agents to the K3s cluster on Lambda Labs
#
# Usage: ./scripts/deploy-agents.sh [--env production|staging] [--dry-run]
#

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default values
ENV="${1:-production}"
DRY_RUN=false
DOCKER_REGISTRY="scoobyjava15"
K8S_NAMESPACE="autonomous-agents"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --env)
            ENV="$2"
            shift 2
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        *)
            shift
            ;;
    esac
done

echo -e "${GREEN}🚀 Deploying Autonomous Agents to ${ENV}${NC}"

# Validate environment
if [[ "$ENV" != "production" && "$ENV" != "staging" ]]; then
    echo -e "${RED}❌ Invalid environment: $ENV${NC}"
    echo "Usage: $0 [--env production|staging] [--dry-run]"
    exit 1
fi

# Check prerequisites
echo -e "${YELLOW}📋 Checking prerequisites...${NC}"

# Check docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker not found${NC}"
    exit 1
fi

# Check kubectl
if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}❌ kubectl not found${NC}"
    exit 1
fi

# Check kubectl connection
if ! kubectl cluster-info &> /dev/null; then
    echo -e "${RED}❌ Cannot connect to Kubernetes cluster${NC}"
    echo "Please configure kubectl to connect to Lambda Labs K3s cluster"
    exit 1
fi

echo -e "${GREEN}✅ Prerequisites satisfied${NC}"

# Create namespace if it doesn't exist
echo -e "${YELLOW}📦 Creating namespace...${NC}"
if [[ "$DRY_RUN" == "false" ]]; then
    kubectl create namespace $K8S_NAMESPACE --dry-run=client -o yaml | kubectl apply -f -
else
    echo "[DRY RUN] Would create namespace: $K8S_NAMESPACE"
fi

# Build and push Docker images
echo -e "${YELLOW}🐳 Building Docker images...${NC}"

AGENTS=(
    "self-healing-orchestrator"
    "lambda-labs-monitor"
    "lambda-labs-autonomous"
    "qdrant-optimizer"
    "prometheus-exporter"
)

for agent in "${AGENTS[@]}"; do
    echo -e "${YELLOW}Building $agent...${NC}"
    
    DOCKERFILE="autonomous-agents/docker/Dockerfile.$agent"
    IMAGE_TAG="$DOCKER_REGISTRY/sophia-$agent:latest"
    
    if [[ "$DRY_RUN" == "false" ]]; then
        # Build image
        docker build -f "$DOCKERFILE" -t "$IMAGE_TAG" .
        
        # Push to registry
        echo -e "${YELLOW}Pushing $IMAGE_TAG...${NC}"
        docker push "$IMAGE_TAG"
    else
        echo "[DRY RUN] Would build and push: $IMAGE_TAG"
    fi
done

# Apply Kubernetes manifests
echo -e "${YELLOW}☸️  Deploying to Kubernetes...${NC}"

# Apply ConfigMaps and Secrets
if [[ "$DRY_RUN" == "false" ]]; then
    kubectl apply -f k8s/agents/configmap.yaml -n $K8S_NAMESPACE
    kubectl apply -f k8s/agents/secrets.yaml -n $K8S_NAMESPACE
else
    echo "[DRY RUN] Would apply ConfigMaps and Secrets"
fi

# Deploy each agent
for agent in "${AGENTS[@]}"; do
    echo -e "${YELLOW}Deploying $agent...${NC}"
    
    MANIFEST="k8s/agents/$agent-deployment.yaml"
    
    if [[ "$DRY_RUN" == "false" ]]; then
        kubectl apply -f "$MANIFEST" -n $K8S_NAMESPACE
    else
        echo "[DRY RUN] Would apply: $MANIFEST"
    fi
done

# Apply services
echo -e "${YELLOW}🌐 Creating services...${NC}"
if [[ "$DRY_RUN" == "false" ]]; then
    kubectl apply -f k8s/agents/services.yaml -n $K8S_NAMESPACE
else
    echo "[DRY RUN] Would apply services"
fi

# Apply ingress
echo -e "${YELLOW}🚪 Configuring ingress...${NC}"
if [[ "$DRY_RUN" == "false" ]]; then
    kubectl apply -f k8s/agents/ingress.yaml -n $K8S_NAMESPACE
else
    echo "[DRY RUN] Would apply ingress"
fi

# Wait for deployments to be ready
if [[ "$DRY_RUN" == "false" ]]; then
    echo -e "${YELLOW}⏳ Waiting for deployments to be ready...${NC}"
    
    for agent in "${AGENTS[@]}"; do
        kubectl rollout status deployment/$agent -n $K8S_NAMESPACE --timeout=300s || {
            echo -e "${RED}❌ Deployment failed for $agent${NC}"
            exit 1
        }
    done
fi

# Show deployment status
echo -e "${GREEN}📊 Deployment Status:${NC}"
if [[ "$DRY_RUN" == "false" ]]; then
    kubectl get deployments -n $K8S_NAMESPACE
    echo ""
    kubectl get pods -n $K8S_NAMESPACE
    echo ""
    kubectl get services -n $K8S_NAMESPACE
else
    echo "[DRY RUN] Would show deployment status"
fi

# Show access instructions
echo -e "${GREEN}✅ Deployment complete!${NC}"
echo ""
echo -e "${YELLOW}📋 Access Instructions:${NC}"
echo "1. View agent dashboard: kubectl port-forward -n $K8S_NAMESPACE svc/agent-dashboard 3000:3000"
echo "   Then open: http://localhost:3000/agent-dashboard"
echo ""
echo "2. View Prometheus metrics: kubectl port-forward -n $K8S_NAMESPACE svc/prometheus 9090:9090"
echo "   Then open: http://localhost:9090"
echo ""
echo "3. Monitor agents: kubectl get pods -n $K8S_NAMESPACE -w"
echo ""
echo "4. View logs: kubectl logs -n $K8S_NAMESPACE -l app=autonomous-agent -f"

# Run post-deployment tests
echo -e "${YELLOW}🧪 Running post-deployment tests...${NC}"
if [[ "$DRY_RUN" == "false" ]]; then
    python scripts/test_agent_deployment.py --namespace $K8S_NAMESPACE
else
    echo "[DRY RUN] Would run post-deployment tests"
fi

echo -e "${GREEN}🎉 All done!${NC}"
