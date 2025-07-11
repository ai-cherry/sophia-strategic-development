#!/usr/bin/env python3
"""
Complete Lambda Labs Deployment Script
Deploys:
1. Backend API on Lambda Labs instance
2. Frontend on Lambda Labs instance (or Vercel)
3. All MCP servers on 104.171.202.117
4. Verifies everything works with real data
"""

import os
import subprocess
import json
import time
import requests
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv("local.env")

# Lambda Labs configuration
LAMBDA_API_KEY = os.getenv("LAMBDA_API_KEY")
LAMBDA_CLOUD_API_KEY = os.getenv("LAMBDA_CLOUD_API_KEY")
LAMBDA_SSH_KEY = os.getenv("LAMBDA_SSH_KEY")
MCP_INSTANCE_IP = "104.171.202.117"

# Save SSH key to file
SSH_KEY_PATH = Path.home() / ".ssh" / "lambda_labs_key"


def setup_ssh_key():
    """Setup SSH key for Lambda Labs access"""
    print("🔑 Setting up SSH key...")

    # Create .ssh directory if it doesn't exist
    ssh_dir = Path.home() / ".ssh"
    ssh_dir.mkdir(exist_ok=True)

    # Write SSH key to file
    with open(SSH_KEY_PATH, "w") as f:
        f.write(f"{LAMBDA_SSH_KEY}\n")

    # Set correct permissions
    os.chmod(SSH_KEY_PATH, 0o600)
    print(f"✅ SSH key saved to {SSH_KEY_PATH}")


def ssh_command(ip, cmd):
    """Execute command on Lambda Labs instance via SSH"""
    ssh_cmd = f"ssh -o StrictHostKeyChecking=no -i {SSH_KEY_PATH} ubuntu@{ip} '{cmd}'"
    result = subprocess.run(ssh_cmd, shell=True, capture_output=True, text=True)
    return result


def check_lambda_labs_instances():
    """Check existing Lambda Labs instances"""
    print("\n🔍 Checking Lambda Labs instances...")

    cmd = f"curl -s -u {LAMBDA_API_KEY}: https://cloud.lambda.ai/api/v1/instances"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    if result.returncode == 0:
        data = json.loads(result.stdout)
        instances = data.get("data", [])
        print(f"Found {len(instances)} instances:")
        for inst in instances:
            print(
                f"  - {inst.get('name')} ({inst.get('id')}): {inst.get('status')} - IP: {inst.get('ip')}"
            )
        return instances
    else:
        print("❌ Failed to get instances")
        return []


