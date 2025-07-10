#!/usr/bin/env python3
"""
Performance Baseline Measurement for Sophia AI
Measures current system performance to establish improvement targets
"""
import asyncio
import json
import os
import statistics
import sys
import time
from datetime import datetime

import aiohttp

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# MCP Server configurations
MCP_SERVERS = {
    "ai_memory": {"port": 9000, "critical": True},
    "codacy": {"port": 3008, "critical": True},
    "github": {"port": 9003, "critical": False},
    "linear": {"port": 9004, "critical": False},
    "snowflake_unified": {"port": 8080, "critical": True},
}

# Test scenarios
TEST_SCENARIOS = {
    "ceo_revenue_query": {
        "endpoint": "/api/v1/chat",
        "payload": {
            "message": "What is our current revenue and growth rate?",
            "context": "ceo_deep_research",
            "access_level": "ceo",
        },
        "sla_ms": 2000,
    },
    "business_intelligence": {
        "endpoint": "/api/v1/chat",
        "payload": {
            "message": "Show me top 5 deals by value",
            "context": "business_intelligence",
            "access_level": "manager",
        },
        "sla_ms": 3000,
    },
    "code_analysis": {
        "endpoint": "/api/v1/chat",
        "payload": {
            "message": "Analyze the security of our authentication module",
            "context": "coding_agents",
            "access_level": "developer",
        },
        "sla_ms": 5000,
    },
}


