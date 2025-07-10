#!/bin/bash
# Sophia AI K3s Deployment Script
# Generated: 2025-07-10 16:46:17

set -e

echo "🚀 Starting Sophia AI K3s deployment..."

# Configuration
K3S_SERVER="192.222.58.232"
NAMESPACE="sophia-ai-prod"

# Check if kubectl is configured
if ! kubectl cluster-info > /dev/null 2>&1; then
    echo "❌ kubectl not configured. Please set up kubeconfig first."
    exit 1
fi

# Create namespace if it doesn't exist
echo "📦 Creating namespace..."
kubectl apply -f kubernetes/base/namespace.yaml

# Apply base configuration
echo "🔧 Applying base configuration..."
kubectl apply -k kubernetes/base

# Wait for deployments to be ready
echo "⏳ Waiting for deployments to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment --all -n $NAMESPACE

# Check deployment status
echo "✅ Deployment status:"
kubectl get all -n $NAMESPACE

echo "🎉 Deployment complete!"
