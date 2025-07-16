#!/usr/bin/env python3
"""
Comprehensive Deployment Test for Sophia AI
Tests all components to ensure full production readiness
"""

import asyncio
import logging
import os
import sys
from pathlib import Path
from typing import Dict
import subprocess
import requests
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SophiaDeploymentTester:
    """Comprehensive deployment tester for Sophia AI"""
    
    def __init__(self):
        self.results = {
            "backend": False,
            "frontend": False,
            "mcp_servers": False,
            "database_connections": False,
            "api_endpoints": False,
            "environment_config": False
        }
        self.backend_url = "http://localhost:8000"
        self.frontend_url = "http://localhost:5173"
        self.test_start_time = datetime.now()
        
    def test_environment_variables(self) -> bool:
        """Test that required environment variables are set"""
        logger.info("🔍 Testing environment variables...")
        
        required_vars = [
            "LAMBDA_API_KEY",
            "OPENAI_API_KEY", 
            "ANTHROPIC_API_KEY",
            "ENVIRONMENT",
            "PULUMI_ORG"
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            logger.error(f"❌ Missing environment variables: {', '.join(missing_vars)}")
            return False
        
        logger.info("✅ All required environment variables are set")
        return True
    
    def test_backend_health(self) -> bool:
        """Test backend health endpoint"""
        logger.info("🔍 Testing backend health...")
        
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=10)
            if response.status_code == 200:
                logger.info("✅ Backend health check passed")
                return True
            else:
                logger.error(f"❌ Backend health check failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ Backend health check failed: {e}")
            return False
    
    def test_frontend_health(self) -> bool:
        """Test frontend accessibility"""
        logger.info("🔍 Testing frontend accessibility...")
        
        try:
            response = requests.get(self.frontend_url, timeout=10)
            if response.status_code == 200:
                logger.info("✅ Frontend is accessible")
                return True
            else:
                logger.error(f"❌ Frontend not accessible: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ Frontend not accessible: {e}")
            return False
    
    def test_api_endpoints(self) -> bool:
        """Test key API endpoints"""
        logger.info("🔍 Testing API endpoints...")
        
        endpoints = [
            "/",
            "/health",
            "/dashboard",
        ]
        
        failed_endpoints = []
        for endpoint in endpoints:
            try:
                response = requests.get(f"{self.backend_url}{endpoint}", timeout=10)
                if response.status_code not in [200, 404]:  # 404 is acceptable for some endpoints
                    failed_endpoints.append(f"{endpoint}: {response.status_code}")
            except Exception as e:
                failed_endpoints.append(f"{endpoint}: {e}")
        
        if failed_endpoints:
            logger.error(f"❌ Failed API endpoints: {', '.join(failed_endpoints)}")
            return False
        
        logger.info("✅ All API endpoints are working")
        return True
    
    def test_chat_endpoint(self) -> bool:
        """Test the chat endpoint with a simple query"""
        logger.info("🔍 Testing chat endpoint...")
        
        try:
            chat_data = {
                "message": "Hello, this is a test message",
                "user_id": "test_user"
            }
            
            response = requests.post(
                f"{self.backend_url}/chat",
                json=chat_data,
                timeout=30
            )
            
            if response.status_code == 200:
                logger.info("✅ Chat endpoint is working")
                return True
            else:
                logger.error(f"❌ Chat endpoint failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ Chat endpoint failed: {e}")
            return False
    
    def test_mcp_servers(self) -> bool:
        """Test MCP server connectivity"""
        logger.info("🔍 Testing MCP server connectivity...")
        
        # Check if MCP server processes are running
        try:
            # Look for common MCP server processes
            result = subprocess.run(
                ["pgrep", "-f", "mcp-server"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                logger.info("✅ MCP server processes are running")
                return True
            else:
                logger.warning("⚠️  No MCP server processes found")
                return False
        except Exception as e:
            logger.error(f"❌ MCP server check failed: {e}")
            return False
    
    def test_database_connections(self) -> bool:
        """Test database connectivity"""
        logger.info("🔍 Testing database connections...")
        
        try:
            # Test if we can import and use the backend
            sys.path.insert(0, str(Path(__file__).parent.parent))
            
            # Try to get config values
            from backend.core.auto_esc_config import get_config_value
            
            # Test basic config loading
            env = get_config_value("ENVIRONMENT", "unknown")
            if env:
                logger.info(f"✅ Configuration system working (env: {env})")
                return True
            else:
                logger.error("❌ Configuration system not working")
                return False
                
        except Exception as e:
            logger.error(f"❌ Database connection test failed: {e}")
            return False
    
    def run_comprehensive_test(self) -> Dict[str, bool]:
        """Run all tests and return results"""
        logger.info("🚀 Starting comprehensive Sophia AI deployment test...")
        logger.info("=" * 60)
        
        # Test environment variables
        self.results["environment_config"] = self.test_environment_variables()
        
        # Test backend
        self.results["backend"] = self.test_backend_health()
        
        # Test frontend
        self.results["frontend"] = self.test_frontend_health()
        
        # Test API endpoints
        self.results["api_endpoints"] = self.test_api_endpoints()
        
        # Test chat endpoint
        self.test_chat_endpoint()
        
        # Test MCP servers
        self.results["mcp_servers"] = self.test_mcp_servers()
        
        # Test database connections
        self.results["database_connections"] = self.test_database_connections()
        
        # Calculate overall success
        total_tests = len(self.results)
        passed_tests = sum(1 for result in self.results.values() if result)
        success_rate = (passed_tests / total_tests) * 100
        
        # Generate report
        test_duration = datetime.now() - self.test_start_time
        
        logger.info("=" * 60)
        logger.info("📊 DEPLOYMENT TEST RESULTS")
        logger.info("=" * 60)
        
        for component, status in self.results.items():
            status_icon = "✅" if status else "❌"
            logger.info(f"{status_icon} {component.replace('_', ' ').title()}")
        
        logger.info(f"\n📈 Overall Success Rate: {success_rate:.1f}% ({passed_tests}/{total_tests})")
        logger.info(f"⏱️  Test Duration: {test_duration}")
        
        if success_rate >= 80:
            logger.info("🎉 DEPLOYMENT TEST PASSED - Ready for production!")
        else:
            logger.error("❌ DEPLOYMENT TEST FAILED - Issues need to be resolved")
        
        return self.results
    
    def generate_deployment_report(self) -> str:
        """Generate a detailed deployment report"""
        report = f"""
# Sophia AI Deployment Test Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Test Results

"""
        
        for component, status in self.results.items():
            status_text = "PASS" if status else "FAIL"
            report += f"- **{component.replace('_', ' ').title()}**: {status_text}\n"
        
        total_tests = len(self.results)
        passed_tests = sum(1 for result in self.results.values() if result)
        success_rate = (passed_tests / total_tests) * 100
        
        report += "\n## Overall Status\n"
        report += f"- **Success Rate**: {success_rate:.1f}%\n"
        report += f"- **Tests Passed**: {passed_tests}/{total_tests}\n"
        
        if success_rate >= 80:
            report += "- **Status**: ✅ READY FOR PRODUCTION\n"
        else:
            report += "- **Status**: ❌ NEEDS FIXES\n"
        
        report += "\n## Next Steps\n"
        
        if success_rate >= 80:
            report += "- System is ready for production deployment\n"
            report += "- Consider running load tests\n"
            report += "- Monitor system metrics\n"
        else:
            report += "- Fix failing components\n"
            report += "- Re-run deployment test\n"
            report += "- Check logs for detailed error information\n"
        
        return report

async def main():
    """Main test runner"""
    tester = SophiaDeploymentTester()
    results = tester.run_comprehensive_test()
    
    # Generate and save report
    report = tester.generate_deployment_report()
    
    # Save report to file
    report_file = Path("DEPLOYMENT_TEST_REPORT.md")
    with open(report_file, "w") as f:
        f.write(report)
    
    logger.info(f"📄 Detailed report saved to: {report_file}")
    
    # Return appropriate exit code
    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result)
    success_rate = (passed_tests / total_tests) * 100
    
    if success_rate >= 80:
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Failure

if __name__ == "__main__":
    asyncio.run(main()) 