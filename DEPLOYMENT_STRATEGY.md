# 🚀 Sophia AI Deployment Strategy

## Current Situation

### Server Status
- **sophia-production-instance (104.171.202.103)**: Experiencing timeouts, unreliable
- **sophia-ai-core (192.222.58.232)**: ✅ WORKING - GH200 with 96GB RAM

### What's Running on sophia-ai-core
- ✅ PostgreSQL (healthy, port 5432)
- ✅ Redis (healthy, port 6379)
- ❌ 9 MCP servers in restart loops (need fixing)
- ✅ sophia-main directory exists and updated

## Recommended Strategy

### Option 1: Deploy to GH200 Server (RECOMMENDED)
The sophia-ai-core server (192.222.58.232) is more powerful and currently accessible.

```bash
# 1. Update DNS to point to GH200
./scripts/update_dns_to_correct_ip.sh 192.222.58.232

# 2. Fix the failing MCP servers
ssh -i ~/.ssh/sophia2025.pem ubuntu@192.222.58.232
cd ~/sophia-main

# Stop failing containers
docker stop $(docker ps -q --filter "status=restarting")
docker rm $(docker ps -aq --filter "status=exited")

# 3. Deploy backend
./scripts/quick_backend_deploy.sh

# 4. Deploy frontend
./scripts/quick_frontend_deploy.sh
```

### Option 2: Debug Production Instance
If you need to use 104.171.202.103:

```bash
# Check instance status
python3 scripts/lambda_labs_manager.py list --json

# Try to restart the instance via API
# (May need to use Lambda Labs dashboard)
```

### Option 3: Full Fresh Deploy
Deploy everything fresh to a working server:

```bash
# Use the robust deployment script
chmod +x scripts/deploy_sophia_robust.sh

# Update IP to use GH200
sed -i '' 's/104.171.202.103/192.222.58.232/g' scripts/deploy_sophia_robust.sh

# Run deployment
./scripts/deploy_sophia_robust.sh
```

## Immediate Action Items

1. **Stop failing MCP containers** on GH200
2. **Update code on server**:
   ```bash
   ssh -i ~/.ssh/sophia2025.pem ubuntu@192.222.58.232
   cd ~/sophia-main
   git pull origin main
   ```

3. **Deploy working backend**:
   ```bash
   # Simple FastAPI backend
   cd ~/sophia-main
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   python -m uvicorn api.main:app --host 0.0.0.0 --port 8000
   ```

4. **Update DNS** to point to 192.222.58.232

## Why MCP Servers Are Failing

The MCP servers are likely failing because:
1. Missing dependencies in the containers
2. Incorrect environment variables
3. Port conflicts
4. Missing source code mounts

## Quick Fix for MCP Servers

```bash
# SSH to server
ssh -i ~/.ssh/sophia2025.pem ubuntu@192.222.58.232

# Stop and remove failing containers
docker stop $(docker ps -q --filter "name=mcp")
docker rm $(docker ps -aq --filter "name=mcp")

# Check logs of one container to see the error
docker logs ai-memory-mcp

# Restart with proper configuration
cd ~/sophia-main
docker-compose -f deployment/docker-compose-mcp.yml up -d
``` 