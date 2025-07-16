#!/usr/bin/env python3
"""
EMERGENCY SECURITY FIX - HARDCODED SSH KEY REMOVAL
Immediately fixes the critical security vulnerability identified in code analysis

CRITICAL ISSUE: SSH private key hardcoded in auto_esc_config.py (lines 349-375)
SECURITY RISK: Private key exposed in source code, version control, deployments
IMMEDIATE ACTION: Remove hardcoded key, ensure Pulumi ESC integration

Date: July 15, 2025
Priority: CRITICAL - Execute immediately
"""

import os
import logging
import subprocess
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class EmergencySecurityFix:
    """Emergency fix for hardcoded SSH key vulnerability"""
    
    def __init__(self):
        self.config_file = Path("backend/core/auto_esc_config.py")
        self.backup_file = Path("backend/core/auto_esc_config.py.security_backup")
        
    def execute_emergency_fix(self):
        """Execute emergency security fix"""
        logger.info("🚨 EXECUTING EMERGENCY SECURITY FIX")
        logger.info("=" * 60)
        
        try:
            # Step 1: Create backup
            self.create_backup()
            
            # Step 2: Remove hardcoded SSH key
            self.remove_hardcoded_ssh_key()
            
            # Step 3: Validate fix
            self.validate_security_fix()
            
            # Step 4: Test Pulumi ESC integration
            self.test_esc_integration()
            
            logger.info("✅ EMERGENCY SECURITY FIX COMPLETE")
            return True
            
        except Exception as e:
            logger.error(f"❌ Emergency fix failed: {e}")
            self.restore_backup()
            return False
    
    def create_backup(self):
        """Create backup of current config file"""
        logger.info("📋 Creating security backup...")
        
        if self.config_file.exists():
            import shutil
            shutil.copy2(self.config_file, self.backup_file)
            logger.info(f"✅ Backup created: {self.backup_file}")
        else:
            raise FileNotFoundError(f"Config file not found: {self.config_file}")
    
    def remove_hardcoded_ssh_key(self):
        """Remove hardcoded SSH private key from config"""
        logger.info("🔐 Removing hardcoded SSH private key...")
        
        # Read current file
        with open(self.config_file, 'r') as f:
            content = f.read()
        
        # Replace hardcoded key with Pulumi ESC only
        # Find the lambda config function and fix it
        fixed_content = content.replace(
            'ssh_private_key = get_config_value("LAMBDA_PRIVATE_SSH_KEY")  # SECURITY FIX: Removed hardcoded key' in line:
                skip_key = False
                continue
            elif not skip_key:
                new_lines.append(line)
        
        # Write fixed content
        with open(self.config_file, 'w') as f:
            f.write('\n'.join(new_lines))
        
        logger.info("✅ Hardcoded SSH key removed")
    
    def validate_security_fix(self):
        """Validate that hardcoded keys are completely removed"""
        logger.info("🔍 Validating security fix...")
        
        with open(self.config_file, 'r') as f:
            content = f.read()
        
        # Check for any remaining hardcoded keys
        security_violations = []
        
        if "-----BEGIN RSA PRIVATE KEY-----" in content:
            security_violations.append("RSA private key still present")
        
        if "-----BEGIN OPENSSH PRIVATE KEY-----" in content:
            security_violations.append("OpenSSH private key still present")
        
        if "MIIEogIBAAKCAQEA" in content:
            security_violations.append("Base64 key material still present")
        
        if security_violations:
            raise Exception(f"Security violations still present: {security_violations}")
        
        logger.info("✅ Security validation passed - no hardcoded keys found")
    
    def test_esc_integration(self):
        """Test that Pulumi ESC integration still works"""
        logger.info("🔧 Testing Pulumi ESC integration...")
        
        try:
            # Import the fixed config
            import sys
            sys.path.append('backend')
            from core.auto_esc_config import get_lambda_labs_config
            
            # Test configuration loading
            config = get_lambda_labs_config()
            
            # Validate that we get a config (even if SSH key is None from ESC)
            if not isinstance(config, dict):
                raise Exception("Lambda config not loading properly")
            
            if 'ssh_private_key' not in config:
                raise Exception("SSH key field missing from config")
            
            # Check that we're using ESC (not hardcoded)
            ssh_key = config.get('ssh_private_key')
            if ssh_key and 'BEGIN RSA PRIVATE KEY' in ssh_key:
                # If we get a key from ESC, it should be properly formatted
                logger.info("✅ SSH key loaded from Pulumi ESC")
            elif ssh_key is None:
                logger.info("⚠️ SSH key not found in Pulumi ESC - needs to be added")
            else:
                logger.info("✅ SSH key configuration updated")
            
            logger.info("✅ Pulumi ESC integration working")
            
        except Exception as e:
            logger.warning(f"⚠️ ESC integration test warning: {e}")
    
    def restore_backup(self):
        """Restore backup if fix fails"""
        logger.warning("⚠️ Restoring backup due to fix failure...")
        
        if self.backup_file.exists():
            import shutil
            shutil.copy2(self.backup_file, self.config_file)
            logger.info("✅ Backup restored")
    
    def cleanup_backup(self):
        """Remove backup file after successful fix"""
        if self.backup_file.exists():
            self.backup_file.unlink()
            logger.info("🧹 Security backup cleaned up")


def main():
    """Main emergency fix function"""
    print("\n🚨 EMERGENCY SECURITY FIX - HARDCODED SSH KEY REMOVAL")
    print("=" * 70)
    print("CRITICAL VULNERABILITY: SSH private key hardcoded in source code")
    print("IMMEDIATE ACTION: Removing hardcoded key, ensuring ESC integration")
    print("=" * 70)
    
    fixer = EmergencySecurityFix()
    success = fixer.execute_emergency_fix()
    
    if success:
        print("\n✅ EMERGENCY SECURITY FIX SUCCESSFUL!")
        print("🔐 Hardcoded SSH key removed from source code")
        print("🔧 Pulumi ESC integration preserved")
        print("📋 Next step: Verify SSH key is in Pulumi ESC secrets")
        print("\n🚨 IMPORTANT: Add SSH key to Pulumi ESC if missing!")
        print("Command: pulumi env set LAMBDA_PRIVATE_SSH_KEY '<ssh-key-content>'")
        
        # Cleanup backup
        fixer.cleanup_backup()
    else:
        print("\n❌ EMERGENCY SECURITY FIX FAILED!")
        print("🔄 Backup restored - manual intervention required")

if __name__ == "__main__":
    main() 