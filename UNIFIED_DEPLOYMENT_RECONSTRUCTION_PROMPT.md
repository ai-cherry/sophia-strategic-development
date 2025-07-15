# 🚀 UNIFIED DEPLOYMENT RECONSTRUCTION PROMPT
**For AI Coding Agent - Complete Sophia AI Deployment Overhaul**

## 🎯 MISSION STATEMENT
Transform the broken Sophia AI deployment system into a **unified, cloud-native, production-ready deployment pipeline** targeting sophia-intel.ai with enterprise-grade reliability and zero technical debt.

---

## 📋 CONTEXT & CURRENT STATE

### **Critical Issues Identified:**
- 9 syntax errors in deployment scripts and configs
- 23 configuration inconsistencies across the stack
- Image registry mismatches preventing container deployment
- Broken secret management integration
- Port configuration conflicts (8000 vs 8001)
- GitHub Actions workflow corruption
- ArgoCD references to non-existent branches
- GPU scheduling misconfigurations
- Missing persistent storage strategy

### **Target Architecture:**
- **Domain:** sophia-intel.ai (cloud-only, no local deployment)
- **Platform:** Lambda Labs K3s cluster (192.222.58.232)
- **Registry:** Docker Hub (scoobyjava15)
- **GitOps:** ArgoCD with automated deployment
- **Secrets:** Pulumi ESC integration
- **Monitoring:** Prometheus + Grafana + custom dashboards
- **SSL:** Automatic TLS with cert-manager

---

## 🛠️ COMPREHENSIVE RECONSTRUCTION PLAN

### **PHASE 1: SYNTAX ERROR ELIMINATION (2 hours)**

#### **1.1 GitHub Actions Workflow Repair**
**File:** `.github/workflows/deploy-production.yml`
```yaml
# CRITICAL FIX REQUIRED:
# Line 213: Complete the broken notification block
# Current (BROKEN):
curl -X POST -H 'Content-type: application/json' \
  --data '{
    "text": "❌ Sophia AI Production Deployment Failed!",
    # MISSING CLOSING BRACKET AND QUOTE

# Fix to:
curl -X POST -H 'Content-type: application/json' \
  --data '{
    "text": "❌ Sophia AI Production Deployment Failed!",
    "channel": "#deployment-alerts"
  }' \
  ${{ secrets.SLACK_WEBHOOK_URL }}
```

#### **1.2 Shell Script Syntax Repair**
**Files to Fix:**
- `scripts/deploy_sophia_production_complete.sh` (Line 89: nginx config escaping)
- `scripts/deploy_step_by_step.sh` (Line 12: missing closing quotes)
- `scripts/deploy_lambda_labs_k3s.sh` (multiple incomplete log statements)

**Standard Pattern:**
```bash
# Replace all instances of incomplete echo statements
echo "🎨 Step 2: Deploying Frontend (Lambda Labs)"  # Add missing quote
echo "Deploy to Lambda Labs: ${LAMBDA_IP}"          # Add proper variable expansion
```

#### **1.3 Docker Configuration Standardization**
**File:** `docker-compose.lambda.yml`
```yaml
# Fix incomplete environment section:
environment:
  - PORT=8000  # STANDARDIZE TO 8000 (not 8001)
  - ENVIRONMENT=prod
  - PULUMI_ORG=scoobyjava-org
  # Add missing environment variables
```

**File:** `Dockerfile.backend`
```dockerfile
# Fix non-existent file reference:
COPY .env.production .  # Replace 'local.env' which doesn't exist
EXPOSE 8000             # Standardize port (not 8001)
```

#### **1.4 Python Script Modernization**
**File:** `scripts/validate_deployment.py`
```python
# Fix deprecated asyncio usage:
# REPLACE:
start_time = asyncio.get_event_loop().time()

# WITH:
import time
start_time = time.time()

# Fix string formatting:
print(f"\n🎉 Production Deployment Complete!")  # Single backslash
```

### **PHASE 2: KUBERNETES CONFIGURATION UNIFICATION (3 hours)**

#### **2.1 Image Registry Standardization**
**Critical Fix:** Update ALL Kubernetes manifests to use consistent Docker Hub registry

**Files to Update:**
- `k8s/base/deployment.yaml`
- `k8s/overlays/production/kustomization.yaml`
- `k8s/production/sophia-ai-production.yaml`
- `k8s/mcp-servers/ai-memory.yaml`

**Standard Pattern:**
```yaml
# REPLACE ALL instances of:
image: sophia-backend:latest              # ❌ No registry
image: sophia-mcp-base:latest            # ❌ No registry

# WITH:
image: scoobyjava15/sophia-backend:latest    # ✅ Full registry path
image: scoobyjava15/sophia-mcp-base:latest   # ✅ Full registry path
```

