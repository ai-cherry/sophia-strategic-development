"""
Pulumi script for setting up Hugging Face resources.
"""
import pulumi
from infrastructure.esc.huggingface_secrets import huggingface_secret_manager

huggingface_api_key = huggingface_secret_manager.get_api_key()
pulumi.export("huggingface_setup_status", "Configuration managed via huggingface_secrets.py.") 