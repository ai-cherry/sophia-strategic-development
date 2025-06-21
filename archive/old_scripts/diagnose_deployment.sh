#!/bin/bash
# Diagnose Sophia AI deployment issues
# This script analyzes deployment issues and provides detailed diagnostics

echo "🔍 Diagnosing Sophia AI deployment issues..."

# Set environment variables
export DEPLOY_ENV="production"
export DEPLOY_TARGET="lambda-labs"
export DEPLOY_REGION="us-west-2"

# Step 1: Set up SSH connection to production server
echo "🔑 Setting up SSH connection to production server..."
SSH_KEY="~/.ssh/lambda_labs_key"
PROD_SERVER="sophia-prod.payready.ai"
PROD_USER="deploy"

# Check if we can connect to the server
echo "🔌 Checking SSH connection..."
if ssh -i $SSH_KEY -o ConnectTimeout=5 $PROD_USER@$PROD_SERVER "echo 'Connection successful'"; then
  echo "✅ SSH connection successful"
else
  echo "❌ SSH connection failed. Please check:"
  echo "  - SSH key exists at $SSH_KEY"
  echo "  - Server $PROD_SERVER is reachable"
  echo "  - User $PROD_USER has access to the server"
  echo "  - Firewall allows SSH connections"
  exit 1
fi

# Step 2: Check if the repository exists
echo "📁 Checking repository..."
if ssh -i $SSH_KEY $PROD_USER@$PROD_SERVER "test -d /opt/sophia && echo 'Repository exists'"; then
  echo "✅ Repository exists"
else
  echo "❌ Repository not found at /opt/sophia. Please run setup_production_server.sh first."
  exit 1
fi

# Step 3: Check environment variables
echo "🔧 Checking environment variables..."
ssh -i $SSH_KEY $PROD_USER@$PROD_SERVER "cd /opt/sophia && grep -q 'ANTHROPIC_API_KEY' .env && echo '✅ ANTHROPIC_API_KEY found' || echo '❌ ANTHROPIC_API_KEY missing'"
ssh -i $SSH_KEY $PROD_USER@$PROD_SERVER "cd /opt/sophia && grep -q 'PULUMI_ACCESS_TOKEN' .env && echo '✅ PULUMI_ACCESS_TOKEN found' || echo '❌ PULUMI_ACCESS_TOKEN missing'"
ssh -i $SSH_KEY $PROD_USER@$PROD_SERVER "cd /opt/sophia && grep -q 'SLACK_BOT_TOKEN' .env && echo '✅ SLACK_BOT_TOKEN found' || echo '❌ SLACK_BOT_TOKEN missing'"
ssh -i $SSH_KEY $PROD_USER@$PROD_SERVER "cd /opt/sophia && grep -q 'SLACK_APP_TOKEN' .env && echo '✅ SLACK_APP_TOKEN found' || echo '❌ SLACK_APP_TOKEN missing'"
ssh -i $SSH_KEY $PROD_USER@$PROD_SERVER "cd /opt/sophia && grep -q 'SLACK_SIGNING_SECRET' .env && echo '✅ SLACK_SIGNING_SECRET found' || echo '❌ SLACK_SIGNING_SECRET missing'"
ssh -i $SSH_KEY $PROD_USER@$PROD_SERVER "cd /opt/sophia && grep -q 'LINEAR_API_TOKEN' .env && echo '✅ LINEAR_API_TOKEN found' || echo '❌ LINEAR_API_TOKEN missing'"

# Step 4: Check Docker and Docker Compose
echo "🐳 Checking Docker and Docker Compose..."
ssh -i $SSH_KEY $PROD_USER@$PROD_SERVER "docker --version && echo '✅ Docker installed' || echo '❌ Docker not installed'"
ssh -i $SSH_KEY $PROD_USER@$PROD_SERVER "docker-compose --version && echo '✅ Docker Compose installed' || echo '❌ Docker Compose not installed'"
ssh -i $SSH_KEY $PROD_USER@$PROD_SERVER "docker ps && echo '✅ Docker daemon running' || echo '❌ Docker daemon not running'"

# Step 5: Check Docker Compose configuration
echo "📄 Checking Docker Compose configuration..."
ssh -i $SSH_KEY $PROD_USER@$PROD_SERVER "cd /opt/sophia && docker-compose -f docker-compose.mcp.yml config && echo '✅ Docker Compose configuration valid' || echo '❌ Docker Compose configuration invalid'"

