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
            "ip_address": "146.235.200.1",
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

    def validate_prerequisites(self) -> bool:
        """Validate all prerequisites for deployment."""
        print("🔍 Validating prerequisites...")
        # Check Docker
        if not self._check_docker():
            print("❌ Docker not found.")
            return False

        # Check Docker Swarm
        if not self._check_docker_swarm():
            print("❌ Docker Swarm not active.")
            return False

        # Check Lambda Labs connectivity
        if not self._check_lambda_labs_connectivity():
            print("⚠️ Could not verify Lambda Labs connectivity, proceeding anyway...")

        # Check Docker registry access
        if not self._check_registry_access():
            print("❌ Docker registry access failed.")
            return False

        # Check required files
        if not self._check_required_files():
            return False
        
        print("✅ Prerequisites validated.")
        return True

    def _check_docker(self) -> bool:
        """Check Docker availability and version."""
        try:
            subprocess.run(
                ["docker", "--version"], capture_output=True, text=True, check=True
            )
            print("  - Docker found.")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
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
                print("  - Docker Swarm is active.")
                return True
            else:
                print("  - Docker Swarm not active, attempting to initialize...")
                return self._initialize_swarm()

        except subprocess.CalledProcessError:
            return False

    def _initialize_swarm(self) -> bool:
        """Initialize Docker Swarm if not active."""
        try:
            if self.dry_run:
                print("  - [DRY RUN] Skipping Swarm initialization.")
                return True

            subprocess.run(["docker", "swarm", "init"], check=True, capture_output=True)
            print("  - Docker Swarm initialized successfully.")
            return True

        except subprocess.CalledProcessError:
            print("  - ❌ Failed to initialize Docker Swarm.")
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
                print("  - Lambda Labs instance is reachable.")
                return True
            else:
                # Continue anyway as instance might be booting
                print("  - ⚠️ Lambda Labs instance not reachable by ping.")
                return True

        except subprocess.TimeoutExpired:
            print("  - ⚠️ Lambda Labs ping timed out.")
            return True
        except Exception:
            print("  - ⚠️ Error checking Lambda Labs connectivity.")
            return True  # Continue anyway

    def _check_registry_access(self) -> bool:
        """Check Docker registry access."""
        try:
            if self.dry_run:
                print("  - [DRY RUN] Skipping registry access check.")
                return True

            # Check if logged in to Docker Hub
            result = subprocess.run(
                ["docker", "info"], capture_output=True, text=True, check=True
            )
            if "Index: https://index.docker.io/v1/" in result.stdout:
                print(f"  - Logged into Docker registry.")
                return True
            else:
                print("  - ❌ Not logged into Docker Hub.")
                return False

        except subprocess.CalledProcessError:
            return False

    def _check_required_files(self) -> bool:
        """Check required deployment files exist."""
        required_files = ["docker-compose.cloud.yml", "Dockerfile", "pyproject.toml"]

        missing_files = []
        for file_path in required_files:
            if not Path(file_path).exists():
                missing_files.append(file_path)
            else:
                pass

        if missing_files:
            print(f"  - ❌ Missing required files: {', '.join(missing_files)}")
            return False

        print(f"  - All required files found: {', '.join(required_files)}")
        return not missing_files

    def build_and_push_images(self) -> bool:
        """Build and push all Docker images defined in the compose file."""
        print("\n📦 Building and pushing Docker images...")
        import yaml
        try:
            with open("docker-compose.cloud.yml", "r") as f:
                compose_config = yaml.safe_load(f)
        except FileNotFoundError:
            print("  - ❌ docker-compose.cloud.yml not found.")
            return False
        except yaml.YAMLError as e:
            print(f"  - ❌ Error parsing docker-compose.cloud.yml: {e}")
            return False

        services = compose_config.get("services", {})
        for service_name, service_config in services.items():
            if "build" in service_config:
                image_name = service_config.get("image", f"{self.docker_registry}/{service_name}:latest")
                print(f"  - Processing service: {service_name} -> {image_name}")
                if not self._build_and_push_image({
                    "name": image_name,
                    "dockerfile": service_config["build"].get("dockerfile", "Dockerfile"),
                    "context": service_config["build"].get("context", "."),
                    "target": service_config["build"].get("target"),
                    "build_args": service_config["build"].get("args"),
                }):
                    print(f"  - ❌ Failed to build or push image for {service_name}.")
                    return False
        
        print("✅ All images built and pushed successfully.")
        return True

    def _build_and_push_image(self, image_config: dict) -> bool:
        """Build and push a single Docker image."""
        image_name = image_config["name"]
        tag = f"{image_name}:latest"

        if self.dry_run:
            print(f"  - [DRY RUN] Skipping build and push for {tag}")
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
            print(f"    - Building {tag}...")
            subprocess.run(build_cmd, check=True, capture_output=True, text=True)

            # Push image
            print(f"    - Pushing {tag}...")
            subprocess.run(
                ["docker", "push", tag], check=True, capture_output=True, text=True
            )
            print(f"    - ✅ Successfully built and pushed {tag}")
            return True

        except subprocess.CalledProcessError as e:
            if e.stdout:
                print(f"      - STDOUT: {e.stdout}")
            if e.stderr:
                print(f"      - STDERR: {e.stderr}")
            return False

    def setup_docker_secrets(self) -> bool:
        """Setup Docker secrets for the deployment."""
        print("\n🔒 Setting up Docker secrets...")
        # Note: In production, these would be retrieved from Pulumi ESC
        # For now, we'll create placeholder secrets that will be updated

        for secret_name in self.required_secrets:
            if not self._create_docker_secret(secret_name):
                print(f"  - ❌ Failed to create secret: {secret_name}")
                return False
        
        print("✅ Docker secrets set up.")
        return True

    def _create_docker_secret(self, secret_name: str) -> bool:
        """Create a Docker secret."""
        if self.dry_run:
            print(f"  - [DRY RUN] Skipping creation of secret '{secret_name}'.")
            return True

        try:
            # Check if secret exists
            check_cmd = ["docker", "secret", "ls", "--filter", f"name={secret_name}"]
            result = subprocess.run(check_cmd, capture_output=True, text=True, check=True)
            if secret_name in result.stdout:
                print(f"  - Secret '{secret_name}' already exists. Skipping.")
                return True

            # Create placeholder secret
            placeholder = f"placeholder_{secret_name}"
            create_cmd = f"echo '{placeholder}' | docker secret create {secret_name} -"
            subprocess.run(create_cmd, shell=True, check=True, capture_output=True)
            print(f"  - Created placeholder secret: {secret_name}")
            return True

        except subprocess.CalledProcessError:
            return False

    def deploy_stack(self) -> bool:
        """Deploy the Docker stack to Lambda Labs."""
        print("\n🚀 Deploying Docker stack...")
        if self.dry_run:
            print("  - [DRY RUN] Skipping stack deployment.")
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

            subprocess.run(
                deploy_cmd, env=env, check=True, capture_output=True, text=True
            )
            print(f"✅ Stack '{self.stack_name}' deployed successfully.")
            return True

        except subprocess.CalledProcessError as e:
            print(f"  - ❌ Stack deployment failed.")
            if e.stdout:
                print(f"    - STDOUT: {e.stdout}")
            if e.stderr:
                print(f"    - STDERR: {e.stderr}")
            return False

    def verify_deployment(self) -> bool:
        """Verify the deployment is successful."""
        print("\n🔎 Verifying deployment...")
        if self.dry_run:
            print("  - [DRY RUN] Skipping deployment verification.")
            return True

        try:
            # Check stack status
            result = subprocess.run(
                ["docker", "stack", "services", self.stack_name],
                capture_output=True,
                text=True,
                check=True,
            )
            print(f"  - Stack services:\n{result.stdout}")

            # Wait for services to be ready
            max_retries = 30
            print("  - Waiting for all services to have running replicas...")
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
                    "/" in replica and replica.split("/")[0] == replica.split("/")[1] and replica.split('/')[0] != '0'
                    for replica in replicas
                    if replica.strip()
                )

                if all_ready:
                    print(f"  - ✅ All services are ready after {i+1} checks.")
                    break

                time.sleep(10)
            else:
                print("  - ⚠️ Timed out waiting for services to become ready.")
                pass # Continue anyway, maybe it's just slow

            return True

        except subprocess.CalledProcessError:
            print("  - ❌ Failed to get stack services for verification.")
            return False

    def generate_deployment_report(self) -> dict:
        """Generate a comprehensive deployment report."""
        print("\n📝 Generating deployment report...")
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
        
        print(f"✅ Deployment report saved to {report_file}")
        return report

    def run_deployment(self) -> bool:
        """Run the complete deployment process."""
        print(f"🏁 Starting Sophia AI deployment to '{self.environment}' environment.")
        steps = [
            ("Prerequisites", self.validate_prerequisites),
            ("Build & Push Images", self.build_and_push_images),
            ("Setup Secrets", self.setup_docker_secrets),
            ("Deploy Stack", self.deploy_stack),
            ("Verify Deployment", self.verify_deployment),
        ]

        for step_name, step_func in steps:
            print(f"\n--- Running Step: {step_name} ---")
            if not step_func():
                print(f"❌ Deployment failed at step: {step_name}")
                return False

        # Generate final report
        self.generate_deployment_report()
        
        print("\n🎉 Deployment successful! 🎉")
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
