#!/bin/bash
# Complete Sophia AI Docker Cloud Deployment Script
# This script handles the entire deployment process

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}=== Sophia AI Complete Docker Cloud Deployment ===${NC}"
echo ""

# Configuration
DOCKER_REGISTRY="${DOCKER_REGISTRY:-scoobyjava15}"
LAMBDA_LABS_IP="146.235.200.1"
LAMBDA_LABS_USER="${LAMBDA_LABS_USER:-ubuntu}"

# Step 1: Build Docker Images Locally
echo -e "${BLUE}Step 1: Building Docker Images${NC}"

build_image() {
    local name=$1
    local dockerfile=$2
    local context=$3

    echo -e "Building ${YELLOW}$name${NC}..."
    if docker build -t "$DOCKER_REGISTRY/$name:latest" -f "$dockerfile" "$context"; then
        echo -e "${GREEN}✓${NC} Built $name"
    else
        echo -e "${RED}✗${NC} Failed to build $name"
        return 1
    fi
}

# Build core images
build_image "sophia-backend" "Dockerfile.uv.production" "."
build_image "sophia-mcp-gateway" "infrastructure/mcp-gateway/Dockerfile.uv.production" "."
build_image "sophia-ai-memory-mcp" "mcp-servers/ai-memory/Dockerfile.production" "."

echo ""

# Step 2: Push Images to Docker Hub
echo -e "${BLUE}Step 2: Pushing Images to Docker Hub${NC}"
echo "Make sure you're logged in to Docker Hub: docker login"
echo ""

push_image() {
    local name=$1
    echo -e "Pushing ${YELLOW}$name${NC}..."
    if docker push "$DOCKER_REGISTRY/$name:latest"; then
        echo -e "${GREEN}✓${NC} Pushed $name"
    else
        echo -e "${RED}✗${NC} Failed to push $name"
        return 1
    fi
}

# Push images
push_image "sophia-backend"
push_image "sophia-mcp-gateway"
push_image "sophia-ai-memory-mcp"

echo ""

# Step 3: Create Deployment Package
echo -e "${BLUE}Step 3: Creating Deployment Package${NC}"

TIMESTAMP=$(date +%Y%m%d-%H%M%S)
DEPLOY_DIR="sophia-cloud-deploy-$TIMESTAMP"

mkdir -p "$DEPLOY_DIR"

# Create simplified docker-compose for cloud
cat > "$DEPLOY_DIR/docker-compose.yml" << 'EOF'
version: '3.8'

services:
  backend:
    image: ${DOCKER_REGISTRY}/sophia-backend:latest
    deploy:
      replicas: 3
      update_config:
        parallelism: 1
        delay: 10s
      restart_policy:
        condition: on-failure
    environment:
      - ENVIRONMENT=prod
      - PULUMI_ORG=scoobyjava-org
    ports:
      - "8000:8000"
    networks:
      - sophia-overlay
    secrets:
      - postgres_password
      - pulumi_access_token

  postgres:
    image: postgres:15-alpine
    deploy:
      placement:
        constraints:
          - node.role == manager
    environment:
      POSTGRES_DB: sophia_ai
      POSTGRES_USER: sophia
      POSTGRES_PASSWORD_FILE: /run/secrets/postgres_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - sophia-overlay
    secrets:
      - postgres_password

  redis:
    image: redis:7-alpine
    deploy:
      replicas: 1
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    networks:
      - sophia-overlay

  mcp-gateway:
    image: ${DOCKER_REGISTRY}/sophia-mcp-gateway:latest
    deploy:
      replicas: 2
    ports:
      - "8090:8090"
      - "9090:9090"
    networks:
      - sophia-overlay

  ai-memory-mcp:
    image: ${DOCKER_REGISTRY}/sophia-ai-memory-mcp:latest
    deploy:
      replicas: 2
    ports:
      - "9000:9000"
    networks:
      - sophia-overlay
    secrets:
      - pulumi_access_token

networks:
  sophia-overlay:
    driver: overlay
    attachable: true

