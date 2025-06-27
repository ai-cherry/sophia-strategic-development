#!/usr/bin/env python3
"""Sophia AI Environment Health Check"""

import os
import subprocess
import json
from datetime import datetime

def check_environment_variables():
    """Check if environment variables are set correctly."""
    env_vars = {
        "ENVIRONMENT": "prod",
        "PULUMI_ORG": "scoobyjava-org"
    }
    
    issues = []
    for var, expected in env_vars.items():
        actual = os.getenv(var)
        if actual != expected:
            issues.append(f"{var}: expected {expected}, got {actual}")
    
    return len(issues) == 0, issues

def check_pulumi_auth():
    """Check Pulumi authentication."""
    try:
        result = subprocess.run(["pulumi", "whoami"], capture_output=True, text=True, timeout=10)
        return result.returncode == 0, result.stderr if result.returncode != 0 else None
    except Exception as e:
        return False, str(e)

def check_stack_access():
    """Check access to production stack."""
    try:
        result = subprocess.run([
            "pulumi", "env", "open", "scoobyjava-org/default/sophia-ai-production", "--format", "json"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            config = json.loads(result.stdout)
            return True, f"Loaded {len(config)} secrets"
        else:
            return False, result.stderr
    except Exception as e:
        return False, str(e)

def main():
    print("🏥 Sophia AI Environment Health Check")
    print("=" * 40)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()
    
    overall_health = True
    
    # Check 1: Environment Variables
    env_ok, env_issues = check_environment_variables()
    print(f"Environment Variables: {✅ if env_ok else ❌}")
    if not env_ok:
        overall_health = False
        for issue in env_issues:
            print(f"  - {issue}")
    print()
    
    # Check 2: Pulumi Authentication
    auth_ok, auth_error = check_pulumi_auth()
    print(f"Pulumi Authentication: {✅ if auth_ok else ❌}")
    if not auth_ok:
        overall_health = False
        print(f"  - {auth_error}")
    print()
    
    # Check 3: Stack Access
    stack_ok, stack_info = check_stack_access()
    print(f"Stack Access: {✅ if stack_ok else ❌}")
    if stack_ok:
        print(f"  - {stack_info}")
    else:
        overall_health = False
        print(f"  - {stack_info}")
    print()
    
    # Overall Status
    print(f"Overall Health: {✅ HEALTHY if overall_health else ❌ ISSUES DETECTED}")
    
    if not overall_health:
        print()
        print("🔧 To fix issues:")
        print("1. Run: export ENVIRONMENT=prod")
        print("2. Run: export PULUMI_ORG=scoobyjava-org")
        print("3. Run: export PULUMI_ACCESS_TOKEN=your_token")
        print("4. Re-run this check")
    
    return 0 if overall_health else 1

if __name__ == "__main__":
    exit(main())
