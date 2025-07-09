# 🚀 SOPHIA AI DOCKER DEPLOYMENT PLAN - PR #179 IMPLEMENTATION

## 📋 Executive Summary

This plan addresses **PR #179: Compile docker images for cloud deployment** by creating a comprehensive Docker image build and deployment strategy across the 5 Lambda Labs GPU instances. The plan consolidates fragmented Docker build processes into a unified, efficient system aligned with the holistic deployment architecture.

**Current State**: 57 Docker images scattered across multiple build scripts and workflows  
**Target State**: Unified Docker image build pipeline with instance-specific optimization  
**Implementation**: Phased approach with automated CI/CD integration  

---

## 🏗️ DOCKER IMAGE ARCHITECTURE

### **Lambda Labs Instance Mapping**

| **Instance** | **GPU** | **IP Address** | **Docker Images** | **Build Priority** |
|-------------|---------|----------------|-------------------|-------------------|
| **sophia-production-instance** | RTX6000 | `104.171.202.103` | 8 core images | **P1 - Critical** |
| **sophia-ai-core** | GH200 | `192.222.58.232` | 12 AI/ML images | **P1 - Critical** |
| **sophia-mcp-orchestrator** | A6000 | `104.171.202.117` | 18 MCP images | **P2 - High** |
| **sophia-data-pipeline** | A100 | `104.171.202.134` | 12 data images | **P2 - High** |
| **sophia-development** | A10 | `155.248.194.183` | 15 dev images | **P3 - Medium** |

---

## 📦 DOCKER IMAGE INVENTORY

### **1. Core Platform Images (Production Instance)**
```yaml
# Priority 1 - Build First
scoobyjava15/sophia-ai:latest                    # Backend API
scoobyjava15/sophia-ai-unified-chat:latest       # WebSocket Chat
scoobyjava15/sophia-ai-dashboard:latest          # React Dashboard
scoobyjava15/sophia-mcp-gateway:latest           # MCP Gateway

# Infrastructure (Use Official Images)
traefik:v3.0                                     # Load Balancer
nginx:alpine                                     # Web Server
redis:7-alpine                                   # Cache
postgres:16-alpine                               # Database
```

### **2. AI/ML Images (AI Core Instance)**
```yaml
# Priority 1 - GPU Optimized Builds
scoobyjava15/sophia-ai-memory-v2:latest          # AI Memory Service
scoobyjava15/sophia-ai-cortex:latest             # Snowflake Cortex
scoobyjava15/sophia-ai-mem0:latest               # Mem0 OpenMemory
scoobyjava15/sophia-snowflake-cortex:latest      # Enhanced Cortex

# Priority 2 - AI Services
scoobyjava15/sophia-perplexity-v2:latest         # AI Research
scoobyjava15/sophia-huggingface-ai:latest        # Model Management
scoobyjava15/sophia-prompt-optimizer:latest      # Prompt Enhancement
scoobyjava15/sophia-gong-v2:latest               # Sales AI
```

### **3. MCP Server Images (MCP Orchestrator)**
```yaml
# V2 MCP Servers - Standardized Builds
scoobyjava15/sophia-github-v2:latest             # GitHub Integration
scoobyjava15/sophia-slack-v2:latest              # Slack Integration
scoobyjava15/sophia-linear-v2:latest             # Linear PM
scoobyjava15/sophia-notion-v2:latest             # Notion KB
scoobyjava15/sophia-codacy-v2:latest             # Code Quality
scoobyjava15/sophia-asana-v2:latest              # Task Management
scoobyjava15/sophia-hubspot:latest               # CRM
scoobyjava15/sophia-salesforce:latest            # Enterprise CRM
```

### **4. Data Processing Images (Data Pipeline)**
```yaml
# Data Services
scoobyjava15/sophia-snowflake-v2:latest          # Data Warehouse
scoobyjava15/sophia-snowflake-unified:latest     # Unified Processing
scoobyjava15/sophia-gong-webhook:latest          # Webhook Handler
ghcr.io/estuary/flow:dev                         # Real-time ETL
```

### **5. Development & Monitoring Images**
```yaml
# Monitoring Stack
prom/prometheus:latest                           # Metrics
grafana/grafana:latest                           # Dashboards
grafana/loki:latest                              # Logs
nvcr.io/nvidia/k8s/dcgm-exporter:3.1.7-3.1.4-ubuntu20.04  # GPU Metrics
```

---

## 🔧 BUILD STRATEGY

### **Phase 1: Core Image Standardization**

