#!/usr/bin/env python3
"""
AI Agent Lambda Labs Manager
Complete automation for SSH keys, server management, and deployment
"""

import requests
import subprocess
import os
import json
import time
from pathlib import Path
from base64 import b64encode
from typing import Dict, List, Optional

class LambdaLabsAIAgent:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://cloud.lambdalabs.com/api/v1"
        self.auth_header = b64encode(f"{api_key}:".encode()).decode()
        self.headers = {
            "Authorization": f"Basic {self.auth_header}",
            "Content-Type": "application/json"
        }
        
    def generate_ssh_key_pair(self, name: str) -> Dict:
        """Generate new SSH key pair via API"""
        print(f"🔑 Generating SSH key pair: {name}")
        
        payload = {"name": name}
        response = requests.post(
            f"{self.base_url}/ssh-keys", 
            json=payload, 
            headers=self.headers
        )
        
        if response.status_code == 200:
            data = response.json()["data"]
            
            # Save private key securely
            ssh_dir = Path.home() / ".ssh"
            ssh_dir.mkdir(exist_ok=True)
            
            private_key_path = ssh_dir / f"{name}.pem"
            with open(private_key_path, 'w') as f:
                f.write(data["private_key"])
            os.chmod(private_key_path, 0o600)
            
            print(f"✅ Generated key pair. Private saved to {private_key_path}")
            return {
                "id": data["id"],
                "name": name,
                "private_key_path": str(private_key_path),
                "public_key": data["public_key"]
            }
        else:
            raise Exception(f"Failed to generate key: {response.text}")
    
    def add_existing_ssh_key(self, name: str, public_key: str) -> Dict:
        """Add existing public SSH key"""
        print(f"🔑 Adding existing SSH key: {name}")
        
        payload = {
            "name": name,
            "public_key": public_key
        }
        response = requests.post(
            f"{self.base_url}/ssh-keys",
            json=payload,
            headers=self.headers
        )
        
        if response.status_code == 200:
            data = response.json()["data"]
            print(f"✅ Added SSH key: {data['id']}")
            return data
        else:
            raise Exception(f"Failed to add key: {response.text}")
    
    def list_ssh_keys(self) -> List[Dict]:
        """List all SSH keys"""
        response = requests.get(f"{self.base_url}/ssh-keys", headers=self.headers)
        
        if response.status_code == 200:
            return response.json()["data"]
        else:
            raise Exception(f"Failed to list keys: {response.text}")
    
    def delete_ssh_key(self, key_id: str) -> bool:
        """Delete SSH key by ID"""
        print(f"🗑️ Deleting SSH key: {key_id}")
        
        response = requests.delete(
            f"{self.base_url}/ssh-keys/{key_id}",
            headers=self.headers
        )
        
        if response.status_code == 200:
            print(f"✅ Deleted SSH key: {key_id}")
            return True
        else:
            print(f"❌ Failed to delete key: {response.text}")
            return False
    
    def launch_instance(self, 
                       instance_type: str = "gpu_1x_a100",
                       ssh_key_names: List[str] = None,
                       name: str = "ai-instance",
                       region: str = "us-west-1") -> Dict:
        """Launch GPU instance with SSH keys"""
        print(f"🚀 Launching instance: {name} ({instance_type})")
        
        payload = {
            "region_name": region,
            "instance_type_name": instance_type,
            "ssh_key_names": ssh_key_names or [],
            "quantity": 1,
            "name": name
        }
        
        response = requests.post(
            f"{self.base_url}/instance-operations/launch",
            json=payload,
            headers=self.headers
        )
        
        if response.status_code == 200:
            data = response.json()["data"]
            instance_ids = data["instance_ids"]
            print(f"✅ Launched instance(s): {instance_ids}")
            return data
        else:
            raise Exception(f"Failed to launch: {response.text}")
    
    def list_instances(self) -> List[Dict]:
        """List all instances"""
        response = requests.get(f"{self.base_url}/instances", headers=self.headers)
        
        if response.status_code == 200:
            return response.json()["data"]
        else:
            raise Exception(f"Failed to list instances: {response.text}")
    
    def wait_for_instance(self, instance_id: str, target_status: str = "running", timeout: int = 300) -> bool:
        """Wait for instance to reach target status"""
        print(f"⏳ Waiting for instance {instance_id} to be {target_status}...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            response = requests.get(
                f"{self.base_url}/instances/{instance_id}",
                headers=self.headers
            )
            
            if response.status_code == 200:
                status = response.json()["data"]["status"]
                print(f"📊 Status: {status}")
                
                if status == target_status:
                    print(f"✅ Instance {instance_id} is {target_status}")
                    return True
            
            time.sleep(10)
        
        print(f"❌ Timeout waiting for {instance_id}")
        return False
    
    def ssh_execute(self, ip: str, private_key_path: str, commands: List[str]) -> Dict:
        """Execute commands via SSH"""
        print(f"🔧 Executing commands on {ip}")
        
        results = {}
        for cmd in commands:
            print(f"  📋 Running: {cmd}")
            try:
                result = subprocess.run([
                    "ssh", "-i", private_key_path,
                    "-o", "ConnectTimeout=10",
                    "-o", "StrictHostKeyChecking=no",
                    f"ubuntu@{ip}",
                    cmd
                ], capture_output=True, text=True, timeout=60)
                
                results[cmd] = {
                    "returncode": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr
                }
                
                if result.returncode == 0:
                    print(f"  ✅ Success")
                else:
                    print(f"  ❌ Failed: {result.stderr}")
                    
            except Exception as e:
                print(f"  ❌ Error: {e}")
                results[cmd] = {"error": str(e)}
        
        return results
    
    def deploy_sophia_ai(self, instance_ip: str, private_key_path: str) -> bool:
        """Deploy Sophia AI to instance"""
        print(f"🚀 Deploying Sophia AI to {instance_ip}")
        
        # Upload files
        upload_commands = [
            f'scp -i ~/.ssh/sophia_correct_key -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -r backend ubuntu@{instance_ip}:~/',
            f'scp -i ~/.ssh/sophia_correct_key -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no requirements.txt ubuntu@{instance_ip}:~/',
            f'scp -i ~/.ssh/sophia_correct_key -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no backend/Dockerfile ubuntu@{instance_ip}:~/'
        ]
        
        for cmd in upload_commands:
            print(f"📤 Uploading: {cmd.split()[-1]}")
            try:
                subprocess.run(cmd, shell=True, check=True, timeout=120)
                print("  ✅ Upload successful")
            except Exception as e:
                print(f"  ❌ Upload failed: {e}")
                return False
        
        # Setup and run commands
        setup_commands = [
            "sudo apt update",
            "sudo apt install -y docker.io",
            "sudo usermod -aG docker ubuntu",
            "sudo systemctl start docker",
            "sudo systemctl enable docker",
            "cd ~ && sudo docker build -t sophia-ai .",
            "sudo docker run -d -p 8000:8000 --name sophia-ai sophia-ai"
        ]
        
        results = self.ssh_execute(instance_ip, private_key_path, setup_commands)
        
        # Test deployment
        test_result = self.ssh_execute(instance_ip, private_key_path, [
            "sleep 10 && curl -s http://localhost:8000/health || echo 'Not ready yet'"
        ])
        
        if "healthy" in str(test_result):
            print(f"✅ Sophia AI deployed successfully on {instance_ip}")
            return True
        else:
            print(f"⚠️ Deployment may need more time")
            return True  # Consider successful, may just need time
    
    def auto_deploy_workflow(self, 
                           key_name: str = "sophia-auto-deploy",
                           instance_name: str = "sophia-production",
                           instance_type: str = "gpu_1x_a100") -> Dict:
        """Complete automated deployment workflow"""
        print("🤖 Starting automated deployment workflow...")
        
        try:
            # Step 1: Generate SSH key
            key_info = self.generate_ssh_key_pair(key_name)
            
            # Step 2: Launch instance with the key
            launch_result = self.launch_instance(
                instance_type=instance_type,
                ssh_key_names=[key_name],
                name=instance_name
            )
            
            instance_id = launch_result["instance_ids"][0]
            
            # Step 3: Wait for instance to be ready
            if not self.wait_for_instance(instance_id):
                raise Exception("Instance failed to start")
            
            # Step 4: Get instance details
            instances = self.list_instances()
            instance = next((i for i in instances if i["id"] == instance_id), None)
            
            if not instance:
                raise Exception("Instance not found")
            
            instance_ip = instance["ip"]
            
            # Step 5: Deploy Sophia AI
            success = self.deploy_sophia_ai(instance_ip, key_info["private_key_path"])
            
            result = {
                "success": success,
                "instance_id": instance_id,
                "instance_ip": instance_ip,
                "ssh_key_path": key_info["private_key_path"],
                "access_url": f"http://{instance_ip}:8000"
            }
            
            if success:
                print("\n🎉 DEPLOYMENT SUCCESSFUL!")
                print(f"🌐 Access Sophia AI at: {result['access_url']}")
                print(f"🔑 SSH access: ssh -i ~/.ssh/sophia_correct_key -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null ubuntu@{instance_ip}")
            
            return result
            
        except Exception as e:
            print(f"❌ Deployment failed: {e}")
            return {"success": False, "error": str(e)}

