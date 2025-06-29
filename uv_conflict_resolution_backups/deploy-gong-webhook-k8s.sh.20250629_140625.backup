#!/bin/bash

# Deploy Gong Webhook Service to Kubernetes
# This script deploys the Gong webhook service with proper secret injection from Pulumi ESC

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
NAMESPACE="sophia-ai"
SERVICE_NAME="gong-webhook-service"
DOCKER_IMAGE="sophia-ai/gong-webhook-service"
VERSION="${VERSION:-latest}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check if kubectl is installed
    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl is not installed. Please install kubectl first."
        exit 1
    fi
    
    # Check if docker is installed
    if ! command -v docker &> /dev/null; then
        log_error "docker is not installed. Please install docker first."
        exit 1
    fi
    
    # Check if pulumi is installed
    if ! command -v pulumi &> /dev/null; then
        log_error "pulumi is not installed. Please install pulumi first."
        exit 1
    fi
    
    # Check kubectl connection
    if ! kubectl cluster-info &> /dev/null; then
        log_error "Cannot connect to Kubernetes cluster. Please check your kubeconfig."
        exit 1
    fi
    
    log_success "Prerequisites check passed"
}

# Build Docker image
build_docker_image() {
    log_info "Building Docker image: ${DOCKER_IMAGE}:${VERSION}"
    
    cd "${PROJECT_ROOT}"
    
    # Build the image using the new Dockerfile
    docker build -f Dockerfile.gong-webhook -t "${DOCKER_IMAGE}:${VERSION}" .
    
    # Tag as latest if not already latest
    if [ "${VERSION}" != "latest" ]; then
        docker tag "${DOCKER_IMAGE}:${VERSION}" "${DOCKER_IMAGE}:latest"
    fi
    
    log_success "Docker image built successfully"
}

# Push Docker image (optional - for production)
push_docker_image() {
    if [ "${PUSH_IMAGE:-false}" = "true" ]; then
        log_info "Pushing Docker image to registry..."
        docker push "${DOCKER_IMAGE}:${VERSION}"
        if [ "${VERSION}" != "latest" ]; then
            docker push "${DOCKER_IMAGE}:latest"
        fi
        log_success "Docker image pushed successfully"
    else
        log_info "Skipping image push (set PUSH_IMAGE=true to enable)"
    fi
}

# Load secrets from Pulumi ESC
load_secrets() {
    log_info "Loading secrets from Pulumi ESC..."
    
    # Check if ESC environment is available
    if ! pulumi env get scoobyjava-org/default/sophia-ai-production &> /dev/null; then
        log_error "Pulumi ESC environment not accessible. Please check your Pulumi configuration."
        exit 1
    fi
    
    # Export ESC environment variables
    eval "$(pulumi env get scoobyjava-org/default/sophia-ai-production --format shell)"
    
    log_success "Secrets loaded from Pulumi ESC"
}

# Create namespace if it doesn't exist
create_namespace() {
    log_info "Creating namespace ${NAMESPACE} if it doesn't exist..."
    
    kubectl create namespace "${NAMESPACE}" --dry-run=client -o yaml | kubectl apply -f -
    
    log_success "Namespace ${NAMESPACE} ready"
}

# Apply Kubernetes secret with ESC values
apply_secrets() {
    log_info "Applying Kubernetes secrets..."
    
    # Create secret with actual values from ESC
    kubectl create secret generic gong-webhook-secrets \
        --namespace="${NAMESPACE}" \
        --from-literal=GONG_API_KEY="${GONG_ACCESS_KEY}" \
        --from-literal=GONG_WEBHOOK_SECRETS="${GONG_CLIENT_SECRET}" \
        --from-literal=SNOWFLAKE_ACCOUNT="${SNOWFLAKE_ACCOUNT}" \
        --from-literal=SNOWFLAKE_USER="${SNOWFLAKE_USER}" \
        --from-literal=SNOWFLAKE_PASSWORD="${SNOWFLAKE_PASSWORD}" \
        --dry-run=client -o yaml | kubectl apply -f -
    
    # Add ESC annotations
    kubectl annotate secret gong-webhook-secrets \
        --namespace="${NAMESPACE}" \
        --overwrite \
        pulumi.com/esc-managed="true" \
        pulumi.com/esc-environment="sophia-ai-production"
    
    log_success "Kubernetes secrets applied"
}

