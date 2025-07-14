#!/usr/bin/env python3
'''
Master Deployment Script for Sophia AI Lambda Labs Infrastructure
Orchestrates complete deployment across all servers
'''

import subprocess
import time
import sys
import requests

def run_command(cmd, description):
    print(f"🚀 {description}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed")
            return True
        else:
            print(f"❌ {description} failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} error: {e}")
        return False

def test_endpoint(url, description):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            print(f"✅ {description}: {url}")
            return True
        else:
            print(f"❌ {description} failed: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ {description} error: {e}")
        return False

def main():
    print("🚀 Starting Sophia AI Lambda Labs Deployment")
    print("=" * 60)
    
    # Phase 1: Build and push Docker images
    print("\n📦 Phase 1: Building Docker Images")
    if not run_command("python3 scripts/deploy_to_lambda_labs.py --build-images", "Building Docker images"):
        sys.exit(1)
    
    # Phase 2: Deploy to primary server
    print("\n🖥️  Phase 2: Deploying Primary Server")
    if not run_command("ssh root@192.222.58.232 'bash -s' < scripts/deploy_primary_server.sh", "Primary server deployment"):
        print("⚠️  Manual deployment required on primary server")
    
    # Phase 3: Deploy MCP orchestrator
    print("\n🤖 Phase 3: Deploying MCP Orchestrator")
    if not run_command("ssh root@104.171.202.117 'bash -s' < scripts/deploy_mcp_server.sh", "MCP orchestrator deployment"):
        print("⚠️  Manual deployment required on MCP server")
    
    # Phase 4: Setup SSL certificates
    print("\n🔒 Phase 4: Setting up SSL Certificates")
    if not run_command("ssh root@192.222.58.232 'bash -s' < scripts/setup_ssl.sh", "SSL setup"):
        print("⚠️  Manual SSL setup required")
    
    # Phase 5: Setup monitoring
    print("\n📊 Phase 5: Setting up Monitoring")
    if not run_command("ssh root@192.222.58.232 'bash -s' < scripts/setup_monitoring.sh", "Monitoring setup"):
        print("⚠️  Manual monitoring setup required")
    
    # Phase 6: Test all endpoints
    print("\n🧪 Phase 6: Testing Deployment")
    time.sleep(30)  # Wait for services to start
    
    endpoints = [
        ("https://sophia-intel.ai", "Main site"),
        ("https://api.sophia-intel.ai/health", "API health"),
        ("https://app.sophia-intel.ai", "Frontend app"),
        ("https://webhooks.sophia-intel.ai/health", "Webhooks"),
        ("https://mcp.sophia-intel.ai/health", "MCP services")
    ]
    
    success_count = 0
    for url, description in endpoints:
        if test_endpoint(url, description):
            success_count += 1
    
    print("\n" + "=" * 60)
    print(f"🎉 Deployment Complete: {success_count}/{len(endpoints)} endpoints working")
    
    if success_count == len(endpoints):
        print("✅ FULL SUCCESS: Sophia AI is live on Lambda Labs!")
        print("🌐 Main site: https://sophia-intel.ai")
        print("🔗 API: https://api.sophia-intel.ai")
        print("📱 App: https://app.sophia-intel.ai")
    else:
        print("⚠️  Partial deployment - manual intervention required")
        print("📋 Check logs and run individual deployment scripts")

if __name__ == "__main__":
    main()