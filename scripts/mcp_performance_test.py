#!/usr/bin/env python3
"""
MCP Performance Testing Script
Performance testing for MCP servers with load testing and metrics
"""

import asyncio
import aiohttp
import json
import logging
import time
import statistics
import sys
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Performance metrics data structure"""

    server_name: str
    total_requests: int
    successful_requests: int
    failed_requests: int
    response_times: List[float]
    error_rate: float
    requests_per_second: float
    avg_response_time: float
    min_response_time: float
    max_response_time: float
    p95_response_time: float
    p99_response_time: float
    test_duration: float


class MCPPerformanceTester:
    """Performance tester for MCP servers"""

    def __init__(self, server_name: str, config_file: str = "cursor_mcp_config.json"):
        self.server_name = server_name
        self.config_file = Path(config_file)
        self.config = self._load_config()
        self.server_config = self._get_server_config()
        self.base_url = self.server_config.get("baseUrl", "http://localhost:8000")

    def _load_config(self) -> Dict[str, Any]:
        """Load MCP configuration"""
        if not self.config_file.exists():
            raise FileNotFoundError(f"MCP config file not found: {self.config_file}")

        with open(self.config_file, "r") as f:
            return json.load(f)

    def _get_server_config(self) -> Dict[str, Any]:
        """Get specific server configuration"""
        servers = self.config.get("mcpServers", {})
        if self.server_name not in servers:
            raise ValueError(f"Server {self.server_name} not found in configuration")

        return servers[self.server_name]

    async def health_check_test(self, session: aiohttp.ClientSession) -> Dict[str, Any]:
        """Perform single health check test"""
        start_time = time.time()

        try:
            async with session.get(f"{self.base_url}/health", timeout=10) as response:
                response_time = time.time() - start_time

                return {
                    "success": response.status == 200,
                    "status_code": response.status,
                    "response_time": response_time,
                    "error": None,
                }
        except asyncio.TimeoutError:
            return {
                "success": False,
                "status_code": 408,
                "response_time": time.time() - start_time,
                "error": "timeout",
            }
        except Exception as e:
            return {
                "success": False,
                "status_code": 500,
                "response_time": time.time() - start_time,
                "error": str(e),
            }

    async def capability_test(
        self, session: aiohttp.ClientSession, endpoint: str
    ) -> Dict[str, Any]:
        """Test specific capability endpoint"""
        start_time = time.time()

        try:
            # Use HEAD request for testing availability
            async with session.head(
                f"{self.base_url}{endpoint}", timeout=5
            ) as response:
                response_time = time.time() - start_time

                return {
                    "success": response.status < 500,
                    "status_code": response.status,
                    "response_time": response_time,
                    "error": None,
                }
        except Exception as e:
            return {
                "success": False,
                "status_code": 500,
                "response_time": time.time() - start_time,
                "error": str(e),
            }

    async def load_test(
        self, duration: int, concurrent_requests: int
    ) -> PerformanceMetrics:
        """Perform load test on MCP server"""
        logger.info(f"🚀 Starting load test for {self.server_name}")
        logger.info(
            f"Duration: {duration}s, Concurrent requests: {concurrent_requests}"
        )

        start_time = time.time()
        end_time = start_time + duration

        response_times = []
        successful_requests = 0
        failed_requests = 0

        connector = aiohttp.TCPConnector(limit=100, limit_per_host=50)
        timeout = aiohttp.ClientTimeout(total=10)

        async with aiohttp.ClientSession(
            connector=connector, timeout=timeout
        ) as session:

            async def make_request():
                nonlocal successful_requests, failed_requests

                result = await self.health_check_test(session)
                response_times.append(result["response_time"])

                if result["success"]:
                    successful_requests += 1
                else:
                    failed_requests += 1

            # Run load test
            while time.time() < end_time:
                # Create batch of concurrent requests
                tasks = [make_request() for _ in range(concurrent_requests)]
                await asyncio.gather(*tasks, return_exceptions=True)

                # Small delay between batches to prevent overwhelming
                await asyncio.sleep(0.01)

        test_duration = time.time() - start_time
        total_requests = successful_requests + failed_requests

        # Calculate metrics
        error_rate = failed_requests / total_requests if total_requests > 0 else 0
        requests_per_second = total_requests / test_duration if test_duration > 0 else 0

        avg_response_time = statistics.mean(response_times) if response_times else 0
        min_response_time = min(response_times) if response_times else 0
        max_response_time = max(response_times) if response_times else 0

        # Calculate percentiles
        if response_times:
            sorted_times = sorted(response_times)
            p95_index = int(0.95 * len(sorted_times))
            p99_index = int(0.99 * len(sorted_times))
            p95_response_time = (
                sorted_times[p95_index]
                if p95_index < len(sorted_times)
                else max_response_time
            )
            p99_response_time = (
                sorted_times[p99_index]
                if p99_index < len(sorted_times)
                else max_response_time
            )
        else:
            p95_response_time = 0
            p99_response_time = 0

        return PerformanceMetrics(
            server_name=self.server_name,
            total_requests=total_requests,
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            response_times=response_times,
            error_rate=error_rate,
            requests_per_second=requests_per_second,
            avg_response_time=avg_response_time,
            min_response_time=min_response_time,
            max_response_time=max_response_time,
            p95_response_time=p95_response_time,
            p99_response_time=p99_response_time,
            test_duration=test_duration,
        )

    async def capability_performance_test(self) -> Dict[str, PerformanceMetrics]:
        """Test performance of different capabilities"""
        logger.info(f"🔧 Testing capability performance for {self.server_name}")

        # Define capability endpoints based on server type
        capability_endpoints = {
            "ai_memory": ["/store", "/recall", "/search"],
            "codacy": ["/analyze", "/security_scan", "/quality_check"],
            "snowflake_admin": ["/execute_admin_task", "/health"],
            "asana": ["/tasks", "/projects"],
            "notion": ["/search", "/pages"],
        }

        endpoints = capability_endpoints.get(self.server_name, ["/health"])
        capability_metrics = {}

        connector = aiohttp.TCPConnector(limit=50)
        timeout = aiohttp.ClientTimeout(total=5)

        async with aiohttp.ClientSession(
            connector=connector, timeout=timeout
        ) as session:
            for endpoint in endpoints:
                logger.info(f"Testing endpoint: {endpoint}")

                # Run mini load test for each endpoint
                response_times = []
                successful_requests = 0
                failed_requests = 0

                # Test for 10 seconds with 5 concurrent requests
                start_time = time.time()
                end_time = start_time + 10

                while time.time() < end_time:
                    tasks = [self.capability_test(session, endpoint) for _ in range(5)]
                    results = await asyncio.gather(*tasks, return_exceptions=True)

                    for result in results:
                        if isinstance(result, dict):
                            response_times.append(result["response_time"])
                            if result["success"]:
                                successful_requests += 1
                            else:
                                failed_requests += 1

                    await asyncio.sleep(0.1)

                test_duration = time.time() - start_time
                total_requests = successful_requests + failed_requests

                if total_requests > 0:
                    capability_metrics[endpoint] = PerformanceMetrics(
                        server_name=f"{self.server_name}{endpoint}",
                        total_requests=total_requests,
                        successful_requests=successful_requests,
                        failed_requests=failed_requests,
                        response_times=response_times,
                        error_rate=failed_requests / total_requests,
                        requests_per_second=total_requests / test_duration,
                        avg_response_time=(
                            statistics.mean(response_times) if response_times else 0
                        ),
                        min_response_time=min(response_times) if response_times else 0,
                        max_response_time=max(response_times) if response_times else 0,
                        p95_response_time=0,  # Simplified for capability test
                        p99_response_time=0,
                        test_duration=test_duration,
                    )

        return capability_metrics

    async def stress_test(
        self, max_concurrent: int = 100, ramp_up_time: int = 30
    ) -> Dict[str, Any]:
        """Perform stress test with gradual ramp-up"""
        logger.info(f"💪 Starting stress test for {self.server_name}")
        logger.info(f"Max concurrent: {max_concurrent}, Ramp-up time: {ramp_up_time}s")

        stress_results = {
            "max_concurrent": max_concurrent,
            "ramp_up_time": ramp_up_time,
            "breaking_point": None,
            "peak_rps": 0,
            "performance_degradation": [],
        }

        connector = aiohttp.TCPConnector(limit=max_concurrent + 20)
        timeout = aiohttp.ClientTimeout(total=10)

        async with aiohttp.ClientSession(
            connector=connector, timeout=timeout
        ) as session:

            for concurrent in range(5, max_concurrent + 1, 5):
                logger.info(f"Testing with {concurrent} concurrent requests")

                # Test for 10 seconds with current concurrency level
                start_time = time.time()
                end_time = start_time + 10

                response_times = []
                successful_requests = 0
                failed_requests = 0

                while time.time() < end_time:
                    tasks = [self.health_check_test(session) for _ in range(concurrent)]
                    results = await asyncio.gather(*tasks, return_exceptions=True)

                    for result in results:
                        if isinstance(result, dict):
                            response_times.append(result["response_time"])
                            if result["success"]:
                                successful_requests += 1
                            else:
                                failed_requests += 1

                    await asyncio.sleep(0.1)

                test_duration = time.time() - start_time
                total_requests = successful_requests + failed_requests

                if total_requests > 0:
                    error_rate = failed_requests / total_requests
                    rps = total_requests / test_duration
                    avg_response_time = (
                        statistics.mean(response_times) if response_times else 0
                    )

                    stress_results["performance_degradation"].append(
                        {
                            "concurrent_requests": concurrent,
                            "requests_per_second": rps,
                            "error_rate": error_rate,
                            "avg_response_time": avg_response_time,
                        }
                    )

                    # Update peak RPS
                    if rps > stress_results["peak_rps"]:
                        stress_results["peak_rps"] = rps

                    # Check for breaking point
                    if (
                        error_rate > 0.1 or avg_response_time > 5.0
                    ):  # 10% error rate or 5s response time
                        stress_results["breaking_point"] = concurrent
                        logger.warning(
                            f"Breaking point reached at {concurrent} concurrent requests"
                        )
                        break

                # Gradual ramp-up delay
                await asyncio.sleep(ramp_up_time / (max_concurrent / 5))

        return stress_results

    def generate_performance_report(
        self,
        metrics: PerformanceMetrics,
        capability_metrics: Optional[Dict[str, PerformanceMetrics]] = None,
        stress_results: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Generate comprehensive performance report"""
        report = []
        report.append(f"# 📊 Performance Test Report - {self.server_name}")
        report.append("")
        report.append(f"**Server**: {metrics.server_name}")
        report.append(f"**Test Duration**: {metrics.test_duration:.2f}s")
        report.append(f"**Total Requests**: {metrics.total_requests}")
        report.append("")

        # Performance Summary
        report.append("## 🎯 Performance Summary")
        report.append(f"- **Requests/Second**: {metrics.requests_per_second:.2f}")
        report.append(f"- **Error Rate**: {metrics.error_rate:.1%}")
        report.append(f"- **Success Rate**: {(1 - metrics.error_rate):.1%}")
        report.append("")

        # Response Time Analysis
        report.append("## ⏱️ Response Time Analysis")
        report.append(f"- **Average**: {metrics.avg_response_time:.3f}s")
        report.append(f"- **Minimum**: {metrics.min_response_time:.3f}s")
        report.append(f"- **Maximum**: {metrics.max_response_time:.3f}s")
        report.append(f"- **95th Percentile**: {metrics.p95_response_time:.3f}s")
        report.append(f"- **99th Percentile**: {metrics.p99_response_time:.3f}s")
        report.append("")

        # Performance Assessment
        report.append("## 📈 Performance Assessment")

        if metrics.error_rate < 0.01:
            report.append("✅ **Excellent**: Error rate < 1%")
        elif metrics.error_rate < 0.05:
            report.append("🟡 **Good**: Error rate < 5%")
        else:
            report.append("🔴 **Needs Attention**: Error rate > 5%")

        if metrics.avg_response_time < 0.1:
            report.append("✅ **Excellent**: Average response time < 100ms")
        elif metrics.avg_response_time < 0.5:
            report.append("🟡 **Good**: Average response time < 500ms")
        else:
            report.append("🔴 **Slow**: Average response time > 500ms")

        if metrics.requests_per_second > 100:
            report.append("✅ **High Throughput**: > 100 requests/second")
        elif metrics.requests_per_second > 50:
            report.append("🟡 **Moderate Throughput**: > 50 requests/second")
        else:
            report.append("🔴 **Low Throughput**: < 50 requests/second")

        report.append("")

        # Capability Performance
        if capability_metrics:
            report.append("## 🔧 Capability Performance")
            for endpoint, cap_metrics in capability_metrics.items():
                report.append(f"### {endpoint}")
                report.append(f"- **RPS**: {cap_metrics.requests_per_second:.2f}")
                report.append(
                    f"- **Avg Response**: {cap_metrics.avg_response_time:.3f}s"
                )
                report.append(f"- **Error Rate**: {cap_metrics.error_rate:.1%}")
                report.append("")

        # Stress Test Results
        if stress_results:
            report.append("## 💪 Stress Test Results")
            report.append(f"- **Peak RPS**: {stress_results['peak_rps']:.2f}")
            if stress_results["breaking_point"]:
                report.append(
                    f"- **Breaking Point**: {stress_results['breaking_point']} concurrent requests"
                )
            else:
                report.append(
                    f"- **Breaking Point**: Not reached (tested up to {stress_results['max_concurrent']})"
                )
            report.append("")

        # Recommendations
        report.append("## 🎯 Recommendations")

        if metrics.error_rate > 0.05:
            report.append("- 🔧 Investigate and fix error causes")

        if metrics.avg_response_time > 0.5:
            report.append(
                "- ⚡ Optimize response time (consider caching, async processing)"
            )

        if metrics.requests_per_second < 50:
            report.append(
                "- 📈 Improve throughput (connection pooling, load balancing)"
            )

        if (
            stress_results
            and stress_results.get("breaking_point")
            and stress_results["breaking_point"] < 50
        ):
            report.append("- 💪 Improve server capacity and resilience")

        return "\n".join(report)


