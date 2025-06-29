#!/usr/bin/env python3
"""
Performance Baseline Measurement for Sophia AI Platform
Benchmarks all components and establishes performance baselines
"""

import argparse
import asyncio
import json
import logging
import statistics
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import psutil

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from backend.agents.infrastructure.sophia_infrastructure_agent import (
    SophiaInfrastructureAgent,
)
from backend.core.auto_esc_config import config
from backend.mcp.ai_memory_mcp_server import AiMemoryMCPServer

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class PerformanceBenchmark:
    """Base class for performance benchmarks"""

    def __init__(self, name: str, target_metric: float = None, unit: str = "ms"):
        self.name = name
        self.target_metric = target_metric
        self.unit = unit
        self.measurements = []

    async def measure(self, iterations: int = 10) -> dict[str, Any]:
        """Perform benchmark measurements"""
        raise NotImplementedError

    def analyze_results(self) -> dict[str, Any]:
        """Analyze benchmark results"""
        if not self.measurements:
            return {"error": "No measurements available"}

        avg = statistics.mean(self.measurements)
        median = statistics.median(self.measurements)
        std_dev = (
            statistics.stdev(self.measurements) if len(self.measurements) > 1 else 0
        )
        min_val = min(self.measurements)
        max_val = max(self.measurements)

        # Determine performance status
        if self.target_metric:
            performance_ratio = avg / self.target_metric
            if performance_ratio <= 1.0:
                status = "excellent"
            elif performance_ratio <= 1.5:
                status = "good"
            elif performance_ratio <= 2.0:
                status = "acceptable"
            else:
                status = "poor"
        else:
            status = "unknown"

        return {
            "average": round(avg, 4),
            "median": round(median, 4),
            "std_dev": round(std_dev, 4),
            "min": round(min_val, 4),
            "max": round(max_val, 4),
            "unit": self.unit,
            "target": self.target_metric,
            "status": status,
            "sample_size": len(self.measurements),
            "raw_measurements": self.measurements,
        }


class ConfigurationLoadBenchmark(PerformanceBenchmark):
    """Benchmark configuration loading performance"""

    def __init__(self):
        super().__init__("Configuration Loading", target_metric=5000, unit="ms")

    async def measure(self, iterations: int = 10) -> dict[str, Any]:
        """Measure configuration loading time"""
        logger.info(f"Benchmarking {self.name} ({iterations} iterations)...")

        for i in range(iterations):
            start_time = time.perf_counter()

            try:
                # Simulate configuration reload
                config.as_enhanced_settings()
                config.get_health_status()

                end_time = time.perf_counter()
                measurement = (end_time - start_time) * 1000  # Convert to ms
                self.measurements.append(measurement)

            except Exception as e:
                logger.error(f"Configuration load iteration {i} failed: {e}")

        return self.analyze_results()


class MCPResponseBenchmark(PerformanceBenchmark):
    """Benchmark MCP server response time"""

    def __init__(self):
        super().__init__("MCP Response Time", target_metric=200, unit="ms")

    async def measure(self, iterations: int = 10) -> dict[str, Any]:
        """Measure MCP server response time"""
        logger.info(f"Benchmarking {self.name} ({iterations} iterations)...")

        mcp_server = AiMemoryMCPServer()

        for i in range(iterations):
            start_time = time.perf_counter()

            try:
                # Test MCP tool execution
                await mcp_server.execute_tool(
                    "store_conversation",
                    {
                        "content": f"Benchmark test {i}",
                        "category": "workflow",
                        "tags": ["benchmark", "test"],
                    },
                )

                end_time = time.perf_counter()
                measurement = (end_time - start_time) * 1000  # Convert to ms
                self.measurements.append(measurement)

            except Exception as e:
                logger.error(f"MCP response iteration {i} failed: {e}")

        return self.analyze_results()


class AgentInstantiationBenchmark(PerformanceBenchmark):
    """Benchmark agent instantiation time"""

    def __init__(self):
        super().__init__("Agent Instantiation", target_metric=0.003, unit="ms")

    async def measure(self, iterations: int = 50) -> dict[str, Any]:
        """Measure agent instantiation time"""
        logger.info(f"Benchmarking {self.name} ({iterations} iterations)...")

        for i in range(iterations):
            start_time = time.perf_counter()

            try:
                # Create new agent instance
                SophiaInfrastructureAgent()

                end_time = time.perf_counter()
                measurement = (end_time - start_time) * 1000  # Convert to ms
                self.measurements.append(measurement)

            except Exception as e:
                logger.error(f"Agent instantiation iteration {i} failed: {e}")

        return self.analyze_results()


