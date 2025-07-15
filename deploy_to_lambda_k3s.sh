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
