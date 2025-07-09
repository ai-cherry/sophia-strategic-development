# Kubernetes and Docker Cloud Deployment Alignment Report

**Date**: January 14, 2025
**Status**: Critical - Multiple conflicting deployment strategies identified

## 🔍 Executive Summary

The Sophia AI codebase currently has **THREE competing deployment strategies** running in parallel:
1. **Docker Swarm** (docker-compose.cloud.yml) - Currently used in production
2. **Kubernetes** (kubernetes/ directory) - Partially implemented
3. **Multiple Docker Compose variants** (deployment/ directory) - Instance-specific

This fragmentation creates confusion, increases technical debt, and makes deployments error-prone.

## 📊 Current State Analysis

### 1. Docker Configurations Found

#### Primary Docker Files
- **docker-compose.cloud.yml** (474 lines) - Main production Swarm config
- **docker-compose.unified.yml** - Alternative unified config
- **docker-compose.enhanced.yml** - Enhanced version with optimizations
- **Dockerfile.production** - Main production Dockerfile
- **Dockerfile.production.2025** - Updated version with BuildKit
- **docker/Dockerfile.optimized** - Optimized multi-stage build
- **docker/Dockerfile.gh200** - GPU-specific build

#### Deployment-Specific Compose Files
- **deployment/docker-compose-production.yml** - RTX6000 instance
- **deployment/docker-compose-ai-core.yml** - GH200 instance
- **deployment/docker-compose-mcp-orchestrator.yml** - A6000 instance
- **deployment/docker-compose-data-pipeline.yml** - A100 instance
- **deployment/docker-compose-development.yml** - A10 instance

### 2. Kubernetes Configurations

#### Kubernetes Structure
```
kubernetes/
├── production/          # Production manifests
├── gitops/             # GitOps with Kustomize
├── keel/               # Automated updates
├── monitoring/         # Prometheus/Grafana
├── security/           # RBAC, NetworkPolicies
└── mcp-servers/        # MCP server deployments
```

#### Key Findings
- Kubernetes manifests exist but aren't actively used
- References to kubectl in workflows but no active K8s cluster
- Helm charts created but not deployed
- Conflicting namespace strategies

### 3. Deployment Scripts (15+ Found)

#### Active Scripts
- `deploy_sophia_unified.sh` - Main unified deployment
- `deploy_to_lambda_labs_kubernetes.py` - K8s deployment (unused)
- `deploy_sophia_platform.sh` - Platform deployment
- `deploy_lambda_labs_complete.py` - Complete deployment
- `lambda_migration_deploy.sh` - Migration script

#### Issues
- Multiple scripts doing the same thing
- Inconsistent error handling
- Different secret management approaches
- No clear "source of truth" for deployments

## 🚨 Critical Inconsistencies

### 1. **Orchestration Confusion**
- **Documentation says**: "Use Kubernetes for production"
- **Reality**: Docker Swarm is actively used
- **Scripts**: Mix of both approaches
- **Recommendation**: Standardize on Kubernetes for cloud-native benefits

### 2. **Secret Management Chaos**
- Docker Swarm uses Docker secrets
- Kubernetes manifests use K8s secrets
- Scripts mix environment variables and file-based secrets
- **Recommendation**: Use Pulumi ESC → Kubernetes Secrets exclusively

### 3. **Service Discovery Mismatch**
- Docker Swarm: Internal DNS (service_name)
- Kubernetes: Service objects with ClusterIP
- Mixed approaches in application code
- **Recommendation**: Use Kubernetes Services with proper DNS

### 4. **Resource Management**
- Docker Swarm: Basic CPU/memory limits
- Kubernetes: Detailed resource quotas, HPA, VPA
- No GPU resource management in Swarm
- **Recommendation**: Kubernetes for proper GPU scheduling

### 5. **Network Configuration**
- Docker Swarm: Overlay networks
- Kubernetes: CNI with NetworkPolicies
- Traefik vs Nginx Ingress confusion
- **Recommendation**: Kubernetes Ingress with cert-manager

