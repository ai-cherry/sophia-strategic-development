#!/usr/bin/env python3
"""
Check deployment status of Sophia AI services
"""

import requests
from typing import Dict
import time


def check_service_health(name: str, url: str, timeout: int = 5) -> Dict:
    """Check if a service is healthy"""
    try:
        start = time.time()
        response = requests.get(url, timeout=timeout)
        elapsed = time.time() - start

        return {
            "name": name,
            "status": "healthy" if response.status_code == 200 else "unhealthy",
            "status_code": response.status_code,
            "response_time": f"{elapsed:.3f}s",
            "url": url,
        }
    except requests.exceptions.ConnectionError:
        return {
            "name": name,
            "status": "down",
            "error": "Connection refused",
            "url": url,
        }
    except requests.exceptions.Timeout:
        return {
            "name": name,
            "status": "timeout",
            "error": f"Timeout after {timeout}s",
            "url": url,
        }
    except Exception as e:
        return {"name": name, "status": "error", "error": str(e), "url": url}


def main():
    """Check all services"""
    print("🔍 Checking Sophia AI Deployment Status...\n")

    services = [
        ("Backend API", "http://localhost:8001/health"),
        ("Backend Docs", "http://localhost:8001/docs"),
        ("Frontend", "http://localhost:3000"),
        ("AI Memory MCP", "http://localhost:9001/health"),
        ("Codacy MCP", "http://localhost:3008/health"),
        ("GitHub MCP", "http://localhost:9003/health"),
        ("Linear MCP", "http://localhost:9004/health"),
        ("Asana MCP", "http://localhost:9006/health"),
        ("Notion MCP", "http://localhost:9102/health"),
        ("Slack MCP", "http://localhost:9101/health"),
    ]

    results = []
    healthy_count = 0

    for name, url in services:
        result = check_service_health(name, url)
        results.append(result)
        if result["status"] == "healthy":
            healthy_count += 1

        # Print result
        if result["status"] == "healthy":
            print(f"✅ {name}: {result['status']} ({result['response_time']})")
        elif result["status"] == "down":
            print(
                f"❌ {name}: {result['status']} - {result.get('error', 'Unknown error')}"
            )
        else:
            print(
                f"⚠️  {name}: {result['status']} - {result.get('error', 'Unknown error')}"
            )

    print(f"\n📊 Summary: {healthy_count}/{len(services)} services are healthy")

    # Check unified chat endpoint
    print("\n🔍 Testing Unified Chat Endpoint...")
    try:
        response = requests.post(
            "http://localhost:8001/api/v4/orchestrate",
            json={
                "query": "What is the status of the system?",
                "user_id": "test_user",
                "session_id": "test_session",
            },
            timeout=10,
        )
        if response.status_code == 200:
            print("✅ Chat endpoint is working")
            print(f"Response: {response.json().get('response', '')[:100]}...")
        else:
            print(f"❌ Chat endpoint returned {response.status_code}")
    except Exception as e:
        print(f"❌ Chat endpoint error: {e}")

    # Print access URLs
    print("\n🌐 Access URLs:")
    print("- Frontend Dashboard: http://localhost:3000")
    print("- Backend API Docs: http://localhost:8001/docs")
    print("- Health Check: http://localhost:8001/health")

    return healthy_count, len(services)


if __name__ == "__main__":
    healthy, total = main()
    exit(0 if healthy == total else 1)
