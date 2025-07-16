#!/usr/bin/env python3
"""
Qdrant Secrets Sync Script
Syncs QDRANT_API_KEY from GitHub Organization Secrets to Pulumi ESC

This script ensures the QDRANT_API_KEY is properly synchronized between:
1. GitHub Organization Secrets (source of truth)
2. Pulumi ESC (sophia-ai-production stack)
3. Backend configuration (auto_esc_config.py)

Usage:
    python scripts/ci/sync_QDRANT_secrets.py
    python scripts/ci/sync_QDRANT_secrets.py --validate-only

Date: January 15, 2025
"""

import os
import sys
import json
import subprocess
from typing import Dict, Any
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.core.auto_esc_config import get_QDRANT_config
from backend.utils.logger import get_logger

logger = get_logger(__name__)

class QdrantSecretsSync:
    """Handles synchronization of Qdrant secrets"""
    
    def __init__(self):
        self.pulumi_org = "scoobyjava-org"
        self.pulumi_stack = "sophia-ai-production"
        self.github_org = "ai-cherry"
        
        # Secret mappings from GitHub Org Secrets to Pulumi ESC
        self.secret_mappings = {
            "QDRANT_API_KEY": "QDRANT_api_key",
            "QDRANT_URL": "QDRANT_URL", 
            "QDRANT_CLUSTER_NAME": "QDRANT_cluster_name",
            "QDRANT_TIMEOUT": "QDRANT_timeout",
            "QDRANT_PREFER_GRPC": "QDRANT_prefer_grpc"
        }
        
        # Default values for optional secrets
        self.default_values = {
            "QDRANT_URL": "https://xyz.qdrant.tech",
            "QDRANT_cluster_name": "sophia-ai-production", 
            "QDRANT_timeout": "30",
            "QDRANT_prefer_grpc": "false"
        }
        
    async def sync_all_secrets(self):
        """Sync all Qdrant-related secrets"""
        logger.info("🔄 Starting Qdrant secrets synchronization...")
        
        success_count = 0
        error_count = 0
        
        for github_secret, esc_key in self.secret_mappings.items():
            try:
                # Get secret from environment (GitHub Actions provides these)
                secret_value = os.getenv(github_secret)
                
                if secret_value:
                    await self._sync_secret_to_esc(esc_key, secret_value)
                    success_count += 1
                    logger.info(f"✅ Synced {github_secret} -> {esc_key}")
                elif esc_key in self.default_values:
                    # Set default value
                    await self._sync_secret_to_esc(esc_key, self.default_values[esc_key])
                    success_count += 1
                    logger.info(f"✅ Set default {esc_key} = {self.default_values[esc_key]}")
                else:
                    logger.warning(f"⚠️ {github_secret} not found and no default available")
                    error_count += 1
                    
            except Exception as e:
                logger.error(f"❌ Failed to sync {github_secret}: {e}")
                error_count += 1
                
        logger.info(f"📊 Sync completed: {success_count} success, {error_count} errors")
        
        if error_count > 0 and success_count == 0:
            raise Exception("All secret synchronization failed")
            
    async def _sync_secret_to_esc(self, key: str, value: str):
        """Sync a single secret to Pulumi ESC"""
        try:
            # Use pulumi env set command
            cmd = [
                "pulumi", "env", "set",
                f"{self.pulumi_org}/default/{self.pulumi_stack}",
                key,
                value
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                timeout=30
            )
            
            logger.debug(f"Pulumi env set output: {result.stdout}")
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Pulumi env set failed: {e.stderr}")
            raise
        except subprocess.TimeoutExpired:
            logger.error("Pulumi env set timed out")
            raise
            
    async def validate_secrets(self) -> Dict[str, Any]:
        """Validate that all secrets are properly configured"""
        logger.info("🔍 Validating Qdrant secrets configuration...")
        
        validation_results = {
            "status": "success",
            "secrets_found": 0,
            "secrets_missing": 0,
            "errors": [],
            "config": {}
        }
        
        try:
            # Test Qdrant configuration loading
            QDRANT_config = get_QDRANT_config()
            validation_results["config"] = QDRANT_config
            
            # Check each required secret
            required_secrets = ["api_key"]
            optional_secrets = ["url", "cluster_name", "timeout", "prefer_grpc"]
            
            for secret in required_secrets:
                if QDRANT_config.get(secret):
                    validation_results["secrets_found"] += 1
                    logger.info(f"✅ Required secret '{secret}' found")
                else:
                    validation_results["secrets_missing"] += 1
                    validation_results["errors"].append(f"Required secret '{secret}' missing")
                    logger.error(f"❌ Required secret '{secret}' missing")
                    
            for secret in optional_secrets:
                if QDRANT_config.get(secret):
                    validation_results["secrets_found"] += 1
                    logger.info(f"✅ Optional secret '{secret}' found: {QDRANT_config[secret]}")
                else:
                    logger.warning(f"⚠️ Optional secret '{secret}' not configured")
                    
            # Test API key format
            api_key = QDRANT_config.get("api_key")
            if api_key:
                if self._validate_api_key_format(api_key):
                    logger.info("✅ API key format validation passed")
                else:
                    validation_results["errors"].append("API key format validation failed")
                    logger.error("❌ API key format validation failed")
                    
        except Exception as e:
            validation_results["status"] = "error"
            validation_results["errors"].append(str(e))
            logger.error(f"❌ Validation failed: {e}")
            
        if validation_results["errors"]:
            validation_results["status"] = "error"
            
        return validation_results
        
    def _validate_api_key_format(self, api_key: str) -> bool:
        """Validate Qdrant API key format"""
        # Qdrant API keys are typically UUIDs with additional characters
        # Format: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx|additional_chars
        if not api_key:
            return False
            
        # Check if it contains the expected format
        if "|" in api_key:
            uuid_part, additional_part = api_key.split("|", 1)
            # Basic UUID format check
            if len(uuid_part) == 36 and uuid_part.count("-") == 4:
                return True
                
        return False
        
    async def test_QDRANT_connection(self) -> Dict[str, Any]:
        """Test actual connection to Qdrant using the configured secrets"""
        logger.info("🔗 Testing Qdrant connection...")
        
        test_results = {
            "status": "unknown",
            "connection_successful": False,
            "api_accessible": False,
            "cluster_info": None,
            "error": None
        }
        
        try:
            # Import and test Qdrant service
                        
            QDRANT_service = QdrantSophiaUnifiedMemoryService()
            await QDRANT_service.initialize()
            
            # Test health check
            health = await QDRANT_service.health_check()
            
            if health["status"] == "healthy":
                test_results["status"] = "success"
                test_results["connection_successful"] = True
                test_results["api_accessible"] = True
                logger.info("✅ Qdrant connection test successful")
            else:
                test_results["status"] = "degraded"
                test_results["error"] = f"Health check failed: {health}"
                logger.warning(f"⚠️ Qdrant connection degraded: {health}")
                
            # Get cluster info
            try:
                stats = await QDRANT_service.get_performance_stats()
                test_results["cluster_info"] = stats
                logger.info(f"📊 Cluster info: {len(stats.get('collections', {}))} collections")
            except Exception as e:
                logger.warning(f"⚠️ Could not get cluster info: {e}")
                
            await QDRANT_service.cleanup()
            
        except ImportError as e:
            test_results["status"] = "error"
            test_results["error"] = f"Qdrant client not available: {e}"
            logger.error(f"❌ Qdrant client import failed: {e}")
        except Exception as e:
            test_results["status"] = "error"
            test_results["error"] = str(e)
            logger.error(f"❌ Qdrant connection test failed: {e}")
            
        return test_results
        
    async def generate_sync_report(self):
        """Generate comprehensive sync report"""
        logger.info("📄 Generating Qdrant secrets sync report...")
        
        # Validate secrets
        validation = await self.validate_secrets()
        
        # Test connection
        connection_test = await self.test_QDRANT_connection()
        
        report = {
            "timestamp": "2025-01-15T00:00:00Z",
            "sync_status": "completed",
            "validation": validation,
            "connection_test": connection_test,
            "configuration": {
                "pulumi_org": self.pulumi_org,
                "pulumi_stack": self.pulumi_stack,
                "github_org": self.github_org,
                "secret_mappings": self.secret_mappings,
                "default_values": self.default_values
            },
            "recommendations": []
        }
        
        # Add recommendations based on results
        if validation["secrets_missing"] > 0:
            report["recommendations"].append(
                "Add missing secrets to GitHub Organization Secrets"
            )
            
        if connection_test["status"] != "success":
            report["recommendations"].append(
                "Verify Qdrant cluster is accessible and API key is valid"
            )
            
        if not validation["errors"] and connection_test["connection_successful"]:
            report["recommendations"].append(
                "Configuration is complete - ready for production use"
            )
            
        # Save report
        report_file = "QDRANT_SECRETS_SYNC_REPORT.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
            
        logger.info(f"📄 Report saved: {report_file}")
        
        # Print summary
        logger.info("=" * 50)
        logger.info("🔐 QDRANT SECRETS SYNC SUMMARY")
        logger.info("=" * 50)
        logger.info(f"✅ Secrets Found: {validation['secrets_found']}")
        logger.info(f"❌ Secrets Missing: {validation['secrets_missing']}")
        logger.info(f"🔗 Connection: {connection_test['status']}")
        logger.info(f"📊 Status: {validation['status']}")
        
        if validation["errors"]:
            logger.info("⚠️ Errors:")
            for error in validation["errors"]:
                logger.info(f"  - {error}")
                
        logger.info("=" * 50)
        
        return report

async def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Sync Qdrant secrets")
    parser.add_argument("--validate-only", action="store_true",
                       help="Only validate existing configuration")
    parser.add_argument("--test-connection", action="store_true",
                       help="Test connection to Qdrant")
    parser.add_argument("--generate-report", action="store_true",
                       help="Generate comprehensive report")
    
    args = parser.parse_args()
    
    sync_service = QdrantSecretsSync()
    
    try:
        if args.validate_only:
            validation = await sync_service.validate_secrets()
            if validation["status"] != "success":
                sys.exit(1)
        elif args.test_connection:
            test_result = await sync_service.test_QDRANT_connection()
            if test_result["status"] != "success":
                sys.exit(1)
        elif args.generate_report:
            await sync_service.generate_sync_report()
        else:
            # Full sync
            await sync_service.sync_all_secrets()
            await sync_service.generate_sync_report()
            
    except Exception as e:
        logger.error(f"❌ Operation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main()) 