#!/usr/bin/env python3
"""
Live Deployment Test Suite for Sophia AI
Comprehensive testing of backend services, Snowflake connectivity, and API endpoints
"""

import asyncio
import json
import logging
import sys
from pathlib import Path
import httpx
import websockets
from datetime import datetime
import snowflake.connector

# Add backend to Python path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Test Configuration
BASE_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000"
CEO_TOKEN = "sophia_ceo_access_2024"
TEST_USER_ID = "ceo_user"

# Snowflake Configuration (from prompts)
SNOWFLAKE_CONFIG = {
    "account": "ZNB04675",
    "user": "SCOOBYJAVA15",
    "password": "eyJraWQiOiI1MDg3NDc2OTQxMyIsImFsZyI6IkVTMjU2In0.eyJwIjoiMTk4NzI5NDc2OjUwODc0NzQ1NDc3IiwiaXNzIjoiU0Y6MTA0OSIsImV4cCI6MTc4MjI4MDQ3OH0.8m-fWI5rvCs6b8bvw1quiM-UzW9uPRxMUmE6VAgOFFylAhRkCzch7ojh7CRLeMdii6DD1Owqap0KoOmyxsW77A",
    "role": "ACCOUNTADMIN",
    "database": "SOPHIA_AI_PROD",
    "schema": "UNIVERSAL_CHAT",
    "warehouse": "SOPHIA_AI_WH"
}

