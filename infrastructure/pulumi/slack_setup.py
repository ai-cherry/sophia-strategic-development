"""
Pulumi script for setting up Slack resources.
"""
import pulumi
from infrastructure.esc.slack_secrets import slack_secret_manager

slack_bot_token = slack_secret_manager.get_bot_token()
pulumi.export("slack_setup_status", "Configuration managed via slack_secrets.py.") 