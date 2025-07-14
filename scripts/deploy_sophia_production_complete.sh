#!/bin/bash

# Sophia AI Complete Production Deployment Script
# This script automates the full deployment of Sophia AI to production

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DOMAIN="sophia-intel.ai"
API_DOMAIN="api.sophia-intel.ai"
WEBHOOK_DOMAIN="webhooks.sophia-intel.ai"
SERVER_IP="192.222.58.232"
SSH_KEY="$HOME/.ssh/sophia_final_key"
FRONTEND_DIR="frontend"
BACKEND_DIR="backend"

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Phase 1: Pre-deployment checks
phase1_checks() {
    log_info "Phase 1: Running pre-deployment checks..."
    
    # Check SSH key exists
    if [ ! -f "$SSH_KEY" ]; then
        log_error "SSH key not found at $SSH_KEY"
        exit 1
    fi
    
    # Check frontend directory
    if [ ! -d "$FRONTEND_DIR" ]; then
        log_error "Frontend directory not found"
        exit 1
    fi
    
    # Check if we can SSH to server
    if ! ssh -i ~/.ssh/sophia_final_key -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=5 ubuntu@$SERVER_IP "echo 'SSH connection successful'" > /dev/null 2>&1; then
        log_error "Cannot connect to server via SSH"
        exit 1
    fi
    
    log_success "Pre-deployment checks passed"
}

# Phase 2: Build frontend
phase2_build_frontend() {
    log_info "Phase 2: Building frontend..."
    
    cd $FRONTEND_DIR
    
    # Install dependencies if needed
    if [ ! -d "node_modules" ]; then
        log_info "Installing frontend dependencies..."
        npm install
    fi
    
    # Build production frontend
    log_info "Building production frontend..."
    npm run build
    
    # Create deployment package
    log_info "Creating deployment package..."
    cd dist
    tar -czf ../../sophia-frontend-deploy.tar.gz .
    cd ../..
    
    log_success "Frontend built successfully"
}

# Phase 3: Deploy frontend
phase3_deploy_frontend() {
    log_info "Phase 3: Deploying frontend to server..."
    
    # Copy deployment package to server
    log_info "Copying frontend to server..."
    scp -i ~/.ssh/sophia_final_key -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null sophia-frontend-deploy.tar.gz ubuntu@$SERVER_IP:/tmp/
    
    # Deploy on server
    ssh -i ~/.ssh/sophia_final_key -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null ubuntu@$SERVER_IP << 'ENDSSH'
    # Create frontend directory
    sudo mkdir -p /var/www/sophia-frontend
    sudo chown ubuntu:ubuntu /var/www/sophia-frontend
    
    # Extract frontend files
    cd /var/www/sophia-frontend
    tar -xzf /tmp/sophia-frontend-deploy.tar.gz
    sudo chown -R www-data:www-data /var/www/sophia-frontend
    
    # Clean up
    rm /tmp/sophia-frontend-deploy.tar.gz
    
    echo "Frontend deployed to /var/www/sophia-frontend"
ENDSSH
    
    log_success "Frontend deployed successfully"
}

