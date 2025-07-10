#!/usr/bin/env python3
"""
Set up K3s deployment configuration for Sophia AI.

This script prepares the deployment configuration for the K3s cluster
on Lambda Labs, including kubeconfig setup instructions and deployment validation.
"""

import os
import yaml
from pathlib import Path
from datetime import datetime
import logging
import subprocess

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

class K3sDeploymentSetup:
    def __init__(self):
        self.root_dir = Path.cwd()
        self.k8s_dir = self.root_dir / "kubernetes"
        self.lambda_labs_ip = "192.222.58.232"
        
    def validate_yaml_files(self):
        """Validate all YAML files are properly formatted."""
        logger.info("🔍 Validating YAML files...")
        
        yaml_files = list(self.k8s_dir.rglob("*.yaml")) + list(self.k8s_dir.rglob("*.yml"))
        errors = []
        
        for yaml_file in yaml_files:
            try:
                with open(yaml_file, 'r') as f:
                    yaml.safe_load_all(f)
                logger.info(f"✅ Valid: {yaml_file.relative_to(self.root_dir)}")
            except yaml.YAMLError as e:
                error_msg = f"❌ Invalid: {yaml_file.relative_to(self.root_dir)} - {e}"
                logger.error(error_msg)
                errors.append(error_msg)
                
        return len(errors) == 0
        
    def generate_deployment_script(self):
        """Generate deployment script for GitHub Actions."""
        deployment_script = f"""#!/bin/bash
# Sophia AI K3s Deployment Script
# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

set -e

echo "🚀 Starting Sophia AI K3s deployment..."

# Configuration
K3S_SERVER="{self.lambda_labs_ip}"
NAMESPACE="sophia-ai-prod"

# Check if kubectl is configured
if ! kubectl cluster-info > /dev/null 2>&1; then
    echo "❌ kubectl not configured. Please set up kubeconfig first."
    exit 1
fi

# Create namespace if it doesn't exist
echo "📦 Creating namespace..."
kubectl apply -f kubernetes/base/namespace.yaml

# Apply base configuration
echo "🔧 Applying base configuration..."
kubectl apply -k kubernetes/base

# Wait for deployments to be ready
echo "⏳ Waiting for deployments to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment --all -n $NAMESPACE

# Check deployment status
echo "✅ Deployment status:"
kubectl get all -n $NAMESPACE

echo "🎉 Deployment complete!"
"""
        
        script_path = self.root_dir / ".github" / "scripts" / "deploy-k3s.sh"
        script_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(script_path, 'w') as f:
            f.write(deployment_script)
            
        # Make executable
        os.chmod(script_path, 0o755)
        logger.info(f"📝 Created deployment script: {script_path.relative_to(self.root_dir)}")
        
    def generate_github_action(self):
        """Generate GitHub Actions workflow for K3s deployment."""
        workflow = {
            "name": "Deploy to K3s",
            "on": {
                "push": {
                    "branches": ["main"]
                },
                "workflow_dispatch": {}
            },
            "env": {
                "DOCKER_REGISTRY": "scoobyjava15",
                "K3S_SERVER": self.lambda_labs_ip
            },
            "jobs": {
                "deploy": {
                    "runs-on": "ubuntu-latest",
                    "steps": [
                        {
                            "name": "Checkout code",
                            "uses": "actions/checkout@v4"
                        },
                        {
                            "name": "Set up Docker Buildx",
                            "uses": "docker/setup-buildx-action@v3"
                        },
                        {
                            "name": "Log in to Docker Hub",
                            "uses": "docker/login-action@v3",
                            "with": {
                                "username": "${{ secrets.DOCKER_HUB_USERNAME }}",
                                "password": "${{ secrets.DOCKER_HUB_ACCESS_TOKEN }}"
                            }
                        },
                        {
                            "name": "Build and push API image",
                            "uses": "docker/build-push-action@v5",
                            "with": {
                                "context": ".",
                                "file": "backend/Dockerfile",
                                "push": True,
                                "tags": "${{ env.DOCKER_REGISTRY }}/sophia-api:${{ github.sha }},${{ env.DOCKER_REGISTRY }}/sophia-api:latest",
                                "platforms": "linux/amd64"
                            }
                        },
                        {
                            "name": "Set up kubectl",
                            "uses": "azure/setup-kubectl@v3",
                            "with": {
                                "version": "v1.28.0"
                            }
                        },
                        {
                            "name": "Configure kubectl",
                            "run": """echo "${{ secrets.LAMBDA_LABS_KUBECONFIG }}" | base64 -d > kubeconfig
export KUBECONFIG=kubeconfig"""
                        },
                        {
                            "name": "Update deployment image",
                            "run": f"""kubectl set image deployment/sophia-api sophia-api=${{{{ env.DOCKER_REGISTRY }}}}/sophia-api:${{{{ github.sha }}}} -n sophia-ai-prod
kubectl rollout status deployment/sophia-api -n sophia-ai-prod"""
                        }
                    ]
                }
            }
        }
        
        workflow_path = self.root_dir / ".github" / "workflows" / "deploy-k3s.yml"
        with open(workflow_path, 'w') as f:
            yaml.dump(workflow, f, default_flow_style=False, sort_keys=False)
            
        logger.info(f"📝 Created GitHub Actions workflow: {workflow_path.relative_to(self.root_dir)}")
        
    def create_setup_instructions(self):
        """Create setup instructions for K3s deployment."""
        instructions = f"""# K3s Deployment Setup Instructions

## Prerequisites

1. **Lambda Labs Access**
   - Server IP: {self.lambda_labs_ip}
   - SSH access configured
   - K3s installed and running

2. **Local Prerequisites**
   - kubectl installed
   - SSH key for Lambda Labs

## Setup Steps

### 1. Get K3s Kubeconfig

SSH into Lambda Labs and get the kubeconfig:

```bash
ssh user@{self.lambda_labs_ip}
sudo cat /etc/rancher/k3s/k3s.yaml
```

### 2. Configure Local kubectl

Save the kubeconfig locally and update the server address:

```bash
# Create .kube directory
mkdir -p ~/.kube

# Save kubeconfig (paste the content from step 1)
cat > ~/.kube/k3s-lambda-labs

# Update the server address in the file
# Change server: https://127.0.0.1:6443
# To: server: https://{self.lambda_labs_ip}:6443

# Set KUBECONFIG environment variable
export KUBECONFIG=~/.kube/k3s-lambda-labs
```

### 3. Test Connection

```bash
kubectl cluster-info
kubectl get nodes
```

### 4. Deploy Sophia AI

```bash
# Deploy using kustomize
kubectl apply -k kubernetes/overlays/production

# Check deployment
kubectl get all -n sophia-ai-prod
```

## GitHub Actions Setup

Add these secrets to your GitHub repository:

1. **DOCKER_HUB_USERNAME**: Your Docker Hub username
2. **DOCKER_HUB_ACCESS_TOKEN**: Docker Hub access token
3. **LAMBDA_LABS_KUBECONFIG**: Base64 encoded kubeconfig
   ```bash
   cat ~/.kube/k3s-lambda-labs | base64
   ```

## Monitoring

Check deployment status:
```bash
kubectl get pods -n sophia-ai-prod
kubectl logs -f deployment/sophia-api -n sophia-ai-prod
```

## Troubleshooting

If pods are not starting:
```bash
kubectl describe pod <pod-name> -n sophia-ai-prod
kubectl get events -n sophia-ai-prod
```
"""
        
        instructions_path = self.root_dir / "docs" / "deployment" / "K3S_DEPLOYMENT_SETUP.md"
        instructions_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(instructions_path, 'w') as f:
            f.write(instructions)
            
        logger.info(f"📝 Created setup instructions: {instructions_path.relative_to(self.root_dir)}")
        
    def run(self):
        """Run the K3s deployment setup."""
        logger.info("🚀 Starting K3s deployment setup...")
        
        # Validate YAML files
        if not self.validate_yaml_files():
            logger.error("❌ YAML validation failed. Please fix errors before proceeding.")
            return
            
        # Generate deployment script
        self.generate_deployment_script()
        
        # Generate GitHub Actions workflow
        self.generate_github_action()
        
        # Create setup instructions
        self.create_setup_instructions()
        
        logger.info("\n✨ K3s deployment setup complete!")
        
        print("\n" + "="*60)
        print("K3S DEPLOYMENT SETUP COMPLETE")
        print("="*60)
        print("\n✅ Generated:")
        print("  - Deployment script: .github/scripts/deploy-k3s.sh")
        print("  - GitHub Actions workflow: .github/workflows/deploy-k3s.yml")
        print("  - Setup instructions: docs/deployment/K3S_DEPLOYMENT_SETUP.md")
        print("\n📋 Next Steps:")
        print("  1. Follow setup instructions to configure kubectl")
        print("  2. Add required secrets to GitHub repository")
        print("  3. Push to main branch to trigger deployment")
        print("\n" + "="*60)

if __name__ == "__main__":
    setup = K3sDeploymentSetup()
    setup.run() 