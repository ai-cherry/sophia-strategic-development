"""
Pulumi script noting the configuration setup for Portkey and OpenRouter.
These services are used via SDKs and their primary IaC component is secret management.
"""
import pulumi
from infrastructure.esc.llm_gateway_secrets import llm_gateway_secret_manager

# This script doesn't provision resources, but it registers the configuration
# in our IaC, which is a best practice.

# We can retrieve the keys to ensure they are set, without exposing them.
portkey_api_key = llm_gateway_secret_manager.get_portkey_api_key()
openrouter_api_key = llm_gateway_secret_manager.get_openrouter_api_key()

pulumi.export("portkey_setup_status", "Configuration managed via llm_gateway_secrets.py. No infrastructure to provision.")
pulumi.export("openrouter_setup_status", "Configuration managed via llm_gateway_secrets.py. No infrastructure to provision.") 