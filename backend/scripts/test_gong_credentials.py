#!/usr/bin/env python3
"""
Gong Credentials Testing Script

Tests Gong API credentials from multiple sources:
1. Pulumi ESC integration
2. Environment variables  
3. Manual credential input

Usage:
    python backend/scripts/test_gong_credentials.py
    python backend/scripts/test_gong_credentials.py --test-api
    python backend/scripts/test_gong_credentials.py --manual-test
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
import argparse

import aiohttp

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GongCredentialTester:
    """
    Comprehensive Gong credential testing and validation
    """

    def __init__(self):
        self.test_results = []
        self.credentials_found = {}

    async def test_all_credential_sources(self) -> Dict[str, Any]:
        """Test credentials from all possible sources"""
        logger.info("🔍 Testing Gong Credentials from All Sources")
        logger.info("=" * 60)
        
        # Test 1: Pulumi ESC
        await self._test_pulumi_esc_credentials()
        
        # Test 2: Environment Variables
        await self._test_environment_variables()
        
        # Test 3: GitHub Organization Secrets (if available)
        await self._test_github_secrets()
        
        # Generate summary
        return self._generate_credential_report()

    async def _test_pulumi_esc_credentials(self) -> None:
        """Test credentials from Pulumi ESC"""
        logger.info("📋 Testing Pulumi ESC Integration")
        
        try:
            from backend.core.auto_esc_config import get_config_value
            
            # Test various naming patterns for Gong credentials
            credential_patterns = [
                ('gong_access_key', 'GONG_ACCESS_KEY'),
                ('gong_client_secret', 'GONG_CLIENT_SECRET'), 
                ('GONG_ACCESS_KEY', 'GONG_ACCESS_KEY'),
                ('GONG_CLIENT_SECRET', 'GONG_CLIENT_SECRET'),
                ('gong_access_key_secret', 'GONG_ACCESS_KEY_SECRET'),
                ('GONG_ACCESS_KEY_SECRET', 'GONG_ACCESS_KEY_SECRET'),
                ('gong_client_access_key', 'GONG_CLIENT_ACCESS_KEY'),
                ('GONG_CLIENT_ACCESS_KEY', 'GONG_CLIENT_ACCESS_KEY'),
                ('gong_base_url', 'GONG_BASE_URL'),
                ('GONG_BASE_URL', 'GONG_BASE_URL')
            ]
            
            found_credentials = {}
            
            for key_name, display_name in credential_patterns:
                try:
                    value = get_config_value(key_name)
                    if value:
                        found_credentials[display_name] = value
                        if 'secret' in key_name.lower() or 'key' in key_name.lower():
                            logger.info(f"✅ {display_name}: {value[:8]}...")
                        else:
                            logger.info(f"✅ {display_name}: {value}")
                except Exception as e:
                    logger.debug(f"❌ {display_name}: Not found")
            
            if found_credentials:
                self.credentials_found['pulumi_esc'] = found_credentials
                logger.info(f"✅ Pulumi ESC: Found {len(found_credentials)} credentials")
            else:
                logger.warning("❌ Pulumi ESC: No Gong credentials found")
                
        except Exception as e:
            logger.error(f"❌ Pulumi ESC test failed: {e}")

    async def _test_environment_variables(self) -> None:
        """Test credentials from environment variables"""
        logger.info("\n📋 Testing Environment Variables")
        
        # Check for Gong-related environment variables
        gong_env_vars = {}
        
        env_patterns = [
            'GONG_ACCESS_KEY',
            'GONG_CLIENT_SECRET', 
            'GONG_ACCESS_KEY_SECRET',
            'GONG_CLIENT_ACCESS_KEY',
            'GONG_BASE_URL'
        ]
        
        for pattern in env_patterns:
            value = os.environ.get(pattern)
            if value:
                gong_env_vars[pattern] = value
                if 'secret' in pattern.lower() or 'key' in pattern.lower():
                    logger.info(f"✅ {pattern}: {value[:8]}...")
                else:
                    logger.info(f"✅ {pattern}: {value}")
        
        if gong_env_vars:
            self.credentials_found['environment'] = gong_env_vars
            logger.info(f"✅ Environment: Found {len(gong_env_vars)} credentials")
        else:
            logger.warning("❌ Environment: No Gong credentials found")

    async def _test_github_secrets(self) -> None:
        """Test if GitHub secrets are available"""
        logger.info("\n📋 Testing GitHub Organization Secrets Access")
        
        # The GitHub secrets you mentioned:
        github_secrets = [
            'GONG_ACCESS_KEY',
            'GONG_ACCESS_KEY_SECRET', 
            'GONG_BASE_URL',
            'GONG_CLIENT_ACCESS_KEY',
            'GONG_CLIENT_SECRET'
        ]
        
        logger.info("Expected GitHub Organization Secrets:")
        for secret in github_secrets:
            logger.info(f"  📝 {secret}")
        
        logger.info("\n💡 GitHub secrets need to be synchronized to Pulumi ESC or environment")

    async def test_gong_api_connectivity(self, access_key: str = None, client_secret: str = None) -> Dict[str, Any]:
        """Test Gong API connectivity with provided credentials"""
        logger.info("\n🌐 Testing Gong API Connectivity")
        
        # Try to get credentials from found sources if not provided
        if not access_key or not client_secret:
            access_key, client_secret = self._get_best_credentials()
        
        if not access_key or not client_secret:
            return {
                "success": False,
                "message": "No valid Gong credentials found for API testing",
                "recommendations": [
                    "Ensure GitHub organization secrets are synchronized to Pulumi ESC",
                    "Set GONG_ACCESS_KEY and GONG_CLIENT_SECRET environment variables",
                    "Verify Pulumi ESC access and authentication"
                ]
            }
        
        try:
            auth = aiohttp.BasicAuth(access_key, client_secret)
            
            async with aiohttp.ClientSession() as session:
                # Test Gong API workspaces endpoint
                async with session.get(
                    "https://api.gong.io/v2/workspaces",
                    auth=auth,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        workspaces = data.get("workspaces", [])
                        
                        logger.info(f"✅ Gong API: Connection successful")
                        logger.info(f"📊 Found {len(workspaces)} workspaces")
                        
                        for workspace in workspaces[:3]:  # Show first 3
                            logger.info(f"  🏢 {workspace.get('name', 'Unknown')}")
                        
                        return {
                            "success": True,
                            "message": "Gong API connection successful",
                            "workspaces_count": len(workspaces),
                            "workspaces": [w.get("name", "Unknown") for w in workspaces],
                            "api_status": response.status,
                            "credentials_used": {
                                "access_key_prefix": access_key[:8] + "...",
                                "has_client_secret": bool(client_secret)
                            }
                        }
                    
                    elif response.status == 401:
                        error_text = await response.text()
                        logger.error(f"❌ Gong API: Authentication failed (401)")
                        logger.error(f"Response: {error_text}")
                        
                        return {
                            "success": False,
                            "message": "Gong API authentication failed - invalid credentials",
                            "api_status": response.status,
                            "error_details": error_text,
                            "recommendations": [
                                "Verify Gong API credentials are correct",
                                "Check if credentials have required scopes: calls:read, transcript:read, users:read, workspaces:read, analytics:read",
                                "Ensure credentials are not expired"
                            ]
                        }
                    
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ Gong API: Request failed ({response.status})")
                        logger.error(f"Response: {error_text}")
                        
                        return {
                            "success": False,
                            "message": f"Gong API request failed with status {response.status}",
                            "api_status": response.status,
                            "error_details": error_text
                        }
                        
        except Exception as e:
            logger.error(f"❌ Gong API test failed: {e}")
            return {
                "success": False,
                "message": f"Gong API test failed: {str(e)}",
                "error_type": type(e).__name__
            }

    def _get_best_credentials(self) -> Tuple[Optional[str], Optional[str]]:
        """Get the best available credentials from found sources"""
        access_key = None
        client_secret = None
        
        # Priority 1: Pulumi ESC
        if 'pulumi_esc' in self.credentials_found:
            creds = self.credentials_found['pulumi_esc']
            access_key = (creds.get('GONG_ACCESS_KEY') or 
                         creds.get('GONG_CLIENT_ACCESS_KEY') or
                         creds.get('gong_access_key'))
            client_secret = (creds.get('GONG_CLIENT_SECRET') or
                           creds.get('GONG_ACCESS_KEY_SECRET') or
                           creds.get('gong_client_secret'))
        
        # Priority 2: Environment variables
        if not access_key or not client_secret:
            if 'environment' in self.credentials_found:
                creds = self.credentials_found['environment']
                access_key = access_key or (creds.get('GONG_ACCESS_KEY') or 
                                          creds.get('GONG_CLIENT_ACCESS_KEY'))
                client_secret = client_secret or (creds.get('GONG_CLIENT_SECRET') or
                                                creds.get('GONG_ACCESS_KEY_SECRET'))
        
        return access_key, client_secret

    def _generate_credential_report(self) -> Dict[str, Any]:
        """Generate comprehensive credential report"""
        access_key, client_secret = self._get_best_credentials()
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "credential_sources": {
                "pulumi_esc": {
                    "available": 'pulumi_esc' in self.credentials_found,
                    "credentials_count": len(self.credentials_found.get('pulumi_esc', {}))
                },
                "environment": {
                    "available": 'environment' in self.credentials_found,
                    "credentials_count": len(self.credentials_found.get('environment', {}))
                }
            },
            "best_credentials": {
                "access_key_available": bool(access_key),
                "client_secret_available": bool(client_secret),
                "ready_for_api_test": bool(access_key and client_secret)
            },
            "github_organization_secrets": {
                "configured": [
                    "GONG_ACCESS_KEY",
                    "GONG_ACCESS_KEY_SECRET", 
                    "GONG_BASE_URL",
                    "GONG_CLIENT_ACCESS_KEY",
                    "GONG_CLIENT_SECRET"
                ],
                "sync_status": "Needs synchronization to Pulumi ESC or environment"
            },
            "recommendations": self._generate_recommendations()
        }

    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on credential status"""
        recommendations = []
        
        access_key, client_secret = self._get_best_credentials()
        
        if not access_key or not client_secret:
            recommendations.extend([
                "🔑 Synchronize GitHub organization secrets to Pulumi ESC",
                "🔧 Set up Pulumi ESC authentication (PULUMI_ACCESS_TOKEN)",
                "⚙️ Alternatively, set environment variables directly:",
                "   export GONG_ACCESS_KEY='your_access_key'",
                "   export GONG_CLIENT_SECRET='your_client_secret'",
                "🧪 Test credentials with: python backend/scripts/test_gong_credentials.py --test-api"
            ])
        else:
            recommendations.extend([
                "✅ Credentials found - ready for Gong API testing",
                "🚀 Proceed with Airbyte setup once API connectivity confirmed",
                "📊 Run full deployment test suite"
            ])
        
        return recommendations

    def print_summary(self, report: Dict[str, Any]) -> None:
        """Print comprehensive summary"""
        logger.info("\n" + "=" * 80)
        logger.info("🎯 GONG CREDENTIALS SUMMARY")
        logger.info("=" * 80)
        
        # Credential sources
        logger.info("📋 Credential Sources:")
        for source, info in report["credential_sources"].items():
            status = "✅" if info["available"] else "❌"
            logger.info(f"  {status} {source.title()}: {info['credentials_count']} credentials")
        
        # Best credentials status
        best = report["best_credentials"]
        logger.info(f"\n🔑 Best Available Credentials:")
        logger.info(f"  Access Key: {'✅' if best['access_key_available'] else '❌'}")
        logger.info(f"  Client Secret: {'✅' if best['client_secret_available'] else '❌'}")
        logger.info(f"  API Test Ready: {'✅' if best['ready_for_api_test'] else '❌'}")
        
        # GitHub secrets
        logger.info(f"\n📝 GitHub Organization Secrets:")
        for secret in report["github_organization_secrets"]["configured"]:
            logger.info(f"  📄 {secret}")
        logger.info(f"  Status: {report['github_organization_secrets']['sync_status']}")
        
        # Recommendations
        logger.info(f"\n💡 Recommendations:")
        for rec in report["recommendations"]:
            logger.info(f"  {rec}")
        
        logger.info("=" * 80)


