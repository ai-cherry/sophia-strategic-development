# Sophia AI: Focused Deployment Plan

## 🎯 Executive Summary

After reviewing the comprehensive deployment analysis, this plan extracts only the **high-value, practical improvements** that will deliver immediate impact without adding unnecessary complexity.

## 🚀 Priority Improvements (What We'll Actually Do)

### 1. **Domain & Environment Alignment** ✅
**Value**: Critical for deployment success
**Implementation**: Simple configuration updates

### 2. **Essential MCP Server Deployment** ✅
**Value**: Core AI functionality
**Implementation**: Deploy only the 5 most-used MCP servers

### 3. **API Health Monitoring** ✅
**Value**: Operational visibility
**Implementation**: Simple health endpoints

### 4. **Frontend Build Fix** ✅
**Value**: Proper Vercel deployment
**Implementation**: Correct build configuration

## ❌ What We're NOT Doing (Avoiding Complexity)

1. **Global Find/Replace Operations** - Too risky, may break working code
2. **20+ MCP Server Deployment** - Start with 5 essential ones
3. **Complex Docker Orchestration** - Use simple deployment first
4. **Extensive Domain Cleanup** - Fix only critical paths
5. **Multi-Phase Deployment Scripts** - Keep it simple

## 📋 Simplified Action Plan

### **Phase 1: Frontend Configuration (15 minutes)**

#### 1.1 Create Production Environment File
```bash
cd frontend
cat > .env.production << 'EOF'
VITE_API_URL=https://api.sophia-intel.ai
VITE_WS_URL=wss://api.sophia-intel.ai
VITE_ENVIRONMENT=production
EOF
```

#### 1.2 Fix Vercel Configuration
```json
// vercel.json (root level)
{
  "version": 2,
  "builds": [
    {
      "src": "frontend/package.json",
      "use": "@vercel/static-build",
      "config": {
        "buildCommand": "cd frontend && npm install && npm run build",
        "outputDirectory": "frontend/dist"
      }
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "https://api.sophia-intel.ai/$1"
    },
    {
      "src": "/(.*)",
      "dest": "/frontend/dist/$1"
    }
  ]
}
```

### **Phase 2: Backend API Deployment (30 minutes)**

#### 2.1 Simple FastAPI Deployment
```python
# backend/main.py - Ensure this exists and works
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Sophia AI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://app.sophia-intel.ai"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "sophia-ai-api"}

@app.get("/api/v1/dashboard/main")
async def dashboard_main():
    return {
        "metrics": {
            "total_users": 1,
            "active_sessions": 1,
            "api_calls_today": 100
        }
    }
```

#### 2.2 Deploy to Lambda Labs
```bash
# Simple deployment script
ssh ubuntu@192.222.58.232 << 'EOF'
cd /opt/sophia-ai
git pull
docker-compose -f docker-compose.api.yml up -d --build
EOF
```

### **Phase 3: Essential MCP Servers (30 minutes)**

#### 3.1 Deploy Only Core MCP Servers
Focus on these 5 essential servers:
1. **AI Memory** (Port 9001) - For context retention
2. **Snowflake** (Port 9002) - For data queries
3. **Unified Intelligence** (Port 9005) - For AI orchestration
4. **Slack** (Port 9103) - For notifications
5. **GitHub** (Port 9104) - For code integration

#### 3.2 Simple Docker Compose
```yaml
# docker-compose.mcp-essential.yml
version: '3.8'
services:
  ai-memory:
    build: ./mcp-servers/ai-memory
    ports:
      - "9001:9001"
    restart: unless-stopped

  snowflake:
    build: ./mcp-servers/snowflake_unified
    ports:
      - "9002:9002"
    restart: unless-stopped

  # ... other 3 essential servers
```

### **Phase 4: Verification (15 minutes)**

#### 4.1 Simple Health Check Script
```bash
#!/bin/bash
# health_check.sh

echo "🏥 Sophia AI Health Check"
echo "========================"

# Check Frontend
curl -s -o /dev/null -w "Frontend: %{http_code}\n" https://app.sophia-intel.ai

# Check API
curl -s https://api.sophia-intel.ai/health | jq '.' || echo "API: Failed"

# Check Essential MCP Servers
for port in 9001 9002 9005 9103 9104; do
  curl -s localhost:$port/health | jq '.status' || echo "MCP $port: Failed"
done
```

## 📊 Success Metrics

### Minimum Viable Deployment:
- ✅ Frontend loads without errors
- ✅ API health endpoint responds
- ✅ Dashboard shows basic data
- ✅ 5 essential MCP servers running
- ✅ No critical errors in logs

### What We're NOT Measuring Yet:
- ❌ Performance metrics
- ❌ Complex monitoring
- ❌ All 20+ MCP servers
- ❌ Full feature parity

## 🔧 Troubleshooting Guide

### Common Issues & Quick Fixes:

1. **Frontend shows blank page**
   - Check browser console for API errors
   - Verify .env.production is loaded
   - Check Vercel deployment logs

2. **API returns 404**
   - Verify backend is running on Lambda Labs
   - Check nginx proxy configuration
   - Ensure /api routes are proxied correctly

3. **MCP servers fail health checks**
   - Check Docker logs: `docker logs mcp-ai-memory`
   - Verify ports aren't already in use
   - Ensure Pulumi ESC secrets are accessible

## 🎯 Next Steps (After Basic Deployment Works)

1. **Add remaining MCP servers** gradually (not all at once)
2. **Implement basic monitoring** (just health checks)
3. **Add error tracking** (Sentry or similar)
4. **Optimize performance** (only if needed)

## 💡 Key Principles

1. **Start Simple** - Get basic functionality working first
2. **Incremental Improvements** - Add features one at a time
3. **Avoid Complexity** - Don't over-engineer the solution
4. **Focus on Value** - Only implement what provides immediate benefit
5. **Monitor Success** - Ensure each step works before proceeding

## 📝 Implementation Checklist

- [ ] Frontend environment configuration
- [ ] Vercel build configuration fix
- [ ] Backend API basic endpoints
- [ ] Deploy to Lambda Labs
- [ ] 5 essential MCP servers only
- [ ] Basic health monitoring
- [ ] Verify core functionality

## ⏱️ Realistic Timeline

- **Phase 1**: 15 minutes (Frontend config)
- **Phase 2**: 30 minutes (Backend deployment)
- **Phase 3**: 30 minutes (Essential MCP servers)
- **Phase 4**: 15 minutes (Verification)

**Total**: ~90 minutes for basic working deployment

## 🚨 What NOT to Do

1. **Don't** try to deploy all 20+ MCP servers at once
2. **Don't** do global find/replace operations
3. **Don't** create complex orchestration systems
4. **Don't** worry about performance optimization yet
5. **Don't** implement extensive monitoring initially

## 📞 Support Strategy

If deployment fails:
1. Check the specific error message
2. Fix only that specific issue
3. Don't try to fix everything at once
4. Use simple solutions first

---

**Remember**: The goal is a working deployment, not a perfect one. We can iterate and improve once the basics are functional.