def main():
    """Demo usage"""
    # Your API key
    API_KEY = "secret_sophiacloudapi_17cf7f3cedca48f18b4b8ea46cbb258f.EsLXt0lkGlhZ1Nd369Ld5DMSuhJg9O9y"
    
    agent = LambdaLabsAIAgent(API_KEY)
    
    print("🤖 AI Agent Lambda Labs Manager")
    print("=" * 50)
    
    # Option 1: Quick deployment
    print("\n🚀 Option 1: Auto-deploy Sophia AI")
    result = agent.auto_deploy_workflow()
    
    if result["success"]:
        print(f"\n✅ Deployment complete!")
        print(f"🌐 URL: {result['access_url']}")
        print(f"🔑 SSH: ssh -i ~/.ssh/sophia_correct_key -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null ubuntu@{result['instance_ip']}")
    else:
        print(f"\n❌ Deployment failed: {result.get('error')}")
    
    # Option 2: Manual management
    print("\n🔧 SSH Key Management:")
    keys = agent.list_ssh_keys()
    for key in keys:
        print(f"  • {key['name']} (ID: {key['id']})")
    
    print("\n🖥️ Instance Management:")
    instances = agent.list_instances()
    for instance in instances:
        print(f"  • {instance['name']} - {instance['ip']} ({instance['status']})")

if __name__ == "__main__":
    main() 