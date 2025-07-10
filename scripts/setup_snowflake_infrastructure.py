#!/usr/bin/env python3
"""
Set up Snowflake infrastructure for Sophia AI
This script creates all necessary databases, schemas, tables, and roles
"""

import os
import sys

# Remove current directory from Python path to avoid conflicts with snowflake package
if os.getcwd() in sys.path:
    sys.path.remove(os.getcwd())
if "" in sys.path:
    sys.path.remove("")

from pathlib import Path

import snowflake.connector


def load_snowflake_config():
    """Load Snowflake configuration from environment"""
    # Try to load from local.env first
    env_file = Path("local.env")
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key.strip()] = value.strip()

    # Try PAT token first, then regular password
    pat_token = os.getenv("SNOWFLAKE_PAT")
    password = pat_token if pat_token else os.getenv("SNOWFLAKE_PASSWORD")

    return {
        "account": os.getenv("SNOWFLAKE_ACCOUNT", "UHDECNO-CVB64222"),
        "user": os.getenv("SNOWFLAKE_USER", "SCOOBYJAVA15"),
        "password": password,
        "role": "ACCOUNTADMIN",
    }


def create_warehouses(cursor):
    """Create compute warehouses"""
    print("🏗️ Creating warehouses...")

    warehouses = [
        {
            "name": "SOPHIA_AI_COMPUTE_WH",
            "size": "MEDIUM",
            "auto_suspend": 60,
            "auto_resume": True,
            "comment": "Primary compute warehouse for Sophia AI",
        },
        {
            "name": "SOPHIA_AI_ETL_WH",
            "size": "LARGE",
            "auto_suspend": 300,
            "auto_resume": True,
            "comment": "ETL and data processing warehouse",
        },
        {
            "name": "SOPHIA_AI_ANALYTICS_WH",
            "size": "SMALL",
            "auto_suspend": 120,
            "auto_resume": True,
            "comment": "Analytics and reporting warehouse",
        },
    ]

    for wh in warehouses:
        sql = f"""
        CREATE WAREHOUSE IF NOT EXISTS {wh['name']}
        WITH
            WAREHOUSE_SIZE = '{wh['size']}'
            AUTO_SUSPEND = {wh['auto_suspend']}
            AUTO_RESUME = {wh['auto_resume']}
            COMMENT = '{wh['comment']}'
        """
        cursor.execute(sql)
        print(f"✅ Created warehouse: {wh['name']}")


def create_databases(cursor):
    """Create databases"""
    print("\n🏗️ Creating databases...")

    databases = [
        ("AI_MEMORY", "Primary AI memory and vector storage"),
        ("SOPHIA_AI_CORE", "Core business data and analytics"),
        ("SOPHIA_AI_STAGING", "Staging area for ETL processes"),
        ("SOPHIA_AI_ANALYTICS", "Analytics and reporting database"),
    ]

    for db_name, comment in databases:
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name} COMMENT = '{comment}'")
        print(f"✅ Created database: {db_name}")


def create_ai_memory_schemas(cursor):
    """Create schemas for AI Memory database"""
    print("\n🏗️ Creating AI Memory schemas...")

    cursor.execute("USE DATABASE AI_MEMORY")

    schemas = [
        ("VECTORS", "Vector embeddings and semantic search"),
        ("MEMORY", "Conversational and agent memory"),
        ("KNOWLEDGE", "Knowledge base and documents"),
        ("CORTEX", "Snowflake Cortex AI functions"),
        ("MONITORING", "Performance and usage monitoring"),
    ]

    for schema_name, comment in schemas:
        cursor.execute(
            f"CREATE SCHEMA IF NOT EXISTS {schema_name} COMMENT = '{comment}'"
        )
        print(f"✅ Created schema: AI_MEMORY.{schema_name}")


