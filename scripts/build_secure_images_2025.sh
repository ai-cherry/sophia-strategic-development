#!/bin/bash
# Build secure Docker images with 2025 best practices
# Includes BuildKit, security scanning, and multi-platform support

set -euo pipefail

# Configuration
DOCKER_REGISTRY="${DOCKER_REGISTRY:-scoobyjava15}"
IMAGE_TAG="${IMAGE_TAG:-latest}"
PLATFORMS="${PLATFORMS:-linux/amd64}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Building Sophia AI Docker Images - 2025 Edition${NC}"
echo -e "${BLUE}Registry: ${DOCKER_REGISTRY}${NC}"
echo -e "${BLUE}Tag: ${IMAGE_TAG}${NC}"
echo -e "${BLUE}Platforms: ${PLATFORMS}${NC}"

# Enable BuildKit
export DOCKER_BUILDKIT=1
export BUILDKIT_PROGRESS=plain

# Function to build and scan image
build_and_scan() {
    local service=$1
    local dockerfile=$2
    local context=$3
    
    echo -e "${YELLOW}Building ${service}...${NC}"
    
    # Build with multi-platform support
    docker buildx build \
        --platform ${PLATFORMS} \
        --build-arg BUILDKIT_INLINE_CACHE=1 \
        --cache-from type=registry,ref=${DOCKER_REGISTRY}/${service}:buildcache \
        --cache-to type=registry,ref=${DOCKER_REGISTRY}/${service}:buildcache,mode=max \
        --load \
        -t ${DOCKER_REGISTRY}/${service}:${IMAGE_TAG} \
        -t ${DOCKER_REGISTRY}/${service}:latest \
        -f ${dockerfile} \
        ${context}
    
    echo -e "${YELLOW}Running security scan for ${service}...${NC}"
    
    # Security scan with Trivy
    docker run --rm \
        -v /var/run/docker.sock:/var/run/docker.sock \
        -v ${HOME}/.cache/trivy:/root/.cache/trivy \
        aquasec/trivy:latest image \
        --severity HIGH,CRITICAL \
        --format table \
        ${DOCKER_REGISTRY}/${service}:${IMAGE_TAG}
    
    # Check if scan passed
    if docker run --rm \
        -v /var/run/docker.sock:/var/run/docker.sock \
        -v ${HOME}/.cache/trivy:/root/.cache/trivy \
        aquasec/trivy:latest image \
        --severity CRITICAL \
        --exit-code 1 \
        --quiet \
        ${DOCKER_REGISTRY}/${service}:${IMAGE_TAG} 2>/dev/null; then
        echo -e "${GREEN}✅ Security scan passed for ${service}${NC}"
    else
        echo -e "${RED}❌ Critical vulnerabilities found in ${service}${NC}"
        echo -e "${RED}Fix vulnerabilities before pushing to registry${NC}"
        exit 1
    fi
}

# Create buildx builder if it doesn't exist
if ! docker buildx ls | grep -q multiarch-builder; then
    echo -e "${YELLOW}Creating buildx builder...${NC}"
    docker buildx create --name multiarch-builder --driver docker-container --use
    docker buildx inspect --bootstrap
fi

# Build backend image
build_and_scan "sophia-backend" "Dockerfile.production.2025" "."

# Build frontend image
if [ -f "frontend/Dockerfile.2025" ]; then
    build_and_scan "sophia-frontend" "frontend/Dockerfile.2025" "./frontend"
else
    build_and_scan "sophia-frontend" "frontend/Dockerfile" "./frontend"
fi

# Build GPU-optimized images if Dockerfiles exist
if [ -f "Dockerfile.ai-core.2025" ]; then
    build_and_scan "sophia-ai-core" "Dockerfile.ai-core.2025" "."
fi

if [ -f "Dockerfile.data-pipeline.2025" ]; then
    build_and_scan "sophia-data-pipeline" "Dockerfile.data-pipeline.2025" "."
fi

echo -e "${GREEN}✅ All images built and scanned successfully!${NC}"
echo -e "${YELLOW}To push images to registry, run:${NC}"
echo -e "${BLUE}docker push ${DOCKER_REGISTRY}/sophia-backend:${IMAGE_TAG}${NC}"
echo -e "${BLUE}docker push ${DOCKER_REGISTRY}/sophia-frontend:${IMAGE_TAG}${NC}" 