#!/usr/bin/env python3
"""
Verify Sophia AI deployment and provide comprehensive status
"""

import requests
import subprocess
from datetime import datetime
from typing import Dict, List


def check_service(name: str, url: str, expected_status: int = 200) -> Dict:
    """Check if a service is healthy"""
    try:
        response = requests.get(url, timeout=5)
        return {
            "name": name,
            "status": "✅ Running"
            if response.status_code == expected_status
            else f"⚠️  Status {response.status_code}",
            "url": url,
            "response_time": f"{response.elapsed.total_seconds():.3f}s",
        }
    except requests.exceptions.ConnectionError:
        return {
            "name": name,
            "status": "❌ Not Running",
            "url": url,
            "error": "Connection refused",
        }
    except Exception as e:
        return {"name": name, "status": "❌ Error", "url": url, "error": str(e)}


def get_running_processes() -> List[str]:
    """Get list of running Python and Node processes"""
    try:
        result = subprocess.run(["ps", "aux"], capture_output=True, text=True)
        processes = []
        for line in result.stdout.split("\n"):
            if "sophia" in line.lower() and ("python" in line or "node" in line):
                # Extract the command part
                parts = line.split()
                if len(parts) > 10:
                    cmd = " ".join(parts[10:])
                    if "unified_chat_backend" in cmd:
                        processes.append("Backend API (unified_chat_backend.py)")
                    elif "vite" in cmd or "npm run dev" in cmd:
                        processes.append("Frontend (Vite dev server)")
                    elif "mcp_server" in cmd:
                        processes.append(f"MCP Server: {cmd.split('/')[-1]}")
        return processes
    except:
        return []


def main():
    print("=" * 80)
    print("🚀 SOPHIA AI DEPLOYMENT STATUS")
    print("=" * 80)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Check core services
    print("📡 CORE SERVICES:")
    print("-" * 40)

    services = [
        ("Backend API", "http://localhost:8001/health"),
        ("Backend Docs", "http://localhost:8001/docs"),
        ("Frontend (Vite)", "http://localhost:5173"),  # Vite default port
        ("Frontend (Fallback)", "http://localhost:3000"),  # Fallback port
    ]

    healthy_count = 0
    for name, url in services:
        result = check_service(name, url)
        print(f"{result['status']} {name}")
        if "✅" in result["status"]:
            healthy_count += 1
            print(f"   URL: {url}")
            if "response_time" in result:
                print(f"   Response Time: {result['response_time']}")
        else:
            print(f"   Error: {result.get('error', 'Unknown')}")

    # Check MCP servers
    print("\n📦 MCP SERVERS:")
    print("-" * 40)

    mcp_servers = [
        ("AI Memory", "http://localhost:9001/health"),
        ("Codacy", "http://localhost:3008/health"),
        ("GitHub", "http://localhost:9003/health"),
        ("Linear", "http://localhost:9004/health"),
        ("Asana", "http://localhost:9006/health"),
        ("Notion", "http://localhost:9102/health"),
        ("Slack", "http://localhost:9101/health"),
    ]

    mcp_healthy = 0
    for name, url in mcp_servers:
        result = check_service(name, url)
        print(f"{result['status']} {name} MCP Server")
        if "✅" in result["status"]:
            mcp_healthy += 1

    # Test chat functionality
    print("\n🤖 CHAT FUNCTIONALITY TEST:")
    print("-" * 40)

    try:
        response = requests.post(
            "http://localhost:8001/api/v4/orchestrate",
            json={
                "query": "What is the current system status?",
                "user_id": "deployment_test",
                "session_id": "test_session",
            },
            timeout=10,
        )
        if response.status_code == 200:
            data = response.json()
            print("✅ Chat API is functional")
            print(f"   Response preview: {data.get('response', '')[:100]}...")
        else:
            print(f"❌ Chat API returned status {response.status_code}")
    except Exception as e:
        print(f"❌ Chat API test failed: {e}")

    # Running processes
    print("\n🔧 RUNNING PROCESSES:")
    print("-" * 40)
    processes = get_running_processes()
    if processes:
        for proc in processes:
            print(f"• {proc}")
    else:
        print("No Sophia-related processes detected")

    # Deployment summary
    print("\n📊 DEPLOYMENT SUMMARY:")
    print("-" * 40)
    print(f"Core Services: {healthy_count}/{len(services)} running")
    print(f"MCP Servers: {mcp_healthy}/{len(mcp_servers)} running")

    # Access URLs
    print("\n🌐 ACCESS URLS:")
    print("-" * 40)

    if any(
        "Frontend" in s[0] and "✅" in check_service(s[0], s[1])["status"]
        for s in services
    ):
        frontend_url = (
            "http://localhost:5173"
            if "✅" in check_service("Frontend", "http://localhost:5173")["status"]
            else "http://localhost:3000"
        )
        print(f"✅ Frontend Dashboard: {frontend_url}")
    else:
        print("❌ Frontend not accessible")

    print("✅ Backend API Docs: http://localhost:8001/docs")
    print("✅ Backend Health: http://localhost:8001/health")

    # Next steps
    print("\n📝 NEXT STEPS:")
    print("-" * 40)

    if healthy_count < len(services):
        print("1. Start missing core services:")
        if "❌" in check_service("Frontend", "http://localhost:5173")["status"]:
            print("   cd frontend && npm run dev")
        if "❌" in check_service("Backend", "http://localhost:8001/health")["status"]:
            print("   python backend/app/unified_chat_backend.py")

    if mcp_healthy < len(mcp_servers):
        print("2. Start MCP servers:")
        print("   python scripts/deploy_sophia_full_stack.py")

    print("3. Configure kubectl for K8s deployment")
    print("4. Add GitHub secrets for automated deployment")

    print("\n" + "=" * 80)

    return healthy_count == len(services) and mcp_healthy == len(mcp_servers)


if __name__ == "__main__":
    all_healthy = main()
    exit(0 if all_healthy else 1)
