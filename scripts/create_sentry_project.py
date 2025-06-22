#!/usr/bin/env python3
"""
Sentry Project Creation Script for Sophia AI
Creates a new Sentry project and retrieves the DSN
"""

import requests
import json
import sys
import os

# Sentry configuration
SENTRY_API_TOKEN = "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"
SENTRY_ORG_SLUG = "pay-ready"
SENTRY_PROJECT_SLUG = "sophia-ai"
SENTRY_BASE_URL = "https://sentry.io/api/0"

def create_sentry_project():
    """Create a new Sentry project for Sophia AI."""
    
    headers = {
        "Authorization": f"Bearer {SENTRY_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # First, check if project already exists
    print(f"🔍 Checking if project '{SENTRY_PROJECT_SLUG}' already exists...")
    
    check_url = f"{SENTRY_BASE_URL}/projects/{SENTRY_ORG_SLUG}/{SENTRY_PROJECT_SLUG}/"
    response = requests.get(check_url, headers=headers)
    
    if response.status_code == 200:
        print(f"✅ Project '{SENTRY_PROJECT_SLUG}' already exists!")
        project_data = response.json()
        return project_data
    
    # Create new project
    print(f"🚀 Creating new Sentry project '{SENTRY_PROJECT_SLUG}'...")
    
    create_url = f"{SENTRY_BASE_URL}/organizations/{SENTRY_ORG_SLUG}/projects/"
    
    project_data = {
        "name": "Sophia AI",
        "slug": SENTRY_PROJECT_SLUG,
        "platform": "python",
        "defaultRules": True
    }
    
    response = requests.post(create_url, headers=headers, json=project_data)
    
    if response.status_code == 201:
        print(f"✅ Successfully created project '{SENTRY_PROJECT_SLUG}'!")
        return response.json()
    else:
        print(f"❌ Failed to create project. Status: {response.status_code}")
        print(f"Response: {response.text}")
        return None

def get_project_dsn(project_data):
    """Extract DSN from project data."""
    
    if not project_data:
        return None
    
    # Get project keys to find the DSN
    headers = {
        "Authorization": f"Bearer {SENTRY_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    project_id = project_data.get("id")
    keys_url = f"{SENTRY_BASE_URL}/projects/{SENTRY_ORG_SLUG}/{SENTRY_PROJECT_SLUG}/keys/"
    
    response = requests.get(keys_url, headers=headers)
    
    if response.status_code == 200:
        keys = response.json()
        if keys:
            dsn = keys[0].get("dsn", {}).get("public")
            return dsn
    
    return None

def update_github_secret(dsn):
    """Update GitHub secret with the DSN."""
    
    print(f"📝 To set the SENTRY_DSN secret in GitHub, run:")
    print(f"   echo '{dsn}' | gh secret set SENTRY_DSN --org ai-cherry --visibility all")
    print("")
    
    # Also save to a file for easy access
    with open("/tmp/sentry_dsn.txt", "w") as f:
        f.write(dsn)
    
    print(f"💾 DSN saved to /tmp/sentry_dsn.txt")

def main():
    """Main function to create Sentry project and get DSN."""
    
    print("🔧 Sentry Project Setup for Sophia AI")
    print("=====================================")
    print("")
    
    # Create or get existing project
    project_data = create_sentry_project()
    
    if not project_data:
        print("❌ Failed to create or retrieve project")
        sys.exit(1)
    
    # Get the DSN
    print("🔑 Retrieving project DSN...")
    dsn = get_project_dsn(project_data)
    
    if dsn:
        print(f"✅ Project DSN: {dsn}")
        print("")
        
        # Provide instructions for setting GitHub secret
        update_github_secret(dsn)
        
        print("")
        print("🚀 Next steps:")
        print("1. Set the SENTRY_DSN GitHub secret using the command above")
        print("2. Run the sync workflow: gh workflow run sync-sentry-secrets.yml --repo ai-cherry/sophia-main")
        print("3. Test the integration: python scripts/test/test_sentry_agent.py")
        
    else:
        print("❌ Failed to retrieve DSN")
        sys.exit(1)

if __name__ == "__main__":
    main()

