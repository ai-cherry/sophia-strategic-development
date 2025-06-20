"""Pulumi script for setting up Exa resources.
"""
import pulumi

from infrastructure.esc.exa_secrets import exa_secret_manager

exa_api_key = exa_secret_manager.get_api_key()
pulumi.export("exa_setup_status", "Configuration managed via exa_secrets.py.")
