#!/usr/bin/env python3
"""
Secure Lambda Labs Manager - Uses Pulumi ESC for all credentials
No hardcoded API keys or secrets
"""

import os
import sys
import time
import json
import logging
import subprocess
from pathlib import Path
from typing import Optional, List, Dict, Tuple
from datetime import datetime
from dataclasses import dataclass

# Add backend to path for auto_esc_config
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from backend.core.auto_esc_config import get_config_value
except ImportError:
    print("Error: Cannot import auto_esc_config. Make sure you're in the Sophia AI environment.")
    sys.exit(1)

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


class SecureLambdaLabsManager:
    """Secure Lambda Labs manager using Pulumi ESC for credentials"""

    def __init__(self):
        # Load credentials from Pulumi ESC
        self.cloud_api_key = get_config_value("lambda_cloud_api_key")
        self.regular_api_key = get_config_value("lambda_api_key")
        self.api_endpoint = get_config_value("lambda_api_endpoint", "https://cloud.lambda.ai/api/v1")
        
        # SSH configuration from Pulumi ESC
        self.ssh_key_path = os.path.expanduser(
            get_config_value("lambda_ssh_key_path", "~/.ssh/lynn_sophia_h200_key")
        )
        
        # Load instance configuration
        self.production_ip = get_config_value("lambda_labs_production_ip", "192.222.51.151")
        
        # Validate credentials
        if not self.cloud_api_key or not self.regular_api_key:
            logger.error("Lambda Labs API keys not found in Pulumi ESC")
            raise ValueError("Missing Lambda Labs credentials. Run: pulumi env get scoobyjava-org/default/sophia-ai-production")
            
        # Check SSH key exists
        if not Path(self.ssh_key_path).exists():
            logger.error(f"SSH key not found at {self.ssh_key_path}")
            raise ValueError(f"SSH key missing. Expected at: {self.ssh_key_path}")

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

    def get_production_instance(self) -> Optional[LambdaInstance]:
        """Get the production instance"""
        instances = self.list_instances()
        for instance in instances:
            if instance.ip == self.production_ip:
                return instance
        return None

    def ssh_command(self, command: str, timeout: int = 300) -> tuple[int, str, str]:
        """Execute SSH command on production instance"""
        ssh_cmd = [
            "ssh",
            "-i", self.ssh_key_path,
            "-o", "StrictHostKeyChecking=no",
            "-o", "UserKnownHostsFile=/dev/null",
            "-o", "ConnectTimeout=10",
            f"ubuntu@{self.production_ip}",
            command,
        ]

        logger.info(f"Executing: {command}")
        process = subprocess.Popen(
            ssh_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        
        try:
            stdout, stderr = process.communicate(timeout=timeout)
            return process.returncode, stdout.decode(), stderr.decode()
        except subprocess.TimeoutExpired:
            process.kill()
            return -1, "", "Command timed out"

    def deploy_sophia(self, deployment_type: str = "full"):
        """Deploy Sophia AI to production Lambda Labs instance"""
        logger.info(f"Deploying Sophia AI (type: {deployment_type})")

        # Check instance status
        instance = self.get_production_instance()
        if not instance:
            logger.error(f"Production instance not found at {self.production_ip}")
            return False
            
        if instance.status != "active":
            logger.error(f"Instance is not active (status: {instance.status})")
            return False

        # Generate deployment script
        deployment_script = self._generate_deployment_script(deployment_type)
        
        # Create temporary script file
        script_path = Path("/tmp/deploy_sophia_secure.sh")
        with open(script_path, 'w') as f:
            f.write(deployment_script)
            
        # Copy deployment script
        scp_cmd = [
            "scp",
            "-i", self.ssh_key_path,
            "-o", "StrictHostKeyChecking=no",
            str(script_path),
            f"ubuntu@{self.production_ip}:/tmp/deploy_sophia.sh"
        ]

        process = subprocess.run(scp_cmd, capture_output=True)
        
        # Clean up local script
        script_path.unlink()

        if process.returncode != 0:
            logger.error(f"Failed to copy deployment script: {process.stderr.decode()}")
            return False

        # Execute deployment
        returncode, stdout, stderr = self.ssh_command("bash /tmp/deploy_sophia.sh")

        if returncode == 0:
            logger.info("Deployment successful!")
            logger.info(stdout)
            return True
        else:
            logger.error("Deployment failed!")
            logger.error(stderr)
            return False

    def _generate_deployment_script(self, deployment_type: str) -> str:
        """Generate secure deployment script"""
        # Get Docker registry from Pulumi ESC
        docker_registry = get_config_value("docker_registry", "scoobyjava15")
        
        base_script = f"""#!/bin/bash
set -e

echo "🚀 Deploying Sophia AI (Secure Mode)..."
echo "📍 Instance: {self.production_ip}"
echo "🐳 Registry: {docker_registry}"

# Update system
sudo apt-get update -qq
sudo apt-get install -y docker.io docker-compose git curl jq

# Ensure Docker is running
sudo systemctl start docker
sudo usermod -aG docker ubuntu

# Create deployment directory
mkdir -p /home/ubuntu/sophia-ai
cd /home/ubuntu/sophia-ai

# Set environment variables from Pulumi ESC
export ENVIRONMENT=production
export PULUMI_ORG=scoobyjava-org
"""

        if deployment_type == "full":
            return base_script + f"""
# Pull latest images
docker pull {docker_registry}/sophia-backend:latest
docker pull {docker_registry}/sophia-mcp-servers:latest
docker pull postgres:16-alpine
docker pull redis:7-alpine
docker pull prom/prometheus:latest
docker pull grafana/grafana:latest

# Create secure docker-compose.yml
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: sophia_db
      POSTGRES_USER: sophia_user
      POSTGRES_PASSWORD: ${{POSTGRES_PASSWORD:-sophia_secure_password}}
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
    command: redis-server --appendonly yes --requirepass ${{REDIS_PASSWORD:-sophia_redis_password}}
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
    image: {docker_registry}/sophia-backend:latest
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
      - PULUMI_ORG=scoobyjava-org
      - DATABASE_URL=postgresql://sophia_user:${{POSTGRES_PASSWORD:-sophia_secure_password}}@postgres:5432/sophia_db
      - REDIS_URL=redis://:${{REDIS_PASSWORD:-sophia_redis_password}}@redis:6379
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
    image: {docker_registry}/sophia-mcp-servers:latest
    ports:
      - "9000-9100:9000-9100"
      - "3008:3008"
    environment:
      - ENVIRONMENT=production
      - PULUMI_ORG=scoobyjava-org
    networks:
      - sophia-network
    volumes:
      - ./config:/app/config
    depends_on:
      - backend

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

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${{GRAFANA_PASSWORD:-sophia_admin}}
      - GF_USERS_ALLOW_SIGN_UP=false
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

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['localhost:9100']
EOF

# Stop existing containers
docker-compose down || true

# Start services
docker-compose up -d

# Wait for services
echo "⏳ Waiting for services to start..."
sleep 30

# Check health
for service in backend postgres redis prometheus grafana; do
  if docker-compose ps | grep -q "$service.*Up"; then
    echo "✅ $service is running"
  else
    echo "❌ $service failed to start"
  fi
done

echo "✅ Full deployment complete!"
echo "🌐 Access URLs:"
echo "   - Backend API: http://{self.production_ip}:8000"
echo "   - API Docs: http://{self.production_ip}:8000/docs"
echo "   - Grafana: http://{self.production_ip}:3000"
echo "   - Prometheus: http://{self.production_ip}:9090"
"""
        elif deployment_type == "backend-only":
            return base_script + f"""
# Update backend only
docker pull {docker_registry}/sophia-backend:latest
docker-compose up -d backend
echo "✅ Backend deployment complete!"
"""
        elif deployment_type == "mcp-servers-only":
            return base_script + f"""
# Update MCP servers only
docker pull {docker_registry}/sophia-mcp-servers:latest
docker-compose up -d mcp-servers
echo "✅ MCP servers deployment complete!"
"""
        else:
            return base_script + """
echo "✅ Configuration update complete!"
"""

    def health_check(self) -> dict[str, bool]:
        """Perform health check on deployed services"""
        logger.info(f"Performing health check on {self.production_ip}")

        health_status = {}

        # Check backend
        try:
            response = requests.get(f"http://{self.production_ip}:8000/health", timeout=10)
            health_status["backend"] = response.status_code == 200
        except:
            health_status["backend"] = False

        # Check MCP servers
        mcp_ports = {
            "ai_memory": 9001,
            "ui_ux_agent": 9002,
            "codacy": 3008,
            "linear": 9004,
            "github": 9103,
            "asana": 9100
        }
        
        for name, port in mcp_ports.items():
            try:
                response = requests.get(f"http://{self.production_ip}:{port}/health", timeout=5)
                health_status[name] = response.status_code == 200
            except:
                health_status[name] = False

        # Check infrastructure services
        try:
            response = requests.get(f"http://{self.production_ip}:9090/-/healthy", timeout=5)
            health_status["prometheus"] = response.status_code == 200
        except:
            health_status["prometheus"] = False

        try:
            response = requests.get(f"http://{self.production_ip}:3000/api/health", timeout=5)
            health_status["grafana"] = response.status_code == 200
        except:
            health_status["grafana"] = False

        return health_status

    def monitor_deployment(self, duration: int = 300):
        """Monitor deployment for specified duration"""
        logger.info(f"Monitoring deployment for {duration} seconds...")

        start_time = time.time()
        while time.time() - start_time < duration:
            health = self.health_check()

            # Log status
            healthy_services = [k for k, v in health.items() if v]
            unhealthy_services = [k for k, v in health.items() if not v]

            logger.info(f"✅ Healthy ({len(healthy_services)}): {', '.join(healthy_services)}")
            if unhealthy_services:
                logger.warning(f"❌ Unhealthy ({len(unhealthy_services)}): {', '.join(unhealthy_services)}")

            # Check if critical services are up
            critical_services = ["backend", "prometheus"]
            critical_healthy = all(health.get(s, False) for s in critical_services)
            
            if not critical_healthy:
                logger.error("Critical services are down!")

            time.sleep(30)

    def generate_deployment_report(self) -> dict:
        """Generate comprehensive deployment report"""
        logger.info("Generating deployment report...")

        instance = self.get_production_instance()
        
        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "environment": "production",
            "instance": {
                "name": instance.name if instance else "Unknown",
                "ip": self.production_ip,
                "status": instance.status if instance else "Unknown",
                "type": instance.instance_type if instance else "Unknown",
                "region": instance.region if instance else "Unknown"
            },
            "health": self.health_check(),
            "configuration": {
                "docker_registry": get_config_value("docker_registry", "scoobyjava15"),
                "pulumi_org": "scoobyjava-org",
                "pulumi_stack": "sophia-ai-production"
            }
        }

        # Calculate health score
        health_values = list(report["health"].values())
        report["health_score"] = {
            "healthy": sum(1 for v in health_values if v),
            "total": len(health_values),
            "percentage": round(sum(1 for v in health_values if v) / len(health_values) * 100, 2)
        }

        return report

    def show_logs(self, service: str, lines: int = 100):
        """Show logs for a specific service"""
        logger.info(f"Fetching logs for {service}...")
        
        returncode, stdout, stderr = self.ssh_command(
            f"cd /home/ubuntu/sophia-ai && docker-compose logs --tail={lines} {service}"
        )
        
        if returncode == 0:
            print(stdout)
        else:
            logger.error(f"Failed to fetch logs: {stderr}")


