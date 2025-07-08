# Unified Chat Deployment Checklist

## 🚀 GitHub Push Status
✅ **Successfully pushed to GitHub** (commit: 336df9091)
- Branch: main
- Repository: https://github.com/ai-cherry/sophia-main

## 📦 Docker Cloud Deployment (Lambda Labs)

### Backend Integration
The unified chat is integrated into the main Sophia backend service:

1. **Docker Image**: `scoobyjava15/sophia-ai:latest`
   - ✅ Contains new unified chat service at `backend/services/unified_chat_service.py`
   - ✅ API routes mounted at `/api/unified-chat/*`
   - ✅ WebSocket support enabled

2. **Environment Variables**:
   ```yaml
   - ENVIRONMENT=prod
   - PULUMI_ORG=scoobyjava-org
   - REDIS_URL=redis://redis:6379
   - POSTGRES_URL=postgresql://sophia:${POSTGRES_PASSWORD}@postgres:5432/sophia
   ```

3. **Health Checks**:
   - Main health endpoint: `http://localhost:8000/api/health`
   - Unified chat health: `http://localhost:8000/api/unified-chat/health`

### Required Services
All these services must be running for full unified chat functionality:

- ✅ **Redis** (port 6379) - For caching and real-time features
- ✅ **PostgreSQL** (port 5432) - For persistent storage
- ✅ **Traefik** - For routing and SSL
- ✅ **Prometheus/Grafana** - For monitoring

## 🌐 Vercel Frontend Deployment

### Configuration Updates
The Vercel configuration already supports the new routes:

1. **Route Rewrites**:
   ```json
   {
     "source": "/chat",
     "destination": "/index.html"
   }
   ```

2. **Environment Variables** (needed in Vercel dashboard):
   ```
   VITE_API_URL=https://api.sophia-ai.lambda.cloud
   VITE_WS_URL=wss://api.sophia-ai.lambda.cloud
   VITE_ENVIRONMENT=production
   ```

## 🔧 Deployment Steps

### 1. Build and Push Docker Image
```bash
# Build the new image with unified chat
cd /Users/lynnmusil/sophia-main
docker build -t scoobyjava15/sophia-ai:latest -f Dockerfile.production .
docker push scoobyjava15/sophia-ai:latest
```

### 2. Deploy to Lambda Labs
```bash
# SSH into Lambda Labs
ssh -i ~/.ssh/lambda_labs ubuntu@146.235.200.1

# Deploy the stack
docker stack deploy -c docker-compose.cloud.yml sophia-ai

# Verify services
docker service ls
docker service logs sophia-ai_sophia-backend
```

### 3. Verify Frontend Deployment
```bash
# Trigger Vercel deployment
vercel --prod

# Or via GitHub Actions (automatic on push to main)
```

## ✅ Post-Deployment Verification

### API Endpoints to Test
1. **Health Check**:
   ```bash
   curl https://api.sophia-ai.lambda.cloud/api/unified-chat/health
   ```

2. **Chat Endpoint**:
   ```bash
   curl -X POST https://api.sophia-ai.lambda.cloud/api/unified-chat/chat \
     -H "Content-Type: application/json" \
     -d '{"query": "Show me recent sales data"}'
   ```

3. **WebSocket Connection**:
   ```javascript
   const ws = new WebSocket('wss://api.sophia-ai.lambda.cloud/api/unified-chat/ws');
   ```

### Frontend Routes to Test
1. Main Chat Interface: `https://app.sophia-ai.lambda.cloud/`
2. Direct Chat Route: `https://app.sophia-ai.lambda.cloud/chat`
3. Legacy Dashboard: `https://app.sophia-ai.lambda.cloud/dashboard/ceo` (should redirect to chat)

## 🔍 Monitoring

### Key Metrics to Watch
1. **Response Times**: Should be < 200ms for chat queries
2. **WebSocket Connections**: Monitor active connections
3. **Error Rates**: Should be < 1%
4. **Memory Usage**: Watch for leaks in long-running WebSocket connections

### Grafana Dashboards
- Unified Chat Performance: `https://grafana.sophia-ai.lambda.cloud/d/unified-chat`
- API Gateway Metrics: `https://grafana.sophia-ai.lambda.cloud/d/api-gateway`

## 🚨 Rollback Plan

If issues arise:
```bash
# Rollback to previous version
docker service update --rollback sophia-ai_sophia-backend

# Or redeploy specific version
docker service update sophia-ai_sophia-backend \
  --image scoobyjava15/sophia-ai:previous-tag
```

## 📝 Notes

- The unified chat consolidates 7 previous implementations into one powerful interface
- All data sources (Snowflake, MCP servers, integrations) are accessible through natural language
- WebSocket support provides real-time streaming responses
- The system gracefully falls back to HTTP if WebSocket fails
- All previous dashboard functionality is preserved but simplified 