#### **1.1 Unified Dockerfile Structure**
```dockerfile
# Base Dockerfile template for all services
FROM python:3.12-slim AS base
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM base AS development
COPY requirements-dev.txt .
RUN pip install --no-cache-dir -r requirements-dev.txt

FROM base AS production
COPY . .
RUN python -m compileall .
USER nobody
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### **1.2 GPU-Optimized Builds**
```dockerfile
# GPU-optimized base for AI services
FROM nvidia/cuda:12.2.0-runtime-ubuntu22.04 AS gpu-base
RUN apt-get update && apt-get install -y python3.12 python3-pip
WORKDIR /app

FROM gpu-base AS ai-service
COPY requirements-gpu.txt .
RUN pip3 install --no-cache-dir -r requirements-gpu.txt
ENV CUDA_VISIBLE_DEVICES=0
```

### **Phase 2: Build Pipeline Implementation**

#### **2.1 Centralized Build Script**
```bash
#!/bin/bash
# scripts/build_all_docker_images.sh

# Build configuration
REGISTRY="scoobyjava15"
BUILD_DATE=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
GIT_COMMIT=$(git rev-parse --short HEAD)

# Build functions for each category
build_core_images() {
    docker build -t $REGISTRY/sophia-ai:latest \
        --build-arg BUILD_DATE=$BUILD_DATE \
        --build-arg GIT_COMMIT=$GIT_COMMIT \
        -f Dockerfile.production .
}

