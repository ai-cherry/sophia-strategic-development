# 🚨 **MCP SERVERS DEPLOYMENT - DETAILED IMPLEMENTATION PLAN**

## 📊 **CURRENT STATUS ANALYSIS**

### **✅ What's Working**
- **Port Allocation:** All ports (9000-9399) are available and conflict-free
- **Infrastructure:** Deployment scripts, health monitoring, and Docker configs exist
- **Configuration:** cursor_enhanced_mcp_config.json properly configured
- **Documentation:** Comprehensive analysis and executive summary complete

### **❌ Critical Issues Discovered**
1. **Dependency Conflicts:** Pinecone package naming conflict (`pinecone-client` vs `pinecone`)
2. **Server Structure:** MCP servers don't have standardized startup mechanisms
3. **Missing Dependencies:** Servers missing required packages (aiohttp for health checks)
4. **Import Errors:** Backend dependencies not available in MCP server context

---

## 🎯 **PHASE 1: IMMEDIATE FIXES (30 minutes)**

### **Step 1.1: Fix Pinecone Dependency Conflict**
```bash
# Current Issue: pinecone-client package conflicts with new pinecone package
# Solution: Update to new pinecone package

cd /Users/lynnmusil/sophia-main
uv remove pinecone-client
uv add pinecone-python-client
```

### **Step 1.2: Add Missing MCP Dependencies**
```bash
# Add required packages for MCP servers
uv add aiohttp fastapi uvicorn
```

### **Step 1.3: Create Minimal Test Server**
Create a simple test server to validate the deployment approach:

```python
# File: mcp-servers/test_server.py
import asyncio
import aiohttp
from aiohttp import web
import json

async def health_check(request):
    return web.json_response({
        "status": "healthy",
        "server": "test_mcp_server",
        "port": request.app.get("port", 9999),
        "timestamp": "2025-06-29T12:00:00Z"
    })

async def create_app(port=9999):
    app = web.Application()
    app["port"] = port
    app.router.add_get("/health", health_check)
    return app

if __name__ == "__main__":
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 9999
    app = create_app(port)
    web.run_app(app, host="localhost", port=port)
```

---

## 🔧 **PHASE 2: SERVER VALIDATION (45 minutes)**

### **Step 2.1: Test Individual Servers**

#### **AI Memory Server (Priority 1)**
```bash
# Navigate to ai_memory
cd mcp-servers/ai_memory

# Fix pinecone import
sed -i '' 's/import pinecone/# import pinecone  # Disabled due to conflict/' ai_memory_mcp_server.py

# Test startup
python ai_memory_mcp_server.py
```

#### **Codacy Server (Priority 2)**
```bash
# Navigate to codacy
cd mcp-servers/codacy

# Test dependencies
python -c "import ast, radon, bandit; print('Dependencies OK')"

# Test startup
python codacy_mcp_server.py
```

### **Step 2.2: Create Server-Specific Startup Scripts**

For each working server, create a startup script:

```bash
# File: mcp-servers/ai_memory/start.sh
#!/bin/bash
export MCP_SERVER_PORT=${1:-9000}
export ENVIRONMENT=prod
export PULUMI_ORG=scoobyjava-org
python ai_memory_mcp_server.py --port $MCP_SERVER_PORT
```

---

## 🚀 **PHASE 3: VALIDATED DEPLOYMENT (30 minutes)**

### **Step 3.1: Deploy Working Servers Only**

Create a conservative deployment script that only starts validated servers:

```bash
# File: mcp-servers/deploy_validated.sh
#!/bin/bash
set -e

echo "🚀 Deploying VALIDATED MCP Servers..."

# Start test server first
echo "🧪 Starting test server..."
python test_server.py 9999 > test_server.log 2>&1 &
echo $! > test_server.pid
sleep 2

# Test health check system
echo "🔍 Testing health check system..."
if python health_check.py | grep -q "test_server"; then
    echo "✅ Health check system working"
else
    echo "❌ Health check system failed"
    exit 1
fi

# Deploy validated servers only
echo "📦 Deploying validated servers..."
# Add working servers here after validation

echo "✅ Validated deployment complete!"
```

### **Step 3.2: Monitor and Validate**

```bash
# Check deployment status
python health_check.py

# Monitor logs
tail -f *.log

# Check resource usage
ps aux | grep python | grep mcp
```

---

## 🔧 **PHASE 4: SHORT-TERM IMPROVEMENTS (2-3 days)**

### **Step 4.1: Server Consolidation**

#### **Merge Duplicate AI Memory Servers**
```bash
# Analysis shows we have:
# - ai_memory/ai_memory_mcp_server.py (787 lines)
# - ai_memory/enhanced_ai_memory_server.py (19,785 lines)
# 
# Action: Merge into single enhanced version
```

#### **Unify Intelligence Servers**
```bash
# Current servers:
# - sophia_ai_intelligence
# - sophia_business_intelligence  
# - sophia_data_intelligence
#
# Action: Create unified sophia_intelligence server
```

### **Step 4.2: Load Testing**

