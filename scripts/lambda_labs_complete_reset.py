#!/usr/bin/env python3
"""
Lambda Labs Complete Reset and Optimization Script
Cleans up everything and sets up optimal infrastructure for Sophia AI
"""

import os
import time
from datetime import datetime

import requests

# Configuration
API_KEY = os.getenv(
    "LAMBDA_LABS_API_KEY",
    "secret_sophia-july-25_989f13097e374c779f28629f5a1ac571.iH4OIeM78TWyzDiltkpLAzlPeaTw68HJ",
)
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
BASE_URL = "https://cloud.lambda.ai/api/v1"


class LambdaLabsOptimizer:
    def __init__(self):
        self.api_key = API_KEY
        self.headers = {"Authorization": f"Bearer {API_KEY}"}
        self.auth = (API_KEY, "")

    def list_instances(self) -> list[dict]:
        """List all Lambda Labs instances"""
        response = requests.get(f"{BASE_URL}/instances", auth=self.auth)
        if response.status_code == 200:
            return response.json()["data"]
        return []

    def terminate_instance(self, instance_id: str, name: str) -> bool:
        """Terminate a specific instance"""
        response = requests.post(
            f"{BASE_URL}/instance-operations/terminate",
            auth=self.auth,
            json={"instance_ids": [instance_id]},
        )
        return response.status_code in [200, 202]

    def list_ssh_keys(self) -> list[dict]:
        """List all SSH keys"""
        response = requests.get(f"{BASE_URL}/ssh-keys", auth=self.auth)
        if response.status_code == 200:
            return response.json()["data"]
        return []

    def delete_ssh_key(self, key_id: str) -> bool:
        """Delete an SSH key"""
        response = requests.delete(f"{BASE_URL}/ssh-keys/{key_id}", auth=self.auth)
        return response.status_code == 204

    def add_ssh_key(self, name: str, public_key: str) -> bool:
        """Add an SSH key"""
        response = requests.post(
            f"{BASE_URL}/ssh-keys",
            auth=self.auth,
            json={"name": name, "public_key": public_key},
        )
        return response.status_code == 201

    def launch_instance(
        self,
        instance_type: str,
        name: str,
        ssh_key_names: list[str],
        region: str = "us-west-1",
    ) -> dict | None:
        """Launch a new instance"""

        payload = {
            "region_name": region,
            "instance_type_name": instance_type,
            "ssh_key_names": ssh_key_names,
            "name": name,
            "quantity": 1,
        }

        response = requests.post(
            f"{BASE_URL}/instance-operations/launch", auth=self.auth, json=payload
        )

        if response.status_code in [200, 201]:
            return response.json()
        else:
            return None


def phase1_cleanup(optimizer: LambdaLabsOptimizer):
    """Phase 1: Clean up all instances and keys"""

    # Get current instances
    instances = optimizer.list_instances()

    # Calculate current monthly cost
    (
        sum(inst["instance_type"]["price_cents_per_hour"] for inst in instances)
        * 24
        * 30
        / 100
    )

    # Show what we'll remove
    for inst in instances:
        hourly = inst["instance_type"]["price_cents_per_hour"] / 100
        hourly * 24 * 30

    print("\n✅ Terminating ALL instances...")
    for inst in instances:
        optimizer.terminate_instance(inst["id"], inst["name"])
        time.sleep(1)  # Rate limiting

    # Clean up SSH keys
    keys = optimizer.list_ssh_keys()

    # Keep only a specific key
    for key in keys:
        if key["name"] != "pulumi_lambda_key":
            if optimizer.delete_ssh_key(key["id"]):
                pass


def phase2_optimal_setup(optimizer: LambdaLabsOptimizer):
    """Phase 2: Create optimal instance configuration"""

    print("\n✅ Creating optimized setup...")

    # Ensure we have our dedicated key
    keys = optimizer.list_ssh_keys()
    if not any(k["name"] == "pulumi_lambda_key" for k in keys):
        # Add the new key if it doesn't exist
        try:
            with open(os.path.expanduser("~/.ssh/pulumi_lambda_key.pub")) as f:
                public_key = f.read()
            if optimizer.add_ssh_key("pulumi_lambda_key", public_key):
                print("✅ Successfully added 'pulumi_lambda_key' to Lambda Labs.")
            else:
                print("❌ Failed to add 'pulumi_lambda_key'. Please add it manually.")
                return
        except FileNotFoundError:
            print("❌ ~/.ssh/pulumi_lambda_key.pub not found. Cannot proceed.")
            return

    # Launch instances
    instances_to_launch = [
        {
            "name": "sophia-platform-prod",
            "type": "gpu_1x_a10",
            "region": "us-west-1",
            "purpose": "Main Platform",
        },
        {
            "name": "sophia-ai-prod",
            "type": "gpu_1x_a100_sxm4",
            "region": "us-west-1",
            "purpose": "AI Processing",
        },
        {
            "name": "sophia-mcp-prod",
            "type": "gpu_1x_a10",
            "region": "us-west-1",
            "purpose": "MCP Orchestration",
        },
    ]

    launched_instances = []
    for inst in instances_to_launch:
        result = optimizer.launch_instance(
            instance_type=inst["type"],
            name=inst["name"],
            ssh_key_names=["pulumi_lambda_key"],
            region=inst["region"],
        )
        if result:
            launched_instances.append(
                {"name": inst["name"], "purpose": inst["purpose"], "type": inst["type"]}
            )
        time.sleep(2)  # Rate limiting


