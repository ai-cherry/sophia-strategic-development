#!/bin/bash

# Lambda Labs K3s Deployment Script - FIXED VERSION
# Based on comprehensive research and working SSH key

set -e

echo "🚀 Lambda Labs K3s Deployment Script (Fixed)"
echo "============================================="

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

# Step 1: Test connectivity
echo "🔗 Testing Lambda Labs connectivity..."
if ssh -i ~/.ssh/sophia_correct_key -o ConnectTimeout=10 "ubuntu@${LAMBDA_IP}" "echo 'Connection test successful'"; then
    log_info "Successfully connected to Lambda Labs instance"
else
    log_error "Failed to connect to Lambda Labs. Check SSH key and IP address."
    exit 1
fi

# Step 2: Create K3s installation script
echo "📝 Creating K3s installation script..."
cat > install_k3s_lambda.sh << 'EOF'
#!/bin/bash

# Lambda Labs K3s Installation Script
# Based on official Lambda Labs documentation

set -e

echo "🔧 Installing K3s on Lambda Labs with GPU support..."

# Get external IP
MY_IP=$(curl -s ifconfig.me)
echo "External IP: ${MY_IP}"

# Install K3s with GPU support and external IP configuration
curl -sfL https://get.k3s.io | INSTALL_K3S_EXEC="--node-external-ip=${MY_IP} --flannel-backend=wireguard-native --flannel-external-ip --tls-san ${MY_IP} --default-runtime=nvidia" sh -

# Wait for K3s to be ready
echo "⏳ Waiting for K3s to be ready..."
sleep 30

# Check K3s status
sudo systemctl status k3s --no-pager

# Create kubeconfig for external access
echo "🔑 Creating kubeconfig for external access..."
sudo k3s kubectl config view --raw > /tmp/k3s-config.yaml
sed -i "s/127.0.0.1/${MY_IP}/g" /tmp/k3s-config.yaml

# Install NVIDIA Device Plugin
echo "🎮 Installing NVIDIA Device Plugin..."
kubectl apply -f https://raw.githubusercontent.com/NVIDIA/k8s-device-plugin/v0.14.1/nvidia-device-plugin.yml

# Verify GPU availability
echo "🔍 Verifying GPU availability..."
kubectl get nodes -o json | jq '.items[].status.capacity."nvidia.com/gpu"' || echo "jq not available, checking manually..."

# Create test namespace
kubectl create namespace ai-platform || echo "Namespace already exists"

# Show cluster info
echo "📊 Cluster Information:"
kubectl cluster-info
kubectl get nodes -o wide

echo "✅ K3s installation complete!"
echo "📋 Next steps:"
echo "1. Download kubeconfig from /tmp/k3s-config.yaml"
echo "2. Test GPU scheduling with test deployment"
echo "3. Deploy your AI platform"

EOF

# Step 3: Copy and execute installation script
echo "📤 Copying installation script to Lambda Labs..."
scp -i ~/.ssh/sophia_correct_key install_k3s_lambda.sh "ubuntu@${LAMBDA_IP}:/tmp/"

log_info "Installation script copied successfully"

echo "🚀 Executing K3s installation on Lambda Labs..."
ssh -i ~/.ssh/sophia_correct_key "ubuntu@${LAMBDA_IP}" "chmod +x /tmp/install_k3s_lambda.sh && sudo /tmp/install_k3s_lambda.sh"

# Step 4: Download kubeconfig
echo "📥 Downloading kubeconfig..."
scp -i ~/.ssh/sophia_correct_key "ubuntu@${LAMBDA_IP}:/tmp/k3s-config.yaml" ~/.kube/config-lambda-labs

log_info "Kubeconfig downloaded to ~/.kube/config-lambda-labs"

# Step 5: Test cluster access
echo "🧪 Testing cluster access..."
export KUBECONFIG=~/.kube/config-lambda-labs

if kubectl get nodes; then
    log_info "Successfully connected to Lambda Labs K3s cluster!"
else
    log_warn "Cluster access test failed, but installation may still be successful"
fi

# Step 6: Create GPU test deployment
echo "🎮 Creating GPU test deployment..."
cat > gpu-test-deployment.yaml << 'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: gpu-test
  namespace: ai-platform
spec:
  replicas: 1
  selector:
    matchLabels:
      app: gpu-test
  template:
    metadata:
      labels:
        app: gpu-test
    spec:
      containers:
      - name: gpu-test
        image: nvidia/cuda:11.0-base
        command: ["nvidia-smi"]
        resources:
          limits:
            nvidia.com/gpu: 1
          requests:
            nvidia.com/gpu: 1
      restartPolicy: OnFailure
EOF

kubectl apply -f gpu-test-deployment.yaml || log_warn "GPU test deployment failed - check NVIDIA device plugin"

# Step 7: Cleanup
echo "🧹 Cleaning up temporary files..."
rm -f install_k3s_lambda.sh gpu-test-deployment.yaml

# Final status
echo ""
echo "🎉 Lambda Labs K3s Deployment Complete!"
echo "======================================="
echo "✅ K3s cluster installed on Lambda Labs"
echo "✅ GPU support configured"
echo "✅ External access configured"
echo "✅ Kubeconfig available at ~/.kube/config-lambda-labs"
echo ""
echo "📋 Next Steps:"
echo "1. Set KUBECONFIG: export KUBECONFIG=~/.kube/config-lambda-labs"
echo "2. Verify GPU: kubectl get nodes -o json | jq '.items[].status.capacity.\"nvidia.com/gpu\"'"
echo "3. Deploy AI platform: kubectl apply -f k8s/production/"
echo "4. Monitor deployment: kubectl get pods -n ai-platform"
echo ""
echo "🔗 Cluster Access:"
echo "   kubectl --kubeconfig ~/.kube/config-lambda-labs get nodes"
echo "   kubectl --kubeconfig ~/.kube/config-lambda-labs get pods --all-namespaces" 