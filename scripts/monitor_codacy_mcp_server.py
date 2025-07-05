#!/usr/bin/env python3
"""
Simplified Real-time Monitoring Dashboard for Codacy MCP Server
Live monitoring with health checks, performance metrics, and request statistics
"""

import asyncio
import aiohttp
import json
import time
import os
import sys
import argparse
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import statistics

@dataclass
class ServerMetrics:
    """Server performance metrics"""
    timestamp: str
    response_time_ms: float
    status_code: int
    requests_per_second: float
    error_rate: float
    uptime_seconds: float
    is_healthy: bool

@dataclass
class HealthStatus:
    """Server health status"""
    is_healthy: bool
    status_code: int
    response_time_ms: float
    error_message: Optional[str] = None
    services_status: Optional[Dict[str, bool]] = None

class CodacyMCPMonitor:
    """Real-time monitoring for Codacy MCP Server"""
    
    def __init__(self, base_url: str = "http://165.1.69.44:3008"):
        self.base_url = base_url
        self.metrics_history: List[ServerMetrics] = []
        self.start_time = time.time()
        self.request_count = 0
        self.error_count = 0
        self.response_times: List[float] = []
        self.check_interval = 2.0  # seconds
        
    async def check_health(self) -> HealthStatus:
        """Check server health"""
        try:
            start_time = time.time()
            timeout = aiohttp.ClientTimeout(total=5.0)
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(f"{self.base_url}/health") as response:
                    response_time = (time.time() - start_time) * 1000
                    
                    if response.status == 200:
                        try:
                            data = await response.json()
                            return HealthStatus(
                                is_healthy=True,
                                status_code=response.status,
                                response_time_ms=response_time,
                                services_status=data.get("services", {})
                            )
                        except json.JSONDecodeError:
                            return HealthStatus(
                                is_healthy=True,
                                status_code=response.status,
                                response_time_ms=response_time,
                                error_message="Invalid JSON response"
                            )
                    else:
                        return HealthStatus(
                            is_healthy=False,
                            status_code=response.status,
                            response_time_ms=response_time,
                            error_message=f"HTTP {response.status}"
                        )
        except asyncio.TimeoutError:
            return HealthStatus(
                is_healthy=False,
                status_code=0,
                response_time_ms=0,
                error_message="Connection timeout"
            )
        except Exception as e:
            return HealthStatus(
                is_healthy=False,
                status_code=0,
                response_time_ms=0,
                error_message=f"Connection error: {str(e)[:50]}"
            )
    
    async def test_analyze_code(self) -> Tuple[bool, float, str]:
        """Test the analyze code endpoint"""
        try:
            start_time = time.time()
            test_code = """
def example_function():
    # Test code for analysis
    x = 1
    y = 2
    return x + y
"""
            
            timeout = aiohttp.ClientTimeout(total=10.0)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    f"{self.base_url}/api/v1/analyze/code",
                    json={"code": test_code, "language": "python"}
                ) as response:
                    response_time = (time.time() - start_time) * 1000
                    
                    if response.status == 200:
                        try:
                            data = await response.json()
                            issues_count = len(data.get('issues', []))
                            return True, response_time, f"Analysis complete: {issues_count} issues found"
                        except json.JSONDecodeError:
                            return True, response_time, "Analysis complete (invalid JSON)"
                    else:
                        return False, response_time, f"HTTP {response.status}"
        except asyncio.TimeoutError:
            return False, 0, "Request timeout"
        except Exception as e:
            return False, 0, f"Error: {str(e)[:50]}"
    
    def calculate_requests_per_second(self) -> float:
        """Calculate requests per second over the last minute"""
        if len(self.metrics_history) < 2:
            return 0
        
        # Calculate RPS over the last minute or available history
        one_minute_ago = time.time() - 60
        recent_metrics = [
            m for m in self.metrics_history 
            if datetime.fromisoformat(m.timestamp).timestamp() > one_minute_ago
        ]
        
        if len(recent_metrics) < 2:
            return 0
        
        time_span = (
            datetime.fromisoformat(recent_metrics[-1].timestamp).timestamp() - 
            datetime.fromisoformat(recent_metrics[0].timestamp).timestamp()
        )
        
        if time_span > 0:
            return len(recent_metrics) / time_span
        return 0
    
    def calculate_error_rate(self) -> float:
        """Calculate error rate percentage"""
        if not self.metrics_history:
            return 0
        
        total_requests = len(self.metrics_history)
        error_requests = len([m for m in self.metrics_history if not m.is_healthy])
        
        return (error_requests / total_requests) * 100 if total_requests > 0 else 0
    
    async def collect_metrics(self) -> ServerMetrics:
        """Collect comprehensive metrics"""
        health = await self.check_health()
        
        # Update response times
        if health.is_healthy:
            self.response_times.append(health.response_time_ms)
        
        # Keep only last 100 response times for calculation
        if len(self.response_times) > 100:
            self.response_times = self.response_times[-100:]
        
        uptime = time.time() - self.start_time
        rps = self.calculate_requests_per_second()
        error_rate = self.calculate_error_rate()
        
        metrics = ServerMetrics(
            timestamp=datetime.now().isoformat(),
            response_time_ms=health.response_time_ms,
            status_code=health.status_code,
            requests_per_second=rps,
            error_rate=error_rate,
            uptime_seconds=uptime,
            is_healthy=health.is_healthy
        )
        
        self.metrics_history.append(metrics)
        
        # Keep only last 200 metrics for memory efficiency
        if len(self.metrics_history) > 200:
            self.metrics_history = self.metrics_history[-200:]
        
        return metrics
    
    def print_dashboard(self, metrics: ServerMetrics, health: HealthStatus):
        """Print live dashboard"""
        # Clear screen
        os.system('clear' if os.name == 'posix' else 'cls')
        
        print("🔍 " + "="*80)
        print("🔍 CODACY MCP SERVER - LIVE MONITORING DASHBOARD")
        print("🔍 " + "="*80)
        print()
        
        # Health Status
        status_emoji = "✅" if health.is_healthy else "❌"
        print(f"📊 SERVER STATUS: {status_emoji} {'HEALTHY' if health.is_healthy else 'UNHEALTHY'}")
        print(f"🌐 Base URL: {self.base_url}")
        print(f"⏰ Last Check: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🕐 Uptime: {timedelta(seconds=int(metrics.uptime_seconds))}")
        
        if not health.is_healthy and health.error_message:
            print(f"❌ Error: {health.error_message}")
        
        print()
        
        # Response Metrics
        print("📈 RESPONSE METRICS:")
        print(f"   Status Code: {metrics.status_code}")
        print(f"   Response Time: {metrics.response_time_ms:.2f}ms")
        
        if self.response_times:
            avg_response = statistics.mean(self.response_times)
            print(f"   Average Response Time: {avg_response:.2f}ms")
            print(f"   Min Response Time: {min(self.response_times):.2f}ms")
            print(f"   Max Response Time: {max(self.response_times):.2f}ms")
        
        print()
        
        # Performance Metrics
        print("⚡ PERFORMANCE METRICS:")
        print(f"   Requests/Second: {metrics.requests_per_second:.2f}")
        print(f"   Error Rate: {metrics.error_rate:.2f}%")
        print(f"   Total Checks: {len(self.metrics_history)}")
        
        healthy_count = len([m for m in self.metrics_history if m.is_healthy])
        unhealthy_count = len(self.metrics_history) - healthy_count
        print(f"   Healthy Checks: {healthy_count}")
        print(f"   Unhealthy Checks: {unhealthy_count}")
        
        print()
        
        # Service Status
        if health.services_status:
            print("🔗 SERVICES STATUS:")
            for service, status in health.services_status.items():
                status_icon = "✅" if status else "❌"
                print(f"   {service}: {status_icon}")
            print()
        
        # Recent Activity
        if len(self.metrics_history) >= 5:
            print("📊 RECENT ACTIVITY (Last 5 checks):")
            for i, m in enumerate(self.metrics_history[-5:], 1):
                timestamp = datetime.fromisoformat(m.timestamp).strftime('%H:%M:%S')
                status_icon = "✅" if m.is_healthy else "❌"
                print(f"   {i}. {timestamp} - {status_icon} {m.status_code} - {m.response_time_ms:.1f}ms")
            print()
        
        # Performance Trend
        if len(self.metrics_history) >= 10:
            recent_response_times = [m.response_time_ms for m in self.metrics_history[-10:] if m.is_healthy]
            if recent_response_times:
                trend = "📈" if recent_response_times[-1] > recent_response_times[0] else "📉"
                avg_recent = statistics.mean(recent_response_times)
                print(f"📊 PERFORMANCE TREND: {trend} {avg_recent:.1f}ms average (last 10 checks)")
                print()
        
        # Controls
        print("🎮 CONTROLS:")
        print("   Press Ctrl+C to stop monitoring")
        print("   Refresh rate: 2 seconds")
        print("="*80)
    
    async def run_monitoring(self):
        """Run continuous monitoring"""
        print("🚀 Starting Codacy MCP Server Monitoring...")
        print("📊 Initializing metrics collection...")
        
        try:
            while True:
                metrics = await self.collect_metrics()
                health = await self.check_health()
                self.print_dashboard(metrics, health)
                
                await asyncio.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            print("\n\n🛑 Monitoring stopped by user")
            await self.generate_report()
        except Exception as e:
            print(f"\n❌ Error in monitoring: {e}")
            await self.generate_report()
    
    async def generate_report(self):
        """Generate monitoring report"""
        if not self.metrics_history:
            print("No metrics collected.")
            return
        
        print("\n📋 MONITORING REPORT")
        print("="*50)
        
        # Summary statistics
        healthy_metrics = [m for m in self.metrics_history if m.is_healthy]
        response_times = [m.response_time_ms for m in healthy_metrics]
        
        if response_times:
            print(f"Average Response Time: {statistics.mean(response_times):.2f}ms")
            print(f"Min Response Time: {min(response_times):.2f}ms")
            print(f"Max Response Time: {max(response_times):.2f}ms")
        
        total_checks = len(self.metrics_history)
        healthy_checks = len(healthy_metrics)
        success_rate = (healthy_checks / total_checks) * 100 if total_checks > 0 else 0
        
        print(f"Success Rate: {success_rate:.2f}%")
        print(f"Total Checks: {total_checks}")
        print(f"Healthy Checks: {healthy_checks}")
        print(f"Unhealthy Checks: {total_checks - healthy_checks}")
        print(f"Total Monitoring Time: {timedelta(seconds=int(time.time() - self.start_time))}")
        
        # Save detailed report
        report_file = f"codacy_monitoring_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            with open(report_file, 'w') as f:
                json.dump({
                    "summary": {
                        "total_checks": total_checks,
                        "healthy_checks": healthy_checks,
                        "success_rate": success_rate,
                        "average_response_time": statistics.mean(response_times) if response_times else 0,
                        "monitoring_duration": time.time() - self.start_time
                    },
                    "metrics": [asdict(m) for m in self.metrics_history]
                }, f, indent=2)
            
            print(f"📄 Detailed report saved to: {report_file}")
        except Exception as e:
            print(f"❌ Could not save report: {e}")

