# Kubernetes Deployment on Lambda Labs GPU Servers - 2025 Guide

## 🚀 Overview

This guide implements the latest 2025 best practices for deploying Sophia AI on Lambda Labs GPU servers using Kubernetes, optimized for the specific GPU instances and regions.

## 📊 Lambda Labs Infrastructure

| Instance Name              | Type           | GPU Model | Region      | IP Address       | Purpose                    |
|----------------------------|----------------|-----------|-------------|------------------|----------------------------|
| sophia-production-instance | gpu_1x_rtx6000 | RTX 6000  | us-south-1  | 104.171.202.103  | Production services        |
| sophia-ai-core             | gpu_1x_gh200   | GH200     | us-east-3   | 192.222.58.232   | AI/ML workloads           |
| sophia-mcp-orchestrator    | gpu_1x_a6000   | RTX A6000 | us-south-1  | 104.171.202.117  | MCP server orchestration  |
| sophia-data-pipeline       | gpu_1x_a100    | A100      | us-south-1  | 104.171.202.134  | Data processing pipeline  |
| sophia-development         | gpu_1x_a10     | A10       | us-west-1   | 155.248.194.183  | Development/staging       |

## 🐳 Docker Image Building (2025 Best Practices)

### Multi-Stage Build with BuildKit

```dockerfile
# Dockerfile.production.2025
# syntax=docker/dockerfile:1.5
# Enable BuildKit features
# Build stage - optimized for caching
FROM python:3.12-slim AS builder

# Install build dependencies
RUN --mount=type=cache,target=/var/cache/apt \
    apt-get update && apt-get install -y \
    gcc g++ git curl \
    && rm -rf /var/lib/apt/lists/*

# Install UV for blazing fast dependency management
RUN curl -LsSf https://github.com/astral-sh/uv/releases/latest/download/uv-installer.sh | sh
ENV PATH="/root/.cargo/bin:$PATH"

WORKDIR /build

# Copy dependency files first for better caching
COPY pyproject.toml uv.lock* ./
COPY backend/ ./backend/

# Use BuildKit cache mount for UV cache
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-dev

# Production stage - minimal runtime
FROM python:3.12-slim

# Install runtime dependencies and security updates
RUN apt-get update && apt-get install -y \
    curl \
    && apt-get upgrade -y \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 sophia

WORKDIR /app

# Copy from builder
COPY --from=builder --chown=sophia:sophia /build/.venv /app/.venv
COPY --from=builder --chown=sophia:sophia /build/backend /app/backend

# Set environment
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH="/app:$PYTHONPATH" \
    ENVIRONMENT="prod" \
    PULUMI_ORG="scoobyjava-org" \
    PYTHONUNBUFFERED=1

# Switch to non-root user
USER sophia

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

# Use exec form for proper signal handling
ENTRYPOINT ["uvicorn"]
CMD ["backend.app.fastapi_app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### GPU-Optimized Base Images

For AI/ML workloads on the GH200 and A100 instances:

```dockerfile
# Dockerfile.ai-core.2025
FROM nvidia/cuda:12.3.1-runtime-ubuntu22.04 AS base

# Install Python and ML dependencies
RUN apt-get update && apt-get install -y \
    python3.12 python3.12-venv python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Continue with multi-stage pattern...
```

### Build Script with Security Scanning

```bash
#!/bin/bash
# scripts/build_secure_images.sh

set -euo pipefail

# Enable BuildKit
export DOCKER_BUILDKIT=1

# Build with multi-platform support
docker buildx build \
  --platform linux/amd64 \
  --build-arg BUILDKIT_INLINE_CACHE=1 \
  --cache-from type=registry,ref=scoobyjava15/sophia-backend:buildcache \
  --cache-to type=registry,ref=scoobyjava15/sophia-backend:buildcache,mode=max \
  -t scoobyjava15/sophia-backend:latest \
  -f Dockerfile.production.2025 \
  .

# Security scan with Trivy
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy:latest image \
  --severity HIGH,CRITICAL \
  --exit-code 1 \
  scoobyjava15/sophia-backend:latest

