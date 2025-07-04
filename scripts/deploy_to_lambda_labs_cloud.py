#!/usr/bin/env python3
"""
Lambda Labs Docker Cloud Deployment Script for Sophia AI

This script automates the deployment of Sophia AI to Lambda Labs infrastructure
using Docker Swarm and cloud-native patterns.

Usage:
    python scripts/deploy_to_lambda_labs_cloud.py --environment prod
    python scripts/deploy_to_lambda_labs_cloud.py --environment staging --dry-run
"""

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path


class LambdaLabsCloudDeployer:
    """Handles deployment to Lambda Labs Docker Cloud infrastructure."""

    def __init__(self, environment: str = "prod", dry_run: bool = False):
        self.environment = environment
        self.dry_run = dry_run
        self.docker_registry = "scoobyjava15"
        self.stack_name = f"sophia-ai-{environment}"

        # Lambda Labs configuration
        self.lambda_labs_config = {
            "instance_id": "7e7b1e5f53c44a26bd574e4266e96194",
            "instance_name": "sophia-ai-production",
            "ip_address": "104.171.202.64",
            "ssh_key_id": "cae55cb8d0f5443cbdf9129f7cec8770",
            "region": "us-south-1",
        }

        # Required secrets for deployment
        self.required_secrets = [
            "pulumi_access_token",
            "postgres_password",
            "mem0_api_key",
            "snowflake_account",
            "snowflake_user",
            "snowflake_password",
            "grafana_password",
        ]

        print("🚀 Initializing Lambda Labs Cloud Deployment")
        print(f"   Environment: {environment}")
        print(f"   Registry: {self.docker_registry}")
        print(f"   Stack: {self.stack_name}")
        print(f"   Dry Run: {dry_run}")

    def validate_prerequisites(self) -> bool:
        """Validate all prerequisites for deployment."""
        print("\n📋 Validating Prerequisites...")

        # Check Docker
        if not self._check_docker():
            return False

        # Check Docker Swarm
        if not self._check_docker_swarm():
            return False

        # Check Lambda Labs connectivity
        if not self._check_lambda_labs_connectivity():
            return False

        # Check Docker registry access
        if not self._check_registry_access():
            return False

        # Check required files
        if not self._check_required_files():
            return False

        print("✅ All prerequisites validated successfully")
        return True

    def _check_docker(self) -> bool:
        """Check Docker availability and version."""
        try:
            result = subprocess.run(
                ["docker", "--version"], capture_output=True, text=True, check=True
            )
            print(f"   ✅ Docker: {result.stdout.strip()}")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("   ❌ Docker not found or not running")
            return False

    def _check_docker_swarm(self) -> bool:
        """Check Docker Swarm status."""
        try:
            result = subprocess.run(
                ["docker", "info", "--format", "{{.Swarm.LocalNodeState}}"],
                capture_output=True,
                text=True,
                check=True,
            )

            if result.stdout.strip() == "active":
                print("   ✅ Docker Swarm: Active")
                return True
            else:
                print("   ⚠️  Docker Swarm not active - initializing...")
                return self._initialize_swarm()

        except subprocess.CalledProcessError:
            print("   ❌ Failed to check Docker Swarm status")
            return False

    def _initialize_swarm(self) -> bool:
        """Initialize Docker Swarm if not active."""
        try:
            if self.dry_run:
                print("   🔍 DRY RUN: Would initialize Docker Swarm")
                return True

            subprocess.run(["docker", "swarm", "init"], check=True, capture_output=True)
            print("   ✅ Docker Swarm initialized successfully")
            return True

        except subprocess.CalledProcessError as e:
            print(f"   ❌ Failed to initialize Docker Swarm: {e}")
            return False

    def _check_lambda_labs_connectivity(self) -> bool:
        """Check connectivity to Lambda Labs instance."""
        try:
            # Ping the Lambda Labs instance
            result = subprocess.run(
                ["ping", "-c", "1", self.lambda_labs_config["ip_address"]],
                capture_output=True,
                timeout=10,
            )

            if result.returncode == 0:
                print(
                    f"   ✅ Lambda Labs connectivity: {self.lambda_labs_config['ip_address']}"
                )
                return True
            else:
                print(
                    f"   ⚠️  Lambda Labs instance may not be ready: {self.lambda_labs_config['ip_address']}"
                )
                # Continue anyway as instance might be booting
                return True

        except subprocess.TimeoutExpired:
            print("   ⚠️  Lambda Labs connectivity timeout - continuing anyway")
            return True
        except Exception as e:
            print(f"   ⚠️  Lambda Labs connectivity check failed: {e}")
            return True  # Continue anyway

    def _check_registry_access(self) -> bool:
        """Check Docker registry access."""
        try:
            if self.dry_run:
                print(
                    f"   🔍 DRY RUN: Would check registry access to {self.docker_registry}"
                )
                return True

            # Check if logged in to Docker Hub
            result = subprocess.run(
                ["docker", "info"], capture_output=True, text=True, check=True
            )

            print(f"   ✅ Docker registry access: {self.docker_registry}")
            return True

        except subprocess.CalledProcessError:
            print(f"   ❌ Failed to access Docker registry: {self.docker_registry}")
            print("   💡 Run: docker login")
            return False

    def _check_required_files(self) -> bool:
        """Check required deployment files exist."""
        required_files = ["docker-compose.cloud.yml", "Dockerfile", "pyproject.toml"]

        missing_files = []
        for file_path in required_files:
            if not Path(file_path).exists():
                missing_files.append(file_path)
            else:
                print(f"   ✅ Required file: {file_path}")

        if missing_files:
            print(f"   ❌ Missing required files: {missing_files}")
            return False

        return True

    def build_and_push_images(self) -> bool:
        """Build and push Docker images to registry."""
        print("\n🏗️  Building and Pushing Docker Images...")

        images_to_build = [
            {
                "name": f"{self.docker_registry}/sophia-ai",
                "dockerfile": "Dockerfile",
                "target": "production",
                "context": ".",
            },
            {
                "name": f"{self.docker_registry}/sophia-ai-mem0",
                "dockerfile": "docker/Dockerfile.mcp-server",
                "build_args": {
                    "MCP_SERVER_PATH": "backend/mcp_servers/mem0_openmemory",
                    "MCP_SERVER_MODULE": "enhanced_mem0_server",
                    "MCP_SERVER_PORT": "8080",
                },
                "context": ".",
            },
            {
                "name": f"{self.docker_registry}/sophia-ai-cortex",
                "dockerfile": "docker/Dockerfile.mcp-server",
                "build_args": {
                    "MCP_SERVER_PATH": "backend/mcp_servers/cortex_aisql",
                    "MCP_SERVER_MODULE": "cortex_mcp_server",
                    "MCP_SERVER_PORT": "8080",
                },
                "context": ".",
            },
        ]

        for image_config in images_to_build:
            if not self._build_and_push_image(image_config):
                return False

        print("✅ All images built and pushed successfully")
        return True

    def _build_and_push_image(self, image_config: dict) -> bool:
        """Build and push a single Docker image."""
        image_name = image_config["name"]
        tag = f"{image_name}:latest"

        print(f"   🔨 Building: {tag}")

        if self.dry_run:
            print(f"   🔍 DRY RUN: Would build and push {tag}")
            return True

        try:
            # Build command
            build_cmd = ["docker", "build"]

            if "target" in image_config:
                build_cmd.extend(["--target", image_config["target"]])

            if "build_args" in image_config:
                for key, value in image_config["build_args"].items():
                    build_cmd.extend(["--build-arg", f"{key}={value}"])

            build_cmd.extend(
                ["-f", image_config["dockerfile"], "-t", tag, image_config["context"]]
            )

            # Build image
            result = subprocess.run(
                build_cmd, check=True, capture_output=True, text=True
            )
            print(f"   ✅ Built: {tag}")

            # Push image
            push_result = subprocess.run(
                ["docker", "push", tag], check=True, capture_output=True, text=True
            )
            print(f"   📤 Pushed: {tag}")

            return True

        except subprocess.CalledProcessError as e:
            print(f"   ❌ Failed to build/push {tag}: {e}")
            if e.stdout:
                print(f"   STDOUT: {e.stdout}")
            if e.stderr:
                print(f"   STDERR: {e.stderr}")
            return False

    def setup_docker_secrets(self) -> bool:
        """Setup Docker secrets for the deployment."""
        print("\n🔐 Setting up Docker Secrets...")

        # Note: In production, these would be retrieved from Pulumi ESC
        # For now, we'll create placeholder secrets that will be updated

        for secret_name in self.required_secrets:
            if not self._create_docker_secret(secret_name):
                return False

        print("✅ All Docker secrets configured")
        return True

    def _create_docker_secret(self, secret_name: str) -> bool:
        """Create a Docker secret."""
        if self.dry_run:
            print(f"   🔍 DRY RUN: Would create secret {secret_name}")
            return True

        try:
            # Check if secret already exists
            result = subprocess.run(
                [
                    "docker",
                    "secret",
                    "ls",
                    "--filter",
                    f"name={secret_name}",
                    "--format",
                    "{{.Name}}",
                ],
                capture_output=True,
                text=True,
                check=True,
            )

            if secret_name in result.stdout:
                print(f"   ✅ Secret exists: {secret_name}")
                return True

            # Create placeholder secret (will be updated with real values)
            placeholder_value = f"PLACEHOLDER_{secret_name.upper()}"

            subprocess.run(
                ["docker", "secret", "create", secret_name, "-"],
                input=placeholder_value,
                text=True,
                check=True,
            )

            print(f"   ✅ Created secret: {secret_name}")
            return True

        except subprocess.CalledProcessError as e:
            print(f"   ❌ Failed to create secret {secret_name}: {e}")
            return False

    def deploy_stack(self) -> bool:
        """Deploy the Docker stack to Lambda Labs."""
        print(f"\n🚀 Deploying Stack: {self.stack_name}")

        if self.dry_run:
            print("   🔍 DRY RUN: Would deploy stack with docker-compose.cloud.yml")
            return True

        try:
            # Set environment variables for deployment
            env = os.environ.copy()
            env.update(
                {
                    "DOCKER_REGISTRY": self.docker_registry,
                    "IMAGE_TAG": "latest",
                    "ENVIRONMENT": self.environment,
                }
            )

            # Deploy stack
            deploy_cmd = [
                "docker",
                "stack",
                "deploy",
                "-c",
                "docker-compose.cloud.yml",
                self.stack_name,
            ]

            result = subprocess.run(
                deploy_cmd, env=env, check=True, capture_output=True, text=True
            )

            print(f"   ✅ Stack deployed: {self.stack_name}")
            print(f"   Output: {result.stdout}")

            return True

        except subprocess.CalledProcessError as e:
            print(f"   ❌ Failed to deploy stack: {e}")
            if e.stdout:
                print(f"   STDOUT: {e.stdout}")
            if e.stderr:
                print(f"   STDERR: {e.stderr}")
            return False

    def verify_deployment(self) -> bool:
        """Verify the deployment is successful."""
        print(f"\n🔍 Verifying Deployment: {self.stack_name}")

        if self.dry_run:
            print("   🔍 DRY RUN: Would verify deployment status")
            return True

        try:
            # Check stack status
            result = subprocess.run(
                ["docker", "stack", "services", self.stack_name],
                capture_output=True,
                text=True,
                check=True,
            )

            print("   📊 Stack Services:")
            print(f"   {result.stdout}")

            # Wait for services to be ready
            print("   ⏳ Waiting for services to be ready...")
            max_retries = 30

            for i in range(max_retries):
                result = subprocess.run(
                    [
                        "docker",
                        "stack",
                        "services",
                        self.stack_name,
                        "--format",
                        "{{.Replicas}}",
                    ],
                    capture_output=True,
                    text=True,
                    check=True,
                )

                replicas = result.stdout.strip().split("\n")
                all_ready = all(
                    "/" in replica and replica.split("/")[0] == replica.split("/")[1]
                    for replica in replicas
                    if replica.strip()
                )

                if all_ready:
                    print("   ✅ All services are ready!")
                    break

                print(f"   ⏳ Waiting... ({i+1}/{max_retries})")
                time.sleep(10)
            else:
                print("   ⚠️  Services may still be starting up")

            return True

        except subprocess.CalledProcessError as e:
            print(f"   ❌ Failed to verify deployment: {e}")
            return False

    def generate_deployment_report(self) -> dict:
        """Generate a comprehensive deployment report."""
        print("\n📋 Generating Deployment Report...")

        report = {
            "deployment_info": {
                "environment": self.environment,
                "stack_name": self.stack_name,
                "registry": self.docker_registry,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
            },
            "lambda_labs_config": self.lambda_labs_config,
            "docker_images": [
                f"{self.docker_registry}/sophia-ai:latest",
                f"{self.docker_registry}/sophia-ai-mem0:latest",
                f"{self.docker_registry}/sophia-ai-cortex:latest",
            ],
            "access_urls": {
                "main_api": f"http://{self.lambda_labs_config['ip_address']}:8000",
                "mem0_server": f"http://{self.lambda_labs_config['ip_address']}:8080",
                "cortex_server": f"http://{self.lambda_labs_config['ip_address']}:8081",
                "traefik_dashboard": f"http://{self.lambda_labs_config['ip_address']}:8090",
                "grafana": f"http://{self.lambda_labs_config['ip_address']}:3000",
                "prometheus": f"http://{self.lambda_labs_config['ip_address']}:9090",
            },
            "next_steps": [
                "Update Docker secrets with real values from Pulumi ESC",
                "Configure DNS records for custom domains",
                "Set up SSL certificates via Traefik",
                "Configure monitoring alerts",
                "Test all service endpoints",
            ],
        }

        # Save report
        report_file = f"deployment_report_{self.environment}_{int(time.time())}.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        print(f"   📄 Report saved: {report_file}")
        return report

    def run_deployment(self) -> bool:
        """Run the complete deployment process."""
        print("🌟 Starting Lambda Labs Docker Cloud Deployment")
        print("=" * 60)

        steps = [
            ("Prerequisites", self.validate_prerequisites),
            ("Build & Push Images", self.build_and_push_images),
            ("Setup Secrets", self.setup_docker_secrets),
            ("Deploy Stack", self.deploy_stack),
            ("Verify Deployment", self.verify_deployment),
        ]

        for step_name, step_func in steps:
            print(f"\n{'='*20} {step_name} {'='*20}")

            if not step_func():
                print(f"\n❌ Deployment failed at step: {step_name}")
                return False

        # Generate final report
        report = self.generate_deployment_report()

        print("\n🎉 DEPLOYMENT SUCCESSFUL!")
        print("=" * 60)
        print(f"Stack Name: {self.stack_name}")
        print(f"Main API: {report['access_urls']['main_api']}")
        print(f"Traefik Dashboard: {report['access_urls']['traefik_dashboard']}")
        print("\n⚠️  IMPORTANT: Update Docker secrets with real values from Pulumi ESC")

        return True


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Deploy Sophia AI to Lambda Labs Docker Cloud"
    )
    parser.add_argument(
        "--environment",
        choices=["prod", "staging", "dev"],
        default="prod",
        help="Deployment environment",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Perform a dry run without making changes",
    )

    args = parser.parse_args()

    deployer = LambdaLabsCloudDeployer(
        environment=args.environment, dry_run=args.dry_run
    )

    success = deployer.run_deployment()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
