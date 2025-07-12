# Lambda Labs K8s Deployment Guide - Phase 4 Infrastructure

## 🚀 Quick Start

This guide deploys the GPU-powered memory architecture to Lambda Labs K8s cluster.

### Prerequisites

1. **Lambda Labs Access**
   ```bash
   # SSH into Lambda Labs control plane
   ssh ubuntu@192.222.58.232 -i ~/.ssh/lambda_labs_key
   
   # Copy kubeconfig locally
   scp ubuntu@192.222.58.232:~/.kube/config ~/.kube/lambda-k3s-config
   export KUBECONFIG=~/.kube/lambda-k3s-config
   ```

2. **Pulumi Configuration**
   ```bash
   cd infrastructure
   pulumi stack select prod
   pulumi config set kubernetes:kubeconfig ~/.kube/lambda-k3s-config
   ```

3. **Container Registry**
   ```bash
   # Login to Docker Hub
   docker login -u scoobyjava15
   
   # Build and push Lambda inference image
   cd infrastructure/services
   docker build -f lambda_inference.Dockerfile -t scoobyjava15/lambda-inference:latest .
   docker push scoobyjava15/lambda-inference:latest
   ```

## 🎯 Deployment Steps

### Step 1: Deploy Infrastructure

```bash
# Deploy to production
cd infrastructure
pulumi up --stack prod --yes

# Expected output:
# + 26 resources created
# - Weaviate deployment (3 replicas)
# - Redis StatefulSet (3 nodes)
# - PostgreSQL deployment (2 replicas)
# - Lambda inference service (2 replicas)
```

### Step 2: Validate Deployment

```bash
# Check pod status
kubectl get pods -n sophia-ai-prod

# Expected output:
NAME                                READY   STATUS    AGE
weaviate-7b9f6d4c5-xxx             1/1     Running   2m
weaviate-7b9f6d4c5-yyy             1/1     Running   2m
weaviate-7b9f6d4c5-zzz             1/1     Running   2m
redis-0                            1/1     Running   3m
redis-1                            1/1     Running   2m
redis-2                            1/1     Running   1m
postgresql-5d7f8b9c4-xxx           1/1     Running   3m
postgresql-5d7f8b9c4-yyy           1/1     Running   2m
lambda-inference-6c8d9f5b7-xxx     1/1     Running   2m
lambda-inference-6c8d9f5b7-yyy     1/1     Running   1m
```

### Step 3: Configure GPU Resources

```bash
# Verify GPU allocation
kubectl describe nodes | grep -A 5 "nvidia.com/gpu"

# Check GPU usage
kubectl exec -n sophia-ai-prod deployment/lambda-inference -- nvidia-smi
```

## 🔧 Service Endpoints

### Internal Cluster Access

```yaml
# From within K8s pods
Weaviate: http://weaviate-service.sophia-ai-prod:8080
Redis: redis://redis-service.sophia-ai-prod:6379
PostgreSQL: postgresql://postgres:${PG_PASSWORD}@postgresql-service.sophia-ai-prod:5432/sophia_vectors
Lambda Inference: http://lambda-inference-service.sophia-ai-prod:8080
```

### External Access (via NodePort)

```bash
# Create NodePort services for external access
kubectl expose service weaviate-service \
  --type=NodePort \
  --name=weaviate-external \
  --port=8080 \
  --target-port=8080 \
  -n sophia-ai-prod

# Get external endpoints
kubectl get services -n sophia-ai-prod

# Access from outside:
# Weaviate: http://192.222.58.232:30080
# Lambda Inference: http://192.222.58.232:30081
```

## 📊 Performance Validation

### Run Benchmarks

```bash
# Execute benchmark suite
python scripts/benchmark_memory_performance.py \
  --weaviate-url http://192.222.58.232:30080 \
  --redis-url redis://192.222.58.232:30379 \
  --postgres-url postgresql://192.222.58.232:30432/sophia_vectors

# Expected results:
# ✅ Embeddings: <50ms (B200 GPU)
# ✅ Vector search: <50ms (Weaviate)
# ✅ Cache hits: >80% (Redis)
# ✅ Hybrid queries: <100ms (pgvector)
```

### Load Testing

```bash
# Ingest 1k records via Estuary
python scripts/load_test_etl.py \
  --records 1000 \
  --parallel 10

# Monitor performance
watch -n 1 kubectl top pods -n sophia-ai-prod
```

