#!/usr/bin/env python3
"""
Automated SSH Key Fix for Lambda Labs
Uses API to directly add SSH key to all instances
"""

import subprocess

# Your credentials
API_KEY = "secret_sophiacloudapi_17cf7f3cedca48f18b4b8ea46cbb258f.EsLXt0lkGlhZ1Nd369Ld5DMSuhJg9O9y"
SSH_PUBLIC_KEY = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCKAPI0WU9UcB5vVnneP3oExytrPcD0PON5NeQxeNAJOWQSWi/fvkQ97dhAEtjyddmaCti7LFrp3CW+4gtGSiC+2/jOVqERLkmycbC8UZNpyqCiLIwO4MkIuxVNiRkg/ucPuf0DjakJh92xFDIyeDAR55OrpMWqX6O0+OZL0DFXE7jBDaloez+oLytM16CMHtlnx+5Br7O+RoPLEFvBz9RZyqlzs5144pvgHyRSwuvXBcYLKqT24kAPqvxc0SqGYLnNAD1q96BPqMwZONAFPDf3jTFGznmO+I3f+cyiR9Mai7Na9C2/21UJL/9APt7unjQhyQtCF++pwUXxhJX42tId SophiaSSH5"

# Server IPs
SERVERS = [
    "192.222.58.232",  # Primary GH200
    "104.171.202.117", # MCP Orchestrator  
    "104.171.202.134", # Data Pipeline
    "104.171.202.103", # Production Services
    "155.248.194.183"  # Development
]

def add_ssh_key_to_server(ip):
    """Add SSH key directly to server using existing sophia2025 key"""
    print(f"🔧 Adding SSH key to {ip}...")
    
    # Use the existing sophia2025 private key to add the new key
    ssh_command = f'''
    ssh -i ~/.ssh/sophia_correct_key -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=10 -o StrictHostKeyChecking=no ubuntu@{ip} "
    echo '{SSH_PUBLIC_KEY}' >> ~/.ssh/authorized_keys && 
    chmod 600 ~/.ssh/authorized_keys && 
    echo 'SSH key added successfully to {ip}'
    "
    '''
    
    try:
        result = subprocess.run(ssh_command, shell=True, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print(f"✅ SUCCESS: SSH key added to {ip}")
            return True
        else:
            print(f"❌ FAILED: {ip} - {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ ERROR: {ip} - {e}")
        return False

def test_new_ssh_key(ip):
    """Test the new SSH key works"""
    print(f"🧪 Testing new SSH key on {ip}...")
    
    ssh_command = f'ssh -i ~/.ssh/sophia_correct_key -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=5 ubuntu@{ip} "echo \'New SSH key working on {ip}\'"'
    
    try:
        result = subprocess.run(ssh_command, shell=True, capture_output=True, text=True, timeout=15)
        if result.returncode == 0:
            print(f"✅ SSH TEST PASSED: {ip}")
            return True
        else:
            print(f"❌ SSH TEST FAILED: {ip}")
            return False
    except Exception as e:
        print(f"❌ SSH TEST ERROR: {ip} - {e}")
        return False

def main():
    print("🚀 AUTOMATED SSH KEY FIX STARTING...")
    print("=" * 50)
    
    # First, ensure we have the working SSH key locally
    print("📋 Setting up local SSH key...")
    
    success_count = 0
    total_servers = len(SERVERS)
    
    for ip in SERVERS:
        print(f"\n🎯 Processing server {ip}...")
        
        if add_ssh_key_to_server(ip):
            if test_new_ssh_key(ip):
                success_count += 1
            else:
                print(f"⚠️  Key added but test failed for {ip}")
        else:
            print(f"❌ Failed to add key to {ip}")
    
    print("\n" + "=" * 50)
    print("📊 FINAL RESULTS:")
    print(f"✅ Success: {success_count}/{total_servers} servers")
    print(f"❌ Failed: {total_servers - success_count}/{total_servers} servers")
    
    if success_count == total_servers:
        print("\n🎉 ALL SERVERS READY! Starting deployment...")
        # Start deployment immediately
        subprocess.run(["python3", "scripts/deploy_to_lambda_labs.py"], check=False)
    else:
        print("\n⚠️  Some servers failed. Manual intervention needed.")
        return False
    
    return True

if __name__ == "__main__":
    main() 