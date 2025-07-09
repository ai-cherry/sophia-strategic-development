# Automated Kubernetes Deployment Guide for Lambda Labs

## 🚀 Overview

This guide implements automated Docker image updates for Kubernetes deployments on Lambda Labs GPU servers, incorporating the best practices from 2025 including GitOps, Keel automation, and GPU optimization.

## 🎯 Three Deployment Strategies

### 1. **Keel Automation (Simplest)**
Automatically updates deployments when new Docker images are pushed to the registry.

```bash
# Deploy with Keel automation
./scripts/deploy_with_automation.sh keel

# Setup Keel monitoring
./scripts/setup_k8s_automation.sh
```

**How it works:**
- Keel polls Docker Hub every minute
- Detects new image tags
- Automatically updates deployments
- No manual intervention required

### 2. **GitOps with Kustomize (Recommended for Production)**
Version-controlled deployments with audit trail.

```bash
# Deploy with GitOps
./scripts/deploy_with_automation.sh gitops

# Update images by editing:
# kubernetes/gitops/kustomization.yaml
```

**How it works:**
- All configurations in Git
- Image updates via pull requests
- Automated deployment on merge
- Full audit trail

### 3. **CI/CD Pipeline Integration**
Fully automated from code push to deployment.

```bash
# Triggered automatically on push to main
# See .github/workflows/k8s-gitops-deploy.yml
```

## 📁 Files Created

### Automation Components
- `kubernetes/keel/keel-deployment.yaml` - Keel controller for automatic updates
- `kubernetes/gitops/kustomization.yaml` - GitOps configuration
- `kubernetes/gitops/argocd/sophia-app.yaml` - ArgoCD application (optional)
- `kubernetes/production/sophia-*-deployment-keel.yaml` - Keel-annotated deployments

### Scripts
- `scripts/setup_k8s_automation.sh` - Setup automation tools
- `scripts/deploy_with_automation.sh` - Deploy with chosen method
- `scripts/trigger_image_update.sh` - Manual update trigger (created by setup)

### CI/CD
- `.github/workflows/k8s-gitops-deploy.yml` - Automated deployment pipeline

## 🔧 Quick Start

### Step 1: Initial Setup
```bash
# Setup kubectl access and install automation tools
./scripts/setup_k8s_automation.sh
```

This will:
- Configure kubectl access
- Install Keel for automatic updates
- Setup GitOps structure
- Optionally install ArgoCD
- Configure monitoring

### Step 2: Deploy Application
```bash
# Choose your deployment method:

# Option A: With Keel automation (simplest)
./scripts/deploy_with_automation.sh keel

# Option B: With GitOps (recommended)
./scripts/deploy_with_automation.sh gitops

# Option C: Manual (traditional)
./scripts/deploy_with_automation.sh manual
```

### Step 3: Trigger Updates

#### For Keel:
```bash
# Just push new images to Docker Hub
docker push scoobyjava15/sophia-backend:new-tag
# Keel will detect and update within 1 minute
```

#### For GitOps:
```bash
# Edit kubernetes/gitops/kustomization.yaml
# Update image tags and commit
git add kubernetes/gitops/kustomization.yaml
git commit -m "Update images to new-tag"
git push
```

#### For CI/CD:
```bash
# Just push to main branch
git push origin main
# GitHub Actions will build, scan, and deploy
```

## 🏗️ Architecture

### Keel Annotations
```yaml
metadata:
  annotations:
    keel.sh/policy: all          # Update on any new tag
    keel.sh/trigger: poll        # Poll registry
    keel.sh/approvals: "0"       # No manual approval
    keel.sh/pollSchedule: "@every 1m"  # Check interval
```

### GitOps Structure
```
kubernetes/gitops/
├── kustomization.yaml          # Main configuration
├── patches/
│   ├── production-resources.yaml   # Resource limits
│   └── gpu-node-selectors.yaml     # GPU placement
└── argocd/
    └── sophia-app.yaml         # ArgoCD app (optional)
```

## 🖥️ GPU Node Placement

The automation respects GPU node selectors:

| Service | GPU Type | Node |
|---------|----------|------|
| AI Core | GH200 | sophia-ai-core |
| Data Pipeline | A100 | sophia-data-pipeline |
| MCP Servers | A6000 | sophia-mcp-orchestrator |

## 🔒 Security Features

1. **Image Scanning**: Trivy scans on every build
2. **RBAC**: Proper permissions for automation tools
3. **Secret Management**: Uses Pulumi ESC
4. **Audit Trail**: All changes tracked in Git

## 📊 Monitoring

### View Keel Logs
```bash
kubectl -n keel logs deployment/keel -f
```

### Check Deployment Status
```bash
kubectl -n sophia-ai-prod get deployments
kubectl -n sophia-ai-prod get pods
```

### View Update History
```bash
kubectl -n sophia-ai-prod rollout history deployment/sophia-backend
```

## 🎯 Best Practices Implemented

1. **Immutable Infrastructure**: New images trigger new deployments
2. **Rolling Updates**: Zero-downtime deployments
3. **Health Checks**: Readiness/liveness probes
4. **Resource Limits**: CPU/memory constraints
5. **GPU Optimization**: Proper node selection and resource allocation
6. **Automated Rollback**: On deployment failure

## 🚨 Troubleshooting

### Keel Not Updating
```bash
# Check Keel logs
kubectl -n keel logs deployment/keel

# Verify annotations
kubectl -n sophia-ai-prod get deployment sophia-backend -o yaml | grep -A5 annotations

# Check Docker Hub connectivity
kubectl -n keel exec deployment/keel -- curl -I https://hub.docker.com
```

### GitOps Not Syncing
```bash
# Check kustomize build
kubectl kustomize kubernetes/gitops/

# Verify image tags
grep -A2 "images:" kubernetes/gitops/kustomization.yaml
```

### Deployment Failed
```bash
# Check events
kubectl -n sophia-ai-prod describe deployment sophia-backend

# View pod logs
kubectl -n sophia-ai-prod logs -l app=sophia-backend

# Rollback if needed
kubectl -n sophia-ai-prod rollout undo deployment/sophia-backend
```

## 📈 Benefits

1. **Automated Updates**: No manual intervention required
2. **Version Control**: All changes tracked
3. **Security**: Automated vulnerability scanning
4. **Reliability**: Health checks and rollbacks
5. **Scalability**: Easy to add new services
6. **Compliance**: Full audit trail

## 🎉 Summary

You now have three ways to deploy with automation:

1. **Keel**: Simplest, polls for new images
2. **GitOps**: Best for production, version controlled
3. **CI/CD**: Fully automated pipeline

All methods support:
- GPU workload placement
- Automatic updates
- Security scanning
- Health monitoring
- Easy rollbacks

Choose based on your needs:
- **Development**: Use Keel for rapid iteration
- **Production**: Use GitOps for control and audit
- **Enterprise**: Use full CI/CD pipeline 