#!/usr/bin/env python3
"""
Comprehensive Sophia AI Deployment Test
=======================================
Validates that the complete Sophia AI platform is operational
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, List

import httpx


class SophiaAIDeploymentTester:
    """Comprehensive deployment testing for Sophia AI"""
    
    def __init__(self):
        self.backend_url = "http://localhost:8000"
        self.frontend_url = "http://localhost:5173"
        self.test_results = []
        
    async def run_all_tests(self) -> Dict:
        """Run all deployment tests"""
        print("🚀 Starting Sophia AI Comprehensive Deployment Test")
        print("=" * 60)
        
        start_time = time.time()
        
        # Test suites
        test_suites = [
            ("Backend API Tests", self.test_backend_api),
            ("Frontend Tests", self.test_frontend),
            ("Integration Tests", self.test_integration),
            ("Performance Tests", self.test_performance),
            ("Lambda Labs Integration", self.test_lambda_labs),
        ]
        
        for suite_name, test_func in test_suites:
            print(f"\n📋 Running {suite_name}...")
            try:
                results = await test_func()
                self.test_results.extend(results)
                print(f"✅ {suite_name} completed")
            except Exception as e:
                print(f"❌ {suite_name} failed: {e}")
                self.test_results.append({
                    "test": suite_name,
                    "status": "FAILED",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
        
        end_time = time.time()
        
        # Generate final report
        return self.generate_report(end_time - start_time)
    
    async def test_backend_api(self) -> List[Dict]:
        """Test backend API endpoints"""
        results = []
        
        async with httpx.AsyncClient() as client:
            # Test root endpoint
            try:
                response = await client.get(f"{self.backend_url}/")
                results.append({
                    "test": "Backend Root Endpoint",
                    "status": "PASSED" if response.status_code == 200 else "FAILED",
                    "response_time": response.elapsed.total_seconds(),
                    "status_code": response.status_code,
                    "timestamp": datetime.now().isoformat()
                })
            except Exception as e:
                results.append({
                    "test": "Backend Root Endpoint",
                    "status": "FAILED",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
            
            # Test health endpoint
            try:
                response = await client.get(f"{self.backend_url}/health")
                results.append({
                    "test": "Backend Health Endpoint",
                    "status": "PASSED" if response.status_code == 200 else "FAILED",
                    "response_time": response.elapsed.total_seconds(),
                    "status_code": response.status_code,
                    "timestamp": datetime.now().isoformat()
                })
            except Exception as e:
                results.append({
                    "test": "Backend Health Endpoint",
                    "status": "FAILED",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
            
            # Test dashboard endpoint
            try:
                response = await client.get(f"{self.backend_url}/dashboard")
                results.append({
                    "test": "Backend Dashboard Endpoint",
                    "status": "PASSED" if response.status_code == 200 else "FAILED",
                    "response_time": response.elapsed.total_seconds(),
                    "status_code": response.status_code,
                    "timestamp": datetime.now().isoformat()
                })
            except Exception as e:
                results.append({
                    "test": "Backend Dashboard Endpoint",
                    "status": "FAILED",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
            
            # Test chat endpoint
            try:
                chat_payload = {"message": "Hello Sophia AI, test deployment"}
                response = await client.post(
                    f"{self.backend_url}/chat",
                    json=chat_payload,
                    headers={"Content-Type": "application/json"}
                )
                results.append({
                    "test": "Backend Chat Endpoint",
                    "status": "PASSED" if response.status_code == 200 else "FAILED",
                    "response_time": response.elapsed.total_seconds(),
                    "status_code": response.status_code,
                    "timestamp": datetime.now().isoformat()
                })
            except Exception as e:
                results.append({
                    "test": "Backend Chat Endpoint",
                    "status": "FAILED",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
        
        return results
    
    async def test_frontend(self) -> List[Dict]:
        """Test frontend availability"""
        results = []
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(self.frontend_url)
                results.append({
                    "test": "Frontend Availability",
                    "status": "PASSED" if response.status_code == 200 else "FAILED",
                    "response_time": response.elapsed.total_seconds(),
                    "status_code": response.status_code,
                    "content_type": response.headers.get("content-type", ""),
                    "timestamp": datetime.now().isoformat()
                })
            except Exception as e:
                results.append({
                    "test": "Frontend Availability",
                    "status": "FAILED",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
        
        return results
    
    async def test_integration(self) -> List[Dict]:
        """Test backend-frontend integration"""
        results = []
        
        # Test CORS and API accessibility from frontend perspective
        async with httpx.AsyncClient() as client:
            try:
                # Simulate frontend calling backend
                response = await client.get(
                    f"{self.backend_url}/health",
                    headers={
                        "Origin": self.frontend_url,
                        "Access-Control-Request-Method": "GET"
                    }
                )
                results.append({
                    "test": "CORS Integration",
                    "status": "PASSED" if response.status_code == 200 else "FAILED",
                    "response_time": response.elapsed.total_seconds(),
                    "status_code": response.status_code,
                    "timestamp": datetime.now().isoformat()
                })
            except Exception as e:
                results.append({
                    "test": "CORS Integration",
                    "status": "FAILED",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
        
        return results
    
    async def test_performance(self) -> List[Dict]:
        """Test performance metrics"""
        results = []
        
        # Test response times
        async with httpx.AsyncClient() as client:
            response_times = []
            for i in range(5):
                try:
                    start = time.time()
                    response = await client.get(f"{self.backend_url}/health")
                    end = time.time()
                    response_times.append(end - start)
                except Exception:
                    continue
            
            if response_times:
                avg_response_time = sum(response_times) / len(response_times)
                max_response_time = max(response_times)
                results.append({
                    "test": "Performance - Response Times",
                    "status": "PASSED" if avg_response_time < 1.0 else "WARNING",
                    "avg_response_time": avg_response_time,
                    "max_response_time": max_response_time,
                    "samples": len(response_times),
                    "timestamp": datetime.now().isoformat()
                })
            else:
                results.append({
                    "test": "Performance - Response Times",
                    "status": "FAILED",
                    "error": "No successful requests",
                    "timestamp": datetime.now().isoformat()
                })
        
        return results
    
    async def test_lambda_labs(self) -> List[Dict]:
        """Test Lambda Labs integration"""
        results = []
        
        # Test Lambda Labs API key configuration
        import os
        lambda_api_key = os.getenv("LAMBDA_API_KEY")
        
        results.append({
            "test": "Lambda Labs API Key Configuration",
            "status": "PASSED" if lambda_api_key else "FAILED",
            "configured": bool(lambda_api_key),
            "key_length": len(lambda_api_key) if lambda_api_key else 0,
            "timestamp": datetime.now().isoformat()
        })
        
        # Test Lambda Labs API connectivity
        if lambda_api_key:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        "https://cloud.lambda.ai/api/v1/instances",
                        auth=(lambda_api_key, ""),
                        timeout=10.0
                    )
                    results.append({
                        "test": "Lambda Labs API Connectivity",
                        "status": "PASSED" if response.status_code == 200 else "FAILED",
                        "response_time": response.elapsed.total_seconds(),
                        "status_code": response.status_code,
                        "timestamp": datetime.now().isoformat()
                    })
            except Exception as e:
                results.append({
                    "test": "Lambda Labs API Connectivity",
                    "status": "FAILED",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
        
        return results
    
    def generate_report(self, total_time: float) -> Dict:
        """Generate comprehensive test report"""
        passed_tests = [r for r in self.test_results if r.get("status") == "PASSED"]
        failed_tests = [r for r in self.test_results if r.get("status") == "FAILED"]
        warning_tests = [r for r in self.test_results if r.get("status") == "WARNING"]
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_execution_time": total_time,
            "summary": {
                "total_tests": len(self.test_results),
                "passed": len(passed_tests),
                "failed": len(failed_tests),
                "warnings": len(warning_tests),
                "success_rate": len(passed_tests) / len(self.test_results) * 100 if self.test_results else 0
            },
            "status": "OPERATIONAL" if len(failed_tests) == 0 else "DEGRADED" if len(passed_tests) > len(failed_tests) else "FAILED",
            "detailed_results": self.test_results
        }
        
        return report
    
    def print_report(self, report: Dict):
        """Print formatted test report"""
        print("\n" + "=" * 60)
        print("🎯 SOPHIA AI DEPLOYMENT TEST REPORT")
        print("=" * 60)
        print(f"⏱️  Total Execution Time: {report['total_execution_time']:.2f}s")
        print(f"📊 Tests Run: {report['summary']['total_tests']}")
        print(f"✅ Passed: {report['summary']['passed']}")
        print(f"❌ Failed: {report['summary']['failed']}")
        print(f"⚠️  Warnings: {report['summary']['warnings']}")
        print(f"📈 Success Rate: {report['summary']['success_rate']:.1f}%")
        print(f"🎯 Overall Status: {report['status']}")
        
        if report['summary']['failed'] > 0:
            print("\n❌ FAILED TESTS:")
            for test in report['detailed_results']:
                if test.get('status') == 'FAILED':
                    print(f"   • {test['test']}: {test.get('error', 'Unknown error')}")
        
        if report['summary']['warnings'] > 0:
            print("\n⚠️  WARNING TESTS:")
            for test in report['detailed_results']:
                if test.get('status') == 'WARNING':
                    print(f"   • {test['test']}: Performance below optimal")
        
        print("\n✅ PASSED TESTS:")
        for test in report['detailed_results']:
            if test.get('status') == 'PASSED':
                response_time = test.get('response_time', 0)
                print(f"   • {test['test']}: {response_time:.3f}s" if response_time else f"   • {test['test']}: OK")
        
        print("\n" + "=" * 60)
        
        if report['status'] == 'OPERATIONAL':
            print("🚀 SOPHIA AI IS FULLY OPERATIONAL!")
        elif report['status'] == 'DEGRADED':
            print("⚠️  SOPHIA AI IS OPERATIONAL WITH SOME ISSUES")
        else:
            print("❌ SOPHIA AI DEPLOYMENT HAS CRITICAL ISSUES")
        
        print("=" * 60)


async def main():
    """Main test execution"""
    tester = SophiaAIDeploymentTester()
    report = await tester.run_all_tests()
    tester.print_report(report)
    
    # Save report to file
    with open("deployment_test_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Full report saved to: deployment_test_report.json")
    
    return report['status'] == 'OPERATIONAL'


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1) 