build_mcp_servers() {
    for server in infrastructure/mcp_servers/*_v2; do
        name=$(basename $server)
        docker build -t $REGISTRY/sophia-$name:latest \
            -f $server/Dockerfile $server/
    done
}
```

#### **2.2 GitHub Actions Workflow**
```yaml
name: 🐳 Build & Push All Images
on:
  workflow_dispatch:
  push:
    branches: [main]
    paths:
      - 'backend/**'
      - 'frontend/**'
      - 'mcp-servers/**'
      - 'Dockerfile*'

jobs:
  build-matrix:
    strategy:
      matrix:
        include:
          - category: core
            images: [backend, unified-chat, dashboard, mcp-gateway]
          - category: ai
            images: [ai-memory-v2, cortex, mem0, huggingface-ai]
          - category: mcp
            images: [github-v2, slack-v2, linear-v2, notion-v2]
```

### **Phase 3: Registry Management**

#### **3.1 Docker Hub Organization**
```yaml
Registry Structure:
  scoobyjava15/
    ├── sophia-ai:latest                    # Main backend
    ├── sophia-ai:v1.2.3                    # Version tags
    ├── sophia-ai:prod-20250109             # Date tags
    ├── sophia-ai-memory-v2:latest          # MCP servers
    └── sophia-*:latest                     # All other services
```

#### **3.2 Image Tagging Strategy**
```bash
# Tagging convention
docker tag $IMAGE $REGISTRY/$IMAGE:latest
docker tag $IMAGE $REGISTRY/$IMAGE:$VERSION
docker tag $IMAGE $REGISTRY/$IMAGE:$ENVIRONMENT-$DATE
docker tag $IMAGE $REGISTRY/$IMAGE:$GIT_COMMIT
```

---

## 🚀 DEPLOYMENT IMPLEMENTATION

### **Step 1: Archive Legacy Build Scripts**
```bash
# Create archive directory
mkdir -p archive/docker-builds-legacy/

# Move old build scripts
mv scripts/build_sophia_images.sh archive/docker-builds-legacy/
mv scripts/docker_build_and_push.sh archive/docker-builds-legacy/
mv unified_build_images.sh archive/docker-builds-legacy/
mv unified_docker_hub_push.sh archive/docker-builds-legacy/
```

### **Step 2: Create Unified Build System**
```bash
# Create new build structure
mkdir -p deployment/docker/
mkdir -p deployment/docker/dockerfiles/
mkdir -p deployment/docker/build-scripts/

# Create master build script
cat > deployment/docker/build-all.sh << 'EOF'
#!/bin/bash
# Master Docker build script for Sophia AI

set -euo pipefail

# Configuration
REGISTRY="${DOCKER_REGISTRY:-scoobyjava15}"
TAG="${IMAGE_TAG:-latest}"
PLATFORM="${BUILD_PLATFORM:-linux/amd64}"

# Build all images
./build-scripts/build-core.sh
./build-scripts/build-ai.sh
./build-scripts/build-mcp.sh
./build-scripts/build-data.sh
./build-scripts/build-dev.sh
EOF
```

### **Step 3: Instance-Specific Build Optimization**

#### **3.1 Production Instance Builds**
```bash
# deployment/docker/build-scripts/build-core.sh
#!/bin/bash
# Build core platform images for RTX6000

docker buildx build \
  --platform linux/amd64 \
  --build-arg OPTIMIZE_FOR=rtx6000 \
  --tag $REGISTRY/sophia-ai:latest \
  --push \
  -f Dockerfile.production .
```

#### **3.2 AI Core Builds (GH200 Optimization)**
```bash
# deployment/docker/build-scripts/build-ai.sh
#!/bin/bash
# Build AI services optimized for GH200

docker buildx build \
  --platform linux/amd64 \
  --build-arg CUDA_VERSION=12.2.0 \
  --build-arg OPTIMIZE_FOR=gh200 \
  --build-arg ENABLE_GPU=true \
  --tag $REGISTRY/sophia-ai-memory-v2:latest \
  --push \
  -f infrastructure/mcp_servers/ai_memory_v2/Dockerfile .
```

### **Step 4: CI/CD Integration**

#### **4.1 GitHub Actions Workflow**
```yaml
# .github/workflows/docker-build-unified.yml
name: 🐳 Unified Docker Build & Deploy

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

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3
        
      - name: Login to Docker Hub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}
          
      - name: Build images for ${{ inputs.target_instance }}
        run: |
          ./deployment/docker/build-all.sh --target ${{ inputs.target_instance }}
          
      - name: Deploy to Lambda Labs
        run: |
          ./scripts/deploy_sophia_unified.sh deploy ${{ inputs.target_instance }}
```

---

## 📊 BUILD OPTIMIZATION MATRIX

| **Instance** | **GPU** | **Optimization Flags** | **Base Image** | **Build Cache** |
|-------------|---------|----------------------|----------------|-----------------|
| **Production** | RTX6000 | `--optimize=web` | `python:3.12-slim` | GitHub Actions |
| **AI Core** | GH200 | `--optimize=gpu --cuda=12.2` | `nvidia/cuda:12.2.0` | Lambda Labs |
| **MCP Hub** | A6000 | `--optimize=concurrent` | `python:3.12-slim` | Docker Hub |
| **Data Pipeline** | A100 | `--optimize=data --tensor` | `nvidia/cuda:11.8.0` | Lambda Labs |
| **Development** | A10 | `--optimize=dev` | `python:3.12` | Local |

---

## 🎯 SUCCESS METRICS

### **Build Performance**
- **Build Time**: < 10 minutes for all images
- **Image Size**: < 500MB for standard services, < 2GB for GPU services
- **Cache Hit Rate**: > 80% for incremental builds
- **Registry Push Time**: < 5 minutes total

### **Deployment Efficiency**
- **Pull Time**: < 2 minutes per instance
- **Startup Time**: < 30 seconds per service
- **Resource Usage**: < 80% of allocated resources
- **Success Rate**: > 95% first-time deployments

---

## 📋 IMPLEMENTATION CHECKLIST

### **Week 1: Foundation**
- [ ] Archive 10+ legacy build scripts
- [ ] Create unified build directory structure
- [ ] Standardize Dockerfile templates
- [ ] Set up Docker Hub organization

### **Week 2: Core Images**
- [ ] Build and test core platform images
- [ ] Implement GPU optimization for AI images
- [ ] Create MCP server build pipeline
- [ ] Test multi-platform builds

### **Week 3: Automation**
- [ ] Implement GitHub Actions workflows
- [ ] Set up build caching strategy
- [ ] Create automated testing for images
- [ ] Implement security scanning

### **Week 4: Deployment**
- [ ] Deploy to all Lambda Labs instances
- [ ] Monitor image performance
- [ ] Optimize based on metrics
- [ ] Document build procedures

---

## 🔐 SECURITY CONSIDERATIONS

### **Image Security**
- Run as non-root user in all containers
- Implement multi-stage builds to reduce attack surface
- Scan all images with Trivy/Snyk
- Sign images with Docker Content Trust

### **Registry Security**
- Use Docker Hub access tokens (not passwords)
- Implement rate limiting awareness
- Set up private registry for sensitive images
- Regular credential rotation

---

## 🚀 NEXT STEPS

1. **Immediate Actions**
   - Review and approve this plan
   - Set up Docker Hub organization structure
   - Begin archiving legacy scripts

2. **This Week**
   - Implement Phase 1 standardization
   - Build first set of core images
   - Test deployment to development instance

3. **Next Week**
   - Complete all image builds
   - Implement CI/CD automation
   - Begin production deployments

This comprehensive plan transforms the fragmented Docker build process into a unified, efficient system that aligns with the Lambda Labs deployment architecture and addresses all requirements from PR #179. 