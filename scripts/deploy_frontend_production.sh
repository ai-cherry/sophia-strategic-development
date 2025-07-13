#!/bin/bash

# Sophia AI Frontend Production Deployment Script
# This script deploys the frontend and configures nginx to serve it properly

set -e

echo "=== Sophia AI Frontend Production Deployment ==="
echo "Date: $(date)"
echo ""

# Configuration
SERVER_IP="192.222.58.232"
SSH_KEY="$HOME/.ssh/sophia2025.pem"
REMOTE_USER="ubuntu"

# Check if SSH key exists
if [ ! -f "$SSH_KEY" ]; then
    echo "❌ Error: SSH key not found at $SSH_KEY"
    exit 1
fi

echo "1. Building frontend..."
cd frontend
npm run build
cd ..

echo -e "\n2. Creating deployment package..."
cd frontend/dist
tar -czf ../../frontend-deploy.tar.gz .
cd ../..

echo -e "\n3. Deploying to server..."
scp -i "$SSH_KEY" frontend-deploy.tar.gz "$REMOTE_USER@$SERVER_IP:/tmp/"

echo -e "\n4. Extracting on server..."
ssh -i "$SSH_KEY" "$REMOTE_USER@$SERVER_IP" << 'EOF'
    # Create frontend directory
    sudo mkdir -p /var/www/sophia-frontend
    sudo chown ubuntu:ubuntu /var/www/sophia-frontend
    
    # Extract frontend files
    cd /var/www/sophia-frontend
    tar -xzf /tmp/frontend-deploy.tar.gz
    
    # Set permissions
    sudo chown -R www-data:www-data /var/www/sophia-frontend
    
    echo "Frontend files deployed to /var/www/sophia-frontend"
EOF

echo -e "\n5. Creating nginx configuration..."
cat > nginx-sophia-frontend.conf << 'NGINX_CONFIG'
# Main site - serves the React frontend
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name sophia-intel.ai www.sophia-intel.ai;

    ssl_certificate /etc/letsencrypt/live/sophia-intel-ai/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/sophia-intel-ai/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    # Frontend root
    root /var/www/sophia-frontend;
    index index.html;

    # Serve frontend files
    location / {
        try_files $uri $uri/ /index.html;
        add_header Cache-Control "no-cache, no-store, must-revalidate";
        add_header Pragma "no-cache";
        add_header Expires "0";
    }

    # API proxy
    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Health check
    location /health {
        proxy_pass http://localhost:8000/health;
    }

    # WebSocket support
    location /ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# API subdomain - proxies to backend
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
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
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
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
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
NGINX_CONFIG

echo -e "\n6. Deploying nginx configuration..."
scp -i "$SSH_KEY" nginx-sophia-frontend.conf "$REMOTE_USER@$SERVER_IP:/tmp/"

ssh -i "$SSH_KEY" "$REMOTE_USER@$SERVER_IP" << 'EOF'
    # Backup current config
    sudo cp /etc/nginx/sites-available/sophia-intel-ai /etc/nginx/sites-available/sophia-intel-ai.backup
    
    # Install new config
    sudo cp /tmp/nginx-sophia-frontend.conf /etc/nginx/sites-available/sophia-intel-ai
    
    # Test nginx configuration
    if sudo nginx -t; then
        echo "✅ Nginx configuration is valid"
        sudo systemctl reload nginx
        echo "✅ Nginx reloaded successfully"
    else
        echo "❌ Nginx configuration error, reverting..."
        sudo cp /etc/nginx/sites-available/sophia-intel-ai.backup /etc/nginx/sites-available/sophia-intel-ai
        exit 1
    fi
EOF

echo -e "\n7. Cleaning up..."
rm -f frontend-deploy.tar.gz
rm -f nginx-sophia-frontend.conf

echo -e "\n✅ Frontend deployment complete!"
echo ""
echo "Access URLs:"
echo "  Main Site: https://sophia-intel.ai"
echo "  WWW: https://www.sophia-intel.ai"
echo "  API: https://api.sophia-intel.ai"
echo "  API Docs: https://api.sophia-intel.ai/docs"
echo ""
echo "To monitor:"
echo "  ssh -i $SSH_KEY $REMOTE_USER@$SERVER_IP 'sudo tail -f /var/log/nginx/access.log'"
echo "" 