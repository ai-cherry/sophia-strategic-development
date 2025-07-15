#!/bin/bash

# Lambda Labs K3s Deployment Script
# Based on official Lambda Labs documentation and web research

set -e

echo "🚀 Lambda Labs K3s Deployment Script"
echo "===================================="

# Configuration
LAMBDA_IP="192.222.58.232"
SSH_KEY="~/.ssh/sophia_correct_key"
DOCKER_REGISTRY="scoobyjava15"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warn() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Step 1: Install K3s on Lambda Labs
echo "🔧 Installing K3s on Lambda Labs..."

# Create K3s installation script
cat > install_k3s.sh << 'EOF'
#!/bin/bash

# Based on Lambda Labs official documentation
# https://docs.lambdalabs.com/education/large-language-models/k8s-ollama-llama-3-2/

echo "🔧 Installing K3s with GPU support..."

# Install K3s with GPU runtime support
curl -sfL https://get.k3s.io | K3S_KUBECONFIG_MODE=644 sh -s - --default-runtime=nvidia

# Wait for K3s to be ready
echo "⏳ Waiting for K3s to be ready..."
sleep 30

# Verify installation
echo "🔍 Verifying K3s installation..."
sudo k3s kubectl get nodes

# Install socat for port forwarding
sudo apt -y install socat

# Check GPU detection
echo "🎯 Checking GPU detection..."
sudo k3s kubectl describe nodes | grep nvidia.com || echo "GPU operator not yet installed"

echo "✅ K3s installation completed!"
EOF

# Copy and execute installation script
echo "📤 Copying installation script to Lambda Labs..."
scp -i ~/.ssh/sophia_correct_key install_k3s.sh ubuntu@${LAMBDA_IP}:~/

echo "🎯 Executing K3s installation on Lambda Labs..."
ssh -i ~/.ssh/sophia_correct_key ubuntu@${LAMBDA_IP} "chmod +x ~/install_k3s.sh && ~/install_k3s.sh"

# Step 2: Install NVIDIA GPU Operator
echo "🎮 Installing NVIDIA GPU Operator..."

cat > install_gpu_operator.sh << 'EOF'
#!/bin/bash

echo "🎮 Installing NVIDIA GPU Operator..."

# Install NVIDIA GPU Operator based on Lambda Labs docs
cat <<GPUEOF | sudo k3s kubectl apply -f -
apiVersion: v1
kind: Namespace
metadata:
  name: gpu-operator
---
apiVersion: helm.cattle.io/v1
kind: HelmChart
metadata:
  name: gpu-operator
  namespace: gpu-operator
spec:
  repo: https://helm.ngc.nvidia.com/nvidia
  chart: gpu-operator
  targetNamespace: gpu-operator
GPUEOF

echo "⏳ Waiting for GPU Operator to be ready..."
sleep 60

# Verify GPU detection
echo "🔍 Verifying GPU detection..."
sudo k3s kubectl describe nodes | grep nvidia.com

echo "✅ GPU Operator installation completed!"
EOF

scp -i ~/.ssh/sophia_correct_key install_gpu_operator.sh ubuntu@${LAMBDA_IP}:~/
ssh -i ~/.ssh/sophia_correct_key ubuntu@${LAMBDA_IP} "chmod +x ~/install_gpu_operator.sh && ~/install_gpu_operator.sh"

# Step 3: Get kubeconfig for local access
echo "🔐 Setting up local kubeconfig..."

# Get kubeconfig from Lambda Labs
ssh -i ~/.ssh/sophia_correct_key ubuntu@${LAMBDA_IP} "sudo cat /etc/rancher/k3s/k3s.yaml" > k3s-config.yaml

# Replace localhost with Lambda Labs IP
sed -i.bak "s/127.0.0.1/${LAMBDA_IP}/g" k3s-config.yaml

# Create .kube directory if it doesn't exist
mkdir -p ~/.kube

# Backup existing config if it exists
if [ -f ~/.kube/config ]; then
    cp ~/.kube/config ~/.kube/config.backup.$(date +%Y%m%d_%H%M%S)
fi

# Install new config
cp k3s-config.yaml ~/.kube/config

log_info "Kubeconfig installed to ~/.kube/config"

# Step 4: Test kubectl connectivity
echo "🧪 Testing kubectl connectivity..."

if kubectl cluster-info > /dev/null 2>&1; then
    log_info "kubectl connectivity successful!"
    kubectl get nodes
else
    log_error "kubectl connectivity failed"
    echo "🔧 Troubleshooting steps:"
    echo "1. Check if Lambda Labs instance is running"
    echo "2. Verify SSH connectivity: ssh -i ~/.ssh/sophia_correct_key ubuntu@${LAMBDA_IP}"
    echo "3. Check K3s status: sudo systemctl status k3s"
fi

# Step 5: Deploy Sophia AI to K3s
echo "🚀 Deploying Sophia AI to K3s..."

cat > deploy_sophia_k3s.yaml << 'EOF'
apiVersion: v1
kind: Namespace
metadata:
  name: sophia-ai