#### **2.2 Port Configuration Unification**
**DECISION:** Standardize ALL services to port 8000

**Files to Update:**
```yaml
# k8s/base/service.yaml
ports:
- port: 8000
  targetPort: 8000

# k8s/overlays/production/deployment-patch.yaml
readinessProbe:
  httpGet:
    port: 8000
livenessProbe:
  httpGet:
    port: 8000

# docker-compose.lambda.yml
ports:
- "8000:8000"  # Not 8001
```

#### **2.3 ArgoCD GitOps Repair**
**File:** `k8s/argocd/sophia-ai-app.yaml`
```yaml
# Fix non-existent branch reference:
source:
  repoURL: https://github.com/ai-cherry/sophia-main
  targetRevision: main  # CHANGE FROM: feature/full-prod-beast
  path: k8s/overlays/production

# Remove references to non-existent paths:
# DELETE: path: k8s/data-services  # This path doesn't exist
```

#### **2.4 GPU Resource Allocation Fix**
**File:** `k8s/mcp-servers/ai-memory.yaml`
```yaml
# REPLACE incorrect GPU scheduling:
nodeSelector:
  nvidia.com/gpu: "true"  # ❌ Doesn't guarantee GPU

# WITH proper GPU resource request:
resources:
  requests:
    nvidia.com/gpu: "1"
    memory: "4Gi"
    cpu: "2"
  limits:
    nvidia.com/gpu: "1"
    memory: "8Gi"
    cpu: "4"
```

### **PHASE 3: SECRET MANAGEMENT INTEGRATION (2 hours)**

#### **3.1 Pulumi ESC Secret Integration**
**Create:** `k8s/base/secrets-esc.yaml`
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: sophia-ai-secrets
  annotations:
    pulumi.com/esc-env: "scoobyjava-org/default/sophia-ai-production"
type: Opaque
stringData:
  OPENAI_API_KEY: ""
  ANTHROPIC_API_KEY: ""
  DOCKER_HUB_ACCESS_TOKEN: ""
  QDRANT_API_KEY: ""
  GONG_API_KEY: ""
  HUBSPOT_API_KEY: ""
  SLACK_WEBHOOK_URL: ""
```

#### **3.2 Environment Variable Standardization**
**Standard Environment Variables Across ALL Services:**
```yaml
env:
- name: ENVIRONMENT
  value: "prod"
- name: PULUMI_ORG
  value: "scoobyjava-org"
- name: PULUMI_STACK
  value: "sophia-ai-production"
- name: LOG_LEVEL
  value: "INFO"
- name: DOMAIN
  value: "sophia-intel.ai"
```

### **PHASE 4: PERSISTENT STORAGE IMPLEMENTATION (1 hour)**

#### **4.1 Database Persistent Volumes**
**Create:** `k8s/base/postgres-pvc.yaml`
```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-storage
spec:
  accessModes: [ReadWriteOnce]
  resources:
    requests:
      storage: 100Gi
  storageClassName: local-path  # K3s default
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: redis-storage
spec:
  accessModes: [ReadWriteOnce]
  resources:
    requests:
      storage: 20Gi
  storageClassName: local-path
```

### **PHASE 5: DOMAIN & SSL CONFIGURATION (1 hour)**

#### **5.1 Ingress with SSL**
**Create:** `k8s/base/ingress-ssl.yaml`
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: sophia-ai-ingress
  annotations:
    kubernetes.io/ingress.class: "traefik"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    traefik.ingress.kubernetes.io/router.tls: "true"
spec:
  tls:
  - hosts:
    - sophia-intel.ai
    - api.sophia-intel.ai
    - grafana.sophia-intel.ai
    secretName: sophia-ai-tls
  rules:
  - host: sophia-intel.ai
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: sophia-ai-frontend
            port:
              number: 3000
  - host: api.sophia-intel.ai
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: sophia-ai-backend
            port:
              number: 8000
  - host: grafana.sophia-intel.ai
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: grafana
            port:
              number: 3000
```

### **PHASE 6: MONITORING & OBSERVABILITY (1 hour)**

#### **6.1 ServiceMonitor for Prometheus**
**Create:** `k8s/monitoring/service-monitors.yaml`
```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: sophia-ai-metrics
  namespace: monitoring
spec:
  namespaceSelector:
    matchNames:
    - sophia-ai-prod
  selector:
    matchLabels:
      app: sophia-ai-backend
  endpoints:
  - port: metrics
    interval: 30s
    path: /metrics
---
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: sophia-mcp-metrics
  namespace: monitoring
spec:
  namespaceSelector:
    matchNames:
    - mcp-servers
  selector:
    matchLabels:
      mcp-server: "true"
  endpoints:
  - port: metrics
    interval: 30s
    path: /metrics
```

