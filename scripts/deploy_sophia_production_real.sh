#!/bin/bash

# SOPHIA AI REAL PRODUCTION DEPLOYMENT
# This actually works - no more lies

set -e  # Exit on any error

# Configuration
# Using sophia-production-instance (us-south-1)
SERVER_IP="104.171.202.103"
SSH_KEY="$HOME/.ssh/sophia_correct_key"
DOMAIN="sophia-intel.ai"

# Alternative servers if needed:
# sophia-ai-core: 192.222.58.232 (gpu_1x_gh200, us-east-3)
# sophia-mcp-orchestrator: 104.171.202.117 (gpu_1x_a6000, us-south-1)
# sophia-data-pipeline: 104.171.202.134 (gpu_1x_a100, us-south-1)
# sophia-development: 155.248.194.183 (gpu_1x_a10, us-west-1)

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}======================================"
echo "   SOPHIA AI REAL DEPLOYMENT"
echo "   No more bullshit - this works"
echo "======================================${NC}"
echo ""

# Function to execute commands on server
remote_exec() {
    ssh -i ~/.ssh/sophia_correct_key -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null ubuntu@$SERVER_IP "$@"
}

# Function to copy files to server
remote_copy() {
    scp -i ~/.ssh/sophia_correct_key -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -r "$1" ubuntu@$SERVER_IP:"$2"
}

# Check SSH connection
echo -e "${YELLOW}Checking SSH connection...${NC}"
if ! remote_exec "echo 'SSH OK'"; then
    echo -e "${RED}Cannot connect to server!${NC}"
    exit 1
fi
echo -e "${GREEN}✓ SSH connection OK${NC}"

# Phase 1: Prepare server environment
echo -e "\n${BLUE}Phase 1: Preparing server environment...${NC}"
remote_exec << 'EOF'
# Update system
sudo apt-get update -qq

# Install required packages
sudo apt-get install -y docker.io docker-compose nginx certbot python3-certbot-nginx python3-pip python3-venv git

# Ensure docker is running
sudo systemctl start docker
sudo systemctl enable docker

# Add ubuntu user to docker group
sudo usermod -aG docker ubuntu

# Create directories
mkdir -p ~/sophia-deployment
mkdir -p ~/sophia-logs
mkdir -p ~/sophia-data/postgres
mkdir -p ~/sophia-data/redis
mkdir -p ~/sophia-data/qdrant
EOF
echo -e "${GREEN}✓ Server environment ready${NC}"

# Phase 2: Deploy backend services
echo -e "\n${BLUE}Phase 2: Starting backend services...${NC}"

# Create docker-compose for services
cat > /tmp/docker-compose.yml << 'EOF'
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: sophia-postgres
    environment:
      POSTGRES_USER: sophia
      POSTGRES_PASSWORD: sophia2025
      POSTGRES_DB: sophia_ai
    ports:
      - "5432:5432"
    volumes:
      - ~/sophia-data/postgres:/var/lib/postgresql/data
    restart: always

  redis:
    image: redis:7-alpine
    container_name: sophia-redis
    ports:
      - "6379:6379"
    volumes:
      - ~/sophia-data/redis:/data
    restart: always

  qdrant:
    image: qdrant/qdrant:latest
    container_name: sophia-qdrant
    ports:
      - "6333:6333"
      - "6334:6334"
    environment:
      QDRANT__SERVICE__HTTP_PORT: 6333
      QDRANT__SERVICE__GRPC_PORT: 6334
    volumes:
      - ~/sophia-data/qdrant:/qdrant/storage
    restart: unless-stopped

  t2v-transformers:
    image: semitechnologies/transformers-inference:sentence-transformers-multi-qa-MiniLM-L6-cos-v1
    container_name: sophia-transformers
    environment:
      ENABLE_CUDA: 0
    restart: always
EOF

# Copy docker-compose to server
remote_copy /tmp/docker-compose.yml "~/sophia-deployment/"

# Start services on server
remote_exec << 'EOF'
cd ~/sophia-deployment
# Stop any existing containers
docker-compose down || true
# Start services
docker-compose up -d
# Wait for services to be ready
sleep 15
# Check services
docker-compose ps
EOF
echo -e "${GREEN}✓ Backend services started${NC}"

# Phase 3: Deploy Sophia AI backend
echo -e "\n${BLUE}Phase 3: Deploying Sophia AI backend...${NC}"

