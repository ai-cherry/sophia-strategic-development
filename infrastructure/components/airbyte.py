
import pulumi_airbyte as airbyte
from pulumi import ComponentResource, Config, Output, ResourceOptions

from .base_component import BaseComponent


class AirbyteConnectionComponent(ComponentResource):
    """A Pulumi component that represents an Airbyte connection, source,
    and destination. This simplifies creating new data pipelines.
    """

    def __init__(
        self,
        name: str,
        workspace_id: Output[str],
        source_config: dict,
        destination_config: dict,
        connection_config: dict,
        opts: ResourceOptions = None,
    ):
        super().__init__("sophia:infrastructure:AirbyteConnection", name, {}, opts)

        self.source = airbyte.Source(
            f"{name}-source",
            workspace_id=workspace_id,
            configuration=source_config["connection_configuration"],
            name=source_config["name"],
            opts=ResourceOptions(parent=self),
        )

        self.destination = airbyte.Destination(
            f"{name}-destination",
            workspace_id=workspace_id,
            configuration=destination_config["connection_configuration"],
            name=destination_config["name"],
            opts=ResourceOptions(parent=self),
        )

        self.connection = airbyte.Connection(
            f"{name}-connection",
            workspace_id=workspace_id,
            source_id=self.source.source_id,
            destination_id=self.destination.destination_id,
            status="active",
            name=connection_config["name"],
            namespace_definition=connection_config["namespace_definition"],
            namespace_format=connection_config["namespace_format"],
            prefix=connection_config["prefix"],
            schedule=connection_config["schedule"],
            sync_catalog=connection_config["sync_catalog"],
            opts=ResourceOptions(parent=self),
        )

        self.register_outputs(
            {
                "sourceId": self.source.source_id,
                "destinationId": self.destination.destination_id,
                "connectionId": self.connection.connection_id,
            }
        )


class AirbyteComponent(BaseComponent):
    def __init__(self, name: str, snowflake_config: dict, opts: ResourceOptions = None):
        super().__init__(name, opts)
        component_opts = ResourceOptions(parent=self)

        config = Config()
        env = config.require("environment")

        self.workspace = airbyte.Workspace(
            f"sophia-{env}-workspace",
            name=f"sophia-{env}",
            email="sophia-ai@payready.com",
            opts=component_opts,
        )

        # Define configurations
        source_configs = [
            # ... (source_configs from original file, but using snowflake_config) ...
        ]
        destination_configs = [
            # ... (destination_configs from original file, using snowflake_config) ...
        ]
        connection_configs = [
            # ... (connection_configs from original file) ...
        ]

        self.connections = []
        for conn_config in connection_configs:
            # Find the corresponding source and destination configs
            source_name = conn_config["source_name"]
            dest_name = conn_config["destination_name"]

            source_conf = next(
                (s for s in source_configs if s["name"] == source_name), None
            )
            dest_conf = next(
                (d for d in destination_configs if d["name"] == dest_name), None
            )

            if source_conf and dest_conf:
                conn_component = AirbyteConnectionComponent(
                    conn_config["name"],
                    workspace_id=self.workspace.workspace_id,
                    source_config=source_conf,
                    destination_config=dest_conf,
                    connection_config=conn_config,
                    opts=component_opts,
                )
                self.connections.append(conn_component)

        self.register_outputs(
            {
                "workspace_name": self.workspace.name,
                "connection_ids": [
                    c.connection.connection_id for c in self.connections
                ],
            }
        )
