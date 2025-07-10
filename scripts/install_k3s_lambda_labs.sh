#!/bin/bash
# Install K3s on Lambda Labs Instances with GPU Support
# Date: July 10, 2025

set -euo pipefail

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}🚀 Sophia AI K3s Installation Script${NC}"
echo "===================================="
echo "This script will install K3s on Lambda Labs instances with GPU support"
echo ""

# Configuration
K3S_VERSION="v1.28.3+k3s1"  # Stable version with GPU support
INSTANCE_TYPE="${1:-worker}"  # master or worker
MASTER_IP="${2:-}"           # Required for worker nodes

# Validate inputs
if [[ "$INSTANCE_TYPE" == "worker" && -z "$MASTER_IP" ]]; then
    echo -e "${RED}Error: Master IP required for worker installation${NC}"
    echo "Usage: $0 [master|worker] [master-ip-for-workers]"
    exit 1
fi

# Function to detect GPU
detect_gpu() {
    echo -e "${YELLOW}Detecting GPU...${NC}"
    if command -v nvidia-smi &> /dev/null; then
        nvidia-smi --query-gpu=name --format=csv,noheader | head -1
        return 0
    else
        echo "No GPU detected"
        return 1
    fi
}

# Function to install NVIDIA drivers if needed
install_nvidia_drivers() {
    if ! command -v nvidia-smi &> /dev/null; then
        echo -e "${YELLOW}Installing NVIDIA drivers...${NC}"
        sudo apt-get update
        sudo apt-get install -y nvidia-driver-525 nvidia-container-toolkit
        sudo systemctl restart docker
    else
        echo -e "${GREEN}NVIDIA drivers already installed${NC}"
    fi
}

# Function to install K3s master
install_k3s_master() {
    echo -e "${YELLOW}Installing K3s master node...${NC}"
    
    # Install K3s with specific configurations
    curl -sfL https://get.k3s.io | INSTALL_K3S_VERSION="$K3S_VERSION" \
        INSTALL_K3S_EXEC="server \
        --disable traefik \
        --write-kubeconfig-mode 644 \
        --node-label gpu-type=$(detect_gpu || echo 'none') \
        --node-label instance-type=master \
        --node-label sophia-role=control-plane" \
        sh -
    
    # Wait for K3s to be ready
    echo -e "${YELLOW}Waiting for K3s to be ready...${NC}"
    sudo k3s kubectl wait --for=condition=Ready node --all --timeout=300s
    
    # Get node token for workers
    echo -e "${GREEN}K3s master installation complete!${NC}"
    echo ""
    echo "Node token (save this for worker nodes):"
    sudo cat /var/lib/rancher/k3s/server/node-token
    echo ""
    echo "Master IP: $(hostname -I | awk '{print $1}')"
}

# Function to install K3s worker
install_k3s_worker() {
    echo -e "${YELLOW}Installing K3s worker node...${NC}"
    
    # Get token from user or environment
    if [[ -z "${K3S_TOKEN:-}" ]]; then
        echo "Enter the node token from master:"
        read -r K3S_TOKEN
    fi
    
    # Install K3s worker
    curl -sfL https://get.k3s.io | INSTALL_K3S_VERSION="$K3S_VERSION" \
        K3S_URL="https://${MASTER_IP}:6443" \
        K3S_TOKEN="$K3S_TOKEN" \
        INSTALL_K3S_EXEC="agent \
        --node-label gpu-type=$(detect_gpu || echo 'none') \
        --node-label instance-type=worker \
        --node-label sophia-role=compute" \
        sh -
    
    echo -e "${GREEN}K3s worker installation complete!${NC}"
}

