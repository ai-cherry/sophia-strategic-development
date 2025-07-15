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
