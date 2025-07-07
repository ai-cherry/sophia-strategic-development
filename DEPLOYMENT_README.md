# Sophia Intel AI Deployment Guide

## 🌐 Production Deployment: sophia-intel.ai

This guide covers the complete deployment process for the Sophia AI platform using the **sophia-intel.ai** domain with integrated Lambda Labs backend and Vercel frontend.

### 🏗️ Infrastructure Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    SOPHIA INTEL AI ARCHITECTURE                 │
├─────────────────────────────────────────────────────────────────┤
│ Frontend (Vercel)           │ Backend (Lambda Labs)             │
├─────────────────────────────┼───────────────────────────────────┤
│ app.sophia-intel.ai         │ api.sophia-intel.ai               │
│ admin.sophia-intel.ai       │ ├─ sophia-ai-core (192.222.58.232)│
│ docs.sophia-intel.ai        │ ├─ sophia-production (104.171.202.103)│
│ status.sophia-intel.ai      │ ├─ sophia-mcp-orchestrator (104.171.202.117)│
│ dev.app.sophia-intel.ai     │ ├─ sophia-data-pipeline (104.171.202.134)│
│                             │ └─ sophia-development (155.248.194.183)│
└─────────────────────────────────────────────────────────────────┘
```

### 🚀 Quick Deployment

#### Automated Deployment (Recommended)
```bash
# Deploy all phases
python scripts/deploy_sophia_intel_ai.py --phase all

# Deploy specific phase
python scripts/deploy_sophia_intel_ai.py --phase 1  # Vercel cleanup
python scripts/deploy_sophia_intel_ai.py --phase 2  # Domain integration
python scripts/deploy_sophia_intel_ai.py --phase 3  # Backend integration
python scripts/deploy_sophia_intel_ai.py --phase 4  # Monitoring setup
```

#### Manual GitHub Actions Deployment
1. Go to GitHub Actions in the repository
2. Select "Deploy Sophia Intel AI" workflow
3. Click "Run workflow"
4. Choose deployment phase (default: all)
5. Monitor deployment progress

### 📋 Deployment Phases

#### Phase 1: Immediate Fixes (4 hours)
**Objective**: Clean up Vercel projects and fix build configurations

**Actions**:
- Delete unnecessary Vercel projects (sophia-ai-frontend-dev, sophia-ai-frontend-prod, etc.)
- Rename main projects to sophia-intel-ai-* naming convention
- Fix build configurations and environment variables
- Ensure first successful deployment

**Verification**:
```bash
# Check Vercel projects
vercel projects ls

# Verify build success
curl -f https://app.sophia-intel.ai
```

#### Phase 2: Domain Integration (6 hours)
**Objective**: Optimize DNS and establish custom domain routing

**Actions**:
- Add missing DNS records (admin, docs, status, staging)
- Configure SSL certificates for all subdomains
- Set up custom domains in Vercel projects
- Implement load balancing for API endpoints

**Verification**:
```bash
# Test DNS resolution
nslookup admin.sophia-intel.ai
nslookup api.sophia-intel.ai

# Verify SSL certificates
curl -I https://app.sophia-intel.ai
```

#### Phase 3: Backend Integration (8 hours)
**Objective**: Connect Vercel frontend to Lambda Labs backend

**Actions**:
- Test Lambda Labs instance connectivity
- Deploy API gateway configuration
- Configure CORS for sophia-intel.ai domains
- Implement WebSocket support for real-time features

**Verification**:
```bash
# Test API connectivity
curl https://api.sophia-intel.ai/health

# Test MCP endpoints
curl https://api.sophia-intel.ai/mcp/health
```

#### Phase 4: Monitoring & Optimization (6 hours)
**Objective**: Implement comprehensive monitoring and optimization

**Actions**:
- Deploy status page at status.sophia-intel.ai
- Configure Prometheus and Grafana monitoring
- Set up cost monitoring and alerts
- Apply performance optimizations

**Verification**:
```bash
# Check status page
curl https://status.sophia-intel.ai

