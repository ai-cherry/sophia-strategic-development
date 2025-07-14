#!/usr/bin/env python3
"""
Quick SSH Access Test for Lambda Labs Servers
Tests SSH connectivity to all configured servers
"""

import subprocess
import sys
from datetime import datetime

def test_ssh_server(alias, ip, description):
    """Test SSH connection to a single server"""
    print(f"🧪 Testing {description} ({alias} - {ip})...")
    
    try:
        result = subprocess.run([
            "ssh", "-o", "ConnectTimeout=10", "-o", "BatchMode=yes",
            alias, "echo 'SSH OK' && hostname && uptime"
        ], capture_output=True, text=True, timeout=15)
        
        if result.returncode == 0:
            output_lines = result.stdout.strip().split('\n')
            hostname = output_lines[1] if len(output_lines) > 1 else "unknown"
            uptime = output_lines[2] if len(output_lines) > 2 else "unknown"
            
            print(f"   ✅ CONNECTED - Hostname: {hostname}")
            print(f"   ⏱️  Uptime: {uptime}")
            return True
        else:
            error_msg = result.stderr.strip() or "Connection failed"
            print(f"   ❌ FAILED - {error_msg}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"   ❌ TIMEOUT - Connection timed out")
        return False
    except Exception as e:
        print(f"   ❌ ERROR - {e}")
        return False

def main():
    """Test all Lambda Labs servers"""
    print("🚀 Sophia AI Lambda Labs SSH Access Test")
    print("=" * 60)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Define all servers
    servers = [
        ("sophia-primary", "192.222.58.232", "Primary Server (GH200)"),
        ("sophia-mcp", "104.171.202.117", "MCP Orchestrator (A6000)"),
        ("sophia-data", "104.171.202.134", "Data Pipeline (A100)"),
        ("sophia-prod", "104.171.202.103", "Production Services (RTX6000)"),
        ("sophia-dev", "155.248.194.183", "Development (A10)")
    ]
    
    # Test each server
    working_servers = []
    failed_servers = []
    
    for alias, ip, description in servers:
        if test_ssh_server(alias, ip, description):
            working_servers.append((alias, ip, description))
        else:
            failed_servers.append((alias, ip, description))
        print()
    
    # Summary
    print("=" * 60)
    print("🎯 SSH ACCESS SUMMARY")
    print("=" * 60)
    
    if working_servers:
        print(f"✅ WORKING SERVERS ({len(working_servers)}/{len(servers)}):")
        for alias, ip, description in working_servers:
            print(f"   ✅ {description} ({alias})")
    
    if failed_servers:
        print(f"\n❌ FAILED SERVERS ({len(failed_servers)}/{len(servers)}):")
        for alias, ip, description in failed_servers:
            print(f"   ❌ {description} ({alias})")
    
    print(f"\n📊 SUCCESS RATE: {len(working_servers)}/{len(servers)} ({len(working_servers)/len(servers)*100:.1f}%)")
    
    # Next steps
    if len(working_servers) == len(servers):
        print("\n🎉 ALL SERVERS ACCESSIBLE!")
        print("🚀 Ready to deploy: python3 scripts/master_deploy.py")
    elif len(working_servers) > 0:
        print(f"\n⚠️  PARTIAL ACCESS - {len(failed_servers)} servers need SSH key setup")
        print("📋 Add SSH public key to failed servers in Lambda Labs console")
    else:
        print("\n🔑 NO ACCESS - SSH public key needs to be added to all servers")
        print("📋 Follow instructions in DEPLOYMENT_STATUS_UPDATE.md")
    
    print("\n💡 SSH Public Key to add:")
    print("ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCKAPI0WU9UcB5vVnneP3oExytrPcD0PON5NeQxeNAJOWQSWi/fvkQ97dhAEtjyddmaCti7LFrp3CW+4gtGSiC+2/jOVqERLkmycbC8UZNpyqCiLIwO4MkIuxVNiRkg/ucPuf0DjakJh92xFDIyeDAR55OrpMWqX6O0+OZL0DFXE7jBDaloez+oLytM16CMHtlnx+5Br7O+RoPLEFvBz9RZyqlzs5144pvgHyRSwuvXBcYLKqT24kAPqvxc0SqGYLnNAD1q96BPqMwZONAFPDf3jTFGznmO+I3f+cyiR9Mai7Na9C2/21UJL/9APt7unjQhyQtCF++pwUXxhJX42tId SophiaSSH5")
    
    return len(working_servers) == len(servers)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 