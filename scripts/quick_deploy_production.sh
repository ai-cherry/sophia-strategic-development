#!/bin/bash
# Quick deployment to production Lambda Labs instance
# Simple approach using docker-compose

set -e

# Configuration
SSH_KEY="${SSH_KEY:-~/.ssh/sophia2025.pem}"
PRODUCTION_IP="104.171.202.103"
DOCKER_REGISTRY="${DOCKER_REGISTRY:-scoobyjava15}"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🚀 Quick Deploy to Production Instance${NC}"
echo -e "${BLUE}Target: ${PRODUCTION_IP}${NC}"

# Step 1: Check connectivity
echo -e "${YELLOW}Checking connectivity...${NC}"
if ssh -i ${SSH_KEY} -o ConnectTimeout=5 ubuntu@${PRODUCTION_IP} "echo 'Connected'" &>/dev/null; then
    echo -e "${GREEN}✅ Connected to production instance${NC}"
else
    echo -e "${RED}❌ Cannot connect to production instance${NC}"
    exit 1
fi

# Step 2: Copy deployment files
echo -e "${YELLOW}Copying deployment files...${NC}"
scp -i ${SSH_KEY} deployment/docker-compose-production.yml ubuntu@${PRODUCTION_IP}:~/

# Step 3: Deploy with docker-compose
echo -e "${YELLOW}Deploying services...${NC}"
ssh -i ${SSH_KEY} ubuntu@${PRODUCTION_IP} << 'EOF'
    # Pull latest images
    docker pull scoobyjava15/sophia-backend:latest
    docker pull scoobyjava15/sophia-frontend:latest
    
    # Stop existing services
    docker-compose -f docker-compose-production.yml down || true
    
    # Start services
    docker-compose -f docker-compose-production.yml up -d
    
    # Show status
    echo -e "\n=== Running Containers ==="
    docker ps
    
    echo -e "\n=== Service Logs ==="
    docker-compose -f docker-compose-production.yml logs --tail=20
EOF

# Step 4: Show access info
echo -e "${GREEN}✅ Deployment Complete!${NC}"
echo -e "${GREEN}Access the application at:${NC}"
echo -e "${BLUE}Frontend: http://${PRODUCTION_IP}${NC}"
echo -e "${BLUE}Backend API: http://${PRODUCTION_IP}:8000${NC}"
echo -e "${BLUE}API Docs: http://${PRODUCTION_IP}:8000/docs${NC}"

# Step 5: Quick health check
echo -e "${YELLOW}Running health check...${NC}"
sleep 10
if curl -s -o /dev/null -w "%{http_code}" http://${PRODUCTION_IP}:8000/health | grep -q "200"; then
    echo -e "${GREEN}✅ Backend is healthy${NC}"
else
    echo -e "${YELLOW}⚠️  Backend may still be starting up${NC}"
fi 