#!/bin/bash
set -e

echo "🔒 Setting up SSL certificates with Let's Encrypt"

# Install certbot
sudo apt update
sudo apt install -y certbot python3-certbot-nginx

# Get certificates for all domains
sudo certbot --nginx -d sophia-intel.ai -d api.sophia-intel.ai -d app.sophia-intel.ai --agree-tos --no-eff-email --email admin@sophia-intel.ai

# Setup auto-renewal
sudo crontab -l | { cat; echo "0 12 * * * /usr/bin/certbot renew --quiet"; } | sudo crontab -

echo "✅ SSL certificates configured!"
echo "🔒 Auto-renewal setup complete"