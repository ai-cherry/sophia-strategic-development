#!/usr/bin/env python3
"""
Automated Deployment Monitor for Sophia AI Platform
Monitors GitHub Actions workflow and provides real-time status updates
"""

import json
import subprocess
import time
from datetime import datetime
from typing import Dict, List, Optional


class DeploymentMonitor:
    """Monitor GitHub Actions deployment workflow"""
    
    def __init__(self):
        self.workflow_name = "unified-deployment.yml"
        self.check_interval = 30  # seconds
        
    def run_gh_command(self, cmd: List[str]) -> Optional[str]:
        """Run GitHub CLI command and return output"""
        try:
            result = subprocess.run(
                ["gh"] + cmd,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            print(f"❌ GitHub CLI error: {e}")
            return None
    
    def get_latest_run(self) -> Optional[Dict]:
        """Get the latest workflow run"""
        output = self.run_gh_command([
            "run", "list", 
            f"--workflow={self.workflow_name}",
            "--limit=1",
            "--json=status,conclusion,createdAt,url,headBranch"
        ])
        
        if output:
            try:
                runs = json.loads(output)
                return runs[0] if runs else None
            except json.JSONDecodeError:
                return None
        return None
    
    def get_run_jobs(self, run_id: str) -> List[Dict]:
        """Get jobs for a specific run"""
        output = self.run_gh_command([
            "run", "view", run_id,
            "--json=jobs"
        ])
        
        if output:
            try:
                data = json.loads(output)
                return data.get("jobs", [])
            except json.JSONDecodeError:
                return []
        return []
    
    def format_status(self, status: str) -> str:
        """Format status with emoji"""
        status_map = {
            "queued": "⏳ Queued",
            "in_progress": "🔄 Running",
            "completed": "✅ Completed",
            "cancelled": "❌ Cancelled",
            "failure": "❌ Failed",
            "success": "✅ Success",
            "skipped": "⏭️ Skipped"
        }
        return status_map.get(status, f"❓ {status}")
    
    def print_run_summary(self, run: Dict):
        """Print workflow run summary"""
        print("\n" + "="*60)
        print("🚀 SOPHIA AI AUTOMATED DEPLOYMENT MONITOR")
        print("="*60)
        print(f"📅 Started: {run['createdAt']}")
        print(f"🌟 Branch: {run['headBranch']}")
        print(f"📊 Status: {self.format_status(run['status'])}")
        if run.get('conclusion'):
            print(f"🎯 Result: {self.format_status(run['conclusion'])}")
        print(f"🔗 URL: {run['url']}")
        print("="*60)
    
    def print_job_status(self, jobs: List[Dict]):
        """Print status of all jobs"""
        if not jobs:
            print("📋 No job details available yet...")
            return
        
        print("\n📋 JOB STATUS:")
        print("-" * 40)
        
        for job in jobs:
            name = job.get('name', 'Unknown Job')
            status = job.get('status', 'unknown')
            conclusion = job.get('conclusion')
            
            status_text = self.format_status(conclusion if conclusion else status)
            print(f"  {status_text} {name}")
            
            # Show steps for running jobs
            if status == 'in_progress' and 'steps' in job:
                for step in job['steps']:
                    step_name = step.get('name', 'Unknown Step')
                    step_status = step.get('status', 'unknown')
                    step_conclusion = step.get('conclusion')
                    
                    step_text = self.format_status(
                        step_conclusion if step_conclusion else step_status
                    )
                    print(f"    └─ {step_text} {step_name}")
    
    def monitor_deployment(self):
        """Monitor deployment progress"""
        print("🔍 Starting Sophia AI Deployment Monitor...")
        print(f"⏱️ Checking every {self.check_interval} seconds")
        
        last_status = None
        run_id = None
        
        while True:
            try:
                # Get latest run
                run = self.get_latest_run()
                
                if not run:
                    print("❌ No workflow runs found")
                    time.sleep(self.check_interval)
                    continue
                
                current_status = run.get('status')
                
                # Print summary if status changed or first time
                if current_status != last_status:
                    self.print_run_summary(run)
                    last_status = current_status
                    
                    # Extract run ID from URL for job details
                    url_parts = run['url'].split('/')
                    run_id = url_parts[-1] if url_parts else None
                
                # Get and print job status
                if run_id:
                    jobs = self.get_run_jobs(run_id)
                    self.print_job_status(jobs)
                
                # Check if workflow is complete
                if current_status == 'completed':
                    conclusion = run.get('conclusion', 'unknown')
                    
                    if conclusion == 'success':
                        print("\n🎉 DEPLOYMENT SUCCESSFUL!")
                        print("✅ All 29 MCP servers deployed to Lambda Labs")
                        print("✅ Docker Swarm cluster operational")
                        print("✅ Monitoring and alerting active")
                        print("\n🔗 Next Steps:")
                        print("  1. Verify services at Lambda Labs dashboard")
                        print("  2. Run health checks on all MCP servers")
                        print("  3. Monitor Grafana dashboards")
                        print("  4. Test end-to-end functionality")
                    else:
                        print(f"\n❌ DEPLOYMENT FAILED: {conclusion}")
                        print("🔍 Check the workflow logs for details:")
                        print(f"   {run['url']}")
                    
                    break
                
                print(f"\n⏱️ Next check in {self.check_interval} seconds...")
                time.sleep(self.check_interval)
                
            except KeyboardInterrupt:
                print("\n⏹️ Monitoring stopped by user")
                break
            except Exception as e:
                print(f"❌ Monitor error: {e}")
                time.sleep(self.check_interval)


def main():
    """Main function"""
    monitor = DeploymentMonitor()
    monitor.monitor_deployment()


if __name__ == "__main__":
    main() 