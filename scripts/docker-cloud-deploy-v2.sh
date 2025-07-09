#!/bin/bash
# Docker Cloud Deployment Script for V2 MCP Servers to Lambda Labs

set -e

# Configuration
DOCKER_REGISTRY="scoobyjava15"
DOCKER_HUB_USER="${DOCKER_HUB_USER:-scoobyjava15}"
LAMBDA_LABS_HOST="${LAMBDA_LABS_HOST:-192.222.58.232}"
LAMBDA_LABS_USER="${LAMBDA_LABS_USER:-ubuntu}"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
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

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

echo "🚀 Docker Cloud Deployment for V2 MCP Servers"
echo "============================================"
echo ""

# Check prerequisites
echo "📋 Checking prerequisites..."

# Check Docker
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed"
    exit 1
fi
print_status "Docker is installed"

# Check Docker Hub login
if ! docker info 2>/dev/null | grep -q "Username: ${DOCKER_HUB_USER}"; then
    print_warning "Not logged into Docker Hub. Logging in..."
    docker login -u ${DOCKER_HUB_USER}
fi
print_status "Docker Hub authenticated"

# Check SSH access to Lambda Labs
if ! ssh -o ConnectTimeout=5 ${LAMBDA_LABS_USER}@${LAMBDA_LABS_HOST} "echo 'SSH OK'" &>/dev/null; then
    print_error "Cannot connect to Lambda Labs via SSH"
    print_info "Please ensure SSH key is configured for ${LAMBDA_LABS_USER}@${LAMBDA_LABS_HOST}"
    exit 1
fi
print_status "Lambda Labs SSH connection verified"

# List of V2 MCP servers with ports
declare -A SERVERS=(
    ["ai_memory_v2"]="9000"
    ["snowflake_v2"]="9001"
    ["linear_v2"]="9002"
    ["notion_v2"]="9003"
    ["asana_v2"]="9004"
    ["codacy_v2"]="9005"
    ["github_v2"]="9006"
    ["slack_v2"]="9007"
    ["perplexity_v2"]="9008"
    ["gong_v2"]="9009"
)

# Build and push images
echo ""
echo "📦 Building and pushing Docker images to Docker Hub..."
echo "======================================================"

BUILD_FAILED=false

