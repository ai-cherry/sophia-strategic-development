# SOPHIA AI REAL DEPLOYMENT STATUS
**Date:** December 2024  
**Server IP:** 104.171.202.103 (sophia-production-instance)  
**Domain:** sophia-intel.ai

## 🔴 CURRENT REALITY

### What's Actually Deployed:
- ✅ **Backend API**: Running at https://api.sophia-intel.ai
- ✅ **SSL Certificates**: Valid until October 2025
- ❌ **Frontend**: NOT deployed (showing backend JSON instead)
- ❌ **Docker Services**: NOT running (PostgreSQL, Redis, Qdrant)
- ❌ **MCP Servers**: NOT running
- ✅ **DNS**: Correctly pointing to 192.222.58.232

### The Problem:
When you visit https://sophia-intel.ai, you see:
```json
{"status":"healthy","environment":"lambda-labs-production"}
```

This is because:
1. Nginx is serving the backend API on the main domain
2. No frontend files exist in `/var/www/sophia-frontend`
3. Backend is running but without required services (databases)

## 🚀 DEPLOYMENT COMMANDS

### Option 1: Full Automated Deployment (Recommended)
```bash
# Make the script executable
chmod +x scripts/deploy_sophia_production_real.sh

# Run the deployment
./scripts/deploy_sophia_production_real.sh
```

This script will:
1. ✅ Install Docker services (PostgreSQL, Redis, Qdrant)
2. ✅ Deploy the backend with proper configuration
3. ✅ Build and deploy the frontend
4. ✅ Configure nginx correctly
5. ✅ Start MCP servers
6. ✅ Verify everything is working

### Option 2: Verify Current Status First
```bash
# Make the script executable
chmod +x scripts/verify_and_fix_deployment.py

# Run verification
python scripts/verify_and_fix_deployment.py
```

This will show you exactly what's broken and how to fix it.

## 📋 MANUAL DEPLOYMENT STEPS

If you prefer to do it manually or the scripts fail:

### 1. SSH to Server
```bash
ssh -i ~/.ssh/sophia_correct_key ubuntu@192.222.58.232
```

### 2. Install Required Services
```bash
# On the server
cd ~
mkdir -p sophia-deployment sophia-logs sophia-data/{postgres,redis,Qdrant}

# Create docker-compose.yml
cat > sophia-deployment/docker-compose.yml << 'EOF'
version: '3.8'
services:
  postgres:
    image: postgres:15-alpine
    container_name: sophia-postgres
    environment:
      POSTGRES_USER: sophia
      POSTGRES_PASSWORD: sophia2025
      POSTGRES_DB: sophia_ai
    ports:
      - "5432:5432"
    volumes:
      - ~/sophia-data/postgres:/var/lib/postgresql/data
    restart: always

  redis:
    image: redis:7-alpine
    container_name: sophia-redis
    ports:
      - "6379:6379"
    volumes:
      - ~/sophia-data/redis:/data
    restart: always

  Qdrant:
    image: semitechnologies/Qdrant:1.25.4
    container_name: sophia-Qdrant
    ports:
      - "8080:8080"
    environment:
      PERSISTENCE_DATA_PATH: /var/lib/Qdrant
      DEFAULT_VECTORIZER_MODULE: text2vec-transformers
      ENABLE_MODULES: text2vec-transformers
    volumes:
      - ~/sophia-data/Qdrant:/var/lib/Qdrant
    restart: always
EOF

# Start services
cd sophia-deployment
docker-compose up -d
```

### 3. Deploy Frontend (from your local machine)
```bash
# Build frontend
cd frontend
npm install
npm run build

# Create package
cd dist
tar -czf ../../sophia-frontend.tar.gz .
cd ../..

# Copy to server
scp -i ~/.ssh/sophia_correct_key sophia-frontend.tar.gz ubuntu@192.222.58.232:~/
```

### 4. Install Frontend on Server
```bash
# On the server
sudo mkdir -p /var/www/sophia-frontend
cd /var/www/sophia-frontend
sudo tar -xzf ~/sophia-frontend.tar.gz
sudo chown -R www-data:www-data /var/www/sophia-frontend
```

### 5. Fix Nginx Configuration
```bash
# On the server
sudo nano /etc/nginx/sites-available/sophia-intel-ai
```

Make sure the main server block has:
```nginx
server {
    listen 443 ssl http2;
    server_name sophia-intel.ai www.sophia-intel.ai;
    
    # This is the key line - serve frontend files
    root /var/www/sophia-frontend;
    index index.html;
    
    # React router support
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    # API proxy
    location /api {
        proxy_pass http://localhost:8000;
        # ... proxy settings ...
    }
}
```

Then reload nginx:
```bash
sudo nginx -t && sudo systemctl reload nginx
```

## ✅ SUCCESS CRITERIA

When properly deployed, you should see:

1. **https://sophia-intel.ai** → React frontend with Sophia AI interface
2. **https://api.sophia-intel.ai** → `{"status":"healthy"}`
3. **https://api.sophia-intel.ai/docs** → FastAPI documentation

## 🔍 TROUBLESHOOTING

### If Frontend Shows Blank Page:
```bash
# Check browser console for errors
# Check nginx error log
sudo tail -f /var/log/nginx/error.log
```

### If API Calls Fail:
```bash
# Check backend is running
curl http://localhost:8000/health

# Check backend logs
tail -f ~/sophia-logs/backend.log
```

### If Database Errors:
```bash
# Check Docker services
docker ps
docker-compose logs postgres
```

## 📞 QUICK COMMANDS

```bash
# Check everything
curl https://sophia-intel.ai  # Should show HTML
curl https://api.sophia-intel.ai/health  # Should show {"status":"healthy"}

# View logs
ssh -i ~/.ssh/sophia_correct_key ubuntu@192.222.58.232 'tail -f ~/sophia-logs/*.log'

# Restart backend
ssh -i ~/.ssh/sophia_correct_key ubuntu@192.222.58.232 'pkill -f uvicorn; cd ~/sophia-main && nohup python -m api.main > ~/sophia-logs/backend.log 2>&1 &'
```

## 🎯 THE BOTTOM LINE

You have a working backend but no frontend deployed. The automated script will fix everything in about 10-15 minutes. Just run:

```bash
./scripts/deploy_sophia_production_real.sh
```

And you'll finally have a live deployment at https://sophia-intel.ai! 