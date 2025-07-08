#!/bin/bash
# Sophia AI Platform Deployment Script
# Deploys the complete platform with all components

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
LAMBDA_LABS_IP="${LAMBDA_LABS_IP:-146.235.200.1}"
DOCKER_REGISTRY="${DOCKER_REGISTRY:-scoobyjava15}"
IMAGE_TAG="${IMAGE_TAG:-latest}"
STACK_NAME="sophia-ai"

echo -e "${BLUE}╔══════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║           SOPHIA AI COMPLETE PLATFORM DEPLOYMENT                      ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}Components to deploy:${NC}"
echo "  • Unified Chat Interface with WebSocket"
echo "  • Unified Dashboard with real-time monitoring"
echo "  • MCP Servers (AI Memory, Gong, Snowflake, etc.)"
echo "  • Backend API (FastAPI)"
echo "  • Frontend (React + TypeScript)"
echo "  • Redis + PostgreSQL"
echo "  • Monitoring (Prometheus + Grafana)"
echo ""

# Function to check prerequisites
check_prerequisites() {
    echo -e "${YELLOW}Checking prerequisites...${NC}"

    # Check Docker
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker is not installed${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ Docker found${NC}"

    # Check SSH access
    if ! ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no root@${LAMBDA_LABS_IP} "echo 'Connected'" &> /dev/null; then
        echo -e "${RED}❌ Cannot connect to Lambda Labs at ${LAMBDA_LABS_IP}${NC}"
        echo "Please check your SSH configuration"
        exit 1
    fi
    echo -e "${GREEN}✅ SSH connection to Lambda Labs successful${NC}"

    # Check if compose file exists
    if [ ! -f "docker-compose.cloud.yml" ]; then
        echo -e "${RED}❌ docker-compose.cloud.yml not found${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ Docker compose file found${NC}"
}

# Function to build and push images
build_and_push_images() {
    echo -e "${YELLOW}Building and pushing Docker images...${NC}"

    # Build backend
    echo -e "${BLUE}Building backend...${NC}"
    docker build -t ${DOCKER_REGISTRY}/sophia-backend:${IMAGE_TAG} -f Dockerfile.production .

    # Build frontend
    echo -e "${BLUE}Building frontend...${NC}"
    docker build -t ${DOCKER_REGISTRY}/sophia-frontend:${IMAGE_TAG} -f frontend/Dockerfile frontend/

    # Build MCP servers
    for server in ai-memory gong snowflake slack notion linear github codacy asana perplexity; do
        server_dir="infrastructure/mcp_servers/${server//-/_}_v2"
        if [ -d "$server_dir" ]; then
            echo -e "${BLUE}Building MCP server: $server${NC}"
            docker build -t ${DOCKER_REGISTRY}/sophia-${server}-v2:${IMAGE_TAG} -f ${server_dir}/Dockerfile ${server_dir}
        fi
    done

    # Push all images
    echo -e "${YELLOW}Pushing images to Docker Hub...${NC}"
    docker push ${DOCKER_REGISTRY}/sophia-backend:${IMAGE_TAG}
    docker push ${DOCKER_REGISTRY}/sophia-frontend:${IMAGE_TAG}

    for server in ai-memory gong snowflake slack notion linear github codacy asana perplexity; do
        if docker images | grep -q "sophia-${server}-v2"; then
            docker push ${DOCKER_REGISTRY}/sophia-${server}-v2:${IMAGE_TAG}
        fi
    done

    echo -e "${GREEN}✅ All images built and pushed${NC}"
}

# Function to deploy to Lambda Labs
deploy_to_lambda_labs() {
    echo -e "${YELLOW}Deploying to Lambda Labs...${NC}"

    # Create deployment directory on remote
    ssh root@${LAMBDA_LABS_IP} "mkdir -p /opt/sophia-ai/deployment"

    # Copy compose file
    scp docker-compose.cloud.yml root@${LAMBDA_LABS_IP}:/opt/sophia-ai/deployment/

    # Create deployment script on remote
    ssh root@${LAMBDA_LABS_IP} << 'REMOTE_SCRIPT'
#!/bin/bash
cd /opt/sophia-ai/deployment

# Set environment variables
export DOCKER_REGISTRY=${DOCKER_REGISTRY}
export IMAGE_TAG=${IMAGE_TAG}
export ENVIRONMENT=prod
export PULUMI_ORG=scoobyjava-org

# Initialize Docker Swarm if needed
if ! docker info | grep -q "Swarm: active"; then
    echo "Initializing Docker Swarm..."
    docker swarm init
fi

# Create required directories
mkdir -p /opt/sophia-ai/data/{redis,postgres,prometheus,grafana,traefik}

# Deploy the stack
docker stack deploy -c docker-compose.cloud.yml sophia-ai --with-registry-auth

echo "Deployment initiated. Waiting for services to start..."
sleep 30

# Check service status
docker stack services sophia-ai
REMOTE_SCRIPT

    echo -e "${GREEN}✅ Deployment initiated on Lambda Labs${NC}"
}

# Function to start local MCP servers
start_local_mcp_servers() {
    echo -e "${YELLOW}Starting local MCP servers...${NC}"

    # Create MCP server startup script
    cat > start_mcp_servers.sh << 'EOF'
#!/bin/bash
# Start MCP servers locally for development

# Function to start a server
start_server() {
    local name=$1
    local port=$2
    local dir="mcp-servers/$name"

    if [ -d "$dir" ] && [ -f "$dir/${name}_mcp_server.py" ]; then
        echo "Starting $name on port $port..."
        cd $dir
        MCP_SERVER_PORT=$port python ${name}_mcp_server.py > ../${name}.log 2>&1 &
        echo $! > ../${name}.pid
        cd ..
        sleep 2
    fi
}

# Start core MCP servers
start_server "ai_memory" 9001
start_server "codacy" 9008
start_server "linear" 9006
start_server "slack" 9004
start_server "github" 9007

echo "MCP servers started. Check logs in mcp-servers/*.log"
EOF

    chmod +x start_mcp_servers.sh

    # Execute the script
    ./start_mcp_servers.sh

    echo -e "${GREEN}✅ Local MCP servers started${NC}"
}

# Function to validate deployment
validate_deployment() {
    echo -e "${YELLOW}Validating deployment...${NC}"

    # Wait for services to stabilize
    echo "Waiting 60 seconds for services to stabilize..."
    sleep 60

    # Check backend health
    echo -ne "Checking backend API... "
    if curl -s -f http://${LAMBDA_LABS_IP}:8000/health > /dev/null; then
        echo -e "${GREEN}✅ Healthy${NC}"
    else
        echo -e "${RED}❌ Not responding${NC}"
    fi

    # Check frontend
    echo -ne "Checking frontend... "
    if curl -s -f http://${LAMBDA_LABS_IP}:3000 > /dev/null; then
        echo -e "${GREEN}✅ Accessible${NC}"
    else
        echo -e "${RED}❌ Not responding${NC}"
    fi

    # Check MCP servers
    for port in 9001 9002 9003 9004 9005 9006 9007 9008 9009 9010; do
        echo -ne "Checking MCP server on port $port... "
        if curl -s -f http://${LAMBDA_LABS_IP}:${port}/health > /dev/null 2>&1; then
            echo -e "${GREEN}✅ Healthy${NC}"
        else
            echo -e "${YELLOW}⚠️  Not responding (may be normal)${NC}"
        fi
    done

    # Check Docker stack status
    echo -e "${BLUE}Docker stack status:${NC}"
    ssh root@${LAMBDA_LABS_IP} "docker stack services sophia-ai"
}

# Function to show access information
show_access_info() {
    echo ""
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                    DEPLOYMENT COMPLETE!                               ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${BLUE}Access URLs:${NC}"
    echo -e "  • Dashboard: ${GREEN}http://${LAMBDA_LABS_IP}:3000${NC}"
    echo -e "  • API: ${GREEN}http://${LAMBDA_LABS_IP}:8000${NC}"
    echo -e "  • API Docs: ${GREEN}http://${LAMBDA_LABS_IP}:8000/docs${NC}"
    echo -e "  • Grafana: ${GREEN}http://${LAMBDA_LABS_IP}:3001${NC}"
    echo -e "  • Prometheus: ${GREEN}http://${LAMBDA_LABS_IP}:9090${NC}"
    echo ""
    echo -e "${BLUE}MCP Servers:${NC}"
    echo -e "  • AI Memory: ${GREEN}http://${LAMBDA_LABS_IP}:9001${NC}"
    echo -e "  • Gong: ${GREEN}http://${LAMBDA_LABS_IP}:9002${NC}"
    echo -e "  • Snowflake: ${GREEN}http://${LAMBDA_LABS_IP}:9003${NC}"
    echo -e "  • Slack: ${GREEN}http://${LAMBDA_LABS_IP}:9004${NC}"
    echo -e "  • Notion: ${GREEN}http://${LAMBDA_LABS_IP}:9005${NC}"
    echo -e "  • Linear: ${GREEN}http://${LAMBDA_LABS_IP}:9006${NC}"
    echo -e "  • GitHub: ${GREEN}http://${LAMBDA_LABS_IP}:9007${NC}"
    echo -e "  • Codacy: ${GREEN}http://${LAMBDA_LABS_IP}:9008${NC}"
    echo ""
    echo -e "${BLUE}Management Commands:${NC}"
    echo "  • View logs: ssh root@${LAMBDA_LABS_IP} 'docker service logs -f sophia-ai_sophia-backend'"
    echo "  • Scale service: ssh root@${LAMBDA_LABS_IP} 'docker service scale sophia-ai_sophia-backend=3'"
    echo "  • Update service: ssh root@${LAMBDA_LABS_IP} 'docker service update --force sophia-ai_sophia-backend'"
    echo "  • Remove stack: ssh root@${LAMBDA_LABS_IP} 'docker stack rm sophia-ai'"
}

# Main deployment flow
main() {
    echo -e "${BLUE}Starting Sophia AI platform deployment...${NC}"
    echo ""

    # Check prerequisites
    check_prerequisites

    # Ask user what to deploy
    echo ""
    echo -e "${YELLOW}Select deployment option:${NC}"
    echo "1) Full deployment (build, push, deploy to Lambda Labs)"
    echo "2) Deploy only (use existing images)"
    echo "3) Start local MCP servers only"
    echo "4) Validate existing deployment"
    read -p "Enter option (1-4): " option

    case $option in
        1)
            build_and_push_images
            deploy_to_lambda_labs
            validate_deployment
            show_access_info
            ;;
        2)
            deploy_to_lambda_labs
            validate_deployment
            show_access_info
            ;;
        3)
            start_local_mcp_servers
            ;;
        4)
            validate_deployment
            show_access_info
            ;;
        *)
            echo -e "${RED}Invalid option${NC}"
            exit 1
            ;;
    esac
}

# Run main function
main
