"""Roles and grants resource definitions for Sophia AI"""

from pulumi_snowflake import Grant, Role, RoleGrants


def setup_roles_and_grants(database_name: str, schemas: dict, warehouses: dict):
    """Setup roles and access grants"""
    roles = {}

    # Create roles
    roles["data_engineer"] = Role(
        "data-engineer-role",
        name="SOPHIA_AI_DATA_ENGINEER",
        comment="Role for data engineers managing ETL pipelines",
    )

    roles["data_analyst"] = Role(
        "data-analyst-role",
        name="SOPHIA_AI_DATA_ANALYST",
        comment="Role for data analysts querying data",
    )

    roles["sophia_app"] = Role(
        "sophia-app-role",
        name="SOPHIA_AI_APPLICATION",
        comment="Role for Sophia AI application access",
    )

    roles["mcp_server"] = Role(
        "mcp-server-role",
        name="SOPHIA_AI_MCP_SERVER",
        comment="Role for MCP servers to sync data",
    )

    # Grant warehouse usage
    for role_key, role in roles.items():
        for warehouse_key, warehouse in warehouses.items():
            Grant(
                f"grant-warehouse-{warehouse_key}-to-{role_key}",
                privilege="USAGE",
                on_warehouse=warehouse.name,
                roles=[role.name],
            )

    # Grant database access
    for role_key, role in roles.items():
        Grant(
            f"grant-database-usage-to-{role_key}",
            privilege="USAGE",
            on_database=database_name,
            roles=[role.name],
        )

    # Grant schema access
    for role_key, role in roles.items():
        for schema_key, schema in schemas.items():
            Grant(
                f"grant-schema-usage-{schema_key}-to-{role_key}",
                privilege="USAGE",
                on_schema=f"{database_name}.{schema.name}",
                roles=[role.name],
            )

    # Grant specific privileges for Sophia AI application
    Grant(
        "grant-select-foundational-knowledge",
        privilege="SELECT",
        on_all_tables_in_schema=f"{database_name}.{schemas['foundational_knowledge'].name}",
        roles=[roles["sophia_app"].name],
    )

    Grant(
        "grant-select-ai-memory",
        privilege="SELECT",
        on_all_tables_in_schema=f"{database_name}.{schemas['ai_memory'].name}",
        roles=[roles["sophia_app"].name],
    )

    # Grant write privileges for MCP servers
    for schema_key in ["foundational_knowledge", "gong", "hubspot", "slack"]:
        Grant(
            f"grant-write-{schema_key}-to-mcp",
            privilege="INSERT",
            on_all_tables_in_schema=f"{database_name}.{schemas[schema_key].name}",
            roles=[roles["mcp_server"].name],
        )

        Grant(
            f"grant-update-{schema_key}-to-mcp",
            privilege="UPDATE",
            on_all_tables_in_schema=f"{database_name}.{schemas[schema_key].name}",
            roles=[roles["mcp_server"].name],
        )

    # Grant role hierarchy
    RoleGrants(
        "grant-analyst-to-engineer",
        role_name=roles["data_analyst"].name,
        roles=[roles["data_engineer"].name],
    )

    return roles
