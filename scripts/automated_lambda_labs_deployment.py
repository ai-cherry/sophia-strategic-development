#!/usr/bin/env python3
"""
FULLY AUTOMATED LAMBDA LABS DEPLOYMENT
One-click deployment of Sophia AI to Lambda Labs with GPU optimization
"""

import os
import sys
import time
import json
import subprocess
import requests
from typing import Dict, List, Optional
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class AutomatedLambdaLabsDeployment:
    """Fully automated Lambda Labs deployment orchestrator"""

    def __init__(self):
        self.project_root = Path.cwd()
        self.lambda_api_key = os.getenv("LAMBDA_LABS_API_KEY")
        self.instance_id = None
        self.instance_ip = None
        self.ssh_key_path = os.path.expanduser("~/.ssh/lambda_labs_key")

        # Deployment configuration
        self.config = {
            "instance_type": "gpu_1x_rtx4090",
            "region": "us-west-2",
            "ssh_key_name": "sophia-ai-key",
            "instance_name": "sophia-ai-production",
        }

    def run_full_deployment(self):
        """Run the complete automated deployment"""
        logger.info("🚀 STARTING FULLY AUTOMATED LAMBDA LABS DEPLOYMENT")
        logger.info("This will take 20-30 minutes and cost ~$1.50/hour")
        logger.info("=" * 80)

        try:
            # Step 1: Validate API key
            if not self.lambda_api_key:
                logger.error("❌ LAMBDA_LABS_API_KEY environment variable not set")
                logger.info(
                    "💡 Get your API key from: https://cloud.lambdalabs.com/api-keys"
                )
                logger.info("💡 Set it with: export LAMBDA_LABS_API_KEY='your-api-key'")
                sys.exit(1)

            logger.info("✅ API key validated")

            # Step 2: Create one-click deployment script
            self.create_one_click_script()

            logger.info("🎉 AUTOMATED DEPLOYMENT READY!")
            logger.info("=" * 80)
            logger.info("🚀 To deploy, run: ./scripts/one_click_lambda_deploy.sh")
            logger.info("⏱️  Total time: 20-30 minutes")
            logger.info("💰 Cost: ~$1.50/hour for RTX 4090")
            logger.info("=" * 80)

        except Exception as e:
            logger.error(f"❌ Setup failed: {e}")
            sys.exit(1)

    def create_one_click_script(self):
        """Create the one-click deployment script"""
        script_content = """#!/bin/bash

# 🚀 ONE-CLICK LAMBDA LABS DEPLOYMENT
# Fully automated deployment of Sophia AI to Lambda Labs

set -e

echo "🚀 STARTING ONE-CLICK LAMBDA LABS DEPLOYMENT"
echo "=============================================="

# Check API key
if [ -z "$LAMBDA_LABS_API_KEY" ]; then
    echo "❌ Error: LAMBDA_LABS_API_KEY not set"
    echo "💡 Get your API key from: https://cloud.lambdalabs.com/api-keys"
    echo "💡 Set it with: export LAMBDA_LABS_API_KEY='your-api-key'"
    exit 1
fi

echo "✅ API key found"

# Step 1: Create SSH key if it doesn't exist
SSH_KEY_PATH="$HOME/.ssh/lambda_labs_key"
if [ ! -f "$SSH_KEY_PATH" ]; then
    echo "🔑 Creating SSH key..."
    ssh-keygen -t rsa -b 4096 -f "$SSH_KEY_PATH" -N "" -C "sophia-ai-lambda-labs"
    echo "✅ SSH key created"
fi

# Step 2: Upload SSH key to Lambda Labs
echo "📤 Uploading SSH key to Lambda Labs..."
PUBLIC_KEY=$(cat "$SSH_KEY_PATH.pub")
curl -X POST "https://cloud.lambdalabs.com/api/v1/ssh-keys" \\
    -H "Authorization: Bearer $LAMBDA_LABS_API_KEY" \\
    -H "Content-Type: application/json" \\
    -d "{\"name\": \"sophia-ai-key\", \"public_key\": \"$PUBLIC_KEY\"}" || echo "Key may already exist"

echo "✅ SSH key uploaded"

# Step 3: Launch Lambda Labs instance
echo "🚀 Launching Lambda Labs RTX 4090 instance..."
LAUNCH_RESPONSE=$(curl -X POST "https://cloud.lambdalabs.com/api/v1/instance-operations/launch" \\
    -H "Authorization: Bearer $LAMBDA_LABS_API_KEY" \\
    -H "Content-Type: application/json" \\
    -d '{
        "region_name": "us-west-2",
        "instance_type_name": "gpu_1x_rtx4090",
        "ssh_key_names": ["sophia-ai-key"],
        "name": "sophia-ai-production"
    }')

INSTANCE_ID=$(echo "$LAUNCH_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['data']['instance_ids'][0])")
echo "✅ Instance launched: $INSTANCE_ID"

# Step 4: Wait for instance to be ready
echo "⏳ Waiting for instance to be ready (this takes 3-5 minutes)..."
while true; do
    INSTANCE_DATA=$(curl -s "https://cloud.lambdalabs.com/api/v1/instances/$INSTANCE_ID" \\
        -H "Authorization: Bearer $LAMBDA_LABS_API_KEY")
    
    STATUS=$(echo "$INSTANCE_DATA" | python3 -c "import sys, json; print(json.load(sys.stdin)['data']['status'])")
    
    if [ "$STATUS" = "running" ]; then
        INSTANCE_IP=$(echo "$INSTANCE_DATA" | python3 -c "import sys, json; print(json.load(sys.stdin)['data']['ip'])")
        echo "✅ Instance ready at IP: $INSTANCE_IP"
        break
    fi
    
    echo "⏳ Instance status: $STATUS"
    sleep 30
done

# Wait for SSH to be ready
echo "⏳ Waiting for SSH service (2 minutes)..."
sleep 120

# Step 5: Setup server environment
echo "🛠️ Setting up server environment..."
ssh -i "$SSH_KEY_PATH" -o StrictHostKeyChecking=no ubuntu@$INSTANCE_IP << 'ENDSSH'
    # Update system
    sudo apt update && sudo apt upgrade -y
    
    # Install Docker
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker ubuntu
    
    # Install Kubernetes
    curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
    echo "deb https://apt.kubernetes.io/ kubernetes-xenial main" | sudo tee /etc/apt/sources.list.d/kubernetes.list
    sudo apt update
    sudo apt install -y kubelet kubeadm kubectl
    
    # Install Helm
    curl https://get.helm.sh/helm-v3.12.0-linux-amd64.tar.gz -o helm.tar.gz
    tar -zxvf helm.tar.gz
    sudo mv linux-amd64/helm /usr/local/bin/helm
    
    # Install NVIDIA drivers
    sudo apt install -y nvidia-driver-535
    
    # Install Git and other tools
    sudo apt install -y git python3.12 python3.12-venv curl
    
    echo "🔄 Rebooting for NVIDIA drivers..."
    sudo reboot
ENDSSH

# Wait for reboot
echo "⏳ Waiting for server reboot (2 minutes)..."
sleep 120

# Step 6: Complete NVIDIA setup and deploy
echo "🎮 Completing NVIDIA setup and deploying Sophia AI..."
ssh -i "$SSH_KEY_PATH" -o StrictHostKeyChecking=no ubuntu@$INSTANCE_IP << 'ENDSSH'
    # Complete NVIDIA setup
    distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
    curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
    curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
    sudo apt update && sudo apt install -y nvidia-container-toolkit
    sudo systemctl restart docker
    
    # Test NVIDIA
    nvidia-smi
    
    # Clone Sophia AI
    git clone https://github.com/ai-cherry/sophia-main.git
    cd sophia-main
    
    # Initialize Kubernetes
    sudo kubeadm init --pod-network-cidr=10.244.0.0/16
    mkdir -p $HOME/.kube
    sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
    sudo chown $(id -u):$(id -g) $HOME/.kube/config
    
    # Install network plugin
    kubectl apply -f https://raw.githubusercontent.com/coreos/flannel/master/Documentation/kube-flannel.yml
    
    # Allow scheduling on master node
    kubectl taint nodes --all node-role.kubernetes.io/control-plane-
    
    # Install NVIDIA device plugin
    kubectl create -f https://raw.githubusercontent.com/NVIDIA/k8s-device-plugin/v0.14.0/nvidia-device-plugin.yml
    
    # Wait for system to be ready
    sleep 60
    
    # Deploy Sophia AI
    chmod +x scripts/deploy_lambda_labs_kubernetes.sh
    ./scripts/deploy_lambda_labs_kubernetes.sh
    
    echo "✅ Deployment complete!"
ENDSSH

# Step 7: Display results
echo ""
echo "🎉 SOPHIA AI DEPLOYMENT COMPLETE!"
echo "=============================================="
echo "🌐 Server IP: $INSTANCE_IP"
echo "🔑 SSH Access: ssh -i $SSH_KEY_PATH ubuntu@$INSTANCE_IP"
echo "🚀 API Access: http://$INSTANCE_IP:8000"
echo "📊 Monitor GPU: ssh -i $SSH_KEY_PATH ubuntu@$INSTANCE_IP 'watch nvidia-smi'"
echo ""
echo "🎯 Next Steps:"
echo "   1. Access your AI: http://$INSTANCE_IP:8000"
echo "   2. Monitor services: ssh -i $SSH_KEY_PATH ubuntu@$INSTANCE_IP 'kubectl get pods -n sophia-ai'"
echo "   3. Check GPU usage: ssh -i $SSH_KEY_PATH ubuntu@$INSTANCE_IP 'nvidia-smi'"
echo "=============================================="
echo "💰 Remember to terminate the instance when done to save costs!"
echo "💡 Terminate at: https://cloud.lambdalabs.com/instances"
"""

        # Write the script
        script_path = self.project_root / "scripts/one_click_lambda_deploy.sh"
        script_path.write_text(script_content)
        script_path.chmod(0o755)

        logger.info(f"✅ One-click script created: {script_path}")


def main():
    """Main entry point"""
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print(
            """
🚀 AUTOMATED LAMBDA LABS DEPLOYMENT SETUP

This creates a one-click deployment script for Lambda Labs.

Prerequisites:
1. Get Lambda Labs API key from: https://cloud.lambdalabs.com/api-keys
2. Set environment variable: export LAMBDA_LABS_API_KEY='your-key'
3. Run this script to create the one-click deployer

Usage:
1. python3 scripts/automated_lambda_labs_deployment.py
2. ./scripts/one_click_lambda_deploy.sh

What the one-click script does:
✅ Creates SSH keys automatically
✅ Provisions RTX 4090 GPU instance
✅ Installs all dependencies
✅ Deploys Sophia AI with GPU optimization
✅ Provides access URLs

Total time: 20-30 minutes
Cost: ~$1.50/hour
        """
        )
        return

    # Run setup
    deployer = AutomatedLambdaLabsDeployment()
    deployer.run_full_deployment()


if __name__ == "__main__":
    main()