## 🚀 Recommended Cloud-Native Architecture

### Phase 1: Kubernetes Migration (Immediate)

```yaml
# Unified Kubernetes deployment approach
apiVersion: v1
kind: Namespace
metadata:
  name: sophia-ai
  labels:
    environment: production
    cloud: lambda-labs
---
# Use Helm for templating
helm/
├── sophia-platform/
│   ├── Chart.yaml
│   ├── values.yaml
│   ├── values-production.yaml
│   ├── values-ai-core.yaml
│   └── templates/
│       ├── deployment.yaml
│       ├── service.yaml
│       ├── ingress.yaml
│       └── configmap.yaml
```

### Phase 2: GitOps Implementation

```yaml
# ArgoCD Application
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: sophia-platform
  namespace: argocd
spec:
  source:
    repoURL: https://github.com/ai-cherry/sophia-main
    path: kubernetes/helm/sophia-platform
    targetRevision: main
    helm:
      valueFiles:
        - values-production.yaml
  destination:
    server: https://kubernetes.default.svc
    namespace: sophia-ai
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

### Phase 3: Service Mesh (Optional)

```yaml
# Istio/Linkerd for advanced networking
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: sophia-routing
spec:
  hosts:
    - sophia-ai.lambda-labs.cloud
  http:
    - match:
        - uri:
            prefix: /api
      route:
        - destination:
            host: sophia-backend
            port:
              number: 8000
```

## 🔧 LLM Gateway Configuration

### Current Portkey/OpenRouter Setup (Keep This!)

```yaml
# This is properly configured - maintain this approach
llm_gateway:
  primary: portkey
  portkey:
    endpoint: https://api.portkey.ai/v1
    fallback: openrouter
  openrouter:
    endpoint: https://openrouter.ai/api/v1
    models:
      - gpt-4o              # Latest GPT-4
      - claude-3-5-sonnet   # Latest Claude
      - deepseek-v3         # Cost-effective
      - gemini-2.0-flash    # Fast responses
```

### Kubernetes ConfigMap for LLM Config

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: llm-config
  namespace: sophia-ai
data:
  portkey-config.json: |
    {
      "default_provider": "openrouter",
      "routing_rules": [
        {
          "task": "code_generation",
          "route_to": "claude-3-5-sonnet-20241022"
        },
        {
          "task": "analysis",
          "route_to": "gpt-4o"
        }
      ]
    }
```

## 📋 Action Plan

### Immediate Actions (Week 1)

1. **Choose Single Orchestrator**
   ```bash
   # Decision: Kubernetes for all cloud deployments
   # Rationale: Better GPU support, scaling, cloud-native
   ```

2. **Consolidate Docker Images**
   ```bash
   # Single Dockerfile per service
   mv Dockerfile.production.2025 Dockerfile
   rm Dockerfile.production Dockerfile.simple
   ```

3. **Unify Deployment Scripts**
   ```bash
   # Single deployment command
   ./deploy.sh --platform kubernetes --env production
   ```

### Short-term (Weeks 2-3)

1. **Migrate to Kubernetes**
   - Convert docker-compose files to Helm charts
   - Test on development instance first
   - Rolling migration instance by instance

2. **Implement GitOps**
   - Set up ArgoCD on Lambda Labs
   - Configure automated deployments
   - Enable progressive rollouts

3. **Standardize Secrets**
   - Pulumi ESC → Kubernetes Secrets
   - Remove all Docker secret references
   - Update application code

### Medium-term (Month 2)

1. **Service Mesh**
   - Evaluate Istio vs Linkerd
   - Implement traffic management
   - Add observability

2. **GPU Optimization**
   - Implement GPU device plugins
   - Configure GPU node selectors
   - Add GPU monitoring

3. **Cost Optimization**
   - Implement cluster autoscaling
   - Use spot instances where possible
   - Optimize resource requests

