"""
Pulumi script for setting up Estuary resources.
"""
import pulumi
from infrastructure.esc.estuary_secrets import estuary_secret_manager

estuary_api_key = estuary_secret_manager.get_api_key()
pulumi.export("estuary_setup_status", "Configuration managed via estuary_secrets.py.") 