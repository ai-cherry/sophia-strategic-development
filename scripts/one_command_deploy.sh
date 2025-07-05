#!/bin/bash
# One-command deployment script for Sophia AI on Lambda Labs
# Run this ON THE LAMBDA LABS SERVER after uploading the deployment package

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}=== Sophia AI One-Command Deployment ===${NC}"
echo "This script will deploy everything to Docker Swarm"
echo ""

# Check if we're on Lambda Labs
if ! docker node ls &>/dev/null; then
    echo -e "${RED}ERROR: Not on a Docker Swarm manager node${NC}"
    echo "This script must be run on Lambda Labs (146.235.200.1)"
    echo ""
    echo "To initialize Swarm (if needed):"
    echo "  docker swarm init --advertise-addr 146.235.200.1"
    exit 1
fi

# Auto-detect deployment package
DEPLOY_PACKAGE=$(ls -t sophia-deployment-*.tar.gz 2>/dev/null | head -1)
if [ -z "$DEPLOY_PACKAGE" ]; then
    echo -e "${RED}ERROR: No deployment package found${NC}"
    echo "Upload the package first:"
    echo "  scp sophia-deployment-*.tar.gz ubuntu@146.235.200.1:~/"
    exit 1
fi

echo -e "${BLUE}Found deployment package: $DEPLOY_PACKAGE${NC}"

# Extract if not already extracted
DEPLOY_DIR="${DEPLOY_PACKAGE%.tar.gz}"
if [ ! -d "$DEPLOY_DIR" ]; then
    echo "Extracting deployment package..."
    tar -xzf "$DEPLOY_PACKAGE"
fi

cd "$DEPLOY_DIR"

# Check for required environment variables and set defaults
echo -e "${BLUE}Checking environment variables...${NC}"

# Set defaults for non-critical variables
export DOCKER_REGISTRY="${DOCKER_REGISTRY:-scoobyjava15}"
export IMAGE_TAG="${IMAGE_TAG:-latest}"
export GRAFANA_PASSWORD="${GRAFANA_PASSWORD:-admin}"
export MEM0_API_KEY="${MEM0_API_KEY:-mem0-default-key}"
export VERCEL_V0DEV_API_KEY="${VERCEL_V0DEV_API_KEY:-v0-default-key}"

# Check critical variables
if [ -z "${POSTGRES_PASSWORD:-}" ]; then
    echo -e "${YELLOW}Setting default POSTGRES_PASSWORD${NC}"
    export POSTGRES_PASSWORD="sophia-postgres-$(date +%s)"
fi

if [ -z "${PULUMI_ACCESS_TOKEN:-}" ]; then
    echo -e "${YELLOW}WARNING: PULUMI_ACCESS_TOKEN not set${NC}"
    echo "Some features may not work without Pulumi ESC"
    export PULUMI_ACCESS_TOKEN="dummy-token"
fi

if [ -z "${SNOWFLAKE_ACCOUNT:-}" ]; then
    echo -e "${YELLOW}Setting Snowflake defaults${NC}"
    export SNOWFLAKE_ACCOUNT="dummy-account"
    export SNOWFLAKE_USER="dummy-user"
    export SNOWFLAKE_PASSWORD="dummy-password"
fi

# Create Docker secrets
echo -e "${BLUE}Creating Docker secrets...${NC}"
create_secret() {
    local name=$1
    local value=$2
    if docker secret ls | grep -q "$name"; then
        echo "  Secret $name already exists"
    else
        echo "$value" | docker secret create "$name" - >/dev/null
        echo -e "  ${GREEN}✓${NC} Created secret: $name"
    fi
}

create_secret "postgres_password" "$POSTGRES_PASSWORD"
create_secret "grafana_password" "$GRAFANA_PASSWORD"
create_secret "pulumi_access_token" "$PULUMI_ACCESS_TOKEN"
create_secret "mem0_api_key" "$MEM0_API_KEY"
create_secret "snowflake_account" "$SNOWFLAKE_ACCOUNT"
create_secret "snowflake_user" "$SNOWFLAKE_USER"
create_secret "snowflake_password" "$SNOWFLAKE_PASSWORD"
create_secret "vercel_v0dev_api_key" "$VERCEL_V0DEV_API_KEY"