class MemoryUsageBenchmark(PerformanceBenchmark):
    """Benchmark memory usage"""

    def __init__(self):
        super().__init__("Memory Usage", target_metric=2048, unit="MB")

    async def measure(self, iterations: int = 5) -> dict[str, Any]:
        """Measure memory usage"""
        logger.info(f"Benchmarking {self.name} ({iterations} iterations)...")

        process = psutil.Process()

        for i in range(iterations):
            try:
                # Get memory info
                memory_info = process.memory_info()
                memory_mb = memory_info.rss / (1024 * 1024)  # Convert to MB
                self.measurements.append(memory_mb)

                # Small delay between measurements
                await asyncio.sleep(0.1)

            except Exception as e:
                logger.error(f"Memory measurement iteration {i} failed: {e}")

        return self.analyze_results()


class CPUUsageBenchmark(PerformanceBenchmark):
    """Benchmark CPU usage"""

    def __init__(self):
        super().__init__("CPU Usage", target_metric=50, unit="%")

    async def measure(self, iterations: int = 10) -> dict[str, Any]:
        """Measure CPU usage"""
        logger.info(f"Benchmarking {self.name} ({iterations} iterations)...")

        process = psutil.Process()

        for i in range(iterations):
            try:
                # Get CPU usage
                cpu_percent = process.cpu_percent(interval=0.1)
                self.measurements.append(cpu_percent)

            except Exception as e:
                logger.error(f"CPU measurement iteration {i} failed: {e}")

        return self.analyze_results()


