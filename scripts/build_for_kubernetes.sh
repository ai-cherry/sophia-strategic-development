#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DOCKER_REGISTRY="${DOCKER_REGISTRY:-scoobyjava15}"
IMAGE_TAG="${IMAGE_TAG:-latest}"

echo -e "${BLUE}🚀 Building Sophia AI images for Kubernetes deployment${NC}"
echo -e "${BLUE}Registry: ${DOCKER_REGISTRY}${NC}"
echo -e "${BLUE}Tag: ${IMAGE_TAG}${NC}"

# Build backend image
echo -e "${YELLOW}Building backend image...${NC}"
docker build -f Dockerfile.production -t ${DOCKER_REGISTRY}/sophia-backend:${IMAGE_TAG} .
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Backend image built successfully${NC}"
    docker push ${DOCKER_REGISTRY}/sophia-backend:${IMAGE_TAG}
else
    echo -e "${RED}❌ Backend image build failed${NC}"
    exit 1
fi

# Build frontend image
echo -e "${YELLOW}Building frontend image...${NC}"
if [ -f "frontend/Dockerfile" ]; then
    docker build -f frontend/Dockerfile -t ${DOCKER_REGISTRY}/sophia-frontend:${IMAGE_TAG} frontend/
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Frontend image built successfully${NC}"
        docker push ${DOCKER_REGISTRY}/sophia-frontend:${IMAGE_TAG}
    else
        echo -e "${RED}❌ Frontend image build failed${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}⚠️  Frontend Dockerfile not found, skipping...${NC}"
fi

# Build MCP servers
echo -e "${YELLOW}Building MCP server images...${NC}"
MCP_SERVERS=(
    "ai-memory"
    "gong"
    "snowflake"
    "slack"
    "linear"
    "github"
    "codacy"
    "asana"
)

for server in "${MCP_SERVERS[@]}"; do
    if [ -d "mcp-servers/${server}" ]; then
        echo -e "${YELLOW}Building MCP server: ${server}...${NC}"
        docker build -t ${DOCKER_REGISTRY}/sophia-mcp-${server}:${IMAGE_TAG} mcp-servers/${server}/
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ MCP ${server} built successfully${NC}"
            docker push ${DOCKER_REGISTRY}/sophia-mcp-${server}:${IMAGE_TAG}
        else
            echo -e "${RED}❌ MCP ${server} build failed${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  MCP server directory mcp-servers/${server} not found, skipping...${NC}"
    fi
done

echo -e "${GREEN}🎉 Build process completed!${NC}" 