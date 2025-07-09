#!/bin/bash
# Deploy Sophia AI to Lambda Labs Kubernetes - 2025 Edition
# Features: BuildKit, security scanning, GPU support, multi-instance deployment

set -euo pipefail

# Configuration
NAMESPACE="${NAMESPACE:-sophia-ai-prod}"
DOCKER_REGISTRY="${DOCKER_REGISTRY:-scoobyjava15}"
IMAGE_TAG="${IMAGE_TAG:-latest}"
SSH_KEY="${SSH_KEY:-~/.ssh/sophia2025.pem}"

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

echo -e "${BLUE}🚀 Deploying Sophia AI to Lambda Labs Kubernetes${NC}"
echo -e "${BLUE}Namespace: ${NAMESPACE}${NC}"
echo -e "${BLUE}Registry: ${DOCKER_REGISTRY}${NC}"

# Function to check prerequisites
check_prerequisites() {
    echo -e "${YELLOW}Checking prerequisites...${NC}"
    
    # Check for required tools
    for tool in docker kubectl helm trivy; do
        if ! command -v $tool &> /dev/null; then
            echo -e "${RED}❌ $tool is not installed${NC}"
            exit 1
        fi
    done
    
    # Check Docker daemon
    if ! docker info &> /dev/null; then
        echo -e "${RED}❌ Docker daemon is not running${NC}"
        exit 1
    fi
    
    # Check SSH key
    if [ ! -f "$SSH_KEY" ]; then
        echo -e "${RED}❌ SSH key not found: $SSH_KEY${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ All prerequisites met${NC}"
}

# Function to build images with BuildKit
build_images() {
    echo -e "${YELLOW}Building images with BuildKit...${NC}"
    
    # Enable BuildKit
    export DOCKER_BUILDKIT=1
    
    # Build backend
    echo -e "${YELLOW}Building backend image...${NC}"
    docker buildx build \
        --platform linux/amd64 \
        --build-arg BUILDKIT_INLINE_CACHE=1 \
        --cache-from type=registry,ref=${DOCKER_REGISTRY}/sophia-backend:buildcache \
        --cache-to type=registry,ref=${DOCKER_REGISTRY}/sophia-backend:buildcache,mode=max \
        --load \
        -t ${DOCKER_REGISTRY}/sophia-backend:${IMAGE_TAG} \
        -f Dockerfile.production.2025 \
        .
    
    # Build frontend
    echo -e "${YELLOW}Building frontend image...${NC}"
    docker buildx build \
        --platform linux/amd64 \
        --load \
        -t ${DOCKER_REGISTRY}/sophia-frontend:${IMAGE_TAG} \
        -f frontend/Dockerfile \
        ./frontend
    
    echo -e "${GREEN}✅ Images built successfully${NC}"
}

# Function to scan images for vulnerabilities
scan_images() {
    echo -e "${YELLOW}Scanning images for vulnerabilities...${NC}"
    
    for image in sophia-backend sophia-frontend; do
        echo -e "${YELLOW}Scanning ${image}...${NC}"
        
        # Run Trivy scan
        if docker run --rm \
            -v /var/run/docker.sock:/var/run/docker.sock \
            -v ${HOME}/.cache/trivy:/root/.cache/trivy \
            aquasec/trivy:latest image \
            --severity CRITICAL \
            --exit-code 1 \
            --quiet \
            ${DOCKER_REGISTRY}/${image}:${IMAGE_TAG} 2>/dev/null; then
            echo -e "${GREEN}✅ ${image} passed security scan${NC}"
        else
            echo -e "${RED}❌ Critical vulnerabilities found in ${image}${NC}"
            echo -e "${YELLOW}Run detailed scan with: trivy image ${DOCKER_REGISTRY}/${image}:${IMAGE_TAG}${NC}"
            exit 1
        fi
    done
}

# Function to push images to registry
push_images() {
    echo -e "${YELLOW}Pushing images to registry...${NC}"
    
    # Login to Docker Hub
    echo -e "${YELLOW}Logging in to Docker Hub...${NC}"
    # Using the permanent secret management solution
    source backend/core/auto_esc_config.py
    docker login -u ${DOCKER_HUB_USERNAME} -p ${DOCKER_HUB_ACCESS_TOKEN}
    
    # Push images
    for image in sophia-backend sophia-frontend; do
        docker push ${DOCKER_REGISTRY}/${image}:${IMAGE_TAG}
        docker push ${DOCKER_REGISTRY}/${image}:latest
    done
    
    echo -e "${GREEN}✅ Images pushed to registry${NC}"
}

