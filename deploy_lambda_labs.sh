#!/bin/bash
# Sophia AI Lambda Labs Deployment Script
# Unified deployment to Lambda Labs infrastructure

set -e

# Load configuration
source "$(dirname "$0")/lambda_labs_deployment.conf"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Test SSH connectivity
test_ssh_connectivity() {
    log_info "Testing SSH connectivity to Lambda Labs servers..."
    
    for server in PRIMARY MCP DATA PROD DEV; do
        server_ip_var="${server}_IP"
        server_name_var="${server}_NAME"
        
        ip="${!server_ip_var}"
        name="${!server_name_var}"
        
        log_info "Testing $name ($ip)..."
        
        if timeout 10 ssh -i "$SSH_KEY_PATH" $SSH_OPTIONS ubuntu@$ip "echo 'OK'" 2>/dev/null | grep -q "OK"; then
            log_success "✅ $name accessible"
        else
            log_warning "❌ $name not accessible"
        fi
    done
}

# Deploy frontend to primary server
deploy_frontend() {
    log_info "Deploying frontend to primary server..."
    
    # Build frontend
    cd frontend
    npm run build
    cd ..
    
    # Create deployment package
    cd frontend/dist
    tar -czf ../../frontend-deploy.tar.gz .
    cd ../..
    
    # Deploy to primary server
    scp -i "$SSH_KEY_PATH" $SSH_OPTIONS frontend-deploy.tar.gz ubuntu@$PRIMARY_IP:/tmp/
    
    ssh -i "$SSH_KEY_PATH" $SSH_OPTIONS ubuntu@$PRIMARY_IP "
        sudo mkdir -p /var/www/sophia-frontend
        sudo chown ubuntu:ubuntu /var/www/sophia-frontend
        cd /var/www/sophia-frontend
        tar -xzf /tmp/frontend-deploy.tar.gz
        sudo chown -R www-data:www-data /var/www/sophia-frontend
        
        # Configure Nginx
        sudo tee /etc/nginx/sites-available/sophia-ai << 'NGINX_EOF'
server {
    listen 80;
    server_name $PRIMARY_IP;
    
    location / {
        root /var/www/sophia-frontend;
        index index.html;
        try_files \$uri \$uri/ /index.html;
    }
    
    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    }
    
    location /health {
        proxy_pass http://localhost:8000/health;
    }
    
    location /chat {
        proxy_pass http://localhost:8000/chat;
    }
}
NGINX_EOF
        
        sudo ln -sf /etc/nginx/sites-available/sophia-ai /etc/nginx/sites-enabled/
        sudo rm -f /etc/nginx/sites-enabled/default
        sudo nginx -t && sudo systemctl reload nginx
    "
    
    log_success "Frontend deployed to http://$PRIMARY_IP"
}

# Deploy backend (already running)
deploy_backend() {
    log_info "Backend deployment verified..."
    
    # Test backend health
    if curl -s "http://$PRIMARY_IP:8000/health" | grep -q "healthy"; then
        log_success "Backend is healthy and running"
    else
        log_error "Backend is not responding"
        return 1
    fi
}

# Main deployment function
main() {
    log_info "Starting Sophia AI Lambda Labs deployment..."
    echo "======================================================"
    
    # Test connectivity
    test_ssh_connectivity
    
    # Deploy components
    deploy_backend
    deploy_frontend
    
    echo ""
    log_success "🎉 Deployment completed successfully!"
    log_info "Access your Sophia AI instance at:"
    log_info "  Frontend: http://$PRIMARY_IP"
    log_info "  API: http://$PRIMARY_IP:8000"
    log_info "  Health: http://$PRIMARY_IP:8000/health"
    
    # Test final deployment
    log_info "Testing final deployment..."
    if curl -s "http://$PRIMARY_IP" | grep -q "Sophia"; then
        log_success "✅ Frontend accessible"
    else
        log_warning "⚠️  Frontend may not be fully ready"
    fi
    
    if curl -s "http://$PRIMARY_IP:8000/health" | grep -q "healthy"; then
        log_success "✅ Backend healthy"
    else
        log_warning "⚠️  Backend health check failed"
    fi
}

# Run main function
main "$@"
