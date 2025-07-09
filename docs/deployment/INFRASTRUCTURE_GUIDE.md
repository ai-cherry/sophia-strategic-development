# Sophia AI Infrastructure Guide

> **Last Updated**: 2025-07-08  
> **Version**: 2.0  
> **Status**: Production

## Overview

Sophia AI runs on Lambda Labs GPU infrastructure with a comprehensive stack including:
- FastAPI backend with async processing
- MCP (Model Context Protocol) servers for AI orchestration
- PostgreSQL for persistent storage
- Redis for caching and message queuing
- Prometheus/Grafana for monitoring
- Docker containerization for all services

## Infrastructure Architecture

```
┌─────────────────────────────────────────────────┐
│           Lambda Labs GH200 Instance            │
│              192.222.58.232                     │
├─────────────────────────────────────────────────┤
│                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────┐│
│  │   Backend   │  │ MCP Servers │  │Frontend ││
│  │  Port 8000  │  │ 9000-9100   │  │Port 3000││
│  └──────┬──────┘  └──────┬──────┘  └────┬────┘│
│         │                 │               │     │
│  ┌──────┴─────────────────┴───────────────┴───┐│
│  │           Docker Network (sophia-net)       ││
│  └──────┬─────────────────┬───────────────┬───┘│
│         │                 │               │     │
│  ┌──────┴──────┐  ┌──────┴──────┐  ┌────┴────┐│
│  │  PostgreSQL │  │    Redis    │  │Prometheus││
│  │  Port 5432  │  │  Port 6379  │  │Port 9090 ││
│  └─────────────┘  └─────────────┘  └──────────┘│
│                                                 │
└─────────────────────────────────────────────────┘
```

## Service Components

### 1. Core Services

#### Backend API (Port 8000)
- **Technology**: FastAPI with Python 3.12
- **Features**: 
  - Async request handling
  - WebSocket support for real-time chat
  - OpenAPI documentation
  - Health monitoring endpoints
- **Endpoints**:
  - `/health` - Service health check
  - `/api/v1/chat` - AI chat interface
  - `/api/v1/lambda-labs/status` - Infrastructure status
  - `/docs` - Interactive API documentation

#### MCP Servers (Ports 9000-9100)
Individual AI orchestration servers:
- **AI Memory** (9001): Persistent memory management
- **UI/UX Agent** (9002): Design automation
- **Codacy** (3008): Code quality analysis
- **Linear** (9004): Project management
- **GitHub** (9103): Repository integration
- **Asana** (9100): Task management
- **Lambda Labs CLI** (9040): Infrastructure control
- **Lambda Labs Serverless** (9025): Serverless functions

### 2. Data Layer

#### PostgreSQL (Port 5432)
- **Version**: 16-alpine
- **Database**: sophia_db
- **Features**:
  - Persistent storage for all application data
  - Automatic backups
  - Connection pooling
  - Health monitoring

#### Redis (Port 6379)
- **Version**: 7-alpine
- **Use Cases**:
  - Session management
  - Caching layer
  - Message queue for async tasks
  - Real-time data synchronization

### 3. Monitoring Stack

#### Prometheus (Port 9090)
- **Metrics Collection**: 15-second intervals
- **Targets**:
  - Backend API metrics
  - MCP server health
  - Infrastructure metrics
  - Custom business metrics

#### Grafana (Port 3000)
- **Dashboards**:
  - System Overview
  - API Performance
  - MCP Server Health
  - Business Metrics
- **Default Login**: admin/sophia_admin

## Deployment Architecture

### Container Orchestration
```yaml
services:
  backend:
    image: scoobyjava15/sophia-backend:latest
    deploy:
      replicas: 2
      resources:
        limits:
          memory: 4G
          cpus: '2'
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
```

### Network Configuration
- **Internal Network**: sophia-network (bridge mode)
- **External Access**: Via Lambda Labs firewall rules
- **Service Discovery**: Docker DNS resolution

### Volume Management
```yaml
volumes:
  postgres_data:
    driver: local
  redis_data:
    driver: local
  prometheus_data:
    driver: local
  grafana_data:
    driver: local
```

## Security Architecture

### Authentication & Authorization
1. **API Keys**: Managed via Pulumi ESC
2. **JWT Tokens**: For user sessions
3. **Service-to-Service**: Internal network authentication
4. **MCP Authentication**: Token-based per server

### Network Security
- **Firewall**: Lambda Labs managed
- **Internal Network**: Isolated Docker network
- **SSL/TLS**: Terminated at Lambda Labs edge
- **Port Restrictions**: Only necessary ports exposed

### Secret Management
```
GitHub Organization Secrets
           ↓
    GitHub Actions
           ↓
     Pulumi ESC
           ↓
  Application Runtime
```

## Performance Optimization

### Caching Strategy
1. **Redis L1 Cache**: Hot data (<1ms access)
2. **PostgreSQL Materialized Views**: Aggregated data
3. **Application Memory Cache**: Frequently accessed configs
4. **CDN**: Static assets (future)

