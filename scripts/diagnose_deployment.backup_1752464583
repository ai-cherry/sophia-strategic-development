#!/usr/bin/env python3
"""
Comprehensive deployment diagnostic script for Sophia AI
Checks all prerequisites and provides solutions
"""

import os
import sys
import subprocess
from pathlib import Path
import json

# Add parent directory to path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from backend.integrations.lambda_labs_client import get_lambda_labs_client
from backend.core.auto_esc_config import get_config_value

# Colors
RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
NC = '\033[0m'

def print_header(text):
    print(f"\n{BLUE}{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}{NC}\n")

def print_status(status, message):
    if status:
        print(f"{GREEN}✅ {message}{NC}")
    else:
        print(f"{RED}❌ {message}{NC}")

def print_warning(message):
    print(f"{YELLOW}⚠️  {message}{NC}")

def check_prerequisites():
    """Check all deployment prerequisites"""
    issues = []
    
    print_header("SOPHIA AI DEPLOYMENT DIAGNOSTICS")
    
    # 1. Check Lambda Labs API
    print("1. Checking Lambda Labs API access...")
    try:
        client = get_lambda_labs_client()
        instances = client.list_instances()
        print_status(True, f"Lambda Labs API working - found {len(instances)} instances")
        
        # Show instances
        print("\n   Available instances:")
        for inst in instances:
            print(f"   - {inst.name}: {inst.ip} ({inst.instance_type.value})")
    except Exception as e:
        print_status(False, f"Lambda Labs API failed: {e}")
        issues.append("Lambda Labs API access")
    
    # 2. Check SSH key
    print("\n2. Checking SSH key configuration...")
    ssh_key_path = Path.home() / ".ssh" / "sophia2025.pem"
    
    if ssh_key_path.exists():
        print_status(True, f"SSH key exists at {ssh_key_path}")
        
        # Check permissions
        mode = ssh_key_path.stat().st_mode & 0o777
        if mode == 0o600:
            print_status(True, "SSH key permissions are correct (600)")
        else:
            print_status(False, f"SSH key permissions are {oct(mode)} (should be 600)")
            issues.append("SSH key permissions")
    else:
        print_status(False, f"SSH key not found at {ssh_key_path}")
        issues.append("SSH key missing")
        
        # Check if it's in Pulumi ESC
        print("\n   Checking Pulumi ESC for SSH key...")
        try:
            ssh_key = get_config_value("lambda_private_ssh_key")
            if ssh_key:
                print_status(True, "SSH key found in Pulumi ESC!")
                print("   Run this to set it up: python3 scripts/setup_ssh_from_esc.py")
            else:
                print_status(False, "SSH key not found in Pulumi ESC")
                issues.append("SSH key not in ESC")
        except Exception as e:
            print_warning(f"Could not check Pulumi ESC: {e}")
    
    # 3. Test SSH connectivity
    print("\n3. Testing SSH connectivity...")
    if ssh_key_path.exists():
        test_ip = "104.171.202.103"  # sophia-production-instance
        
        cmd = [
            "ssh", "-i", str(ssh_key_path),
            "-o", "StrictHostKeyChecking=no",
            "-o", "ConnectTimeout=5",
            "-o", "BatchMode=yes",
            f"ubuntu@{test_ip}",
            "echo 'SSH_OK'"
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if result.returncode == 0 and "SSH_OK" in result.stdout:
                print_status(True, f"SSH connection to {test_ip} successful")
            else:
                print_status(False, f"SSH connection failed: {result.stderr}")
                issues.append("SSH connectivity")
                
                # Try to diagnose
                if "Permission denied" in result.stderr:
                    print_warning("SSH key might not match the server's authorized_keys")
                elif "Connection timed out" in result.stderr:
                    print_warning("Server might be down or firewall blocking")
                elif "Host key verification failed" in result.stderr:
                    print_warning("Known hosts issue")
        except subprocess.TimeoutExpired:
            print_status(False, "SSH connection timed out")
            issues.append("SSH timeout")
        except Exception as e:
            print_status(False, f"SSH test failed: {e}")
            issues.append("SSH test error")
    
    # 4. Check Pulumi configuration
    print("\n4. Checking Pulumi configuration...")
    pulumi_token = os.getenv("PULUMI_ACCESS_TOKEN")
    if pulumi_token:
        print_status(True, "PULUMI_ACCESS_TOKEN is set")
    else:
        print_status(False, "PULUMI_ACCESS_TOKEN not set")
        issues.append("Pulumi token missing")
    
    # 5. Check Docker
    print("\n5. Checking Docker...")
    try:
        result = subprocess.run(["docker", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print_status(True, f"Docker installed: {result.stdout.strip()}")
        else:
            print_status(False, "Docker not working")
            issues.append("Docker")
    except:
        print_status(False, "Docker not installed")
        issues.append("Docker missing")
    
    # Summary and solutions
    print_header("DIAGNOSTIC SUMMARY")
    
    if not issues:
        print(f"{GREEN}✅ All checks passed! Ready for deployment.{NC}")
        print("\nYou can now run:")
        print("  ./scripts/deploy_sophia_production_real.sh")
        print("  OR")
        print("  ./scripts/deploy_sophia_production_fixed.sh")
    else:
        print(f"{RED}Found {len(issues)} issue(s):{NC}")
        for issue in issues:
            print(f"  - {issue}")
        
        print(f"\n{YELLOW}SOLUTIONS:{NC}")
        
        if "SSH key missing" in issues:
            print("\n🔑 SSH Key Setup:")
            print("  The SSH private key needs to be obtained from:")
            print("  1. Check if you have it backed up somewhere")
            print("  2. Check with the team if someone has it")
            print("  3. If using Lambda Labs dashboard, you might need to:")
            print("     - Generate a new key pair")
            print("     - Update the public key in Lambda Labs")
            print("     - Save the private key to ~/.ssh/sophia2025.pem")
        
        if "SSH connectivity" in issues or "SSH timeout" in issues:
            print("\n🌐 SSH Connectivity:")
            print("  1. Check if the instance is running in Lambda Labs dashboard")
            print("  2. Verify the IP address is correct")
            print("  3. Check firewall/security group settings")
            print("  4. Try a different instance:")
            print("     - sophia-ai-core: 192.222.58.232")
            print("     - sophia-mcp-orchestrator: 104.171.202.117")
        
        if "Pulumi token missing" in issues:
            print("\n🔐 Pulumi Setup:")
            print("  export PULUMI_ACCESS_TOKEN='your-token-here'")
    
    return len(issues) == 0

if __name__ == "__main__":
    success = check_prerequisites()
    sys.exit(0 if success else 1) 