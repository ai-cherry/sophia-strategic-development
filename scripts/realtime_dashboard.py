#!/usr/bin/env python3
"""Real-time monitoring dashboard for Sophia AI infrastructure."""

import asyncio
import os
import time
from datetime import datetime
from typing import Any

import requests


class SophiaRealtimeDashboard:
    """Real-time dashboard for monitoring Sophia AI services."""

    def __init__(self):
        self.services = {
            "api_gateway": {
                "url": "http://localhost:8000",
                "name": "API Gateway",
                "icon": "🌐",
            },
            "ai_memory": {
                "url": "http://localhost:9001",
                "name": "AI Memory",
                "icon": "🧠",
            },
            "codacy": {"url": "http://localhost:3008", "name": "Codacy", "icon": "🔍"},
            "github": {"url": "http://localhost:9003", "name": "GitHub", "icon": "📁"},
            "linear": {"url": "http://localhost:9004", "name": "Linear", "icon": "📋"},
        }

        self.metrics_history = {service: [] for service in self.services.keys()}
        self.start_time = time.time()

    def clear_screen(self):
        """Clear the terminal screen."""
        os.system("clear" if os.name == "posix" else "cls")

    async def get_service_metrics(self, service_key: str) -> dict[str, Any]:
        """Get current metrics for a service."""
        service = self.services[service_key]
        start_time = time.time()

        try:
            response = requests.get(f"{service['url']}/health", timeout=3)
            response_time = (time.time() - start_time) * 1000

            if response.status_code == 200:
                return {
                    "status": "healthy",
                    "response_time": response_time,
                    "timestamp": datetime.now(),
                    "details": response.json(),
                }
            else:
                return {
                    "status": "unhealthy",
                    "response_time": response_time,
                    "timestamp": datetime.now(),
                    "error": f"HTTP {response.status_code}",
                }
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return {
                "status": "error",
                "response_time": response_time,
                "timestamp": datetime.now(),
                "error": str(e),
            }

    async def collect_all_metrics(self) -> dict[str, Any]:
        """Collect metrics from all services."""
        tasks = [self.get_service_metrics(service) for service in self.services.keys()]
        results = await asyncio.gather(*tasks)

        metrics = {}
        for i, service_key in enumerate(self.services.keys()):
            metrics[service_key] = results[i]

            # Store in history (keep last 50 measurements)
            self.metrics_history[service_key].append(results[i])
            if len(self.metrics_history[service_key]) > 50:
                self.metrics_history[service_key].pop(0)

        return metrics

    def get_status_icon(self, status: str) -> str:
        """Get status icon."""
        if status == "healthy":
            return "✅"
        elif status == "unhealthy":
            return "⚠️"
        else:
            return "❌"

    def get_response_time_grade(self, response_time: float) -> tuple:
        """Get response time grade and color."""
        if response_time < 5:
            return "A+", "🟢"
        elif response_time < 10:
            return "A", "🟢"
        elif response_time < 25:
            return "B", "🟡"
        elif response_time < 50:
            return "C", "🟠"
        else:
            return "D", "🔴"

    def calculate_uptime(self, service_key: str) -> float:
        """Calculate uptime percentage for a service."""
        history = self.metrics_history[service_key]
        if not history:
            return 100.0

        healthy_count = len([m for m in history if m["status"] == "healthy"])
        return (healthy_count / len(history)) * 100

    def get_average_response_time(self, service_key: str) -> float:
        """Get average response time for a service."""
        history = self.metrics_history[service_key]
        if not history:
            return 0.0

        response_times = [
            m["response_time"] for m in history if m["status"] == "healthy"
        ]
        return sum(response_times) / len(response_times) if response_times else 0.0

    def render_dashboard(self, metrics: dict[str, Any]):
        """Render the real-time dashboard."""
        self.clear_screen()

        # Header
        uptime = time.time() - self.start_time
        uptime_str = f"{int(uptime // 60)}m {int(uptime % 60)}s"

        print("🚀 SOPHIA AI REAL-TIME DASHBOARD")
        print("=" * 80)
        print(
            f"⏰ Uptime: {uptime_str} | 🔄 Updated: {datetime.now().strftime('%H:%M:%S')}"
        )
        print()

        # Overall status
        healthy_services = len(
            [m for m in metrics.values() if m["status"] == "healthy"]
        )
        total_services = len(metrics)
        overall_health = (healthy_services / total_services) * 100

        health_icon = (
            "🟢" if overall_health == 100 else "🟡" if overall_health >= 80 else "🔴"
        )
        print(
            f"🏥 OVERALL HEALTH: {health_icon} {overall_health:.1f}% ({healthy_services}/{total_services} services)"
        )

        # Average response time
        avg_response_times = [
            m["response_time"] for m in metrics.values() if m["status"] == "healthy"
        ]
        if avg_response_times:
            overall_avg = sum(avg_response_times) / len(avg_response_times)
            grade, grade_icon = self.get_response_time_grade(overall_avg)
            print(
                f"⚡ AVERAGE RESPONSE: {grade_icon} {overall_avg:.1f}ms (Grade: {grade})"
            )

        print()
        print("📊 SERVICE STATUS")
        print("-" * 80)

        # Service details
        for service_key, service in self.services.items():
            metric = metrics[service_key]
            status_icon = self.get_status_icon(metric["status"])

            # Service name and status
            service_line = f"{service['icon']} {service['name']:<15} {status_icon}"

            if metric["status"] == "healthy":
                response_time = metric["response_time"]
                grade, grade_icon = self.get_response_time_grade(response_time)
                uptime = self.calculate_uptime(service_key)
                avg_response = self.get_average_response_time(service_key)

                service_line += f" {response_time:>6.1f}ms {grade_icon} {grade:<2} | "
                service_line += f"Uptime: {uptime:>5.1f}% | Avg: {avg_response:>5.1f}ms"
            else:
                error = metric.get("error", "Unknown error")
                service_line += f" ERROR: {error[:40]}..."

            print(service_line)

        print()
        print("📈 PERFORMANCE TRENDS (Last 10 measurements)")
        print("-" * 80)

        for service_key, service in self.services.items():
            history = self.metrics_history[service_key][-10:]  # Last 10
            if not history:
                continue

            response_times = [
                m["response_time"] for m in history if m["status"] == "healthy"
            ]
            if response_times:
                min_time = min(response_times)
                max_time = max(response_times)
                avg_time = sum(response_times) / len(response_times)

                # Create simple ASCII chart
                chart = ""
                for m in history:
                    if m["status"] == "healthy":
                        if m["response_time"] < 5:
                            chart += "█"
                        elif m["response_time"] < 10:
                            chart += "▇"
                        elif m["response_time"] < 25:
                            chart += "▅"
                        else:
                            chart += "▃"
                    else:
                        chart += "░"

                print(
                    f"{service['icon']} {service['name']:<15} [{chart:<10}] "
                    f"Min: {min_time:>5.1f}ms | Max: {max_time:>5.1f}ms | Avg: {avg_time:>5.1f}ms"
                )

        print()
        print("🔧 SYSTEM INFORMATION")
        print("-" * 80)

        # Calculate system metrics
        total_measurements = sum(
            len(history) for history in self.metrics_history.values()
        )
        healthy_measurements = sum(
            len([m for m in history if m["status"] == "healthy"])
            for history in self.metrics_history.values()
        )

        if total_measurements > 0:
            system_reliability = (healthy_measurements / total_measurements) * 100
            print(
                f"📊 System Reliability: {system_reliability:.2f}% ({healthy_measurements}/{total_measurements} checks)"
            )

        # Performance classification
        if avg_response_times:
            overall_avg = sum(avg_response_times) / len(avg_response_times)
            if overall_avg < 5:
                perf_class = "🚀 EXCEPTIONAL"
            elif overall_avg < 10:
                perf_class = "⚡ EXCELLENT"
            elif overall_avg < 25:
                perf_class = "✅ GOOD"
            elif overall_avg < 50:
                perf_class = "🟡 FAIR"
            else:
                perf_class = "🔴 POOR"

            print(f"🎯 Performance Class: {perf_class}")

        print(f"📏 Measurements Collected: {total_measurements}")
        print(f"📊 Services Monitored: {len(self.services)}")

        print()
        print("⌨️  Press Ctrl+C to stop monitoring")

    async def run_dashboard(self, refresh_interval: int = 2):
        """Run the real-time dashboard."""
        print("🚀 Starting Sophia AI Real-time Dashboard...")
        print(f"📊 Refresh interval: {refresh_interval} seconds")
        print("⏳ Loading initial metrics...")

        try:
            while True:
                metrics = await self.collect_all_metrics()
                self.render_dashboard(metrics)
                await asyncio.sleep(refresh_interval)

        except KeyboardInterrupt:
            print("\n\n🛑 Dashboard stopped by user")
            print("📊 Final Statistics:")

            total_measurements = sum(
                len(history) for history in self.metrics_history.values()
            )
            healthy_measurements = sum(
                len([m for m in history if m["status"] == "healthy"])
                for history in self.metrics_history.values()
            )

            if total_measurements > 0:
                system_reliability = (healthy_measurements / total_measurements) * 100
                print(f"   System Reliability: {system_reliability:.2f}%")
                print(f"   Total Measurements: {total_measurements}")
                print(
                    f"   Monitoring Duration: {int((time.time() - self.start_time) // 60)} minutes"
                )

            print("\n✅ Dashboard session complete!")


async def main():
    """Main dashboard function."""
    dashboard = SophiaRealtimeDashboard()
    await dashboard.run_dashboard(refresh_interval=2)


if __name__ == "__main__":
    asyncio.run(main())
