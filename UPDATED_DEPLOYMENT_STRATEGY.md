# 🚀 Sophia AI Updated Deployment Strategy
**Date:** December 2024  
**Version:** 2.0  
**Status:** Production Active

## 📋 Executive Summary

Sophia AI is deployed across 5 Lambda Labs GPU servers with a total monthly cost of ~$3,500. The deployment strategy focuses on high availability, performance, and cost optimization using modern cloud-native technologies.

## 🏗️ Infrastructure Overview

### Lambda Labs GPU Servers

| Server Name | IP Address | GPU | RAM | Purpose | Monthly Cost |
|------------|------------|-----|-----|---------|--------------|
| sophia-production-instance | 104.171.202.103 | RTX 6000 Ada | 48GB | Main production | $719 |
| sophia-ai-core | 192.222.58.232 | GH200 | 96GB | AI workloads | $1,269 |
| sophia-mcp-orchestrator | 104.171.202.117 | A6000 | 48GB | MCP servers | $539 |
| sophia-data-pipeline | 104.171.202.134 | A100 | 40GB | ETL/Analytics | $809 |
| sophia-development | 155.248.194.183 | A10 | 24GB | Development | $299 |
| **Total** | | | | | **~$3,635** |

### DNS Configuration
- **Primary Domain**: sophia-intel.ai
- **Frontend**: app.sophia-intel.ai → Lambda Labs
- **API**: api.sophia-intel.ai → 104.171.202.103 (production)
- **Wildcard**: *.sophia-intel.ai → 104.171.202.103

## 🔄 Deployment Process

### 1. **Pre-Deployment Checklist**
```bash
# Verify infrastructure
□ All Lambda Labs servers accessible via SSH
□ Pulumi ESC secrets configured
□ GitHub repository up to date
□ Docker Hub credentials valid
□ DNS records properly configured
```

### 2. **Environment Setup**
```bash
# SSH into production server
ssh -i ~/.ssh/lambda_labs_key ubuntu@104.171.202.103

# Clone repository (if not exists)
git clone https://github.com/ai-cherry/sophia-main.git
cd sophia-main

# Set environment variables
export ENVIRONMENT=prod
export PULUMI_ORG=scoobyjava-org
export PULUMI_ACCESS_TOKEN=${PULUMI_ACCESS_TOKEN}  # Set from Pulumi ESC or env
```

### 3. **Core Services Deployment**

#### PostgreSQL Database
```bash
# Deploy PostgreSQL with pgvector
docker run -d \
  --name postgres \
  --restart unless-stopped \
  -e POSTGRES_PASSWORD=$(pulumi env get POSTGRES_PASSWORD) \
  -e POSTGRES_DB=sophia_ai_db \
  -v postgres_data:/var/lib/postgresql/data \
  -p 5432:5432 \
  pgvector/pgvector:pg16

# Initialize schemas
docker exec -i postgres psql -U postgres sophia_ai_db < database/init/01-init-schema.sql
```

#### Redis Cache
```bash
# Deploy Redis
docker run -d \
  --name redis \
  --restart unless-stopped \
  -v redis_data:/data \
  -p 6379:6379 \
  redis:7-alpine \
  redis-server --appendonly yes
```

#### Qdrant Vector Database
```bash
# Deploy Qdrant
docker run -d \
  --name Qdrant \
  --restart unless-stopped \
  -e AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED=true \
  -e PERSISTENCE_DATA_PATH=/var/lib/Qdrant \
  -e DEFAULT_VECTORIZER_MODULE=text2vec-transformers \
  -e ENABLE_MODULES=text2vec-transformers \
  -e TRANSFORMERS_INFERENCE_API=http://t2v-transformers:8080 \
  -v Qdrant_data:/var/lib/Qdrant \
  -p 8080:8080 \
  -p 50051:50051 \
  semitechnologies/Qdrant:1.25.4

# Deploy transformer model
docker run -d \
  --name t2v-transformers \
  --restart unless-stopped \
  -e ENABLE_CUDA=1 \
  --gpus all \
  semitechnologies/transformers-inference:sentence-transformers-multi-qa-MiniLM-L6-cos-v1
```

