# 🚀 Sophia AI Production Deployment Architecture

**Last Updated**: July 6, 2025
**Domain**: sophia-intel.ai
**Status**: Production Ready

## 📋 Architecture Overview

```
┌──────────────────────────────────────────────────────────────────────────┐
│                           SOPHIA AI PRODUCTION                            │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────────┐              ┌──────────────────────────────────┐ │
│  │   VERCEL (CDN)   │              │   LAMBDA LABS K3S CLUSTER       │ │
│  │                  │              │                                  │ │
│  │ ┌──────────────┐ │              │ ┌─────────┐┌─────────┐┌──────┐ │ │
│  │ │sophia-intel.ai│ │◄────────────►│ │Master-01││Worker-01││Worker│ │ │
│  │ │app.sophia-    │ │   API/WS     │ │GH200    ││GH200    ││-02   │ │ │
│  │ │intel.ai       │ │              │ │96GB     ││96GB     ││GH200 │ │ │
│  │ └──────────────┘ │              │ └─────────┘└─────────┘└──────┘ │ │
│  │                  │              │                                  │ │
│  │ Global Edge      │              │ • K3s Kubernetes                │ │
│  │ Network          │              │ • NVIDIA GPU Operator           │ │
│  │ Auto-scaling     │              │ • Prometheus/Grafana            │ │
│  └──────────────────┘              └──────────────────────────────────┘ │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                        DNS CONFIGURATION                          │  │
│  ├──────────────────────────────────────────────────────────────────┤  │
│  │ sophia-intel.ai      → Vercel (Frontend)                         │  │
│  │ app.sophia-intel.ai  → Vercel (Frontend)                         │  │
│  │ api.sophia-intel.ai  → Lambda Labs (Backend API)                 │  │
│  │ mcp.sophia-intel.ai  → Lambda Labs (MCP Gateway)                 │  │
│  │ monitor.sophia-intel.ai → Lambda Labs (Prometheus/Grafana)       │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────────┘
```

## 🏗️ Infrastructure Components

### **1. Frontend - Vercel**
- **Technology**: React + Vite + TypeScript
- **Deployment**: Vercel Edge Network
- **Features**:
  - Global CDN distribution
  - Automatic HTTPS/SSL
  - Edge functions for API routing
  - Preview deployments for PRs
  - Analytics and monitoring

### **2. Backend - Lambda Labs K3s Cluster**
- **Nodes**: 3x NVIDIA GH200 (96GB GPU memory each)
  - Master-01: 192.222.58.232
  - Worker-01: TBD (auto-provisioned)
  - Worker-02: TBD (auto-provisioned)
- **Orchestration**: K3s (Lightweight Kubernetes)
- **GPU Support**: NVIDIA GPU Operator
- **Networking**: Flannel CNI with VXLAN backend

### **3. Core Services**
```yaml
Services:
  - Sophia Backend API (3 replicas)
  - PostgreSQL (HA with streaming replication)
  - Redis (3 nodes with Sentinel)
  - MCP Servers (2 replicas each):
    - AI Memory
    - Codacy
    - GitHub
    - Linear
    - Asana
    - Notion
    - HubSpot
    - Slack
```

## 🔧 Deployment Process

### **Phase 1: Infrastructure Setup**
```bash
# 1. Launch Lambda Labs cluster
python launch_production_cluster.py

# 2. Setup K3s cluster
./setup_k3s_cluster.sh

# 3. Install GPU operator
kubectl apply -f https://nvidia.github.io/gpu-operator/stable/gpu-operator.yaml
```

### **Phase 2: Frontend Deployment**
```bash
# 1. Prepare frontend
cd frontend
npm install
npm run build

# 2. Deploy to Vercel
vercel --prod --token=$VERCEL_API_TOKEN

# 3. Configure custom domain
vercel domains add sophia-intel.ai
```

### **Phase 3: Backend Deployment**
```bash
# 1. Build Docker images
docker build -f Dockerfile.production -t scoobyjava15/sophia-backend:latest .
docker push scoobyjava15/sophia-backend:latest

# 2. Deploy to K3s
kubectl apply -f k8s-manifests/

# 3. Configure ingress and SSL
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.3/cert-manager.yaml
```

### **Phase 4: DNS Configuration**
```bash
# Configure Namecheap DNS
python configure_dns.py
```

## 🔐 Security Configuration

