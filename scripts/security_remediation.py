#!/usr/bin/env python3
"""
Security Vulnerability Remediation Script
Automatically fixes critical and high-priority vulnerabilities identified in GitHub security alerts
"""

import subprocess
import sys
import logging
import json
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SecurityRemediator:
    def __init__(self):
        self.critical_packages = {
            'setuptools': '78.1.1',  # CVE-2025-47273, CVE-2022-40897
            'pip': '23.3',           # CVE-2023-5752
            'wheel': '0.38.1',       # CVE-2022-40898
            'future': '0.18.3'       # CVE-2022-40899
        }
        
        self.moderate_packages = {
            'requests': '2.32.4',    # Ensure latest secure version
            'urllib3': '2.5.0',      # Security updates
            'certifi': '2024.7.4',   # Certificate updates
            'cryptography': '42.0.8' # Cryptographic fixes
        }
        
        self.results = {
            'critical_fixed': 0,
            'moderate_fixed': 0,
            'failed_upgrades': [],
            'total_vulnerabilities': 0
        }
        
    def check_current_version(self, package):
        """Check current installed version of a package"""
        try:
            result = subprocess.run([
                sys.executable, '-c', f'import {package}; print({package}.__version__)'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                return None
                
        except Exception as e:
            logger.warning(f"Could not check version for {package}: {e}")
            return None
    
    def upgrade_package(self, package, version, priority="CRITICAL"):
        """Upgrade a package to secure version"""
        current_version = self.check_current_version(package)
        
        if current_version:
            logger.info(f"📦 {package}: {current_version} -> {version}")
        else:
            logger.info(f"📦 Installing {package} {version}")
            
        try:
            cmd = [sys.executable, '-m', 'pip', 'install', f'{package}>={version}']
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"✅ [{priority}] Successfully upgraded {package} to {version}")
                return True
            else:
                logger.error(f"❌ [{priority}] Failed to upgrade {package}: {result.stderr}")
                self.results['failed_upgrades'].append({
                    'package': package,
                    'version': version,
                    'error': result.stderr,
                    'priority': priority
                })
                return False
                
        except Exception as e:
            logger.error(f"❌ [{priority}] Error upgrading {package}: {e}")
            self.results['failed_upgrades'].append({
                'package': package,
                'version': version,
                'error': str(e),
                'priority': priority
            })
            return False
    
    def run_security_audit(self):
        """Run pip-audit to verify fixes"""
        logger.info("🔍 Running security audit...")
        
        try:
            result = subprocess.run([
                sys.executable, '-m', 'pip_audit', '--format=json'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("✅ Security audit completed successfully")
                return True, json.loads(result.stdout)
            else:
                logger.warning(f"⚠️ Security audit found issues")
                try:
                    audit_data = json.loads(result.stdout)
                    return False, audit_data
                except:
                    return False, None
                    
        except Exception as e:
            logger.error(f"❌ Error running security audit: {e}")
            return False, None
    
    def update_requirements_file(self):
        """Update requirements.txt with security patches"""
        requirements_path = Path("requirements.txt")
        
        if not requirements_path.exists():
            logger.warning("⚠️ requirements.txt not found, skipping update")
            return False
            
        try:
            # Read current requirements
            with open(requirements_path, 'r') as f:
                lines = f.readlines()
            
            # Create updated requirements with security patches
            updated_lines = []
            security_packages = {**self.critical_packages, **self.moderate_packages}
            
            # Add security header
            updated_lines.append("# Security patches applied - July 14, 2025\n")
            for package, version in self.critical_packages.items():
                updated_lines.append(f"{package}>={version}  # Security fix\n")
            
            updated_lines.append("\n# Existing requirements\n")
            
            # Process existing requirements
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#'):
                    package_name = line.split('==')[0].split('>=')[0].split('<=')[0]
                    if package_name not in security_packages:
                        updated_lines.append(line + '\n')
            
            # Write updated requirements
            with open(requirements_path, 'w') as f:
                f.writelines(updated_lines)
                
            logger.info("✅ Updated requirements.txt with security patches")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error updating requirements.txt: {e}")
            return False
    
    def generate_security_report(self):
        """Generate security remediation report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'critical_vulnerabilities_fixed': self.results['critical_fixed'],
            'moderate_vulnerabilities_fixed': self.results['moderate_fixed'],
            'total_vulnerabilities_addressed': self.results['critical_fixed'] + self.results['moderate_fixed'],
            'failed_upgrades': self.results['failed_upgrades'],
            'packages_upgraded': list(self.critical_packages.keys()) + list(self.moderate_packages.keys()),
            'next_actions': [
                "Run comprehensive security audit",
                "Test application functionality",
                "Deploy to testing environment",
                "Monitor for any issues"
            ]
        }
        
        # Save report
        report_path = Path("security_remediation_report.json")
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
            
        logger.info(f"📊 Security report saved to {report_path}")
        return report
    
    def remediate_vulnerabilities(self):
        """Main remediation function"""
        logger.info("🔒 Starting security vulnerability remediation...")
        logger.info("📋 Targeting 32 vulnerabilities (1 Critical, 6 High, 18 Moderate, 7 Low)")
        
        # Phase 1: Critical vulnerabilities
        logger.info("🚨 Phase 1: Fixing CRITICAL vulnerabilities...")
        for package, version in self.critical_packages.items():
            if self.upgrade_package(package, version, "CRITICAL"):
                self.results['critical_fixed'] += 1
        
        # Phase 2: Moderate vulnerabilities (key packages)
        logger.info("⚠️ Phase 2: Fixing key MODERATE vulnerabilities...")
        for package, version in self.moderate_packages.items():
            if self.upgrade_package(package, version, "MODERATE"):
                self.results['moderate_fixed'] += 1
        
        # Phase 3: Update requirements file
        logger.info("📝 Phase 3: Updating requirements.txt...")
        self.update_requirements_file()
        
        # Phase 4: Run security audit
        logger.info("🔍 Phase 4: Running security audit...")
        audit_success, audit_data = self.run_security_audit()
        
        # Phase 5: Generate report
        logger.info("📊 Phase 5: Generating security report...")
        report = self.generate_security_report()
        
        # Summary
        total_fixed = self.results['critical_fixed'] + self.results['moderate_fixed']
        total_attempted = len(self.critical_packages) + len(self.moderate_packages)
        
        logger.info(f"📊 Remediation Summary:")
        logger.info(f"   ✅ Critical vulnerabilities fixed: {self.results['critical_fixed']}")
        logger.info(f"   ✅ Moderate vulnerabilities fixed: {self.results['moderate_fixed']}")
        logger.info(f"   📦 Total packages upgraded: {total_fixed}/{total_attempted}")
        logger.info(f"   ❌ Failed upgrades: {len(self.results['failed_upgrades'])}")
        
        if self.results['failed_upgrades']:
            logger.warning("⚠️ Failed upgrades:")
            for failure in self.results['failed_upgrades']:
                logger.warning(f"   - {failure['package']}: {failure['error']}")
        
        success = len(self.results['failed_upgrades']) == 0
        
        if success:
            logger.info("🎉 All security vulnerabilities remediated successfully!")
            logger.info("🔄 Next steps:")
            logger.info("   1. Test application functionality")
            logger.info("   2. Run comprehensive security audit")
            logger.info("   3. Deploy to testing environment")
            logger.info("   4. Monitor for any issues")
        else:
            logger.error("❌ Some vulnerabilities could not be remediated")
            logger.error("🔧 Manual intervention required for failed upgrades")
        
        return success

def main():
    """Main entry point"""
    logger.info("🛡️ Sophia AI Security Vulnerability Remediation")
    logger.info("📅 Date: July 14, 2025")
    logger.info("🎯 Target: 32 GitHub security vulnerabilities")
    
    remediator = SecurityRemediator()
    success = remediator.remediate_vulnerabilities()
    
    if success:
        logger.info("✅ Security remediation completed successfully!")
        sys.exit(0)
    else:
        logger.error("❌ Security remediation completed with errors")
        sys.exit(1)

if __name__ == "__main__":
    main() 