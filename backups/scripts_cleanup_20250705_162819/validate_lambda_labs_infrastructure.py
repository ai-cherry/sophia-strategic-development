#!/usr/bin/env python3
"""
Lambda Labs Infrastructure Validation Script
============================================

Validates the complete Lambda Labs infrastructure for Sophia AI MCP deployment.
Checks connectivity, resources, secrets, and deployment readiness.

Usage: python scripts/validate_lambda_labs_infrastructure.py [--environment prod]
"""

import asyncio
import json
import logging
import subprocess
import sys
import time
from datetime import datetime

import aiohttp

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class LambdaLabsInfrastructureValidator:
    """Validates Lambda Labs infrastructure for MCP deployment"""

    def __init__(self, environment: str = "prod"):
        self.environment = environment
        self.start_time = time.time()
        self.validation_results = {
            "infrastructure": {},
            "connectivity": {},
            "secrets": {},
            "resources": {},
            "deployment_readiness": {},
            "summary": {},
        }

        # Lambda Labs instances configuration
        self.instances = {
            "platform": {
                "name": "sophia-platform-prod",
                "ip": "146.235.200.1",
                "gpu_type": "gpu_1x_a10",
                "purpose": "Main Platform Services",
                "required_ports": [8000, 3000, 5432, 6379, 9090],
            },
            "mcp": {
                "name": "sophia-mcp-prod",
                "ip": "165.1.69.44",
                "gpu_type": "gpu_1x_a10",
                "purpose": "MCP Servers",
                "required_ports": [
                    8080,
                    9001,
                    3008,
                    9004,
                    9100,
                    9005,
                    9103,
                    9020,
                    9040,
                ],
            },
            "ai": {
                "name": "sophia-ai-prod",
                "ip": "137.131.6.213",
                "gpu_type": "gpu_1x_a100_sxm4",
                "purpose": "AI Processing",
                "required_ports": [8080, 9030],
            },
        }

        # Required secrets
        self.required_secrets = [
            "OPENAI_API_KEY",
            "ANTHROPIC_API_KEY",
            "SNOWFLAKE_ACCOUNT",
            "SNOWFLAKE_USER",
            "SNOWFLAKE_PASSWORD",
            "GONG_ACCESS_KEY",
            "HUBSPOT_ACCESS_TOKEN",
            "LINEAR_API_KEY",
            "ASANA_ACCESS_TOKEN",
            "NOTION_API_KEY",
            "LAMBDA_LABS_API_KEY",
            "DOCKER_HUB_PASSWORD",
        ]

    async def run_complete_validation(self) -> dict:
        """Run complete infrastructure validation"""
        logger.info("🔍 Starting Lambda Labs Infrastructure Validation...")

        try:
            # Phase 1: Infrastructure Validation
            await self._validate_infrastructure()

            # Phase 2: Connectivity Testing
            await self._validate_connectivity()

            # Phase 3: Secret Management Validation
            await self._validate_secrets()

            # Phase 4: Resource Availability
            await self._validate_resources()

            # Phase 5: Deployment Readiness
            await self._validate_deployment_readiness()

            # Generate summary
            self._generate_validation_summary()

            logger.info("✅ Infrastructure validation completed!")
            return self.validation_results

        except Exception as e:
            logger.error(f"❌ Infrastructure validation failed: {e}")
            self.validation_results["error"] = str(e)
            return self.validation_results

    async def _validate_infrastructure(self):
        """Phase 1: Validate Lambda Labs infrastructure"""
        logger.info("\n📋 Phase 1: Infrastructure Validation")

        infrastructure_results = {}

        for instance_name, config in self.instances.items():
            logger.info(f"   🔍 Validating {instance_name} ({config['ip']})...")

            instance_result = {
                "name": config["name"],
                "ip": config["ip"],
                "gpu_type": config["gpu_type"],
                "purpose": config["purpose"],
                "status": "unknown",
                "ssh_accessible": False,
                "docker_available": False,
                "gpu_available": False if "gpu" in config["gpu_type"] else None,
                "disk_space": "unknown",
                "validation_time": datetime.now().isoformat(),
            }

            # Test SSH connectivity
            ssh_result = await self._test_ssh_connectivity(config["ip"])
            instance_result["ssh_accessible"] = ssh_result["success"]
            instance_result["ssh_details"] = ssh_result

            if ssh_result["success"]:
                # Test Docker availability
                docker_result = await self._test_docker_availability(config["ip"])
                instance_result["docker_available"] = docker_result["success"]
                instance_result["docker_details"] = docker_result

                # Test GPU availability (if applicable)
                if "gpu" in config["gpu_type"]:
                    gpu_result = await self._test_gpu_availability(config["ip"])
                    instance_result["gpu_available"] = gpu_result["success"]
                    instance_result["gpu_details"] = gpu_result

                # Check disk space
                disk_result = await self._check_disk_space(config["ip"])
                instance_result["disk_space"] = disk_result

                # Determine overall status
                if (
                    instance_result["ssh_accessible"]
                    and instance_result["docker_available"]
                    and (instance_result["gpu_available"] is not False)
                ):
                    instance_result["status"] = "healthy"
                else:
                    instance_result["status"] = "unhealthy"
            else:
                instance_result["status"] = "unreachable"

            infrastructure_results[instance_name] = instance_result

            # Log results
            status_emoji = "✅" if instance_result["status"] == "healthy" else "❌"
            logger.info(
                f"   {status_emoji} {instance_name}: {instance_result['status']}"
            )

        self.validation_results["infrastructure"] = infrastructure_results

    async def _validate_connectivity(self):
        """Phase 2: Validate network connectivity and port accessibility"""
        logger.info("\n🌐 Phase 2: Connectivity Validation")

        connectivity_results = {}

        for instance_name, config in self.instances.items():
            logger.info(f"   🔍 Testing connectivity for {instance_name}...")

            instance_connectivity = {
                "instance": instance_name,
                "ip": config["ip"],
                "port_tests": {},
                "cross_instance_connectivity": {},
                "internet_connectivity": False,
                "dns_resolution": False,
            }

            # Test required ports
            for port in config["required_ports"]:
                port_result = await self._test_port_connectivity(config["ip"], port)
                instance_connectivity["port_tests"][port] = port_result

                status_emoji = "✅" if port_result["accessible"] else "❌"
                logger.info(f"     {status_emoji} Port {port}: {port_result['status']}")

            # Test cross-instance connectivity
            for other_instance, other_config in self.instances.items():
                if other_instance != instance_name:
                    cross_connect = await self._test_cross_instance_connectivity(
                        config["ip"], other_config["ip"]
                    )
                    instance_connectivity["cross_instance_connectivity"][
                        other_instance
                    ] = cross_connect

            # Test internet connectivity
            internet_result = await self._test_internet_connectivity(config["ip"])
            instance_connectivity["internet_connectivity"] = internet_result["success"]
            instance_connectivity["internet_details"] = internet_result

            # Test DNS resolution
            dns_result = await self._test_dns_resolution(config["ip"])
            instance_connectivity["dns_resolution"] = dns_result["success"]
            instance_connectivity["dns_details"] = dns_result

            connectivity_results[instance_name] = instance_connectivity

        self.validation_results["connectivity"] = connectivity_results

    async def _validate_secrets(self):
        """Phase 3: Validate secret management and access"""
        logger.info("\n🔐 Phase 3: Secret Management Validation")

        secrets_results = {
            "pulumi_esc_access": False,
            "github_secrets": {},
            "docker_hub_access": False,
            "secret_counts": {},
            "missing_secrets": [],
            "secret_validation_details": {},
        }

        # Test Pulumi ESC access
        pulumi_result = await self._test_pulumi_esc_access()
        secrets_results["pulumi_esc_access"] = pulumi_result["success"]
        secrets_results["pulumi_details"] = pulumi_result

        if pulumi_result["success"]:
            # Validate required secrets
            for secret_name in self.required_secrets:
                secret_result = await self._validate_secret(secret_name)
                secrets_results["secret_validation_details"][
                    secret_name
                ] = secret_result

                if not secret_result["available"]:
                    secrets_results["missing_secrets"].append(secret_name)

                status_emoji = "✅" if secret_result["available"] else "❌"
                logger.info(
                    f"   {status_emoji} {secret_name}: {'Available' if secret_result['available'] else 'Missing'}"
                )

        # Test Docker Hub access
        docker_result = await self._test_docker_hub_access()
        secrets_results["docker_hub_access"] = docker_result["success"]
        secrets_results["docker_hub_details"] = docker_result

        # Count available secrets
        secrets_results["secret_counts"] = {
            "total_required": len(self.required_secrets),
            "available": len(self.required_secrets)
            - len(secrets_results["missing_secrets"]),
            "missing": len(secrets_results["missing_secrets"]),
            "availability_percentage": (
                (len(self.required_secrets) - len(secrets_results["missing_secrets"]))
                / len(self.required_secrets)
            )
            * 100,
        }

        self.validation_results["secrets"] = secrets_results

    async def _validate_resources(self):
        """Phase 4: Validate resource availability and capacity"""
        logger.info("\n💾 Phase 4: Resource Validation")

        resources_results = {}

        for instance_name, config in self.instances.items():
            logger.info(f"   🔍 Checking resources for {instance_name}...")

            instance_resources = {
                "instance": instance_name,
                "cpu_info": {},
                "memory_info": {},
                "disk_info": {},
                "gpu_info": {},
                "docker_resources": {},
                "resource_sufficiency": "unknown",
            }

            # Get system resources
            cpu_info = await self._get_cpu_info(config["ip"])
            instance_resources["cpu_info"] = cpu_info

            memory_info = await self._get_memory_info(config["ip"])
            instance_resources["memory_info"] = memory_info

            disk_info = await self._get_disk_info(config["ip"])
            instance_resources["disk_info"] = disk_info

            # Get GPU info if applicable
            if "gpu" in config["gpu_type"]:
                gpu_info = await self._get_gpu_info(config["ip"])
                instance_resources["gpu_info"] = gpu_info

            # Get Docker resource info
            docker_resources = await self._get_docker_resources(config["ip"])
            instance_resources["docker_resources"] = docker_resources

            # Assess resource sufficiency
            sufficiency = self._assess_resource_sufficiency(
                instance_resources, instance_name
            )
            instance_resources["resource_sufficiency"] = sufficiency

            resources_results[instance_name] = instance_resources

            status_emoji = (
                "✅"
                if sufficiency == "sufficient"
                else "⚠️"
                if sufficiency == "marginal"
                else "❌"
            )
            logger.info(f"   {status_emoji} {instance_name}: {sufficiency} resources")

        self.validation_results["resources"] = resources_results

    async def _validate_deployment_readiness(self):
        """Phase 5: Validate deployment readiness"""
        logger.info("\n🚀 Phase 5: Deployment Readiness Validation")

        readiness_results = {
            "docker_images_available": {},
            "network_configuration": {},
            "security_configuration": {},
            "monitoring_setup": {},
            "backup_configuration": {},
            "overall_readiness": "unknown",
            "readiness_score": 0,
            "blocking_issues": [],
            "recommendations": [],
        }

        # Check Docker images availability
        required_images = [
            "scoobyjava15/sophia-codacy-mcp:latest",
            "scoobyjava15/sophia-linear-mcp:latest",
            "scoobyjava15/sophia-ai-memory-mcp:latest",
            "scoobyjava15/sophia-asana-mcp:latest",
            "scoobyjava15/sophia-notion-mcp:latest",
        ]

        for image in required_images:
            image_result = await self._check_docker_image_availability(image)
            readiness_results["docker_images_available"][image] = image_result

            if not image_result["available"]:
                readiness_results["blocking_issues"].append(
                    f"Docker image not available: {image}"
                )

        # Calculate readiness score
        readiness_score = self._calculate_readiness_score()
        readiness_results["readiness_score"] = readiness_score

        # Determine overall readiness
        if readiness_score >= 90:
            readiness_results["overall_readiness"] = "ready"
        elif readiness_score >= 70:
            readiness_results["overall_readiness"] = "mostly_ready"
        elif readiness_score >= 50:
            readiness_results["overall_readiness"] = "partially_ready"
        else:
            readiness_results["overall_readiness"] = "not_ready"

        # Generate recommendations
        recommendations = self._generate_recommendations()
        readiness_results["recommendations"] = recommendations

        self.validation_results["deployment_readiness"] = readiness_results

    def _generate_validation_summary(self):
        """Generate comprehensive validation summary"""
        summary = {
            "validation_start_time": datetime.fromtimestamp(
                self.start_time
            ).isoformat(),
            "validation_end_time": datetime.now().isoformat(),
            "validation_duration": time.time() - self.start_time,
            "environment": self.environment,
            "infrastructure_health": "unknown",
            "connectivity_status": "unknown",
            "secrets_availability": "unknown",
            "resource_adequacy": "unknown",
            "deployment_readiness": "unknown",
            "overall_status": "unknown",
            "critical_issues": [],
            "warnings": [],
            "recommendations": [],
        }

        # Assess infrastructure health
        healthy_instances = sum(
            1
            for instance in self.validation_results["infrastructure"].values()
            if instance["status"] == "healthy"
        )
        total_instances = len(self.validation_results["infrastructure"])

        if healthy_instances == total_instances:
            summary["infrastructure_health"] = "excellent"
        elif healthy_instances >= total_instances * 0.8:
            summary["infrastructure_health"] = "good"
        elif healthy_instances >= total_instances * 0.5:
            summary["infrastructure_health"] = "fair"
        else:
            summary["infrastructure_health"] = "poor"

        # Assess secrets availability
        secrets_percentage = self.validation_results["secrets"]["secret_counts"][
            "availability_percentage"
        ]
        if secrets_percentage >= 95:
            summary["secrets_availability"] = "excellent"
        elif secrets_percentage >= 85:
            summary["secrets_availability"] = "good"
        elif secrets_percentage >= 70:
            summary["secrets_availability"] = "fair"
        else:
            summary["secrets_availability"] = "poor"

        # Determine overall status
        readiness_score = self.validation_results["deployment_readiness"][
            "readiness_score"
        ]
        if readiness_score >= 90:
            summary["overall_status"] = "ready_for_production"
        elif readiness_score >= 70:
            summary["overall_status"] = "ready_for_staging"
        elif readiness_score >= 50:
            summary["overall_status"] = "needs_improvements"
        else:
            summary["overall_status"] = "not_ready"

        self.validation_results["summary"] = summary

    # Helper methods for individual validations
    async def _test_ssh_connectivity(self, ip: str) -> dict:
        """Test SSH connectivity to instance"""
        try:
            cmd = f"ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no ubuntu@{ip} 'echo SSH_SUCCESS'"
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, timeout=15
            )

            return {
                "success": result.returncode == 0 and "SSH_SUCCESS" in result.stdout,
                "response_time": "unknown",
                "details": result.stdout.strip()
                if result.returncode == 0
                else result.stderr.strip(),
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "details": "SSH connection failed",
            }

    async def _test_docker_availability(self, ip: str) -> dict:
        """Test Docker availability on instance"""
        try:
            cmd = f"ssh ubuntu@{ip} 'docker --version && docker ps'"
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, timeout=15
            )

            return {
                "success": result.returncode == 0,
                "docker_version": result.stdout.split("\n")[0]
                if result.returncode == 0
                else "unknown",
                "running_containers": len(result.stdout.split("\n")) - 2
                if result.returncode == 0
                else 0,
                "details": result.stdout.strip()
                if result.returncode == 0
                else result.stderr.strip(),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _test_gpu_availability(self, ip: str) -> dict:
        """Test GPU availability on instance"""
        try:
            cmd = f"ssh ubuntu@{ip} 'nvidia-smi --query-gpu=name,memory.total --format=csv,noheader,nounits'"
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, timeout=15
            )

            if result.returncode == 0:
                gpu_info = result.stdout.strip().split("\n")
                return {
                    "success": True,
                    "gpu_count": len(gpu_info),
                    "gpu_details": gpu_info,
                    "details": result.stdout.strip(),
                }
            else:
                return {
                    "success": False,
                    "error": result.stderr.strip(),
                    "details": "GPU not available or nvidia-smi not found",
                }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _test_port_connectivity(self, ip: str, port: int) -> dict:
        """Test port connectivity"""
        try:
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=5)
            ) as session:
                try:
                    async with session.get(f"http://{ip}:{port}/health") as response:
                        return {
                            "accessible": True,
                            "status": f"HTTP {response.status}",
                            "response_time": "< 5s",
                        }
                except aiohttp.ClientError:
                    # Try basic TCP connection
                    import socket

                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(5)
                    result = sock.connect_ex((ip, port))
                    sock.close()

                    return {
                        "accessible": result == 0,
                        "status": "TCP connection successful"
                        if result == 0
                        else "TCP connection failed",
                        "response_time": "< 5s" if result == 0 else "timeout",
                    }
        except Exception as e:
            return {"accessible": False, "status": "Connection failed", "error": str(e)}

    async def _test_pulumi_esc_access(self) -> dict:
        """Test Pulumi ESC access"""
        try:
            cmd = "pulumi env get scoobyjava-org/default/sophia-ai-production --json"
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, timeout=30
            )

            if result.returncode == 0:
                try:
                    env_data = json.loads(result.stdout)
                    return {
                        "success": True,
                        "environment_accessible": True,
                        "secret_count": len(env_data.get("properties", {})),
                        "details": "Pulumi ESC environment accessible",
                    }
                except json.JSONDecodeError:
                    return {
                        "success": False,
                        "error": "Invalid JSON response from Pulumi ESC",
                    }
            else:
                return {
                    "success": False,
                    "error": result.stderr.strip(),
                    "details": "Pulumi ESC access failed",
                }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _validate_secret(self, secret_name: str) -> dict:
        """Validate individual secret availability"""
        try:
            # Try to get secret from Pulumi ESC
            cmd = f"pulumi config get {secret_name} --stack scoobyjava-org/sophia-ai-production"
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, timeout=10
            )

            return {
                "available": result.returncode == 0 and len(result.stdout.strip()) > 0,
                "masked_value": "***" if result.returncode == 0 else None,
                "source": "pulumi_esc",
                "details": "Secret available"
                if result.returncode == 0
                else "Secret not found",
            }
        except Exception as e:
            return {"available": False, "error": str(e), "source": "pulumi_esc"}

    async def _check_docker_image_availability(self, image: str) -> dict:
        """Check if Docker image is available"""
        try:
            cmd = f"docker manifest inspect {image}"
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, timeout=30
            )

            return {
                "available": result.returncode == 0,
                "image": image,
                "details": "Image available in registry"
                if result.returncode == 0
                else "Image not found",
            }
        except Exception as e:
            return {"available": False, "image": image, "error": str(e)}

    def _calculate_readiness_score(self) -> int:
        """Calculate overall deployment readiness score"""
        score = 0

        # Infrastructure health (30 points)
        healthy_instances = sum(
            1
            for instance in self.validation_results["infrastructure"].values()
            if instance["status"] == "healthy"
        )
        total_instances = len(self.validation_results["infrastructure"])
        infrastructure_score = (healthy_instances / total_instances) * 30
        score += infrastructure_score

        # Secrets availability (25 points)
        secrets_percentage = self.validation_results["secrets"]["secret_counts"][
            "availability_percentage"
        ]
        secrets_score = (secrets_percentage / 100) * 25
        score += secrets_score

        # Connectivity (20 points)
        # Calculate based on successful port tests
        total_ports = sum(
            len(instance["port_tests"])
            for instance in self.validation_results["connectivity"].values()
        )
        successful_ports = sum(
            sum(
                1
                for port_test in instance["port_tests"].values()
                if port_test["accessible"]
            )
            for instance in self.validation_results["connectivity"].values()
        )
        connectivity_score = (
            (successful_ports / total_ports) * 20 if total_ports > 0 else 0
        )
        score += connectivity_score

        # Docker images (15 points)
        available_images = sum(
            1
            for image in self.validation_results["deployment_readiness"][
                "docker_images_available"
            ].values()
            if image["available"]
        )
        total_images = len(
            self.validation_results["deployment_readiness"]["docker_images_available"]
        )
        images_score = (
            (available_images / total_images) * 15 if total_images > 0 else 15
        )
        score += images_score

        # General readiness (10 points)
        if self.validation_results["secrets"]["pulumi_esc_access"]:
            score += 5
        if self.validation_results["secrets"]["docker_hub_access"]:
            score += 5

        return int(score)

    def _generate_recommendations(self) -> list[str]:
        """Generate recommendations based on validation results"""
        recommendations = []

        # Infrastructure recommendations
        unhealthy_instances = [
            name
            for name, instance in self.validation_results["infrastructure"].items()
            if instance["status"] != "healthy"
        ]
        if unhealthy_instances:
            recommendations.append(
                f"Fix unhealthy instances: {', '.join(unhealthy_instances)}"
            )

        # Secrets recommendations
        missing_secrets = self.validation_results["secrets"]["missing_secrets"]
        if missing_secrets:
            recommendations.append(
                f"Add missing secrets to Pulumi ESC: {', '.join(missing_secrets)}"
            )

        # Connectivity recommendations
        for instance_name, connectivity in self.validation_results[
            "connectivity"
        ].items():
            failed_ports = [
                str(port)
                for port, result in connectivity["port_tests"].items()
                if not result["accessible"]
            ]
            if failed_ports:
                recommendations.append(
                    f"Fix port accessibility on {instance_name}: {', '.join(failed_ports)}"
                )

        # Docker images recommendations
        unavailable_images = [
            image
            for image, result in self.validation_results["deployment_readiness"][
                "docker_images_available"
            ].items()
            if not result["available"]
        ]
        if unavailable_images:
            recommendations.append("Build and push missing Docker images to registry")

        return recommendations

    # Additional helper methods for resource checking
    async def _check_disk_space(self, ip: str) -> dict:
        """Check disk space on instance"""
        try:
            cmd = f"ssh ubuntu@{ip} 'df -h / | tail -1'"
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, timeout=10
            )

            if result.returncode == 0:
                disk_info = result.stdout.strip().split()
                return {
                    "total": disk_info[1],
                    "used": disk_info[2],
                    "available": disk_info[3],
                    "usage_percentage": disk_info[4],
                    "sufficient": int(disk_info[4].replace("%", "")) < 80,
                }
            else:
                return {"error": result.stderr.strip()}
        except Exception as e:
            return {"error": str(e)}

    async def _test_cross_instance_connectivity(self, from_ip: str, to_ip: str) -> dict:
        """Test connectivity between instances"""
        try:
            cmd = f"ssh ubuntu@{from_ip} 'ping -c 3 {to_ip}'"
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, timeout=15
            )

            return {
                "success": result.returncode == 0,
                "packet_loss": "0%" if result.returncode == 0 else "100%",
                "details": result.stdout.strip()
                if result.returncode == 0
                else result.stderr.strip(),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _test_internet_connectivity(self, ip: str) -> dict:
        """Test internet connectivity from instance"""
        try:
            cmd = f"ssh ubuntu@{ip} 'curl -s --max-time 10 https://www.google.com'"
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, timeout=15
            )

            return {
                "success": result.returncode == 0,
                "details": "Internet accessible"
                if result.returncode == 0
                else "Internet not accessible",
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _test_dns_resolution(self, ip: str) -> dict:
        """Test DNS resolution from instance"""
        try:
            cmd = f"ssh ubuntu@{ip} 'nslookup google.com'"
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, timeout=10
            )

            return {
                "success": result.returncode == 0,
                "details": "DNS resolution working"
                if result.returncode == 0
                else "DNS resolution failed",
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _test_docker_hub_access(self) -> dict:
        """Test Docker Hub access"""
        try:
            cmd = "docker pull hello-world:latest"
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, timeout=30
            )

            return {
                "success": result.returncode == 0,
                "details": "Docker Hub accessible"
                if result.returncode == 0
                else "Docker Hub access failed",
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _get_cpu_info(self, ip: str) -> dict:
        """Get CPU information from instance"""
        try:
            cmd = f"ssh ubuntu@{ip} 'nproc && lscpu | grep \"Model name\"'"
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, timeout=10
            )

            if result.returncode == 0:
                lines = result.stdout.strip().split("\n")
                return {
                    "cores": int(lines[0]),
                    "model": lines[1].split(":")[1].strip()
                    if len(lines) > 1
                    else "unknown",
                }
            else:
                return {"error": result.stderr.strip()}
        except Exception as e:
            return {"error": str(e)}

    async def _get_memory_info(self, ip: str) -> dict:
        """Get memory information from instance"""
        try:
            cmd = f"ssh ubuntu@{ip} 'free -h'"
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, timeout=10
            )

            if result.returncode == 0:
                lines = result.stdout.strip().split("\n")
                mem_line = lines[1].split()
                return {
                    "total": mem_line[1],
                    "used": mem_line[2],
                    "available": mem_line[6],
                    "usage_percentage": f"{int((float(mem_line[2].replace('Gi', '')) / float(mem_line[1].replace('Gi', ''))) * 100)}%",
                }
            else:
                return {"error": result.stderr.strip()}
        except Exception as e:
            return {"error": str(e)}

    async def _get_disk_info(self, ip: str) -> dict:
        """Get disk information from instance"""
        try:
            cmd = f"ssh ubuntu@{ip} 'df -h /'"
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, timeout=10
            )

            if result.returncode == 0:
                lines = result.stdout.strip().split("\n")
                disk_line = lines[1].split()
                return {
                    "total": disk_line[1],
                    "used": disk_line[2],
                    "available": disk_line[3],
                    "usage_percentage": disk_line[4],
                }
            else:
                return {"error": result.stderr.strip()}
        except Exception as e:
            return {"error": str(e)}

    async def _get_gpu_info(self, ip: str) -> dict:
        """Get GPU information from instance"""
        try:
            cmd = f"ssh ubuntu@{ip} 'nvidia-smi --query-gpu=name,memory.total,memory.used,memory.free --format=csv,noheader,nounits'"
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, timeout=10
            )

            if result.returncode == 0:
                gpu_lines = result.stdout.strip().split("\n")
                gpus = []
                for line in gpu_lines:
                    parts = line.split(", ")
                    if len(parts) >= 4:
                        gpus.append(
                            {
                                "name": parts[0],
                                "memory_total": f"{parts[1]} MB",
                                "memory_used": f"{parts[2]} MB",
                                "memory_free": f"{parts[3]} MB",
                            }
                        )
                return {"gpu_count": len(gpus), "gpus": gpus}
            else:
                return {"error": result.stderr.strip()}
        except Exception as e:
            return {"error": str(e)}

    async def _get_docker_resources(self, ip: str) -> dict:
        """Get Docker resource information from instance"""
        try:
            cmd = f"ssh ubuntu@{ip} 'docker system df && docker stats --no-stream --format \"table {{{{.Container}}}}\t{{{{.CPUPerc}}}}\t{{{{.MemUsage}}}}\"'"
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, timeout=15
            )

            if result.returncode == 0:
                return {
                    "docker_system_info": result.stdout.strip(),
                    "running_containers": len(result.stdout.strip().split("\n")) - 1,
                }
            else:
                return {"error": result.stderr.strip()}
        except Exception as e:
            return {"error": str(e)}

    def _assess_resource_sufficiency(self, resources: dict, instance_name: str) -> str:
        """Assess if resources are sufficient for the instance role"""
        try:
            # Define minimum requirements by instance type
            requirements = {
                "platform": {"cpu_cores": 4, "memory_gb": 8, "disk_usage_max": 70},
                "mcp": {"cpu_cores": 2, "memory_gb": 4, "disk_usage_max": 80},
                "ai": {
                    "cpu_cores": 8,
                    "memory_gb": 16,
                    "disk_usage_max": 60,
                    "gpu_required": True,
                },
            }

            if instance_name not in requirements:
                return "unknown"

            req = requirements[instance_name]

            # Check CPU
            cpu_cores = resources.get("cpu_info", {}).get("cores", 0)
            if cpu_cores < req["cpu_cores"]:
                return "insufficient"

            # Check memory (simplified check)
            memory_info = resources.get("memory_info", {})
            if "error" in memory_info:
                return "unknown"

            # Check disk usage
            disk_info = resources.get("disk_info", {})
            if "usage_percentage" in disk_info:
                usage = int(disk_info["usage_percentage"].replace("%", ""))
                if usage > req["disk_usage_max"]:
                    return "insufficient"

            # Check GPU if required
            if req.get("gpu_required", False):
                gpu_info = resources.get("gpu_info", {})
                if "error" in gpu_info or gpu_info.get("gpu_count", 0) == 0:
                    return "insufficient"

            return "sufficient"

        except Exception as e:
            logger.warning(f"Error assessing resources for {instance_name}: {e}")
            return "unknown"

    def print_validation_summary(self):
        """Print comprehensive validation summary"""
        summary = self.validation_results["summary"]

        print("\n" + "=" * 80)
        print("🔍 LAMBDA LABS INFRASTRUCTURE VALIDATION SUMMARY")
        print("=" * 80)

        print(f"Environment: {summary['environment']}")
        print(f"Validation Duration: {summary['validation_duration']:.2f} seconds")
        print(f"Overall Status: {summary['overall_status'].replace('_', ' ').title()}")

        print("\n📊 COMPONENT HEALTH:")
        print(f"  Infrastructure: {summary['infrastructure_health'].title()}")
        print(
            f"  Connectivity: {summary.get('connectivity_status', 'Unknown').title()}"
        )
        print(f"  Secrets: {summary['secrets_availability'].title()}")
        print(f"  Resources: {summary.get('resource_adequacy', 'Unknown').title()}")
        print(
            f"  Deployment Readiness: {self.validation_results['deployment_readiness']['overall_readiness'].replace('_', ' ').title()}"
        )

        readiness_score = self.validation_results["deployment_readiness"][
            "readiness_score"
        ]
        print(f"\n🎯 READINESS SCORE: {readiness_score}/100")

        # Print instance status
        print("\n🖥️ INSTANCE STATUS:")
        for instance_name, instance in self.validation_results[
            "infrastructure"
        ].items():
            status_emoji = "✅" if instance["status"] == "healthy" else "❌"
            print(
                f"  {status_emoji} {instance_name} ({instance['ip']}): {instance['status']}"
            )

        # Print secret status
        secrets = self.validation_results["secrets"]["secret_counts"]
        print("\n🔐 SECRETS STATUS:")
        print(
            f"  Available: {secrets['available']}/{secrets['total_required']} ({secrets['availability_percentage']:.1f}%)"
        )

        if self.validation_results["secrets"]["missing_secrets"]:
            print(
                f"  Missing: {', '.join(self.validation_results['secrets']['missing_secrets'])}"
            )

        # Print recommendations
        recommendations = self.validation_results["deployment_readiness"][
            "recommendations"
        ]
        if recommendations:
            print("\n💡 RECOMMENDATIONS:")
            for i, rec in enumerate(recommendations, 1):
                print(f"  {i}. {rec}")

        # Print blocking issues
        blocking_issues = self.validation_results["deployment_readiness"][
            "blocking_issues"
        ]
        if blocking_issues:
            print("\n🚨 BLOCKING ISSUES:")
            for i, issue in enumerate(blocking_issues, 1):
                print(f"  {i}. {issue}")

        print("\n✅ Validation completed successfully!")


def main():
    """Main validation function"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Validate Lambda Labs infrastructure for MCP deployment"
    )
    parser.add_argument(
        "--environment",
        default="prod",
        choices=["prod", "staging", "dev"],
        help="Target environment",
    )
    parser.add_argument("--output", help="Output file for validation results (JSON)")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")

    args = parser.parse_args()

    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Run validation
    validator = LambdaLabsInfrastructureValidator(environment=args.environment)

    try:
        results = asyncio.run(validator.run_complete_validation())

        # Print summary
        validator.print_validation_summary()

        # Save results if requested
        if args.output:
            with open(args.output, "w") as f:
                json.dump(results, f, indent=2, default=str)
            print(f"\n📄 Validation results saved to: {args.output}")

        # Exit with appropriate code
        overall_status = results["summary"]["overall_status"]
        if overall_status in ["ready_for_production", "ready_for_staging"]:
            sys.exit(0)
        else:
            print(f"\n❌ Infrastructure not ready for deployment: {overall_status}")
            sys.exit(1)

    except Exception as e:
        logger.error(f"❌ Validation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
