"""Pulumi script for setting up Apify resources using the bridged Terraform provider."""

import pulumi
from pulumi_terraform import state

# --- Configuration ---
config = pulumi.Config("apify")
tf_state_path = config.get("terraform_state_path", "apify.tfstate")

# --- Resource Definitions using Terraform State ---


class ApifyWorkspace(state.RemoteStateReference):
    def __init__(self, name, state_path):
        super().__init__(name, state.LocalStateArgs(path=state_path))


# Create a reference to the Apify Terraform state
apify_state = ApifyWorkspace("apify-tf-state", state_path=tf_state_path)

# You can now access outputs from your Terraform state.
# For example, if your Terraform code outputs an `actor_id`:
# actor_id = apify_state.get_output("default_actor_id")


# --- Outputs ---
pulumi.export(
    "apify_setup_status",
    "Apify resources are managed via a bridged Terraform state. See your Terraform files for definitions.",
)
# pulumi.export("apify_actor_id_from_tf", actor_id)
