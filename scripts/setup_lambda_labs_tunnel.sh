#!/bin/bash

# Lambda Labs SSH Tunnel Setup for Kubernetes Access
# Bypasses Lambda Labs firewall restrictions

set -e

echo "🔗 Setting up SSH tunnel for Lambda Labs Kubernetes access"
echo "======================================================="

# Configuration
LAMBDA_IP="192.222.58.232"
SSH_KEY="~/.ssh/sophia_correct_key"
LOCAL_PORT="6443"
REMOTE_PORT="6443"

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

# Step 1: Kill any existing tunnel
echo "🔄 Cleaning up existing tunnels..."
pkill -f "ssh.*$LAMBDA_IP.*6443" || true
sleep 2

# Step 2: Create SSH tunnel
echo "🚇 Creating SSH tunnel to Lambda Labs..."
ssh -i ~/.ssh/sophia_correct_key -L $LOCAL_PORT:localhost:$REMOTE_PORT -N -f ubuntu@$LAMBDA_IP

if [ $? -eq 0 ]; then
    log_info "SSH tunnel established successfully"
else
    log_error "Failed to create SSH tunnel"
    exit 1
fi

# Step 3: Update kubeconfig for tunnel access
echo "🔧 Updating kubeconfig for tunnel access..."
cp ~/.kube/config-lambda-labs ~/.kube/config-lambda-labs-tunnel

# Replace the server URL to use localhost tunnel
sed -i.bak 's|https://192.222.58.232:6443|https://localhost:6443|g' ~/.kube/config-lambda-labs-tunnel

log_info "Kubeconfig updated for tunnel access"

# Step 4: Test cluster access
echo "🧪 Testing cluster access through tunnel..."
export KUBECONFIG=~/.kube/config-lambda-labs-tunnel

if kubectl get nodes --request-timeout=10s; then
    log_info "Successfully connected to Lambda Labs K3s cluster through tunnel!"
else
    log_error "Cluster access test failed"
    exit 1
fi

# Step 5: Check GPU availability
echo "🎮 Checking GPU availability..."
kubectl get nodes -o json | jq '.items[].status.capacity."nvidia.com/gpu"' 2>/dev/null || echo "GPU info not available (jq not installed locally)"

# Step 6: Create deployment script
echo "📝 Creating deployment helper script..."
cat > deploy_to_lambda_k3s.sh << 'EOF'
#!/bin/bash

# Helper script to deploy to Lambda Labs K3s cluster

export KUBECONFIG=~/.kube/config-lambda-labs-tunnel

echo "🚀 Deploying to Lambda Labs K3s cluster..."

# Check if tunnel is active
if ! nc -z localhost 6443; then
    echo "❌ SSH tunnel not active. Run setup_lambda_labs_tunnel.sh first"
    exit 1
fi

# Deploy application
kubectl apply -f k8s/production/

# Check deployment status
kubectl get deployments -n ai-platform
kubectl get pods -n ai-platform

echo "✅ Deployment complete!"
EOF

chmod +x deploy_to_lambda_k3s.sh

# Final instructions
echo ""
echo "🎉 Lambda Labs Kubernetes Access Setup Complete!"
echo "==============================================="
echo ""
echo "✅ SSH tunnel active on port 6443"
echo "✅ Kubeconfig configured for tunnel access"
echo "✅ Cluster connectivity verified"
echo ""
echo "📋 Usage Instructions:"
echo "1. Use kubeconfig: export KUBECONFIG=~/.kube/config-lambda-labs-tunnel"
echo "2. Deploy application: ./deploy_to_lambda_k3s.sh"
echo "3. Check cluster: kubectl get nodes"
echo "4. Monitor pods: kubectl get pods -n ai-platform"
echo ""
echo "🔧 Tunnel Management:"
echo "   Check tunnel: nc -z localhost 6443"
echo "   Kill tunnel: pkill -f 'ssh.*$LAMBDA_IP.*6443'"
echo "   Restart tunnel: bash scripts/setup_lambda_labs_tunnel.sh"
echo ""
echo "⚠️  Note: Keep this terminal session open to maintain the SSH tunnel" 