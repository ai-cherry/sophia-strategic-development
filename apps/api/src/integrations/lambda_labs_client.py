#!/usr/bin/env python3
"""
Unified Lambda Labs Client for Sophia AI
Consolidates all Lambda Labs functionality into a single, reusable client.
Uses actual production server configuration.
"""

import logging
import os
import subprocess
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional

import requests

from backend.core.auto_esc_config import get_config_value

logger = logging.getLogger(__name__)


class InstanceType(Enum):
    """Lambda Labs GPU instance types"""

    GPU_1X_RTX6000 = "gpu_1x_rtx6000"
    GPU_1X_GH200 = "gpu_1x_gh200"
    GPU_1X_A6000 = "gpu_1x_a6000"
    GPU_1X_A100 = "gpu_1x_a100"
    GPU_1X_A10 = "gpu_1x_a10"


class Region(Enum):
    """Lambda Labs regions"""

    US_SOUTH_1 = "us-south-1"
    US_EAST_3 = "us-east-3"
    US_WEST_1 = "us-west-1"


@dataclass
class LambdaInstance:
    """Lambda Labs instance information"""

    name: str
    ip: str
    instance_type: InstanceType
    region: Region
    ssh_login: str
    status: Optional[str] = None
    id: Optional[str] = None


class LambdaLabsClient:
    """Unified client for Lambda Labs operations"""

    # Production server configuration
    PRODUCTION_SERVERS = {
        "sophia-production-instance": LambdaInstance(
            name="sophia-production-instance",
            ip="104.171.202.103",
            instance_type=InstanceType.GPU_1X_RTX6000,
            region=Region.US_SOUTH_1,
            ssh_login="ssh ubuntu@104.171.202.103",
        ),
        "sophia-ai-core": LambdaInstance(
            name="sophia-ai-core",
            ip="192.222.58.232",
            instance_type=InstanceType.GPU_1X_GH200,
            region=Region.US_EAST_3,
            ssh_login="ssh ubuntu@192.222.58.232",
        ),
        "sophia-mcp-orchestrator": LambdaInstance(
            name="sophia-mcp-orchestrator",
            ip="104.171.202.117",
            instance_type=InstanceType.GPU_1X_A6000,
            region=Region.US_SOUTH_1,
            ssh_login="ssh ubuntu@104.171.202.117",
        ),
        "sophia-data-pipeline": LambdaInstance(
            name="sophia-data-pipeline",
            ip="104.171.202.134",
            instance_type=InstanceType.GPU_1X_A100,
            region=Region.US_SOUTH_1,
            ssh_login="ssh ubuntu@104.171.202.134",
        ),
        "sophia-development": LambdaInstance(
            name="sophia-development",
            ip="155.248.194.183",
            instance_type=InstanceType.GPU_1X_A10,
            region=Region.US_WEST_1,
            ssh_login="ssh ubuntu@155.248.194.183",
        ),
    }

    def __init__(self):
        """Initialize Lambda Labs client with credentials from Pulumi ESC"""
        # Get API credentials from Pulumi ESC
        self.api_key = get_config_value("lambda_labs_api_key")
        if not self.api_key:
            logger.warning(
                "Lambda Labs API key not found in Pulumi ESC, checking environment"
            )
            self.api_key = os.getenv("LAMBDA_LABS_API_KEY")

        self.api_endpoint = get_config_value(
            "lambda_labs_api_endpoint", "https://cloud.lambda.ai/api/v1"
        )

        # SSH configuration
        ssh_key_path = (
            get_config_value("lambda_labs_ssh_key_path", "~/.ssh/sophia_correct_key")
            or "~/.ssh/sophia_correct_key"
        )
        self.ssh_key_path = os.path.expanduser(ssh_key_path)

        # Verify SSH key exists
        if not os.path.exists(self.ssh_key_path):
            logger.warning(f"SSH key not found at {self.ssh_key_path}")

    def _make_api_request(
        self, endpoint: str, method: str = "GET", data: Optional[dict] = None
    ) -> dict:
        """Make authenticated API request to Lambda Labs"""
        if not self.api_key:
            raise ValueError("Lambda Labs API key not configured")

        url = f"{self.api_endpoint}/{endpoint}"
        headers = {"Authorization": f"Bearer {self.api_key}"}

        try:
            if method == "GET":
                response = requests.get(url, headers=headers, timeout=30)
            elif method == "POST":
                response = requests.post(url, headers=headers, json=data, timeout=30)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers, timeout=30)
            else:
                raise ValueError(f"Unsupported method: {method}")

            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Lambda Labs API request failed: {e}")
            raise

    def list_instances(self) -> list[LambdaInstance]:
        """List all Lambda Labs instances"""
        logger.info("Fetching Lambda Labs instances...")

        # Return our known production servers
        # In production, we could also fetch from API and merge with known servers
        return list(self.PRODUCTION_SERVERS.values())

    def get_instance(self, instance_name: str) -> Optional[LambdaInstance]:
        """Get a specific instance by name"""
        return self.PRODUCTION_SERVERS.get(instance_name)

    def ssh_command(
        self, instance_name: str, command: str, timeout: int = 300
    ) -> tuple[int, str, str]:
        """Execute SSH command on instance"""
        instance = self.get_instance(instance_name)
        if not instance:
            raise ValueError(f"Unknown instance: {instance_name}")

        ssh_cmd = [
            "ssh",
            "-i",
            self.ssh_key_path,
            "-o",
            "StrictHostKeyChecking=no",
            "-o",
            "UserKnownHostsFile=/dev/null",
            "-o",
            f"ConnectTimeout={timeout}",
            f"ubuntu@{instance.ip}",
            command,
        ]

        logger.info(f"Executing on {instance_name}: {command}")
        process = subprocess.Popen(
            ssh_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        stdout, stderr = process.communicate()

        return process.returncode, stdout.decode(), stderr.decode()

    def scp_file(self, instance_name: str, local_path: str, remote_path: str) -> bool:
        """Copy file to instance using SCP"""
        instance = self.get_instance(instance_name)
        if not instance:
            raise ValueError(f"Unknown instance: {instance_name}")

        scp_cmd = [
            "scp",
            "-i",
            self.ssh_key_path,
            "-o",
            "StrictHostKeyChecking=no",
            "-o",
            "UserKnownHostsFile=/dev/null",
            local_path,
            f"ubuntu@{instance.ip}:{remote_path}",
        ]

        logger.info(f"Copying {local_path} to {instance_name}:{remote_path}")
        process = subprocess.run(scp_cmd, capture_output=True, check=False)

        if process.returncode == 0:
            logger.info("File copied successfully")
            return True
        else:
            logger.error(f"Failed to copy file: {process.stderr.decode()}")
            return False

    def health_check(self, instance_name: str) -> dict[str, bool]:
        """Perform health check on deployed services"""
        instance = self.get_instance(instance_name)
        if not instance:
            raise ValueError(f"Unknown instance: {instance_name}")

        logger.info(f"Performing health check on {instance_name}")
        health_status = {}

        # Check backend
        try:
            response = requests.get(f"http://{instance.ip}:8000/health", timeout=10)
            health_status["backend"] = response.status_code == 200
        except:
            health_status["backend"] = False

        # Check MCP servers (ports 9000-9100)
        for port in range(9000, 9101, 10):
            try:
                response = requests.get(
                    f"http://{instance.ip}:{port}/health", timeout=5
                )
                health_status[f"mcp_{port}"] = response.status_code == 200
            except:
                health_status[f"mcp_{port}"] = False

        # Check monitoring services
        try:
            response = requests.get(f"http://{instance.ip}:9090/-/healthy", timeout=5)
            health_status["prometheus"] = response.status_code == 200
        except:
            health_status["prometheus"] = False

        try:
            response = requests.get(f"http://{instance.ip}:3000/api/health", timeout=5)
            health_status["grafana"] = response.status_code == 200
        except:
            health_status["grafana"] = False

        return health_status

    def deploy_sophia(self, instance_name: str, deployment_type: str = "full") -> bool:
        """Deploy Sophia AI to Lambda Labs instance"""
        instance = self.get_instance(instance_name)
        if not instance:
            raise ValueError(f"Unknown instance: {instance_name}")

        logger.info(f"Deploying Sophia AI to {instance_name} (type: {deployment_type})")

        # Use unified Kubernetes deployment script
        deployment_script = (
            "/home/ubuntu/sophia-main/scripts/deploy_unified_kubernetes.sh"
        )

        # Execute deployment
        command = (
            f"cd /home/ubuntu/sophia-main && bash {deployment_script} {deployment_type}"
        )
        returncode, stdout, stderr = self.ssh_command(
            instance_name, command, timeout=1800
        )

        if returncode == 0:
            logger.info("Deployment successful!")
            logger.info(stdout)
            return True
        else:
            logger.error("Deployment failed!")
            logger.error(stderr)
            return False

    def get_instance_metrics(self, instance_name: str) -> dict:
        """Get instance metrics and resource usage"""
        instance = self.get_instance(instance_name)
        if not instance:
            raise ValueError(f"Unknown instance: {instance_name}")

        metrics = {
            "instance": instance_name,
            "ip": instance.ip,
            "type": instance.instance_type.value,
            "region": instance.region.value,
            "timestamp": datetime.utcnow().isoformat(),
        }

        # Get system metrics
        commands = {
            "cpu_usage": "top -bn1 | grep 'Cpu(s)' | awk '{print $2}' | cut -d'%' -f1",
            "memory_usage": "free -m | awk 'NR==2{printf \"%.2f\", $3*100/$2}'",
            "disk_usage": "df -h / | awk 'NR==2{print $5}' | cut -d'%' -f1",
            "gpu_usage": "nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits",
            "gpu_memory": "nvidia-smi --query-gpu=memory.used,memory.total --format=csv,noheader,nounits",
        }

        for metric_name, command in commands.items():
            try:
                returncode, stdout, stderr = self.ssh_command(
                    instance_name, command, timeout=30
                )
                if returncode == 0:
                    metrics[metric_name] = stdout.strip()
            except:
                metrics[metric_name] = "N/A"

        return metrics

    def get_deployment_status(self) -> dict:
        """Get deployment status across all instances"""
        status = {"timestamp": datetime.utcnow().isoformat(), "instances": {}}

        for instance_name, instance in self.PRODUCTION_SERVERS.items():
            instance_status = {
                "ip": instance.ip,
                "type": instance.instance_type.value,
                "region": instance.region.value,
                "health": {},
            }

            try:
                instance_status["health"] = self.health_check(instance_name)
                instance_status["status"] = (
                    "healthy" if all(instance_status["health"].values()) else "degraded"
                )
            except Exception as e:
                instance_status["status"] = "error"
                instance_status["error"] = str(e)

            status["instances"][instance_name] = instance_status

        return status


# Singleton instance
_client = None


def get_lambda_labs_client() -> LambdaLabsClient:
    """Get or create Lambda Labs client singleton"""
    global _client
    if _client is None:
        _client = LambdaLabsClient()
    return _client
