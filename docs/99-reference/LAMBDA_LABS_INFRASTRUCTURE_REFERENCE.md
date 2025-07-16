# Lambda Labs Infrastructure Reference

## 🔐 **IP Addresses for Whitelisting**

**CRITICAL**: These IP addresses must be whitelisted in any external services:

### **Production Infrastructure IPs:**
- **`104.171.202.103`** - sophia-production-instance (RTX6000)
- **`192.222.58.232`** - sophia-ai-core (GH200) **← PRIMARY PRODUCTION**
- **`104.171.202.117`** - sophia-mcp-orchestrator (A6000)
- **`104.171.202.134`** - sophia-data-pipeline (A100)
- **`155.248.194.183`** - sophia-development (A10)

### **Primary Production Server:**
**`192.222.58.232`** - Main production server with GH200 GPU

---

## 🏗️ **Infrastructure Overview**

| Instance | IP Address | GPU Type | Region | Purpose | SSH Command |
|----------|------------|----------|---------|---------|-------------|
| sophia-production-instance | 104.171.202.103 | RTX6000 | us-south-1 | Production Services | `ssh ubuntu@104.171.202.103` |
| sophia-ai-core | 192.222.58.232 | GH200 | us-east-3 | AI Processing | `ssh ubuntu@192.222.58.232` |
| sophia-mcp-orchestrator | 104.171.202.117 | A6000 | us-south-1 | MCP Servers | `ssh ubuntu@104.171.202.117` |
| sophia-data-pipeline | 104.171.202.134 | A100 | us-south-1 | Data Processing | `ssh ubuntu@104.171.202.134` |
| sophia-development | 155.248.194.183 | A10 | us-west-1 | Development | `ssh ubuntu@155.248.194.183` |

---

## 🔑 **Secret Management**

### **GitHub Organization Secrets → Pulumi ESC → Backend**
All secrets are managed through the unified pipeline:

1. **GitHub Organization**: `https://github.com/organizations/ai-cherry/settings/secrets/actions`
2. **Pulumi ESC**: `scoobyjava-org/default/sophia-ai-production`
3. **Backend**: `backend/core/auto_esc_config.py`

### **Lambda Labs Secrets:**
- `LAMBDA_API_KEY` - API authentication
- `LAMBDA_SSH_KEY` - SSH public key
- `LAMBDA_PRIVATE_SSH_KEY` - SSH private key
- `LAMBDA_API_ENDPOINT` - https://cloud.lambda.ai/api/v1/instances

---

## 🌐 **Domain Configuration**

### **DNS Records (Namecheap)**
- **sophia-intel.ai** → 192.222.58.232
- **api.sophia-intel.ai** → 192.222.58.232
- **webhooks.sophia-intel.ai** → 192.222.58.232
- **app.sophia-intel.ai** → Lambda Labs CNAME
- **dev.app.sophia-intel.ai** → Lambda Labs CNAME

### **SSL/TLS**
- All domains secured with Let's Encrypt
- Automatic renewal via Certbot
- Nginx reverse proxy configuration

---

## 📊 **Service Distribution**

### **sophia-ai-core (192.222.58.232) - PRIMARY**
- Backend API (Port 8000)
- AI Memory MCP (Port 9001)
- PostgreSQL (Port 5432)
- Redis (Port 6379)
- Qdrant (Port 8080)

### **sophia-mcp-orchestrator (104.171.202.117)**
- MCP Gateway (Port 8080)
- Individual MCP Servers (Ports 9000-9021)
- Business Intelligence APIs

### **sophia-data-pipeline (104.171.202.134)**
- ETL Pipelines
- Data Processing
- Analytics Services

### **sophia-production-instance (104.171.202.103)**
- Monitoring (Prometheus/Grafana)
- Load Balancing
- Production Operations

### **sophia-development (155.248.194.183)**
- Development Environment
- Testing Infrastructure
- CI/CD Services

---

## 🔧 **Quick Reference Commands**

### **Health Checks**
```bash
# Primary production
curl http://192.222.58.232:8000/health

# MCP servers
curl http://104.171.202.117:8080/health

# All instances
for ip in 104.171.202.103 192.222.58.232 104.171.202.117 104.171.202.134 155.248.194.183; do
  echo "Checking $ip..."
  ssh ubuntu@$ip "echo 'OK'"
done
```

### **Deployment Commands**
```bash
# Deploy to production
python scripts/deploy_to_lambda_labs.py --environment=prod

# Deploy MCP servers
python scripts/deploy_mcp_servers.py --target=104.171.202.117

# Full deployment
python scripts/unified_deployment_orchestrator.py
```

---

## 💰 **Cost Information**

| Instance | Cost/Hour | Monthly Cost | Annual Cost |
|----------|-----------|--------------|-------------|
| sophia-production-instance | $0.50 | $360 | $4,320 |
| sophia-ai-core | $1.49 | $1,073 | $12,876 |
| sophia-mcp-orchestrator | $0.80 | $576 | $6,912 |
| sophia-data-pipeline | $1.29 | $929 | $11,148 |
| sophia-development | $0.75 | $540 | $6,480 |
| **TOTAL** | **$4.83** | **$3,478** | **$41,736** |

---

## 🚨 **Critical Notes**

1. **Primary Production IP**: `192.222.58.232` - This is the main server that handles all production traffic
2. **Whitelist All IPs**: External services should whitelist all 5 IP addresses for redundancy
3. **SSH Access**: All instances use the same SSH key (`sophia2025`)
4. **Secret Management**: Never hardcode secrets - always use Pulumi ESC integration
5. **Domain Routing**: All API traffic goes through `192.222.58.232`

---

## 📞 **Support Information**

- **Infrastructure Code**: `backend/integrations/lambda_labs_client.py`
- **Deployment Scripts**: `scripts/deploy_to_lambda_labs.py`
- **Secret Management**: `backend/core/auto_esc_config.py`
- **DNS Management**: Namecheap console
- **Monitoring**: Grafana at `http://104.171.202.103:3000` 