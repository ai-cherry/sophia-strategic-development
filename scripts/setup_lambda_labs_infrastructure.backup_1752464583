#!/usr/bin/env python3
"""
Set up Lambda Labs infrastructure for Sophia AI
Configures serverless architecture for frontend, backend, and MCP servers
"""

import json
import subprocess
import sys
import os
from datetime import datetime

def run_command(cmd, check=True):
    """Run a command and return the output"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            check=check
        )
        return result.stdout.strip(), result.returncode
    except subprocess.CalledProcessError as e:
        return e.stderr, e.returncode

def get_lambda_instances(api_key):
    """Get current Lambda Labs instances"""
    cmd = f'curl -s -u {api_key}: https://cloud.lambda.ai/api/v1/instances'
    output, _ = run_command(cmd)
    
    try:
        data = json.loads(output)
        return data.get('data', [])
    except:
        return []

def create_instance(api_key, name, instance_type, region):
    """Create a new Lambda Labs instance"""
    print(f"\n🚀 Creating instance: {name}")
    
    payload = {
        "name": name,
        "instance_type_name": instance_type,
        "region_name": region,
        "ssh_key_names": ["sophia2025"],
        "file_system_names": []
    }
    
    cmd = f'''curl -s -X POST \
        -u {api_key}: \
        -H "Content-Type: application/json" \
        -d '{json.dumps(payload)}' \
        https://cloud.lambda.ai/api/v1/instance-operations/launch'''
    
    output, returncode = run_command(cmd)
    
    if returncode == 0:
        try:
            data = json.loads(output)
            if 'data' in data:
                print(f"  ✅ Instance {name} created successfully")
                return data['data']
            else:
                print(f"  ❌ Failed to create instance: {data.get('error', {}).get('message', 'Unknown error')}")
        except:
            print(f"  ❌ Failed to parse response: {output}")
    else:
        print(f"  ❌ Failed to create instance: {output}")
    
    return None

def setup_instance(instance_ip, setup_type):
    """Set up an instance based on its type"""
    
    print(f"\n🔧 Setting up {setup_type} on {instance_ip}...")
    
    ssh_key = os.path.expanduser("~/.ssh/sophia2025.pem")
    
    # Base setup commands
    base_setup = """
    sudo apt-get update && sudo apt-get upgrade -y
    sudo apt-get install -y docker.io docker-compose git nginx certbot python3-certbot-nginx
    sudo usermod -aG docker ubuntu
    
    # Install Node.js 20
    curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
    sudo apt-get install -y nodejs
    
    # Install Python 3.11
    sudo add-apt-repository ppa:deadsnakes/ppa -y
    sudo apt-get update
    sudo apt-get install -y python3.11 python3.11-venv python3.11-dev
    
    # Clone repository
    git clone https://github.com/ai-cherry/sophia-main.git
    cd sophia-main
    """
    
    # Type-specific setup
    if setup_type == "frontend":
        specific_setup = """
        # Frontend setup
        cd frontend
        npm install
        npm run build
        
        # Nginx configuration for React app
        sudo tee /etc/nginx/sites-available/sophia-frontend << EOF
server {
    listen 80;
    server_name _;
    root /home/ubuntu/sophia-main/frontend/dist;
    index index.html;
    
    location / {
        try_files \\$uri /index.html;
    }
    
    location /api {
        proxy_pass http://backend-ip:8000;
        proxy_set_header Host \\$host;
        proxy_set_header X-Real-IP \\$remote_addr;
    }
}
EOF
        
        sudo ln -s /etc/nginx/sites-available/sophia-frontend /etc/nginx/sites-enabled/
        sudo rm /etc/nginx/sites-enabled/default
        sudo nginx -t && sudo systemctl restart nginx
        """
    
    elif setup_type == "backend":
        specific_setup = """
        # Backend setup
        cd backend
        python3.11 -m venv venv
        source venv/bin/activate
        pip install -r requirements.txt
        
        # Create systemd service
        sudo tee /etc/systemd/system/sophia-backend.service << EOF
[Unit]
Description=Sophia AI Backend
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/sophia-main
Environment="PATH=/home/ubuntu/sophia-main/backend/venv/bin"
ExecStart=/home/ubuntu/sophia-main/backend/venv/bin/uvicorn api.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
EOF
        
        sudo systemctl daemon-reload
        sudo systemctl enable sophia-backend
        sudo systemctl start sophia-backend
        """
    
    elif setup_type == "mcp-servers":
        specific_setup = """
        # MCP Servers setup
        cd mcp-servers
        
        # Set up each MCP server as a Docker container
        docker-compose up -d
        
        # Create monitoring script
        tee ~/monitor_mcp.sh << 'EOF'
