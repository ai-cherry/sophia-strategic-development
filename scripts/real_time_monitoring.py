#!/usr/bin/env python3
"""
Real-Time Monitoring Dashboard for Sophia AI
Provides continuous monitoring with live updates
"""

import asyncio
import os
import statistics
import time
from datetime import datetime
from typing import Any

import aiohttp

class RealTimeMonitor:
    def __init__(self):
        self.services = {
            "api_gateway": {
                "url": "http://localhost:8000/health",
                "name": "API Gateway",
                "port": 8000,
            },
            "ai_memory": {
                "url": "http://localhost:9001/health",
                "name": "AI Memory MCP",
                "port": 9001,
            },
            "codacy": {
                "url": "http://localhost:3008/health",
                "name": "Codacy MCP",
                "port": 3008,
            },
            "github": {
                "url": "http://localhost:9003/health",
                "name": "GitHub MCP",
                "port": 9003,
            },
            "linear": {
                "url": "http://localhost:9004/health",
                "name": "Linear MCP",
                "port": 9004,
            },
        }
        self.metrics_history = []
        self.running = True

    def clear_screen(self):
        """Clear the terminal screen"""
        os.system("clear" if os.name == "posix" else "cls")

    async def check_all_services(self) -> dict[str, Any]:
        """Check all services and return comprehensive status"""
        start_time = time.time()
        results = {
            "timestamp": datetime.now().isoformat(),
            "services": {},
            "summary": {},
        }

        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=5)
        ) as session:
            tasks = []
            for service_id, service_info in self.services.items():
                task = self.check_service(session, service_id, service_info)
                tasks.append(task)

            service_results = await asyncio.gather(*tasks, return_exceptions=True)

            healthy_count = 0
            total_response_time = 0

            for i, (service_id, service_info) in enumerate(self.services.items()):
                result = service_results[i]

                if isinstance(result, Exception):
                    results["services"][service_id] = {
                        "status": "error",
                        "error": str(result),
                        "response_time": None,
                        "name": service_info["name"],
                    }
                else:
                    results["services"][service_id] = result
                    if result["status"] == "healthy":
                        healthy_count += 1
                        total_response_time += result["response_time"]

        # Calculate summary metrics
        execution_time = (time.time() - start_time) * 1000
        health_percentage = (healthy_count / len(self.services)) * 100
        avg_response_time = total_response_time / max(healthy_count, 1)

        results["summary"] = {
            "health_percentage": round(health_percentage, 1),
            "avg_response_time": round(avg_response_time, 2),
            "healthy_services": healthy_count,
            "total_services": len(self.services),
            "check_duration": round(execution_time, 2),
            "performance_grade": self.calculate_grade(
                avg_response_time, health_percentage
            ),
        }

        # Store metrics
        self.metrics_history.append(
            {
                "timestamp": results["timestamp"],
                "health_percentage": health_percentage,
                "avg_response_time": avg_response_time,
            }
        )

        # Keep only last 50 measurements
        if len(self.metrics_history) > 50:
            self.metrics_history = self.metrics_history[-50:]

        return results

    async def check_service(
        self, session: aiohttp.ClientSession, service_id: str, service_info: dict
    ) -> dict[str, Any]:
        """Check individual service"""
        start_time = time.time()

        try:
            async with session.get(service_info["url"]) as response:
                response_time = (time.time() - start_time) * 1000

                if response.status == 200:
                    return {
                        "status": "healthy",
                        "response_time": round(response_time, 2),
                        "status_code": response.status,
                        "name": service_info["name"],
                        "port": service_info["port"],
                    }
                else:
                    return {
                        "status": "unhealthy",
                        "response_time": round(response_time, 2),
                        "status_code": response.status,
                        "name": service_info["name"],
                        "port": service_info["port"],
                        "error": f"HTTP {response.status}",
                    }

        except Exception as e:
            return {
                "status": "error",
                "response_time": None,
                "name": service_info["name"],
                "port": service_info["port"],
                "error": str(e),
            }

    def calculate_grade(
        self, avg_response_time: float, health_percentage: float
    ) -> str:
        """Calculate performance grade"""
        if health_percentage == 100 and avg_response_time < 100:
            return "A+"
        elif health_percentage >= 90 and avg_response_time < 500:
            return "A"
        elif health_percentage >= 80 and avg_response_time < 1000:
            return "B"
        elif health_percentage >= 70:
            return "C"
        else:
            return "D"

    def get_status_icon(self, status: str) -> str:
        """Get status icon"""
        icons = {"healthy": "🟢", "unhealthy": "��", "error": "🔴", "timeout": "⚫"}
        return icons.get(status, "❓")

    def display_dashboard(self, results: dict[str, Any]):
        """Display the monitoring dashboard"""
        self.clear_screen()

        # Header

        # Overall Status
        summary = results["summary"]
        (
            "🟢"
            if summary["health_percentage"] == 100
            else "🟡"
            if summary["health_percentage"] >= 80
            else "🔴"
        )

        # Service Details
        for service_data in results["services"].values():
            self.get_status_icon(service_data["status"])
            service_data["name"]
            service_data["port"]

            if service_data["status"] == "healthy":
                service_data["response_time"]
            else:
                service_data.get("error", "Unknown error")[:30]

        # Trends (if we have history)
        if len(self.metrics_history) > 1:
            recent_health = [m["health_percentage"] for m in self.metrics_history[-10:]]
            recent_response = [
                m["avg_response_time"] for m in self.metrics_history[-10:]
            ]

            statistics.mean(recent_health)
            statistics.mean(recent_response)

            (
                "📈"
                if recent_health[-1] > recent_health[0]
                else "📉"
                if recent_health[-1] < recent_health[0]
                else "➡️"
            )
            (
                "📈"
                if recent_response[-1] > recent_response[0]
                else "📉"
                if recent_response[-1] < recent_response[0]
                else "➡️"
            )

        # Controls

    async def run_monitoring(self):
        """Run continuous monitoring"""

        try:
            while self.running:
                # Check all services
                results = await self.check_all_services()

                # Display dashboard
                self.display_dashboard(results)

                # Wait before next check
                await asyncio.sleep(5)

        except KeyboardInterrupt:
            self.running = False
        except Exception:
            self.running = False

async def main():
    """Main function"""
    monitor = RealTimeMonitor()
    await monitor.run_monitoring()

if __name__ == "__main__":
    asyncio.run(main())