def phase3_deployment_prep():
    """Phase 3: Prepare deployment scripts"""

    # Create optimized deployment script
    deployment_script = f"""#!/bin/bash
# Sophia AI Optimized Deployment Script
# Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

# Configuration
GITHUB_TOKEN="{GITHUB_TOKEN}"
PLATFORM_IP=""  # Will be set after instances launch
AI_IP=""        # Will be set after instances launch
MCP_IP=""       # Will be set after instances launch

# Colors
GREEN='\\033[0;32m'
RED='\\033[0;31m'
NC='\\033[0m'

echo "🚀 Sophia AI Production Deployment"
echo "=================================="

# Function to setup instance
setup_instance() {{
    local IP=$1
    local ROLE=$2

    echo -e "${{GREEN}}Setting up $ROLE on $IP${{NC}}"

    ssh -i ~/.ssh/pulumi_lambda_key ubuntu@$IP << 'SETUP'
        # Update system
        sudo apt-get update
        sudo apt-get upgrade -y

        # Install Docker
        curl -fsSL https://get.docker.com -o get-docker.sh
        sudo sh get-docker.sh
        sudo usermod -aG docker ubuntu

        # Install dependencies
        sudo apt-get install -y python3-pip git nginx certbot

        # Clone repository
        git clone https://github.com/ai-cherry/sophia-main.git
        cd sophia-main

        # Set environment
        echo "export ENVIRONMENT=prod" >> ~/.bashrc
        echo "export PULUMI_ORG=scoobyjava-org" >> ~/.bashrc
        echo "export GITHUB_TOKEN=$GITHUB_TOKEN" >> ~/.bashrc
        source ~/.bashrc

        # Install Python dependencies
        pip install uv
        uv venv
        source .venv/bin/activate
        uv sync
SETUP
}}

# Main deployment
echo "Waiting for instances to be ready..."
sleep 30

# Deploy to each instance
setup_instance $PLATFORM_IP "Platform Server"
setup_instance $AI_IP "AI Server"
setup_instance $MCP_IP "MCP Server"

echo -e "${{GREEN}}✅ Deployment preparation complete!${{NC}}"
"""

    with open("scripts/deploy_sophia_optimized.sh", "w") as f:
        f.write(deployment_script)
    os.chmod("scripts/deploy_sophia_optimized.sh", 0o755)

    # Create docker-compose for each server
    create_docker_configs()


def create_docker_configs():
    """Create optimized Docker configurations"""

    # Platform server docker-compose
    platform_compose = """version: '3.8'
services:
  api:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=prod
      - PULUMI_ORG=scoobyjava-org
    depends_on:
      - postgres
      - redis
    volumes:
      - ./backend:/app
    restart: unless-stopped

  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: sophia
      POSTGRES_USER: sophia
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    command: redis-server --maxmemory 2gb --maxmemory-policy allkeys-lru
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./certs:/etc/nginx/certs
    depends_on:
      - api
    restart: unless-stopped

volumes:
  postgres_data:
"""

    # AI server docker-compose
    ai_compose = """version: '3.8'
services:
  ai-inference:
    build: ./ai-services
    runtime: nvidia
    ports:
      - "8080:8080"
    environment:
      - ENVIRONMENT=prod
      - CUDA_VISIBLE_DEVICES=0
    volumes:
      - ./models:/models
      - ./cache:/cache
    restart: unless-stopped

  embedding-service:
    build: ./embedding-service
    runtime: nvidia
    ports:
      - "8081:8081"
    environment:
      - ENVIRONMENT=prod
    restart: unless-stopped

  snowflake-cortex:
    build: ./snowflake-cortex
    ports:
      - "8082:8082"
    environment:
      - ENVIRONMENT=prod
    restart: unless-stopped
"""

    # MCP server docker-compose
    mcp_compose = """version: '3.8'
services:
  mcp-gateway:
    build: ./mcp-gateway
    ports:
      - "9000:9000"
    environment:
      - ENVIRONMENT=prod
    restart: unless-stopped

  ai-memory:
    build: ./mcp-servers/ai-memory
    ports:
      - "9001:9001"
    restart: unless-stopped

  codacy:
    build: ./mcp-servers/codacy
    ports:
      - "9002:9002"
    restart: unless-stopped

  github:
    build: ./mcp-servers/github
    ports:
      - "9003:9003"
    restart: unless-stopped

  linear:
    build: ./mcp-servers/linear
    ports:
      - "9004:9004"
    restart: unless-stopped

  snowflake-admin:
    build: ./mcp-servers/snowflake-admin
    ports:
      - "9005:9005"
    restart: unless-stopped
"""

    # Save configurations
    configs = {
        "docker-compose.platform.yml": platform_compose,
        "docker-compose.ai.yml": ai_compose,
        "docker-compose.mcp.yml": mcp_compose,
    }

    for filename, content in configs.items():
        with open(filename, "w") as f:
            f.write(content)


def main():
    print("\n⚠️  This script will DELETE all current instances and rebuild.")

    optimizer = LambdaLabsOptimizer()

    # Phase 1: Cleanup
    phase1_cleanup(optimizer)

    # Wait for terminations to complete
    time.sleep(30)

    # Phase 2: Optimal setup
    phase2_optimal_setup(optimizer)

    # Phase 3: Deployment preparation
    phase3_deployment_prep()


if __name__ == "__main__":
    main()
