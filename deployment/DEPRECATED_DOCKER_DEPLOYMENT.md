# ⚠️ DEPRECATED: Docker-Based Deployment

**STATUS:** DEPRECATED - These files conflict with production infrastructure  
**DATE:** July 16, 2025  
**REASON:** Production uses distributed systemd services, not containerized deployment

## 🚨 CRITICAL NOTICE

**ALL DOCKER COMPOSE FILES IN THIS DIRECTORY ARE DEPRECATED**

The production Sophia AI infrastructure uses:
- ✅ **5 Lambda Labs instances** with direct Python processes
- ✅ **systemd service management** with auto-restart
- ✅ **nginx load balancing** on primary instance (192.222.58.232)
- ✅ **Direct inter-instance HTTP communication** on ports 8000-8499

**These Docker files expect:**
- ❌ **Containerized services** (conflicts with direct Python processes)
- ❌ **Docker overlay networks** (conflicts with direct IP routing)
- ❌ **Docker Swarm/Compose** (conflicts with systemd management)
- ❌ **Container-to-container communication** (conflicts with HTTP)

## 📋 DEPRECATED FILES

| File | Purpose | Conflicts With |
|------|---------|----------------|
| `docker-compose-production.yml` | Production Docker deployment | systemd services |
| `docker-compose-ai-core.yml` | AI Core containers | Direct Python processes |
| `docker-compose-mcp-orchestrator.yml` | MCP container orchestration | Distributed MCP services |
| `docker-compose-data-pipeline.yml` | Data processing containers | Direct service deployment |
| `docker-compose-development.yml` | Development environment | Development instance systemd |

## 🎯 USE INSTEAD

### **Production Deployment**
```bash
# Deploy to distributed systemd infrastructure
python scripts/deploy_distributed_systemd.py

# Validate deployment
python scripts/deploy_distributed_systemd.py --validate-only

# Deploy to specific instance
python scripts/deploy_distributed_systemd.py --instance ai_core
```

### **Configuration**
```python
# Production infrastructure configuration
from config.production_infrastructure import PRODUCTION_INFRASTRUCTURE

# Production-aligned port configuration  
# See: config/production_aligned_mcp_ports.json
```

### **Health Monitoring**
```bash
# Monitor all instances
python scripts/monitor_production_deployment.py

# Check specific service
curl http://192.222.58.232:8000/health  # AI Core
curl http://104.171.202.117:8100/health  # Business Tools
curl http://104.171.202.134:8200/health  # Data Pipeline
```

## 📊 DEPLOYMENT ALIGNMENT SCORECARD

| Component | Docker Approach | Production Reality | Status |
|-----------|-----------------|-------------------|---------|
| **Service Management** | Docker Compose | systemd services | ❌ **CONFLICT** |
| **Networking** | Docker overlay | Direct IP routing | ❌ **CONFLICT** |
| **Load Balancing** | Docker Swarm | nginx upstream | ❌ **CONFLICT** |
| **Port Allocation** | Container ports | 8000-8499 range | ❌ **CONFLICT** |
| **Instance Distribution** | Single Docker host | 5 Lambda Labs instances | ❌ **CONFLICT** |

## ⚡ MIGRATION IMPACT

**If you were using Docker deployment:**
1. **Immediate Impact:** Docker files will not work with production
2. **Required Action:** Use `scripts/deploy_distributed_systemd.py`
3. **Configuration Update:** Switch to `config/production_aligned_mcp_ports.json`
4. **Monitoring Change:** Use production health check endpoints

## 🔄 FUTURE PLANS

These Docker files will be:
1. **Archived** after 30 days (August 15, 2025)
2. **Removed** from active codebase
3. **Replaced** with systemd-based deployment tooling

## 🆘 NEED HELP?

**For Production Deployment Issues:**
- Use: `scripts/deploy_distributed_systemd.py --dry-run`
- Check: `config/production_infrastructure.py`
- Monitor: `http://192.222.58.232:9100` (Health Dashboard)

**For Emergency Support:**
- Validate current deployment: `scripts/deploy_distributed_systemd.py --validate-only`
- Check service status: Individual health endpoints listed above

---

**⚠️ DO NOT USE THESE DOCKER FILES FOR PRODUCTION DEPLOYMENT**

They will fail because production infrastructure is fundamentally different.
Use the systemd-based deployment approach documented above. 