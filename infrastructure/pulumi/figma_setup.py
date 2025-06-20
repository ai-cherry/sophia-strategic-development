"""
Pulumi script for setting up Figma resources.
"""
import pulumi
from infrastructure.esc.figma_secrets import figma_secret_manager

figma_api_key = figma_secret_manager.get_api_key()
pulumi.export("figma_setup_status", "Configuration managed via figma_secrets.py.") 