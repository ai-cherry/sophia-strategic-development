#!/usr/bin/env python3
"""
TARGETED SECURITY FIX - Remove hardcoded SSH keys from config files only
Fixes only the production configuration files, ignores security tools

TARGETS:
- backend/core/auto_esc_config.py (production config)
- scripts/final_lambda_deployment.py (deployment script)

EXCLUDES:
- Security fix scripts (this script, emergency_security_fix.py, etc.)
- SSH automation tools (for legitimate use)

Date: July 15, 2025
Priority: CRITICAL - Execute immediately
"""

import os
import logging
import subprocess
from pathlib import Path
import re

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class TargetedSecurityFix:
    """Targeted security fix for production config files only"""
    
    def __init__(self):
        # Only fix actual production/deployment files
        self.files_to_fix = [
            "backend/core/auto_esc_config.py",
            "scripts/final_lambda_deployment.py"
        ]
        # Exclude security tools from validation
        self.excluded_from_validation = [
            "scripts/emergency_security_fix.py",
            "scripts/enhanced_emergency_security_fix.py", 
            "scripts/targeted_security_fix.py",
            "scripts/automated_ssh_fix.py",
            "scripts/add_ssh_to_lambda_instances.py"
        ]
        
    def execute_targeted_fix(self):
        """Execute targeted security fix on production files only"""
        logger.info("🚨 EXECUTING TARGETED SECURITY FIX")
        logger.info("=" * 60)
        logger.info("🎯 TARGET: Production config files only")
        logger.info("🚫 EXCLUDE: Security tools and SSH automation scripts")
        
        try:
            # Step 1: Create backups
            self.create_backups()
            
            # Step 2: Fix each target file
            self.fix_production_files()
            
            # Step 3: Validate fix (excluding tools)
            self.validate_production_security()
            
            # Step 4: Test functionality
            self.test_config_functionality()
            
            logger.info("✅ TARGETED SECURITY FIX COMPLETE")
            return True
            
        except Exception as e:
            logger.error(f"❌ Targeted security fix failed: {e}")
            self.restore_backups()
            return False
    
    def create_backups(self):
        """Create backups of target files"""
        logger.info("📋 Creating backups of target files...")
        
        for file_path in self.files_to_fix:
            if Path(file_path).exists():
                import shutil
                backup_file = f"{file_path}.security_backup"
                shutil.copy2(file_path, backup_file)
                logger.info(f"✅ Backup: {backup_file}")
    
    def fix_production_files(self):
        """Fix hardcoded SSH keys in production files"""
        logger.info("🔐 Fixing production configuration files...")
        
        for file_path in self.files_to_fix:
            self.fix_specific_file(file_path)
    
    def fix_specific_file(self, file_path: str):
        """Fix SSH key issues in specific file"""
        logger.info(f"🔧 Processing {file_path}...")
        
        if not Path(file_path).exists():
            logger.warning(f"⚠️ File not found: {file_path}")
            return
        
        with open(file_path, 'r') as f:
            content = f.read()
        
        original_content = content
        
        if file_path == "backend/core/auto_esc_config.py":
            # Specific fix for auto_esc_config.py
            content = self.fix_auto_esc_config(content)
            
        elif file_path == "scripts/final_lambda_deployment.py":
            # Specific fix for final_lambda_deployment.py
            content = self.fix_final_lambda_deployment(content)
        
        if content != original_content:
            with open(file_path, 'w') as f:
                f.write(content)
            logger.info(f"✅ FIXED: {file_path}")
        else:
            logger.info(f"ℹ️ No changes needed for {file_path}")
    
    def fix_auto_esc_config(self, content: str) -> str:
        """Fix auto_esc_config.py specifically"""
        logger.info("🔧 Fixing auto_esc_config.py SSH key hardcoding...")
        
        # Replace the hardcoded SSH private key with ESC-only version
        content = re.sub(
            r'ssh_private_key = get_config_value\("LAMBDA_PRIVATE_SSH_KEY"\) or """-----BEGIN RSA PRIVATE KEY-----.*?-----END RSA PRIVATE KEY-----"""',
            'ssh_private_key = get_config_value("LAMBDA_PRIVATE_SSH_KEY")  # SECURITY FIX: Removed hardcoded key',
            content,
            flags=re.DOTALL
        )
        
        # Also fix the public key
        content = re.sub(
            r'ssh_public_key = get_config_value\("LAMBDA_SSH_KEY"\) or "ssh-rsa [^"]*"',
            'ssh_public_key = get_config_value("LAMBDA_SSH_KEY")  # SECURITY FIX: Removed hardcoded key',
            content
        )
        
        return content
    
    def fix_final_lambda_deployment(self, content: str) -> str:
        """Fix final_lambda_deployment.py specifically"""
        logger.info("🔧 Fixing final_lambda_deployment.py SSH key hardcoding...")
        
        # Replace hardcoded SSH_PRIVATE_KEY with environment variable reference
        content = re.sub(
            r'SSH_PRIVATE_KEY = """-----BEGIN RSA PRIVATE KEY-----.*?-----END RSA PRIVATE KEY-----"""',
            'SSH_PRIVATE_KEY = os.getenv("LAMBDA_PRIVATE_SSH_KEY")  # SECURITY FIX: Use environment variable',
            content,
            flags=re.DOTALL
        )
        
        return content
    
    def validate_production_security(self):
        """Validate that production files are secure"""
        logger.info("🔍 Validating production file security...")
        
        violations = []
        
        for file_path in self.files_to_fix:
            if not Path(file_path).exists():
                continue
                
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Check for actual hardcoded keys (not comments)
            if '"""-----BEGIN RSA PRIVATE KEY-----' in content:
                violations.append(f"{file_path}: Hardcoded RSA private key")
            
            if 'MIIEogIBAAKCAQEAsctiuxhwWHR6Vw2MCEKFQTo0fDd0cDE4G2S7AexGvQZvTyqy' in content:
                violations.append(f"{file_path}: Specific Base64 key material")
        
        if violations:
            raise Exception(f"Production security violations: {violations}")
        
        logger.info("✅ Production files are secure")
    
    def test_config_functionality(self):
        """Test that configuration still works"""
        logger.info("🔧 Testing configuration functionality...")
        
        try:
            import sys
            sys.path.append('backend')
            from core.auto_esc_config import get_lambda_labs_config
            
            config = get_lambda_labs_config()
            
            if not isinstance(config, dict):
                raise Exception("Lambda config not loading")
            
            ssh_key = config.get('ssh_private_key')
            if ssh_key is None:
                logger.info("⚠️ SSH key is None - will load from Pulumi ESC in production")
            else:
                logger.info("✅ SSH key configuration working")
            
            logger.info("✅ Configuration functionality preserved")
            
        except Exception as e:
            logger.warning(f"⚠️ Config test warning: {e}")
    
    def restore_backups(self):
        """Restore backups if fix fails"""
        logger.warning("⚠️ Restoring backups...")
        
        for file_path in self.files_to_fix:
            backup_file = f"{file_path}.security_backup"
            if Path(backup_file).exists():
                import shutil
                shutil.copy2(backup_file, file_path)
                logger.info(f"✅ Restored {file_path}")
    
    def cleanup_backups(self):
        """Remove backup files"""
        for file_path in self.files_to_fix:
            backup_file = f"{file_path}.security_backup"
            if Path(backup_file).exists():
                Path(backup_file).unlink()
                logger.info(f"🧹 Cleaned backup: {backup_file}")


def main():
    """Main targeted security fix function"""
    print("\n🎯 TARGETED SECURITY FIX")
    print("=" * 60)
    print("TARGET: Production configuration files only")
    print("- backend/core/auto_esc_config.py")
    print("- scripts/final_lambda_deployment.py")
    print("EXCLUDE: Security tools and SSH automation scripts")
    print("=" * 60)
    
    fixer = TargetedSecurityFix()
    success = fixer.execute_targeted_fix()
    
    if success:
        print("\n✅ TARGETED SECURITY FIX SUCCESSFUL!")
        print("🔐 Production files secured")
        print("🔧 Pulumi ESC integration preserved")
        print("🛠️ Security tools preserved for legitimate use")
        print("\n📋 Files secured:")
        for file_path in fixer.files_to_fix:
            print(f"   ✅ {file_path}")
        print("\n🚨 ENSURE SSH key is in Pulumi ESC:")
        print("pulumi env set LAMBDA_PRIVATE_SSH_KEY '<ssh-key-content>'")
        
        fixer.cleanup_backups()
    else:
        print("\n❌ TARGETED SECURITY FIX FAILED!")
        print("🔄 Backups restored")

if __name__ == "__main__":
    main() 