# Deploy the stack
echo -e "${BLUE}Deploying Sophia AI stack...${NC}"

# First, remove any existing stack
if docker stack ls | grep -q sophia-ai; then
    echo "Removing existing stack..."
    docker stack rm sophia-ai
    echo "Waiting for cleanup..."
    sleep 10
fi

# Deploy optimized configuration
if [ -f "docker-compose.cloud.yml.optimized" ]; then
    echo "Deploying optimized configuration..."
    docker stack deploy -c docker-compose.cloud.yml.optimized sophia-ai
elif [ -f "docker-compose.production.yml" ]; then
    echo "Deploying production configuration..."
    docker stack deploy -c docker-compose.production.yml sophia-ai
else
    echo -e "${RED}ERROR: No docker-compose file found${NC}"
    exit 1
fi

# Wait for initial deployment
echo "Waiting for services to start..."
sleep 20

# Deploy MCP servers
echo -e "${BLUE}Deploying MCP servers...${NC}"

# Create MCP server configuration inline
cat > docker-compose.mcp-servers.yml << 'EOF'
version: '3.8'

services:
  dashboard-mcp:
    image: ${DOCKER_REGISTRY:-scoobyjava15}/sophia-dashboard-mcp:${IMAGE_TAG:-latest}
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '1.0'
          memory: 2G
    environment:
      - ENVIRONMENT=prod
      - SERVICE_PORT=9100
    networks:
      - sophia-overlay
    ports:
      - "9100:9100"

  chat-mcp:
    image: ${DOCKER_REGISTRY:-scoobyjava15}/sophia-chat-mcp:${IMAGE_TAG:-latest}
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
    environment:
      - ENVIRONMENT=prod
      - SERVICE_PORT=9101
    networks:
      - sophia-overlay
    ports:
      - "9101:9101"

  codacy-mcp:
    image: ${DOCKER_REGISTRY:-scoobyjava15}/sophia-codacy-mcp:${IMAGE_TAG:-latest}
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '1.5'
          memory: 3G
    environment:
      - ENVIRONMENT=prod
      - SERVICE_PORT=3008
    networks:
      - sophia-overlay
    ports:
      - "3008:3008"

networks:
  sophia-overlay:
    external: true
EOF

# Deploy MCP servers
docker stack deploy -c docker-compose.mcp-servers.yml sophia-ai

# Monitor deployment
echo -e "${BLUE}=== Deployment Status ===${NC}"
sleep 10

# Show service status
docker service ls --filter label=com.docker.stack.namespace=sophia-ai

# Check for failures
failed=$(docker service ls --filter label=com.docker.stack.namespace=sophia-ai --format "{{.Name}}:{{.Replicas}}" | grep ':0/' || true)
if [ -n "$failed" ]; then
    echo -e "${YELLOW}Warning: Some services may be starting up:${NC}"
    echo "$failed"
    echo "Check logs with: docker service logs <service-name>"
else
    echo -e "${GREEN}✓ All services deployed successfully!${NC}"
fi

# Show access URLs
echo -e "${BLUE}=== Access URLs ===${NC}"
echo "Dashboard: https://api.sophia-ai.lambda.cloud/dashboard"
echo "Chat: https://chat-mcp.sophia-ai.lambda.cloud"
echo "API Docs: https://api.sophia-ai.lambda.cloud/docs"
echo "Grafana: http://146.235.200.1:3000 (admin/$GRAFANA_PASSWORD)"
echo "Prometheus: http://146.235.200.1:9090"

echo -e "${BLUE}=== Next Steps ===${NC}"
echo "1. Monitor services: docker service ls"
echo "2. Check logs: docker service logs sophia-ai_backend"
echo "3. Run performance monitor: ./monitor_swarm_performance.sh"
echo ""
echo -e "${GREEN}Deployment complete!${NC}"