# Push only if scan passes
docker push scoobyjava15/sophia-backend:latest
```

## 🎯 Kubernetes Setup with SkyPilot (Recommended)

### Install SkyPilot

```bash
pip install skypilot[lambda]
sky check
```

### Configure Lambda Labs Access

```bash
# Set Lambda Labs API key
export LAMBDA_API_KEY="${LAMBDA_API_KEY}"

# Configure firewall rules
sky launch --cloud lambda --ports 6443,10250,30000-32767 firewall-setup
```

### Launch Multi-Region GPU Cluster

```yaml
# skypilot-cluster.yaml
cluster:
  name: sophia-ai-cluster
  
nodes:
  - name: control-plane
    cloud: lambda
    instance_type: gpu_1x_rtx6000
    region: us-south-1
    disk_size: 100
    
  - name: ai-core
    cloud: lambda
    instance_type: gpu_1x_gh200
    region: us-east-3
    disk_size: 500
    
  - name: mcp-orchestrator
    cloud: lambda
    instance_type: gpu_1x_a6000
    region: us-south-1
    disk_size: 200
    
  - name: data-pipeline
    cloud: lambda
    instance_type: gpu_1x_a100
    region: us-south-1
    disk_size: 500
    
  - name: development
    cloud: lambda
    instance_type: gpu_1x_a10
    region: us-west-1
    disk_size: 100

setup: |
  # Install Kubernetes components
  sudo apt-get update
  sudo apt-get install -y apt-transport-https ca-certificates curl
  curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.29/deb/Release.key | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg
  echo 'deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.29/deb/ /' | sudo tee /etc/apt/sources.list.d/kubernetes.list
  sudo apt-get update
  sudo apt-get install -y kubelet kubeadm kubectl
  sudo apt-mark hold kubelet kubeadm kubectl
  
  # Install NVIDIA GPU Operator
  kubectl apply -f https://raw.githubusercontent.com/NVIDIA/gpu-operator/v23.9.1/deployments/gpu-operator.yaml

run: |
  # Initialize cluster on control plane
  if [[ $(hostname) == *"control-plane"* ]]; then
    sudo kubeadm init --pod-network-cidr=10.244.0.0/16
    mkdir -p $HOME/.kube
    sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
    sudo chown $(id -u):$(id -g) $HOME/.kube/config
    
    # Install Flannel CNI
    kubectl apply -f https://github.com/flannel-io/flannel/releases/latest/download/kube-flannel.yml
    
    # Generate join command
    kubeadm token create --print-join-command > /tmp/join-command.sh
  fi
```

### Deploy with SkyPilot

```bash
sky launch -c sophia-ai-cluster skypilot-cluster.yaml
```

## 📦 Kubernetes Manifests (Production-Ready)

### Namespace with Resource Quotas

```yaml
# kubernetes/production/00-namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: sophia-ai-prod
  labels:
    app: sophia-ai
    environment: production
---
apiVersion: v1
kind: ResourceQuota
metadata:
  name: compute-quota
  namespace: sophia-ai-prod
spec:
  hard:
    requests.cpu: "100"
    requests.memory: 200Gi
    requests.nvidia.com/gpu: "5"
    persistentvolumeclaims: "10"
```

### GPU-Enabled Backend Deployment

```yaml
# kubernetes/production/sophia-backend-gpu.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: sophia-ai-core
  namespace: sophia-ai-prod
  labels:
    app: sophia-ai-core
    gpu-type: gh200
