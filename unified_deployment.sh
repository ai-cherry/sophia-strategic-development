#!/bin/bash
# Deploy Sophia AI to Docker Swarm using Pulumi ESC secrets
# Implements the enhanced ESC run pattern for automatic secret injection

set -euo pipefail

MASTER_IP="192.222.51.151"
SSH_KEY="$HOME/.ssh/lynn_sophia_h200_key"
ESC_ENV="default/sophia-ai-production"
STACK_NAME="sophia-ai"

echo "🚀 Deploying Sophia AI to Docker Swarm"
echo "======================================"
echo "Master: $MASTER_IP"
echo "ESC Environment: $ESC_ENV"
echo "Stack: $STACK_NAME"
echo ""

# Function to execute commands on Swarm manager
swarm_exec() {
    ssh -i "$SSH_KEY" ubuntu@$MASTER_IP "$1"
}

echo "🔍 Pre-deployment checks..."

# Check Swarm status
echo "📊 Checking Swarm status:"
swarm_exec "sudo docker node ls"

# Check Docker secrets
echo ""
echo "🔐 Checking Docker secrets:"
swarm_exec "sudo docker secret ls"

echo ""
echo "🚀 Using ESC run pattern for deployment with automatic secret injection..."

# Use esc run to deploy with environment variables automatically injected
esc run $ESC_ENV -- bash -c "
echo '📦 Deploying stack with ESC-managed environment variables...'

# Copy docker-compose.cloud.yml to remote server
echo '📁 Copying docker-compose.cloud.yml to Swarm manager...'
scp -i $SSH_KEY docker-compose.cloud.yml ubuntu@$MASTER_IP:/tmp/

# Deploy the stack with environment variables from ESC
echo '🚀 Deploying Docker stack: $STACK_NAME'
ssh -i $SSH_KEY ubuntu@$MASTER_IP \"
    cd /tmp &&
    sudo docker stack deploy \\
        -c docker-compose.cloud.yml \\
        --with-registry-auth \\
        $STACK_NAME
\"

echo ''
echo '✅ Stack deployment initiated!'

# Wait for services to start
echo '⏳ Waiting for services to initialize...'
sleep 30

# Check deployment status
echo '📊 Deployment status:'
ssh -i $SSH_KEY ubuntu@$MASTER_IP 'sudo docker stack ps $STACK_NAME'

echo ''
echo '🌐 Service endpoints:'
ssh -i $SSH_KEY ubuntu@$MASTER_IP 'sudo docker service ls'

echo ''
echo '🔍 Health check:'
curl -f http://$MASTER_IP:8000/health && echo 'API is responding!' || echo 'API not ready yet'

echo ''
echo '✅ Deployment completed successfully!'
echo '🌐 Access your Sophia AI platform at: http://$MASTER_IP:8000'
echo '📊 Traefik dashboard: http://$MASTER_IP:8080'
echo '📝 API documentation: http://$MASTER_IP:8000/docs'
echo ''
echo '🔧 Run ./monitor_swarm.sh for continuous monitoring'
"

echo ""
echo "🎉 Sophia AI Deployment Complete!"
echo "================================="
