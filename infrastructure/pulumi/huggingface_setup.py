"""
Pulumi script for managing Hugging Face resources using the `huggingface-cli`.
"""
import pulumi
import pulumi_command as command
from infrastructure.esc.huggingface_secrets import huggingface_secret_manager

# --- Configuration ---
config = pulumi.Config("huggingface")
model_to_deploy = config.get("model", "distilbert-base-uncased")
endpoint_name = config.get("endpoint_name", "sophia-distilbert-endpoint")
aws_region = config.get("aws_region", "us-east-1")

# Get the Hugging Face API token from our secret manager
hf_token = huggingface_secret_manager.get_api_key()

# --- Resource Definition using the Command Provider ---

# This resource represents a Hugging Face Inference Endpoint.
# The `create` command uses the CLI to deploy a model.
# The `delete` command uses the CLI to delete the endpoint.
inference_endpoint = command.local.Command("hf-inference-endpoint",
    create=pulumi.Output.concat(
        "huggingface-cli inference-endpoints create ",
        endpoint_name,
        f" --repository {model_to_deploy}",
        " --type aws",
        f" --region {aws_region}",
        " --instance-size medium --instance-type cpu" # Cost-effective default
    ),
    delete=pulumi.Output.concat(
        "huggingface-cli inference-endpoints delete ",
        endpoint_name
    ),
    environment={
        "HF_TOKEN": hf_token
    }
)

# --- Outputs ---
pulumi.export("huggingface_endpoint_name", endpoint_name)
pulumi.export("huggingface_endpoint_stdout", inference_endpoint.stdout) 