---
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
      - name: sophia-backend
        image: scoobyjava15/sophia-ai-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: ENVIRONMENT
          value: "prod"
        - name: PULUMI_ORG
          value: "scoobyjava-org"
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
            nvidia.com/gpu: "1"
---
apiVersion: v1
kind: Service
metadata:
  name: sophia-backend-service
  namespace: sophia-ai
spec:
  selector:
    app: sophia-backend
  ports:
  - port: 8000
    targetPort: 8000
  type: LoadBalancer
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres
  namespace: sophia-ai
spec:
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:16-alpine
        ports:
        - containerPort: 5432
        env:
        - name: POSTGRES_DB
          value: "sophia"
        - name: POSTGRES_USER
          value: "sophia"
        - name: POSTGRES_PASSWORD
          value: "sophia123"
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
---
apiVersion: v1
kind: Service
metadata:
  name: postgres-service
  namespace: sophia-ai
spec:
  selector:
    app: postgres
  ports:
  - port: 5432
    targetPort: 5432
  type: ClusterIP
---
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
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
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
  type: ClusterIP
EOF

# Apply the deployment
if kubectl apply -f deploy_sophia_k3s.yaml; then
    log_info "Sophia AI deployment applied successfully!"
else
    log_error "Failed to apply Sophia AI deployment"
fi

# Step 6: Monitor deployment
echo "📊 Monitoring deployment status..."

echo "⏳ Waiting for pods to be ready..."
kubectl wait --for=condition=ready pod -l app=postgres -n sophia-ai --timeout=300s
kubectl wait --for=condition=ready pod -l app=redis -n sophia-ai --timeout=300s
kubectl wait --for=condition=ready pod -l app=sophia-backend -n sophia-ai --timeout=300s

# Get deployment status
echo "📋 Deployment Status:"
kubectl get pods -n sophia-ai
kubectl get services -n sophia-ai

# Get external IP
EXTERNAL_IP=$(kubectl get service sophia-backend-service -n sophia-ai -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
if [ -n "$EXTERNAL_IP" ]; then
    log_info "Sophia AI is accessible at: http://${EXTERNAL_IP}:8000"
    log_info "API Documentation: http://${EXTERNAL_IP}:8000/docs"
else
    log_warn "External IP not yet assigned. Check with: kubectl get services -n sophia-ai"
fi

# Step 7: Create monitoring script
cat > monitor_k3s.sh << 'EOF'
#!/bin/bash

echo "📊 Sophia AI K3s Monitoring Dashboard"
echo "===================================="

echo "🔍 Cluster Status:"
kubectl get nodes

echo ""
echo "📦 Pod Status:"
kubectl get pods -n sophia-ai

echo ""
echo "🌐 Service Status:"
kubectl get services -n sophia-ai

echo ""
echo "🎯 GPU Usage:"
kubectl describe nodes | grep -A 10 "nvidia.com/gpu"

echo ""
echo "📈 Resource Usage:"
kubectl top nodes 2>/dev/null || echo "Metrics server not installed"
kubectl top pods -n sophia-ai 2>/dev/null || echo "Metrics server not installed"

echo ""
echo "🔗 Access URLs:"
EXTERNAL_IP=$(kubectl get service sophia-backend-service -n sophia-ai -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
if [ -n "$EXTERNAL_IP" ]; then
    echo "Backend: http://${EXTERNAL_IP}:8000"
    echo "API Docs: http://${EXTERNAL_IP}:8000/docs"
else
    echo "External IP not yet assigned"
fi
EOF

chmod +x monitor_k3s.sh

# Cleanup
rm -f install_k3s.sh install_gpu_operator.sh k3s-config.yaml k3s-config.yaml.bak

echo ""
echo "🎉 Lambda Labs K3s Deployment Complete!"
echo "========================================"
echo ""
echo "📋 Summary:"
echo "✅ K3s installed on Lambda Labs with GPU support"
echo "✅ NVIDIA GPU Operator installed"
echo "✅ kubectl configured for local access"
echo "✅ Sophia AI deployed to K3s cluster"
echo ""
echo "🔧 Management Commands:"
echo "• Monitor cluster: ./monitor_k3s.sh"
echo "• Check pods: kubectl get pods -n sophia-ai"
echo "• Check services: kubectl get services -n sophia-ai"
echo "• View logs: kubectl logs -f deployment/sophia-backend -n sophia-ai"
echo ""
echo "🌐 Access:"
echo "• SSH to cluster: ssh -i ~/.ssh/sophia_correct_key ubuntu@${LAMBDA_IP}"
echo "• Local kubectl: kubectl cluster-info"
echo ""
echo "🚨 Troubleshooting:"
echo "• If pods fail to start, check: kubectl describe pod <pod-name> -n sophia-ai"
echo "• If external IP not assigned, check LoadBalancer: kubectl get services -n sophia-ai"
echo "• For GPU issues, check: kubectl describe nodes | grep nvidia" 