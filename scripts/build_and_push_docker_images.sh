#!/bin/bash
# Build and push all Docker images for Sophia AI unified deployment
# This script implements the Docker image compilation from PR #179

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DOCKER_REGISTRY="${DOCKER_REGISTRY:-scoobyjava15}"
IMAGE_TAG="${IMAGE_TAG:-latest}"
BUILD_PARALLEL="${BUILD_PARALLEL:-4}"

# Function to print colored output
print_status() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

print_error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1"
}

print_info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO:${NC} $1"
}

# Docker login
docker_login() {
    print_info "Logging in to Docker Hub..."
    if docker login -u "$DOCKER_REGISTRY"; then
        print_status "✅ Docker Hub login successful"
    else
        print_error "❌ Docker Hub login failed"
        exit 1
    fi
}

# Build and push image function
build_and_push() {
    local service_name=$1
    local dockerfile=$2
    local context_dir=$3
    local build_args="${4:-}"
    
    local image_name="${DOCKER_REGISTRY}/${service_name}:${IMAGE_TAG}"
    
    print_info "Building $service_name..."
    
    # Build command
    local build_cmd="docker build -f $dockerfile -t $image_name"
    
    # Add build args if provided
    if [ -n "$build_args" ]; then
        build_cmd="$build_cmd $build_args"
    fi
    
    # Add context
    build_cmd="$build_cmd $context_dir"
    
    # Execute build
    if eval "$build_cmd"; then
        print_status "✅ Built $service_name"
        
        # Push image
        if docker push "$image_name"; then
            print_status "✅ Pushed $service_name to registry"
            return 0
        else
            print_error "❌ Failed to push $service_name"
            return 1
        fi
    else
        print_error "❌ Failed to build $service_name"
        return 1
    fi
}

# Build core platform services
build_core_services() {
    print_info "===================================================="
    print_info "Building Core Platform Services"
    print_info "===================================================="
    
    # Main backend
    build_and_push "sophia-ai" "Dockerfile" "." \
        "--build-arg ENVIRONMENT=prod --build-arg PULUMI_ORG=scoobyjava-org"
    
    # Unified chat service
    build_and_push "sophia-ai-unified-chat" "docker/Dockerfile.unified-chat" "." \
        "--build-arg ENVIRONMENT=prod"
    
    # Dashboard
    build_and_push "sophia-ai-dashboard" "frontend/Dockerfile" "frontend" \
        "--build-arg NODE_ENV=production"
    
    # MCP Gateway
    build_and_push "sophia-mcp-gateway" "mcp-gateway/Dockerfile" "mcp-gateway"
}

# Build AI/ML services
build_ai_services() {
    print_info "===================================================="
    print_info "Building AI/ML Services"
    print_info "===================================================="
    
    # AI Memory V2
    build_and_push "sophia-ai-memory-v2" "mcp-servers/ai-memory/Dockerfile" "mcp-servers/ai-memory"
    
    # Snowflake Cortex
    build_and_push "sophia-snowflake-cortex" "mcp-servers/snowflake_cortex/Dockerfile" "mcp-servers/snowflake_cortex"
    
    # Mem0 OpenMemory
    build_and_push "sophia-mem0-openmemory" "mcp-servers/mem0/Dockerfile" "mcp-servers/mem0"
    
    # HuggingFace AI
    build_and_push "sophia-huggingface-ai" "mcp-servers/huggingface/Dockerfile" "mcp-servers/huggingface"
    
    # Portkey Admin
    build_and_push "sophia-portkey-admin" "mcp-servers/portkey_admin/Dockerfile" "mcp-servers/portkey_admin"
    
    # Gong V2
    build_and_push "sophia-gong-v2" "mcp-servers/gong/Dockerfile" "mcp-servers/gong"
}

