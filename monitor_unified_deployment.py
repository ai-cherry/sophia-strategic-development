#!/usr/bin/env python3
"""
Monitor Sophia AI Unified Deployment Progress
"""

import json
import subprocess
import time
from datetime import datetime


def get_latest_run():
    """Get the latest workflow run"""
    cmd = [
        "gh", "run", "list",
        "--workflow=sophia-unified-deployment.yml",
        "--limit", "1",
        "--json", "databaseId,status,conclusion,createdAt,headBranch,name"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0 and result.stdout:
        runs = json.loads(result.stdout)
        return runs[0] if runs else None
    return None


def get_run_jobs(run_id):
    """Get jobs for a specific run"""
    cmd = [
        "gh", "run", "view", str(run_id),
        "--json", "jobs"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0 and result.stdout:
        data = json.loads(result.stdout)
        return data.get("jobs", [])
    return []


def print_status(run, jobs):
    """Print deployment status"""
    print("\033[2J\033[H")  # Clear screen
    print("=" * 80)
    print("🚀 SOPHIA AI UNIFIED DEPLOYMENT MONITOR")
    print("=" * 80)
    
    if run:
        status_emoji = {
            "in_progress": "⏳",
            "completed": "✅" if run.get("conclusion") == "success" else "❌",
            "queued": "🔄"
        }.get(run["status"], "❓")
        
        print(f"\n📅 Started: {run['createdAt']}")
        print(f"🌿 Branch: {run['headBranch']}")
        print(f"{status_emoji} Status: {run['status'].upper()}")
        if run.get("conclusion"):
            print(f"📊 Result: {run['conclusion'].upper()}")
        
        print(f"\n{'JOB':<30} {'STATUS':<15} {'RESULT':<15}")
        print("-" * 60)
        
        for job in jobs:
            job_status = job.get("status", "pending")
            job_conclusion = job.get("conclusion", "-")
            
            status_emoji = {
                "in_progress": "⏳",
                "completed": "✅" if job_conclusion == "success" else "❌",
                "queued": "🔄",
                "pending": "⏸️"
            }.get(job_status, "❓")
            
            print(f"{job['name']:<30} {status_emoji} {job_status:<12} {job_conclusion:<15}")
    
    print("\n" + "=" * 80)
    print(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Press Ctrl+C to exit")


def main():
    """Main monitoring loop"""
    print("Starting deployment monitor...")
    
    try:
        while True:
            run = get_latest_run()
            if run:
                jobs = get_run_jobs(run["databaseId"])
                print_status(run, jobs)
                
                # Exit if deployment is complete
                if run["status"] == "completed":
                    print("\n🎉 Deployment complete!")
                    if run.get("conclusion") == "success":
                        print("✅ All systems deployed successfully!")
                        print("\n📌 Access your deployment:")
                        print("   - API: http://192.222.51.122:8000")
                        print("   - Grafana: http://192.222.51.122:3000")
                        print("   - Frontend: https://app.sophia-intel.ai")
                    else:
                        print("❌ Deployment failed. Check the logs for details.")
                    break
            
            time.sleep(5)  # Update every 5 seconds
            
    except KeyboardInterrupt:
        print("\n\n👋 Monitoring stopped.")


if __name__ == "__main__":
    main() 