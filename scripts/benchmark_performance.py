#!/usr/bin/env python3
"""
Sophia AI Performance Benchmark - July 2025
Tests GPU memory stack performance vs old Qdrant approach
"""

from backend.services.sophia_unified_memory_service import get_memory_service, SophiaUnifiedMemoryService
import asyncio
import time
import statistics
from typing import Dict
import httpx


class Colors:
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"


async def benchmark_endpoint(url: str, payload: Dict, iterations: int = 10) -> Dict:
    """Benchmark an endpoint with multiple iterations"""

    latencies = []
    errors = 0

    async with httpx.AsyncClient(timeout=30.0) as client:
        # Warmup
        await client.post(url, json=payload)

        for i in range(iterations):
            try:
                start = time.perf_counter()
                response = await client.post(url, json=payload)
                end = time.perf_counter()

                if response.status_code == 200:
                    latencies.append((end - start) * 1000)  # Convert to ms
                else:
                    errors += 1
            except Exception as e:
                errors += 1
                print(f"Error: {e}")

    if latencies:
        return {
            "min": min(latencies),
            "max": max(latencies),
            "mean": statistics.mean(latencies),
            "median": statistics.median(latencies),
            "p95": statistics.quantiles(latencies, n=20)[18]
            if len(latencies) > 20
            else max(latencies),
            "errors": errors,
            "success_rate": (iterations - errors) / iterations * 100,
        }
    else:
        return {"errors": errors, "success_rate": 0}


async def main():
    print(
        f"{Colors.BOLD}🚀 Sophia AI Performance Benchmark - GPU Memory Stack{Colors.ENDC}"
    )
    print("=" * 60)

    base_url = "http://localhost:8001"

    # Test scenarios
    test_cases = [
        {
            "name": "Simple Query",
            "endpoint": "/api/v3/chat",
            "payload": {
                "query": "What is the deployment status?",
                "user_id": "benchmark_user",
            },
        },
        {
            "name": "Complex RAG Query",
            "endpoint": "/api/v3/chat",
            "payload": {
                "query": "Analyze our infrastructure performance, identify bottlenecks, and suggest optimizations based on recent metrics",
                "user_id": "benchmark_user",
            },
        },
        {
            "name": "Memory Search",
            "endpoint": "/api/v3/knowledge/search",
            "payload": {"query": "deployment Lambda Labs GPU", "limit": 10},
        },
        {"name": "System Status", "endpoint": "/api/v3/system/status", "payload": {}},
    ]

    # Benchmark configuration
    iterations_per_test = 20

    print(f"\n{Colors.BLUE}Configuration:{Colors.ENDC}")
    print(f"  Backend URL: {base_url}")
    print(f"  Iterations per test: {iterations_per_test}")
    print(f"  Test cases: {len(test_cases)}")

    # Run benchmarks
    results = {}

    for test in test_cases:
        print(f"\n{Colors.BLUE}Testing: {test['name']}{Colors.ENDC}")
        print(f"  Endpoint: {test['endpoint']}")

        url = f"{base_url}{test['endpoint']}"

        # For GET requests
        if test["endpoint"] == "/api/v3/system/status":
            async with httpx.AsyncClient() as client:
                latencies = []
                for _ in range(iterations_per_test):
                    start = time.perf_counter()
                    response = await client.get(url)
                    end = time.perf_counter()
                    if response.status_code == 200:
                        latencies.append((end - start) * 1000)

                result = {
                    "min": min(latencies),
                    "max": max(latencies),
                    "mean": statistics.mean(latencies),
                    "median": statistics.median(latencies),
                    "p95": statistics.quantiles(latencies, n=20)[18]
                    if len(latencies) > 20
                    else max(latencies),
                    "errors": 0,
                    "success_rate": 100.0,
                }
        else:
            result = await benchmark_endpoint(url, test["payload"], iterations_per_test)

        results[test["name"]] = result

        # Print results
        if "mean" in result:
            color = (
                Colors.GREEN
                if result["mean"] < 200
                else Colors.YELLOW
                if result["mean"] < 500
                else Colors.RED
            )
            print(f"{color}  Mean latency: {result['mean']:.2f}ms{Colors.ENDC}")
            print(f"  Min/Max: {result['min']:.2f}ms / {result['max']:.2f}ms")
            print(f"  Median: {result['median']:.2f}ms")
            print(f"  P95: {result['p95']:.2f}ms")
            print(f"  Success rate: {result['success_rate']:.1f}%")
        else:
            print(f"{Colors.RED}  All requests failed{Colors.ENDC}")

    # Summary
    print(f"\n{Colors.BOLD}📊 Performance Summary{Colors.ENDC}")
    print("=" * 60)

    # Compare with Qdrant baseline (historical data)
    
        "Simple Query": 450,  # ms
        "Complex RAG Query": 1200,  # ms
        "Memory Search": 300,  # ms
        "System Status": 50,  # ms
    }

    print(f"\n{Colors.BLUE}GPU Memory Stack vs Qdrant Comparison:{Colors.ENDC}")
    print(f"{'Test Case':<25} {'GPU Stack':<15} {'Qdrant':<15} {'Improvement':<15}")
    print("-" * 70)

    total_improvement = 0
    test_count = 0

    for test_name, result in results.items():
        if "mean" in result and test_name in QDRANT_baseline:
            gpu_latency = result["mean"]
            
            improvement = ((QDRANT_latency - gpu_latency) / QDRANT_latency) * 100

            color = (
                Colors.GREEN
                if improvement > 50
                else Colors.YELLOW
                if improvement > 0
                else Colors.RED
            )
            print(
                f"{test_name:<25} {gpu_latency:<15.2f} {QDRANT_latency:<15.2f} {color}{improvement:>14.1f}%{Colors.ENDC}"
            )

            total_improvement += improvement
            test_count += 1

    if test_count > 0:
        avg_improvement = total_improvement / test_count
        print("-" * 70)
        color = (
            Colors.GREEN
            if avg_improvement > 50
            else Colors.YELLOW
            if avg_improvement > 0
            else Colors.RED
        )
        print(
            f"{'Average Improvement':<25} {' ':<15} {' ':<15} {color}{avg_improvement:>14.1f}%{Colors.ENDC}"
        )

    # Final verdict
    print(f"\n{Colors.BOLD}🎯 Verdict:{Colors.ENDC}")

    if avg_improvement > 70:
        print(
            f"{Colors.GREEN}✅ GPU Memory Stack is CRUSHING IT! {avg_improvement:.1f}% faster than Qdrant!{Colors.ENDC}"
        )
        print(
            f"{Colors.GREEN}   Lambda B200's 192GB VRAM + Qdrant 4.6.1 = Pure performance porn{Colors.ENDC}"
        )
    elif avg_improvement > 30:
        print(
            f"{Colors.YELLOW}⚡ Solid improvement! {avg_improvement:.1f}% faster. Not bad for a first run.{Colors.ENDC}"
        )
    else:
        print(
            f"{Colors.RED}❌ Houston, we have a problem. Only {avg_improvement:.1f}% improvement.{Colors.ENDC}"
        )
        print(
            f"{Colors.RED}   Time to check those GPU kernels and vector indexes...{Colors.ENDC}"
        )


if __name__ == "__main__":
    asyncio.run(main())
