# infrastructure/kubernetes/developer_tools_mcp_stack.py
"""Deploys the Business Operations & Developer Experience MCP server stack.

This includes specialized, best-in-class MCP servers for all core business
and engineering platforms.
"""

import pulumi
import pulumi_kubernetes as k8s

k8s_provider = k8s.Provider(
    "k8s-provider", kubeconfig=pulumi.Config("").require_secret("kubeconfig")
)
mcp_namespace = "mcp-servers"


# A helper function to create a standard MCP deployment
def create_mcp_deployment(name: str, image: str):
    app_labels = {"app": name}
    deployment = k8s.apps.v1.Deployment(
        f"{name}-deployment",
        metadata=k8s.meta.v1.ObjectMetaArgs(namespace=mcp_namespace),
        spec=k8s.apps.v1.DeploymentSpecArgs(
            replicas=1,
            selector=k8s.meta.v1.LabelSelectorArgs(match_labels=app_labels),
            template=k8s.core.v1.PodTemplateSpecArgs(
                metadata=k8s.meta.v1.ObjectMetaArgs(labels=app_labels),
                spec=k8s.core.v1.PodSpecArgs(
                    containers=[
                        k8s.core.v1.ContainerArgs(
                            name=name,
                            image=image,
                            ports=[k8s.core.v1.ContainerPortArgs(container_port=9000)],
                            env_from=[
                                k8s.core.v1.EnvFromSourceArgs(
                                    secret_ref=k8s.core.v1.SecretEnvSourceArgs(
                                        name="sophia-esc-secrets"
                                    )
                                )
                            ],
                        )
                    ]
                ),
            ),
        ),
        opts=pulumi.ResourceOptions(provider=k8s_provider),
    )
    service = k8s.core.v1.Service(
        f"{name}-service",
        metadata=k8s.meta.v1.ObjectMetaArgs(
            name=f"{name}-service", namespace=mcp_namespace
        ),
        spec=k8s.core.v1.ServiceSpecArgs(
            selector=app_labels,
            ports=[k8s.core.v1.ServicePortArgs(port=9000)],
        ),
        opts=pulumi.ResourceOptions(provider=k8s_provider, depends_on=[deployment]),
    )
    return service


# --- Deploy the Business Operations MCP Stack ---
gong_service = create_mcp_deployment("gong-mcp", "ghcr.io/kenazk/gong-mcp:latest")
hubspot_service = create_mcp_deployment(
    "hubspot-mcp", "ghcr.io/hubspot/mcp-server:beta"
)
slack_service = create_mcp_deployment(
    "slack-mcp", "ghcr.io/korotovsky/slack-mcp-server:latest"
)
asana_service = create_mcp_deployment("asana-mcp", "ghcr.io/asana/mcp-server:latest")

# --- Deploy the Research & Prospecting MCP Stack ---
apify_service = create_mcp_deployment(
    "apify-mcp", "ghcr.io/apify/rag-web-browser-mcp:latest"
)  # Assuming image name
apollo_service = create_mcp_deployment(
    "apollo-io-mcp", "ghcr.io/lkm1developer/apollo-io-mcp:latest"
)  # Assuming image name
exa_service = create_mcp_deployment("exa-mcp", "ghcr.io/exa-labs/exa-mcp-server:latest")
serpapi_service = create_mcp_deployment(
    "serpapi-mcp", "ghcr.io/ilyazub/serpapi-mcp-server:latest"
)

# Note: Zenrows (Pipedream) and Looker (Zapier) are webhook-based and do not require a deployed server.

# --- Deploy the Content & Automation MCP Stack ---
slidespeak_service = create_mcp_deployment(
    "slidespeak-mcp", "ghcr.io/slidespeak/mcp-server:latest"
)  # Assuming image name
llama_service = create_mcp_deployment(
    "llama-mcp", "ghcr.io/run-llama/llamacloud-mcp:latest"
)
notion_service = create_mcp_deployment(
    "notion-mcp", "ghcr.io/makenotion/notion-mcp-server:latest"
)

# --- Keep the existing Developer & Infrastructure Servers ---
consult7_service = create_mcp_deployment(
    "consult7-mcp", "ghcr.io/wong2/consult7-mcp-server:latest"
)
snowflake_service = create_mcp_deployment(
    "snowflake-mcp", "ghcr.io/appcypher/snowflake-mcp-server:latest"
)

pulumi.export("gong_mcp_service", gong_service.metadata["name"])
pulumi.export("hubspot_mcp_service", hubspot_service.metadata["name"])
pulumi.export("slack_mcp_service", slack_service.metadata["name"])
pulumi.export("asana_mcp_service", asana_service.metadata["name"])
pulumi.export("apify_mcp_service", apify_service.metadata["name"])
pulumi.export("apollo_mcp_service", apollo_service.metadata["name"])
pulumi.export("exa_mcp_service", exa_service.metadata["name"])
pulumi.export("serpapi_mcp_service", serpapi_service.metadata["name"])
pulumi.export("consult7_mcp_service", consult7_service.metadata["name"])
pulumi.export("snowflake_mcp_service", snowflake_service.metadata["name"])
pulumi.export("slidespeak_mcp_service", slidespeak_service.metadata["name"])
pulumi.export("llama_mcp_service", llama_service.metadata["name"])
pulumi.export("notion_mcp_service", notion_service.metadata["name"])
