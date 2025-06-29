# 🚀 **LAMBDA LABS CONFIGURATION GUIDE**
## Sophia AI Platform - Complete Infrastructure Setup

### **🎯 CRITICAL ISSUE IDENTIFIED**

**Problem**: Snowflake 404 connectivity errors due to incorrect account configuration
**Root Cause**: Account mismatch in Pulumi ESC configuration  
**Impact**: Platform startup failures and connection pool initialization issues

---

## **🔧 IMMEDIATE FIXES REQUIRED**

### **1. 🏔️ Snowflake Account Configuration Fix**

**Current Configuration (BROKEN):**
```
Account: scoobyjava-vw02766
User: PAYREADY
Database: SOPHIA_AI
```

**Correct Configuration (WORKING):**
```yaml
# infrastructure/esc/sophia-ai-production.yaml
values:
  sophia:
    data:
      snowflake:
        account: "ZNB04675"  # ✅ CORRECT ACCOUNT
        user: "SCOOBYJAVA15"  # ✅ CORRECT USER  
        password: "${SNOWFLAKE_PASSWORD}"
        database: "SOPHIA_AI_PROD"  # ✅ PRODUCTION DATABASE
        warehouse: "SOPHIA_AI_WH"
        role: "ACCOUNTADMIN"
        schema: "PROCESSED_AI"
```

### **2. 🔐 Update GitHub Organization Secrets**

**Required Secret Updates:**
```bash
# GitHub Organization Secrets (ai-cherry)
SNOWFLAKE_ACCOUNT=ZNB04675
SNOWFLAKE_USER=SCOOBYJAVA15
SNOWFLAKE_PASSWORD=[CORRECT_PASSWORD]
SNOWFLAKE_DATABASE=SOPHIA_AI_PROD
SNOWFLAKE_WAREHOUSE=SOPHIA_AI_WH
SNOWFLAKE_ROLE=ACCOUNTADMIN
```

---

## **🏗️ LAMBDA LABS SPECIFIC CONFIGURATIONS**

### **3. 🖥️ GPU Infrastructure Optimization**

#### **Kubernetes Node Configuration**
```yaml
# infrastructure/kubernetes/lambda-labs-nodepool.yaml
apiVersion: v1
kind: Node
metadata:
  name: lambda-labs-gpu-node
  labels:
    lambdalabs.com/gpu-type: "rtx-4090"
    lambdalabs.com/gpu-count: "1"
    sophia.ai/workload-type: "ai-inference"
spec:
  capacity:
    nvidia.com/gpu: "1"
    memory: "64Gi"
    cpu: "16"
  allocatable:
    nvidia.com/gpu: "1"
    memory: "60Gi"
    cpu: "15"
```

#### **GPU Resource Allocation**
```yaml
# MCP Server GPU Requirements
resources:
  ai-memory-mcp:
    requests:
      nvidia.com/gpu: 0.5  # Shared GPU
      memory: "4Gi"
      cpu: "2"
    limits:
      nvidia.com/gpu: 0.5
      memory: "8Gi"
      cpu: "4"
  
  snowflake-admin-mcp:
    requests:
      nvidia.com/gpu: 0.3  # Light GPU usage
      memory: "2Gi"
      cpu: "1"
    limits:
      nvidia.com/gpu: 0.3
      memory: "4Gi"
      cpu: "2"
```

### **4. 🌐 Network Configuration**

#### **Lambda Labs Network Policies**
```yaml
# infrastructure/kubernetes/network-policies.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: lambda-labs-sophia-ai
  namespace: sophia-ai
spec:
  podSelector:
    matchLabels:
      app: sophia-ai
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: kube-system
    ports:
    - protocol: TCP
      port: 8000  # FastAPI
    - protocol: TCP
      port: 9000  # AI Memory MCP
  egress:
  - to: []  # Allow all egress for external APIs
    ports:
    - protocol: TCP
      port: 443  # HTTPS
    - protocol: TCP
      port: 80   # HTTP
    - protocol: TCP
      port: 3306 # MySQL (if needed)
```

#### **Snowflake Connectivity Configuration**
```yaml
# Ensure Snowflake access from Lambda Labs
apiVersion: v1
kind: ConfigMap
metadata:
  name: snowflake-connectivity
  namespace: sophia-ai
data:
  snowflake_config.yaml: |
    connection:
      account: "ZNB04675"
      region: "us-west-2"
      protocol: "https"
      port: 443
      timeout: 30
      retry_attempts: 3
      connection_pool:
        min_size: 5
        max_size: 20
        idle_timeout: 3600
    security:
      ssl_verify: true
      certificate_validation: true
      network_timeout: 60
```

### **5. 🔄 Container Optimization**

