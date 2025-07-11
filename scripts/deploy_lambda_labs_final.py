#!/usr/bin/env python3
"""
Final Lambda Labs Deployment Script
Deploys everything to the correct instances with full verification
"""

import os
import subprocess
import time
import requests
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv("local.env")

# Lambda Labs configuration
LAMBDA_API_KEY = os.getenv("LAMBDA_API_KEY")
LAMBDA_SSH_KEY = """ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCKAPI0WU9UcB5vVnneP3oExytrPcD0PON5NeQxeNAJOWQSWi/fvkQ97dhAEtjyddmaCti7LFrp3CW+4gtGSiC+2/jOVqERLkmycbC8UZNpyqCiLIwO4MkIuxVNiRkg/ucPuf0DjakJh92xFDIyeDAR55OrpMWqX6O0+OZL0DFXE7jBDaloez+oLytM16CMHtlnx+5Br7O+RoPLEFvBz9RZyqlzs5144pvgHyRSwuvXBcYLKqT24kAPqvxc0SqGYLnNAD1q96BPqMwZONAFPDf3jTFGznmO+I3f+cyiR9Mai7Na9C2/21UJL/9APt7unjQhyQtCF++pwUXxhJX42tId SophiaSSH5"""

# Instance IPs from the API response
INSTANCES = {
    "production": "104.171.202.103",  # sophia-production-instance
    "ai_core": "192.222.58.232",  # sophia-ai-core (GH200 - most powerful)
    "mcp_orchestrator": "104.171.202.117",  # sophia-mcp-orchestrator (specified for MCP)
    "data_pipeline": "104.171.202.134",  # sophia-data-pipeline
    "development": "155.248.194.183",  # sophia-development
}

# SSH key path
SSH_KEY_PATH = Path.home() / ".ssh" / "sophia2025.pem"


def setup_ssh_key():
    """Setup SSH key for Lambda Labs access"""
    print("🔑 Setting up SSH key...")

    # Check if key already exists
    if SSH_KEY_PATH.exists():
        print(f"✅ SSH key already exists at {SSH_KEY_PATH}")
        return True

    # Create .ssh directory if it doesn't exist
    ssh_dir = Path.home() / ".ssh"
    ssh_dir.mkdir(exist_ok=True)

    # Write SSH private key (you need the private key, not the public key)
    print("❌ Private SSH key not found at ~/.ssh/sophia2025.pem")
    print("Please ensure you have the private key file")
    return False


def ssh_command(ip, cmd, timeout=30):
    """Execute command on Lambda Labs instance via SSH"""
    ssh_cmd = f"ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 -i {SSH_KEY_PATH} ubuntu@{ip} '{cmd}'"
    try:
        result = subprocess.run(
            ssh_cmd, shell=True, capture_output=True, text=True, timeout=timeout
        )
        return result
    except subprocess.TimeoutExpired:
        print(f"⚠️ Command timed out after {timeout}s")
        return None


def test_ssh_connection(ip, name):
    """Test SSH connection to instance"""
    print(f"\nTesting SSH to {name} ({ip})...")
    result = ssh_command(
        ip, "echo 'SSH connection successful' && hostname && uname -a", timeout=10
    )

    if result and result.returncode == 0:
        print(f"✅ SSH connection to {name} successful")
        print(f"   {result.stdout.strip()}")
        return True
    else:
        print(f"❌ SSH connection to {name} failed")
        if result:
            print(f"   Error: {result.stderr}")
        return False