# Verify monitoring
curl https://status.sophia-intel.ai/api/status
```

### 🔐 Environment Configuration

#### Required GitHub Organization Secrets
```bash
LAMBDA_API_KEY=<lambda_labs_api_key>
LAMBDA_SSH_KEY=<ssh_public_key>
LAMBDA_PRIVATE_SSH_KEY=<ssh_private_key>
VERCEL_API_TOKEN=zjlHk1AEREFUS3DmLivZ90GZ
NAMECHEAP_API_KEY=d6913ec33b2c4d328be9cbb4db382eca
SOPHIA_INTEL_DOMAIN=sophia-intel.ai
```

#### Pulumi ESC Configuration
The deployment uses Pulumi ESC environment: `sophia-intel-ai-production`

**Configuration file**: `infrastructure/esc/sophia-intel-ai-production.yaml`

**Key features**:
- Centralized secret management
- Environment variable distribution
- Cost monitoring configuration
- Security and CORS settings

### 🌐 Domain Configuration

#### Current DNS Records (Namecheap)
```yaml
DNS Records:
  "@":          A      → 34.74.88.2
  "api":        A      → 34.74.88.2
  "webhooks":   A      → 34.74.88.2
  "app":        CNAME  → cname.vercel-dns.com
  "admin":      CNAME  → cname.vercel-dns.com
  "docs":       CNAME  → cname.vercel-dns.com
  "status":     CNAME  → cname.vercel-dns.com
  "dev.app":    CNAME  → cname.vercel-dns.com
  "staging":    CNAME  → cname.vercel-dns.com
  "www":        CNAME  → sophia-intel.ai
```

#### SSL Configuration
- **Provider**: Vercel (Let's Encrypt)
- **Coverage**: *.sophia-intel.ai
- **Auto-renewal**: Enabled
- **HTTPS redirect**: Forced

### 🖥️ Lambda Labs Infrastructure

#### Instance Configuration
```yaml
sophia-ai-core:
  ip: 192.222.58.232
  type: GH200 (96GB GPU)
  cost: $1.49/hour
  services: [AI Memory MCP (9001), FastAPI Backend (8000)]
  
sophia-production-instance:
  ip: 104.171.202.103
  type: RTX6000 (24GB GPU)
  cost: $0.50/hour
  services: [Prometheus (9090), Grafana (3000)]
  
sophia-mcp-orchestrator:
  ip: 104.171.202.117
  type: A6000 (48GB GPU)
  cost: $0.80/hour
  services: [MCP Gateway (8080)]
  
sophia-data-pipeline:
  ip: 104.171.202.134
  type: A100 (40GB GPU)
  cost: $1.29/hour
  services: [Snowflake Connections, ETL Pipelines]
  
sophia-development:
  ip: 155.248.194.183
  type: A10 (24GB GPU)
  cost: $0.75/hour
  services: [Development MCP Servers]
```

**Total Cost**: $4.83/hour ($115.92/day, $3,477.60/month)

### 📊 Monitoring & Health Checks

#### Status Page: https://status.sophia-intel.ai
- Real-time infrastructure status
- API endpoint health monitoring
- Performance metrics dashboard
- Incident management integration

#### Monitoring Endpoints
```yaml
Health Checks:
  - https://api.sophia-intel.ai/health
  - https://app.sophia-intel.ai
  - https://admin.sophia-intel.ai
  - 192.222.58.232:8000/health
  - 104.171.202.103:3000/health

Monitoring Tools:
  - Prometheus: 104.171.202.103:9090
  - Grafana: 104.171.202.103:3000
  - Vercel Analytics: Enabled
  - Speed Insights: Enabled
```

#### Performance Targets
```yaml
Frontend Performance:
  - First Contentful Paint: <1.5s
  - Largest Contentful Paint: <2.5s
  - Cumulative Layout Shift: <0.1

Backend Performance:
  - API Response Time: <500ms
  - WebSocket Latency: <100ms
  - Uptime: >99.9%

Deployment Health:
  - Success Rate: >99%
  - Build Time: <3 minutes
  - Rollback Time: <1 minute
```

### 🔄 CI/CD Pipeline

#### GitHub Actions Workflow
**File**: `.github/workflows/deploy-sophia-intel-ai.yml`

**Triggers**:
- Push to main branch
- Pull request to main branch
- Manual workflow dispatch

**Jobs**:
1. **Test**: Run frontend/backend tests and linting
2. **Validate Infrastructure**: Check Lambda Labs connectivity
3. **Deploy Staging**: Deploy to staging environment (PR only)
4. **Deploy Production**: Full production deployment (main branch)
5. **Manual Deployment**: On-demand deployment with phase selection

#### Deployment Strategy
- **Rolling deployment** with health checks
- **Automatic rollback** on failure
- **Blue-green deployment** for zero-downtime updates
- **Feature flag** support for gradual rollouts

### 🚨 Troubleshooting

#### Common Issues

**1. Vercel Deployment Failures**
```bash
# Check build logs
vercel logs <deployment-url>