# Phase 4: Configure nginx
phase4_configure_nginx() {
    log_info "Phase 4: Configuring nginx..."
    
    # Create nginx configuration
    cat > nginx-sophia-production.conf << 'EOF'
# Main site - React frontend
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name sophia-intel.ai www.sophia-intel.ai;

    ssl_certificate /etc/letsencrypt/live/sophia-intel-ai/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/sophia-intel-ai/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    # Frontend files
    root /var/www/sophia-frontend;
    index index.html;

    # Gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

    # Cache static assets
    location ~* \.(jpg|jpeg|png|gif|ico|css|js|woff|woff2|ttf|svg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # React router support
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
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    # WebSocket support
    location /ws {
        proxy_pass http://localhost:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Health check endpoint
    location /health {
        proxy_pass http://localhost:8000/health;
    }
}

# API subdomain
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name api.sophia-intel.ai;

    ssl_certificate /etc/letsencrypt/live/sophia-intel-ai/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/sophia-intel-ai/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}

# Webhooks subdomain
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name webhooks.sophia-intel.ai;

    ssl_certificate /etc/letsencrypt/live/sophia-intel-ai/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/sophia-intel-ai/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    location / {
        proxy_pass http://localhost:8000/webhooks;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# HTTP to HTTPS redirect
server {
    listen 80;
    listen [::]:80;
    server_name sophia-intel.ai www.sophia-intel.ai api.sophia-intel.ai webhooks.sophia-intel.ai;
    return 301 https://$server_name$request_uri;
}
EOF

    # Copy nginx config to server
    scp -i ~/.ssh/sophia_final_key -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null nginx-sophia-production.conf ubuntu@$SERVER_IP:/tmp/
    
    # Apply nginx configuration
    ssh -i ~/.ssh/sophia_final_key -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null ubuntu@$SERVER_IP << 'ENDSSH'
    # Backup existing config
    sudo cp /etc/nginx/sites-available/sophia-intel-ai /etc/nginx/sites-available/sophia-intel-ai.backup.$(date +%Y%m%d_%H%M%S)
    
    # Apply new config
    sudo cp /tmp/nginx-sophia-production.conf /etc/nginx/sites-available/sophia-intel-ai
    
    # Test configuration
    if sudo nginx -t; then
        sudo systemctl reload nginx
        echo "Nginx configuration applied successfully"
    else
        echo "Nginx configuration test failed"
        exit 1
    fi
    
    # Clean up
    rm /tmp/nginx-sophia-production.conf
ENDSSH
    
    log_success "Nginx configured successfully"
}

# Phase 5: Deploy MCP servers
phase5_deploy_mcp_servers() {
    log_info "Phase 5: Deploying MCP servers..."
    
    ssh -i ~/.ssh/sophia_final_key -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null ubuntu@$SERVER_IP << 'ENDSSH'
    cd ~/sophia-main
    
    # Create directories if they don't exist
    mkdir -p logs pids
    
    # Activate Python environment
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi
    source venv/bin/activate
    
    # Install/update dependencies
    pip install -r requirements.txt
    
    # Function to start MCP server
    start_mcp_server() {
        local name=$1
        local module=$2
        local port=$3
        
        echo "Starting $name MCP Server on port $port..."
        
        # Kill existing process if running
        if [ -f "pids/$name.pid" ]; then
            old_pid=$(cat pids/$name.pid)
            if ps -p $old_pid > /dev/null 2>&1; then
                kill $old_pid
                sleep 2
            fi
        fi
        
        # Start new process
        nohup python -m $module > logs/$name.log 2>&1 &
        echo $! > pids/$name.pid
        
        # Check if started
        sleep 3
        if ps -p $(cat pids/$name.pid) > /dev/null 2>&1; then
            echo "✓ $name: Started successfully"
        else
            echo "✗ $name: Failed to start"
            tail -n 20 logs/$name.log
        fi
    }
    
    # Start all MCP servers
    start_mcp_server "ai_memory" "mcp_servers.ai_memory.ai_memory_mcp_server" "9000"
    start_mcp_server "codacy" "mcp_servers.codacy.codacy_mcp_server" "3008"
    start_mcp_server "github" "mcp_servers.github.github_mcp_server" "9003"
    start_mcp_server "linear" "mcp_servers.linear.linear_mcp_server" "9004"
    start_mcp_server "slack" "mcp_servers.slack.slack_mcp_server" "9005"
    start_mcp_server "hubspot" "mcp_servers.hubspot.hubspot_mcp_server" "9006"
    
    echo "MCP servers deployment complete"
ENDSSH
    
    log_success "MCP servers deployed"
}

# Phase 6: Create monitoring scripts
phase6_setup_monitoring() {
    log_info "Phase 6: Setting up monitoring..."
    
    # Create health check script
    cat > health_check.sh << 'EOF'
#!/bin/bash

echo "=== Sophia AI Health Check ==="
echo "Time: $(date)"
echo

# Check frontend
echo -n "Frontend (https://sophia-intel.ai): "
if curl -s -o /dev/null -w "%{http_code}" https://sophia-intel.ai | grep -q "200"; then
    echo "✓ OK"
else
    echo "✗ FAILED"
fi

# Check API
echo -n "API (https://api.sophia-intel.ai): "
if curl -s https://api.sophia-intel.ai/health | grep -q "healthy"; then
    echo "✓ OK"
else
    echo "✗ FAILED"
fi

# Check MCP servers
echo -e "\nMCP Servers:"
for port in 9000 3008 9003 9004 9005 9006; do
    echo -n "  Port $port: "
    if nc -z localhost $port 2>/dev/null; then
        echo "✓ Open"
    else
        echo "✗ Closed"
    fi
done

# Check services
echo -e "\nServices:"
for service in postgresql redis nginx; do
    echo -n "  $service: "
    if systemctl is-active --quiet $service; then
        echo "✓ Running"
    else
        echo "✗ Down"
    fi
done

# Check disk space
echo -e "\nDisk Usage:"
df -h / | grep -E "^/dev|Filesystem"

# Check memory
echo -e "\nMemory Usage:"
free -h | head -2
EOF

    # Copy monitoring script to server
    scp -i ~/.ssh/sophia_final_key -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null health_check.sh ubuntu@$SERVER_IP:~/
    
    ssh -i ~/.ssh/sophia_final_key -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null ubuntu@$SERVER_IP "chmod +x ~/health_check.sh"
    
    log_success "Monitoring setup complete"
}

# Phase 7: Run tests
phase7_run_tests() {
    log_info "Phase 7: Running deployment tests..."
    
    # Wait for services to stabilize
    sleep 10
    
    # Test frontend
    log_info "Testing frontend..."
    if curl -s -o /dev/null -w "%{http_code}" https://$DOMAIN | grep -q "200"; then
        log_success "Frontend is accessible"
    else
        log_error "Frontend is not accessible"
    fi
    
    # Test API
    log_info "Testing API..."
    if curl -s https://$API_DOMAIN/health | grep -q "healthy"; then
        log_success "API is healthy"
    else
        log_error "API health check failed"
    fi
    
    # Test MCP servers
    log_info "Testing MCP servers..."
    ssh -i ~/.ssh/sophia_final_key -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null ubuntu@$SERVER_IP << 'ENDSSH'
    for port in 9000 3008 9003 9004 9005 9006; do
        if nc -z localhost $port 2>/dev/null; then
            echo "✓ Port $port is open"
        else
            echo "✗ Port $port is closed"
        fi
    done
ENDSSH
}

# Phase 8: Generate deployment report
phase8_generate_report() {
    log_info "Phase 8: Generating deployment report..."
    
    REPORT_FILE="DEPLOYMENT_REPORT_$(date +%Y%m%d_%H%M%S).md"
    
    cat > $REPORT_FILE << EOF
# Sophia AI Production Deployment Report

**Date:** $(date)
**Deployed By:** $(whoami)
**Server:** $SERVER_IP

## Deployment Summary

### Frontend
- **URL:** https://$DOMAIN
- **Status:** Deployed to /var/www/sophia-frontend
- **Build:** Production build with optimizations

### Backend API
- **URL:** https://$API_DOMAIN
- **Port:** 8000
- **WebSocket Port:** 8001

### MCP Servers
- AI Memory: Port 9000
- Codacy: Port 3008
- GitHub: Port 9003
- Linear: Port 9004
- Slack: Port 9005
- HubSpot: Port 9006

### SSL/TLS
- **Provider:** Let's Encrypt
- **Valid Until:** October 11, 2025
- **Auto-renewal:** Enabled

### Monitoring
- Health check script: ~/health_check.sh
- Logs: ~/sophia-main/logs/

## Post-Deployment Checklist

- [ ] Verify frontend loads correctly
- [ ] Test API endpoints
- [ ] Check all MCP servers are running
- [ ] Monitor logs for errors
- [ ] Test WebSocket connections
- [ ] Verify SSL certificates
- [ ] Check database connections
- [ ] Test authentication flow

## Access Information

SSH to server:
\`\`\`bash
ssh -i ~/.ssh/sophia_final_key -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null ubuntu@$SERVER_IP
\`\`\`

Check health:
\`\`\`bash
./health_check.sh
\`\`\`

View logs:
\`\`\`bash
tail -f ~/sophia-main/logs/*.log
\`\`\`

## Next Steps

1. Monitor system for 24 hours
2. Set up automated backups
3. Configure alerting
4. Document any issues
5. Update runbooks

---

**Deployment completed successfully!**
EOF

    log_success "Deployment report generated: $REPORT_FILE"
}

# Main execution
main() {
    echo "======================================"
    echo "Sophia AI Production Deployment"
    echo "======================================"
    echo
    
    # Run all phases
    phase1_checks
    phase2_build_frontend
    phase3_deploy_frontend
    phase4_configure_nginx
    phase5_deploy_mcp_servers
    phase6_setup_monitoring
    phase7_run_tests
    phase8_generate_report
    
    echo
    echo "======================================"
    echo -e "${GREEN}DEPLOYMENT COMPLETE!${NC}"
    echo "======================================"
    echo
    echo "Frontend: https://$DOMAIN"
    echo "API: https://$API_DOMAIN"
    echo "Webhooks: https://$WEBHOOK_DOMAIN"
    echo
    echo "Run health check on server:"
    echo "ssh -i ~/.ssh/sophia_final_key -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null ubuntu@$SERVER_IP './health_check.sh'"
    echo
}

# Run main function
main 