# Docker Cloud Quick Deploy Guide

## 🚀 Immediate Deployment Steps

### 1. Verify Prerequisites
```bash
# Check Docker login
docker login -u scoobyjava15

# Test Lambda Labs SSH
ssh ubuntu@192.222.58.232 "echo 'SSH OK'"
```

### 2. Deploy All V2 MCP Servers
```bash
# Run the automated deployment script
./scripts/docker-cloud-deploy-v2.sh
```

This script will:
- Build all 10 MCP server images
- Push to Docker Hub (scoobyjava15)
- Deploy to Lambda Labs via Docker Swarm
- Verify health checks

### 3. Manual Deployment (if script fails)

#### Build & Push Individual Server
```bash
# Example: Gong V2
docker build -t scoobyjava15/sophia-gong:latest \
  -f infrastructure/mcp_servers/gong_v2/Dockerfile \
  infrastructure/mcp_servers/gong_v2/

docker push scoobyjava15/sophia-gong:latest
```

#### Deploy on Lambda Labs
```bash
# SSH to Lambda Labs
ssh ubuntu@192.222.58.232

# Deploy stack
docker stack deploy -c docker-compose.mcp-v2.yml sophia-mcp-v2

# Check services
docker stack services sophia-mcp-v2
```

### 4. Verify Deployment
```bash
# From Lambda Labs
curl http://localhost:9000/health  # AI Memory
curl http://localhost:9001/health  # Snowflake
curl http://localhost:9006/health  # GitHub
curl http://localhost:9007/health  # Slack
curl http://localhost:9009/health  # Gong
```

## 🔥 Critical Services First

Deploy these first for immediate value:

1. **GitHub V2** (9006) - Source control
2. **Slack V2** (9007) - Team communication
3. **Gong V2** (9009) - Sales intelligence
4. **AI Memory V2** (9000) - Context management
5. **Codacy V2** (9005) - Code quality

## 🚨 Common Issues

### Docker Push Fails
```bash
# Re-authenticate
docker logout
docker login -u scoobyjava15
```

### Service Won't Start
```bash
# Check logs
docker service logs sophia-mcp-v2_gong-v2

# Remove and redeploy
docker service rm sophia-mcp-v2_gong-v2
docker stack deploy -c docker-compose.mcp-v2.yml sophia-mcp-v2
```

### Port Already in Use
```bash
# Find process using port
sudo lsof -i :9009
# Kill if necessary
sudo kill -9 <PID>
```

## ✅ Success Indicators

- All health endpoints return `{"status": "healthy"}`
- No error logs in first 5 minutes
- Cursor can connect to MCP servers
- API calls succeed (test with curl)

## 📞 Quick Commands

```bash
# View all logs
docker service logs sophia-mcp-v2_gong-v2 --follow

# Scale service
docker service scale sophia-mcp-v2_gong-v2=3

# Update service
docker service update --force sophia-mcp-v2_gong-v2

# Remove everything
docker stack rm sophia-mcp-v2
```

---

**Deploy NOW with: `./scripts/docker-cloud-deploy-v2.sh`** 🚀
