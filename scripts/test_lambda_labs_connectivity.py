#!/usr/bin/env python3
"""
Lambda Labs Connectivity Test Script

Tests connectivity to various services on the Lambda Labs server
to understand what's currently deployed and accessible.
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Optional

import aiohttp


class LambdaLabsConnectivityTester:
    """Test connectivity to Lambda Labs services"""

    def __init__(self, host: str = "165.1.69.44"):
        self.host = host
        self.results = []

        # Common ports to test
        self.test_ports = {
            # Sophia AI Services
            "Main API": 8000,
            "Codacy MCP": 3008,
            "AI Memory": 9001,
            "Snowflake Admin": 9020,
            "Linear": 9004,
            "GitHub": 9103,
            "Asana": 9100,
            "Notion": 9005,
            "UI/UX Agent": 9002,
            "Portkey Admin": 9013,
            "Lambda Labs CLI": 9020,
            "Snowflake Cortex": 9030,
            # Infrastructure Services
            "Grafana": 3000,
            "Prometheus": 9090,
            "MCP Gateway": 8080,
            "Loki": 3100,
            # Common web services
            "HTTP": 80,
            "HTTPS": 443,
            "SSH": 22,
        }

    async def test_http_endpoint(
        self, port: int, timeout: float = 5.0
    ) -> tuple[bool, Optional[str], float]:
        """Test HTTP connectivity to a specific port"""
        url = f"http://{self.host}:{port}"

        try:
            start_time = time.time()
            timeout_config = aiohttp.ClientTimeout(total=timeout)

            async with aiohttp.ClientSession(timeout=timeout_config) as session:
                async with session.get(url) as response:
                    response_time = (time.time() - start_time) * 1000

                    if response.status < 500:  # Accept any non-server error
                        try:
                            # Try to get some response info
                            content_type = response.headers.get(
                                "content-type", "unknown"
                            )
                            server = response.headers.get("server", "unknown")
                            info = f"Status: {response.status}, Type: {content_type}, Server: {server}"
                        except Exception:
                            info = f"Status: {response.status}"

                        return True, info, response_time
                    else:
                        return False, f"Server error: {response.status}", response_time

        except asyncio.TimeoutError:
            return False, "Timeout", timeout * 1000
        except aiohttp.ClientConnectorError:
            return False, "Connection refused", 0
        except Exception as e:
            return False, f"Error: {str(e)[:50]}", 0

    async def test_health_endpoint(
        self, port: int
    ) -> tuple[bool, Optional[str], float]:
        """Test the /health endpoint specifically"""
        url = f"http://{self.host}:{port}/health"

        try:
            start_time = time.time()
            timeout_config = aiohttp.ClientTimeout(total=5.0)

            async with aiohttp.ClientSession(timeout=timeout_config) as session:
                async with session.get(url) as response:
                    response_time = (time.time() - start_time) * 1000

                    if response.status == 200:
                        try:
                            data = await response.json()
                            status = data.get("status", "unknown")
                            return True, f"Health: {status}", response_time
                        except json.JSONDecodeError:
                            return (
                                True,
                                "Health endpoint responding (non-JSON)",
                                response_time,
                            )
                    else:
                        return (
                            False,
                            f"Health check failed: {response.status}",
                            response_time,
                        )

        except Exception as e:
            return False, f"Health error: {str(e)[:30]}", 0

    async def run_connectivity_tests(self):
        """Run comprehensive connectivity tests"""
        print(f"🔍 Testing connectivity to Lambda Labs server: {self.host}")
        print(f"⏰ Test started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)

        results = []

        for service_name, port in self.test_ports.items():
            print(f"Testing {service_name:20} (port {port:5})... ", end="", flush=True)

            # Test basic HTTP connectivity
            success, info, response_time = await self.test_http_endpoint(port)

            if success:
                print(f"✅ {response_time:6.1f}ms - {info}")

                # If basic HTTP works, test health endpoint
                (
                    health_success,
                    health_info,
                    health_time,
                ) = await self.test_health_endpoint(port)
                if health_success:
                    print(
                        f"    Health endpoint: ✅ {health_time:6.1f}ms - {health_info}"
                    )
                else:
                    print(f"    Health endpoint: ❌ {health_info}")

                results.append(
                    {
                        "service": service_name,
                        "port": port,
                        "status": "accessible",
                        "response_time": response_time,
                        "info": info,
                        "health_status": "healthy"
                        if health_success
                        else "no_health_endpoint",
                        "health_info": health_info if health_success else None,
                    }
                )
            else:
                print(f"❌ {info}")
                results.append(
                    {
                        "service": service_name,
                        "port": port,
                        "status": "not_accessible",
                        "error": info,
                        "response_time": response_time,
                    }
                )

        return results

    def generate_report(self, results: list[dict]):
        """Generate connectivity report"""
        accessible_services = [r for r in results if r["status"] == "accessible"]
        healthy_services = [
            r for r in accessible_services if r.get("health_status") == "healthy"
        ]

        print("\n" + "=" * 80)
        print("📊 CONNECTIVITY REPORT")
        print("=" * 80)

        print(f"🌐 Server: {self.host}")
        print(f"⚡ Total services tested: {len(results)}")
        print(f"✅ Accessible services: {len(accessible_services)}")
        print(f"🏥 Healthy services: {len(healthy_services)}")
        print(f"❌ Inaccessible services: {len(results) - len(accessible_services)}")

        if accessible_services:
            print("\n✅ ACCESSIBLE SERVICES:")
            for service in accessible_services:
                health_icon = "🏥" if service.get("health_status") == "healthy" else "⚠️"
                print(
                    f"   {health_icon} {service['service']:20} (:{service['port']}) - {service['response_time']:6.1f}ms"
                )
                if service.get("health_info"):
                    print(f"       Health: {service['health_info']}")

        inaccessible_services = [r for r in results if r["status"] == "not_accessible"]
        if inaccessible_services:
            print("\n❌ INACCESSIBLE SERVICES:")
            for service in inaccessible_services:
                print(
                    f"   ❌ {service['service']:20} (:{service['port']}) - {service['error']}"
                )

        # Save detailed report
        report_file = f"lambda_labs_connectivity_report_{int(time.time())}.json"
        with open(report_file, "w") as f:
            json.dump(
                {
                    "test_info": {
                        "host": self.host,
                        "timestamp": datetime.now().isoformat(),
                        "total_services": len(results),
                        "accessible_services": len(accessible_services),
                        "healthy_services": len(healthy_services),
                    },
                    "results": results,
                },
                f,
                indent=2,
            )

        print(f"\n📄 Detailed report saved to: {report_file}")

        return {
            "accessible": accessible_services,
            "healthy": healthy_services,
            "total": len(results),
        }


async def main():
    """Main function"""
    tester = LambdaLabsConnectivityTester()

    print("🚀 Lambda Labs Connectivity Tester")
    print("Testing all Sophia AI services and infrastructure components...")
    print()

    results = await tester.run_connectivity_tests()
    summary = tester.generate_report(results)

    print("\n🎯 QUICK ACCESS URLS:")
    for service in summary["accessible"]:
        print(f"   {service['service']}: http://{tester.host}:{service['port']}")

    if summary["healthy"]:
        print(f"\n🎉 Found {len(summary['healthy'])} healthy services!")
        print("You can use these URLs to access the running services.")
    else:
        print(
            "\n⚠️ No healthy services found. The deployment might still be in progress."
        )

    print("\n✨ Test completed. Check the JSON report for detailed results.")


if __name__ == "__main__":
    asyncio.run(main())
