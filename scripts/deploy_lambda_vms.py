#!/usr/bin/env python3
"""
Deploy Lambda Labs VMs for Sophia AI Infrastructure
Handles VM provisioning with GPU selection and IP capture
"""

import argparse
import json
import requests
import time
from typing import Dict, List
import os
import sys

class LambdaLabsDeployer:
    """Manages Lambda Labs VM deployment"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.lambdalabs.com/v1"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
    def get_available_instances(self) -> List[Dict]:
        """Get list of available instance types"""
        response = requests.get(
            f"{self.base_url}/instance-types",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()["data"]
    
    def deploy_vm(self, config: Dict) -> Dict:
        """Deploy a single VM and return its details"""
        payload = {
            "name": config["name"],
            "instance_type": config["instance_type"],
            "region": config.get("region", "us-south-1"),
            "ssh_key_names": ["sophia-deploy-key"],
            "user_data": self._generate_user_data(config["purpose"])
        }
        
        response = requests.post(
            f"{self.base_url}/instances",
            headers=self.headers,
            json=payload
        )
        
        if response.status_code == 200:
            instance = response.json()["data"]
            print(f"✅ Deployed {config['name']} - IP: {instance['ip_address']}")
            return instance
        else:
            print(f"❌ Failed to deploy {config['name']}: {response.text}")
            raise Exception(f"Deployment failed: {response.text}")
    
    def _generate_user_data(self, purpose: str) -> str:
        """Generate user data script based on VM purpose"""
        base_script = """#!/bin/bash
apt-get update
apt-get install -y docker.io docker-compose git curl
systemctl enable docker
systemctl start docker

# Install NVIDIA Docker
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | tee /etc/apt/sources.list.d/nvidia-docker.list
apt-get update && apt-get install -y nvidia-docker2
systemctl restart docker
"""
        
        if purpose.startswith("qdrant"):
            return base_script + """
# Deploy Qdrant with GPU support
docker run -d \\
  --name qdrant \\
  --runtime=nvidia \\
  --gpus all \\
  -p 6333:6333 \\
  -p 6334:6334 \\
  -v /qdrant/storage:/qdrant/storage \\
  -e QDRANT__SERVICE__HTTP_PORT=6333 \\
  -e QDRANT__SERVICE__GRPC_PORT=6334 \\
  -e QDRANT__GPU_ENABLED=true \\
  -e QDRANT__GPU_MEMORY_LIMIT=70GB \\
  qdrant/qdrant:latest-gpu
"""
        
        elif purpose == "redis-mem0-postgres":
            return base_script + """
# Create docker-compose for memory services
cat > /root/docker-compose.yml <<'EOF'
version: '3.8'
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --maxmemory 60gb --maxmemory-policy allkeys-lru
    restart: always
  
  postgres:
    image: pgvector/pgvector:pg16
    ports:
      - "5432:5432"
    environment:
      POSTGRES_DB: sophia_memory
      POSTGRES_USER: sophia
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-sophia_secure_pass}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: always
  
  mem0:
    image: mem0ai/mem0:latest
    ports:
      - "8080:8080"
    environment:
      REDIS_URL: redis://redis:6379
      POSTGRES_URL: postgresql://sophia:${POSTGRES_PASSWORD:-sophia_secure_pass}@postgres:5432/sophia_memory
    depends_on:
      - redis
      - postgres
    restart: always

volumes:
  redis_data:
  postgres_data:
EOF

cd /root && docker-compose up -d
"""
        
        else:  # main-api
            return base_script + """
# Prepare for main API deployment
mkdir -p /app
git clone https://github.com/ai-cherry/sophia-main.git /app
"""

def main():
    parser = argparse.ArgumentParser(description="Deploy Lambda Labs VMs")
    parser.add_argument("--environment", required=True, choices=["production", "staging", "development"])
    parser.add_argument("--output-file", default="vm_ips.json", help="Output file for VM IPs")
    parser.add_argument("--api-key", default=os.getenv("LAMBDA_LABS_API_KEY"))
    
    args = parser.parse_args()
    
    if not args.api_key:
        print("❌ LAMBDA_LABS_API_KEY not provided")
        sys.exit(1)
    
    # VM configurations
    vm_configs = [
        {
            "name": f"sophia-main-node-{args.environment}",
            "instance_type": "gpu_1x_h200_96gb",
            "gpu": "H200",
            "purpose": "main-api"
        },
        {
            "name": f"sophia-qdrant-1-{args.environment}",
            "instance_type": "gpu_1x_h100_80gb",
            "gpu": "H100",
            "purpose": "qdrant-primary"
        },
        {
            "name": f"sophia-qdrant-2-{args.environment}",
            "instance_type": "gpu_1x_h100_80gb",
            "gpu": "H100",
            "purpose": "qdrant-replica"
        },
        {
            "name": f"sophia-memory-services-{args.environment}",
            "instance_type": "gpu_1x_a100_40gb",
            "gpu": "A100",
            "purpose": "redis-mem0-postgres"
        }
    ]
    
    deployer = LambdaLabsDeployer(args.api_key)
    deployed_ips = {}
    
    print(f"🚀 Deploying VMs for {args.environment} environment...")
    
    for config in vm_configs:
        try:
            instance = deployer.deploy_vm(config)
            deployed_ips[config["purpose"]] = instance["ip_address"]
            time.sleep(5)  # Rate limiting
        except Exception as e:
            print(f"❌ Error deploying {config['name']}: {e}")
            # Continue with other VMs
    
    # Save IPs to file
    with open(args.output_file, 'w') as f:
        json.dump(deployed_ips, f, indent=2)
    
    print(f"\n✅ Deployment complete! IPs saved to {args.output_file}")
    print(json.dumps(deployed_ips, indent=2))

if __name__ == "__main__":
    main()
