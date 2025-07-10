# 🚀 Sophia AI K3s Deployment Checklist

## 📋 Pre-Deployment Verification

### Infrastructure Requirements
- [x] **Lambda Labs Instance**: 192.222.58.232 (H100 GPU)
- [x] **GitHub Actions**: Configured with organization secrets
- [x] **Docker Hub Registry**: scoobyjava15 authenticated
- [x] **Pulumi ESC**: Environment configuration synced
- [x] **K3s**: Ready on Lambda Labs instance
- [x] **kubectl**: Configured for remote access

### Configuration Files
- [x] **k8s/**: Kubernetes manifests and Kustomization files
- [x] **GitHub Workflows**: `.github/workflows/deploy-*.yml`
- [x] **Secrets**: All managed via Pulumi ESC

## 🚀 Deployment Steps

### Step 1: Verify GitHub Secrets
```bash
# All secrets should be configured at organization level:
# - DOCKER_HUB_USERNAME
# - DOCKER_HUB_ACCESS_TOKEN  
# - LAMBDA_PRIVATE_SSH_KEY
# - PULUMI_ACCESS_TOKEN
```

### Step 2: Initialize K3s Cluster (First Time Only)
```bash
# On Lambda Labs instance
curl -sfL https://get.k3s.io | sh -
# Get kubeconfig for remote access
sudo cat /etc/rancher/k3s/k3s.yaml
```

### Step 3: Deploy via GitHub Actions
```bash
# Push to main branch triggers deployment
git add .
git commit -m "Deploy: Update configuration"
git push origin main

# Monitor deployment
# Go to: https://github.com/[org]/[repo]/actions
```

### Step 4: Verify Deployment
```bash
# Check pod status
kubectl get pods -n sophia-ai-prod

# Check services
kubectl get svc -n sophia-ai-prod

# Check MCP servers
kubectl get pods -n mcp-servers

# View logs
kubectl logs -n sophia-ai-prod deployment/backend-api
```

## 📊 Monitoring

### Health Checks
```bash
# Backend API
curl https://api.sophia-ai.com/health

# MCP Gateway  
curl https://mcp.sophia-ai.com/health

# Individual MCP servers
for port in {9000..9015}; do
  echo "Checking MCP server on port $port"
  curl http://192.222.58.232:$port/health
done
```

### Resource Usage
```bash
# Overall cluster resources
kubectl top nodes

# Pod resource usage
kubectl top pods -n sophia-ai-prod

# GPU utilization
nvidia-smi
```

### Logs
```bash
# Backend logs
kubectl logs -n sophia-ai-prod -l app=backend-api --tail=100 -f

# MCP Gateway logs
kubectl logs -n mcp-servers -l app=mcp-gateway --tail=100 -f

# All MCP server logs
kubectl logs -n mcp-servers -l tier=mcp --tail=50
```

## 🔄 Common Operations

### Update Deployment
```bash
# Via GitHub Actions (recommended)
git push origin main

# Manual update (emergency only)
kubectl apply -k k8s/overlays/production
```

### Scale Services
```bash
# Scale backend
kubectl scale deployment backend-api -n sophia-ai-prod --replicas=3

# Scale MCP servers
kubectl scale deployment -n mcp-servers -l tier=mcp --replicas=2
```

### Restart Services
```bash
# Restart backend
kubectl rollout restart deployment/backend-api -n sophia-ai-prod

# Restart all MCP servers
kubectl rollout restart deployment -n mcp-servers
```

### View Configuration
```bash
# Current deployments
kubectl get deployments -A

# ConfigMaps
kubectl get configmaps -n sophia-ai-prod

# Secrets (names only)
kubectl get secrets -n sophia-ai-prod
```

## 🚨 Troubleshooting

### Pod Issues
```bash
# Describe pod for events
kubectl describe pod [pod-name] -n [namespace]

# Get pod logs
kubectl logs [pod-name] -n [namespace] --previous

# Execute into pod
kubectl exec -it [pod-name] -n [namespace] -- /bin/bash
```

### Service Connectivity
```bash
# Test service DNS
kubectl run test-pod --image=busybox -it --rm --restart=Never -- \
  nslookup backend-api.sophia-ai-prod.svc.cluster.local

# Port forward for local testing
kubectl port-forward -n sophia-ai-prod svc/backend-api 8000:8000
```

### Resource Constraints
```bash
# Check resource quotas
kubectl describe resourcequota -n sophia-ai-prod

# Check persistent volumes
kubectl get pv
kubectl get pvc -A
```

## 🔥 Emergency Procedures

### Rollback Deployment
```bash
# Via kubectl
kubectl rollout undo deployment/backend-api -n sophia-ai-prod

# Check rollout history
kubectl rollout history deployment/backend-api -n sophia-ai-prod
```

### Emergency Access
```bash
# Direct SSH to Lambda Labs
ssh root@192.222.58.232

# Check K3s status
sudo systemctl status k3s

# View K3s logs
sudo journalctl -u k3s -f
```

### Complete Reset
```bash
# WARNING: This removes everything
kubectl delete namespace sophia-ai-prod
kubectl delete namespace mcp-servers

# Redeploy
kubectl apply -k k8s/overlays/production
```

## ✅ Post-Deployment Validation

- [ ] All pods running (kubectl get pods -A)
- [ ] Services accessible via ingress
- [ ] Health endpoints responding
- [ ] Logs showing normal operation
- [ ] GPU resources properly allocated
- [ ] Monitoring stack operational
- [ ] Secrets properly mounted
- [ ] Persistent volumes attached

## 📚 Documentation

- K3s Documentation: https://docs.k3s.io/
- Kubernetes Docs: https://kubernetes.io/docs/
- GitHub Actions: `.github/workflows/`
- Architecture: `docs/system_handbook/`