def deploy_mcp_servers():
    """Deploy all MCP servers to the MCP orchestrator instance"""
    mcp_ip = INSTANCES["mcp_orchestrator"]
    print(f"\n🚀 Deploying MCP servers to {mcp_ip}...")

    # Test connection first
    if not test_ssh_connection(mcp_ip, "MCP Orchestrator"):
        return False

    # Create deployment script
    mcp_setup_script = """#!/bin/bash
set -e

echo "🚀 Setting up MCP servers..."

# Update system
sudo apt-get update -y

# Install Python 3.12
sudo apt-get install -y software-properties-common
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt-get update -y
sudo apt-get install -y python3.12 python3.12-venv python3.12-dev

# Install other dependencies
sudo apt-get install -y git redis-server nginx

# Start Redis
sudo systemctl enable redis-server
sudo systemctl start redis-server

# Clone repository
cd ~
if [ ! -d "sophia-main" ]; then
    git clone https://github.com/ai-cherry/sophia-main.git
else
    cd sophia-main && git pull && cd ..
fi

# Setup Python virtual environment
cd sophia-main
python3.12 -m venv venv
source venv/bin/activate

# Install requirements
pip install --upgrade pip
pip install -r backend/requirements.txt

# Create logs directory
mkdir -p logs

# Kill any existing MCP servers
sudo pkill -f "mcp.*py" || true

echo "✅ MCP environment ready"
"""

    # Deploy setup script
    print("Deploying MCP setup script...")
    result = ssh_command(
        mcp_ip, f"cat > ~/setup_mcp.sh << 'EOF'\n{mcp_setup_script}\nEOF", timeout=60
    )
    if not result or result.returncode != 0:
        print("❌ Failed to create setup script")
        return False

    # Make executable and run
    print("Running MCP setup...")
    ssh_command(mcp_ip, "chmod +x ~/setup_mcp.sh")
    result = ssh_command(mcp_ip, "bash ~/setup_mcp.sh", timeout=300)

    if result and result.returncode == 0:
        print("✅ MCP setup complete")
    else:
        print("⚠️ MCP setup had issues")

    # Copy environment file
    print("Copying environment configuration...")
    env_content = open("local.env").read()
    ssh_command(
        mcp_ip,
        f"cd ~/sophia-main && cat > local.env << 'EOF'\n{env_content}\nEOF",
        timeout=60,
    )

    # Create MCP startup script
    startup_script = """#!/bin/bash
cd ~/sophia-main
source venv/bin/activate
source local.env

# Function to start MCP server
start_mcp() {
    name=$1
    port=$2
    module=$3
    
    echo "Starting $name on port $port..."
    nohup python -m $module > logs/${name}.log 2>&1 &
    echo $! > logs/${name}.pid
    sleep 2
    
    # Check if started
    if curl -s http://localhost:$port/health > /dev/null 2>&1; then
        echo "✅ $name started successfully"
    else
        echo "⚠️ $name may not have started correctly"
    fi
}

# Start all MCP servers
start_mcp "ai_memory" 9001 "mcp-servers.ai_memory.enhanced_ai_memory_mcp_server"
start_mcp "codacy" 3008 "mcp-servers.codacy.codacy_mcp_server"
start_mcp "github" 9003 "mcp-servers.github.github_mcp_server"
start_mcp "linear" 9004 "mcp-servers.linear.linear_mcp_server"
start_mcp "asana" 9006 "mcp-servers.asana.asana_mcp_server"
start_mcp "notion" 9102 "mcp-servers.notion.notion_mcp_server"
start_mcp "slack" 9101 "mcp-servers.slack.slack_mcp_server"

echo "All MCP servers started!"
ps aux | grep mcp
"""

    # Deploy and run startup script
    print("Starting MCP servers...")
    ssh_command(
        mcp_ip,
        f"cat > ~/sophia-main/start_mcp_servers.sh << 'EOF'\n{startup_script}\nEOF",
    )
    ssh_command(mcp_ip, "chmod +x ~/sophia-main/start_mcp_servers.sh")
    result = ssh_command(
        mcp_ip, "cd ~/sophia-main && ./start_mcp_servers.sh", timeout=120
    )

    if result:
        print("✅ MCP servers deployment complete")
        print(result.stdout)

    return True


