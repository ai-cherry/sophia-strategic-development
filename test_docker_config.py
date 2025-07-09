#!/usr/bin/env python3
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.core.auto_esc_config import get_docker_hub_config

# Test Docker Hub configuration
config = get_docker_hub_config()
print(f"Docker Hub Username: {config['username']}")
print(f"Has Access Token: {config['access_token'] is not None}")
print(f"Token Length: {len(config['access_token']) if config['access_token'] else 0}")

# If we have credentials, try to use them
if config['access_token']:
    print("\nAttempting Docker login...")
    import subprocess
    
    # Use the token with docker login
    process = subprocess.Popen(
        ['docker', 'login', '-u', config['username'], '--password-stdin'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    stdout, stderr = process.communicate(input=config['access_token'])
    
    if process.returncode == 0:
        print("✅ Docker login successful!")
    else:
        print("❌ Docker login failed!")
        print(f"Error: {stderr}")
else:
    print("\n⚠️  No Docker Hub access token found in configuration") 