```bash
# File: scripts/load_test_mcp.py
import asyncio
import aiohttp
import time

async def test_server_load(url, concurrent_requests=10):
    """Test server with concurrent requests"""
    start_time = time.time()
    
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in range(concurrent_requests):
            tasks.append(session.get(f"{url}/health"))
        
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
    end_time = time.time()
    
    success_count = sum(1 for r in responses if hasattr(r, 'status') and r.status == 200)
    
    return {
        "total_requests": concurrent_requests,
        "successful_requests": success_count,
        "duration": end_time - start_time,
        "requests_per_second": concurrent_requests / (end_time - start_time)
    }

# Usage:
# python -c "
# import asyncio
# from scripts.load_test_mcp import test_server_load
# result = asyncio.run(test_server_load('http://localhost:9000'))
# print(result)
# "
```

### **Step 4.3: Security Hardening**

```bash
# Network policies for MCP servers
# File: mcp-servers/security/network_policy.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: mcp-servers-policy
spec:
  podSelector:
    matchLabels:
      app: mcp-server
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: sophia-backend
    ports:
    - protocol: TCP
      port: 9000-9399
```

### **Step 4.4: Performance Optimization**

```bash
# Resource monitoring script
# File: scripts/monitor_mcp_resources.py
import psutil
import json
import time

def monitor_mcp_processes():
    """Monitor MCP server resource usage"""
    mcp_processes = []
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'cpu_percent', 'memory_info']):
        try:
            if 'mcp_server.py' in ' '.join(proc.info['cmdline']):
                mcp_processes.append({
                    'pid': proc.info['pid'],
                    'name': proc.info['name'],
                    'cpu_percent': proc.info['cpu_percent'],
                    'memory_mb': proc.info['memory_info'].rss / 1024 / 1024,
                    'cmdline': ' '.join(proc.info['cmdline'])
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    return {
        'timestamp': time.time(),
        'processes': mcp_processes,
        'total_memory_mb': sum(p['memory_mb'] for p in mcp_processes),
        'avg_cpu_percent': sum(p['cpu_percent'] for p in mcp_processes) / len(mcp_processes) if mcp_processes else 0
    }

# Usage: python -c "from scripts.monitor_mcp_resources import monitor_mcp_processes; print(json.dumps(monitor_mcp_processes(), indent=2))"
```

---

## 📊 **SUCCESS METRICS & VALIDATION**

### **Phase 1 Success Criteria**
- [ ] Pinecone dependency conflict resolved
- [ ] Test server starts and responds to health checks
- [ ] Health monitoring system functional

### **Phase 2 Success Criteria**
- [ ] At least 2 MCP servers (ai_memory, codacy) start successfully
- [ ] Health checks return 200 OK for running servers
- [ ] No critical errors in server logs

### **Phase 3 Success Criteria**
- [ ] Validated deployment script works reliably
- [ ] All running servers accessible on assigned ports
- [ ] Resource usage within acceptable limits (<100MB per server)

### **Phase 4 Success Criteria**
- [ ] Load testing shows stable performance under 10 concurrent requests
- [ ] Security policies implemented and tested
- [ ] Performance monitoring shows <10% CPU usage per server

---

## 🚨 **IMMEDIATE NEXT STEPS**

### **Right Now (Next 15 minutes)**
1. **Fix Pinecone dependency:** `uv remove pinecone-client && uv add pinecone-python-client`
2. **Create test server:** Simple HTTP server for validation
3. **Test health check system:** Verify monitoring works

### **Next 30 minutes**
1. **Validate ai_memory server:** Fix imports and test startup
2. **Validate codacy server:** Test dependencies and startup
3. **Create conservative deployment script:** Only deploy working servers

### **Next 2 hours**
1. **Deploy validated servers:** Start working servers only
2. **Monitor performance:** Check resource usage and logs
3. **Document working configuration:** Save successful setup

---

## 💡 **RISK MITIGATION**

### **High-Risk Items**
- **Dependency conflicts:** Use virtual environments and careful package management
- **Port conflicts:** Validate port availability before starting
- **Resource exhaustion:** Monitor memory and CPU usage

### **Fallback Plans**
- **Individual server testing:** Test each server in isolation before group deployment
- **Gradual rollout:** Start with 1-2 servers, add more as validated
- **Quick rollback:** Keep PID files for easy server shutdown

### **Monitoring & Alerts**
- **Health checks:** Run every 30 seconds during deployment
- **Resource monitoring:** Alert if memory usage >500MB total
- **Log monitoring:** Watch for critical errors and startup failures

---

## 🎯 **EXPECTED OUTCOMES**

### **Immediate (Today)**
- **2-3 MCP servers running successfully**
- **Health monitoring system operational**
- **Basic deployment automation working**

### **Short-term (This Week)**
- **5-7 MCP servers operational**
- **Load testing completed and passed**
- **Security hardening implemented**

### **Medium-term (Next 2 weeks)**
- **All 21 servers standardized and operational**
- **Performance optimization completed**
- **Full production deployment ready**

**🚀 Ready to execute Phase 1 immediately!** 