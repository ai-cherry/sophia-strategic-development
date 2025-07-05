#!/usr/bin/env python3
"""Comprehensive monitoring and testing for Sophia AI infrastructure."""

import asyncio
import statistics
import time
from datetime import datetime
from typing import Any

import requests


class SophiaInfrastructureMonitor:
    """Comprehensive monitoring for all Sophia AI services."""

    def __init__(self):
        self.services = {
            "api_gateway": {"url": "http://localhost:8000", "name": "API Gateway"},
            "ai_memory": {"url": "http://localhost:9001", "name": "AI Memory MCP"},
            "codacy": {"url": "http://localhost:3008", "name": "Codacy MCP"},
            "github": {"url": "http://localhost:9003", "name": "GitHub MCP"},
            "linear": {"url": "http://localhost:9004", "name": "Linear MCP"},
        }

        self.metrics = {service: [] for service in self.services}
        self.test_results = {service: [] for service in self.services}

    async def check_service_health(self, service_key: str) -> dict[str, Any]:
        """Check health of a specific service."""
        service = self.services[service_key]
        start_time = time.time()

        try:
            response = requests.get(f"{service['url']}/health", timeout=5)
            response_time = (time.time() - start_time) * 1000  # ms

            if response.status_code == 200:
                data = response.json()
                return {
                    "service": service_key,
                    "name": service["name"],
                    "status": "healthy",
                    "response_time": response_time,
                    "timestamp": datetime.now().isoformat(),
                    "details": data,
                }
            else:
                return {
                    "service": service_key,
                    "name": service["name"],
                    "status": "unhealthy",
                    "response_time": response_time,
                    "timestamp": datetime.now().isoformat(),
                    "error": f"HTTP {response.status_code}",
                }

        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return {
                "service": service_key,
                "name": service["name"],
                "status": "error",
                "response_time": response_time,
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
            }

    async def test_service_functionality(self, service_key: str) -> dict[str, Any]:
        """Test specific functionality of each service."""
        service = self.services[service_key]

        try:
            if service_key == "ai_memory":
                # Test memory storage and recall
                test_memory = {
                    "content": f"Test memory at {datetime.now().isoformat()}",
                    "category": "test",
                    "importance_score": 0.5,
                }

                # Store memory
                store_response = requests.post(
                    f"{service['url']}/api/v1/memory/store", json=test_memory, timeout=5
                )

                if store_response.status_code != 200:
                    return {"status": "failed", "error": "Memory storage failed"}

                # Recall memory
                recall_response = requests.post(
                    f"{service['url']}/api/v1/memory/recall",
                    json={"query": "test"},
                    timeout=5,
                )

                if recall_response.status_code != 200:
                    return {"status": "failed", "error": "Memory recall failed"}

                return {"status": "passed", "test": "memory_storage_recall"}

            elif service_key == "codacy":
                # Test code analysis
                test_code = {
                    "code": "def test_function():\n    return 'Hello World'",
                    "filename": "test.py",
                }

                response = requests.post(
                    f"{service['url']}/api/v1/analyze/code", json=test_code, timeout=5
                )

                if response.status_code != 200:
                    return {"status": "failed", "error": "Code analysis failed"}

                data = response.json()
                if "quality_score" not in data:
                    return {"status": "failed", "error": "Invalid response format"}

                return {
                    "status": "passed",
                    "test": "code_analysis",
                    "quality_score": data["quality_score"],
                }

            elif service_key == "github":
                # Test repository listing
                response = requests.get(
                    f"{service['url']}/api/v1/repositories", timeout=5
                )

                if response.status_code != 200:
                    return {"status": "failed", "error": "Repository listing failed"}

                data = response.json()
                if "repositories" not in data:
                    return {"status": "failed", "error": "Invalid response format"}

                return {
                    "status": "passed",
                    "test": "repository_listing",
                    "repo_count": data["count"],
                }

            elif service_key == "linear":
                # Test project health
                response = requests.get(f"{service['url']}/api/v1/health", timeout=5)

                if response.status_code != 200:
                    return {"status": "failed", "error": "Project health failed"}

                data = response.json()
                if "overall_health" not in data:
                    return {"status": "failed", "error": "Invalid response format"}

                return {
                    "status": "passed",
                    "test": "project_health",
                    "health_score": data["overall_health"],
                }

            elif service_key == "api_gateway":
                # Test basic health
                response = requests.get(f"{service['url']}/health", timeout=5)

                if response.status_code != 200:
                    return {"status": "failed", "error": "Health check failed"}

                return {"status": "passed", "test": "health_check"}

            else:
                return {"status": "failed", "error": f"Unknown service: {service_key}"}

        except Exception as e:
            return {"status": "failed", "error": str(e)}

    async def run_comprehensive_test_cycle(self) -> dict[str, Any]:
        """Run a complete test cycle across all services."""
        cycle_start = time.time()
        results = {}

        # Health checks
        health_tasks = [self.check_service_health(service) for service in self.services]
        health_results = await asyncio.gather(*health_tasks)

        # Functionality tests
        functionality_results = []
        for service_key in self.services:
            func_result = await self.test_service_functionality(service_key)
            func_result["service"] = service_key
            functionality_results.append(func_result)

        # Compile results
        healthy_services = [r for r in health_results if r["status"] == "healthy"]
        passed_tests = [r for r in functionality_results if r["status"] == "passed"]

        cycle_time = (time.time() - cycle_start) * 1000

        results = {
            "timestamp": datetime.now().isoformat(),
            "cycle_time_ms": cycle_time,
            "health_summary": {
                "total_services": len(self.services),
                "healthy_services": len(healthy_services),
                "health_percentage": (len(healthy_services) / len(self.services)) * 100,
            },
            "functionality_summary": {
                "total_tests": len(functionality_results),
                "passed_tests": len(passed_tests),
                "pass_percentage": (len(passed_tests) / len(functionality_results))
                * 100,
            },
            "health_details": health_results,
            "functionality_details": functionality_results,
            "response_times": {
                r["service"]: r["response_time"] for r in health_results
            },
            "average_response_time": statistics.mean(
                [r["response_time"] for r in health_results]
            ),
        }

        # Store metrics
        for result in health_results:
            self.metrics[result["service"]].append(
                {
                    "timestamp": result["timestamp"],
                    "response_time": result["response_time"],
                    "status": result["status"],
                }
            )

        # Store test results
        for result in functionality_results:
            self.test_results[result["service"]].append(
                {
                    "timestamp": datetime.now().isoformat(),
                    "status": result["status"],
                    "test": result.get("test", "unknown"),
                }
            )

        return results

    def print_results(self, results: dict[str, Any]):
        """Print formatted results."""

        # Health summary
        results["health_summary"]

        # Functionality summary
        results["functionality_summary"]

        # Response times

        # Service details
        for detail in results["health_details"]:
            "✅" if detail["status"] == "healthy" else "❌"

        # Functionality details
        for detail in results["functionality_details"]:
            "✅" if detail["status"] == "passed" else "❌"
            detail.get("test", "unknown")

            # Additional test-specific info
            if (
                "quality_score" in detail
                or "repo_count" in detail
                or "health_score" in detail
            ):
                pass

    def get_performance_trends(self) -> dict[str, Any]:
        """Analyze performance trends."""
        trends = {}

        for service, metrics in self.metrics.items():
            if len(metrics) < 2:
                continue

            recent_metrics = metrics[-10:]  # Last 10 measurements
            response_times = [m["response_time"] for m in recent_metrics]

            trends[service] = {
                "average_response_time": statistics.mean(response_times),
                "min_response_time": min(response_times),
                "max_response_time": max(response_times),
                "response_time_std": (
                    statistics.stdev(response_times) if len(response_times) > 1 else 0
                ),
                "measurement_count": len(recent_metrics),
                "uptime_percentage": (
                    len([m for m in recent_metrics if m["status"] == "healthy"])
                    / len(recent_metrics)
                )
                * 100,
            }

        return trends

    async def continuous_monitoring(
        self, duration_minutes: int = 5, interval_seconds: int = 30
    ):
        """Run continuous monitoring for specified duration."""

        end_time = time.time() + (duration_minutes * 60)
        cycle_count = 0

        while time.time() < end_time:
            cycle_count += 1

            results = await self.run_comprehensive_test_cycle()
            self.print_results(results)

            # Show trends every 5 cycles
            if cycle_count % 5 == 0:
                trends = self.get_performance_trends()
                if trends:
                    for _service, _trend in trends.items():
                        pass

            if time.time() < end_time:
                await asyncio.sleep(interval_seconds)

        return self.get_final_report()

    def get_final_report(self) -> dict[str, Any]:
        """Generate final monitoring report."""
        total_measurements = sum(len(metrics) for metrics in self.metrics.values())

        return {
            "monitoring_summary": {
                "total_cycles": (
                    max(len(metrics) for metrics in self.metrics.values())
                    if self.metrics
                    else 0
                ),
                "total_measurements": total_measurements,
                "services_monitored": len(self.services),
            },
            "performance_trends": self.get_performance_trends(),
            "service_reliability": {
                service: {
                    "total_checks": len(self.metrics[service]),
                    "successful_checks": len(
                        [m for m in self.metrics[service] if m["status"] == "healthy"]
                    ),
                    "uptime_percentage": (
                        (
                            len(
                                [
                                    m
                                    for m in self.metrics[service]
                                    if m["status"] == "healthy"
                                ]
                            )
                            / len(self.metrics[service])
                        )
                        * 100
                        if self.metrics[service]
                        else 0
                    ),
                }
                for service in self.services
            },
        }


async def main():
    """Main monitoring function."""
    monitor = SophiaInfrastructureMonitor()

    # Run single test cycle first
    results = await monitor.run_comprehensive_test_cycle()
    monitor.print_results(results)

    # Ask user for continuous monitoring

    # For automated execution, run a short continuous test
    await monitor.continuous_monitoring(duration_minutes=2, interval_seconds=20)


if __name__ == "__main__":
    asyncio.run(main())
