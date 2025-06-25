#!/usr/bin/env python3
"""
Test current Gong credentials from Pulumi ESC
This script validates that Gong credentials are properly synced and accessible.
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_gong_credentials():
    """Test Gong credentials from Pulumi ESC."""
    logger.info("🔍 Testing Gong credentials from Pulumi ESC")
    logger.info("=" * 50)
    
    try:
        # Import after setting up the path
        sys.path.append('.')
        from backend.core.auto_esc_config import get_config_value
        
        # Test Gong credentials
        gong_access_key = get_config_value("gong_access_key")
        gong_client_secret = get_config_value("gong_client_secret")
        
        results = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "test_results": {},
            "overall_status": "UNKNOWN"
        }
        
        # Test 1: Check if credentials exist
        logger.info("🔑 Testing credential availability...")
        if gong_access_key and gong_client_secret:
            logger.info("✅ Gong credentials found in Pulumi ESC")
            results["test_results"]["credential_availability"] = {
                "status": "PASS",
                "access_key_length": len(gong_access_key),
                "client_secret_length": len(gong_client_secret),
                "access_key_prefix": gong_access_key[:8] + "..." if len(gong_access_key) > 8 else "short"
            }
        else:
            logger.error("❌ Gong credentials not found")
            results["test_results"]["credential_availability"] = {
                "status": "FAIL",
                "error": "Gong credentials not found in Pulumi ESC",
                "access_key_found": bool(gong_access_key),
                "client_secret_found": bool(gong_client_secret)
            }
        
        # Test 2: Validate credential format
        logger.info("🧪 Testing credential format...")
        if gong_access_key and gong_client_secret:
            if len(gong_access_key) > 10 and len(gong_client_secret) > 10:
                logger.info("✅ Gong credentials appear properly formatted")
                results["test_results"]["credential_format"] = {
                    "status": "PASS",
                    "message": "Credentials appear properly formatted"
                }
            else:
                logger.warning("⚠️ Gong credentials appear too short")
                results["test_results"]["credential_format"] = {
                    "status": "WARN",
                    "message": "Credentials may be too short or invalid"
                }
        else:
            results["test_results"]["credential_format"] = {
                "status": "SKIP",
                "message": "No credentials to validate"
            }
        
        # Test 3: Check other critical secrets
        logger.info("🔍 Testing other critical secrets...")
        other_secrets = {
            "openai_api_key": get_config_value("openai_api_key"),
            "snowflake_account": get_config_value("snowflake_account"),
            "snowflake_password": get_config_value("snowflake_password"),
            "pinecone_api_key": get_config_value("pinecone_api_key")
        }
        
        missing_secrets = []
        for secret_name, secret_value in other_secrets.items():
            if not secret_value:
                missing_secrets.append(secret_name)
        
        if not missing_secrets:
            logger.info("✅ All critical secrets available")
            results["test_results"]["other_secrets"] = {
                "status": "PASS",
                "secrets_checked": len(other_secrets),
                "all_available": True
            }
        else:
            logger.warning(f"⚠️ Missing secrets: {', '.join(missing_secrets)}")
            results["test_results"]["other_secrets"] = {
                "status": "WARN",
                "secrets_checked": len(other_secrets),
                "missing_secrets": missing_secrets
            }
        
        # Determine overall status
        test_statuses = [test["status"] for test in results["test_results"].values()]
        if all(status == "PASS" for status in test_statuses):
            results["overall_status"] = "READY"
            logger.info("🎉 Overall Status: READY - All tests passed")
        elif any(status == "FAIL" for status in test_statuses):
            results["overall_status"] = "FAILED"
            logger.error("❌ Overall Status: FAILED - Critical tests failed")
        else:
            results["overall_status"] = "WARNING"
            logger.warning("⚠️ Overall Status: WARNING - Some tests have warnings")
        
        # Save results
        with open('gong_credential_test_results.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info("📄 Results saved to: gong_credential_test_results.json")
        
        return results["overall_status"] == "READY"
        
    except Exception as e:
        logger.error(f"❌ Test failed with error: {str(e)}")
        error_results = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "overall_status": "ERROR",
            "error": str(e)
        }
        
        with open('gong_credential_test_results.json', 'w') as f:
            json.dump(error_results, f, indent=2)
        
        return False

async def main():
    """Main entry point."""
    logger.info("🚀 Gong Credential Test")
    logger.info("Testing credentials from Pulumi ESC...")
    
    # Set Pulumi org environment variable
    os.environ["PULUMI_ORG"] = "scoobyjava-org"
    
    success = await test_gong_credentials()
    
    if success:
        logger.info("✅ All credential tests passed!")
        sys.exit(0)
    else:
        logger.error("❌ Credential tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
