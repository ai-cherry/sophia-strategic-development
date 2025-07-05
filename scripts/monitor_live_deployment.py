#!/usr/bin/env python3
"""
Live Deployment Monitor for Sophia AI
====================================

Monitors the live deployment progress without interfering with the deployment process.
"""

import asyncio
import os
import subprocess
from datetime import datetime

import aiohttp


class LiveDeploymentMonitor:
    """Monitor live deployment progress"""

    def __init__(self):
        self.instances = {
            "platform": "146.235.200.1",
            "mcp": "165.1.69.44",
            "ai": "137.131.6.213",
        }

        self.endpoints = {
            "platform": "http://146.235.200.1:8000/health",
            "mcp": "http://165.1.69.44:3008/health",
            "ai": "http://137.131.6.213:9030/health",
        }

    def print_status_header(self):
        """Print monitoring header"""
        print("\n" + "=" * 60)
        print("📊 SOPHIA AI LIVE DEPLOYMENT MONITOR")
        print("=" * 60)
        print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

    def check_deployment_process(self):
        """Check if deployment process is still running"""
        try:
            result = subprocess.run(["ps", "aux"], capture_output=True, text=True)
            return "deploy_sophia_complete_platform.py" in result.stdout
        except:
            return False

    async def test_endpoint_health(self, endpoint: str) -> tuple:
        """Test single endpoint health"""
        try:
            timeout = aiohttp.ClientTimeout(total=3)
            async with aiohttp.ClientSession() as session:
                async with session.get(endpoint, timeout=timeout) as response:
                    return True, response.status
        except:
            return False, None

    async def check_all_services(self):
        """Check health of all services"""
        results = {}
        for name, endpoint in self.endpoints.items():
            healthy, status = await self.test_endpoint_health(endpoint)
            results[name] = {"healthy": healthy, "status": status, "endpoint": endpoint}
        return results

    def check_for_reports(self):
        """Check for new deployment reports"""
        try:
            reports = []
            for file in os.listdir("."):
                if file.startswith("deployment_report_") and file.endswith(".json"):
                    reports.append(file)
            return sorted(reports)[-1] if reports else None
        except:
            return None

    def print_service_status(self, results):
        """Print service status"""
        print("🌐 Service Health Status:")
        healthy_count = 0
        total_count = len(results)

        for name, result in results.items():
            status_emoji = "✅" if result["healthy"] else "❌"
            status_text = (
                f"HTTP {result['status']}" if result["status"] else "No Response"
            )
            print(f"   {status_emoji} {name.title()}: {status_text}")
            if result["healthy"]:
                healthy_count += 1

        print(f"\n📈 Overall: {healthy_count}/{total_count} services healthy")

        if healthy_count == total_count:
            print("🎉 ALL SERVICES HEALTHY! Deployment appears successful!")
        elif healthy_count > 0:
            print("🔄 Partial deployment - some services responding")
        else:
            print("⏳ Deployment in progress - no services responding yet")

    async def monitor_deployment(self):
        """Main monitoring loop"""
        print("🚀 Starting live deployment monitoring...")
        print("   Press Ctrl+C to stop monitoring")

        try:
            while True:
                self.print_status_header()

                # Check if deployment process is running
                process_running = self.check_deployment_process()
                print(
                    f"🔧 Deployment Process: {'🔄 Running' if process_running else '✅ Completed'}"
                )

                # Check for deployment reports
                latest_report = self.check_for_reports()
                if latest_report:
                    print(f"📄 Latest Report: {latest_report}")

                # Test service health
                print("\n" + "-" * 40)
                results = await self.check_all_services()
                self.print_service_status(results)

                # Check GitHub Actions status
                print("\n🔗 Monitoring URLs:")
                print(
                    "   GitHub Actions: https://github.com/ai-cherry/sophia-main/actions"
                )
                print(
                    "   Lambda Labs Dashboard: https://cloud.lambdalabs.com/instances"
                )

                # Show service URLs for when they're ready
                print("\n🎯 Service URLs (when ready):")
                for name, endpoint in self.endpoints.items():
                    print(f"   {name.title()}: {endpoint}")

                # If all services are healthy, show success and exit
                healthy_count = sum(1 for r in results.values() if r["healthy"])
                if healthy_count == len(results):
                    print("\n🎉 DEPLOYMENT SUCCESSFUL!")
                    print("   All services are healthy and responding")
                    break

                print(
                    f"\n⏳ Next check in 30 seconds... (Process: {'Running' if process_running else 'Done'})"
                )
                await asyncio.sleep(30)

        except KeyboardInterrupt:
            print("\n\n⏹️  Monitoring stopped by user")
            print("   Deployment may still be running in background")


async def main():
    """Main function"""
    monitor = LiveDeploymentMonitor()
    await monitor.monitor_deployment()


if __name__ == "__main__":
    asyncio.run(main())
