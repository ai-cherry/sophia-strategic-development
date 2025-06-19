#!/bin/bash
# Deploy Sophia AI to production
# This script deploys the Sophia AI system to production servers

echo "🚀 Deploying Sophia AI to production..."

# Set environment variables
export DEPLOY_ENV="production"
export DEPLOY_TARGET="lambda-labs"
export DEPLOY_REGION="us-west-2"

# Step 1: Set up SSH connection to production server
echo "🔑 Setting up SSH connection to production server..."
SSH_KEY="~/.ssh/lambda_labs_key"
PROD_SERVER="sophia-prod.payready.ai"
PROD_USER="deploy"

# Step 2: Pull latest changes on production server
echo "📥 Pulling latest changes on production server..."
ssh -i $SSH_KEY $PROD_USER@$PROD_SERVER "cd /opt/sophia && git pull origin main"

# Step 3: Run the setup script on production server
echo "🔧 Running setup on production server..."
ssh -i $SSH_KEY $PROD_USER@$PROD_SERVER "cd /opt/sophia && make"

# Step 4: Restart services
echo "🔄 Restarting services..."
ssh -i $SSH_KEY $PROD_USER@$PROD_SERVER "cd /opt/sophia && docker-compose -f docker-compose.mcp.yml down && docker-compose -f docker-compose.mcp.yml up -d"

# Step 5: Run health check
echo "🩺 Running health check..."
ssh -i $SSH_KEY $PROD_USER@$PROD_SERVER "cd /opt/sophia && ./run_with_ssl_fix.py automated_health_check.py"

# Step 6: Verify deployment
echo "✅ Verifying deployment..."
ssh -i $SSH_KEY $PROD_USER@$PROD_SERVER "cd /opt/sophia && ./run_with_ssl_fix.py unified_command_interface.py 'check system status'"

echo "✅ Sophia AI has been deployed to production successfully!"
echo "🌐 You can access the system at: https://sophia.payready.ai"
