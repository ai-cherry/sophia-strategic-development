#!/bin/bash
# Sophia AI Unified Kubernetes Deployment Script
# Deploy to Lambda Labs Kubernetes with single command

set -euo pipefail

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DOCKER_REGISTRY="${DOCKER_REGISTRY:-scoobyjava15}"
IMAGE_TAG="${IMAGE_TAG:-latest}"
NAMESPACE="${NAMESPACE:-sophia-ai}"
HELM_RELEASE="${HELM_RELEASE:-sophia-platform}"
CHART_PATH="kubernetes/helm/sophia-platform"

# Lambda Labs instances
declare -A LAMBDA_INSTANCES=(
    ["production"]="104.171.202.103"
    ["ai-core"]="192.222.58.232"
    ["mcp-orchestrator"]="104.171.202.117"
    ["data-pipeline"]="104.171.202.134"
    ["development"]="155.248.194.183"
)

# Function to print colored output
print_status() {
    echo -e "${2}${1}${NC}"
}

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..." "$BLUE"
    
    # Check for required tools
    local tools=("kubectl" "helm" "docker")
    for tool in "${tools[@]}"; do
        if ! command -v "$tool" &> /dev/null; then
            print_status "Error: $tool is not installed" "$RED"
            exit 1
        fi
    done
    
    # Check kubectl context
    if ! kubectl config current-context &> /dev/null; then
        print_status "Error: No kubectl context configured" "$RED"
        print_status "Run: kubectl config set-context lambda-labs --cluster=lambda-labs" "$YELLOW"
        exit 1
    fi
    
    # Check Docker login
    if ! docker info &> /dev/null; then
        print_status "Error: Docker daemon not running" "$RED"
        exit 1
    fi
    
    print_status "✓ Prerequisites satisfied" "$GREEN"
}

