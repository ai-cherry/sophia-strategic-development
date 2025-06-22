#!/usr/bin/env python3
"""
Updated Sentry Project Creation Script for Sophia AI
Uses team-based approach for project creation
"""

import requests
import json
import sys
import os

# Sentry configuration
SENTRY_PAT = "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"
SENTRY_ORG_SLUG = "pay-ready"
SENTRY_PROJECT_SLUG = "sophia-ai"
SENTRY_TEAM_SLUG = "pay-ready"  # From the API response
SENTRY_BASE_URL = "https://sentry.io/api/0"

def create_project_via_team():
    """Create project using team-based endpoint."""
    
    headers = {
        "Authorization": f"Bearer {SENTRY_PAT}",
        "Content-Type": "application/json"
    }
    
    print(f"🚀 Creating project '{SENTRY_PROJECT_SLUG}' via team '{SENTRY_TEAM_SLUG}'...")
    
    # Try team-based project creation
    create_url = f"{SENTRY_BASE_URL}/teams/{SENTRY_ORG_SLUG}/{SENTRY_TEAM_SLUG}/projects/"
    
    project_data = {
        "name": "Sophia AI",
        "slug": SENTRY_PROJECT_SLUG,
        "platform": "python"
    }
    
    response = requests.post(create_url, headers=headers, json=project_data)
    
    if response.status_code == 201:
        print(f"✅ Successfully created project '{SENTRY_PROJECT_SLUG}' via team!")
        return response.json()
    else:
        print(f"❌ Team-based creation failed. Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        # Try direct organization endpoint with different payload
        print("🔄 Trying alternative organization endpoint...")
        
        alt_url = f"{SENTRY_BASE_URL}/organizations/{SENTRY_ORG_SLUG}/projects/"
        alt_data = {
            "name": "Sophia AI",
            "slug": SENTRY_PROJECT_SLUG,
            "team": SENTRY_TEAM_SLUG,
            "platform": "python"
        }
        
        alt_response = requests.post(alt_url, headers=headers, json=alt_data)
        
        if alt_response.status_code == 201:
            print(f"✅ Successfully created project '{SENTRY_PROJECT_SLUG}' via organization!")
            return alt_response.json()
        else:
            print(f"❌ Alternative creation failed. Status: {alt_response.status_code}")
            print(f"Response: {alt_response.text}")
            return None

def get_project_keys(project_data):
    """Get project keys and DSN."""
    
    if not project_data:
        return None
    
    headers = {
        "Authorization": f"Bearer {SENTRY_PAT}",
        "Content-Type": "application/json"
    }
    
    print("🔑 Retrieving project keys...")
    
    # Get project keys
    keys_url = f"{SENTRY_BASE_URL}/projects/{SENTRY_ORG_SLUG}/{SENTRY_PROJECT_SLUG}/keys/"
    
    response = requests.get(keys_url, headers=headers)
    
    if response.status_code == 200:
        keys = response.json()
        if keys:
            key_data = keys[0]
            dsn = key_data.get("dsn", {}).get("public")
            print(f"✅ Retrieved DSN: {dsn}")
            return dsn
        else:
            print("⚠️ No keys found, creating default key...")
            # Create a default key
            create_key_response = requests.post(keys_url, headers=headers, json={"name": "Default"})
            if create_key_response.status_code == 201:
                key_data = create_key_response.json()
                dsn = key_data.get("dsn", {}).get("public")
                print(f"✅ Created key and retrieved DSN: {dsn}")
                return dsn
    
    print(f"❌ Failed to retrieve keys. Status: {response.status_code}")
    print(f"Response: {response.text}")
    return None

def main():
    """Main function."""
    
    print("🔧 Sentry Project Creation for Sophia AI (Team-based)")
    print("====================================================")
    print("")
    
    # Create project
    project_data = create_project_via_team()
    
    if not project_data:
        print("❌ Failed to create project")
        sys.exit(1)
    
    print("")
    print(f"✅ Project created successfully!")
    print(f"   Name: {project_data.get('name')}")
    print(f"   Slug: {project_data.get('slug')}")
    print(f"   ID: {project_data.get('id')}")
    print("")
    
    # Get DSN
    dsn = get_project_keys(project_data)
    
    if dsn:
        print("")
        print(f"🎉 SUCCESS! Project '{SENTRY_PROJECT_SLUG}' created with DSN:")
        print(f"   {dsn}")
        
        # Save DSN to file
        with open("/tmp/sentry_dsn.txt", "w") as f:
            f.write(dsn)
        
        print("")
        print("💾 DSN saved to /tmp/sentry_dsn.txt")
        print("")
        print("🚀 Ready for GitHub secret update and workflow sync!")
        
        return dsn
    else:
        print("❌ Failed to retrieve DSN")
        sys.exit(1)

if __name__ == "__main__":
    dsn = main()
    print(f"\nFinal DSN: {dsn}")

