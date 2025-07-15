#!/bin/bash
# 🚀 Sophia AI Production Deployment Script

set -euo pipefail

echo "🚀 Sophia AI Production Deployment"
echo "=================================="

# Verify environment
if [[ "${GITHUB_ACTIONS:-false}" != "true" ]]; then
    echo "❌ This script should only run in GitHub Actions"
    exit 1
fi

# Environment setup
export PULUMI_ORG="scoobyjava-org"
export PULUMI_STACK="sophia-ai-production"
export ENVIRONMENT="production"
export SOPHIA_VERSION="${SOPHIA_VERSION:-3.4.0}"

echo "📋 Configuration:"
echo "  Organization: $PULUMI_ORG"
echo "  Stack: $PULUMI_STACK"
echo "  Environment: $ENVIRONMENT"
echo "  Version: $SOPHIA_VERSION"

# Verify required secrets
echo "🔑 Verifying secrets..."
required_secrets=(
    "PULUMI_ACCESS_TOKEN"
    "OPENAI_API_KEY"
    "ANTHROPIC_API_KEY"
    "QDRANT_API_KEY"
    "LAMBDA_API_KEY"
    "DOCKER_USER_NAME"
    "DOCKER_PERSONAL_ACCESS_TOKEN"
)

for secret in "${required_secrets[@]}"; do
    if [[ -z "${!secret:-}" ]]; then
        echo "❌ Missing required secret: $secret"
        exit 1
    fi
    echo "✅ $secret: Available"
done

# Deploy with full ESC integration
echo "🏗️ Starting deployment with Pulumi ESC..."
pulumi esc env run $PULUMI_ORG/default/$PULUMI_STACK -- \
    bash -c "
    set -euo pipefail
    
    echo '🏗️ Infrastructure Deployment'
    pulumi up --yes --stack $PULUMI_STACK
    
    echo '🐳 Container Deployment'
    docker build -t scoobyjava15/sophia-ai:$SOPHIA_VERSION .
    docker push scoobyjava15/sophia-ai:$SOPHIA_VERSION
    
    echo '☸️ Kubernetes Deployment'
    kubectl apply -k k8s/overlays/production
    
    echo '⏳ Waiting for deployment to stabilize...'
    kubectl rollout status deployment/sophia-ai-backend -n sophia-ai-prod
    kubectl rollout status deployment/sophia-ai-frontend -n sophia-ai-prod
    
    echo '🧪 Health Validation'
    python scripts/validate_deployment.py --environment=production
    
    echo '📊 Deployment Metrics'
    python scripts/report_deployment_metrics.py
    
    echo '✅ Deployment Complete!'
    echo '🌐 Sophia AI is now live on Lambda Labs!'
    "

echo "🎉 Production deployment completed successfully!" 