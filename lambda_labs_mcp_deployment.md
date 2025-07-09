# MCP Production Deployment - ALL SERVERS
Timestamp: 2025-07-06 16:46:39 UTC
Target: Lambda Labs Production (165.1.69.44)
Registry: scoobyjava15
Environment: prod

## DEPLOYING ALL 20 MCP SERVERS TO LAMBDA LABS

### Critical Servers (Production Essential):
- **ai_memory** (Port: 9000) - 🔴 CRITICAL
- **codacy** (Port: 3008) - 🔴 CRITICAL
- **linear** (Port: 9004) - 🔴 CRITICAL
- **github** (Port: 9001) - 🔴 CRITICAL
- **slack_unified** (Port: 9002) - 🔴 CRITICAL
- **hubspot_unified** (Port: 9003) - 🔴 CRITICAL
- **snowflake_unified** (Port: 9005) - 🔴 CRITICAL

### Standard Servers (Extended Functionality):
- **notion** (Port: 9006) - 🟢 STANDARD
- **asana** (Port: 9007) - 🟢 STANDARD
- **lambda_labs_cli** (Port: 9008) - 🟢 STANDARD
- **postgres** (Port: 9009) - 🟢 STANDARD
- **pulumi** (Port: 9010) - 🟢 STANDARD
- **playwright** (Port: 9011) - 🟢 STANDARD
- **figma_context** (Port: 9012) - 🟢 STANDARD
- **ui_ux_agent** (Port: 9013) - 🟢 STANDARD
- **v0dev** (Port: 9014) - 🟢 STANDARD
- **intercom** (Port: 9015) - 🟢 STANDARD
- **apollo** (Port: 9016) - 🟢 STANDARD
- **bright_data** (Port: 9017) - 🟢 STANDARD
- **salesforce** (Port: 9018) - 🟢 STANDARD

## Deployment Configuration:
- **Registry**: scoobyjava15
- **Environment**: prod
- **Target Host**: 165.1.69.44
- **Deployment Method**: GitHub Actions Automated Pipeline
- **Docker Images**: sophia-[server]-mcp:latest format

## Expected Deployment Results:
- All 20 MCP servers built and pushed to registry
- All servers deployed to Lambda Labs production infrastructure
- Health endpoints active and monitored
- Production logging and monitoring enabled
- Automatic restart policies configured

## Health Check URLs (Post-Deployment):
- ai_memory: http://165.1.69.44:9000/health
- codacy: http://165.1.69.44:3008/health
- linear: http://165.1.69.44:9004/health
- github: http://165.1.69.44:9001/health
- slack_unified: http://165.1.69.44:9002/health
- hubspot_unified: http://165.1.69.44:9003/health
- snowflake_unified: http://165.1.69.44:9005/health
- notion: http://165.1.69.44:9006/health
- asana: http://165.1.69.44:9007/health
- lambda_labs_cli: http://165.1.69.44:9008/health
- postgres: http://165.1.69.44:9009/health
- pulumi: http://165.1.69.44:9010/health
- playwright: http://165.1.69.44:9011/health
- figma_context: http://165.1.69.44:9012/health
- ui_ux_agent: http://165.1.69.44:9013/health
- v0dev: http://165.1.69.44:9014/health
- intercom: http://165.1.69.44:9015/health
- apollo: http://165.1.69.44:9016/health
- bright_data: http://165.1.69.44:9017/health
- salesforce: http://165.1.69.44:9018/health

# MCP Servers Deployment Strategy for Lambda Labs

## 🎯 Where Should MCP Servers Run?

**Answer: On Lambda Labs Server (192.222.58.232), NOT locally**

### Why Lambda Labs?
1. **Production Environment** - Closer to backend API and databases
2. **Better Performance** - Direct network access, no internet latency
3. **Security** - Secrets managed through Docker Swarm/Pulumi ESC
4. **Scalability** - Can leverage GPU resources when needed
5. **High Availability** - Docker Swarm handles restarts and health checks

### Current Architecture:
- **Frontend**: Vercel (app.sophia-intel.ai)
- **Backend API**: Lambda Labs (api.sophia-intel.ai)
- **MCP Servers**: Lambda Labs (ports 9001-9104)
- **Database**: Lambda Labs (PostgreSQL + Redis)

## 📋 Updated Deployment Approach

### Step 1: Update Docker Compose for Lambda Labs

Create `docker-compose.mcp-lambda.yml`:

