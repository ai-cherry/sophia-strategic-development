"""
Sophia AI - Lambda Labs Integration Infrastructure as Code
This module defines Lambda Labs resources using Pulumi
"""

import pulumi
import json
import pulumi_aws as aws
from pulumi import Config
import pulumi_lambda_labs as lambda_labs
from typing import List, Optional

# Load configuration
config = Config()
env = config.require("environment")  # development, staging, or production

# Get Lambda Labs credentials from Pulumi config (encrypted)
lambda_labs_api_key = config.require_secret("lambda_labs_api_key")

# Define environment-specific configurations
instance_types = {
    "development": "gpu_1x_a10",
    "staging": "gpu_2x_a10",
    "production": "gpu_4x_a10"
}

regions = {
    "development": "us-west-2",
    "staging": "us-west-2",
    "production": "us-west-2"
}

# Define Lambda Labs instance configuration
instance_config = {
    "name": f"sophia-{env}",
    "instance_type": instance_types.get(env, instance_types["development"]),
    "region": regions.get(env, regions["development"]),
    "ssh_key_name": f"sophia-{env}-key",
    "file_system_size": 100,  # GB
    "os_image": "ubuntu-server-22-04-lts",
    "jupyter_lab": True,
    "jupyter_lab_password": config.require_secret("lambda_labs_jupyter_password")
}

# Create an AWS key pair for SSH access to Lambda Labs instances
ssh_key = aws.ec2.KeyPair(f"sophia-{env}-key",
    key_name=instance_config["ssh_key_name"],
    public_key=config.require("lambda_labs_ssh_public_key")
)

# Create an AWS S3 bucket for Lambda Labs data
data_bucket = aws.s3.Bucket(f"sophia-{env}-lambda-labs-data",
    bucket=f"sophia-{env}-lambda-labs-data",
    acl="private",
    versioning=aws.s3.BucketVersioningArgs(
        enabled=True
    ),
    server_side_encryption_configuration=aws.s3.BucketServerSideEncryptionConfigurationArgs(
        rule=aws.s3.BucketServerSideEncryptionConfigurationRuleArgs(
            apply_server_side_encryption_by_default=aws.s3.BucketServerSideEncryptionConfigurationRuleApplyServerSideEncryptionByDefaultArgs(
                sse_algorithm="AES256"
            )
        )
    )
)

# Create an IAM role for Lambda Labs instances to access AWS resources
lambda_labs_role = aws.iam.Role(f"sophia-{env}-lambda-labs-role",
    assume_role_policy=json.dumps({
        "Version": "2012-10-17",
        "Statement": [{
            "Action": "sts:AssumeRole",
            "Effect": "Allow",
            "Principal": {
                "Service": "ec2.amazonaws.com"
            }
        }]
    })
)

# Attach policies to the IAM role
s3_policy_attachment = aws.iam.RolePolicyAttachment(f"sophia-{env}-lambda-labs-s3-policy",
    role=lambda_labs_role.name,
    policy_arn=aws.iam.ManagedPolicy.AMAZON_S3_FULL_ACCESS
)

# Create a Lambda Labs configuration file
lambda_labs_config = pulumi.asset.AssetArchive({
    "lambda_labs_config.json": pulumi.asset.StringAsset(json.dumps({
        "api_key": lambda_labs_api_key,
        "instance": instance_config,
        "s3_bucket": data_bucket.bucket,
        "ssh_key_name": ssh_key.key_name,
        "iam_role": lambda_labs_role.name
    }, indent=2))
})

# Export outputs
pulumi.export("lambda_labs_instance_type", instance_config["instance_type"])
pulumi.export("lambda_labs_region", instance_config["region"])
pulumi.export("lambda_labs_ssh_key_name", ssh_key.key_name)
pulumi.export("lambda_labs_data_bucket", data_bucket.bucket)
pulumi.export("lambda_labs_iam_role", lambda_labs_role.name)
pulumi.export("lambda_labs_environment", env)

class LambdaLabsInstance(pulumi.ComponentResource):
    """
    A custom Pulumi component to provision a Lambda Labs instance.
    """
    def __init__(self,
                 name: str,
                 instance_type: str,
                 region: str,
                 ssh_key_names: List[str],
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        Args:
            name: The name of the resource.
            instance_type: The type of instance to provision (e.g., 'gpu_1x_a10', 'cpu_1x_c2').
            region: The region to deploy the instance in (e.g., 'us-east-1').
            ssh_key_names: A list of SSH key names already registered in Lambda Labs.
            opts: Optional Pulumi resource options.
        """
        super().__init__('sophia:infrastructure:LambdaLabsInstance', name, {}, opts)

        # Provision the instance using the lambda-labs provider
        self.instance = lambda_labs.Instance(name,
            instance_type_name=instance_type,
            region_name=region,
            ssh_key_names=ssh_key_names,
            # Ensure the component depends on the instance
            opts=pulumi.ResourceOptions(parent=self)
        )

        # Register outputs for the component
        self.ip = self.instance.ip
        self.name = self.instance.name
        self.register_outputs({
            'ip': self.ip,
            'name': self.name,
            'instance_id': self.instance.id
        })

# Example of how to use it (for reference)
# dev_server = LambdaLabsInstance("my-dev-server",
#     instance_type="cpu_1x_c2",
#     region="us-east-1",
#     ssh_key_names=["my-ssh-key"]
# )
# pulumi.export("server_ip", dev_server.ip)
