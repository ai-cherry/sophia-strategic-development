#!/bin/bash
# Deploy V2 MCP Servers to Lambda Labs

set -e

echo "🚀 Deploying V2 MCP Servers to Lambda Labs"
echo "=========================================="

# Configuration
DOCKER_REGISTRY="scoobyjava15"
LAMBDA_LABS_HOST="146.235.200.1"
LAMBDA_LABS_USER="ubuntu"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Function to print colored output
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Check if running from correct directory
if [ ! -f "docker-compose.mcp-v2.yml" ]; then
    print_error "docker-compose.mcp-v2.yml not found. Please run from project root."
    exit 1
fi

# Build and push images
echo ""
echo "📦 Building and pushing Docker images..."
echo "--------------------------------------"

SERVERS=("ai_memory_v2" "snowflake_v2" "linear_v2" "notion_v2" "asana_v2" "codacy_v2")

for server in "${SERVERS[@]}"; do
    echo ""
    echo "Building $server..."
    
    # Build image
    docker build -t ${DOCKER_REGISTRY}/sophia-${server//_/-}:latest \
        -f infrastructure/mcp_servers/$server/Dockerfile \
        infrastructure/mcp_servers/$server/
    
    if [ $? -eq 0 ]; then
        print_status "Built $server successfully"
        
        # Push to registry
        echo "Pushing $server to registry..."
        docker push ${DOCKER_REGISTRY}/sophia-${server//_/-}:latest
        
        if [ $? -eq 0 ]; then
            print_status "Pushed $server successfully"
        else
            print_error "Failed to push $server"
            exit 1
        fi
    else
        print_error "Failed to build $server"
        exit 1
    fi
done

# Deploy to Lambda Labs
echo ""
echo "🚀 Deploying to Lambda Labs..."
echo "-----------------------------"

# Copy docker-compose file to Lambda Labs
scp docker-compose.mcp-v2.yml ${LAMBDA_LABS_USER}@${LAMBDA_LABS_HOST}:/home/ubuntu/

# SSH to Lambda Labs and deploy
ssh ${LAMBDA_LABS_USER}@${LAMBDA_LABS_HOST} << 'EOF'
    cd /home/ubuntu
    
    # Initialize Docker Swarm if not already done
    docker swarm init 2>/dev/null || true
    
    # Create network if not exists
    docker network create --driver overlay sophia-ai-network 2>/dev/null || true
    
    # Deploy stack
    docker stack deploy -c docker-compose.mcp-v2.yml sophia-mcp-v2
    
    # Wait for services to start
    sleep 10
    
    # Check services
    docker stack services sophia-mcp-v2
EOF

# Health check
echo ""
echo "🏥 Running health checks..."
echo "--------------------------"

PORTS=(9000 9001 9002 9003 9004 9005)
NAMES=("AI Memory V2" "Snowflake V2" "Linear V2" "Notion V2" "Asana V2" "Codacy V2")

for i in "${!PORTS[@]}"; do
    PORT=${PORTS[$i]}
    NAME=${NAMES[$i]}
    
    echo -n "Checking $NAME (port $PORT)... "
    
    # Check health endpoint
    if curl -s -f http://${LAMBDA_LABS_HOST}:${PORT}/health > /dev/null 2>&1; then
        print_status "Healthy"
    else
        print_warning "Not responding yet"
    fi
done

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📊 Service URLs:"
echo "- AI Memory V2: http://${LAMBDA_LABS_HOST}:9000"
echo "- Snowflake V2: http://${LAMBDA_LABS_HOST}:9001"
echo "- Linear V2: http://${LAMBDA_LABS_HOST}:9002"
echo "- Notion V2: http://${LAMBDA_LABS_HOST}:9003"
echo "- Asana V2: http://${LAMBDA_LABS_HOST}:9004"
echo "- Codacy V2: http://${LAMBDA_LABS_HOST}:9005"
echo ""
echo "📝 View logs: ssh ${LAMBDA_LABS_USER}@${LAMBDA_LABS_HOST} 'docker service logs sophia-mcp-v2_<service-name>'"
echo "📊 View status: ssh ${LAMBDA_LABS_USER}@${LAMBDA_LABS_HOST} 'docker stack ps sophia-mcp-v2'" 