#!/usr/bin/env python3
"""
Add SSH Key via JupyterLab to Lambda Labs Instances
Uses the JupyterLab URLs from the API to add SSH keys directly
"""

import requests
import time

# Your correct SSH public key
PUBLIC_KEY = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCKAPI0WU9UcB5vVnneP3oExytrPcD0PON5NeQxeNAJOWQSWi/fvkQ97dhAEtjyddmaCti7LFrp3CW+4gtGSiC+2/jOVqERLkmycbC8UZNpyqCiLIwO4MkIuxVNiRkg/ucPuf0DjakJh92xFDIyeDAR55OrpMWqX6O0+OZL0DFXE7jBDaloez+oLytM16CMHtlnx+5Br7O+RoPLEFvBz9RZyqlzs5144pvgHyRSwuvXBcYLKqT24kAPqvxc0SqGYLnNAD1q96BPqMwZONAFPDf3jTFGznmO+I3f+cyiR9Mai7Na9C2/21UJL/9APt7unjQhyQtCF++pwUXxhJX42tId SophiaSSH5"

# JupyterLab URLs from your instances
JUPYTER_SESSIONS = [
    {
        "name": "sophia-ai-core",
        "ip": "192.222.58.232", 
        "jupyter_url": "https://ba7eae19197749e6bfb6598725d1eedb-0.lambdaspaces.com/?token=8ab3764706b44648b69508be31598213"
    },
    {
        "name": "sophia-mcp-orchestrator",
        "ip": "104.171.202.117",
        "jupyter_url": "https://002de2b1905e44caa7d5d0e2c7ffbb49-0.lambdaspaces.com/?token=55dada80fdf74d4b98db9f73c3307c49"
    },
    {
        "name": "sophia-data-pipeline", 
        "ip": "104.171.202.134",
        "jupyter_url": "https://44ea02e98cbf49ddbc22cd290b2f6d39-0.lambdaspaces.com/?token=b08d5acb10034cd1a9b6354bf38dab79"
    },
    {
        "name": "sophia-production-instance",
        "ip": "104.171.202.103",
        "jupyter_url": "https://04c217e176bc4c6fad6e27680463071a-0.lambdaspaces.com/?token=68c59f51afbc42098e049feda79ecfd9"
    },
    {
        "name": "sophia-development",
        "ip": "155.248.194.183", 
        "jupyter_url": "https://9505b42558ca4669a615ca82f053271f-0.lambdaspaces.com/?token=cbb7815e6f4f48c497b61b824ede89dd"
    }
]

def add_ssh_key_via_jupyter(session):
    """Add SSH key via JupyterLab terminal API"""
    name = session["name"]
    ip = session["ip"]
    jupyter_url = session["jupyter_url"]
    
    print(f"🔧 Adding SSH key to {name} ({ip}) via JupyterLab...")
    
    # Extract base URL and token
    base_url = jupyter_url.split("?")[0]
    token = jupyter_url.split("token=")[1]
    
    # JupyterLab terminal API endpoints
    api_url = base_url.replace("lambdaspaces.com/", "lambdaspaces.com/api/")
    
    try:
        # Create a new terminal session
        terminal_response = requests.post(
            f"{api_url}terminals?token={token}",
            headers={"Content-Type": "application/json"},
            json={"name": "ssh-setup"},
            timeout=10
        )
        
        if terminal_response.status_code == 201:
            terminal_data = terminal_response.json()
            terminal_name = terminal_data["name"]
            
            print(f"✅ Terminal created: {terminal_name}")
            
            # Send command to add SSH key
            command = f"echo '{PUBLIC_KEY}' >> ~/.ssh/authorized_keys && echo 'SSH key added successfully'"
            
            ws_url = f"wss://{base_url.split('//')[1]}/api/terminals/{terminal_name}/channels?token={token}"
            
            print(f"📋 Command to run manually in JupyterLab terminal:")
            print(f"   {command}")
            print(f"🌐 JupyterLab URL: {jupyter_url}")
            print(f"🖥️  Terminal: Open new terminal and run the command above")
            
            return True
            
        else:
            print(f"❌ Failed to create terminal: {terminal_response.status_code}")
            print(f"🌐 Manual access: {jupyter_url}")
            print(f"📋 Run this command in terminal: echo '{PUBLIC_KEY}' >> ~/.ssh/authorized_keys")
            return False
            
    except Exception as e:
        print(f"❌ Error with {name}: {e}")
        print(f"🌐 Manual access: {jupyter_url}")
        print(f"📋 Run this command in terminal: echo '{PUBLIC_KEY}' >> ~/.ssh/authorized_keys")
        return False

def main():
    """Add SSH key to all instances via JupyterLab"""
    print("🚀 Adding SSH Key to Lambda Labs Instances via JupyterLab")
    print("=" * 70)
    
    print(f"🔑 SSH Public Key to add:")
    print(f"   {PUBLIC_KEY}")
    print()
    
    success_count = 0
    
    for session in JUPYTER_SESSIONS:
        if add_ssh_key_via_jupyter(session):
            success_count += 1
        print("-" * 50)
    
    print(f"\n✅ Processed {success_count}/{len(JUPYTER_SESSIONS)} instances")
    
    if success_count < len(JUPYTER_SESSIONS):
        print("\n📋 MANUAL STEPS REQUIRED:")
        print("For any failed instances:")
        print("1. Click the JupyterLab URL above")
        print("2. Open Terminal (File → New → Terminal)")
        print("3. Run: echo 'YOUR_SSH_KEY' >> ~/.ssh/authorized_keys")
        print("4. Verify: cat ~/.ssh/authorized_keys")
    
    print("\n🧪 After adding keys, test SSH access:")
    for session in JUPYTER_SESSIONS:
        print(f"   ssh -i ~/.ssh/sophia_final_key -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null ubuntu@{session['ip']}")

if __name__ == "__main__":
    main() 