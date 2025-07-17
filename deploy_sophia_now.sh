#!/bin/bash
# 🚀 SOPHIA AI COMPLETE DEPLOYMENT SCRIPT
# Execute this script to deploy everything to Lambda Labs
# Date: July 16, 2025

set -e

echo "🚀 SOPHIA AI COMPLETE DEPLOYMENT STARTING..."
echo "==========================================="
echo "📅 Date: $(date)"
echo ""

# Configuration
LAMBDA_KEY="$HOME/.ssh/lambda_labs_key"
PRIMARY_SERVER="192.222.58.232"
BUSINESS_SERVER="104.171.202.117"
DATA_SERVER="104.171.202.134"
PRODUCTION_SERVER="104.171.202.103"
DEV_SERVER="155.248.194.183"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

# Check prerequisites
print_step "Checking prerequisites..."
if [ ! -f "$LAMBDA_KEY" ]; then
    print_warning "Lambda Labs SSH key not found at $LAMBDA_KEY"
    echo "Please ensure your SSH key is at: $LAMBDA_KEY"
    exit 1
fi

# Step 1: Build and push Docker images
print_step "1. Building and pushing Docker images..."
echo "Building backend image..."
docker build -f backend/Dockerfile -t scoobyjava15/sophia-backend:latest .
docker push scoobyjava15/sophia-backend:latest

