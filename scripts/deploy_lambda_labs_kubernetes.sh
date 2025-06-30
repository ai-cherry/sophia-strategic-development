#!/bin/bash

# Sophia AI Lambda Labs Kubernetes Deployment Script
# Deploys GPU-optimized MCP servers and infrastructure

set -e

echo "🚀 DEPLOYING SOPHIA AI TO LAMBDA LABS KUBERNETES"
echo "=============================================="

# Configuration
NAMESPACE="sophia-ai"
HELM_CHART_PATH="infrastructure/kubernetes/helm/sophia-mcp"
VALUES_FILE="values-lambda-labs.yaml"

# Step 1: Create namespace and apply GPU resources
echo "📋 Step 1: Setting up Lambda Labs GPU resources..."
kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -
kubectl apply -f infrastructure/kubernetes/lambda-labs-gpu-resources.yaml

# Step 2: Deploy Helm chart with Lambda Labs values
echo "🚀 Step 2: Deploying MCP servers with GPU optimization..."
helm upgrade --install sophia-mcp $HELM_CHART_PATH \
  --namespace $NAMESPACE \
  --values $HELM_CHART_PATH/$VALUES_FILE \
  --set global.lambdaLabs.enabled=true \
  --set global.gpu.enabled=true \
  --set global.environment=production \
  --wait --timeout=600s

# Step 3: Deploy Clean Architecture API
echo "🏗️ Step 3: Deploying Clean Architecture API..."
kubectl apply -f infrastructure/kubernetes/clean-architecture/sophia-api-deployment.yaml

# Step 4: Verify GPU allocation
echo "🔍 Step 4: Verifying GPU allocation..."
echo "Checking GPU nodes:"
kubectl get nodes -o custom-columns=NAME:.metadata.name,GPU:.status.allocatable."nvidia\.com/gpu"

echo "Checking pod GPU allocation:"
kubectl get pods -n $NAMESPACE -o custom-columns=NAME:.metadata.name,GPU_REQUESTS:.spec.containers[*].resources.requests."nvidia\.com/gpu",GPU_LIMITS:.spec.containers[*].resources.limits."nvidia\.com/gpu"

# Step 5: Test GPU availability
echo "🧪 Step 5: Testing GPU availability..."
echo "Waiting for pods to be ready..."
kubectl wait --for=condition=ready pod -l app=sophia-mcp-ai-memory -n $NAMESPACE --timeout=300s

echo "Testing GPU access in AI Memory pod:"
POD_NAME=$(kubectl get pods -n $NAMESPACE -l app=sophia-mcp-ai-memory -o jsonpath='{.items[0].metadata.name}')
kubectl exec -it $POD_NAME -n $NAMESPACE -- nvidia-smi || echo "⚠️ nvidia-smi not available, checking Python GPU access..."
kubectl exec -it $POD_NAME -n $NAMESPACE -- python3 -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}'); print(f'GPU count: {torch.cuda.device_count()}')" || echo "⚠️ PyTorch GPU test failed"

# Step 6: Monitor deployment
echo "📊 Step 6: Deployment monitoring..."
echo "Pod status:"
kubectl get pods -n $NAMESPACE -o wide

echo "Service status:"
kubectl get services -n $NAMESPACE

echo "GPU resource usage:"
kubectl top nodes --selector=lambdalabs.com/gpu-type=rtx-4090 || echo "⚠️ Metrics server not available"

echo ""
echo "✅ LAMBDA LABS DEPLOYMENT COMPLETE!"
echo "=============================================="
echo "🎯 Next steps:"
echo "   1. Monitor GPU utilization: kubectl top nodes"
echo "   2. Check MCP server logs: kubectl logs -f deployment/sophia-mcp-ai-memory -n $NAMESPACE"
echo "   3. Test API endpoints: kubectl port-forward service/sophia-api-service 8000:80 -n $NAMESPACE"
echo "   4. View GPU metrics: kubectl port-forward service/nvidia-dcgm-exporter 9400:9400 -n $NAMESPACE"