### **SSL/TLS**
- **Frontend**: Automatic SSL via Vercel
- **Backend**: Let's Encrypt via cert-manager
- **All traffic**: Forced HTTPS redirect

### **Authentication**
- **API Keys**: Stored in Pulumi ESC
- **JWT**: For user authentication
- **OAuth2**: For third-party integrations

### **Network Security**
- **Firewall**: Only required ports open
- **Private networking**: K3s internal communication
- **DDoS protection**: Via Vercel and Cloudflare

## 📊 Monitoring & Observability

### **Metrics**
- **Prometheus**: Cluster and application metrics
- **Grafana**: Visualization dashboards
- **GPU metrics**: NVIDIA DCGM exporter

### **Logging**
- **Loki**: Log aggregation
- **Fluent Bit**: Log forwarding
- **Structured logging**: JSON format

### **Alerting**
- **AlertManager**: Alert routing
- **PagerDuty**: On-call management
- **Slack**: Team notifications

## 🚀 Scaling Strategy

### **Horizontal Scaling**
```yaml
Backend API:
  min_replicas: 3
  max_replicas: 10
  target_cpu: 70%
  target_memory: 80%

MCP Servers:
  min_replicas: 2
  max_replicas: 5
  target_cpu: 60%
```

### **Vertical Scaling**
- **Add nodes**: Up to 16 GH200 nodes
- **GPU allocation**: Dynamic based on workload
- **Memory limits**: Auto-adjusted

## 🔄 CI/CD Pipeline

### **GitHub Actions**
```yaml
Workflow:
  1. Code push to main
  2. Run tests and linting
  3. Build Docker images
  4. Push to registry
  5. Deploy to K3s
  6. Run integration tests
  7. Update production
```

### **Deployment Environments**
- **Production**: sophia-intel.ai
- **Staging**: staging.sophia-intel.ai
- **Development**: dev.sophia-intel.ai

## 📝 Configuration Management

### **Environment Variables**
```bash
# Frontend (Vercel)
VITE_API_URL=https://api.sophia-intel.ai
VITE_ENVIRONMENT=production

# Backend (K3s)
ENVIRONMENT=prod
PULUMI_ORG=scoobyjava-org
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
```

### **Secrets Management**
- **GitHub Secrets**: Source of truth
- **Pulumi ESC**: Secret synchronization
- **K8s Secrets**: Runtime secrets

## 🆘 Disaster Recovery

### **Backup Strategy**
- **Database**: Daily snapshots to S3
- **Redis**: AOF persistence
- **Code**: GitHub repository
- **Configs**: Pulumi state

### **Recovery Time Objectives**
- **RTO**: < 1 hour
- **RPO**: < 15 minutes
- **Uptime target**: 99.9%

## 📞 Support & Maintenance

### **Monitoring URLs**
- Frontend: https://sophia-intel.ai
- API: https://api.sophia-intel.ai
- Docs: https://api.sophia-intel.ai/docs
- Grafana: https://monitor.sophia-intel.ai
- Health: https://api.sophia-intel.ai/health

### **SSH Access**
```bash
# Master node
ssh -i ~/.ssh/sophia2025.pem ubuntu@192.222.58.232

# Kubernetes access
export KUBECONFIG=~/.kube/sophia-production
kubectl get pods -n sophia-ai
```

### **Emergency Procedures**
1. **Service down**: Check K3s pod status
2. **High load**: Scale replicas manually
3. **GPU issues**: Check NVIDIA GPU operator
4. **SSL issues**: Verify cert-manager logs

## 🎯 Performance Targets

- **API Response Time**: < 200ms (p95)
- **Frontend Load Time**: < 2s
- **GPU Utilization**: 60-80%
- **Availability**: 99.9%
- **Concurrent Users**: 10,000+

## 🔧 Maintenance Commands

```bash
# Check cluster status
kubectl get nodes
kubectl top nodes

# View logs
kubectl logs -n sophia-ai deployment/sophia-backend -f

# Scale deployment
kubectl scale deployment/sophia-backend -n sophia-ai --replicas=5

# Update image
kubectl set image deployment/sophia-backend sophia-backend=scoobyjava15/sophia-backend:v2.0 -n sophia-ai

# Restart pods
kubectl rollout restart deployment/sophia-backend -n sophia-ai
```

This architecture provides a production-grade, scalable platform for Sophia AI with global reach via Vercel's CDN and powerful GPU computing via Lambda Labs.
