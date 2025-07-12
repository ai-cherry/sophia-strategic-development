#!/usr/bin/env python3
"""
Monitor Sophia AI deployment status
Shows real-time health of all components
"""

import time
import requests
import subprocess
from datetime import datetime
from typing import Tuple

# Lambda Labs servers
SERVERS = {
    "primary": "104.171.202.103",
    "gpu": "192.222.58.232",
    "mcp": "104.171.202.117",
}

# Service endpoints to check
HEALTH_CHECKS = [
    ("Backend API", f"http://{SERVERS['primary']}:8000/health"),
    ("Memory Service", f"http://{SERVERS['gpu']}:8000/api/v2/memory/stats"),
    ("Chat Service", f"http://{SERVERS['primary']}:8000/api/v4/sophia/health"),
    ("MCP Gateway", f"http://{SERVERS['mcp']}:8080/health"),
    ("AI Memory MCP", f"http://{SERVERS['mcp']}:9001/health"),
    ("Gong MCP", f"http://{SERVERS['mcp']}:9007/health"),
]


def check_health(name: str, url: str) -> Tuple[str, int, str]:
    """Check health of a service"""
    try:
        response = requests.get(url, timeout=5)
        status_code = response.status_code

        if status_code == 200:
            return "✅", status_code, "Healthy"
        else:
            return "⚠️", status_code, f"HTTP {status_code}"
    except requests.exceptions.ConnectionError:
        return "❌", 0, "Connection Failed"
    except requests.exceptions.Timeout:
        return "⏱️", 0, "Timeout"
    except Exception as e:
        return "❓", 0, str(e)[:30]


def check_docker_builds():
    """Check if Docker builds are still running"""
    try:
        result = subprocess.run(
            "ps aux | grep 'docker build' | grep -v grep",
            shell=True,
            capture_output=True,
            text=True,
        )
        return len(result.stdout.strip()) > 0
    except:
        return False


def check_kubernetes_pods():
    """Check Kubernetes pod status"""
    try:
        # Check main namespace
        result = subprocess.run(
            "kubectl get pods -n sophia-ai-prod --no-headers 2>/dev/null",
            shell=True,
            capture_output=True,
            text=True,
        )

        pods = []
        if result.returncode == 0 and result.stdout:
            for line in result.stdout.strip().split("\n"):
                if line:
                    parts = line.split()
                    if len(parts) >= 3:
                        name = parts[0]
                        ready = parts[1]
                        status = parts[2]
                        pods.append(f"{name}: {ready} ({status})")

        # Check MCP namespace
        result = subprocess.run(
            "kubectl get pods -n mcp-servers --no-headers 2>/dev/null",
            shell=True,
            capture_output=True,
            text=True,
        )

        if result.returncode == 0 and result.stdout:
            for line in result.stdout.strip().split("\n"):
                if line:
                    parts = line.split()
                    if len(parts) >= 3:
                        name = parts[0]
                        ready = parts[1]
                        status = parts[2]
                        pods.append(f"MCP/{name}: {ready} ({status})")

        return pods
    except:
        return []


def test_sophia_personality():
    """Test if Sophia's personality is working"""
    try:
        response = requests.post(
            f"http://{SERVERS['primary']}:8000/api/v4/sophia/chat",
            json={"query": "Test query", "user_id": "test_user"},
            timeout=10,
        )

        if response.status_code == 200:
            data = response.json()
            personality = data.get("metadata", {}).get("personality", "Unknown")
            return f"✅ Personality: {personality}"
        else:
            return "❌ Personality test failed"
    except:
        return "⏳ Personality not ready"


def main():
    """Main monitoring loop"""
    print("🔍 SOPHIA AI DEPLOYMENT MONITOR")
    print("=" * 60)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Press Ctrl+C to stop")
    print("=" * 60)

    iteration = 0
    while True:
        iteration += 1
        print(f"\n📊 Status Check #{iteration} - {datetime.now().strftime('%H:%M:%S')}")
        print("-" * 60)

        # Check Docker builds
        if check_docker_builds():
            print("🐳 Docker builds: Still running...")
        else:
            print("🐳 Docker builds: Complete or not running")

        # Check Kubernetes pods
        pods = check_kubernetes_pods()
        if pods:
            print("\n☸️  Kubernetes Pods:")
            for pod in pods[:10]:  # Show first 10
                print(f"  {pod}")
            if len(pods) > 10:
                print(f"  ... and {len(pods) - 10} more")

        # Check service health
        print("\n🏥 Service Health:")
        all_healthy = True
        for name, url in HEALTH_CHECKS:
            status, code, message = check_health(name, url)
            print(f"  {status} {name}: {message}")
            if status != "✅":
                all_healthy = False

        # Test personality if backend is up
        if all_healthy:
            personality_status = test_sophia_personality()
            print(f"\n{personality_status}")

        # Summary
        if all_healthy:
            print("\n✅ ALL SYSTEMS OPERATIONAL!")
            print("🔥 Sophia AI is ready to rock!")
        else:
            print("\n⏳ Deployment in progress...")

        # Wait before next check
        time.sleep(10)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Monitoring stopped")
    except Exception as e:
        print(f"\n❌ Error: {e}")
