"""Pulumi script for setting up Gong resources."""

import pulumi

from infrastructure.esc.gong_secrets import gong_secret_manager

gong_api_key = gong_secret_manager.get_api_key()
pulumi.export("gong_setup_status", "Configuration managed via gong_secrets.py.")
