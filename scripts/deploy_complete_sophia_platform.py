#!/usr/bin/env python3
"""
Sophia AI Complete Platform Deployment Script

This script deploys the entire Sophia AI platform including:
- All MCP servers (AI Memory, Gong, Snowflake, Linear, Slack, etc.)
- Unified Chat Interface
- Unified Dashboard
- Backend services
- Frontend applications
- Monitoring and observability
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(
            f'deployment_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
        ),
    ],
)
logger = logging.getLogger(__name__)

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

try:
    from backend.core.auto_esc_config import get_config_value
except ImportError:
    logger.warning("Could not import auto_esc_config, using environment variables")

    def get_config_value(key: str, default: str = None) -> str:
        return os.getenv(key.upper(), default)


class SophiaPlatformDeployer:
    """Complete Sophia AI Platform Deployment Manager"""

    def __init__(self):
        self.deployment_start_time = time.time()
        self.deployment_report = {
            "timestamp": datetime.now().isoformat(),
            "environment": "production",
            "components": {},
            "services": {},
            "mcp_servers": {},
            "success": False,
        }

        # Lambda Labs configuration
        self.lambda_labs_host = os.getenv(
            "LAMBDA_LABS_HOST", get_config_value("LAMBDA_LABS_HOST", "192.222.51.151")
        )
        self.ssh_key = os.path.expanduser(
            os.getenv(
                "LAMBDA_SSH_KEY_PATH",
                get_config_value("LAMBDA_SSH_KEY_PATH", "~/.ssh/lynn_sophia_h200_key"),
            )
        )

        # Docker configuration
        self.docker_registry = get_config_value("DOCKER_REGISTRY", "scoobyjava15")
        self.image_tag = get_config_value("IMAGE_TAG", "latest")

        # MCP server configurations with updated ports
        self.mcp_servers = [
            {"name": "ai-memory-v2", "port": 9001, "type": "core"},
            {"name": "gong-v2", "port": 9002, "type": "integration"},
            {"name": "snowflake-v2", "port": 9003, "type": "data"},
            {"name": "slack-v2", "port": 9004, "type": "communication"},
            {"name": "notion-v2", "port": 9005, "type": "productivity"},
            {"name": "linear-v2", "port": 9006, "type": "project"},
            {"name": "github-v2", "port": 9007, "type": "development"},
            {"name": "codacy-v2", "port": 9008, "type": "quality"},
            {"name": "asana-v2", "port": 9009, "type": "project"},
            {"name": "perplexity-v2", "port": 9010, "type": "ai"},
        ]

    def print_banner(self):
        """Print deployment banner"""
        banner = """
