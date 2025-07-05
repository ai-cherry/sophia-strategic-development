#!/usr/bin/env python3
"""
Deployment Status Checker for Sophia AI

Monitors the deployment status by checking:
- Docker Hub image registry
- GitHub Actions workflow status
- Lambda Labs connectivity
- Expected deployment indicators
"""

import asyncio
import json
import subprocess
import time
from datetime import datetime
from typing import Any

import aiohttp


class DeploymentStatusChecker:
    """Check comprehensive deployment status"""

    def __init__(self):
        self.lambda_labs_ip = "165.1.69.44"
        self.docker_hub_user = "scoobyjava15"
        self.expected_services = {
            "Codacy MCP": 3008,
            "Main API": 8000,
            "MCP Gateway": 8080,
            "AI Memory": 9001,
            "Grafana": 3000,
            "Prometheus": 9090,
        }

    async def check_docker_hub_images(self) -> dict[str, Any]:
        """Check if Docker images are available on Docker Hub"""
        print("🐳 Checking Docker Hub images...")

        # Expected image names based on docker-compose.cloud.yml
        expected_images = [
            "sophia-ai-codacy-mcp",
            "sophia-ai-memory",
            "sophia-snowflake-admin",
            "sophia-codacy",
            "sophia-linear",
            "sophia-github",
            "sophia-asana",
            "sophia-notion",
        ]

        image_status = {}

        for image_name in expected_images:
            try:
                # Check Docker Hub API for image existence
                url = f"https://hub.docker.com/v2/repositories/{self.docker_hub_user}/{image_name}/tags/"

                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        url, timeout=aiohttp.ClientTimeout(total=10)
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            tags = [tag["name"] for tag in data.get("results", [])]
                            latest_tag = tags[0] if tags else None
                            image_status[image_name] = {
                                "exists": True,
                                "latest_tag": latest_tag,
                                "total_tags": len(tags),
                                "status": "✅ Available",
                            }
                            print(
                                f"   ✅ {image_name} - Latest: {latest_tag}, Total tags: {len(tags)}"
                            )
                        else:
                            image_status[image_name] = {
                                "exists": False,
                                "status": f"❌ Not found (HTTP {response.status})",
                            }
                            print(f"   ❌ {image_name} - Not found")
            except Exception as e:
                image_status[image_name] = {
                    "exists": False,
                    "error": str(e),
                    "status": f"❌ Error: {str(e)[:30]}",
                }
                print(f"   ❌ {image_name} - Error: {str(e)[:50]}")

        return image_status

    def check_recent_commits(self) -> dict[str, Any]:
        """Check recent Git commits for deployment-related changes"""
        print("\n📝 Checking recent commits...")

        try:
            # Get last 5 commits
            result = subprocess.run(
                ["git", "log", "--oneline", "-5"],
                capture_output=True,
                text=True,
                check=True,
            )

            commits = result.stdout.strip().split("\n")
            recent_commits = []

            for commit_line in commits:
                if commit_line.strip():
                    commit_hash = commit_line.split()[0]
                    commit_msg = " ".join(commit_line.split()[1:])

                    # Get commit timestamp
                    timestamp_result = subprocess.run(
                        ["git", "show", "-s", "--format=%ct", commit_hash],
                        capture_output=True,
                        text=True,
                        check=True,
                    )

                    timestamp = int(timestamp_result.stdout.strip())
                    commit_date = datetime.fromtimestamp(timestamp)

                    recent_commits.append(
                        {
                            "hash": commit_hash,
                            "message": commit_msg,
                            "timestamp": commit_date.isoformat(),
                            "age_minutes": (
                                datetime.now() - commit_date
                            ).total_seconds()
                            / 60,
                        }
                    )

                    print(
                        f"   📌 {commit_hash}: {commit_msg} ({commit_date.strftime('%H:%M:%S')})"
                    )

            return {
                "commits": recent_commits,
                "latest_commit_age_minutes": recent_commits[0]["age_minutes"]
                if recent_commits
                else 0,
            }

        except subprocess.CalledProcessError as e:
            print(f"   ❌ Error getting commits: {e}")
            return {"error": str(e)}

    async def quick_connectivity_test(self) -> dict[str, Any]:
        """Quick connectivity test to key services"""
        print("\n🔗 Quick connectivity test...")

        results = {}

        for service_name, port in self.expected_services.items():
            try:
                start_time = time.time()
                timeout = aiohttp.ClientTimeout(
                    total=3.0
                )  # Shorter timeout for quick test

                async with aiohttp.ClientSession(timeout=timeout) as session:
                    url = f"http://{self.lambda_labs_ip}:{port}/health"
                    async with session.get(url) as response:
                        response_time = (time.time() - start_time) * 1000

                        if response.status == 200:
                            results[service_name] = {
                                "status": "✅ Healthy",
                                "response_time": response_time,
                                "port": port,
                            }
                            print(
                                f"   ✅ {service_name} ({port}) - {response_time:.1f}ms"
                            )
                        else:
                            results[service_name] = {
                                "status": f"⚠️ HTTP {response.status}",
                                "response_time": response_time,
                                "port": port,
                            }
                            print(
                                f"   ⚠️ {service_name} ({port}) - HTTP {response.status}"
                            )

            except asyncio.TimeoutError:
                results[service_name] = {"status": "❌ Timeout", "port": port}
                print(f"   ❌ {service_name} ({port}) - Timeout")
            except Exception as e:
                results[service_name] = {"status": f"❌ {str(e)[:30]}", "port": port}
                print(f"   ❌ {service_name} ({port}) - {str(e)[:30]}")

        return results

    def analyze_deployment_status(
        self, docker_status: dict, git_status: dict, connectivity_status: dict
    ) -> dict:
        """Analyze overall deployment status"""
        print("\n📊 Deployment Status Analysis")
        print("=" * 60)

        # Calculate metrics
        total_images = len(docker_status)
        available_images = len(
            [img for img in docker_status.values() if img.get("exists", False)]
        )

        total_services = len(connectivity_status)
        healthy_services = len(
            [
                svc
                for svc in connectivity_status.values()
                if "✅" in svc.get("status", "")
            ]
        )

        latest_commit_age = git_status.get("latest_commit_age_minutes", 999)

        # Determine deployment phase
        if available_images == 0:
            phase = "Not Started"
            phase_emoji = "⏳"
        elif available_images < total_images:
            phase = "Building Images"
            phase_emoji = "🔨"
        elif healthy_services == 0 and latest_commit_age < 30:
            phase = "Deploying Services"
            phase_emoji = "🚀"
        elif healthy_services > 0 and healthy_services < total_services:
            phase = "Partial Deployment"
            phase_emoji = "⚠️"
        elif healthy_services == total_services:
            phase = "Fully Deployed"
            phase_emoji = "✅"
        else:
            phase = "Unknown"
            phase_emoji = "❓"

        analysis = {
            "phase": phase,
            "phase_emoji": phase_emoji,
            "metrics": {
                "images_available": f"{available_images}/{total_images}",
                "services_healthy": f"{healthy_services}/{total_services}",
                "latest_commit_age_minutes": latest_commit_age,
            },
            "recommendations": [],
        }

        print(f"🎯 Current Phase: {phase_emoji} {phase}")
        print(f"📦 Docker Images: {available_images}/{total_images} available")
        print(f"🏥 Healthy Services: {healthy_services}/{total_services}")
        print(f"⏰ Latest Commit: {latest_commit_age:.1f} minutes ago")

        # Generate recommendations
        if phase == "Not Started":
            analysis["recommendations"].append(
                "Check if GitHub Actions workflow is triggered"
            )
            analysis["recommendations"].append(
                "Verify Docker Hub credentials in GitHub secrets"
            )
        elif phase == "Building Images":
            analysis["recommendations"].append(
                "Wait for Docker image builds to complete"
            )
            analysis["recommendations"].append("Check GitHub Actions workflow logs")
        elif phase == "Deploying Services":
            analysis["recommendations"].append(
                "Wait for services to start (usually 2-5 minutes)"
            )
            analysis["recommendations"].append(
                "Monitor connectivity for service health"
            )
        elif phase == "Partial Deployment":
            analysis["recommendations"].append("Check logs for failed services")
            analysis["recommendations"].append(
                "Verify all required secrets are available"
            )
        elif phase == "Fully Deployed":
            analysis["recommendations"].append("Run comprehensive health checks")
            analysis["recommendations"].append("Test all API endpoints")

        if analysis["recommendations"]:
            print("\n💡 Recommendations:")
            for i, rec in enumerate(analysis["recommendations"], 1):
                print(f"   {i}. {rec}")

        return analysis

    async def run_comprehensive_check(self):
        """Run comprehensive deployment status check"""
        print("🔍 Sophia AI Deployment Status Checker")
        print(f"⏰ Check started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)

        # Run all checks
        docker_status = await self.check_docker_hub_images()
        git_status = self.check_recent_commits()
        connectivity_status = await self.quick_connectivity_test()

        # Analyze results
        analysis = self.analyze_deployment_status(
            docker_status, git_status, connectivity_status
        )

        # Save detailed report
        report = {
            "timestamp": datetime.now().isoformat(),
            "lambda_labs_ip": self.lambda_labs_ip,
            "docker_status": docker_status,
            "git_status": git_status,
            "connectivity_status": connectivity_status,
            "analysis": analysis,
        }

        report_file = f"deployment_status_report_{int(time.time())}.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        print(f"\n📄 Detailed report saved to: {report_file}")

        # Final status
        print(f"\n🎯 FINAL STATUS: {analysis['phase_emoji']} {analysis['phase']}")

        if analysis["phase"] in ["Fully Deployed", "Partial Deployment"]:
            print("\n🌐 Access URLs:")
            for service_name, status in connectivity_status.items():
                if "✅" in status.get("status", ""):
                    port = status["port"]
                    print(f"   {service_name}: http://{self.lambda_labs_ip}:{port}")

        return analysis


async def main():
    """Main function"""
    checker = DeploymentStatusChecker()
    analysis = await checker.run_comprehensive_check()

    # If deployment is in progress, offer to monitor
    if analysis["phase"] in ["Building Images", "Deploying Services"]:
        print("\n⏳ Deployment appears to be in progress...")
        print("💡 You can run this script again in a few minutes to check progress.")
        print("💡 Or use the monitoring script once services are healthy.")


if __name__ == "__main__":
    asyncio.run(main())