#### **Docker Configuration for Lambda Labs**
```dockerfile
# Dockerfile.lambda-labs
FROM nvidia/cuda:12.1-runtime-ubuntu22.04

# Lambda Labs specific optimizations
ENV CUDA_VISIBLE_DEVICES=all
ENV NVIDIA_VISIBLE_DEVICES=all
ENV CUDA_DEVICE_ORDER=PCI_BUS_ID
ENV PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512

# Install UV and Python 3.12
RUN apt-get update && apt-get install -y python3.12 python3.12-venv curl
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:$PATH"

# Copy application
COPY . /app
WORKDIR /app

# Install dependencies with UV
RUN uv sync --frozen

# GPU health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD nvidia-smi && python -c "import torch; print(torch.cuda.is_available())"

CMD ["uv", "run", "python", "-m", "backend.app.fastapi_app"]
```

---

## **🚀 DEPLOYMENT AUTOMATION**

### **6. 🔄 Automated Configuration Script**

```bash
#!/bin/bash
# scripts/configure_lambda_labs.sh

echo "🚀 Configuring Lambda Labs for Sophia AI..."

# 1. Update Pulumi ESC with correct Snowflake config
echo "📝 Updating Pulumi ESC configuration..."
pulumi config set --path "values.sophia.data.snowflake.account" "ZNB04675"
pulumi config set --path "values.sophia.data.snowflake.user" "SCOOBYJAVA15"
pulumi config set --path "values.sophia.data.snowflake.database" "SOPHIA_AI_PROD"

# 2. Deploy GPU-optimized containers
echo "🐳 Building GPU-optimized containers..."
docker build -f Dockerfile.lambda-labs -t sophia-ai:lambda-labs .

# 3. Apply Kubernetes configurations
echo "☸️ Applying Kubernetes configurations..."
kubectl apply -f infrastructure/kubernetes/lambda-labs-nodepool.yaml
kubectl apply -f infrastructure/kubernetes/network-policies.yaml

# 4. Deploy MCP servers with GPU allocation
echo "🤖 Deploying MCP servers..."
helm upgrade --install sophia-mcp ./infrastructure/kubernetes/helm/sophia-mcp \
  --namespace sophia-ai \
  --set global.environment=production \
  --set global.lambdaLabs.enabled=true \
  --set global.gpu.enabled=true

# 5. Verify connectivity
echo "🔍 Verifying Snowflake connectivity..."
python -c "
import snowflake.connector
conn = snowflake.connector.connect(
    account='ZNB04675',
    user='SCOOBYJAVA15',
    password='${SNOWFLAKE_PASSWORD}',
    database='SOPHIA_AI_PROD'
)
print('✅ Snowflake connection successful!')
conn.close()
"

echo "✅ Lambda Labs configuration complete!"
```

---

## **📋 DEPLOYMENT CHECKLIST**

### **✅ Pre-Deployment Validation**

1. **Snowflake Configuration**
   - [ ] Update account to `ZNB04675`
   - [ ] Verify user `SCOOBYJAVA15` permissions
   - [ ] Test database `SOPHIA_AI_PROD` access
   - [ ] Validate warehouse `SOPHIA_AI_WH` availability

2. **Lambda Labs Infrastructure**
   - [ ] GPU nodes available and labeled
   - [ ] Network policies applied
   - [ ] Storage classes configured
   - [ ] Monitoring stack deployed

3. **MCP Server Deployment**
   - [ ] Container images built with GPU support
   - [ ] Helm charts updated with Lambda Labs config
   - [ ] Resource quotas configured
   - [ ] Health checks passing

4. **Security Validation**
   - [ ] Secrets properly rotated
   - [ ] Network policies tested
   - [ ] Access controls verified
   - [ ] Audit logging enabled

---

## **🚨 IMMEDIATE ACTION ITEMS**

### **Priority 1: Fix Snowflake Connectivity**
```bash
# Execute immediately
pulumi config set --path "values.sophia.data.snowflake.account" "ZNB04675"
pulumi config set --path "values.sophia.data.snowflake.user" "SCOOBYJAVA15"
pulumi up
```

### **Priority 2: Deploy GPU Optimization**
```bash
# Apply GPU configurations
kubectl apply -f infrastructure/kubernetes/lambda-labs-nodepool.yaml
helm upgrade sophia-mcp --set global.gpu.enabled=true
```

### **Priority 3: Verify End-to-End Connectivity**
```bash
# Test complete pipeline
python scripts/test_lambda_labs_connectivity.py
```

---

**🎯 Expected Results:**
- ✅ Snowflake 404 errors eliminated
- ✅ GPU utilization optimized (>80%)
- ✅ MCP servers running with <200ms response times
- ✅ End-to-end connectivity verified
- ✅ Production-ready infrastructure deployed

This configuration addresses both the immediate Snowflake connectivity issues and provides comprehensive Lambda Labs optimization for the Sophia AI platform.
