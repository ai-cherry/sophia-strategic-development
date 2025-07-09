#!/usr/bin/env python3
"""
Complete Sophia AI Deployment Orchestrator
Handles full deployment pipeline to Lambda Labs infrastructure
"""

import argparse
import json
import logging
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class SophiaDeploymentOrchestrator:
    """Orchestrates complete Sophia AI deployment"""

    def __init__(self):
        self.start_time = datetime.now()
        self.deployment_id = (
            f"sophia-deploy-{self.start_time.strftime('%Y%m%d-%H%M%S')}"
        )

        # Instance configuration with deployment roles
        self.deployment_config = {
            "sophia-production-instance": {
                "ip": "104.171.202.103",
                "services": ["backend", "mcp-servers", "monitoring"],
                "priority": 1,
            },
            "sophia-ai-core": {
                "ip": "192.222.58.232",
                "services": ["ai-services", "llm-routing", "snowflake-cortex"],
                "priority": 2,
            },
            "sophia-mcp-orchestrator": {
                "ip": "104.171.202.117",
                "services": ["mcp-gateway", "mcp-servers"],
                "priority": 2,
            },
            "sophia-data-pipeline": {
                "ip": "104.171.202.134",
                "services": ["etl", "data-processing", "analytics"],
                "priority": 3,
            },
            "sophia-development": {
                "ip": "155.248.194.183",
                "services": ["dev-environment", "testing"],
                "priority": 4,
            },
        }

        self.ssh_key_path = os.path.expanduser("~/.ssh/lambda_labs_sophia_key")
        self.deployment_report = {
            "deployment_id": self.deployment_id,
            "start_time": self.start_time.isoformat(),
            "instances": {},
            "status": "in_progress",
        }

    def run_command(self, command: str) -> tuple[int, str, str]:
        """Execute local command"""
        logger.debug(f"Running: {command}")
        process = subprocess.Popen(
            command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        stdout, stderr = process.communicate()
        return process.returncode, stdout.decode(), stderr.decode()

    def ssh_command(self, ip: str, command: str) -> tuple[int, str, str]:
        """Execute SSH command on remote instance"""
        ssh_cmd = f"ssh -i {self.ssh_key_path} -o StrictHostKeyChecking=no ubuntu@{ip} '{command}'"
        return self.run_command(ssh_cmd)

    def scp_file(self, local_path: str, ip: str, remote_path: str) -> bool:
        """Copy file to remote instance"""
        scp_cmd = f"scp -i {self.ssh_key_path} -o StrictHostKeyChecking=no {local_path} ubuntu@{ip}:{remote_path}"
        returncode, _, stderr = self.run_command(scp_cmd)
        if returncode != 0:
            logger.error(f"SCP failed: {stderr}")
            return False
        return True

    def build_docker_images(self) -> bool:
        """Build and push Docker images"""
        logger.info("🐳 Building Docker images...")

        images = [
            {
                "name": "sophia-backend",
                "dockerfile": "Dockerfile.production",
                "context": ".",
            },
            {
                "name": "sophia-mcp-servers",
                "dockerfile": "docker/Dockerfile.mcp-server",
                "context": ".",
            },
        ]

        for image in images:
            logger.info(f"Building {image['name']}...")

            # Build image
            build_cmd = f"docker build -f {image['dockerfile']} -t scoobyjava15/{image['name']}:latest -t scoobyjava15/{image['name']}:{self.deployment_id} {image['context']}"
            returncode, stdout, stderr = self.run_command(build_cmd)

            if returncode != 0:
                logger.error(f"Build failed for {image['name']}: {stderr}")
                return False

            # Push to Docker Hub
            logger.info(f"Pushing {image['name']} to Docker Hub...")
            push_cmd = f"docker push scoobyjava15/{image['name']}:latest && docker push scoobyjava15/{image['name']}:{self.deployment_id}"
            returncode, stdout, stderr = self.run_command(push_cmd)

            if returncode != 0:
                logger.error(f"Push failed for {image['name']}: {stderr}")
                return False

        logger.info("✅ Docker images built and pushed successfully")
        return True

    def prepare_deployment_files(self) -> dict[str, str]:
        """Prepare deployment configuration files"""
        logger.info("📝 Preparing deployment files...")

        files = {}

        # Docker Compose configuration
        files[
            "docker-compose.yml"
        ] = """version: '3.8'

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
      - ./logs:/app/logs
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    restart: unless-stopped

  mcp-servers:
    image: scoobyjava15/sophia-mcp-servers:latest
    ports:
      - "9000-9100:9000-9100"
      - "3008:3008"
    environment:
      - ENVIRONMENT=production
    networks:
      - sophia-network
    volumes:
      - ./config:/app/config
      - ./logs:/app/logs
    restart: unless-stopped

  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    networks:
      - sophia-network
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/usr/share/prometheus/console_libraries'
      - '--web.console.templates=/usr/share/prometheus/consoles'
    restart: unless-stopped

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=sophia_admin
      - GF_INSTALL_PLUGINS=redis-datasource,postgres-datasource
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana-dashboards:/etc/grafana/provisioning/dashboards
    networks:
      - sophia-network
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
  prometheus_data:
  grafana_data:

networks:
  sophia-network:
    driver: bridge
"""

        # Prometheus configuration
        files[
            "prometheus.yml"
        ] = """global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'sophia-backend'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: '/metrics'

  - job_name: 'mcp-servers'
    static_configs:
      - targets:
        - 'mcp-servers:9001'
        - 'mcp-servers:9002'
        - 'mcp-servers:9003'
        - 'mcp-servers:9004'
        - 'mcp-servers:9005'

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres:5432']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']
"""

        # Deployment script
        files[
            "deploy.sh"
        ] = """#!/bin/bash
set -e

echo "🚀 Deploying Sophia AI..."

# Update system
sudo apt-get update
sudo apt-get install -y docker.io docker-compose git curl jq htop iotop

# Start Docker
sudo systemctl start docker
sudo usermod -aG docker ubuntu

# Create directories
mkdir -p /home/ubuntu/sophia-ai/{config,logs,grafana-dashboards}
cd /home/ubuntu/sophia-ai

# Stop existing services
docker-compose down || true

# Pull latest images
docker-compose pull

# Start services
docker-compose up -d

# Wait for services
echo "⏳ Waiting for services to start..."
sleep 60

# Check status
docker-compose ps

echo "✅ Deployment complete!"
"""

        return files

    def deploy_to_instance(self, instance_name: str, config: dict) -> bool:
        """Deploy to a specific Lambda Labs instance"""
        logger.info(f"🚀 Deploying to {instance_name} ({config['ip']})...")

        ip = config["ip"]

        # Test SSH connection
        returncode, stdout, stderr = self.ssh_command(
            ip, "echo 'SSH connection successful'"
        )
        if returncode != 0:
            logger.error(f"SSH connection failed to {instance_name}: {stderr}")
            self.deployment_report["instances"][instance_name] = {
                "status": "failed",
                "error": "SSH connection failed",
            }
            return False

        # Create deployment directory
        self.ssh_command(ip, "mkdir -p /tmp/sophia-deployment")

        # Copy deployment files
        files = self.prepare_deployment_files()
        for filename, content in files.items():
            # Write file locally
            temp_path = f"/tmp/{filename}"
            with open(temp_path, "w") as f:
                f.write(content)

            # Copy to remote
            if not self.scp_file(temp_path, ip, f"/tmp/sophia-deployment/{filename}"):
                logger.error(f"Failed to copy {filename} to {instance_name}")
                return False

        # Make deploy script executable
        self.ssh_command(ip, "chmod +x /tmp/sophia-deployment/deploy.sh")

        # Execute deployment
        logger.info(f"Executing deployment on {instance_name}...")
        returncode, stdout, stderr = self.ssh_command(
            ip, "cd /tmp/sophia-deployment && sudo bash deploy.sh"
        )

        if returncode != 0:
            logger.error(f"Deployment failed on {instance_name}: {stderr}")
            self.deployment_report["instances"][instance_name] = {
                "status": "failed",
                "error": stderr,
            }
            return False

        logger.info(f"✅ Deployment successful on {instance_name}")
        self.deployment_report["instances"][instance_name] = {
            "status": "success",
            "services": config["services"],
            "ip": ip,
        }
        return True

    def health_check_instance(self, instance_name: str, ip: str) -> dict[str, bool]:
        """Perform health check on deployed services"""
        logger.info(f"🏥 Health check for {instance_name}...")

        health_status = {}

        # Check backend
        try:
            response = requests.get(f"http://{ip}:8000/health", timeout=10)
            health_status["backend"] = response.status_code == 200
        except:
            health_status["backend"] = False

        # Check MCP servers
        for port in [9001, 9002, 9003, 9004, 9005]:
            try:
                response = requests.get(f"http://{ip}:{port}/health", timeout=5)
                health_status[f"mcp_{port}"] = response.status_code == 200
            except:
                health_status[f"mcp_{port}"] = False

        # Check monitoring
        try:
            response = requests.get(f"http://{ip}:9090/-/healthy", timeout=5)
            health_status["prometheus"] = response.status_code == 200
        except:
            health_status["prometheus"] = False

        try:
            response = requests.get(f"http://{ip}:3000/api/health", timeout=5)
            health_status["grafana"] = response.status_code == 200
        except:
            health_status["grafana"] = False

        return health_status

    def deploy_all(self, parallel: bool = True) -> bool:
        """Deploy to all instances"""
        logger.info(f"🚀 Starting deployment {self.deployment_id}")

        # Build Docker images first
        if not self.build_docker_images():
            logger.error("Docker image build failed")
            self.deployment_report["status"] = "failed"
            return False

        # Sort instances by priority
        sorted_instances = sorted(
            self.deployment_config.items(), key=lambda x: x[1]["priority"]
        )

        if parallel:
            # Deploy in parallel within same priority
            priority_groups = {}
            for instance, config in sorted_instances:
                priority = config["priority"]
                if priority not in priority_groups:
                    priority_groups[priority] = []
                priority_groups[priority].append((instance, config))

            for priority in sorted(priority_groups.keys()):
                logger.info(f"Deploying priority {priority} instances...")
                with ThreadPoolExecutor(max_workers=3) as executor:
                    futures = {
                        executor.submit(
                            self.deploy_to_instance, instance, config
                        ): instance
                        for instance, config in priority_groups[priority]
                    }

                    for future in as_completed(futures):
                        instance = futures[future]
                        try:
                            success = future.result()
                            if not success:
                                logger.error(f"Deployment failed for {instance}")
                        except Exception as e:
                            logger.error(
                                f"Exception during deployment of {instance}: {e}"
                            )
        else:
            # Deploy sequentially
            for instance, config in sorted_instances:
                if not self.deploy_to_instance(instance, config):
                    logger.error(f"Deployment failed for {instance}")

        # Perform health checks
        logger.info("🏥 Performing health checks...")
        time.sleep(30)  # Wait for services to stabilize

        all_healthy = True
        for instance, config in self.deployment_config.items():
            if (
                instance in self.deployment_report["instances"]
                and self.deployment_report["instances"][instance]["status"] == "success"
            ):
                health = self.health_check_instance(instance, config["ip"])
                self.deployment_report["instances"][instance]["health"] = health

                healthy_count = sum(1 for v in health.values() if v)
                total_count = len(health)
                logger.info(
                    f"{instance}: {healthy_count}/{total_count} services healthy"
                )

                if healthy_count < total_count:
                    all_healthy = False

        # Update final status
        self.deployment_report["status"] = (
            "completed" if all_healthy else "completed_with_issues"
        )
        self.deployment_report["end_time"] = datetime.now().isoformat()
        self.deployment_report["duration"] = str(datetime.now() - self.start_time)

        return all_healthy

    def generate_report(self) -> str:
        """Generate deployment report"""
        report_path = f"deployment_reports/{self.deployment_id}.json"
        os.makedirs("deployment_reports", exist_ok=True)

        with open(report_path, "w") as f:
            json.dump(self.deployment_report, f, indent=2)

        logger.info(f"📊 Deployment report saved to {report_path}")
        return report_path

    def print_summary(self):
        """Print deployment summary"""
        print("\n" + "=" * 60)
        print("🚀 Sophia AI Deployment Summary")
        print("=" * 60)
        print(f"Deployment ID: {self.deployment_id}")
        print(f"Status: {self.deployment_report['status']}")
        print(f"Duration: {self.deployment_report.get('duration', 'N/A')}")
        print("\nInstance Status:")

        for instance, info in self.deployment_report["instances"].items():
            status_icon = "✅" if info["status"] == "success" else "❌"
            print(f"  {status_icon} {instance}: {info['status']}")

            if "health" in info:
                healthy = sum(1 for v in info["health"].values() if v)
                total = len(info["health"])
                print(f"     Health: {healthy}/{total} services")

        print("\nAccess Points:")
        for instance, config in self.deployment_config.items():
            if (
                instance in self.deployment_report["instances"]
                and self.deployment_report["instances"][instance]["status"] == "success"
            ):
                print(f"  {instance}:")
                print(f"    - Backend: http://{config['ip']}:8000")
                print(f"    - Grafana: http://{config['ip']}:3000")
                print(f"    - Prometheus: http://{config['ip']}:9090")

        print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="Sophia AI Deployment Orchestrator")
    parser.add_argument(
        "--parallel", action="store_true", help="Deploy instances in parallel"
    )
    parser.add_argument("--instance", help="Deploy to specific instance only")
    parser.add_argument(
        "--skip-build", action="store_true", help="Skip Docker image build"
    )

    args = parser.parse_args()

    orchestrator = SophiaDeploymentOrchestrator()

    try:
        if args.instance:
            # Deploy to specific instance
            if args.instance not in orchestrator.deployment_config:
                logger.error(f"Unknown instance: {args.instance}")
                sys.exit(1)

            config = orchestrator.deployment_config[args.instance]
            success = orchestrator.deploy_to_instance(args.instance, config)

            if success:
                health = orchestrator.health_check_instance(args.instance, config["ip"])
                orchestrator.deployment_report["instances"][args.instance][
                    "health"
                ] = health
        else:
            # Deploy to all instances
            success = orchestrator.deploy_all(parallel=args.parallel)

        # Generate report
        orchestrator.generate_report()

        # Print summary
        orchestrator.print_summary()

        sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        logger.warning("Deployment interrupted by user")
        orchestrator.deployment_report["status"] = "interrupted"
        orchestrator.generate_report()
        sys.exit(1)
    except Exception as e:
        logger.error(f"Deployment failed with error: {e}")
        orchestrator.deployment_report["status"] = "failed"
        orchestrator.deployment_report["error"] = str(e)
        orchestrator.generate_report()
        sys.exit(1)


if __name__ == "__main__":
    main()
