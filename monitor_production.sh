#!/bin/bash
# Monitor Sophia AI production deployment
# This script monitors the health and status of the Sophia AI production deployment

echo "🔍 Monitoring Sophia AI production deployment..."

# Set environment variables
export DEPLOY_ENV="production"
export DEPLOY_TARGET="lambda-labs"
export DEPLOY_REGION="us-west-2"

# Step 1: Set up SSH connection to production server
echo "🔑 Setting up SSH connection to production server..."
SSH_KEY="~/.ssh/lambda_labs_key"
PROD_SERVER="sophia-prod.payready.ai"
PROD_USER="deploy"

# Step 2: Check system status
echo "🔄 Checking system status..."
ssh -i $SSH_KEY $PROD_USER@$PROD_SERVER "cd /opt/sophia && ./run_with_ssl_fix.py unified_command_interface.py 'check system status'"

# Step 3: Check Docker container status
echo "🐳 Checking Docker container status..."
ssh -i $SSH_KEY $PROD_USER@$PROD_SERVER "cd /opt/sophia && docker-compose -f docker-compose.mcp.yml ps"

# Step 4: Check system logs
echo "📜 Checking system logs..."
ssh -i $SSH_KEY $PROD_USER@$PROD_SERVER "cd /opt/sophia && journalctl -u sophia -n 50 --no-pager"

# Step 5: Check resource usage
echo "📊 Checking resource usage..."
ssh -i $SSH_KEY $PROD_USER@$PROD_SERVER "top -b -n 1 | head -n 20"

# Step 6: Check disk usage
echo "💾 Checking disk usage..."
ssh -i $SSH_KEY $PROD_USER@$PROD_SERVER "df -h"

# Step 7: Check memory usage
echo "🧠 Checking memory usage..."
ssh -i $SSH_KEY $PROD_USER@$PROD_SERVER "free -h"

# Step 8: Check network connections
echo "🌐 Checking network connections..."
ssh -i $SSH_KEY $PROD_USER@$PROD_SERVER "netstat -tuln"

# Step 9: Check API endpoints
echo "🔌 Checking API endpoints..."
ssh -i $SSH_KEY $PROD_USER@$PROD_SERVER "curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/api/health"

# Step 10: Check frontend
echo "🖥️ Checking frontend..."
ssh -i $SSH_KEY $PROD_USER@$PROD_SERVER "curl -s -o /dev/null -w '%{http_code}' http://localhost:3000"

echo "✅ Monitoring complete!"