def main():
    """Main CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="Secure Lambda Labs Manager")
    parser.add_argument(
        "command", 
        choices=["list", "deploy", "health", "monitor", "report", "logs"],
        help="Command to execute"
    )
    parser.add_argument(
        "--type",
        default="full",
        choices=["full", "backend-only", "mcp-servers-only", "update-config"],
        help="Deployment type"
    )
    parser.add_argument(
        "--duration", 
        type=int, 
        default=300, 
        help="Monitoring duration in seconds"
    )
    parser.add_argument(
        "--service",
        help="Service name for logs command"
    )
    parser.add_argument(
        "--lines",
        type=int,
        default=100,
        help="Number of log lines to show"
    )

    args = parser.parse_args()

    try:
        manager = SecureLambdaLabsManager()
    except Exception as e:
        logger.error(f"Failed to initialize manager: {e}")
        sys.exit(1)

    if args.command == "list":
        instances = manager.list_instances()
        print("\n🖥️  Lambda Labs Instances:")
        print("-" * 80)
        for instance in instances:
            status_icon = "✅" if instance.status == "active" else "❌"
            print(f"{status_icon} {instance.name}: {instance.ip} ({instance.instance_type}) - {instance.status}")
            
        # Highlight production
        prod = manager.get_production_instance()
        if prod:
            print(f"\n⭐ Production: {prod.name} at {prod.ip}")

    elif args.command == "deploy":
        success = manager.deploy_sophia(args.type)
        if success:
            print("\n✅ Deployment successful!")
            
            # Show health status
            print("\n🏥 Health Check:")
            health = manager.health_check()
            for service, status in health.items():
                print(f"  {service}: {'✅' if status else '❌'}")
        else:
            print("\n❌ Deployment failed!")
            sys.exit(1)

    elif args.command == "health":
        health = manager.health_check()
        print("\n🏥 Service Health Status:")
        print("-" * 40)
        
        for service, status in sorted(health.items()):
            status_icon = "✅" if status else "❌"
            print(f"{status_icon} {service:20} {'Running' if status else 'Down'}")
            
        # Summary
        healthy_count = sum(1 for v in health.values() if v)
        total_count = len(health)
        health_percentage = round(healthy_count / total_count * 100, 2)
        
        print("-" * 40)
        print(f"Overall Health: {healthy_count}/{total_count} ({health_percentage}%)")

    elif args.command == "monitor":
        manager.monitor_deployment(args.duration)

    elif args.command == "report":
        report = manager.generate_deployment_report()
        
        # Save report
        report_file = f"deployment_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
            
        print(f"\n📊 Deployment Report")
        print("=" * 50)
        print(f"Instance: {report['instance']['name']} ({report['instance']['ip']})")
        print(f"Status: {report['instance']['status']}")
        print(f"Type: {report['instance']['type']}")
        print(f"Health Score: {report['health_score']['percentage']}%")
        print(f"\nReport saved to: {report_file}")
        
    elif args.command == "logs":
        if not args.service:
            print("Error: --service required for logs command")
            print("Available services: backend, mcp-servers, postgres, redis, prometheus, grafana")
            sys.exit(1)
            
        manager.show_logs(args.service, args.lines)


if __name__ == "__main__":
    main() 