# 🚀 Sophia AI K3s Deployment Guide

## Overview

This guide covers the deployment of Sophia AI platform using K3s (lightweight Kubernetes) on Lambda Labs infrastructure. K3s provides a production-ready Kubernetes distribution optimized for edge computing and resource-constrained environments.

## 🏗️ Architecture Overview

### Infrastructure Stack
- **Orchestration**: K3s (Lightweight Kubernetes)
- **Compute**: Lambda Labs H100 GPU instances
- **Container Registry**: Docker Hub (scoobyjava15)
- **Ingress**: Traefik (built-in with K3s)
- **Secrets**: Pulumi ESC with automatic K8s sync
- **CI/CD**: GitHub Actions

### Deployment Structure
```
k8s/
├── base/                    # Base Kubernetes manifests
│   ├── backend/            # Backend API resources
│   ├── database/           # PostgreSQL and Redis
│   ├── mcp-gateway/        # MCP Gateway service
│   └── mcp-servers/        # All 16 MCP servers
├── overlays/               # Environment-specific configs
│   ├── production/         # Production overlay
│   └── staging/            # Staging overlay
└── helm/                   # Helm charts (optional)
```

## 📋 Prerequisites

### 1. Lambda Labs Access
- SSH access to Lambda Labs instance (192.222.58.232)
- Root or sudo privileges
- K3s installed and running

### 2. GitHub Secrets Configuration
Required organization secrets:
- `DOCKER_HUB_USERNAME`
- `DOCKER_HUB_ACCESS_TOKEN`
- `LAMBDA_PRIVATE_SSH_KEY`
- `K3S_KUBECONFIG` (base64 encoded)
- `PULUMI_ACCESS_TOKEN`

### 3. Local Development Tools
```bash
# Install kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl
sudo mv kubectl /usr/local/bin/

# Install kustomize
curl -s "https://raw.githubusercontent.com/kubernetes-sigs/kustomize/master/hack/install_kustomize.sh" | bash
sudo mv kustomize /usr/local/bin/
```

## 🚀 Deployment Methods

### Method 1: GitHub Actions (Recommended)

All deployments should go through GitHub Actions for consistency and security.

```bash
# Ensure you're on main branch
git checkout main

# Make your changes
git add .
git commit -m "feat: Update configuration"

# Push triggers automatic deployment
git push origin main

# Monitor deployment
# Visit: https://github.com/[your-org]/sophia-ai/actions
```

### Method 2: Manual Deployment (Emergency Only)

Use only when GitHub Actions is unavailable:

```bash
# 1. Configure kubectl
export KUBECONFIG=~/.kube/k3s-lambda-labs
# Add K3s cluster config to the file

# 2. Apply manifests
kubectl apply -k k8s/overlays/production

# 3. Monitor rollout
kubectl rollout status deployment -n sophia-ai-prod
kubectl rollout status deployment -n mcp-servers
```

## 🏗️ Initial K3s Setup

### Install K3s on Lambda Labs

```bash
# SSH to Lambda Labs
ssh root@192.222.58.232

# Install K3s with GPU support
curl -sfL https://get.k3s.io | sh -s - \
  --disable traefik \
  --write-kubeconfig-mode 644

# Install NVIDIA device plugin for GPU support
kubectl apply -f https://raw.githubusercontent.com/NVIDIA/k8s-device-plugin/v0.13.0/nvidia-device-plugin.yml

# Install Traefik with custom config
kubectl apply -f k8s/infrastructure/traefik/

# Create namespaces
kubectl create namespace sophia-ai-prod
kubectl create namespace mcp-servers
kubectl create namespace monitoring

# Label namespaces
kubectl label namespace sophia-ai-prod environment=production
kubectl label namespace mcp-servers environment=production
```

### Configure Remote Access

```bash
# On Lambda Labs instance
sudo cat /etc/rancher/k3s/k3s.yaml

# Copy the output and on your local machine:
# 1. Replace 'server: https://127.0.0.1:6443' with 'server: https://192.222.58.232:6443'
# 2. Save to ~/.kube/k3s-lambda-labs
# 3. Set appropriate permissions
chmod 600 ~/.kube/k3s-lambda-labs

# Test connection
export KUBECONFIG=~/.kube/k3s-lambda-labs
kubectl get nodes
```

## 📦 Application Deployment

### Deploy Core Services

```bash
# Deploy using Kustomize
kubectl apply -k k8s/overlays/production

# This deploys:
# - Backend API
# - PostgreSQL database
# - Redis cache
# - MCP Gateway
# - All 16 MCP servers
```

### Verify Deployment

```bash
# Check deployments
kubectl get deployments -A

# Check pods
kubectl get pods -n sophia-ai-prod
kubectl get pods -n mcp-servers

# Check services
kubectl get svc -A

# Check ingress
kubectl get ingress -A
```

## 🔒 Secret Management

All secrets are managed through Pulumi ESC and automatically synced to K3s:

```bash
# List secrets (names only)
kubectl get secrets -n sophia-ai-prod

# Secrets are created automatically by Pulumi ESC operator
# Never create secrets manually
```

### Secret Structure
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: sophia-ai-secrets
  namespace: sophia-ai-prod
type: Opaque
data:
  # All values are base64 encoded and synced from Pulumi ESC
  DATABASE_URL: <auto-synced>
  REDIS_URL: <auto-synced>
  OPENAI_API_KEY: <auto-synced>
  # ... etc
```

## 📊 Monitoring and Logging

### View Logs

```bash
# Backend API logs
kubectl logs -n sophia-ai-prod deployment/backend-api -f

# MCP Gateway logs
kubectl logs -n mcp-servers deployment/mcp-gateway -f

# All MCP server logs
kubectl logs -n mcp-servers -l tier=mcp --tail=100

