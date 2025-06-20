"""
Pulumi script for setting up Apify resources.
"""
import pulumi
from infrastructure.esc.apify_secrets import apify_secret_manager

apify_api_key = apify_secret_manager.get_api_key()
pulumi.export("apify_setup_status", "Configuration managed via apify_secrets.py.") 