# Function to install GPU support
install_gpu_support() {
    if detect_gpu; then
        echo -e "${YELLOW}Installing NVIDIA device plugin for Kubernetes...${NC}"
        
        # Only install on master or if kubectl is available
        if command -v kubectl &> /dev/null || [[ "$INSTANCE_TYPE" == "master" ]]; then
            # Create NVIDIA device plugin
            cat <<EOF | sudo k3s kubectl apply -f -
apiVersion: v1
kind: Namespace
metadata:
  name: nvidia-device-plugin
---
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: nvidia-device-plugin-daemonset
  namespace: nvidia-device-plugin
spec:
  selector:
    matchLabels:
      name: nvidia-device-plugin-ds
  updateStrategy:
    type: RollingUpdate
  template:
    metadata:
      labels:
        name: nvidia-device-plugin-ds
    spec:
      tolerations:
      - key: nvidia.com/gpu
        operator: Exists
        effect: NoSchedule
      priorityClassName: "system-node-critical"
      runtimeClassName: nvidia
      containers:
      - image: nvcr.io/nvidia/k8s-device-plugin:v0.14.1
        name: nvidia-device-plugin-ctr
        env:
        - name: FAIL_ON_INIT_ERROR
          value: "false"
        securityContext:
          allowPrivilegeEscalation: false
          capabilities:
            drop: ["ALL"]
        volumeMounts:
        - name: device-plugin
          mountPath: /var/lib/kubelet/device-plugins
      volumes:
      - name: device-plugin
        hostPath:
          path: /var/lib/kubelet/device-plugins
EOF
            
            # Create RuntimeClass for NVIDIA
            cat <<EOF | sudo k3s kubectl apply -f -
apiVersion: node.k8s.io/v1
kind: RuntimeClass
metadata:
  name: nvidia
handler: nvidia
EOF
            
            echo -e "${GREEN}GPU support installed successfully!${NC}"
        else
            echo -e "${YELLOW}GPU support will be configured from master node${NC}"
        fi
    fi
}

# Function to setup K3s for MCP servers
setup_mcp_namespace() {
    if [[ "$INSTANCE_TYPE" == "master" ]]; then
        echo -e "${YELLOW}Setting up MCP namespace and configurations...${NC}"
        
        cat <<EOF | sudo k3s kubectl apply -f -
apiVersion: v1
kind: Namespace
metadata:
  name: sophia-ai
  labels:
    app: sophia-ai
    environment: production
---
apiVersion: v1
kind: Namespace
metadata:
  name: sophia-mcp
  labels:
    app: sophia-mcp
    tier: microservices
EOF
        
        echo -e "${GREEN}MCP namespaces created!${NC}"
    fi
}

# Function to verify installation
verify_installation() {
    echo -e "${YELLOW}Verifying K3s installation...${NC}"
    
    # Check K3s service
    if systemctl is-active --quiet k3s || systemctl is-active --quiet k3s-agent; then
        echo -e "${GREEN}✓ K3s service is running${NC}"
    else
        echo -e "${RED}✗ K3s service is not running${NC}"
        return 1
    fi
    
    # Check GPU if available
    if detect_gpu > /dev/null; then
        if [[ "$INSTANCE_TYPE" == "master" ]] || command -v kubectl &> /dev/null; then
            echo -e "${YELLOW}Checking GPU availability in K3s...${NC}"
            sudo k3s kubectl describe nodes | grep -i nvidia || true
        fi
    fi
    
    echo -e "${GREEN}Installation verification complete!${NC}"
}

# Main installation flow
main() {
    echo -e "${YELLOW}Starting K3s installation for ${INSTANCE_TYPE} node...${NC}"
    echo "Instance type: $INSTANCE_TYPE"
    
    # Update system
    echo -e "${YELLOW}Updating system packages...${NC}"
    sudo apt-get update
    sudo apt-get upgrade -y
    
    # Install prerequisites
    echo -e "${YELLOW}Installing prerequisites...${NC}"
    sudo apt-get install -y curl wget apt-transport-https ca-certificates software-properties-common
    
    # Install NVIDIA drivers if GPU present
    if detect_gpu > /dev/null; then
        install_nvidia_drivers
    fi
    
    # Install K3s based on node type
    if [[ "$INSTANCE_TYPE" == "master" ]]; then
        install_k3s_master
        install_gpu_support
        setup_mcp_namespace
    else
        install_k3s_worker
    fi
    
    # Verify installation
    verify_installation
    
    echo ""
    echo -e "${GREEN}🎉 K3s installation complete!${NC}"
    echo ""
    echo "Next steps:"
    if [[ "$INSTANCE_TYPE" == "master" ]]; then
        echo "1. Save the node token for worker installations"
        echo "2. Configure kubectl: export KUBECONFIG=/etc/rancher/k3s/k3s.yaml"
        echo "3. Deploy MCP servers using: kubectl apply -f k3s/"
    else
        echo "1. Verify worker joined cluster from master node"
        echo "2. Check GPU availability: kubectl describe node $(hostname)"
    fi
}

# Run main function
main 