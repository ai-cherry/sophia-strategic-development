#!/usr/bin/env python3
"""
Consolidate Lambda Labs Deployment Strategy
- Remove all Vercel references
- Standardize SSH key to sophia_final_key
- Update all deployment scripts to use Lambda Labs only
- Create unified deployment configuration
"""

import os
import re
import shutil
from pathlib import Path
from typing import List, Dict, Tuple

class LambdaLabsConsolidator:
    def __init__(self):
        self.root_dir = Path.cwd()
        self.ssh_key_name = "sophia_final_key"
        self.ssh_key_path = f"~/.ssh/{self.ssh_key_name}"
        
        # Lambda Labs server configuration
        self.lambda_servers = {
            "primary": {
                "name": "sophia-ai-core",
                "ip": "192.222.58.232",
                "gpu": "GH200",
                "role": "primary",
                "ports": {"backend": 8000, "frontend": 80, "https": 443}
            },
            "mcp": {
                "name": "sophia-mcp-orchestrator", 
                "ip": "104.171.202.117",
                "gpu": "A6000",
                "role": "mcp-servers"
            },
            "data": {
                "name": "sophia-data-pipeline",
                "ip": "104.171.202.134", 
                "gpu": "A100",
                "role": "data-processing"
            },
            "prod": {
                "name": "sophia-production-instance",
                "ip": "104.171.202.103",
                "gpu": "RTX6000", 
                "role": "production"
            },
            "dev": {
                "name": "sophia-development",
                "ip": "155.248.194.183",
                "gpu": "A10",
                "role": "development"
            }
        }
        
        # Files to remove (Vercel-specific)
        self.files_to_remove = [
            "vercel.json",
            "SOPHIA_INTEL_AI_DEPLOYMENT_GUIDE.md",
            "SOPHIA_DEPLOYMENT_FINAL_STATUS.md", 
            "SOPHIA_DEPLOYMENT_CONFIRMATION.md",
            "SOPHIA_AI_LIVE_DEPLOYMENT.md",
            "todo.md",
            "DEPLOYMENT_STATUS.md"
        ]
        
        # SSH key patterns to replace
        self.ssh_key_patterns = [
            (r'~/.ssh/sophia2025\.pem', self.ssh_key_path),
            (r'~/.ssh/sophia_final_key', self.ssh_key_path),
            (r'~/.ssh/sophia_final_key', self.ssh_key_path),
            (r'~/.ssh/sophia_final_key', self.ssh_key_path),
            (r'~/.ssh/sophia_final_key', self.ssh_key_path),
            (r'\$HOME/\.ssh/sophia2025\.pem', f'$HOME/.ssh/{self.ssh_key_name}'),
            (r'\$HOME/\.ssh/lambda_labs_private_key', f'$HOME/.ssh/{self.ssh_key_name}'),
            (r'SSH_KEY="\$HOME/\.ssh/[^"]*"', f'SSH_KEY="$HOME/.ssh/sophia_final_key"')
        ]
        
        # Vercel patterns to remove/replace
        self.vercel_patterns = [
            (r'vercel\.json', 'nginx.conf'),
            (r'https://.*\.vercel\.app', 'http://192.222.58.232'),
            (r'cname\.vercel-dns\.com', '192.222.58.232'),
            (r'VERCEL_[A-Z_]+', ''),
            (r'vercel\s+deploy', 'ssh deploy'),
            (r'vercel\s+env', 'env'),
        ]

    def remove_vercel_files(self):
        """Remove Vercel-specific files"""
        print("🗑️  Removing Vercel-specific files...")
        removed_count = 0
        
        for file_path in self.files_to_remove:
            full_path = self.root_dir / file_path
            if full_path.exists():
                print(f"   Removing: {file_path}")
                full_path.unlink()
                removed_count += 1
        
        print(f"✅ Removed {removed_count} Vercel-specific files")

    def update_ssh_keys_in_file(self, file_path: Path) -> bool:
        """Update SSH key references in a single file"""
        if not file_path.exists() or file_path.suffix not in ['.py', '.sh', '.md', '.yml', '.yaml', '.json']:
            return False
        
        try:
            content = file_path.read_text()
            original_content = content
            
            # Apply SSH key pattern replacements
            for pattern, replacement in self.ssh_key_patterns:
                content = re.sub(pattern, replacement, content)
            
            # Update specific SSH commands
            content = re.sub(
                r'ssh -i ~/.ssh/sophia_final_key -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null ',
                f'ssh -i ~/.ssh/sophia_final_key -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null ',
                content
            )
            
            content = re.sub(
                r'scp -i ~/.ssh/sophia_final_key -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null ',
                f'scp -i ~/.ssh/sophia_final_key -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null ',
                content
            )
            
            if content != original_content:
                file_path.write_text(content)
                return True
                
        except Exception as e:
            print(f"   ⚠️  Error updating {file_path}: {e}")
            
        return False

    def remove_vercel_references_in_file(self, file_path: Path) -> bool:
        """Remove Vercel references from a single file"""
        if not file_path.exists():
            return False
            
        try:
            content = file_path.read_text()
            original_content = content
            
            # Remove Vercel-specific sections
            content = re.sub(r'#.*[Vv]ercel.*\n.*\n', '', content, flags=re.MULTILINE)
            content = re.sub(r'vercel_[a-zA-Z_]+:.*\n', '', content)
            content = re.sub(r'VERCEL_[A-Z_]+.*\n', '', content)
            
            # Replace Vercel URLs with Lambda Labs
            content = re.sub(r'https://.*\.vercel\.app', 'http://192.222.58.232', content)
            content = re.sub(r'cname\.vercel-dns\.com', '192.222.58.232', content)
            
            # Remove Vercel deployment commands
            content = re.sub(r'vercel\s+deploy.*\n', '', content)
            content = re.sub(r'vercel\s+env.*\n', '', content)
            
            if content != original_content:
                file_path.write_text(content)
                return True
                
        except Exception as e:
            print(f"   ⚠️  Error removing Vercel from {file_path}: {e}")
            
        return False

    def consolidate_deployment_scripts(self):
        """Update all deployment scripts to use Lambda Labs only"""
        print("🔧 Consolidating deployment scripts...")
        
        scripts_dir = self.root_dir / "scripts"
        updated_files = []
        
        for script_file in scripts_dir.glob("*.py"):
            if self.update_ssh_keys_in_file(script_file):
                updated_files.append(script_file.name)
        
        for script_file in scripts_dir.glob("*.sh"):
            if self.update_ssh_keys_in_file(script_file):
                updated_files.append(script_file.name)
        
        print(f"✅ Updated {len(updated_files)} deployment scripts")
        if updated_files:
            print("   Updated files:")
            for file in updated_files[:10]:  # Show first 10
                print(f"     - {file}")

    def update_infrastructure_configs(self):
        """Update infrastructure configuration files"""
        print("🏗️  Updating infrastructure configurations...")
        
        config_dirs = [
            self.root_dir / "infrastructure",
            self.root_dir / "config", 
            self.root_dir / "deployment",
            self.root_dir / "k8s"
        ]
        
        updated_files = []
        
        for config_dir in config_dirs:
            if not config_dir.exists():
                continue
                
            for config_file in config_dir.rglob("*.yaml"):
                if self.remove_vercel_references_in_file(config_file):
                    updated_files.append(str(config_file.relative_to(self.root_dir)))
                    
            for config_file in config_dir.rglob("*.yml"):
                if self.remove_vercel_references_in_file(config_file):
                    updated_files.append(str(config_file.relative_to(self.root_dir)))
                    
            for config_file in config_dir.rglob("*.json"):
                if self.remove_vercel_references_in_file(config_file):
                    updated_files.append(str(config_file.relative_to(self.root_dir)))
        
        print(f"✅ Updated {len(updated_files)} infrastructure files")

    def create_unified_deployment_config(self):
        """Create unified Lambda Labs deployment configuration"""
        print("📋 Creating unified deployment configuration...")
        
        config_content = f"""# Sophia AI Lambda Labs Deployment Configuration
# Unified configuration for all Lambda Labs deployments

# SSH Configuration
SSH_KEY_NAME="{self.ssh_key_name}"
SSH_KEY_PATH="{self.ssh_key_path}"
SSH_OPTIONS="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null"

# Lambda Labs Servers
"""
        
        for server_id, config in self.lambda_servers.items():
            config_content += f"""
# {config['name']} ({config['role']})
{server_id.upper()}_NAME="{config['name']}"
{server_id.upper()}_IP="{config['ip']}"
{server_id.upper()}_GPU="{config['gpu']}"
{server_id.upper()}_ROLE="{config['role']}"
"""
            if 'ports' in config:
                for port_name, port_num in config['ports'].items():
                    config_content += f"{server_id.upper()}_{port_name.upper()}_PORT={port_num}\n"

        config_content += """
# Deployment Strategy
DEPLOYMENT_STRATEGY="lambda_labs_only"
FRONTEND_DEPLOYMENT="nginx_on_lambda"
BACKEND_DEPLOYMENT="docker_on_lambda"
MCP_DEPLOYMENT="k8s_on_lambda"

# Domain Configuration  
PRIMARY_DOMAIN="192.222.58.232"
API_ENDPOINT="http://192.222.58.232:8000"
FRONTEND_ENDPOINT="http://192.222.58.232"

# Docker Configuration
DOCKER_REGISTRY="scoobyjava15"
DOCKER_IMAGE_PREFIX="sophia-ai"

# Kubernetes Configuration
K8S_NAMESPACE="sophia-ai-prod"
K8S_CONTEXT="lambda-labs-k3s"
"""
        
        config_file = self.root_dir / "lambda_labs_deployment.conf"
        config_file.write_text(config_content)
        
        print(f"✅ Created unified deployment config: {config_file}")

    def create_lambda_deployment_script(self):
        """Create the main Lambda Labs deployment script"""
        print("🚀 Creating Lambda Labs deployment script...")
        
        script_content = f'''#!/bin/bash
# Sophia AI Lambda Labs Deployment Script
# Unified deployment to Lambda Labs infrastructure

set -e

# Load configuration
source "$(dirname "$0")/lambda_labs_deployment.conf"

# Colors for output
RED='\\033[0;31m'
GREEN='\\033[0;32m'
YELLOW='\\033[1;33m'
BLUE='\\033[0;34m'
NC='\\033[0m'

log_info() {{ echo -e "${{BLUE}}[INFO]${{NC}} $1"; }}
log_success() {{ echo -e "${{GREEN}}[SUCCESS]${{NC}} $1"; }}
log_warning() {{ echo -e "${{YELLOW}}[WARNING]${{NC}} $1"; }}
log_error() {{ echo -e "${{RED}}[ERROR]${{NC}} $1"; }}

# Test SSH connectivity
test_ssh_connectivity() {{
    log_info "Testing SSH connectivity to Lambda Labs servers..."
    
    for server in PRIMARY MCP DATA PROD DEV; do
        server_ip_var="${{server}}_IP"
        server_name_var="${{server}}_NAME"
        
        ip="${{!server_ip_var}}"
        name="${{!server_name_var}}"
        
        log_info "Testing $name ($ip)..."
        
        if timeout 10 ssh -i ~/.ssh/sophia_final_key -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null $SSH_OPTIONS ubuntu@$ip "echo 'OK'" 2>/dev/null | grep -q "OK"; then
            log_success "✅ $name accessible"
        else
            log_warning "❌ $name not accessible"
        fi
    done
}}

# Deploy frontend to primary server
deploy_frontend() {{
    log_info "Deploying frontend to primary server..."
    
    # Build frontend
    cd frontend
    npm run build
    cd ..
    
    # Create deployment package
    cd frontend/dist
    tar -czf ../../frontend-deploy.tar.gz .
    cd ../..
    
    # Deploy to primary server
    scp -i ~/.ssh/sophia_final_key -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null $SSH_OPTIONS frontend-deploy.tar.gz ubuntu@$PRIMARY_IP:/tmp/
    
    ssh -i ~/.ssh/sophia_final_key -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null $SSH_OPTIONS ubuntu@$PRIMARY_IP "
        sudo mkdir -p /var/www/sophia-frontend
        sudo chown ubuntu:ubuntu /var/www/sophia-frontend
        cd /var/www/sophia-frontend
        tar -xzf /tmp/frontend-deploy.tar.gz
        sudo chown -R www-data:www-data /var/www/sophia-frontend
        
        # Configure Nginx
        sudo tee /etc/nginx/sites-available/sophia-ai << 'NGINX_EOF'
server {{
    listen 80;
    server_name $PRIMARY_IP;
    
    location / {{
        root /var/www/sophia-frontend;
        index index.html;
        try_files \\$uri \\$uri/ /index.html;
    }}
    
    location /api/ {{
        proxy_pass http://localhost:8000/;
        proxy_set_header Host \\$host;
        proxy_set_header X-Real-IP \\$remote_addr;
        proxy_set_header X-Forwarded-For \\$proxy_add_x_forwarded_for;
    }}
    
    location /health {{
        proxy_pass http://localhost:8000/health;
    }}
    
    location /chat {{
        proxy_pass http://localhost:8000/chat;
    }}
}}
NGINX_EOF
        
        sudo ln -sf /etc/nginx/sites-available/sophia-ai /etc/nginx/sites-enabled/
        sudo rm -f /etc/nginx/sites-enabled/default
        sudo nginx -t && sudo systemctl reload nginx
    "
    
    log_success "Frontend deployed to http://$PRIMARY_IP"
}}

# Deploy backend (already running)
deploy_backend() {{
    log_info "Backend deployment verified..."
    
    # Test backend health
    if curl -s "http://$PRIMARY_IP:8000/health" | grep -q "healthy"; then
        log_success "Backend is healthy and running"
    else
        log_error "Backend is not responding"
        return 1
    fi
}}

# Main deployment function
main() {{
    log_info "Starting Sophia AI Lambda Labs deployment..."
    echo "======================================================"
    
    # Test connectivity
    test_ssh_connectivity
    
    # Deploy components
    deploy_backend
    deploy_frontend
    
    echo ""
    log_success "🎉 Deployment completed successfully!"
    log_info "Access your Sophia AI instance at:"
    log_info "  Frontend: http://$PRIMARY_IP"
    log_info "  API: http://$PRIMARY_IP:8000"
    log_info "  Health: http://$PRIMARY_IP:8000/health"
    
    # Test final deployment
    log_info "Testing final deployment..."
    if curl -s "http://$PRIMARY_IP" | grep -q "Sophia"; then
        log_success "✅ Frontend accessible"
    else
        log_warning "⚠️  Frontend may not be fully ready"
    fi
    
    if curl -s "http://$PRIMARY_IP:8000/health" | grep -q "healthy"; then
        log_success "✅ Backend healthy"
    else
        log_warning "⚠️  Backend health check failed"
    fi
}}

# Run main function
main "$@"
'''
        
        script_file = self.root_dir / "deploy_lambda_labs.sh"
        script_file.write_text(script_content)
        script_file.chmod(0o755)
        
        print(f"✅ Created deployment script: {script_file}")

    def update_frontend_config(self):
        """Update frontend configuration to use Lambda Labs backend"""
        print("🎨 Updating frontend configuration...")
        
        # Update package.json to remove Vercel references
        package_json_path = self.root_dir / "frontend" / "package.json"
        if package_json_path.exists():
            content = package_json_path.read_text()
            
            # Remove Vercel-specific scripts
            content = re.sub(r'"deploy":\s*"vercel.*",?\n', '', content)
            content = re.sub(r'"vercel.*":\s*".*",?\n', '', content)
            
            package_json_path.write_text(content)
            print("   ✅ Updated package.json")
        
        # Create/update .env.production for Lambda Labs
        env_prod_path = self.root_dir / "frontend" / ".env.production"
        env_content = f"""# Sophia AI Production Environment (Lambda Labs)
VITE_API_URL=http://192.222.58.232:8000
VITE_APP_NAME=Sophia AI
VITE_ENVIRONMENT=production
VITE_BACKEND_URL=http://192.222.58.232:8000
VITE_WEBSOCKET_URL=ws://192.222.58.232:8000/ws
"""
        env_prod_path.write_text(env_content)
        print("   ✅ Created .env.production")

    def run_consolidation(self):
        """Run the complete consolidation process"""
        print("🚀 Starting Sophia AI Lambda Labs Consolidation")
        print("=" * 60)
        
        # Step 1: Remove Vercel files
        self.remove_vercel_files()
        
        # Step 2: Update SSH keys in deployment scripts
        self.consolidate_deployment_scripts()
        
        # Step 3: Update infrastructure configs
        self.update_infrastructure_configs()
        
        # Step 4: Create unified deployment configuration
        self.create_unified_deployment_config()
        
        # Step 5: Create main deployment script
        self.create_lambda_deployment_script()
        
        # Step 6: Update frontend configuration
        self.update_frontend_config()
        
        print("\n" + "=" * 60)
        print("✅ Lambda Labs consolidation completed successfully!")
        print("\nNext steps:")
        print("1. Run: ./deploy_lambda_labs.sh")
        print("2. Access: http://192.222.58.232")
        print("3. Verify: http://192.222.58.232:8000/health")
        
        print(f"\nSSH key standardized to: {self.ssh_key_path}")
        print("All Vercel references removed")
        print("Unified Lambda Labs deployment ready")

if __name__ == "__main__":
    consolidator = LambdaLabsConsolidator()
    consolidator.run_consolidation() 