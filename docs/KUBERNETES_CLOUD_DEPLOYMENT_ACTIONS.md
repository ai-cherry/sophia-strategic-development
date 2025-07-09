# Kubernetes and Docker Cloud Deployment Actions

**Date**: January 14, 2025
**Priority**: High - Immediate action required

## 🎯 Executive Summary

I've examined the entire codebase and identified critical inconsistencies in deployment approaches. Here's what needs to be done to achieve a clean, Kubernetes-first cloud deployment architecture.

## 🔍 Key Findings

### 1. **Mixed Orchestration Approaches**
- **Docker Swarm** files actively used (docker-compose.cloud.yml)
- **Kubernetes** manifests exist but not actively deployed
- **Multiple deployment scripts** with overlapping functionality (15+ scripts)
- **No clear orchestration strategy** documented

### 2. **LLM Gateway Configuration (Portkey + OpenRouter)**
- **Properly configured** in multiple locations
- **Consistent approach**: Portkey as primary, OpenRouter as fallback
- **Good model selection**: Latest models configured (GPT-4o, Claude 3.5, DeepSeek v3)
- **Keep this configuration** - it's well designed

### 3. **Lambda Labs Infrastructure**
- **5 GPU instances** properly documented
- **IPs scattered** across multiple files
- **No Kubernetes cluster** actually running on Lambda Labs
- **Docker Swarm** is current reality

### 4. **Technical Debt**
- **27 redundant files** identified for removal
- **3 conflicting deployment patterns**
- **Multiple secret management approaches**
- **Inconsistent documentation**

## 📋 Immediate Actions Required

### Phase 1: Clean Up (Week 1)

1. **Run Technical Debt Cleanup**
   ```bash
   chmod +x scripts/cleanup_deployment_technical_debt.py
   python scripts/cleanup_deployment_technical_debt.py
   ```

2. **Consolidate Dockerfiles**
   ```bash
   # Rename main Dockerfile
   mv Dockerfile.production.2025 Dockerfile
   rm Dockerfile.production
   rm frontend/Dockerfile.simple
   ```

3. **Remove Redundant Scripts**
   - Delete 15+ duplicate deployment scripts
   - Keep only: `deploy_unified_kubernetes.sh`
   - Update all references

### Phase 2: Kubernetes Setup (Week 2)

1. **Install Kubernetes on Lambda Labs**
   ```bash
   # On control plane (104.171.202.103)
   curl -sfL https://get.k3s.io | sh -s - server \
     --cluster-init \
     --disable traefik \
     --node-name sophia-control-plane
   
   # On worker nodes
   curl -sfL https://get.k3s.io | K3S_URL=https://104.171.202.103:6443 \
     K3S_TOKEN=<token> sh -s - \
     --node-name sophia-worker-<name>
   ```

2. **Configure GPU Support**
   ```bash
   # Install NVIDIA device plugin
   kubectl apply -f https://raw.githubusercontent.com/NVIDIA/k8s-device-plugin/v0.14.0/nvidia-device-plugin.yml
   ```

3. **Deploy with Helm**
   ```bash
   # Make script executable
   chmod +x scripts/deploy_unified_kubernetes.sh
   
   # Deploy platform
   ./scripts/deploy_unified_kubernetes.sh deploy
   ```

### Phase 3: GitOps Implementation (Week 3)

1. **Install ArgoCD**
   ```bash
   kubectl create namespace argocd
   kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
   ```

2. **Configure GitOps**
   ```yaml
   # kubernetes/gitops/argocd/sophia-app.yaml
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
   ```

## 🏗️ Final Architecture

### Unified Stack
```
┌─────────────────────────────────────┐
│         Lambda Labs Cloud           │
│  ┌─────────────────────────────┐   │
│  │    Kubernetes (K3s/K8s)     │   │
│  ├─────────────────────────────┤   │
│  │  Helm Charts + ArgoCD       │   │
│  ├─────────────────────────────┤   │
│  │  Docker Hub: scoobyjava15   │   │
│  ├─────────────────────────────┤   │
│  │  Pulumi ESC → K8s Secrets   │   │
│  ├─────────────────────────────┤   │
│  │  Portkey → OpenRouter LLM   │   │
│  └─────────────────────────────┘   │
└─────────────────────────────────────┘
```