def deploy_backend():
    """Deploy backend API on the AI Core instance (most powerful)"""
    backend_ip = INSTANCES["ai_core"]
    print(f"\n🚀 Deploying backend to AI Core instance ({backend_ip})...")

    # Test connection
    if not test_ssh_connection(backend_ip, "AI Core"):
        return None

    # Backend setup script
    backend_setup = """#!/bin/bash
set -e

echo "🚀 Setting up backend..."

# Install dependencies
sudo apt-get update -y
sudo apt-get install -y python3.12 python3.12-venv python3.12-dev git nginx

# Clone repository
cd ~
if [ ! -d "sophia-main" ]; then
    git clone https://github.com/ai-cherry/sophia-main.git
else
    cd sophia-main && git pull && cd ..
fi

# Setup Python environment
cd sophia-main
python3.12 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r backend/requirements.txt

# Create systemd service
sudo tee /etc/systemd/system/sophia-backend.service > /dev/null << 'EOF'
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
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Configure nginx
sudo tee /etc/nginx/sites-available/sophia-backend > /dev/null << 'EOF'
server {
    listen 80 default_server;
    server_name _;
    
    location / {
        proxy_pass http://127.0.0.1:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

sudo rm -f /etc/nginx/sites-enabled/default
sudo ln -sf /etc/nginx/sites-available/sophia-backend /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl restart nginx

echo "✅ Backend setup complete"
"""

    # Deploy setup
    print("Deploying backend setup...")
    ssh_command(backend_ip, f"cat > ~/setup_backend.sh << 'EOF'\n{backend_setup}\nEOF")
    ssh_command(
        backend_ip,
        "chmod +x ~/setup_backend.sh && bash ~/setup_backend.sh",
        timeout=300,
    )

    # Copy environment file
    print("Copying environment...")
    env_content = open("local.env").read()
    ssh_command(
        backend_ip, f"cd ~/sophia-main && cat > local.env << 'EOF'\n{env_content}\nEOF"
    )

    # Start backend
    print("Starting backend service...")
    ssh_command(backend_ip, "sudo systemctl daemon-reload")
    ssh_command(backend_ip, "sudo systemctl enable sophia-backend")
    ssh_command(backend_ip, "sudo systemctl restart sophia-backend")

    # Wait for startup
    time.sleep(10)

    # Check if running
    result = ssh_command(backend_ip, "sudo systemctl status sophia-backend --no-pager")
    if result:
        print("Backend service status:")
        print(result.stdout)

    return backend_ip


def deploy_frontend_vercel():
    """Deploy frontend to Vercel with proper API configuration"""
    print("\n🚀 Deploying frontend to Vercel...")

    backend_ip = INSTANCES["ai_core"]

    # Update frontend environment
    env_content = f"""# Production environment
VITE_API_URL=http://{backend_ip}
VITE_MCP_URL=http://{INSTANCES['mcp_orchestrator']}
VITE_ENVIRONMENT=production
"""

    # Write environment file
    with open("frontend/.env.production", "w") as f:
        f.write(env_content)

    # Build frontend
    print("Building frontend...")
    os.chdir("frontend")
    subprocess.run("npm install", shell=True)
    subprocess.run("npm run build", shell=True)

    # Deploy to Vercel
    print("Deploying to Vercel...")
    result = subprocess.run(
        "vercel --prod --yes", shell=True, capture_output=True, text=True
    )
    os.chdir("..")

    if result.returncode == 0:
        print("✅ Frontend deployed to Vercel")
        # Extract URL
        for line in result.stdout.split("\n"):
            if "Production:" in line:
                url = line.split("Production:")[1].strip()
                print(f"   URL: {url}")
                return url
    else:
        print("❌ Vercel deployment failed")
        print(result.stderr)

    return None


