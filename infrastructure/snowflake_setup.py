"""Pulumi script for setting up Snowflake resources for Sophia AI.

This includes the database, warehouse, schemas, and roles.
"""

import pulumi
import pulumi_snowflake as snowflake

# --- Configuration ---
# These values can be customized in Pulumi.<stack>.yaml
config = pulumi.Config()
db_name = config.get("snowflake_db_name", "SOPHIA_DB")
warehouse_name = config.get("snowflake_warehouse_name", "SOPHIA_WH")
admin_role_name = "SOPHIA_ADMIN"

# --- Resource Definitions ---

# 1. Create the main database for the application
sophia_db = snowflake.Database(
    db_name, name=db_name, comment="Main database for the Sophia AI application."
)

# 2. Create the primary data warehouse for compute
sophia_warehouse = snowflake.Warehouse(
    warehouse_name,
    name=warehouse_name,
    comment="Primary data warehouse for Sophia AI processing and analytics.",
    warehouse_size="X-Small",
    auto_suspend=60,  # Suspend after 60 seconds of inactivity
    auto_resume=True,
)

# 3. Create necessary schemas within the database
raw_schema = snowflake.Schema(
    "schema-raw",
    database=sophia_db.name,
    name="SOPHIA_RAW",
    comment="Schema for raw, unprocessed data ingested from sources.",
)

analytics_schema = snowflake.Schema(
    "schema-analytics",
    database=sophia_db.name,
    name="SOPHIA_ANALYTICS",
    comment="Schema for transformed data ready for analytics and BI.",
)

# 4. Create a dedicated role for the application admin/service account
sophia_admin_role = snowflake.Role(
    admin_role_name,
    name=admin_role_name,
    comment="Admin role for the Sophia AI application.",
)

# 5. Grant privileges to the new role
# Grant usage on the database
snowflake.RoleGrants(
    f"grant-db-usage-to-{admin_role_name}",
    role_name=sophia_admin_role.name,
    roles=[],  # Not granting other roles
    users=[],
    privileges=["USAGE"],
    on="DATABASE",
    name=sophia_db.name,
)

# Grant usage on the warehouse
snowflake.RoleGrants(
    f"grant-warehouse-usage-to-{admin_role_name}",
    role_name=sophia_admin_role.name,
    privileges=["USAGE", "OPERATE"],
    on="WAREHOUSE",
    name=sophia_warehouse.name,
)

# Grant all privileges on the schemas
for schema in [raw_schema, analytics_schema]:
    snowflake.RoleGrants(
        f"grant-schema-all-on-{schema._name}-to-{admin_role_name}",
        role_name=sophia_admin_role.name,
        privileges=["ALL"],
        on="SCHEMA",
        name=pulumi.Output.concat(sophia_db.name, ".", schema.name),
    )

# --- Outputs ---
pulumi.export("snowflake_database_name", sophia_db.name)
pulumi.export("snowflake_warehouse_name", sophia_warehouse.name)
pulumi.export("snowflake_raw_schema", raw_schema.name)
pulumi.export("snowflake_analytics_schema", analytics_schema.name)
pulumi.export("snowflake_admin_role", sophia_admin_role.name)
