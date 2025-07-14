#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Sophia AI Kubernetes Health Check ===${NC}"
echo ""

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}❌ kubectl not found. Please install kubectl first.${NC}"
    exit 1
fi

# Check namespace
echo -e "${YELLOW}Checking namespace...${NC}"
if kubectl get namespace sophia-ai-prod &> /dev/null; then
    echo -e "${GREEN}✅ Namespace sophia-ai-prod exists${NC}"
else
    echo -e "${RED}❌ Namespace sophia-ai-prod not found${NC}"
    echo "Creating namespace..."
    kubectl create namespace sophia-ai-prod
fi

echo ""
echo -e "${YELLOW}=== Pod Status ===${NC}"
kubectl get pods -n sophia-ai-prod

echo ""
echo -e "${YELLOW}=== Service Endpoints ===${NC}"
kubectl get endpoints -n sophia-ai-prod

echo ""
echo -e "${YELLOW}=== Ingress Status ===${NC}"
kubectl get ingress -n sophia-ai-prod

echo ""
echo -e "${YELLOW}=== Persistent Volume Claims ===${NC}"
kubectl get pvc -n sophia-ai-prod

echo ""
echo -e "${YELLOW}=== API Health Tests ===${NC}"
# Test backend health
if kubectl get service sophia-backend -n sophia-ai-prod &> /dev/null; then
    echo "Testing backend health endpoint..."
    kubectl port-forward service/sophia-backend 8000:8000 -n sophia-ai-prod &
    PF_PID=$!
    sleep 5
    
    if curl -f http://localhost:8000/api/health &> /dev/null; then
        echo -e "${GREEN}✅ Backend health check passed${NC}"
    else
        echo -e "${RED}❌ Backend health check failed${NC}"
    fi
    
    kill $PF_PID 2>/dev/null
else
    echo -e "${YELLOW}⚠️  Backend service not found${NC}"
fi

echo ""
echo -e "${YELLOW}=== MCP Server Tests ===${NC}"
MCP_SERVERS=(
    "ai-memory:9000"
    "gong:9001"
    "modern_stack:9002"
    "slack:9003"
    "linear:9004"
    "github:9005"
    "codacy:9006"
    "asana:9007"
)

for server_config in "${MCP_SERVERS[@]}"; do
    IFS=':' read -r server_name port <<< "$server_config"
    
    if kubectl get service mcp-${server_name} -n sophia-ai-prod &> /dev/null; then
        echo -e "${GREEN}✅ MCP ${server_name} service exists${NC}"
    else
        echo -e "${RED}❌ MCP ${server_name} service not found${NC}"
    fi
done

echo ""
echo -e "${BLUE}=== Health Check Complete ===${NC}" 