# Build MCP orchestrator services
build_mcp_services() {
    print_info "===================================================="
    print_info "Building MCP Orchestrator Services"
    print_info "===================================================="
    
    local mcp_services=(
        "github-v2:github"
        "slack-v2:slack"
        "linear-v2:linear"
        "notion-v2:notion"
        "codacy-v2:codacy"
        "asana-v2:asana"
        "hubspot:hubspot"
        "playwright:playwright"
        "lambda-labs-cli:lambda_labs_cli"
        "ui-ux-agent:ui_ux_agent"
        "v0dev:v0dev"
        "figma-context:figma_context"
    )
    
    for service in "${mcp_services[@]}"; do
        IFS=':' read -r image_name dir_name <<< "$service"
        build_and_push "sophia-$image_name" "mcp-servers/$dir_name/Dockerfile" "mcp-servers/$dir_name"
    done
}

# Build data pipeline services
build_data_services() {
    print_info "===================================================="
    print_info "Building Data Pipeline Services"
    print_info "===================================================="
    
    # Snowflake services
    build_and_push "sophia-snowflake-v2" "mcp-servers/snowflake/Dockerfile" "mcp-servers/snowflake"
    build_and_push "sophia-snowflake-unified" "mcp-servers/snowflake_unified/Dockerfile" "mcp-servers/snowflake_unified"
    
    # Gong Webhook
    build_and_push "sophia-gong-webhook" "gong-webhook-service/Dockerfile" "gong-webhook-service"
    
    # Estuary Flow
    build_and_push "sophia-estuary-flow" "mcp-servers/estuary_flow/Dockerfile" "mcp-servers/estuary_flow"
}

# Build development services
build_dev_services() {
    print_info "===================================================="
    print_info "Building Development Services"
    print_info "===================================================="
    
    # Codacy
    build_and_push "sophia-codacy" "mcp-servers/codacy/Dockerfile" "mcp-servers/codacy"
    
    # Performance Monitor
    build_and_push "sophia-performance-monitor" "infrastructure/monitoring/Dockerfile.performance" "infrastructure/monitoring"
    
    # Health Aggregator
    build_and_push "sophia-health-aggregator" "infrastructure/monitoring/Dockerfile.health" "infrastructure/monitoring"
    
    # Secret services
    build_and_push "sophia-secret-rotator" "infrastructure/security/Dockerfile.rotator" "infrastructure/security"
    build_and_push "sophia-secret-health-checker" "infrastructure/security/Dockerfile.checker" "infrastructure/security"
}

# Main execution
main() {
    print_info "===================================================="
    print_info "SOPHIA AI DOCKER IMAGE BUILD & PUSH"
    print_info "===================================================="
    print_info "Registry: $DOCKER_REGISTRY"
    print_info "Tag: $IMAGE_TAG"
    print_info "===================================================="
    
    # Docker login
    docker_login
    
    # Track failures
    local failed_builds=()
    
    # Build all service categories
    if ! build_core_services; then
        failed_builds+=("core-services")
    fi
    
    if ! build_ai_services; then
        failed_builds+=("ai-services")
    fi
    
    if ! build_mcp_services; then
        failed_builds+=("mcp-services")
    fi
    
    if ! build_data_services; then
        failed_builds+=("data-services")
    fi
    
    if ! build_dev_services; then
        failed_builds+=("dev-services")
    fi
    
    # Summary
    print_info "===================================================="
    print_info "BUILD SUMMARY"
    print_info "===================================================="
    
    if [ ${#failed_builds[@]} -eq 0 ]; then
        print_status "🎉 ALL IMAGES BUILT AND PUSHED SUCCESSFULLY!"
        print_info "Total images: 57"
        print_info "Registry: $DOCKER_REGISTRY"
        print_info "Tag: $IMAGE_TAG"
    else
        print_error "❌ SOME BUILDS FAILED:"
        for category in "${failed_builds[@]}"; do
            print_error "  • $category"
        done
        exit 1
    fi
}

# Check if running from project root
if [ ! -f "docker-compose.cloud.unified.yml" ]; then
    print_error "This script must be run from the project root directory"
    exit 1
fi

# Execute main function
main "$@" 