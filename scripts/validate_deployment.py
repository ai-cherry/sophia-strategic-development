#!/usr/bin/env python3
"""
Comprehensive Deployment Validation Script
Validates that all services are properly deployed and healthy
"""

import argparse
import json
import sys
import time
from datetime import datetime

import requests


class DeploymentValidator:
    def __init__(self, host: str, timeout: int = 300):
        self.host = host
        self.timeout = timeout
        self.start_time = time.time()
        self.results = {
            "host": host,
            "timestamp": datetime.utcnow().isoformat(),
            "services": {},
            "overall_status": "pending",
        }

    def check_endpoint(self, url: str, expected_status: int = 200) -> tuple[bool, str]:
        """Check if an endpoint is responsive"""
        try:
            response = requests.get(url, timeout=10)
            success = response.status_code == expected_status
            message = f"Status: {response.status_code}"

            # Try to get version info
            if success and response.headers.get("content-type", "").startswith(
                "application/json"
            ):
                try:
                    data = response.json()
                    if "version" in data:
                        message += f", Version: {data['version']}"
                    if "commit" in data:
                        message += f", Commit: {data['commit'][:8]}"
                except:
                    pass

            return success, message
        except requests.exceptions.ConnectionError:
            return False, "Connection refused"
        except requests.exceptions.Timeout:
            return False, "Request timeout"
        except Exception as e:
            return False, str(e)

    def wait_for_service(self, service: str, endpoints: list[str]) -> dict:
        """Wait for a service to become healthy"""
        service_result = {
            "status": "checking",
            "endpoints": {},
            "start_time": time.time(),
        }

        print(f"\n🔍 Checking {service}...")

        all_healthy = False
        while not all_healthy and (time.time() - self.start_time) < self.timeout:
            all_healthy = True

            for endpoint in endpoints:
                url = f"http://{self.host}{endpoint}"
                success, message = self.check_endpoint(url)

                service_result["endpoints"][endpoint] = {
                    "url": url,
                    "healthy": success,
                    "message": message,
                    "last_check": time.time(),
                }

                if success:
                    print(f"  ✅ {endpoint}: {message}")
                else:
                    print(f"  ⏳ {endpoint}: {message}")
                    all_healthy = False

            if not all_healthy:
                time.sleep(5)

        service_result["status"] = "healthy" if all_healthy else "unhealthy"
        service_result["duration"] = time.time() - service_result["start_time"]

        return service_result

    def check_docker_swarm(self) -> dict:
        """Check Docker Swarm service status via SSH"""
        import subprocess

        print("\n🐳 Checking Docker Swarm services...")
        swarm_result = {"status": "checking", "services": {}}

        try:
            # Get service list
            cmd = f"ssh -o StrictHostKeyChecking=no ubuntu@{self.host} 'docker service ls --format json'"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=False)

            if result.returncode == 0:
                for line in result.stdout.strip().split("\n"):
                    if line:
                        service = json.loads(line)
                        name = service.get("Name", "")
                        replicas = service.get("Replicas", "0/0")

                        swarm_result["services"][name] = {
                            "replicas": replicas,
                            "healthy": "/" in replicas
                            and replicas.split("/")[0] == replicas.split("/")[1],
                        }

                        print(
                            f"  {'✅' if swarm_result['services'][name]['healthy'] else '❌'} {name}: {replicas}"
                        )

                swarm_result["status"] = (
                    "healthy"
                    if all(s["healthy"] for s in swarm_result["services"].values())
                    else "unhealthy"
                )
            else:
                swarm_result["status"] = "error"
                swarm_result["error"] = result.stderr
                print(f"  ❌ Failed to check Swarm: {result.stderr}")

        except Exception as e:
            swarm_result["status"] = "error"
            swarm_result["error"] = str(e)
            print(f"  ❌ Error checking Swarm: {e}")

        return swarm_result

    def validate_deployment(self, services: dict[str, list[str]]) -> bool:
        """Validate the complete deployment"""
        print(f"🚀 Validating deployment on {self.host}")
        print(f"⏱️  Timeout: {self.timeout} seconds")
        print("=" * 60)

        # Check each service
        all_healthy = True
        for service, endpoints in services.items():
            result = self.wait_for_service(service, endpoints)
            self.results["services"][service] = result

            if result["status"] != "healthy":
                all_healthy = False

        # Check Docker Swarm
        swarm_result = self.check_docker_swarm()
        self.results["docker_swarm"] = swarm_result

        if swarm_result["status"] != "healthy":
            all_healthy = False

        # Overall result
        self.results["overall_status"] = "healthy" if all_healthy else "unhealthy"
        self.results["total_duration"] = time.time() - self.start_time

        # Print summary
        print("\n" + "=" * 60)
        print("📊 VALIDATION SUMMARY")
        print("=" * 60)

        for service, result in self.results["services"].items():
            status_icon = "✅" if result["status"] == "healthy" else "❌"
            print(
                f"{status_icon} {service}: {result['status']} ({result['duration']:.1f}s)"
            )

            for endpoint, details in result["endpoints"].items():
                sub_icon = "  ✓" if details["healthy"] else "  ✗"
                print(f"{sub_icon} {endpoint}: {details['message']}")

        if "docker_swarm" in self.results:
            swarm = self.results["docker_swarm"]
            status_icon = "✅" if swarm["status"] == "healthy" else "❌"
            print(f"\n{status_icon} Docker Swarm: {swarm['status']}")

            if "services" in swarm:
                for svc, details in swarm["services"].items():
                    sub_icon = "  ✓" if details["healthy"] else "  ✗"
                    print(f"{sub_icon} {svc}: {details['replicas']}")

        print(f"\n🎯 Overall Status: {self.results['overall_status'].upper()}")
        print(f"⏱️  Total Duration: {self.results['total_duration']:.1f}s")

        return all_healthy

    def save_report(self, filename: str = "deployment_validation_report.json"):
        """Save validation report to file"""
        with open(filename, "w") as f:
            json.dump(self.results, f, indent=2)
        print(f"\n📄 Report saved to: {filename}")


def main():
    parser = argparse.ArgumentParser(description="Validate Sophia AI deployment")
    parser.add_argument("--host", required=True, help="Host to validate")
    parser.add_argument(
        "--services",
        default="backend,mcp-gateway",
        help="Comma-separated list of services",
    )
    parser.add_argument(
        "--health-endpoints",
        default="/health,/api/health",
        help="Health check endpoints",
    )
    parser.add_argument("--timeout", type=int, default=300, help="Timeout in seconds")
    parser.add_argument(
        "--output",
        default="deployment_validation_report.json",
        help="Output report file",
    )

    args = parser.parse_args()

    # Parse services and endpoints
    service_list = args.services.split(",")
    endpoint_list = args.health_endpoints.split(",")

    # Build service configuration
    services = {}
    for service in service_list:
        if service == "backend":
            services["backend"] = [":8000/health", ":8000/api/health", ":8000/docs"]
        elif service == "mcp-gateway":
            services["mcp-gateway"] = [":8080/health", ":8080/mcp/list"]
        elif service == "frontend":
            services["frontend"] = [":3000"]
        else:
            # Generic service with provided endpoints
            services[service] = [
                f":{8000 + service_list.index(service)}{ep}" for ep in endpoint_list
            ]

    # Run validation
    validator = DeploymentValidator(args.host, args.timeout)
    success = validator.validate_deployment(services)
    validator.save_report(args.output)

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
