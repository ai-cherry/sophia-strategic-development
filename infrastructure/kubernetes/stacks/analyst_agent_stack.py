"""Defines the Pulumi Stack for the Analyst Agent as a Kubernetes resource.

An AI agent would generate and apply this configuration to the cluster
to deploy the Analyst Agent.
"""

import pulumi
import pulumi_kubernetes as k8s

# Assumes this program is run with a kubeconfig pointing to the EKS cluster
k8s_provider = k8s.Provider(
    "k8s-provider", kubeconfig=pulumi.Config("").require_secret("kubeconfig")
)

# --- 1. Define the Kubernetes Secret for ESC values ---
# This pulls the secrets from Pulumi ESC and makes them available as a native
# Kubernetes Secret object in the cluster.
esc_config = pulumi.Config("scoobyjava-org/default/sophia-ai-production")
k8s_secret = k8s.core.v1.Secret(
    "sophia-esc-secrets",
    metadata=k8s.meta.v1.ObjectMetaArgs(namespace="sophia-agents"),
    # The 'stringData' field allows us to pass plaintext values, which Kubernetes
    # will automatically encode. Pulumi handles the secret encryption.
    string_data={
        "AGNO_API_KEY": esc_config.require_secret("AGNO_API_KEY"),
        "ARIZE_API_KEY": esc_config.require_secret("ARIZE_API_KEY"),
        "ARIZE_SPACE_ID": esc_config.require_secret("ARIZE_SPACE_ID"),
        # Add other necessary secrets here
    },
    opts=pulumi.ResourceOptions(provider=k8s_provider),
)

# --- 2. Define the Pulumi Stack Resource ---
# This custom resource tells the Pulumi Operator to deploy the agent's manifests.
analyst_agent_stack = k8s.apiextensions.CustomResource(
    "analyst-agent-stack",
    api_version="pulumi.com/v1",
    kind="Stack",
    metadata={
        "name": "analyst-agent-stack",
        "namespace": "pulumi-operator-system",  # The operator's namespace
    },
    spec={
        "stack": "sophia-ai-org/agent-deployments/analyst-agent-prod",
        "projectRepo": "https://github.com/ai-cherry/sophia-main.git",  # Your repo
        "commit": "HEAD",  # Or a specific commit hash
        "destroyOnFinalize": True,
        # This is where we point the Stack to the agent's actual Kubernetes manifests.
        # The Operator will run `pulumi up` on this directory.
        "program": {"dir": "infrastructure/kubernetes/manifests/"},
        # Pass the Kubernetes Secret to the Pulumi program run by the operator
        "stackConfig": {
            "secretRef": k8s_secret.metadata["name"],
        },
    },
    opts=pulumi.ResourceOptions(provider=k8s_provider, depends_on=[k8s_secret]),
)

pulumi.export("analyst_agent_stack_name", analyst_agent_stack.metadata["name"])