def create_vector_tables(cursor):
    """Create vector storage tables"""
    print("\n🏗️ Creating vector tables...")

    cursor.execute("USE SCHEMA AI_MEMORY.VECTORS")

    # Knowledge base table with vector embeddings
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS KNOWLEDGE_BASE (
            id VARCHAR(36) DEFAULT UUID_STRING(),
            content TEXT NOT NULL,
            embedding VECTOR(FLOAT, 768),
            metadata VARIANT,
            source VARCHAR(500),
            source_type VARCHAR(50),
            created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
            updated_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
            PRIMARY KEY (id)
        )
    """
    )
    print("✅ Created table: KNOWLEDGE_BASE")

    # Document chunks table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS DOCUMENT_CHUNKS (
            id VARCHAR(36) DEFAULT UUID_STRING(),
            document_id VARCHAR(36) NOT NULL,
            chunk_index INTEGER NOT NULL,
            content TEXT NOT NULL,
            embedding VECTOR(FLOAT, 768),
            metadata VARIANT,
            created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
            PRIMARY KEY (id),
            UNIQUE KEY (document_id, chunk_index)
        )
    """
    )
    print("✅ Created table: DOCUMENT_CHUNKS")

    # Entity embeddings table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS ENTITY_EMBEDDINGS (
            id VARCHAR(36) DEFAULT UUID_STRING(),
            entity_type VARCHAR(50) NOT NULL,
            entity_id VARCHAR(100) NOT NULL,
            entity_name VARCHAR(500),
            embedding VECTOR(FLOAT, 768),
            metadata VARIANT,
            created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
            updated_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
            PRIMARY KEY (id),
            UNIQUE KEY (entity_type, entity_id)
        )
    """
    )
    print("✅ Created table: ENTITY_EMBEDDINGS")


def create_memory_tables(cursor):
    """Create memory storage tables"""
    print("\n🏗️ Creating memory tables...")

    cursor.execute("USE SCHEMA AI_MEMORY.MEMORY")

    # Conversational memory
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS CONVERSATIONAL_MEMORY (
            id VARCHAR(36) DEFAULT UUID_STRING(),
            user_id VARCHAR(100),
            session_id VARCHAR(100),
            content TEXT NOT NULL,
            embedding VECTOR(FLOAT, 768),
            metadata VARIANT,
            memory_type VARCHAR(50),
            importance_score FLOAT DEFAULT 0.5,
            created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
            PRIMARY KEY (id),
            INDEX idx_user_session (user_id, session_id)
        )
    """
    )
    print("✅ Created table: CONVERSATIONAL_MEMORY")

    # Agent memory
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS AGENT_MEMORY (
            id VARCHAR(36) DEFAULT UUID_STRING(),
            agent_id VARCHAR(100) NOT NULL,
            memory_type VARCHAR(50) NOT NULL,
            content TEXT NOT NULL,
            embedding VECTOR(FLOAT, 768),
            metadata VARIANT,
            importance_score FLOAT DEFAULT 0.5,
            created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
            expires_at TIMESTAMP_NTZ,
            PRIMARY KEY (id),
            INDEX idx_agent (agent_id, memory_type)
        )
    """
    )
    print("✅ Created table: AGENT_MEMORY")

    # Memory consolidation
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS MEMORY_CONSOLIDATION (
            id VARCHAR(36) DEFAULT UUID_STRING(),
            source_type VARCHAR(50) NOT NULL,
            consolidated_content TEXT NOT NULL,
            original_memory_ids ARRAY,
            embedding VECTOR(FLOAT, 768),
            metadata VARIANT,
            consolidation_score FLOAT,
            created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
            PRIMARY KEY (id)
        )
    """
    )
    print("✅ Created table: MEMORY_CONSOLIDATION")


