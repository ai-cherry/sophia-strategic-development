# Sophia AI Unified Deployment - Complete Implementation

## 🚀 Deployment Overview

All V2 MCP servers are ready for Docker Cloud deployment to Lambda Labs (146.235.200.1).

### Architecture
- **Frontend**: Vercel (app.sophia-intel.ai)
- **Backend API**: Lambda Labs port 8000
- **MCP Servers**: Lambda Labs ports 9000-9009
- **Database**: PostgreSQL on Lambda Labs
- **Cache**: Redis on Lambda Labs
- **Container Orchestration**: Docker Swarm

## 📦 V2 MCP Servers Ready

| Server | Port | Priority | Purpose | Status |
|--------|------|----------|---------|--------|
| AI Memory V2 | 9000 | HIGH | Memory & context management | ✅ Ready |
| Snowflake V2 | 9001 | HIGH | Data warehouse operations | ✅ Ready |
| Linear V2 | 9002 | MEDIUM | Project management | ✅ Ready |
| Notion V2 | 9003 | MEDIUM | Documentation | ✅ Ready |
| Asana V2 | 9004 | MEDIUM | Task management | ✅ Ready |
| Codacy V2 | 9005 | HIGH | Code quality | ✅ Ready |
| GitHub V2 | 9006 | CRITICAL | Source control | ✅ Ready |
| Slack V2 | 9007 | CRITICAL | Team communication | ✅ Ready |
| Perplexity V2 | 9008 | HIGH | AI research | ✅ Ready |
| Gong V2 | 9009 | CRITICAL | Sales intelligence | ✅ Ready |

## 🔧 Deployment Commands

### 1. Build & Push All Images
```bash
chmod +x scripts/docker-cloud-deploy-v2.sh
./scripts/docker-cloud-deploy-v2.sh
```

### 2. Deploy to Lambda Labs
```bash
# SSH to Lambda Labs
ssh ubuntu@146.235.200.1

# Deploy stack
docker stack deploy -c docker-compose.mcp-v2.yml sophia-mcp-v2

# Check status
docker stack services sophia-mcp-v2
```

### 3. Verify Health
```bash
# From Lambda Labs
for port in {9000..9009}; do
  echo -n "Port $port: "
  curl -s http://localhost:$port/health | jq -r '.status' || echo "Not responding"
done
```

## 📋 Pre-Deployment Checklist

### Docker Hub
- [ ] Login: `docker login -u scoobyjava15`
- [ ] Verify push access to scoobyjava15 registry

### Lambda Labs
- [ ] SSH access verified: `ssh ubuntu@146.235.200.1`
- [ ] Docker Swarm initialized
- [ ] Overlay network created: sophia-ai-network

### Secrets (via Pulumi ESC)
- [ ] OPENAI_API_KEY
- [ ] ANTHROPIC_API_KEY
- [ ] SNOWFLAKE_ACCOUNT/USER/PASSWORD
- [ ] LINEAR_API_KEY
- [ ] NOTION_API_KEY
- [ ] ASANA_API_KEY
- [ ] CODACY_API_KEY
- [ ] GITHUB_TOKEN
- [ ] SLACK_BOT_TOKEN
- [ ] PERPLEXITY_API_KEY
- [ ] GONG_API_KEY
- [ ] GONG_API_SECRET

## 🚨 Critical Configuration

### Environment Variables (All Services)
```yaml
PULUMI_ORG: scoobyjava-org
ENVIRONMENT: production
```

### Docker Compose Features
- Health checks on all services
- Resource limits configured
- Automatic restart policies
- Overlay network for service discovery
- Docker secrets for credentials

## 📊 Post-Deployment Monitoring

### Service Logs
```bash
# View logs for specific service
docker service logs sophia-mcp-v2_gong-v2 --follow

# View all service logs
docker service logs sophia-mcp-v2_ai-memory-v2
docker service logs sophia-mcp-v2_snowflake-v2
# ... etc
```

### Service Scaling
```bash
# Scale high-priority services
docker service scale sophia-mcp-v2_github-v2=3
docker service scale sophia-mcp-v2_slack-v2=3
docker service scale sophia-mcp-v2_gong-v2=3
```

### Update Service
```bash
# Build new image
docker build -t scoobyjava15/sophia-gong-v2:latest infrastructure/mcp_servers/gong_v2/

# Push to Docker Hub
docker push scoobyjava15/sophia-gong-v2:latest

# Update running service
docker service update --image scoobyjava15/sophia-gong-v2:latest sophia-mcp-v2_gong-v2
```

## 🎯 Gong V2 Features

### Sales Intelligence
- Recent calls with insights
- Call transcripts with sentiment analysis
- Team performance analytics
- Coaching opportunities identification
- Conversation search
- Deal intelligence
- Action item tracking

### API Endpoints
- `GET /health` - Health check
- `POST /calls/recent` - Get recent calls
- `POST /transcript` - Get call transcript
- `POST /insights` - Generate sales insights
- `POST /coaching` - Find coaching opportunities
- `POST /search` - Search conversations
- `POST /team/analytics` - Team performance

### Integration with Sophia AI
- AI Memory integration for context
- Snowflake data warehouse sync
- Slack notifications for insights
- Linear/Asana task creation from action items

## 🔄 Rollback Procedure

If deployment fails:

```bash
# Remove failed stack
docker stack rm sophia-mcp-v2

# Redeploy previous version
docker stack deploy -c docker-compose.mcp-v1.yml sophia-mcp

# Check logs for errors
docker service logs sophia-mcp-v2_<service-name>
```

## 📝 Next Steps

1. **Deploy Phase 1** (Critical Services)
   - GitHub V2, Slack V2, Gong V2

2. **Deploy Phase 2** (High Priority)
   - AI Memory V2, Snowflake V2, Codacy V2, Perplexity V2

3. **Deploy Phase 3** (Supporting Services)
   - Linear V2, Notion V2, Asana V2

4. **Configure Cursor Integration**
   - Update cursor_mcp_config.json with Lambda Labs endpoints
   - Test MCP server connections
   - Verify tool availability

## 🎉 Success Criteria

- [ ] All 10 MCP servers responding to health checks
- [ ] Cursor can connect to all MCP servers
- [ ] API integrations verified (GitHub, Slack, Gong)
- [ ] Memory persistence working
- [ ] Snowflake queries executing
- [ ] No error logs in first 30 minutes

## 📞 Support

- **Docker Issues**: Check service logs
- **Network Issues**: Verify overlay network
- **Secret Issues**: Check Pulumi ESC configuration
- **Performance Issues**: Scale services as needed

---

**Ready for Production Deployment!** 🚀
