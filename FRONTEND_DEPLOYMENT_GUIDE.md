# Sophia AI Frontend Deployment Guide

## Current Status

The Sophia AI backend is successfully deployed and running at:
- **API:** https://api.sophia-intel.ai (✅ Working)
- **Backend Health:** `{"status":"healthy","environment":"lambda-labs-production"}`

However, the main domain (https://sophia-intel.ai) is currently showing the backend JSON response instead of the frontend application.

## Quick Fix Instructions

To deploy the React frontend to your server, follow these steps:

### Option 1: Quick Manual Deployment

1. **SSH into your server:**
```bash
ssh -i ~/.ssh/sophia2025.pem ubuntu@192.222.58.232
```

2. **Create frontend directory:**
```bash
sudo mkdir -p /var/www/sophia-frontend
sudo chown ubuntu:ubuntu /var/www/sophia-frontend
```

3. **On your local machine, create a deployment package:**
```bash
cd frontend
npm run build
cd dist
tar -czf ../../frontend-deploy.tar.gz .
cd ../..
```

4. **Copy the package to server:**
```bash
scp -i ~/.ssh/sophia2025.pem frontend-deploy.tar.gz ubuntu@192.222.58.232:/tmp/
```

5. **On the server, extract the files:**
```bash
cd /var/www/sophia-frontend
tar -xzf /tmp/frontend-deploy.tar.gz
sudo chown -R www-data:www-data /var/www/sophia-frontend
```

6. **Update nginx configuration:**
```bash
sudo nano /etc/nginx/sites-available/sophia-intel-ai
```

Replace the content with:
```nginx
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
    }

    # API proxy
    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
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
        proxy_cache_bypass $http_upgrade;
    }
}

# HTTP to HTTPS redirect
server {
    listen 80;
    listen [::]:80;
    server_name sophia-intel.ai www.sophia-intel.ai api.sophia-intel.ai webhooks.sophia-intel.ai;
    return 301 https://$server_name$request_uri;
}
```

7. **Test and reload nginx:**
```bash
sudo nginx -t
sudo systemctl reload nginx
```

### Option 2: Using Static Files from Backend

If you prefer to serve the frontend from the backend's static directory:

1. **Copy frontend files to backend static directory:**
```bash
# On server
cd ~/sophia-main/static
rm -rf *
# Copy the built frontend files here
```

2. **Update the backend to serve static files:**
The backend at port 8000 needs to be configured to serve static files from the `/` route instead of returning JSON.

### Option 3: Deploy to Vercel (Recommended for Production)

For a production-grade deployment with CDN and automatic scaling:

1. **Install Vercel CLI:**
```bash
npm i -g vercel
```

2. **Deploy frontend:**
```bash
cd frontend
vercel --prod
```

3. **Update DNS:**
Point sophia-intel.ai to Vercel's servers while keeping api.sophia-intel.ai pointing to Lambda Labs.

## What You'll See When It Works

Once properly deployed, visiting https://sophia-intel.ai will show:
- **Sophia AI Production** header
- Navigation with "Executive Chat" and "Memory Dashboard"
- Interactive chat interface
- Real-time metrics and visualizations

## Current Frontend Features

The deployed frontend includes:
1. **Executive Chat Dashboard** - AI-powered chat with multiple personality modes
2. **Unified Dashboard** - Business metrics, revenue charts, and X trends
3. **WebSocket Support** - Real-time updates
4. **Responsive Design** - Works on all devices

## Troubleshooting

### If nginx won't reload:
```bash
sudo nginx -t  # Check for errors
sudo journalctl -u nginx -n 50  # View logs
```

### If frontend shows blank page:
- Check browser console for errors
- Ensure all files were copied correctly
- Verify file permissions

### If API calls fail:
- Check that `/api` proxy is working
- Verify backend is running on port 8000
- Check CORS settings

## Next Steps

After deployment:
1. Test all features at https://sophia-intel.ai
2. Monitor nginx logs: `sudo tail -f /var/log/nginx/access.log`
3. Set up monitoring and alerts
4. Configure CDN for better performance

---

**Note:** The automated deployment script (`scripts/deploy_frontend_production.sh`) is available but requires SSH access to work properly. 