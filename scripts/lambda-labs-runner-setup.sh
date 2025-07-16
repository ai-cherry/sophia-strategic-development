#!/bin/bash

# Lambda Labs GPU Runner Setup Script
# Optimized for Lambda Labs cloud instances with NVIDIA GPUs
# For ai-cherry organization GitHub Actions

set -e

# Configuration
ORGANIZATION="ai-cherry"
RUNNER_VERSION="2.321.0"
RUNNER_GROUP="production"
INSTANCE_TYPE=""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO: $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
    exit 1
}

# Detect Lambda Labs instance type and GPU configuration
detect_lambda_instance() {
    log "Detecting Lambda Labs instance configuration..."
    
    # Get GPU information
    if command -v nvidia-smi &> /dev/null; then
        GPU_COUNT=$(nvidia-smi --list-gpus | wc -l)
        GPU_NAME=$(nvidia-smi --query-gpu=name --format=csv,noheader,nounits | head -1)
        GPU_MEMORY=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits | head -1)
        
        info "Detected $GPU_COUNT x $GPU_NAME with ${GPU_MEMORY}MB memory each"
        
        # Determine instance type based on GPU configuration
        if echo "$GPU_NAME" | grep -qi "a100"; then
            if [ "$GPU_COUNT" -eq 1 ]; then
                INSTANCE_TYPE="1x-a100"
            elif [ "$GPU_COUNT" -eq 2 ]; then
                INSTANCE_TYPE="2x-a100"
            elif [ "$GPU_COUNT" -eq 4 ]; then
                INSTANCE_TYPE="4x-a100"
            elif [ "$GPU_COUNT" -eq 8 ]; then
                INSTANCE_TYPE="8x-a100"
            fi
        elif echo "$GPU_NAME" | grep -qi "h100"; then
            if [ "$GPU_COUNT" -eq 1 ]; then
                INSTANCE_TYPE="1x-h100"
            elif [ "$GPU_COUNT" -eq 8 ]; then
                INSTANCE_TYPE="8x-h100"
            fi
        elif echo "$GPU_NAME" | grep -qi "rtx"; then
            INSTANCE_TYPE="rtx-$(echo $GPU_NAME | grep -o 'RTX [0-9]*' | tr ' ' '-' | tr '[:upper:]' '[:lower:]')"
        fi
        
        # Set runner labels based on detected configuration
        RUNNER_LABELS="self-hosted,linux,x64,gpu,nvidia,lambda-labs,$INSTANCE_TYPE"
        
        if echo "$GPU_NAME" | grep -qi "a100"; then
            RUNNER_LABELS="$RUNNER_LABELS,a100"
        elif echo "$GPU_NAME" | grep -qi "h100"; then
            RUNNER_LABELS="$RUNNER_LABELS,h100"
        elif echo "$GPU_NAME" | grep -qi "rtx"; then
            RUNNER_LABELS="$RUNNER_LABELS,rtx"
        fi
        
        # Add memory-based labels
        if [ "$GPU_MEMORY" -gt 40000 ]; then
            RUNNER_LABELS="$RUNNER_LABELS,high-memory"
        fi
        
        log "Instance type: $INSTANCE_TYPE"
        log "Runner labels: $RUNNER_LABELS"
    else
        error "No NVIDIA GPU detected. This script is for GPU instances only."
    fi
}

# Install Lambda Labs optimized dependencies
install_lambda_dependencies() {
    log "Installing Lambda Labs optimized dependencies..."
    
    # Update system
    sudo apt-get update && sudo apt-get upgrade -y
    
    # Install essential packages
    sudo apt-get install -y \
        curl \
        wget \
        git \
        jq \
        unzip \
        tar \
        build-essential \
        python3 \
        python3-pip \
        python3-venv \
        htop \
        nvtop \
        tmux \
        screen
    
    # Install Docker with NVIDIA container runtime
    log "Installing Docker with NVIDIA container runtime..."
    
    # Remove old Docker versions
    sudo apt-get remove -y docker docker-engine docker.io containerd runc || true
    
    # Install Docker
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    
    # Install NVIDIA Container Toolkit
    distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
    curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
    curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
    
    sudo apt-get update
    sudo apt-get install -y nvidia-docker2
    sudo systemctl restart docker
    
    # Test NVIDIA Docker
    log "Testing NVIDIA Docker integration..."
    if sudo docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi; then
        log "NVIDIA Docker integration successful"
    else
        warn "NVIDIA Docker test failed, but continuing setup"
    fi
    
    # Install Python ML libraries
    log "Installing Python ML libraries..."
    pip3 install --user \
        torch \
        torchvision \
        torchaudio \
        transformers \
        accelerate \
        datasets \
        numpy \
        pandas \
        scikit-learn \
        matplotlib \
        jupyter \
        notebook
    
    log "Dependencies installation complete"
}

