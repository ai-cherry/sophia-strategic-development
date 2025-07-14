# 🚨 IMMEDIATE ACTION REQUIRED - Sophia AI Frontend Deployment

## Current Situation
- ✅ **Backend API**: Fully operational at https://api.sophia-intel.ai
- ✅ **SSL**: Active and working
- ✅ **DNS**: Correctly configured
- ❌ **Frontend**: NOT deployed - main site showing backend JSON
- ❌ **MCP Servers**: Status unknown

## To Complete Deployment NOW

### Step 1: SSH to Server
```bash
ssh -i ~/.ssh/sophia2025.pem ubuntu@192.222.58.232
```

### Step 2: Deploy Frontend (ON THE SERVER)
```bash
# Clean the directory
sudo rm -rf /var/www/sophia-frontend/*

# Extract the frontend (already uploaded)
cd /var/www/sophia-frontend
sudo tar -xzf /tmp/sophia-frontend-deploy.tar.gz

# Fix permissions
sudo chown -R www-data:www-data /var/www/sophia-frontend

# Verify files are there
ls -la
# Should see: index.html, assets folder, etc.
```

### Step 3: Fix Nginx Configuration (ON THE SERVER)
```bash
# Edit nginx config
sudo nano /etc/nginx/sites-available/sophia-intel-ai
```

Make sure the main server block has:
```nginx
server {
    listen 443 ssl http2;
    server_name sophia-intel.ai www.sophia-intel.ai;
    
    # THIS IS THE KEY LINE - MUST POINT TO FRONTEND
    root /var/www/sophia-frontend;
    index index.html;
    
    # React router support
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    # API proxy
    location /api {
        proxy_pass http://localhost:8000;
        # ... rest of proxy config
    }
}
```

### Step 4: Apply Changes
```bash
# Test nginx config
sudo nginx -t

# If successful, reload
sudo systemctl reload nginx
```

### Step 5: Verify It Works
```bash
# Should return HTML, not JSON
curl https://sophia-intel.ai | head -5

# Should see something like:
# <!DOCTYPE html>
# <html lang="en">
# ...
```

## Expected Result

After these steps, visiting https://sophia-intel.ai should show:
- The Sophia AI React application
- NOT the JSON message `{"message":"Sophia AI Backend is running on Lambda Labs!"}`

## If It's Still Not Working

1. Check nginx error log:
   ```bash
   sudo tail -f /var/log/nginx/error.log
   ```

2. Verify frontend files exist:
   ```bash
   ls -la /var/www/sophia-frontend/
   ```

3. Check nginx is using the right config:
   ```bash
   sudo nginx -T | grep -A 10 "sophia-intel.ai"
   ```

## Time Required
- **5-10 minutes** to complete all steps
- The frontend files are already on the server in `/tmp/sophia-frontend-deploy.tar.gz`
- Just need to extract them to the right place and update nginx

---

**ACTION**: SSH to the server NOW and run the commands above to complete the deployment! 