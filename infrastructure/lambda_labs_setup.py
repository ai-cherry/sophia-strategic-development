"""Lambda Labs Infrastructure Setup.

Pulumi script to provision Lambda Labs GPU compute resources
"""

import pulumi
import pulumi_command as command
from pulumi import Config, export

# Get configuration
config = Config()
lambda_labs_config = Config("lambda_labs")

# Lambda Labs configuration
api_key = lambda_labs_config.require_secret("api_key")
ssh_public_key = lambda_labs_config.get("ssh_public_key")
instance_type = lambda_labs_config.get("instance_type") or "gpu_1x_a10"
region = lambda_labs_config.get("region") or "us-west-2"

# Create Lambda Labs instance using command provider
# This uses the Lambda Labs CLI to provision resources
lambda_instance = command.local.Command(
    "lambda-instance",
    create=f"""# Install Lambda Labs CLI if not present.

    if ! command -v lambda &> /dev/null; then
        pip install lambda-labs
    fi

    # Configure Lambda Labs CLI
    lambda config --api-key {api_key}

    # Launch instance
    lambda launch {instance_type} \
        --name sophia-ai-compute \
        --region {region} \
        --ssh-key-name sophia-key
    """,.

        delete=
    """lambda terminate sophia-ai-compute.""",
    opts=pulumi.ResourceOptions(additional_secret_outputs=["create", "delete"]),
)

# Export instance information
export("instance_name", "sophia-ai-compute")
export("instance_type", instance_type)
export("region", region)
export("lambda_labs_setup", "completed")