```yaml
version: "3.8"

services:
  # Essential MCP Servers for Lambda Labs deployment
  ai-memory:
    image: ${DOCKER_REGISTRY:-scoobyjava15}/sophia-mcp-ai-memory:${IMAGE_TAG:-latest}
    environment:
      - PORT=9001
      - ENVIRONMENT=production
      - PULUMI_ORG=scoobyjava-org
    ports:
      - "9001:9001"
    deploy:
      mode: replicated
      replicas: 1
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9001/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - sophia-overlay

  snowflake-unified:
    image: ${DOCKER_REGISTRY:-scoobyjava15}/sophia-mcp-snowflake:${IMAGE_TAG:-latest}
    environment:
      - PORT=9002
      - ENVIRONMENT=production
      - PULUMI_ORG=scoobyjava-org
    ports:
      - "9002:9002"
    deploy:
      mode: replicated
      replicas: 1
      restart_policy:
        condition: on-failure
    networks:
      - sophia-overlay

  # Add other 3 essential servers...

networks:
  sophia-overlay:
    external: true
```

### Step 2: Deploy to Lambda Labs

```bash
# SSH into Lambda Labs
ssh ubuntu@192.222.58.232

# Navigate to Sophia AI directory
cd /opt/sophia-ai

# Pull latest code
git pull origin main

# Build and deploy MCP servers
docker-compose -f docker-compose.mcp-lambda.yml build
docker-compose -f docker-compose.mcp-lambda.yml up -d

# Or use Docker Swarm (recommended for production)
docker stack deploy -c docker-compose.mcp-lambda.yml sophia-mcp
```

### Step 3: Update Frontend API Client

The frontend should connect to MCP servers via the backend API, not directly:

```javascript
// frontend/src/services/apiClient.js
const API_CONFIG = {
  production: 'https://api.sophia-intel.ai',
  // MCP servers accessed through backend proxy
  mcp: {
    aiMemory: '/api/v1/mcp/ai-memory',
    snowflake: '/api/v1/mcp/snowflake',
    // etc...
  }
};
```

### Step 4: Backend Proxy for MCP Servers

The backend should proxy MCP requests:

```python
# backend/api/mcp_proxy_routes.py
from fastapi import APIRouter
import httpx

router = APIRouter(prefix="/api/v1/mcp")

@router.post("/ai-memory/{path:path}")
async def proxy_ai_memory(path: str, request: Request):
    async with httpx.AsyncClient() as client:
        # Proxy to internal MCP server
        response = await client.post(
            f"http://ai-memory:9001/{path}",
            json=await request.json(),
            headers=request.headers
        )
        return response.json()
```

## 🔧 Updated Health Check Script

```bash
#!/bin/bash
# health_check_lambda.sh

echo "🏥 Sophia AI Health Check (Lambda Labs)"
echo "======================================="

# Check services on Lambda Labs
echo "Checking Lambda Labs services..."

# Frontend (still on Vercel)
echo -n "Frontend (app.sophia-intel.ai): "
curl -s -o /dev/null -w "%{http_code}\n" https://app.sophia-intel.ai

# Backend API on Lambda Labs
echo -n "Backend API (api.sophia-intel.ai): "
curl -s https://api.sophia-intel.ai/health | jq '.' || echo "Failed"

# MCP Servers on Lambda Labs (via SSH)
echo ""
echo "MCP Servers (on Lambda Labs):"
ssh ubuntu@192.222.58.232 << 'EOF'
for port in 9001 9002 9005 9103 9104; do
  echo -n "  Port $port: "
  curl -s localhost:$port/health | jq '.status' || echo "Not responding"
done
EOF
```

## 📊 Benefits of Lambda Labs Deployment

1. **Unified Infrastructure** - All backend services in one place
2. **Better Security** - No exposed MCP ports to internet
3. **Improved Performance** - Internal network communication
4. **Easier Management** - Single server to maintain
5. **Cost Effective** - Utilizing existing Lambda Labs instance

## 🚨 Important Notes

1. **Never expose MCP ports directly to internet** - Always proxy through backend
2. **Use Docker Swarm for production** - Better than docker-compose
3. **Monitor resource usage** - MCP servers can be memory intensive
4. **Keep secrets in Pulumi ESC** - Never hardcode credentials

## 🎯 Summary

MCP servers should run on **Lambda Labs (192.222.58.232)** alongside the backend API, not locally. This provides better security, performance, and easier management in production.
