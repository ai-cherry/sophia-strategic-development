#!/usr/bin/env python3
"""
Lambda Labs Instance Manager for Sophia AI
Manages Lambda Labs instances, deployments, and monitoring
"""

import json
import logging
import os
import subprocess
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class LambdaInstance:
    """Lambda Labs instance information"""

    id: str
    name: str
    ip: str
    status: str
    instance_type: str
    region: str
    ssh_key_names: list[str]


class LambdaLabsManager:
    """Manages Lambda Labs instances and deployments"""

    def __init__(self):
        # API credentials
        self.cloud_api_key = "secret_sophiacloudapi_17cf7f3cedca48f18b4b8ea46cbb258f.EsLXt0lkGlhZ1Nd369Ld5DMSuhJg9O9y"
        self.regular_api_key = "secret_sophia5apikey_a404a99d985d41828d7020f0b9a122a2.PjbWZb0lLubKu1nmyWYLy9Ycl3vyL18o"
        self.api_endpoint = "https://cloud.lambda.ai/api/v1"

        # SSH configuration
        self.ssh_key_path = os.path.expanduser("~/.ssh/sophia2025.pem")

        # Instance mapping
        self.instance_mapping = {
            "sophia-production-instance": "104.171.202.103",
            "sophia-ai-core": "192.222.58.232",
            "sophia-mcp-orchestrator": "104.171.202.117",
            "sophia-data-pipeline": "104.171.202.134",
            "sophia-development": "155.248.194.183",
        }

    def _make_api_request(
        self, endpoint: str, method: str = "GET", data: Optional[dict] = None
    ) -> dict:
        """Make authenticated API request to Lambda Labs"""
        url = f"{self.api_endpoint}/{endpoint}"
        headers = {"Authorization": f"Bearer {self.cloud_api_key}"}

        try:
            if method == "GET":
                response = requests.get(url, headers=headers)
            elif method == "POST":
                response = requests.post(url, headers=headers, json=data)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers)
            else:
                raise ValueError(f"Unsupported method: {method}")

            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            raise

    def list_instances(self) -> list[LambdaInstance]:
        """List all Lambda Labs instances"""
        logger.info("Fetching Lambda Labs instances...")
        data = self._make_api_request("instances")

        instances = []
        for item in data.get("data", []):
            instance = LambdaInstance(
                id=item["id"],
                name=item["name"],
                ip=item["ip"],
                status=item["status"],
                instance_type=item["instance_type"]["name"],
                region=item["region"]["name"],
                ssh_key_names=item["ssh_key_names"],
            )
            instances.append(instance)

        return instances

    def get_instance_status(self, instance_name: str) -> Optional[str]:
        """Get status of a specific instance"""
        instances = self.list_instances()
        for instance in instances:
            if instance.name == instance_name:
                return instance.status
        return None

    def ssh_command(self, instance_name: str, command: str) -> tuple[int, str, str]:
        """Execute SSH command on instance"""
        if instance_name not in self.instance_mapping:
            raise ValueError(f"Unknown instance: {instance_name}")

        ip = self.instance_mapping[instance_name]
        ssh_cmd = [
            "ssh",
            "-i",
            self.ssh_key_path,
            "-o",
            "StrictHostKeyChecking=no",
            "-o",
            "UserKnownHostsFile=/dev/null",
            f"ubuntu@{ip}",
            command,
        ]

        logger.info(f"Executing on {instance_name}: {command}")
        process = subprocess.Popen(
            ssh_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        stdout, stderr = process.communicate()

        return process.returncode, stdout.decode(), stderr.decode()

    def deploy_sophia(self, instance_name: str, deployment_type: str = "full"):
        """Deploy Sophia AI to Lambda Labs instance"""
        logger.info(f"Deploying Sophia AI to {instance_name} (type: {deployment_type})")

        # Check instance status
        status = self.get_instance_status(instance_name)
        if status != "active":
            logger.error(f"Instance {instance_name} is not active (status: {status})")
            return False

        # Prepare deployment script
        deployment_script = self._generate_deployment_script(deployment_type)

        # Copy deployment script
        ip = self.instance_mapping[instance_name]
        scp_cmd = [
            "scp",
            "-i",
            self.ssh_key_path,
            "-o",
            "StrictHostKeyChecking=no",
            "-",
            f"ubuntu@{ip}:/tmp/deploy_sophia.sh",
        ]

        process = subprocess.Popen(scp_cmd, stdin=subprocess.PIPE)
        process.communicate(input=deployment_script.encode())

        if process.returncode != 0:
            logger.error("Failed to copy deployment script")
            return False

        # Execute deployment
        returncode, stdout, stderr = self.ssh_command(
            instance_name, "bash /tmp/deploy_sophia.sh"
        )

        if returncode == 0:
            logger.info("Deployment successful!")
            logger.info(stdout)
            return True
        else:
            logger.error("Deployment failed!")
            logger.error(stderr)
            return False

    def _generate_deployment_script(self, deployment_type: str) -> str:
        """Generate deployment script based on type"""
        base_script = """#!/bin/bash
set -e

echo "🚀 Deploying Sophia AI..."

# Update system
sudo apt-get update
sudo apt-get install -y docker.io docker-compose git curl jq

# Ensure Docker is running
sudo systemctl start docker
sudo usermod -aG docker ubuntu

# Create deployment directory
mkdir -p /home/ubuntu/sophia-ai
cd /home/ubuntu/sophia-ai
"""

        if deployment_type == "full":
            return (
                base_script
                + """
# Pull all images
docker pull scoobyjava15/sophia-backend:latest
docker pull scoobyjava15/sophia-mcp-servers:latest
docker pull postgres:16-alpine
docker pull redis:7-alpine
docker pull prom/prometheus:latest
docker pull grafana/grafana:latest

# Create docker-compose.yml
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: sophia_db
      POSTGRES_USER: sophia_user
      POSTGRES_PASSWORD: sophia_secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - sophia-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U sophia_user"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    networks:
      - sophia-network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    image: scoobyjava15/sophia-backend:latest
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
      - DATABASE_URL=postgresql://sophia_user:sophia_secure_password@postgres:5432/sophia_db
      - REDIS_URL=redis://redis:6379
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - sophia-network
    volumes:
      - ./config:/app/config
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  mcp-servers:
    image: scoobyjava15/sophia-mcp-servers:latest
    ports:
      - "9000-9100:9000-9100"
    environment:
      - ENVIRONMENT=production
    networks:
      - sophia-network
    volumes:
      - ./config:/app/config

  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    networks:
      - sophia-network

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=sophia_admin
    volumes:
      - grafana_data:/var/lib/grafana
    networks:
      - sophia-network

volumes:
  postgres_data:
  redis_data:
  prometheus_data:
  grafana_data:

networks:
  sophia-network:
    driver: bridge
EOF

# Create Prometheus config
cat > prometheus.yml << 'EOF'
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'sophia-backend'
    static_configs:
      - targets: ['backend:8000']

  - job_name: 'mcp-servers'
    static_configs:
      - targets: ['mcp-servers:9001', 'mcp-servers:9002', 'mcp-servers:9003']
EOF

# Stop existing containers
docker-compose down || true

# Start services
docker stack deploy

# Wait for services
echo "⏳ Waiting for services to start..."
sleep 60

# Check status
docker-compose ps

echo "✅ Full deployment complete!"
"""
            )
        elif deployment_type == "backend-only":
            return (
                base_script
                + """
# Update backend only
docker pull scoobyjava15/sophia-backend:latest
docker stack deploy backend
echo "✅ Backend deployment complete!"
"""
            )
        elif deployment_type == "mcp-servers-only":
            return (
                base_script
                + """
# Update MCP servers only
docker pull scoobyjava15/sophia-mcp-servers:latest
docker stack deploy mcp-servers
echo "✅ MCP servers deployment complete!"
"""
            )
        else:
            return (
                base_script
                + """
echo "✅ Configuration update complete!"
"""
            )

    def health_check(self, instance_name: str) -> dict[str, bool]:
        """Perform health check on deployed services"""
        logger.info(f"Performing health check on {instance_name}")

        ip = self.instance_mapping[instance_name]
        health_status = {}

        # Check backend
        try:
            response = requests.get(f"http://{ip}:8000/health", timeout=10)
            health_status["backend"] = response.status_code == 200
        except:
            health_status["backend"] = False

        # Check MCP servers
        for port in range(9001, 9006):
            try:
                response = requests.get(f"http://{ip}:{port}/health", timeout=5)
                health_status[f"mcp_{port}"] = response.status_code == 200
            except:
                health_status[f"mcp_{port}"] = False

        # Check Prometheus
        try:
            response = requests.get(f"http://{ip}:9090/-/healthy", timeout=5)
            health_status["prometheus"] = response.status_code == 200
        except:
            health_status["prometheus"] = False

        # Check Grafana
        try:
            response = requests.get(f"http://{ip}:3000/api/health", timeout=5)
            health_status["grafana"] = response.status_code == 200
        except:
            health_status["grafana"] = False

        return health_status

    def monitor_deployment(self, instance_name: str, duration: int = 300):
        """Monitor deployment for specified duration"""
        logger.info(f"Monitoring {instance_name} for {duration} seconds...")

        start_time = time.time()
        while time.time() - start_time < duration:
            health = self.health_check(instance_name)

            # Log status
            healthy_services = [k for k, v in health.items() if v]
            unhealthy_services = [k for k, v in health.items() if not v]

            logger.info(f"Healthy: {', '.join(healthy_services)}")
            if unhealthy_services:
                logger.warning(f"Unhealthy: {', '.join(unhealthy_services)}")

            time.sleep(30)

    def generate_deployment_report(self) -> dict:
        """Generate comprehensive deployment report"""
        logger.info("Generating deployment report...")

        report = {"timestamp": datetime.utcnow().isoformat(), "instances": []}

        instances = self.list_instances()
        for instance in instances:
            instance_info = {
                "name": instance.name,
                "ip": instance.ip,
                "status": instance.status,
                "type": instance.instance_type,
                "region": instance.region,
                "health": {},
            }

            if instance.status == "active":
                instance_info["health"] = self.health_check(instance.name)

            report["instances"].append(instance_info)

        return report


def main():
    """Main CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="Lambda Labs Instance Manager")
    parser.add_argument(
        "command", choices=["list", "deploy", "health", "monitor", "report"]
    )
    parser.add_argument("--instance", help="Instance name")
    parser.add_argument(
        "--type",
        default="full",
        choices=["full", "backend-only", "mcp-servers-only", "update-config"],
    )
    parser.add_argument(
        "--duration", type=int, default=300, help="Monitoring duration in seconds"
    )

    args = parser.parse_args()

    manager = LambdaLabsManager()

    if args.command == "list":
        instances = manager.list_instances()
        for instance in instances:
            print(
                f"{instance.name}: {instance.ip} ({instance.status}) - {instance.instance_type}"
            )

    elif args.command == "deploy":
        if not args.instance:
            print("Error: --instance required for deploy")
            return
        success = manager.deploy_sophia(args.instance, args.type)
        if success:
            print("Deployment successful!")
        else:
            print("Deployment failed!")

    elif args.command == "health":
        if not args.instance:
            print("Error: --instance required for health check")
            return
        health = manager.health_check(args.instance)
        for service, status in health.items():
            print(f"{service}: {'✅' if status else '❌'}")

    elif args.command == "monitor":
        if not args.instance:
            print("Error: --instance required for monitoring")
            return
        manager.monitor_deployment(args.instance, args.duration)

    elif args.command == "report":
        report = manager.generate_deployment_report()
        print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
