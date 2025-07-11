# Lambda Labs Final Deployment Plan

## Current Status
- **Backend**: Running locally on port 8001 ✅
- **Frontend**: Running locally on port 5173 ✅
- **Snowflake**: Connected and working ✅
- **Lambda Labs**: All servers accessible ✅

## Lambda Labs Infrastructure

### Available Servers
1. **Backend Server** (sophia-ai-core)
   - IP: 192.222.58.232
   - Purpose: Backend API
   - Software: Docker installed

2. **MCP Server** (sophia-mcp-orchestrator)
   - IP: 104.171.202.117
   - Purpose: All MCP microservices
   - Software: Docker + Docker Compose v2

3. **Frontend Server** (sophia-production-instance)
   - IP: 104.171.202.103
   - Purpose: Web frontend
   - Software: Needs nginx

## Deployment Strategy

### Phase 1: Backend Deployment
```bash
# Deploy backend to 192.222.58.232
python scripts/deploy_docker_lambda.py
```

### Phase 2: MCP Servers
- Deploy all MCP servers to 104.171.202.117
- Use Docker Compose for orchestration
- Ports: 9001, 3008, 9003, 9004, 9006, 9102, 9101

### Phase 3: Frontend
- Build with production API URL
- Deploy to 104.171.202.103 with nginx

## Access URLs After Deployment
- **Frontend**: http://104.171.202.103
- **Backend API**: http://192.222.58.232:8001
- **API Docs**: http://192.222.58.232:8001/docs
- **MCP Servers**: http://104.171.202.117:PORT

## Verification Steps
1. Check backend health endpoint
2. Verify frontend loads
3. Test chat functionality
4. Monitor MCP server health

## Troubleshooting
- SSH Key: ~/.ssh/sophia2025.pem
- Default user: ubuntu
- Logs: `docker logs <container-name>` 