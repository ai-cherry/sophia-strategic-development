"""Provisions a production-ready Amazon EKS (Elastic Kubernetes Service) cluster.

using the high-level Pulumi EKS component.
"""

import pulumi
import pulumi_eks as eks

# --- EKS Cluster Configuration ---
# Create an EKS cluster with default settings.
# The pulumi_eks component handles creating the VPC, subnets, node groups,
# and all necessary IAM roles and policies.
cluster = eks.Cluster(
    "sophia-ai-eks-cluster",
    instance_type="t3.medium",
    desired_capacity=2,
    min_size=2,
    max_size=4,
    storage_classes="gp2",
    deploy_dashboard=False,  # The Kubernetes dashboard is often disabled for security.
)

# Export the cluster's kubeconfig and name.
# The kubeconfig is marked as a secret as it provides administrative access.
pulumi.export("cluster_name", cluster.eks_cluster.name)
pulumi.export("kubeconfig", pulumi.Output.secret(cluster.kubeconfig))
