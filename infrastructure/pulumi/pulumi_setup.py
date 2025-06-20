"""Pulumi script for setting up Pulumi resources.
"""
import pulumi

from infrastructure.esc.pulumi_secrets import pulumi_secret_manager

pulumi_access_token = pulumi_secret_manager.get_access_token()
pulumi.export("pulumi_setup_status", "Configuration managed via pulumi_secrets.py.")
