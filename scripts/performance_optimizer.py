#!/usr/bin/env python3
"""Performance optimization and adjustment for Sophia AI MCP servers."""

import asyncio
import json
import time
from datetime import datetime
from typing import Any

import requests


class SophiaPerformanceOptimizer:
    """Performance optimization for Sophia AI infrastructure."""

    def __init__(self):
        self.services = {
            "api_gateway": {"url": "http://localhost:8000", "name": "API Gateway"},
            "ai_memory": {"url": "http://localhost:9001", "name": "AI Memory MCP"},
            "codacy": {"url": "http://localhost:3008", "name": "Codacy MCP"},
            "github": {"url": "http://localhost:9003", "name": "GitHub MCP"},
            "linear": {"url": "http://localhost:9004", "name": "Linear MCP"},
        }

        self.performance_metrics = {}

    async def run_performance_benchmark(self) -> dict[str, Any]:
        """Run comprehensive performance benchmarks."""
        print("🚀 Running Performance Benchmarks...")
        print("=" * 50)

        results = {}

        for service_key, service in self.services.items():
            print(f"\n🔧 Testing {service['name']}...")

            # Test response time under load
            response_times = []
            errors = 0

            for _i in range(10):  # 10 rapid requests
                start_time = time.time()
                try:
                    response = requests.get(f"{service['url']}/health", timeout=5)
                    response_time = (time.time() - start_time) * 1000

                    if response.status_code == 200:
                        response_times.append(response_time)
                    else:
                        errors += 1

                except Exception:
                    errors += 1

                await asyncio.sleep(0.1)  # Small delay between requests

            if response_times:
                avg_response = sum(response_times) / len(response_times)
                min_response = min(response_times)
                max_response = max(response_times)

                # Performance grade
                if avg_response < 5:
                    grade = "A+"
                elif avg_response < 10:
                    grade = "A"
                elif avg_response < 25:
                    grade = "B"
                elif avg_response < 50:
                    grade = "C"
                else:
                    grade = "D"

                results[service_key] = {
                    "name": service["name"],
                    "avg_response_time": avg_response,
                    "min_response_time": min_response,
                    "max_response_time": max_response,
                    "error_rate": (errors / 10) * 100,
                    "performance_grade": grade,
                    "requests_tested": 10,
                    "successful_requests": len(response_times),
                }

                print(f"  ✅ Avg: {avg_response:.1f}ms, Grade: {grade}")
            else:
                results[service_key] = {
                    "name": service["name"],
                    "error": "All requests failed",
                    "error_rate": 100,
                    "performance_grade": "F",
                }
                print("  ❌ All requests failed")

        return results

    def analyze_performance_bottlenecks(
        self, results: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Analyze performance results and identify bottlenecks."""
        bottlenecks = []
        recommendations = []

        print("\n🔍 Performance Analysis:")
        print("=" * 50)

        for service_key, metrics in results.items():
            if "error" in metrics:
                bottlenecks.append(
                    {
                        "service": service_key,
                        "issue": "Service unavailable",
                        "severity": "critical",
                        "recommendation": "Check service health and restart if needed",
                    }
                )
                continue

            avg_time = metrics["avg_response_time"]
            error_rate = metrics["error_rate"]
            grade = metrics["performance_grade"]

            print(f"\n📊 {metrics['name']}:")
            print(f"   Response Time: {avg_time:.1f}ms (Grade: {grade})")
            print(f"   Error Rate: {error_rate:.1f}%")

            # Identify issues
            if avg_time > 50:
                bottlenecks.append(
                    {
                        "service": service_key,
                        "issue": f"High response time ({avg_time:.1f}ms)",
                        "severity": "high",
                        "recommendation": "Optimize processing logic or add caching",
                    }
                )
            elif avg_time > 25:
                bottlenecks.append(
                    {
                        "service": service_key,
                        "issue": f"Moderate response time ({avg_time:.1f}ms)",
                        "severity": "medium",
                        "recommendation": "Consider optimization opportunities",
                    }
                )

            if error_rate > 5:
                bottlenecks.append(
                    {
                        "service": service_key,
                        "issue": f"High error rate ({error_rate:.1f}%)",
                        "severity": "high",
                        "recommendation": "Investigate error causes and improve error handling",
                    }
                )

            # Generate recommendations
            if grade in ["A+", "A"]:
                recommendations.append(f"✅ {metrics['name']}: Excellent performance")
            elif grade == "B":
                recommendations.append(
                    f"🟡 {metrics['name']}: Good performance, minor optimizations possible"
                )
            elif grade == "C":
                recommendations.append(
                    f"🟠 {metrics['name']}: Moderate performance, optimization recommended"
                )
            else:
                recommendations.append(
                    f"🔴 {metrics['name']}: Poor performance, immediate optimization needed"
                )

        if not bottlenecks:
            print("\n🎉 No significant performance bottlenecks detected!")
        else:
            print(f"\n⚠️ Found {len(bottlenecks)} performance issues:")
            for bottleneck in bottlenecks:
                severity_icon = (
                    "🔴"
                    if bottleneck["severity"] == "critical"
                    else "🟠" if bottleneck["severity"] == "high" else "🟡"
                )
                print(
                    f"  {severity_icon} {bottleneck['service']}: {bottleneck['issue']}"
                )
                print(f"     💡 {bottleneck['recommendation']}")

        print("\n📋 Recommendations:")
        for rec in recommendations:
            print(f"  {rec}")

        return bottlenecks

    async def test_load_handling(self) -> dict[str, Any]:
        """Test how services handle concurrent load."""
        print("\n🏋️ Load Testing (Concurrent Requests)...")
        print("=" * 50)

        results = {}

        for service_key, service in self.services.items():
            print(f"\n🔧 Load testing {service['name']}...")

            # Create 20 concurrent requests
            async def make_request():
                start_time = time.time()
                try:
                    response = requests.get(f"{service['url']}/health", timeout=10)
                    response_time = (time.time() - start_time) * 1000
                    return {
                        "success": response.status_code == 200,
                        "time": response_time,
                    }
                except Exception as e:
                    response_time = (time.time() - start_time) * 1000
                    return {"success": False, "time": response_time, "error": str(e)}

            # Run concurrent requests
            start_time = time.time()
            tasks = [make_request() for _ in range(20)]
            responses = await asyncio.gather(*tasks)
            total_time = time.time() - start_time

            successful = [r for r in responses if r["success"]]
            failed = [r for r in responses if not r["success"]]

            if successful:
                avg_response = sum(r["time"] for r in successful) / len(successful)
                throughput = len(successful) / total_time

                results[service_key] = {
                    "name": service["name"],
                    "total_requests": 20,
                    "successful_requests": len(successful),
                    "failed_requests": len(failed),
                    "success_rate": (len(successful) / 20) * 100,
                    "avg_response_time": avg_response,
                    "throughput_rps": throughput,
                    "total_test_time": total_time,
                }

                print(f"  ✅ {len(successful)}/20 successful ({throughput:.1f} req/s)")
            else:
                results[service_key] = {
                    "name": service["name"],
                    "total_requests": 20,
                    "successful_requests": 0,
                    "failed_requests": 20,
                    "success_rate": 0,
                    "error": "All concurrent requests failed",
                }
                print("  ❌ All concurrent requests failed")

        return results

    def generate_optimization_plan(
        self, perf_results: dict[str, Any], load_results: dict[str, Any]
    ) -> dict[str, Any]:
        """Generate comprehensive optimization plan."""
        plan = {
            "timestamp": datetime.now().isoformat(),
            "overall_health": "excellent",
            "optimizations": [],
            "monitoring_recommendations": [],
            "infrastructure_recommendations": [],
        }

        # Analyze overall performance
        avg_response_times = []
        for service_key, metrics in perf_results.items():
            if "avg_response_time" in metrics:
                avg_response_times.append(metrics["avg_response_time"])

        if avg_response_times:
            overall_avg = sum(avg_response_times) / len(avg_response_times)

            if overall_avg < 10:
                plan["overall_health"] = "excellent"
            elif overall_avg < 25:
                plan["overall_health"] = "good"
            elif overall_avg < 50:
                plan["overall_health"] = "fair"
            else:
                plan["overall_health"] = "poor"

        # Generate specific optimizations
        for service_key, metrics in perf_results.items():
            if "avg_response_time" in metrics:
                avg_time = metrics["avg_response_time"]

                if avg_time > 25:
                    plan["optimizations"].append(
                        {
                            "service": service_key,
                            "type": "response_time",
                            "current_value": avg_time,
                            "target_value": 10,
                            "actions": [
                                "Add response caching",
                                "Optimize database queries",
                                "Review async operations",
                            ],
                        }
                    )

        # Load testing recommendations
        for service_key, metrics in load_results.items():
            if "success_rate" in metrics and metrics["success_rate"] < 95:
                plan["optimizations"].append(
                    {
                        "service": service_key,
                        "type": "reliability",
                        "current_value": metrics["success_rate"],
                        "target_value": 99,
                        "actions": [
                            "Implement connection pooling",
                            "Add circuit breaker pattern",
                            "Increase timeout values",
                        ],
                    }
                )

        # General recommendations
        plan["monitoring_recommendations"] = [
            "Set up automated health monitoring",
            "Implement performance alerting",
            "Track response time trends",
            "Monitor error rates and patterns",
        ]

        plan["infrastructure_recommendations"] = [
            "Consider horizontal scaling for high-load services",
            "Implement load balancing if needed",
            "Add Redis caching layer",
            "Set up log aggregation and analysis",
        ]

        return plan

    async def run_comprehensive_optimization(self):
        """Run complete performance optimization analysis."""
        print("🎯 Sophia AI Performance Optimization")
        print("=" * 50)

        # Run performance benchmarks
        perf_results = await self.run_performance_benchmark()

        # Analyze bottlenecks
        bottlenecks = self.analyze_performance_bottlenecks(perf_results)

        # Run load testing
        load_results = await self.test_load_handling()

        # Generate optimization plan
        plan = self.generate_optimization_plan(perf_results, load_results)

        print("\n📋 Optimization Plan Generated")
        print("=" * 50)
        print(f"Overall Health: {plan['overall_health'].upper()}")

        if plan["optimizations"]:
            print("\n🔧 Recommended Optimizations:")
            for opt in plan["optimizations"]:
                print(f"  📊 {opt['service']} ({opt['type']}):")
                print(f"     Current: {opt['current_value']}")
                print(f"     Target: {opt['target_value']}")
                for action in opt["actions"]:
                    print(f"     • {action}")
        else:
            print("\n🎉 No immediate optimizations needed!")

        print("\n📈 Monitoring Recommendations:")
        for rec in plan["monitoring_recommendations"]:
            print(f"  • {rec}")

        return {
            "performance_results": perf_results,
            "load_results": load_results,
            "optimization_plan": plan,
            "bottlenecks": bottlenecks,
        }


async def main():
    """Main optimization function."""
    optimizer = SophiaPerformanceOptimizer()
    results = await optimizer.run_comprehensive_optimization()

    # Save results
    with open("performance_optimization_report.json", "w") as f:
        json.dump(results, f, indent=2)

    print("\n💾 Full report saved to: performance_optimization_report.json")


if __name__ == "__main__":
    asyncio.run(main())
