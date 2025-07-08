#!/usr/bin/env python3
"""Deploy Lambda Labs infrastructure using Pulumi."""

import json
import os
import subprocess
import sys
from pathlib import Path

from pulumi import automation as auto


def deploy_lambda_infrastructure():
    """Deploy Lambda Labs monitoring infrastructure."""
    print("🚀 Deploying Lambda Labs infrastructure with Pulumi...")

    # Set up Pulumi
    project_name = "sophia-ai-lambda"
    stack_name = "production"
    work_dir = Path("infrastructure/pulumi")

    # Ensure Pulumi is logged in
    try:
        subprocess.run(["pulumi", "whoami"], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        print("❌ Pulumi not logged in. Please run: pulumi login")
        sys.exit(1)

    # Create or select stack
    try:
        # Create stack
        stack = auto.create_or_select_stack(
            stack_name=stack_name,
            project_name=project_name,
            program=lambda: None,  # We'll use the TypeScript program
            work_dir=str(work_dir),
        )

        print(f"✅ Using stack: {stack_name}")

        # Set configuration
        print("🔧 Setting configuration...")
        stack.set_config("aws:region", auto.ConfigValue("us-east-1"))
        stack.set_config("environment", auto.ConfigValue("production"))

        # Set secrets from environment
        lambda_api_key = os.getenv("LAMBDA_SERVERLESS_API_KEY")
        slack_webhook = os.getenv("SLACK_WEBHOOK_URL")

        if not lambda_api_key:
            print("❌ LAMBDA_SERVERLESS_API_KEY not set")
            sys.exit(1)

        stack.set_config("lambdaApiKey", auto.ConfigValue(lambda_api_key, secret=True))

        if slack_webhook:
            stack.set_config(
                "slackWebhook", auto.ConfigValue(slack_webhook, secret=True)
            )

        # Install dependencies
        print("📦 Installing dependencies...")
        subprocess.run(["npm", "install"], cwd=work_dir, check=True)

        # Preview changes
        print("👀 Previewing changes...")
        preview_result = stack.preview()

        # Deploy
        print("🚀 Deploying infrastructure...")
        up_result = stack.up()

        # Print outputs
        print("\n✅ Deployment complete!")
        print("\n📊 Outputs:")
        for key, value in up_result.outputs.items():
            print(f"  {key}: {value.value}")

        # Create monitoring dashboard
        create_grafana_dashboard()

        # Set up alerts
        setup_cloudwatch_alerts()

        print("\n🎉 Lambda Labs infrastructure deployed successfully!")

    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        sys.exit(1)


def create_grafana_dashboard():
    """Create Grafana dashboard for Lambda Labs monitoring."""
    print("\n📊 Creating Grafana dashboard...")

    dashboard_config = {
        "dashboard": {
            "title": "Lambda Labs Serverless Monitoring",
            "panels": [
                {
                    "title": "Request Rate",
                    "type": "graph",
                    "targets": [
                        {
                            "expr": "rate(lambda_labs_requests_total[5m])",
                            "legendFormat": "{{model}}",
                        }
                    ],
                },
                {
                    "title": "Cost per Hour",
                    "type": "graph",
                    "targets": [
                        {
                            "expr": "increase(lambda_labs_cost_total[1h])",
                            "legendFormat": "{{model}}",
                        }
                    ],
                },
                {
                    "title": "Response Time",
                    "type": "graph",
                    "targets": [
                        {
                            "expr": "histogram_quantile(0.95, lambda_labs_latency_bucket)",
                            "legendFormat": "p95",
                        }
                    ],
                },
                {
                    "title": "Budget Usage",
                    "type": "gauge",
                    "targets": [{"expr": "lambda_labs_budget_usage_percent"}],
                },
            ],
        }
    }

    # Save dashboard config
    dashboard_path = Path("config/grafana/dashboards/lambda-labs.json")
    dashboard_path.parent.mkdir(parents=True, exist_ok=True)

    with open(dashboard_path, "w") as f:
        json.dump(dashboard_config, f, indent=2)

    print(f"✅ Dashboard saved to: {dashboard_path}")


def setup_cloudwatch_alerts():
    """Set up CloudWatch alerts for Lambda Labs."""
    print("\n🚨 Setting up CloudWatch alerts...")

    alerts = [
        {
            "name": "lambda-labs-budget-80-percent",
            "description": "Alert when Lambda Labs budget reaches 80%",
            "metric": "BudgetUsagePercent",
            "threshold": 80,
            "comparison": "GreaterThanThreshold",
        },
        {
            "name": "lambda-labs-high-error-rate",
            "description": "Alert on high error rate",
            "metric": "ErrorRate",
            "threshold": 0.05,  # 5%
            "comparison": "GreaterThanThreshold",
        },
        {
            "name": "lambda-labs-high-latency",
            "description": "Alert on high latency",
            "metric": "ResponseTime",
            "threshold": 5000,  # 5 seconds
            "comparison": "GreaterThanThreshold",
        },
    ]

    # Save alert configurations
    alerts_path = Path("config/cloudwatch/alerts/lambda-labs.json")
    alerts_path.parent.mkdir(parents=True, exist_ok=True)

    with open(alerts_path, "w") as f:
        json.dump(alerts, f, indent=2)

    print(f"✅ Alerts configured: {len(alerts)} alerts")


if __name__ == "__main__":
    deploy_lambda_infrastructure()
