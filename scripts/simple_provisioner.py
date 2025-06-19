"""
A simple, standalone script to provision a Lambda Labs instance using the REST API.
This script has minimal dependencies and is designed to be run locally to bypass
complex environment issues.
"""
import os
import requests
import json
import time

# --- Configuration ---
API_KEY = os.getenv("LAMBDA_API_KEY")
SERVER_NAME = "sophia-ai-dev-docker-host-simple"
SSH_KEY_NAME = "cherry-ai-collaboration-key" # Must exist in your Lambda account
INSTANCE_TYPE = "cpu.c2"
REGION = "us-east-1"

def check_ssh_key():
    """Checks if the specified SSH key exists in the Lambda Labs account."""
    print(f"Verifying SSH key '{SSH_KEY_NAME}' exists...")
    url = "https://cloud.lambda.ai/api/v1/ssh-keys"
    response = requests.get(url, auth=(API_KEY, ""))
    response.raise_for_status()
    keys = response.json()["data"]
    if not any(key["name"] == SSH_KEY_NAME for key in keys):
        print(f"--- ERROR: SSH Key '{SSH_KEY_NAME}' not found in your Lambda Labs account. ---")
        print("Please upload your public key via the Lambda Labs dashboard first.")
        return False
    print("SSH key verified successfully.")
    return True

def provision_server():
    """Provisions the server and returns the instance data."""
    print(f"Launching instance '{SERVER_NAME}' of type '{INSTANCE_TYPE}'...")
    url = "https://cloud.lambda.ai/api/v1/instance-operations/launch"
    payload = {
        "region_name": REGION,
        "instance_type_name": INSTANCE_TYPE,
        "ssh_key_names": [SSH_KEY_NAME],
        "name": SERVER_NAME,
    }
    response = requests.post(url, json=payload, auth=(API_KEY, ""))
    response.raise_for_status()
    
    instance_id = response.json()["data"]["instance_ids"][0]
    print(f"Instance launch initiated. ID: {instance_id}")
    return instance_id

def get_instance_details(instance_id):
    """Waits for the instance to get an IP address and returns its details."""
    print("Waiting for instance to be assigned an IP address...")
    url = f"https://cloud.lambda.ai/api/v1/instances/{instance_id}"
    
    for _ in range(20): # Try for 10 minutes (20 * 30s)
        time.sleep(30)
        response = requests.get(url, auth=(API_KEY, ""))
        if response.status_code != 200:
            print(f"Still waiting... (status: {response.status_code})")
            continue
            
        data = response.json()["data"]
        if data.get("ip"):
            print("Instance is running and has an IP.")
            return data
        else:
            print(f"Still waiting for IP... (status: {data.get('status')})")
            
    raise TimeoutError("Instance did not get an IP address in time.")

def main():
    """Main execution block."""
    if not API_KEY:
        print("--- ERROR: LAMBDA_API_KEY environment variable not set. ---")
        print("Please set it before running the script.")
        return

    try:
        if not check_ssh_key():
            return
            
        instance_id = provision_server()
        details = get_instance_details(instance_id)
        
        ip_address = details["ip"]
        
        print("\n" + "="*50)
        print("🎉 Remote Docker Host Provisioned Successfully! 🎉")
        print(f"    IP Address: {ip_address}")
        print("="*50)
        print("\n--- NEXT STEPS ---")
        print("1. Connect your local Docker client to the new host:")
        print(f"   docker context create remote-dev --docker \"host=ssh://ubuntu@{ip_address}\"")
        print("\n2. Switch to the new context:")
        print("   docker context use remote-dev")
        print("\n3. Verify the connection (should show an empty list):")
        print("   docker ps")
        print("\n4. You can now run docker-compose commands which will execute on your new cloud server!")
        
    except requests.HTTPError as e:
        print(f"\n--- API Error ---")
        print(f"Request to {e.request.url} failed with status {e.response.status_code}")
        print(f"Response: {e.response.text}")
    except Exception as e:
        print(f"\n--- An unexpected error occurred ---")
        print(str(e))

if __name__ == "__main__":
    main() 