## 🏗️ Recommended Architecture

### Kubernetes Cluster Setup

```yaml
# Lambda Labs Kubernetes Configuration
nodes:
  - name: sophia-control-plane
    instance: sophia-production-instance
    role: master
    gpu: RTX6000
  
  - name: sophia-worker-ai
    instance: sophia-ai-core
    role: worker
    gpu: GH200
    taints:
      - key: nvidia.com/gpu
        value: "true"
        effect: NoSchedule
  
  - name: sophia-worker-mcp
    instance: sophia-mcp-orchestrator
    role: worker
    gpu: A6000
  
  - name: sophia-worker-data
    instance: sophia-data-pipeline
    role: worker
    gpu: A100
  
  - name: sophia-worker-dev
    instance: sophia-development
    role: worker
    gpu: A10
```

### Standardized Service Pattern

```yaml
# Template for all services
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ .Values.service.name }}
  namespace: sophia-ai
spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels:
      app: {{ .Values.service.name }}
  template:
    metadata:
      labels:
        app: {{ .Values.service.name }}
    spec:
      nodeSelector:
        gpu-type: {{ .Values.gpu.type }}
      containers:
      - name: {{ .Values.service.name }}
        image: scoobyjava15/{{ .Values.service.name }}:{{ .Values.image.tag }}
        resources:
          requests:
            memory: {{ .Values.resources.requests.memory }}
            cpu: {{ .Values.resources.requests.cpu }}
            nvidia.com/gpu: {{ .Values.gpu.count | default 0 }}
          limits:
            memory: {{ .Values.resources.limits.memory }}
            cpu: {{ .Values.resources.limits.cpu }}
            nvidia.com/gpu: {{ .Values.gpu.count | default 0 }}
```

## 🎯 Benefits of Alignment

### Technical Benefits
- **Consistency**: Single deployment pattern
- **Scalability**: Kubernetes HPA/VPA
- **GPU Management**: Proper scheduling
- **Observability**: Built-in monitoring
- **Security**: RBAC, NetworkPolicies

### Business Benefits
- **Faster Deployments**: GitOps automation
- **Lower Costs**: Better resource utilization
- **Higher Reliability**: Self-healing
- **Easier Maintenance**: Standard patterns

### Developer Benefits
- **Clear Documentation**: Single approach
- **Better Testing**: Consistent environments
- **Faster Onboarding**: Standard tools
- **Less Confusion**: Clear patterns

## 🚫 Technical Debt to Remove

### Files to Delete
```bash
# Redundant Docker files
rm docker-compose.enhanced.yml
rm docker-compose.override.yml
rm frontend/Dockerfile.simple

# Old deployment scripts
rm scripts/deploy_lambda_labs_complete.py
rm scripts/deploy_real_internet_sophia*.py
rm scripts/deploy_enhanced_*.py

# Conflicting configs
rm config/mcp/registry.yaml  # Use K8s ConfigMaps
```

### Patterns to Eliminate
- Direct SSH deployments
- Manual Docker commands
- Environment-specific compose files
- Hardcoded configurations

## ✅ Final Recommendations

1. **Commit to Kubernetes** - It's the industry standard for cloud deployments
2. **Use Helm Charts** - Templating reduces duplication
3. **Implement GitOps** - ArgoCD for automated deployments
4. **Standardize on One Pattern** - Less is more
5. **Document Everything** - Clear runbooks

## 🎉 Expected Outcomes

After implementing these recommendations:
- **90% reduction** in deployment scripts
- **Single source of truth** for configurations
- **Automated deployments** via GitOps
- **Proper GPU utilization** with Kubernetes
- **Cost savings** through better resource management
- **Improved reliability** with self-healing
- **Better observability** with standard tools

---

**Next Steps**: 
1. Review and approve this plan
2. Create migration timeline
3. Start with development instance
4. Roll out to production gradually

**Remember**: The goal is simplification. If it doesn't make deployments simpler, don't do it. 