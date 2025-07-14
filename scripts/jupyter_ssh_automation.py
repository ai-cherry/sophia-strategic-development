#!/usr/bin/env python3
"""
JupyterLab SSH Key Automation
Uses JupyterLab URLs to add SSH keys via web interface
"""

import requests
import time

# Your SSH public key
SSH_PUBLIC_KEY = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCKAPI0WU9UcB5vVnneP3oExytrPcD0PON5NeQxeNAJOWQSWi/fvkQ97dhAEtjyddmaCti7LFrp3CW+4gtGSiC+2/jOVqERLkmycbC8UZNpyqCiLIwO4MkIuxVNiRkg/ucPuf0DjakJh92xFDIyeDAR55OrpMWqX6O0+OZL0DFXE7jBDaloez+oLytM16CMHtlnx+5Br7O+RoPLEFvBz9RZyqlzs5144pvgHyRSwuvXBcYLKqT24kAPqvxc0SqGYLnNAD1q96BPqMwZONAFPDf3jTFGznmO+I3f+cyiR9Mai7Na9C2/21UJL/9APt7unjQhyQtCF++pwUXxhJX42tId SophiaSSH5"

# JupyterLab instances from your API
JUPYTER_INSTANCES = [
    {
        "name": "sophia-production-instance",
        "ip": "104.171.202.103",
        "jupyter_url": "https://04c217e176bc4c6fad6e27680463071a-0.lambdaspaces.com",
        "token": "68c59f51afbc42098e049feda79ecfd9"
    },
    {
        "name": "sophia-ai-core", 
        "ip": "192.222.58.232",
        "jupyter_url": "https://ba7eae19197749e6bfb6598725d1eedb-0.lambdaspaces.com",
        "token": "8ab3764706b44648b69508be31598213"
    },
    {
        "name": "sophia-mcp-orchestrator",
        "ip": "104.171.202.117", 
        "jupyter_url": "https://002de2b1905e44caa7d5d0e2c7ffbb49-0.lambdaspaces.com",
        "token": "55dada80fdf74d4b98db9f73c3307c49"
    },
    {
        "name": "sophia-data-pipeline",
        "ip": "104.171.202.134",
        "jupyter_url": "https://44ea02e98cbf49ddbc22cd290b2f6d39-0.lambdaspaces.com", 
        "token": "b08d5acb10034cd1a9b6354bf38dab79"
    },
    {
        "name": "sophia-development",
        "ip": "155.248.194.183",
        "jupyter_url": "https://9505b42558ca4669a615ca82f053271f-0.lambdaspaces.com",
        "token": "cbb7815e6f4f48c497b61b824ede89dd"
    }
]

def add_ssh_key_via_jupyter(instance):
    """Add SSH key via JupyterLab terminal API"""
    name = instance["name"]
    jupyter_url = instance["jupyter_url"] 
    token = instance["token"]
    ip = instance["ip"]
    
    print(f"🔧 Adding SSH key to {name} ({ip}) via JupyterLab...")
    
    # JupyterLab API endpoint for terminal
    api_url = f"{jupyter_url}/api/terminals"
    
    session = requests.Session()
    
    try:
        # Create a new terminal session
        print(f"  📟 Creating terminal session...")
        create_response = session.post(
            api_url,
            params={"token": token},
            json={"name": "bash"},
            timeout=10
        )
        
        if create_response.status_code != 200:
            print(f"  ❌ Failed to create terminal: {create_response.status_code}")
            return False
            
        terminal_data = create_response.json()
        terminal_name = terminal_data.get("name", "1")
        
        print(f"  ✅ Terminal created: {terminal_name}")
        
        # Execute command to add SSH key
        command = f'echo "{SSH_PUBLIC_KEY}" >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys && echo "SSH_KEY_ADDED_SUCCESS"'
        
        exec_url = f"{jupyter_url}/api/terminals/{terminal_name}"
        
        print(f"  🔑 Adding SSH key...")
        exec_response = session.post(
            exec_url,
            params={"token": token},
            json={"stdin": command + "\n"},
            timeout=15
        )
        
        if exec_response.status_code == 200:
            print(f"  ✅ SSH key added to {name}")
            
            # Clean up terminal
            session.delete(f"{api_url}/{terminal_name}", params={"token": token})
            return True
        else:
            print(f"  ❌ Failed to execute command: {exec_response.status_code}")
            return False
            
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def test_ssh_access(ip):
    """Test SSH access to server"""
    print(f"🧪 Testing SSH access to {ip}...")
    
    import subprocess
    try:
        result = subprocess.run([
            "ssh", "-i", "~/.ssh/sophia_final_key",
            "-o", "ConnectTimeout=10",
            "-o", "StrictHostKeyChecking=no",
            f"ubuntu@{ip}",
            "echo 'SSH working on {ip}'"
        ], capture_output=True, text=True, timeout=15)
        
        if result.returncode == 0:
            print(f"  ✅ SSH access confirmed for {ip}")
            return True
        else:
            print(f"  ❌ SSH access failed for {ip}: {result.stderr}")
            return False
    except Exception as e:
        print(f"  ❌ SSH test error for {ip}: {e}")
        return False

def main():
    print("🚀 JUPYTER SSH KEY AUTOMATION STARTING...")
    print("=" * 60)
    
    success_count = 0
    total_instances = len(JUPYTER_INSTANCES)
    
    for instance in JUPYTER_INSTANCES:
        print(f"\n🎯 Processing {instance['name']}...")
        
        if add_ssh_key_via_jupyter(instance):
            # Wait a moment for the key to be written
            time.sleep(2)
            
            if test_ssh_access(instance['ip']):
                success_count += 1
            else:
                print(f"  ⚠️  Key added but SSH test failed")
        else:
            print(f"  ❌ Failed to add SSH key")
    
    print("\n" + "=" * 60)
    print(f"📊 FINAL RESULTS:")
    print(f"✅ Success: {success_count}/{total_instances} servers")
    print(f"❌ Failed: {total_instances - success_count}/{total_instances} servers")
    
    if success_count >= 3:  # At least 3 servers working
        print("\n🎉 SUFFICIENT SERVERS READY! Starting deployment...")
        import subprocess
        subprocess.run(["python3", "scripts/deploy_to_lambda_labs.py"])
        return True
    else:
        print(f"\n⚠️  Need at least 3 working servers for deployment")
        return False

if __name__ == "__main__":
    main() 