#!/usr/bin/env python3
"""
Docker Deployment Validation for Sophia AI Platform
Validates Docker Compose deployment and service health
"""

import asyncio
import argparse
import json
import logging
import sys
import time
import requests
import docker
from datetime import datetime, timezone
from typing import Dict, Any

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class DockerServiceValidator:
    """Validates Docker services and containers"""

    def __init__(self):
        try:
            self.client = docker.from_env()
        except Exception as e:
            logger.error(f"Failed to connect to Docker: {e}")
            self.client = None

    def get_service_status(self, service_name: str) -> Dict[str, Any]:
        """Get status of a specific Docker service"""
        if not self.client:
            return {"status": "error", "error": "Docker client not available"}

        try:
            # Find container by service name
            containers = self.client.containers.list(all=True)
            service_containers = [c for c in containers if service_name in c.name]

            if not service_containers:
                return {
                    "status": "not_found",
                    "error": f"No containers found for service {service_name}",
                }

            container = service_containers[0]  # Get first matching container

            status = {
                "status": container.status,
                "name": container.name,
                "image": container.image.tags[0] if container.image.tags else "unknown",
                "created": container.attrs.get("Created", "unknown"),
                "started_at": container.attrs.get("State", {}).get(
                    "StartedAt", "unknown"
                ),
                "ports": container.attrs.get("NetworkSettings", {}).get("Ports", {}),
                "health": "unknown",
            }

            # Check health status if available
            health_status = container.attrs.get("State", {}).get("Health", {})
            if health_status:
                status["health"] = health_status.get("Status", "unknown")

            return status

        except Exception as e:
            return {"status": "error", "error": str(e)}

    def validate_network_connectivity(self) -> Dict[str, Any]:
        """Validate Docker network connectivity"""
        if not self.client:
            return {"status": "error", "error": "Docker client not available"}

        try:
            networks = self.client.networks.list()
            sophia_networks = [n for n in networks if "sophia" in n.name.lower()]

            network_info = {}
            for network in sophia_networks:
                network_info[network.name] = {
                    "id": network.id,
                    "driver": network.attrs.get("Driver", "unknown"),
                    "containers": len(network.attrs.get("Containers", {})),
                    "scope": network.attrs.get("Scope", "unknown"),
                }

            return {
                "status": "healthy" if sophia_networks else "warning",
                "networks": network_info,
                "total_networks": len(networks),
            }

        except Exception as e:
            return {"status": "error", "error": str(e)}


class HealthEndpointValidator:
    """Validates service health endpoints"""

    def __init__(self, timeout: int = 10):
        self.timeout = timeout

    async def check_endpoint(
        self, url: str, expected_status: int = 200
    ) -> Dict[str, Any]:
        """Check if a health endpoint is responding"""
        try:
            start_time = time.perf_counter()

            response = requests.get(url, timeout=self.timeout)

            end_time = time.perf_counter()
            response_time = (end_time - start_time) * 1000  # Convert to ms

            return {
                "status": (
                    "healthy"
                    if response.status_code == expected_status
                    else "unhealthy"
                ),
                "status_code": response.status_code,
                "response_time": round(response_time, 2),
                "content_length": len(response.content),
                "headers": dict(response.headers),
            }

        except requests.exceptions.Timeout:
            return {
                "status": "timeout",
                "error": f"Request timed out after {self.timeout}s",
            }
        except requests.exceptions.ConnectionError:
            return {
                "status": "connection_error",
                "error": "Could not connect to endpoint",
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}


