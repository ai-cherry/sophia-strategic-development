#!/bin/bash
set -e

echo "🚀 Deploying to Primary Production Server (192.222.58.232)"

# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker if not present
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
fi

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install K3s
curl -sfL https://get.k3s.io | sh -

# Install cert-manager for SSL
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Wait for cert-manager
kubectl wait --for=condition=Ready pods --all -n cert-manager --timeout=300s

# Create namespace
kubectl create namespace sophia-ai-prod --dry-run=client -o yaml | kubectl apply -f -

# Check for required files
if [ ! -d "k8s/production" ]; then
    echo "❌ Error: Directory k8s/production not found!"
    exit 1
fi

if [ ! -f "k8s/production/sophia-deployment.yaml" ]; then
    echo "❌ Error: Required file k8s/production/sophia-deployment.yaml not found!"
    exit 1
fi

# Deploy Sophia AI
kubectl apply -f k8s/production/sophia-deployment.yaml

# Check deployment status
kubectl get pods -n sophia-ai-prod
kubectl get services -n sophia-ai-prod
kubectl get ingress -n sophia-ai-prod

echo "✅ Primary server deployment complete!"
echo "🌐 Access: https://sophia-intel.ai"