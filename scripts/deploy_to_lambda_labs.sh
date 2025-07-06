#!/bin/bash
# Deploy Sophia AI to Lambda Labs

set -e

echo "🚀 Deploying Sophia AI to Lambda Labs"
echo "======================================"

# Configuration
LAMBDA_LABS_IP="192.9.243.87"  # Replace with your Lambda Labs IP
SSH_KEY="~/.ssh/pulumi_lambda_key"
REMOTE_USER="ubuntu"

# Check if we can connect
echo "📡 Testing connection to Lambda Labs..."
if ssh -i "$SSH_KEY" -o ConnectTimeout=5 "$REMOTE_USER@$LAMBDA_LABS_IP" "echo '✅ Connected to Lambda Labs'"; then
    echo "✅ Connection successful"
else
    echo "❌ Cannot connect to Lambda Labs. Check IP and SSH key."
    exit 1
fi

# Build images locally
echo "🔨 Building Docker images..."
docker build -t scoobyjava15/sophia-ai:latest -f Dockerfile.production .
docker build -t scoobyjava15/sophia-frontend:latest -f frontend/Dockerfile .

# Push images to Docker Hub
echo "📤 Pushing images to Docker Hub..."
docker push scoobyjava15/sophia-ai:latest
docker push scoobyjava15/sophia-frontend:latest

# Copy docker-compose file to Lambda Labs
echo "📋 Copying docker-compose.cloud.yml to Lambda Labs..."
scp -i "$SSH_KEY" docker-compose.cloud.yml "$REMOTE_USER@$LAMBDA_LABS_IP:~/docker-compose.yml"

# Deploy on Lambda Labs
echo "🚀 Deploying on Lambda Labs..."
ssh -i "$SSH_KEY" "$REMOTE_USER@$LAMBDA_LABS_IP" << 'EOF'
    # Pull latest images
    docker pull scoobyjava15/sophia-ai:latest
    docker pull scoobyjava15/sophia-frontend:latest
    
    # Stop existing containers
    docker-compose down || true
    
    # Start new containers
    docker-compose up -d
    
    # Check status
    sleep 10
    docker ps
    
    # Test backend health
    curl -s http://localhost:8000/health | python3 -m json.tool || echo "Backend not ready yet"
EOF

echo "✅ Deployment complete!"
echo "🌐 Access your application at:"
echo "   Frontend: http://$LAMBDA_LABS_IP"
echo "   Backend API: http://$LAMBDA_LABS_IP:8000"
echo "   API Docs: http://$LAMBDA_LABS_IP:8000/docs" 