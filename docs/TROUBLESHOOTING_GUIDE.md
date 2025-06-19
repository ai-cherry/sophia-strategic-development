# Sophia AI - Troubleshooting Guide

## 🚨 **Common Issues and Solutions**

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

# Restart all MCP servers
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

# Check environment variables
echo $ANTHROPIC_API_KEY
echo $LINEAR_API_TOKEN
```

---

### **2. Pulumi ESC Secret Management Issues**

#### **Problem:** Secrets not found or access denied
**Symptoms:**
- "Secret not found" errors
- Authentication failures for services
- Empty configuration values

**Solutions:**
```bash
# Check Pulumi ESC connection
pulumi whoami
pulumi stack ls

# Test secret retrieval
python infrastructure/esc/get_secret.py --secret-name snowflake_password

# Validate ESC environment
pulumi config get --stack production

# Re-sync secrets from GitHub
python infrastructure/esc/github_sync_bidirectional.py --direction github-to-pulumi
```

#### **Problem:** Secret rotation failures
**Symptoms:**
- Rotation scripts fail with permission errors
- Services lose access after rotation
- GitHub Actions workflows fail

**Solutions:**
```bash
# Check rotation status
python infrastructure/esc/check_rotation_status.py

# Manual secret rotation
python infrastructure/esc/secret_rotation_framework.py --service gong --dry-run

# Validate GitHub secrets
gh secret list --org ai-cherry

# Re-run failed rotation
python infrastructure/esc/secret_rotation_framework.py --service gong --force
```

---

### **3. Claude Integration Issues**

#### **Problem:** Claude API calls failing
**Symptoms:**
- Code generation requests timeout
- "Invalid API key" errors
- Rate limit exceeded messages

**Solutions:**
```bash
# Test Claude API key
export ANTHROPIC_API_KEY="your-key"
python test_claude_as_code.py

# Check API usage
curl -H "Authorization: Bearer $ANTHROPIC_API_KEY" \
     https://api.anthropic.com/v1/messages

# Reset Claude integration
python start_claude_as_code.py --reset

# Check rate limits
python -c "
from backend.integrations.claude_integration import claude_integration
import asyncio
asyncio.run(claude_integration.get_usage_stats())
"
```

#### **Problem:** Code generation produces poor results
**Symptoms:**
- Generated code has syntax errors
- Code doesn't match requirements
- Inconsistent code style

**Solutions:**
```bash
# Update Claude prompts in .cursorrules
# Add more specific context to requests
# Use explicit programming language and framework specifications

# Example improved prompt:
"Generate a Python FastAPI endpoint using async/await, 
with proper error handling, type hints, and Pydantic models"
```

---

### **4. Infrastructure Deployment Issues**

#### **Problem:** Deployment failures
**Symptoms:**
- GitHub Actions workflows fail
- Pulumi stack updates fail
- Services become unavailable

**Solutions:**
```bash
# Check GitHub Actions status
gh run list --repo ai-cherry/sophia-main

# View failed workflow logs
gh run view [run-id] --log

# Manual deployment
cd infrastructure
pulumi up --stack production --yes

# Rollback if needed
pulumi stack history
pulumi cancel  # if stuck
```

#### **Problem:** Service health check failures
**Symptoms:**
- Health endpoints return 500 errors
- Services show as unhealthy in monitoring
- Intermittent connection issues

**Solutions:**
```bash
# Check service logs
docker-compose logs [service-name]

# Test individual services
curl http://localhost:8000/snowflake/health
curl http://localhost:8000/gong/health

# Restart unhealthy services
docker-compose restart [service-name]

# Check resource usage
docker stats
```

---

### **5. Natural Language Command Issues**

#### **Problem:** Commands not recognized
**Symptoms:**
- Cursor IDE doesn't understand commands
- Commands execute wrong actions
- No response to natural language input

**Solutions:**
```bash
# Check .cursorrules configuration
cat .cursorrules | grep -A 5 -B 5 "your-command-pattern"

# Update command patterns in .cursorrules
# Add more specific examples and context

# Restart Cursor IDE to reload configuration
# Test with simpler, more explicit commands
```

#### **Problem:** Command execution failures
**Symptoms:**
- Commands are recognized but fail to execute
- Partial execution with errors
- Timeout during execution

**Solutions:**
```bash
# Check MCP server logs
docker-compose -f docker-compose.mcp.yml logs