class SophiaPerformanceBenchmarker:
    """Main performance benchmarker orchestrator"""

    def __init__(self, component: str = "all", iterations: int = 10):
        self.component = component
        self.iterations = iterations

        self.benchmarks = {
            "configuration": ConfigurationLoadBenchmark(),
            "mcp_response": MCPResponseBenchmark(),
            "agent_instantiation": AgentInstantiationBenchmark(),
            "memory_usage": MemoryUsageBenchmark(),
            "cpu_usage": CPUUsageBenchmark(),
        }

    async def run_benchmarks(self) -> dict[str, Any]:
        """Run performance benchmarks"""
        logger.info("🚀 Starting Sophia AI Performance Benchmarking...")

        start_time = datetime.now(UTC)
        results = {}

        # Select benchmarks to run
        if self.component == "all":
            selected_benchmarks = self.benchmarks
        else:
            selected_benchmarks = {self.component: self.benchmarks.get(self.component)}
            if selected_benchmarks[self.component] is None:
                raise ValueError(f"Unknown component: {self.component}")

        # Run benchmarks
        for name, benchmark in selected_benchmarks.items():
            logger.info(f"Running {benchmark.name} benchmark...")

            try:
                result = await benchmark.measure(self.iterations)
                results[name] = result

                status_emoji = {
                    "excellent": "🚀",
                    "good": "✅",
                    "acceptable": "⚠️",
                    "poor": "❌",
                    "unknown": "❓",
                }.get(result.get("status", "unknown"), "❓")

                avg = result.get("average", 0)
                unit = result.get("unit", "")
                target = result.get("target", 0)

                logger.info(
                    f"{status_emoji} {benchmark.name}: {avg}{unit} (target: {target}{unit})"
                )

            except Exception as e:
                logger.error(f"Benchmark {name} failed: {e}")
                results[name] = {"error": str(e)}

        end_time = datetime.now(UTC)

        # Generate summary
        summary = self._generate_summary(results)

        benchmark_report = {
            "timestamp": datetime.now(UTC).isoformat(),
            "total_execution_time": (end_time - start_time).total_seconds(),
            "sophia_ai_version": "v2.0.0",
            "environment": "staging",
            "iterations": self.iterations,
            "component": self.component,
            "system_info": self._get_system_info(),
            "summary": summary,
            "detailed_results": results,
        }

        return benchmark_report

    def _generate_summary(self, results: dict[str, Any]) -> dict[str, Any]:
        """Generate benchmark summary"""
        total_benchmarks = len(results)
        status_counts = {}

        for result in results.values():
            if "error" in result:
                status = "error"
            else:
                status = result.get("status", "unknown")
            status_counts[status] = status_counts.get(status, 0) + 1

        # Calculate overall performance score
        excellent_count = status_counts.get("excellent", 0)
        good_count = status_counts.get("good", 0)
        acceptable_count = status_counts.get("acceptable", 0)

        performance_score = (
            ((excellent_count * 100) + (good_count * 80) + (acceptable_count * 60))
            / total_benchmarks
            if total_benchmarks > 0
            else 0
        )

        # Determine overall status
        if performance_score >= 90:
            overall_status = "excellent"
        elif performance_score >= 70:
            overall_status = "good"
        elif performance_score >= 50:
            overall_status = "acceptable"
        else:
            overall_status = "poor"

        return {
            "overall_status": overall_status,
            "performance_score": round(performance_score, 1),
            "total_benchmarks": total_benchmarks,
            "excellent_count": excellent_count,
            "good_count": good_count,
            "acceptable_count": acceptable_count,
            "poor_count": status_counts.get("poor", 0),
            "error_count": status_counts.get("error", 0),
            "production_ready": overall_status in ["excellent", "good"],
            "status_distribution": status_counts,
        }

    def _get_system_info(self) -> dict[str, Any]:
        """Get system information"""
        try:
            return {
                "cpu_count": psutil.cpu_count(),
                "cpu_freq": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None,
                "memory_total": round(
                    psutil.virtual_memory().total / (1024**3), 2
                ),  # GB
                "memory_available": round(
                    psutil.virtual_memory().available / (1024**3), 2
                ),  # GB
                "disk_usage": round(psutil.disk_usage("/").free / (1024**3), 2),  # GB
                "python_version": sys.version.split()[0],
                "platform": sys.platform,
            }
        except Exception as e:
            return {"error": str(e)}

    def save_report(self, report: dict[str, Any], output_file: str = None) -> str:
        """Save benchmark report to file"""
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"sophia_performance_report_{timestamp}.json"

        with open(output_file, "w") as f:
            json.dump(report, f, indent=2, default=str)

        return output_file

    def print_summary(self, report: dict[str, Any]) -> None:
        """Print formatted benchmark summary"""
        summary = report["summary"]

        print("\n" + "=" * 60)
        print("🚀 SOPHIA AI PERFORMANCE BENCHMARK SUMMARY")
        print("=" * 60)

        status_emoji = {
            "excellent": "🚀",
            "good": "✅",
            "acceptable": "⚠️",
            "poor": "❌",
        }.get(summary["overall_status"], "❓")

        print(
            f"Overall Performance: {status_emoji} {summary['overall_status'].upper()}"
        )
        print(f"Performance Score: {summary['performance_score']}/100")
        print(
            f"Benchmarks: {summary['excellent_count'] + summary['good_count']}/{summary['total_benchmarks']} meeting targets"
        )
        print(f"Total Execution Time: {report['total_execution_time']:.2f}s")
        print(
            f"Production Ready: {'✅ YES' if summary['production_ready'] else '❌ NO'}"
        )

        # System info
        sys_info = report.get("system_info", {})
        if sys_info and "error" not in sys_info:
            print("\n💻 System Info:")
            print(f"  CPU: {sys_info.get('cpu_count', 'unknown')} cores")
            print(f"  Memory: {sys_info.get('memory_total', 'unknown')} GB total")
            print(f"  Python: {sys_info.get('python_version', 'unknown')}")

        print("\n📊 Benchmark Results:")
        for name, result in report["detailed_results"].items():
            if "error" in result:
                print(f"  ❌ {name}: ERROR - {result['error']}")
                continue

            status_emoji = {
                "excellent": "🚀",
                "good": "✅",
                "acceptable": "⚠️",
                "poor": "❌",
                "unknown": "❓",
            }.get(result.get("status", "unknown"), "❓")

            avg = result.get("average", 0)
            target = result.get("target", 0)
            unit = result.get("unit", "")

            print(f"  {status_emoji} {name}: {avg}{unit} (target: {target}{unit})")

            # Show percentiles for performance metrics
            if "min" in result and "max" in result:
                print(f"    Range: {result['min']}{unit} - {result['max']}{unit}")

        print("\n" + "=" * 60)


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Sophia AI Performance Benchmarking")
    parser.add_argument(
        "--component",
        choices=[
            "all",
            "configuration",
            "mcp_response",
            "agent_instantiation",
            "memory_usage",
            "cpu_usage",
        ],
        default="all",
        help="Component to benchmark",
    )
    parser.add_argument(
        "--iterations", type=int, default=10, help="Number of iterations per benchmark"
    )
    parser.add_argument("--output", type=str, help="Output file for detailed report")
    parser.add_argument("--quiet", action="store_true", help="Suppress verbose output")

    args = parser.parse_args()

    if args.quiet:
        logging.getLogger().setLevel(logging.WARNING)

    # Run benchmarks
    benchmarker = SophiaPerformanceBenchmarker(args.component, args.iterations)
    report = await benchmarker.run_benchmarks()

    # Save detailed report
    report_file = benchmarker.save_report(report, args.output)

    # Print summary
    benchmarker.print_summary(report)

    print(f"\n📄 Detailed report saved to: {report_file}")

    # Exit with appropriate code
    overall_status = report["summary"]["overall_status"]
    exit_code = {"excellent": 0, "good": 0, "acceptable": 1, "poor": 2}.get(
        overall_status, 3
    )

    sys.exit(exit_code)


if __name__ == "__main__":
    asyncio.run(main())
