#!/usr/bin/env python3
"""
Complete Snowflake Configuration Setup
Configure all Snowflake settings with working PAT token
"""

import os
import json
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_snowflake_configuration():
    """Setup complete Snowflake configuration with working credentials."""
    
    logger.info("🚀 Setting up complete Snowflake configuration")
    
    # Working credentials from successful test
    config = {
        'account': 'UHDECNO-CVB64222',  # Account locator (resolves to ZNB04675)
        'user': 'SCOOBYJAVA15',
        'password': 'eyJraWQiOiI1MDg3NDc2OTQxMyIsImFsZyI6IkVTMjU2In0.eyJwIjoiMTk4NzI5NDc2OjUwODc0NzQ1NDc3IiwiaXNzIjoiU0Y6MTA0OSIsImV4cCI6MTc4MjI4MDQ3OH0.8m-fWI5rvCs6b8bvw1quiM-UzW9uPRxMUmE6VAgOFFylAhRkCzch7ojh7CRLeMdii6DD1Owqap0KoOmyxsW77A',  # PAT token (JWT only)
        'role': 'ACCOUNTADMIN',
        'warehouse': 'COMPUTE_WH',
        'database': 'SOPHIA_AI',
        'schema': 'PROCESSED_AI'
    }
    
    logger.info("✅ Working configuration identified:")
    logger.info(f"   Account: {config['account']} (resolves to ZNB04675)")
    logger.info(f"   User: {config['user']}")
    logger.info(f"   Role: {config['role']}")
    logger.info(f"   PAT Token: Valid until June 24, 2026")
    
    return config

def test_complete_snowflake_setup():
    """Test complete Snowflake setup with database operations."""
    
    try:
        import snowflake.connector
        
        config = setup_snowflake_configuration()
        
        logger.info("🔗 Testing complete Snowflake setup...")
        
        # Connect with working configuration
        conn = snowflake.connector.connect(
            account=config['account'],
            user=config['user'],
            password=config['password'],
            role=config['role']
        )
        
        cursor = conn.cursor()
        
        # Test 1: Basic connection info
        cursor.execute("SELECT CURRENT_ACCOUNT(), CURRENT_USER(), CURRENT_ROLE(), CURRENT_WAREHOUSE(), CURRENT_DATABASE()")
        result = cursor.fetchone()
        
        logger.info("✅ Connection successful!")
        logger.info(f"   Actual Account: {result[0]}")
        logger.info(f"   User: {result[1]}")
        logger.info(f"   Role: {result[2]}")
        logger.info(f"   Warehouse: {result[3]}")
        logger.info(f"   Database: {result[4]}")
        
        # Test 2: List available databases
        cursor.execute("SHOW DATABASES")
        databases = cursor.fetchall()
        logger.info(f"✅ Available databases: {len(databases)}")
        
        db_names = [db[1] for db in databases]  # Database name is in second column
        logger.info(f"   Database names: {db_names}")
        
        # Test 3: List available warehouses
        cursor.execute("SHOW WAREHOUSES")
        warehouses = cursor.fetchall()
        logger.info(f"✅ Available warehouses: {len(warehouses)}")
        
        wh_names = [wh[0] for wh in warehouses]  # Warehouse name is in first column
        logger.info(f"   Warehouse names: {wh_names}")
        
        # Test 4: Check if SOPHIA_AI database exists
        if 'SOPHIA_AI' in db_names:
            logger.info("✅ SOPHIA_AI database exists")
            
            # Use the database and check schemas
            cursor.execute("USE DATABASE SOPHIA_AI")
            cursor.execute("SHOW SCHEMAS")
            schemas = cursor.fetchall()
            schema_names = [schema[1] for schema in schemas]
            logger.info(f"   Available schemas: {schema_names}")
            
        else:
            logger.info("⚠️ SOPHIA_AI database does not exist - will need to create")
        
        # Test 5: Check permissions
        cursor.execute("SHOW GRANTS TO ROLE ACCOUNTADMIN")
        grants = cursor.fetchall()
        logger.info(f"✅ ACCOUNTADMIN has {len(grants)} grants")
        
        cursor.close()
        conn.close()
        
        logger.info("🎉 Complete Snowflake setup test successful!")
        
        return {
            'status': 'success',
            'config': config,
            'actual_account': result[0],
            'databases': db_names,
            'warehouses': wh_names,
            'schemas': schema_names if 'SOPHIA_AI' in db_names else []
        }
        
    except Exception as e:
        logger.error(f"❌ Snowflake setup test failed: {e}")
        return {'status': 'failed', 'error': str(e)}

