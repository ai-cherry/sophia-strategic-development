"""Pulumi script for setting up Together AI resources.
"""
import pulumi

from infrastructure.esc.together_secrets import together_secret_manager

together_api_key = together_secret_manager.get_api_key()
pulumi.export("together_setup_status", "Configuration managed via together_secrets.py.")