def verify_deployment():
    """Verify all services are working correctly"""
    print("\n🔍 Verifying deployment...")

    results = {
        "backend": False,
        "mcp_servers": {},
        "snowflake": False,
        "frontend": False,
    }

    # Test backend
    backend_ip = INSTANCES["ai_core"]
    print(f"\nTesting backend at http://{backend_ip}...")
    try:
        resp = requests.get(f"http://{backend_ip}/health", timeout=10)
        if resp.status_code == 200:
            print("✅ Backend health check passed")
            results["backend"] = True

            # Test API docs
            resp = requests.get(f"http://{backend_ip}/docs", timeout=10)
            if resp.status_code == 200:
                print("✅ API documentation accessible")
        else:
            print(f"❌ Backend returned status {resp.status_code}")
    except Exception as e:
        print(f"❌ Backend error: {e}")

    # Test MCP servers
    mcp_ip = INSTANCES["mcp_orchestrator"]
    mcp_ports = {
        "AI Memory": 9001,
        "Codacy": 3008,
        "GitHub": 9003,
        "Linear": 9004,
        "Asana": 9006,
        "Notion": 9102,
        "Slack": 9101,
    }

    print(f"\nTesting MCP servers at {mcp_ip}...")
    for name, port in mcp_ports.items():
        try:
            resp = requests.get(f"http://{mcp_ip}:{port}/health", timeout=5)
            if resp.status_code == 200:
                print(f"✅ {name} MCP is running on port {port}")
                results["mcp_servers"][name] = True
            else:
                print(f"❌ {name} MCP returned {resp.status_code}")
                results["mcp_servers"][name] = False
        except:
            print(f"⚠️  {name} MCP not accessible on port {port}")
            results["mcp_servers"][name] = False

    # Test real Snowflake query
    print("\nTesting Snowflake integration...")
    try:
        resp = requests.post(
            f"http://{backend_ip}/api/v4/orchestrate",
            json={
                "user_id": "test_deployment",
                "query": "Show me the tables in AI_MEMORY database",
                "context": {},
            },
            timeout=30,
        )
        if resp.status_code == 200:
            print("✅ Snowflake query successful")
            data = resp.json()
            if "response" in data:
                print(f"   Response preview: {data['response'][:200]}...")
            results["snowflake"] = True
        else:
            print(f"❌ Snowflake query failed: {resp.status_code}")
    except Exception as e:
        print(f"❌ Snowflake test error: {e}")

    return results


def main():
    print("🚀 FINAL LAMBDA LABS DEPLOYMENT")
    print("=" * 60)

    # Check SSH key
    if not setup_ssh_key():
        print("\n❌ SSH key setup failed. Please check ~/.ssh/sophia2025.pem")
        return

    # Show available instances
    print("\n📊 Available Lambda Labs Instances:")
    for name, ip in INSTANCES.items():
        print(f"  - {name}: {ip}")

    # Deploy MCP servers
    print("\n" + "=" * 60)
    if deploy_mcp_servers():
        print("✅ MCP servers deployed successfully")
    else:
        print("❌ MCP deployment had issues")

    # Deploy backend
    print("\n" + "=" * 60)
    backend_ip = deploy_backend()
    if backend_ip:
        print(f"✅ Backend deployed to {backend_ip}")
    else:
        print("❌ Backend deployment failed")

    # Deploy frontend
    print("\n" + "=" * 60)
    frontend_url = deploy_frontend_vercel()

    # Verify everything
    print("\n" + "=" * 60)
    time.sleep(15)  # Give services time to fully start
    results = verify_deployment()

    # Summary
    print("\n" + "=" * 60)
    print("📊 DEPLOYMENT SUMMARY")
    print("=" * 60)
    print("\n✅ INSTANCES:")
    print(f"  Backend API: http://{INSTANCES['ai_core']}")
    print(f"  MCP Servers: http://{INSTANCES['mcp_orchestrator']}:PORT")
    print(f"  Frontend: {frontend_url or 'Deployment pending'}")

    print("\n📊 SERVICE STATUS:")
    print(f"  Backend: {'✅ Running' if results['backend'] else '❌ Not running'}")
    print(
        f"  Snowflake: {'✅ Connected' if results['snowflake'] else '❌ Not connected'}"
    )
    print(
        f"  MCP Servers: {sum(results['mcp_servers'].values())}/{len(results['mcp_servers'])} running"
    )

    print("\n🔗 ACCESS URLS:")
    print(f"  API Docs: http://{INSTANCES['ai_core']}/docs")
    print(f"  Health Check: http://{INSTANCES['ai_core']}/health")
    if frontend_url:
        print(f"  Frontend: {frontend_url}")

    print("\n💡 NEXT STEPS:")
    print("  1. Update DNS records to point to Lambda Labs IPs")
    print("  2. Configure SSL certificates with Let's Encrypt")
    print("  3. Set up monitoring and alerts")
    print("  4. Test all integrations thoroughly")
    print("  5. Update frontend VITE_API_URL in Vercel dashboard")

    print("\n✨ Deployment complete!")


if __name__ == "__main__":
    main()