def create_snowflake_infrastructure():
    """Create necessary Snowflake infrastructure for Sophia AI."""
    
    try:
        import snowflake.connector
        
        config = setup_snowflake_configuration()
        
        logger.info("🏗️ Creating Snowflake infrastructure for Sophia AI...")
        
        conn = snowflake.connector.connect(
            account=config['account'],
            user=config['user'],
            password=config['password'],
            role=config['role']
        )
        
        cursor = conn.cursor()
        
        # Create database if it doesn't exist
        logger.info("📊 Creating SOPHIA_AI database...")
        cursor.execute("CREATE DATABASE IF NOT EXISTS SOPHIA_AI")
        
        # Create warehouse if it doesn't exist
        logger.info("🏭 Creating SOPHIA_AI_WH warehouse...")
        cursor.execute("""
            CREATE WAREHOUSE IF NOT EXISTS SOPHIA_AI_WH
            WITH WAREHOUSE_SIZE = 'SMALL'
            AUTO_SUSPEND = 300
            AUTO_RESUME = TRUE
            INITIALLY_SUSPENDED = FALSE
        """)
        
        # Use the database
        cursor.execute("USE DATABASE SOPHIA_AI")
        
        # Create schemas
        schemas_to_create = [
            'PROCESSED_AI',
            'RAW_DATA',
            'ANALYTICS',
            'CORTEX_AI',
            'REAL_ESTATE',
            'COLLECTIONS',
            'MONITORING'
        ]
        
        for schema in schemas_to_create:
            logger.info(f"📁 Creating schema {schema}...")
            cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {schema}")
        
        # Create sample tables for Sophia AI
        cursor.execute("USE SCHEMA PROCESSED_AI")
        
        # AI Memory table
        logger.info("🧠 Creating AI_MEMORY table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS AI_MEMORY (
                id STRING PRIMARY KEY,
                content STRING,
                tags ARRAY,
                timestamp TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
                access_count INTEGER DEFAULT 0,
                embedding VECTOR(FLOAT, 1536)
            )
        """)
        
        # Conversation History table
        logger.info("💬 Creating CONVERSATION_HISTORY table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS CONVERSATION_HISTORY (
                id STRING PRIMARY KEY,
                session_id STRING,
                content STRING,
                role STRING,
                timestamp TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
                metadata OBJECT
            )
        """)
        
        # Real Estate Collections table
        cursor.execute("USE SCHEMA COLLECTIONS")
        logger.info("🏠 Creating REAL_ESTATE_COLLECTIONS table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS REAL_ESTATE_COLLECTIONS (
                id STRING PRIMARY KEY,
                property_id STRING,
                debtor_info OBJECT,
                collection_status STRING,
                amount_owed DECIMAL(15,2),
                last_contact TIMESTAMP_NTZ,
                ai_analysis OBJECT,
                created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
                updated_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
            )
        """)
        
        # Analytics views with Cortex AI
        cursor.execute("USE SCHEMA ANALYTICS")
        logger.info("📈 Creating AI-powered analytics views...")
        
        cursor.execute("""
            CREATE OR REPLACE VIEW COLLECTION_INSIGHTS AS
            SELECT 
                collection_status,
                COUNT(*) as count,
                AVG(amount_owed) as avg_amount,
                SNOWFLAKE.CORTEX.SENTIMENT(MAX(ai_analysis:notes::STRING)) as sentiment_score,
                SNOWFLAKE.CORTEX.SUMMARIZE(LISTAGG(ai_analysis:notes::STRING, ' ')) as ai_summary
            FROM COLLECTIONS.REAL_ESTATE_COLLECTIONS
            GROUP BY collection_status
        """)
        
        cursor.close()
        conn.close()
        
        logger.info("🎉 Snowflake infrastructure created successfully!")
        
        return {
            'status': 'success',
            'database': 'SOPHIA_AI',
            'warehouse': 'SOPHIA_AI_WH',
            'schemas': schemas_to_create,
            'tables': ['AI_MEMORY', 'CONVERSATION_HISTORY', 'REAL_ESTATE_COLLECTIONS'],
            'views': ['COLLECTION_INSIGHTS']
        }
        
    except Exception as e:
        logger.error(f"❌ Infrastructure creation failed: {e}")
        return {'status': 'failed', 'error': str(e)}

def save_configuration_summary():
    """Save configuration summary for reference."""
    
    config = setup_snowflake_configuration()
    
    summary = {
        'snowflake_configuration': {
            'account_locator': config['account'],
            'actual_account': 'ZNB04675',  # From successful connection test
            'user': config['user'],
            'role': config['role'],
            'authentication': 'PAT (Programmatic Access Token)',
            'token_expiry': 'June 24, 2026',
            'warehouse': 'SOPHIA_AI_WH',
            'database': 'SOPHIA_AI',
            'default_schema': 'PROCESSED_AI'
        },
        'connection_details': {
            'url': f"https://{config['account']}.snowflakecomputing.com",
            'resolved_url': "https://ZNB04675.snowflakecomputing.com",
            'port': 443,
            'protocol': 'HTTPS'
        },
        'capabilities': {
            'cortex_ai': True,
            'vector_search': True,
            'full_admin_access': True,
            'bypasses_mfa': True,
            'bypasses_network_policies': True
        },
        'infrastructure': {
            'database': 'SOPHIA_AI',
            'warehouse': 'SOPHIA_AI_WH',
            'schemas': [
                'PROCESSED_AI',
                'RAW_DATA', 
                'ANALYTICS',
                'CORTEX_AI',
                'REAL_ESTATE',
                'COLLECTIONS',
                'MONITORING'
            ]
        }
    }
    
    # Save to file
    with open('snowflake_configuration_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    logger.info("💾 Configuration summary saved to snowflake_configuration_summary.json")
    
    return summary

if __name__ == "__main__":
    logger.info("🚀 Starting complete Snowflake configuration setup")
    
    # Test the setup
    test_result = test_complete_snowflake_setup()
    
    if test_result['status'] == 'success':
        logger.info("✅ Snowflake connection test successful")
        
        # Create infrastructure
        infra_result = create_snowflake_infrastructure()
        
        if infra_result['status'] == 'success':
            logger.info("✅ Snowflake infrastructure created successfully")
            
            # Save configuration summary
            summary = save_configuration_summary()
            
            logger.info("🎉 Complete Snowflake setup finished successfully!")
            logger.info("🔗 Ready for Sophia AI integration!")
            
        else:
            logger.error(f"❌ Infrastructure creation failed: {infra_result['error']}")
    
    else:
        logger.error(f"❌ Connection test failed: {test_result['error']}")