### Resource Allocation
- **Backend**: 2-4 CPU cores, 4-8GB RAM
- **PostgreSQL**: 2 CPU cores, 4GB RAM
- **Redis**: 1 CPU core, 2GB RAM
- **MCP Servers**: 1 CPU core, 1GB RAM each

### Scaling Strategy
1. **Horizontal Scaling**: Backend replicas
2. **Vertical Scaling**: Lambda Labs instance upgrade
3. **Database Scaling**: Read replicas (future)
4. **Cache Scaling**: Redis cluster (future)

## Monitoring & Alerting

### Key Metrics
1. **System Metrics**:
   - CPU utilization < 80%
   - Memory usage < 85%
   - Disk usage < 90%
   - Network latency < 100ms

2. **Application Metrics**:
   - API response time < 200ms (p95)
   - Error rate < 1%
   - Request rate tracking
   - Active users monitoring

3. **Business Metrics**:
   - Chat completions per hour
   - MCP server utilization
   - Feature usage statistics

### Alert Configuration
```yaml
alerts:
  - name: HighErrorRate
    condition: rate(errors) > 0.05
    severity: critical
    
  - name: HighMemoryUsage
    condition: memory_usage > 0.85
    severity: warning
    
  - name: ServiceDown
    condition: up == 0
    severity: critical
```

## Backup & Recovery

### Backup Strategy
1. **PostgreSQL**: Daily automated backups at 2 AM
2. **Volumes**: Weekly snapshots on Sunday
3. **Configuration**: Git versioned
4. **Secrets**: Pulumi ESC versioned

### Recovery Procedures
1. **Service Failure**: Docker auto-restart
2. **Data Loss**: Restore from latest backup
3. **Complete Failure**: Redeploy from Git + backups

### RTO/RPO Targets
- **RTO**: 1 hour (Recovery Time Objective)
- **RPO**: 24 hours (Recovery Point Objective)

## Maintenance Procedures

### Regular Maintenance
1. **Daily**:
   - Monitor health endpoints
   - Check error logs
   - Review metrics

2. **Weekly**:
   - Update Docker images
   - Review security patches
   - Backup verification

3. **Monthly**:
   - Performance optimization
   - Capacity planning
   - Security audit

### Update Procedures
```bash
# 1. Build new images
docker build -t scoobyjava15/sophia-backend:latest .

# 2. Push to registry
docker push scoobyjava15/sophia-backend:latest

# 3. Deploy update
docker-compose up -d --no-deps backend

# 4. Verify health
curl http://192.222.58.232:8000/health
```

## Troubleshooting

### Common Issues

1. **Service Won't Start**
   ```bash
   # Check logs
   docker-compose logs -f [service-name]
   
   # Check resources
   docker stats
   
   # Restart service
   docker-compose restart [service-name]
   ```

2. **Database Connection Issues**
   ```bash
   # Test connection
   docker exec -it postgres psql -U sophia_user -d sophia_db
   
   # Check network
   docker network inspect sophia-network
   ```

3. **High Memory Usage**
   ```bash
   # Identify culprit
   docker stats --no-stream
   
   # Restart service
   docker-compose restart [service-name]
   ```

### Debug Commands
```bash
# System overview
ssh ubuntu@192.222.58.232 'docker-compose ps'

# Service logs
ssh ubuntu@192.222.58.232 'docker-compose logs -f --tail=100 backend'

# Resource usage
ssh ubuntu@192.222.58.232 'docker stats --no-stream'

# Network inspection
ssh ubuntu@192.222.58.232 'docker network ls'
```

## Cost Optimization

### Current Costs
- **Lambda Labs GH200**: $1.49/hour ($1,087.70/month)
- **Docker Hub**: Free tier
- **Monitoring**: Self-hosted (no additional cost)

### Optimization Strategies
1. **Right-sizing**: Monitor actual usage
2. **Scheduling**: Scale down during off-hours
3. **Caching**: Reduce compute needs
4. **Efficient Queries**: Optimize database access

## Future Enhancements

### Planned Improvements
1. **Kubernetes Migration**: For better orchestration
2. **Multi-Region**: Disaster recovery
3. **Auto-scaling**: Based on load
4. **Enhanced Monitoring**: APM integration

### Technology Roadmap
- Q1 2025: Kubernetes migration
- Q2 2025: Multi-region deployment
- Q3 2025: Enhanced security features
- Q4 2025: ML model optimization

## Support & Resources

### Documentation
- [Deployment Guide](./DEPLOYMENT_GUIDE.md)
- [Lambda Labs Guide](./LAMBDA_LABS_GUIDE.md)
- [Secret Management](./SECRET_MANAGEMENT.md)

### External Resources
- [Lambda Labs Documentation](https://docs.lambdalabs.com)
- [Docker Documentation](https://docs.docker.com)
- [FastAPI Documentation](https://fastapi.tiangolo.com)

### Support Channels
- GitHub Issues: [sophia-main/issues](https://github.com/ai-cherry/sophia-main/issues)
- Internal Slack: #sophia-infrastructure
- On-call: See rotation schedule 