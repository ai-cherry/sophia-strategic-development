#!/usr/bin/env python3
"""
Simplified Test Suite for Sophia AI Standalone Server
Tests all core functionality without import conflicts
"""

import asyncio
import json
import logging
import sys

# Required packages test
try:
    import httpx
    import websockets
    import snowflake.connector
    print("✅ All required packages available")
except ImportError as e:
    print(f"❌ Missing package: {e}")
    print("Run: pip install httpx websockets snowflake-connector-python")
    sys.exit(1)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Test Configuration
BASE_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000"
CEO_TOKEN = "sophia_ceo_access_2024"

# Snowflake Configuration for direct testing
SNOWFLAKE_CONFIG = {
    "account": "ZNB04675",
    "user": "SCOOBYJAVA15",
    "password": "eyJraWQiOiI1MDg3NDc2OTQxMyIsImFsZyI6IkVTMjU2In0.eyJwIjoiMTk4NzI5NDc2OjUwODc0NzQ1NDc3IiwiaXNzIjoiU0Y6MTA0OSIsImV4cCI6MTc4MjI4MDQ3OH0.8m-fWI5rvCs6b8bvw1quiM-UzW9uPRxMUmE6VAgOFFylAhRkCzch7ojh7CRLeMdii6DD1Owqap0KoOmyxsW77A",
    "role": "ACCOUNTADMIN",
    "database": "SOPHIA_AI_PROD",
    "schema": "UNIVERSAL_CHAT",
    "warehouse": "SOPHIA_AI_WH"
}

class SimpleTestSuite:
    def __init__(self):
        self.passed = 0
        self.failed = 0

    def log_result(self, test_name: str, success: bool, message: str = ""):
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        
        if success:
            self.passed += 1
        else:
            self.failed += 1

    async def test_direct_snowflake(self):
        """Test direct Snowflake connectivity"""
        try:
            connection = snowflake.connector.connect(**SNOWFLAKE_CONFIG)
            cursor = connection.cursor()
            cursor.execute("SELECT 1 as test")
            cursor.fetchone()
            cursor.execute("SHOW TABLES IN SCHEMA UNIVERSAL_CHAT")
            tables = cursor.fetchall()
            cursor.close()
            connection.close()
            
            self.log_result("Direct Snowflake", True, f"Connected, found {len(tables)} tables")
            return True
        except Exception as e:
            self.log_result("Direct Snowflake", False, str(e))
            return False

    async def test_server_health(self):
        """Test server health endpoint"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{BASE_URL}/health")
                if response.status_code == 200:
                    data = response.json()
                    self.log_result("Server Health", True, f"Status: {data.get('status')}")
                    return True
                else:
                    self.log_result("Server Health", False, f"HTTP {response.status_code}")
                    return False
        except Exception as e:
            self.log_result("Server Health", False, str(e))
            return False

    async def test_file_upload(self):
        """Test file upload functionality"""
        try:
            # Create test CSV content
            test_csv = """Company,Contact,Email,Industry
