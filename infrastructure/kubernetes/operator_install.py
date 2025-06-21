"""Installs the Pulumi Kubernetes Operator into the EKS cluster."""

import pulumi
import pulumi_kubernetes as k8s
from pulumi_kubernetes.helm.v3 import Release, ReleaseArgs, RepositoryOptsArgs

# This program assumes that it is run with a kubeconfig that points to the
# EKS cluster created in the previous step.
k8s_provider = k8s.Provider(
    "k8s-provider", kubeconfig=pulumi.Config("").require_secret("kubeconfig")
)

# Install the Pulumi Kubernetes Operator using its Helm chart.
pulumi_operator_chart = Release(
    "pulumi-kubernetes-operator",
    ReleaseArgs(
        chart="pulumi-kubernetes-operator",
        version="1.12.0",  # Use a specific, stable version
        namespace="pulumi-operator-system",
        create_namespace=True,
        repository_opts=RepositoryOptsArgs(
            repo="https://pulumi.github.io/pulumi-kubernetes-operator",
        ),
    ),
    opts=pulumi.ResourceOptions(provider=k8s_provider),
)

pulumi.export("operator_status", pulumi_operator_chart.status)
