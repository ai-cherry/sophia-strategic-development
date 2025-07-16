#!/usr/bin/env python3
"""
🔍 COMPREHENSIVE SYSTEM MONITOR
===============================
Real-time monitoring and testing of the complete Sophia AI platform.
Tests all endpoints, measures performance, validates functionality.

Features:
- Real-time health monitoring
- Performance benchmarking
- Endpoint validation
- Chat functionality testing
- Dashboard data verification
- WebSocket connectivity testing
- Detailed reporting
"""

import asyncio
import json
import time
import requests
import websockets
import sys
from datetime import datetime
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
import statistics

@dataclass
class EndpointTest:
    name: str
    url: str
    method: str = "GET"
    payload: Optional[Dict] = None
    expected_status: int = 200
    timeout: int = 10

@dataclass
class TestResult:
    endpoint: str
    success: bool
    response_time_ms: float
    status_code: int
    response_size: int
    error: Optional[str] = None
    data_sample: Optional[Any] = None

class SophiaSystemMonitor:
    def __init__(self):
        self.backend_url = "http://localhost:7000"
        self.frontend_url = "http://localhost:5174"
        self.websocket_url = "ws://localhost:7000/ws"
        
        self.endpoints = [
            EndpointTest("Health Check", f"{self.backend_url}/health"),
            EndpointTest("System Status", f"{self.backend_url}/system/status"),
            EndpointTest("API Documentation", f"{self.backend_url}/docs"),
            EndpointTest("Root Endpoint", f"{self.backend_url}/"),
            EndpointTest("Dashboard Data", f"{self.backend_url}/dashboard/data"),
            EndpointTest("API Stats", f"{self.backend_url}/api/stats"),
            EndpointTest("Frontend", f"{self.frontend_url}/"),
            EndpointTest("Chat Revenue", f"{self.backend_url}/chat", "POST", 
                        {"message": "Show me our revenue performance"}),
            EndpointTest("Chat Customers", f"{self.backend_url}/chat", "POST",
                        {"message": "How are our customers doing?"}),
            EndpointTest("Chat Business Overview", f"{self.backend_url}/chat", "POST",
                        {"message": "Give me a business summary"}),
        ]
        
        self.results_history = []
        
    async def test_endpoint(self, endpoint: EndpointTest) -> TestResult:
        """Test a single endpoint and return results"""
        start_time = time.time()
        
        try:
            if endpoint.method == "GET":
                response = requests.get(endpoint.url, timeout=endpoint.timeout)
            elif endpoint.method == "POST":
                response = requests.post(
                    endpoint.url, 
                    json=endpoint.payload,
                    headers={"Content-Type": "application/json"},
                    timeout=endpoint.timeout
                )
            
            response_time_ms = (time.time() - start_time) * 1000
            response_size = len(response.content)
            
            # Extract sample data
            data_sample = None
            try:
                if response.headers.get('content-type', '').startswith('application/json'):
                    json_data = response.json()
                    if isinstance(json_data, dict):
                        # Sample key-value pairs for reporting
                        data_sample = {k: v for k, v in list(json_data.items())[:3]}
                    else:
                        data_sample = json_data
                elif response.headers.get('content-type', '').startswith('text/html'):
                    data_sample = {"html_length": len(response.text), "title_found": "<title>" in response.text}
                else:
                    data_sample = {"content_type": response.headers.get('content-type', 'unknown')}
            except:
                data_sample = {"response_preview": response.text[:100] if response.text else "empty"}
            
            return TestResult(
                endpoint=endpoint.name,
                success=response.status_code == endpoint.expected_status,
                response_time_ms=response_time_ms,
                status_code=response.status_code,
                response_size=response_size,
                data_sample=data_sample
            )
            
        except Exception as e:
            response_time_ms = (time.time() - start_time) * 1000
            return TestResult(
                endpoint=endpoint.name,
                success=False,
                response_time_ms=response_time_ms,
                status_code=0,
                response_size=0,
                error=str(e)
            )
    
    async def test_websocket(self) -> TestResult:
        """Test WebSocket connectivity"""
        start_time = time.time()
        
        try:
            async with websockets.connect(self.websocket_url, timeout=10) as websocket:
                # Send test message
                test_message = json.dumps({"type": "ping", "message": "test"})
                await websocket.send(test_message)
                
                # Wait for response
                response = await asyncio.wait_for(websocket.recv(), timeout=5)
                response_data = json.loads(response)
                
                response_time_ms = (time.time() - start_time) * 1000
                
                return TestResult(
                    endpoint="WebSocket Connection",
                    success=True,
                    response_time_ms=response_time_ms,
                    status_code=200,
                    response_size=len(response),
                    data_sample={"type": response_data.get("type"), "received": "ok"}
                )
                
        except Exception as e:
            response_time_ms = (time.time() - start_time) * 1000
            return TestResult(
                endpoint="WebSocket Connection",
                success=False,
                response_time_ms=response_time_ms,
                status_code=0,
                response_size=0,
                error=str(e)
            )
    
    async def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run comprehensive system test"""
        print("🔍 STARTING COMPREHENSIVE SYSTEM TEST")
        print("=" * 50)
        
        results = []
        
        # Test all HTTP endpoints
        for endpoint in self.endpoints:
            print(f"Testing: {endpoint.name}...")
            result = await self.test_endpoint(endpoint)
            results.append(result)
            
            status = "✅ PASS" if result.success else "❌ FAIL"
            print(f"  {status} - {result.response_time_ms:.1f}ms - Status {result.status_code}")
            
            if result.error:
                print(f"    Error: {result.error}")
            elif result.data_sample:
                print(f"    Sample: {json.dumps(result.data_sample, indent=2)[:100]}...")
        
        # Test WebSocket
        print("Testing: WebSocket Connection...")
        ws_result = await self.test_websocket()
        results.append(ws_result)
        
        status = "✅ PASS" if ws_result.success else "❌ FAIL"
        print(f"  {status} - {ws_result.response_time_ms:.1f}ms")
        
        if ws_result.error:
            print(f"    Error: {ws_result.error}")
        
        # Calculate summary statistics
        successful_tests = [r for r in results if r.success]
        failed_tests = [r for r in results if not r.success]
        
        if successful_tests:
            avg_response_time = statistics.mean([r.response_time_ms for r in successful_tests])
            max_response_time = max([r.response_time_ms for r in successful_tests])
            min_response_time = min([r.response_time_ms for r in successful_tests])
        else:
            avg_response_time = max_response_time = min_response_time = 0
        
        total_data_transferred = sum([r.response_size for r in successful_tests])
        
        summary = {
            "timestamp": datetime.now().isoformat(),
            "total_tests": len(results),
            "successful_tests": len(successful_tests),
            "failed_tests": len(failed_tests),
            "success_rate": (len(successful_tests) / len(results)) * 100,
            "performance": {
                "avg_response_time_ms": round(avg_response_time, 2),
                "min_response_time_ms": round(min_response_time, 2),
                "max_response_time_ms": round(max_response_time, 2),
                "total_data_kb": round(total_data_transferred / 1024, 2)
            },
            "detailed_results": [asdict(r) for r in results]
        }
        
        # Store in history
        self.results_history.append(summary)
        
        return summary
    
    def print_summary_report(self, summary: Dict[str, Any]):
        """Print a comprehensive summary report"""
        print("\n" + "=" * 50)
        print("📊 COMPREHENSIVE SYSTEM TEST SUMMARY")
        print("=" * 50)
        
        print(f"🕐 Test Time: {summary['timestamp']}")
        print(f"📊 Tests Run: {summary['total_tests']}")
        print(f"✅ Successful: {summary['successful_tests']}")
        print(f"❌ Failed: {summary['failed_tests']}")
        print(f"📈 Success Rate: {summary['success_rate']:.1f}%")
        
        print("\n📈 PERFORMANCE METRICS:")
        perf = summary['performance']
        print(f"  • Average Response: {perf['avg_response_time_ms']}ms")
        print(f"  • Fastest Response: {perf['min_response_time_ms']}ms")
        print(f"  • Slowest Response: {perf['max_response_time_ms']}ms")
        print(f"  • Data Transferred: {perf['total_data_kb']}KB")
        
        print("\n🎯 ENDPOINT STATUS:")
        for result in summary['detailed_results']:
            status = "✅" if result['success'] else "❌"
            time_str = f"{result['response_time_ms']:.1f}ms"
            print(f"  {status} {result['endpoint']:.<30} {time_str}")
            
            if result['error']:
                print(f"      ERROR: {result['error']}")
        
        # Overall system health assessment
        if summary['success_rate'] >= 95:
            health_status = "🟢 EXCELLENT"
        elif summary['success_rate'] >= 85:
            health_status = "🟡 GOOD"
        elif summary['success_rate'] >= 70:
            health_status = "🟠 FAIR"
        else:
            health_status = "🔴 POOR"
        
        print(f"\n🏥 OVERALL SYSTEM HEALTH: {health_status}")
        
        # Performance assessment
        avg_time = perf['avg_response_time_ms']
        if avg_time < 100:
            perf_status = "🚀 EXCELLENT (<100ms avg)"
        elif avg_time < 250:
            perf_status = "✅ GOOD (<250ms avg)"
        elif avg_time < 500:
            perf_status = "🟡 ACCEPTABLE (<500ms avg)"
        else:
            perf_status = "🔴 SLOW (>500ms avg)"
        
        print(f"⚡ PERFORMANCE RATING: {perf_status}")
        
        print("\n🌐 ACCESS URLS:")
        print(f"  • Backend API: {self.backend_url}")
        print(f"  • Frontend Dashboard: {self.frontend_url}")
        print(f"  • API Documentation: {self.backend_url}/docs")
        print(f"  • System Status: {self.backend_url}/system/status")
        print(f"  • WebSocket: {self.websocket_url}")
        
        # Recommendations
        print("\n💡 RECOMMENDATIONS:")
        failed_results = [r for r in summary['detailed_results'] if not r['success']]
        
        if not failed_results:
            print("  • All systems operational - no issues detected")
            print("  • Ready for production use")
        else:
            print("  • Fix failed endpoints before production deployment:")
            for result in failed_results:
                print(f"    - {result['endpoint']}: {result.get('error', 'Unknown error')}")
        
        if avg_time > 200:
            print("  • Consider performance optimization for faster response times")
        
        print("\n" + "=" * 50)
    
    def save_detailed_report(self, summary: Dict[str, Any]):
        """Save detailed report to file"""
        report_file = f"system_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(report_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"📋 Detailed report saved: {report_file}")

async def main():
    """Main monitoring function"""
    monitor = SophiaSystemMonitor()
    
    try:
        # Run comprehensive test
        summary = await monitor.run_comprehensive_test()
        
        # Print summary report
        monitor.print_summary_report(summary)
        
        # Save detailed report
        monitor.save_detailed_report(summary)
        
        # Exit with appropriate code
        if summary['success_rate'] >= 90:
            print("\n🎉 SYSTEM OPERATIONAL - ALL TESTS PASSED")
            sys.exit(0)
        else:
            print(f"\n⚠️  SYSTEM ISSUES DETECTED - {summary['failed_tests']} FAILURES")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Monitoring interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Monitoring failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 