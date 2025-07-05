#!/usr/bin/env python3
"""Deploy Grafana dashboards for Sophia AI monitoring"""
import json
import os
import sys
from pathlib import Path

import requests

# Configuration
GRAFANA_URL = os.getenv("GRAFANA_URL", "http://localhost:3000")
GRAFANA_API_KEY = os.getenv("GRAFANA_API_KEY", "")
DASHBOARD_DIR = Path("infrastructure/monitoring/grafana-dashboards")


def deploy_dashboard(dashboard_file: Path):
    """Deploy a single dashboard to Grafana"""

    # Read dashboard JSON
    with open(dashboard_file) as f:
        dashboard_json = json.load(f)

    # Prepare API payload
    payload = {
        "dashboard": dashboard_json,
        "overwrite": True,
        "message": f"Automated deployment of {dashboard_file.name}",
    }

    # API headers
    headers = {
        "Authorization": f"Bearer {GRAFANA_API_KEY}",
        "Content-Type": "application/json",
    }

    # Deploy dashboard
    try:
        response = requests.post(
            f"{GRAFANA_URL}/api/dashboards/db", headers=headers, json=payload
        )
        response.raise_for_status()

        response.json()
        return True

    except requests.exceptions.RequestException as e:
        if (
            hasattr(e, "response")
            and e.response is not None
            and hasattr(e.response, "text")
        ):
            pass
        return False


def main():
    """Deploy all Grafana dashboards"""

    # Check for API key
    if not GRAFANA_API_KEY:
        sys.exit(1)

    # Check if dashboard directory exists
    if not DASHBOARD_DIR.exists():
        sys.exit(1)

    # Find all dashboard JSON files
    dashboard_files = list(DASHBOARD_DIR.glob("*.json"))

    if not dashboard_files:
        sys.exit(1)

    # Deploy each dashboard
    success_count = 0
    for dashboard_file in dashboard_files:
        if deploy_dashboard(dashboard_file):
            success_count += 1

    # Summary

    if success_count < len(dashboard_files):
        sys.exit(1)


if __name__ == "__main__":
    main()
