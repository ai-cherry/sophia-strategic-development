#!/usr/bin/env python3
"""
Deployment Status Notification for Sophia AI Platform
Sends notifications about deployment status to various channels
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from typing import Dict, Optional


class DeploymentNotifier:
    """Send deployment notifications"""
    
    def __init__(self, status: str, environment: str, commit: str, host: str):
        self.status = status
        self.environment = environment
        self.commit = commit
        self.host = host
        self.timestamp = datetime.utcnow().isoformat()
    
    def get_status_emoji(self) -> str:
        """Get emoji for deployment status"""
        status_emojis = {
            "success": "🎉",
            "failure": "❌",
            "cancelled": "⏹️",
            "skipped": "⏭️"
        }
        return status_emojis.get(self.status, "❓")
    
    def get_status_color(self) -> str:
        """Get color for deployment status"""
        status_colors = {
            "success": "good",
            "failure": "danger",
            "cancelled": "warning",
            "skipped": "#808080"
        }
        return status_colors.get(self.status, "#808080")
    
    def create_slack_message(self) -> Dict:
        """Create Slack message payload"""
        emoji = self.get_status_emoji()
        color = self.get_status_color()
        
        title = f"{emoji} Sophia AI Deployment {self.status.title()}"
        
        # Create rich message
        message = {
            "text": title,
            "attachments": [
                {
                    "color": color,
                    "title": title,
                    "fields": [
                        {
                            "title": "Environment",
                            "value": self.environment.title(),
                            "short": True
                        },
                        {
                            "title": "Host",
                            "value": self.host,
                            "short": True
                        },
                        {
                            "title": "Commit",
                            "value": f"`{self.commit[:8]}`",
                            "short": True
                        },
                        {
                            "title": "Timestamp",
                            "value": self.timestamp,
                            "short": True
                        }
                    ],
                    "footer": "Sophia AI Platform",
                    "footer_icon": "https://github.com/ai-cherry.png"
                }
            ]
        }
        
        # Add specific details based on status
        if self.status == "success":
            message["attachments"][0]["text"] = (
                "✅ All 29 MCP servers deployed successfully\n"
                "✅ Docker Swarm cluster operational\n"
                "✅ Monitoring and alerting active\n"
                "✅ Platform ready for use"
            )
            message["attachments"][0]["fields"].append({
                "title": "Next Steps",
                "value": (
                    "• Verify services in Lambda Labs dashboard\n"
                    "• Run health checks on all MCP servers\n"
                    "• Monitor Grafana dashboards\n"
                    "• Test end-to-end functionality"
                ),
                "short": False
            })
        elif self.status == "failure":
            message["attachments"][0]["text"] = (
                "❌ Deployment failed\n"
                "🔍 Check GitHub Actions logs for details\n"
                "⚠️ Platform may be in degraded state"
            )
            message["attachments"][0]["fields"].append({
                "title": "Action Required",
                "value": (
                    "• Review GitHub Actions workflow logs\n"
                    "• Check Lambda Labs infrastructure status\n"
                    "• Verify secret configuration\n"
                    "• Consider manual deployment if needed"
                ),
                "short": False
            })
        
        return message
    
    def send_slack_notification(self, webhook_url: str) -> bool:
        """Send notification to Slack"""
        if not webhook_url:
            print("⚠️ No Slack webhook URL provided")
            return False
        
        try:
            import requests
            
            message = self.create_slack_message()
            
            response = requests.post(
                webhook_url,
                json=message,
                timeout=10
            )
            
            if response.status_code == 200:
                print("✅ Slack notification sent successfully")
                return True
            else:
                print(f"❌ Slack notification failed: {response.status_code}")
                return False
                
        except ImportError:
            print("⚠️ requests library not available for Slack notifications")
            return False
        except Exception as e:
            print(f"❌ Slack notification error: {e}")
            return False
    
    def send_github_comment(self) -> bool:
        """Send deployment status as GitHub comment"""
        try:
            # Create comment content
            emoji = self.get_status_emoji()
            comment = f"""
## {emoji} Deployment Status: {self.status.title()}

**Environment:** {self.environment}  
**Host:** {self.host}  
**Commit:** `{self.commit}`  
**Timestamp:** {self.timestamp}

"""
            
            if self.status == "success":
                comment += """
### ✅ Deployment Successful

- All 29 MCP servers deployed to Lambda Labs
- Docker Swarm cluster operational
- Monitoring and alerting active
- Platform ready for use

### 🔗 Next Steps

1. Verify services at Lambda Labs dashboard
2. Run health checks on all MCP servers  
3. Monitor Grafana dashboards
4. Test end-to-end functionality
"""
            elif self.status == "failure":
                comment += """
### ❌ Deployment Failed

The automated deployment encountered issues. Please:

1. Review the GitHub Actions workflow logs
2. Check Lambda Labs infrastructure status
3. Verify secret configuration
4. Consider manual deployment if needed

### 🔍 Troubleshooting

Check the deployment artifacts and logs for detailed error information.
"""
            
            # Try to post comment using GitHub CLI
            result = subprocess.run([
                "gh", "pr", "comment", "--body", comment
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ GitHub comment posted successfully")
                return True
            else:
                print(f"⚠️ GitHub comment failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ GitHub comment error: {e}")
            return False
    
    def send_console_notification(self):
        """Send notification to console"""
        emoji = self.get_status_emoji()
        
        print("\n" + "=" * 60)
        print(f"{emoji} SOPHIA AI DEPLOYMENT NOTIFICATION")
        print("=" * 60)
        print(f"📊 Status: {self.status.upper()}")
        print(f"🌍 Environment: {self.environment}")
        print(f"🖥️ Host: {self.host}")
        print(f"📝 Commit: {self.commit}")
        print(f"⏰ Timestamp: {self.timestamp}")
        
        if self.status == "success":
            print("\n🎉 DEPLOYMENT SUCCESSFUL!")
            print("✅ All systems operational")
            print("✅ 29 MCP servers deployed")
            print("✅ Platform ready for use")
        elif self.status == "failure":
            print("\n❌ DEPLOYMENT FAILED!")
            print("⚠️ Check logs for details")
            print("🔧 Manual intervention may be required")
        
        print("=" * 60)
    
    def send_notifications(self):
        """Send notifications to all configured channels"""
        print("📢 Sending deployment notifications...")
        
        # Always send console notification
        self.send_console_notification()
        
        # Send Slack notification if webhook is available
        slack_webhook = os.getenv("SLACK_WEBHOOK")
        if slack_webhook:
            self.send_slack_notification(slack_webhook)
        else:
            print("⚠️ SLACK_WEBHOOK not configured - skipping Slack notification")
        
        # Send GitHub comment (best effort)
        self.send_github_comment()
        
        print("📢 Notification process completed")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Send Sophia AI deployment notifications"
    )
    parser.add_argument(
        "--status", required=True,
        choices=["success", "failure", "cancelled", "skipped"],
        help="Deployment status"
    )
    parser.add_argument(
        "--environment", required=True,
        help="Target environment"
    )
    parser.add_argument(
        "--commit", required=True,
        help="Git commit hash"
    )
    parser.add_argument(
        "--host", required=True,
        help="Deployment host"
    )
    
    args = parser.parse_args()
    
    notifier = DeploymentNotifier(
        args.status, args.environment, args.commit, args.host
    )
    notifier.send_notifications()


if __name__ == "__main__":
    main() 