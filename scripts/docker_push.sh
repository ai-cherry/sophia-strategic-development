#!/bin/bash

# Docker Push Script for Sophia AI
# This script handles Docker login and image push to Docker Hub

set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Docker Hub configuration
DOCKERHUB_USERNAME="scoobyjava15"
DOCKER_REGISTRY="docker.io"

# Image configuration
IMAGE_NAME="sophia-backend"
IMAGE_TAG="${IMAGE_TAG:-latest}"
FULL_IMAGE_NAME="${DOCKERHUB_USERNAME}/${IMAGE_NAME}:${IMAGE_TAG}"

echo -e "${YELLOW}🐳 Docker Push Script for Sophia AI${NC}"
echo "========================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running. Please start Docker Desktop.${NC}"
    exit 1
fi

# Login to Docker Hub using the token from environment or stdin
if [ -z "$DOCKER_TOKEN" ]; then
    echo -e "${YELLOW}Please enter your Docker Personal Access Token:${NC}"
    read -s DOCKER_TOKEN
    echo
fi

echo -e "${YELLOW}📝 Logging into Docker Hub...${NC}"
echo "$DOCKER_TOKEN" | docker login -u "$DOCKERHUB_USERNAME" --password-stdin

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Successfully logged into Docker Hub${NC}"
else
    echo -e "${RED}❌ Failed to login to Docker Hub${NC}"
    exit 1
fi

# Check if the image exists locally
if docker images | grep -q "${DOCKERHUB_USERNAME}/${IMAGE_NAME}"; then
    echo -e "${GREEN}✅ Found image: ${FULL_IMAGE_NAME}${NC}"
else
    echo -e "${RED}❌ Image not found: ${FULL_IMAGE_NAME}${NC}"
    echo -e "${YELLOW}💡 Please build the image first using: docker build -t ${FULL_IMAGE_NAME} -f Dockerfile.simple .${NC}"
    exit 1
fi

# Push the image
echo -e "${YELLOW}🚀 Pushing image to Docker Hub...${NC}"
docker push "${FULL_IMAGE_NAME}"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Successfully pushed ${FULL_IMAGE_NAME} to Docker Hub${NC}"
    echo -e "${GREEN}🎉 Image is now available at: https://hub.docker.com/r/${DOCKERHUB_USERNAME}/${IMAGE_NAME}${NC}"
else
    echo -e "${RED}❌ Failed to push image to Docker Hub${NC}"
    exit 1
fi

# Logout for security
docker logout
echo -e "${GREEN}✅ Logged out from Docker Hub${NC}"

echo
echo -e "${GREEN}🎯 Next steps:${NC}"
echo "1. Pull the image on Lambda Labs: docker pull ${FULL_IMAGE_NAME}"
echo "2. Run the container: docker run -p 8000:8000 ${FULL_IMAGE_NAME}"
echo "3. Access the API at: http://localhost:8000"
