#!/bin/bash
set -e

# FINAL WORKING CONFIGURATION - DO NOT CHANGE
LAMBDA_IP="192.222.58.232"  # GH200 Instance - ONLY WORKING IP
SSH_KEY="~/.ssh/sophia2025.pem"  # ONLY WORKING SSH KEY
DOCKER_REGISTRY="scoobyjava15"

echo "🚀 FINAL Sophia AI Deployment Script"
echo "====================================="
echo "📍 Lambda Labs GH200: $LAMBDA_IP"
echo "🔑 SSH Key: $SSH_KEY"
echo ""

# Test SSH
echo "🔗 Testing SSH connection..."
if ! ssh -i $SSH_KEY -o ConnectTimeout=10 ubuntu@$LAMBDA_IP "echo 'Connected'"; then
    echo "❌ SSH failed. Make sure you have the sophia2025.pem key."
    exit 1
fi

# Deploy
echo "🚀 Deploying to Lambda Labs..."
ssh -i $SSH_KEY ubuntu@$LAMBDA_IP << 'DEPLOY'
set -e

# Install docker-compose if needed
if ! command -v docker-compose &> /dev/null; then
    echo "📦 Installing docker-compose..."
    sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

# Create deployment directory
mkdir -p ~/sophia-ai && cd ~/sophia-ai

# Create docker-compose.yml
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: sophia_db
      POSTGRES_USER: sophia_user
      POSTGRES_PASSWORD: sophia_secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U sophia_user"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    image: scoobyjava15/sophia-backend:latest
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
      - DATABASE_URL=postgresql://sophia_user:sophia_secure_password@postgres:5432/sophia_db
      - REDIS_URL=redis://redis:6379
    depends_on:
      - postgres
      - redis
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  mcp-servers:
    image: scoobyjava15/sophia-mcp-servers:latest
    ports:
      - "9001-9103:9001-9103"
      - "3008:3008"
    environment:
      - ENVIRONMENT=production
    depends_on:
      - backend

  frontend:
    image: scoobyjava15/sophia-frontend:latest
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://192.222.58.232:8000
      - NEXT_PUBLIC_WS_URL=ws://192.222.58.232:8000
    depends_on:
      - backend

  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=sophia_admin
    volumes:
      - grafana_data:/var/lib/grafana

volumes:
  postgres_data:
  redis_data:
  prometheus_data:
  grafana_data:
EOF

# Create Prometheus config
cat > prometheus.yml << 'EOF'
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'sophia-backend'
    static_configs:
      - targets: ['backend:8000']
  - job_name: 'mcp-servers'
    static_configs:
      - targets: ['mcp-servers:9001']
EOF

# Deploy
docker-compose down || true
docker-compose pull
docker-compose up -d

# Wait
sleep 30

# Check
docker-compose ps
DEPLOY

# Test deployment
echo ""
echo "🧪 Testing deployment..."
echo -n "Backend: "
curl -s http://$LAMBDA_IP:8000/health | jq -r '.status' 2>/dev/null || echo "Failed"

echo ""
echo "✅ Deployment complete!"
echo ""
echo "🌐 Access URLs:"
echo "   - Unified Chat/Dashboard: http://$LAMBDA_IP:3000"
echo "   - Backend API: http://$LAMBDA_IP:8000"
echo "   - API Docs: http://$LAMBDA_IP:8000/docs"
echo "   - Grafana: http://$LAMBDA_IP:3001 (admin/sophia_admin)"
echo "   - Prometheus: http://$LAMBDA_IP:9090"
echo ""
echo "📊 MCP Servers:"
echo "   - AI Memory: port 9001"
echo "   - UI/UX Agent: port 9002"
echo "   - Linear: port 9004"
echo "   - GitHub: port 9103"
echo "   - Asana: port 9100"
echo "   - Codacy: port 3008" 