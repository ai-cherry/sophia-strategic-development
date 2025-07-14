# 🚀 **LAMBDA LABS / KUBERNETES SPECIFIC SETUP REQUIREMENTS**
## Immediate Infrastructure Updates Needed

---

## 📋 **CRITICAL UPDATES REQUIRED**

### **1. GPU RESOURCE ALLOCATION FOR ALL MCP SERVERS**

#### **File:** `infrastructure/kubernetes/helm/sophia-mcp/values.yaml`
**SPECIFIC CHANGES NEEDED:**

```yaml
# ADD GPU RESOURCES TO EACH MCP SERVER:
mcpServers:
  aiMemory:
    resources:
      requests:
        nvidia.com/gpu: 0.25  # ADD THIS LINE
        memory: "512Mi"       # INCREASE FROM 256Mi
        cpu: "200m"           # INCREASE FROM 100m
      limits:
        nvidia.com/gpu: 0.25  # ADD THIS LINE
        memory: "2Gi"         # INCREASE FROM 1Gi
        cpu: "1000m"          # INCREASE FROM 500m

  modern_stackAdmin:
    resources:
      requests:
        nvidia.com/gpu: 0.25  # ADD THIS LINE
        memory: "512Mi"       # INCREASE FROM 256Mi
        cpu: "200m"           # INCREASE FROM 100m
      limits:
        nvidia.com/gpu: 0.25  # ADD THIS LINE
        memory: "2Gi"         # INCREASE FROM 1Gi
        cpu: "1000m"          # INCREASE FROM 500m

  # REPEAT FOR ALL MCP SERVERS: linear, asana, gong
```

#### **ADD LAMBDA LABS NODE SELECTOR:**
```yaml
# ADD TO ROOT LEVEL OF values.yaml:
nodeSelector:
  lambdalabs.com/gpu-type: "rtx-4090"
  lambdalabs.com/instance-type: "gpu_1x_a10"
  kubernetes.io/arch: amd64

tolerations:
  - key: "lambdalabs.com/gpu"
    operator: "Equal"
    value: "true"
    effect: "NoSchedule"
```

---

### **2. UPDATE DEPLOYMENT TEMPLATES WITH CUDA ENVIRONMENT**

#### **File:** `infrastructure/kubernetes/helm/sophia-mcp/templates/deployment.yaml`
**ADD CUDA ENVIRONMENT VARIABLES:**

```yaml
# FIND THIS SECTION (around line 85):
        env:
        - name: PORT
          value: "{{ $config.port }}"
        - name: ENVIRONMENT
          value: {{ $.Values.global.environment }}

# ADD THESE CUDA VARIABLES:
        - name: CUDA_VISIBLE_DEVICES
          value: "all"
        - name: NVIDIA_VISIBLE_DEVICES
          value: "all"
        - name: PYTORCH_CUDA_ALLOC_CONF
          value: "max_split_size_mb:512"
        - name: NVIDIA_DRIVER_CAPABILITIES
          value: "compute,utility"
```

---

### **3. UPDATE MCP SERVER DOCKERFILES FOR GPU SUPPORT**

#### **All MCP Server Dockerfiles Need GPU Base Image:**
**Files to Update:**
- `mcp-servers/ai_memory/Dockerfile`
- `mcp-servers/modern_stack/Dockerfile`
- `mcp-servers/codacy/Dockerfile`
- `mcp-servers/asana/Dockerfile`
- `mcp-servers/notion/Dockerfile`
- `mcp-servers/linear/Dockerfile`

**REPLACE CURRENT BASE IMAGE WITH:**
```dockerfile
FROM nvidia/cuda:12.1-runtime-ubuntu22.04

# Lambda Labs GPU optimization
ENV CUDA_VISIBLE_DEVICES=all
ENV NVIDIA_VISIBLE_DEVICES=all
ENV PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512
ENV NVIDIA_DRIVER_CAPABILITIES=compute,utility

# Install Python and UV
RUN apt-get update && apt-get install -y \
    python3.12 \
    python3.12-venv \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install UV
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:$PATH"

# GPU health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD nvidia-smi && python3 -c "import torch; print(torch.cuda.is_available())" || exit 1

# Copy application code
COPY . /app
WORKDIR /app

# Install dependencies with UV
RUN uv sync --frozen

CMD ["uv", "run", "python", "-m", "mcp_server"]
```

---

### **4. UPDATE CLEAN ARCHITECTURE DEPLOYMENT**

#### **File:** `infrastructure/kubernetes/clean-architecture/sophia-api-deployment.yaml`
**SPECIFIC LINE UPDATES:**

```yaml
# LINE 22: UPDATE NODE SELECTOR
      nodeSelector:
        lambdalabs.com/gpu-type: "rtx-4090"          # CHANGE FROM old selector
        lambdalabs.com/instance-type: "gpu_1x_a10"   # ADD THIS LINE

# LINE 67: ADD GPU RESOURCE ALLOCATION
        resources:
          requests:
            memory: "4Gi"
            cpu: "2"
            nvidia.com/gpu: 1                         # ADD THIS LINE
          limits:
            memory: "8Gi"
            cpu: "4"
            nvidia.com/gpu: 1                         # ADD THIS LINE

# LINE 169: UPDATE STORAGE CLASS
        storageClassName: lambda-labs-ssd             # CHANGE FROM gp3
```

---

## 🚀 **DEPLOYMENT COMMANDS**

### **Step 1: Update Helm Deployment with GPU Support**
```bash
helm upgrade --install sophia-mcp infrastructure/kubernetes/helm/sophia-mcp \
  --namespace sophia-ai \
  --set global.lambdaLabs.enabled=true \
  --set global.gpu.enabled=true \
  --set global.environment=production \
  --wait --timeout=600s
```

### **Step 2: Verify GPU Allocation**
```bash
kubectl get nodes -o custom-columns=NAME:.metadata.name,GPU:.status.allocatable."nvidia\.com/gpu"
kubectl get pods -n sophia-ai -o wide
```

### **Step 3: Test GPU Availability**
```bash
kubectl exec -it deployment/sophia-mcp-ai-memory -n sophia-ai -- nvidia-smi
kubectl exec -it deployment/sophia-mcp-ai-memory -n sophia-ai -- python -c "import torch; print(torch.cuda.is_available())"
```

---

## 🎯 **EXPECTED RESULTS AFTER IMPLEMENTATION**

### **GPU Utilization Metrics:**
- ✅ **GPU Allocation:** 4 GPUs shared across MCP servers (0.25 each)
- ✅ **GPU Utilization:** >80% average utilization
- ✅ **Performance Improvement:** 3-5x faster AI operations

### **Resource Optimization:**
- ✅ **CPU Allocation:** 16 cores total across MCP servers
- ✅ **Memory Allocation:** 32Gi total memory
- ✅ **Storage:** Lambda Labs SSD for optimal I/O

**🚀 THESE SPECIFIC UPDATES WILL OPTIMIZE SOPHIA AI FOR LAMBDA LABS GPU INFRASTRUCTURE**