## 🛡️ Security Configuration

### 1. OIDC Authentication for Weaviate

```bash
# Update Weaviate auth config
kubectl create secret generic weaviate-oidc \
  --from-literal=issuer=https://auth.sophia-ai.com \
  --from-literal=client-id=sophia-ai \
  --from-literal=admin-users=admin@sophia-ai.com \
  -n sophia-ai-prod

# Patch deployment
kubectl set env deployment/weaviate \
  AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED=false \
  AUTHENTICATION_OIDC_ENABLED=true \
  -n sophia-ai-prod
```

### 2. Network Policies

```yaml
# Apply network isolation
kubectl apply -f - <<EOF
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: sophia-ai-network-policy
  namespace: sophia-ai-prod
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: sophia-ai-prod
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: sophia-ai-prod
  - to:
    - namespaceSelector: {}
    ports:
    - protocol: TCP
      port: 53  # DNS
EOF
```

## 🔍 Monitoring Setup

### Prometheus Metrics

```bash
# Deploy Prometheus
kubectl apply -f infrastructure/monitoring/prometheus-deployment.yaml

# Access Prometheus UI
kubectl port-forward -n sophia-ai-prod svc/prometheus 9090:9090
# http://localhost:9090
```

### Grafana Dashboards

```bash
# Deploy Grafana
kubectl apply -f infrastructure/monitoring/grafana-deployment.yaml

# Import dashboards
# 1. Weaviate Performance (ID: 15441)
# 2. Redis Monitoring (ID: 11835)
# 3. PostgreSQL Statistics (ID: 9628)
# 4. GPU Utilization (Custom)
```

## 🚨 Troubleshooting

### Common Issues

1. **GPU Not Available**
   ```bash
   # Check node labels
   kubectl get nodes --show-labels | grep gpu
   
   # Add GPU taint toleration
   kubectl patch deployment lambda-inference \
     -p '{"spec":{"template":{"spec":{"tolerations":[{"key":"nvidia.com/gpu","operator":"Exists","effect":"NoSchedule"}]}}}}' \
     -n sophia-ai-prod
   ```

2. **PVC Pending**
   ```bash
   # Check storage class
   kubectl get storageclass
   
   # Create if missing
   kubectl apply -f - <<EOF
   apiVersion: storage.k8s.io/v1
   kind: StorageClass
   metadata:
     name: fast-ssd
   provisioner: rancher.io/local-path
   reclaimPolicy: Delete
   volumeBindingMode: WaitForFirstConsumer
   EOF
   ```

3. **Memory Pressure**
   ```bash
   # Increase resource limits
   kubectl set resources deployment/weaviate \
     --limits=memory=32Gi \
     --requests=memory=16Gi \
     -n sophia-ai-prod
   ```

## 📈 Scaling Configuration

### Horizontal Pod Autoscaling

```bash
# Verify HPA status
kubectl get hpa -n sophia-ai-prod

# Manual scaling if needed
kubectl scale deployment/weaviate --replicas=5 -n sophia-ai-prod
kubectl scale statefulset/redis --replicas=5 -n sophia-ai-prod
```

### GPU Autoscaling

```bash
# Add more GPU nodes if needed
# Contact Lambda Labs support for node scaling
# Current limit: 8 GPUs across cluster
```

## 🔄 Rollback Procedure

```bash
# If deployment fails
pulumi destroy --stack prod --yes

# Or selective rollback
kubectl rollout undo deployment/weaviate -n sophia-ai-prod
kubectl rollout undo statefulset/redis -n sophia-ai-prod
```

## ✅ Post-Deployment Checklist

- [ ] All pods running and ready
- [ ] GPU resources allocated correctly
- [ ] Services accessible internally
- [ ] External endpoints configured
- [ ] Monitoring stack deployed
- [ ] Alerts configured in Prometheus
- [ ] Benchmarks meet targets (<50ms)
- [ ] Security policies applied
- [ ] Backup strategy configured
- [ ] Documentation updated

## 🎉 Success Metrics

When deployment is successful, you should see:

```
✅ Weaviate P95 latency: <50ms
✅ Redis cache hit rate: >80%
✅ GPU utilization: 40-60%
✅ ETL throughput: >1000 records/min
✅ Zero failed pods
✅ All health checks passing
```

---

**Next Step**: Once validated, proceed to Phase 5 - MCP Refactor to integrate all 53 servers with the new memory architecture. 