# Test command routing
python -c "
from backend.mcp.sophia_mcp_server import sophia_mcp_server
# Test specific command routing
"

# Validate service configurations
python backend/core/config_manager.py --validate-all
```

---

### **6. Performance Issues**

#### **Problem:** Slow response times
**Symptoms:**
- Commands take longer than 30 seconds
- API calls timeout
- UI becomes unresponsive

**Solutions:**
```bash
# Check system resources
htop
df -h
free -m

# Optimize Docker containers
docker system prune -f
docker-compose -f docker-compose.mcp.yml restart

# Check database performance
python -c "
from backend.core.config_manager import config_manager
import asyncio
asyncio.run(config_manager.test_connection('snowflake'))
"

# Enable caching
# Update cache TTL in config_manager.py
```

---

### **7. Security Issues**

#### **Problem:** Authentication failures
**Symptoms:**
- "Unauthorized" errors
- Token expiration issues
- Permission denied errors

**Solutions:**
```bash
# Refresh OAuth tokens
python gong_oauth_application.py --refresh-tokens

# Check token expiration
python -c "
import os
from datetime import datetime
# Check token metadata in Pulumi ESC
"

# Rotate compromised secrets
python infrastructure/esc/secret_rotation_framework.py --emergency-rotation

# Audit access logs
grep "401\|403" /var/log/sophia/*.log
```

---

## 🔧 **Diagnostic Commands**

### **System Health Check**
```bash
#!/bin/bash
# Complete system health check

echo "=== Sophia AI System Health Check ==="

# Check Docker services
echo "Docker Services:"
docker-compose -f docker-compose.mcp.yml ps

# Check Pulumi ESC
echo "Pulumi ESC Status:"
pulumi whoami
pulumi stack ls

# Check API endpoints
echo "API Health Checks:"
curl -s http://localhost:8000/health | jq .

# Check secret access
echo "Secret Access Test:"
python infrastructure/esc/get_secret.py --secret-name test_secret --dry-run

# Check Claude integration
echo "Claude Integration:"
python test_claude_as_code.py --quick-test

echo "=== Health Check Complete ==="
```

### **Performance Monitoring**
```bash
#!/bin/bash
# Performance monitoring script

echo "=== Performance Monitoring ==="

# System resources
echo "System Resources:"
echo "CPU: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)%"
echo "Memory: $(free | grep Mem | awk '{printf "%.1f%%", $3/$2 * 100.0}')"
echo "Disk: $(df -h / | awk 'NR==2{printf "%s", $5}')"

# Docker stats
echo "Docker Container Stats:"
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"

# API response times
echo "API Response Times:"
time curl -s http://localhost:8000/health > /dev/null

echo "=== Monitoring Complete ==="
```

---

## 📞 **Getting Help**

### **Log Collection**
```bash
# Collect all relevant logs
mkdir -p /tmp/sophia-logs
docker-compose -f docker-compose.mcp.yml logs > /tmp/sophia-logs/mcp-services.log
cp /var/log/sophia/*.log /tmp/sophia-logs/
tar -czf sophia-debug-$(date +%Y%m%d-%H%M%S).tar.gz /tmp/sophia-logs/
```

### **Configuration Backup**
```bash
# Backup current configuration
mkdir -p /tmp/sophia-config
cp mcp_config.json /tmp/sophia-config/
cp .cursorrules /tmp/sophia-config/
cp infrastructure/Pulumi.yaml /tmp/sophia-config/
tar -czf sophia-config-backup-$(date +%Y%m%d-%H%M%S).tar.gz /tmp/sophia-config/
```

### **Support Channels**
- **GitHub Issues**: https://github.com/ai-cherry/sophia-main/issues
- **Documentation**: https://docs.sophia.ai
- **Community**: https://discord.gg/sophia-ai
- **Email**: support@sophia.ai

### **Emergency Procedures**
```bash
# Emergency shutdown
docker-compose -f docker-compose.mcp.yml down

# Emergency rollback
cd infrastructure
pulumi stack history
pulumi refresh --stack production
# Select previous working state

# Emergency secret rotation
python infrastructure/esc/secret_rotation_framework.py --emergency-rotation --all-services
```