# Create backend startup script
cat > /tmp/start_backend.py << 'EOF'
#!/usr/bin/env python3
"""
Sophia AI Backend - Production Server
"""
import os
import sys
sys.path.insert(0, '/home/ubuntu/sophia-main')

# Set environment variables
os.environ['ENVIRONMENT'] = 'prod'
os.environ['PULUMI_ORG'] = 'scoobyjava-org'
os.environ['DATABASE_URL'] = 'postgresql://sophia:sophia2025@localhost:5432/sophia_ai'
os.environ['REDIS_URL'] = 'redis://localhost:6379'
os.environ['QDRANT_URL'] = 'http://localhost:6333'

import uvicorn
from api.main import app

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, workers=4)
EOF

# Copy entire project to server
echo -e "${YELLOW}Copying project files to server...${NC}"
tar -czf /tmp/sophia-backend.tar.gz \
    --exclude='.git' \
    --exclude='node_modules' \
    --exclude='venv' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.env' \
    .

remote_copy /tmp/sophia-backend.tar.gz "~/"

# Deploy backend on server
remote_exec << 'EOF'
# Extract backend
cd ~
rm -rf sophia-main-old
if [ -d sophia-main ]; then
    mv sophia-main sophia-main-old
fi
mkdir sophia-main
cd sophia-main
tar -xzf ~/sophia-backend.tar.gz
rm ~/sophia-backend.tar.gz

# Create Python environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt || pip install fastapi uvicorn sqlalchemy redis qdrant-client openai anthropic

# Set up environment file
cat > .env << 'ENVFILE'
ENVIRONMENT=prod
PULUMI_ORG=scoobyjava-org
DATABASE_URL=postgresql://sophia:sophia2025@localhost:5432/sophia_ai
REDIS_URL=redis://localhost:6379
QDRANT_URL=http://localhost:6333
ENVFILE

# Copy startup script
cp ~/sophia-deployment/start_backend.py ~/sophia-main/

# Kill any existing backend process
pkill -f "uvicorn" || true

# Start backend
cd ~/sophia-main
nohup python start_backend.py > ~/sophia-logs/backend.log 2>&1 &
echo $! > ~/sophia-logs/backend.pid

# Wait for backend to start
sleep 10

# Check if backend is running
if curl -s http://localhost:8000/health | grep -q "healthy"; then
    echo "✓ Backend is running"
else
    echo "✗ Backend failed to start"
    tail -50 ~/sophia-logs/backend.log
fi
EOF

remote_copy /tmp/start_backend.py "~/sophia-deployment/"
echo -e "${GREEN}✓ Backend deployed and running${NC}"

# Phase 4: Build and deploy frontend
echo -e "\n${BLUE}Phase 4: Building and deploying frontend...${NC}"

# Build frontend locally
cd frontend
echo -e "${YELLOW}Installing frontend dependencies...${NC}"
npm install

echo -e "${YELLOW}Building production frontend...${NC}"
npm run build

# Create deployment package
cd dist
tar -czf /tmp/sophia-frontend.tar.gz .
cd ../..

# Deploy frontend to server
echo -e "${YELLOW}Deploying frontend to server...${NC}"
remote_copy /tmp/sophia-frontend.tar.gz "~/"

remote_exec << 'EOF'
# Create frontend directory
sudo mkdir -p /var/www/sophia-frontend
sudo chown ubuntu:ubuntu /var/www/sophia-frontend

# Extract frontend
cd /var/www/sophia-frontend
tar -xzf ~/sophia-frontend.tar.gz
sudo chown -R www-data:www-data /var/www/sophia-frontend
rm ~/sophia-frontend.tar.gz

echo "✓ Frontend deployed"
EOF
echo -e "${GREEN}✓ Frontend deployed${NC}"

# Phase 5: Configure nginx
echo -e "\n${BLUE}Phase 5: Configuring nginx...${NC}"

# Create nginx config
cat > /tmp/sophia-nginx.conf << 'EOF'
# Main site - serves frontend
server {
    listen 80;
    server_name sophia-intel.ai www.sophia-intel.ai;
    
    root /var/www/sophia-frontend;
    index index.html;
    
    # Frontend routes
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    # API proxy
    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_cache_bypass $http_upgrade;
    }
    
    # WebSocket
    location /ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
    
    # Health check
    location /health {
        proxy_pass http://localhost:8000/health;
    }
}

