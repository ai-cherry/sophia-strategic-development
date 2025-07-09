"""Schema resource definitions for Sophia AI"""

from pulumi_snowflake import Schema


def create_foundational_knowledge_schema(database_name: str):
    """Create the FOUNDATIONAL_KNOWLEDGE schema"""
    return Schema(
        "foundational-knowledge-schema",
        database=database_name,
        name="FOUNDATIONAL_KNOWLEDGE",
        comment="Core business knowledge: employees, customers, products, competitors",
        is_transient=False,
        is_managed=True,
        data_retention_days=30,
    )


def create_gong_schema(database_name: str):
    """Create the GONG schema for call data"""
    return Schema(
        "gong-schema",
        database=database_name,
        name="GONG",
        comment="Gong.io call recordings and analytics data",
        is_transient=False,
        is_managed=True,
        data_retention_days=90,
    )


def create_hubspot_schema(database_name: str):
    """Create the HUBSPOT schema for CRM data"""
    return Schema(
        "hubspot-schema",
        database=database_name,
        name="HUBSPOT",
        comment="HubSpot CRM data: contacts, deals, companies",
        is_transient=False,
        is_managed=True,
        data_retention_days=90,
    )


def create_slack_schema(database_name: str):
    """Create the SLACK schema for communication data"""
    return Schema(
        "slack-schema",
        database=database_name,
        name="SLACK",
        comment="Slack communication data and analytics",
        is_transient=False,
        is_managed=True,
        data_retention_days=30,
    )


def create_ai_memory_schema(database_name: str):
    """Create the AI_MEMORY schema for Sophia's memory"""
    return Schema(
        "ai-memory-schema",
        database=database_name,
        name="AI_MEMORY",
        comment="Sophia AI memory storage and context",
        is_transient=False,
        is_managed=True,
        data_retention_days=90,
    )
