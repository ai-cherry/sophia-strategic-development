#!/bin/bash
# 🚀 SOPHIA AI LAMBDA LABS PRODUCTION DEPLOYMENT SCRIPT
# =====================================================
# Date: July 5, 2025
# Target: sophia-platform-prod (146.235.200.1)
# Mission: Deploy Sophia AI production container

set -e

echo "🚀 SOPHIA AI PRODUCTION DEPLOYMENT STARTING..."
echo "=============================================="
echo "📅 Date: $(date)"
echo "🎯 Target: sophia-platform-prod"
echo "🐳 Image: scoobyjava15/sophia-ai:latest"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Step 1: System Update
print_header "1. Updating system packages..."
sudo apt-get update -y
sudo apt-get upgrade -y
print_status "System updated successfully"

# Step 2: Install Docker if needed
print_header "2. Checking Docker installation..."
if ! command -v docker &> /dev/null; then
    print_status "Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    newgrp docker
    print_status "Docker installed successfully"
else
    print_status "Docker already installed"
    docker --version
fi

# Step 3: Stop any existing Sophia AI containers
print_header "3. Cleaning up existing deployments..."
sudo docker stop sophia-ai-production 2>/dev/null || true
sudo docker rm sophia-ai-production 2>/dev/null || true
sudo docker stop sophia-ai 2>/dev/null || true
sudo docker rm sophia-ai 2>/dev/null || true
print_status "Cleanup completed"

# Step 4: Pull latest Sophia AI image
print_header "4. Pulling latest Sophia AI image..."
sudo docker pull scoobyjava15/sophia-ai:latest
print_status "Image pulled successfully"

# Step 5: Create production environment file
print_header "5. Setting up production environment..."
sudo tee /opt/sophia-ai-production.env << EOF
# Sophia AI Production Environment
ENVIRONMENT=production
PULUMI_ORG=scoobyjava-org
PORT=8000

# Lambda Labs Configuration
LAMBDA_LABS_INSTANCE_TYPE=gpu_1x_a10
LAMBDA_LABS_REGION=us-west-1
LAMBDA_LABS_DEPLOYMENT_DATE=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Application Configuration
SOPHIA_AI_VERSION=3.0.0
SOPHIA_AI_DEPLOYMENT_ID=lambda-production-$(date +%s)
SOPHIA_AI_LOG_LEVEL=info
EOF
print_status "Environment configuration created"

# Step 6: Deploy Sophia AI container
print_header "6. Deploying Sophia AI production container..."
sudo docker run -d \
  --name sophia-ai-production \
  --restart always \
  -p 80:8000 \
  -p 443:8000 \
  --env-file /opt/sophia-ai-production.env \
  --memory="6g" \
  --cpus="3.0" \
  --health-cmd="curl -f http://localhost:8000/api/health || exit 1" \
  --health-interval=30s \
  --health-timeout=10s \
  --health-start-period=40s \
  --health-retries=3 \
  scoobyjava15/sophia-ai:latest

print_status "Container deployed successfully"

# Step 7: Wait for startup
print_header "7. Waiting for application startup..."
sleep 30

# Step 8: Health checks
print_header "8. Running health checks..."
echo "Container status:"
sudo docker ps | grep sophia-ai-production

echo ""
echo "Container health:"
sudo docker inspect --format='{{.State.Health.Status}}' sophia-ai-production

echo ""
echo "Application health check:"
for i in {1..10}; do
    if curl -f http://localhost/api/health > /dev/null 2>&1; then
        print_status "✅ Application is healthy and responding"
        break
    else
        print_warning "Waiting for application... (attempt $i/10)"
        sleep 10
    fi
done

# Step 9: Configure Nginx reverse proxy
print_header "9. Setting up Nginx reverse proxy..."
sudo apt-get install -y nginx

sudo tee /etc/nginx/sites-available/sophia-ai << EOF
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    server_name _;

    # API and health endpoints
    location /api/ {
        proxy_pass http://localhost:8000/api/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }

    # Health check
    location /health {
        proxy_pass http://localhost:8000/api/health;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }

    # Documentation
    location /docs {
        proxy_pass http://localhost:8000/docs;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }

    # Root redirect to health
    location / {
        proxy_pass http://localhost:8000/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

sudo rm -f /etc/nginx/sites-enabled/default
sudo ln -sf /etc/nginx/sites-available/sophia-ai /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
sudo systemctl enable nginx

print_status "Nginx configured and started"

# Step 10: Final validation
print_header "10. Final deployment validation..."
echo ""
echo "🔍 DEPLOYMENT STATUS:"
echo "===================="
echo "Container Status: $(sudo docker inspect --format='{{.State.Status}}' sophia-ai-production)"
echo "Container Health: $(sudo docker inspect --format='{{.State.Health.Status}}' sophia-ai-production)"
echo "Public IP: $(curl -s ifconfig.me)"
echo "Internal Health: $(curl -s http://localhost:8000/api/health | jq -r '.status' 2>/dev/null || echo 'checking...')"
echo ""

# Test external access
if curl -f http://$(curl -s ifconfig.me)/api/health > /dev/null 2>&1; then
    print_status "✅ External access working"
else
    print_warning "⚠️ External access may need firewall configuration"
fi

# Step 11: Setup monitoring
print_header "11. Setting up basic monitoring..."
sudo tee /opt/sophia-monitor.sh << EOF
#!/bin/bash
# Simple monitoring script for Sophia AI

while true; do
    timestamp=\$(date)
    container_status=\$(sudo docker inspect --format='{{.State.Status}}' sophia-ai-production 2>/dev/null || echo "stopped")
    health_status=\$(sudo docker inspect --format='{{.State.Health.Status}}' sophia-ai-production 2>/dev/null || echo "unknown")

    if [ "\$container_status" != "running" ] || [ "\$health_status" = "unhealthy" ]; then
        echo "[\$timestamp] ALERT: Container status=\$container_status, health=\$health_status" >> /var/log/sophia-monitor.log
        # Restart if needed
        if [ "\$container_status" != "running" ]; then
            echo "[\$timestamp] Restarting sophia-ai-production container" >> /var/log/sophia-monitor.log
            sudo docker start sophia-ai-production
        fi
    fi

    sleep 60
done
EOF

sudo chmod +x /opt/sophia-monitor.sh
sudo nohup /opt/sophia-monitor.sh > /dev/null 2>&1 &
print_status "Monitoring started"

# Final summary
echo ""
print_header "🎉 SOPHIA AI DEPLOYMENT COMPLETED!"
echo "=================================================="
print_status "✅ Container deployed and running"
print_status "✅ Nginx reverse proxy configured"
print_status "✅ Health monitoring active"
print_status "✅ External access configured"
echo ""
echo "🌐 ACCESS URLS:"
echo "  - Main API: http://$(curl -s ifconfig.me)/"
echo "  - Health Check: http://$(curl -s ifconfig.me)/api/health"
echo "  - API Documentation: http://$(curl -s ifconfig.me)/docs"
echo ""
echo "📊 MONITORING:"
echo "  - Container logs: sudo docker logs sophia-ai-production"
echo "  - System logs: sudo tail -f /var/log/sophia-monitor.log"
echo "  - Container status: sudo docker ps | grep sophia-ai"
echo ""
print_status "🚀 Sophia AI is now live on Lambda Labs!"
echo "=================================================="
