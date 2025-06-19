"""
Provisions a remote development server on Lambda Labs, configured as a Docker host,
using the Lambda Labs REST API directly via a dynamic Pulumi provider.
"""
import pulumi
import requests
import json

# --- User-configurable settings ---
INSTANCE_TYPE = "cpu.c2"
REGION = "us-east-1"
SERVER_NAME = "sophia-ai-dev-docker-host-pulumi"
SSH_KEY_NAME = "cherry-ai-collaboration-key" # The SSH key must already exist in your Lambda Labs account

class LambdaLabsProvider(pulumi.dynamic.ResourceProvider):
    """A dynamic provider to manage a Lambda Labs instance via their REST API."""

    def create(self, props):
        """Provisions a new Lambda Labs instance."""
        api_key = props["api_key"]
        
        url = "https://cloud.lambda.ai/api/v1/instance-operations/launch"
        payload = {
            "region_name": props["region"],
            "instance_type_name": props["instance_type"],
            "ssh_key_names": [props["ssh_key_name"]],
            "name": props["name"],
        }
        
        response = requests.post(url, json=payload, auth=(api_key, ""))
        response.raise_for_status()
        
        data = response.json()
        instance_id = data["data"]["instance_ids"][0]
        
        # We need to fetch the instance details to get the IP
        details_url = f"https://cloud.lambda.ai/api/v1/instances/{instance_id}"
        instance_details_resp = requests.get(details_url, auth=(api_key, ""))
        instance_details_resp.raise_for_status()
        
        instance_data = instance_details_resp.json()["data"]
        
        return pulumi.dynamic.CreateResult(
            id_=instance_id,
            outs={
                "id": instance_id,
                "ip": instance_data.get("ip"),
                **props
            }
        )

    def delete(self, id, props):
        """Terminates a Lambda Labs instance."""
        api_key = props["api_key"]
        
        url = "https://cloud.lambda.ai/api/v1/instance-operations/terminate"
        payload = {"instance_ids": [id]}
        
        response = requests.post(url, json=payload, auth=(api_key, ""))
        # Don't raise for status on delete, as the instance might already be gone.
        # Check for non-200 and log instead if needed.

class LambdaLabsServer(pulumi.dynamic.Resource):
    """A Pulumi resource representing a Lambda Labs server."""
    def __init__(self, name, api_key, region, instance_type, ssh_key_name, server_name, opts=None):
        super().__init__(
            LambdaLabsProvider(),
            name,
            {
                "api_key": api_key,
                "region": region,
                "instance_type": instance_type,
                "ssh_key_name": ssh_key_name,
                "name": server_name,
                "ip": None, # Will be populated by the provider
            },
            opts=opts
        )

# --- Pulumi Infrastructure Definition ---

# 1. Get the Lambda Labs API key from Pulumi config
lambda_config = pulumi.Config("lambda")
api_key = lambda_config.require_secret("api_key")

# 2. Create the custom Lambda Labs Server resource
dev_server = LambdaLabsServer("sophia-dev-server",
    api_key=api_key,
    region=REGION,
    instance_type=INSTANCE_TYPE,
    ssh_key_name=SSH_KEY_NAME,
    server_name=SERVER_NAME
)

# --- Outputs ---
pulumi.export("dev_server_ip", dev_server.ip)
pulumi.export("dev_server_name", dev_server.name)
pulumi.export("dev_server_id", dev_server.id)
pulumi.export("dev_server_ssh_command", pulumi.Output.concat("ssh ubuntu@", dev_server.ip)) 