# 🚀 PR #179 IMPLEMENTATION GUIDE: DOCKER IMAGE COMPILATION FOR CLOUD DEPLOYMENT

## 📋 Overview

This guide provides the complete implementation plan for **PR #179: Compile docker images for cloud deployment**. It consolidates the fragmented Docker build processes into a unified system aligned with the 5 Lambda Labs GPU instances.

**PR Status**: Ready for implementation  
**Estimated Time**: 2 weeks for full implementation  
**Impact**: Transforms 57 scattered Docker images into a unified, optimized build pipeline  

---

## 🎯 IMPLEMENTATION ROADMAP

### **Phase 1: Immediate Actions (Day 1-2)**

#### **1.1 Archive Legacy Build Scripts**
```bash
# Create archive structure
mkdir -p archive/docker-builds-legacy/
mkdir -p archive/deployment-scripts-legacy/
mkdir -p archive/docker-compose-legacy/

# Archive old Docker build scripts
mv unified_build_images.sh archive/docker-builds-legacy/
mv unified_docker_hub_push.sh archive/docker-builds-legacy/
mv scripts/build_sophia_images.sh archive/docker-builds-legacy/ 2>/dev/null || true
mv scripts/docker_build_and_push.sh archive/docker-builds-legacy/ 2>/dev/null || true

# Archive redundant deployment scripts
mv scripts/deploy_sophia_final.sh archive/deployment-scripts-legacy/
mv scripts/deploy_sophia_complete.py archive/deployment-scripts-legacy/
mv scripts/deploy_to_lambda.sh archive/deployment-scripts-legacy/

# Archive old Docker Compose files
mv docker-compose.enhanced.yml archive/docker-compose-legacy/
mv docker-compose.mcp-v2.yml archive/docker-compose-legacy/
mv docker-compose.override.yml archive/docker-compose-legacy/
```

#### **1.2 Create New Directory Structure**
```bash
# Create unified deployment structure
mkdir -p deployment/docker/build-scripts/
mkdir -p deployment/docker/dockerfiles/
mkdir -p deployment/docker/configs/
mkdir -p deployment/compose-files/

# Create instance-specific directories
mkdir -p deployment/instances/production/
mkdir -p deployment/instances/ai-core/
mkdir -p deployment/instances/mcp-orchestrator/
mkdir -p deployment/instances/data-pipeline/
mkdir -p deployment/instances/development/
```

### **Phase 2: Docker Image Standardization (Day 3-5)**

#### **2.1 Create Base Dockerfiles**

**Standard Service Dockerfile** (`deployment/docker/dockerfiles/Dockerfile.base`):
```dockerfile
# Base image for standard Python services
FROM python:3.12-slim AS base

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Production stage
FROM base AS production
COPY . .
RUN python -m compileall .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**GPU-Optimized Dockerfile** (`deployment/docker/dockerfiles/Dockerfile.gpu`):
```dockerfile
# GPU-optimized image for AI services
FROM nvidia/cuda:12.2.0-runtime-ubuntu22.04 AS gpu-base

# Install Python and dependencies
RUN apt-get update && apt-get install -y \
    python3.12 \
    python3.12-pip \
    python3.12-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install GPU-optimized Python packages
COPY requirements-gpu.txt .
RUN python3.12 -m pip install --no-cache-dir -r requirements-gpu.txt

# Production stage
FROM gpu-base AS production
COPY . .

