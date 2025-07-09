#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SSH_KEY="${SSH_KEY:-~/.ssh/sophia2025.pem}"
LAMBDA_IP="${1:-104.171.202.103}"

echo -e "${BLUE}🚀 Deploying Sophia AI to Lambda Labs (Building on Server)${NC}"
echo -e "${BLUE}Target: ${LAMBDA_IP}${NC}"

# Step 1: Create deployment directory on server
echo -e "${YELLOW}Creating deployment directory...${NC}"
ssh -i ${SSH_KEY} ubuntu@${LAMBDA_IP} "mkdir -p ~/sophia-deployment"

# Step 2: Copy source code to Lambda Labs
echo -e "${YELLOW}Copying source code to Lambda Labs...${NC}"
rsync -avz --exclude='node_modules' --exclude='.git' --exclude='*.pyc' --exclude='__pycache__' \
    --exclude='dist' --exclude='build' --exclude='.env' \
    -e "ssh -i ${SSH_KEY}" \
    . ubuntu@${LAMBDA_IP}:~/sophia-deployment/

# Step 3: Build images on Lambda Labs
echo -e "${YELLOW}Building Docker images on Lambda Labs...${NC}"
ssh -i ${SSH_KEY} ubuntu@${LAMBDA_IP} << 'EOF'
cd ~/sophia-deployment

# Build backend
echo "Building backend image..."
docker build -f docker/Dockerfile.optimized -t sophia-backend:latest . || {
    echo "Backend build failed, trying with simpler Dockerfile..."
    cat > Dockerfile.backend.simple << 'DOCKERFILE'
FROM python:3.12-slim
WORKDIR /app
COPY requirements.docker.clean.txt ./
RUN pip install --no-cache-dir -r requirements.docker.clean.txt
COPY backend/ ./backend/
COPY config/ ./config/
ENV PYTHONPATH=/app
CMD ["python", "-m", "uvicorn", "backend.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
DOCKERFILE
    docker build -f docker/Dockerfile.optimized.simple -t sophia-backend:latest .
}

# Build frontend
echo "Building frontend image..."
if [ -d "frontend/dist" ]; then
    cd frontend
    docker build -f Dockerfile.simple -t sophia-frontend:latest . || {
        echo "Frontend build failed, using nginx directly..."
        cat > Dockerfile.frontend.simple << 'DOCKERFILE'
FROM nginx:alpine
COPY dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
DOCKERFILE
        docker build -f Dockerfile.frontend.simple -t sophia-frontend:latest .
    }
    cd ..
else
    echo "No frontend dist folder, skipping frontend build"
fi
EOF

# Step 4: Deploy with Docker Swarm
echo -e "${YELLOW}Deploying services...${NC}"
ssh -i ${SSH_KEY} ubuntu@${LAMBDA_IP} << 'EOF'
cd ~/sophia-deployment

# Remove existing stack if any
docker stack rm sophia 2>/dev/null || true
sleep 5

# Create simple docker-compose
cat > docker-compose.yml << 'COMPOSE'
version: '3.8'

services:
  backend:
    image: sophia-backend:latest
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=prod
      - DATABASE_URL=postgresql://sophia:sophia123@postgres:5432/sophia
      - REDIS_URL=redis://redis:6379
      - PULUMI_ORG=scoobyjava-org
    deploy:
      replicas: 2
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

  postgres:
    image: postgres:16-alpine
    environment:
      - POSTGRES_USER=sophia
      - POSTGRES_PASSWORD=sophia123
      - POSTGRES_DB=sophia
    volumes:
      - postgres_data:/var/lib/postgresql/data
    deploy:
      replicas: 1
      placement:
        constraints:
          - node.role == manager

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    deploy:
      replicas: 1

volumes:
  postgres_data:
  redis_data:

networks:
  default:
    driver: overlay
    attachable: true
COMPOSE

# Deploy the stack
docker stack deploy -c docker-compose.yml sophia
EOF

# Step 5: Wait and check status
echo -e "${YELLOW}Waiting for services to start...${NC}"
sleep 15

echo -e "${YELLOW}Checking deployment status...${NC}"
ssh -i ${SSH_KEY} ubuntu@${LAMBDA_IP} "docker service ls && echo '' && docker stack ps sophia"

echo -e "${GREEN}✅ Deployment complete!${NC}"
echo -e "${GREEN}Access the application at:${NC}"
echo -e "${GREEN}  Frontend: http://${LAMBDA_IP}${NC}"
echo -e "${GREEN}  Backend API: http://${LAMBDA_IP}:8000${NC}"
echo -e "${GREEN}  API Docs: http://${LAMBDA_IP}:8000/docs${NC}" 