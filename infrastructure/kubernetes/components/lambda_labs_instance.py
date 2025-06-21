"""A Pulumi dynamic provider for provisioning and managing Lambda Labs instances."""

import pulumi
import requests
from pulumi.dynamic import CreateResult, Resource, ResourceProvider


class LambdaLabsInstanceProvider(ResourceProvider):
    """The dynamic provider for managing a Lambda Labs instance via their REST API."""

    def create(self, props):
        api_key = props["api_key"]
        headers = {"Authorization": f"Bearer {api_key}"}

        # Payload to launch a new instance
        payload = {
            "region_name": props["region_name"],
            "instance_type_name": props["instance_type_name"],
            "ssh_key_names": props["ssh_key_names"],
            "name": props["name"],
        }

        # Launch the instance
        response = requests.post(
            "https://cloud.lambda.ai/api/v1/instance-operations/launch",
            headers=headers,
            json={"instances": [payload]},
        )
        response.raise_for_status()

        instance_id = response.json()["data"]["instance_ids"][0]

        # We need to wait for the instance to get an IP address
        # This is a simplified polling loop. A production version would have better error handling.
        instance_ip = None
        for _ in range(20):  # Poll for up to 10 minutes
            import time

            time.sleep(30)
            instance_details_resp = requests.get(
                f"https://cloud.lambda.ai/api/v1/instances/{instance_id}",
                headers=headers,
            )
            instance_details = instance_details_resp.json()["data"]
            if instance_details.get("ip"):
                instance_ip = instance_details["ip"]
                break

        if not instance_ip:
            raise Exception("Timed out waiting for instance IP address.")

        return CreateResult(
            id_=instance_id,
            outs={"instance_id": instance_id, "ip_address": instance_ip},
        )

    def delete(self, id, props):
        api_key = props["api_key"]
        headers = {"Authorization": f"Bearer {api_key}"}
        requests.post(
            "https://cloud.lambda.ai/api/v1/instance-operations/terminate",
            headers=headers,
            json={"instance_ids": [id]},
        )


class LambdaLabsInstance(Resource):
    """A Pulumi resource representing a single Lambda Labs GPU instance."""

    instance_id: pulumi.Output[str]
    ip_address: pulumi.Output[str]

    def __init__(
        self,
        name,
        api_key: pulumi.Input[str],
        region_name: str,
        instance_type_name: str,
        ssh_key_names: list[str],
        opts=None,
    ):
        super().__init__(
            LambdaLabsInstanceProvider(),
            name,
            {
                "api_key": api_key,
                "region_name": region_name,
                "instance_type_name": instance_type_name,
                "ssh_key_names": ssh_key_names,
                "name": name,
                "instance_id": None,
                "ip_address": None,
            },
            opts,
        )
