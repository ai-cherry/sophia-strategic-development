"""
Connects to an EXISTING Lambda Labs instance and installs k3s to serve as
our Kubernetes cluster. It then saves the kubeconfig to Pulumi ESC.
"""
import pulumi
import pulumi_command as command
import pulumi_pulumiservice as pulumiservice

# --- 1. Get Required Config from ESC ---
# These values MUST be configured in your GitHub organization secrets.
esc_config = pulumi.Config()

CONTROL_PLANE_IP = "170.9.9.253" 
# Use the new, correctly named secret for the private key
ssh_private_key = esc_config.require_secret("SOPHIA_DEPLOYMENT_KEY_2025") 
pulumi_org = esc_config.require("PULUMI_ORG")

# We no longer need the LAMBDA_SSH_KEY_NAME from config, as it's only used
# when creating a *new* instance, and we are targeting an existing one.

# --- 2. Install Kubernetes on the Existing Instance ---
connection = command.remote.ConnectionArgs(
    host=CONTROL_PLANE_IP,
    user="ubuntu", 
    private_key=ssh_private_key
)

# ... (rest of the file is unchanged) ... 