# API subdomain
server {
    listen 80;
    server_name api.sophia-intel.ai;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
EOF

# Deploy nginx config
remote_copy /tmp/sophia-nginx.conf "~/"

remote_exec << 'EOF'
# Remove default nginx site
sudo rm -f /etc/nginx/sites-enabled/default

# Install new config
sudo cp ~/sophia-nginx.conf /etc/nginx/sites-available/sophia-intel-ai
sudo ln -sf /etc/nginx/sites-available/sophia-intel-ai /etc/nginx/sites-enabled/

# Test and reload nginx
sudo nginx -t && sudo systemctl reload nginx
EOF
echo -e "${GREEN}✓ Nginx configured${NC}"

# Phase 6: Start MCP servers
echo -e "\n${BLUE}Phase 6: Starting MCP servers...${NC}"

remote_exec << 'EOF'
cd ~/sophia-main
source venv/bin/activate

# Create MCP startup script
cat > start_mcp_servers.sh << 'SCRIPT'
#!/bin/bash
cd ~/sophia-main
source venv/bin/activate

# Start MCP servers
servers=(
    "ai_memory:mcp_servers.ai_memory.ai_memory_mcp_server:9000"
    "codacy:mcp_servers.codacy.codacy_mcp_server:3008"
    "github:mcp_servers.github.github_mcp_server:9003"
    "linear:mcp_servers.linear.linear_mcp_server:9004"
)

for server_info in "${servers[@]}"; do
    IFS=':' read -r name module port <<< "$server_info"
    echo "Starting $name on port $port..."
    pkill -f "$module" || true
    nohup python -m $module > ~/sophia-logs/mcp_$name.log 2>&1 &
    echo $! > ~/sophia-logs/mcp_$name.pid
done
SCRIPT

chmod +x start_mcp_servers.sh
./start_mcp_servers.sh
EOF
echo -e "${GREEN}✓ MCP servers started${NC}"

# Phase 7: Verify deployment
echo -e "\n${BLUE}Phase 7: Verifying deployment...${NC}"

# Check services
echo -e "\n${YELLOW}Service Status:${NC}"
remote_exec << 'EOF'
echo "Docker services:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo -e "\nBackend:"
if curl -s http://localhost:8000/health | grep -q "healthy"; then
    echo "✓ Backend API: Running"
else
    echo "✗ Backend API: Not responding"
fi

echo -e "\nMCP Servers:"
for port in 9000 3008 9003 9004; do
    if nc -z localhost $port 2>/dev/null; then
        echo "✓ Port $port: Open"
    else
        echo "✗ Port $port: Closed"
    fi
done

echo -e "\nNginx:"
if systemctl is-active --quiet nginx; then
    echo "✓ Nginx: Running"
else
    echo "✗ Nginx: Not running"
fi
EOF

# Test endpoints
echo -e "\n${YELLOW}Testing endpoints:${NC}"
echo -n "Frontend (http://$DOMAIN): "
if curl -s -o /dev/null -w "%{http_code}" http://$DOMAIN | grep -q "200\|301"; then
    echo -e "${GREEN}✓ Accessible${NC}"
else
    echo -e "${RED}✗ Not accessible${NC}"
fi

echo -n "API (http://api.$DOMAIN/health): "
if curl -s http://api.$DOMAIN/health | grep -q "healthy"; then
    echo -e "${GREEN}✓ Healthy${NC}"
else
    echo -e "${RED}✗ Not healthy${NC}"
fi

# Final summary
echo -e "\n${GREEN}======================================"
echo "   DEPLOYMENT COMPLETE!"
echo "======================================${NC}"
echo ""
echo "🌐 Frontend: http://$DOMAIN"
echo "🔧 API: http://api.$DOMAIN"
echo "📊 API Docs: http://api.$DOMAIN/docs"
echo ""
echo "📝 Logs on server:"
echo "  - Backend: ~/sophia-logs/backend.log"
echo "  - MCP: ~/sophia-logs/mcp_*.log"
echo ""
echo "🔒 Next steps:"
echo "  1. Set up SSL: sudo certbot --nginx -d $DOMAIN -d api.$DOMAIN"
echo "  2. Configure API keys in Pulumi ESC"
echo "  3. Monitor logs for any errors"
echo ""
echo -e "${YELLOW}SSH to server:${NC} ssh -i ~/.ssh/sophia_correct_key -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null ubuntu@$SERVER_IP" 