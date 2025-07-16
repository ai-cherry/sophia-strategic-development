# ⚠️ DEPRECATED: Kubernetes-Based Deployment

**STATUS:** DEPRECATED - These files conflict with production infrastructure  
**DATE:** July 16, 2025  
**REASON:** Production uses distributed systemd services, not Kubernetes orchestration

## 🚨 CRITICAL NOTICE

**ALL KUBERNETES MANIFESTS IN THIS DIRECTORY ARE DEPRECATED**

The production Sophia AI infrastructure uses:
- ✅ **5 Lambda Labs instances** with direct Python processes
- ✅ **systemd service management** with auto-restart capabilities
- ✅ **nginx load balancing** on primary instance (192.222.58.232)
- ✅ **Direct inter-instance HTTP communication** on ports 8000-8499
- ✅ **SSH-based deployment** and configuration management

**These Kubernetes files expect:**
- ❌ **Pod orchestration** (conflicts with direct Python processes)
- ❌ **K8s service discovery** (conflicts with nginx upstream configuration)
- ❌ **Container deployment** (conflicts with systemd service management)
- ❌ **Kubernetes networking** (conflicts with direct IP routing)
- ❌ **kubectl commands** (conflicts with SSH-based deployment)

## 📋 DEPRECATED FILES AND DIRECTORIES

| Path | Purpose | Conflicts With |
|------|---------|----------------|
| `k8s/base/deployment.yaml` | Basic K8s deployments | systemd services |
| `k8s/production/sophia-ai-production.yaml` | Production K8s config | Production systemd setup |
| `k8s/mcp-servers/ai-memory.yaml` | MCP server pods | Direct MCP processes |
| `k8s/overlays/production/` | Kustomize overlays | Instance-specific configs |
| `k8s/monitoring/` | K8s monitoring | systemd health monitoring |
| `kubernetes/` | Complete K8s setup | Distributed systemd architecture |

## 🎯 USE INSTEAD

### **Production Deployment**
```bash
# Deploy to distributed systemd infrastructure
python scripts/deploy_distributed_systemd.py

# Dry run to see what would be deployed
python scripts/deploy_distributed_systemd.py --dry-run

# Deploy to specific instance only
python scripts/deploy_distributed_systemd.py --instance business_tools
```

### **Service Management**
```bash
# Instead of kubectl commands, use systemd:

# OLD K8s approach:
# kubectl get pods -n sophia-ai
# kubectl restart deployment sophia-ai-backend

# NEW systemd approach:
ssh ubuntu@192.222.58.232 "sudo systemctl status sophia-vector_search_mcp"
ssh ubuntu@104.171.202.117 "sudo systemctl restart sophia-gong_mcp"
```

### **Configuration**
```python
# Instead of K8s ConfigMaps/Secrets:
from config.production_infrastructure import PRODUCTION_INFRASTRUCTURE

# Get service configuration
instance_name, instance = get_service_instance("gong_mcp")
endpoint = f"http://{instance.ip}:{instance.ports['gong_mcp']}"
```

### **Health Monitoring**
```bash
# Instead of kubectl health checks:

# OLD K8s approach:
# kubectl get pods -l app=sophia-ai

# NEW production approach:
python scripts/monitor_production_deployment.py
curl http://192.222.58.232:9100  # Central health monitor
```

## 📊 KUBERNETES vs PRODUCTION COMPARISON

| Aspect | Kubernetes Approach | Production Reality | Alignment |
|--------|-------------------|-------------------|-----------|
| **Orchestration** | K8s control plane | systemd per instance | ❌ **FUNDAMENTAL CONFLICT** |
| **Service Discovery** | K8s Services/DNS | nginx upstream blocks | ❌ **ARCHITECTURAL CONFLICT** |
| **Networking** | K8s CNI/ClusterIP | Direct IP + nginx | ❌ **NETWORK CONFLICT** |
| **Configuration** | ConfigMaps/Secrets | Environment variables | ❌ **CONFIG CONFLICT** |
| **Deployment** | kubectl apply | SSH + systemd | ❌ **DEPLOYMENT CONFLICT** |
| **Health Checks** | K8s probes | Direct HTTP endpoints | ⚠️ **PATTERN CONFLICT** |
| **Scaling** | K8s HPA/VPA | Instance distribution | ❌ **SCALING CONFLICT** |

## 🚫 WHY KUBERNETES DOESN'T WORK HERE

