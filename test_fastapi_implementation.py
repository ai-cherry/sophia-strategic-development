#!/usr/bin/env python3
"""
FastAPI 2025 Implementation Test Script
Tests all key functionality and improvements
"""

import asyncio
import sys
import time
from datetime import datetime

import httpx

# Test configuration
TEST_CONFIG = {
    "base_url": "http://localhost:8000",
    "timeout": 10.0,
    "test_message": "Hello Sophia AI! Test streaming response.",
    "expected_endpoints": [
        "/",
        "/health",
        "/health/detailed",
        "/debug/routes",
        "/api/v1/chat"
    ]
}

class FastAPITester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=TEST_CONFIG["timeout"])
        self.results = []

    async def log_test(self, test_name: str, success: bool, details: str = "", duration: float = 0):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        timestamp = datetime.now().strftime("%H:%M:%S")

        result = {
            "test_name": test_name,
            "success": success,
            "details": details,
            "duration": f"{duration:.2f}s",
            "timestamp": timestamp
        }

        self.results.append(result)
        print(f"[{timestamp}] {status} {test_name} ({duration:.2f}s)")
        if details:
            print(f"    📝 {details}")

    async def test_health_endpoint(self):
        """Test basic health endpoint"""
        start_time = time.time()
        try:
            response = await self.client.get(f"{self.base_url}/health")
            duration = time.time() - start_time

            if response.status_code == 200:
                data = response.json()
                await self.log_test(
                    "Health Endpoint",
                    True,
                    f"Status: {data.get('status', 'unknown')}",
                    duration
                )
                return True
            else:
                await self.log_test(
                    "Health Endpoint",
                    False,
                    f"HTTP {response.status_code}",
                    duration
                )
                return False
        except Exception as e:
            duration = time.time() - start_time
            await self.log_test(
                "Health Endpoint",
                False,
                f"Error: {str(e)}",
                duration
            )
            return False

    async def test_detailed_health_endpoint(self):
        """Test enhanced detailed health endpoint"""
        start_time = time.time()
        try:
            response = await self.client.get(f"{self.base_url}/health/detailed")
            duration = time.time() - start_time

            if response.status_code == 200:
                data = response.json()
                expected_fields = ["status", "service", "version", "environment", "timestamp"]
                missing_fields = [field for field in expected_fields if field not in data]

                if not missing_fields:
                    await self.log_test(
                        "Detailed Health Endpoint",
                        True,
                        f"Service: {data.get('service')}, Version: {data.get('version')}",
                        duration
                    )
                    return True
                else:
                    await self.log_test(
                        "Detailed Health Endpoint",
                        False,
                        f"Missing fields: {missing_fields}",
                        duration
                    )
                    return False
            else:
                await self.log_test(
                    "Detailed Health Endpoint",
                    False,
                    f"HTTP {response.status_code}",
                    duration
                )
                return False
        except Exception as e:
            duration = time.time() - start_time
            await self.log_test(
                "Detailed Health Endpoint",
                False,
                f"Error: {str(e)}",
                duration
            )
            return False

    async def test_chat_endpoint_regular(self):
        """Test regular chat endpoint (non-streaming)"""
        start_time = time.time()
        try:
            payload = {
                "message": TEST_CONFIG["test_message"],
                "user_id": "test_user",
                "stream": False
            }

            response = await self.client.post(
                f"{self.base_url}/api/v1/chat",
                json=payload
            )
            duration = time.time() - start_time

            if response.status_code == 200:
                data = response.json()
                if "content" in data and "user_id" in data:
                    await self.log_test(
                        "Chat Endpoint (Regular)",
                        True,
                        f"Response length: {len(data['content'])} chars",
                        duration
                    )
                    return True
                else:
                    await self.log_test(
                        "Chat Endpoint (Regular)",
                        False,
                        f"Invalid response format: {list(data.keys())}",
                        duration
                    )
                    return False
            else:
                await self.log_test(
                    "Chat Endpoint (Regular)",
                    False,
                    f"HTTP {response.status_code}",
                    duration
                )
                return False
        except Exception as e:
            duration = time.time() - start_time
            await self.log_test(
                "Chat Endpoint (Regular)",
                False,
                f"Error: {str(e)}",
                duration
            )
            return False

    async def test_chat_endpoint_streaming(self):
        """Test streaming chat endpoint (SSE)"""
        start_time = time.time()
        try:
            payload = {
                "message": TEST_CONFIG["test_message"],
                "user_id": "test_user",
                "stream": True
            }

            response = await self.client.post(
                f"{self.base_url}/api/v1/chat",
                json=payload
            )
            duration = time.time() - start_time

            if response.status_code == 200:
                # Check for streaming response headers
                content_type = response.headers.get("content-type", "")
                if "text/event-stream" in content_type:
                    # Read some streaming content
                    content_chunks = []
                    async for chunk in response.aiter_text():
                        content_chunks.append(chunk)
                        if len(content_chunks) >= 3:  # Read first few chunks
                            break

                    total_content = "".join(content_chunks)
                    if "data:" in total_content:
                        await self.log_test(
                            "Chat Endpoint (Streaming)",
                            True,
                            f"Received {len(content_chunks)} chunks",
                            duration
                        )
                        return True
                    else:
                        await self.log_test(
                            "Chat Endpoint (Streaming)",
                            False,
                            "No SSE data format found",
                            duration
                        )
                        return False
                else:
                    await self.log_test(
                        "Chat Endpoint (Streaming)",
                        False,
                        f"Wrong content-type: {content_type}",
                        duration
                    )
                    return False
            else:
                await self.log_test(
                    "Chat Endpoint (Streaming)",
                    False,
                    f"HTTP {response.status_code}",
                    duration
                )
                return False
        except Exception as e:
            duration = time.time() - start_time
            await self.log_test(
                "Chat Endpoint (Streaming)",
                False,
                f"Error: {str(e)}",
                duration
            )
            return False

    async def test_debug_routes_endpoint(self):
        """Test debug routes endpoint"""
        start_time = time.time()
        try:
            response = await self.client.get(f"{self.base_url}/debug/routes")
            duration = time.time() - start_time

            if response.status_code == 200:
                data = response.json()
                if "routes" in data and isinstance(data["routes"], list):
                    route_count = len(data["routes"])
                    await self.log_test(
                        "Debug Routes Endpoint",
                        True,
                        f"Found {route_count} routes",
                        duration
                    )
                    return True
                else:
                    await self.log_test(
                        "Debug Routes Endpoint",
                        False,
                        "Invalid routes format",
                        duration
                    )
                    return False
            else:
                await self.log_test(
                    "Debug Routes Endpoint",
                    False,
                    f"HTTP {response.status_code}",
                    duration
                )
                return False
        except Exception as e:
            duration = time.time() - start_time
            await self.log_test(
                "Debug Routes Endpoint",
                False,
                f"Error: {str(e)}",
                duration
            )
            return False

    async def test_cors_configuration(self):
        """Test CORS configuration"""
        start_time = time.time()
        try:
            # Send an OPTIONS request to test CORS
            response = await self.client.options(f"{self.base_url}/health")
            duration = time.time() - start_time

            cors_headers = {
                "access-control-allow-origin": response.headers.get("access-control-allow-origin"),
                "access-control-allow-methods": response.headers.get("access-control-allow-methods"),
                "access-control-allow-headers": response.headers.get("access-control-allow-headers")
            }

            if cors_headers["access-control-allow-origin"]:
                await self.log_test(
                    "CORS Configuration",
                    True,
                    f"Origin: {cors_headers['access-control-allow-origin']}",
                    duration
                )
                return True
            else:
                await self.log_test(
                    "CORS Configuration",
                    False,
                    "Missing CORS headers",
                    duration
                )
                return False
        except Exception as e:
            duration = time.time() - start_time
            await self.log_test(
                "CORS Configuration",
                False,
                f"Error: {str(e)}",
                duration
            )
            return False

    async def run_all_tests(self):
        """Run all tests and generate report"""
        print("🚀 Starting FastAPI 2025 Implementation Tests")
        print(f"🎯 Target URL: {self.base_url}")
        print("=" * 60)

        # Run all tests
        test_functions = [
            self.test_health_endpoint,
            self.test_detailed_health_endpoint,
            self.test_chat_endpoint_regular,
            self.test_chat_endpoint_streaming,
            self.test_debug_routes_endpoint,
            self.test_cors_configuration
        ]

        total_tests = len(test_functions)
        passed_tests = 0

        for test_func in test_functions:
            success = await test_func()
            if success:
                passed_tests += 1

        # Generate summary
        print("=" * 60)
        print("📊 TEST SUMMARY")
        print(f"✅ Passed: {passed_tests}/{total_tests}")
        print(f"❌ Failed: {total_tests - passed_tests}/{total_tests}")
        print(f"📈 Success Rate: {(passed_tests/total_tests)*100:.1f}%")

        # Close client
        await self.client.aclose()

        return passed_tests == total_tests

async def main():
    """Main test function"""
    print("🔍 FastAPI 2025 Implementation Validator")
    print("=" * 60)

    tester = FastAPITester(TEST_CONFIG["base_url"])

    try:
        success = await tester.run_all_tests()

        if success:
            print("\n🎉 ALL TESTS PASSED! FastAPI 2025 implementation is working correctly.")
            return 0
        else:
            print("\n⚠️  Some tests failed. Please check the implementation.")
            return 1

    except KeyboardInterrupt:
        print("\n⏹️  Tests interrupted by user")
        return 1
    except Exception as e:
        print(f"\n💥 Test suite error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