# GPU environment variables
ENV CUDA_VISIBLE_DEVICES=0
ENV TF_FORCE_GPU_ALLOW_GROWTH=true
ENV PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000
CMD ["python3.12", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### **2.2 Create Unified Build Script**

**Master Build Script** (`deployment/docker/build-all.sh`):
```bash
#!/bin/bash
# Unified Docker build script for Sophia AI

set -euo pipefail

# Configuration
REGISTRY="${DOCKER_REGISTRY:-scoobyjava15}"
TAG="${IMAGE_TAG:-latest}"
BUILD_DATE=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
GIT_COMMIT=$(git rev-parse --short HEAD)

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() { echo -e "${GREEN}[$(date +'%H:%M:%S')]${NC} $1"; }
print_error() { echo -e "${RED}[$(date +'%H:%M:%S')] ERROR:${NC} $1"; }
print_warning() { echo -e "${YELLOW}[$(date +'%H:%M:%S')] WARNING:${NC} $1"; }

# Build functions
build_core_images() {
    print_status "Building core platform images..."
    
    # Backend API
    docker buildx build \
        --platform linux/amd64 \
        --build-arg BUILD_DATE=$BUILD_DATE \
        --build-arg GIT_COMMIT=$GIT_COMMIT \
        --tag $REGISTRY/sophia-ai:$TAG \
        --tag $REGISTRY/sophia-ai:$GIT_COMMIT \
        --push \
        -f Dockerfile.production .
    
    # Unified Chat
    docker buildx build \
        --platform linux/amd64 \
        --tag $REGISTRY/sophia-ai-unified-chat:$TAG \
        --push \
        -f deployment/docker/dockerfiles/Dockerfile.chat .
    
    # Dashboard
    docker buildx build \
        --platform linux/amd64 \
        --tag $REGISTRY/sophia-ai-dashboard:$TAG \
        --push \
        -f frontend/Dockerfile frontend/
    
    # MCP Gateway
    docker buildx build \
        --platform linux/amd64 \
        --tag $REGISTRY/sophia-mcp-gateway:$TAG \
        --push \
        -f deployment/docker/dockerfiles/Dockerfile.gateway .
}

build_ai_images() {
    print_status "Building AI/ML images for GH200..."
    
    local ai_services=(
        "ai-memory-v2"
        "ai-cortex"
        "mem0"
        "snowflake-cortex"
        "huggingface-ai"
        "perplexity-v2"
        "gong-v2"
    )
    
    for service in "${ai_services[@]}"; do
        if [ -d "infrastructure/mcp_servers/${service//-/_}" ]; then
            docker buildx build \
                --platform linux/amd64 \
                --build-arg CUDA_VERSION=12.2.0 \
                --build-arg OPTIMIZE_FOR=gh200 \
                --tag $REGISTRY/sophia-$service:$TAG \
                --push \
                -f infrastructure/mcp_servers/${service//-/_}/Dockerfile \
                infrastructure/mcp_servers/${service//-/_}/
        fi
    done
}

build_mcp_images() {
    print_status "Building MCP server images..."
    
    local mcp_servers=(
        "github-v2"
        "slack-v2"
        "linear-v2"
        "notion-v2"
        "codacy-v2"
        "asana-v2"
        "hubspot"
        "salesforce"
    )
    
    for server in "${mcp_servers[@]}"; do
        if [ -d "infrastructure/mcp_servers/${server//-/_}" ]; then
            docker buildx build \
                --platform linux/amd64 \
                --tag $REGISTRY/sophia-$server:$TAG \
                --push \
                -f infrastructure/mcp_servers/${server//-/_}/Dockerfile \
                infrastructure/mcp_servers/${server//-/_}/
        fi
    done
}

# Main execution
main() {
    print_status "Starting Sophia AI Docker build process..."
    print_status "Registry: $REGISTRY"
    print_status "Tag: $TAG"
    
    # Set up Docker Buildx
    docker buildx create --use --name sophia-builder || true
    
    # Build all image categories
    build_core_images
    build_ai_images
    build_mcp_images
    
    print_status "✅ All images built and pushed successfully!"
}

main "$@"
```

### **Phase 3: Instance-Specific Deployment (Day 6-8)**

#### **3.1 Production Instance Configuration**

**Docker Compose** (`deployment/instances/production/docker-compose.yml`):
```yaml
version: '3.8'

x-default-logging: &default-logging
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"

services:
  sophia-backend:
    image: ${DOCKER_REGISTRY:-scoobyjava15}/sophia-ai:${TAG:-latest}
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=prod
      - INSTANCE_TYPE=production
      - GPU_TYPE=rtx6000
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '3'
          memory: 8G
    logging: *default-logging

  sophia-unified-chat:
    image: ${DOCKER_REGISTRY:-scoobyjava15}/sophia-ai-unified-chat:${TAG:-latest}
    ports:
      - "8001:8001"
    environment:
      - BACKEND_URL=http://sophia-backend:8000
      - WEBSOCKET_ENABLED=true
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '2'
          memory: 4G
    logging: *default-logging

  sophia-dashboard:
    image: ${DOCKER_REGISTRY:-scoobyjava15}/sophia-ai-dashboard:${TAG:-latest}
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://sophia-backend:8000
      - REACT_APP_CHAT_URL=http://sophia-unified-chat:8001
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '2'
          memory: 4G
    logging: *default-logging
```

#### **3.2 Deployment Script Integration**

Update the existing `scripts/deploy_sophia_unified.sh` to use new Docker images:
```bash
# Add to deploy_instance function
print_info "Pulling latest Docker images..."
ssh -i "$SSH_KEY" ubuntu@$ip "
    cd /opt/sophia-ai
    
    # Pull all required images
    docker pull $DOCKER_REGISTRY/sophia-ai:$IMAGE_TAG
    docker pull $DOCKER_REGISTRY/sophia-ai-unified-chat:$IMAGE_TAG
    docker pull $DOCKER_REGISTRY/sophia-ai-dashboard:$IMAGE_TAG
    docker pull $DOCKER_REGISTRY/sophia-mcp-gateway:$IMAGE_TAG
    
    # Deploy with new images
    docker stack deploy -c docker-compose.yml sophia-$instance_name --with-registry-auth
"
```

### **Phase 4: CI/CD Integration (Day 9-10)**

#### **4.1 GitHub Actions Workflow**

Create `.github/workflows/docker-build-deploy.yml`:
```yaml
name: 🐳 Docker Build & Deploy to Lambda Labs

on:
  workflow_dispatch:
    inputs:
      target_instance:
        description: 'Target Lambda Labs instance'
        required: true
        type: choice
        options:
          - all
          - production
          - ai-core
          - mcp-orchestrator
          - data-pipeline
          - development
      build_images:
        description: 'Build new images'
        type: boolean
        default: true

env:
  DOCKER_REGISTRY: scoobyjava15
  IMAGE_TAG: ${{ github.sha }}

jobs:
  build-images:
    name: 🏗️ Build Docker Images
    runs-on: ubuntu-latest
    if: inputs.build_images
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3
        
      - name: Login to Docker Hub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}
          
      - name: Build and push images
        run: |
          chmod +x deployment/docker/build-all.sh
          ./deployment/docker/build-all.sh
          
  deploy:
    name: 🚀 Deploy to Lambda Labs
    needs: build-images
    runs-on: ubuntu-latest
    if: always() && (needs.build-images.result == 'success' || !inputs.build_images)
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup SSH
        run: |
          mkdir -p ~/.ssh
          echo "${{ secrets.LAMBDA_PRIVATE_SSH_KEY }}" > ~/.ssh/sophia2025.pem
          chmod 600 ~/.ssh/sophia2025.pem
          
      - name: Deploy to ${{ inputs.target_instance }}
        run: |
          chmod +x scripts/deploy_sophia_unified.sh
          ./scripts/deploy_sophia_unified.sh deploy ${{ inputs.target_instance }}
```

### **Phase 5: Validation & Monitoring (Day 11-14)**

#### **5.1 Image Validation Script**

Create `scripts/validate_docker_images.sh`:
```bash
#!/bin/bash
# Validate all Docker images are built and accessible

REGISTRY="scoobyjava15"
REQUIRED_IMAGES=(
    "sophia-ai"
    "sophia-ai-unified-chat"
    "sophia-ai-dashboard"
    "sophia-mcp-gateway"
    "sophia-ai-memory-v2"
    "sophia-github-v2"
    "sophia-slack-v2"
)

for image in "${REQUIRED_IMAGES[@]}"; do
    if docker pull $REGISTRY/$image:latest > /dev/null 2>&1; then
        echo "✅ $image:latest - Available"
    else
        echo "❌ $image:latest - Missing"
    fi
done
```

#### **5.2 Deployment Health Check**

Create `scripts/check_deployment_health.sh`:
```bash
#!/bin/bash
# Check health of deployed services across all instances

INSTANCES=(
    "104.171.202.103:production"
    "192.222.58.232:ai-core"
    "104.171.202.117:mcp-orchestrator"
    "104.171.202.134:data-pipeline"
    "155.248.194.183:development"
)

for instance in "${INSTANCES[@]}"; do
    IP=$(echo $instance | cut -d: -f1)
    NAME=$(echo $instance | cut -d: -f2)
    
    echo "Checking $NAME ($IP)..."
    
    ssh -i ~/.ssh/sophia2025.pem ubuntu@$IP "
        docker stack services sophia-$NAME --format 'table {{.Name}}\t{{.Replicas}}\t{{.Image}}'
    "
done
```

---

## 📊 DEPLOYMENT MATRIX

| **Instance** | **Services** | **Docker Images** | **Resource Allocation** |
|-------------|--------------|-------------------|------------------------|
| **Production (RTX6000)** | Backend, Chat, Dashboard, Gateway | 4 core images | 8GB RAM, 3 CPU per service |
| **AI Core (GH200)** | AI Memory, Cortex, ML Services | 8 GPU-optimized images | 32GB RAM, GPU acceleration |
| **MCP Hub (A6000)** | GitHub, Slack, Linear, etc. | 15 MCP images | 4GB RAM per service |
| **Data Pipeline (A100)** | Snowflake, ETL, Analytics | 10 data images | 8GB RAM, tensor cores |
| **Development (A10)** | All services (testing) | All images | 2GB RAM per service |

---

## 🚀 DEPLOYMENT COMMANDS

### **Build All Images**
```bash
cd deployment/docker
./build-all.sh
```

### **Deploy to Specific Instance**
```bash
./scripts/deploy_sophia_unified.sh deploy production
./scripts/deploy_sophia_unified.sh deploy ai-core
./scripts/deploy_sophia_unified.sh deploy mcp-orchestrator
./scripts/deploy_sophia_unified.sh deploy data-pipeline
./scripts/deploy_sophia_unified.sh deploy development
```

### **Deploy to All Instances**
```bash
./scripts/deploy_sophia_unified.sh deploy all
```

### **Check Deployment Status**
```bash
./scripts/deploy_sophia_unified.sh status
```

---

## ✅ SUCCESS CRITERIA

### **Build Success**
- [ ] All 57 Docker images build successfully
- [ ] Images are pushed to Docker Hub
- [ ] Build time < 10 minutes
- [ ] Image sizes optimized (< 500MB standard, < 2GB GPU)

### **Deployment Success**
- [ ] All services running on correct instances
- [ ] Health checks passing
- [ ] Inter-instance communication working
- [ ] GPU acceleration verified on AI instances

### **Performance Metrics**
- [ ] Service startup < 30 seconds
- [ ] Memory usage < 80% allocated
- [ ] GPU utilization > 70% on AI workloads
- [ ] Network latency < 10ms between instances

---

## 🔐 SECURITY CHECKLIST

- [ ] All images run as non-root user
- [ ] Secrets managed through Docker secrets
- [ ] Images scanned for vulnerabilities
- [ ] Network policies implemented
- [ ] SSL/TLS configured for all services

---

## 📋 FINAL CHECKLIST

### **Week 1**
- [ ] Archive legacy scripts
- [ ] Create new directory structure
- [ ] Implement base Dockerfiles
- [ ] Build core images
- [ ] Test on development instance

### **Week 2**
- [ ] Build all MCP server images
- [ ] Implement CI/CD workflow
- [ ] Deploy to all instances
- [ ] Validate deployments
- [ ] Document procedures

---

This implementation guide provides a complete roadmap for PR #179, transforming the fragmented Docker build process into a unified, efficient system optimized for your Lambda Labs deployment architecture. 