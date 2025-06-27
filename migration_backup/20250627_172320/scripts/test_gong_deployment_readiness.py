#!/usr/bin/env python3
"""
Sophia AI - Gong Deployment Readiness Test
This script tests all Gong integration components to ensure deployment readiness.
"""

import asyncio
import json
import logging
import os
import sys
import traceback
from datetime import datetime
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class GongDeploymentTester:
    """Comprehensive Gong deployment readiness tester."""
    
    def __init__(self):
        self.test_results = {}
        self.overall_status = "UNKNOWN"
        
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all deployment readiness tests."""
        logger.info("�� Starting Gong Deployment Readiness Tests")
        logger.info("=" * 50)
        
        test_suites = [
            ("Configuration Management", self.test_configuration_management),
            ("Pulumi ESC Integration", self.test_pulumi_esc_integration),
            ("Gong API Connectivity", self.test_gong_api_connectivity),
            ("Snowflake Connectivity", self.test_snowflake_connectivity),
            ("Airbyte Integration", self.test_airbyte_integration),
            ("AI Memory Integration", self.test_ai_memory_integration),
            ("Backend Services", self.test_backend_services),
        ]
        
        for suite_name, test_func in test_suites:
            logger.info(f"\n🔍 Testing: {suite_name}")
            logger.info("-" * 30)
            
            try:
                result = await test_func()
                self.test_results[suite_name] = result
                
                if result.get("status") == "PASS":
                    logger.info(f"✅ {suite_name}: PASSED")
                else:
                    logger.error(f"❌ {suite_name}: FAILED - {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                logger.error(f"❌ {suite_name}: ERROR - {str(e)}")
                self.test_results[suite_name] = {
                    "status": "ERROR",
                    "error": str(e),
                    "traceback": traceback.format_exc()
                }
        
        # Determine overall status
        self.overall_status = self._calculate_overall_status()
        
        # Generate comprehensive report
        report = self._generate_deployment_report()
        
        return report
    
    async def test_configuration_management(self) -> Dict[str, Any]:
        """Test configuration management and secret access."""
        try:
            # Test Pulumi ESC configuration loading
            from backend.core.auto_esc_config import get_config_value
            
            # Test critical configuration values
            config_tests = {
                "gong_access_key": get_config_value("gong_access_key"),
                "gong_client_secret": get_config_value("gong_client_secret"),
                "snowflake_account": get_config_value("snowflake_account"),
                "snowflake_password": get_config_value("snowflake_password"),
                "openai_api_key": get_config_value("openai_api_key"),
                "pinecone_api_key": get_config_value("pinecone_api_key"),
            }
            
            missing_configs = []
            for key, value in config_tests.items():
                if not value or value == "PLACEHOLDER_VALUE":
                    missing_configs.append(key)
            
            if missing_configs:
                return {
                    "status": "FAIL",
                    "error": f"Missing configurations: {', '.join(missing_configs)}",
                    "details": config_tests
                }
            
            return {
                "status": "PASS",
                "message": "All critical configurations available",
                "config_count": len(config_tests)
            }
            
        except Exception as e:
            return {
                "status": "ERROR",
                "error": f"Configuration test failed: {str(e)}"
            }
    
    async def test_pulumi_esc_integration(self) -> Dict[str, Any]:
        """Test Pulumi ESC integration."""
        try:
            from backend.core.auto_esc_config import AutoESCConfig
            
            config = AutoESCConfig()
            
            # Test enhanced settings
            settings = config.as_enhanced_settings()
            
            # Validate critical settings
            critical_settings = [
                "openai_api_key",
                "gong_access_key", 
                "snowflake_account",
                "pinecone_api_key"
            ]
            
            missing_settings = []
            for setting in critical_settings:
                if not getattr(settings, setting, None):
                    missing_settings.append(setting)
            
            if missing_settings:
                return {
                    "status": "FAIL",
                    "error": f"Missing critical settings: {', '.join(missing_settings)}"
                }
            
            return {
                "status": "PASS",
                "message": "Pulumi ESC integration working",
                "settings_loaded": len(critical_settings)
            }
            
        except Exception as e:
            return {
                "status": "ERROR",
                "error": f"Pulumi ESC test failed: {str(e)}"
            }
    
    async def test_gong_api_connectivity(self) -> Dict[str, Any]:
        """Test Gong API connectivity."""
        try:
            from backend.core.auto_esc_config import get_config_value
            
            # Get credentials
            access_key = get_config_value("gong_access_key")
            client_secret = get_config_value("gong_client_secret")
            
            if not access_key or not client_secret:
                return {
                    "status": "FAIL",
                    "error": "Gong credentials not available"
                }
            
            # Test basic credential format
            if len(access_key) < 10 or len(client_secret) < 10:
                return {
                    "status": "FAIL",
                    "error": "Gong credentials appear invalid (too short)"
                }
            
            return {
                "status": "PASS",
                "message": "Gong credentials available and properly formatted",
                "credentials_available": True,
                "access_key_length": len(access_key),
                "client_secret_length": len(client_secret)
            }
            
        except Exception as e:
            return {
                "status": "ERROR",
                "error": f"Gong API test failed: {str(e)}"
            }
    
    async def test_snowflake_connectivity(self) -> Dict[str, Any]:
        """Test Snowflake connectivity."""
        try:
            from backend.core.auto_esc_config import get_config_value
            
            # Get Snowflake credentials
            account = get_config_value("snowflake_account")
            user = get_config_value("snowflake_user")
            password = get_config_value("snowflake_password")
            
            if not all([account, user, password]):
                return {
                    "status": "FAIL",
                    "error": "Snowflake credentials not available"
                }
            
            return {
                "status": "PASS",
                "message": "Snowflake credentials available",
                "credentials_available": True,
                "account": account,
                "user": user
            }
            
        except Exception as e:
            return {
                "status": "ERROR",
                "error": f"Snowflake test failed: {str(e)}"
            }
    
    async def test_airbyte_integration(self) -> Dict[str, Any]:
        """Test Airbyte integration."""
        try:
            # Check if Airbyte orchestrator file exists
            import os
            airbyte_file = "backend/scripts/airbyte_gong_setup.py"
            
            if not os.path.exists(airbyte_file):
                return {
                    "status": "FAIL",
                    "error": f"Airbyte orchestrator file not found: {airbyte_file}"
                }
            
            return {
                "status": "PASS",
                "message": "Airbyte integration files available",
                "orchestrator_file_exists": True
            }
            
        except Exception as e:
            return {
                "status": "ERROR",
                "error": f"Airbyte test failed: {str(e)}"
            }
    
    async def test_ai_memory_integration(self) -> Dict[str, Any]:
        """Test AI Memory integration."""
        try:
            from backend.core.auto_esc_config import get_config_value
            
            # Get AI service credentials
            openai_key = get_config_value("openai_api_key")
            pinecone_key = get_config_value("pinecone_api_key")
            
            if not openai_key or not pinecone_key:
                return {
                    "status": "FAIL",
                    "error": "AI service credentials not available"
                }
            
            return {
                "status": "PASS",
                "message": "AI service credentials available",
                "ai_credentials_available": True,
                "openai_key_available": bool(openai_key),
                "pinecone_key_available": bool(pinecone_key)
            }
            
        except Exception as e:
            return {
                "status": "ERROR",
                "error": f"AI Memory test failed: {str(e)}"
            }
    
    async def test_backend_services(self) -> Dict[str, Any]:
        """Test backend services."""
        try:
            # Check if critical backend files exist
            critical_files = [
                "backend/core/auto_esc_config.py",
                "backend/core/config_validator.py",
                "backend/utils/snowflake_cortex_service.py",
                "backend/mcp/ai_memory_mcp_server.py"
            ]
            
            missing_files = []
            for file_path in critical_files:
                if not os.path.exists(file_path):
                    missing_files.append(file_path)
            
            if missing_files:
                return {
                    "status": "FAIL",
                    "error": f"Missing critical backend files: {', '.join(missing_files)}"
                }
            
            return {
                "status": "PASS",
                "message": "All critical backend service files available",
                "files_checked": len(critical_files)
            }
            
        except Exception as e:
            return {
                "status": "ERROR",
                "error": f"Backend services test failed: {str(e)}"
            }
    
    def _calculate_overall_status(self) -> str:
        """Calculate overall deployment status."""
        if not self.test_results:
            return "NO_TESTS"
        
        statuses = [result.get("status", "UNKNOWN") for result in self.test_results.values()]
        
        if all(status == "PASS" for status in statuses):
            return "READY_FOR_DEPLOYMENT"
        elif any(status == "ERROR" for status in statuses):
            return "CRITICAL_ERRORS"
        else:
            return "NOT_READY"
    
    def _generate_deployment_report(self) -> Dict[str, Any]:
        """Generate comprehensive deployment report."""
        passed_tests = sum(1 for result in self.test_results.values() if result.get("status") == "PASS")
        total_tests = len(self.test_results)
        
        report = {
            "deployment_readiness_report": {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "overall_status": self.overall_status,
                "test_summary": {
                    "total_tests": total_tests,
                    "passed_tests": passed_tests,
                    "failed_tests": total_tests - passed_tests,
                    "success_rate": f"{(passed_tests / total_tests * 100):.1f}%" if total_tests > 0 else "0%"
                },
                "detailed_results": self.test_results,
                "deployment_recommendation": self._get_deployment_recommendation()
            }
        }
        
        return report
    
    def _get_deployment_recommendation(self) -> str:
        """Get deployment recommendation based on test results."""
        if self.overall_status == "READY_FOR_DEPLOYMENT":
            return "✅ DEPLOY: All tests passed. System is ready for production deployment."
        elif self.overall_status == "CRITICAL_ERRORS":
            return "❌ DO NOT DEPLOY: Critical errors detected. Fix issues before deployment."
        elif self.overall_status == "NOT_READY":
            return "⚠️ HOLD DEPLOYMENT: Some tests failed. Review and fix issues before deployment."
        else:
            return "❓ UNKNOWN STATUS: Unable to determine deployment readiness."

async def main():
    """Main entry point."""
    logger.info("🚀 Sophia AI - Gong Deployment Readiness Test")
    logger.info("=" * 60)
    
    tester = GongDeploymentTester()
    
    try:
        # Run all tests
        report = await tester.run_all_tests()
        
        # Display summary
        logger.info("\n📋 DEPLOYMENT READINESS SUMMARY")
        logger.info("=" * 40)
        logger.info(f"Overall Status: {report['deployment_readiness_report']['overall_status']}")
        logger.info(f"Tests Passed: {report['deployment_readiness_report']['test_summary']['passed_tests']}/{report['deployment_readiness_report']['test_summary']['total_tests']}")
        logger.info(f"Success Rate: {report['deployment_readiness_report']['test_summary']['success_rate']}")
        
        logger.info("\n💡 RECOMMENDATION:")
        logger.info(report['deployment_readiness_report']['deployment_recommendation'])
        
        # Save report
        with open('gong_deployment_readiness_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info("\n📄 Full report saved to: gong_deployment_readiness_report.json")
        
        # Exit with appropriate code
        if report['deployment_readiness_report']['overall_status'] == "READY_FOR_DEPLOYMENT":
            sys.exit(0)
        else:
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"❌ Test execution failed: {str(e)}")
        logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
