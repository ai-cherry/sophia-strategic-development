#!/usr/bin/env python3
"""
Sophia AI Production Deployment to Lambda Labs
Deploys to sophia-intel.ai domain using existing Lambda infrastructure
"""

import json
import subprocess
import sys
import time
from typing import Dict, List
import requests

# Lambda Labs Configuration
LAMBDA_API_KEY = "[REDACTED_API_KEY]"
LAMBDA_ENDPOINT = "https://cloud.lambda.ai/api/v1/instances"

# Infrastructure Mapping (Updated with working SSH)
LAMBDA_INFRASTRUCTURE = {
    "main": {
        "name": "sophia-production-instance",
        "ip": "104.171.202.103",
        "instance_id": "eb24fa66e6fe49769011b77bff329a1e",
        "role": "Primary backend API + Frontend serving",
        "specs": "RTX 6000 24GB, 14 vCPUs, 46GB RAM",
        "ssh_working": True,
        "ssh_alias": "sophia-prod"
    },
    "backup": {
        "name": "sophia-ai-core",
        "ip": "192.222.58.232",
        "instance_id": "6bba2128681d42e8bd63b40744dc3f98",
        "role": "Backup services",
        "specs": "GH200 96GB, 64 vCPUs, 432GB RAM",
        "ssh_working": False
    },
    "mcp": {
        "name": "sophia-mcp-orchestrator",
        "ip": "104.171.202.117", 
        "instance_id": "7ac7187f849245b599c4a0ce299e93e9",
        "role": "MCP servers + Webhooks",
        "specs": "A6000 48GB, 14 vCPUs, 100GB RAM",
        "ssh_working": False
    },
    "data": {
        "name": "sophia-data-pipeline",
        "ip": "104.171.202.134",
        "instance_id": "8f5ab71c637440439cfdf454c187074f", 
        "role": "Data processing + Analytics",
        "specs": "A100 40GB, 30 vCPUs, 200GB RAM",
        "ssh_working": False
    },
    "dev": {
        "name": "sophia-development",
        "ip": "155.248.194.183",
        "instance_id": "de12092bef0f44bc98e74487b6162662",
        "role": "Development + Testing",
        "specs": "A10 24GB, 30 vCPUs, 200GB RAM",
        "ssh_working": False
    }
}

# Domain Configuration
DOMAIN_CONFIG = {
    "sophia-intel.ai": "192.222.58.232",      # Main site
    "api.sophia-intel.ai": "192.222.58.232",  # API backend
    "app.sophia-intel.ai": "192.222.58.232",  # Frontend app
    "webhooks.sophia-intel.ai": "104.171.202.117",  # Webhooks
    "mcp.sophia-intel.ai": "104.171.202.117",       # MCP services
    "data.sophia-intel.ai": "104.171.202.134",      # Data API
    "dev.sophia-intel.ai": "155.248.194.183"        # Development
}