# Previous container logs (after restart)
kubectl logs -n sophia-ai-prod deployment/backend-api --previous
```

### Resource Monitoring

```bash
# Node resources
kubectl top nodes

# Pod resources
kubectl top pods -n sophia-ai-prod
kubectl top pods -n mcp-servers

# GPU usage (on Lambda Labs node)
nvidia-smi

# Detailed pod resource usage
kubectl describe pod -n sophia-ai-prod
```

### Health Checks

```bash
# Service health endpoints
curl https://api.sophia-ai.com/health
curl https://mcp.sophia-ai.com/health

# Individual MCP server health
for i in {9000..9015}; do
  echo "MCP Server on port $i:"
  curl -s http://192.222.58.232:$i/health | jq .
done
```

## 🔄 Common Operations

### Scale Services

```bash
# Scale backend API
kubectl scale deployment backend-api -n sophia-ai-prod --replicas=3

# Scale all MCP servers
kubectl scale deployment -n mcp-servers -l tier=mcp --replicas=2

# Auto-scaling (if HPA configured)
kubectl get hpa -n sophia-ai-prod
```

### Update Services

```bash
# Update image (triggers rolling update)
kubectl set image deployment/backend-api -n sophia-ai-prod \
  backend-api=scoobyjava15/sophia-backend:v2.0.0

# Update using new manifests
kubectl apply -k k8s/overlays/production

# Force restart (keeps same image)
kubectl rollout restart deployment/backend-api -n sophia-ai-prod
```

### Rollback

```bash
# Check rollout history
kubectl rollout history deployment/backend-api -n sophia-ai-prod

# Rollback to previous version
kubectl rollout undo deployment/backend-api -n sophia-ai-prod

# Rollback to specific revision
kubectl rollout undo deployment/backend-api -n sophia-ai-prod --to-revision=2
```

## 🚨 Troubleshooting

### Pod Issues

```bash
# Get pod details and events
kubectl describe pod [pod-name] -n [namespace]

# Common issues to check:
# - ImagePullBackOff: Check Docker Hub credentials
# - CrashLoopBackOff: Check logs for startup errors
# - Pending: Check resource constraints and node capacity

# Interactive debugging
kubectl run debug --image=busybox -it --rm --restart=Never -- sh
```

### Network Issues

```bash
# Test DNS resolution
kubectl run -it --rm debug --image=busybox --restart=Never -- \
  nslookup backend-api.sophia-ai-prod.svc.cluster.local

# Test service connectivity
kubectl run -it --rm debug --image=nicolaka/netshoot --restart=Never -- \
  curl backend-api.sophia-ai-prod.svc.cluster.local:8000/health

# Port forwarding for local testing
kubectl port-forward -n sophia-ai-prod svc/backend-api 8000:8000
```

### Resource Constraints

```bash
# Check node capacity
kubectl describe nodes

# Check resource quotas
kubectl describe resourcequota -A

# Check PVC status
kubectl get pvc -A

# Check GPU allocation
kubectl describe pod -n sophia-ai-prod | grep -A5 "nvidia.com/gpu"
```

## 🔧 Maintenance

### K3s Updates

```bash
# On Lambda Labs instance
curl -sfL https://get.k3s.io | sh -

# Verify version
kubectl version
```

### Cleanup Operations

```bash
# Remove completed jobs
kubectl delete jobs --field-selector status.successful=1 -A

# Remove evicted pods
kubectl delete pods --field-selector status.phase=Failed -A

# Clean up old replica sets
kubectl delete rs -A --field-selector status.replicas=0
```

### Backup

```bash
# Backup K3s cluster data
# On Lambda Labs instance
sudo tar -czf k3s-backup-$(date +%Y%m%d).tar.gz \
  /var/lib/rancher/k3s/server/db \
  /etc/rancher/k3s

# Backup application data
kubectl exec -n sophia-ai-prod deployment/postgres -- \
  pg_dump -U postgres sophia_ai > sophia-backup-$(date +%Y%m%d).sql
```

## 📈 Performance Optimization

### Resource Limits

Ensure all deployments have appropriate resource limits:

```yaml
resources:
  requests:
    memory: "256Mi"
    cpu: "100m"
  limits:
    memory: "512Mi"
    cpu: "500m"
    nvidia.com/gpu: 1  # For GPU workloads
```

### Node Affinity

Use node affinity for GPU workloads:

```yaml
affinity:
  nodeAffinity:
    requiredDuringSchedulingIgnoredDuringExecution:
      nodeSelectorTerms:
      - matchExpressions:
        - key: nvidia.com/gpu
          operator: Exists
```

## 🚀 Best Practices

1. **Always use GitHub Actions** for production deployments
2. **Monitor resource usage** to prevent OOM kills
3. **Use resource limits** on all containers
4. **Implement health checks** for all services
5. **Use rolling updates** for zero-downtime deployments
6. **Keep manifests in Git** for version control
7. **Use Kustomize overlays** for environment differences
8. **Regular backups** of stateful data
9. **Monitor logs** for early issue detection
10. **Document changes** in commit messages

## 📚 Additional Resources

- [K3s Documentation](https://docs.k3s.io/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Kustomize Documentation](https://kustomize.io/)
- [Traefik Documentation](https://doc.traefik.io/traefik/)
- Project Architecture: `docs/system_handbook/`
- MCP Server Docs: `docs/06-mcp-servers/`

## 🆘 Emergency Contacts

- **Lambda Labs Support**: support@lambdalabs.com
- **GitHub Actions Status**: https://www.githubstatus.com/
- **Docker Hub Status**: https://status.docker.com/

---

**Remember**: All production deployments should go through GitHub Actions. Manual deployment should only be used in emergency situations. 