echo "Building MCP server images..."
for mcp in mcp-servers/*/; do
    if [ -f "$mcp/Dockerfile" ]; then
        service=$(basename "$mcp")
        echo "Building $service..."
        docker build -t "scoobyjava15/mcp-$service:latest" "$mcp"
        docker push "scoobyjava15/mcp-$service:latest"
    fi
done
print_status "Docker images built and pushed"

# Step 2: Deploy to AI Core Server (Primary)
print_step "2. Deploying to AI Core Server ($PRIMARY_SERVER)..."
ssh -i "$LAMBDA_KEY" ubuntu@$PRIMARY_SERVER << 'EOF'
set -e
echo "Setting up AI Core server..."

# Clone/update repository
if [ ! -d "sophia-main" ]; then
    git clone https://github.com/ai-cherry/sophia-main.git
else
    cd sophia-main && git pull && cd ..
fi

# Stop existing services
sudo systemctl stop sophia-* 2>/dev/null || true
docker stop $(docker ps -aq) 2>/dev/null || true
docker rm $(docker ps -aq) 2>/dev/null || true

# Deploy PostgreSQL
docker run -d \
  --name postgres \
  --restart unless-stopped \
  -e POSTGRES_PASSWORD=sophia_secure_password \
  -e POSTGRES_DB=sophia_ai_db \
  -v postgres_data:/var/lib/postgresql/data \
  -p 5432:5432 \
  pgvector/pgvector:pg16

# Deploy Redis
docker run -d \
  --name redis \
  --restart unless-stopped \
  -v redis_data:/data \
  -p 6379:6379 \
  redis:7-alpine

# Deploy Qdrant
docker run -d \
  --name qdrant \
  --restart unless-stopped \
  -p 6333:6333 \
  -v qdrant_data:/qdrant/storage \
  qdrant/qdrant

# Deploy Backend API
docker run -d \
  --name sophia-backend \
  --restart unless-stopped \
  -e ENVIRONMENT=prod \
  -e DATABASE_URL=postgresql://postgres:sophia_secure_password@localhost:5432/sophia_ai_db \
  -e REDIS_URL=redis://localhost:6379 \
  -e QDRANT_URL=http://localhost:6333 \
  -p 8003:8000 \
  --network host \
  scoobyjava15/sophia-backend:latest

# Deploy MCP servers
docker run -d --name mcp-vector-search --restart unless-stopped -p 8000:8000 --network host scoobyjava15/mcp-vector_search_mcp:latest
docker run -d --name mcp-real-time-chat --restart unless-stopped -p 8001:8001 --network host scoobyjava15/mcp-real_time_chat_mcp:latest
docker run -d --name mcp-ai-memory --restart unless-stopped -p 8002:8002 --network host scoobyjava15/mcp-ai_memory_mcp:latest
docker run -d --name mcp-unified-memory --restart unless-stopped -p 9001:9001 --network host scoobyjava15/mcp-unified_memory_service:latest

# Setup Nginx
sudo apt-get update && sudo apt-get install -y nginx
sudo tee /etc/nginx/sites-available/sophia-ai << 'NGINX'
server {
    listen 80;
    server_name _;

    location / {
        root /var/www/sophia-frontend;
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://localhost:8003/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /mcp/ {
        proxy_pass http://localhost:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
NGINX

sudo rm -f /etc/nginx/sites-enabled/default
sudo ln -sf /etc/nginx/sites-available/sophia-ai /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl restart nginx

echo "AI Core server deployment complete!"
EOF
print_status "AI Core server deployed"

# Step 3: Deploy to Business Tools Server
print_step "3. Deploying to Business Tools Server ($BUSINESS_SERVER)..."
ssh -i "$LAMBDA_KEY" ubuntu@$BUSINESS_SERVER << 'EOF'
set -e
echo "Setting up Business Tools server..."

# Stop existing services
docker stop $(docker ps -aq) 2>/dev/null || true
docker rm $(docker ps -aq) 2>/dev/null || true

# Deploy MCP servers
docker run -d --name mcp-gong --restart unless-stopped -p 8100:8100 --network host scoobyjava15/mcp-gong_mcp:latest
docker run -d --name mcp-hubspot --restart unless-stopped -p 8101:8101 --network host scoobyjava15/mcp-hubspot_mcp:latest
docker run -d --name mcp-linear --restart unless-stopped -p 8102:8102 --network host scoobyjava15/mcp-linear_mcp:latest
docker run -d --name mcp-asana --restart unless-stopped -p 8103:8103 --network host scoobyjava15/mcp-asana_mcp:latest
docker run -d --name mcp-slack --restart unless-stopped -p 8104:8104 --network host scoobyjava15/mcp-slack_mcp:latest

echo "Business Tools server deployment complete!"
EOF
print_status "Business Tools server deployed"

# Step 4: Deploy to Data Pipeline Server
print_step "4. Deploying to Data Pipeline Server ($DATA_SERVER)..."
ssh -i "$LAMBDA_KEY" ubuntu@$DATA_SERVER << 'EOF'
set -e
echo "Setting up Data Pipeline server..."

# Stop existing services
docker stop $(docker ps -aq) 2>/dev/null || true
docker rm $(docker ps -aq) 2>/dev/null || true

# Deploy MCP servers
docker run -d --name mcp-github --restart unless-stopped -p 8200:8200 --network host scoobyjava15/mcp-github_mcp:latest
docker run -d --name mcp-notion --restart unless-stopped -p 8201:8201 --network host scoobyjava15/mcp-notion_mcp:latest
docker run -d --name mcp-postgres --restart unless-stopped -p 8202:8202 --network host scoobyjava15/mcp-postgres_mcp:latest

echo "Data Pipeline server deployment complete!"
EOF
print_status "Data Pipeline server deployed"

# Step 5: Deploy to Production Services Server
print_step "5. Deploying to Production Services Server ($PRODUCTION_SERVER)..."
ssh -i "$LAMBDA_KEY" ubuntu@$PRODUCTION_SERVER << 'EOF'
set -e
echo "Setting up Production Services server..."

# Stop existing services
docker stop $(docker ps -aq) 2>/dev/null || true
docker rm $(docker ps -aq) 2>/dev/null || true

# Deploy MCP servers
docker run -d --name mcp-codacy --restart unless-stopped -p 8300:8300 --network host scoobyjava15/mcp-codacy_mcp:latest
docker run -d --name mcp-portkey --restart unless-stopped -p 8301:8301 --network host scoobyjava15/mcp-portkey_admin:latest
docker run -d --name mcp-ui-ux --restart unless-stopped -p 8302:8302 --network host scoobyjava15/mcp-ui_ux_agent:latest

echo "Production Services server deployment complete!"
EOF
print_status "Production Services server deployed"

# Step 6: Build and deploy frontend
print_step "6. Building and deploying frontend..."
cd frontend
npm install
npm run build
cd ..

# Copy frontend to primary server
scp -i "$LAMBDA_KEY" -r frontend/dist/* ubuntu@$PRIMARY_SERVER:/tmp/
ssh -i "$LAMBDA_KEY" ubuntu@$PRIMARY_SERVER << 'EOF'
sudo mkdir -p /var/www/sophia-frontend
sudo cp -r /tmp/dist/* /var/www/sophia-frontend/
sudo chown -R www-data:www-data /var/www/sophia-frontend
EOF
print_status "Frontend deployed"

# Step 7: Validation
print_step "7. Validating deployment..."
echo ""
echo "🔍 DEPLOYMENT VALIDATION:"
echo "========================"

# Check each server
for server in $PRIMARY_SERVER $BUSINESS_SERVER $DATA_SERVER $PRODUCTION_SERVER; do
    echo ""
    echo "Server: $server"
    ssh -i "$LAMBDA_KEY" ubuntu@$server "docker ps --format 'table {{.Names}}\t{{.Status}}' | grep -E '(sophia|mcp)'"
done

# Test endpoints
echo ""
echo "Testing endpoints..."
curl -s http://$PRIMARY_SERVER/api/health && echo " ✓ Backend API healthy" || echo " ✗ Backend API failed"
curl -s http://$PRIMARY_SERVER/ && echo " ✓ Frontend accessible" || echo " ✗ Frontend failed"

echo ""
echo "🎉 SOPHIA AI DEPLOYMENT COMPLETED!"
echo "=================================="
echo ""
echo "🌐 ACCESS URLS:"
echo "  Frontend: http://$PRIMARY_SERVER/"
echo "  Backend API: http://$PRIMARY_SERVER/api/"
echo "  Health Check: http://$PRIMARY_SERVER/api/health"
echo ""
echo "📊 MONITORING:"
echo "  AI Core: ssh ubuntu@$PRIMARY_SERVER 'docker ps'"
echo "  Business: ssh ubuntu@$BUSINESS_SERVER 'docker ps'"
echo "  Data: ssh ubuntu@$DATA_SERVER 'docker ps'"
echo "  Production: ssh ubuntu@$PRODUCTION_SERVER 'docker ps'"
echo ""
echo "🚀 Sophia AI is now live on Lambda Labs!"