class DockerDeploymentValidator:
    """Main Docker deployment validator"""

    def __init__(self):
        self.docker_validator = DockerServiceValidator()
        self.health_validator = HealthEndpointValidator()

        # Expected services in Sophia AI deployment
        self.expected_services = [
            "sophia-backend",
            "sophia-frontend",
            "sophia-mcp-gateway",
            "redis",
            "postgres",
        ]

        # Health endpoints to check
        self.health_endpoints = [
            {"name": "backend_health", "url": "http://localhost:8000/health"},
            {"name": "frontend", "url": "http://localhost:3000"},
            {"name": "mcp_gateway", "url": "http://localhost:8080/health"},
        ]

    async def validate_deployment(self) -> Dict[str, Any]:
        """Validate the entire Docker deployment"""
        logger.info("🔍 Starting Docker Deployment Validation...")

        start_time = datetime.now(timezone.utc)

        validation_results = {
            "docker_services": await self._validate_docker_services(),
            "network_connectivity": self._validate_network_connectivity(),
            "health_endpoints": await self._validate_health_endpoints(),
            "resource_usage": self._validate_resource_usage(),
        }

        end_time = datetime.now(timezone.utc)

        # Generate summary
        summary = self._generate_summary(validation_results)

        report = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_execution_time": (end_time - start_time).total_seconds(),
            "sophia_ai_version": "v2.0.0",
            "deployment_type": "docker-compose",
            "summary": summary,
            "detailed_results": validation_results,
        }

        return report

    async def _validate_docker_services(self) -> Dict[str, Any]:
        """Validate Docker services"""
        logger.info("Checking Docker services...")

        service_results = {}

        for service in self.expected_services:
            logger.info(f"  Validating {service}...")
            service_results[service] = self.docker_validator.get_service_status(service)

        # Count healthy services
        healthy_services = sum(
            1
            for result in service_results.values()
            if result.get("status") == "running"
        )

        return {
            "services": service_results,
            "total_expected": len(self.expected_services),
            "healthy_count": healthy_services,
            "overall_status": (
                "healthy"
                if healthy_services == len(self.expected_services)
                else "degraded"
            ),
        }

    def _validate_network_connectivity(self) -> Dict[str, Any]:
        """Validate network connectivity"""
        logger.info("Checking network connectivity...")
        return self.docker_validator.validate_network_connectivity()

    async def _validate_health_endpoints(self) -> Dict[str, Any]:
        """Validate health endpoints"""
        logger.info("Checking health endpoints...")

        endpoint_results = {}

        for endpoint in self.health_endpoints:
            logger.info(f"  Checking {endpoint['name']}...")
            endpoint_results[
                endpoint["name"]
            ] = await self.health_validator.check_endpoint(endpoint["url"])

        # Count healthy endpoints
        healthy_endpoints = sum(
            1
            for result in endpoint_results.values()
            if result.get("status") == "healthy"
        )

        return {
            "endpoints": endpoint_results,
            "total_expected": len(self.health_endpoints),
            "healthy_count": healthy_endpoints,
            "overall_status": (
                "healthy"
                if healthy_endpoints == len(self.health_endpoints)
                else "degraded"
            ),
        }

    def _validate_resource_usage(self) -> Dict[str, Any]:
        """Validate resource usage"""
        logger.info("Checking resource usage...")

        if not self.docker_validator.client:
            return {"status": "error", "error": "Docker client not available"}

        try:
            # Get container stats
            containers = self.docker_validator.client.containers.list()
            sophia_containers = [c for c in containers if "sophia" in c.name.lower()]

            total_memory = 0
            total_cpu = 0
            container_count = len(sophia_containers)

            container_stats = {}
            for container in sophia_containers:
                try:
                    stats = container.stats(stream=False)

                    # Calculate memory usage
                    memory_usage = stats["memory_stats"].get("usage", 0)
                    memory_limit = stats["memory_stats"].get("limit", 0)
                    memory_percent = (
                        (memory_usage / memory_limit * 100) if memory_limit > 0 else 0
                    )

                    # Calculate CPU usage
                    cpu_stats = stats.get("cpu_stats", {})
                    precpu_stats = stats.get("precpu_stats", {})

                    cpu_delta = cpu_stats.get("cpu_usage", {}).get(
                        "total_usage", 0
                    ) - precpu_stats.get("cpu_usage", {}).get("total_usage", 0)
                    system_delta = cpu_stats.get(
                        "system_cpu_usage", 0
                    ) - precpu_stats.get("system_cpu_usage", 0)

                    cpu_percent = 0
                    if system_delta > 0 and cpu_delta > 0:
                        cpu_count = len(
                            cpu_stats.get("cpu_usage", {}).get("percpu_usage", [])
                        )
                        cpu_percent = (cpu_delta / system_delta) * cpu_count * 100

                    container_stats[container.name] = {
                        "memory_usage_mb": round(memory_usage / (1024 * 1024), 2),
                        "memory_percent": round(memory_percent, 2),
                        "cpu_percent": round(cpu_percent, 2),
                    }

                    total_memory += memory_usage
                    total_cpu += cpu_percent

                except Exception as e:
                    logger.warning(f"Could not get stats for {container.name}: {e}")

            return {
                "status": "healthy",
                "container_count": container_count,
                "total_memory_mb": round(total_memory / (1024 * 1024), 2),
                "average_cpu_percent": (
                    round(total_cpu / container_count, 2) if container_count > 0 else 0
                ),
                "container_stats": container_stats,
            }

        except Exception as e:
            return {"status": "error", "error": str(e)}

    def _generate_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate validation summary"""
        # Count healthy components
        service_status = results.get("docker_services", {}).get(
            "overall_status", "unknown"
        )
        network_status = results.get("network_connectivity", {}).get(
            "status", "unknown"
        )
        endpoint_status = results.get("health_endpoints", {}).get(
            "overall_status", "unknown"
        )
        resource_status = results.get("resource_usage", {}).get("status", "unknown")

        healthy_components = sum(
            1
            for status in [
                service_status,
                network_status,
                endpoint_status,
                resource_status,
            ]
            if status == "healthy"
        )

        total_components = 4

        # Determine overall status
        if healthy_components == total_components:
            overall_status = "healthy"
        elif healthy_components >= total_components * 0.75:
            overall_status = "degraded"
        else:
            overall_status = "unhealthy"

        # Calculate deployment readiness
        deployment_ready = overall_status == "healthy"

        return {
            "overall_status": overall_status,
            "healthy_components": healthy_components,
            "total_components": total_components,
            "deployment_ready": deployment_ready,
            "service_health": service_status,
            "network_health": network_status,
            "endpoint_health": endpoint_status,
            "resource_health": resource_status,
        }

    def save_report(self, report: Dict[str, Any], output_file: str = None) -> str:
        """Save validation report to file"""
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"sophia_docker_validation_{timestamp}.json"

        with open(output_file, "w") as f:
            json.dump(report, f, indent=2, default=str)

        return output_file

    def print_summary(self, report: Dict[str, Any]) -> None:
        """Print formatted validation summary"""
        summary = report["summary"]

        print("\n" + "=" * 60)
        print("🐳 SOPHIA AI DOCKER DEPLOYMENT VALIDATION")
        print("=" * 60)

        status_emoji = {"healthy": "✅", "degraded": "⚠️", "unhealthy": "❌"}.get(
            summary["overall_status"], "❓"
        )

        print(f"Overall Status: {status_emoji} {summary['overall_status'].upper()}")
        print(
            f"Components: {summary['healthy_components']}/{summary['total_components']} healthy"
        )
        print(
            f"Deployment Ready: {'✅ YES' if summary['deployment_ready'] else '❌ NO'}"
        )
        print(f"Execution Time: {report['total_execution_time']:.2f}s")

        # Component status
        print("\n📊 Component Status:")
        components = [
            ("Docker Services", summary["service_health"]),
            ("Network Connectivity", summary["network_health"]),
            ("Health Endpoints", summary["endpoint_health"]),
            ("Resource Usage", summary["resource_health"]),
        ]

        for name, status in components:
            emoji = {
                "healthy": "✅",
                "degraded": "⚠️",
                "unhealthy": "❌",
                "warning": "⚠️",
                "error": "❌",
            }.get(status, "❓")
            print(f"  {emoji} {name}: {status}")

        # Detailed service information
        services = (
            report["detailed_results"].get("docker_services", {}).get("services", {})
        )
        if services:
            print("\n🔧 Service Details:")
            for service_name, service_info in services.items():
                status = service_info.get("status", "unknown")
                emoji = {"running": "✅", "exited": "❌", "not_found": "❓"}.get(
                    status, "❓"
                )
                print(f"  {emoji} {service_name}: {status}")

        # Health endpoint details
        endpoints = (
            report["detailed_results"].get("health_endpoints", {}).get("endpoints", {})
        )
        if endpoints:
            print("\n🌐 Health Endpoints:")
            for endpoint_name, endpoint_info in endpoints.items():
                status = endpoint_info.get("status", "unknown")
                emoji = {
                    "healthy": "✅",
                    "unhealthy": "❌",
                    "timeout": "⏰",
                    "connection_error": "🔌",
                }.get(status, "❓")
                response_time = endpoint_info.get("response_time", 0)
                print(f"  {emoji} {endpoint_name}: {status} ({response_time}ms)")

        print("\n" + "=" * 60)


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Sophia AI Docker Deployment Validation"
    )
    parser.add_argument("--output", type=str, help="Output file for detailed report")
    parser.add_argument("--quiet", action="store_true", help="Suppress verbose output")

    args = parser.parse_args()

    if args.quiet:
        logging.getLogger().setLevel(logging.WARNING)

    # Run validation
    validator = DockerDeploymentValidator()
    report = await validator.validate_deployment()

    # Save detailed report
    report_file = validator.save_report(report, args.output)

    # Print summary
    validator.print_summary(report)

    print(f"\n📄 Detailed report saved to: {report_file}")

    # Exit with appropriate code
    overall_status = report["summary"]["overall_status"]
    exit_code = {"healthy": 0, "degraded": 1, "unhealthy": 2}.get(overall_status, 3)

    sys.exit(exit_code)


if __name__ == "__main__":
    asyncio.run(main())
