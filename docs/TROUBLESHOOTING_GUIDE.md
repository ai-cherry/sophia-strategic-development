# Sophia AI - Troubleshooting Guide

## 🚨 **Common Issues and Solutions**

## 🔐 **PERMANENT SECRET MANAGEMENT SOLUTION**

**IMPORTANT**: Sophia AI now uses a **PERMANENT GitHub Organization Secrets → Pulumi ESC** solution. Most secret-related issues are now automatically resolved.

### **✅ What's Automated (No More Manual Fixes)**
- ❌ No more `.env` file management
- ❌ No more manual secret configuration
- ❌ No more environment variable setup
- ❌ No more API key sharing/copying
- ✅ All secrets managed in [GitHub ai-cherry organization](https://github.com/ai-cherry)
- ✅ Automatic synchronization to Pulumi ESC
- ✅ Backend automatically loads all secrets

### **🔧 New Secret Management Troubleshooting**

#### **Problem:** "Secret not found" or "API key invalid"
**Root Cause:** Secret not set in GitHub organization or sync failed

**Solutions:**
1. **Check GitHub Organization Secrets**:
   - Go to [GitHub ai-cherry organization secrets](https://github.com/ai-cherry/settings/secrets/actions)
   - Verify the required secret exists and has correct value

2. **Verify Pulumi ESC Access**:
   ```bash
   export PULUMI_ORG=scoobyjava-org
   pulumi whoami
   pulumi env ls
   ```

3. **Test ESC Environment**:
   ```bash
   pulumi env open scoobyjava-org/default/sophia-ai-production
   ```

4. **Check Backend Auto-Loading**:
   ```python
   from backend.core.auto_esc_config import config
   print(config.openai_api_key)  # Should not be None
   ```

5. **Re-run Sync Process**:
   ```bash
   python scripts/sync_github_to_pulumi.sh
   ```

#### **Problem:** "Pulumi ESC access denied"
**Root Cause:** Invalid or expired `PULUMI_ACCESS_TOKEN`

**Solutions:**
1. **Update GitHub Organization Secret**:
   - Update `PULUMI_ACCESS_TOKEN` in [GitHub organization secrets](https://github.com/ai-cherry/settings/secrets/actions)
   - Use your current Pulumi access token

2. **Test Local Access**:
   ```bash
   export PULUMI_ORG=scoobyjava-org
   pulumi whoami
   ```

#### **Problem:** Backend fails to start with credential errors
**Root Cause:** ESC integration not working

**Solutions:**
1. **Run Permanent Solution Test**:
   ```bash
   python scripts/test_permanent_solution.py
   ```

2. **Check ESC Configuration**:
   ```bash
   export PULUMI_ORG=scoobyjava-org
   python -c "from backend.core.auto_esc_config import config; print('Config loaded successfully' if config else 'Config failed')"
   ```

3. **Verify GitHub Actions Workflow**:
   - Check latest workflow run at [GitHub Actions](https://github.com/ai-cherry/sophia-main/actions)
   - Look for sync workflow failures

---

### **1. MCP Server Connection Issues**

#### **Problem:** MCP servers not responding or timing out
**Symptoms:**
- Natural language commands fail with timeout errors
- Health checks show services as unhealthy
- Cursor IDE commands don't execute

**Solutions:**
```bash
# Check MCP server status
docker-compose -f docker-compose.mcp.yml ps

# Restart all MCP servers (they will auto-load secrets)
docker-compose -f docker-compose.mcp.yml restart

# Check individual server logs
docker-compose -f docker-compose.mcp.yml logs claude

# Test MCP server directly
curl http://localhost:8000/claude/health
```

#### **Problem:** MCP configuration not loading
**Symptoms:**
- Cursor IDE doesn't recognize MCP servers
- Commands route to wrong services

**Solutions:**
```bash
# Validate MCP configuration
python -c "import json; print(json.load(open('mcp_config.json')))"

# Restart Cursor IDE with fresh configuration
# Close Cursor IDE completely and reopen

# Check automatic secret loading (NEW)
export PULUMI_ORG=scoobyjava-org
python -c "from backend.core.auto_esc_config import config; print('Secrets loaded:', bool(config.openai_api_key))"
```

---

### **2. Backend Service Issues**

#### **Problem:** Backend fails to start
**Symptoms:**
- Import errors or missing dependencies
- Configuration errors
- Database connection failures

**Solutions:**
```bash
# Test backend with automatic secret loading
export PULUMI_ORG=scoobyjava-org
python backend/main.py

# Check health endpoint
curl http://localhost:8000/health

# Verify all integrations
python -c "
from backend.core.auto_esc_config import config
print('OpenAI:', bool(config.openai_api_key))
print('Gong:', bool(config.gong_access_key))
print('Slack:', bool(config.slack_bot_token))
print('Snowflake:', bool(config.snowflake_password))
"
```

#### **Problem:** API integration failures
**Symptoms:**
- External API calls fail
- Authentication errors with third-party services
- Rate limiting issues

**Solutions:**
```bash
# Test specific service integration
python -c "
from backend.integrations.gong.gong_integration import GongIntegration
from backend.core.auto_esc_config import config
gong = GongIntegration(config)
print('Gong integration test:', gong.test_connection())
"

# Check service-specific health
python -c "
import asyncio
from backend.core.config_manager import health_check
services = ['gong', 'hubspot', 'slack', 'snowflake']
for service in services:
    result = asyncio.run(health_check(service))
    print(f'{service}: {result}')
"
```

---

### **3. Frontend Issues**

#### **Problem:** Frontend won't start or build
**Symptoms:**
- npm/yarn errors
- Build failures
- Missing dependencies

**Solutions:**
```bash
# Clean install
cd frontend
rm -rf node_modules package-lock.json
npm install

# Start development server
npm run dev

# Check for build issues
npm run build
```

#### **Problem:** API connection issues
**Symptoms:**
- Frontend can't connect to backend
- CORS errors
- Network timeouts

**Solutions:**
```bash
# Verify backend is running
curl http://localhost:8000/health

# Check CORS configuration
curl -H "Origin: http://localhost:5173" \
     -H "Access-Control-Request-Method: GET" \
     -H "Access-Control-Request-Headers: X-Requested-With" \
     -X OPTIONS \
     http://localhost:8000/api/v1/health
```

---

### **4. Docker and Container Issues**

#### **Problem:** Docker containers won't start
**Symptoms:**
- Container exit codes
- Port binding errors
- Volume mounting issues

**Solutions:**
```bash
# Check container status
docker-compose ps

# View container logs
docker-compose logs [service-name]

# Restart specific service
docker-compose restart [service-name]

# Clean rebuild
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

#### **Problem:** MCP Docker containers failing
**Symptoms:**
- MCP servers not accessible
- Container startup failures
- Network connectivity issues

**Solutions:**
```bash
# Check MCP container logs
docker-compose -f docker-compose.mcp.yml logs

# Restart MCP services (auto-loads secrets)
docker-compose -f docker-compose.mcp.yml restart

# Test MCP connectivity
curl http://localhost:8000/health
```

---

### **5. Development Environment Issues**

#### **Problem:** Python environment issues
**Symptoms:**
- Import errors
- Version conflicts
- Missing packages

**Solutions:**
```bash
# Create fresh virtual environment
python -m venv sophia_venv
source sophia_venv/bin/activate  # On Windows: sophia_venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "import backend.main; print('Backend imports successful')"
```

#### **Problem:** Database connection issues
**Symptoms:**
- Connection timeouts
- Authentication failures
- Schema errors

**Solutions:**
```bash
# Test database connection with auto-loaded credentials
python -c "
from backend.core.auto_esc_config import config
print('Database config loaded:', bool(config.postgres_password))
"

# Check database health
python -c "
import asyncio
from backend.core.config_manager import health_check
result = asyncio.run(health_check('postgres'))
print('Database health:', result)
"
```

---

### **6. Performance Issues**

#### **Problem:** Slow API responses
**Symptoms:**
- High latency
- Timeout errors
- Poor user experience

**Solutions:**
```bash
# Check system resources
htop
df -h

# Monitor API performance
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8000/health

# Check database performance
python -c "
import asyncio
from backend.monitoring.enhanced_metrics import get_performance_metrics
metrics = asyncio.run(get_performance_metrics())
print('Performance metrics:', metrics)
"
```

#### **Problem:** Memory or CPU issues
**Symptoms:**
- High resource usage
- System slowdowns
- Out of memory errors

**Solutions:**
```bash
# Monitor resource usage
docker stats

# Check for memory leaks
python -c "
import psutil
import os
process = psutil.Process(os.getpid())
print('Memory usage:', process.memory_info().rss / 1024 / 1024, 'MB')
"

# Optimize configuration
python -c "
from backend.core.config_manager import optimize_performance
optimize_performance()
"
```

---

### **7. Deployment Issues**

#### **Problem:** GitHub Actions workflow failures
**Symptoms:**
- Deployment failures
- Secret access issues
- Build errors

**Solutions:**
```bash
# Check workflow status
# Go to: https://github.com/ai-cherry/sophia-main/actions

# Verify organization secrets are set
# Go to: https://github.com/ai-cherry/settings/secrets/actions

# Test deployment locally
python scripts/test_permanent_solution.py
```

#### **Problem:** Pulumi infrastructure issues
**Symptoms:**
- Infrastructure deployment failures
- Resource conflicts
- State inconsistencies

**Solutions:**
```bash
# Check Pulumi status
export PULUMI_ORG=scoobyjava-org
pulumi stack ls
pulumi preview

# Refresh state
pulumi refresh

# Check ESC environments
pulumi env ls
```

---

### **8. Monitoring and Logging**

#### **Problem:** Missing logs or metrics
**Symptoms:**
- No log output
- Missing performance data
- Monitoring gaps

**Solutions:**
```bash
# Check log configuration
python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.info('Logging test successful')
"

# View application logs
tail -f logs/sophia.log

# Check monitoring metrics
curl http://localhost:8000/metrics
```

---

### **9. Security Issues**

#### **Problem:** Authentication failures
**Symptoms:**
- Login errors
- Token validation failures
- Permission denied errors

**Solutions:**
```bash
# Test JWT token generation
python -c "
from backend.core.auto_esc_config import config
print('JWT secret loaded:', bool(config.jwt_secret))
"

# Verify authentication configuration
python -c "
from backend.security.enhanced_security import SecurityManager
security = SecurityManager()
print('Security configured:', security.is_configured())
"
```

---

### **10. Quick Diagnostic Commands**

#### **System Health Check**
```bash
# Run comprehensive health check
python scripts/test_permanent_solution.py

# Check all service health
python -c "
import asyncio
from backend.core.config_manager import health_check, list_services
services = asyncio.run(list_services())
for service in services:
    health = asyncio.run(health_check(service))
    print(f'{service}: {health}')
"
```

#### **Configuration Validation**
```bash
# Validate all configurations
python -c "
from backend.core.auto_esc_config import config
print('Configuration loaded successfully:', bool(config))
print('OpenAI configured:', bool(config.openai_api_key))
print('Gong configured:', bool(config.gong_access_key))
print('Slack configured:', bool(config.slack_bot_token))
"
```

#### **Secret Management Status**
```bash
# Check GitHub organization secrets sync status
python scripts/sync_github_to_pulumi.sh --dry-run

# Verify ESC environment access
export PULUMI_ORG=scoobyjava-org
pulumi env open scoobyjava-org/default/sophia-ai-production
```

---

## 🆘 **Emergency Recovery**

### **Complete System Reset**
```bash
# 1. Reset Pulumi ESC access
export PULUMI_ORG=scoobyjava-org
pulumi logout
pulumi login

# 2. Re-run permanent solution setup
python scripts/setup_permanent_secrets_solution.py

# 3. Test the solution
python scripts/test_permanent_solution.py

# 4. Restart all services
docker-compose down
docker-compose -f docker-compose.mcp.yml down
docker-compose up -d
docker-compose -f docker-compose.mcp.yml up -d
```

### **Contact Support**
If issues persist after trying these solutions:

1. **Check GitHub Issues**: [Sophia AI Issues](https://github.com/ai-cherry/sophia-main/issues)
2. **Review Documentation**: `PERMANENT_GITHUB_ORG_SECRETS_SOLUTION.md`
3. **Run Diagnostics**: `python scripts/test_permanent_solution.py`
4. **Collect Logs**: Include output from diagnostic commands

---

## 🎯 **Success Indicators**

When everything is working correctly:
- ✅ `python scripts/test_permanent_solution.py` passes all tests
- ✅ Backend starts without credential errors
- ✅ All MCP servers respond to health checks
- ✅ Frontend connects to backend successfully
- ✅ All API integrations work
- ✅ No manual secret management required

**🔒 PERMANENT SOLUTION GUARANTEE: Once properly configured, the system manages all secrets automatically with zero manual intervention required.**
