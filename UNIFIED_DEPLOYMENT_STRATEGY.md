# 🚀 SOPHIA AI UNIFIED DEPLOYMENT STRATEGY

**Domain**: sophia-intel.ai
**Last Updated**: July 6, 2025
**Status**: DEFINITIVE PRODUCTION ARCHITECTURE

## 🎯 Executive Summary

This is the **SINGLE SOURCE OF TRUTH** for Sophia AI deployment. We use:
- **Frontend**: Vercel (global CDN, automatic SSL)
- **Backend**: Lambda Labs Docker Swarm (GPU-accelerated)
- **Data**: Snowflake (center of universe)
- **Secrets**: Pulumi ESC (GitHub → ESC → Services)
- **Domain**: sophia-intel.ai via Namecheap

## 📋 Component Breakdown

### **1. Frontend Services (Vercel)**

**Components**:
- Unified Dashboard (`frontend/src/components/dashboard/UnifiedDashboard.tsx`)
- Unified Chat Interface
- Executive KPIs and Analytics
- Knowledge Management UI

**Deployment**:
```bash
cd frontend
vercel --prod --token=$VERCEL_API_TOKEN
```

**URLs**:
- Production: https://sophia-intel.ai
- App: https://app.sophia-intel.ai

### **2. Backend Services (Lambda Labs Docker Swarm)**

**Infrastructure**:
- 3x NVIDIA GH200 nodes (96GB each = 288GB total)
- Container orchestration via Docker Swarm (manager + workers)
- Auto-scaling 3-10 replicas per service (Swarm will manage placement)

**Core Services** (managed via `docker stack deploy`):
```yaml
services:
  sophia-backend:
    image: scoobyjava15/sophia-backend:latest
    deploy:
      replicas: 3
      placement:
        constraints: [node.role == worker]
    ports:
      - published: 8000
        target: 8000

  mcp-servers:
    # Each MCP server runs as its own service, e.g.:
    ai-memory:
      image: scoobyjava15/sophia-mcp-ai-memory:latest
      deploy:
        replicas: 2
    # ... other MCP servers follow similar pattern ...

  postgres:
    image: postgres:15-alpine
    deploy:
      replicas: 1
    ports:
      - published: 5432
        target: 5432

  redis:
    image: redis:7-alpine
    deploy:
      replicas: 3
    ports:
      - published: 6379
        target: 6379

  prometheus:
    image: prom/prometheus:latest
  grafana:
    image: grafana/grafana:latest
```

### **3. Data Layer (Snowflake)**

**Architecture**:
- Center of universe - ALL data flows through Snowflake
- Cortex AI for embeddings and LLM operations
- Vector search capabilities
- GPU-accelerated external functions

**Schemas**:
```sql
SOPHIA_AI_PRODUCTION
├── AI_MEMORY          # Persistent memory with embeddings
├── BUSINESS_DATA      # HubSpot, Gong, etc.
├── PROJECT_DATA       # Linear, Asana
├── KNOWLEDGE_BASE     # Documents and learning
└── ANALYTICS          # Usage and performance
```

### **4. Infrastructure Management (Pulumi)**

**Managed Resources**:
- Lambda Labs instances
- Vercel project and domains
- Namecheap DNS records
- Kubernetes configurations
- Secret management

**Deployment**:
```bash
pulumi up --stack sophia-ai-production
```

## 🔄 Deployment Flow

### **Phase 1: Infrastructure**
```bash
# 1. Provision Lambda Labs cluster
python launch_production_cluster.py

# 2. Setup K3s Kubernetes
./setup_k3s_cluster.sh

# 3. Configure DNS
python configure_dns.py
```

### **Phase 2: Backend**
```bash
# 1. Build Docker images
docker build -f docker/Dockerfile.optimized -t scoobyjava15/sophia-backend:latest .
docker push scoobyjava15/sophia-backend:latest

# 2. Deploy to K3s
kubectl apply -f k8s-manifests/
```

### **Phase 3: Frontend**
```bash
# 1. Deploy to Vercel
cd frontend
vercel --prod

# 2. Configure domain
vercel domains add sophia-intel.ai
```

## 🔐 Secret Management

**Flow**:
```
GitHub Org Secrets (ai-cherry)
         ↓
GitHub Actions Sync
         ↓
Pulumi ESC Environment
         ↓
K8s Secrets / Vercel Env
         ↓
Running Services
```

**Key Secrets**:
- `NAMECHEAP_API_KEY`: DNS management
- `VERCEL_API_TOKEN`: Frontend deployment
- `LAMBDA_LABS_API_KEY`: Infrastructure
- `SNOWFLAKE_*`: Database access
- `OPENAI_API_KEY`, etc.: AI services

## 📊 Monitoring & Operations

### **Health Checks**
- Frontend: https://sophia-intel.ai/health
- API: https://api.sophia-intel.ai/health
- Grafana: https://monitor.sophia-intel.ai

### **Scaling Strategy**
```yaml
Auto-scaling Rules:
  CPU > 70%: Scale up
  Memory > 80%: Scale up
  Requests > 100/s: Scale up

Limits:
  Min replicas: 3
  Max replicas: 10
  Max nodes: 16
```

## 🚨 Why This Architecture?

### **Why Vercel for Frontend?**
- Global edge network (faster than self-hosted)
- Automatic SSL and domain management
- Preview deployments for every PR
- Built-in analytics and monitoring
- Zero-config deployment

### **Why Docker Swarm on Lambda Labs?**
- GPU acceleration for AI workloads
- More control than managed K8s
- Cost-effective for our scale
- Easy multi-node management
- Production-grade but simple

### **Why NOT Docker Swarm/Cloud?**
- K8s has better GPU support
- More extensive ecosystem
- Better scaling capabilities
- Industry standard
- Better monitoring tools

### **Why Pulumi?**
- Infrastructure as Code in Python
- Excellent secret management (ESC)
- Multi-cloud support
- GitOps friendly
- Type-safe configurations

## 🎯 Mid-Long Term Benefits

1. **Scalability**: Can grow from 3 to 16+ nodes seamlessly
2. **Performance**: GPU acceleration for all AI operations
3. **Reliability**: Multi-node redundancy, auto-healing
4. **Cost**: Pay for what we use, scale down when quiet
5. **Developer Experience**: One command deployments
6. **Security**: Enterprise-grade secret management
7. **Monitoring**: Full observability stack included

## 📝 Quick Commands

```bash
# Deploy everything
./deploy_production_complete.sh

# Check status
kubectl get pods -n sophia-ai
vercel ls

# View logs
kubectl logs -n sophia-ai -l app=sophia-backend -f

# Scale up
kubectl scale deployment/sophia-backend -n sophia-ai --replicas=5

# Update frontend
cd frontend && vercel --prod
```

## ⚡ Emergency Procedures

1. **Service Down**:
   ```bash
   kubectl rollout restart deployment/sophia-backend -n sophia-ai
   ```

2. **High Load**:
   ```bash
   kubectl scale deployment/sophia-backend -n sophia-ai --replicas=10
   ```

3. **SSL Issues**:
   ```bash
   kubectl describe certificate -n sophia-ai
   ```

## 🏁 Conclusion

This architecture provides:
- **Enterprise-grade** reliability
- **Startup-speed** deployment
- **AI-first** infrastructure
- **Cost-effective** scaling
- **Developer-friendly** operations

**This is THE way we deploy Sophia AI. Period.**
