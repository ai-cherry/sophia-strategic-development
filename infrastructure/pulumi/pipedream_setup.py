"""
Pulumi script for setting up Pipedream resources.
"""
import pulumi
from infrastructure.esc.pipedream_secrets import pipedream_secret_manager

pipedream_api_key = pipedream_secret_manager.get_api_key()
pulumi.export("pipedream_setup_status", "Configuration managed via pipedream_secrets.py.") 