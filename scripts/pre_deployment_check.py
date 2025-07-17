#!/usr/bin/env python3
"""
🔍 SOPHIA AI PRE-DEPLOYMENT CHECKER
==================================
Verify all prerequisites before deployment
"""

import subprocess
import os
import sys
from pathlib import Path

def check_ssh_key():
    """Check SSH key for Lambda Labs"""
    key_path = Path.home() / ".ssh" / "lambda_labs_key"
    if key_path.exists():
        print("✅ SSH key found")
        return True
    else:
        print("❌ SSH key not found at ~/.ssh/lambda_labs_key")
        return False

def check_docker_login():
    """Check Docker Hub login"""
    try:
        result = subprocess.run(["docker", "info"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Docker is running")
            return True
        else:
            print("❌ Docker is not running")
            return False
    except FileNotFoundError:
        print("❌ Docker not installed")
        return False

def check_server_connectivity():
    """Check connectivity to Lambda Labs servers"""
    servers = [
        ("AI Core", "192.222.58.232"),
        ("Business", "104.171.202.117"),
        ("Data", "104.171.202.134"),
        ("Production", "104.171.202.103")
    ]
    
    all_connected = True
    for name, ip in servers:
        try:
            result = subprocess.run(
                ["ping", "-c", "1", "-W", "5000", ip],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print(f"✅ {name} server ({ip}) reachable")
            else:
                print(f"❌ {name} server ({ip}) unreachable")
                all_connected = False
        except Exception as e:
            print(f"❌ Error checking {name}: {e}")
            all_connected = False
    
    return all_connected

def main():
    """Main pre-deployment check"""
    print("🔍 PRE-DEPLOYMENT CHECKS")
    print("=" * 40)
    
    checks = [
        ("SSH Key", check_ssh_key),
        ("Docker", check_docker_login),
        ("Server Connectivity", check_server_connectivity)
    ]
    
    all_passed = True
    for name, check_func in checks:
        print(f"\n📋 Checking {name}...")
        if not check_func():
            all_passed = False
    
    print("\n" + "=" * 40)
    if all_passed:
        print("✅ ALL CHECKS PASSED - READY FOR DEPLOYMENT!")
        return True
    else:
        print("❌ SOME CHECKS FAILED - FIX ISSUES BEFORE DEPLOYMENT")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 