ABC Corp,John Smith,john@abccorp.com,Technology
XYZ Ltd,Jane Doe,jane@xyzltd.com,Finance
123 Inc,Bob Johnson,bob@123inc.com,Healthcare"""

            headers = {"Authorization": f"Bearer {CEO_TOKEN}"}
            
            async with httpx.AsyncClient() as client:
                files = {"file": ("test_customers.csv", test_csv, "text/csv")}
                data = {
                    "title": "Test Customer Data for Pay Ready",
                    "category_id": "customers"
                }
                
                response = await client.post(
                    f"{BASE_URL}/upload",
                    headers=headers,
                    files=files,
                    data=data
                )
                
                if response.status_code == 200:
                    result = response.json()
                    self.log_result("File Upload", True, f"Entry ID: {result.get('entry_id', 'unknown')}")
                    return result.get('entry_id')
                else:
                    self.log_result("File Upload", False, f"HTTP {response.status_code}: {response.text}")
                    return None
        except Exception as e:
            self.log_result("File Upload", False, str(e))
            return None

    async def test_knowledge_search(self):
        """Test knowledge search"""
        try:
            headers = {"Authorization": f"Bearer {CEO_TOKEN}"}
            search_data = {"query": "customer", "limit": 10}
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{BASE_URL}/search",
                    headers=headers,
                    json=search_data
                )
                
                if response.status_code == 200:
                    data = response.json()
                    count = data.get('total_results', 0)
                    self.log_result("Knowledge Search", True, f"Found {count} results")
                    return True
                else:
                    self.log_result("Knowledge Search", False, f"HTTP {response.status_code}")
                    return False
        except Exception as e:
            self.log_result("Knowledge Search", False, str(e))
            return False

    async def test_chat_api(self):
        """Test chat API"""
        try:
            headers = {"Authorization": f"Bearer {CEO_TOKEN}"}
            chat_data = {
                "message": "Tell me about our customers",
                "use_knowledge": True
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{BASE_URL}/chat",
                    headers=headers,
                    json=chat_data
                )
                
                if response.status_code == 200:
                    data = response.json()
                    session_id = data.get('session_id', 'unknown')
                    sources = len(data.get('knowledge_sources', []))
                    self.log_result("Chat API", True, f"Session: {session_id[:8]}..., Sources: {sources}")
                    return True
                else:
                    self.log_result("Chat API", False, f"HTTP {response.status_code}: {response.text}")
                    return False
        except Exception as e:
            self.log_result("Chat API", False, str(e))
            return False

    async def test_websocket(self):
        """Test WebSocket functionality"""
        try:
            ws_url = f"{WS_URL}/ws/chat/ceo_user"
            
            async with websockets.connect(ws_url) as websocket:
                # Send test message
                test_message = {
                    "content": "Hello Sophia, what can you tell me about our business?",
                    "session_id": None
                }
                
                await websocket.send(json.dumps(test_message))
                
                # Wait for response
                response = await asyncio.wait_for(websocket.recv(), timeout=15.0)
                response_data = json.loads(response)
                
                if response_data.get('content'):
                    content_length = len(response_data['content'])
                    self.log_result("WebSocket", True, f"Received {content_length} chars response")
                    return True
                else:
                    self.log_result("WebSocket", False, "No content in response")
                    return False
        except Exception as e:
            self.log_result("WebSocket", False, str(e))
            return False

    async def run_all_tests(self):
        """Run all tests in sequence"""
        print("🔬 Starting Sophia AI Standalone Server Test Suite")
        print("=" * 60)
        
        tests = [
            ("Direct Snowflake Connection", self.test_direct_snowflake),
            ("Server Health Check", self.test_server_health),
            ("File Upload", self.test_file_upload),
            ("Knowledge Search", self.test_knowledge_search),
            ("Chat API", self.test_chat_api),
            ("WebSocket Chat", self.test_websocket),
        ]
        
        for test_name, test_func in tests:
            print(f"\n🧪 Running: {test_name}")
            try:
                await test_func()
            except Exception as e:
                self.log_result(test_name, False, f"Test exception: {str(e)}")
            
            # Brief pause between tests
            await asyncio.sleep(1)
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"✅ Passed: {self.passed}")
        print(f"❌ Failed: {self.failed}")
        
        if self.failed == 0:
            print("\n🎉 ALL TESTS PASSED!")
            print("🚀 System is ready for live testing with Pay Ready data!")
            print("\n📋 Next Steps:")
            print("1. Upload customer lists, product info, employee data")
            print("2. Test chat with real business questions")
            print("3. Verify search finds uploaded content")
            return True
        else:
            total = self.passed + self.failed
            success_rate = (self.passed / total * 100) if total > 0 else 0
            print(f"📈 Success Rate: {success_rate:.1f}%")
            print("\n⚠️ Some tests failed. Check the server and try again.")
            return False

async def main():
    print("🚀 Sophia AI Standalone Server Test Suite")
    print("=" * 60)
    print("This will test the standalone server running on localhost:8000")
    print("Make sure to start the server first: python sophia_standalone_server.py")
    print("=" * 60)
    
    try:
        input("Press Enter to start testing (Ctrl+C to cancel)...")
    except KeyboardInterrupt:
        print("\n❌ Tests cancelled")
        return
    
    suite = SimpleTestSuite()
    success = await suite.run_all_tests()
    
    if success:
        print("\n🎯 READY FOR LIVE PAY READY DATA TESTING!")
        print("\nRecommended test data to upload:")
        print("• Customer list (CSV): company names, contacts, industries")
        print("• Product catalog (TXT/PDF): service descriptions, pricing")
        print("• Employee directory (CSV): names, roles, departments")
        print("\nUse the API documentation at: http://localhost:8000/docs")
    else:
        print("\n❌ Fix the failed tests before proceeding")

if __name__ == "__main__":
    asyncio.run(main()) 