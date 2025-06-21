"""Deploys the official Agno Agent UI into the EKS cluster."""

import pulumi
import pulumi_kubernetes as k8s

# Get the kubeconfig securely from our central Pulumi ESC environment.
esc_config = pulumi.Config("scoobyjava-org/default/sophia-ai-production")
kubeconfig = esc_config.require_secret("LAMBDA_LABS_KUBECONFIG")
k8s_provider = k8s.Provider("k8s-provider", kubeconfig=kubeconfig)

# --- 1. Namespace for the Agent UI ---
ui_namespace = k8s.core.v1.Namespace(
    "agno-ui-ns",
    metadata={"name": "agno-ui"},
    opts=pulumi.ResourceOptions(provider=k8s_provider),
)

# --- 2. Deployment for the Agno Agent UI ---
app_labels = {"app": "agno-agent-ui"}
deployment = k8s.apps.v1.Deployment(
    "agno-ui-deployment",
    metadata=k8s.meta.v1.ObjectMetaArgs(
        namespace=ui_namespace.metadata["name"],
    ),
    spec=k8s.apps.v1.DeploymentSpecArgs(
        replicas=1,
        selector=k8s.meta.v1.LabelSelectorArgs(match_labels=app_labels),
        template=k8s.core.v1.PodTemplateSpecArgs(
            metadata=k8s.meta.v1.ObjectMetaArgs(labels=app_labels),
            spec=k8s.core.v1.PodSpecArgs(
                containers=[
                    k8s.core.v1.ContainerArgs(
                        name="agent-ui",
                        image="ghcr.io/agno-agi/agent-ui:latest",  # Use the official image
                        ports=[k8s.core.v1.ContainerPortArgs(container_port=3000)],
                        env=[
                            # This tells the UI where to find the backend agent server.
                            # We'll point it to the ClusterIP service of our main backend.
                            k8s.core.v1.EnvVarArgs(
                                name="AGNO_AGENT_API_URL",
                                value="http://sophia-backend-service.default.svc.cluster.local:8000",
                            )
                        ],
                    )
                ]
            ),
        ),
    ),
    opts=pulumi.ResourceOptions(provider=k8s_provider),
)

# --- 3. Service to Expose the UI ---
# We can use a LoadBalancer service to expose the UI to the internet.
service = k8s.core.v1.Service(
    "agno-ui-service",
    metadata=k8s.meta.v1.ObjectMetaArgs(
        namespace=ui_namespace.metadata["name"],
    ),
    spec=k8s.core.v1.ServiceSpecArgs(
        selector=app_labels,
        ports=[k8s.core.v1.ServicePortArgs(port=80, target_port=3000)],
        type="LoadBalancer",  # This will provision an AWS Load Balancer
    ),
    opts=pulumi.ResourceOptions(provider=k8s_provider),
)

pulumi.export(
    "agno_ui_url",
    service.status.apply(
        lambda status: (
            status.load_balancer.ingress[0].hostname
            if status.load_balancer.ingress
            else "pending"
        )
    ),
)