volumes:
  postgres_data:
  redis_data:

secrets:
  postgres_password:
    external: true
  pulumi_access_token:
    external: true
EOF

# Create deployment script
cat > "$DEPLOY_DIR/deploy.sh" << 'EOF'
#!/bin/bash
set -euo pipefail

echo "=== Deploying Sophia AI to Docker Swarm ==="

# Check if Swarm is initialized
if ! docker info | grep -q "Swarm: active"; then
    echo "Initializing Docker Swarm..."
    docker swarm init --advertise-addr $(hostname -I | awk '{print $1}')
fi

# Create secrets
echo "Creating Docker secrets..."
create_secret() {
    local name=$1
    local value=$2
    if docker secret ls | grep -q "$name"; then
        echo "Secret $name already exists"
    else
        echo "$value" | docker secret create "$name" -
        echo "Created secret: $name"
    fi
}

# Set default values if not provided
POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-sophia-postgres-$(date +%s)}"
PULUMI_ACCESS_TOKEN="${PULUMI_ACCESS_TOKEN:-dummy-token}"

create_secret "postgres_password" "$POSTGRES_PASSWORD"
create_secret "pulumi_access_token" "$PULUMI_ACCESS_TOKEN"

# Deploy stack
echo "Deploying Sophia AI stack..."
export DOCKER_REGISTRY="${DOCKER_REGISTRY:-scoobyjava15}"
docker stack deploy -c docker-compose.yml sophia-ai

echo ""
echo "=== Deployment Started ==="
echo "Monitor with: docker service ls"
echo "Check logs: docker service logs sophia-ai_backend"
echo ""
echo "Access points:"
echo "  Backend API: http://$(hostname -I | awk '{print $1}'):8000"
echo "  MCP Gateway: http://$(hostname -I | awk '{print $1}'):8090"
echo "  AI Memory: http://$(hostname -I | awk '{print $1}'):9000"
EOF

chmod +x "$DEPLOY_DIR/deploy.sh"

# Create package
tar -czf "$DEPLOY_DIR.tar.gz" "$DEPLOY_DIR"
rm -rf "$DEPLOY_DIR"

echo -e "${GREEN}✓${NC} Created deployment package: $DEPLOY_DIR.tar.gz"
echo ""

# Step 4: Provide deployment instructions
echo -e "${BLUE}=== Next Steps ===${NC}"
echo ""
echo "1. Upload deployment package to Lambda Labs:"
echo -e "   ${YELLOW}scp $DEPLOY_DIR.tar.gz $LAMBDA_LABS_USER@$LAMBDA_LABS_IP:~/${NC}"
echo ""
echo "2. SSH to Lambda Labs:"
echo -e "   ${YELLOW}ssh $LAMBDA_LABS_USER@$LAMBDA_LABS_IP${NC}"
echo ""
echo "3. Extract and deploy:"
echo -e "   ${YELLOW}tar -xzf $DEPLOY_DIR.tar.gz${NC}"
echo -e "   ${YELLOW}cd $DEPLOY_DIR${NC}"
echo -e "   ${YELLOW}./deploy.sh${NC}"
echo ""
echo "4. Access your services:"
echo -e "   Backend: ${GREEN}http://$LAMBDA_LABS_IP:8000${NC}"
echo -e "   Docs: ${GREEN}http://$LAMBDA_LABS_IP:8000/docs${NC}"
echo ""

# Optional: Auto-deploy if SSH key is set up
if [ "${AUTO_DEPLOY:-false}" = "true" ]; then
    echo -e "${BLUE}Auto-deploying to Lambda Labs...${NC}"
    scp "$DEPLOY_DIR.tar.gz" "$LAMBDA_LABS_USER@$LAMBDA_LABS_IP:~/"
    ssh "$LAMBDA_LABS_USER@$LAMBDA_LABS_IP" "tar -xzf $DEPLOY_DIR.tar.gz && cd $DEPLOY_DIR && ./deploy.sh"
    echo -e "${GREEN}✓ Deployment complete!${NC}"
fi
