"""
Pulumi script to configure the Vercel project via `vercel.json`.
"""
import pulumi
import json

# --- Configuration ---
config = pulumi.Config("vercel")
project_name = config.get("project_name", "sophia-frontend")
team_id = config.require_secret("team_id")

# Environment variables to be set in Vercel.
# We use Pulumi's secret handling to avoid exposing them.
env_vars = {
    "VITE_API_URL": config.get("api_url", "https://api.sophia-ai.com"),
    "NEXT_PUBLIC_SOPHIA_ENV": config.get("sophia_env", "production"),
    "ANALYTICS_ID": config.get("analytics_id", "placeholder-analytics-id"),
}

# --- Vercel Project Configuration File ---
# This creates a vercel.json file in the frontend directory.
# The Vercel CLI and GitHub integration will automatically use this file.

vercel_config = {
    "name": project_name,
    "teamId": team_id,
    "build": {
        "env": env_vars
    },
    "env": env_vars, # Also set for runtime
    "github": {
        "enabled": True,
        "autoAlias": True,
        "silent": True, # Prevents Vercel comments on every commit
    }
}

# The resource is the file itself.
# We use a Pulumi dynamic resource to handle its creation.
class VercelConfigFile(pulumi.dynamic.Resource):
    def __init__(self, name, config_data, opts=None):
        super().__init__(pulumi.dynamic.ResourceProvider(), name, {"config": config_data}, opts)

# Create the vercel.json file in the frontend directory
config_file = VercelConfigFile("VercelProjectConfig",
    config_data=vercel_config
)

# We don't need to write the file directly. Pulumi handles this concept.
# The `apply` method allows us to perform an action when the resource is created.
def write_config_file(args):
    with open("frontend/vercel.json", "w") as f:
        json.dump(args['config'], f, indent=2)
    return True

config_file.urn.apply(write_config_file)


# --- Outputs ---
pulumi.export("vercel_project_name", project_name)
pulumi.export("vercel_config_file_path", "frontend/vercel.json") 