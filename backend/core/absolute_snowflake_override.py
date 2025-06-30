"""
ABSOLUTE SNOWFLAKE OVERRIDE - DO NOT MODIFY
This file provides the FINAL, ABSOLUTE override for Snowflake configuration
"""


def get_snowflake_connection_params():
    """Get ABSOLUTE Snowflake connection parameters - CANNOT BE OVERRIDDEN"""
    return {
        "account": "ZNB04675",  # ABSOLUTE - NEVER CHANGE
        "user": "SCOOBYJAVA15",
        "password": "Gsk_6oDcGjZtRQ5H4yD1lCZJlFzRmOOhGhVb6P9E",  # From Pulumi ESC
        "role": "ACCOUNTADMIN",
        "warehouse": "SOPHIA_AI_WH",
        "database": "SOPHIA_AI",
        "schema": "PROCESSED_AI",
        "timeout": 30,
    }


# Immediately set environment variables when imported
import os

os.environ["SNOWFLAKE_ACCOUNT"] = "ZNB04675"
os.environ["SNOWFLAKE_USER"] = "SCOOBYJAVA15"
os.environ["SNOWFLAKE_DATABASE"] = "SOPHIA_AI"
os.environ["SNOWFLAKE_WAREHOUSE"] = "SOPHIA_AI_WH"
os.environ["SNOWFLAKE_ROLE"] = "ACCOUNTADMIN"
os.environ["SNOWFLAKE_SCHEMA"] = "PROCESSED_AI"

print("🔧 ABSOLUTE Snowflake override applied - Account: ZNB04675")
