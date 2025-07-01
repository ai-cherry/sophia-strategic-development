#!/usr/bin/env python3
"""
Snowflake Alignment Setup Script
Connects to Snowflake using provided credentials and sets up all necessary schemas,
tables, and configurations for the Sophia AI pure Estuary Flow pipeline
"""

import json
import logging
import sys
from datetime import datetime
from typing import Dict, List, Optional

import snowflake.connector
from snowflake.connector import DictCursor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SnowflakeAlignmentSetup:
    """
    Snowflake alignment setup for Sophia AI
    Sets up all necessary schemas, tables, and configurations
    """
    
    def __init__(self):
        # Snowflake connection parameters from user
        self.connection_params = {
            'account': 'UHDECNO-CVB64222',
            'user': 'SCOOBYJAVA15',
            'password': 'eyJraWQiOiI1MDg3NDc2OTQxMyIsImFsZyI6IkVTMjU2In0.eyJwIjoiMTk4NzI5NDc2OjUwODc0NzQ1NDc3IiwiaXNzIjoiU0Y6MTA0OSIsImV4cCI6MTc4MjI4MDQ3OH0.8m-fWI5rvCs6b8bvw1quiM-UzW9uPRxMUmE6VAgOFFylAhRkCzch7ojh7CRLeMdii6DD1Owqap0KoOmyxsW77A',
            'role': 'ACCOUNTADMIN'
        }
        self.connection = None
        self.setup_status = {
            'connection_established': False,
            'warehouse_created': False,
            'database_created': False,
            'schemas_created': False,
            'tables_created': False,
            'cortex_functions_tested': False,
            'estuary_integration_configured': False,
            'gong_data_share_checked': False
        }
    
    def connect_to_snowflake(self, attempt: int = 1) -> bool:
        """
        Connect to Snowflake with provided credentials
        Only attempts twice to avoid 5-attempt lockout
        """
        logger.info(f"🔌 Attempting Snowflake connection (attempt {attempt}/2)...")
        
        try:
            self.connection = snowflake.connector.connect(**self.connection_params)
            
            # Test connection
            cursor = self.connection.cursor()
            cursor.execute("SELECT CURRENT_VERSION(), CURRENT_USER(), CURRENT_ROLE()")
            result = cursor.fetchone()
            
            logger.info(f"✅ Connected to Snowflake successfully!")
            logger.info(f"   Version: {result[0]}")
            logger.info(f"   User: {result[1]}")
            logger.info(f"   Role: {result[2]}")
            
            cursor.close()
            self.setup_status['connection_established'] = True
            return True
            
        except Exception as e:
            logger.error(f"❌ Snowflake connection failed (attempt {attempt}): {e}")
            if attempt < 2:
                logger.info("🔄 Retrying connection...")
                return self.connect_to_snowflake(attempt + 1)
            else:
                logger.error("❌ Maximum connection attempts reached. Stopping to avoid lockout.")
                return False
    
    def setup_warehouse(self):
        """Create and configure Sophia AI warehouse"""
        logger.info("🏭 Setting up Sophia AI warehouse...")
        
        try:
            cursor = self.connection.cursor()
            
            # Create warehouse
            warehouse_sql = """
            CREATE WAREHOUSE IF NOT EXISTS SOPHIA_AI_WH
            WITH 
                WAREHOUSE_SIZE = 'MEDIUM'
                AUTO_SUSPEND = 300
                AUTO_RESUME = TRUE
                INITIALLY_SUSPENDED = FALSE
                COMMENT = 'Sophia AI data processing warehouse'
            """
            cursor.execute(warehouse_sql)
            
            # Use the warehouse
            cursor.execute("USE WAREHOUSE SOPHIA_AI_WH")
            
            logger.info("✅ Sophia AI warehouse created and configured")
            cursor.close()
            self.setup_status['warehouse_created'] = True
            
        except Exception as e:
            logger.error(f"❌ Warehouse setup failed: {e}")
            raise
    
    def setup_database_and_schemas(self):
        """Create database and all necessary schemas"""
        logger.info("🗄️ Setting up Sophia AI database and schemas...")
        
        try:
            cursor = self.connection.cursor()
            
            # Create database
            cursor.execute("CREATE DATABASE IF NOT EXISTS SOPHIA_AI_DB")
            cursor.execute("USE DATABASE SOPHIA_AI_DB")
            
            # Create schemas for different purposes
            schemas = [
                ('RAW_DATA', 'Raw data from Estuary Flow ingestion'),
                ('STAGING', 'Staging area for data transformations'),
                ('ANALYTICS', 'Analytics and business intelligence tables'),
                ('ESTUARY_FLOW', 'Estuary Flow materialization target'),
                ('CORTEX_AI', 'Snowflake Cortex AI functions and results'),
                ('VECTOR_SEARCH', 'Vector embeddings and search'),
                ('MONITORING', 'Pipeline monitoring and metrics')
            ]
            
            for schema_name, description in schemas:
                schema_sql = f"""
                CREATE SCHEMA IF NOT EXISTS {schema_name}
                COMMENT = '{description}'
                """
                cursor.execute(schema_sql)
                logger.info(f"✅ Created schema: {schema_name}")
            
            cursor.close()
            self.setup_status['database_created'] = True
            self.setup_status['schemas_created'] = True
            
        except Exception as e:
            logger.error(f"❌ Database/schema setup failed: {e}")
            raise
    
    def create_estuary_flow_tables(self):
        """Create tables for Estuary Flow data ingestion"""
        logger.info("📊 Creating Estuary Flow tables...")
        
        try:
            cursor = self.connection.cursor()
            cursor.execute("USE SCHEMA ESTUARY_FLOW")
            
            # HubSpot tables
            hubspot_contacts_sql = """
            CREATE TABLE IF NOT EXISTS HUBSPOT_CONTACTS (
                ID VARCHAR PRIMARY KEY,
                EMAIL VARCHAR,
                FIRSTNAME VARCHAR,
                LASTNAME VARCHAR,
                COMPANY VARCHAR,
                PHONE VARCHAR,
                CREATED_AT TIMESTAMP_NTZ,
                UPDATED_AT TIMESTAMP_NTZ,
                PROPERTIES VARIANT,
                _ESTUARY_FLOW_DOCUMENT VARIANT,
                _ESTUARY_FLOW_PUBLISHED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
            )
            """
            cursor.execute(hubspot_contacts_sql)
            
            hubspot_deals_sql = """
            CREATE TABLE IF NOT EXISTS HUBSPOT_DEALS (
                ID VARCHAR PRIMARY KEY,
                DEALNAME VARCHAR,
                AMOUNT NUMBER(15,2),
                DEALSTAGE VARCHAR,
                PIPELINE VARCHAR,
                CLOSEDATE TIMESTAMP_NTZ,
                CREATED_AT TIMESTAMP_NTZ,
                UPDATED_AT TIMESTAMP_NTZ,
                PROPERTIES VARIANT,
                _ESTUARY_FLOW_DOCUMENT VARIANT,
                _ESTUARY_FLOW_PUBLISHED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
            )
            """
            cursor.execute(hubspot_deals_sql)
            
            # Gong tables
            gong_calls_sql = """
            CREATE TABLE IF NOT EXISTS GONG_CALLS (
                ID VARCHAR PRIMARY KEY,
                TITLE VARCHAR,
                URL VARCHAR,
                STARTED TIMESTAMP_NTZ,
                DURATION INTEGER,
                PARTICIPANTS VARIANT,
                TRANSCRIPT TEXT,
                SUMMARY TEXT,
                SENTIMENT VARCHAR,
                TOPICS VARIANT,
                CREATED_AT TIMESTAMP_NTZ,
                _ESTUARY_FLOW_DOCUMENT VARIANT,
                _ESTUARY_FLOW_PUBLISHED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
            )
            """
            cursor.execute(gong_calls_sql)
            
            # Slack tables
            slack_messages_sql = """
            CREATE TABLE IF NOT EXISTS SLACK_MESSAGES (
                TS VARCHAR,
                CHANNEL VARCHAR,
                USER_ID VARCHAR,
                TEXT TEXT,
                THREAD_TS VARCHAR,
                REPLY_COUNT INTEGER,
                CREATED_AT TIMESTAMP_NTZ,
                _ESTUARY_FLOW_DOCUMENT VARIANT,
                _ESTUARY_FLOW_PUBLISHED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
                PRIMARY KEY (TS, CHANNEL)
            )
            """
            cursor.execute(slack_messages_sql)
            
            # Unified tables
            unified_contacts_sql = """
            CREATE TABLE IF NOT EXISTS UNIFIED_CONTACTS (
                CONTACT_ID VARCHAR PRIMARY KEY,
                SOURCE_SYSTEM VARCHAR,
                EMAIL VARCHAR,
                FIRSTNAME VARCHAR,
                LASTNAME VARCHAR,
                COMPANY VARCHAR,
                PHONE VARCHAR,
                CREATED_AT TIMESTAMP_NTZ,
                UPDATED_AT TIMESTAMP_NTZ,
                PROPERTIES VARIANT,
                PROCESSED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
            )
            """
            cursor.execute(unified_contacts_sql)
            
            deal_intelligence_sql = """
            CREATE TABLE IF NOT EXISTS DEAL_INTELLIGENCE (
                DEAL_ID VARCHAR PRIMARY KEY,
                DEALNAME VARCHAR,
                AMOUNT NUMBER(15,2),
                DEALSTAGE VARCHAR,
                PIPELINE VARCHAR,
                CLOSEDATE TIMESTAMP_NTZ,
                DEAL_TIER VARCHAR,
                DEAL_STATUS VARCHAR,
                CREATED_AT TIMESTAMP_NTZ,
                UPDATED_AT TIMESTAMP_NTZ,
                PROPERTIES VARIANT,
                PROCESSED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
            )
            """
            cursor.execute(deal_intelligence_sql)
            
            logger.info("✅ Estuary Flow tables created successfully")
            cursor.close()
            self.setup_status['tables_created'] = True
            
        except Exception as e:
            logger.error(f"❌ Table creation failed: {e}")
            raise
    
    def create_analytics_views(self):
        """Create analytics views and tables"""
        logger.info("📈 Creating analytics views...")
        
        try:
            cursor = self.connection.cursor()
            cursor.execute("USE SCHEMA ANALYTICS")
            
            # Contact analytics view
            contact_analytics_sql = """
            CREATE OR REPLACE VIEW CONTACT_ANALYTICS AS
            SELECT 
                c.CONTACT_ID,
                c.EMAIL,
                c.FIRSTNAME,
                c.LASTNAME,
                c.COMPANY,
                c.SOURCE_SYSTEM,
                COUNT(d.DEAL_ID) as TOTAL_DEALS,
                SUM(d.AMOUNT) as TOTAL_DEAL_VALUE,
                AVG(d.AMOUNT) as AVG_DEAL_VALUE,
                MAX(d.CLOSEDATE) as LAST_DEAL_DATE,
                c.CREATED_AT,
                c.UPDATED_AT
            FROM ESTUARY_FLOW.UNIFIED_CONTACTS c
            LEFT JOIN ESTUARY_FLOW.DEAL_INTELLIGENCE d ON c.EMAIL = d.PROPERTIES:contact_email::VARCHAR
            GROUP BY c.CONTACT_ID, c.EMAIL, c.FIRSTNAME, c.LASTNAME, c.COMPANY, c.SOURCE_SYSTEM, c.CREATED_AT, c.UPDATED_AT
            """
            cursor.execute(contact_analytics_sql)
            
            # Deal pipeline analytics
            deal_pipeline_sql = """
            CREATE OR REPLACE VIEW DEAL_PIPELINE_ANALYTICS AS
            SELECT 
                DEALSTAGE,
                PIPELINE,
                DEAL_TIER,
                DEAL_STATUS,
                COUNT(*) as DEAL_COUNT,
                SUM(AMOUNT) as TOTAL_VALUE,
                AVG(AMOUNT) as AVG_VALUE,
                MIN(CREATED_AT) as EARLIEST_DEAL,
                MAX(UPDATED_AT) as LATEST_UPDATE
            FROM ESTUARY_FLOW.DEAL_INTELLIGENCE
            GROUP BY DEALSTAGE, PIPELINE, DEAL_TIER, DEAL_STATUS
            """
            cursor.execute(deal_pipeline_sql)
            
            # Call analytics view
            call_analytics_sql = """
            CREATE OR REPLACE VIEW CALL_ANALYTICS AS
            SELECT 
                DATE_TRUNC('day', STARTED) as CALL_DATE,
                COUNT(*) as TOTAL_CALLS,
                AVG(DURATION) as AVG_DURATION,
                SUM(DURATION) as TOTAL_DURATION,
                COUNT(CASE WHEN SENTIMENT = 'positive' THEN 1 END) as POSITIVE_CALLS,
                COUNT(CASE WHEN SENTIMENT = 'negative' THEN 1 END) as NEGATIVE_CALLS,
                COUNT(CASE WHEN SENTIMENT = 'neutral' THEN 1 END) as NEUTRAL_CALLS
            FROM ESTUARY_FLOW.GONG_CALLS
            GROUP BY DATE_TRUNC('day', STARTED)
            ORDER BY CALL_DATE DESC
            """
            cursor.execute(call_analytics_sql)
            
            logger.info("✅ Analytics views created successfully")
            cursor.close()
            
        except Exception as e:
            logger.error(f"❌ Analytics view creation failed: {e}")
            raise
    
    def test_cortex_functions(self):
        """Test Snowflake Cortex AI functions"""
        logger.info("🧠 Testing Snowflake Cortex AI functions...")
        
        try:
            cursor = self.connection.cursor()
            cursor.execute("USE SCHEMA CORTEX_AI")
            
            # Test COMPLETE function
            complete_test_sql = """
            SELECT SNOWFLAKE.CORTEX.COMPLETE(
                'mistral-7b',
                'Summarize the key benefits of using Estuary Flow for data pipeline management:'
            ) as AI_RESPONSE
            """
            cursor.execute(complete_test_sql)
            result = cursor.fetchone()
            logger.info(f"✅ Cortex COMPLETE function test successful")
            logger.info(f"   Response preview: {result[0][:100]}...")
            
            # Test SENTIMENT function
            sentiment_test_sql = """
            SELECT SNOWFLAKE.CORTEX.SENTIMENT(
                'I am very excited about the new Sophia AI data pipeline implementation!'
            ) as SENTIMENT_SCORE
            """
            cursor.execute(sentiment_test_sql)
            result = cursor.fetchone()
            logger.info(f"✅ Cortex SENTIMENT function test successful")
            logger.info(f"   Sentiment score: {result[0]}")
            
            # Test EXTRACT_ANSWER function
            extract_test_sql = """
            SELECT SNOWFLAKE.CORTEX.EXTRACT_ANSWER(
                'Estuary Flow is a real-time data pipeline platform that enables organizations to build reliable, scalable data infrastructure.',
                'What is Estuary Flow?'
            ) as EXTRACTED_ANSWER
            """
            cursor.execute(extract_test_sql)
            result = cursor.fetchone()
            logger.info(f"✅ Cortex EXTRACT_ANSWER function test successful")
            logger.info(f"   Answer: {result[0]}")
            
            cursor.close()
            self.setup_status['cortex_functions_tested'] = True
            
        except Exception as e:
            logger.error(f"❌ Cortex function testing failed: {e}")
            # Don't raise here as Cortex functions might not be available in all regions
            logger.warning("⚠️ Continuing without Cortex functions...")
    
    def check_gong_data_share(self):
        """Check for Gong data share availability"""
        logger.info("🔍 Checking Gong data share availability...")
        
        try:
            cursor = self.connection.cursor()
            
            # List available shares
            cursor.execute("SHOW SHARES")
            shares = cursor.fetchall()
            
            gong_shares = [share for share in shares if 'GONG' in str(share).upper()]
            
            if gong_shares:
                logger.info(f"✅ Found {len(gong_shares)} Gong-related data shares")
                for share in gong_shares:
                    logger.info(f"   Share: {share}")
            else:
                logger.warning("⚠️ No Gong data shares found")
                logger.info("💡 To enable Gong data share, contact Gong support with account: UHDECNO-CVB64222")
            
            cursor.close()
            self.setup_status['gong_data_share_checked'] = True
            
        except Exception as e:
            logger.error(f"❌ Gong data share check failed: {e}")
            # Don't raise as this is informational
    
    def create_monitoring_tables(self):
        """Create monitoring and metrics tables"""
        logger.info("📊 Creating monitoring tables...")
        
        try:
            cursor = self.connection.cursor()
            cursor.execute("USE SCHEMA MONITORING")
            
            # Pipeline metrics table
            pipeline_metrics_sql = """
            CREATE TABLE IF NOT EXISTS PIPELINE_METRICS (
                METRIC_ID VARCHAR DEFAULT UUID_STRING() PRIMARY KEY,
                TIMESTAMP TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
                FLOW_NAME VARCHAR,
                STATUS VARCHAR,
                RECORDS_PROCESSED INTEGER,
                PROCESSING_TIME_SECONDS INTEGER,
                ERROR_COUNT INTEGER,
                ERROR_DETAILS VARIANT,
                METRICS VARIANT
            )
            """
            cursor.execute(pipeline_metrics_sql)
            
            # Data quality metrics
            data_quality_sql = """
            CREATE TABLE IF NOT EXISTS DATA_QUALITY_METRICS (
                QUALITY_ID VARCHAR DEFAULT UUID_STRING() PRIMARY KEY,
                TIMESTAMP TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
                TABLE_NAME VARCHAR,
                TOTAL_RECORDS INTEGER,
                NULL_RECORDS INTEGER,
                DUPLICATE_RECORDS INTEGER,
                QUALITY_SCORE FLOAT,
                QUALITY_ISSUES VARIANT
            )
            """
            cursor.execute(data_quality_sql)
            
            logger.info("✅ Monitoring tables created successfully")
            cursor.close()
            
        except Exception as e:
            logger.error(f"❌ Monitoring table creation failed: {e}")
            raise
    
    def run_complete_setup(self) -> bool:
        """Run the complete Snowflake alignment setup"""
        logger.info("🚀 Starting Snowflake alignment setup for Sophia AI...")
        
        try:
            # Step 1: Connect to Snowflake
            if not self.connect_to_snowflake():
                return False
            
            # Step 2: Set up warehouse
            self.setup_warehouse()
            
            # Step 3: Set up database and schemas
            self.setup_database_and_schemas()
            
            # Step 4: Create Estuary Flow tables
            self.create_estuary_flow_tables()
            
            # Step 5: Create analytics views
            self.create_analytics_views()
            
            # Step 6: Create monitoring tables
            self.create_monitoring_tables()
            
            # Step 7: Test Cortex functions
            self.test_cortex_functions()
            
            # Step 8: Check Gong data share
            self.check_gong_data_share()
            
            # Final status
            logger.info("✅ Snowflake alignment setup completed successfully!")
            logger.info("📊 Setup Status Summary:")
            for component, status in self.setup_status.items():
                status_icon = "✅" if status else "❌"
                logger.info(f"   {status_icon} {component.replace('_', ' ').title()}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Snowflake setup failed: {e}")
            return False
        
        finally:
            if self.connection:
                self.connection.close()
                logger.info("🔌 Snowflake connection closed")
    
    def get_connection_info(self) -> Dict:
        """Get connection information for other components"""
        return {
            'account': self.connection_params['account'],
            'user': self.connection_params['user'],
            'role': self.connection_params['role'],
            'warehouse': 'SOPHIA_AI_WH',
            'database': 'SOPHIA_AI_DB',
            'schemas': {
                'raw_data': 'RAW_DATA',
                'staging': 'STAGING',
                'analytics': 'ANALYTICS',
                'estuary_flow': 'ESTUARY_FLOW',
                'cortex_ai': 'CORTEX_AI',
                'vector_search': 'VECTOR_SEARCH',
                'monitoring': 'MONITORING'
            }
        }


def main():
    """Main execution function"""
    logger.info("🎯 Sophia AI Snowflake Alignment Setup")
    logger.info("=" * 50)
    
    setup = SnowflakeAlignmentSetup()
    success = setup.run_complete_setup()
    
    if success:
        logger.info("🎉 Snowflake alignment setup completed successfully!")
        
        # Save connection info for other components
        connection_info = setup.get_connection_info()
        with open('/home/ubuntu/sophia-project/snowflake_connection_info.json', 'w') as f:
            json.dump(connection_info, f, indent=2)
        
        logger.info("💾 Connection info saved to snowflake_connection_info.json")
        return 0
    else:
        logger.error("❌ Snowflake alignment setup failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())