spec:
  replicas: 2
  selector:
    matchLabels:
      app: sophia-ai-core
  template:
    metadata:
      labels:
        app: sophia-ai-core
        gpu-type: gh200
    spec:
      # Node selector for GH200 GPU
      nodeSelector:
        kubernetes.io/hostname: sophia-ai-core
        nvidia.com/gpu.product: GH200
      
      # Tolerations for GPU nodes
      tolerations:
      - key: nvidia.com/gpu
        operator: Exists
        effect: NoSchedule
      
      containers:
      - name: ai-core
        image: scoobyjava15/sophia-ai-core:latest
        imagePullPolicy: Always
        
        resources:
          requests:
            memory: "16Gi"
            cpu: "4"
            nvidia.com/gpu: 1
          limits:
            memory: "32Gi"
            cpu: "8"
            nvidia.com/gpu: 1
        
        env:
        - name: CUDA_VISIBLE_DEVICES
          value: "0"
        - name: ENVIRONMENT
          value: "prod"
        - name: GPU_MEMORY_FRACTION
          value: "0.9"
        
        # Volume mounts for model storage
        volumeMounts:
        - name: model-cache
          mountPath: /models
        - name: shared-memory
          mountPath: /dev/shm
        
        # Probes
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 60
          periodSeconds: 30
        
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        
        # Security context
        securityContext:
          runAsNonRoot: true
          runAsUser: 1000
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: true
      
      volumes:
      - name: model-cache
        persistentVolumeClaim:
          claimName: model-cache-pvc
      - name: shared-memory
        emptyDir:
          medium: Memory
          sizeLimit: 8Gi
```

### Data Pipeline with A100 GPU

```yaml
# kubernetes/production/data-pipeline-a100.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: sophia-data-pipeline
  namespace: sophia-ai-prod
spec:
  replicas: 1
  selector:
    matchLabels:
      app: sophia-data-pipeline
  template:
    metadata:
      labels:
        app: sophia-data-pipeline
        gpu-type: a100
    spec:
      nodeSelector:
        kubernetes.io/hostname: sophia-data-pipeline
        nvidia.com/gpu.product: A100
      
      containers:
      - name: data-pipeline
        image: scoobyjava15/sophia-data-pipeline:latest
        
        resources:
          requests:
            memory: "32Gi"
            cpu: "8"
            nvidia.com/gpu: 1
          limits:
            memory: "64Gi"
            cpu: "16"
            nvidia.com/gpu: 1
        
        env:
        - name: PYTORCH_CUDA_ALLOC_CONF
          value: "max_split_size_mb:512"
        - name: CUDA_LAUNCH_BLOCKING
          value: "0"
```

### Ingress with SSL/TLS

```yaml
# kubernetes/production/ingress-nginx.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: sophia-ingress
  namespace: sophia-ai-prod
  annotations:
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/proxy-body-size: "100m"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  tls:
  - hosts:
    - api.sophia-ai.com
    - app.sophia-ai.com
    secretName: sophia-tls
  
  rules:
  - host: api.sophia-ai.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: sophia-backend
            port:
              number: 80
  
  - host: app.sophia-ai.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: sophia-frontend
            port:
              number: 80
```

## 🚀 Deployment Automation

### GitHub Actions Workflow

```yaml
# .github/workflows/deploy-k8s-lambda.yml
name: Deploy to Lambda Labs Kubernetes

on:
  push:
    branches: [main]
  workflow_dispatch:

env:
  DOCKER_REGISTRY: scoobyjava15

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v3
      with:
        driver-opts: |
          image=moby/buildkit:v0.12.0
          network=host
    
    - name: Login to Docker Hub
      uses: docker/login-action@v3
      with:
        username: ${{ secrets.DOCKER_HUB_USERNAME }}
        password: ${{ secrets.DOCKER_HUB_ACCESS_TOKEN }}
    
    - name: Build and push multi-platform images
      run: |
        docker buildx build \
          --platform linux/amd64 \
          --build-arg BUILDKIT_INLINE_CACHE=1 \
          --cache-from type=registry,ref=${{ env.DOCKER_REGISTRY }}/sophia-backend:buildcache \
          --cache-to type=registry,ref=${{ env.DOCKER_REGISTRY }}/sophia-backend:buildcache,mode=max \
          --push \
          -t ${{ env.DOCKER_REGISTRY }}/sophia-backend:${{ github.sha }} \
          -t ${{ env.DOCKER_REGISTRY }}/sophia-backend:latest \
          -f Dockerfile.production.2025 .
    
    - name: Security scan
      uses: aquasecurity/trivy-action@master
      with:
        image-ref: ${{ env.DOCKER_REGISTRY }}/sophia-backend:${{ github.sha }}
        exit-code: '1'
        severity: 'CRITICAL,HIGH'
    
    - name: Deploy to Kubernetes
      run: |
        # Configure kubectl with Lambda Labs cluster
        echo "${{ secrets.LAMBDA_KUBECONFIG }}" | base64 -d > /tmp/kubeconfig
        export KUBECONFIG=/tmp/kubeconfig
        
        # Update image tags
        kubectl set image deployment/sophia-backend \
          sophia-backend=${{ env.DOCKER_REGISTRY }}/sophia-backend:${{ github.sha }} \
          -n sophia-ai-prod
        
        # Wait for rollout
        kubectl rollout status deployment/sophia-backend -n sophia-ai-prod
