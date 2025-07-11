#!/usr/bin/env python3
"""
Simple MCP Server Deployment to Lambda Labs
Converts MCP servers to FastAPI apps for easy deployment
"""

import subprocess
from pathlib import Path

MCP_INSTANCE_IP = "104.171.202.117"
SSH_KEY_PATH = Path.home() / ".ssh" / "sophia2025.pem"


def ssh_cmd(cmd):
    """Execute command on MCP instance"""
    ssh_command = f"ssh -o StrictHostKeyChecking=no -i {SSH_KEY_PATH} ubuntu@{MCP_INSTANCE_IP} '{cmd}'"
    return subprocess.run(ssh_command, shell=True, capture_output=True, text=True)


def create_fastapi_wrapper():
    """Create a FastAPI wrapper for MCP servers"""
    wrapper_content = '''#!/usr/bin/env python3
"""
Simple FastAPI wrapper for MCP servers
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import importlib
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = FastAPI(title="MCP Server API")

# Load MCP servers dynamically
mcp_servers = {}

class MCPRequest(BaseModel):
    server: str
    method: str
    params: Optional[Dict[str, Any]] = {}

class MCPResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "servers": list(mcp_servers.keys()),
        "message": "MCP servers running on Lambda Labs"
    }

@app.post("/mcp/call")
async def call_mcp(request: MCPRequest):
    """Call a method on an MCP server"""
    if request.server not in mcp_servers:
        raise HTTPException(status_code=404, detail=f"Server {request.server} not found")
    
    try:
        server = mcp_servers[request.server]
        if hasattr(server, request.method):
            method = getattr(server, request.method)
            result = await method(**request.params) if callable(method) else method
            return MCPResponse(success=True, data=result)
        else:
            raise HTTPException(status_code=404, detail=f"Method {request.method} not found")
    except Exception as e:
        return MCPResponse(success=False, error=str(e))

@app.get("/mcp/servers")
def list_servers():
    """List available MCP servers"""
    return {
        "servers": {
            name: {
                "methods": [m for m in dir(server) if not m.startswith("_")]
            }
            for name, server in mcp_servers.items()
        }
    }

# Initialize servers on startup
@app.on_event("startup")
async def startup():
    """Initialize MCP servers"""
    print("Loading MCP servers...")
    
    # Try to load each server
    server_modules = [
        ("ai_memory", "mcp-servers.ai_memory.server"),
        ("codacy", "mcp-servers.codacy.server"),
        ("github", "mcp-servers.github.server"),
        ("slack", "mcp-servers.slack.server"),
        ("linear", "mcp-servers.linear.server"),
    ]
    
    for name, module_path in server_modules:
        try:
            module = importlib.import_module(module_path)
            # Try to find the server class
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if hasattr(attr, "__call__") or hasattr(attr, "handle_request"):
                    mcp_servers[name] = attr
                    print(f"✅ Loaded {name} server")
                    break
        except Exception as e:
            print(f"❌ Failed to load {name}: {e}")
    
    print(f"Loaded {len(mcp_servers)} MCP servers")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
'''

    return wrapper_content


def deploy_mcp_servers():
    """Deploy MCP servers to Lambda Labs"""
    print(f"🚀 Deploying MCP servers to {MCP_INSTANCE_IP}")

    # Create deployment script
    deployment_script = f"""#!/bin/bash
cd /home/ubuntu/sophia-main
source venv/bin/activate

# Install dependencies
pip install fastapi uvicorn redis httpx

# Create the FastAPI wrapper
cat > /home/ubuntu/sophia-main/mcp_api.py << 'PYTHON'
{create_fastapi_wrapper()}
PYTHON

# Create systemd service
sudo tee /etc/systemd/system/mcp-api.service << 'EOF'
[Unit]
Description=MCP Server API
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/sophia-main
Environment="PYTHONPATH=/home/ubuntu/sophia-main"
ExecStart=/home/ubuntu/sophia-main/venv/bin/python /home/ubuntu/sophia-main/mcp_api.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Start the service
sudo systemctl daemon-reload
sudo systemctl enable mcp-api
sudo systemctl restart mcp-api
"""

    # Write deployment script
    ssh_cmd(f"cat > /home/ubuntu/deploy_mcp.sh << 'EOF'\n{deployment_script}\nEOF")
    ssh_cmd("chmod +x /home/ubuntu/deploy_mcp.sh")

    # Execute deployment
    print("Executing deployment...")
    result = ssh_cmd("/home/ubuntu/deploy_mcp.sh")
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(f"Errors: {result.stderr}")

    # Setup nginx
    print("Configuring nginx...")
    nginx_config = """server {
    listen 80;
    server_name _;
    
    location / {
        proxy_pass http://localhost:8002;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}"""

    ssh_cmd(f"echo '{nginx_config}' | sudo tee /etc/nginx/sites-available/mcp-api")
    ssh_cmd("sudo ln -sf /etc/nginx/sites-available/mcp-api /etc/nginx/sites-enabled/")
    ssh_cmd("sudo rm -f /etc/nginx/sites-enabled/default")
    ssh_cmd("sudo nginx -t && sudo systemctl restart nginx")

    print("✅ MCP servers deployed!")
    print(f"📍 MCP API: http://{MCP_INSTANCE_IP}/health")
    print(f"📍 MCP Servers: http://{MCP_INSTANCE_IP}/mcp/servers")


if __name__ == "__main__":
    deploy_mcp_servers()
