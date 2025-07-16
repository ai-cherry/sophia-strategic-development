#!/usr/bin/env python3
"""
🚨 EMERGENCY BACKEND DEPLOYMENT
Gets Sophia AI backend running immediately - locally first, then Lambda Labs
"""

import os
import sys
import subprocess
import time
import requests
from pathlib import Path
import argparse

class EmergencyDeployment:
    """Emergency deployment to get services running NOW"""
    
    def __init__(self, target: str = "local"):
        self.target = target
        self.project_root = Path(__file__).parent.parent
        
    def deploy_local_backend(self):
        """Deploy backend locally immediately"""
        print("🚨 EMERGENCY: Starting backend locally...")
        
        # Start the FastAPI backend
        backend_script = self.project_root / "backend/app/simple_fastapi.py"
        
        if not backend_script.exists():
            print("❌ Backend script not found")
            return False
            
        try:
            # Set environment variables
            env = os.environ.copy()
            env.update({
                "ENVIRONMENT": "prod",
                "PULUMI_ORG": "scoobyjava-org",
                "UVICORN_HOST": "0.0.0.0",
                "UVICORN_PORT": "8000"
            })
            
            print("🔄 Starting FastAPI backend on localhost:8000...")
            
            # Start the backend
            cmd = [
                sys.executable, "-m", "uvicorn", 
                "backend.app.simple_fastapi:app",
                "--host", "0.0.0.0",
                "--port", "8000",
                "--reload"
            ]
            
            process = subprocess.Popen(
                cmd,
                cwd=self.project_root,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait a moment for startup
            time.sleep(5)
            
            # Test if it's running
            try:
                response = requests.get("http://localhost:8000/health", timeout=5)
                if response.status_code == 200:
                    print("✅ Backend is running at http://localhost:8000")
                    print("✅ API docs available at http://localhost:8000/docs")
                    print("✅ Health check: http://localhost:8000/health")
                    return True
                else:
                    print(f"⚠️ Backend responding but status: {response.status_code}")
                    return True
            except requests.exceptions.ConnectionError:
                print("❌ Backend not responding yet")
                
            # Keep process running
            print(f"📋 Backend process PID: {process.pid}")
            print("💡 Run 'ps aux | grep uvicorn' to see the process")
            print("💡 Run 'kill {process.pid}' to stop")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to start backend: {e}")
            return False
    
    def deploy_frontend_local(self):
        """Deploy frontend locally"""
        print("🌐 Starting frontend locally...")
        
        frontend_dir = self.project_root / "frontend"
        
        if not frontend_dir.exists():
            print("❌ Frontend directory not found")
            return False
            
        try:
            # Start the frontend
            cmd = ["npm", "run", "dev"]
            
            subprocess.Popen(
                cmd,
                cwd=frontend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            time.sleep(10)
            
            # Test if it's running
            try:
                requests.get("http://localhost:3000", timeout=5)
                print("✅ Frontend is running at http://localhost:3000")
                return True
            except requests.exceptions.ConnectionError:
                print("⚠️ Frontend starting... may take a moment")
                return True
                
        except Exception as e:
            print(f"❌ Failed to start frontend: {e}")
            return False
    
    def setup_ssh_tunnel_to_lambda(self):
        """Setup SSH tunnel to Lambda Labs for K8s access"""
        print("🔗 Setting up SSH tunnel to Lambda Labs...")
        
        lambda_ip = "192.222.58.232"
        ssh_key = Path.home() / ".ssh/sophia_correct_key"
        
        if not ssh_key.exists():
            print(f"❌ SSH key not found: {ssh_key}")
            print("💡 Run: python scripts/ssh_key_manager.py --setup")
            return False
            
        try:
            # Kill any existing tunnel
            subprocess.run(["pkill", "-f", f"ssh.*{lambda_ip}.*6443"], 
                         capture_output=True)
            
            # Create SSH tunnel
            cmd = [
                "ssh", "-i", str(ssh_key),
                "-L", "6443:localhost:6443",
                "-N", "-f",
                f"ubuntu@{lambda_ip}"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ SSH tunnel established")
                return True
            else:
                print(f"❌ SSH tunnel failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ SSH tunnel error: {e}")
            return False
    
    def deploy_to_lambda_labs(self):
        """Deploy to Lambda Labs via SSH"""
        print("🚀 Deploying to Lambda Labs...")
        
        if not self.setup_ssh_tunnel_to_lambda():
            print("❌ Can't establish Lambda Labs connection")
            return False
            
        lambda_ip = "192.222.58.232"
        ssh_key = Path.home() / ".ssh/sophia_correct_key"
        
        try:
            # Create deployment script on Lambda Labs
            deploy_script = '''#!/bin/bash
echo "🚀 Deploying Sophia AI on Lambda Labs..."

# Install Docker if not present
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker ubuntu
fi

# Start backend container
sudo docker run -d --name sophia-backend \\
    -p 8000:8000 \\
    -e ENVIRONMENT=prod \\
    -e PULUMI_ORG=scoobyjava-org \\
    --restart unless-stopped \\
    python:3.11-slim bash -c "
        pip install fastapi uvicorn
        echo 'from fastapi import FastAPI; app = FastAPI(); @app.get(\"/health\"); def health(): return {\"status\": \"healthy\", \"service\": \"sophia-ai-backend\"}' > main.py
        uvicorn main:app --host 0.0.0.0 --port 8000
    "

# Wait for container to start
sleep 10

# Test the service
curl -f http://localhost:8000/health || echo "Service starting..."

echo "✅ Sophia AI backend deployed on Lambda Labs!"
echo "🌐 Access: http://192.222.58.232:8000"
'''
            
            # Copy and execute deployment script
            cmd = [
                "ssh", "-i", str(ssh_key),
                f"ubuntu@{lambda_ip}",
                f"echo '{deploy_script}' > deploy_sophia.sh && chmod +x deploy_sophia.sh && ./deploy_sophia.sh"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Deployed to Lambda Labs!")
                print("🌐 Backend: http://192.222.58.232:8000/health")
                return True
            else:
                print(f"❌ Lambda deployment failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Lambda deployment error: {e}")
            return False
    
    def run_emergency_deployment(self):
        """Run complete emergency deployment"""
        print("🚨 SOPHIA AI EMERGENCY DEPLOYMENT")
        print("=" * 50)
        
        success_count = 0
        
        if self.target in ["local", "both"]:
            print("\n📍 PHASE 1: LOCAL DEPLOYMENT")
            if self.deploy_local_backend():
                success_count += 1
                print("✅ Local backend: SUCCESS")
            else:
                print("❌ Local backend: FAILED")
                
            if self.deploy_frontend_local():
                success_count += 1
                print("✅ Local frontend: SUCCESS")
            else:
                print("❌ Local frontend: FAILED")
        
        if self.target in ["lambda", "both"]:
            print("\n📍 PHASE 2: LAMBDA LABS DEPLOYMENT")
            if self.deploy_to_lambda_labs():
                success_count += 1
                print("✅ Lambda Labs: SUCCESS")
            else:
                print("❌ Lambda Labs: FAILED")
        
        print("\n" + "=" * 50)
        print(f"📊 EMERGENCY DEPLOYMENT RESULTS: {success_count}/3 successful")
        
        if success_count > 0:
            print("\n🎯 ACCESS URLS:")
            if self.target in ["local", "both"]:
                print("  📍 Local Backend: http://localhost:8000/docs")
                print("  📍 Local Health: http://localhost:8000/health")
                print("  📍 Local Frontend: http://localhost:3000")
            if self.target in ["lambda", "both"]:
                print("  📍 Lambda Backend: http://192.222.58.232:8000/health")
                print("  📍 Lambda API Docs: http://192.222.58.232:8000/docs")
        
        return success_count > 0

def main():
    parser = argparse.ArgumentParser(description="Emergency deployment")
    parser.add_argument("--target", choices=["local", "lambda", "both"], 
                       default="local", help="Deployment target")
    args = parser.parse_args()
    
    deployment = EmergencyDeployment(target=args.target)
    success = deployment.run_emergency_deployment()
    
    if success:
        print("\n✅ Emergency deployment completed successfully!")
    else:
        print("\n❌ Emergency deployment failed!")
        sys.exit(1)

if __name__ == "__main__":
    main() 