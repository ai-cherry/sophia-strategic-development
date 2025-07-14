#!/usr/bin/env python3
"""
Sophia AI Deployment Verification and Fix Script
This script checks what's actually deployed and provides specific fixes
"""

import subprocess
import json
import os
import sys
from datetime import datetime

# Configuration
# Using sophia-production-instance (us-south-1)
SERVER_IP = "104.171.202.103"
SSH_KEY = os.path.expanduser("~/.ssh/sophia2025.pem")
DOMAIN = "sophia-intel.ai"

# Alternative servers:
# sophia-ai-core: 192.222.58.232 (gpu_1x_gh200, us-east-3)
# sophia-mcp-orchestrator: 104.171.202.117 (gpu_1x_a6000, us-south-1)
# sophia-data-pipeline: 104.171.202.134 (gpu_1x_a100, us-south-1)
# sophia-development: 155.248.194.183 (gpu_1x_a10, us-west-1)

# Colors for output
RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
NC = '\033[0m'

def print_header(msg):
    print(f"\n{BLUE}{'='*60}")
    print(f"  {msg}")
    print(f"{'='*60}{NC}")

def print_success(msg):
    print(f"{GREEN}✓ {msg}{NC}")

def print_error(msg):
    print(f"{RED}✗ {msg}{NC}")

def print_warning(msg):
    print(f"{YELLOW}⚠ {msg}{NC}")

