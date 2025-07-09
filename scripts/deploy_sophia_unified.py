#!/usr/bin/env python3
"""
Unified Deployment Script for Sophia AI
Single source of truth for all deployment operations
"""

import argparse
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# ANSI color codes
RED = "\033[0;31m"
GREEN = "\033[0;32m"
YELLOW = "\033[1;33m"
BLUE = "\033[0;34m"
NC = "\033[0m"  # No Color


class UnifiedDeployer:
    """Unified deployment orchestrator for Sophia AI"""

    def __init__(self, environment: str = "production"):
        self.environment = environment
        self.docker_registry = os.getenv("DOCKER_REGISTRY", "scoobyjava15")
        self.lambda_labs_host = os.getenv("LAMBDA_LABS_HOST", "192.222.58.232")
        self.stack_name = "sophia-ai"
        self.compose_file = "docker-compose.unified.yml"

    def log(self, message: str, color: str = NC):
        """Log message with color"""
        print(f"{color}{message}{NC}")

    def run_command(
        self, cmd: list[str], check: bool = True
    ) -> subprocess.CompletedProcess:
        """Run a command and return result"""
        self.log(f"Running: {' '.join(cmd)}", BLUE)
        return subprocess.run(cmd, check=check, capture_output=True, text=True)

    def check_prerequisites(self) -> bool:
        """Check if all prerequisites are met"""
        self.log("🔍 Checking prerequisites...", BLUE)

        # Check Docker
        try:
            result = self.run_command(["docker", "--version"], check=False)
            if result.returncode != 0:
                self.log("❌ Docker is not installed", RED)
                return False
            self.log("✅ Docker is installed", GREEN)
        except FileNotFoundError:
            self.log("❌ Docker is not installed", RED)
            return False

        # Check Docker Compose
        try:
            result = self.run_command(["docker", "compose", "version"], check=False)
            if result.returncode != 0:
                # Try old docker-compose
                result = self.run_command(["docker-compose", "--version"], check=False)
                if result.returncode != 0:
                    self.log("❌ Docker Compose is not installed", RED)
                    return False
            self.log("✅ Docker Compose is installed", GREEN)
        except FileNotFoundError:
            self.log("❌ Docker Compose is not installed", RED)
            return False

        # Check if compose file exists
        if not Path(self.compose_file).exists():
            self.log(f"❌ Compose file not found: {self.compose_file}", RED)
            return False
        self.log(f"✅ Compose file found: {self.compose_file}", GREEN)

        return True

    def detect_mcp_servers(self) -> list[str]:
        """Detect available MCP servers"""
        mcp_dir = Path("infrastructure/mcp_servers")
        if not mcp_dir.exists():
            return []

        servers = []
        for server_dir in mcp_dir.iterdir():
            if server_dir.is_dir() and server_dir.name.endswith("_v2"):
                servers.append(server_dir.name)

        self.log(f"Found {len(servers)} MCP servers: {', '.join(servers)}", BLUE)
        return servers

    def build_images(self, backend: bool = True, mcp_servers: bool = True) -> bool:
        """Build Docker images"""
        self.log("🏗️  Building Docker images...", BLUE)

        images_built = []

        # Build backend
        if backend:
            self.log("Building backend image...", YELLOW)
            try:
                self.run_command(
                    [
                        "docker",
                        "build",
                        "-t",
                        f"{self.docker_registry}/sophia-ai:latest",
                        "-t",
                        f"{self.docker_registry}/sophia-ai:{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        "-f",
                        "Dockerfile.production",
                        ".",
                    ]
                )
                images_built.append("backend")
                self.log("✅ Backend image built", GREEN)
            except subprocess.CalledProcessError as e:
                self.log(f"❌ Failed to build backend: {e}", RED)
                return False

        # Build MCP servers
        if mcp_servers:
            servers = self.detect_mcp_servers()
            for server in servers:
                self.log(f"Building {server}...", YELLOW)
                try:
                    self.run_command(
                        [
                            "docker",
                            "build",
                            "-t",
                            f"{self.docker_registry}/sophia-{server}:latest",
                            "-f",
                            f"infrastructure/mcp_servers/{server}/Dockerfile",
                            f"infrastructure/mcp_servers/{server}",
                        ]
                    )
                    images_built.append(server)
                    self.log(f"✅ {server} built", GREEN)
                except subprocess.CalledProcessError as e:
                    self.log(f"⚠️  Failed to build {server}: {e}", YELLOW)
                    # Continue with other servers

        self.log(f"Built {len(images_built)} images", GREEN)
        return len(images_built) > 0

    def push_images(self, images: list[str]) -> bool:
        """Push images to registry"""
        self.log("📤 Pushing images to registry...", BLUE)

        # Login to Docker Hub
        self.log("Logging in to Docker Hub...", YELLOW)
        try:
            # Use token from environment or prompt
            token = os.getenv("DOCKER_HUB_TOKEN")
            if token:
                process = subprocess.Popen(
                    ["docker", "login", "-u", self.docker_registry, "--password-stdin"],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )
                stdout, stderr = process.communicate(input=token)
                if process.returncode != 0:
                    self.log(f"❌ Docker login failed: {stderr}", RED)
                    return False
            else:
                self.log(
                    "⚠️  DOCKER_HUB_TOKEN not set, assuming already logged in", YELLOW
                )
        except Exception as e:
            self.log(f"❌ Docker login failed: {e}", RED)
            return False

        # Push images
        pushed = 0
        for image in images:
            if image == "backend":
                tag = f"{self.docker_registry}/sophia-ai:latest"
            else:
                tag = f"{self.docker_registry}/sophia-{image}:latest"

            self.log(f"Pushing {tag}...", YELLOW)
            try:
                self.run_command(["docker", "push", tag])
                pushed += 1
                self.log(f"✅ Pushed {tag}", GREEN)
            except subprocess.CalledProcessError as e:
                self.log(f"❌ Failed to push {tag}: {e}", RED)

        self.log(
            f"Pushed {pushed}/{len(images)} images",
            GREEN if pushed == len(images) else YELLOW,
        )
        return pushed > 0

    def deploy_local(self) -> bool:
        """Deploy locally using Docker Compose"""
        self.log("🚀 Deploying locally...", BLUE)

        # Create .env file
        env_content = f"""# Auto-generated deployment environment
ENVIRONMENT={self.environment}
DOCKER_REGISTRY={self.docker_registry}
IMAGE_TAG=latest
BACKEND_REPLICAS=1
GATEWAY_REPLICAS=1
AI_MEMORY_REPLICAS=1
"""

        with open(".env", "w") as f:
            f.write(env_content)

        # Deploy using docker compose
        try:
            self.run_command(["docker", "compose", "-f", self.compose_file, "up", "-d"])
            self.log("✅ Local deployment started", GREEN)
            return True
        except subprocess.CalledProcessError as e:
            self.log(f"❌ Local deployment failed: {e}", RED)
            return False

    def deploy_swarm(self, host: Optional[str] = None) -> bool:
        """Deploy to Docker Swarm on Lambda Labs"""
        host = host or self.lambda_labs_host
        self.log(f"🚀 Deploying to Swarm on {host}...", BLUE)

        # Check SSH key
        ssh_key = os.path.expanduser("~/.ssh/sophia2025.pem")
        if not Path(ssh_key).exists():
            ssh_key = os.path.expanduser("~/.ssh/sophia2025.pem")
            if not Path(ssh_key).exists():
                self.log("❌ SSH key not found", RED)
                return False

        # Create deployment package
        self.log("Creating deployment package...", YELLOW)
        deploy_dir = Path("deployment_package")
        deploy_dir.mkdir(exist_ok=True)

        # Copy files
        subprocess.run(["cp", self.compose_file, str(deploy_dir)], check=False)

        # Create environment file
        env_content = f"""ENVIRONMENT={self.environment}
DOCKER_REGISTRY={self.docker_registry}
IMAGE_TAG=latest
BACKEND_REPLICAS=3
GATEWAY_REPLICAS=3
AI_MEMORY_REPLICAS=2
"""
        (deploy_dir / ".env").write_text(env_content)

        # Create deployment script
        deploy_script = """#!/bin/bash
set -euo pipefail

echo "🚀 Deploying Sophia AI Stack"
source .env

# Deploy stack
docker stack deploy -c docker-compose.unified.yml sophia-ai --with-registry-auth

# Wait and check
sleep 30
docker stack services sophia-ai
"""
        (deploy_dir / "deploy.sh").write_text(deploy_script)
        (deploy_dir / "deploy.sh").chmod(0o755)

        # Copy to remote
        self.log(f"Copying to {host}...", YELLOW)
        try:
            self.run_command(
                [
                    "scp",
                    "-i",
                    ssh_key,
                    "-r",
                    str(deploy_dir) + "/*",
                    f"ubuntu@{host}:~/",
                ]
            )
        except subprocess.CalledProcessError as e:
            self.log(f"❌ Failed to copy files: {e}", RED)
            return False

        # Execute deployment
        self.log("Executing deployment...", YELLOW)
        try:
            self.run_command(["ssh", "-i", ssh_key, f"ubuntu@{host}", "bash deploy.sh"])
            self.log("✅ Swarm deployment completed", GREEN)
            return True
        except subprocess.CalledProcessError as e:
            self.log(f"❌ Swarm deployment failed: {e}", RED)
            return False

    def validate_deployment(self, host: Optional[str] = None) -> bool:
        """Validate deployment health"""
        host = host or "localhost"
        self.log(f"🔍 Validating deployment on {host}...", BLUE)

        services = [
            ("Backend API", f"http://{host}:8000/api/health"),
            ("MCP Gateway", f"http://{host}:8080/health"),
        ]

        healthy = 0
        for name, url in services:
            try:
                result = self.run_command(["curl", "-s", "-f", url], check=False)
                if result.returncode == 0:
                    self.log(f"✅ {name} is healthy", GREEN)
                    healthy += 1
                else:
                    self.log(f"❌ {name} is not responding", RED)
            except Exception as e:
                self.log(f"❌ {name} check failed: {e}", RED)

        self.log(
            f"Health check: {healthy}/{len(services)} services healthy",
            GREEN if healthy == len(services) else YELLOW,
        )
        return healthy == len(services)


