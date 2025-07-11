#!/bin/bash
# SOPHIA AI K3S DEPLOYMENT - NO BS EDITION
# "If this deployment fails, at least Sophia can orchestrate your funeral playlist via Slack integration"

set -e  # Exit on any error because we're not here to debug all day

# Configuration
MCP_SERVER="104.171.202.117"
PRODUCTION_SERVER="104.171.202.103"
AI_CORE_SERVER="192.222.58.232"
PEM_FILE="$HOME/.ssh/sophia2025.pem"
DOCKER_REGISTRY="scoobyjava15"  # Your Docker Hub

# Colors for output (because we're not savages)
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}🚀 SOPHIA AI K3S DEPLOYMENT - CUT THE CRAP EDITION${NC}"
echo -e "${BLUE}================================================${NC}"

# Function to execute commands on remote server
remote_exec() {
    local server=$1
    local command=$2
    echo -e "${YELLOW}➜ Executing on $server: $command${NC}"
    ssh -i "$PEM_FILE" -o StrictHostKeyChecking=no ubuntu@$server "$command"
}

# Function to check if command succeeded
check_status() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Success${NC}"
    else
        echo -e "${RED}❌ Failed - Fix this before continuing${NC}"
        exit 1
    fi
}

# Phase 1: Server Prep (The Boring But Necessary Stuff)
echo -e "\n${BLUE}PHASE 1: SERVER PREP${NC}"
echo -e "${YELLOW}Installing build dependencies on MCP server...${NC}"

remote_exec $MCP_SERVER "sudo apt update && sudo apt upgrade -y"
check_status

remote_exec $MCP_SERVER "sudo apt install -y docker.io curl git python3-pip build-essential g++ libssl-dev rustc cargo python3-dev"
check_status

remote_exec $MCP_SERVER "sudo systemctl enable --now docker"
check_status

remote_exec $MCP_SERVER "sudo usermod -aG docker ubuntu"
check_status

# Phase 2: K3s Installation (The Good Stuff)
echo -e "\n${BLUE}PHASE 2: K3S INSTALLATION${NC}"
echo -e "${YELLOW}Installing K3s on MCP orchestrator...${NC}"

# Install K3s with Traefik enabled (we're keeping it for simplicity)
remote_exec $MCP_SERVER "curl -sfL https://get.k3s.io | sh -"
check_status

# Verify K3s is running
remote_exec $MCP_SERVER "sudo k3s kubectl get nodes"
check_status

# Install Helm (for the fancy kids)
echo -e "${YELLOW}Installing Helm...${NC}"
remote_exec $MCP_SERVER "curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash"
check_status

# Copy kubeconfig to local for management
echo -e "${YELLOW}Copying kubeconfig to local...${NC}"
mkdir -p ~/.kube
scp -i "$PEM_FILE" ubuntu@$MCP_SERVER:/etc/rancher/k3s/k3s.yaml ~/.kube/sophia-k3s.yaml
sed -i "s/127.0.0.1/$MCP_SERVER/g" ~/.kube/sophia-k3s.yaml
export KUBECONFIG=~/.kube/sophia-k3s.yaml

echo -e "${GREEN}✅ K3s cluster ready on $MCP_SERVER${NC}"

# Phase 3: Create K8s Namespace and Secrets
echo -e "\n${BLUE}PHASE 3: K8S SETUP${NC}"
kubectl create namespace sophia-ai || true

# Create secrets (replace with actual values)
kubectl create secret generic sophia-secrets \
  --from-literal=SNOWFLAKE_USER=SCOOBYJAVA15 \
  --from-literal=SNOWFLAKE_ACCOUNT=UHDECNO-CVB64222 \
  --from-literal=SNOWFLAKE_DATABASE=SOPHIA_AI_PRODUCTION \
  --from-literal=SNOWFLAKE_WAREHOUSE=SOPHIA_AI_COMPUTE_WH_MAIN \
  --from-literal=SNOWFLAKE_SCHEMA=PAYREADY_SALESIQ \
  --from-literal=REDIS_HOST=redis-service \
  --from-literal=REDIS_PORT=6379 \
  -n sophia-ai --dry-run=client -o yaml | kubectl apply -f -

echo -e "${GREEN}✅ Namespace and secrets created${NC}"

# Phase 4: Deploy Monitoring Stack (Because We're Not Flying Blind)
echo -e "\n${BLUE}PHASE 4: MONITORING STACK${NC}"
echo -e "${YELLOW}Installing Prometheus & Grafana...${NC}"

helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm install prometheus prometheus-community/kube-prometheus-stack \
  -n monitoring --create-namespace \
  --set grafana.adminPassword='sophia-admin-2025' \
  --set prometheus.prometheusSpec.serviceMonitorSelectorNilUsesHelmValues=false

echo -e "${GREEN}✅ Monitoring stack deployed${NC}"

# Phase 5: Build Docker Images (The Fun Part)
echo -e "\n${BLUE}PHASE 5: DOCKER BUILDS${NC}"
echo -e "${YELLOW}This would normally build and push images...${NC}"
echo -e "${YELLOW}Run these commands from your local sophia-main directory:${NC}"

cat << 'EOF'
# Backend
cd backend
docker build -f Dockerfile.backend -t $DOCKER_REGISTRY/sophia-backend:latest .
docker push $DOCKER_REGISTRY/sophia-backend:latest

# MCP Servers (repeat for each)
cd mcp-servers/ai_memory
docker build -t $DOCKER_REGISTRY/mcp-ai-memory:latest .
docker push $DOCKER_REGISTRY/mcp-ai-memory:latest
EOF

# Phase 6: Deploy to K3s
echo -e "\n${BLUE}PHASE 6: DEPLOYMENT${NC}"
echo -e "${YELLOW}Creating K8s manifests...${NC}"

# Create manifests directory
mkdir -p k8s-deployment

# Backend deployment manifest
cat > k8s-deployment/backend.yaml << 'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: sophia-backend
  namespace: sophia-ai
spec:
  replicas: 1
  selector:
    matchLabels:
      app: sophia-backend
  template:
    metadata:
      labels:
        app: sophia-backend
    spec:
      containers:
      - name: backend
        image: scoobyjava15/sophia-backend:latest
        ports:
        - containerPort: 8001
        envFrom:
        - secretRef:
            name: sophia-secrets
        livenessProbe:
          httpGet:
            path: /health
            port: 8001
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8001
          initialDelaySeconds: 10
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: sophia-backend
  namespace: sophia-ai
spec:
  selector:
    app: sophia-backend
  ports:
  - port: 8001
    targetPort: 8001
    name: http
EOF

# Redis deployment
cat > k8s-deployment/redis.yaml << 'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis
  namespace: sophia-ai
spec:
  replicas: 1
  selector:
    matchLabels:
      app: redis
  template:
    metadata:
      labels:
        app: redis
    spec:
      containers:
      - name: redis
        image: redis:7-alpine
        ports:
        - containerPort: 6379
---
apiVersion: v1
kind: Service
metadata:
  name: redis-service
  namespace: sophia-ai
spec:
  selector:
    app: redis
  ports:
  - port: 6379
    targetPort: 6379
EOF

# Ingress for backend
cat > k8s-deployment/ingress.yaml << 'EOF'
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: sophia-ingress
  namespace: sophia-ai
  annotations:
    traefik.ingress.kubernetes.io/router.entrypoints: websecure
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  rules:
  - host: api.sophia-intel.ai
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: sophia-backend
            port:
              number: 8001
  tls:
  - hosts:
    - api.sophia-intel.ai
    secretName: sophia-tls
EOF

echo -e "${GREEN}✅ Manifests created${NC}"

# Deploy everything
echo -e "${YELLOW}Deploying to K3s...${NC}"
kubectl apply -f k8s-deployment/

# Wait for deployments
kubectl rollout status deployment/sophia-backend -n sophia-ai
kubectl rollout status deployment/redis -n sophia-ai

echo -e "\n${GREEN}================================================${NC}"
echo -e "${GREEN}🎉 DEPLOYMENT COMPLETE!${NC}"
echo -e "${GREEN}================================================${NC}"
echo -e "\n${YELLOW}Next Steps:${NC}"
echo -e "1. Build and push Docker images (see Phase 5 commands)"
echo -e "2. Update DNS: Point api.sophia-intel.ai to $MCP_SERVER"
echo -e "3. Deploy frontend to Vercel with VITE_API_URL=https://api.sophia-intel.ai"
echo -e "4. Test with: curl https://api.sophia-intel.ai/health"
echo -e "\n${BLUE}Grafana Dashboard:${NC} http://$MCP_SERVER:30080 (admin/sophia-admin-2025)"
echo -e "${BLUE}K8s Dashboard:${NC} kubectl proxy then http://localhost:8001/api/v1/namespaces/kubernetes-dashboard/services/https:kubernetes-dashboard:/proxy/"
echo -e "\n${YELLOW}If this breaks, remember: ${NC}"
echo -e "${RED}\"If this deployment fails, at least Sophia can orchestrate your funeral playlist via Slack integration\"${NC}" 