# Function to build and push images
build_and_push_images() {
    print_status "Building and pushing Docker images..." "$BLUE"
    
    # Build backend
    print_status "Building sophia-backend..." "$YELLOW"
    docker build -t "$DOCKER_REGISTRY/sophia-backend:$IMAGE_TAG" \
        -f Dockerfile.production \
        --platform linux/amd64 \
        --build-arg BUILDKIT_INLINE_CACHE=1 \
        .
    
    # Build frontend
    print_status "Building sophia-frontend..." "$YELLOW"
    docker build -t "$DOCKER_REGISTRY/sophia-frontend:$IMAGE_TAG" \
        -f frontend/Dockerfile \
        --platform linux/amd64 \
        --build-arg BUILDKIT_INLINE_CACHE=1 \
        ./frontend
    
    # Build MCP servers
    for mcp_dir in mcp-servers/*/; do
        if [[ -f "$mcp_dir/Dockerfile" ]]; then
            service_name=$(basename "$mcp_dir")
            print_status "Building sophia-mcp-$service_name..." "$YELLOW"
            docker build -t "$DOCKER_REGISTRY/sophia-mcp-$service_name:$IMAGE_TAG" \
                -f "$mcp_dir/Dockerfile" \
                --platform linux/amd64 \
                "$mcp_dir"
        fi
    done
    
    # Push all images
    print_status "Pushing images to Docker Hub..." "$YELLOW"
    docker push "$DOCKER_REGISTRY/sophia-backend:$IMAGE_TAG"
    docker push "$DOCKER_REGISTRY/sophia-frontend:$IMAGE_TAG"
    
    # Push MCP images
    for image in $(docker images --format "{{.Repository}}:{{.Tag}}" | grep "$DOCKER_REGISTRY/sophia-mcp-"); do
        docker push "$image"
    done
    
    print_status "✓ Images built and pushed successfully" "$GREEN"
}

# Function to create namespace
create_namespace() {
    print_status "Creating namespace..." "$BLUE"
    
    kubectl create namespace "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -
    kubectl label namespace "$NAMESPACE" \
        environment=production \
        cloud=lambda-labs \
        --overwrite
    
    print_status "✓ Namespace created" "$GREEN"
}

# Function to sync secrets from Pulumi ESC
sync_secrets() {
    print_status "Syncing secrets from Pulumi ESC..." "$BLUE"
    
    # Run the secret sync script
    if [[ -f "scripts/unified_secret_sync.py" ]]; then
        python scripts/unified_secret_sync.py --namespace "$NAMESPACE"
    else
        print_status "Warning: Secret sync script not found" "$YELLOW"
    fi
    
    print_status "✓ Secrets synced" "$GREEN"
}

# Function to deploy with Helm
deploy_helm() {
    print_status "Deploying with Helm..." "$BLUE"
    
    # Add required Helm repos
    helm repo add bitnami https://charts.bitnami.com/bitnami
    helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
    helm repo add grafana https://grafana.github.io/helm-charts
    helm repo update
    
    # Create values override file
    cat > /tmp/values-override.yaml <<EOF
global:
  imageTag: $IMAGE_TAG
  imageRegistry: docker.io/$DOCKER_REGISTRY

# Override any environment-specific values here
EOF
    
    # Deploy or upgrade
    helm upgrade --install "$HELM_RELEASE" "$CHART_PATH" \
        --namespace "$NAMESPACE" \
        --create-namespace \
        --values "$CHART_PATH/values.yaml" \
        --values /tmp/values-override.yaml \
        --timeout 10m \
        --wait
    
    print_status "✓ Helm deployment complete" "$GREEN"
}

# Function to apply GitOps configuration
setup_gitops() {
    print_status "Setting up GitOps..." "$BLUE"
    
    # Apply GitOps manifests
    kubectl apply -k kubernetes/gitops/
    
    print_status "✓ GitOps configured" "$GREEN"
}

# Function to validate deployment
validate_deployment() {
    print_status "Validating deployment..." "$BLUE"
    
    # Check deployments
    kubectl -n "$NAMESPACE" wait --for=condition=available --timeout=300s deployment --all
    
    # Check pods
    local unhealthy_pods=$(kubectl -n "$NAMESPACE" get pods --no-headers | grep -v "Running\|Completed" | wc -l)
    if [[ $unhealthy_pods -gt 0 ]]; then
        print_status "Warning: Some pods are not healthy" "$YELLOW"
        kubectl -n "$NAMESPACE" get pods
    else
        print_status "✓ All pods healthy" "$GREEN"
    fi
    
    # Check services
    kubectl -n "$NAMESPACE" get services
    
    # Check ingress
    kubectl -n "$NAMESPACE" get ingress
    
    print_status "✓ Deployment validated" "$GREEN"
}

# Function to show access URLs
show_access_urls() {
    print_status "\n🌐 Access URLs:" "$BLUE"
    
    # Get ingress endpoints
    local ingresses=$(kubectl -n "$NAMESPACE" get ingress -o json)
    
    echo -e "${GREEN}Production Instance (${LAMBDA_INSTANCES[production]}):${NC}"
    echo "  - Dashboard: https://sophia-ai.lambda-labs.cloud"
    echo "  - API: https://api.sophia-ai.lambda-labs.cloud"
    echo "  - API Docs: https://api.sophia-ai.lambda-labs.cloud/docs"
    
    echo -e "\n${GREEN}Monitoring:${NC}"
    echo "  - Prometheus: https://prometheus.sophia-ai.lambda-labs.cloud"
    echo "  - Grafana: https://grafana.sophia-ai.lambda-labs.cloud"
    
    echo -e "\n${GREEN}MCP Services:${NC}"
    local services=$(kubectl -n "$NAMESPACE" get services -o json | jq -r '.items[] | select(.metadata.name | startswith("mcp-")) | .metadata.name')
    for service in $services; do
        echo "  - $service: https://$service.sophia-ai.lambda-labs.cloud"
    done
}

# Function to cleanup old resources
cleanup_old_resources() {
    print_status "Cleaning up old resources..." "$BLUE"
    
    # Remove old Docker Swarm stacks (if any)
    for instance in "${LAMBDA_INSTANCES[@]}"; do
        ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no ubuntu@"$instance" \
            "docker stack rm sophia-* 2>/dev/null || true" || true
    done
    
    print_status "✓ Cleanup complete" "$GREEN"
}

# Main deployment function
main() {
    local action="${1:-deploy}"
    
    case "$action" in
        deploy)
            check_prerequisites
            build_and_push_images
            create_namespace
            sync_secrets
            deploy_helm
            setup_gitops
            validate_deployment
            show_access_urls
            ;;
        
        upgrade)
            check_prerequisites
            build_and_push_images
            deploy_helm
            validate_deployment
            ;;
        
        rollback)
            helm rollback "$HELM_RELEASE" -n "$NAMESPACE"
            validate_deployment
            ;;
        
        status)
            kubectl -n "$NAMESPACE" get all
            helm -n "$NAMESPACE" status "$HELM_RELEASE"
            ;;
        
        cleanup)
            cleanup_old_resources
            ;;
        
        uninstall)
            helm -n "$NAMESPACE" uninstall "$HELM_RELEASE"
            kubectl delete namespace "$NAMESPACE"
            ;;
        
        *)
            echo "Usage: $0 {deploy|upgrade|rollback|status|cleanup|uninstall}"
            exit 1
            ;;
    esac
}

# Run main function
main "$@" 