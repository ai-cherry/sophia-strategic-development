#!/usr/bin/env python3
"""
Test Real Linear API Integration
Tests the Linear GraphQL API with real credentials
"""

import sys
import asyncio
import json
from pathlib import Path

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import httpx
from backend.core.auto_esc_config import get_config_value

async def test_linear_api():
    """Test Linear API connection and basic queries"""
    
    print("🔍 Testing Linear API Integration...")
    
    # Get API credentials
    api_key = get_config_value("linear_api_key")
    if not api_key or api_key == "NOT_FOUND":
        print("❌ Linear API key not found in configuration")
        return False
    
    api_url = "https://api.linear.app/graphql"
    headers = {
        "Authorization": api_key,
        "Content-Type": "application/json",
    }
    
    # Test 1: Basic viewer query
    print("\n1. Testing viewer query...")
    viewer_query = """
    query {
        viewer {
            id
            name
            email
            organization {
                name
            }
        }
    }
    """
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                api_url,
                headers=headers,
                json={"query": viewer_query}
            )
            
            if response.status_code == 200:
                data = response.json()
                if "errors" in data:
                    print(f"❌ GraphQL errors: {data['errors']}")
                    return False
                
                viewer = data.get("data", {}).get("viewer", {})
                print(f"✅ Connected as: {viewer.get('name')} ({viewer.get('email')})")
                print(f"✅ Organization: {viewer.get('organization', {}).get('name')}")
            else:
                print(f"❌ HTTP error: {response.status_code} - {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False
    
    # Test 2: List teams
    print("\n2. Testing teams query...")
    teams_query = """
    query {
        teams {
            nodes {
                id
                name
                key
                description
            }
        }
    }
    """
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                api_url,
                headers=headers,
                json={"query": teams_query}
            )
            
            if response.status_code == 200:
                data = response.json()
                teams = data.get("data", {}).get("teams", {}).get("nodes", [])
                print(f"✅ Found {len(teams)} teams:")
                for team in teams[:3]:  # Show first 3 teams
                    print(f"   - {team.get('name')} ({team.get('key')})")
            else:
                print(f"❌ Teams query failed: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Teams query error: {e}")
        return False
    
    # Test 3: List recent issues
    print("\n3. Testing issues query...")
    issues_query = """
    query {
        issues(first: 5) {
            nodes {
                id
                identifier
                title
                state {
                    name
                }
                assignee {
                    name
                }
                team {
                    name
                    key
                }
                createdAt
            }
        }
    }
    """
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                api_url,
                headers=headers,
                json={"query": issues_query}
            )
            
            if response.status_code == 200:
                data = response.json()
                issues = data.get("data", {}).get("issues", {}).get("nodes", [])
                print(f"✅ Found {len(issues)} recent issues:")
                for issue in issues:
                    assignee = issue.get("assignee", {}).get("name", "Unassigned")
                    team = issue.get("team", {}).get("key", "No team")
                    state = issue.get("state", {}).get("name", "Unknown")
                    print(f"   - {issue.get('identifier')}: {issue.get('title')[:50]}...")
                    print(f"     Team: {team}, State: {state}, Assignee: {assignee}")
            else:
                print(f"❌ Issues query failed: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Issues query error: {e}")
        return False
    
    print("\n✅ All Linear API tests passed!")
    return True

async def main():
    """Main test function"""
    success = await test_linear_api()
    if success:
        print("\n🎉 Linear API integration is working!")
        print("Ready to implement real data integration.")
    else:
        print("\n❌ Linear API integration failed!")
        print("Check API key and permissions.")
    
    return success

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1) 