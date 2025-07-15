#!/bin/bash

# Lambda Labs K3s Installation Script
# Based on official Lambda Labs documentation

set -e

echo "🔧 Installing K3s on Lambda Labs with GPU support..."

# Get external IP
MY_IP=$(curl -s ifconfig.me)
echo "External IP: $MY_IP"

# Install K3s with GPU support and external IP configuration
curl -sfL https://get.k3s.io | INSTALL_K3S_EXEC="--node-external-ip=$MY_IP --flannel-backend=wireguard-native --flannel-external-ip --tls-san $MY_IP --default-runtime=nvidia" sh -

# Wait for K3s to be ready
echo "⏳ Waiting for K3s to be ready..."
sleep 30

# Check K3s status
sudo systemctl status k3s --no-pager

# Create kubeconfig for external access
echo "🔑 Creating kubeconfig for external access..."
sudo k3s kubectl config view --raw > /tmp/k3s-config.yaml
sed -i "s/127.0.0.1/$MY_IP/g" /tmp/k3s-config.yaml

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