╔══════════════════════════════════════════════════════════════════════╗
║                  SOPHIA AI COMPLETE PLATFORM DEPLOYMENT               ║
║                                                                       ║
║  Components:                                                          ║
║  • Unified Chat Interface with WebSocket support                     ║
║  • Unified Dashboard with real-time monitoring                       ║
║  • 10 MCP Servers (AI Memory, Gong, Snowflake, etc.)                ║
║  • Backend API with FastAPI                                          ║
║  • Frontend with React + TypeScript                                  ║
║  • Monitoring with Prometheus + Grafana                              ║
║  • Redis caching and PostgreSQL database                             ║
║                                                                       ║
║  Target: Lambda Labs Infrastructure                                   ║
╚══════════════════════════════════════════════════════════════════════╝
        """
        logger.info(banner)

    def check_prerequisites(self) -> bool:
        """Check deployment prerequisites"""
        logger.info("🔍 Checking prerequisites...")

        # Check Docker
        try:
            result = subprocess.run(
                ["docker", "--version"], capture_output=True, text=True, check=False
            )
            if result.returncode == 0:
                logger.info(f"✅ Docker: {result.stdout.strip()}")
            else:
                logger.error("❌ Docker not found")
                return False
        except Exception as e:
            logger.error(f"❌ Docker check failed: {e}")
            return False

        # Check SSH key
        if not Path(self.ssh_key).exists():
            logger.error(f"❌ SSH key not found: {self.ssh_key}")
            return False
        logger.info(f"✅ SSH key found: {self.ssh_key}")

        # Check SSH connectivity
        try:
            result = subprocess.run(
                [
                    "ssh",
                    "-o",
                    "ConnectTimeout=5",
                    "-o",
                    "StrictHostKeyChecking=no",
                    "-i",
                    self.ssh_key,
                    f"ubuntu@{self.lambda_labs_host}",
                    "echo 'Connected'",
                ],
                capture_output=True,
                text=True, check=False,
            )
            if result.returncode == 0:
                logger.info(f"✅ SSH connection to {self.lambda_labs_host}")
            else:
                logger.error(f"❌ Cannot connect to Lambda Labs: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"❌ SSH check failed: {e}")
            return False

        return True

    def build_images(self) -> bool:
        """Build all Docker images"""
        logger.info("🔨 Building Docker images...")

        images_to_build = [
            {
                "name": "sophia-backend",
                "context": ".",
                "dockerfile": "Dockerfile.production",
                "tag": f"{self.docker_registry}/sophia-backend:{self.image_tag}",
            },
            {
                "name": "sophia-frontend",
                "context": "frontend",
                "dockerfile": "frontend/Dockerfile",
                "tag": f"{self.docker_registry}/sophia-frontend:{self.image_tag}",
            },
        ]

        # Add MCP server images
        for mcp_server in self.mcp_servers:
            server_name = mcp_server["name"]
            server_dir = f"infrastructure/mcp_servers/{server_name.replace('-', '_')}"
            if Path(server_dir).exists():
                images_to_build.append(
                    {
                        "name": f"sophia-{server_name}",
                        "context": server_dir,
                        "dockerfile": f"{server_dir}/Dockerfile",
                        "tag": f"{self.docker_registry}/sophia-{server_name}:{self.image_tag}",
                    }
                )

        # Build each image
        for image in images_to_build:
            logger.info(f"Building {image['name']}...")
            try:
                result = subprocess.run(
                    [
                        "docker",
                        "build",
                        "-t",
                        image["tag"],
                        "-f",
                        image["dockerfile"],
                        image["context"],
                    ],
                    capture_output=True,
                    text=True, check=False,
                )
                if result.returncode == 0:
                    logger.info(f"✅ Built {image['name']}")
                    self.deployment_report["components"][image["name"]] = "built"
                else:
                    logger.error(f"❌ Failed to build {image['name']}: {result.stderr}")
                    return False
            except Exception as e:
                logger.error(f"❌ Build error for {image['name']}: {e}")
                return False

        return True

    def push_images(self) -> bool:
        """Push Docker images to registry"""
        logger.info("📤 Pushing images to Docker Hub...")

        # Login to Docker Hub
        try:
            docker_password = get_config_value("DOCKER_HUB_ACCESS_TOKEN")
            if docker_password:
                login_result = subprocess.run(
                    ["docker", "login", "-u", self.docker_registry, "--password-stdin"],
                    input=docker_password,
                    capture_output=True,
                    text=True, check=False,
                )
                if login_result.returncode != 0:
                    logger.error(f"❌ Docker login failed: {login_result.stderr}")
                    return False
        except Exception as e:
            logger.error(f"❌ Docker login error: {e}")
            return False

        # Push images
        images_to_push = [
            f"{self.docker_registry}/sophia-backend:{self.image_tag}",
            f"{self.docker_registry}/sophia-frontend:{self.image_tag}",
        ]

        for mcp_server in self.mcp_servers:
            images_to_push.append(
                f"{self.docker_registry}/sophia-{mcp_server['name']}:{self.image_tag}"
            )

        for image in images_to_push:
            logger.info(f"Pushing {image}...")
            try:
                result = subprocess.run(
                    ["docker", "push", image], capture_output=True, text=True, check=False
                )
                if result.returncode == 0:
                    logger.info(f"✅ Pushed {image}")
                else:
                    logger.error(f"❌ Failed to push {image}: {result.stderr}")
                    return False
            except Exception as e:
                logger.error(f"❌ Push error for {image}: {e}")
                return False

        return True

    def deploy_to_lambda_labs(self) -> bool:
        """Deploy to Lambda Labs using Docker Swarm"""
        logger.info("🚀 Deploying to Lambda Labs...")

        # Create deployment package
        deploy_dir = Path("deployment_package")
        deploy_dir.mkdir(exist_ok=True)

        # Create unified Docker Compose file
        compose_content = self.generate_unified_compose()
        compose_file = deploy_dir / "docker-compose.unified.yml"
        compose_file.write_text(compose_content)

        # Create deployment script
        deploy_script = f"""#!/bin/bash