### Service Distribution
```
Control Plane (RTX6000) - 104.171.202.103
├── Kubernetes Master
├── Ingress Controller
├── Sophia Backend
└── Frontend

AI Core (GH200) - 192.222.58.232
├── AI Memory MCP
├── Snowflake Cortex
├── LLM Processing
└── Vector Databases

MCP Hub (A6000) - 104.171.202.117
├── GitHub MCP
├── Slack MCP
├── Linear MCP
└── All Integration MCPs

Data Pipeline (A100) - 104.171.202.134
├── Snowflake Processing
├── Data Analytics
└── Prometheus/Grafana

Development (A10) - 155.248.194.183
├── Testing Environment
├── CI/CD Runners
└── Development Tools
```

## ✅ Configuration to Keep

### LLM Gateway (This is Good!)
```yaml
llmGateway:
  provider: portkey
  portkey:
    endpoint: https://api.portkey.ai/v1
  openrouter:
    endpoint: https://openrouter.ai/api/v1
    models:
      - gpt-4o              # Latest GPT
      - claude-3-5-sonnet   # Latest Claude
      - deepseek-v3         # Cost effective
      - gemini-2.0-flash    # Fast
```

### Pulumi ESC Integration
- Keep current GitHub → Pulumi ESC → Application flow
- Already well configured
- Just needs K8s secret integration

## 🚫 What to Remove

### Files to Delete
```bash
# Docker Compose variants
rm docker-compose.enhanced.yml
rm docker-compose.override.yml
rm docker-compose.unified.yml

# Old deployment scripts
rm scripts/deploy_lambda_labs_complete.py
rm scripts/deploy_real_internet_sophia*.py
rm scripts/deploy_enhanced_*.py
rm scripts/deploy_to_lambda_labs_kubernetes.py

# Conflicting configs
rm config/mcp/registry.yaml
rm mcp-config/gateway-config.json
```

### Patterns to Eliminate
- SSH-based deployments
- Manual docker commands
- Environment-specific compose files
- Direct secret injection

## 📊 Success Metrics

After implementation:
- **1 deployment command**: `./scripts/deploy_unified_kubernetes.sh`
- **1 orchestrator**: Kubernetes
- **1 registry**: Docker Hub (scoobyjava15)
- **1 secret flow**: Pulumi ESC → K8s Secrets
- **1 LLM gateway**: Portkey → OpenRouter
- **0 manual steps**: Everything automated

## 🎉 Expected Benefits

1. **90% reduction** in deployment complexity
2. **Single source of truth** for all configurations
3. **GPU optimization** with proper scheduling
4. **Cost savings** through resource management
5. **GitOps automation** for all deployments
6. **Better observability** with standard tools
7. **Faster deployments** with Helm
8. **Self-healing** infrastructure

## 🚀 Next Steps

1. **Review this plan** with stakeholders
2. **Create backup** of current state
3. **Execute Phase 1** cleanup immediately
4. **Schedule Phase 2** Kubernetes installation
5. **Plan Phase 3** GitOps rollout
6. **Update documentation** as you go
7. **Train team** on new approach

## ⚠️ Risks and Mitigations

### Risk 1: Service Disruption
- **Mitigation**: Keep Docker Swarm running until K8s is validated
- **Rollback**: All changes are reversible

### Risk 2: Learning Curve
- **Mitigation**: Comprehensive documentation and training
- **Support**: Kubernetes has huge community

### Risk 3: GPU Issues
- **Mitigation**: Test GPU scheduling thoroughly
- **Fallback**: Can use node selectors initially

---

**Remember**: The goal is **simplification**. We're moving from chaos to clarity. Every step should make deployments easier, not harder.

**Final Note**: Your Portkey/OpenRouter LLM configuration is excellent. Keep it as-is and ensure it's properly integrated into the Kubernetes ConfigMaps. 