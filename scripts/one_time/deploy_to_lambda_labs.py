#!/usr/bin/env python3
"""
Deploy Sophia AI to Lambda Labs Infrastructure
Complete deployment with SSL, services, and monitoring
"""

import os
import sys
import subprocess
import json
import time
from typing import Dict, Any, List
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LambdaLabsDeployer:
    """Deploy Sophia AI to Lambda Labs infrastructure"""
    
    def __init__(self):
        self.servers = {
            "primary": {
                "ip": "192.222.58.232",
                "gpu": "GH200",
                "purpose": "Main API + Frontend",
                "services": ["backend-api", "frontend", "nginx"]
            },
            "mcp_orchestrator": {
                "ip": "104.171.202.117", 
                "gpu": "A6000",
                "purpose": "MCP Services + Webhooks",
                "services": ["mcp-servers", "webhooks", "k3s"]
            },
            "data_pipeline": {
                "ip": "104.171.202.134",
                "gpu": "A100", 
                "purpose": "Data Processing",
                "services": ["data-pipeline", "etl", "analytics"]
            },
            "development": {
                "ip": "155.248.194.183",
                "gpu": "A10",
                "purpose": "Development + Testing",
                "services": ["dev-backend", "dev-frontend", "testing"]
            }
        }
        
        self.domains = {
            "sophia-intel.ai": "primary",
            "api.sophia-intel.ai": "primary", 
            "app.sophia-intel.ai": "primary",
            "webhooks.sophia-intel.ai": "mcp_orchestrator",
            "mcp.sophia-intel.ai": "mcp_orchestrator",
            "data.sophia-intel.ai": "data_pipeline",
            "dev.sophia-intel.ai": "development"
        }

    def create_docker_images(self):
        """Build and push Docker images to Docker Hub"""
        logger.info("🐳 Building Docker images...")
        
        images = [
            {
                "name": "sophia-ai-backend",
                "dockerfile": "backend/Dockerfile",
                "context": ".",
                "tag": "scoobyjava15/sophia-ai-backend:latest"
            },
            {
                "name": "sophia-ai-frontend", 
                "dockerfile": "frontend/Dockerfile",
                "context": "frontend",
                "tag": "scoobyjava15/sophia-ai-frontend:latest"
            },
            {
                "name": "sophia-mcp-orchestrator",
                "dockerfile": "mcp-servers/Dockerfile",
                "context": "mcp-servers", 
                "tag": "scoobyjava15/sophia-mcp-orchestrator:latest"
            }
        ]
        
        for image in images:
            logger.info(f"Building {image['name']}...")
            
            # Build image
            build_cmd = [
                "docker", "build",
                "-f", image["dockerfile"],
                "-t", image["tag"],
                image["context"]
            ]
            
            try:
                result = subprocess.run(build_cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    logger.info(f"✅ Built {image['name']}")
                    
                    # Push to Docker Hub
                    push_cmd = ["docker", "push", image["tag"]]
                    push_result = subprocess.run(push_cmd, capture_output=True, text=True)
                    
                    if push_result.returncode == 0:
                        logger.info(f"✅ Pushed {image['name']} to Docker Hub")
                    else:
                        logger.error(f"❌ Failed to push {image['name']}: {push_result.stderr}")
                else:
                    logger.error(f"❌ Failed to build {image['name']}: {result.stderr}")
                    
            except Exception as e:
                logger.error(f"❌ Error building {image['name']}: {e}")

    def create_backend_dockerfile(self):
        """Create optimized Dockerfile for backend"""
        dockerfile_content = """
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    g++ \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variables
ENV PYTHONPATH=/app
ENV ENVIRONMENT=prod
ENV PULUMI_ORG=scoobyjava-org

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8000/health || exit 1

# Start application
CMD ["python", "-m", "uvicorn", "backend.app.simple_fastapi:app", "--host", "0.0.0.0", "--port", "8000"]
"""
        
        with open("backend/Dockerfile", "w") as f:
            f.write(dockerfile_content.strip())
        
        logger.info("✅ Created backend Dockerfile")

    def create_frontend_dockerfile(self):
        """Create optimized Dockerfile for frontend"""
        dockerfile_content = """
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./
RUN npm ci

# Copy source code and build
COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built files
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost/health || exit 1

CMD ["nginx", "-g", "daemon off;"]
"""
        
        with open("frontend/Dockerfile", "w") as f:
            f.write(dockerfile_content.strip())
        
        # Create nginx config
        nginx_config = """
events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    
    server {
        listen 80;
        server_name _;
        root /usr/share/nginx/html;
        index index.html;
        
        # Health check endpoint
        location /health {
            access_log off;
            return 200 "healthy\\n";
            add_header Content-Type text/plain;
        }
        
        # API proxy
        location /api/ {
            proxy_pass http://backend:8000/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        # Frontend routes
        location / {
            try_files $uri $uri/ /index.html;
        }
    }
}
"""
        
        with open("frontend/nginx.conf", "w") as f:
            f.write(nginx_config.strip())
        
        logger.info("✅ Created frontend Dockerfile and nginx config")

    def create_kubernetes_manifests(self):
        """Create Kubernetes deployment manifests"""
        
        # Backend deployment
        backend_manifest = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: sophia-backend
  namespace: sophia-ai-prod
spec:
  replicas: 3
  selector:
    matchLabels:
      app: sophia-backend
  template:
    metadata:
      labels:
        app: sophia-backend
    spec:
      containers:
      - name: backend
        image: scoobyjava15/sophia-ai-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: ENVIRONMENT
          value: "prod"
        - name: PULUMI_ORG
          value: "scoobyjava-org"
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: sophia-backend-service
  namespace: sophia-ai-prod
spec:
  selector:
    app: sophia-backend
  ports:
  - port: 8000
    targetPort: 8000
  type: ClusterIP
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: sophia-frontend
  namespace: sophia-ai-prod
spec:
  replicas: 2
  selector:
    matchLabels:
      app: sophia-frontend
  template:
    metadata:
      labels:
        app: sophia-frontend
    spec:
      containers:
      - name: frontend
        image: scoobyjava15/sophia-ai-frontend:latest
        ports:
        - containerPort: 80
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 80
          initialDelaySeconds: 30
          periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: sophia-frontend-service
  namespace: sophia-ai-prod
spec:
  selector:
    app: sophia-frontend
  ports:
  - port: 80
    targetPort: 80
  type: ClusterIP
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: sophia-ingress
  namespace: sophia-ai-prod
  annotations:
    kubernetes.io/ingress.class: "traefik"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    traefik.ingress.kubernetes.io/redirect-entry-point: https
spec:
  tls:
  - hosts:
    - sophia-intel.ai
    - api.sophia-intel.ai
    - app.sophia-intel.ai
    secretName: sophia-tls
  rules:
  - host: sophia-intel.ai
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: sophia-frontend-service
            port:
              number: 80
  - host: api.sophia-intel.ai
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: sophia-backend-service
            port:
              number: 8000
  - host: app.sophia-intel.ai
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: sophia-frontend-service
            port:
              number: 80
"""
        
        os.makedirs("k8s/production", exist_ok=True)
        with open("k8s/production/sophia-deployment.yaml", "w") as f:
            f.write(backend_manifest.strip())
        
        logger.info("✅ Created Kubernetes manifests")

    def create_deployment_scripts(self):
        """Create deployment scripts for each server"""
        
        # Primary server deployment script
        primary_script = """#!/bin/bash
set -e

echo "🚀 Deploying to Primary Production Server (192.222.58.232)"

# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker if not present
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
fi

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install K3s
curl -sfL https://get.k3s.io | sh -

# Install cert-manager for SSL
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Wait for cert-manager
kubectl wait --for=condition=Ready pods --all -n cert-manager --timeout=300s

# Create namespace
kubectl create namespace sophia-ai-prod --dry-run=client -o yaml | kubectl apply -f -

# Deploy Sophia AI
kubectl apply -f k8s/production/sophia-deployment.yaml

# Check deployment status
kubectl get pods -n sophia-ai-prod
kubectl get services -n sophia-ai-prod
kubectl get ingress -n sophia-ai-prod

echo "✅ Primary server deployment complete!"
echo "🌐 Access: https://sophia-intel.ai"
"""
        
        with open("scripts/deploy_primary_server.sh", "w") as f:
            f.write(primary_script.strip())
        
        os.chmod("scripts/deploy_primary_server.sh", 0o755)
        
        # MCP orchestrator deployment script
        mcp_script = """#!/bin/bash
set -e

echo "🚀 Deploying to MCP Orchestrator Server (104.171.202.117)"

# Install K3s if not present
if ! command -v k3s &> /dev/null; then
    curl -sfL https://get.k3s.io | sh -
fi

# Create MCP namespace
kubectl create namespace mcp-servers --dry-run=client -o yaml | kubectl apply -f -

# Deploy MCP servers
kubectl apply -f k8s/mcp-servers/

# Setup webhook handlers
kubectl apply -f k8s/webhooks/

echo "✅ MCP orchestrator deployment complete!"
echo "🔗 Webhooks: https://webhooks.sophia-intel.ai"
echo "🤖 MCP: https://mcp.sophia-intel.ai"
"""
        
        with open("scripts/deploy_mcp_server.sh", "w") as f:
            f.write(mcp_script.strip())
        
        os.chmod("scripts/deploy_mcp_server.sh", 0o755)
        
        logger.info("✅ Created deployment scripts")

    def create_ssl_setup_script(self):
        """Create SSL certificate setup script"""
        ssl_script = """#!/bin/bash
set -e

echo "🔒 Setting up SSL certificates with Let's Encrypt"

# Install certbot
sudo apt update
sudo apt install -y certbot python3-certbot-nginx

# Get certificates for all domains
sudo certbot --nginx -d sophia-intel.ai -d api.sophia-intel.ai -d app.sophia-intel.ai --agree-tos --no-eff-email --email admin@sophia-intel.ai

# Setup auto-renewal
sudo crontab -l | { cat; echo "0 12 * * * /usr/bin/certbot renew --quiet"; } | sudo crontab -

echo "✅ SSL certificates configured!"
echo "🔒 Auto-renewal setup complete"
"""
        
        with open("scripts/setup_ssl.sh", "w") as f:
            f.write(ssl_script.strip())
        
        os.chmod("scripts/setup_ssl.sh", 0o755)
        
        logger.info("✅ Created SSL setup script")

    def create_monitoring_setup(self):
        """Create monitoring and health check setup"""
        monitoring_script = """#!/bin/bash
set -e

echo "📊 Setting up monitoring and health checks"

# Install Prometheus and Grafana
kubectl create namespace monitoring --dry-run=client -o yaml | kubectl apply -f -

# Add Prometheus Helm repo
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Install Prometheus
helm install prometheus prometheus-community/kube-prometheus-stack -n monitoring

# Install Grafana dashboards for Sophia AI
kubectl apply -f k8s/monitoring/

echo "✅ Monitoring setup complete!"
echo "📊 Grafana: http://localhost:3000 (port-forward required)"
echo "📈 Prometheus: http://localhost:9090 (port-forward required)"
"""
        
        with open("scripts/setup_monitoring.sh", "w") as f:
            f.write(monitoring_script.strip())
        
        os.chmod("scripts/setup_monitoring.sh", 0o755)
        
        logger.info("✅ Created monitoring setup script")

    def create_master_deployment_script(self):
        """Create master deployment orchestrator"""
        master_script = """#!/usr/bin/env python3
'''
Master Deployment Script for Sophia AI Lambda Labs Infrastructure
Orchestrates complete deployment across all servers
'''

import subprocess
import time
import sys
import requests

def run_command(cmd, description):
    print(f"🚀 {description}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed")
            return True
        else:
            print(f"❌ {description} failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} error: {e}")
        return False

def test_endpoint(url, description):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            print(f"✅ {description}: {url}")
            return True
        else:
            print(f"❌ {description} failed: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ {description} error: {e}")
        return False

def main():
    print("🚀 Starting Sophia AI Lambda Labs Deployment")
    print("=" * 60)
    
    # Phase 1: Build and push Docker images
    print("\\n📦 Phase 1: Building Docker Images")
    if not run_command("python3 scripts/deploy_to_lambda_labs.py --build-images", "Building Docker images"):
        sys.exit(1)
    
    # Phase 2: Deploy to primary server
    print("\\n🖥️  Phase 2: Deploying Primary Server")
    if not run_command("ssh root@192.222.58.232 'bash -s' < scripts/deploy_primary_server.sh", "Primary server deployment"):
        print("⚠️  Manual deployment required on primary server")
    
    # Phase 3: Deploy MCP orchestrator
    print("\\n🤖 Phase 3: Deploying MCP Orchestrator")
    if not run_command("ssh root@104.171.202.117 'bash -s' < scripts/deploy_mcp_server.sh", "MCP orchestrator deployment"):
        print("⚠️  Manual deployment required on MCP server")
    
    # Phase 4: Setup SSL certificates
    print("\\n🔒 Phase 4: Setting up SSL Certificates")
    if not run_command("ssh root@192.222.58.232 'bash -s' < scripts/setup_ssl.sh", "SSL setup"):
        print("⚠️  Manual SSL setup required")
    
    # Phase 5: Setup monitoring
    print("\\n📊 Phase 5: Setting up Monitoring")
    if not run_command("ssh root@192.222.58.232 'bash -s' < scripts/setup_monitoring.sh", "Monitoring setup"):
        print("⚠️  Manual monitoring setup required")
    
    # Phase 6: Test all endpoints
    print("\\n🧪 Phase 6: Testing Deployment")
    time.sleep(30)  # Wait for services to start
    
    endpoints = [
        ("https://sophia-intel.ai", "Main site"),
        ("https://api.sophia-intel.ai/health", "API health"),
        ("https://app.sophia-intel.ai", "Frontend app"),
        ("https://webhooks.sophia-intel.ai/health", "Webhooks"),
        ("https://mcp.sophia-intel.ai/health", "MCP services")
    ]
    
    success_count = 0
    for url, description in endpoints:
        if test_endpoint(url, description):
            success_count += 1
    
    print("\\n" + "=" * 60)
    print(f"🎉 Deployment Complete: {success_count}/{len(endpoints)} endpoints working")
    
    if success_count == len(endpoints):
        print("✅ FULL SUCCESS: Sophia AI is live on Lambda Labs!")
        print("🌐 Main site: https://sophia-intel.ai")
        print("🔗 API: https://api.sophia-intel.ai")
        print("📱 App: https://app.sophia-intel.ai")
    else:
        print("⚠️  Partial deployment - manual intervention required")
        print("📋 Check logs and run individual deployment scripts")

if __name__ == "__main__":
    main()
"""
        
        with open("scripts/master_deploy.py", "w") as f:
            f.write(master_script.strip())
        
        os.chmod("scripts/master_deploy.py", 0o755)
        
        logger.info("✅ Created master deployment script")

    def deploy_all(self):
        """Execute complete deployment"""
        logger.info("🚀 Starting Lambda Labs deployment...")
        
        try:
            # Create all necessary files
            self.create_backend_dockerfile()
            self.create_frontend_dockerfile() 
            self.create_kubernetes_manifests()
            self.create_deployment_scripts()
            self.create_ssl_setup_script()
            self.create_monitoring_setup()
            self.create_master_deployment_script()
            
            # Build and push Docker images
            self.create_docker_images()
            
            logger.info("✅ Deployment preparation complete!")
            logger.info("📋 Next steps:")
            logger.info("1. Run: python3 scripts/master_deploy.py")
            logger.info("2. Or deploy manually with individual scripts")
            logger.info("3. Test endpoints after deployment")
            
        except Exception as e:
            logger.error(f"❌ Deployment failed: {e}")
            sys.exit(1)

def main():
    """Main deployment function"""
    deployer = LambdaLabsDeployer()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--build-images":
        deployer.create_docker_images()
    else:
        deployer.deploy_all()

if __name__ == "__main__":
    main() 