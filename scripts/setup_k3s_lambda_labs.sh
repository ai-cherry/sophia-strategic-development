#!/bin/bash
# 🚀 SETUP K3S ON LAMBDA LABS INSTANCE
# Establishes K3s cluster on sophia-ai-core (192.222.58.232)

set -euo pipefail

# Configuration
LAMBDA_K3S_IP="192.222.58.232"
SSH_KEY_PATH="$HOME/.ssh/sophia2025_private_key"
LOCAL_KUBECONFIG="$HOME/.kube/k3s-lambda-labs"
SSH_USER="ubuntu"

echo "🚀 Setting up K3s cluster on Lambda Labs"
echo "Target: $LAMBDA_K3S_IP (sophia-ai-core)"
echo ""

# Function to run commands on the remote instance
run_remote() {
    ssh -o StrictHostKeyChecking=no -i "$SSH_KEY_PATH" "$SSH_USER@$LAMBDA_K3S_IP" "$1"
}

# Function to run commands with sudo
run_remote_sudo() {
    ssh -o StrictHostKeyChecking=no -i "$SSH_KEY_PATH" "$SSH_USER@$LAMBDA_K3S_IP" "sudo $1"
}

# Step 1: Test SSH connectivity
echo "📋 Step 1: Testing SSH connectivity..."
if run_remote "echo 'SSH connection successful'"; then
    echo "✅ SSH connection to $LAMBDA_K3S_IP established"
else
    echo "❌ Cannot SSH to $LAMBDA_K3S_IP"
    echo "💡 Make sure SSH key is correct and instance is accessible"
    exit 1
fi

# Step 2: Check if K3s is already installed
echo -e "\n📋 Step 2: Checking K3s installation..."
    if run_remote "which k3s &>/dev/null"; then
    echo "✅ K3s is already installed"
    K3S_STATUS=$(run_remote_sudo "systemctl is-active k3s" || echo "inactive")
    echo "K3s service status: $K3S_STATUS"
    
    if [ "$K3S_STATUS" != "active" ]; then
        echo "🔧 Starting K3s service..."
        run_remote_sudo "systemctl start k3s"
        run_remote_sudo "systemctl enable k3s"
    fi
else
    echo "🔧 Installing K3s..."
    # Install K3s with external access enabled
    run_remote "curl -sfL https://get.k3s.io | INSTALL_K3S_EXEC='--bind-address=0.0.0.0 --node-external-ip=$LAMBDA_K3S_IP --tls-san=$LAMBDA_K3S_IP' sh -s -"
    
    echo "⏳ Waiting for K3s to start..."
    sleep 30
fi

# Step 3: Verify K3s is running
echo -e "\n📋 Step 3: Verifying K3s cluster..."
if run_remote_sudo "kubectl get nodes"; then
    echo "✅ K3s cluster is running"
else
    echo "❌ K3s cluster not responding"
    exit 1
fi

# Step 4: Copy kubeconfig
echo -e "\n📋 Step 4: Setting up local kubeconfig..."
mkdir -p $(dirname "$LOCAL_KUBECONFIG")

# Get the kubeconfig and modify it for external access
run_remote_sudo "cat /etc/rancher/k3s/k3s.yaml" | \
    sed "s/127.0.0.1/$LAMBDA_K3S_IP/g" | \
    sed "s/localhost/$LAMBDA_K3S_IP/g" > "$LOCAL_KUBECONFIG"

chmod 600 "$LOCAL_KUBECONFIG"
echo "✅ Kubeconfig saved to $LOCAL_KUBECONFIG"

# Step 5: Test local kubectl access
echo -e "\n📋 Step 5: Testing local kubectl access..."
export KUBECONFIG="$LOCAL_KUBECONFIG"
if kubectl cluster-info; then
    echo "✅ Local kubectl access working"
    kubectl get nodes -o wide
else
    echo "❌ Local kubectl access failed"
    echo "This might be due to firewall restrictions on port 6443"
    echo "You may need to use SSH tunneling for access"
fi

# Step 6: Setup SSH tunnel option
echo -e "\n📋 Step 6: Setting up SSH tunnel option..."
TUNNEL_KUBECONFIG="$HOME/.kube/k3s-lambda-labs-tunnel"

# Create a tunnel-based kubeconfig
run_remote_sudo "cat /etc/rancher/k3s/k3s.yaml" | \
    sed "s/127.0.0.1/localhost/g" > "$TUNNEL_KUBECONFIG"

chmod 600 "$TUNNEL_KUBECONFIG"
echo "✅ Tunnel kubeconfig saved to $TUNNEL_KUBECONFIG"

echo -e "\n🎉 K3s setup complete!"
echo "=========================="
echo "Direct access kubeconfig: $LOCAL_KUBECONFIG"
echo "Tunnel access kubeconfig: $TUNNEL_KUBECONFIG"
echo ""
echo "To use direct access:"
echo "  export KUBECONFIG='$LOCAL_KUBECONFIG'"
echo "  kubectl get nodes"
echo ""
echo "To use SSH tunnel access:"
echo "  # Terminal 1: Create tunnel"
echo "  ssh -L 6443:localhost:6443 -N -i $SSH_KEY_PATH $SSH_USER@$LAMBDA_K3S_IP"
echo "  # Terminal 2: Use kubectl"
echo "  export KUBECONFIG='$TUNNEL_KUBECONFIG'"
echo "  kubectl get nodes" 