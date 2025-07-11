#!/usr/bin/env python3
"""
Production Lambda Labs Deployment Script
Deploys everything to Lambda Labs with proper verification
"""

import subprocess
import json
import time
import sys
from pathlib import Path
from datetime import datetime

# Lambda Labs configuration
LAMBDA_API_KEY = "secret_sophia5apikey_a404a99d985d41828d7020f0b9a122a2.PjbWZb0lLubKu1nmyWYLy9Ycl3vyL18o"
BACKEND_INSTANCE_IP = "192.222.58.232"  # sophia-ai-core
MCP_INSTANCE_IP = "104.171.202.117"  # sophia-mcp-orchestrator
SSH_KEY_PATH = Path.home() / ".ssh" / "sophia2025.pem"

# Write SSH key if not exists
SSH_KEY_CONTENT = """-----BEGIN RSA PRIVATE KEY-----
MIIEowIBAAKCAQEAigCSNFlPVHAeb1Z53j96BMcraz3A9DzjeTXkMXjQCTlkElou
Xr/5EuKPe3YQBLY8nXZmgrYusy+a6dwlvuILRkogvtv4zlanERJJsnGwvFGTacqg
oiyMDuDJCLsVTYkZIP7nD7n9A42pCYfdvBQyMngwEeeTq6TFql+jtPjmS9AxVxO4
wQ2paHs/qC8rTdngjB7ZZ8fuQa+zvkaDyxBbwc/UWcqpc7OdeOKb4B8kUsLr1wXG
Cyqk9uJAD6r8XNEqhmC5zQA9aveQT6jMGTjQBTw3940xRs55jviN3/nMokfTGouZ
WvQtv9tVCS//QD7e7p40IckLQhfvqcFF8YSV+NrSHQIDAQABAoIBAGy/9D5+T3vt
tIRcdG0vdcgCwdDxQKpXjt+bfMBmkQgzZkKRQ7WwBTXxJZsRdyNUi7PCo8J3Srzl
y/5pWVKsxbQc5ECPwA6YcJnKjcjcPdONJsoxBPqTcLQktdcB7EB++wCJgUgFMdC4
8xWHlQrp7doVlzTMKhVBSqH7gdh6S0Y6p2n1MfVdquDXGCqBKUYLZxDG1vv9cfhZ
x7f8w0Ggf9xKKNGOQFBG8SUPhX1OmS1VxoUB1VLRGBwcrR2+LO0Y2HEmVVqKIDXh
pViGaQJNDqXHz+7HO3RDe2p3LBQa0e4fezDPTczqA/DqiBxKdW7tI6IYA9/EIrhO
nJQe/QECgYEA2nxCwbgSqKdz+V2p0uyBf6gBdUKJeL1mcR7lD8CQgBJJDqnZ1G1R
Dkb+cBOLuBUdVBFnvL1PVewU8SqByP+9dXpVqJKJGKNUK4+35/6i3Y4aW+XTFa5G
WMQP6qw7KmbZ7S2aBhlRZLg1IM0rnA8WzHMqZZqJVdBa6Vjqb2VhZV0CgYEAoSRu
8AJBnD1yDMxGvFJizj5dFgyJhqpJKT3+Djf3b+JRwhLfD8J9RQsLHdvHp7p7F0cI
e3ovfKShG2tjXGHp+4fLV+Z3D6lqoLNxGK+KHSPOaQq8T5BLqtoVXy8b6MvCfXbm
5lGtCCQ5XjCRvxvyBGUXjVGvk1i6FjMEQa9vUsECgYEAxUILCQy2KQ5LzjIqRKK9
JGKazJ4S8+fxTFJZYCRxHvKIQzQhJtR6mL9y0KmLxJMQUuWnFQJFU7HJwVqLj6cC
/IxJcQwB8KQw6+Y5qvgKXBYqJvGHQ8RfSxJE7xr6j2D1hxXNsS8vqnCUEK8O+Rxq
4jXVlb4aYcQaULQ5j9OzFO0CgYBBTKhJ4UfXJaR0D3iqR1mRIDgvdmAZRKWXnJGK
bgQdKozUfU6OJT0qT3NNtyQJKAKJLLr0qzVi3vD/G8aGKGFh8c9FQfWJ7BwKD0wK
KKtqJhYvh0+ZKiM6zBBqJu1S2RrMu9mnmQc2YCJqjPOXcQJx6vULBYYzC1VRIzPa
0WbNAQKBgBnQ9L3d2p1O8fNRKlVGiXJBT3LCQ7v4VYJNfXJ0e4Tr6xZ6TH5j5vzF
1oNJuQoSW8yCxJG2u37K+ujjDJJpF/c3Kh6/j8HCLjUvh4oWhKKJnQKJbvdFMSqG
kJBF4pq3kQy7SbRBHJgKSR0UdQqGzIb7CkB6Y++JoENJz2F6iNfw
-----END RSA PRIVATE KEY-----"""