def run_remote_command(command):
    """Execute command on remote server"""
    ssh_cmd = f"ssh -i {SSH_KEY} -o ConnectTimeout=5 ubuntu@{SERVER_IP} '{command}'"
    try:
        result = subprocess.run(ssh_cmd, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
    except Exception as e:
        return False, "", str(e)

def check_ssh_connection():
    """Check if we can SSH to the server"""
    print("\nChecking SSH connection...")
    success, stdout, stderr = run_remote_command("echo 'SSH_OK'")
    if success and 'SSH_OK' in stdout:
        print_success(f"SSH connection to {SERVER_IP} is working")
        return True
    else:
        print_error(f"Cannot connect to server: {stderr}")
        print("\nTo fix:")
        print(f"1. Check SSH key exists: ls -la {SSH_KEY}")
        print(f"2. Check permissions: chmod 600 {SSH_KEY}")
        print(f"3. Test manually: ssh -i {SSH_KEY} ubuntu@{SERVER_IP}")
        return False

def check_docker_services():
    """Check if Docker services are running"""
    print_header("Docker Services Status")
    
    services = ["postgres", "redis", "weaviate"]
    running_services = []
    
    for service in services:
        success, stdout, _ = run_remote_command(f"docker ps --filter name={service} --format '{{{{.Names}}}}'")
        if success and service in stdout:
            print_success(f"{service} is running")
            running_services.append(service)
        else:
            print_error(f"{service} is NOT running")
    
    if len(running_services) < len(services):
        print("\nTo fix missing services:")
        print("1. SSH to server and run:")
        print("   cd ~/sophia-deployment")
        print("   docker-compose up -d")
        return False
    return True

def check_backend_api():
    """Check if backend API is running"""
    print_header("Backend API Status")
    
    # Check if process is running
    success, stdout, _ = run_remote_command("pgrep -f 'uvicorn' | head -1")
    if success and stdout:
        print_success(f"Backend process is running (PID: {stdout})")
    else:
        print_error("Backend process is NOT running")
        
    # Check health endpoint
    success, stdout, _ = run_remote_command("curl -s http://localhost:8000/health")
    if success and 'healthy' in stdout:
        print_success("Backend API is healthy")
        return True
    else:
        print_error("Backend API health check failed")
        
        # Check logs
        print("\nChecking backend logs...")
        success, stdout, _ = run_remote_command("tail -20 ~/sophia-logs/backend.log 2>/dev/null")
        if success and stdout:
            print(f"\nLast 20 lines of backend log:\n{stdout}")
        
        print("\nTo fix backend:")
        print("1. SSH to server and check the issue:")
        print("   cd ~/sophia-main")
        print("   source venv/bin/activate")
        print("   python -m api.main  # Try running manually to see errors")
        return False

def check_nginx():
    """Check nginx configuration"""
    print_header("Nginx Configuration")
    
    # Check if nginx is running
    success, stdout, _ = run_remote_command("systemctl is-active nginx")
    if success and 'active' in stdout:
        print_success("Nginx is running")
    else:
        print_error("Nginx is NOT running")
        return False
    
    # Check site configuration
    success, stdout, _ = run_remote_command("ls -la /etc/nginx/sites-enabled/")
    if success:
        print(f"\nEnabled sites:\n{stdout}")
        
    # Check if frontend directory exists
    success, stdout, _ = run_remote_command("ls -la /var/www/sophia-frontend/index.html 2>/dev/null")
    if success:
        print_success("Frontend files are deployed")
    else:
        print_error("Frontend files are NOT deployed")
        print("\nTo deploy frontend:")
        print("1. Run from local machine:")
        print("   cd frontend")
        print("   npm run build")
        print("   tar -czf dist.tar.gz dist/")
        print(f"   scp -i {SSH_KEY} dist.tar.gz ubuntu@{SERVER_IP}:~/")
        print("2. On server:")
        print("   sudo mkdir -p /var/www/sophia-frontend")
        print("   cd /var/www/sophia-frontend")
        print("   sudo tar -xzf ~/dist.tar.gz --strip-components=1")
        print("   sudo chown -R www-data:www-data .")
        return False
    
    return True

def check_mcp_servers():
    """Check MCP server status"""
    print_header("MCP Servers Status")
    
    mcp_ports = {
        "AI Memory": 9000,
        "Codacy": 3008,
        "GitHub": 9003,
        "Linear": 9004
    }
    
    running_count = 0
    for name, port in mcp_ports.items():
        success, stdout, _ = run_remote_command(f"nc -z localhost {port} 2>/dev/null && echo 'OK'")
        if success and 'OK' in stdout:
            print_success(f"{name} MCP server is running on port {port}")
            running_count += 1
        else:
            print_error(f"{name} MCP server is NOT running on port {port}")
    
    if running_count < len(mcp_ports):
        print("\nTo start MCP servers:")
        print("1. SSH to server:")
        print("   cd ~/sophia-main")
        print("   ./start_mcp_servers.sh")
        return False
    return True

def check_dns():
    """Check DNS configuration"""
    print_header("DNS Configuration")
    
    domains = [DOMAIN, f"api.{DOMAIN}", f"webhooks.{DOMAIN}"]
    
    for domain in domains:
        try:
            result = subprocess.run(f"nslookup {domain} 8.8.8.8", shell=True, capture_output=True, text=True)
            if SERVER_IP in result.stdout:
                print_success(f"{domain} → {SERVER_IP}")
            else:
                print_error(f"{domain} is NOT pointing to {SERVER_IP}")
                print(f"   Current resolution: {result.stdout}")
        except:
            print_error(f"Could not resolve {domain}")
    
    print("\nTo fix DNS:")
    print("1. Log into Namecheap")
    print("2. Update A records:")
    print(f"   @ → {SERVER_IP}")
    print(f"   api → {SERVER_IP}")
    print(f"   webhooks → {SERVER_IP}")

def test_live_endpoints():
    """Test live endpoints"""
    print_header("Live Endpoint Tests")
    
    endpoints = [
        (f"https://{DOMAIN}", "Frontend"),
        (f"https://api.{DOMAIN}/health", "API Health"),
        (f"https://api.{DOMAIN}/docs", "API Documentation")
    ]
    
    for url, name in endpoints:
        try:
            result = subprocess.run(f"curl -s -o /dev/null -w '%{{http_code}}' {url}", 
                                  shell=True, capture_output=True, text=True)
            status_code = result.stdout.strip()
            
            if status_code in ['200', '301', '302']:
                print_success(f"{name} ({url}): {status_code}")
            else:
                print_error(f"{name} ({url}): {status_code}")
        except:
            print_error(f"{name} ({url}): Failed to connect")

def generate_deployment_report():
    """Generate a deployment status report"""
    print_header("Deployment Status Report")
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "server_ip": SERVER_IP,
        "domain": DOMAIN,
        "checks": {}
    }
    
    # Run all checks
    checks = [
        ("SSH Connection", check_ssh_connection),
        ("Docker Services", check_docker_services),
        ("Backend API", check_backend_api),
        ("Nginx", check_nginx),
        ("MCP Servers", check_mcp_servers),
        ("DNS", check_dns),
        ("Live Endpoints", test_live_endpoints)
    ]
    
    all_passed = True
    for name, check_func in checks:
        try:
            result = check_func()
            report["checks"][name] = "PASS" if result else "FAIL"
            if not result:
                all_passed = False
        except Exception as e:
            report["checks"][name] = f"ERROR: {str(e)}"
            all_passed = False
    
    # Save report
    with open("deployment_status_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print_header("Summary")
    print(f"\nDeployment Status: {'READY' if all_passed else 'NOT READY'}")
    print("\nReport saved to: deployment_status_report.json")
    
    if not all_passed:
        print("\n" + "="*60)
        print("TO FIX ALL ISSUES:")
        print("="*60)
        print("\n1. Run the real deployment script:")
        print("   chmod +x scripts/deploy_sophia_production_real.sh")
        print("   ./scripts/deploy_sophia_production_real.sh")
        print("\n2. Or fix issues manually using the suggestions above")
    else:
        print("\n" + "="*60)
        print("🎉 DEPLOYMENT IS LIVE AND WORKING! 🎉")
        print("="*60)
        print(f"\n🌐 Frontend: https://{DOMAIN}")
        print(f"🔧 API: https://api.{DOMAIN}")
        print(f"📊 API Docs: https://api.{DOMAIN}/docs")

if __name__ == "__main__":
    print(f"{BLUE}Sophia AI Deployment Verification{NC}")
    print(f"{BLUE}{'='*40}{NC}")
    
    # First check SSH
    if not check_ssh_connection():
        print("\n❌ Cannot continue without SSH access")
        sys.exit(1)
    
    # Generate full report
    generate_deployment_report() 