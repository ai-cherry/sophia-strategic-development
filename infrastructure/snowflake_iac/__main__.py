"""
Sophia AI Snowflake Infrastructure as Code
Main Pulumi program for managing Snowflake resources
"""

from snowflake_resources.database import create_sophia_ai_database
from snowflake_resources.roles_grants import setup_roles_and_grants
from snowflake_resources.schemas import (
    create_ai_memory_schema,
    create_foundational_knowledge_schema,
    create_gong_schema,
    create_hubspot_schema,
    create_slack_schema,
)
from snowflake_resources.tables import (
    create_existing_tables,
    create_foundational_knowledge_tables,
)
from snowflake_resources.tasks_streams import create_embedding_tasks
from snowflake_resources.views import create_foundational_knowledge_views
from snowflake_resources.warehouses import create_warehouses

import pulumi

# Create Database
db = create_sophia_ai_database()

# Create Schemas
schemas = {
    "foundational_knowledge": create_foundational_knowledge_schema(db.name),
    "gong": create_gong_schema(db.name),
    "hubspot": create_hubspot_schema(db.name),
    "slack": create_slack_schema(db.name),
    "ai_memory": create_ai_memory_schema(db.name),
}

# Create Warehouses
warehouses = create_warehouses()

# Create Tables
tables = create_foundational_knowledge_tables(
    db.name, schemas["foundational_knowledge"].name
)
existing_tables = create_existing_tables(db.name, schemas)

# Create Views
views = create_foundational_knowledge_views(
    db.name, schemas["foundational_knowledge"].name
)

# Setup Roles and Grants
roles = setup_roles_and_grants(db.name, schemas, warehouses)

# Create Tasks for Embeddings
tasks = create_embedding_tasks(
    db.name, schemas["foundational_knowledge"].name, warehouses["analytics"].name
)

# Export important outputs
pulumi.export("database_name", db.name)
pulumi.export("foundational_knowledge_schema", schemas["foundational_knowledge"].name)
pulumi.export("warehouses", {k: v.name for k, v in warehouses.items()})
pulumi.export("roles", {k: v.name for k, v in roles.items()})
