"""Database resource definitions for Sophia AI"""

from pulumi_snowflake import Database


def create_sophia_ai_database():
    """Create the main SOPHIA_AI database"""
    return Database(
        "sophia-ai-database",
        name="SOPHIA_AI",
        comment="Main database for Sophia AI platform - managed by Pulumi IaC",
        data_retention_time_in_days=7,  # 7 days for dev, increase for prod
    )