---

## 🎯 VALIDATION & DEPLOYMENT STRATEGY

### **Pre-Deployment Validation Commands:**
```bash
# 1. Syntax validation
find k8s/ -name "*.yaml" | xargs yamllint
find scripts/ -name "*.sh" -exec shellcheck {} \;
python -m py_compile scripts/*.py

# 2. Docker build validation
docker build -f Dockerfile.backend . --dry-run

# 3. Kubernetes manifest validation
kubectl apply --dry-run=client -k k8s/overlays/production

# 4. Secret validation
pulumi config -s sophia-ai-production
```

### **Deployment Sequence:**
```bash
# 1. Apply base infrastructure
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml
kubectl wait --for=condition=Ready pods --all -n cert-manager --timeout=300s

# 2. Deploy Sophia AI platform
kubectl apply -k k8s/overlays/production

# 3. Verify deployment
kubectl rollout status deployment/sophia-ai-backend -n sophia-ai-prod
kubectl rollout status deployment/sophia-ai-mcp-orchestrator -n sophia-ai-prod

# 4. Test endpoints
curl -f https://api.sophia-intel.ai/health
curl -f https://sophia-intel.ai
curl -f https://grafana.sophia-intel.ai
```

---

## 🏆 SUCCESS CRITERIA

### **Technical Validation:**
- [ ] All YAML files pass `yamllint` validation
- [ ] All shell scripts pass `shellcheck` validation
- [ ] All Python files compile without syntax errors
- [ ] Docker images build successfully
- [ ] ArgoCD applications sync without errors
- [ ] All pods start and pass health checks
- [ ] Services respond on correct ports (8000)
- [ ] SSL certificates provision automatically
- [ ] Monitoring metrics collected successfully

### **Functional Validation:**
- [ ] https://sophia-intel.ai loads the frontend
- [ ] https://api.sophia-intel.ai/health returns 200 OK
- [ ] https://grafana.sophia-intel.ai shows Sophia AI dashboards
- [ ] MCP servers respond to orchestrator requests
- [ ] GPU resources allocated to AI workloads
- [ ] Secrets populated from Pulumi ESC
- [ ] Auto-scaling responds to load changes

### **Performance Targets:**
- [ ] Pod startup time < 60 seconds
- [ ] API response time < 200ms P95
- [ ] Frontend load time < 3 seconds
- [ ] SSL certificate provisioning < 5 minutes
- [ ] Deployment rollout time < 10 minutes

---

## 🚀 EXECUTION INSTRUCTIONS

### **Priority Order (CRITICAL):**
1. **FIRST:** Fix all syntax errors (GitHub Actions, shell scripts, Docker configs)
2. **SECOND:** Standardize image references and port configurations
3. **THIRD:** Implement secret management and ArgoCD fixes
4. **FOURTH:** Add persistent storage and SSL configuration
5. **FIFTH:** Deploy and validate complete system

### **File Creation Requirements:**
- Create any missing configuration files referenced in scripts
- Ensure all paths referenced in manifests actually exist
- Generate comprehensive kustomization.yaml files for all overlays
- Create environment-specific .env files if needed

### **Quality Gates:**
- Every file must pass syntax validation before proceeding
- Every change must maintain backward compatibility
- Every new configuration must follow established patterns
- Every deployment must be testable and reversible

---

## 📝 DELIVERABLES

### **Primary Output:**
1. **Unified Deployment Pipeline** - Single command deployment to sophia-intel.ai
2. **Zero Syntax Errors** - All scripts and configs validated
3. **Consistent Configuration** - Standardized ports, images, and environment variables
4. **Production SSL** - Automatic HTTPS with Let's Encrypt
5. **Complete Monitoring** - Grafana dashboards with real metrics
6. **GitOps Ready** - ArgoCD automated deployment from GitHub

### **Documentation Updates:**
- Update all README files with new deployment commands
- Create sophia-intel.ai access documentation
- Document secret management procedures
- Create troubleshooting guide for common issues

---

## ⚡ EMERGENCY ROLLBACK PLAN

```bash
# If deployment fails:
kubectl delete -k k8s/overlays/production
kubectl apply -k k8s/overlays/staging  # Fallback environment

# Revert ArgoCD applications:
argocd app sync sophia-ai-production --revision main~1

# Check cluster health:
kubectl get pods --all-namespaces
kubectl top nodes
```

---

**MISSION SUCCESS:** Transform broken deployment chaos into unified, cloud-native production system accessible at sophia-intel.ai with enterprise-grade reliability and monitoring.
