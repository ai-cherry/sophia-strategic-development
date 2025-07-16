#!/bin/bash
# 🚀 Manual Deployment Script for sophia-intel.ai SSL Fix
# Run this on the Lambda Labs primary instance (192.222.58.232)

set -e

echo "🚀 Starting sophia-intel.ai SSL/domain fix deployment..."

# Step 1: Apply the correct ingress configuration
echo "📦 Applying ingress configuration..."
kubectl apply -f k8s/production/sophia-intel-ingress-fix.yaml

# Step 2: Verify cert-manager is installed
echo "🔍 Checking cert-manager..."
if ! kubectl get namespace cert-manager &> /dev/null; then
    echo "📦 Installing cert-manager..."
    kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml
    kubectl wait --for=condition=ready pod -l app=cert-manager -n cert-manager --timeout=300s
fi

# Step 3: Verify nginx-ingress is installed  
echo "🔍 Checking nginx-ingress..."
if ! kubectl get pods -n ingress-nginx &> /dev/null; then
    echo "📦 Installing nginx-ingress..."
    kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.2/deploy/static/provider/cloud/deploy.yaml
    kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=ingress-nginx -n ingress-nginx --timeout=300s
fi

# Step 4: Wait for SSL certificate
echo "⏳ Waiting for SSL certificate provisioning..."
timeout 300 bash -c '
    while true; do
        if kubectl get certificate sophia-intel-production-cert -n sophia-ai-prod -o jsonpath="{.status.conditions[?(@.type==\"Ready\")].status}" | grep -q "True"; then
            echo "✅ SSL certificate ready!"
            break
        fi
        echo "⏳ Certificate still provisioning..."
        sleep 15
    done
'

# Step 5: Verify deployment
echo "🔍 Verifying deployment..."
echo "Checking ingress status:"
kubectl get ingress -n sophia-ai-prod

echo "Checking certificate status:"
kubectl get certificate -n sophia-ai-prod

echo "Checking backend pods:"
kubectl get pods -n sophia-ai-prod -l app=sophia-backend

# Step 6: Test endpoints
echo "🌐 Testing endpoints..."
curl -f https://api.sophia-intel.ai/health || echo "❌ API health check failed"
curl -f https://sophia-intel.ai || echo "❌ Frontend check failed"

echo "🎉 Deployment complete!"
echo "📋 Next steps:"
echo "1. Verify DNS propagation: nslookup api.sophia-intel.ai"
echo "2. Test SSL: openssl s_client -connect api.sophia-intel.ai:443"
echo "3. Check frontend: https://sophia-intel.ai"
echo "4. Verify real data: https://api.sophia-intel.ai/api/v3/dashboard/metrics"
