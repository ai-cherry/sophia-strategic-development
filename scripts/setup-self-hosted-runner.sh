#!/bin/bash

# Self-hosted GitHub Actions Runner Setup Script
# For ai-cherry organization
# Supports both Lambda Labs GPU instances and standard Linux servers

set -e

# Configuration
ORGANIZATION="ai-cherry"
RUNNER_VERSION="2.321.0"
RUNNER_GROUP="production"  # or "development"
RUNNER_LABELS="self-hosted,linux,x64"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
    exit 1
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   error "This script should not be run as root for security reasons"
fi

# Check for required parameters
if [ -z "$GITHUB_TOKEN" ]; then
    error "GITHUB_TOKEN environment variable is required"
fi

# Detect GPU capabilities
detect_gpu() {
    if command -v nvidia-smi &> /dev/null; then
        GPU_INFO=$(nvidia-smi --query-gpu=name --format=csv,noheader,nounits | head -1)
        log "GPU detected: $GPU_INFO"
        RUNNER_LABELS="$RUNNER_LABELS,gpu,nvidia"
        
        # Check for specific GPU types
        if echo "$GPU_INFO" | grep -qi "a100"; then
            RUNNER_LABELS="$RUNNER_LABELS,a100"
        elif echo "$GPU_INFO" | grep -qi "h100"; then
            RUNNER_LABELS="$RUNNER_LABELS,h100"
        elif echo "$GPU_INFO" | grep -qi "rtx"; then
            RUNNER_LABELS="$RUNNER_LABELS,rtx"
        fi
    else
        log "No GPU detected, setting up CPU-only runner"
        RUNNER_LABELS="$RUNNER_LABELS,cpu-only"
    fi
}

# Install dependencies
install_dependencies() {
    log "Installing dependencies..."
    
    # Update package list
    sudo apt-get update
    
    # Install required packages
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
        docker.io \
        docker-compose
    
    # Add user to docker group
    sudo usermod -aG docker $USER
    
    # Install Docker Compose v2
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    
    log "Dependencies installed successfully"
}

# Download and configure GitHub Actions runner
setup_runner() {
    log "Setting up GitHub Actions runner..."
    
    # Create runner directory
    mkdir -p ~/actions-runner
    cd ~/actions-runner
    
    # Download the latest runner package
    log "Downloading GitHub Actions runner v$RUNNER_VERSION..."
    curl -o actions-runner-linux-x64-$RUNNER_VERSION.tar.gz -L \
        https://github.com/actions/runner/releases/download/v$RUNNER_VERSION/actions-runner-linux-x64-$RUNNER_VERSION.tar.gz
    
    # Extract the installer
    tar xzf ./actions-runner-linux-x64-$RUNNER_VERSION.tar.gz
    
    # Get registration token
    log "Getting registration token..."
    REGISTRATION_TOKEN=$(curl -s -X POST \
        -H "Authorization: token $GITHUB_TOKEN" \
        -H "Accept: application/vnd.github.v3+json" \
        "https://api.github.com/orgs/$ORGANIZATION/actions/runners/registration-token" | jq -r .token)
    
    if [ "$REGISTRATION_TOKEN" = "null" ] || [ -z "$REGISTRATION_TOKEN" ]; then
        error "Failed to get registration token. Check your GitHub token permissions."
    fi
    
    # Configure the runner
    log "Configuring runner with labels: $RUNNER_LABELS"
    ./config.sh \
        --url "https://github.com/$ORGANIZATION" \
        --token "$REGISTRATION_TOKEN" \
        --name "$(hostname)-$(date +%s)" \
        --runnergroup "$RUNNER_GROUP" \
        --labels "$RUNNER_LABELS" \
        --work "_work" \
        --replace \
        --unattended
    
    log "Runner configured successfully"
}

# Install runner as a service
install_service() {
    log "Installing runner as a system service..."
    
    cd ~/actions-runner
    sudo ./svc.sh install
    sudo ./svc.sh start
    
    # Enable service to start on boot
    sudo systemctl enable actions.runner.$ORGANIZATION.$(hostname)-*.service
    
    log "Runner service installed and started"
}

# Setup monitoring and logging
setup_monitoring() {
    log "Setting up monitoring and logging..."
    
    # Create log directory
    sudo mkdir -p /var/log/github-runner
    sudo chown $USER:$USER /var/log/github-runner
    
    # Setup log rotation
    sudo tee /etc/logrotate.d/github-runner > /dev/null <<EOF
/var/log/github-runner/*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    copytruncate
}
EOF
    
    # Create monitoring script
    cat > ~/monitor-runner.sh <<'EOF'
#!/bin/bash
# Simple runner monitoring script

LOGFILE="/var/log/github-runner/monitor.log"
SERVICE_NAME=$(systemctl list-units --type=service | grep "actions.runner" | awk '{print $1}' | head -1)

if [ -z "$SERVICE_NAME" ]; then
    echo "$(date): No GitHub runner service found" >> $LOGFILE
    exit 1
fi

if ! systemctl is-active --quiet $SERVICE_NAME; then
    echo "$(date): Runner service $SERVICE_NAME is not running, attempting restart" >> $LOGFILE
    sudo systemctl restart $SERVICE_NAME
    sleep 10
    if systemctl is-active --quiet $SERVICE_NAME; then
        echo "$(date): Runner service $SERVICE_NAME restarted successfully" >> $LOGFILE
    else
        echo "$(date): Failed to restart runner service $SERVICE_NAME" >> $LOGFILE
    fi
else
    echo "$(date): Runner service $SERVICE_NAME is running normally" >> $LOGFILE
fi
EOF
    
    chmod +x ~/monitor-runner.sh
    
    # Add to crontab for monitoring every 5 minutes
    (crontab -l 2>/dev/null; echo "*/5 * * * * $HOME/monitor-runner.sh") | crontab -
    
    log "Monitoring setup complete"
}

# Main execution
main() {
    log "Starting GitHub Actions self-hosted runner setup..."
    log "Organization: $ORGANIZATION"
    log "Runner Group: $RUNNER_GROUP"
    
    detect_gpu
    install_dependencies
    setup_runner
    install_service
    setup_monitoring
    
    log "Setup complete! Runner is now active and will appear in GitHub Actions."
    log "Monitor the runner status at: https://github.com/organizations/$ORGANIZATION/settings/actions/runners"
    
    warn "Please log out and log back in for Docker group membership to take effect."
    warn "Or run 'newgrp docker' to activate Docker access in current session."
}

# Run main function
main "$@"

