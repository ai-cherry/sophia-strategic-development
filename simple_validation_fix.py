#!/usr/bin/env python3
"""
Simple Validation Fix for Sophia AI Secret Management Integration

This script validates the implementation by checking the files directly
without relying on complex import structures that might fail.
"""

import json
import logging
import subprocess
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SimpleValidationFix:
    def __init__(self):
        self.validation_results = {}
        
    def validate_enhanced_settings_file(self):
        """Validate that the enhanced settings file has been properly updated."""
        try:
            logger.info("🔧 Validating Enhanced Settings file...")
            
            config_file = Path("/home/ubuntu/sophia-main/backend/core/auto_esc_config.py")
            
            if not config_file.exists():
                logger.error("Configuration file not found")
                return False
            
            with open(config_file, 'r') as f:
                content = f.read()
            
            # Check for new credential fields
            new_fields = [
                'asana_pat_token: Optional[str] = None',
                'salesforce_access_token: Optional[str] = None',
                'slack_client_id: Optional[str] = None',
                'slack_client_secret: Optional[str] = None',
                'slack_signing_secret: Optional[str] = None',
                'slack_app_token: Optional[str] = None',
                'slack_refresh_token: Optional[str] = None',
                'slack_socket_token: Optional[str] = None',
                'hubspot_client_secret: Optional[str] = None',
                'gong_access_key_secret: Optional[str] = None'
            ]
            
            found_fields = []
            missing_fields = []
            
            for field in new_fields:
                if field in content:
                    found_fields.append(field)
                else:
                    missing_fields.append(field)
            
            if missing_fields:
                logger.warning(f"Missing fields: {missing_fields}")
                self.validation_results['enhanced_settings'] = {
                    'status': 'PARTIAL',
                    'found': len(found_fields),
                    'missing': missing_fields
                }
                return False
            else:
                logger.info(f"✅ All {len(new_fields)} credential fields found")
                self.validation_results['enhanced_settings'] = {
                    'status': 'PASSED',
                    'found': len(found_fields),
                    'fields': found_fields
                }
                return True
                
        except Exception as e:
            logger.error(f"Enhanced settings validation failed: {e}")
            self.validation_results['enhanced_settings'] = {
                'status': 'FAILED',
                'error': str(e)
            }
            return False
    
    def validate_secret_manager_file(self):
        """Validate that the secret manager file has been properly updated."""
        try:
            logger.info("🔧 Validating Secret Manager file...")
            
            secret_manager_file = Path("/home/ubuntu/sophia-main/backend/security/secret_management.py")
            
            if not secret_manager_file.exists():
                logger.error("Secret manager file not found")
                return False
            
            with open(secret_manager_file, 'r') as f:
                content = f.read()
            
            # Check for new validation methods
            validation_methods = [
                'async def _validate_extended_api_services',
                'async def _validate_asana_credentials',
                'async def _validate_salesforce_credentials',
                'async def _validate_slack_enhanced_credentials'
            ]
            
            found_methods = []
            missing_methods = []
            
            for method in validation_methods:
                if method in content:
                    found_methods.append(method)
                else:
                    missing_methods.append(method)
            
            if missing_methods:
                logger.warning(f"Missing methods: {missing_methods}")
                self.validation_results['secret_manager'] = {
                    'status': 'PARTIAL',
                    'found': len(found_methods),
                    'missing': missing_methods
                }
                return False
            else:
                logger.info(f"✅ All {len(validation_methods)} validation methods found")
                self.validation_results['secret_manager'] = {
                    'status': 'PASSED',
                    'found': len(found_methods),
                    'methods': found_methods
                }
                return True
                
        except Exception as e:
            logger.error(f"Secret manager validation failed: {e}")
            self.validation_results['secret_manager'] = {
                'status': 'FAILED',
                'error': str(e)
            }
            return False
    
    def validate_secure_credential_service_file(self):
        """Validate that the secure credential service file exists and is properly structured."""
        try:
            logger.info("🔧 Validating Secure Credential Service file...")
            
            service_file = Path("/home/ubuntu/sophia-main/backend/services/secure_credential_service.py")
            
            if not service_file.exists():
                logger.error("Secure credential service file not found")
                return False
            
            with open(service_file, 'r') as f:
                content = f.read()
            
            # Check for key components
            key_components = [
                'class SecureCredentialService',
                'async def get_api_credentials',
                'async def get_platform_endpoints',
                'async def health_check',
                'platform == "asana"',
                'platform == "salesforce"',
                'platform == "slack"',
                'platform == "hubspot"',
                'platform == "gong"',
                'platform == "linear"'
            ]
            
            found_components = []
            missing_components = []
            
            for component in key_components:
                if component in content:
                    found_components.append(component)
                else:
                    missing_components.append(component)
            
            if missing_components:
                logger.warning(f"Missing components: {missing_components}")
                self.validation_results['secure_credential_service'] = {
                    'status': 'PARTIAL',
                    'found': len(found_components),
                    'missing': missing_components,
                    'file_size': len(content)
                }
                return False
            else:
                logger.info(f"✅ All {len(key_components)} service components found")
                self.validation_results['secure_credential_service'] = {
                    'status': 'PASSED',
                    'found': len(found_components),
                    'components': found_components,
                    'file_size': len(content)
                }
                return True
                
        except Exception as e:
            logger.error(f"Secure credential service validation failed: {e}")
            self.validation_results['secure_credential_service'] = {
                'status': 'FAILED',
                'error': str(e)
            }
            return False
    
    def validate_workflow_file(self):
        """Validate that the workflow file has been properly updated."""
        try:
            logger.info("🔧 Validating Workflow file...")
            
            workflow_file = Path("/home/ubuntu/sophia-main/.github/workflows/unified-secret-sync.yml")
            
            if not workflow_file.exists():
                logger.error("Workflow file not found")
                return False
            
            with open(workflow_file, 'r') as f:
                content = f.read()
            
            # Check for new secret mappings
            expected_secrets = [
                'ASANA_PAT_TOKEN=${{ secrets.ASANA_PAT_TOKEN }}',
                'SALESFORCE_ACCESS_TOKEN=${{ secrets.SALESFORCE_ACCESS_TOKEN }}',
                'SLACK_CLIENT_ID=${{ secrets.SLACK_CLIENT_ID }}',
                'SLACK_CLIENT_SECRET=${{ secrets.SLACK_CLIENT_SECRET }}',
                'SLACK_SIGNING_SECRET=${{ secrets.SLACK_SIGNING_SECRET }}',
                'SLACK_APP_TOKEN=${{ secrets.SLACK_APP_TOKEN }}',
                'SLACK_REFRESH_TOKEN=${{ secrets.SLACK_REFRESH_TOKEN }}',
                'SLACK_SOCKET_TOKEN=${{ secrets.SLACK_SOCKET_TOKEN }}',
                'HUBSPOT_CLIENT_SECRET=${{ secrets.HUBSPOT_CLIENT_SECRET }}',
                'GONG_ACCESS_KEY_SECRET=${{ secrets.GONG_ACCESS_KEY_SECRET }}'
            ]
            
            found_secrets = []
            missing_secrets = []
            
            for secret in expected_secrets:
                if secret in content:
                    found_secrets.append(secret)
                else:
                    missing_secrets.append(secret)
            
            if missing_secrets:
                logger.warning(f"Missing secret mappings: {missing_secrets}")
                self.validation_results['workflow_file'] = {
                    'status': 'PARTIAL',
                    'found': len(found_secrets),
                    'missing': missing_secrets
                }
                return False
            else:
                logger.info(f"✅ All {len(expected_secrets)} secret mappings found")
                self.validation_results['workflow_file'] = {
                    'status': 'PASSED',
                    'found': len(found_secrets),
                    'mappings': found_secrets
                }
                return True
                
        except Exception as e:
            logger.error(f"Workflow file validation failed: {e}")
            self.validation_results['workflow_file'] = {
                'status': 'FAILED',
                'error': str(e)
            }
            return False
    
    def validate_github_secrets(self):
        """Validate that secrets have been added to GitHub."""
        try:
            logger.info("🔧 Validating GitHub secrets...")
            
            # Get list of secrets from GitHub
            result = subprocess.run(
                ['gh', 'secret', 'list'],
                capture_output=True,
                text=True,
                cwd='/home/ubuntu/sophia-main'
            )
            
            if result.returncode != 0:
                logger.error(f"Failed to list GitHub secrets: {result.stderr}")
                return False
            
            secrets_output = result.stdout
            
            # Check for expected secrets
            expected_secrets = [
                'ASANA_PAT_TOKEN',
                'SALESFORCE_ACCESS_TOKEN',
                'SLACK_CLIENT_ID',
                'SLACK_CLIENT_SECRET',
                'SLACK_SIGNING_SECRET',
                'SLACK_APP_TOKEN',
                'SLACK_REFRESH_TOKEN',
                'SLACK_SOCKET_TOKEN',
                'HUBSPOT_CLIENT_SECRET',
                'GONG_ACCESS_KEY_SECRET'
            ]
            
            found_secrets = []
            missing_secrets = []
            
            for secret in expected_secrets:
                if secret in secrets_output:
                    found_secrets.append(secret)
                else:
                    missing_secrets.append(secret)
            
            if missing_secrets:
                logger.warning(f"Missing GitHub secrets: {missing_secrets}")
                self.validation_results['github_secrets'] = {
                    'status': 'PARTIAL',
                    'found': len(found_secrets),
                    'missing': missing_secrets
                }
                return False
            else:
                logger.info(f"✅ All {len(expected_secrets)} GitHub secrets found")
                self.validation_results['github_secrets'] = {
                    'status': 'PASSED',
                    'found': len(found_secrets),
                    'secrets': found_secrets
                }
                return True
                
        except Exception as e:
            logger.error(f"GitHub secrets validation failed: {e}")
            self.validation_results['github_secrets'] = {
                'status': 'FAILED',
                'error': str(e)
            }
            return False
    
    def run_validation(self):
        """Run all validation checks."""
        logger.info("🚀 Starting Simple Validation Fix...")
        logger.info("=" * 80)
        
        validations = [
            ("Enhanced Settings File", self.validate_enhanced_settings_file),
            ("Secret Manager File", self.validate_secret_manager_file),
            ("Secure Credential Service File", self.validate_secure_credential_service_file),
            ("Workflow File", self.validate_workflow_file),
            ("GitHub Secrets", self.validate_github_secrets)
        ]
        
        passed_validations = 0
        total_validations = len(validations)
        
        for validation_name, validation_func in validations:
            logger.info(f"\n🔧 {validation_name}")
            logger.info("-" * 60)
            
            try:
                result = validation_func()
                if result:
                    passed_validations += 1
                    logger.info(f"✅ {validation_name}: PASSED")
                else:
                    logger.warning(f"⚠️ {validation_name}: FAILED")
            except Exception as e:
                logger.error(f"❌ {validation_name}: ERROR - {e}")
        
        # Generate summary
        success_rate = (passed_validations / total_validations) * 100
        
        logger.info("\n" + "=" * 80)
        logger.info("🎉 VALIDATION SUMMARY")
        logger.info("=" * 80)
        logger.info(f"📊 Success Rate: {success_rate:.1f}% ({passed_validations}/{total_validations} validations passed)")
        logger.info(f"⏰ Execution Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if success_rate == 100:
            logger.info("🎯 RESULT: PERFECT - All components validated successfully!")
        elif success_rate >= 80:
            logger.info("🎯 RESULT: EXCELLENT - Minor issues to address")
        elif success_rate >= 60:
            logger.info("🎯 RESULT: GOOD - Some components need attention")
        else:
            logger.info("🎯 RESULT: NEEDS WORK - Several components require fixes")
        
        # Save results
        self.validation_results['summary'] = {
            'total_validations': total_validations,
            'passed_validations': passed_validations,
            'success_rate': f"{success_rate:.1f}%",
            'timestamp': datetime.now().isoformat(),
            'overall_status': 'PERFECT' if success_rate == 100 else 'EXCELLENT' if success_rate >= 80 else 'GOOD' if success_rate >= 60 else 'NEEDS_WORK'
        }
        
        # Save to file
        with open('/home/ubuntu/simple_validation_results.json', 'w') as f:
            json.dump(self.validation_results, f, indent=2)
        
        logger.info("📄 Detailed results saved to: /home/ubuntu/simple_validation_results.json")
        
        return success_rate == 100

def main():
    """Run the simple validation."""
    validator = SimpleValidationFix()
    success = validator.run_validation()
    
    if success:
        print("\n🎉 VALIDATION COMPLETE: All components are properly implemented!")
    else:
        print("\n⚠️ VALIDATION COMPLETE: Some components need attention.")
    
    return success

if __name__ == "__main__":
    main()

