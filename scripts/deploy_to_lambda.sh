#!/bin/bash
set -e

# Lambda Labs GH200 Instance Configuration
LAMBDA_IP="192.222.58.232"
SSH_KEY="~/.ssh/sophia2025.pem"
DOCKER_REGISTRY="scoobyjava15"

echo "🚀 Deploying Sophia AI to Lambda Labs GH200 Instance"
echo "📍 Target: $LAMBDA_IP"
echo "🔑 SSH Key: $SSH_KEY"

# Test SSH connection
echo "🔗 Testing SSH connection..."
if ssh -i $SSH_KEY -o ConnectTimeout=10 ubuntu@$LAMBDA_IP "echo 'Connected'"; then
    echo "✅ SSH connection successful"
else
    echo "❌ SSH connection failed"
    exit 1
fi

# Create deployment script
cat > /tmp/deploy_sophia.sh << 'EOF'
#!/bin/bash
set -e

echo "🚀 Starting Sophia AI deployment on Lambda Labs"

# Update system
echo "📦 Updating system packages..."
sudo apt-get update -qq
sudo apt-get install -y docker.io docker-compose git curl jq

# Ensure Docker is running
sudo systemctl start docker
sudo usermod -aG docker ubuntu

# Create deployment directory
mkdir -p /home/ubuntu/sophia-ai
cd /home/ubuntu/sophia-ai

# Create docker-compose.yml
echo "📝 Creating docker-compose configuration..."
cat > docker-compose.yml << 'COMPOSE'
version: '3.8'

services:
  # Database
  postgres:
    image: postgres:16-alpine
    container_name: sophia-postgres
    environment:
      POSTGRES_DB: sophia_db
      POSTGRES_USER: sophia_user
      POSTGRES_PASSWORD: sophia_secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - sophia-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U sophia_user"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis
  redis:
    image: redis:7-alpine
    container_name: sophia-redis
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    networks:
      - sophia-network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Backend API
  backend:
    image: scoobyjava15/sophia-backend:latest
    container_name: sophia-backend
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
      - DATABASE_URL=postgresql://sophia_user:sophia_secure_password@postgres:5432/sophia_db
      - REDIS_URL=redis://redis:6379
      - PULUMI_ORG=scoobyjava-org
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - sophia-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # MCP Servers
  mcp-servers:
    image: scoobyjava15/sophia-mcp-servers:latest
    container_name: sophia-mcp-servers
    ports:
      - "9000-9100:9000-9100"
      - "3008:3008"
    environment:
      - ENVIRONMENT=production
      - PULUMI_ORG=scoobyjava-org
    networks:
      - sophia-network
    depends_on:
      - backend

  # Frontend (Unified Chat & Dashboard)
  frontend:
    image: scoobyjava15/sophia-frontend:latest
    container_name: sophia-frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://${LAMBDA_IP}:8000
      - NEXT_PUBLIC_WS_URL=ws://${LAMBDA_IP}:8000
    depends_on:
      - backend
    networks:
      - sophia-network

  # Prometheus
  prometheus:
    image: prom/prometheus:latest
    container_name: sophia-prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    networks:
      - sophia-network
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'

  # Grafana
  grafana:
    image: grafana/grafana:latest
    container_name: sophia-grafana
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=sophia_admin
      - GF_USERS_ALLOW_SIGN_UP=false
    volumes:
      - grafana_data:/var/lib/grafana
    networks:
      - sophia-network

volumes:
  postgres_data:
  redis_data:
  prometheus_data:
  grafana_data:

networks:
  sophia-network:
    driver: bridge
COMPOSE

# Set Lambda IP
export LAMBDA_IP=192.222.58.232
envsubst < docker-compose.yml > docker-compose.tmp && mv docker-compose.tmp docker-compose.yml

# Create Prometheus config
cat > prometheus.yml << 'PROM'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'sophia-backend'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: '/metrics'

  - job_name: 'mcp-servers'
    static_configs:
      - targets: 
        - 'mcp-servers:9001'
        - 'mcp-servers:9002'
        - 'mcp-servers:9003'
        - 'mcp-servers:9004'
        - 'mcp-servers:9100'
        - 'mcp-servers:9103'
PROM

# Pull latest images
echo "🐳 Pulling Docker images..."
docker pull scoobyjava15/sophia-backend:latest || echo "⚠️  Backend image not found, will build locally"
docker pull scoobyjava15/sophia-mcp-servers:latest || echo "⚠️  MCP servers image not found, will build locally"
docker pull scoobyjava15/sophia-frontend:latest || echo "⚠️  Frontend image not found, will build locally"

# Stop existing containers
echo "🛑 Stopping existing containers..."
docker-compose down || true

# Start services
echo "🚀 Starting services..."
docker-compose up -d

# Wait for services to start
echo "⏳ Waiting for services to start (60 seconds)..."
sleep 60

# Check service health
echo "🏥 Checking service health..."
for service in postgres redis backend mcp-servers frontend prometheus grafana; do
  if docker-compose ps | grep -q "$service.*Up"; then
    echo "✅ $service is running"
  else
    echo "❌ $service failed to start"
    docker-compose logs $service | tail -20
  fi
done

# Display access URLs
echo ""
echo "🎉 Deployment complete!"
echo ""
echo "📌 Access URLs:"
echo "   - Backend API: http://192.222.58.232:8000"
echo "   - API Docs: http://192.222.58.232:8000/docs"
echo "   - Unified Chat & Dashboard: http://192.222.58.232:3000"
echo "   - Grafana: http://192.222.58.232:3001 (admin/sophia_admin)"
echo "   - Prometheus: http://192.222.58.232:9090"
echo ""
echo "📊 MCP Server Ports:"
echo "   - AI Memory: 9001"
echo "   - UI/UX Agent: 9002"
echo "   - Codacy: 3008"
echo "   - Linear: 9004"
echo "   - GitHub: 9103"
echo "   - Asana: 9100"
echo ""
echo "🔍 To check logs:"
echo "   docker-compose logs -f [service-name]"
echo ""
EOF

# Copy deployment script
echo "📤 Copying deployment script..."
scp -i $SSH_KEY /tmp/deploy_sophia.sh ubuntu@$LAMBDA_IP:/tmp/

# Execute deployment
echo "🚀 Executing deployment..."
ssh -i $SSH_KEY ubuntu@$LAMBDA_IP "bash /tmp/deploy_sophia.sh"

# Test deployment
echo ""
echo "🧪 Testing deployment..."
echo -n "Backend health: "
curl -s http://$LAMBDA_IP:8000/health | jq -r '.status' || echo "Failed"

echo -n "MCP servers status: "
curl -s http://$LAMBDA_IP:8000/api/v1/mcp/status | jq -r '.health_percentage' || echo "Failed"

echo ""
echo "✅ Deployment complete!"
echo ""
echo "🌐 Access your deployment at:"
echo "   - Unified Chat & Dashboard: http://$LAMBDA_IP:3000"
echo "   - API Documentation: http://$LAMBDA_IP:8000/docs"
echo "   - Grafana Monitoring: http://$LAMBDA_IP:3001"
EOF 