#!/bin/bash
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
EOF
        chmod +x ~/monitor_mcp.sh
        """
    else:
        print(f"  ⚠️  Unknown setup type: {setup_type}")
        return False
    
    # Execute setup
    full_setup = base_setup + specific_setup
    
    cmd = f'ssh -i {ssh_key} -o StrictHostKeyChecking=no ubuntu@{instance_ip} "{full_setup}"'
    output, returncode = run_command(cmd, check=False)
    
    if returncode == 0:
        print(f"  ✅ {setup_type} setup completed successfully")
    else:
        print(f"  ⚠️  {setup_type} setup completed with warnings")
    
    return returncode == 0

def main():
    """Main infrastructure setup"""
    
    print("🏗️  Sophia AI Lambda Labs Infrastructure Setup")
    print("=" * 60)
    
    # Get API key from Pulumi ESC
    try:
        from backend.core.auto_esc_config import get_config_value
        api_key = get_config_value('lambda_labs.api_key')
        cloud_api_key = get_config_value('lambda_labs.cloud_api_key')
    except:
        print("❌ Failed to get API keys from Pulumi ESC")
        print("   Run: python scripts/setup_pulumi_esc_secrets.py first")
        sys.exit(1)
    
    # Check current instances
    print("\n📊 Current Lambda Labs instances:")
    instances = get_lambda_instances(api_key)
    
    if instances:
        for instance in instances:
            print(f"  - {instance['name']}: {instance['ip']} ({instance['instance_type']['name']}) - {instance['status']}")
    else:
        print("  No instances found")
    
    # Infrastructure plan
    infrastructure_plan = {
        'sophia-frontend-serverless': {
            'type': 'gpu_1x_a10',
            'region': 'us-south-1',
            'setup': 'frontend',
            'description': 'Serverless frontend with React + Nginx'
        },
        'sophia-backend-serverless': {
            'type': 'gpu_1x_a10',
            'region': 'us-south-1',
            'setup': 'backend',
            'description': 'Serverless backend API with FastAPI'
        },
        'sophia-mcp-orchestrator': {
            'type': 'gpu_1x_a6000',
            'region': 'us-south-1',
            'setup': 'mcp-servers',
            'description': 'MCP servers orchestration with Docker'
        }
    }
    
    print("\n📋 Infrastructure Plan:")
    for name, config in infrastructure_plan.items():
        print(f"  - {name}: {config['type']} in {config['region']}")
        print(f"    {config['description']}")
    
    # Create instances if they don't exist
    existing_names = [i['name'] for i in instances]
    
    for name, config in infrastructure_plan.items():
        if name not in existing_names:
            instance = create_instance(
                api_key,
                name,
                config['type'],
                config['region']
            )
            
            if instance:
                # Wait for instance to be ready
                print(f"    ⏳ Waiting for {name} to be ready...")
                import time
                time.sleep(30)
                
                # Get updated instance info
                instances = get_lambda_instances(api_key)
                for i in instances:
                    if i['name'] == name and i['ip']:
                        setup_instance(i['ip'], config['setup'])
                        break
        else:
            print(f"\n✓ {name} already exists")
    
    # Generate infrastructure report
    print("\n📄 Generating infrastructure report...")
    
    report = {
        'timestamp': datetime.now().isoformat(),
        'instances': [],
        'endpoints': {}
    }
    
    # Get final instance state
    instances = get_lambda_instances(api_key)
    
    for instance in instances:
        report['instances'].append({
            'name': instance['name'],
            'ip': instance['ip'],
            'type': instance['instance_type']['name'],
            'region': instance['region']['name'],
            'status': instance['status']
        })
        
        # Set endpoints
        if 'frontend' in instance['name']:
            report['endpoints']['frontend'] = f"http://{instance['ip']}"
        elif 'backend' in instance['name']:
            report['endpoints']['backend'] = f"http://{instance['ip']}:8000"
        elif 'mcp' in instance['name']:
            report['endpoints']['mcp_orchestrator'] = f"http://{instance['ip']}:3000"
    
    # Save report
    with open('lambda_labs_infrastructure.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print("\n✅ Infrastructure setup complete!")
    print(f"\n🌐 Endpoints:")
    for service, endpoint in report['endpoints'].items():
        print(f"  - {service}: {endpoint}")
    
    print("\n📋 Next steps:")
    print("1. Update DNS records to point to the new IPs")
    print("2. Configure SSL certificates with: sudo certbot --nginx")
    print("3. Deploy application code with: pulumi up")
    print("4. Monitor instances with: python scripts/monitor_lambda_labs.py")

if __name__ == "__main__":
    main() 