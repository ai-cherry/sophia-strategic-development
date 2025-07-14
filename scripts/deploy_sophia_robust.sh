#!/bin/bash

# SOPHIA AI ROBUST DEPLOYMENT
# Handles Docker conflicts and connection timeouts

set -e

# Configuration
SERVER_IP="104.171.202.103"
SSH_KEY="$HOME/.ssh/lambda_labs_private_key"
DOMAIN="sophia-intel.ai"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}======================================"
echo "   SOPHIA AI ROBUST DEPLOYMENT"
echo "   Handling Docker conflicts"
echo "======================================${NC}"

# SSH function with keepalive
ssh_exec() {
    ssh -i "$SSH_KEY" -o ServerAliveInterval=30 -o ServerAliveCountMax=10 ubuntu@$SERVER_IP "$@"
}

# Step 1: Fix Docker conflict
echo -e "\n${YELLOW}Step 1: Fixing Docker/containerd conflict...${NC}"
ssh_exec << 'EOF'
# Remove conflicting packages
sudo apt-get remove -y containerd docker docker-engine docker.io 2>/dev/null || true

# Clean up
sudo apt-get autoremove -y
sudo apt-get clean

# Install Docker properly
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# Install docker-compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

echo "Docker installation complete"
EOF

echo -e "${GREEN}✓ Docker conflict resolved${NC}"

# Step 2: Quick server check
echo -e "\n${YELLOW}Step 2: Checking server status...${NC}"
ssh_exec "docker --version && docker-compose --version && df -h /"

# Step 3: Create deployment structure
echo -e "\n${YELLOW}Step 3: Setting up deployment structure...${NC}"
ssh_exec << 'EOF'
mkdir -p ~/sophia-deployment/{backend,frontend,data,logs}
mkdir -p ~/sophia-data/{postgres,redis,weaviate}
EOF

# Step 4: Deploy services one by one
echo -e "\n${YELLOW}Step 4: Deploying services...${NC}"

# Create docker-compose.yml
cat > /tmp/docker-compose.yml << 'COMPOSE'
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
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U sophia"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: sophia-redis
    ports:
      - "6379:6379"
    volumes:
      - ~/sophia-data/redis:/data
    restart: always
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  weaviate:
    image: semitechnologies/weaviate:1.25.4
    container_name: sophia-weaviate
    ports:
      - "8080:8080"
    environment:
      AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED: 'true'
      PERSISTENCE_DATA_PATH: '/var/lib/weaviate'
      DEFAULT_VECTORIZER_MODULE: 'text2vec-transformers'
      ENABLE_MODULES: 'text2vec-transformers'
      TRANSFORMERS_INFERENCE_API: 'http://t2v-transformers:8080'
    volumes:
      - ~/sophia-data/weaviate:/var/lib/weaviate
    restart: always
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/v1/.well-known/ready"]
      interval: 10s
      timeout: 5s
      retries: 5

  t2v-transformers:
    image: semitechnologies/transformers-inference:sentence-transformers-multi-qa-MiniLM-L6-cos-v1
    container_name: sophia-t2v-transformers
    environment:
      ENABLE_CUDA: '0'
    restart: always
COMPOSE

# Copy docker-compose file
scp -i "$SSH_KEY" /tmp/docker-compose.yml ubuntu@$SERVER_IP:~/sophia-deployment/

# Start services
echo -e "\n${BLUE}Starting Docker services...${NC}"
ssh_exec "cd ~/sophia-deployment && docker-compose up -d"

# Wait for services
echo -e "\n${YELLOW}Waiting for services to be healthy...${NC}"
sleep 10

# Check services
ssh_exec "cd ~/sophia-deployment && docker-compose ps"

echo -e "\n${GREEN}✅ Deployment complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Deploy backend: ./scripts/quick_backend_deploy.sh"
echo "2. Deploy frontend: ./scripts/quick_frontend_deploy.sh"
echo "3. Check status: ssh -i ~/.ssh/lambda_labs_private_key ubuntu@$SERVER_IP 'docker ps'" 