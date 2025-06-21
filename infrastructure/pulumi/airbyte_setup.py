"""Pulumi script for setting up Airbyte resources using the bridged Terraform provider."""

import pulumi
from pulumi_terraform import state

# --- Configuration ---
config = pulumi.Config("airbyte")
# This local state is a placeholder. In a real scenario, you would use a remote
# Terraform state backend like S3 or Terraform Cloud.
tf_state_path = config.get("terraform_state_path", "airbyte.tfstate")

# --- Resource Definitions using Terraform State ---


# This setup assumes you have a separate Terraform project that manages your
# Airbyte sources, destinations, and connections. Pulumi can then read the
class AirbyteWorkspace(state.RemoteStateReference):
    def __init__(self, name, state_path):
        super().__init__(name, state.LocalStateArgs(path=state_path))


# Create a reference to the Airbyte Terraform state
airbyte_state = AirbyteWorkspace("airbyte-tf-state", state_path=tf_state_path)

# You can now access outputs from your Terraform state.
# For example, if your Terraform code outputs a `workspace_id` and a `source_id`:
# workspace_id = airbyte_state.get_output("workspace_id")
# source_id = airbyte_state.get_output("source_id")


# --- Outputs ---
# This demonstrates that Pulumi is aware of the resources managed by Terraform.
# The actual resources are defined in your .tf files.
pulumi.export(
    "airbyte_setup_status",
    "Airbyte resources are managed via a bridged Terraform state. See your Terraform files for definitions.",
)
# pulumi.export("airbyte_workspace_id_from_tf", workspace_id)
# pulumi.export("airbyte_source_id_from_tf", source_id)
