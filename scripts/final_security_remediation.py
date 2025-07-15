#!/usr/bin/env python3
"""
Final Security Remediation Script
Addresses the remaining 4 vulnerabilities found by pip-audit
"""

import subprocess
import sys
import json
import os
from datetime import datetime

def run_command(cmd, capture_output=True):
    """Run a command and return the result"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=capture_output, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def upgrade_vulnerable_packages():
    """Upgrade the vulnerable packages identified by pip-audit"""
    print("🔧 Upgrading Vulnerable Packages...")
    
    # Vulnerable packages and their fixes
    vulnerable_packages = [
        ("requests", "2.32.4"),  # CVE-2024-47081
        ("urllib3", "2.5.0"),    # CVE-2025-50182, CVE-2025-50181
        ("torch", "latest")      # CVE-2025-3730 (no fix version specified)
    ]
    
    upgraded = []
    failed = []
    
    for package, version in vulnerable_packages:
        print(f"📦 Upgrading {package} to {version}...")
        
        if version == "latest":
            cmd = f"python3 -m pip install --upgrade {package}"
        else:
            cmd = f"python3 -m pip install --upgrade {package}>={version}"
        
        success, stdout, stderr = run_command(cmd)
        
        if success:
            print(f"✅ {package}: Successfully upgraded")
            upgraded.append(package)
        else:
            print(f"❌ {package}: Failed to upgrade - {stderr}")
            failed.append((package, stderr))
    
    return upgraded, failed

def verify_fixes():
    """Verify that the security fixes were successful"""
    print("🔍 Verifying Security Fixes...")
    
    success, stdout, stderr = run_command("python3 -m pip_audit --format=json")
    
    if success:
        try:
            audit_data = json.loads(stdout)
            dependencies = audit_data.get("dependencies", [])
            
            # Count vulnerabilities
            total_vulns = 0
            for dep in dependencies:
                total_vulns += len(dep.get("vulns", []))
            
            if total_vulns == 0:
                print("✅ All vulnerabilities fixed!")
                return True
            else:
                print(f"⚠️  {total_vulns} vulnerabilities remain")
                
                # Show remaining vulnerabilities
                for dep in dependencies:
                    vulns = dep.get("vulns", [])
                    if vulns:
                        print(f"  📦 {dep['name']} {dep['version']}:")
                        for vuln in vulns:
                            print(f"    - {vuln['id']}: {vuln['description'][:100]}...")
                
                return False
        except json.JSONDecodeError:
            print("❌ Failed to parse pip-audit output")
            return False
    else:
        print(f"❌ pip-audit failed: {stderr}")
        return False

def create_security_summary():
    """Create a comprehensive security summary"""
    print("\n" + "="*70)
    print("🔒 FINAL SECURITY REMEDIATION SUMMARY")
    print("="*70)
    
    # Get current package versions
    success, stdout, stderr = run_command("python3 -m pip list --format=json")
    
    if success:
        try:
            packages = json.loads(stdout)
            security_packages = ["requests", "urllib3", "torch", "setuptools", "pip", "wheel"]
            
            print("📦 Security-Critical Package Versions:")
            for pkg in packages:
                if pkg["name"].lower() in security_packages:
                    print(f"  ✅ {pkg['name']}: {pkg['version']}")
        except json.JSONDecodeError:
            print("❌ Failed to get package list")
    
    # Run final audit
    print("\n🔍 Final Security Audit:")
    success, stdout, stderr = run_command("python3 -m pip_audit")
    
    if success:
        if "No known vulnerabilities found" in stdout:
            print("✅ No vulnerabilities found - System is secure!")
            return True
        else:
            print("⚠️  Some vulnerabilities remain:")
            print(stdout)
            return False
    else:
        print(f"❌ Final audit failed: {stderr}")
        return False

def main():
    """Main remediation function"""
    print("🚀 Starting Final Security Remediation...")
    print("Target: Fix remaining 4 vulnerabilities in 3 packages")
    print("="*70)
    
    # Upgrade vulnerable packages
    upgraded, failed = upgrade_vulnerable_packages()
    
    print(f"\n📊 Upgrade Results:")
    print(f"✅ Successfully upgraded: {len(upgraded)} packages")
    print(f"❌ Failed to upgrade: {len(failed)} packages")
    
    if upgraded:
        print("✅ Upgraded packages:", ", ".join(upgraded))
    
    if failed:
        print("❌ Failed packages:")
        for package, error in failed:
            print(f"  - {package}: {error[:100]}...")
    
    # Verify fixes
    print("\n" + "="*70)
    verification_success = verify_fixes()
    
    # Create summary
    final_success = create_security_summary()
    
    # Generate report
    report = {
        "timestamp": datetime.now().isoformat(),
        "upgraded_packages": upgraded,
        "failed_packages": [pkg for pkg, _ in failed],
        "verification_success": verification_success,
        "final_success": final_success
    }
    
    report_file = f"final_security_remediation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📋 Detailed report saved to: {report_file}")
    
    if final_success:
        print("\n🎉 FINAL SECURITY REMEDIATION COMPLETE - SYSTEM FULLY SECURE!")
        return True
    else:
        print("\n⚠️  SECURITY IMPROVEMENTS MADE - SOME ISSUES MAY REMAIN")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 