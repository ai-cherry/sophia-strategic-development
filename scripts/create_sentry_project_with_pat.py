#!/usr/bin/env python3
"""
Enhanced Sentry Project Creation Script for Sophia AI
Uses Personal Access Token to create project and retrieve DSN
"""

import requests
import json
import sys
import os

# Sentry configuration
SENTRY_PAT = "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"
SENTRY_ORG_SLUG = "pay-ready"
SENTRY_PROJECT_SLUG = "sophia-ai"
SENTRY_BASE_URL = "https://sentry.io/api/0"

def test_pat_permissions():
    """Test PAT permissions and available organizations."""
    print("🔍 Testing PAT permissions...")
    
    headers = {
        "Authorization": f"Bearer {SENTRY_PAT}",
        "Content-Type": "application/json"
    }
    
    # Test organizations access
    orgs_url = f"{SENTRY_BASE_URL}/organizations/"
    response = requests.get(orgs_url, headers=headers)
    
    if response.status_code == 200:
        orgs = response.json()
        print(f"✅ PAT has access to {len(orgs)} organizations")
        for org in orgs:
            print(f"  - {org['slug']} ({org['name']})")
        return orgs
    else:
        print(f"❌ Failed to access organizations. Status: {response.status_code}")
        print(f"Response: {response.text}")
        return None

def check_organization_access():
    """Check if we have access to the pay-ready organization."""
    print(f"🔍 Checking access to '{SENTRY_ORG_SLUG}' organization...")
    
    headers = {
        "Authorization": f"Bearer {SENTRY_PAT}",
        "Content-Type": "application/json"
    }
    
    org_url = f"{SENTRY_BASE_URL}/organizations/{SENTRY_ORG_SLUG}/"
    response = requests.get(org_url, headers=headers)
    
    if response.status_code == 200:
        org_data = response.json()
        print(f"✅ Access confirmed to organization: {org_data['name']}")
        return org_data
    else:
        print(f"❌ No access to organization '{SENTRY_ORG_SLUG}'. Status: {response.status_code}")
        print(f"Response: {response.text}")
        return None

def list_existing_projects():
    """List existing projects in the organization."""
    print(f"📋 Listing existing projects in '{SENTRY_ORG_SLUG}'...")
    
    headers = {
        "Authorization": f"Bearer {SENTRY_PAT}",
        "Content-Type": "application/json"
    }
    
    projects_url = f"{SENTRY_BASE_URL}/organizations/{SENTRY_ORG_SLUG}/projects/"
    response = requests.get(projects_url, headers=headers)
    
    if response.status_code == 200:
        projects = response.json()
        print(f"✅ Found {len(projects)} existing projects:")
        for project in projects:
            print(f"  - {project['slug']} ({project['name']})")
        return projects
    else:
        print(f"❌ Failed to list projects. Status: {response.status_code}")
        print(f"Response: {response.text}")
        return None

def create_or_get_project():
    """Create Sentry project or get existing one."""
    
    headers = {
        "Authorization": f"Bearer {SENTRY_PAT}",
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
        "Authorization": f"Bearer {SENTRY_PAT}",
        "Content-Type": "application/json"
    }
    
    keys_url = f"{SENTRY_BASE_URL}/projects/{SENTRY_ORG_SLUG}/{SENTRY_PROJECT_SLUG}/keys/"
    
    response = requests.get(keys_url, headers=headers)
    
    if response.status_code == 200:
        keys = response.json()
        if keys:
            dsn = keys[0].get("dsn", {}).get("public")
            return dsn
    
    print(f"❌ Failed to retrieve DSN. Status: {response.status_code}")
    print(f"Response: {response.text}")
    return None

def main():
    """Main function to create Sentry project and get DSN."""
    
    print("🔧 Sentry Project Setup for Sophia AI (Enhanced)")
    print("===============================================")
    print("")
    
    # Test PAT permissions
    orgs = test_pat_permissions()
    if not orgs:
        print("❌ PAT doesn't have sufficient permissions")
        sys.exit(1)
    
    print("")
    
    # Check organization access
    org_data = check_organization_access()
    if not org_data:
        print("❌ Cannot access the required organization")
        sys.exit(1)
    
    print("")
    
    # List existing projects
    projects = list_existing_projects()
    
    print("")
    
    # Create or get existing project
    project_data = create_or_get_project()
    
    if not project_data:
        print("❌ Failed to create or retrieve project")
        sys.exit(1)
    
    # Get the DSN
    print("🔑 Retrieving project DSN...")
    dsn = get_project_dsn(project_data)
    
    if dsn:
        print(f"✅ Project DSN: {dsn}")
        print("")
        
        # Save DSN to file for easy access
        with open("/tmp/sentry_dsn.txt", "w") as f:
            f.write(dsn)
        
        print("💾 DSN saved to /tmp/sentry_dsn.txt")
        print("")
        print("🚀 Next steps:")
        print("1. DSN will be automatically set in GitHub secrets")
        print("2. Sync workflow will be triggered")
        print("3. Integration will be complete!")
        
        return dsn
        
    else:
        print("❌ Failed to retrieve DSN")
        sys.exit(1)

if __name__ == "__main__":
    dsn = main()
    print(f"\nDSN: {dsn}")

