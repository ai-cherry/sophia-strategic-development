#!/usr/bin/env python3
"""
Lambda Labs Infrastructure Health Monitor
Comprehensive monitoring for all deployed services and resources
"""

import json
import logging
import os
import subprocess
import sys
import time
from datetime import datetime
from typing import Any

import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Lambda Labs instance configuration
INSTANCES = {
    "sophia-ai-core": {
        "ip": "192.222.58.232",
        "gpu": "GH200",
        "memory": "96GB",
        "services": [{"name": "backend", "port": 8000, "endpoint": "/health"}],
    },
    "sophia-mcp-orchestrator": {
        "ip": "104.171.202.117",
        "gpu": "A6000",
        "memory": "48GB",
        "services": [{"name": "mcp-orchestrator", "port": 8001, "endpoint": "/health"}],
    },
    "sophia-data-pipeline": {
        "ip": "104.171.202.134",
        "gpu": "A100",
        "memory": "40GB",
        "services": [],
    },
    "sophia-development": {
        "ip": "155.248.194.183",
        "gpu": "A10",
        "memory": "24GB",
        "services": [],
    },
}

# Cost information
INSTANCE_COSTS = {
    "GH200": {"hourly": 1.49, "daily": 35.76},
    "A6000": {"hourly": 0.80, "daily": 19.20},
    "A100": {"hourly": 1.29, "daily": 30.96},
    "A10": {"hourly": 0.75, "daily": 18.00},
}


