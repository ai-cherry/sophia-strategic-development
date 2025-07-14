#!/bin/bash
# Strategic Integration Docker Deployment

echo "🚀 Building and deploying strategic integration components..."

# Build Docker images
docker build -t scoobyjava15/sophia-enhanced-router:latest -f Dockerfile.router .
docker build -t scoobyjava15/sophia-adaptive-dashboard:latest -f Dockerfile.dashboard .
docker build -t scoobyjava15/sophia-unified-mcp:latest -f Dockerfile.mcp .

# Push to Docker Hub
docker push scoobyjava15/sophia-enhanced-router:latest
docker push scoobyjava15/sophia-adaptive-dashboard:latest  
docker push scoobyjava15/sophia-unified-mcp:latest

# Deploy to Lambda Labs
kubectl apply -f k8s/strategic-integration.yaml

echo "✅ Strategic integration deployment complete!"