async def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Gong Credentials Tester")
    parser.add_argument("--test-api", action="store_true", 
                       help="Test Gong API connectivity")
    parser.add_argument("--manual-test", action="store_true",
                       help="Manual credential input for testing")
    parser.add_argument("--output", help="Output file for results (JSON)")
    
    args = parser.parse_args()
    
    tester = GongCredentialTester()
    
    # Test all credential sources
    report = await tester.test_all_credential_sources()
    
    # Test API if requested or credentials are available
    if args.test_api or report["best_credentials"]["ready_for_api_test"]:
        api_result = await tester.test_gong_api_connectivity()
        report["api_test"] = api_result
    
    # Manual test if requested
    if args.manual_test:
        logger.info("\n🔧 Manual Credential Test")
        access_key = input("Enter Gong Access Key: ").strip()
        client_secret = input("Enter Gong Client Secret: ").strip()
        
        if access_key and client_secret:
            api_result = await tester.test_gong_api_connectivity(access_key, client_secret)
            report["manual_api_test"] = api_result
    
    # Print summary
    tester.print_summary(report)
    
    # Save results if requested
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(report, f, indent=2)
        logger.info(f"\n💾 Results saved to: {args.output}")
    
    # Exit with appropriate code
    if report["best_credentials"]["ready_for_api_test"]:
        if "api_test" in report and report["api_test"]["success"]:
            logger.info("\n🎉 SUCCESS: Gong credentials are valid and API is accessible!")
            sys.exit(0)
        else:
            logger.error("\n❌ FAILED: Gong API test failed")
            sys.exit(1)
    else:
        logger.warning("\n⏳ PENDING: Gong credentials need to be configured")
        sys.exit(2)


if __name__ == "__main__":
    asyncio.run(main()) 