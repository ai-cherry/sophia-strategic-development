#!/bin/bash
# Deploy Let's Encrypt SSL Certificates for Sophia AI
# Run this script on the primary instance (sophia-ai-core)

set -e

echo "🔐 Deploying Let's Encrypt SSL certificates for Sophia AI"

# Install certbot if not present
if ! command -v certbot &> /dev/null; then
    echo "Installing certbot..."
    sudo apt update
    sudo apt install -y certbot python3-certbot-nginx
fi

# Stop nginx temporarily
sudo systemctl stop nginx

# Obtain certificates for domain
sudo certbot certonly --standalone -d sophia-ai.com -d api.sophia-ai.com --email admin@sophia-ai.com --agree-tos --no-eff-email

# Start nginx
sudo systemctl start nginx

# Update nginx configuration with new certificates
sudo sed -i 's|/etc/ssl/certs/sophia-ai.crt|/etc/letsencrypt/live/sophia-ai.com/fullchain.pem|g' /etc/nginx/sites-available/sophia-mcp
sudo sed -i 's|/etc/ssl/private/sophia-ai.key|/etc/letsencrypt/live/sophia-ai.com/privkey.pem|g' /etc/nginx/sites-available/sophia-mcp

# Test nginx configuration
sudo nginx -t

# Reload nginx
sudo systemctl reload nginx

# Setup automatic renewal
echo "0 12 * * * /usr/bin/certbot renew --quiet" | sudo crontab -

echo "✅ SSL certificates deployed successfully"
echo "   Certificates: /etc/letsencrypt/live/sophia-ai.com/"
echo "   Auto-renewal: Configured via cron"