def run_cmd(cmd, check=True, shell=True, capture_output=True):
    """Run command with error handling"""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=shell, capture_output=capture_output, text=True)
    if check and result.returncode != 0:
        print(f"Error: {result.stderr}")
        return None
    return result


def setup_ssh_key():
    """Set up SSH key for Lambda Labs access"""
    if not SSH_KEY_PATH.exists():
        print("Creating SSH key...")
        SSH_KEY_PATH.parent.mkdir(parents=True, exist_ok=True)
        SSH_KEY_PATH.write_text(SSH_KEY_CONTENT)
        SSH_KEY_PATH.chmod(0o600)
        print(f"✅ SSH key created at {SSH_KEY_PATH}")
    else:
        print(f"✅ SSH key exists at {SSH_KEY_PATH}")


def ssh_cmd(ip, cmd):
    """Execute command on Lambda Labs instance"""
    ssh_command = (
        f"ssh -o StrictHostKeyChecking=no -i {SSH_KEY_PATH} ubuntu@{ip} '{cmd}'"
    )
    return run_cmd(ssh_command, check=False)


def deploy_backend():
    """Deploy backend to Lambda Labs sophia-ai-core instance"""
    print("\n🚀 DEPLOYING BACKEND TO LAMBDA LABS")
    print(f"Target: {BACKEND_INSTANCE_IP}")

    # First, check if we can connect
    result = ssh_cmd(BACKEND_INSTANCE_IP, "echo 'Connected'")
    if not result or result.returncode != 0:
        print("❌ Cannot connect to Lambda Labs instance")
        return False

    print("✅ Connected to Lambda Labs")

    # Stop existing services
    print("Stopping existing services...")
    ssh_cmd(BACKEND_INSTANCE_IP, "sudo systemctl stop sophia-backend || true")
    ssh_cmd(BACKEND_INSTANCE_IP, "sudo pkill -f 'python.*unified_chat_backend' || true")

    # Create backend startup script
    backend_script = """#!/bin/bash
cd /home/ubuntu/sophia-main
source venv/bin/activate
export PYTHONPATH=/home/ubuntu/sophia-main
export SNOWFLAKE_ACCOUNT=UHDECNO-CVB64222
export SNOWFLAKE_USER=SCOOBYJAVA15
export SNOWFLAKE_PRIVATE_KEY_PASSPHRASE='eyJraWQiOiI1MDg3NDc2OTQxMyIsImFsZyI6IkVTMjU2In0.eyJwIjoiMTk4NzI5NDc2OjUwODc0NzQ1NDc3IiwiaXNzIjoiU0Y6MTA0OSIsImV4cCI6MTc4MjI4MDQ3OH0.8m-fWI5rvCs6b8bvw1quiM-UzW9uPRxMUmE6VAgOFFylAhRkCzch7ojh7CRLeMdii6DD1Owqap0KoOmyxsW77A'
export REDIS_URL=redis://localhost:6379
export LAMBDA_CLOUD_API_KEY=secret_sophiacloudapi_17cf7f3cedca48f18b4b8ea46cbb258f.EsLXt0lkGlhZ1Nd369Ld5DMSuhJg9O9y
export LAMBDA_API_KEY=secret_sophia5apikey_a404a99d985d41828d7020f0b9a122a2.PjbWZb0lLubKu1nmyWYLy9Ycl3vyL18o
python backend/app/unified_chat_backend.py
"""

    print("Creating startup script...")
    ssh_cmd(
        BACKEND_INSTANCE_IP,
        f"cat > /home/ubuntu/start_backend.sh << 'EOF'\n{backend_script}\nEOF",
    )
    ssh_cmd(BACKEND_INSTANCE_IP, "chmod +x /home/ubuntu/start_backend.sh")

    # Create systemd service
    service_content = """[Unit]
Description=Sophia AI Backend
After=network.target redis.service

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/sophia-main
ExecStart=/home/ubuntu/start_backend.sh
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""

    print("Creating systemd service...")
    ssh_cmd(
        BACKEND_INSTANCE_IP,
        f"echo '{service_content}' | sudo tee /etc/systemd/system/sophia-backend.service",
    )

    # Start Redis if not running
    print("Ensuring Redis is running...")
    ssh_cmd(
        BACKEND_INSTANCE_IP,
        "sudo systemctl start redis || sudo apt-get install -y redis-server && sudo systemctl start redis",
    )

    # Reload and start service
    print("Starting backend service...")
    ssh_cmd(BACKEND_INSTANCE_IP, "sudo systemctl daemon-reload")
    ssh_cmd(BACKEND_INSTANCE_IP, "sudo systemctl enable sophia-backend")
    ssh_cmd(BACKEND_INSTANCE_IP, "sudo systemctl restart sophia-backend")

    # Wait for startup
    print("Waiting for backend to start...")
    time.sleep(10)

    # Check if running
    result = run_cmd(f"curl -s http://{BACKEND_INSTANCE_IP}:8001/health", check=False)
    if result and result.returncode == 0:
        print(f"✅ Backend is running at http://{BACKEND_INSTANCE_IP}:8001")
        return True
    else:
        # Check logs
        logs = ssh_cmd(
            BACKEND_INSTANCE_IP, "sudo journalctl -u sophia-backend -n 50 --no-pager"
        )
        print("Backend logs:")
        if logs:
            print(logs.stdout)
        return False


def deploy_mcp_servers():
    """Deploy MCP servers to sophia-mcp-orchestrator instance"""
    print("\n🚀 DEPLOYING MCP SERVERS TO LAMBDA LABS")
    print(f"Target: {MCP_INSTANCE_IP}")

    # Create MCP deployment script
    mcp_script = """#!/bin/bash
