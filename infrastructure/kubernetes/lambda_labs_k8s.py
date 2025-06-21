"""Connects to an EXISTING Lambda Labs instance and installs k3s.

This version reads the SSH key directly from the local filesystem path
to ensure a successful connection.
"""

from os.path import expanduser

import pulumi
import pulumi_command as command
import pulumi_pulumiservice as pulumiservice

# --- 1. Get Required Config & Keys ---
esc_config = pulumi.Config()
CONTROL_PLANE_IP = "170.9.9.253"
pulumi_org = esc_config.require("PULUMI_ORG")

#
# ** THE DEFINITIVE FIX V2 **
# Provide the DIRECT FILE PATH to the private key for the connection.
# This avoids any issues with the key's content being passed incorrectly.
#
ssh_private_key_path = expanduser("~/.ssh/sophia_deployment_key")

# --- 2. Install Kubernetes on the Existing Instance ---
connection = command.remote.ConnectionArgs(
    host=CONTROL_PLANE_IP,
    user="ubuntu",
    private_key_path=ssh_private_key_path,  # Use the direct path
)

# --- 3. Fetch and Sanitize the Kubeconfig ---
# The rest of the file logic depends on the successful connection.
install_k3s = command.remote.Command(
    "install-k3s",
    connection=connection,
    create="curl -sfL https://get.k3s.io | sh -s - --write-kubeconfig-mode 644",
    opts=pulumi.ResourceOptions(),
)

get_kubeconfig = command.remote.Command(
    "get-kubeconfig",
    connection=connection,
    create="cat /etc/rancher/k3s/k3s.yaml",
    opts=pulumi.ResourceOptions(depends_on=[install_k3s]),
)

sanitized_kubeconfig = get_kubeconfig.stdout.apply(
    lambda config_content: config_content.replace("127.0.0.1", CONTROL_PLANE_IP)
)

# --- 4. Store the Kubeconfig in Pulumi ESC ---
kubeconfig_esc_secret = pulumiservice.EnvironmentSecret(
    "lambda-labs-kubeconfig-secret",
    organization=pulumi_org,
    environment="sophia-ai-production",
    name="LAMBDA_LABS_KUBECONFIG",
    value=sanitized_kubeconfig,
    opts=pulumi.ResourceOptions(depends_on=[get_kubeconfig]),
)

# --- 5. Export Outputs ---
pulumi.export("cluster_control_plane_ip", CONTROL_PLANE_IP)
pulumi.export("kubeconfig_storage_status", "Successfully stored in Pulumi ESC.")
