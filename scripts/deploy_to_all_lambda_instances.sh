#!/bin/bash
# Deploy Sophia AI across all Lambda Labs instances using Docker Swarm
# This approach uses Docker Swarm for simplicity while we transition to Kubernetes

set -euo pipefail

# Configuration
SSH_KEY="${SSH_KEY:-~/.ssh/sophia2025.pem}"
DOCKER_REGISTRY="${DOCKER_REGISTRY:-scoobyjava15}"

# Lambda Labs instances
declare -A INSTANCES=(
    ["production"]="104.171.202.103"
    ["ai-core"]="192.222.58.232"
    ["mcp-orchestrator"]="104.171.202.117"
    ["data-pipeline"]="104.171.202.134"
    ["development"]="155.248.194.183"
)

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🚀 Deploying Sophia AI to All Lambda Labs Instances${NC}"

# Function to check SSH connectivity
check_connectivity() {
    echo -e "${YELLOW}Checking connectivity to all instances...${NC}"
    for name in "${!INSTANCES[@]}"; do
        ip=${INSTANCES[$name]}
        if ssh -i ${SSH_KEY} -o ConnectTimeout=5 ubuntu@${ip} "echo 'Connected'" &>/dev/null; then
            echo -e "${GREEN}✅ ${name} (${ip}) - Connected${NC}"
        else
            echo -e "${RED}❌ ${name} (${ip}) - Failed${NC}"
            exit 1
        fi
    done
}

# Function to initialize Docker Swarm
init_swarm() {
    echo -e "${YELLOW}Initializing Docker Swarm on production instance...${NC}"
    
    MANAGER_IP=${INSTANCES["production"]}
    
    # Initialize swarm on manager
    ssh -i ${SSH_KEY} ubuntu@${MANAGER_IP} << 'EOF'
        # Check if already in swarm
        if docker info | grep -q "Swarm: active"; then
            echo "Already in swarm mode"
        else
            docker swarm init --advertise-addr $(hostname -I | awk '{print $1}')
        fi
        
        # Get join token
        docker swarm join-token worker -q > /tmp/worker-token
EOF
    
    # Get worker token
    WORKER_TOKEN=$(ssh -i ${SSH_KEY} ubuntu@${MANAGER_IP} "cat /tmp/worker-token")
    
    # Join workers
    for name in "ai-core" "mcp-orchestrator" "data-pipeline" "development"; do
        ip=${INSTANCES[$name]}
        echo -e "${YELLOW}Joining ${name} to swarm...${NC}"
        
        ssh -i ${SSH_KEY} ubuntu@${ip} << EOF
            # Leave any existing swarm
            docker swarm leave --force 2>/dev/null || true
            
            # Join new swarm
            docker swarm join --token ${WORKER_TOKEN} ${MANAGER_IP}:2377
EOF
    done
    
    echo -e "${GREEN}✅ Docker Swarm initialized${NC}"
}

# Function to label nodes
label_nodes() {
    echo -e "${YELLOW}Labeling nodes for workload placement...${NC}"
    
    ssh -i ${SSH_KEY} ubuntu@${INSTANCES["production"]} << 'EOF'
        # Label nodes
        docker node update --label-add gpu=rtx6000 --label-add role=manager sophia-production-instance
        docker node update --label-add gpu=gh200 --label-add role=ai-core sophia-ai-core
        docker node update --label-add gpu=a6000 --label-add role=mcp sophia-mcp-orchestrator
        docker node update --label-add gpu=a100 --label-add role=data sophia-data-pipeline
        docker node update --label-add gpu=a10 --label-add role=dev sophia-development
        
        # Show nodes
        docker node ls
EOF
}

# Function to deploy services
deploy_services() {
    echo -e "${YELLOW}Deploying services across the swarm...${NC}"
    
    # Copy deployment files to manager
    scp -i ${SSH_KEY} deployment/docker-compose-*.yml ubuntu@${INSTANCES["production"]}:~/
    
    # Deploy stack
    ssh -i ${SSH_KEY} ubuntu@${INSTANCES["production"]} << 'EOF'
        # Create overlay network
        docker network create --driver overlay --attachable sophia-net 2>/dev/null || true
        
        # Deploy production services on manager
        docker stack deploy -c docker-compose-production.yml sophia-prod
        
        # Deploy AI core services
        docker stack deploy -c docker-compose-ai-core.yml sophia-ai
        
        # Deploy MCP services
        docker stack deploy -c docker-compose-mcp-orchestrator.yml sophia-mcp
        
        # Deploy data pipeline
        docker stack deploy -c docker-compose-data-pipeline.yml sophia-data
        
        # Deploy development services
        docker stack deploy -c docker-compose-development.yml sophia-dev
EOF
}

# Function to setup GPU support
setup_gpu() {
    echo -e "${YELLOW}Setting up GPU support on all nodes...${NC}"
    
    for name in "${!INSTANCES[@]}"; do
        ip=${INSTANCES[$name]}
        echo -e "${YELLOW}Configuring GPU on ${name}...${NC}"
        
        ssh -i ${SSH_KEY} ubuntu@${ip} << 'EOF'
            # Install NVIDIA container toolkit if not present
            if ! command -v nvidia-container-toolkit &> /dev/null; then
                distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
                curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
                curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
                sudo apt-get update
                sudo apt-get install -y nvidia-container-toolkit
                sudo nvidia-ctk runtime configure --runtime=docker
                sudo systemctl restart docker
            fi
            
            # Test GPU access
            docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi
EOF
    done
}

# Function to check deployment status
check_status() {
    echo -e "${YELLOW}Checking deployment status...${NC}"
    
    ssh -i ${SSH_KEY} ubuntu@${INSTANCES["production"]} << 'EOF'
        echo "=== Stack Status ==="
        docker stack ls
        
        echo -e "\n=== Service Status ==="
        docker service ls
        
        echo -e "\n=== Running Containers by Node ==="
        docker node ps $(docker node ls -q)
EOF
}

# Function to show access URLs
show_urls() {
    echo -e "${GREEN}✅ Deployment Complete!${NC}"
    echo -e "${GREEN}Access URLs:${NC}"
    echo -e "${BLUE}Production Dashboard: http://${INSTANCES["production"]}${NC}"
    echo -e "${BLUE}API Gateway: http://${INSTANCES["production"]}:8000${NC}"
    echo -e "${BLUE}AI Core: http://${INSTANCES["ai-core"]}:8001${NC}"
    echo -e "${BLUE}MCP Gateway: http://${INSTANCES["mcp-orchestrator"]}:9000${NC}"
    echo -e "${BLUE}Data Pipeline: http://${INSTANCES["data-pipeline"]}:8002${NC}"
    echo -e "${BLUE}Development: http://${INSTANCES["development"]}:3000${NC}"
}

# Main execution
main() {
    echo -e "${BLUE}Starting multi-instance deployment...${NC}"
    
    check_connectivity
    init_swarm
    label_nodes
    setup_gpu
    deploy_services
    
    echo -e "${YELLOW}Waiting for services to start...${NC}"
    sleep 30
    
    check_status
    show_urls
}

# Run main
main "$@" 