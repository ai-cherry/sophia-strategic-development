class LambdaLabsInstanceProvider(ResourceProvider):
    def create(self, props):
        # ...
        response = requests.post(
            "https://cloud.lambda.ai/api/v1/instance-operations/launch",
            headers=headers,
            json={"instances": [payload]},
            timeout=60,
        )
        # ...
        for _ in range(20):  # Poll for up to 10 minutes
            # ...
            instance_details_resp = requests.get(
                f"https://cloud.lambda.ai/api/v1/instances/{instance_id}",
                headers=headers,
                timeout=30,
            )
            # ...

    def delete(self, id, props):
        api_key = props["api_key"]
        headers = {"Authorization": f"Bearer {api_key}"}
        requests.post(
            "https://cloud.lambda.ai/api/v1/instance-operations/terminate",
            headers=headers,
            json={"instance_ids": [id]},
            timeout=60,
        )


class MCPClient:
    """A single client to rule them all.

        An agent uses this client to talk to any MCP-compliant server via the gateway.
    """

    # ...