def main():
    parser = argparse.ArgumentParser(description="Unified Sophia AI Deployment")
    parser.add_argument(
        "--environment",
        default="production",
        choices=["production", "staging", "development"],
        help="Deployment environment",
    )
    parser.add_argument("--build", action="store_true", help="Build images")
    parser.add_argument("--push", action="store_true", help="Push images to registry")
    parser.add_argument("--deploy", choices=["local", "swarm"], help="Deploy mode")
    parser.add_argument("--host", help="Remote host for swarm deployment")
    parser.add_argument("--validate", action="store_true", help="Validate deployment")
    parser.add_argument("--no-backend", action="store_true", help="Skip backend build")
    parser.add_argument("--no-mcp", action="store_true", help="Skip MCP server builds")

    args = parser.parse_args()

    deployer = UnifiedDeployer(args.environment)

    # Check prerequisites
    if not deployer.check_prerequisites():
        sys.exit(1)

    # Build images if requested
    images_built = []
    if args.build:
        if deployer.build_images(
            backend=not args.no_backend, mcp_servers=not args.no_mcp
        ):
            # Track what was built
            if not args.no_backend:
                images_built.append("backend")
            if not args.no_mcp:
                images_built.extend(deployer.detect_mcp_servers())

    # Push images if requested
    if args.push and images_built:
        if not deployer.push_images(images_built):
            deployer.log("⚠️  Some images failed to push", YELLOW)

    # Deploy if requested
    if args.deploy:
        if args.deploy == "local":
            if not deployer.deploy_local():
                sys.exit(1)
        elif args.deploy == "swarm":
            if not deployer.deploy_swarm(args.host):
                sys.exit(1)

    # Validate if requested
    if args.validate:
        host = args.host if args.deploy == "swarm" else "localhost"
        if not deployer.validate_deployment(host):
            sys.exit(1)

    deployer.log("✅ Deployment workflow completed!", GREEN)


if __name__ == "__main__":
    main()