class SophiaTestSuite:
    def __init__(self):
        self.test_results = {}
        self.passed_tests = 0
        self.failed_tests = 0

    def log_test_result(self, test_name: str, success: bool, message: str = ""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"{status} {test_name}: {message}")
        
        self.test_results[test_name] = {
            "status": "PASS" if success else "FAIL",
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        
        if success:
            self.passed_tests += 1
        else:
            self.failed_tests += 1

    async def test_snowflake_connectivity(self):
        """Test direct Snowflake connectivity"""
        try:
            connection = snowflake.connector.connect(**SNOWFLAKE_CONFIG)
            cursor = connection.cursor()
            
            # Test basic query
            cursor.execute("SELECT 1 as test")
            cursor.fetchone()
            
            # Test schema access
            cursor.execute("SHOW TABLES IN SCHEMA UNIVERSAL_CHAT")
            tables = cursor.fetchall()
            
            cursor.close()
            connection.close()
            
            self.log_test_result(
                "Snowflake Connectivity", 
                True, 
                f"Connected successfully, found {len(tables)} tables"
            )
            return True
            
        except Exception as e:
            self.log_test_result("Snowflake Connectivity", False, str(e))
            return False

    async def test_platform_health(self):
        """Test platform health endpoint"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{BASE_URL}/health")
                
                if response.status_code == 200:
                    data = response.json()
                    self.log_test_result(
                        "Platform Health", 
                        True, 
                        f"Status: {data.get('status', 'unknown')}"
                    )
                    return True
                else:
                    self.log_test_result(
                        "Platform Health", 
                        False, 
                        f"HTTP {response.status_code}"
                    )
                    return False
                    
        except Exception as e:
            self.log_test_result("Platform Health", False, str(e))
            return False

    async def test_knowledge_service_health(self):
        """Test knowledge service health"""
        try:
            headers = {"Authorization": f"Bearer {CEO_TOKEN}"}
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{BASE_URL}/api/v1/knowledge/health",
                    headers=headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self.log_test_result(
                        "Knowledge Service Health", 
                        True, 
                        f"Status: {data.get('status', 'unknown')}"
                    )
                    return True
                else:
                    self.log_test_result(
                        "Knowledge Service Health", 
                        False, 
                        f"HTTP {response.status_code}"
                    )
                    return False
                    
        except Exception as e:
            self.log_test_result("Knowledge Service Health", False, str(e))
            return False

    async def test_authentication(self):
        """Test CEO authentication"""
        try:
            headers = {"Authorization": f"Bearer {CEO_TOKEN}"}
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{BASE_URL}/api/v1/knowledge/stats",
                    headers=headers
                )
                
                if response.status_code == 200:
                    self.log_test_result("CEO Authentication", True, "Token accepted")
                    return True
                else:
                    self.log_test_result(
                        "CEO Authentication", 
                        False, 
                        f"HTTP {response.status_code}"
                    )
                    return False
                    
        except Exception as e:
            self.log_test_result("CEO Authentication", False, str(e))
            return False

    async def test_knowledge_upload(self):
        """Test knowledge entry creation"""
        try:
            headers = {"Authorization": f"Bearer {CEO_TOKEN}"}
            
            # Test data
            test_data = {
                "title": "Test Customer Data",
                "content": "This is test customer information for Pay Ready. Customer: ABC Corp, Contact: John Smith, Email: john@abccorp.com",
                "category_id": "customers"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{BASE_URL}/api/v1/knowledge/entries",
                    headers=headers,
                    json=test_data
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self.log_test_result(
                        "Knowledge Upload", 
                        True, 
                        f"Entry created: {data.get('entry_id', 'unknown')}"
                    )
                    return data.get('entry_id')
                else:
                    self.log_test_result(
                        "Knowledge Upload", 
                        False, 
                        f"HTTP {response.status_code}: {response.text}"
                    )
                    return None
                    
        except Exception as e:
            self.log_test_result("Knowledge Upload", False, str(e))
            return None

    async def test_knowledge_search(self):
        """Test knowledge base search"""
        try:
            headers = {"Authorization": f"Bearer {CEO_TOKEN}"}
            
            search_data = {
                "query": "customer",
                "limit": 5
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{BASE_URL}/api/v1/knowledge/search",
                    headers=headers,
                    json=search_data
                )
                
                if response.status_code == 200:
                    data = response.json()
                    result_count = data.get('total_results', 0)
                    self.log_test_result(
                        "Knowledge Search", 
                        True, 
                        f"Found {result_count} results"
                    )
                    return True
                else:
                    self.log_test_result(
                        "Knowledge Search", 
                        False, 
                        f"HTTP {response.status_code}"
                    )
                    return False
                    
        except Exception as e:
            self.log_test_result("Knowledge Search", False, str(e))
            return False

    async def test_chat_with_knowledge(self):
        """Test chat integration with knowledge base"""
        try:
            headers = {"Authorization": f"Bearer {CEO_TOKEN}"}
            
            chat_data = {
                "message": "Tell me about our customers",
                "use_knowledge": True
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{BASE_URL}/api/v1/knowledge/chat",
                    headers=headers,
                    json=chat_data
                )
                
                if response.status_code == 200:
                    data = response.json()
                    session_id = data.get('session_id', 'unknown')
                    sources = len(data.get('knowledge_sources', []))
                    self.log_test_result(
                        "Chat with Knowledge", 
                        True, 
                        f"Session: {session_id}, Sources: {sources}"
                    )
                    return True
                else:
                    self.log_test_result(
                        "Chat with Knowledge", 
                        False, 
                        f"HTTP {response.status_code}: {response.text}"
                    )
                    return False
                    
        except Exception as e:
            self.log_test_result("Chat with Knowledge", False, str(e))
            return False

    async def test_websocket_connection(self):
        """Test WebSocket chat functionality"""
        try:
            ws_url = f"{WS_URL}/ws/chat/{TEST_USER_ID}"
            
            async with websockets.connect(ws_url) as websocket:
                # Send test message
                test_message = {
                    "content": "Hello Sophia, this is a test message",
                    "session_id": None
                }
                
                await websocket.send(json.dumps(test_message))
                
                # Wait for response (with timeout)
                response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                response_data = json.loads(response)
                
                if response_data.get('content'):
                    self.log_test_result(
                        "WebSocket Chat", 
                        True, 
                        f"Received response: {len(response_data['content'])} chars"
                    )
                    return True
                else:
                    self.log_test_result("WebSocket Chat", False, "No content in response")
                    return False
                    
        except Exception as e:
            self.log_test_result("WebSocket Chat", False, str(e))
            return False

    async def test_categories(self):
        """Test category management"""
        try:
            headers = {"Authorization": f"Bearer {CEO_TOKEN}"}
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{BASE_URL}/api/v1/knowledge/categories",
                    headers=headers
                )
                
                if response.status_code == 200:
                    categories = response.json()
                    self.log_test_result(
                        "Category Management", 
                        True, 
                        f"Found {len(categories)} categories"
                    )
                    return True
                else:
                    self.log_test_result(
                        "Category Management", 
                        False, 
                        f"HTTP {response.status_code}"
                    )
                    return False
                    
        except Exception as e:
            self.log_test_result("Category Management", False, str(e))
            return False

    async def run_comprehensive_test(self):
        """Run all tests"""
        logger.info("🔬 Starting Comprehensive Sophia AI Test Suite...")
        logger.info("=" * 60)
        
        # Test sequence
        tests = [
            ("Snowflake Connectivity", self.test_snowflake_connectivity),
            ("Platform Health", self.test_platform_health),
            ("Knowledge Service Health", self.test_knowledge_service_health),
            ("CEO Authentication", self.test_authentication),
            ("Category Management", self.test_categories),
            ("Knowledge Upload", self.test_knowledge_upload),
            ("Knowledge Search", self.test_knowledge_search),
            ("Chat with Knowledge", self.test_chat_with_knowledge),
            ("WebSocket Chat", self.test_websocket_connection),
        ]
        
        for test_name, test_func in tests:
            logger.info(f"🧪 Running: {test_name}")
            try:
                await test_func()
            except Exception as e:
                self.log_test_result(test_name, False, f"Test exception: {str(e)}")
            
            # Small delay between tests
            await asyncio.sleep(1)
        
        # Summary
        logger.info("=" * 60)
        logger.info("📊 TEST SUMMARY")
        logger.info("=" * 60)
        logger.info(f"✅ Passed: {self.passed_tests}")
        logger.info(f"❌ Failed: {self.failed_tests}")
        logger.info(f"📈 Success Rate: {(self.passed_tests / (self.passed_tests + self.failed_tests) * 100):.1f}%")
        
        if self.failed_tests == 0:
            logger.info("🎉 ALL TESTS PASSED! System is ready for live testing.")
            return True
        else:
            logger.info("⚠️ Some tests failed. Please check the issues above.")
            return False

async def main():
    """Main test runner"""
    print("🚀 Sophia AI Live Deployment Test Suite")
    print("=" * 60)
    print("This script will test all backend services and connectivity.")
    print("Make sure the backend server is running on localhost:8000")
    print("=" * 60)
    
    # Wait for user confirmation
    try:
        input("Press Enter to start testing (Ctrl+C to cancel)...")
    except KeyboardInterrupt:
        print("\n❌ Test cancelled by user")
        return
    
    suite = SophiaTestSuite()
    success = await suite.run_comprehensive_test()
    
    # Save test results
    with open("test_results.json", "w") as f:
        json.dump({
            "summary": {
                "passed": suite.passed_tests,
                "failed": suite.failed_tests,
                "success_rate": suite.passed_tests / (suite.passed_tests + suite.failed_tests) * 100,
                "overall_success": success
            },
            "tests": suite.test_results,
            "timestamp": datetime.now().isoformat()
        }, f, indent=2)
    
    print("\n📄 Detailed results saved to test_results.json")
    
    if success:
        print("\n🎯 SYSTEM READY FOR LIVE TESTING!")
        print("You can now:")
        print("1. Access the knowledge dashboard at http://localhost:8000/docs")
        print("2. Upload foundational business data via API")
        print("3. Test chat functionality with uploaded knowledge")
        print("4. Use WebSocket for real-time chat")
    else:
        print("\n⚠️ Please fix the failed tests before proceeding with live testing.")

if __name__ == "__main__":
    asyncio.run(main()) 