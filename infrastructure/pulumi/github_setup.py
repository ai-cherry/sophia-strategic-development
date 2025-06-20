"""
Pulumi script for setting up GitHub resources.
"""
import pulumi
from infrastructure.esc.github_secrets import github_secret_manager

github_pat = github_secret_manager.get_pat()
pulumi.export("github_setup_status", "Configuration managed via github_secrets.py.") 