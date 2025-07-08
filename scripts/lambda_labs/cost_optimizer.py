#!/usr/bin/env python3
"""
Lambda Labs Cost Optimizer
Analyzes usage patterns and provides cost optimization recommendations
"""

import json
import logging
import os
import subprocess
from datetime import datetime
from typing import Optional

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Instance costs
INSTANCE_COSTS = {
    "GH200": {"hourly": 1.49, "daily": 35.76, "monthly": 1072.80},
    "A6000": {"hourly": 0.80, "daily": 19.20, "monthly": 576.00},
    "A100": {"hourly": 1.29, "daily": 30.96, "monthly": 928.80},
    "A10": {"hourly": 0.75, "daily": 18.00, "monthly": 540.00},
}

# Utilization thresholds
THRESHOLDS = {
    "gpu_idle": 15,  # GPU utilization below this is considered idle
    "gpu_optimal": 70,  # GPU utilization above this is optimal
    "memory_low": 20,  # Memory usage below this is underutilized
    "cost_burn_rate_alert": 120,  # Daily cost above this triggers alert
}


class CostOptimizer:
    """Optimize Lambda Labs infrastructure costs"""

    def __init__(self):
        self.instances = {
            "sophia-ai-core": {
                "ip": "192.222.58.232",
                "gpu": "GH200",
                "purpose": "Primary AI Core",
                "always_on": True,
            },
            "sophia-mcp-orchestrator": {
                "ip": "104.171.202.117",
                "gpu": "A6000",
                "purpose": "MCP Orchestration",
                "always_on": True,
            },
            "sophia-data-pipeline": {
                "ip": "104.171.202.134",
                "gpu": "A100",
                "purpose": "Data Processing",
                "always_on": False,
            },
            "sophia-development": {
                "ip": "155.248.194.183",
                "gpu": "A10",
                "purpose": "Development",
                "always_on": False,
                "business_hours_only": True,
            },
        }

        self.metrics = {}
        self.recommendations = []

    def get_gpu_utilization(self, ip: str) -> Optional[float]:
        """Get current GPU utilization for an instance"""
        try:
            cmd = [
                "ssh",
                "-o",
                "ConnectTimeout=5",
                "-o",
                "StrictHostKeyChecking=no",
                f"ubuntu@{ip}",
                "nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits",
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10, check=False)

            if result.returncode == 0 and result.stdout.strip():
                return float(result.stdout.strip())

        except Exception as e:
            logger.error(f"Failed to get GPU utilization for {ip}: {e}")

        return None

    def get_memory_usage(self, ip: str) -> Optional[dict[str, float]]:
        """Get memory usage for an instance"""
        try:
            cmd = [
                "ssh",
                "-o",
                "ConnectTimeout=5",
                "-o",
                "StrictHostKeyChecking=no",
                f"ubuntu@{ip}",
                "free -b | grep Mem | awk '{print $2,$3}'",
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10, check=False)

            if result.returncode == 0 and result.stdout.strip():
                total, used = map(int, result.stdout.strip().split())
                return {
                    "total_gb": total / (1024**3),
                    "used_gb": used / (1024**3),
                    "usage_percent": (used / total) * 100,
                }

        except Exception as e:
            logger.error(f"Failed to get memory usage for {ip}: {e}")

        return None

    def get_service_status(self, ip: str, port: int) -> bool:
        """Check if a service is running on an instance"""
        try:
            import requests

            response = requests.get(f"http://{ip}:{port}/health", timeout=5)
            return response.status_code == 200
        except:
            return False

    def collect_metrics(self):
        """Collect metrics from all instances"""
        logger.info("Collecting metrics from Lambda Labs instances...")

        for name, config in self.instances.items():
            ip = config["ip"]
            gpu_type = config["gpu"]

            metrics = {
                "gpu_utilization": self.get_gpu_utilization(ip),
                "memory": self.get_memory_usage(ip),
                "services": {
                    "backend": self.get_service_status(ip, 8000)
                    if name == "sophia-ai-core"
                    else False,
                    "mcp": self.get_service_status(ip, 8001)
                    if name == "sophia-mcp-orchestrator"
                    else False,
                },
                "cost": INSTANCE_COSTS[gpu_type],
            }

            self.metrics[name] = metrics

            # Log current status
            gpu_util = metrics["gpu_utilization"]
            if gpu_util is not None:
                logger.info(
                    f"{name}: GPU {gpu_util:.1f}%, "
                    f"Memory {metrics['memory']['usage_percent']:.1f}% if metrics['memory'] else 'N/A', "
                    f"Cost ${metrics['cost']['daily']}/day"
                )
            else:
                logger.warning(f"{name}: Unable to collect metrics")

    def analyze_utilization(self):
        """Analyze utilization patterns and generate recommendations"""
        logger.info("\nAnalyzing utilization patterns...")

        total_daily_cost = 0
        underutilized_instances = []
        idle_instances = []

        for name, metrics in self.metrics.items():
            config = self.instances[name]
            daily_cost = metrics["cost"]["daily"]
            total_daily_cost += daily_cost

            gpu_util = metrics.get("gpu_utilization")
            memory = metrics.get("memory", {})

            # Check for idle instances
            if gpu_util is not None and gpu_util < THRESHOLDS["gpu_idle"]:
                if not config.get("always_on"):
                    idle_instances.append(
                        {
                            "name": name,
                            "gpu_util": gpu_util,
                            "daily_cost": daily_cost,
                            "potential_savings": daily_cost
                            * 0.7,  # Assume 70% time savings
                        }
                    )
                else:
                    underutilized_instances.append(
                        {"name": name, "gpu_util": gpu_util, "daily_cost": daily_cost}
                    )

            # Check memory utilization
            if memory and memory.get("usage_percent", 100) < THRESHOLDS["memory_low"]:
                self.recommendations.append(
                    {
                        "type": "memory_underutilized",
                        "instance": name,
                        "current": f"{memory['usage_percent']:.1f}%",
                        "recommendation": "Consider downsizing instance or running more workloads",
                    }
                )

        # Cost burn rate alert
        if total_daily_cost > THRESHOLDS["cost_burn_rate_alert"]:
            self.recommendations.append(
                {
                    "type": "high_burn_rate",
                    "current": f"${total_daily_cost:.2f}/day",
                    "threshold": f"${THRESHOLDS['cost_burn_rate_alert']}/day",
                    "recommendation": "Review instance usage and implement auto-scaling",
                }
            )

        # Idle instance recommendations
        if idle_instances:
            total_potential_savings = sum(
                i["potential_savings"] for i in idle_instances
            )
            self.recommendations.append(
                {
                    "type": "idle_instances",
                    "instances": [i["name"] for i in idle_instances],
                    "potential_savings": f"${total_potential_savings:.2f}/day",
                    "recommendation": "Implement auto-shutdown for idle instances",
                }
            )

        # Development instance optimization
        dev_instance = self.metrics.get("sophia-development", {})
        if dev_instance and self.instances["sophia-development"].get(
            "business_hours_only"
        ):
            # Assume 8 hours/day, 5 days/week usage
            current_cost = dev_instance["cost"]["monthly"]
            optimized_cost = current_cost * (8 / 24) * (5 / 7)
            savings = current_cost - optimized_cost

            self.recommendations.append(
                {
                    "type": "business_hours_optimization",
                    "instance": "sophia-development",
                    "current_cost": f"${current_cost:.2f}/month",
                    "optimized_cost": f"${optimized_cost:.2f}/month",
                    "potential_savings": f"${savings:.2f}/month",
                    "recommendation": "Implement business hours auto-scheduling",
                }
            )

        return {
            "total_daily_cost": total_daily_cost,
            "total_monthly_cost": total_daily_cost * 30,
            "underutilized_instances": underutilized_instances,
            "idle_instances": idle_instances,
        }

    def generate_auto_scaling_script(self):
        """Generate auto-scaling script based on analysis"""
        script = """#!/bin/bash
# Lambda Labs Auto-Scaling Script
# Generated: {timestamp}

# Configuration
GPU_IDLE_THRESHOLD={gpu_idle}
CHECK_INTERVAL=300  # 5 minutes

# Function to check GPU utilization
check_gpu_utilization() {
    local ip=$1
    ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no ubuntu@$ip \\
        "nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits" 2>/dev/null
}

# Function to stop instance containers
stop_instance_services() {
    local ip=$1
    local name=$2
    echo "Stopping services on $name ($ip)..."
    ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no ubuntu@$ip \\
        "docker ps -q | xargs -r docker stop"
}

# Main monitoring loop
while true; do
    echo "Checking instance utilization..."

    # Check non-critical instances
    for instance in "104.171.202.134:sophia-data-pipeline" "155.248.194.183:sophia-development"; do
        ip=$(echo $instance | cut -d: -f1)
        name=$(echo $instance | cut -d: -f2)

        util=$(check_gpu_utilization $ip)
        if [[ -n "$util" && $(echo "$util < $GPU_IDLE_THRESHOLD" | bc) -eq 1 ]]; then
            echo "$name GPU utilization: $util% - below threshold"
            # stop_instance_services $ip $name  # Uncomment to enable auto-stop
        fi
    done

    sleep $CHECK_INTERVAL
done
""".format(
            timestamp=datetime.now().isoformat(), gpu_idle=THRESHOLDS["gpu_idle"]
        )

        with open("auto_scaling.sh", "w") as f:
            f.write(script)
        os.chmod("auto_scaling.sh", 0o755)

        logger.info("Generated auto_scaling.sh script")

    def generate_report(self):
        """Generate cost optimization report"""
        analysis = self.analyze_utilization()

        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_daily_cost": analysis["total_daily_cost"],
                "total_monthly_cost": analysis["total_monthly_cost"],
                "total_yearly_cost": analysis["total_monthly_cost"] * 12,
                "recommendation_count": len(self.recommendations),
            },
            "instance_metrics": self.metrics,
            "recommendations": self.recommendations,
            "potential_savings": {
                "immediate": sum(
                    r.get("potential_savings", 0)
                    for r in self.recommendations
                    if isinstance(r.get("potential_savings"), (int, float))
                ),
                "monthly": sum(
                    float(
                        r.get("potential_savings", "0")
                        .replace("$", "")
                        .replace("/month", "")
                    )
                    for r in self.recommendations
                    if "/month" in str(r.get("potential_savings", ""))
                ),
            },
        }

        # Save report
        filename = (
            f"cost_optimization_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(filename, "w") as f:
            json.dump(report, f, indent=2)

        # Print summary
        print("\n" + "=" * 60)
        print("LAMBDA LABS COST OPTIMIZATION REPORT")
        print("=" * 60)
        print("Current Costs:")
        print(f"  Daily: ${analysis['total_daily_cost']:.2f}")
        print(f"  Monthly: ${analysis['total_monthly_cost']:.2f}")
        print(f"  Yearly: ${analysis['total_monthly_cost'] * 12:.2f}")

        if self.recommendations:
            print(f"\n{len(self.recommendations)} Optimization Recommendations:")
            for i, rec in enumerate(self.recommendations, 1):
                print(f"\n{i}. {rec['type'].replace('_', ' ').title()}")
                print(f"   Recommendation: {rec['recommendation']}")
                if "potential_savings" in rec:
                    print(f"   Potential Savings: {rec['potential_savings']}")

        print(f"\nDetailed report saved to: {filename}")
        print("\nTo implement auto-scaling, review and deploy: auto_scaling.sh")

        return report


def main():
    """Main entry point"""
    # Load environment if available
    if os.path.exists(".env.lambda-labs"):
        from dotenv import load_dotenv

        load_dotenv(".env.lambda-labs")

    optimizer = CostOptimizer()
    optimizer.collect_metrics()
    report = optimizer.generate_report()
    optimizer.generate_auto_scaling_script()

    # Exit with error if burn rate exceeded
    if report["summary"]["total_daily_cost"] > THRESHOLDS["cost_burn_rate_alert"]:
        logger.warning(
            f"⚠️  Daily cost (${report['summary']['total_daily_cost']:.2f}) "
            f"exceeds threshold (${THRESHOLDS['cost_burn_rate_alert']})"
        )
        return 1

    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
