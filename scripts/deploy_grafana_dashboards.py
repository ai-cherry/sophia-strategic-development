#!/usr/bin/env python3
"""Deploy Grafana dashboards for Sophia AI monitoring"""
import json
import os
import requests
import sys
from pathlib import Path

# Configuration
GRAFANA_URL = os.getenv("GRAFANA_URL", "http://localhost:3000")
GRAFANA_API_KEY = os.getenv("GRAFANA_API_KEY", "")
DASHBOARD_DIR = Path("infrastructure/monitoring/grafana-dashboards")

def deploy_dashboard(dashboard_file: Path):
    """Deploy a single dashboard to Grafana"""
    print(f"Deploying dashboard: {dashboard_file.name}")
    
    # Read dashboard JSON
    with open(dashboard_file, 'r') as f:
        dashboard_json = json.load(f)
    
    # Prepare API payload
    payload = {
        "dashboard": dashboard_json,
        "overwrite": True,
        "message": f"Automated deployment of {dashboard_file.name}"
    }
    
    # API headers
    headers = {
        "Authorization": f"Bearer {GRAFANA_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Deploy dashboard
    try:
        response = requests.post(
            f"{GRAFANA_URL}/api/dashboards/db",
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        
        result = response.json()
        print(f"✅ Dashboard deployed successfully!")
        print(f"   URL: {GRAFANA_URL}{result.get('url', '')}")
        print(f"   UID: {result.get('uid', '')}")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to deploy dashboard: {e}")
        if hasattr(e, 'response') and e.response is not None and hasattr(e.response, 'text'):
            print(f"   Error details: {e.response.text}")
        return False

def main():
    """Deploy all Grafana dashboards"""
    print("🚀 Sophia AI Grafana Dashboard Deployment")
    print("=" * 50)
    
    # Check for API key
    if not GRAFANA_API_KEY:
        print("❌ Error: GRAFANA_API_KEY environment variable not set")
        print("   Generate an API key from Grafana UI:")
        print(f"   {GRAFANA_URL}/org/apikeys")
        sys.exit(1)
    
    # Check if dashboard directory exists
    if not DASHBOARD_DIR.exists():
        print(f"❌ Dashboard directory not found: {DASHBOARD_DIR}")
        sys.exit(1)
    
    # Find all dashboard JSON files
    dashboard_files = list(DASHBOARD_DIR.glob("*.json"))
    
    if not dashboard_files:
        print(f"❌ No dashboard JSON files found in {DASHBOARD_DIR}")
        sys.exit(1)
    
    print(f"Found {len(dashboard_files)} dashboard(s) to deploy")
    print()
    
    # Deploy each dashboard
    success_count = 0
    for dashboard_file in dashboard_files:
        if deploy_dashboard(dashboard_file):
            success_count += 1
        print()
    
    # Summary
    print("=" * 50)
    print(f"Deployment complete: {success_count}/{len(dashboard_files)} dashboards deployed")
    
    if success_count < len(dashboard_files):
        sys.exit(1)

if __name__ == "__main__":
    main() 