# Setup Lambda Labs specific optimizations
setup_lambda_optimizations() {
    log "Applying Lambda Labs specific optimizations..."
    
    # Set GPU performance mode
    sudo nvidia-smi -pm 1
    
    # Set maximum GPU clocks
    sudo nvidia-smi -ac $(nvidia-smi --query-supported-clocks=memory,graphics --format=csv,noheader,nounits | tail -1 | tr ',' ' ')
    
    # Create GPU monitoring script
    cat > ~/gpu-monitor.sh <<'EOF'
#!/bin/bash
# GPU monitoring script for Lambda Labs instances

LOGFILE="/var/log/github-runner/gpu-monitor.log"
mkdir -p $(dirname $LOGFILE)

while true; do
    echo "$(date): GPU Status:" >> $LOGFILE
    nvidia-smi --query-gpu=timestamp,name,temperature.gpu,utilization.gpu,utilization.memory,memory.used,memory.total --format=csv >> $LOGFILE
    echo "---" >> $LOGFILE
    sleep 60
done
EOF
    
    chmod +x ~/gpu-monitor.sh
    
    # Create systemd service for GPU monitoring
    sudo tee /etc/systemd/system/gpu-monitor.service > /dev/null <<EOF
[Unit]
Description=GPU Monitoring Service
After=network.target

[Service]
Type=simple
User=$USER
ExecStart=$HOME/gpu-monitor.sh
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
    
    sudo systemctl enable gpu-monitor.service
    sudo systemctl start gpu-monitor.service
    
    # Setup automatic GPU memory cleanup
    cat > ~/cleanup-gpu-memory.sh <<'EOF'
#!/bin/bash
# Cleanup GPU memory between jobs

echo "$(date): Cleaning up GPU memory..." >> /var/log/github-runner/cleanup.log

# Kill any hanging Python processes
pkill -f python || true

# Clear GPU memory
if command -v nvidia-smi &> /dev/null; then
    nvidia-smi --gpu-reset || true
fi

# Clear system cache
sync && echo 3 | sudo tee /proc/sys/vm/drop_caches > /dev/null

echo "$(date): GPU memory cleanup complete" >> /var/log/github-runner/cleanup.log
EOF
    
    chmod +x ~/cleanup-gpu-memory.sh
    
    log "Lambda Labs optimizations applied"
}

# Configure runner for AI/ML workloads
configure_ml_runner() {
    log "Configuring runner for AI/ML workloads..."
    
    # Create ML workspace directory
    mkdir -p ~/ml-workspace/{models,datasets,checkpoints,logs}
    
    # Set environment variables for ML frameworks
    cat >> ~/.bashrc <<EOF

# AI/ML Environment Variables
export CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7
export TORCH_CUDA_ARCH_LIST="7.0;8.0;8.6"
export TRANSFORMERS_CACHE=~/ml-workspace/models
export HF_HOME=~/ml-workspace/models
export WANDB_CACHE_DIR=~/ml-workspace/logs
EOF
    
    # Create runner environment file
    cat > ~/actions-runner/.env <<EOF
# Lambda Labs Runner Environment
CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7
TORCH_CUDA_ARCH_LIST=7.0;8.0;8.6
TRANSFORMERS_CACHE=$HOME/ml-workspace/models
HF_HOME=$HOME/ml-workspace/models
WANDB_CACHE_DIR=$HOME/ml-workspace/logs
NVIDIA_VISIBLE_DEVICES=all
NVIDIA_DRIVER_CAPABILITIES=compute,utility
EOF
    
    log "ML runner configuration complete"
}

# Setup cost monitoring
setup_cost_monitoring() {
    log "Setting up cost monitoring..."
    
    # Create cost tracking script
    cat > ~/track-usage.sh <<'EOF'
#!/bin/bash
# Track instance usage for cost monitoring

LOGFILE="/var/log/github-runner/usage.log"
mkdir -p $(dirname $LOGFILE)

# Log instance start time
echo "$(date): Instance started" >> $LOGFILE

# Log GPU utilization every minute
while true; do
    GPU_UTIL=$(nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits | head -1)
    CPU_UTIL=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
    
    echo "$(date): GPU: ${GPU_UTIL}%, CPU: ${CPU_UTIL}%" >> $LOGFILE
    
    # If GPU utilization is 0 for extended period, log warning
    if [ "$GPU_UTIL" -eq 0 ]; then
        echo "$(date): WARNING: GPU idle - consider stopping instance to save costs" >> $LOGFILE
    fi
    
    sleep 60
done
EOF
    
    chmod +x ~/track-usage.sh
    
    # Start usage tracking in background
    nohup ~/track-usage.sh &
    
    log "Cost monitoring setup complete"
}

# Main execution function
main() {
    log "Starting Lambda Labs GPU runner setup for $ORGANIZATION..."
    
    # Check for required environment variables
    if [ -z "$GITHUB_TOKEN" ]; then
        error "GITHUB_TOKEN environment variable is required"
    fi
    
    detect_lambda_instance
    install_lambda_dependencies
    setup_lambda_optimizations
    configure_ml_runner
    setup_cost_monitoring
    
    # Run the main runner setup script
    log "Running main runner setup..."
    export RUNNER_LABELS
    export RUNNER_GROUP
    
    # Download and run the main setup script
    curl -s https://raw.githubusercontent.com/ai-cherry/sophia-main/main/scripts/setup-self-hosted-runner.sh | bash
    
    log "Lambda Labs GPU runner setup complete!"
    log "Instance type: $INSTANCE_TYPE"
    log "Runner labels: $RUNNER_LABELS"
    log "Monitor GPU usage: watch nvidia-smi"
    log "View logs: tail -f /var/log/github-runner/*.log"
    
    warn "Remember to stop the instance when not in use to minimize costs!"
}

# Execute main function
main "$@"

