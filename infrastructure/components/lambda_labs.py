import json

import pulumi_aws as aws
import pulumi_lambda_labs as lambda_labs
from pulumi import Config, ResourceOptions

from .base_component import BaseComponent


class LambdaLabsComponent(BaseComponent):
    def __init__(self, name: str, opts: ResourceOptions = None):
        super().__init__(name, opts)
        component_opts = ResourceOptions(parent=self)

        config = Config()
        env = config.require("environment")

        # Define environment-specific configurations
        instance_types = {
            "development": "gpu_1x_a10",
            "staging": "gpu_2x_a10",
            "production": "gpu_4x_a10",
        }

        # Create an AWS key pair for SSH access
        ssh_key_name = f"sophia-{env}-key"
        self.ssh_key = aws.ec2.KeyPair(
            ssh_key_name,
            key_name=ssh_key_name,
            public_key=config.require("lambda_labs_ssh_public_key"),
            opts=component_opts,
        )

        # Provision the instance using the lambda-labs provider
        instance_name = f"sophia-{env}"
        self.instance = lambda_labs.Instance(
            instance_name,
            instance_type_name=instance_types.get(env, instance_types["development"]),
            region_name="us-west-2",
            ssh_key_names=[self.ssh_key.key_name],
            opts=component_opts,
        )

        # Create an AWS S3 bucket for data
        bucket_name = f"sophia-{env}-lambda-data"
        self.data_bucket = aws.s3.Bucket(
            bucket_name, bucket=bucket_name, acl="private", opts=component_opts
        )

        # Create an IAM role for the instance
        role_name = f"sophia-{env}-lambda-role"
        self.iam_role = aws.iam.Role(
            role_name,
            assume_role_policy=json.dumps(
                {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Action": "sts:AssumeRole",
                            "Effect": "Allow",
                            "Principal": {"Service": "ec2.amazonaws.com"},
                        }
                    ],
                }
            ),
            opts=component_opts,
        )

        # Attach policies to the IAM role
        aws.iam.RolePolicyAttachment(
            f"{role_name}-s3-policy",
            role=self.iam_role.name,
            policy_arn=aws.iam.ManagedPolicy.AMAZON_S3_FULL_ACCESS,
            opts=component_opts,
        )

        # Register outputs
        self.register_outputs(
            {
                "instance_name": self.instance.name,
                "instance_ip": self.instance.ip,
                "instance_type": self.instance.instance_type_name,
                "ssh_key_name": self.ssh_key.key_name,
                "data_bucket_name": self.data_bucket.bucket,
                "iam_role_name": self.iam_role.name,
            }
        )