# Function to setup Kubernetes cluster
setup_kubernetes() {
    echo -e "${YELLOW}Setting up Kubernetes cluster...${NC}"
    
    # Initialize control plane on production instance
    CONTROL_PLANE_IP=${INSTANCES["production"]}
    
    echo -e "${YELLOW}Initializing control plane on ${CONTROL_PLANE_IP}...${NC}"
    ssh -i ${SSH_KEY} ubuntu@${CONTROL_PLANE_IP} << 'EOF'
        # Check if already initialized
        if kubectl get nodes &> /dev/null; then
            echo "Kubernetes already initialized"
        else
            # Initialize cluster
            sudo kubeadm init \
                --pod-network-cidr=10.244.0.0/16 \
                --apiserver-advertise-address=$(hostname -I | awk '{print $1}')
            
            # Setup kubectl
            mkdir -p $HOME/.kube
            sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
            sudo chown $(id -u):$(id -g) $HOME/.kube/config
            
            # Install Flannel
            kubectl apply -f https://github.com/flannel-io/flannel/releases/latest/download/kube-flannel.yml
            
            # Install GPU operator
            kubectl apply -f https://raw.githubusercontent.com/NVIDIA/gpu-operator/v23.9.1/deployments/gpu-operator.yaml
        fi
        
        # Generate join command
        kubeadm token create --print-join-command > /tmp/join-command.sh
EOF
    
    # Get join command
    JOIN_CMD=$(ssh -i ${SSH_KEY} ubuntu@${CONTROL_PLANE_IP} "cat /tmp/join-command.sh")
    
    # Join worker nodes
    for node in "ai-core" "mcp-orchestrator" "data-pipeline" "development"; do
        NODE_IP=${INSTANCES[$node]}
        echo -e "${YELLOW}Joining ${node} (${NODE_IP}) to cluster...${NC}"
        
        ssh -i ${SSH_KEY} ubuntu@${NODE_IP} << EOF
            # Check if already joined
            if systemctl is-active --quiet kubelet; then
                echo "Node already joined to cluster"
            else
                sudo ${JOIN_CMD}
            fi
EOF
    done
    
    echo -e "${GREEN}✅ Kubernetes cluster setup complete${NC}"
}

# Function to deploy applications
deploy_applications() {
    echo -e "${YELLOW}Deploying applications to Kubernetes...${NC}"
    
    # Get kubeconfig from control plane
    scp -i ${SSH_KEY} ubuntu@${INSTANCES["production"]}:~/.kube/config /tmp/kubeconfig
    export KUBECONFIG=/tmp/kubeconfig
    
    # Create namespace
    kubectl create namespace ${NAMESPACE} --dry-run=client -o yaml | kubectl apply -f -
    
    # Apply manifests
    echo -e "${YELLOW}Applying Kubernetes manifests...${NC}"
    
    # Update image tags in manifests
    find kubernetes/production -name "*.yaml" -exec sed -i \
        "s|image: ${DOCKER_REGISTRY}/\(.*\):.*|image: ${DOCKER_REGISTRY}/\1:${IMAGE_TAG}|g" {} \;
    
    # Apply in order
    kubectl apply -f kubernetes/production/namespace.yaml
    kubectl apply -f kubernetes/production/storage.yaml
    kubectl apply -f kubernetes/production/postgres-deployment.yaml
    kubectl apply -f kubernetes/production/redis-deployment.yaml
    kubectl apply -f kubernetes/production/sophia-backend-deployment.yaml
    kubectl apply -f kubernetes/production/frontend-deployment.yaml
    
    # Apply MCP servers
    for mcp in kubernetes/production/mcp-*.yaml; do
        kubectl apply -f $mcp
    done
    
    # Apply ingress
    kubectl apply -f kubernetes/production/ingress.yaml
    
    # Apply monitoring
    kubectl apply -f kubernetes/monitoring/
    
    echo -e "${GREEN}✅ Applications deployed${NC}"
}

# Function to verify deployment
verify_deployment() {
    echo -e "${YELLOW}Verifying deployment...${NC}"
    
    # Wait for deployments
    kubectl -n ${NAMESPACE} wait --for=condition=available --timeout=300s deployment --all
    
    # Check pod status
    echo -e "${YELLOW}Pod status:${NC}"
    kubectl -n ${NAMESPACE} get pods
    
    # Check services
    echo -e "${YELLOW}Service status:${NC}"
    kubectl -n ${NAMESPACE} get services
    
    # Check GPU allocation
    echo -e "${YELLOW}GPU allocation:${NC}"
    kubectl get nodes -o custom-columns=NAME:.metadata.name,GPU:.status.allocatable.nvidia\\.com/gpu
    
    # Get ingress IP
    INGRESS_IP=$(kubectl -n ${NAMESPACE} get ingress sophia-ingress -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
    
    echo -e "${GREEN}✅ Deployment verified${NC}"
    echo -e "${GREEN}Access the application at: http://${INGRESS_IP}${NC}"
}

# Main execution
main() {
    echo -e "${BLUE}Starting Sophia AI Kubernetes deployment...${NC}"
    
    check_prerequisites
    build_images
    scan_images
    push_images
    setup_kubernetes
    deploy_applications
    verify_deployment
    
    echo -e "${GREEN}✅ Deployment complete!${NC}"
    echo -e "${GREEN}Dashboard: http://${INSTANCES["production"]}${NC}"
    echo -e "${GREEN}API: http://${INSTANCES["production"]}:8000${NC}"
}

# Run main function
main "$@" 