async def main():
    """Main performance testing function"""
    import argparse

    parser = argparse.ArgumentParser(description="MCP Performance Testing")
    parser.add_argument("--server", required=True, help="MCP server name")
    parser.add_argument(
        "--config", default="cursor_mcp_config.json", help="MCP config file"
    )
    parser.add_argument(
        "--duration", type=int, default=60, help="Load test duration (seconds)"
    )
    parser.add_argument(
        "--concurrent-requests", type=int, default=10, help="Concurrent requests"
    )
    parser.add_argument(
        "--capability-test", action="store_true", help="Test individual capabilities"
    )
    parser.add_argument("--stress-test", action="store_true", help="Run stress test")
    parser.add_argument(
        "--max-concurrent", type=int, default=100, help="Max concurrent for stress test"
    )
    parser.add_argument("--output", help="Output file for results")

    args = parser.parse_args()

    try:
        tester = MCPPerformanceTester(args.server, args.config)

        # Run load test
        logger.info("🚀 Starting performance tests")
        metrics = await tester.load_test(args.duration, args.concurrent_requests)

        # Optional capability test
        capability_metrics = None
        if args.capability_test:
            capability_metrics = await tester.capability_performance_test()

        # Optional stress test
        stress_results = None
        if args.stress_test:
            stress_results = await tester.stress_test(args.max_concurrent)

        # Generate report
        report = tester.generate_performance_report(
            metrics, capability_metrics, stress_results
        )

        if args.output:
            with open(args.output, "w") as f:
                f.write(report)
            logger.info(f"📊 Performance report saved to {args.output}")
        else:
            print(report)

        # Print summary
        print(f"\n📊 Performance Summary for {args.server}:")
        print(f"RPS: {metrics.requests_per_second:.2f}")
        print(f"Error Rate: {metrics.error_rate:.1%}")
        print(f"Avg Response Time: {metrics.avg_response_time:.3f}s")

        return 0

    except Exception as e:
        logger.error(f"❌ Performance test failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
