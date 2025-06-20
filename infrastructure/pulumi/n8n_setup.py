"""
Pulumi script for setting up n8n resources.
"""
import pulumi
from infrastructure.esc.n8n_secrets import n8n_secret_manager

n8n_api_key = n8n_secret_manager.get_api_key()
pulumi.export("n8n_setup_status", "Configuration managed via n8n_secrets.py.") 