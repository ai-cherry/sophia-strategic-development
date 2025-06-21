"""Provisions a Lambda Labs instance and then installs a self-managed
Kubernetes cluster on it.
"""

import pulumi
import pulumi_command as command
import pulumi_pulumiservice as pulumiservice

from .components.lambda_labs_instance import LambdaLabsInstance

# --- 1. Get Required Config from ESC ---
esc_config = pulumi.Config("scoobyjava-org/default/sophia-ai-production")
lambda_api_key = esc_config.require_secret("LAMBDA_API_KEY")
ssh_private_key = esc_config.require_secret("LAMBDA_SSH_PRIVATE_KEY")
ssh_key_name = esc_config.require(
    "LAMBDA_SSH_KEY_NAME"
)  # The name of the SSH key registered in Lambda Labs

# --- 2. Provision the Lambda Labs Instance ---
control_plane_node = LambdaLabsInstance(
    "sophia-k8s-control-plane",
    api_key=lambda_api_key,
    region_name="us-tx-1",  # Example region
    instance_type_name="gpu_1x_a10",  # Example instance type
    ssh_key_names=[ssh_key_name],
)

# --- 3. Install Kubernetes on the New Instance ---
connection = command.remote.ConnectionArgs(
    host=control_plane_node.ip_address, user="ubuntu", private_key=ssh_private_key
)

install_k3s = command.remote.Command(
    "install-k3s",
    connection=connection,
    create="curl -sfL https://get.k3s.io | sh -s - --write-kubeconfig-mode 644",
    opts=pulumi.ResourceOptions(depends_on=[control_plane_node]),
)

# --- 4. Fetch and Sanitize the Kubeconfig ---
get_kubeconfig = command.remote.Command(
    "get-kubeconfig",
    connection=connection,
    create="cat /etc/rancher/k3s/k3s.yaml",
    opts=pulumi.ResourceOptions(depends_on=[install_k3s]),
)

sanitized_kubeconfig = pulumi.Output.all(
    get_kubeconfig.stdout, control_plane_node.ip_address
).apply(lambda args: args[0].replace("127.0.0.1", args[1]))

# --- 5. Store the Kubeconfig in Pulumi ESC ---
kubeconfig_esc_secret = pulumiservice.EnvironmentSecret(
    "lambda-labs-kubeconfig-secret",
    organization=esc_config.require("PULUMI_ORG"),
    environment="sophia-ai-production",
    name="LAMBDA_LABS_KUBECONFIG",
    value=sanitized_kubeconfig,
    opts=pulumi.ResourceOptions(depends_on=[get_kubeconfig]),
)

# --- 6. Export Outputs ---
pulumi.export("cluster_control_plane_ip", control_plane_node.ip_address)
pulumi.export("kubeconfig_storage_status", "Successfully stored in Pulumi ESC.")