for server in "${!SERVERS[@]}"; do
    port=${SERVERS[$server]}
    server_name=${server//_/-}
    image_tag="${DOCKER_REGISTRY}/sophia-${server_name}:latest"

    echo ""
    echo "🔨 Building ${server} (port ${port})..."

    # Check if Dockerfile exists
    if [ ! -f "infrastructure/mcp_servers/${server}/Dockerfile" ]; then
        print_error "Dockerfile not found for ${server}"
        BUILD_FAILED=true
        continue
    fi

    # Build image
    if docker build \
        -t ${image_tag} \
        -f infrastructure/mcp_servers/${server}/Dockerfile \
        --build-arg PORT=${port} \
        infrastructure/mcp_servers/${server}/ \
        --progress=plain; then

        print_status "Built ${server} successfully"

        # Push to Docker Hub
        echo "📤 Pushing ${server} to Docker Hub..."
        if docker push ${image_tag}; then
            print_status "Pushed ${server} to Docker Hub"
        else
            print_error "Failed to push ${server}"
            BUILD_FAILED=true
        fi
    else
        print_error "Failed to build ${server}"
        BUILD_FAILED=true
    fi
done

if [ "$BUILD_FAILED" = true ]; then
    print_error "Some images failed to build/push. Please fix errors before proceeding."
    exit 1
fi

# Deploy to Lambda Labs
echo ""
echo "🚀 Deploying to Lambda Labs..."
echo "=============================="

# Copy docker-compose file
echo "📋 Copying docker-compose.mcp-v2.yml to Lambda Labs..."
scp docker-compose.mcp-v2.yml ${LAMBDA_LABS_USER}@${LAMBDA_LABS_HOST}:~/

# Create deployment script on Lambda Labs
ssh ${LAMBDA_LABS_USER}@${LAMBDA_LABS_HOST} << 'REMOTE_SCRIPT'
#!/bin/bash

echo "🔧 Setting up on Lambda Labs..."

# Create necessary directories
mkdir -p ~/sophia-mcp-v2/logs
cd ~/sophia-mcp-v2

# Move docker-compose file
mv ~/docker-compose.mcp-v2.yml ./

# Initialize Docker Swarm if not already done
if ! docker info 2>/dev/null | grep -q "Swarm: active"; then
    echo "🔄 Initializing Docker Swarm..."
    docker swarm init
fi

# Create overlay network if not exists
if ! docker network ls | grep -q "sophia-ai-network"; then
    echo "🌐 Creating overlay network..."
    docker network create --driver overlay --attachable sophia-ai-network
fi

# Create secrets from environment (these should be set via Pulumi ESC)
echo "🔐 Creating Docker secrets..."

# Function to create secret if not exists
create_secret() {
    local secret_name=$1
    local secret_value=$2

    if ! docker secret ls | grep -q "^${secret_name}"; then
        echo "${secret_value}" | docker secret create ${secret_name} -
        echo "✓ Created secret: ${secret_name}"
    else
        echo "ℹ Secret already exists: ${secret_name}"
    fi
}

# Note: In production, these should come from Pulumi ESC
# For now, we'll check if they exist in environment
if [ -n "$OPENAI_API_KEY" ]; then
    create_secret "openai_api_key" "$OPENAI_API_KEY"
fi

if [ -n "$GONG_API_KEY" ]; then
    create_secret "gong_api_key" "$GONG_API_KEY"
fi

if [ -n "$GONG_API_SECRET" ]; then
    create_secret "gong_api_secret" "$GONG_API_SECRET"
fi

# Deploy the stack
echo "📦 Deploying MCP V2 stack..."
docker stack deploy -c docker-compose.mcp-v2.yml sophia-mcp-v2

# Wait for services to start
echo "⏳ Waiting for services to start (30 seconds)..."
sleep 30

# Check service status
echo ""
echo "📊 Service Status:"
docker stack services sophia-mcp-v2

# Check which services are running
echo ""
echo "🏥 Health Check Results:"
for port in 9000 9001 9002 9003 9004 9005 9006 9007 9008 9009; do
    service_name=$(docker service ls --format "table {{.Name}}" | grep -E "sophia-mcp-v2_.*" | grep -v NAME | head -1)
    echo -n "Port $port: "
    if curl -s -f http://localhost:$port/health > /dev/null 2>&1; then
        echo "✅ Healthy"
    else
        echo "❌ Not responding"
    fi
done

echo ""
echo "✅ Deployment complete!"
REMOTE_SCRIPT

# Final status check
echo ""
echo "🎉 Docker Cloud Deployment Complete!"
echo "===================================="
echo ""
echo "📊 Service URLs (via Lambda Labs):"
echo "  - AI Memory V2: http://${LAMBDA_LABS_HOST}:9000"
echo "  - Snowflake V2: http://${LAMBDA_LABS_HOST}:9001"
echo "  - Linear V2: http://${LAMBDA_LABS_HOST}:9002"
echo "  - Notion V2: http://${LAMBDA_LABS_HOST}:9003"
echo "  - Asana V2: http://${LAMBDA_LABS_HOST}:9004"
echo "  - Codacy V2: http://${LAMBDA_LABS_HOST}:9005"
echo "  - GitHub V2: http://${LAMBDA_LABS_HOST}:9006"
echo "  - Slack V2: http://${LAMBDA_LABS_HOST}:9007"
echo "  - Perplexity V2: http://${LAMBDA_LABS_HOST}:9008"
echo "  - Gong V2: http://${LAMBDA_LABS_HOST}:9009"
echo ""
echo "🔍 To view logs:"
echo "  ssh ${LAMBDA_LABS_USER}@${LAMBDA_LABS_HOST} 'docker service logs sophia-mcp-v2_<service-name>'"
echo ""
echo "📊 To check status:"
echo "  ssh ${LAMBDA_LABS_USER}@${LAMBDA_LABS_HOST} 'docker stack ps sophia-mcp-v2'"
echo ""
echo "🔄 To update a service:"
echo "  docker build -t ${DOCKER_REGISTRY}/sophia-<service>:latest ..."
echo "  docker push ${DOCKER_REGISTRY}/sophia-<service>:latest"
echo "  ssh ${LAMBDA_LABS_USER}@${LAMBDA_LABS_HOST} 'docker service update --image ${DOCKER_REGISTRY}/sophia-<service>:latest sophia-mcp-v2_<service>'"
echo ""
echo "⚠️  Note: Ensure all required secrets are configured in Pulumi ESC"