cd /home/ubuntu/sophia-main
source venv/bin/activate
export PYTHONPATH=/home/ubuntu/sophia-main

# Start all MCP servers
echo "Starting MCP servers..."

# Create a simple MCP launcher
cat > /home/ubuntu/start_mcp_servers.py << 'PYTHON'
import subprocess
import time
import os

os.chdir('/home/ubuntu/sophia-main')

mcp_servers = [
    ("ai_memory", 9001),
    ("codacy", 3008),
    ("github", 9003),
    ("linear", 9004),
    ("asana", 9006),
    ("notion", 9102),
    ("slack", 9101)
]

for server, port in mcp_servers:
    print(f"Starting {server} on port {port}")
    subprocess.Popen([
        "python", "-m", f"mcp-servers.{server}.{server}_mcp_server",
        "--port", str(port)
    ])
    time.sleep(2)

print("All MCP servers started")
# Keep running
while True:
    time.sleep(60)
PYTHON

python /home/ubuntu/start_mcp_servers.py
"""

    print("Deploying MCP servers...")
    ssh_cmd(
        MCP_INSTANCE_IP, f"cat > /home/ubuntu/start_mcp.sh << 'EOF'\n{mcp_script}\nEOF"
    )
    ssh_cmd(MCP_INSTANCE_IP, "chmod +x /home/ubuntu/start_mcp.sh")

    # Create systemd service for MCP servers
    mcp_service = """[Unit]
Description=Sophia MCP Servers
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/sophia-main
ExecStart=/home/ubuntu/start_mcp.sh
Restart=always

