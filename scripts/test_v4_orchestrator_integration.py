#!/usr/bin/env python3
"""
Test V4 Orchestrator Integration

This script tests the integration of the v4 orchestrator with the backend.

Date: July 9, 2025
"""

import json
import sys
from pathlib import Path

import requests

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# API base URL
API_BASE = "http://localhost:8001"


def test_health_endpoints():
    """Test health check endpoints"""
    print("\n🏥 Testing Health Endpoints...")

    # Test v4 orchestrator health
    try:
        response = requests.get(f"{API_BASE}/api/v4/orchestrator/health")
        print(f"✅ v4 Health: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {json.dumps(response.json(), indent=2)[:200]}...")
    except Exception as e:
        print(f"❌ v4 Health failed: {e}")

    # Test v3 system status (compatibility)
    try:
        response = requests.get(f"{API_BASE}/api/v3/system/status")
        print(f"✅ v3 System Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Orchestrator: {data.get('orchestrator', 'Unknown')}")
            print(f"   Status: {data.get('status', 'Unknown')}")
    except Exception as e:
        print(f"❌ v3 System Status failed: {e}")


def test_metrics_endpoint():
    """Test metrics endpoint"""
    print("\n📊 Testing Metrics Endpoint...")

    try:
        response = requests.get(f"{API_BASE}/api/v4/orchestrator/metrics")
        print(f"✅ Metrics: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {json.dumps(response.json(), indent=2)[:200]}...")
    except Exception as e:
        print(f"❌ Metrics failed: {e}")


def test_chat_endpoints():
    """Test chat functionality"""
    print("\n💬 Testing Chat Endpoints...")

    test_query = {
        "query": "What are my current tasks and projects?",
        "user_id": "test_user",
        "session_id": "test_session_123",
    }

    # Test v4 orchestrate endpoint
    try:
        response = requests.post(f"{API_BASE}/api/v4/orchestrate", json=test_query)
        print(f"✅ v4 Orchestrate: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Response: {data.get('response', '')[:100]}...")
            print(
                f"   Intent: {data.get('metadata', {}).get('intent', {}).get('type', 'Unknown')}"
            )
    except Exception as e:
        print(f"❌ v4 Orchestrate failed: {e}")

    # Test v3 chat endpoint (compatibility)
    v3_query = {
        "message": test_query["query"],
        "user_id": test_query["user_id"],
        "session_id": test_query["session_id"],
    }

    try:
        response = requests.post(f"{API_BASE}/api/v3/chat", json=v3_query)
        print(f"✅ v3 Chat (Compatibility): {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Response: {data.get('response', '')[:100]}...")
    except Exception as e:
        print(f"❌ v3 Chat failed: {e}")


def test_streaming_endpoint():
    """Test streaming endpoint"""
    print("\n🌊 Testing Streaming Endpoint...")

    test_query = {
        "query": "Analyze my project health across all systems",
        "user_id": "test_user",
        "session_id": "test_stream_123",
    }

    try:
        response = requests.post(
            f"{API_BASE}/api/v4/orchestrate/stream", json=test_query, stream=True
        )
        print(f"✅ Streaming: {response.status_code}")

        if response.status_code == 200:
            print("   Receiving stream...")
            chunk_count = 0
            for line in response.iter_lines():
                if line:
                    chunk_count += 1
                    if chunk_count <= 3:  # Show first 3 chunks
                        print(f"   Chunk {chunk_count}: {line.decode()[:50]}...")
            print(f"   Total chunks received: {chunk_count}")
    except Exception as e:
        print(f"❌ Streaming failed: {e}")


def test_business_intelligence_queries():
    """Test business intelligence queries"""
    print("\n🧠 Testing Business Intelligence Queries...")

    queries = [
        "What is the project status across Linear and Asana?",
        "Show me recent Gong call insights",
        "Analyze team productivity from Slack data",
    ]

    for query in queries:
        try:
            response = requests.post(
                f"{API_BASE}/api/v4/orchestrate",
                json={
                    "query": query,
                    "user_id": "test_user",
                    "session_id": f"test_bi_{hash(query)}",
                },
            )

            if response.status_code == 200:
                data = response.json()
                intent = data.get("metadata", {}).get("intent", {})
                print(f"✅ Query: '{query[:50]}...'")
                print(f"   Intent: {intent.get('type', 'Unknown')}")
                print(f"   Confidence: {intent.get('confidence', 0)}")
                print(f"   Sources: {data.get('sources', [])}")
            else:
                print(f"❌ Query failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Query error: {e}")


def main():
    """Run all tests"""
    print("🚀 Testing V4 Orchestrator Integration")
    print("=====================================")
    print(f"API Base: {API_BASE}")
    print("Date: July 9, 2025")

    # Check if backend is running
    try:
        response = requests.get(f"{API_BASE}/")
        print(f"\n✅ Backend is running: {response.json().get('service', 'Unknown')}")
    except Exception as e:
        print(f"\n❌ Backend not accessible: {e}")
        print(
            "Please start the backend with: python backend/app/unified_chat_backend.py"
        )
        return

    # Run tests
    test_health_endpoints()
    test_metrics_endpoint()
    test_chat_endpoints()
    test_streaming_endpoint()
    test_business_intelligence_queries()

    print("\n✅ Integration tests complete!")
    print("\nNext steps:")
    print("1. Check for any ❌ failures above")
    print("2. Review backend logs for errors")
    print("3. Update frontend to use v4 endpoints")
    print("4. Complete MCP integration")


if __name__ == "__main__":
    main()
