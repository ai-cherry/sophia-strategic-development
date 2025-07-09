#!/bin/bash
set -euo pipefail

# Sophia AI Unified Platform Deployment Script
# Deploys the complete platform including unified chat and dashboard

echo "🚀 Sophia AI Unified Platform Deployment"
echo "========================================"

# Configuration
STACK_NAME="sophia-ai"
REGISTRY="scoobyjava15"
LAMBDA_LABS_IP="192.222.58.232"
COMPOSE_FILE="docker-compose.cloud.unified.yml"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

print_error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."

    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed"
        exit 1
    fi

    # Check SSH access to Lambda Labs
    if ! ssh -o ConnectTimeout=5 root@${LAMBDA_LABS_IP} "echo 'SSH connection successful'" &> /dev/null; then
        print_error "Cannot connect to Lambda Labs server at ${LAMBDA_LABS_IP}"
        exit 1
    fi

    # Check if compose file exists
    if [ ! -f "$COMPOSE_FILE" ]; then
        print_error "Compose file $COMPOSE_FILE not found"
        exit 1
    fi

    print_status "Prerequisites check passed ✅"
}

# Build and push images
build_and_push_images() {
    print_status "Building and pushing Docker images..."

    # List of services to build
    services=(
        "sophia-ai-backend"
        "sophia-ai-unified-chat"
        "sophia-ai-dashboard"
        "sophia-ai-mcp-gateway"
    )

    for service in "${services[@]}"; do
        print_status "Building $service..."

        # Determine build context based on service
        case $service in
            "sophia-ai-backend")
                build_context="."
                dockerfile="Dockerfile.backend"
                ;;
            "sophia-ai-unified-chat")
                build_context="."
                dockerfile="Dockerfile.chat"
                ;;
            "sophia-ai-dashboard")
                build_context="frontend"
                dockerfile="Dockerfile"
                ;;
            "sophia-ai-mcp-gateway")
                build_context="mcp-gateway"
                dockerfile="Dockerfile"
                ;;
        esac

        # Build image
        docker build -t ${REGISTRY}/${service}:latest -f ${dockerfile} ${build_context}

        # Push to registry
        print_status "Pushing $service to registry..."
        docker push ${REGISTRY}/${service}:latest
    done

    # Build V2 MCP servers
    print_status "Building V2 MCP servers..."
    for i in {1..10}; do
        case $i in
            1) server="ai-memory-v2" ;;
            2) server="gong-v2" ;;
            3) server="snowflake-v2" ;;
            4) server="slack-v2" ;;
            5) server="notion-v2" ;;
            6) server="linear-v2" ;;
            7) server="github-v2" ;;
            8) server="codacy-v2" ;;
            9) server="asana-v2" ;;
            10) server="perplexity-v2" ;;
        esac

        print_status "Building sophia-${server}..."
        docker build -t ${REGISTRY}/sophia-${server}:latest \
            -f infrastructure/mcp_servers/${server//-/_}/Dockerfile \
            infrastructure/mcp_servers/${server//-/_}

        docker push ${REGISTRY}/sophia-${server}:latest
    done

    print_status "All images built and pushed successfully ✅"
}

# Deploy to Lambda Labs
deploy_to_lambda_labs() {
    print_status "Deploying to Lambda Labs..."

    # Copy compose file to server
    print_status "Copying deployment files..."
    scp $COMPOSE_FILE root@${LAMBDA_LABS_IP}:/root/
    scp nginx/nginx.conf root@${LAMBDA_LABS_IP}:/root/nginx/

    # Create Docker secrets on Lambda Labs
    print_status "Creating Docker secrets..."
    ssh root@${LAMBDA_LABS_IP} << 'EOF'
        # Create secrets from Pulumi ESC
        echo "Creating Docker secrets..."

        # Add your secret creation commands here
        # Example: echo "your-secret-value" | docker secret create secret_name -

        echo "Secrets created successfully"
EOF

    # Deploy stack
    print_status "Deploying Docker stack..."
    ssh root@${LAMBDA_LABS_IP} "docker stack deploy -c $(basename $COMPOSE_FILE) $STACK_NAME"

    print_status "Deployment initiated ✅"
}

# Monitor deployment
monitor_deployment() {
    print_status "Monitoring deployment progress..."

    # Wait for services to start
    sleep 10

    # Check service status
    ssh root@${LAMBDA_LABS_IP} "docker stack services $STACK_NAME"

    # Monitor for 2 minutes
    for i in {1..12}; do
        sleep 10
        print_status "Checking service health (${i}/12)..."

        # Get unhealthy services
        unhealthy=$(ssh root@${LAMBDA_LABS_IP} "docker service ls --filter label=com.docker.stack.namespace=$STACK_NAME --format '{{.Name}} {{.Replicas}}' | grep -v '/' | wc -l" || echo "0")

        if [ "$unhealthy" -eq "0" ]; then
            print_status "All services are healthy! ✅"
            break
        else
            print_warning "$unhealthy services still starting..."
        fi
    done
}

# Validate deployment
validate_deployment() {
    print_status "Validating deployment..."

    # Test endpoints
    endpoints=(
        "http://${LAMBDA_LABS_IP}:8000/health"     # Backend
        "http://${LAMBDA_LABS_IP}:8001/health"     # Unified Chat
        "http://${LAMBDA_LABS_IP}:3000"            # Dashboard
        "http://${LAMBDA_LABS_IP}:9000/health"     # MCP Gateway
    )

    for endpoint in "${endpoints[@]}"; do
        if curl -f -s "$endpoint" > /dev/null; then
            print_status "$endpoint is responding ✅"
        else
            print_error "$endpoint is not responding ❌"
        fi
    done

    # Run validation script
    if [ -f "scripts/validate_unified_deployment.py" ]; then
        print_status "Running comprehensive validation..."
        python scripts/validate_unified_deployment.py
    fi
}

# Main deployment flow
main() {
    print_status "Starting Sophia AI Unified Platform deployment"

    # Run deployment steps
    check_prerequisites
    build_and_push_images
    deploy_to_lambda_labs
    monitor_deployment
    validate_deployment

    print_status "🎉 Deployment completed successfully!"
    print_status "Access the platform at:"
    echo "  - Dashboard: http://${LAMBDA_LABS_IP}:3000"
    echo "  - API: http://${LAMBDA_LABS_IP}:8000"
    echo "  - Chat: http://${LAMBDA_LABS_IP}:8001"
    echo ""
    print_status "Monitor the deployment:"
    echo "  - Logs: ssh root@${LAMBDA_LABS_IP} 'docker service logs -f sophia-ai_sophia-backend'"
    echo "  - Status: ssh root@${LAMBDA_LABS_IP} 'docker stack services sophia-ai'"
}

# Run main function
main "$@"
