#!/usr/bin/env python3
"""Monitor Sophia AI deployment progress in real-time."""

import json
import subprocess
import sys
import time
from datetime import datetime


def get_workflow_runs() -> list[dict]:
    """Get recent workflow runs from GitHub API."""
    cmd = [
        "curl",
        "-s",
        "-H",
        f"Authorization: token {subprocess.check_output(['gh', 'auth', 'token']).decode().strip()}",
        "https://api.github.com/repos/ai-cherry/sophia-main/actions/runs?per_page=10",
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if result.returncode == 0:
        data = json.loads(result.stdout)
        return data.get("workflow_runs", [])
    return []


def get_job_details(run_id: str) -> list[dict]:
    """Get job details for a specific run."""
    cmd = [
        "curl",
        "-s",
        "-H",
        f"Authorization: token {subprocess.check_output(['gh', 'auth', 'token']).decode().strip()}",
        f"https://api.github.com/repos/ai-cherry/sophia-main/actions/runs/{run_id}/jobs",
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if result.returncode == 0:
        data = json.loads(result.stdout)
        return data.get("jobs", [])
    return []


def format_duration(start_time: str, end_time: str = None) -> str:
    """Format duration between two times."""
    start = datetime.fromisoformat(start_time.replace("Z", "+00:00"))

    if end_time:
        end = datetime.fromisoformat(end_time.replace("Z", "+00:00"))
    else:
        end = datetime.now(start.tzinfo)

    duration = end - start
    minutes = int(duration.total_seconds() / 60)
    seconds = int(duration.total_seconds() % 60)

    return f"{minutes}m {seconds}s"


def print_status():
    """Print current deployment status."""
    print("\033[2J\033[H")  # Clear screen
    print("=" * 80)
    print(
        f"🚀 SOPHIA AI DEPLOYMENT MONITOR - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    print("=" * 80)
    print()

    runs = get_workflow_runs()

    # Filter for our deployments
    deployment_runs = []
    for run in runs[:5]:  # Check last 5 runs
        if run["name"] in [
            "🚀 Sophia AI Production Deployment",
            "Deploy V2 MCP Servers",
        ]:
            deployment_runs.append(run)

    if not deployment_runs:
        print("⏳ No active deployments found...")
        return

    for run in deployment_runs:
        status_icon = {
            "queued": "⏳",
            "in_progress": "🔄",
            "completed": "✅" if run["conclusion"] == "success" else "❌",
        }.get(run["status"], "❓")

        print(f"{status_icon} {run['name']}")
        print(f"   Status: {run['status'].upper()}")
        if run["conclusion"]:
            print(f"   Result: {run['conclusion'].upper()}")
        print(f"   Started: {run['created_at']}")
        print(f"   Duration: {format_duration(run['created_at'], run['updated_at'])}")
        print(f"   URL: {run['html_url']}")
        print()

        # Get job details if in progress
        if run["status"] == "in_progress":
            jobs = get_job_details(run["id"])
            for job in jobs:
                job_icon = {
                    "queued": "⏳",
                    "in_progress": "🔄",
                    "completed": "✅" if job["conclusion"] == "success" else "❌",
                }.get(job["status"], "❓")

                print(f"   {job_icon} {job['name']}")
                if job["status"] == "in_progress" and job["steps"]:
                    current_step = next(
                        (s for s in job["steps"] if s["status"] == "in_progress"), None
                    )
                    if current_step:
                        print(f"      └─ {current_step['name']}")
            print()

    print("\n" + "=" * 80)
    print("Press Ctrl+C to exit")


def main():
    """Main monitoring loop."""
    print("Starting deployment monitor...")

    try:
        while True:
            print_status()
            time.sleep(5)  # Refresh every 5 seconds
    except KeyboardInterrupt:
        print("\n\n✋ Monitoring stopped.")
        sys.exit(0)


if __name__ == "__main__":
    main()
