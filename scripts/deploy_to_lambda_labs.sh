#!/bin/bash
# Deploy Sophia AI to Lambda Labs

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SSH_KEY="${SSH_KEY:-~/.ssh/sophia2025.pem}"
PRODUCTION_IP="104.171.202.103"
DOCKER_REGISTRY="${DOCKER_REGISTRY:-scoobyjava15}"

echo -e "${BLUE}🚀 Deploying Sophia AI to Lambda Labs${NC}"
echo -e "${BLUE}Target: ${PRODUCTION_IP}${NC}"

# Step 1: Save Docker images locally
echo -e "${YELLOW}Saving Docker images...${NC}"
docker save sophia-backend:latest -o /tmp/sophia-backend.tar
docker save sophia-frontend:latest -o /tmp/sophia-frontend.tar

# Step 2: Copy images to Lambda Labs
echo -e "${YELLOW}Copying images to Lambda Labs...${NC}"
scp -i ${SSH_KEY} /tmp/sophia-backend.tar ubuntu@${PRODUCTION_IP}:/tmp/
scp -i ${SSH_KEY} /tmp/sophia-frontend.tar ubuntu@${PRODUCTION_IP}:/tmp/

# Step 3: Load images on Lambda Labs
echo -e "${YELLOW}Loading images on Lambda Labs...${NC}"
ssh -i ${SSH_KEY} ubuntu@${PRODUCTION_IP} "docker load -i /tmp/sophia-backend.tar && docker load -i /tmp/sophia-frontend.tar"

# Step 4: Create necessary directories and files
echo -e "${YELLOW}Setting up deployment files...${NC}"
ssh -i ${SSH_KEY} ubuntu@${PRODUCTION_IP} "mkdir -p ~/sophia-deployment"

# Step 5: Create docker-compose file on the server
cat > /tmp/docker-compose.prod.yml << 'EOF'
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
    deploy:
      replicas: 1
      placement:
        constraints:
          - node.role == manager

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes --maxmemory 512mb --maxmemory-policy allkeys-lru
    volumes:
      - redis_data:/data
    deploy:
      replicas: 1

  backend:
    image: sophia-backend:latest
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
    deploy:
      replicas: 2
      update_config:
        parallelism: 1
        delay: 10s
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3

  frontend:
    image: sophia-frontend:latest
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - backend
    deploy:
      replicas: 2
      update_config:
        parallelism: 1
        delay: 10s

  nginx:
    image: nginx:alpine
    ports:
      - "8080:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    deploy:
      replicas: 1

volumes:
  postgres_data:
  redis_data:

networks:
  default:
    driver: overlay
    attachable: true
EOF

# Step 6: Copy docker-compose file
scp -i ${SSH_KEY} /tmp/docker-compose.prod.yml ubuntu@${PRODUCTION_IP}:~/sophia-deployment/

# Step 7: Create nginx config
cat > /tmp/nginx.conf << 'EOF'
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

scp -i ${SSH_KEY} /tmp/nginx.conf ubuntu@${PRODUCTION_IP}:~/sophia-deployment/

# Step 8: Deploy the stack
echo -e "${YELLOW}Deploying Docker Stack...${NC}"
ssh -i ${SSH_KEY} ubuntu@${PRODUCTION_IP} "cd ~/sophia-deployment && docker stack deploy -c docker-compose.prod.yml sophia"

# Step 9: Check deployment status
echo -e "${YELLOW}Checking deployment status...${NC}"
sleep 10
ssh -i ${SSH_KEY} ubuntu@${PRODUCTION_IP} "docker service ls && echo '' && docker stack ps sophia"

# Cleanup temp files
rm -f /tmp/sophia-backend.tar /tmp/sophia-frontend.tar /tmp/docker-compose.prod.yml /tmp/nginx.conf

echo -e "${GREEN}✅ Deployment initiated!${NC}"
echo -e "${GREEN}Access the application at: http://${PRODUCTION_IP}${NC}"
echo -e "${GREEN}API endpoint: http://${PRODUCTION_IP}:8000${NC}"
echo -e "${YELLOW}Note: It may take a few minutes for all services to be fully ready.${NC}"
