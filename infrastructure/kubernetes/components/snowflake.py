import pulumi_snowflake as snowflake
from pulumi import Config, ResourceOptions

from .base_component import BaseComponent


class SnowflakeComponent(BaseComponent):
    def __init__(self, name: str, opts: ResourceOptions = None):
        super().__init__(name, opts)

        config = Config()
        env = config.require("environment")

        # Define resource names based on environment
        db_name = f"SOPHIA_DB_{env.upper()}"
        wh_name = f"SOPHIA_WH_{env.upper()}"
        schema_name = "RAW_DATA"
        role_name = f"SOPHIA_ROLE_{env.upper()}"

        # Create Snowflake resources
        self.database = snowflake.Database(
            db_name, name=db_name, comment="Database for the Sophia AI platform"
        )

        self.warehouse = snowflake.Warehouse(
            wh_name,
            name=wh_name,
            comment="Warehouse for the Sophia AI platform",
            warehouse_size="X-SMALL",
            auto_suspend=60,
            auto_resume=True,
            initially_suspended=True,
        )

        self.schema = snowflake.Schema(
            schema_name,
            name=schema_name,
            database=self.database.name,
            comment="Schema for raw data ingested from various sources",
        )

        self.role = snowflake.Role(
            role_name, name=role_name, comment="Role for Sophia AI application access"
        )

        # Grant privileges
        # ... (grant logic would go here)

        # Register outputs
        self.register_outputs(
            {
                "warehouse_name": self.warehouse.name,
                "database_name": self.database.name,
                "schema_name": self.schema.name,
                "role_name": self.role.name,
            }
        )
