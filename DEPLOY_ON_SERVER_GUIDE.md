# 🚀 Sophia AI Server Deployment Guide

You're now SSH'd into the production server (104.171.202.103). Follow these steps:

## Step 1: Clone/Update the Repository

```bash
# Check if sophia-main exists
if [ -d "sophia-main" ]; then
    cd sophia-main
    git pull origin main
else
    git clone https://github.com/ai-cherry/sophia-main.git
    cd sophia-main
fi
```

## Step 2: Start Core Services

```bash
# Create data directories
mkdir -p ~/sophia-data/{postgres,redis,weaviate}

# Start PostgreSQL
docker run -d \
  --name sophia-postgres \
  -e POSTGRES_USER=sophia \
  -e POSTGRES_PASSWORD=sophia2025 \
  -e POSTGRES_DB=sophia_ai \
  -p 5432:5432 \
  -v ~/sophia-data/postgres:/var/lib/postgresql/data \
  postgres:15-alpine

# Start Redis
docker run -d \
  --name sophia-redis \
  -p 6379:6379 \
  -v ~/sophia-data/redis:/data \
  redis:7-alpine

# Start Weaviate
docker run -d \
  --name sophia-weaviate \
  -p 8080:8080 \
  -e AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED=true \
  -e PERSISTENCE_DATA_PATH=/var/lib/weaviate \
  -e DEFAULT_VECTORIZER_MODULE=text2vec-transformers \
  -e ENABLE_MODULES=text2vec-transformers \
  -e TRANSFORMERS_INFERENCE_API=http://t2v-transformers:8080 \
  -v ~/sophia-data/weaviate:/var/lib/weaviate \
  semitechnologies/weaviate:1.25.4

# Start transformer model for Weaviate
docker run -d \
  --name sophia-t2v-transformers \
  -e ENABLE_CUDA=0 \
  semitechnologies/transformers-inference:sentence-transformers-multi-qa-MiniLM-L6-cos-v1

# Check all services
docker ps
```

## Step 3: Initialize Weaviate Schema

```bash
# Install Python dependencies (if needed)
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install weaviate-client redis psycopg2-binary

# Initialize Weaviate schema
python scripts/init_weaviate_schema.py
```

## Step 4: Deploy Backend

```bash
# Create .env file
cat > .env << 'EOF'
ENVIRONMENT=prod
API_HOST=0.0.0.0
API_PORT=8000
DATABASE_URL=postgresql://sophia:sophia2025@localhost:5432/sophia_ai
REDIS_URL=redis://localhost:6379
WEAVIATE_URL=http://localhost:8080
OPENAI_API_KEY=${OPENAI_API_KEY}
ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
GONG_API_KEY=${GONG_API_KEY}
EOF

# Install backend dependencies
pip install -r requirements.txt

# Start the backend (in screen or tmux)
screen -S sophia-backend
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

# Detach from screen: Ctrl+A, then D
```

## Step 5: Set up Nginx (Optional)

```bash
# Install nginx
sudo apt-get install -y nginx

# Configure nginx
sudo tee /etc/nginx/sites-available/sophia-ai << 'EOF'
server {
    listen 80;
    server_name sophia-intel.ai;

    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
EOF

# Enable the site
sudo ln -s /etc/nginx/sites-available/sophia-ai /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## Step 6: Verify Deployment

```bash
# Check backend health
curl http://localhost:8000/health

# Check from outside (from your local machine)
curl http://104.171.202.103:8000/health

# Check logs
screen -r sophia-backend
```

## Useful Commands

```bash
# View logs
docker logs sophia-postgres
docker logs sophia-redis
docker logs sophia-weaviate

# Restart services
docker restart sophia-postgres sophia-redis sophia-weaviate

# Stop all services
docker stop sophia-postgres sophia-redis sophia-weaviate sophia-t2v-transformers

# Remove containers (careful!)
docker rm sophia-postgres sophia-redis sophia-weaviate sophia-t2v-transformers
```

## Troubleshooting

1. **Port already in use**: Check with `sudo lsof -i :8000`
2. **Docker permission denied**: Run `sudo usermod -aG docker $USER` and logout/login
3. **Module not found**: Make sure you're in the virtual environment
4. **Connection refused**: Check firewall with `sudo ufw status` 