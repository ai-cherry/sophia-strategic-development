#!/usr/bin/env python3
"""Sophia AI - Pulumi IDP Main Infrastructure.

Replaces Retool with AI-powered dashboard platform
"""import pulumi

from components.dashboard_platform import DashboardPlatform, DashboardPlatformArgs
from pulumi import Config, export

# Get configuration
config = Config()
environment = config.get("environment") or "development"
region = config.get("region") or "us-east-1"

# Pulumi stack and project info
stack_name = pulumi.get_stack()
project_name = pulumi.get_project()

# Configuration for dashboard platform
dashboard_platform_args = DashboardPlatformArgs(
    name="sophia-ai",
    environment=environment,
    region=region,
    availability_zones=[f"{region}a", f"{region}b"],
    backend_url=config.get("backend_url") or "http://localhost:8000",
    dashboard_types=["ceo", "knowledge", "project", "ai-generator"],
)

# Create the dashboard platform
dashboard_platform = DashboardPlatform(
    "sophia-dashboard-platform", dashboard_platform_args
)

# Export important outputs
export("dashboard_platform_url", dashboard_platform.outputs["dashboard_url"])
export("dashboard_services", dashboard_platform.outputs["dashboard_services"])
export("cluster_name", dashboard_platform.outputs["cluster_name"])
export("vpc_id", dashboard_platform.outputs["vpc_id"])

# Export individual dashboard URLs
export(
    "ceo_dashboard_url",
    pulumi.Output.concat(dashboard_platform.outputs["dashboard_url"], "/ceo"),
)
export(
    "knowledge_dashboard_url",
    pulumi.Output.concat(dashboard_platform.outputs["dashboard_url"], "/knowledge"),
)
export(
    "project_dashboard_url",
    pulumi.Output.concat(dashboard_platform.outputs["dashboard_url"], "/project"),
)
export(
    "ai_generator_url",
    pulumi.Output.concat(dashboard_platform.outputs["dashboard_url"], "/ai-generator"),
)

# Export deployment information
export(
    "deployment_info",
    {
        "project": project_name,
        "stack": stack_name,
        "environment": environment,
        "region": region,
        "platform": "Pulumi IDP",
        "replaces": "Retool",
        "ai_powered": True,
        "natural_language_generation": True,
    },
)

print(
    f"""🚀 Sophia AI - Pulumi IDP Dashboard Platform Deployment.

Stack: {stack_name}
Environment: {environment}
Region: {region}

This deployment replaces Retool with:
✅ Self-hosted dashboard platform
✅ AI-powered dashboard generation
✅ Natural language dashboard creation
✅ Full infrastructure as code
✅ No vendor lock-in
✅ Cost optimization
✅ Enhanced security and compliance

Dashboard Services:
- CEO Dashboard: Strategic intelligence and business insights
- Knowledge Dashboard: AI-powered knowledge management
- Project Dashboard: Unified project intelligence
- AI Generator: Natural language dashboard creation

Features:
🤖 AI-powered dashboard generation using Claude + GPT-4
🔧 Infrastructure as code with Pulumi
🎯 Natural language dashboard creation
📊 Real-time business intelligence
🔒 Enterprise security and compliance
💰 Cost-optimized infrastructure
🚀 Auto-scaling and high availability
"""
)