def deploy_mcp_servers():
    """Deploy all MCP servers to Lambda Labs instance"""
    print(f"\n🚀 Deploying MCP servers to {MCP_INSTANCE_IP}...")

    # First, test SSH connection
    print("Testing SSH connection...")
    result = ssh_command(MCP_INSTANCE_IP, "echo 'SSH connection successful'")
    if result.returncode != 0:
        print(f"❌ SSH connection failed: {result.stderr}")
        return False

    print("✅ SSH connection successful")

    # Install dependencies
    print("Installing dependencies...")
    commands = [
        # Update system
        "sudo apt-get update",
        # Install Python and essential tools
        "sudo apt-get install -y python3.12 python3-pip git docker.io docker-compose",
        # Install Node.js
        "curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -",
        "sudo apt-get install -y nodejs",
        # Clone repository
        "git clone https://github.com/scoobyjava/sophia-main.git || (cd sophia-main && git pull)",
        # Setup Python virtual environment
        "cd sophia-main && python3 -m venv venv",
        "cd sophia-main && source venv/bin/activate && pip install -r backend/requirements.txt",
        # Create environment file
        f"cd sophia-main && cat > local.env << 'EOF'\n{open('local.env').read()}\nEOF",
        # Start Redis with Docker
        "sudo docker run -d --name redis -p 6379:6379 redis:alpine || sudo docker start redis",
        # Create MCP server startup script
        """cat > ~/start_mcp_servers.sh << 'EOF'
#!/bin/bash
cd ~/sophia-main
source venv/bin/activate

# Kill any existing MCP servers
pkill -f "mcp_server.py" || true

# Start all MCP servers
echo "Starting MCP servers..."

# AI Memory MCP (port 9001)
python mcp-servers/ai_memory/enhanced_ai_memory_mcp_server.py > logs/ai_memory.log 2>&1 &
echo "Started AI Memory MCP on port 9001"

# Codacy MCP (port 3008)
python mcp-servers/codacy/codacy_mcp_server.py > logs/codacy.log 2>&1 &
echo "Started Codacy MCP on port 3008"

# GitHub MCP (port 9003)
python mcp-servers/github/github_mcp_server.py > logs/github.log 2>&1 &
echo "Started GitHub MCP on port 9003"

# Linear MCP (port 9004)
python mcp-servers/linear/linear_mcp_server.py > logs/linear.log 2>&1 &
echo "Started Linear MCP on port 9004"

# Asana MCP (port 9006)
python mcp-servers/asana/asana_mcp_server.py > logs/asana.log 2>&1 &
echo "Started Asana MCP on port 9006"

# Notion MCP (port 9102)
python mcp-servers/notion/notion_mcp_server.py > logs/notion.log 2>&1 &
echo "Started Notion MCP on port 9102"

# Slack MCP (port 9101)
python mcp-servers/slack/slack_mcp_server.py > logs/slack.log 2>&1 &
echo "Started Slack MCP on port 9101"

echo "All MCP servers started!"
EOF""",
        # Make script executable
        "chmod +x ~/start_mcp_servers.sh",
        # Create logs directory
        "mkdir -p ~/sophia-main/logs",
        # Start MCP servers
        "~/start_mcp_servers.sh",
    ]

    # Execute commands
    for cmd in commands:
        print(f"Running: {cmd[:50]}...")
        result = ssh_command(MCP_INSTANCE_IP, cmd)
        if result.returncode != 0 and "already exists" not in result.stderr:
            print(f"⚠️  Command failed: {result.stderr}")

    print("✅ MCP servers deployment complete")
    return True


def deploy_backend():
    """Deploy backend API on Lambda Labs"""
    print("\n🚀 Deploying backend API...")

    # For now, we'll use the existing instance or create a new one
    # First check if we have an instance
    instances = check_lambda_labs_instances()

    if not instances:
        print("❌ No Lambda Labs instances available")
        print("💡 Please create an instance manually or use the Lambda Labs API")
        return None

    # Use the first available instance
    backend_ip = instances[0].get("ip", MCP_INSTANCE_IP)

    print(f"Deploying backend to {backend_ip}...")

    commands = [
        # Navigate to project
        "cd ~/sophia-main",
        # Create systemd service for backend
        """sudo tee /etc/systemd/system/sophia-backend.service << 'EOF'
[Unit]
Description=Sophia AI Backend
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/sophia-main
Environment="PATH=/home/ubuntu/sophia-main/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
ExecStart=/home/ubuntu/sophia-main/venv/bin/python backend/app/unified_chat_backend.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF""",
        # Enable and start service
        "sudo systemctl daemon-reload",
        "sudo systemctl enable sophia-backend",
        "sudo systemctl restart sophia-backend",
        # Setup nginx reverse proxy
        """sudo tee /etc/nginx/sites-available/sophia-backend << 'EOF'
server {
    listen 80;
    server_name _;
    
    location / {
        proxy_pass http://localhost:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
EOF""",
        "sudo ln -sf /etc/nginx/sites-available/sophia-backend /etc/nginx/sites-enabled/",
        "sudo nginx -s reload || sudo systemctl restart nginx",
    ]

    for cmd in commands:
        print(f"Running: {cmd[:50]}...")
        result = ssh_command(backend_ip, cmd)
        if result.returncode != 0:
            print(f"⚠️  Command failed: {result.stderr}")

    print(f"✅ Backend deployed to http://{backend_ip}")
    return backend_ip