### 4. **Backend Deployment**

#### Build and Deploy Backend
```bash
# Build Docker image
docker build -f backend/Dockerfile -t scoobyjava15/sophia-backend:latest .

# Push to Docker Hub
docker push scoobyjava15/sophia-backend:latest

# Deploy backend
docker run -d \
  --name sophia-backend \
  --restart unless-stopped \
  -e ENVIRONMENT=prod \
  -e PULUMI_ORG=scoobyjava-org \
  -e DATABASE_URL=postgresql://postgres:password@postgres:5432/sophia_ai_db \
  -e REDIS_URL=redis://redis:6379 \
  -e QDRANT_URL=http://Qdrant:8080 \
  -p 8000:8000 \
  --link postgres \
  --link redis \
  --link Qdrant \
  scoobyjava15/sophia-backend:latest
```

### 5. **MCP Servers Deployment**

Deploy critical MCP servers using Kubernetes manifests:

```bash
# Apply K3s manifests
kubectl apply -f k3s-manifests/

# Or deploy individually
docker run -d \
  --name mcp-ai-memory \
  --restart unless-stopped \
  -e ENVIRONMENT=prod \
  -e QDRANT_URL=http://Qdrant:8080 \
  -e REDIS_URL=redis://redis:6379 \
  -p 9001:9001 \
  scoobyjava15/mcp-ai-memory:latest

# Repeat for other MCP servers...
```

### 6. **Frontend Deployment**

Frontend is deployed to Lambda Labs:

```bash
# Build frontend
cd frontend
npm install
npm run build

# Deploy to Lambda Labs (automated via GitHub)
Lambda Labs --prod
```

## 📊 Monitoring & Health Checks

### Health Check Endpoints
- **Backend**: http://api.sophia-intel.ai/health
- **Qdrant**: http://api.sophia-intel.ai:8080/v1/.well-known/ready
- **Redis**: `redis-cli ping`
- **PostgreSQL**: `pg_isready`

### Monitoring Stack
```bash
# Deploy Prometheus
docker run -d \
  --name prometheus \
  -v $(pwd)/configs/prometheus.yml:/etc/prometheus/prometheus.yml \
  -p 9090:9090 \
  prom/prometheus

# Deploy Grafana
docker run -d \
  --name grafana \
  -e GF_SECURITY_ADMIN_PASSWORD=admin \
  -p 3001:3000 \
  grafana/grafana
```

## 🔒 Security Configuration

### SSL/TLS Setup
```nginx
# Nginx configuration for SSL
server {
    listen 443 ssl http2;
    server_name api.sophia-intel.ai;

    ssl_certificate /etc/letsencrypt/live/sophia-intel.ai/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/sophia-intel.ai/privkey.pem;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Firewall Rules
```bash
# Allow only necessary ports
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw allow 8000/tcp  # Backend API
sudo ufw enable
```

## 🔄 CI/CD Pipeline

### GitHub Actions Workflow
```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Build and Push Docker Image
        env:
          DOCKER_HUB_USERNAME: ${{ secrets.DOCKER_HUB_USERNAME }}
          DOCKER_HUB_ACCESS_TOKEN: ${{ secrets.DOCKER_HUB_ACCESS_TOKEN }}
        run: |
          echo $DOCKER_HUB_ACCESS_TOKEN | docker login -u $DOCKER_HUB_USERNAME --password-stdin
          docker build -t scoobyjava15/sophia-backend:latest .
          docker push scoobyjava15/sophia-backend:latest
      
      - name: Deploy to Lambda Labs
        uses: appleboy/ssh-action@v0.1.5
        with:
          host: 104.171.202.103
          username: ubuntu
          key: ${{ secrets.LAMBDA_PRIVATE_SSH_KEY }}
          script: |
            cd /home/ubuntu/sophia-main
            git pull
            docker pull scoobyjava15/sophia-backend:latest
            docker-compose up -d
