#!/usr/bin/env python3
"""
Docker Swarm Resource Optimizer
Analyzes actual resource usage and provides optimization recommendations
"""

import json
import statistics
import time
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

import docker


class SwarmResourceOptimizer:
    def __init__(self):
        self.client = docker.from_env()
        self.recommendations = []

    def calculate_cpu_percent(self, stats: dict) -> float:
        """Calculate CPU percentage from Docker stats"""
        cpu_delta = (
            stats["cpu_stats"]["cpu_usage"]["total_usage"]
            - stats["precpu_stats"]["cpu_usage"]["total_usage"]
        )
        system_delta = (
            stats["cpu_stats"]["system_cpu_usage"]
            - stats["precpu_stats"]["system_cpu_usage"]
        )

        if system_delta > 0 and cpu_delta > 0:
            cpu_percent = (cpu_delta / system_delta) * 100.0
            return cpu_percent
        return 0.0

    def analyze_service_usage(self, service_name: str, sample_count: int = 10) -> dict:
        """Analyze actual resource usage over time"""
        containers = self.client.containers.list(
            filters={"label": f"com.docker.swarm.service.name={service_name}"}
        )

        if not containers:
            return None

        cpu_samples = []
        memory_samples = []


        for i in range(sample_count):
            for container in containers:
                try:
                    stats = container.stats(stream=False)
                    cpu_percent = self.calculate_cpu_percent(stats)
                    memory_mb = stats["memory_stats"]["usage"] / (1024 * 1024)

                    cpu_samples.append(cpu_percent)
                    memory_samples.append(memory_mb)
                except Exception:
                    pass

            if i < sample_count - 1:
                time.sleep(2)  # Wait between samples

        if not cpu_samples or not memory_samples:
            return None

        return {
            "service": service_name,
            "cpu_avg": statistics.mean(cpu_samples),
            "cpu_p95": statistics.quantile(cpu_samples, 0.95),
            "cpu_max": max(cpu_samples),
            "memory_avg_mb": statistics.mean(memory_samples),
            "memory_p95_mb": statistics.quantile(memory_samples, 0.95),
            "memory_max_mb": max(memory_samples),
            "sample_count": len(cpu_samples),
            "recommendation": self.generate_recommendation(
                service_name, cpu_samples, memory_samples
            ),
        }

    def generate_recommendation(
        self, service_name: str, cpu_samples: list[float], memory_samples: list[float]
    ) -> dict:
        """Generate resource allocation recommendations"""
        cpu_p95 = statistics.quantile(cpu_samples, 0.95)
        memory_p95_mb = statistics.quantile(memory_samples, 0.95)

        # Get current limits from service spec
        try:
            service = self.client.services.get(service_name)
            spec = service.attrs["Spec"]["TaskTemplate"]["Resources"]

            current_cpu_limit = spec.get("Limits", {}).get("NanoCPUs", 0) / 1e9
            current_memory_limit_mb = spec.get("Limits", {}).get("MemoryBytes", 0) / (
                1024 * 1024
            )

            current_cpu_reservation = (
                spec.get("Reservations", {}).get("NanoCPUs", 0) / 1e9
            )
            current_memory_reservation_mb = spec.get("Reservations", {}).get(
                "MemoryBytes", 0
            ) / (1024 * 1024)
        except:
            current_cpu_limit = 0
            current_memory_limit_mb = 0
            current_cpu_reservation = 0
            current_memory_reservation_mb = 0

        # Calculate recommended values with safety margins
        recommended_cpu_limit = max(0.5, (cpu_p95 / 100) * 1.5)  # 50% margin
        recommended_memory_limit_mb = max(256, memory_p95_mb * 1.3)  # 30% margin

        recommended_cpu_reservation = max(0.1, (cpu_p95 / 100) * 0.8)  # 80% of P95
        recommended_memory_reservation_mb = max(128, memory_p95_mb * 0.7)  # 70% of P95

        # Round to sensible values
        recommended_cpu_limit = round(recommended_cpu_limit * 4) / 4  # Quarter CPUs
        recommended_memory_limit_mb = (
            round(recommended_memory_limit_mb / 128) * 128
        )  # 128MB increments

        return {
            "current": {
                "cpu_limit": current_cpu_limit,
                "memory_limit_mb": current_memory_limit_mb,
                "cpu_reservation": current_cpu_reservation,
                "memory_reservation_mb": current_memory_reservation_mb,
            },
            "recommended": {
                "cpu_limit": recommended_cpu_limit,
                "memory_limit_mb": recommended_memory_limit_mb,
                "cpu_reservation": recommended_cpu_reservation,
                "memory_reservation_mb": recommended_memory_reservation_mb,
            },
            "savings": {
                "cpu_reduction": max(0, current_cpu_limit - recommended_cpu_limit),
                "memory_reduction_mb": max(
                    0, current_memory_limit_mb - recommended_memory_limit_mb
                ),
            },
        }

    def analyze_all_services(self) -> list[dict]:
        """Analyze all services in the Swarm"""
        services = self.client.services.list()
        results = []

        for service in services:
            service_name = service.name

            usage = self.analyze_service_usage(service_name)
            if usage:
                results.append(usage)

        return results

    def generate_update_commands(self, results: list[dict]) -> list[str]:
        """Generate Docker commands to update resource allocations"""
        commands = []

        for result in results:
            service_name = result["service"]
            rec = result["recommendation"]["recommended"]

            cpu_limit = rec["cpu_limit"]
            memory_limit_mb = rec["memory_limit_mb"]
            cpu_reservation = rec["cpu_reservation"]
            memory_reservation_mb = rec["memory_reservation_mb"]

            cmd = (
                f"docker service update {service_name} "
                f"--limit-cpu {cpu_limit} "
                f"--limit-memory {int(memory_limit_mb)}M "
                f"--reserve-cpu {cpu_reservation} "
                f"--reserve-memory {int(memory_reservation_mb)}M"
            )

            commands.append(cmd)

        return commands

    def print_report(self, results: list[dict]):
        """Print a formatted report of the analysis"""

        total_cpu_savings = 0
        total_memory_savings = 0

        for result in results:

            rec = result["recommendation"]


            if (
                rec["savings"]["cpu_reduction"] > 0
                or rec["savings"]["memory_reduction_mb"] > 0
            ):

                total_cpu_savings += rec["savings"]["cpu_reduction"]
                total_memory_savings += rec["savings"]["memory_reduction_mb"]


    def save_report(
        self, results: list[dict], filename: str = "resource_optimization_report.json"
    ):
        """Save the analysis results to a JSON file"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "services": results,
            "commands": self.generate_update_commands(results),
        }

        with open(filename, "w") as f:
            json.dump(report, f, indent=2)



def main():
    """Main execution function"""

    optimizer = SwarmResourceOptimizer()

    # Analyze all services
    results = optimizer.analyze_all_services()

    if not results:
        return

    # Print report
    optimizer.print_report(results)

    # Generate update commands
    commands = optimizer.generate_update_commands(results)

    for cmd in commands:
        pass

    # Save report
    optimizer.save_report(results)



if __name__ == "__main__":
    main()