class PerformanceBaseline:
    """Measure and document performance baseline"""

    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "mcp_servers": {},
            "api_endpoints": {},
            "scenarios": {},
            "summary": {},
        }

    async def measure_mcp_health(self) -> dict[str, dict]:
        """Measure MCP server health check response times"""

        for server_name, config in MCP_SERVERS.items():
            port = config["port"]
            times = []
            errors = 0

            for _i in range(10):
                try:
                    start = time.time()
                    async with aiohttp.ClientSession() as session:
                        async with session.get(
                            f"http://localhost:{port}/health",
                            timeout=aiohttp.ClientTimeout(total=5),
                        ) as response:
                            await response.text()
                            elapsed = (time.time() - start) * 1000  # Convert to ms
                            times.append(elapsed)

                            if response.status == 200:
                                pass
                            else:
                                errors += 1

                except Exception:
                    errors += 1

                await asyncio.sleep(0.1)  # Small delay between requests

            if times:
                self.results["mcp_servers"][server_name] = {
                    "avg_ms": statistics.mean(times),
                    "p95_ms": (
                        statistics.quantiles(times, n=20)[18]
                        if len(times) > 1
                        else times[0]
                    ),
                    "max_ms": max(times),
                    "min_ms": min(times),
                    "success_rate": (10 - errors) / 10,
                    "critical": config["critical"],
                }
            else:
                self.results["mcp_servers"][server_name] = {
                    "status": "unreachable",
                    "critical": config["critical"],
                }

    async def measure_api_endpoints(self) -> None:
        """Measure main API endpoint response times"""

        base_url = "http://localhost:8000"

        # Test different endpoints
        endpoints = [
            ("/", "GET", None),
            ("/api/mcp/health", "GET", None),
            ("/api/cache/stats", "GET", None),
            ("/api/metrics", "GET", None),
        ]

        for endpoint, method, _payload in endpoints:
            times = []
            errors = 0

            for _i in range(5):
                try:
                    start = time.time()
                    async with aiohttp.ClientSession() as session:
                        if method == "GET":
                            async with session.get(
                                f"{base_url}{endpoint}",
                                timeout=aiohttp.ClientTimeout(total=10),
                            ) as response:
                                await response.text()
                                elapsed = (time.time() - start) * 1000
                                times.append(elapsed)

                except Exception:
                    errors += 1

                await asyncio.sleep(0.1)

            if times:
                self.results["api_endpoints"][endpoint] = {
                    "method": method,
                    "avg_ms": statistics.mean(times),
                    "max_ms": max(times),
                    "min_ms": min(times),
                    "success_rate": (5 - errors) / 5,
                }

    async def measure_chat_scenarios(self) -> None:
        """Measure performance of realistic chat scenarios"""

        base_url = "http://localhost:8000"

        for scenario_name, scenario in TEST_SCENARIOS.items():
            times = []
            errors = 0

            for _i in range(3):  # Fewer iterations for expensive operations
                try:
                    start = time.time()
                    async with aiohttp.ClientSession() as session:
                        async with session.post(
                            f"{base_url}{scenario['endpoint']}",
                            json=scenario["payload"],
                            timeout=aiohttp.ClientTimeout(total=30),
                        ) as response:
                            await response.json()
                            elapsed = (time.time() - start) * 1000
                            times.append(elapsed)

                            "✅" if elapsed < scenario["sla_ms"] else "❌"

                            if response.status != 200:
                                errors += 1

                except Exception:
                    errors += 1

                await asyncio.sleep(1)  # Longer delay for chat requests

            if times:
                avg_time = statistics.mean(times)
                self.results["scenarios"][scenario_name] = {
                    "avg_ms": avg_time,
                    "max_ms": max(times),
                    "min_ms": min(times),
                    "sla_ms": scenario["sla_ms"],
                    "sla_met": avg_time < scenario["sla_ms"],
                    "success_rate": (3 - errors) / 3,
                }

    def generate_summary(self) -> None:
        """Generate performance summary and recommendations"""

        # MCP Server Summary
        healthy_servers = sum(
            1
            for s in self.results["mcp_servers"].values()
            if s.get("success_rate", 0) == 1.0
        )
        critical_issues = sum(
            1
            for s in self.results["mcp_servers"].values()
            if s.get("critical") and s.get("success_rate", 0) < 1.0
        )

        # API Performance Summary
        api_avg_response = (
            statistics.mean(
                [
                    e["avg_ms"]
                    for e in self.results["api_endpoints"].values()
                    if "avg_ms" in e
                ]
            )
            if self.results["api_endpoints"]
            else 0
        )

        # Scenario Summary
        sla_violations = sum(
            1 for s in self.results["scenarios"].values() if not s.get("sla_met", True)
        )

        self.results["summary"] = {
            "mcp_servers": {
                "total": len(MCP_SERVERS),
                "healthy": healthy_servers,
                "critical_issues": critical_issues,
            },
            "api_performance": {
                "avg_response_ms": api_avg_response,
                "endpoints_tested": len(self.results["api_endpoints"]),
            },
            "scenarios": {
                "total": len(TEST_SCENARIOS),
                "sla_violations": sla_violations,
            },
            "recommendations": self._generate_recommendations(),
        }

    def _generate_recommendations(self) -> list[str]:
        """Generate performance improvement recommendations"""
        recommendations = []

        # Check MCP server performance
        for server, stats in self.results["mcp_servers"].items():
            if stats.get("avg_ms", 0) > 100:
                recommendations.append(
                    f"⚡ Optimize {server} server - avg response {stats['avg_ms']:.0f}ms > 100ms target"
                )
            if stats.get("success_rate", 0) < 1.0:
                recommendations.append(
                    f"🔧 Fix {server} server reliability - {stats['success_rate']*100:.0f}% success rate"
                )

        # Check scenario SLAs
        for scenario, stats in self.results["scenarios"].items():
            if not stats.get("sla_met", True):
                recommendations.append(
                    f"🎯 Optimize {scenario} - {stats['avg_ms']:.0f}ms exceeds {stats['sla_ms']}ms SLA"
                )

        # General recommendations
        if not recommendations:
            recommendations.append(
                "✅ All performance metrics within acceptable ranges"
            )

        return recommendations

    def save_results(self) -> None:
        """Save results to file"""
        filename = (
            f"performance_baseline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        filepath = os.path.join("docs", "performance", filename)

        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        with open(filepath, "w") as f:
            json.dump(self.results, f, indent=2)

    def print_summary(self) -> None:
        """Print performance summary to console"""

        summary = self.results["summary"]

        for _rec in summary["recommendations"]:
            pass


async def main():
    """Run performance baseline measurement"""

    baseline = PerformanceBaseline()

    # Run measurements
    await baseline.measure_mcp_health()
    await baseline.measure_api_endpoints()
    await baseline.measure_chat_scenarios()

    # Generate summary and save
    baseline.generate_summary()
    baseline.print_summary()
    baseline.save_results()


if __name__ == "__main__":
    asyncio.run(main())