### **Infrastructure Mismatch**
- Production has **5 separate Lambda Labs instances**
- Kubernetes expects **single cluster** or **managed cluster**
- **No K8s control plane** exists in production

### **Service Architecture Mismatch**  
- Production uses **direct Python processes** with systemd
- Kubernetes expects **containerized workloads**
- **Direct processes** ≠ **containerized services**

### **Network Architecture Mismatch**
- Production uses **nginx load balancing** with upstream blocks
- Kubernetes uses **service discovery** and ClusterIP
- **nginx routing** ≠ **K8s service discovery**

### **Deployment Model Mismatch**
- Production uses **SSH-based deployment** with code sync
- Kubernetes uses **container image** deployment
- **Code sync** ≠ **container deployment**

## ⚡ MIGRATION REQUIREMENTS

**If you were planning to use K8s deployment:**

### **IMMEDIATE ACTIONS REQUIRED:**
1. **Stop using kubectl commands** - They will fail
2. **Switch to systemd deployment script**
3. **Update monitoring to use HTTP health checks**
4. **Reconfigure networking expectations**

### **CONFIGURATION CHANGES:**
```bash
# OLD: K8s configuration
kubectl apply -f k8s/production/

# NEW: systemd deployment
python scripts/deploy_distributed_systemd.py
```

### **MONITORING CHANGES:**
```bash
# OLD: K8s health monitoring
kubectl get pods -l app=sophia-ai

# NEW: HTTP health monitoring
curl http://192.222.58.232:8000/health
curl http://104.171.202.117:8100/health
```

## 🏗️ PRODUCTION ARCHITECTURE OVERVIEW

```
Production Infrastructure (ACTUAL):
├── AI Core Instance (192.222.58.232)
│   ├── nginx (Load Balancer)
│   ├── vector_search_mcp (systemd:8000)
│   ├── real_time_chat_mcp (systemd:8001)
│   └── unified_memory_service (systemd:9000)
├── Business Tools (104.171.202.117)
│   ├── gong_mcp (systemd:8100)
│   ├── hubspot_mcp (systemd:8101)
│   └── linear_mcp (systemd:8102)
├── Data Pipeline (104.171.202.134)
│   ├── github_mcp (systemd:8200)
│   └── notion_mcp (systemd:8201)
└── Production Services (104.171.202.103)
    ├── codacy_mcp (systemd:8300)
    └── ui_ux_agent (systemd:8302)

K8s Architecture (INCOMPATIBLE):
├── Control Plane (DOESN'T EXIST)
├── Worker Nodes (NOT APPLICABLE)
├── Pod Network (CONFLICTS)
└── Service Discovery (CONFLICTS)
```

## 🔄 DEPRECATION TIMELINE

- **July 16, 2025:** Kubernetes files marked as DEPRECATED
- **August 1, 2025:** Warning messages added to K8s scripts
- **August 15, 2025:** K8s files moved to `deprecated/` directory
- **September 1, 2025:** K8s files removed from active codebase

## 🆘 EMERGENCY MIGRATION GUIDE

**If you have K8s configurations that need conversion:**

1. **Identify services** in your K8s manifests
2. **Map to production instances** using `config/production_infrastructure.py`
3. **Convert to systemd deployment** using `scripts/deploy_distributed_systemd.py`
4. **Update health checks** to use HTTP endpoints instead of K8s probes

**Example Conversion:**
```yaml
# OLD K8s manifest:
apiVersion: apps/v1
kind: Deployment
metadata:
  name: gong-mcp
spec:
  replicas: 2
  ports:
  - containerPort: 9101

# NEW production reality:
# Service: gong_mcp
# Instance: business_tools (104.171.202.117)
# Port: 8100 (NOT 9101)
# Management: systemd (NOT K8s)
# Endpoint: http://104.171.202.117:8100
```

## 📞 SUPPORT & TROUBLESHOOTING

**For Production Deployment Issues:**
- **Deployment:** `python scripts/deploy_distributed_systemd.py --dry-run`
- **Configuration:** Check `config/production_infrastructure.py`
- **Health Status:** `http://192.222.58.232:9100`

**For Migration Questions:**
- **Port Mapping:** See `config/production_aligned_mcp_ports.json`
- **Service Status:** Use direct health check endpoints
- **Architecture:** Review production vs K8s comparison above

---

**⚠️ KUBERNETES DEPLOYMENT WILL FAIL IN PRODUCTION**

The production infrastructure is fundamentally incompatible with Kubernetes.
Use the distributed systemd deployment approach instead. 