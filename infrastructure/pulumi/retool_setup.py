"""
Pulumi script for setting up Retool resources using a dynamic provider.
"""
import pulumi
import requests
from infrastructure.esc.retool_secrets import retool_secret_manager

class RetoolAppProvider(pulumi.dynamic.ResourceProvider):
    """A dynamic provider to manage a Retool Application via the REST API."""

    def create(self, props):
        """Creates a new Retool application."""
        api_key = props["api_key"]
        
        response = requests.post("https://api.retool.com/v1/applications",
            headers={"Authorization": f"Bearer {api_key}"},
            json={"name": props["name"], "displayName": props["displayName"]}
        )
        response.raise_for_status()
        
        data = response.json()
        app_id = data["id"]
        return pulumi.dynamic.CreateResult(id_=app_id, outs={"id": app_id, **props})

    def delete(self, id, props):
        """Deletes a Retool application."""
        api_key = props["api_key"]
        requests.delete(f"https://api.retool.com/v1/applications/{id}",
            headers={"Authorization": f"Bearer {api_key}"}
        )

class RetoolApp(pulumi.dynamic.Resource):
    """A Pulumi resource representing a Retool Application."""
    def __init__(self, name, app_name, display_name, api_key, opts=None):
        super().__init__(
            RetoolAppProvider(),
            name,
            {
                "name": app_name,
                "displayName": display_name,
                "api_key": api_key,
                "id": None
            },
            opts=opts
        )

# --- Resource Definitions ---
retool_api_key = retool_secret_manager.get_retool_api_token()

# Example: Create the Mission Control Dashboard app
mission_control_app = RetoolApp("mission-control-dashboard",
    app_name="mcp_mission_control",
    display_name="MCP Mission Control",
    api_key=retool_api_key
)

# --- Outputs ---
pulumi.export("retool_mission_control_app_id", mission_control_app.id)
pulumi.export("retool_mission_control_app_name", mission_control_app.name) 