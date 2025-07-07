#!/usr/bin/env python3
"""
Deployment Status Notification
Sends deployment status to Slack and other channels
"""

import argparse
import json
import os
from datetime import datetime

import requests


def send_slack_notification(
    webhook_url: str, status: str, environment: str, commit: str, host: str
):
    """Send Slack notification"""
    if not webhook_url:
        print("⚠️ No Slack webhook configured, skipping notification")
        return

    color = "good" if status == "success" else "danger"
    emoji = "✅" if status == "success" else "❌"

    payload = {
        "attachments": [
            {
                "color": color,
                "title": f"{emoji} Sophia AI Deployment {status.title()}",
                "fields": [
                    {"title": "Environment", "value": environment, "short": True},
                    {"title": "Host", "value": host, "short": True},
                    {"title": "Commit", "value": commit[:8], "short": True},
                    {
                        "title": "Timestamp",
                        "value": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
                        "short": True,
                    },
                ],
            }
        ]
    }

    try:
        response = requests.post(webhook_url, json=payload)
        if response.status_code == 200:
            print("📱 Slack notification sent successfully")
        else:
            print(f"⚠️ Slack notification failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Slack notification error: {e}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--status", required=True, choices=["success", "failure"])
    parser.add_argument("--environment", default="production")
    parser.add_argument("--commit", required=True)
    parser.add_argument("--host", required=True)
    args = parser.parse_args()

    # Send Slack notification
    slack_webhook = os.getenv("SLACK_WEBHOOK")
    if slack_webhook:
        send_slack_notification(
            slack_webhook, args.status, args.environment, args.commit, args.host
        )

    print(f"📢 Deployment notification sent: {args.status}")


if __name__ == "__main__":
    main()
