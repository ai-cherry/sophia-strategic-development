#!/bin/bash
set -euo pipefail

STACK_NAME="sophia-ai"
DOCKER_REGISTRY="scoobyjava15"

echo "📦 Building and pushing backend image..."
docker build -f Dockerfile.production -t $DOCKER_REGISTRY/sophia-backend:latest .
docker push $DOCKER_REGISTRY/sophia-backend:latest

echo "🌐 Deploying stack with Docker Swarm..."
docker stack deploy -c docker-compose.cloud.yml $STACK_NAME

echo "✅ Stack deployed. Check services with: docker stack ps $STACK_NAME"
