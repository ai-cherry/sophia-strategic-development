"""Pulumi script for setting up Eleven Labs resources."""

import pulumi

from infrastructure.esc.eleven_labs_secrets import eleven_labs_secret_manager

eleven_labs_api_key = eleven_labs_secret_manager.get_api_key()
pulumi.export(
    "eleven_labs_setup_status", "Configuration managed via eleven_labs_secrets.py."
)