set -euo pipefail

echo "🚀 Deploying Sophia AI Platform"

# Set environment variables
export DOCKER_REGISTRY={self.docker_registry}
export IMAGE_TAG={self.image_tag}
export ENVIRONMENT=prod
export PULUMI_ORG=scoobyjava-org

# Initialize Docker Swarm if needed
if ! docker info | grep -q "Swarm: active"; then
    echo "Initializing Docker Swarm..."
    docker swarm init
fi

# Create Docker secrets
echo "Creating Docker secrets..."
# Add your secret creation commands here

# Deploy stack
echo "Deploying stack..."
docker stack deploy -c docker-compose.unified.yml sophia-ai --with-registry-auth

# Wait for services to start
echo "Waiting for services to start..."
sleep 30

# Check service status
docker stack services sophia-ai

echo "✅ Deployment complete!"
"""

        deploy_script_file = deploy_dir / "deploy.sh"
        deploy_script_file.write_text(deploy_script)
        deploy_script_file.chmod(0o755)

        # Copy to Lambda Labs
        logger.info("Copying deployment files to Lambda Labs...")
        try:
            # Copy deployment directory
            scp_result = subprocess.run(
                [
                    "scp",
                    "-r",
                    "-i",
                    self.ssh_key,
                    str(deploy_dir),
                    f"ubuntu@{self.lambda_labs_host}:~/",
                ],
                capture_output=True,
                text=True, check=False,
            )
            if scp_result.returncode != 0:
                logger.error(f"❌ Failed to copy files: {scp_result.stderr}")
                return False

            # Execute deployment script
            logger.info("Executing deployment on Lambda Labs...")
            ssh_result = subprocess.run(
                [
                    "ssh",
                    "-i",
                    self.ssh_key,
                    f"ubuntu@{self.lambda_labs_host}",
                    "cd ~/deployment_package && ./deploy.sh",
                ],
                capture_output=True,
                text=True, check=False,
            )
            if ssh_result.returncode == 0:
                logger.info("✅ Deployment executed successfully")
                self.deployment_report["services"]["deployment"] = "success"
            else:
                logger.error(f"❌ Deployment failed: {ssh_result.stderr}")
                return False

        except Exception as e:
            logger.error(f"❌ Deployment error: {e}")
            return False

        return True

    def generate_unified_compose(self) -> str:
        """Generate unified Docker Compose configuration"""
        compose = {
            "version": "3.8",
            "services": {
                # Backend service
                "sophia-backend": {
                    "image": f"{self.docker_registry}/sophia-backend:{self.image_tag}",
                    "environment": [
                        "ENVIRONMENT=prod",
                        "PULUMI_ORG=scoobyjava-org",
                        "LOG_LEVEL=INFO",
                        "REDIS_URL=redis://redis:6379",
                        "POSTGRES_URL=postgresql://sophia:password@postgres:5432/sophia",
                    ],
                    "ports": ["8000:8000"],
                    "deploy": {
                        "replicas": 3,
                        "resources": {
                            "limits": {"cpus": "2.0", "memory": "4G"},
                            "reservations": {"cpus": "1.0", "memory": "2G"},
                        },
                    },
                    "healthcheck": {
                        "test": ["CMD", "curl", "-f", "http://localhost:8000/health"],
                        "interval": "30s",
                        "timeout": "10s",
                        "retries": 3,
                    },
                    "networks": ["sophia-network"],
                },
                # Frontend service
                "sophia-frontend": {
                    "image": f"{self.docker_registry}/sophia-frontend:{self.image_tag}",
                    "environment": [
                        "REACT_APP_API_URL=http://sophia-backend:8000",
                        "REACT_APP_WS_URL=ws://sophia-backend:8000/ws",
                    ],
                    "ports": ["3000:3000"],
                    "deploy": {
                        "replicas": 2,
                        "resources": {
                            "limits": {"cpus": "1.0", "memory": "2G"},
                            "reservations": {"cpus": "0.5", "memory": "1G"},
                        },
                    },
                    "networks": ["sophia-network"],
                },
                # MCP Gateway
                "mcp-gateway": {
                    "image": f"{self.docker_registry}/sophia-mcp-gateway:{self.image_tag}",
                    "environment": ["ENVIRONMENT=prod", "LOG_LEVEL=INFO"],
                    "ports": ["8080:8080"],
                    "deploy": {
                        "replicas": 2,
                        "resources": {
                            "limits": {"cpus": "1.0", "memory": "2G"},
                            "reservations": {"cpus": "0.5", "memory": "1G"},
                        },
                    },
                    "networks": ["sophia-network"],
                },
                # Redis
                "redis": {
                    "image": "redis:7-alpine",
                    "command": "redis-server --appendonly yes",
                    "ports": ["6379:6379"],
                    "volumes": ["redis_data:/data"],
                    "deploy": {
                        "replicas": 1,
                        "resources": {
                            "limits": {"cpus": "0.5", "memory": "1G"},
                            "reservations": {"cpus": "0.25", "memory": "512M"},
                        },
                    },
                    "networks": ["sophia-network"],
                },
                # PostgreSQL
                "postgres": {
                    "image": "postgres:16-alpine",
                    "environment": [
                        "POSTGRES_DB=sophia",
                        "POSTGRES_USER=sophia",
                        "POSTGRES_PASSWORD=password",
                    ],
                    "ports": ["5432:5432"],
                    "volumes": ["postgres_data:/var/lib/postgresql/data"],
                    "deploy": {
                        "replicas": 1,
                        "resources": {
                            "limits": {"cpus": "2.0", "memory": "4G"},
                            "reservations": {"cpus": "1.0", "memory": "2G"},
                        },
                    },
                    "networks": ["sophia-network"],
                },
            },
            "volumes": {
                "redis_data": {"driver": "local"},
                "postgres_data": {"driver": "local"},
            },
            "networks": {"sophia-network": {"driver": "overlay", "attachable": True}},
        }

        # Add MCP servers
        for mcp_server in self.mcp_servers:
            service_name = f"mcp-{mcp_server['name']}"
            compose["services"][service_name] = {
                "image": f"{self.docker_registry}/sophia-{mcp_server['name']}:{self.image_tag}",
                "environment": [
                    "ENVIRONMENT=prod",
                    "LOG_LEVEL=INFO",
                    f"MCP_PORT={mcp_server['port']}",
                ],
                "ports": [f"{mcp_server['port']}:{mcp_server['port']}"],
                "deploy": {
                    "replicas": 1,
                    "resources": {
                        "limits": {"cpus": "1.0", "memory": "2G"},
                        "reservations": {"cpus": "0.5", "memory": "1G"},
                    },
                },
                "healthcheck": {
                    "test": [
                        "CMD",
                        "curl",
                        "-f",
                        f"http://localhost:{mcp_server['port']}/health",
                    ],
                    "interval": "30s",
                    "timeout": "10s",
                    "retries": 3,
                },
                "networks": ["sophia-network"],
            }

        import yaml

        return yaml.dump(compose, default_flow_style=False)

    def validate_deployment(self) -> bool:
        """Validate the deployment"""
        logger.info("🔍 Validating deployment...")

        # Check main services
        services_to_check = [
            {
                "name": "Backend API",
                "url": f"http://{self.lambda_labs_host}:8000/health",
            },
            {"name": "Frontend", "url": f"http://{self.lambda_labs_host}:3000"},
            {
                "name": "MCP Gateway",
                "url": f"http://{self.lambda_labs_host}:8080/health",
            },
        ]

        # Add MCP server checks
        for mcp_server in self.mcp_servers:
            services_to_check.append(
                {
                    "name": f"MCP {mcp_server['name']}",
                    "url": f"http://{self.lambda_labs_host}:{mcp_server['port']}/health",
                }
            )

        # Check each service
        import requests

        for service in services_to_check:
            try:
                response = requests.get(service["url"], timeout=10)
                if response.status_code == 200:
                    logger.info(f"✅ {service['name']} is healthy")
                    self.deployment_report["services"][service["name"]] = "healthy"
                else:
                    logger.warning(
                        f"⚠️  {service['name']} returned {response.status_code}"
                    )
                    self.deployment_report["services"][
                        service["name"]
                    ] = f"unhealthy ({response.status_code})"
            except Exception as e:
                logger.error(f"❌ {service['name']} is not responding: {e}")
                self.deployment_report["services"][service["name"]] = "not responding"

        return True

    def print_summary(self):
        """Print deployment summary"""
        duration = time.time() - self.deployment_start_time

        logger.info("\n" + "=" * 70)
        logger.info("DEPLOYMENT SUMMARY")
        logger.info("=" * 70)
        logger.info(f"Duration: {duration:.2f} seconds")
        logger.info("Environment: Production")
        logger.info(f"Target: {self.lambda_labs_host}")

        # Component status
        logger.info("\nComponents:")
        for component, status in self.deployment_report["components"].items():
            logger.info(f"  • {component}: {status}")

        # Service status
        logger.info("\nServices:")
        for service, status in self.deployment_report["services"].items():
            if "healthy" in status:
                logger.info(f"  ✅ {service}: {status}")
            else:
                logger.warning(f"  ⚠️  {service}: {status}")

        # Access URLs
        logger.info("\nAccess URLs:")
        logger.info(f"  • Dashboard: http://{self.lambda_labs_host}:3000")
        logger.info(f"  • API: http://{self.lambda_labs_host}:8000")
        logger.info(f"  • API Docs: http://{self.lambda_labs_host}:8000/docs")
        logger.info(f"  • MCP Gateway: http://{self.lambda_labs_host}:8080")

        # MCP Server URLs
        logger.info("\nMCP Servers:")
        for mcp_server in self.mcp_servers:
            logger.info(
                f"  • {mcp_server['name']}: http://{self.lambda_labs_host}:{mcp_server['port']}"
            )

        # Save deployment report
        report_file = (
            f"deployment_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(report_file, "w") as f:
            json.dump(self.deployment_report, f, indent=2)
        logger.info(f"\nDeployment report saved to: {report_file}")

    async def deploy(self) -> bool:
        """Execute the complete deployment"""
        self.print_banner()

        try:
            # Check prerequisites
            if not self.check_prerequisites():
                logger.error("❌ Prerequisites check failed")
                return False

            # Build images
            if not self.build_images():
                logger.error("❌ Image build failed")
                return False

            # Push images
            if not self.push_images():
                logger.error("❌ Image push failed")
                return False

            # Deploy to Lambda Labs
            if not self.deploy_to_lambda_labs():
                logger.error("❌ Deployment failed")
                return False

            # Validate deployment
            time.sleep(60)  # Wait for services to stabilize
            self.validate_deployment()

            # Print summary
            self.deployment_report["success"] = True
            self.print_summary()

            logger.info("\n🎉 SOPHIA AI PLATFORM DEPLOYMENT COMPLETE! 🎉")
            return True

        except KeyboardInterrupt:
            logger.warning("\n⚠️  Deployment interrupted by user")
            return False
        except Exception as e:
            logger.exception(f"❌ Unexpected error: {e}")
            return False


async def main():
    """Main deployment function"""
    deployer = SophiaPlatformDeployer()
    success = await deployer.deploy()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