```

## 📈 Performance Optimization

### Database Optimization
```sql
-- Create indexes for performance
CREATE INDEX idx_gong_calls_embedding ON gong_raw.stg_gong_calls USING GIN (embedding);
CREATE INDEX idx_hubspot_contacts_email ON hubspot_raw.stg_hubspot_contacts(email);

-- Vacuum and analyze
VACUUM ANALYZE;
```

### Caching Strategy
- **L1 (Redis)**: 5-minute TTL for hot data
- **L2 (Qdrant)**: 1-hour TTL for warm data
- **L3 (PostgreSQL)**: 24-hour TTL for cold data

### GPU Utilization
```bash
# Monitor GPU usage
nvidia-smi -l 1

# Set CUDA visible devices for specific containers
docker run -e CUDA_VISIBLE_DEVICES=0 ...
```

## 🚨 Disaster Recovery

### Backup Strategy
```bash
# Automated daily backups
0 2 * * * /home/ubuntu/scripts/backup/backup_all.sh

# PostgreSQL backup
pg_dump -h localhost -U postgres sophia_ai_db > backup_$(date +%Y%m%d).sql

# Qdrant backup
curl -X POST http://localhost:8080/v1/backups/filesystem \
  -H "Content-Type: application/json" \
  -d '{"id": "backup-'$(date +%Y%m%d)'"}'
```

### Recovery Procedures
1. **Database Recovery**
   ```bash
   psql -h localhost -U postgres sophia_ai_db < backup_20241215.sql
   ```

2. **Service Recovery**
   ```bash
   docker-compose down
   docker-compose up -d
   ```

3. **Full System Recovery**
   ```bash
   bash scripts/deployment/full_system_recovery.sh
   ```

## 📊 Cost Optimization

### Current Monthly Costs
- **Lambda Labs**: $3,635
- **Lambda Labs**: $20 (Pro plan)
- **Namecheap**: $15 (Domain + DNS)
- **Total**: ~$3,670/month

### Optimization Strategies
1. **Server Consolidation**
   - Combine MCP servers on fewer machines
   - Use K3s for better resource utilization

2. **Auto-scaling**
   - Scale down development server when not in use
   - Use spot instances for non-critical workloads

3. **Caching**
   - Aggressive caching to reduce compute
   - CDN for static assets

## 🔧 Troubleshooting Guide

### Common Issues

1. **Container Won't Start**
   ```bash
   # Check logs
   docker logs sophia-backend
   
   # Check resource usage
   docker stats
   ```

2. **Database Connection Failed**
   ```bash
   # Test connection
   psql -h localhost -U postgres -d sophia_ai_db
   
   # Check firewall
   sudo ufw status
   ```

3. **GPU Not Available**
   ```bash
   # Check NVIDIA runtime
   docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi
   
   # Install NVIDIA Docker runtime
   distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
   curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
   ```

## 📅 Maintenance Schedule

### Daily
- Health check monitoring
- Log rotation
- Backup verification

### Weekly
- Security updates
- Performance review
- Cost analysis

### Monthly
- Full system backup
- Dependency updates
- Infrastructure review

## 🎯 Future Improvements

1. **Kubernetes Migration**
   - Full K8s deployment for better orchestration
   - Helm charts for all services
   - ArgoCD for GitOps

2. **Multi-region Deployment**
   - Disaster recovery site
   - Global load balancing
   - Data replication

3. **Enhanced Monitoring**
   - APM integration
   - Custom dashboards
   - Automated alerting

4. **Security Hardening**
   - Zero-trust networking
   - Secret rotation
   - Compliance automation 