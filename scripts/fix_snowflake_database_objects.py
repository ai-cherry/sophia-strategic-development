#!/usr/bin/env python3
"""
Fix Snowflake Database Objects for Sophia AI
Creates missing schemas and tables causing SQL compilation errors
"""

import asyncio
import logging
from backend.core.optimized_connection_manager import OptimizedConnectionManager, ConnectionType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def create_missing_database_objects():
    """Create missing Snowflake database objects."""
    logger.info("🔧 Creating missing Snowflake database objects")
    
    connection_manager = OptimizedConnectionManager()
    
    try:
        # Get Snowflake connection
        conn = await connection_manager.get_connection(ConnectionType.SNOWFLAKE)
        
        # SQL commands to create missing objects
        sql_commands = [
            "USE DATABASE SOPHIA_AI_PROD;",
            "USE WAREHOUSE SOPHIA_AI_WH;",
            
            # Create schemas
            "CREATE SCHEMA IF NOT EXISTS PROCESSED_AI;",
            "CREATE SCHEMA IF NOT EXISTS RAW_DATA;", 
            "CREATE SCHEMA IF NOT EXISTS ANALYTICS;",
            "CREATE SCHEMA IF NOT EXISTS CORTEX;",
            
            # Core conversation tables
            """CREATE TABLE IF NOT EXISTS PROCESSED_AI.CONVERSATION_HISTORY (
                id STRING PRIMARY KEY,
                session_id STRING,
                user_id STRING,
                message_content STRING,
                response_content STRING,
                timestamp TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
                metadata VARIANT
            );""",
            
            # Automated insights tables
            """CREATE TABLE IF NOT EXISTS ANALYTICS.INSIGHTS (
                id STRING PRIMARY KEY,
                insight_type STRING,
                content STRING,
                confidence_score FLOAT,
                created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
                metadata VARIANT
            );""",
            
            # Cortex AI functions table
            """CREATE TABLE IF NOT EXISTS CORTEX.AI_FUNCTIONS (
                function_name STRING PRIMARY KEY,
                function_type STRING,
                parameters VARIANT,
                created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
            );""",
            
            # Knowledge base table
            """CREATE TABLE IF NOT EXISTS PROCESSED_AI.KNOWLEDGE_BASE (
                id STRING PRIMARY KEY,
                title STRING,
                content STRING,
                category STRING,
                tags ARRAY,
                embedding ARRAY,
                created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
                updated_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
            );"""
        ]
        
        # Execute each command
        for sql in sql_commands:
            try:
                logger.info(f"Executing: {sql[:50]}...")
                cursor = conn.cursor()
                cursor.execute(sql)
                cursor.close()
                logger.info("✅ Command executed successfully")
            except Exception as e:
                logger.error(f"❌ Error executing SQL: {e}")
                # Continue with other commands
        
        logger.info("✅ Database objects created successfully")
        
    except Exception as e:
        logger.error(f"❌ Failed to create database objects: {e}")
        raise
    finally:
        await connection_manager.close_all_connections()

if __name__ == "__main__":
    asyncio.run(create_missing_database_objects())
