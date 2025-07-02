#!/usr/bin/env python3
"""
Launch Script for Enhanced CEO Dashboard
Integrates real-time monitoring with Streamlit dashboard
"""

import subprocess
import sys
import os
import time
import signal
import asyncio
from pathlib import Path

def install_requirements():
    """Install required packages"""
    requirements = [
        "streamlit",
        "aiohttp",
        "pandas",
        "plotly"
    ]
    
    print("🔧 Installing required packages...")
    for req in requirements:
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", req], 
                         capture_output=True, check=True)
            print(f"✅ Installed {req}")
        except subprocess.CalledProcessError:
            print(f"⚠️ Failed to install {req} (may already be installed)")

def check_mcp_servers():
    """Check if MCP servers are running"""
    import aiohttp
    
    async def check_health():
        services = {
            "API Gateway": "http://localhost:8000/health",
            "AI Memory": "http://localhost:9001/health", 
            "Codacy": "http://localhost:3008/health",
            "GitHub": "http://localhost:9003/health",
            "Linear": "http://localhost:9004/health"
        }
        
        print("🏥 Checking MCP server health...")
        healthy_count = 0
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
            for name, url in services.items():
                try:
                    async with session.get(url) as response:
                        if response.status == 200:
                            print(f"✅ {name}: Healthy")
                            healthy_count += 1
                        else:
                            print(f"⚠️ {name}: Unhealthy (HTTP {response.status})")
                except Exception as e:
                    print(f"❌ {name}: Error - {e}")
        
        print(f"\n📊 System Health: {healthy_count}/5 services operational")
        return healthy_count >= 3  # At least 3 services must be healthy
    
    return asyncio.run(check_health())

def launch_dashboard():
    """Launch the Streamlit CEO dashboard"""
    project_root = Path(__file__).parent.parent
    dashboard_path = project_root / "frontend" / "ceo_dashboard_enhanced.py"
    
    if not dashboard_path.exists():
        print(f"❌ Dashboard file not found: {dashboard_path}")
        return False
    
    print("🚀 Launching CEO Dashboard...")
    print("📊 Dashboard will be available at: http://localhost:8501")
    print("🔄 Real-time monitoring integrated")
    print("\n💡 Press Ctrl+C to stop the dashboard")
    
    try:
        # Launch Streamlit dashboard
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            str(dashboard_path),
            "--server.port", "8501",
            "--server.address", "0.0.0.0",
            "--browser.gatherUsageStats", "false"
        ])
        return True
    except KeyboardInterrupt:
        print("\n🛑 Dashboard stopped by user")
        return True
    except Exception as e:
        print(f"❌ Failed to launch dashboard: {e}")
        return False

def main():
    """Main launch function"""
    print("🎯 SOPHIA AI CEO DASHBOARD LAUNCHER")
    print("=" * 50)
    
    # Install requirements
    install_requirements()
    
    # Check MCP server health
    if not check_mcp_servers():
        print("\n⚠️ Warning: Some MCP servers are not healthy")
        print("💡 Dashboard will still launch but some features may be limited")
        
        response = input("\n🤔 Continue anyway? (y/N): ")
        if response.lower() != 'y':
            print("🛑 Launch cancelled")
            return 1
    
    # Launch dashboard
    success = launch_dashboard()
    
    if success:
        print("\n✅ Dashboard session completed successfully")
        return 0
    else:
        print("\n❌ Dashboard launch failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
