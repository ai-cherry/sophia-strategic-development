#!/usr/bin/env python3
"""
Lambda Labs API SSH Fix
Uses the Lambda Labs API to directly execute commands on instances
"""

import requests
import json
import time

# Your API credentials
API_KEY = "secret_sophiacloudapi_17cf7f3cedca48f18b4b8ea46cbb258f.EsLXt0lkGlhZ1Nd369Ld5DMSuhJg9O9y"
BASE_URL = "https://cloud.lambda.ai/api/v1"

# Your SSH public key
SSH_PUBLIC_KEY = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCKAPI0WU9UcB5vVnneP3oExytrPcD0PON5NeQxeNAJOWQSWi/fvkQ97dhAEtjyddmaCti7LFrp3CW+4gtGSiC+2/jOVqERLkmycbC8UZNpyqCiLIwO4MkIuxVNiRkg/ucPuf0DjakJh92xFDIyeDAR55OrpMWqX6O0+OZL0DFXE7jBDaloez+oLytM16CMHtlnx+5Br7O+RoPLEFvBz9RZyqlzs5144pvgHyRSwuvXBcYLKqT24kAPqvxc0SqGYLnNAD1q96BPqMwZONAFPDf3jTFGznmO+I3f+cyiR9Mai7Na9C2/21UJL/9APt7unjQhyQtCF++pwUXxhJX42tId SophiaSSH5"

def get_auth_headers():
    """Get authentication headers for API calls"""
    return {
        'Authorization': f'Basic {API_KEY}',
        'Content-Type': 'application/json'
    }

def get_instances():
    """Get all running instances"""
    print("🔍 Getting all instances...")
    
    response = requests.get(f"{BASE_URL}/instances", auth=(API_KEY, ''))
    
    if response.status_code == 200:
        instances = response.json()['data']
        print(f"✅ Found {len(instances)} instances")
        return instances
    else:
        print(f"❌ Failed to get instances: {response.text}")
        return []

def restart_instance(instance_id):
    """Restart an instance to apply new SSH keys"""
    print(f"🔄 Restarting instance {instance_id}...")
    
    response = requests.post(f"{BASE_URL}/instances/{instance_id}/restart", auth=(API_KEY, ''))
    
    if response.status_code == 200:
        print(f"✅ Instance {instance_id} restart initiated")
        return True
    else:
        print(f"❌ Failed to restart instance {instance_id}: {response.text}")
        return False

def wait_for_instance(instance_id, target_status="running"):
    """Wait for instance to reach target status"""
    print(f"⏳ Waiting for instance {instance_id} to be {target_status}...")
    
    for i in range(30):  # 5 minute timeout
        response = requests.get(f"{BASE_URL}/instances/{instance_id}", auth=(API_KEY, ''))
        
        if response.status_code == 200:
            status = response.json()['data']['status']['status']
            print(f"📊 Instance {instance_id} status: {status}")
            
            if status == target_status:
                print(f"✅ Instance {instance_id} is {target_status}")
                return True
        
        time.sleep(10)
    
    print(f"❌ Timeout waiting for instance {instance_id}")
    return False

def terminate_and_restart_with_new_key(instance_id, instance_type, region):
    """Terminate instance and launch new one with updated SSH key"""
    print(f"🔥 Terminating and relaunching instance {instance_id}...")
    
    # Terminate instance
    terminate_response = requests.post(f"{BASE_URL}/instances/{instance_id}/terminate", auth=(API_KEY, ''))
    
    if terminate_response.status_code != 200:
        print(f"❌ Failed to terminate instance: {terminate_response.text}")
        return False
    
    print("✅ Instance terminated, waiting 30 seconds...")
    time.sleep(30)
    
    # Launch new instance with SSH key
    launch_data = {
        "region_name": region,
        "instance_type_name": instance_type,
        "ssh_key_names": ["sophia-deployment-working"],  # Use our new SSH key
        "file_system_names": [],
        "quantity": 1
    }
    
    launch_response = requests.post(f"{BASE_URL}/instances", 
                                   json=launch_data, 
                                   auth=(API_KEY, ''))
    
    if launch_response.status_code == 200:
        new_instance_id = launch_response.json()['data']['instance_ids'][0]
        print(f"✅ New instance launched: {new_instance_id}")
        return new_instance_id
    else:
        print(f"❌ Failed to launch new instance: {launch_response.text}")
        return None

def main():
    print("🚀 LAMBDA LABS API SSH FIX STARTING...")
    print("=" * 60)
    
    # Get all instances
    instances = get_instances()
    
    if not instances:
        print("❌ No instances found or API error")
        return False
    
    print("\n📋 CURRENT INSTANCES:")
    for instance in instances:
        instance_id = instance['id']
        name = instance.get('name', 'unnamed')
        ip = instance.get('ip', 'no-ip')
        status = instance['status']['status']
        instance_type = instance['instance_type']['name']
        region = instance['region']['name']
        ssh_keys = [key['name'] for key in instance.get('ssh_key_names', [])]
        
        print(f"  🖥️  {name} ({instance_id})")
        print(f"      IP: {ip}")
        print(f"      Status: {status}")
        print(f"      Type: {instance_type}")
        print(f"      Region: {region}")
        print(f"      SSH Keys: {ssh_keys}")
        print()
    
    # Strategy: Restart instances to pick up the new SSH key we added
    print("🔄 RESTARTING ALL INSTANCES TO PICK UP NEW SSH KEY...")
    
    restarted_instances = []
    
    for instance in instances:
        instance_id = instance['id']
        name = instance.get('name', 'unnamed')
        
        print(f"\n🎯 Processing {name} ({instance_id})...")
        
        if restart_instance(instance_id):
            restarted_instances.append(instance_id)
        else:
            print(f"❌ Failed to restart {name}")
    
    # Wait for all instances to come back online
    print(f"\n⏳ WAITING FOR {len(restarted_instances)} INSTANCES TO RESTART...")
    
    all_ready = True
    for instance_id in restarted_instances:
        if not wait_for_instance(instance_id, "running"):
            all_ready = False
    
    print("\n" + "=" * 60)
    
    if all_ready:
        print("🎉 ALL INSTANCES RESTARTED SUCCESSFULLY!")
        print("🔑 New SSH key should now be active on all servers")
        print("\n🚀 STARTING DEPLOYMENT...")
        
        # Test SSH access
        import subprocess
        test_ip = "192.222.58.232"
        print(f"🧪 Testing SSH access to {test_ip}...")
        
        try:
            result = subprocess.run([
                "ssh", "-i", "~/.ssh/sophia_working_key", 
                "-o", "ConnectTimeout=10", 
                f"ubuntu@{test_ip}", 
                "echo 'SSH working!'"
            ], capture_output=True, text=True, timeout=15)
            
            if result.returncode == 0:
                print("✅ SSH ACCESS CONFIRMED! Starting deployment...")
                subprocess.run(["python3", "scripts/deploy_to_lambda_labs.py"])
            else:
                print(f"❌ SSH still not working: {result.stderr}")
        except Exception as e:
            print(f"❌ SSH test error: {e}")
        
        return True
    else:
        print("❌ Some instances failed to restart properly")
        return False

if __name__ == "__main__":
    main() 