# Verify environment variables
vercel env ls --scope=<project-name>

# Test build locally
cd frontend && npm run build
```

**2. Lambda Labs Connectivity Issues**
```bash
# Test instance connectivity
python scripts/validate_lambda_infrastructure.py

# Check SSH access
ssh -i ~/.ssh/sophia_lambda_key ubuntu@192.222.58.232

# Verify API endpoints
curl https://api.sophia-intel.ai/health
```

**3. DNS Resolution Problems**
```bash
# Check DNS propagation
nslookup app.sophia-intel.ai
dig app.sophia-intel.ai

# Verify SSL certificates
openssl s_client -connect app.sophia-intel.ai:443
```

#### Emergency Procedures

**Rollback Deployment**:
```bash
# Vercel rollback
vercel rollback <deployment-url>

# Lambda Labs rollback
python scripts/deploy_sophia_intel_ai.py --rollback
```

**Emergency Contacts**:
- **Vercel Support**: support@vercel.com
- **Lambda Labs Support**: support@lambdalabs.com
- **Namecheap Support**: support@namecheap.com

### 📈 Cost Optimization

#### Current Costs
```yaml
Monthly Breakdown:
  Lambda Labs: $3,477.60 (5 instances × $4.83/hour × 24h × 30 days)
  Vercel: $0 (Pro plan included)
  Namecheap: $1 (Annual domain cost amortized)
  Total: ~$3,478.60/month
```

#### Optimization Strategies
- **Instance scheduling**: Consider shutting down development instance during off-hours
- **Auto-scaling**: Implement demand-based scaling for non-critical instances
- **Cost alerts**: Set up alerts at 90% of monthly budget
- **Resource monitoring**: Track GPU utilization and optimize instance types

### 🔒 Security

#### Security Headers
```yaml
Implemented Headers:
  - Strict-Transport-Security: max-age=31536000; includeSubDomains
  - Content-Security-Policy: default-src 'self' https://api.sophia-intel.ai
  - X-Frame-Options: DENY
  - X-Content-Type-Options: nosniff
  - Referrer-Policy: strict-origin-when-cross-origin
```

#### CORS Configuration
```yaml
Allowed Origins:
  - https://app.sophia-intel.ai
  - https://admin.sophia-intel.ai
  - https://docs.sophia-intel.ai
  - https://dev.app.sophia-intel.ai
  - https://staging.sophia-intel.ai
  - https://sophia-intel.ai
```

#### Secret Management
- **Storage**: GitHub Organization Secrets → Pulumi ESC
- **Encryption**: AES-256 at rest and in transit
- **Access Control**: Role-based with audit logging
- **Rotation**: Automated every 90 days

### 📚 Additional Resources

- **Lambda Labs Documentation**: [docs.lambdalabs.com](https://docs.lambdalabs.com)
- **Vercel Documentation**: [vercel.com/docs](https://vercel.com/docs)
- **Pulumi ESC Documentation**: [pulumi.com/docs/esc](https://pulumi.com/docs/esc)
- **Namecheap API Documentation**: [namecheap.com/support/api](https://namecheap.com/support/api)

### 🎯 Success Metrics

#### Deployment Success Criteria
- [ ] All Vercel projects deploying successfully (100% success rate)
- [ ] Custom domains resolving correctly
- [ ] SSL certificates active and valid
- [ ] API endpoints responding within 500ms
- [ ] Frontend applications loading within 2 seconds
- [ ] WebSocket connections stable
- [ ] Monitoring dashboards operational
- [ ] Cost tracking within budget

#### Post-Deployment Validation
```bash
# Run comprehensive validation
python scripts/validate_sophia_intel_ai_deployment.py

# Check all endpoints
curl -f https://app.sophia-intel.ai
curl -f https://admin.sophia-intel.ai
curl -f https://api.sophia-intel.ai/health
curl -f https://status.sophia-intel.ai

# Verify performance
lighthouse https://app.sophia-intel.ai
```

---

**🎉 Deployment Complete!**

Your Sophia AI platform is now live at **sophia-intel.ai** with full Lambda Labs integration, monitoring, and optimization. The platform is production-ready and scalable for enterprise use.

