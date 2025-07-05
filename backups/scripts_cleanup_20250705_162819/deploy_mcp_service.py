#!/usr/bin/env python3
"""
MCP Service Deployment Script
============================

Deploys individual MCP services to specified Lambda Labs instances.
Used by the complete platform deployment orchestrator.

Usage: python scripts/deploy_mcp_service.py --service <service> --target <ip>
"""

import argparse
import asyncio
import json
import os
import subprocess
import time
from datetime import datetime
from typing import Any

import aiohttp


class MCPServiceDeployer:
    """Deploy individual MCP services"""

    def __init__(self, service: str, target_ip: str, dry_run: bool = False):
        self.service = service
        self.target_ip = target_ip
        self.dry_run = dry_run
        self.start_time = time.time()

        # MCP service configurations
        self.service_configs = {
            "codacy-mcp": {
                "port": 3008,
                "dockerfile": "mcp-servers/codacy/Dockerfile",
                "image": "scoobyjava15/sophia-codacy-mcp",
                "health_endpoint": "/health",
            },
            "ai-memory-mcp": {
                "port": 9001,
                "dockerfile": "mcp-servers/ai_memory/Dockerfile",
                "image": "scoobyjava15/sophia-ai-memory-mcp",
                "health_endpoint": "/health",
            },
            "github-mcp": {
                "port": 9003,
                "dockerfile": "mcp-servers/github/Dockerfile",
                "image": "scoobyjava15/sophia-github-mcp",
                "health_endpoint": "/health",
            },
            "linear-mcp": {
                "port": 9004,
                "dockerfile": "mcp-servers/linear/Dockerfile",
                "image": "scoobyjava15/sophia-linear-mcp",
                "health_endpoint": "/health",
            },
            "asana-mcp": {
                "port": 9100,
                "dockerfile": "mcp-servers/asana/Dockerfile",
                "image": "scoobyjava15/sophia-asana-mcp",
                "health_endpoint": "/health",
            },
            "hubspot-mcp": {
                "port": 9200,
                "dockerfile": "mcp-servers/hubspot_unified/Dockerfile",
                "image": "scoobyjava15/sophia-hubspot-mcp",
                "health_endpoint": "/health",
            },
        }

    def print_deployment_header(self):
        """Print deployment header"""
        print(f"\n{'='*60}")
        print(f"🚀 MCP SERVICE DEPLOYMENT: {self.service.upper()}")
        print(f"{'='*60}")
        print(f"📅 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🎯 Target: {self.target_ip}")
        print(f"🔧 Mode: {'DRY RUN' if self.dry_run else 'LIVE DEPLOYMENT'}")

        if self.service in self.service_configs:
            config = self.service_configs[self.service]
            print(f"🔗 Port: {config['port']}")
            print(f"🐳 Image: {config['image']}")
        print(f"{'='*60}")

    def validate_service(self) -> bool:
        """Validate that the service is supported"""
        if self.service not in self.service_configs:
            available = ", ".join(self.service_configs.keys())
            print(f"❌ Error: Service '{self.service}' not supported")
            print(f"   Available services: {available}")
            return False
        return True

    def build_docker_image(self) -> bool:
        """Build Docker image for the service"""
        if not self.validate_service():
            return False

        config = self.service_configs[self.service]
        dockerfile_path = config["dockerfile"]
        image_name = config["image"]

        print("\n🔨 Building Docker image...")
        print(f"   📄 Dockerfile: {dockerfile_path}")
        print(f"   🏷️  Image: {image_name}")

        if self.dry_run:
            print("   [DRY RUN] Would build Docker image")
            return True

        # Check if Dockerfile exists
        if not os.path.exists(dockerfile_path):
            print(f"   ❌ Dockerfile not found: {dockerfile_path}")
            return False

        try:
            # Build the image
            result = subprocess.run(
                ["docker", "build", "-f", dockerfile_path, "-t", image_name, "."],
                capture_output=True,
                text=True,
                timeout=600,
            )

            if result.returncode == 0:
                print("   ✅ Image built successfully")
                return True
            else:
                print(f"   ❌ Build failed: {result.stderr}")
                return False

        except Exception as e:
            print(f"   ❌ Build error: {e}")
            return False

    def push_docker_image(self) -> bool:
        """Push Docker image to registry"""
        config = self.service_configs[self.service]
        image_name = config["image"]

        print("\n📤 Pushing Docker image to registry...")
        print(f"   🏷️  Image: {image_name}")

        if self.dry_run:
            print("   [DRY RUN] Would push Docker image")
            return True

        try:
            # Push the image
            result = subprocess.run(
                ["docker", "push", image_name],
                capture_output=True,
                text=True,
                timeout=300,
            )

            if result.returncode == 0:
                print("   ✅ Image pushed successfully")
                return True
            else:
                print(f"   ❌ Push failed: {result.stderr}")
                return False

        except Exception as e:
            print(f"   ❌ Push error: {e}")
            return False

    def deploy_to_lambda_labs(self) -> bool:
        """Deploy service to Lambda Labs instance"""
        config = self.service_configs[self.service]
        image_name = config["image"]
        port = config["port"]

        print("\n🚀 Deploying to Lambda Labs instance...")
        print(f"   🌐 Target: {self.target_ip}")
        print(f"   🔗 Port: {port}")

        if self.dry_run:
            print("   [DRY RUN] Would deploy to Lambda Labs")
            return True

        try:
            # Deploy via SSH
            deploy_command = f"""
                docker pull {image_name} && \
                docker stop {self.service} 2>/dev/null || true && \
                docker rm {self.service} 2>/dev/null || true && \
                docker run -d \
                  --name {self.service} \
                  --restart unless-stopped \
                  -p {port}:{port} \
                  --env-file /opt/sophia-ai/.env \
                  {image_name}
            """

            result = subprocess.run(
                [
                    "ssh",
                    "-o",
                    "StrictHostKeyChecking=no",
                    f"ubuntu@{self.target_ip}",
                    deploy_command,
                ],
                capture_output=True,
                text=True,
                timeout=300,
            )

            if result.returncode == 0:
                print("   ✅ Service deployed successfully")
                return True
            else:
                print(f"   ❌ Deployment failed: {result.stderr}")
                return False

        except Exception as e:
            print(f"   ❌ Deployment error: {e}")
            return False

    async def verify_deployment(self) -> bool:
        """Verify that the deployed service is healthy"""
        config = self.service_configs[self.service]
        port = config["port"]
        health_endpoint = config["health_endpoint"]

        url = f"http://{self.target_ip}:{port}{health_endpoint}"

        print("\n🔍 Verifying deployment...")
        print(f"   🌐 Health URL: {url}")

        if self.dry_run:
            print("   [DRY RUN] Would verify deployment")
            return True

        # Wait for service to start
        max_attempts = 12  # 2 minutes with 10-second intervals
        for attempt in range(max_attempts):
            try:
                timeout = aiohttp.ClientTimeout(total=5)
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, timeout=timeout) as response:
                        if response.status == 200:
                            print(f"   ✅ Service is healthy (HTTP {response.status})")
                            return True
                        else:
                            print(f"   ⚠️  HTTP {response.status} - retrying...")

            except Exception:
                print(
                    f"   ⏳ Attempt {attempt + 1}/{max_attempts} - waiting for service..."
                )

            if attempt < max_attempts - 1:
                await asyncio.sleep(10)

        print(f"   ❌ Service failed to respond after {max_attempts} attempts")
        return False

    async def deploy_service(self) -> dict[str, Any]:
        """Execute complete service deployment"""
        self.print_deployment_header()

        deployment_result = {
            "service": self.service,
            "target_ip": self.target_ip,
            "start_time": self.start_time,
            "steps": {},
            "success": False,
            "duration": 0,
            "error": None,
        }

        try:
            # Step 1: Build Docker image
            print("\n" + "=" * 40)
            print("STEP 1: BUILD DOCKER IMAGE")
            print("=" * 40)

            step_start = time.time()
            if self.build_docker_image():
                deployment_result["steps"]["build"] = {
                    "success": True,
                    "duration": time.time() - step_start,
                }
            else:
                deployment_result["steps"]["build"] = {
                    "success": False,
                    "duration": time.time() - step_start,
                    "error": "Failed to build Docker image",
                }
                deployment_result["error"] = "Build failed"
                return deployment_result

            # Step 2: Push Docker image
            print("\n" + "=" * 40)
            print("STEP 2: PUSH DOCKER IMAGE")
            print("=" * 40)

            step_start = time.time()
            if self.push_docker_image():
                deployment_result["steps"]["push"] = {
                    "success": True,
                    "duration": time.time() - step_start,
                }
            else:
                deployment_result["steps"]["push"] = {
                    "success": False,
                    "duration": time.time() - step_start,
                    "error": "Failed to push Docker image",
                }
                deployment_result["error"] = "Push failed"
                return deployment_result

            # Step 3: Deploy to Lambda Labs
            print("\n" + "=" * 40)
            print("STEP 3: DEPLOY TO LAMBDA LABS")
            print("=" * 40)

            step_start = time.time()
            if self.deploy_to_lambda_labs():
                deployment_result["steps"]["deploy"] = {
                    "success": True,
                    "duration": time.time() - step_start,
                }
            else:
                deployment_result["steps"]["deploy"] = {
                    "success": False,
                    "duration": time.time() - step_start,
                    "error": "Failed to deploy to Lambda Labs",
                }
                deployment_result["error"] = "Deployment failed"
                return deployment_result

            # Step 4: Verify deployment
            print("\n" + "=" * 40)
            print("STEP 4: VERIFY DEPLOYMENT")
            print("=" * 40)

            step_start = time.time()
            if await self.verify_deployment():
                deployment_result["steps"]["verify"] = {
                    "success": True,
                    "duration": time.time() - step_start,
                }
                deployment_result["success"] = True
            else:
                deployment_result["steps"]["verify"] = {
                    "success": False,
                    "duration": time.time() - step_start,
                    "error": "Failed to verify deployment",
                }
                deployment_result["error"] = "Verification failed"
                return deployment_result

        except Exception as e:
            deployment_result["error"] = str(e)
            print(f"\n❌ Deployment error: {e}")

        finally:
            deployment_result["duration"] = time.time() - self.start_time

            # Print summary
            self.print_deployment_summary(deployment_result)

        return deployment_result

    def print_deployment_summary(self, result: dict[str, Any]):
        """Print deployment summary"""
        print(f"\n{'='*60}")
        print("📊 DEPLOYMENT SUMMARY")
        print(f"{'='*60}")

        status_emoji = "✅" if result["success"] else "❌"
        status_text = "SUCCESS" if result["success"] else "FAILED"

        print(f"{status_emoji} Status: {status_text}")
        print(f"⏱️  Duration: {result['duration']:.1f} seconds")
        print(f"🎯 Service: {result['service']}")
        print(f"🌐 Target: {result['target_ip']}")

        if result["error"]:
            print(f"❌ Error: {result['error']}")

        print("\n📋 Step Results:")
        for step, details in result["steps"].items():
            emoji = "✅" if details["success"] else "❌"
            print(f"   {emoji} {step.title()}: {details['duration']:.1f}s")
            if not details["success"] and "error" in details:
                print(f"      Error: {details['error']}")

        if result["success"]:
            config = self.service_configs[self.service]
            url = f"http://{self.target_ip}:{config['port']}{config['health_endpoint']}"
            print(f"\n🔗 Service URL: {url}")


async def main():
    """Main deployment function"""
    parser = argparse.ArgumentParser(description="Deploy MCP service to Lambda Labs")
    parser.add_argument("--service", required=True, help="MCP service to deploy")
    parser.add_argument("--target", required=True, help="Target Lambda Labs IP address")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Perform dry run without actual deployment",
    )

    args = parser.parse_args()

    deployer = MCPServiceDeployer(
        service=args.service, target_ip=args.target, dry_run=args.dry_run
    )

    result = await deployer.deploy_service()

    # Save result to file
    report_file = f"mcp_deployment_{args.service}_{int(time.time())}.json"
    with open(report_file, "w") as f:
        json.dump(result, f, indent=2)

    print(f"\n📄 Deployment report saved: {report_file}")

    # Exit with appropriate code
    exit(0 if result["success"] else 1)


if __name__ == "__main__":
    asyncio.run(main())
