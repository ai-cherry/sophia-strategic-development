#!/bin/bash
# K3s installation script for Lambda Labs
# 🚨 ONE-TIME SCRIPT - DELETE AFTER USE

echo "🚀 Installing K3s on Lambda Labs..."

# Install K3s
curl -sfL https://get.k3s.io | sh -s - \
  --write-kubeconfig-mode 644 \
  --disable traefik \
  --node-label sophia-ai=true

# Wait for K3s to be ready
echo "⏳ Waiting for K3s to be ready..."
sleep 30

# Create namespaces
kubectl create namespace sophia-ai-prod
kubectl create namespace mcp-servers
kubectl create namespace monitoring
kubectl create namespace ingress

# Install GPU operator for Lambda Labs GPUs
kubectl apply -f https://raw.githubusercontent.com/NVIDIA/gpu-operator/master/deployments/gpu-operator/gpu-operator.yaml

# Label nodes for GPU workloads
kubectl label nodes --all sophia-ai/gpu=true

echo "✅ K3s installation complete!"

# Export kubeconfig
echo ""
echo "To access the cluster, run:"
echo "export KUBECONFIG=/etc/rancher/k3s/k3s.yaml"

echo ""
echo "🧹 CLEANUP REMINDER: This is a one-time setup script"
echo "   Delete with: rm $0" 