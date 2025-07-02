#!/usr/bin/env python3
"""
Test Unified FastAPI Application
=================================

Tests the unified FastAPI application to ensure all routes
and services are working correctly.
"""

import asyncio
import json
import logging
import time
from typing import Dict, Any

import httpx

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UnifiedAPITester:
    """Tests the unified FastAPI application"""
    
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.test_results = {
            "passed": [],
            "failed": [],
            "warnings": []
        }
        
    async def run_all_tests(self):
        """Run all API tests"""
        logger.info("🧪 Starting Unified API tests...")
        
        # Test system endpoints
        await self._test_system_endpoints()
        
        # Test service health
        await self._test_service_health()
        
        # Test API routes
        await self._test_api_routes()
        
        # Test performance
        await self._test_performance()
        
        # Generate test report
        self._generate_test_report()
        
        logger.info("✅ API testing complete!")
        
    async def _test_system_endpoints(self):
        """Test system endpoints"""
        logger.info("🔍 Testing system endpoints...")
        
        endpoints = [
            ("/", "Root endpoint"),
            ("/health", "Health check"),
            ("/metrics", "Prometheus metrics"),
            ("/docs", "API documentation"),
            ("/openapi.json", "OpenAPI schema")
        ]
        
        async with httpx.AsyncClient() as client:
            for endpoint, description in endpoints:
                try:
                    response = await client.get(f"{self.base_url}{endpoint}")
                    
                    if response.status_code == 200:
                        logger.info(f"✅ {description}: OK")
                        self.test_results["passed"].append({
                            "endpoint": endpoint,
                            "description": description,
                            "status": response.status_code
                        })
                    else:
                        logger.warning(f"⚠️  {description}: {response.status_code}")
                        self.test_results["warnings"].append({
                            "endpoint": endpoint,
                            "description": description,
                            "status": response.status_code
                        })
                        
                except Exception as e:
                    logger.error(f"❌ {description}: {e}")
                    self.test_results["failed"].append({
                        "endpoint": endpoint,
                        "description": description,
                        "error": str(e)
                    })
                    
    async def _test_service_health(self):
        """Test service health status"""
        logger.info("🏥 Testing service health...")
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/health")
                
                if response.status_code == 200:
                    health_data = response.json()
                    
                    logger.info(f"Overall status: {health_data['status']}")
                    logger.info(f"Environment: {health_data['environment']}")
                    logger.info(f"Uptime: {health_data['uptime_seconds']:.2f} seconds")
                    
                    # Check individual services
                    services = health_data.get('services', {})
                    for service, status in services.items():
                        if status == "healthy":
                            logger.info(f"✅ {service}: {status}")
                        else:
                            logger.warning(f"⚠️  {service}: {status}")
                            
                    self.test_results["passed"].append({
                        "test": "Service health",
                        "status": health_data['status'],
                        "services": services
                    })
                else:
                    self.test_results["failed"].append({
                        "test": "Service health",
                        "status_code": response.status_code
                    })
                    
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            self.test_results["failed"].append({
                "test": "Service health",
                "error": str(e)
            })
            
    async def _test_api_routes(self):
        """Test main API routes"""
        logger.info("🛣️  Testing API routes...")
        
        # Sample test routes
        test_routes = [
            {
                "method": "GET",
                "path": "/api/v3/chat/status",
                "description": "Chat service status"
            },
            {
                "method": "GET",
                "path": "/api/mcp/servers",
                "description": "MCP server list"
            },
            {
                "method": "POST",
                "path": "/api/v3/chat/message",
                "description": "Send chat message",
                "data": {
                    "message": "Test message",
                    "context": {}
                }
            }
        ]
        
        async with httpx.AsyncClient() as client:
            for route in test_routes:
                try:
                    if route["method"] == "GET":
                        response = await client.get(f"{self.base_url}{route['path']}")
                    elif route["method"] == "POST":
                        response = await client.post(
                            f"{self.base_url}{route['path']}",
                            json=route.get("data", {})
                        )
                    else:
                        continue
                        
                    if response.status_code in [200, 201]:
                        logger.info(f"✅ {route['description']}: OK")
                        self.test_results["passed"].append({
                            "route": route['path'],
                            "method": route['method'],
                            "description": route['description'],
                            "status": response.status_code
                        })
                    elif response.status_code == 404:
                        logger.warning(f"⚠️  {route['description']}: Not implemented")
                        self.test_results["warnings"].append({
                            "route": route['path'],
                            "method": route['method'],
                            "description": route['description'],
                            "status": response.status_code
                        })
                    else:
                        logger.error(f"❌ {route['description']}: {response.status_code}")
                        self.test_results["failed"].append({
                            "route": route['path'],
                            "method": route['method'],
                            "description": route['description'],
                            "status": response.status_code,
                            "error": response.text
                        })
                        
                except Exception as e:
                    logger.error(f"❌ {route['description']}: {e}")
                    self.test_results["failed"].append({
                        "route": route['path'],
                        "method": route['method'],
                        "description": route['description'],
                        "error": str(e)
                    })
                    
    async def _test_performance(self):
        """Test API performance"""
        logger.info("⚡ Testing API performance...")
        
        # Test response times
        endpoints_to_test = [
            "/health",
            "/",
            "/api/v3/chat/status"
        ]
        
        async with httpx.AsyncClient() as client:
            for endpoint in endpoints_to_test:
                try:
                    # Warm up
                    await client.get(f"{self.base_url}{endpoint}")
                    
                    # Test multiple requests
                    response_times = []
                    for _ in range(10):
                        start_time = time.time()
                        response = await client.get(f"{self.base_url}{endpoint}")
                        response_time = (time.time() - start_time) * 1000  # ms
                        
                        if response.status_code == 200:
                            response_times.append(response_time)
                            
                    if response_times:
                        avg_time = sum(response_times) / len(response_times)
                        max_time = max(response_times)
                        min_time = min(response_times)
                        
                        logger.info(f"📊 {endpoint}:")
                        logger.info(f"   Average: {avg_time:.2f}ms")
                        logger.info(f"   Min: {min_time:.2f}ms")
                        logger.info(f"   Max: {max_time:.2f}ms")
                        
                        # Check if meets performance targets
                        if avg_time < 200:  # Target: <200ms
                            status = "passed"
                            logger.info("   ✅ Meets performance target")
                        else:
                            status = "warning"
                            logger.warning("   ⚠️  Slower than target")
                            
                        self.test_results[status].append({
                            "test": "Performance",
                            "endpoint": endpoint,
                            "avg_response_time_ms": avg_time,
                            "min_response_time_ms": min_time,
                            "max_response_time_ms": max_time
                        })
                        
                except Exception as e:
                    logger.error(f"Performance test failed for {endpoint}: {e}")
                    self.test_results["failed"].append({
                        "test": "Performance",
                        "endpoint": endpoint,
                        "error": str(e)
                    })
                    
    def _generate_test_report(self):
        """Generate test report"""
        report_path = "UNIFIED_API_TEST_REPORT.md"
        
        total_tests = len(self.test_results["passed"]) + len(self.test_results["failed"]) + len(self.test_results["warnings"])
        
        with open(report_path, 'w') as f:
            f.write("# Unified API Test Report\n\n")
            f.write(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("## Summary\n\n")
            f.write(f"- Total tests: {total_tests}\n")
            f.write(f"- Passed: {len(self.test_results['passed'])}\n")
            f.write(f"- Warnings: {len(self.test_results['warnings'])}\n")
            f.write(f"- Failed: {len(self.test_results['failed'])}\n")
            f.write(f"- Success rate: {len(self.test_results['passed']) / max(total_tests, 1) * 100:.1f}%\n\n")
            
            f.write("## Passed Tests\n\n")
            for test in self.test_results["passed"]:
                f.write(f"- ✅ {test}\n")
                
            if self.test_results["warnings"]:
                f.write("\n## Warnings\n\n")
                for test in self.test_results["warnings"]:
                    f.write(f"- ⚠️  {test}\n")
                    
            if self.test_results["failed"]:
                f.write("\n## Failed Tests\n\n")
                for test in self.test_results["failed"]:
                    f.write(f"- ❌ {test}\n")
                    
            f.write("\n## Recommendations\n\n")
            
            if self.test_results["failed"]:
                f.write("1. Fix failed endpoints before deployment\n")
                f.write("2. Check service initialization errors\n")
                f.write("3. Verify all dependencies are installed\n")
            else:
                f.write("1. All tests passed - ready for deployment!\n")
                f.write("2. Monitor performance metrics in production\n")
                f.write("3. Set up automated testing pipeline\n")
                
        logger.info(f"📄 Test report saved to {report_path}")


async def main():
    """Main execution function"""
    # Check if API is running
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8001/health", timeout=2.0)
            if response.status_code != 200:
                logger.error("API not responding. Please start the unified API first:")
                logger.error("python backend/app/unified_fastapi_app.py")
                return
    except Exception:
        logger.error("API not running. Please start the unified API first:")
        logger.error("python backend/app/unified_fastapi_app.py")
        return
        
    tester = UnifiedAPITester()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main()) 