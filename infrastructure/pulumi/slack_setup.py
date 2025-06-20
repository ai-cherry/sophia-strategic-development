"""Pulumi script for setting up Slack resources using a dynamic provider.
"""
import pulumi
import requests

from infrastructure.esc.slack_secrets import slack_secret_manager


class SlackChannelProvider(pulumi.dynamic.ResourceProvider):
    """A dynamic provider to manage a Slack channel via the REST API."""

    def create(self, props):
        """Creates a new Slack channel."""
        token = props["token"]
        channel_name = props["name"]

        response = requests.post(
            "https://slack.com/api/conversations.create",
            headers={"Authorization": f"Bearer {token}"},
            json={"name": channel_name, "is_private": props.get("is_private", False)},
        )
        response.raise_for_status()

        data = response.json()
        if not data.get("ok"):
            raise Exception(f"Failed to create channel: {data.get('error')}")

        channel_id = data["channel"]["id"]
        return pulumi.dynamic.CreateResult(
            id_=channel_id, outs={"id": channel_id, **props}
        )

    def delete(self, id, props):
        """Archives a Slack channel."""
        token = props["token"]
        requests.post(
            "https://slack.com/api/conversations.archive",
            headers={"Authorization": f"Bearer {token}"},
            json={"channel": id},
        )
        # No need to raise for status, as archiving is idempotent.


class SlackChannel(pulumi.dynamic.Resource):
    """A Pulumi resource representing a Slack Channel."""

    def __init__(self, name, channel_name, token, is_private=False, opts=None):
        super().__init__(
            SlackChannelProvider(),
            name,
            {
                "name": channel_name,
                "token": token,
                "is_private": is_private,
                "id": None,  # Will be populated by the provider
            },
            opts=opts,
        )


# --- Resource Definitions ---
bot_token = slack_secret_manager.get_bot_token()

# Example: Create a new public channel for deployment notifications
deployment_channel = SlackChannel(
    "deployments-channel",
    channel_name="sophia-deployments",
    token=bot_token,
    is_private=False,
)

# --- Outputs ---
pulumi.export("slack_deployment_channel_id", deployment_channel.id)
pulumi.export("slack_deployment_channel_name", deployment_channel.name)
