# infrastructure/kubernetes/developer_tools_mcp_stack.py
"""
Deploys the Developer Experience & Infrastructure MCP server stack.

This includes the official Pulumi server for infrastructure management,
a GitHub server for project management, and a database gateway.
"""
import pulumi
import pulumi_kubernetes as k8s

k8s_provider = k8s.Provider("k8s-provider", kubeconfig=pulumi.Config("").require_secret("kubeconfig"))
mcp_namespace = "mcp-servers" # Assumes the namespace from mcp_servers.py exists

# --- 1. Deployment for the GitHub Project Manager MCP Server ---
github_app_labels = {"app": "github-project-mcp"}
github_mcp_deployment = k8s.apps.v1.Deployment("github-project-mcp-deployment",
    metadata=k8s.meta.v1.ObjectMetaArgs(namespace=mcp_namespace),
    spec=k8s.apps.v1.DeploymentSpecArgs(
        replicas=1,
        selector=k8s.meta.v1.LabelSelectorArgs(match_labels=github_app_labels),
        template=k8s.core.v1.PodTemplateSpecArgs(
            metadata=k8s.meta.v1.ObjectMetaArgs(labels=github_app_labels),
            spec=k8s.core.v1.PodSpecArgs(
                containers=[k8s.core.v1.ContainerArgs(
                    name="github-project-mcp",
                    # This image corresponds to the GitHub Project Manager from the research
                    image="ghcr.io/community/github-project-manager-mcp:latest",
                    ports=[k8s.core.v1.ContainerPortArgs(container_port=9000)],
                    env_from=[k8s.core.v1.EnvFromSourceArgs(
                        secret_ref=k8s.core.v1.SecretEnvSourceArgs(name="sophia-esc-secrets")
                    )]
                )]
            )
        )
    ),
    opts=pulumi.ResourceOptions(provider=k8s_provider)
)
github_mcp_service = k8s.core.v1.Service("github-mcp-service",
    metadata=k8s.meta.v1.ObjectMetaArgs(name="github-mcp-service", namespace=mcp_namespace),
    spec=k8s.core.v1.ServiceSpecArgs(
        selector=github_app_labels,
        ports=[k8s.core.v1.ServicePortArgs(port=9000)],
    ),
    opts=pulumi.ResourceOptions(provider=k8s_provider)
)

# --- 2. Deployment for the Centralmind Database Gateway MCP Server ---
db_app_labels = {"app": "centralmind-db-gateway"}
db_mcp_deployment = k8s.apps.v1.Deployment("centralmind-db-deployment",
    metadata=k8s.meta.v1.ObjectMetaArgs(namespace=mcp_namespace),
    spec=k8s.apps.v1.DeploymentSpecArgs(
        replicas=1,
        selector=k8s.meta.v1.LabelSelectorArgs(match_labels=db_app_labels),
        template=k8s.core.v1.PodTemplateSpecArgs(
            metadata=k8s.meta.v1.ObjectMetaArgs(labels=db_app_labels),
            spec=k8s.core.v1.PodSpecArgs(
                containers=[k8s.core.v1.ContainerArgs(
                    name="centralmind-db-gateway",
                    image="ghcr.io/centralmind/database-gateway-mcp:latest",
                    ports=[k8s.core.v1.ContainerPortArgs(container_port=9000)],
                    env_from=[k8s.core.v1.EnvFromSourceArgs(
                        secret_ref=k8s.core.v1.SecretEnvSourceArgs(name="sophia-esc-secrets")
                    )]
                )]
            )
        )
    ),
    opts=pulumi.ResourceOptions(provider=k8s_provider)
)
db_mcp_service = k8s.core.v1.Service("database-mcp-service",
    metadata=k8s.meta.v1.ObjectMetaArgs(name="database-mcp-service", namespace=mcp_namespace),
    spec=k8s.core.v1.ServiceSpecArgs(
        selector=db_app_labels,
        ports=[k8s.core.v1.ServicePortArgs(port=9000)],
    ),
    opts=pulumi.ResourceOptions(provider=k8s_provider)
)

# --- 3. Deployment for the Portkey Admin MCP Server ---
portkey_admin_labels = {"app": "portkey-admin-mcp"}
portkey_admin_deployment = k8s.apps.v1.Deployment("portkey-admin-mcp-deployment",
    metadata=k8s.meta.v1.ObjectMetaArgs(namespace=mcp_namespace),
    spec=k8s.apps.v1.DeploymentSpecArgs(
        replicas=1,
        selector=k8s.meta.v1.LabelSelectorArgs(match_labels=portkey_admin_labels),
        template=k8s.core.v1.PodTemplateSpecArgs(
            metadata=k8s.meta.v1.ObjectMetaArgs(labels=portkey_admin_labels),
            spec=k8s.core.v1.PodSpecArgs(
                containers=[k8s.core.v1.ContainerArgs(
                    name="portkey-admin-mcp",
                    # This is the image from the research
                    image="ghcr.io/r-huijts/portkey-admin-mcp:latest",
                    ports=[k8s.core.v1.ContainerPortArgs(container_port=9000)],
                    env_from=[k8s.core.v1.EnvFromSourceArgs(
                        secret_ref=k8s.core.v1.SecretEnvSourceArgs(name="sophia-esc-secrets")
                    )]
                )]
            )
        )
    ),
    opts=pulumi.ResourceOptions(provider=k8s_provider)
)
portkey_admin_service = k8s.core.v1.Service("portkey-admin-mcp-service",
    metadata=k8s.meta.v1.ObjectMetaArgs(name="portkey-admin-mcp-service", namespace=mcp_namespace),
    spec=k8s.core.v1.ServiceSpecArgs(
        selector=portkey_admin_labels,
        ports=[k8s.core.v1.ServicePortArgs(port=9000)],
    ),
    opts=pulumi.ResourceOptions(provider=k8s_provider)
)

pulumi.export("github_mcp_service", github_mcp_service.metadata["name"])
pulumi.export("database_mcp_service", db_mcp_service.metadata["name"])
pulumi.export("portkey_admin_mcp_service", portkey_admin_service.metadata["name"]) 