def create_business_tables(cursor):
    """Create core business tables"""
    print("\n🏗️ Creating business tables...")

    cursor.execute("USE DATABASE SOPHIA_AI_CORE")
    cursor.execute("CREATE SCHEMA IF NOT EXISTS BUSINESS")
    cursor.execute("USE SCHEMA BUSINESS")

    # Gong call data
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS GONG_CALLS (
            id VARCHAR(100) PRIMARY KEY,
            title VARCHAR(1000),
            participants VARIANT,
            transcript TEXT,
            summary TEXT,
            sentiment_score FLOAT,
            topics ARRAY,
            action_items VARIANT,
            risks VARIANT,
            opportunities VARIANT,
            embedding VECTOR(FLOAT, 768),
            metadata VARIANT,
            call_date TIMESTAMP_NTZ,
            created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
        )
    """
    )
    print("✅ Created table: GONG_CALLS")

    # HubSpot data
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS HUBSPOT_CONTACTS (
            id VARCHAR(100) PRIMARY KEY,
            email VARCHAR(500),
            firstname VARCHAR(100),
            lastname VARCHAR(100),
            company VARCHAR(500),
            properties VARIANT,
            embedding VECTOR(FLOAT, 768),
            metadata VARIANT,
            created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
            updated_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
        )
    """
    )
    print("✅ Created table: HUBSPOT_CONTACTS")

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS HUBSPOT_DEALS (
            id VARCHAR(100) PRIMARY KEY,
            dealname VARCHAR(1000),
            amount FLOAT,
            stage VARCHAR(100),
            close_date DATE,
            properties VARIANT,
            embedding VECTOR(FLOAT, 768),
            metadata VARIANT,
            created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
            updated_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
        )
    """
    )
    print("✅ Created table: HUBSPOT_DEALS")


def create_monitoring_tables(cursor):
    """Create monitoring and analytics tables"""
    print("\n🏗️ Creating monitoring tables...")

    cursor.execute("USE SCHEMA AI_MEMORY.MONITORING")

    # Query performance
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS QUERY_PERFORMANCE (
            id VARCHAR(36) DEFAULT UUID_STRING(),
            query_type VARCHAR(50),
            query_text TEXT,
            execution_time_ms INTEGER,
            rows_returned INTEGER,
            warehouse_used VARCHAR(100),
            user_id VARCHAR(100),
            metadata VARIANT,
            created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
            PRIMARY KEY (id)
        )
    """
    )
    print("✅ Created table: QUERY_PERFORMANCE")

    # AI usage metrics
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS AI_USAGE_METRICS (
            id VARCHAR(36) DEFAULT UUID_STRING(),
            function_name VARCHAR(100),
            model_used VARCHAR(100),
            tokens_used INTEGER,
            cost_estimate FLOAT,
            execution_time_ms INTEGER,
            user_id VARCHAR(100),
            metadata VARIANT,
            created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
            PRIMARY KEY (id)
        )
    """
    )
    print("✅ Created table: AI_USAGE_METRICS")


def create_roles_and_permissions(cursor):
    """Create roles and set permissions"""
    print("\n🏗️ Creating roles and permissions...")

    roles = [
        ("SOPHIA_AI_ADMIN", "Full administrative access to Sophia AI"),
        ("SOPHIA_AI_DEVELOPER", "Developer access for Sophia AI"),
        ("SOPHIA_AI_ANALYST", "Read-only analyst access"),
        ("SOPHIA_AI_SERVICE", "Service account for applications"),
    ]

    for role_name, comment in roles:
        cursor.execute(f"CREATE ROLE IF NOT EXISTS {role_name} COMMENT = '{comment}'")
        print(f"✅ Created role: {role_name}")

    # Grant permissions
    cursor.execute("GRANT ROLE SOPHIA_AI_ADMIN TO ROLE ACCOUNTADMIN")
    cursor.execute("GRANT ROLE SOPHIA_AI_DEVELOPER TO ROLE SOPHIA_AI_ADMIN")
    cursor.execute("GRANT ROLE SOPHIA_AI_ANALYST TO ROLE SOPHIA_AI_DEVELOPER")
    cursor.execute("GRANT ROLE SOPHIA_AI_SERVICE TO ROLE SOPHIA_AI_DEVELOPER")

    # Grant warehouse usage
    for role in ["SOPHIA_AI_ADMIN", "SOPHIA_AI_DEVELOPER", "SOPHIA_AI_SERVICE"]:
        cursor.execute(f"GRANT USAGE ON WAREHOUSE SOPHIA_AI_COMPUTE_WH TO ROLE {role}")
        cursor.execute(f"GRANT USAGE ON WAREHOUSE SOPHIA_AI_ETL_WH TO ROLE {role}")

    cursor.execute(
        "GRANT USAGE ON WAREHOUSE SOPHIA_AI_ANALYTICS_WH TO ROLE SOPHIA_AI_ANALYST"
    )

    # Grant database access
    for db in [
        "AI_MEMORY",
        "SOPHIA_AI_CORE",
        "SOPHIA_AI_STAGING",
        "SOPHIA_AI_ANALYTICS",
    ]:
        cursor.execute(f"GRANT USAGE ON DATABASE {db} TO ROLE SOPHIA_AI_SERVICE")
        cursor.execute(f"GRANT ALL ON DATABASE {db} TO ROLE SOPHIA_AI_DEVELOPER")
        cursor.execute(f"GRANT USAGE ON DATABASE {db} TO ROLE SOPHIA_AI_ANALYST")

    print("✅ Permissions granted")


def create_cortex_functions(cursor):
    """Create Snowflake Cortex AI functions and procedures"""
    print("\n🏗️ Creating Cortex AI functions...")

    cursor.execute("USE SCHEMA AI_MEMORY.CORTEX")

    # Semantic search function
    cursor.execute(
        """
        CREATE OR REPLACE FUNCTION SEMANTIC_SEARCH(
            query_text STRING,
            table_name STRING,
            embedding_column STRING,
            limit_count INTEGER DEFAULT 10,
            threshold FLOAT DEFAULT 0.7
        )
        RETURNS TABLE(id STRING, content STRING, similarity FLOAT, metadata VARIANT)
        AS $$
            WITH query_embedding AS (
                SELECT SNOWFLAKE.CORTEX.EMBED_TEXT_768('e5-base-v2', query_text) as embedding
            )
            SELECT
                id,
                content,
                VECTOR_COSINE_SIMILARITY(embedding, q.embedding) as similarity,
                metadata
            FROM IDENTIFIER(table_name) t, query_embedding q
            WHERE VECTOR_COSINE_SIMILARITY(t.embedding, q.embedding) > threshold
            ORDER BY similarity DESC
            LIMIT limit_count
        $$
    """
    )
    print("✅ Created function: SEMANTIC_SEARCH")

    # Text summarization procedure
    cursor.execute(
        """
        CREATE OR REPLACE PROCEDURE SUMMARIZE_TEXT(text STRING)
        RETURNS STRING
        LANGUAGE SQL
        AS
        BEGIN
            RETURN SNOWFLAKE.CORTEX.SUMMARIZE(text);
        END
    """
    )
    print("✅ Created procedure: SUMMARIZE_TEXT")

    # Sentiment analysis procedure
    cursor.execute(
        """
        CREATE OR REPLACE PROCEDURE ANALYZE_SENTIMENT(text STRING)
        RETURNS VARIANT
        LANGUAGE SQL
        AS
        BEGIN
            RETURN OBJECT_CONSTRUCT(
                'sentiment', SNOWFLAKE.CORTEX.SENTIMENT(text),
                'classification', SNOWFLAKE.CORTEX.CLASSIFY_TEXT(text, ARRAY_CONSTRUCT('positive', 'negative', 'neutral'))
            );
        END
    """
    )
    print("✅ Created procedure: ANALYZE_SENTIMENT")


def main():
    """Main function to set up Snowflake infrastructure"""
    print("🚀 Setting up Snowflake infrastructure for Sophia AI")

    # Load configuration
    config = load_snowflake_config()

    if not config["password"]:
        print("❌ Snowflake password not found in environment")
        sys.exit(1)

    # Initialize variables
    conn = None
    cursor = None

    try:
        # Connect to Snowflake
        print(f"\n🔌 Connecting to Snowflake account: {config['account']}")
        conn = snowflake.connector.connect(**config)
        cursor = conn.cursor()

        # Create infrastructure
        create_warehouses(cursor)
        create_databases(cursor)
        create_ai_memory_schemas(cursor)
        create_vector_tables(cursor)
        create_memory_tables(cursor)
        create_business_tables(cursor)
        create_monitoring_tables(cursor)
        create_roles_and_permissions(cursor)
        create_cortex_functions(cursor)

        # Commit changes
        conn.commit()

        print("\n✅ Snowflake infrastructure setup complete!")

        # Test the setup
        print("\n🧪 Testing setup...")
        cursor.execute("SELECT CURRENT_VERSION()")
        result = cursor.fetchone()
        if result:
            version = result[0]
            print(f"✅ Snowflake version: {version}")

        cursor.execute(
            "SELECT COUNT(*) FROM INFORMATION_SCHEMA.DATABASES WHERE DATABASE_NAME LIKE 'SOPHIA_AI%' OR DATABASE_NAME = 'AI_MEMORY'"
        )
        result = cursor.fetchone()
        if result:
            db_count = result[0]
            print(f"✅ Created {db_count} databases")

        cursor.execute(
            "SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA IN ('VECTORS', 'MEMORY', 'BUSINESS')"
        )
        result = cursor.fetchone()
        if result:
            table_count = result[0]
            print(f"✅ Created {table_count} tables")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


if __name__ == "__main__":
    main()
