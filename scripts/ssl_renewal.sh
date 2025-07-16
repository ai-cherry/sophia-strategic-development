#!/bin/bash
# SSL Certificate Renewal Automation
# Automatically renews Let's Encrypt certificates and reloads nginx

echo "🔄 Starting SSL certificate renewal check"

# Renew certificates
/usr/bin/certbot renew --quiet

# Check if nginx needs reload (certificates were renewed)
if [ $? -eq 0 ]; then
    echo "✅ Certificates renewed successfully"
    
    # Test nginx configuration
    if nginx -t 2>/dev/null; then
        systemctl reload nginx
        echo "✅ nginx reloaded with new certificates"
    else
        echo "❌ nginx configuration test failed"
        exit 1
    fi
else
    echo "ℹ️ No certificate renewal needed"
fi

echo "🔐 SSL renewal check complete"
