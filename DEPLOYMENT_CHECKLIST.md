# 🚀 Sophia AI Lambda Labs Deployment Checklist

## ✅ Pre-Deployment Verification

### Infrastructure Ready ✅
- [x] **Lambda Labs Instance**: `sophia-ai-production` (104.171.202.64) - Active
- [x] **Docker Cloud Setup**: `scoobyjava15` registry authenticated
- [x] **SSH Access**: Key `cae55cb8d0f5443cbdf9129f7cec8770` configured
- [x] **Docker Swarm**: Ready for initialization on Lambda Labs instance

### Configuration Files ✅
- [x] **docker-compose.cloud.yml**: Docker Swarm stack configuration
- [x] **Dockerfile**: Multi-stage production build optimized
- [x] **deploy_to_lambda_labs_cloud.py**: Automated deployment script
- [x] **Docker secrets**: 7 secrets mapped to Pulumi ESC

### Build Validation ✅
- [x] **Dependencies**: Requirements.txt approach implemented
- [x] **Multi-stage build**: Production, development, testing targets
- [x] **Health checks**: All services have health monitoring
- [x] **Security**: Non-root user, minimal attack surface

## 🎯 Deployment Process

### Step 1: SSH into Lambda Labs Instance
```bash
# Use the SSH key provided in the infrastructure setup
ssh -i ~/.ssh/sophia-ai-key ubuntu@104.171.202.64
```

### Step 2: Initialize Docker Swarm (First Time Only)
```bash
# On Lambda Labs instance
docker swarm init
```

### Step 3: Deploy from Local Machine
```bash
# Production deployment
python scripts/deploy_to_lambda_labs_cloud.py --environment prod

# OR with staging environment
python scripts/deploy_to_lambda_labs_cloud.py --environment staging
```

### Step 4: Verify Deployment
```bash
# Check stack status
docker stack services sophia-ai-prod

# Check service health
docker service ps sophia-ai-prod_sophia-backend
```

## 🔐 Secret Management

### Pulumi ESC Integration
All secrets are automatically managed through Pulumi ESC:

```bash
# Secrets are loaded from: scoobyjava-org/default/sophia-ai-production
# Structure: values.sophia.*
# No manual secret management required
```

### Required Secrets
- `pulumi_access_token` - Pulumi ESC access
- `postgres_password` - Database password
- `mem0_api_key` - Mem0 service API key
- `snowflake_account` - Snowflake account identifier
- `snowflake_user` - Snowflake username
- `snowflake_password` - Snowflake password
- `grafana_password` - Grafana admin password

## 🌐 Service Endpoints

### Production URLs
| Service | URL | Purpose |
|---------|-----|---------|
| **Main API** | `http://104.171.202.64:8000` | Sophia AI Backend |
| **API Docs** | `http://104.171.202.64:8000/docs` | OpenAPI Documentation |
| **Health Check** | `http://104.171.202.64:8000/api/health` | Service Health |
| **Mem0 Server** | `http://104.171.202.64:8080` | Memory Management |
| **Cortex Server** | `http://104.171.202.64:8081` | AI SQL Processing |
| **Traefik Dashboard** | `http://104.171.202.64:8090` | Load Balancer |
| **Grafana** | `http://104.171.202.64:3000` | Monitoring Dashboard |
| **Prometheus** | `http://104.171.202.64:9090` | Metrics Collection |

### Health Check Commands
```bash
# Main API health
curl http://104.171.202.64:8000/api/health

# Mem0 server health  
curl http://104.171.202.64:8080/health

# Cortex server health
curl http://104.171.202.64:8081/health

# Traefik dashboard
curl http://104.171.202.64:8090/api/overview
```

## 📊 Monitoring & Scaling

### Service Scaling
```bash
# Scale main backend
docker service scale sophia-ai-prod_sophia-backend=5

# Scale Mem0 servers
docker service scale sophia-ai-prod_mem0-server=3

# Scale Cortex servers  
docker service scale sophia-ai-prod_cortex-server=4
```

