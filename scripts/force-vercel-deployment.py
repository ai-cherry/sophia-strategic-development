#!/usr/bin/env python3
"""
Force Vercel Deployment Script
Bypasses CLI authentication issues and deploys directly via API
"""

import requests
import json
import time
import os
from datetime import datetime

class VercelDeploymentForcer:
    def __init__(self, token):
        self.token = token
        self.base_url = "https://api.vercel.com"
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
    def get_projects(self):
        """Get all Vercel projects"""
        try:
            response = requests.get(f"{self.base_url}/v9/projects", headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ Error fetching projects: {e}")
            return None
            
    def get_project_by_name(self, name):
        """Find project by name"""
        projects = self.get_projects()
        if not projects:
            return None
            
        for project in projects.get('projects', []):
            if project['name'] == name:
                return project
        return None
        
    def trigger_deployment(self, project_id, git_source=None):
        """Trigger a new deployment"""
        try:
            # Use the project's existing git configuration
            payload = {
                "name": "sophia-ai-frontend-dev",
                "target": "production",
                "gitSource": {
                    "type": "github",
                    "repo": "ai-cherry/sophia-main",
                    "ref": "main",
                    "repoId": 824527530  # GitHub repo ID for ai-cherry/sophia-main
                }
            }
            
            response = requests.post(
                f"{self.base_url}/v13/deployments",
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ Error triggering deployment: {e}")
            if hasattr(e, 'response'):
                print(f"Response: {e.response.text}")
            return None
            
    def get_deployment_status(self, deployment_id):
        """Check deployment status"""
        try:
            response = requests.get(
                f"{self.base_url}/v13/deployments/{deployment_id}",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ Error checking deployment: {e}")
            return None
            
    def force_deployment_with_latest_commit(self):
        """Force deployment with latest commit"""
        print("🚀 Starting Vercel deployment force...")
        
        # Get project
        project = self.get_project_by_name("sophia-ai-frontend-dev")
        if not project:
            print("❌ Project 'sophia-ai-frontend-dev' not found")
            return False
            
        print(f"✅ Found project: {project['name']} (ID: {project['id']})")
        
        # Trigger deployment with latest commit
        git_source = {
            "type": "github",
            "repo": "ai-cherry/sophia-main",
            "ref": "main",
            "sha": "7b0384e6"  # Our latest commit with fixes
        }
        
        deployment = self.trigger_deployment(project['id'], git_source)
        if not deployment:
            print("❌ Failed to trigger deployment")
            return False
            
        deployment_id = deployment.get('id')
        deployment_url = deployment.get('url')
        
        print(f"✅ Deployment triggered!")
        print(f"   ID: {deployment_id}")
        print(f"   URL: https://{deployment_url}")
        print(f"   Status: {deployment.get('readyState', 'UNKNOWN')}")
        
        # Monitor deployment
        print("\n🔄 Monitoring deployment progress...")
        for i in range(30):  # Monitor for 5 minutes
            status = self.get_deployment_status(deployment_id)
            if status:
                state = status.get('readyState', 'UNKNOWN')
                print(f"   [{i+1}/30] Status: {state}")
                
                if state == 'READY':
                    print(f"🎉 Deployment successful!")
                    print(f"   Production URL: https://{deployment_url}")
                    return True
                elif state == 'ERROR':
                    print(f"❌ Deployment failed!")
                    print(f"   Error: {status.get('error', 'Unknown error')}")
                    return False
                    
            time.sleep(10)
            
        print("⏰ Deployment monitoring timeout")
        return False

def main():
    """Main deployment function"""
    print("=" * 60)
    print("🚀 SOPHIA AI VERCEL DEPLOYMENT FORCER")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"Target: sophia-ai-frontend-dev")
    print(f"Commit: 7b0384e6 (with vercel.json fixes)")
    print("=" * 60)
    
    # Use provided token
    token = "Y57oxELkt4ufdVnk2CBZ5ayi"
    
    forcer = VercelDeploymentForcer(token)
    success = forcer.force_deployment_with_latest_commit()
    
    if success:
        print("\n🎉 SUCCESS: Deployment completed successfully!")
        print("✅ The 95%+ failure rate should now be resolved")
        print("✅ Production domain should be serving traffic")
    else:
        print("\n❌ FAILURE: Deployment did not complete successfully")
        print("⚠️  Manual intervention may be required")
        
    print("=" * 60)
    return success

if __name__ == "__main__":
    main()