async def main():
    """Main monitoring function"""
    parser = argparse.ArgumentParser(description="Codacy MCP Server Monitoring")
    parser.add_argument("--local", action="store_true", help="Use local server")
    args = parser.parse_args()

    base_url = "http://165.1.69.44:3008" if not args.local else "http://localhost:3008"
    monitor = CodacyMCPMonitor(base_url)
    
    # Test initial connection
    print("🔍 Testing connection to Codacy MCP Server...")
    health = await monitor.check_health()
    
    if not health.is_healthy:
        print(f"❌ Cannot connect to Codacy MCP Server at {monitor.base_url}")
        print(f"   Error: {health.error_message}")
        print("   Please ensure the server is running on port 3008")
        return
    
    print("✅ Connection successful!")
    print(f"   Status Code: {health.status_code}")
    print(f"   Response Time: {health.response_time_ms:.2f}ms")
    
    if health.services_status:
        print("   Services:")
        for service, status in health.services_status.items():
            status_icon = "✅" if status else "❌"
            print(f"     {service}: {status_icon}")
    
    print()
    
    # Test analyze code endpoint
    print("🧪 Testing analyze code endpoint...")
    success, response_time, message = await monitor.test_analyze_code()
    if success:
        print(f"✅ Analyze code endpoint working - {response_time:.2f}ms")
        print(f"   {message}")
    else:
        print(f"❌ Analyze code endpoint failed - {message}")
    
    print("\n🚀 Starting live monitoring in 2 seconds...")
    await asyncio.sleep(2)
    
    await monitor.run_monitoring()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Monitoring stopped by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1) 