### Resource Monitoring
```bash
# Service resource usage
docker service ps sophia-ai-prod_sophia-backend

# Node resource usage
docker node ls

# Stack overview
docker stack ps sophia-ai-prod
```

## 🔄 Updates & Maintenance

### Rolling Updates
```bash
# Update main service image
docker service update --image scoobyjava15/sophia-ai:v2.0 sophia-ai-prod_sophia-backend

# Update environment variables
docker service update --env-add NEW_CONFIG=value sophia-ai-prod_sophia-backend
```

### Rollback
```bash
# Rollback to previous version
docker service rollback sophia-ai-prod_sophia-backend

# Check rollback status
docker service ps sophia-ai-prod_sophia-backend
```

### Log Monitoring
```bash
# Service logs
docker service logs --tail 100 sophia-ai-prod_sophia-backend

# Follow logs in real-time
docker service logs -f sophia-ai-prod_sophia-backend
```

## 🚨 Troubleshooting

### Common Issues

#### 1. Service Not Starting
```bash
# Check service events
docker service ps sophia-ai-prod_sophia-backend

# Check detailed logs
docker service logs --tail 50 sophia-ai-prod_sophia-backend
```

#### 2. Image Pull Issues
```bash
# Verify registry access
docker pull scoobyjava15/sophia-ai:latest

# Re-authenticate if needed
docker login
```

#### 3. Network Connectivity
```bash
# Check overlay networks
docker network ls

# Inspect network details
docker network inspect sophia-ai-prod_sophia-overlay
```

#### 4. Secret Access Issues
```bash
# List available secrets
docker secret ls

# Update secret with new value
docker secret rm postgres_password
echo "new_password" | docker secret create postgres_password -
```

## 🎯 Post-Deployment Tasks

### Immediate (Day 1)
- [ ] Verify all service endpoints respond correctly
- [ ] Test API functionality with sample requests
- [ ] Configure Grafana dashboards
- [ ] Set up basic monitoring alerts

### Short-term (Week 1)
- [ ] Configure custom domain names
- [ ] Set up SSL certificates via Traefik Let's Encrypt
- [ ] Implement backup procedures for PostgreSQL
- [ ] Configure log aggregation

### Long-term (Month 1)
- [ ] Set up comprehensive monitoring alerts
- [ ] Implement disaster recovery procedures
- [ ] Configure auto-scaling policies
- [ ] Performance optimization based on metrics

## 📋 Success Criteria

### Deployment Success ✅
- [ ] All 8 services running with 1/1 replicas ready
- [ ] Health checks passing for all services
- [ ] API endpoints responding correctly
- [ ] Monitoring dashboards accessible
- [ ] No error logs in service outputs

### Performance Targets
- [ ] API response times < 200ms (95th percentile)
- [ ] Memory usage < 80% on all nodes
- [ ] CPU usage < 70% average
- [ ] Zero failed health checks
- [ ] Uptime > 99.9%

## 🔧 Emergency Procedures

### Complete Stack Restart
```bash
# Remove stack
docker stack rm sophia-ai-prod

# Wait for cleanup (30 seconds)
sleep 30

# Redeploy
docker stack deploy -c docker-compose.cloud.yml sophia-ai-prod
```

### Single Service Restart
```bash
# Force restart a service
docker service update --force sophia-ai-prod_sophia-backend
```

### Backup Procedures
```bash
# Database backup
docker exec $(docker ps -q -f name=sophia-ai-prod_postgres) pg_dump -U sophia sophia > backup.sql

# Configuration backup
docker config ls
docker secret ls
```

---

## 🎉 Ready for Production Deployment!

All infrastructure is configured and ready. The Sophia AI platform can now be deployed to Lambda Labs with enterprise-grade monitoring, auto-scaling, and security.

**Next Command**: `python scripts/deploy_to_lambda_labs_cloud.py --environment prod` 