# Deploy Kubernetes manifests
deploy_manifests() {
    log_info "Deploying Kubernetes manifests..."
    
    # Apply the main manifest
    kubectl apply -f "${PROJECT_ROOT}/infrastructure/kubernetes/manifests/gong-webhook-service.yaml"
    
    # Update the deployment image
    kubectl set image deployment/${SERVICE_NAME} \
        --namespace="${NAMESPACE}" \
        gong-webhook="${DOCKER_IMAGE}:${VERSION}"
    
    log_success "Kubernetes manifests deployed"
}

# Wait for deployment to be ready
wait_for_deployment() {
    log_info "Waiting for deployment to be ready..."
    
    kubectl rollout status deployment/${SERVICE_NAME} \
        --namespace="${NAMESPACE}" \
        --timeout=300s
    
    log_success "Deployment is ready"
}

# Verify deployment
verify_deployment() {
    log_info "Verifying deployment..."
    
    # Check pod status
    kubectl get pods -l app=${SERVICE_NAME} --namespace="${NAMESPACE}"
    
    # Check service
    kubectl get service ${SERVICE_NAME} --namespace="${NAMESPACE}"
    
    # Check ingress
    kubectl get ingress gong-webhook-ingress --namespace="${NAMESPACE}"
    
    # Test health endpoint
    log_info "Testing health endpoint..."
    if kubectl port-forward service/${SERVICE_NAME} 8080:80 --namespace="${NAMESPACE}" &
    then
        PORT_FORWARD_PID=$!
        sleep 5
        
        if curl -f http://localhost:8080/health &> /dev/null; then
            log_success "Health check passed"
        else
            log_warning "Health check failed - service may still be starting up"
        fi
        
        kill $PORT_FORWARD_PID &> /dev/null || true
    fi
    
    log_success "Deployment verification completed"
}

# Show deployment information
show_deployment_info() {
    log_info "Deployment Information:"
    echo "=========================="
    echo "Service: ${SERVICE_NAME}"
    echo "Namespace: ${NAMESPACE}"
    echo "Image: ${DOCKER_IMAGE}:${VERSION}"
    echo "External URL: https://gong-webhook.sophia-ai.com"
    echo ""
    echo "Useful commands:"
    echo "  View pods: kubectl get pods -l app=${SERVICE_NAME} -n ${NAMESPACE}"
    echo "  View logs: kubectl logs -l app=${SERVICE_NAME} -n ${NAMESPACE} -f"
    echo "  Scale: kubectl scale deployment ${SERVICE_NAME} --replicas=5 -n ${NAMESPACE}"
    echo "  Delete: kubectl delete -f ${PROJECT_ROOT}/infrastructure/kubernetes/manifests/gong-webhook-service.yaml"
}

# Cleanup on error
cleanup() {
    if [ $? -ne 0 ]; then
        log_error "Deployment failed. Cleaning up..."
        kubectl delete deployment ${SERVICE_NAME} --namespace="${NAMESPACE}" --ignore-not-found=true
        kubectl delete service ${SERVICE_NAME} --namespace="${NAMESPACE}" --ignore-not-found=true
    fi
}

# Main deployment function
main() {
    log_info "Starting Gong Webhook Service deployment..."
    
    # Set up error handling
    trap cleanup EXIT
    
    # Run deployment steps
    check_prerequisites
    load_secrets
    build_docker_image
    push_docker_image
    create_namespace
    apply_secrets
    deploy_manifests
    wait_for_deployment
    verify_deployment
    show_deployment_info
    
    log_success "Gong Webhook Service deployment completed successfully!"
}

# Handle command line arguments
case "${1:-deploy}" in
    "deploy")
        main
        ;;
    "build")
        check_prerequisites
        build_docker_image
        ;;
    "secrets")
        load_secrets
        apply_secrets
        ;;
    "verify")
        verify_deployment
        ;;
    "clean")
        log_info "Cleaning up Gong Webhook Service..."
        kubectl delete -f "${PROJECT_ROOT}/infrastructure/kubernetes/manifests/gong-webhook-service.yaml" --ignore-not-found=true
        log_success "Cleanup completed"
        ;;
    *)
        echo "Usage: $0 {deploy|build|secrets|verify|clean}"
        echo ""
        echo "Commands:"
        echo "  deploy  - Full deployment (default)"
        echo "  build   - Build Docker image only"
        echo "  secrets - Load and apply secrets only"
        echo "  verify  - Verify existing deployment"
        echo "  clean   - Remove all resources"
        echo ""
        echo "Environment variables:"
        echo "  VERSION     - Docker image version (default: latest)"
        echo "  PUSH_IMAGE  - Push image to registry (default: false)"
        exit 1
        ;;
esac 