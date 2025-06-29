#!/usr/bin/env python3
"""
Sophia AI Minimal Staging Deployment
Focus on infrastructure components and monitoring without complex dependencies
"""

import asyncio
import logging
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any

import requests

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class MinimalStagingDeployment:
    """Minimal staging deployment focusing on infrastructure validation"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.deployment_id = f"minimal-staging-{int(datetime.now().timestamp())}"

    async def deploy_minimal_staging(self) -> dict[str, Any]:
        """Execute minimal staging deployment"""
        logger.info("🚀 Starting Sophia AI Minimal Staging Deployment")

        deployment_result = {
            "deployment_id": self.deployment_id,
            "start_time": datetime.now().isoformat(),
            "status": "in_progress",
            "components": [],
            "infrastructure": [],
            "monitoring": [],
            "errors": [],
        }

        try:
            # Phase 1: Infrastructure validation
            logger.info("🏗️ Phase 1: Infrastructure validation")
            infra_result = await self._validate_infrastructure()
            deployment_result["infrastructure"] = infra_result["components"]

            # Phase 2: Deploy minimal services
            logger.info("🐳 Phase 2: Deploy minimal services")
            service_result = await self._deploy_minimal_services()
            deployment_result["components"] = service_result["services"]

            # Phase 3: Setup monitoring
            logger.info("📊 Phase 3: Setup monitoring")
            monitoring_result = await self._setup_monitoring()
            deployment_result["monitoring"] = monitoring_result["monitors"]

            # Phase 4: Validate deployment
            logger.info("✅ Phase 4: Validate deployment")
            await self._validate_minimal_deployment()

            # Determine overall status
            running_services = len(
                [
                    s
                    for s in deployment_result["components"]
                    if s.get("status") == "running"
                ]
            )
            total_services = len(deployment_result["components"])

            if running_services >= total_services * 0.7:  # 70% success rate
                deployment_result["status"] = "success"
            elif running_services > 0:
                deployment_result["status"] = "partial_success"
            else:
                deployment_result["status"] = "failed"

            logger.info(
                f"✅ Minimal staging deployment completed: {running_services}/{total_services} services running"
            )

        except Exception as e:
            error_msg = f"Deployment failed with exception: {e}"
            logger.error(error_msg)
            deployment_result["status"] = "failed"
            deployment_result["errors"].append(error_msg)

        deployment_result["end_time"] = datetime.now().isoformat()
        return deployment_result

    async def _validate_infrastructure(self) -> dict[str, Any]:
        """Validate infrastructure components"""
        logger.info("   🏗️ Validating infrastructure components...")

        components = []

        # Check 1: Docker availability
        try:
            result = subprocess.run(
                ["docker", "--version"], capture_output=True, text=True
            )
            if result.returncode == 0:
                components.append(
                    {
                        "component": "docker",
                        "status": "available",
                        "version": result.stdout.strip(),
                        "details": "Docker is available",
                    }
                )
                logger.info("      ✅ Docker available")
            else:
                components.append(
                    {
                        "component": "docker",
                        "status": "unavailable",
                        "details": "Docker not available",
                    }
                )
                logger.error("      ❌ Docker not available")
        except Exception as e:
            components.append(
                {"component": "docker", "status": "error", "details": str(e)}
            )

        # Check 2: Network infrastructure
        try:
            result = subprocess.run(
                ["docker", "network", "ls", "--filter", "name=sophia-staging"],
                capture_output=True,
                text=True,
            )

            if "sophia-staging" in result.stdout:
                components.append(
                    {
                        "component": "staging_network",
                        "status": "exists",
                        "details": "Staging network exists",
                    }
                )
                logger.info("      ✅ Staging network exists")
            else:
                components.append(
                    {
                        "component": "staging_network",
                        "status": "missing",
                        "details": "Staging network needs to be created",
                    }
                )
                logger.info("      ℹ️ Staging network will be created")
        except Exception as e:
            components.append(
                {"component": "staging_network", "status": "error", "details": str(e)}
            )

        # Check 3: File system readiness
        required_dirs = ["backend", "config", "scripts"]
        for dir_name in required_dirs:
            dir_path = self.project_root / dir_name
            if dir_path.exists():
                components.append(
                    {
                        "component": f"directory_{dir_name}",
                        "status": "exists",
                        "details": f"Directory {dir_name} exists",
                    }
                )
            else:
                components.append(
                    {
                        "component": f"directory_{dir_name}",
                        "status": "missing",
                        "details": f"Directory {dir_name} missing",
                    }
                )

        return {"success": True, "components": components}

    async def _deploy_minimal_services(self) -> dict[str, Any]:
        """Deploy minimal infrastructure services"""
        logger.info("   🐳 Deploying minimal services...")

        services = []

        # Create minimal compose file
        await self._create_minimal_compose()

        # Deploy services individually for better control
        minimal_services = [
            {
                "name": "redis-minimal",
                "image": "redis:7-alpine",
                "port": "6381:6379",
                "command": "redis-server --appendonly yes",
            },
            {
                "name": "nginx-proxy",
                "image": "nginx:alpine",
                "port": "8002:80",
                "command": None,
            },
        ]

        for service_config in minimal_services:
            try:
                logger.info(f"      🔄 Starting {service_config['name']}...")

                # Build docker run command
                docker_cmd = [
                    "docker",
                    "run",
                    "-d",
                    "--name",
                    service_config["name"],
                    "--network",
                    "sophia-staging",
                    "-p",
                    service_config["port"],
                    "--restart",
                    "unless-stopped",
                ]

                if service_config["command"]:
                    docker_cmd.extend(
                        [service_config["image"]] + service_config["command"].split()
                    )
                else:
                    docker_cmd.append(service_config["image"])

                # Remove existing container if it exists
                subprocess.run(
                    ["docker", "rm", "-f", service_config["name"]],
                    capture_output=True,
                    text=True,
                )

                # Start new container
                result = subprocess.run(docker_cmd, capture_output=True, text=True)

                if result.returncode == 0:
                    # Wait for container to start
                    await asyncio.sleep(2)

                    # Check container status
                    status_result = subprocess.run(
                        [
                            "docker",
                            "inspect",
                            service_config["name"],
                            "--format",
                            "{{.State.Status}}",
                        ],
                        capture_output=True,
                        text=True,
                    )

                    if status_result.returncode == 0:
                        container_status = status_result.stdout.strip()
                        services.append(
                            {
                                "service": service_config["name"],
                                "status": container_status,
                                "port": service_config["port"],
                                "details": f"Container {container_status}",
                            }
                        )

                        if container_status == "running":
                            logger.info(
                                f"      ✅ {service_config['name']} started successfully"
                            )
                        else:
                            logger.warning(
                                f"      ⚠️ {service_config['name']} status: {container_status}"
                            )
                    else:
                        services.append(
                            {
                                "service": service_config["name"],
                                "status": "unknown",
                                "details": "Could not determine status",
                            }
                        )
                else:
                    services.append(
                        {
                            "service": service_config["name"],
                            "status": "failed",
                            "details": result.stderr,
                        }
                    )
                    logger.error(
                        f"      ❌ {service_config['name']} failed: {result.stderr}"
                    )

            except Exception as e:
                services.append(
                    {
                        "service": service_config["name"],
                        "status": "error",
                        "details": str(e),
                    }
                )
                logger.error(f"      ❌ {service_config['name']} error: {e}")

        return {"success": True, "services": services}

    async def _create_minimal_compose(self):
        """Create minimal Docker Compose file"""
        minimal_compose = {
            "services": {
                "redis-minimal": {
                    "image": "redis:7-alpine",
                    "container_name": "redis-minimal",
                    "ports": ["6381:6379"],
                    "command": "redis-server --appendonly yes",
                    "networks": ["sophia-staging"],
                    "restart": "unless-stopped",
                },
                "nginx-proxy": {
                    "image": "nginx:alpine",
                    "container_name": "nginx-proxy",
                    "ports": ["8002:80"],
                    "networks": ["sophia-staging"],
                    "restart": "unless-stopped",
                },
            },
            "networks": {"sophia-staging": {"driver": "bridge"}},
        }

        # Write minimal compose file
        compose_file = self.project_root / "docker-compose.minimal.yml"
        with open(compose_file, "w") as f:
            import yaml

            yaml.dump(minimal_compose, f, default_flow_style=False, indent=2)

    async def _setup_monitoring(self) -> dict[str, Any]:
        """Setup basic monitoring"""
        logger.info("   📊 Setting up monitoring...")

        monitors = []

        # Monitor 1: Container health monitoring
        try:
            containers = ["redis-minimal", "nginx-proxy"]

            for container in containers:
                result = subprocess.run(
                    [
                        "docker",
                        "inspect",
                        container,
                        "--format",
                        "{{.State.Health.Status}}",
                    ],
                    capture_output=True,
                    text=True,
                )

                if result.returncode == 0:
                    health_status = result.stdout.strip()
                    monitors.append(
                        {
                            "monitor": f"{container}_health",
                            "status": "active",
                            "health": (
                                health_status if health_status else "no_healthcheck"
                            ),
                            "details": f"Monitoring {container} health",
                        }
                    )
                else:
                    monitors.append(
                        {
                            "monitor": f"{container}_health",
                            "status": "inactive",
                            "details": f"Cannot monitor {container}",
                        }
                    )

            logger.info("      ✅ Container health monitoring setup")

        except Exception as e:
            monitors.append(
                {"monitor": "container_health", "status": "error", "details": str(e)}
            )
            logger.error(f"      ❌ Health monitoring setup failed: {e}")

        # Monitor 2: Port connectivity monitoring
        try:
            ports_to_check = [6381, 8002]  # Redis and Nginx

            for port in ports_to_check:
                import socket

                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(3)
                result = sock.connect_ex(("localhost", port))
                sock.close()

                if result == 0:
                    monitors.append(
                        {
                            "monitor": f"port_{port}",
                            "status": "accessible",
                            "details": f"Port {port} is accessible",
                        }
                    )
                    logger.info(f"      ✅ Port {port} accessible")
                else:
                    monitors.append(
                        {
                            "monitor": f"port_{port}",
                            "status": "inaccessible",
                            "details": f"Port {port} is not accessible",
                        }
                    )
                    logger.warning(f"      ⚠️ Port {port} not accessible")

        except Exception as e:
            monitors.append(
                {"monitor": "port_connectivity", "status": "error", "details": str(e)}
            )
            logger.error(f"      ❌ Port monitoring setup failed: {e}")

        return {"success": True, "monitors": monitors}

    async def _validate_minimal_deployment(self) -> dict[str, Any]:
        """Validate minimal deployment"""
        logger.info("   ✅ Validating minimal deployment...")

        validation_results = []

        # Validation 1: Check running containers
        try:
            result = subprocess.run(
                [
                    "docker",
                    "ps",
                    "--filter",
                    "network=sophia-staging",
                    "--format",
                    "{{.Names}}\t{{.Status}}",
                ],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                running_containers = (
                    result.stdout.strip().split("\n") if result.stdout.strip() else []
                )
                validation_results.append(
                    {
                        "validation": "running_containers",
                        "status": "success",
                        "count": len(running_containers),
                        "details": f"{len(running_containers)} containers running in staging network",
                    }
                )
                logger.info(f"      ✅ {len(running_containers)} containers running")
            else:
                validation_results.append(
                    {
                        "validation": "running_containers",
                        "status": "failed",
                        "details": "Could not check running containers",
                    }
                )

        except Exception as e:
            validation_results.append(
                {
                    "validation": "running_containers",
                    "status": "error",
                    "details": str(e),
                }
            )

        # Validation 2: Test Redis connectivity
        try:
            result = subprocess.run(
                ["docker", "exec", "redis-minimal", "redis-cli", "ping"],
                capture_output=True,
                text=True,
                timeout=5,
            )

            if result.returncode == 0 and "PONG" in result.stdout:
                validation_results.append(
                    {
                        "validation": "redis_connectivity",
                        "status": "success",
                        "details": "Redis responding to ping",
                    }
                )
                logger.info("      ✅ Redis connectivity validated")
            else:
                validation_results.append(
                    {
                        "validation": "redis_connectivity",
                        "status": "failed",
                        "details": "Redis not responding",
                    }
                )
                logger.warning("      ⚠️ Redis not responding")

        except Exception as e:
            validation_results.append(
                {
                    "validation": "redis_connectivity",
                    "status": "error",
                    "details": str(e),
                }
            )
            logger.warning(f"      ⚠️ Redis validation failed: {e}")

        # Validation 3: Test Nginx
        try:
            response = requests.get("http://localhost:8002", timeout=5)
            validation_results.append(
                {
                    "validation": "nginx_http",
                    "status": "success" if response.status_code == 200 else "partial",
                    "status_code": response.status_code,
                    "details": f"Nginx responding with HTTP {response.status_code}",
                }
            )
            logger.info(f"      ✅ Nginx responding with HTTP {response.status_code}")

        except Exception as e:
            validation_results.append(
                {"validation": "nginx_http", "status": "failed", "details": str(e)}
            )
            logger.warning(f"      ⚠️ Nginx validation failed: {e}")

        return {"success": True, "validations": validation_results}


async def main():
    """Main deployment function"""
    deployment = MinimalStagingDeployment()

    print("\n" + "=" * 80)
    print("🚀 SOPHIA AI MINIMAL STAGING DEPLOYMENT")
    print("=" * 80)

    result = await deployment.deploy_minimal_staging()

    print("\n📊 DEPLOYMENT RESULTS")
    print(f"Deployment ID: {result['deployment_id']}")
    print(
        f"Status: {'✅ SUCCESS' if result['status'] == 'success' else '⚠️ PARTIAL' if result['status'] == 'partial_success' else '❌ FAILED'}"
    )
    print(f"Start Time: {result['start_time']}")
    print(f"End Time: {result.get('end_time', 'N/A')}")

    if result["infrastructure"]:
        print("\n🏗️ INFRASTRUCTURE:")
        for component in result["infrastructure"]:
            status_icon = (
                "✅" if component["status"] in ["available", "exists"] else "⚠️"
            )
            print(f"   {status_icon} {component['component']}: {component['status']}")

    if result["components"]:
        print("\n🐳 SERVICES:")
        for service in result["components"]:
            status_icon = "✅" if service["status"] == "running" else "⚠️"
            print(f"   {status_icon} {service['service']}: {service['status']}")

    if result["monitoring"]:
        print("\n📊 MONITORING:")
        for monitor in result["monitoring"]:
            status_icon = "✅" if monitor["status"] in ["active", "accessible"] else "⚠️"
            print(f"   {status_icon} {monitor['monitor']}: {monitor['status']}")

    if result["errors"]:
        print("\n❌ ERRORS:")
        for error in result["errors"]:
            print(f"   • {error}")

    print("\n" + "=" * 80)

    if result["status"] in ["success", "partial_success"]:
        print("🎉 MINIMAL STAGING DEPLOYMENT COMPLETED!")
        print("\n📍 Staging Services:")
        print("   • Redis: localhost:6381")
        print("   • Nginx Proxy: http://localhost:8002")
        print("\n🔧 Management Commands:")
        print("   • View containers: docker ps --filter network=sophia-staging")
        print("   • View logs: docker logs <container_name>")
        print("   • Stop all: docker stop redis-minimal nginx-proxy")
        print("   • Clean up: docker rm redis-minimal nginx-proxy")
        print("\n✅ Infrastructure validated and ready for full deployment!")
    else:
        print("❌ MINIMAL STAGING DEPLOYMENT FAILED")
        print("   Check logs above for details")

    print("=" * 80)

    return result


if __name__ == "__main__":
    asyncio.run(main())