class LambdaLabsMonitor:
    """Monitor Lambda Labs infrastructure health and performance"""

    def __init__(self):
        self.api_key = os.getenv("LAMBDA_API_KEY")
        if not self.api_key:
            logger.warning("LAMBDA_API_KEY not found in environment")

        self.results = {
            "timestamp": datetime.utcnow().isoformat(),
            "infrastructure": {},
            "services": {},
            "costs": {},
            "alerts": [],
        }

    def check_lambda_api(self) -> bool:
        """Check Lambda Labs API connectivity"""
        if not self.api_key:
            self.results["alerts"].append(
                {"level": "ERROR", "message": "Lambda Labs API key not configured"}
            )
            return False

        try:
            response = requests.get(
                "https://cloud.lambdalabs.com/api/v1/instances",
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=10,
            )

            if response.status_code == 200:
                instances = response.json().get("data", [])
                self.results["infrastructure"]["lambda_api"] = {
                    "status": "healthy",
                    "instance_count": len(instances),
                }
                return True
            else:
                self.results["alerts"].append(
                    {
                        "level": "ERROR",
                        "message": f"Lambda API returned status {response.status_code}",
                    }
                )
                return False

        except Exception as e:
            self.results["alerts"].append(
                {"level": "ERROR", "message": f"Lambda API connection failed: {e!s}"}
            )
            return False

    def check_ssh_connectivity(self, ip: str, name: str) -> bool:
        """Check SSH connectivity to an instance"""
        try:
            result = subprocess.run(
                [
                    "ssh",
                    "-o",
                    "ConnectTimeout=5",
                    "-o",
                    "StrictHostKeyChecking=no",
                    f"ubuntu@{ip}",
                    "echo 'OK'",
                ],
                capture_output=True,
                text=True,
                timeout=10,
                check=False,
            )

            return result.returncode == 0 and "OK" in result.stdout

        except Exception as e:
            logger.error(f"SSH check failed for {name}: {e}")
            return False

    def check_service_health(self, ip: str, port: int, endpoint: str) -> dict[str, Any]:
        """Check health of a specific service"""
        url = f"http://{ip}:{port}{endpoint}"

        try:
            start_time = time.time()
            response = requests.get(url, timeout=5)
            response_time = (time.time() - start_time) * 1000

            if response.status_code == 200:
                return {
                    "status": "healthy",
                    "response_time_ms": round(response_time, 2),
                    "data": response.json()
                    if response.headers.get("content-type", "").startswith(
                        "application/json"
                    )
                    else {},
                }
            else:
                return {
                    "status": "unhealthy",
                    "status_code": response.status_code,
                    "response_time_ms": round(response_time, 2),
                }

        except requests.exceptions.Timeout:
            return {"status": "timeout"}
        except requests.exceptions.ConnectionError:
            return {"status": "unreachable"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_instance_metrics(self, ip: str) -> dict[str, Any]:
        """Get system metrics from an instance via SSH"""
        metrics = {}

        try:
            # Memory usage
            mem_cmd = "free -b | grep Mem | awk '{print $2,$3}'"
            result = subprocess.run(
                [
                    "ssh",
                    "-o",
                    "ConnectTimeout=5",
                    "-o",
                    "StrictHostKeyChecking=no",
                    f"ubuntu@{ip}",
                    mem_cmd,
                ],
                capture_output=True,
                text=True,
                timeout=10,
                check=False,
            )

            if result.returncode == 0:
                total, used = map(int, result.stdout.strip().split())
                metrics["memory"] = {
                    "total_gb": round(total / (1024**3), 2),
                    "used_gb": round(used / (1024**3), 2),
                    "usage_percent": round((used / total) * 100, 2),
                }

            # CPU usage
            cpu_cmd = "top -bn1 | grep 'Cpu(s)' | sed 's/.*, *\\([0-9.]*\\)%* id.*/\\1/' | awk '{print 100 - $1}'"
            result = subprocess.run(
                [
                    "ssh",
                    "-o",
                    "ConnectTimeout=5",
                    "-o",
                    "StrictHostKeyChecking=no",
                    f"ubuntu@{ip}",
                    cpu_cmd,
                ],
                capture_output=True,
                text=True,
                timeout=10,
                check=False,
            )

            if result.returncode == 0:
                metrics["cpu_usage_percent"] = float(result.stdout.strip())

            # GPU usage (if available)
            gpu_cmd = "nvidia-smi --query-gpu=utilization.gpu,memory.used,memory.total --format=csv,noheader,nounits"
            result = subprocess.run(
                [
                    "ssh",
                    "-o",
                    "ConnectTimeout=5",
                    "-o",
                    "StrictHostKeyChecking=no",
                    f"ubuntu@{ip}",
                    gpu_cmd,
                ],
                capture_output=True,
                text=True,
                timeout=10,
                check=False,
            )

            if result.returncode == 0 and result.stdout.strip():
                gpu_data = result.stdout.strip().split(",")
                if len(gpu_data) >= 3:
                    metrics["gpu"] = {
                        "utilization_percent": float(gpu_data[0]),
                        "memory_used_mb": float(gpu_data[1]),
                        "memory_total_mb": float(gpu_data[2]),
                        "memory_usage_percent": round(
                            (float(gpu_data[1]) / float(gpu_data[2])) * 100, 2
                        ),
                    }

        except Exception as e:
            logger.error(f"Failed to get metrics for {ip}: {e}")

        return metrics

    def calculate_costs(self):
        """Calculate infrastructure costs"""
        total_daily = 0
        total_monthly = 0

        for name, config in INSTANCES.items():
            gpu_type = config["gpu"]
            if gpu_type in INSTANCE_COSTS:
                cost = INSTANCE_COSTS[gpu_type]
                self.results["costs"][name] = {
                    "gpu": gpu_type,
                    "hourly": cost["hourly"],
                    "daily": cost["daily"],
                    "monthly": round(cost["daily"] * 30, 2),
                }
                total_daily += cost["daily"]
                total_monthly += cost["daily"] * 30

        self.results["costs"]["total"] = {
            "daily": round(total_daily, 2),
            "monthly": round(total_monthly, 2),
            "yearly": round(total_monthly * 12, 2),
        }

        # Cost optimization alerts
        active_services = sum(
            1
            for inst in self.results["services"].values()
            if any(s.get("status") == "healthy" for s in inst.values())
        )

        if active_services < len(INSTANCES):
            utilization = (active_services / len(INSTANCES)) * 100
            self.results["alerts"].append(
                {
                    "level": "WARNING",
                    "message": f"Infrastructure utilization at {utilization:.0f}% - ${total_daily:.2f}/day for partial usage",
                }
            )

    def run_health_check(self):
        """Run complete health check"""
        logger.info("Starting Lambda Labs health check...")

        # Check Lambda API
        self.check_lambda_api()

        # Check each instance
        for name, config in INSTANCES.items():
            ip = config["ip"]
            instance_health = {
                "ip": ip,
                "gpu": config["gpu"],
                "memory": config["memory"],
                "ssh_accessible": False,
                "metrics": {},
                "services": {},
            }

            # Check SSH connectivity
            ssh_ok = self.check_ssh_connectivity(ip, name)
            instance_health["ssh_accessible"] = ssh_ok

            if ssh_ok:
                # Get system metrics
                instance_health["metrics"] = self.get_instance_metrics(ip)

                # Check services
                for service in config.get("services", []):
                    service_health = self.check_service_health(
                        ip, service["port"], service["endpoint"]
                    )
                    instance_health["services"][service["name"]] = service_health

                    # Add alerts for unhealthy services
                    if service_health["status"] != "healthy":
                        self.results["alerts"].append(
                            {
                                "level": "ERROR",
                                "message": f"Service {service['name']} on {name} is {service_health['status']}",
                            }
                        )
            else:
                self.results["alerts"].append(
                    {
                        "level": "ERROR",
                        "message": f"Instance {name} ({ip}) is not accessible via SSH",
                    }
                )

            self.results["services"][name] = instance_health

        # Calculate costs
        self.calculate_costs()

        # Add summary
        self.results["summary"] = {
            "total_instances": len(INSTANCES),
            "accessible_instances": sum(
                1 for i in self.results["services"].values() if i["ssh_accessible"]
            ),
            "healthy_services": sum(
                1
                for inst in self.results["services"].values()
                for svc in inst.get("services", {}).values()
                if svc.get("status") == "healthy"
            ),
            "total_alerts": len(self.results["alerts"]),
            "critical_alerts": len(
                [a for a in self.results["alerts"] if a["level"] == "ERROR"]
            ),
        }

        logger.info("Health check complete")
        return self.results

    def print_report(self):
        """Print formatted health report"""
        print("\n" + "=" * 60)
        print("LAMBDA LABS INFRASTRUCTURE HEALTH REPORT")
        print("=" * 60)
        print(f"Timestamp: {self.results['timestamp']}")
        print(
            f"Total Cost: ${self.results['costs']['total']['daily']}/day (${self.results['costs']['total']['monthly']}/month)"
        )
        print("")

        # Instance status
        print("INSTANCE STATUS:")
        for name, health in self.results["services"].items():
            status = "✅" if health["ssh_accessible"] else "❌"
            print(f"\n{status} {name} ({health['ip']}) - {health['gpu']} GPU")

            if health["ssh_accessible"]:
                # Metrics
                if "memory" in health["metrics"]:
                    mem = health["metrics"]["memory"]
                    print(
                        f"   Memory: {mem['used_gb']:.1f}/{mem['total_gb']:.1f} GB ({mem['usage_percent']:.1f}%)"
                    )

                if "cpu_usage_percent" in health["metrics"]:
                    print(f"   CPU: {health['metrics']['cpu_usage_percent']:.1f}%")

                if "gpu" in health["metrics"]:
                    gpu = health["metrics"]["gpu"]
                    print(
                        f"   GPU: {gpu['utilization_percent']:.1f}% utilization, "
                        f"{gpu['memory_used_mb']:.0f}/{gpu['memory_total_mb']:.0f} MB memory"
                    )

                # Services
                for svc_name, svc_health in health.get("services", {}).items():
                    svc_status = "✅" if svc_health["status"] == "healthy" else "❌"
                    if "response_time_ms" in svc_health:
                        print(
                            f"   {svc_status} {svc_name}: {svc_health['status']} ({svc_health['response_time_ms']:.0f}ms)"
                        )
                    else:
                        print(f"   {svc_status} {svc_name}: {svc_health['status']}")

        # Alerts
        if self.results["alerts"]:
            print("\nALERTS:")
            for alert in self.results["alerts"]:
                icon = "🔴" if alert["level"] == "ERROR" else "⚠️"
                print(f"{icon} [{alert['level']}] {alert['message']}")

        # Summary
        summary = self.results["summary"]
        print("\nSUMMARY:")
        print(
            f"Accessible Instances: {summary['accessible_instances']}/{summary['total_instances']}"
        )
        print(f"Healthy Services: {summary['healthy_services']}")
        print(f"Critical Alerts: {summary['critical_alerts']}")
        print("=" * 60)

        # Save to file
        filename = f"health_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, "w") as f:
            json.dump(self.results, f, indent=2)
        print(f"\nDetailed report saved to: {filename}")


def main():
    """Main entry point"""
    # Load environment if .env.lambda-labs exists
    if os.path.exists(".env.lambda-labs"):
        from dotenv import load_dotenv

        load_dotenv(".env.lambda-labs")

    monitor = LambdaLabsMonitor()
    monitor.run_health_check()
    monitor.print_report()

    # Exit with error code if critical alerts
    if monitor.results["summary"]["critical_alerts"] > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