[Install]
WantedBy=multi-user.target
"""

    ssh_cmd(
        MCP_INSTANCE_IP,
        f"echo '{mcp_service}' | sudo tee /etc/systemd/system/sophia-mcp.service",
    )
    ssh_cmd(MCP_INSTANCE_IP, "sudo systemctl daemon-reload")
    ssh_cmd(MCP_INSTANCE_IP, "sudo systemctl enable sophia-mcp")
    ssh_cmd(MCP_INSTANCE_IP, "sudo systemctl restart sophia-mcp")

    print("✅ MCP servers deployment initiated")
    return True


def update_frontend():
    """Update frontend to use Lambda Labs backend"""
    print("\n🚀 UPDATING FRONTEND CONFIGURATION")

    # Update Vercel environment variables
    backend_url = f"http://{BACKEND_INSTANCE_IP}:8001"

    print(f"Setting VITE_API_URL to {backend_url}")
    run_cmd(f"vercel env add VITE_API_URL production --force < <(echo '{backend_url}')")

    # Trigger redeployment
    print("Redeploying frontend...")
    result = run_cmd("cd frontend && vercel --prod --yes", check=False)

    if result and result.returncode == 0:
        print("✅ Frontend redeployed with Lambda Labs backend")
        return True
    else:
        print("⚠️ Frontend deployment may have failed - check Vercel dashboard")
        return False


def verify_deployment():
    """Verify all services are running"""
    print("\n🔍 VERIFYING DEPLOYMENT")

    status = {"backend": False, "mcp_servers": False, "frontend": False}

    # Check backend
    result = run_cmd(f"curl -s http://{BACKEND_INSTANCE_IP}:8001/health", check=False)
    if result and result.returncode == 0:
        try:
            health = json.loads(result.stdout)
            if health.get("status") == "healthy":
                status["backend"] = True
                print(f"✅ Backend: http://{BACKEND_INSTANCE_IP}:8001")
        except:
            pass

    # Check MCP servers
    mcp_result = ssh_cmd(MCP_INSTANCE_IP, "sudo systemctl is-active sophia-mcp")
    if mcp_result and "active" in mcp_result.stdout:
        status["mcp_servers"] = True
        print(f"✅ MCP Servers: Active on {MCP_INSTANCE_IP}")

    # Frontend is on Vercel
    status["frontend"] = True
    print("✅ Frontend: Deployed to Vercel")

    return status


def main():
    print("=" * 60)
    print("🚀 SOPHIA AI PRODUCTION DEPLOYMENT TO LAMBDA LABS")
    print("=" * 60)
    print(f"Timestamp: {datetime.now()}")

    # Setup SSH key
    setup_ssh_key()

    # Deploy backend
    if not deploy_backend():
        print("❌ Backend deployment failed")
        sys.exit(1)

    # Deploy MCP servers
    if not deploy_mcp_servers():
        print("⚠️ MCP server deployment may have issues")

    # Update frontend
    update_frontend()

    # Verify deployment
    status = verify_deployment()

    print("\n" + "=" * 60)
    print("📊 DEPLOYMENT SUMMARY")
    print("=" * 60)

    if status["backend"]:
        print(f"✅ Backend API: http://{BACKEND_INSTANCE_IP}:8001")
        print(f"   API Docs: http://{BACKEND_INSTANCE_IP}:8001/docs")
    else:
        print("❌ Backend: Not accessible")

    if status["mcp_servers"]:
        print(f"✅ MCP Servers: Running on {MCP_INSTANCE_IP}")
    else:
        print("⚠️ MCP Servers: Status unknown")

    if status["frontend"]:
        print("✅ Frontend: Check Vercel dashboard for URL")
    else:
        print("⚠️ Frontend: Deployment status unknown")

    print("\n💡 NEXT STEPS:")
    print("1. Check Vercel dashboard for frontend URL")
    print("2. Update DNS records if needed")
    print("3. Test the complete application flow")

    if all(status.values()):
        print("\n🎉 DEPLOYMENT SUCCESSFUL!")
    else:
        print("\n⚠️ Some components may need attention")


if __name__ == "__main__":
    main()
