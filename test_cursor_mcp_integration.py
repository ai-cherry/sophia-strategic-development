#!/usr/bin/env python3
"""
Sophia AI Cursor MCP Integration Test Suite
Comprehensive testing of MCP server integration and Cursor AI configuration.
"""

import asyncio
import json
import logging
import subprocess
import time
from datetime import datetime
from typing import Dict, List, Tuple
import requests

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CursorMCPIntegrationTest:
    def __init__(self):
        self.base_urls = {
            "backend_api": "http://localhost:8000",
            "mcp_8092": "http://localhost:8092",
            "mcp_8093": "http://localhost:8093", 
            "mcp_8094": "http://localhost:8094",
            "mcp_8095": "http://localhost:8095"
        }
        
        self.test_results = []
        
    def log_test_result(self, test_name: str, status: str, details: str = "", response_time: float = 0):
        """Log a test result."""
        self.test_results.append({
            "test": test_name,
            "status": status,
            "details": details,
            "response_time": response_time,
            "timestamp": datetime.now()
        })
        
        icon = "✅" if status == "PASS" else "❌"
        time_str = f"({response_time:.2f}ms)" if response_time > 0 else ""
        logger.info(f"{icon} {test_name}: {status} {time_str} - {details}")
    
    async def test_health_endpoints(self):
        """Test all health endpoints."""
        logger.info("🔍 Testing health endpoints...")
        
        for service, url in self.base_urls.items():
            start_time = time.time()
            try:
                response = requests.get(f"{url}/health", timeout=5)
                response_time = (time.time() - start_time) * 1000
                
                if response.status_code == 200:
                    data = response.json()
                    status = data.get('status', 'unknown')
                    self.log_test_result(
                        f"Health Check {service}",
                        "PASS",
                        f"Status: {status}",
                        response_time
                    )
                else:
                    self.log_test_result(
                        f"Health Check {service}",
                        "FAIL",
                        f"HTTP {response.status_code}",
                        response_time
                    )
            except Exception as e:
                self.log_test_result(
                    f"Health Check {service}",
                    "FAIL",
                    str(e)[:50]
                )
    
    async def test_backend_api_endpoints(self):
        """Test backend API specific endpoints."""
        logger.info("🔍 Testing backend API endpoints...")
        
        endpoints = [
            ("/api/v1/agents/status", "Agent Status"),
            ("/api/v1/mcp/servers", "MCP Server Status"),
            ("/api/v1/deployment/status", "Deployment Status"),
            ("/api/v1/cursor/optimization", "Cursor Optimization")
        ]
        
        for endpoint, test_name in endpoints:
            start_time = time.time()
            try:
                response = requests.get(f"{self.base_urls['backend_api']}{endpoint}", timeout=5)
                response_time = (time.time() - start_time) * 1000
                
                if response.status_code == 200:
                    data = response.json()
                    self.log_test_result(
                        f"Backend API {test_name}",
                        "PASS",
                        f"Response received",
                        response_time
                    )
                else:
                    self.log_test_result(
                        f"Backend API {test_name}",
                        "FAIL",
                        f"HTTP {response.status_code}",
                        response_time
                    )
            except Exception as e:
                self.log_test_result(
                    f"Backend API {test_name}",
                    "FAIL",
                    str(e)[:50]
                )
    
    async def test_agent_creation(self):
        """Test agent creation functionality."""
        logger.info("🔍 Testing agent creation...")
        
        test_agents = [
            {"agent_type": "gong_agent", "task": "analyze_call_data"},
            {"agent_type": "business_intelligence", "task": "generate_insights"},
            {"agent_type": "infrastructure", "task": "monitor_systems"}
        ]
        
        for agent_data in test_agents:
            start_time = time.time()
            try:
                response = requests.post(
                    f"{self.base_urls['backend_api']}/api/v1/agents/create",
                    json=agent_data,
                    timeout=5
                )
                response_time = (time.time() - start_time) * 1000
                
                if response.status_code == 200:
                    data = response.json()
                    agent_id = data.get('agent_id', 'unknown')
                    instantiation_time = data.get('instantiation_time', 'unknown')
                    self.log_test_result(
                        f"Agent Creation {agent_data['agent_type']}",
                        "PASS",
                        f"ID: {agent_id[:20]}..., Time: {instantiation_time}",
                        response_time
                    )
                else:
                    self.log_test_result(
                        f"Agent Creation {agent_data['agent_type']}",
                        "FAIL",
                        f"HTTP {response.status_code}",
                        response_time
                    )
            except Exception as e:
                self.log_test_result(
                    f"Agent Creation {agent_data['agent_type']}",
                    "FAIL",
                    str(e)[:50]
                )
    
    async def test_mcp_server_capabilities(self):
        """Test MCP server specific capabilities."""
        logger.info("🔍 Testing MCP server capabilities...")
        
        mcp_tests = [
            ("mcp_8092", "/status", "Intelligence Server Status"),
            ("mcp_8093", "/status", "Business Server Status"),
            ("mcp_8094", "/status", "Data Server Status"),
            ("mcp_8095", "/status", "Infrastructure Server Status")
        ]
        
        for server, endpoint, test_name in mcp_tests:
            start_time = time.time()
            try:
                response = requests.get(f"{self.base_urls[server]}{endpoint}", timeout=5)
                response_time = (time.time() - start_time) * 1000
                
                if response.status_code == 200:
                    data = response.json()
                    self.log_test_result(
                        test_name,
                        "PASS",
                        f"Server operational",
                        response_time
                    )
                else:
                    self.log_test_result(
                        test_name,
                        "FAIL",
                        f"HTTP {response.status_code}",
                        response_time
                    )
            except Exception as e:
                self.log_test_result(
                    test_name,
                    "FAIL",
                    str(e)[:50]
                )
    
    def test_cursor_configuration(self):
        """Test Cursor AI configuration."""
        logger.info("🔍 Testing Cursor AI configuration...")
        
        config_path = "/Users/lynnmusil/.cursor/mcp_servers.json"
        
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            # Check required sections
            if 'mcpServers' in config:
                servers = config['mcpServers']
                expected_servers = ['sophia_intelligence', 'sophia_business', 'sophia_data', 'sophia_infrastructure']
                
                for server in expected_servers:
                    if server in servers:
                        server_config = servers[server]
                        if 'baseUrl' in server_config and 'type' in server_config:
                            self.log_test_result(
                                f"Cursor Config {server}",
                                "PASS",
                                f"URL: {server_config['baseUrl']}"
                            )
                        else:
                            self.log_test_result(
                                f"Cursor Config {server}",
                                "FAIL",
                                "Missing required fields"
                            )
                    else:
                        self.log_test_result(
                            f"Cursor Config {server}",
                            "FAIL",
                            "Server not found in config"
                        )
            else:
                self.log_test_result(
                    "Cursor Configuration",
                    "FAIL",
                    "mcpServers section missing"
                )
                
        except FileNotFoundError:
            self.log_test_result(
                "Cursor Configuration",
                "FAIL",
                "Configuration file not found"
            )
        except json.JSONDecodeError:
            self.log_test_result(
                "Cursor Configuration",
                "FAIL",
                "Invalid JSON format"
            )
        except Exception as e:
            self.log_test_result(
                "Cursor Configuration",
                "FAIL",
                str(e)[:50]
            )
    
    async def test_performance_metrics(self):
        """Test performance metrics."""
        logger.info("🔍 Testing performance metrics...")
        
        # Test multiple requests to measure consistency
        performance_tests = []
        
        for i in range(5):
            start_time = time.time()
            try:
                response = requests.get(f"{self.base_urls['backend_api']}/health", timeout=5)
                response_time = (time.time() - start_time) * 1000
                
                if response.status_code == 200:
                    performance_tests.append(response_time)
            except:
                pass
        
        if performance_tests:
            avg_time = sum(performance_tests) / len(performance_tests)
            max_time = max(performance_tests)
            min_time = min(performance_tests)
            
            # Performance targets: < 50ms average, < 100ms max
            if avg_time < 50 and max_time < 100:
                self.log_test_result(
                    "Performance Metrics",
                    "PASS",
                    f"Avg: {avg_time:.1f}ms, Max: {max_time:.1f}ms, Min: {min_time:.1f}ms",
                    avg_time
                )
            else:
                self.log_test_result(
                    "Performance Metrics",
                    "FAIL",
                    f"Avg: {avg_time:.1f}ms, Max: {max_time:.1f}ms (targets: <50ms avg, <100ms max)",
                    avg_time
                )
        else:
            self.log_test_result(
                "Performance Metrics",
                "FAIL",
                "No successful requests"
            )
    
    async def run_all_tests(self):
        """Run all integration tests."""
        logger.info("🚀 Starting Comprehensive MCP Integration Tests...")
        logger.info("=" * 80)
        
        start_time = time.time()
        
        # Run all test suites
        await self.test_health_endpoints()
        await self.test_backend_api_endpoints()
        await self.test_agent_creation()
        await self.test_mcp_server_capabilities()
        self.test_cursor_configuration()
        await self.test_performance_metrics()
        
        total_time = time.time() - start_time
        
        # Generate summary report
        self.print_test_summary(total_time)
        
        return self.get_test_success_rate()
    
    def print_test_summary(self, total_time: float):
        """Print comprehensive test summary."""
        print("\n" + "=" * 80)
        print("🧪 SOPHIA AI MCP INTEGRATION TEST SUMMARY")
        print("=" * 80)
        
        passed = sum(1 for result in self.test_results if result['status'] == 'PASS')
        failed = sum(1 for result in self.test_results if result['status'] == 'FAIL')
        total = len(self.test_results)
        
        print(f"📊 Overall Results: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
        print(f"⏱️  Total test time: {total_time:.2f} seconds")
        print(f"🎯 Success rate: {'✅ EXCELLENT' if passed == total else '⚠️  NEEDS ATTENTION' if passed/total > 0.8 else '❌ CRITICAL ISSUES'}")
        print()
        
        # Group results by category
        categories = {}
        for result in self.test_results:
            category = result['test'].split()[0] + " " + result['test'].split()[1] if len(result['test'].split()) > 1 else result['test'].split()[0]
            if category not in categories:
                categories[category] = {'passed': 0, 'failed': 0, 'total': 0}
            
            categories[category]['total'] += 1
            if result['status'] == 'PASS':
                categories[category]['passed'] += 1
            else:
                categories[category]['failed'] += 1
        
        print("📋 Test Categories:")
        for category, stats in categories.items():
            success_rate = (stats['passed'] / stats['total']) * 100
            status_icon = "✅" if success_rate == 100 else "⚠️" if success_rate > 80 else "❌"
            print(f"  {status_icon} {category:<25} | {stats['passed']}/{stats['total']} passed ({success_rate:.0f}%)")
        
        print("\n" + "=" * 80)
        print("🎯 INTEGRATION STATUS:")
        
        if passed == total:
            print("✅ ALL SYSTEMS OPERATIONAL - Ready for Cursor AI integration")
            print("✅ MCP servers responding correctly")
            print("✅ Backend API fully functional")
            print("✅ Cursor AI configuration installed")
            print("✅ Performance targets met")
        elif passed / total > 0.8:
            print("⚠️  MOSTLY OPERATIONAL - Minor issues detected")
            print("🔧 Some components may need attention")
            print("📝 Review failed tests and address issues")
        else:
            print("❌ CRITICAL ISSUES DETECTED")
            print("🚨 Multiple system failures")
            print("🔧 Immediate attention required")
        
        print("=" * 80)
        
        # Show failed tests if any
        failed_tests = [r for r in self.test_results if r['status'] == 'FAIL']
        if failed_tests:
            print("\n❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"  • {test['test']}: {test['details']}")
            print()
    
    def get_test_success_rate(self) -> float:
        """Get overall test success rate."""
        if not self.test_results:
            return 0.0
        
        passed = sum(1 for result in self.test_results if result['status'] == 'PASS')
        return passed / len(self.test_results)


async def main():
    """Main test execution."""
    tester = CursorMCPIntegrationTest()
    success_rate = await tester.run_all_tests()
    
    print(f"\n🎯 Final Success Rate: {success_rate * 100:.1f}%")
    
    if success_rate == 1.0:
        print("🎉 READY FOR CURSOR AI INTEGRATION!")
        print("\n📋 Next Steps:")
        print("1. Restart Cursor AI to load MCP configuration")
        print("2. Test with: 'Show me Sophia AI system status'")
        print("3. Try all three modes: Chat, Composer, Agent")
    else:
        print("🔧 Address failed tests before proceeding")
    
    return success_rate


if __name__ == "__main__":
    asyncio.run(main()) 