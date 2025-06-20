from pulumi import ComponentResource, ResourceOptions, Config
import pulumi_pulumiservice as pulumiservice
import json

from .base_component import BaseComponent

class PulumiEscComponent(BaseComponent):
    def __init__(self, name: str, opts: ResourceOptions = None):
        super().__init__(name, opts)
        component_opts = ResourceOptions(parent=self)

        config = Config()
        env = config.require("environment")
        
        pulumi_organization = config.require("pulumi_organization")
        pulumi_project = config.require("pulumi_project")

        self.esc_environment = pulumiservice.Environment(f"sophia-{env}",
            organization=pulumi_organization,
            name=f"sophia-{env}",
            description=f"Sophia AI environment for {env}",
            opts=component_opts
        )

        # In a real component, you would pass the secrets in as a structured input
        # instead of reading them all from config here.
        secrets_to_create = {
            "SNOWFLAKE_PASSWORD": config.require_secret("snowflake_password"),
            "GONG_API_KEY": config.require_secret("gong_api_key"),
            # ... and so on
        }

        for name, value in secrets_to_create.items():
            pulumiservice.EnvironmentSecret(f"sophia-{env}-{name}-secret",
                organization=pulumi_organization,
                environment=self.esc_environment.name,
                name=name,
                value=value,
                opts=component_opts
            )

        self.stack = pulumiservice.Stack(f"sophia-{env}-stack",
            organization=pulumi_organization,
            project=pulumi_project,
            stack=env,
            opts=component_opts
        )

        self.stack_binding = pulumiservice.StackEnvironmentBinding(f"sophia-{env}-stack-binding",
            organization=pulumi_organization,
            project=pulumi_project,
            stack=self.stack.stack,
            environment=self.esc_environment.name,
            opts=component_opts
        )

        self.register_outputs({
            "environment_name": self.esc_environment.name,
            "stack_name": self.stack.stack,
            "project_name": pulumi_project,
            "organization_name": pulumi_organization
        }) 