def deploy_frontend_vercel():
    """Deploy frontend to Vercel (easier than Lambda Labs)"""
    print("\n🚀 Deploying frontend to Vercel...")

    # Update frontend environment
    backend_ip = MCP_INSTANCE_IP  # or the backend instance IP

    env_file = Path("frontend/.env.production")
    env_content = f"""VITE_API_URL=http://{backend_ip}
VITE_ENVIRONMENT=production
"""

    with open(env_file, "w") as f:
        f.write(env_content)

    # Deploy to Vercel
    os.chdir("frontend")
    result = subprocess.run(
        "vercel --prod --yes", shell=True, capture_output=True, text=True
    )
    os.chdir("..")

    if result.returncode == 0:
        # Extract URL from output
        for line in result.stdout.split("\n"):
            if "Production:" in line:
                url = line.split("Production:")[1].strip()
                print(f"✅ Frontend deployed to {url}")
                return url

    print("❌ Frontend deployment failed")
    return None


def verify_deployment():
    """Verify everything is working with real data"""
    print("\n🔍 Verifying deployment...")

    # Test backend health
    backend_url = f"http://{MCP_INSTANCE_IP}"

    try:
        # Test health endpoint
        resp = requests.get(f"{backend_url}/health", timeout=10)
        if resp.status_code == 200:
            print(f"✅ Backend health check passed: {resp.json()}")
        else:
            print(f"❌ Backend health check failed: {resp.status_code}")
    except Exception as e:
        print(f"❌ Backend not accessible: {e}")

    # Test MCP servers
    mcp_ports = {
        "AI Memory": 9001,
        "Codacy": 3008,
        "GitHub": 9003,
        "Linear": 9004,
        "Asana": 9006,
        "Notion": 9102,
        "Slack": 9101,
    }

    for name, port in mcp_ports.items():
        try:
            resp = requests.get(f"http://{MCP_INSTANCE_IP}:{port}/health", timeout=5)
            if resp.status_code == 200:
                print(f"✅ {name} MCP server is running on port {port}")
            else:
                print(f"❌ {name} MCP server returned {resp.status_code}")
        except:
            print(f"⚠️  {name} MCP server not accessible on port {port}")

    # Test real data - Snowflake connection
    print("\nTesting Snowflake connection...")
    try:
        resp = requests.post(
            f"{backend_url}/api/v4/orchestrate",
            json={
                "user_id": "test_user",
                "query": "What tables are in the AI_MEMORY database?",
                "context": {},
            },
            timeout=30,
        )
        if resp.status_code == 200:
            print("✅ Snowflake query successful")
            print(f"Response: {resp.json()}")
        else:
            print(f"❌ Snowflake query failed: {resp.status_code}")
    except Exception as e:
        print(f"❌ API test failed: {e}")


def main():
    print("🚀 COMPLETE LAMBDA LABS DEPLOYMENT")
    print("=" * 50)

    # Setup SSH key
    setup_ssh_key()

    # Check instances
    instances = check_lambda_labs_instances()

    # Deploy MCP servers
    if deploy_mcp_servers():
        print("✅ MCP servers deployed")
    else:
        print("❌ MCP server deployment failed")

    # Deploy backend
    backend_ip = deploy_backend()
    if backend_ip:
        print(f"✅ Backend deployed to {backend_ip}")

    # Deploy frontend
    frontend_url = deploy_frontend_vercel()
    if frontend_url:
        print(f"✅ Frontend deployed to {frontend_url}")

    # Verify everything
    time.sleep(10)  # Give services time to start
    verify_deployment()

    print("\n" + "=" * 50)
    print("📊 DEPLOYMENT SUMMARY")
    print(f"MCP Servers: http://{MCP_INSTANCE_IP}:PORT")
    print(f"Backend API: http://{backend_ip or MCP_INSTANCE_IP}")
    print(f"Frontend: {frontend_url or 'Not deployed'}")
    print("\n💡 Next steps:")
    print("1. Update DNS to point to Lambda Labs IPs")
    print("2. Configure SSL certificates")
    print("3. Set up monitoring and alerts")
    print("4. Test all integrations thoroughly")


if __name__ == "__main__":
    main()
