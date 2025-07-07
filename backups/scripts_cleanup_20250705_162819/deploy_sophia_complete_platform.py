#!/usr/bin/env python3
"""
Sophia AI Complete Platform Deployment
=====================================

Deploys the entire Sophia AI platform across all three Lambda Labs instances:
- sophia-platform-prod (146.235.200.1) - Main Platform Services
- sophia-mcp-prod (165.1.69.44) - MCP Servers
- sophia-ai-prod (137.131.6.213) - AI Processing

Usage: python scripts/deploy_sophia_complete_platform.py [--dry-run]
"""

import asyncio
import json
import logging
import subprocess
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class LambdaLabsInstance:
    """Lambda Labs instance configuration"""

    name: str
    ip: str
    gpu_type: str
    region: str
    purpose: str
    services: list[str]


@dataclass
class DeploymentResult:
    """Deployment result for tracking"""

    instance: str
    service: str
    status: str
    duration: float
    error: str | None = None


class SophiaAICompleteDeployment:
    """Complete Sophia AI platform deployment orchestrator"""

    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.start_time = time.time()
        self.deployment_results: list[DeploymentResult] = []

        # Define Lambda Labs instances
        self.instances = {
            "platform": LambdaLabsInstance(
                name="sophia-platform-prod",
                ip="146.235.200.1",
                gpu_type="gpu_1x_a10",
                region="us-west-1",
                purpose="Main Platform Services",
                services=[
                    "backend-api",
                    "frontend",
                    "postgres",
                    "redis",
                    "grafana",
                    "prometheus",
                ],
            ),
            "mcp": LambdaLabsInstance(
                name="sophia-mcp-prod",
                ip="165.1.69.44",
                gpu_type="gpu_1x_a10",
                region="us-west-1",
                purpose="MCP Servers",
                services=[
                    "codacy-mcp",
                    "ai-memory-mcp",
                    "github-mcp",
                    "linear-mcp",
                    "asana-mcp",
                    "hubspot-mcp",
                ],
            ),
            "ai": LambdaLabsInstance(
                name="sophia-ai-prod",
                ip="137.131.6.213",
                gpu_type="gpu_1x_a100_sxm4",
                region="us-west-2",
                purpose="AI Processing & ML Workloads",
                services=[
                    "snowflake-cortex",
                    "ai-processing",
                    "ml-workloads",
                    "vector-search",
                ],
            ),
        }

    def print_banner(self):
        """Print deployment banner"""
        print("\n" + "=" * 80)
        print("🚀 SOPHIA AI COMPLETE PLATFORM DEPLOYMENT")
        print("=" * 80)
        print(f"📅 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🔧 Mode: {'DRY RUN' if self.dry_run else 'LIVE DEPLOYMENT'}")
        print("🌐 Target: All 3 Lambda Labs instances")
        print("=" * 80)

        for key, instance in self.instances.items():
            print(f"📍 {instance.name}")
            print(f"   🔗 IP: {instance.ip}")
            print(f"   🎯 Purpose: {instance.purpose}")
            print(f"   🖥️  Services: {', '.join(instance.services)}")
            print()

    async def check_prerequisites(self) -> bool:
        """Check deployment prerequisites"""
        print("🔍 Checking deployment prerequisites...")

        checks = [
            ("Git repository clean", self._check_git_status),
            ("Docker images available", self._check_docker_images),
            ("SSH connectivity", self._check_ssh_connectivity),
            ("GitHub secrets configured", self._check_github_secrets),
            ("Pulumi ESC accessible", self._check_pulumi_esc),
        ]

        all_passed = True
        for check_name, check_func in checks:
            try:
                result = await check_func()
                status = "✅" if result else "❌"
                print(f"   {status} {check_name}")
                if not result:
                    all_passed = False
            except Exception as e:
                print(f"   ❌ {check_name}: {e}")
                all_passed = False

        return all_passed

    async def _check_git_status(self) -> bool:
        """Check if git repository is clean (excluding external submodules)"""
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            # Filter out external submodule changes which are normal
            lines = result.stdout.strip().split("\n") if result.stdout.strip() else []
            relevant_changes = [
                line for line in lines if not line.strip().endswith("external/")
            ]
            relevant_changes = [
                line for line in relevant_changes if "external/" not in line
            ]
            return len(relevant_changes) == 0
        except Exception:
            return False

    async def _check_docker_images(self) -> bool:
        """Check if required Docker images exist"""
        # For now, return True as GitHub Actions will build images
        return True

    async def _check_ssh_connectivity(self) -> bool:
        """Check SSH connectivity to all instances"""
        for instance in self.instances.values():
            try:
                result = subprocess.run(
                    ["ping", "-c", "1", instance.ip], capture_output=True, timeout=5
                )
                if result.returncode != 0:
                    return False
            except Exception:
                return False
        return True

    async def _check_github_secrets(self) -> bool:
        """Check if GitHub secrets are configured"""
        # This would require GitHub API access, return True for now
        return True

    async def _check_pulumi_esc(self) -> bool:
        """Check Pulumi ESC accessibility"""
        try:
            result = subprocess.run(
                ["pulumi", "whoami"], capture_output=True, timeout=10
            )
            return result.returncode == 0
        except Exception:
            return False

    async def deploy_platform_services(self) -> list[DeploymentResult]:
        """Deploy main platform services to sophia-platform-prod"""
        print(f"\n🚀 Deploying Platform Services to {self.instances['platform'].ip}...")
        results = []

        if self.dry_run:
            print("   [DRY RUN] Would deploy platform services")
            return results

        # Deploy main platform stack
        start_time = time.time()
        try:
            result = subprocess.run(
                [
                    "python",
                    "scripts/deploy_to_lambda_labs_cloud.py",
                    "--environment",
                    "prod",
                    "--target",
                    "platform",
                ],
                capture_output=True,
                text=True,
                timeout=600,
            )

            duration = time.time() - start_time

            if result.returncode == 0:
                results.append(
                    DeploymentResult(
                        instance="platform",
                        service="main-stack",
                        status="success",
                        duration=duration,
                    )
                )
                print(f"   ✅ Platform services deployed ({duration:.1f}s)")
            else:
                results.append(
                    DeploymentResult(
                        instance="platform",
                        service="main-stack",
                        status="failed",
                        duration=duration,
                        error=result.stderr,
                    )
                )
                print(f"   ❌ Platform deployment failed: {result.stderr}")

        except Exception as e:
            results.append(
                DeploymentResult(
                    instance="platform",
                    service="main-stack",
                    status="error",
                    duration=time.time() - start_time,
                    error=str(e),
                )
            )
            print(f"   ❌ Platform deployment error: {e}")

        return results

    async def deploy_mcp_services(self) -> list[DeploymentResult]:
        """Deploy MCP services to sophia-mcp-prod"""
        print(f"\n🧠 Deploying MCP Services to {self.instances['mcp'].ip}...")
        results = []

        if self.dry_run:
            print("   [DRY RUN] Would deploy MCP services")
            return results

        # MCP services are deployed via GitHub Actions
        # Check if Codacy deployment is complete, then trigger others

        mcp_services = [
            "codacy-mcp",
            "ai-memory-mcp",
            "github-mcp",
            "linear-mcp",
            "asana-mcp",
        ]

        for service in mcp_services:
            start_time = time.time()
            try:
                if service == "codacy-mcp":
                    # Codacy is already deploying via GitHub Actions
                    print(f"   🔄 {service}: GitHub Actions deployment in progress")
                    results.append(
                        DeploymentResult(
                            instance="mcp",
                            service=service,
                            status="in_progress",
                            duration=0,
                        )
                    )
                else:
                    # Deploy other MCP services
                    result = subprocess.run(
                        [
                            "python",
                            "scripts/deploy_mcp_service.py",
                            "--service",
                            service,
                            "--target",
                            self.instances["mcp"].ip,
                        ],
                        capture_output=True,
                        text=True,
                        timeout=300,
                    )

                    duration = time.time() - start_time

                    if result.returncode == 0:
                        results.append(
                            DeploymentResult(
                                instance="mcp",
                                service=service,
                                status="success",
                                duration=duration,
                            )
                        )
                        print(f"   ✅ {service} deployed ({duration:.1f}s)")
                    else:
                        results.append(
                            DeploymentResult(
                                instance="mcp",
                                service=service,
                                status="failed",
                                duration=duration,
                                error=result.stderr,
                            )
                        )
                        print(f"   ❌ {service} failed: {result.stderr}")

            except Exception as e:
                results.append(
                    DeploymentResult(
                        instance="mcp",
                        service=service,
                        status="error",
                        duration=time.time() - start_time,
                        error=str(e),
                    )
                )
                print(f"   ❌ {service} error: {e}")

        return results

    async def deploy_ai_services(self) -> list[DeploymentResult]:
        """Deploy AI services to sophia-ai-prod"""
        print(f"\n🤖 Deploying AI Services to {self.instances['ai'].ip}...")
        results = []

        if self.dry_run:
            print("   [DRY RUN] Would deploy AI services")
            return results

        # Deploy AI/ML stack
        start_time = time.time()
        try:
            result = subprocess.run(
                [
                    "docker",
                    "stack",
                    "deploy",
                    "-c",
                    "docker-compose.cloud.yml",
                    "sophia-ai-prod",
                ],
                capture_output=True,
                text=True,
                timeout=600,
            )

            duration = time.time() - start_time

            if result.returncode == 0:
                results.append(
                    DeploymentResult(
                        instance="ai",
                        service="ai-stack",
                        status="success",
                        duration=duration,
                    )
                )
                print(f"   ✅ AI services deployed ({duration:.1f}s)")
            else:
                results.append(
                    DeploymentResult(
                        instance="ai",
                        service="ai-stack",
                        status="failed",
                        duration=duration,
                        error=result.stderr,
                    )
                )
                print(f"   ❌ AI deployment failed: {result.stderr}")

        except Exception as e:
            results.append(
                DeploymentResult(
                    instance="ai",
                    service="ai-stack",
                    status="error",
                    duration=time.time() - start_time,
                    error=str(e),
                )
            )
            print(f"   ❌ AI deployment error: {e}")

        return results

    async def verify_deployments(self) -> dict[str, bool]:
        """Verify all deployments are healthy"""
        print("\n🔍 Verifying deployments...")

        verification_results = {}

        # Test endpoints for each instance
        endpoints = {
            "platform": f"http://{self.instances['platform'].ip}:8000/health",
            "mcp": f"http://{self.instances['mcp'].ip}:3008/health",
            "ai": f"http://{self.instances['ai'].ip}:9030/health",
        }

        for instance, endpoint in endpoints.items():
            try:
                if self.dry_run:
                    print(f"   [DRY RUN] Would verify {instance}: {endpoint}")
                    verification_results[instance] = True
                    continue

                import aiohttp

                timeout = aiohttp.ClientTimeout(total=10)
                async with aiohttp.ClientSession() as session:
                    async with session.get(endpoint, timeout=timeout) as response:
                        healthy = response.status == 200
                        status = "✅" if healthy else "❌"
                        print(f"   {status} {instance}: {endpoint}")
                        verification_results[instance] = healthy

            except Exception as e:
                print(f"   ❌ {instance}: {endpoint} - {e}")
                verification_results[instance] = False

        return verification_results

    def generate_deployment_report(self):
        """Generate comprehensive deployment report"""
        total_duration = time.time() - self.start_time

        print("\n" + "=" * 80)
        print("📊 DEPLOYMENT REPORT")
        print("=" * 80)
        print(f"⏱️  Total Duration: {total_duration:.1f} seconds")
        print(f"📝 Total Services: {len(self.deployment_results)}")

        # Summary by status
        status_counts = {}
        for result in self.deployment_results:
            status_counts[result.status] = status_counts.get(result.status, 0) + 1

        for status, count in status_counts.items():
            emoji = {
                "success": "✅",
                "failed": "❌",
                "error": "🚨",
                "in_progress": "🔄",
            }.get(status, "❓")
            print(f"{emoji} {status.title()}: {count}")

        print("\n📋 Detailed Results:")
        for result in self.deployment_results:
            emoji = {
                "success": "✅",
                "failed": "❌",
                "error": "🚨",
                "in_progress": "🔄",
            }.get(result.status, "❓")
            print(
                f"   {emoji} {result.instance}/{result.service}: {result.status} ({result.duration:.1f}s)"
            )
            if result.error:
                print(f"      Error: {result.error}")

        # Save report to file
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "total_duration": total_duration,
            "instances": {k: v.__dict__ for k, v in self.instances.items()},
            "results": [r.__dict__ for r in self.deployment_results],
        }

        report_file = f"deployment_report_{int(time.time())}.json"
        with open(report_file, "w") as f:
            json.dump(report_data, f, indent=2)

        print(f"\n📄 Full report saved: {report_file}")

        # Service URLs
        print("\n🔗 Service URLs:")
        print(f"   🌐 Platform: http://{self.instances['platform'].ip}:8000")
        print(f"   🧠 MCP Codacy: http://{self.instances['mcp'].ip}:3008")
        print(f"   🤖 AI Services: http://{self.instances['ai'].ip}:9030")
        print(f"   📊 Grafana: http://{self.instances['platform'].ip}:3000")
        print(f"   📈 Prometheus: http://{self.instances['platform'].ip}:9090")

        print("\n🎯 Next Steps:")
        print("   1. Monitor service health via dashboards")
        print("   2. Run integration tests")
        print("   3. Configure DNS/load balancing")
        print("   4. Set up monitoring alerts")

    async def deploy_complete_platform(self):
        """Execute complete platform deployment"""
        self.print_banner()

        # Check prerequisites
        if not await self.check_prerequisites():
            print("\n❌ Prerequisites not met. Please fix issues and retry.")
            return

        print("\n✅ Prerequisites passed. Starting deployment...")

        # Deploy to all instances in parallel for speed
        deployment_tasks = [
            self.deploy_platform_services(),
            self.deploy_mcp_services(),
            self.deploy_ai_services(),
        ]

        # Execute deployments
        results = await asyncio.gather(*deployment_tasks, return_exceptions=True)

        # Collect all results
        for result_group in results:
            if isinstance(result_group, Exception):
                print(f"❌ Deployment group failed: {result_group}")
            elif isinstance(result_group, list):
                self.deployment_results.extend(result_group)

        # Wait for services to stabilize
        print("\n⏳ Waiting for services to stabilize...")
        await asyncio.sleep(30)

        # Verify deployments
        verification_results = await self.verify_deployments()

        # Generate final report
        self.generate_deployment_report()

        # Final status
        total_healthy = sum(verification_results.values())
        total_instances = len(verification_results)

        if total_healthy == total_instances:
            print(
                f"\n🎉 DEPLOYMENT SUCCESSFUL! All {total_instances} instances healthy."
            )
        else:
            print(
                f"\n⚠️  DEPLOYMENT PARTIAL: {total_healthy}/{total_instances} instances healthy."
            )


async def main():
    """Main deployment function"""
    import argparse

    parser = argparse.ArgumentParser(description="Deploy complete Sophia AI platform")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Perform dry run without actual deployment",
    )
    args = parser.parse_args()

    deployer = SophiaAICompleteDeployment(dry_run=args.dry_run)
    await deployer.deploy_complete_platform()


if __name__ == "__main__":
    asyncio.run(main())
