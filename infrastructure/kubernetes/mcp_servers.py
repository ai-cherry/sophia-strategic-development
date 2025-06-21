# infrastructure/kubernetes/mcp_servers.py
"""
Deploys all necessary MCP (Model Context Protocol) servers into the EKS cluster.
"""
import pulumi
import pulumi_kubernetes as k8s

# Assumes this program is run with a kubeconfig pointing to the EKS cluster
k8s_provider = k8s.Provider("k8s-provider", kubeconfig=pulumi.Config("").require_secret("kubeconfig"))

# --- 1. Namespace for all MCP Servers ---
mcp_namespace = k8s.core.v1.Namespace("mcp-servers-ns",
    metadata={"name": "mcp-servers"},
    opts=pulumi.ResourceOptions(provider=k8s_provider))

# --- 2. Deployment for the Official Pulumi MCP Server ---
pulumi_mcp_app_labels = {"app": "pulumi-mcp-server"}
pulumi_mcp_deployment = k8s.apps.v1.Deployment("pulumi-mcp-deployment",
    metadata=k8s.meta.v1.ObjectMetaArgs(
        namespace=mcp_namespace.metadata["name"],
    ),
    spec=k8s.apps.v1.DeploymentSpecArgs(
        replicas=1,
        selector=k8s.meta.v1.LabelSelectorArgs(match_labels=pulumi_mcp_app_labels),
        template=k8s.core.v1.PodTemplateSpecArgs(
            metadata=k8s.meta.v1.ObjectMetaArgs(labels=pulumi_mcp_app_labels),
            spec=k8s.core.v1.PodSpecArgs(
                containers=[k8s.core.v1.ContainerArgs(
                    name="pulumi-mcp-server",
                    image="pulumi/mcp-server:latest", # Use the official image
                    ports=[k8s.core.v1.ContainerPortArgs(container_port=9000)],
                    # Secrets would be mounted from the same k8s Secret as the agents
                    env_from=[k8s.core.v1.EnvFromSourceArgs(
                        secret_ref=k8s.core.v1.SecretEnvSourceArgs(name="sophia-esc-secrets")
                    )]
                )]
            )
        )
    ),
    opts=pulumi.ResourceOptions(provider=k8s_provider)
)
pulumi_mcp_service = k8s.core.v1.Service("pulumi-mcp-service",
    metadata=k8s.meta.v1.ObjectMetaArgs(
        name="pulumi-mcp-service", # This name matches the gateway endpoint
        namespace=mcp_namespace.metadata["name"],
    ),
    spec=k8s.core.v1.ServiceSpecArgs(
        selector=pulumi_mcp_app_labels,
        ports=[k8s.core.v1.ServicePortArgs(port=9000)],
        type="ClusterIP"
    ),
    opts=pulumi.ResourceOptions(provider=k8s_provider)
)


# --- 3. Deployment for the Kubernetes MCP Server ---
k8s_mcp_app_labels = {"app": "k8s-mcp-server"}
k8s_mcp_deployment = k8s.apps.v1.Deployment("k8s-mcp-deployment",
    metadata=k8s.meta.v1.ObjectMetaArgs(
        namespace=mcp_namespace.metadata["name"],
    ),
    spec=k8s.apps.v1.DeploymentSpecArgs(
        replicas=1,
        selector=k8s.meta.v1.LabelSelectorArgs(match_labels=k8s_mcp_app_labels),
        template=k8s.core.v1.PodTemplateSpecArgs(
            metadata=k8s.meta.v1.ObjectMetaArgs(labels=k8s_mcp_app_labels),
            spec=k8s.core.v1.PodSpecArgs(
                containers=[k8s.core.v1.ContainerArgs(
                    name="k8s-mcp-server",
                    image="ghcr.io/flux159/mcp-server-kubernetes:latest", # Use the community image
                    ports=[k8s.core.v1.ContainerPortArgs(container_port=9000)],
                )],
                # This service account needs RBAC permissions to read from the Kubernetes API
                service_account_name="k8s-mcp-sa"
            )
        )
    ),
    opts=pulumi.ResourceOptions(provider=k8s_provider)
)
k8s_mcp_service = k8s.core.v1.Service("k8s-mcp-service",
    metadata=k8s.meta.v1.ObjectMetaArgs(
        name="k8s-mcp-service", # This name matches the gateway endpoint
        namespace=mcp_namespace.metadata["name"],
    ),
    spec=k8s.core.v1.ServiceSpecArgs(
        selector=k8s_mcp_app_labels,
        ports=[k8s.core.v1.ServicePortArgs(port=9000)],
        type="ClusterIP"
    ),
    opts=pulumi.ResourceOptions(provider=k8s_provider)
)

# Note: We would also need to create the ServiceAccount (k8s-mcp-sa) and the
# necessary ClusterRole and ClusterRoleBinding for it to have read access to the cluster.

pulumi.export("pulumi_mcp_service_name", pulumi_mcp_service.metadata["name"])
pulumi.export("k8s_mcp_service_name", k8s_mcp_service.metadata["name"])
