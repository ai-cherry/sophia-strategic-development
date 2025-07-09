#!/bin/bash
# Deploy Sophia AI on Lambda Labs instance

set -e

echo "🚀 Deploying Sophia AI on Lambda Labs"

# Load Docker images
echo "Loading Docker images..."
gunzip -c sophia-backend.tar.gz | docker load
gunzip -c sophia-frontend.tar.gz | docker load

# Create deployment directory
mkdir -p ~/sophia-deployment

# Create docker-compose.yml
cat > ~/sophia-deployment/docker-compose.yml << 'EOF'
version: '3.8'

services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: sophia
      POSTGRES_USER: sophia
      POSTGRES_PASSWORD: sophia_secure_password_2025
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: always

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes --maxmemory 512mb --maxmemory-policy allkeys-lru
    volumes:
      - redis_data:/data
    restart: always

  backend:
    image: scoobyjava15/sophia-backend:latest
    environment:
      DATABASE_URL: postgresql://sophia:sophia_secure_password_2025@postgres:5432/sophia
      REDIS_URL: redis://redis:6379
      ENVIRONMENT: prod
      PULUMI_ORG: scoobyjava-org
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis
    restart: always
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    image: scoobyjava15/sophia-frontend:latest
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - backend
    restart: always

  nginx:
    image: nginx:alpine
    ports:
      - "8080:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - backend
      - frontend
    restart: always

volumes:
  postgres_data:
  redis_data:
EOF

# Create nginx configuration
cat > ~/sophia-deployment/nginx.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:8000;
    }

    upstream frontend {
        server frontend:80;
    }

    server {
        listen 80;
        server_name _;

        location /api {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location / {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
EOF

# Stop any existing containers
echo "Stopping existing containers..."
cd ~/sophia-deployment
docker-compose down || true

# Start services
echo "Starting services..."
docker stack deploy

# Wait for services to be ready
echo "Waiting for services to start..."
sleep 30

# Check status
echo "Checking service status..."
docker-compose ps

echo "✅ Deployment complete!"
echo "Access the application at:"
echo "Frontend: http://$(hostname -I | awk '{print $1}')"
echo "Backend API: http://$(hostname -I | awk '{print $1}'):8000"
echo "API Docs: http://$(hostname -I | awk '{print $1}'):8000/docs" 