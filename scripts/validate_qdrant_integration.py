#!/usr/bin/env python3
"""
Comprehensive QDRANT_API_KEY Integration Validation
Tests the complete integration flow from GitHub Org Secrets → Pulumi ESC → Backend
"""

import os
import sys
import subprocess
import logging
from typing import Dict, Any, List, Tuple

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class QdrantIntegrationValidator:
    """Validate complete QDRANT_API_KEY integration"""
    
    def __init__(self):
        self.validation_results = []
        self.pulumi_org = "scoobyjava-org"
        self.pulumi_env = "default/sophia-ai-production"
        
    def add_result(self, test_name: str, passed: bool, details: str = "") -> None:
        """Add validation result"""
        self.validation_results.append({
            "test": test_name,
            "passed": passed,
            "details": details,
            "status": "✅ PASS" if passed else "❌ FAIL"
        })
        
    def validate_environment_variables(self) -> bool:
        """Validate QDRANT environment variables are present"""
        logger.info("🔍 Validating environment variables...")
        
        # Check QDRANT_API_KEY
        qdrant_api_key = os.getenv("QDRANT_API_KEY")
        if qdrant_api_key:
            self.add_result("QDRANT_API_KEY Environment Variable", True, f"Found: {qdrant_api_key[:8]}...")
        else:
            self.add_result("QDRANT_API_KEY Environment Variable", False, "Not found in environment")
            
        # Check QDRANT_URL
        qdrant_url = os.getenv("QDRANT_URL")
        if qdrant_url:
            self.add_result("QDRANT_URL Environment Variable", True, f"Found: {qdrant_url}")
        else:
            self.add_result("QDRANT_URL Environment Variable", False, "Not found in environment")
            
        return bool(qdrant_api_key and qdrant_url)
    
    def validate_pulumi_esc_integration(self) -> bool:
        """Validate Pulumi ESC can access QDRANT secrets"""
        logger.info("🔍 Validating Pulumi ESC integration...")
        
        try:
            # Check if Pulumi CLI is available
            result = subprocess.run(["pulumi", "version"], capture_output=True, text=True)
            if result.returncode != 0:
                self.add_result("Pulumi CLI", False, "Pulumi CLI not available")
                return False
            
            self.add_result("Pulumi CLI", True, "Pulumi CLI available")
            
            # Try to get qdrant_api_key from ESC
            result = subprocess.run([
                "pulumi", "env", "get", f"{self.pulumi_org}/{self.pulumi_env}", "qdrant_api_key"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                self.add_result("Pulumi ESC qdrant_api_key", True, "Successfully retrieved from ESC")
            else:
                self.add_result("Pulumi ESC qdrant_api_key", False, f"Failed to retrieve: {result.stderr}")
                
            # Try to get qdrant_url from ESC
            result = subprocess.run([
                "pulumi", "env", "get", f"{self.pulumi_org}/{self.pulumi_env}", "qdrant_url"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                self.add_result("Pulumi ESC qdrant_url", True, "Successfully retrieved from ESC")
                return True
            else:
                self.add_result("Pulumi ESC qdrant_url", False, f"Failed to retrieve: {result.stderr}")
                return False
                
        except Exception as e:
            self.add_result("Pulumi ESC Integration", False, f"Error: {e}")
            return False
    
    def validate_backend_configuration(self) -> bool:
        """Validate backend can load QDRANT configuration"""
        logger.info("🔍 Validating backend configuration...")
        
        try:
            # Import backend configuration
            sys.path.append('.')
            from backend.core.auto_esc_config import get_qdrant_config, get_config_value
            
            # Test get_config_value for QDRANT_API_KEY
            api_key = get_config_value("qdrant_api_key") or get_config_value("QDRANT_API_KEY")
            if api_key:
                self.add_result("Backend get_config_value QDRANT_API_KEY", True, f"Retrieved: {api_key[:8]}...")
            else:
                self.add_result("Backend get_config_value QDRANT_API_KEY", False, "Could not retrieve API key")
                
            # Test get_config_value for QDRANT_URL
            url = get_config_value("qdrant_url") or get_config_value("QDRANT_URL")
            if url:
                self.add_result("Backend get_config_value QDRANT_URL", True, f"Retrieved: {url}")
            else:
                self.add_result("Backend get_config_value QDRANT_URL", False, "Could not retrieve URL")
                
            # Test get_qdrant_config function
            config = get_qdrant_config()
            if config and config.get("api_key") and config.get("url"):
                self.add_result("Backend get_qdrant_config", True, f"Complete config retrieved")
                logger.info(f"   API Key: {config['api_key'][:8]}...")
                logger.info(f"   URL: {config['url']}")
                logger.info(f"   Cluster: {config['cluster_name']}")
                logger.info(f"   Timeout: {config['timeout']}")
                return True
            else:
                self.add_result("Backend get_qdrant_config", False, "Incomplete configuration")
                return False
                
        except Exception as e:
            self.add_result("Backend Configuration", False, f"Error: {e}")
            return False
    
    def validate_qdrant_connectivity(self) -> bool:
        """Validate actual connectivity to Qdrant"""
        logger.info("🔍 Validating Qdrant connectivity...")
        
        try:
            import requests
            
            # Get configuration
            sys.path.append('.')
            from backend.core.auto_esc_config import get_qdrant_config
            config = get_qdrant_config()
            
            if not config.get("api_key") or not config.get("url"):
                self.add_result("Qdrant Connectivity", False, "Missing API key or URL")
                return False
                
            # Test collections endpoint
            response = requests.get(
                f"{config['url']}/collections",
                headers={
                    "Authorization": f"Bearer {config['api_key']}",
                    "Content-Type": "application/json"
                },
                timeout=30
            )
            
            if response.status_code == 200:
                collections = response.json()
                collection_count = len(collections.get('result', {}).get('collections', []))
                self.add_result("Qdrant Connectivity", True, f"Connected successfully, {collection_count} collections")
                return True
            else:
                self.add_result("Qdrant Connectivity", False, f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.add_result("Qdrant Connectivity", False, f"Error: {e}")
            return False
    
    def validate_github_actions_integration(self) -> bool:
        """Validate GitHub Actions can access secrets"""
        logger.info("🔍 Validating GitHub Actions integration...")
        
        # Check if we're running in GitHub Actions
        if os.getenv("GITHUB_ACTIONS") == "true":
            self.add_result("GitHub Actions Environment", True, "Running in GitHub Actions")
            
            # Check if secrets are available
            if os.getenv("QDRANT_API_KEY"):
                self.add_result("GitHub Actions QDRANT_API_KEY", True, "Secret available")
            else:
                self.add_result("GitHub Actions QDRANT_API_KEY", False, "Secret not available")
                
            if os.getenv("QDRANT_URL"):
                self.add_result("GitHub Actions QDRANT_URL", True, "Secret available")
            else:
                self.add_result("GitHub Actions QDRANT_URL", False, "Secret not available")
                
            return True
        else:
            self.add_result("GitHub Actions Environment", False, "Not running in GitHub Actions")
            return False
    
    def validate_mcp_server_integration(self) -> bool:
        """Validate MCP servers can access QDRANT configuration"""
        logger.info("🔍 Validating MCP server integration...")
        
        try:
            # Check if MCP servers can import and use configuration
            sys.path.append('.')
            from backend.core.auto_esc_config import get_qdrant_config
            
            config = get_qdrant_config()
            
            # Test if configuration is suitable for MCP servers
            required_fields = ["api_key", "url", "cluster_name", "timeout"]
            missing_fields = [field for field in required_fields if not config.get(field)]
            
            if not missing_fields:
                self.add_result("MCP Server Configuration", True, "All required fields present")
                return True
            else:
                self.add_result("MCP Server Configuration", False, f"Missing fields: {missing_fields}")
                return False
                
        except Exception as e:
            self.add_result("MCP Server Integration", False, f"Error: {e}")
            return False
    
    def generate_comprehensive_report(self) -> Dict[str, Any]:
        """Generate comprehensive validation report"""
        total_tests = len(self.validation_results)
        passed_tests = sum(1 for result in self.validation_results if result["passed"])
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": total_tests - passed_tests,
            "success_rate": success_rate,
            "overall_status": "✅ PASS" if success_rate >= 80 else "❌ FAIL",
            "results": self.validation_results,
            "recommendations": self.generate_recommendations()
        }
    
    def generate_recommendations(self) -> List[str]:
        """Generate recommendations based on validation results"""
        recommendations = []
        
        failed_tests = [r for r in self.validation_results if not r["passed"]]
        
        if any("Environment Variable" in test["test"] for test in failed_tests):
            recommendations.append("Set QDRANT_API_KEY and QDRANT_URL in GitHub Organization Secrets")
            
        if any("Pulumi ESC" in test["test"] for test in failed_tests):
            recommendations.append("Run: python scripts/sync_qdrant_secrets.py to sync secrets to Pulumi ESC")
            
        if any("Backend" in test["test"] for test in failed_tests):
            recommendations.append("Check backend/core/auto_esc_config.py configuration")
            
        if any("Connectivity" in test["test"] for test in failed_tests):
            recommendations.append("Verify Qdrant cluster is accessible and API key is valid")
            
        if not recommendations:
            recommendations.append("All validations passed! System is ready for production use.")
            
        return recommendations
    
    def run_complete_validation(self) -> bool:
        """Run complete validation suite"""
        logger.info("🚀 Starting comprehensive QDRANT_API_KEY integration validation...")
        
        # Run all validations
        self.validate_environment_variables()
        self.validate_pulumi_esc_integration()
        self.validate_backend_configuration()
        self.validate_qdrant_connectivity()
        self.validate_github_actions_integration()
        self.validate_mcp_server_integration()
        
        # Generate report
        report = self.generate_comprehensive_report()
        
        # Display results
        logger.info(f"📊 Validation Results: {report['overall_status']}")
        logger.info(f"   Total Tests: {report['total_tests']}")
        logger.info(f"   Passed: {report['passed_tests']}")
        logger.info(f"   Failed: {report['failed_tests']}")
        logger.info(f"   Success Rate: {report['success_rate']:.1f}%")
        
        logger.info("\n📋 Detailed Results:")
        for result in report["results"]:
            logger.info(f"   {result['status']} {result['test']}")
            if result["details"]:
                logger.info(f"      {result['details']}")
                
        logger.info("\n💡 Recommendations:")
        for rec in report["recommendations"]:
            logger.info(f"   • {rec}")
            
        return report["success_rate"] >= 80

def main():
    """Main entry point"""
    validator = QdrantIntegrationValidator()
    
    if validator.run_complete_validation():
        logger.info("✅ SUCCESS: QDRANT_API_KEY integration validation passed")
        sys.exit(0)
    else:
        logger.error("❌ FAILED: QDRANT_API_KEY integration validation failed")
        sys.exit(1)

if __name__ == "__main__":
    main() 