# Step 6: Check if containers are running
echo "🔄 Checking if containers are running..."
ssh -i $SSH_KEY $PROD_USER@$PROD_SERVER "cd /opt/sophia && docker-compose -f docker-compose.mcp.yml ps"

# Step 7: Check container logs
echo "📜 Checking container logs..."
ssh -i $SSH_KEY $PROD_USER@$PROD_SERVER "cd /opt/sophia && docker-compose -f docker-compose.mcp.yml logs --tail=50"

# Step 8: Check Nginx configuration
echo "🌐 Checking Nginx configuration..."
ssh -i $SSH_KEY $PROD_USER@$PROD_SERVER "sudo nginx -t && echo '✅ Nginx configuration valid' || echo '❌ Nginx configuration invalid'"
ssh -i $SSH_KEY $PROD_USER@$PROD_SERVER "systemctl status nginx && echo '✅ Nginx running' || echo '❌ Nginx not running'"

# Step 9: Check SSL certificates
echo "🔒 Checking SSL certificates..."
ssh -i $SSH_KEY $PROD_USER@$PROD_SERVER "test -f /etc/ssl/sophia/sophia.crt && echo '✅ SSL certificate exists' || echo '❌ SSL certificate missing'"
ssh -i $SSH_KEY $PROD_USER@$PROD_SERVER "test -f /etc/ssl/sophia/sophia.key && echo '✅ SSL key exists' || echo '❌ SSL key missing'"

# Step 10: Check systemd service
echo "⚙️ Checking systemd service..."
ssh -i $SSH_KEY $PROD_USER@$PROD_SERVER "systemctl status sophia && echo '✅ Sophia service running' || echo '❌ Sophia service not running'"

# Step 11: Check network connectivity
echo "🌐 Checking network connectivity..."
ssh -i $SSH_KEY $PROD_USER@$PROD_SERVER "curl -s -o /dev/null -w '%{http_code}' http://localhost:3000 && echo '✅ Frontend reachable' || echo '❌ Frontend not reachable'"
ssh -i $SSH_KEY $PROD_USER@$PROD_SERVER "curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/api/health && echo '✅ API reachable' || echo '❌ API not reachable'"

# Step 12: Check DNS resolution
echo "🔍 Checking DNS resolution..."
ssh -i $SSH_KEY $PROD_USER@$PROD_SERVER "nslookup sophia.payready.ai && echo '✅ DNS resolves' || echo '❌ DNS does not resolve'"

# Step 13: Check firewall
echo "🔥 Checking firewall..."
ssh -i $SSH_KEY $PROD_USER@$PROD_SERVER "sudo ufw status && echo '✅ Firewall configured' || echo '❌ Firewall not configured'"

# Step 14: Check disk space
echo "💾 Checking disk space..."
ssh -i $SSH_KEY $PROD_USER@$PROD_SERVER "df -h | grep -E '(Filesystem|/$)'"

# Step 15: Check memory
echo "🧠 Checking memory..."
ssh -i $SSH_KEY $PROD_USER@$PROD_SERVER "free -h | head -2"

# Step 16: Check CPU usage
echo "💻 Checking CPU usage..."
ssh -i $SSH_KEY $PROD_USER@$PROD_SERVER "top -bn1 | head -3"

# Step 17: Check Python version
echo "🐍 Checking Python version..."
ssh -i $SSH_KEY $PROD_USER@$PROD_SERVER "python3 --version && echo '✅ Python installed' || echo '❌ Python not installed'"

# Step 18: Check Python packages
echo "📦 Checking Python packages..."
ssh -i $SSH_KEY $PROD_USER@$PROD_SERVER "cd /opt/sophia && pip list | grep -E '(pydantic|mcp)'"

# Step 19: Check automated health check
echo "🩺 Running automated health check..."
ssh -i $SSH_KEY $PROD_USER@$PROD_SERVER "cd /opt/sophia && ./run_with_ssl_fix.py automated_health_check.py || echo '❌ Automated health check failed'"

# Step 20: Generate comprehensive report
echo "📊 Generating comprehensive report..."
ssh -i $SSH_KEY $PROD_USER@$PROD_SERVER "cd /opt/sophia && ./run_with_ssl_fix.py unified_command_interface.py 'generate deployment report' || echo '❌ Report generation failed'"

echo "✅ Diagnosis complete!"
echo "Please review the output above to identify and fix deployment issues."