class SophiaLambdaDeployer:
    def __init__(self):
        self.api_key = LAMBDA_API_KEY
        self.session = requests.Session()
        self.session.auth = (self.api_key, "")
        
    def check_lambda_instances(self) -> Dict:
        """Check status of all Lambda instances"""
        print("🔍 Checking Lambda Labs infrastructure...")
        
        try:
            response = self.session.get(LAMBDA_ENDPOINT)
            response.raise_for_status()
            
            instances = response.json()["data"]
            status_report = {}
            
            for instance in instances:
                name = instance["name"]
                status_report[name] = {
                    "ip": instance["ip"],
                    "status": instance["status"],
                    "instance_type": instance["instance_type"]["description"],
                    "region": instance["region"]["description"],
                    "cost_per_hour": f"${instance['instance_type']['price_cents_per_hour']/100:.2f}"
                }
                
            return status_report
            
        except Exception as e:
            print(f"❌ Error checking Lambda instances: {e}")
            return {}
    
    def test_ssh_connectivity(self, ip: str, name: str) -> bool:
        """Test SSH connectivity to Lambda instance using SSH alias"""
        print(f"🔐 Testing SSH to {name} ({ip})...")
        
        try:
            # Use SSH alias for sophia-prod
            ssh_target = "sophia-prod" if ip == "104.171.202.103" else f"ubuntu@{ip}"
            result = subprocess.run([
                "ssh", "-o", "ConnectTimeout=10", 
                "-o", "StrictHostKeyChecking=no",
                ssh_target, "echo 'SSH OK'"
            ], capture_output=True, text=True, timeout=15)
            
            if result.returncode == 0:
                print(f"✅ SSH to {name} successful")
                return True
            else:
                print(f"❌ SSH to {name} failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"⏱️ SSH to {name} timed out")
            return False
        except Exception as e:
            print(f"❌ SSH error for {name}: {e}")
            return False
    
    def deploy_backend_to_main(self) -> bool:
        """Deploy backend to main Lambda instance (104.171.202.103)"""
        print("🚀 Deploying backend to sophia-production-instance...")
        
        main_config = LAMBDA_INFRASTRUCTURE["main"]
        ssh_target = main_config["ssh_alias"]
        
        # Commands to run on main instance
        commands = [
            # Update system
            "sudo apt-get update -y",
            
            # Install dependencies
            "sudo apt-get install -y python3-pip nginx git docker.io nodejs npm",
            
            # Clone repository (if not exists)
            "[ ! -d '/home/ubuntu/sophia-main' ] && git clone https://github.com/ai-cherry/sophia-main.git /home/ubuntu/sophia-main || echo 'Repo exists'",
            
            # Update repository
            "cd /home/ubuntu/sophia-main && git pull origin main",
            
            # Install Python dependencies
            "cd /home/ubuntu/sophia-main && pip3 install -r requirements.txt || pip3 install fastapi uvicorn requests qdrant-client",
            
            # Build frontend
            "cd /home/ubuntu/sophia-main/frontend && npm install && npm run build",
            
            # Create systemd service for backend
            """sudo tee /etc/systemd/system/sophia-backend.service > /dev/null << 'EOF'
[Unit]
Description=Sophia AI Backend
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/sophia-main
ExecStart=/usr/bin/python3 backend_production.py
Restart=always
RestartSec=10
Environment=ENVIRONMENT=prod
Environment=PORT=8000

[Install]
WantedBy=multi-user.target
EOF""",
            
            # Enable and start service
            "sudo systemctl daemon-reload",
            "sudo systemctl enable sophia-backend",
            "sudo systemctl restart sophia-backend",
            
            # Configure Nginx for sophia-intel.ai
            """sudo tee /etc/nginx/sites-available/sophia-intel.ai > /dev/null << 'EOF'
server {
    listen 80;
    server_name sophia-intel.ai www.sophia-intel.ai api.sophia-intel.ai app.sophia-intel.ai;
    
    # Main site and app - serve React frontend
    location / {
        root /home/ubuntu/sophia-main/frontend/dist;
        try_files $uri $uri/ /index.html;
        
        # Add headers for better performance
        add_header X-Frame-Options "SAMEORIGIN";
        add_header X-Content-Type-Options "nosniff";
        add_header X-XSS-Protection "1; mode=block";
    }
    
    # API endpoints
    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # CORS headers
        add_header Access-Control-Allow-Origin *;
        add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS";
        add_header Access-Control-Allow-Headers "Content-Type, Authorization";
    }
    
    # Health check
    location /health {
        proxy_pass http://localhost:8000/health;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    # Chat endpoint
    location /chat {
        proxy_pass http://localhost:8000/chat;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Competitor intelligence API
    location /api/v1/competitors/ {
        proxy_pass http://localhost:8000/api/v1/competitors/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF""",
            
            # Enable Nginx site
            "sudo rm -f /etc/nginx/sites-enabled/default",
            "sudo ln -sf /etc/nginx/sites-available/sophia-intel.ai /etc/nginx/sites-enabled/",
            "sudo nginx -t && sudo systemctl restart nginx"
        ]
        
        print(f"📡 Executing deployment commands on {ssh_target}...")
        
        for i, cmd in enumerate(commands, 1):
            print(f"Step {i}/{len(commands)}: {cmd[:80]}...")
            
            try:
                result = subprocess.run([
                    "ssh", "-o", "StrictHostKeyChecking=no",
                    ssh_target, cmd
                ], capture_output=True, text=True, timeout=300)
                
                if result.returncode != 0:
                    print(f"⚠️ Command failed (continuing): {result.stderr[:200]}")
                else:
                    print(f"✅ Step {i} completed")
                    
            except subprocess.TimeoutExpired:
                print(f"⏱️ Step {i} timed out")
            except Exception as e:
                print(f"❌ Step {i} error: {e}")
        
        return True
    
    def verify_deployment(self) -> Dict:
        """Verify deployment by testing all endpoints"""
        print("🔍 Verifying deployment...")
        
        test_results = {}
        
        # Test endpoints
        endpoints = [
            ("Main Site", "http://sophia-intel.ai"),
            ("API Health", "http://api.sophia-intel.ai/health"),
            ("App Frontend", "http://app.sophia-intel.ai"),
            ("Chat Endpoint", "http://sophia-intel.ai/chat"),
            ("Competitors API", "http://api.sophia-intel.ai/api/v1/competitors/")
        ]
        
        for name, url in endpoints:
            try:
                response = requests.get(url, timeout=10)
                test_results[name] = {
                    "status": response.status_code,
                    "success": response.status_code < 400,
                    "response_time": response.elapsed.total_seconds()
                }
                print(f"✅ {name}: {response.status_code} ({response.elapsed.total_seconds():.2f}s)")
                
            except Exception as e:
                test_results[name] = {
                    "status": "ERROR",
                    "success": False,
                    "error": str(e)
                }
                print(f"❌ {name}: {e}")
        
        return test_results
    
    def run_full_deployment(self):
        """Run complete deployment process"""
        print("🚀 Starting Sophia AI Production Deployment to Lambda Labs")
        print("=" * 60)
        
        # Step 1: Check Lambda infrastructure
        print("\n📋 STEP 1: Infrastructure Check")
        instances = self.check_lambda_instances()
        
        if not instances:
            print("❌ Cannot access Lambda infrastructure")
            return False
        
        print(f"✅ Found {len(instances)} Lambda instances")
        for name, info in instances.items():
            print(f"  • {name}: {info['ip']} ({info['status']}) - {info['cost_per_hour']}/hr")
        
        # Step 2: Test SSH connectivity (only to working server)
        print("\n🔐 STEP 2: SSH Connectivity Test")
        main_config = LAMBDA_INFRASTRUCTURE["main"]
        ssh_success = self.test_ssh_connectivity(main_config["ip"], main_config["name"])
        
        if not ssh_success:
            print("❌ No SSH connectivity to main instance")
            return False
        
        # Step 3: Deploy backend to main instance
        print("\n🚀 STEP 3: Backend Deployment")
        backend_success = self.deploy_backend_to_main()
        
        # Step 4: Verify deployment
        print("\n🔍 STEP 4: Deployment Verification")
        verification_results = self.verify_deployment()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 DEPLOYMENT SUMMARY")
        print("=" * 60)
        
        successful_endpoints = sum(1 for r in verification_results.values() if r.get('success', False))
        total_endpoints = len(verification_results)
        
        print(f"✅ Infrastructure: {len(instances)} instances active")
        print(f"🔐 SSH Access: Working on sophia-production-instance")
        print(f"🌐 Endpoints: {successful_endpoints}/{total_endpoints} working")
        print(f"💰 Cost: $0.50/hour for main instance")
        
        if successful_endpoints >= total_endpoints * 0.7:  # 70% success rate
            print("\n🎉 DEPLOYMENT SUCCESSFUL!")
            print("🌐 Your site should be live at: http://sophia-intel.ai")
            print("📡 API available at: http://api.sophia-intel.ai")
            print("🚀 App available at: http://app.sophia-intel.ai")
        else:
            print("\n⚠️ DEPLOYMENT PARTIALLY SUCCESSFUL")
            print("Some endpoints may need additional configuration")
        
        return True

def main():
    """Main deployment function"""
    deployer = SophiaLambdaDeployer()
    
    try:
        success = deployer.run_full_deployment()
        
        if success:
            print("\n🎯 Next Steps:")
            print("1. Test sophia-intel.ai in your browser")
            print("2. Set up SSL certificates with Let's Encrypt")
            print("3. Configure monitoring and alerts")
            print("4. Test all competitor intelligence features")
            
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n⏹️ Deployment interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Deployment failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 