```

### Deployment Script

```bash
#!/bin/bash
# scripts/deploy_k8s_lambda_2025.sh

set -euo pipefail

# Configuration
NAMESPACE="sophia-ai-prod"
DOCKER_REGISTRY="scoobyjava15"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}🚀 Deploying Sophia AI to Lambda Labs Kubernetes${NC}"

# Build images with BuildKit
echo -e "${YELLOW}Building images with BuildKit...${NC}"
DOCKER_BUILDKIT=1 docker build \
  -f Dockerfile.production.2025 \
  -t ${DOCKER_REGISTRY}/sophia-backend:latest \
  --build-arg BUILDKIT_INLINE_CACHE=1 \
  .

# Security scan
echo -e "${YELLOW}Running security scan...${NC}"
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy:latest image \
  --severity HIGH,CRITICAL \
  ${DOCKER_REGISTRY}/sophia-backend:latest

# Push to registry
echo -e "${YELLOW}Pushing to registry...${NC}"
docker push ${DOCKER_REGISTRY}/sophia-backend:latest

# Deploy to Kubernetes
echo -e "${YELLOW}Deploying to Kubernetes...${NC}"
kubectl apply -f kubernetes/production/

# Monitor deployment
echo -e "${YELLOW}Monitoring deployment...${NC}"
kubectl rollout status deployment --all -n ${NAMESPACE}

echo -e "${GREEN}✅ Deployment complete!${NC}"
```

## 🔍 Monitoring and Observability

### GPU Metrics with DCGM Exporter

```yaml
# kubernetes/monitoring/dcgm-exporter.yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: dcgm-exporter
  namespace: sophia-ai-prod
spec:
  selector:
    matchLabels:
      app: dcgm-exporter
  template:
    metadata:
      labels:
        app: dcgm-exporter
    spec:
      containers:
      - name: dcgm-exporter
        image: nvidia/dcgm-exporter:3.1.7-3.1.4-ubuntu20.04
        ports:
        - containerPort: 9400
        securityContext:
          privileged: true
        volumeMounts:
        - name: gpu-metrics
          mountPath: /var/lib/kubelet/pod-resources
      volumes:
      - name: gpu-metrics
        hostPath:
          path: /var/lib/kubelet/pod-resources
```

## 📋 Summary Checklist

- [ ] Enable Docker BuildKit for faster builds
- [ ] Use multi-stage builds with minimal base images
- [ ] Implement security scanning in CI/CD pipeline
- [ ] Deploy Kubernetes with SkyPilot for automated GPU setup
- [ ] Use node selectors for GPU-specific workloads
- [ ] Configure resource limits and requests properly
- [ ] Implement proper health checks and probes
- [ ] Set up GPU monitoring with DCGM
- [ ] Use non-root containers for security
- [ ] Enable TLS/SSL with cert-manager
- [ ] Implement proper secret management with Pulumi ESC
- [ ] Monitor with Prometheus and Grafana

## 🎯 Next Steps

1. **Test GPU functionality**: Verify CUDA availability in pods
2. **Optimize model loading**: Use persistent volumes for model caching
3. **Implement autoscaling**: HPA based on GPU utilization
4. **Set up backup**: Regular snapshots of persistent volumes
5. **Configure alerts**: GPU temperature, memory, and utilization alerts 