"""Main Pulumi entry point for the Sophia AI infrastructure stack.

This program orchestrates the entire deployment in the correct order:
1. Provisions the Kubernetes cluster on Lambda Labs.
2. Deploys all MCP servers and application services onto the new cluster.
"""

import pulumi
from kubernetes.agent_ui import agno_ui_url
from kubernetes.dashboard_hosting import dashboard_url

# Import the logic from our modularized infrastructure programs.
from kubernetes.stacks.analyst_agent_stack import analyst_agent_stack_name

# --- Export Final Outputs ---
# We can re-export the most important outputs from the sub-modules
# to have a single, clean output view for the entire infrastructure stack.

pulumi.export("sophia_dashboard_url", dashboard_url)
pulumi.export("agno_agent_ui_url", agno_ui_url)
pulumi.export("analyst_agent_stack_status", analyst_agent_stack_name)
pulumi.export("lambda_labs_kubeconfig_secret_name", "LAMBDA_LABS_KUBECONFIG (in ESC)")
