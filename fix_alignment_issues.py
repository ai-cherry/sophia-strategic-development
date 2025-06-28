#!/usr/bin/env python3
from backend.core.auto_esc_config import get_config_value
"""
Fix Alignment Issues Script
Fixes the SQL syntax and table creation issues found in the alignment analysis
"""

import snowflake.connector
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AlignmentIssuesFixer:
    """
    Fixes alignment issues between GitHub memory system and Snowflake implementation
    """
    
    def __init__(self):
        # Snowflake connection configuration
        self.snowflake_config = {
            'account': 'UHDECNO-CVB64222',
            'user': 'SCOOBYJAVA15',
            'password': get_config_value("snowflake_password"),
            'role': 'ACCOUNTADMIN'
        }
        
        # Estuary credentials
        self.estuary_credentials = {
            'client_id': '9630134c-359d-4c9c-aa97-95ab3a2ff8f5',
            'client_secret': 'NfwyhFUjemKlC66h7iECE9Tjedo6SGFh',
            'access_token': 'eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJ6Z1BPdmhDSC1Ic21OQnhhV3lnLU11dlF6dHJERTBDSEJHZDB2MVh0Vnk0In0.eyJleHAiOjE3NTAxNzA0MTcsImlhdCI6MTc1MDE2OTUxNywianRpIjoiYzAxMDRmODItOTQ3MC00NDJkLThiZDAtNDlmZDIzMDk5NTM0IiwiaXNzIjoiaHR0cHM6Ly9jbG91ZC5haXJieXRlLmNvbS9hdXRoL3JlYWxtcy9fYWlyYnl0ZS1hcHBsaWNhdGlvbi1jbGllbnRzIiwiYXVkIjoiYWNjb3VudCIsInN1YiI6IjkwNzJmYzI0LTE0MjUtNDBlNy05ZmU4LTg0ZWYxM2I2M2Q4MCIsInR5cCI6IkJlYXJlciIsImF6cCI6ImQ3OGNhZDM2LWU4MDAtNDhjOS04NTcxLTFkYWNiZDFiMjE3YyIsImFjciI6IjEiLCJyZWFsbV9hY2Nlc3MiOnsicm9sZXMiOlsib2ZmbGluZV9hY2Nlc3MiLCJ1bWFfYXV0aG9yaXphdGlvbiIsImRlZmF1bHQtcm9sZXMtX2FpcmJ5dGUtYXBwbGljYXRpb24tY2xpZW50cyJdfSwicmVzb3VyY2VfYWNjZXNzIjp7ImFjY291bnQiOnsicm9sZXMiOlsibWFuYWdlLWFjY291bnQiLCJtYW5hZ2UtYWNjb3VudC1saW5rcyIsInZpZXctcHJvZmlsZSJdfX0sInNjb3BlIjoib3BlbmlkIGVtYWlsIHByb2ZpbGUiLCJlbWFpbF92ZXJpZmllZCI6ZmFsc2UsImNsaWVudEhvc3QiOiIxNzIuMjMuMC4yNDMiLCJ1c2VyX2lkIjoiOTA3MmZjMjQtMTQyNS00MGU3LTlmZTgtODRlZjEzYjYzZDgwIiwicHJlZmVycmVkX3VzZXJuYW1lIjoic2VydmljZS1hY2NvdW50LWQ3OGNhZDM2LWU4MDAtNDhjOS04NTcxLTFkYWNiZDFiMjE3YyIsImNsaWVudEFkZHJlc3MiOiIxNzIuMjMuMC4yNDMiLCJjbGllbnRfaWQiOiJkNzhjYWQzNi1lODAwLTQ4YzktODU3MS0xZGFjYmQxYjIxN2MifQ.P8qAiLkkEO05MPEZJ1JfiE41aMQHxr7IoUxam-X66GtnSv_SvqUMgyxTg61Gmee6y7OU2EEcXaEmWzKPaqDFIXimXKrInn9DiOfMqB2gGfDiZmDmLT6rU9a5yHydflGNb8Z8V2hCvZDdpX48SmGtUUv-QEIytElP_LaYzaB20-fGXPwYCHzUEWZchC1N97xSWdYm-SneB_wNwNmAvoBZ3MYB9Il0LIwNAIJjihc6bnI9ka2Mlvxa1JbVp55vwmEDAOE86DAe6arJkOIz4xgjy6fvcSyqLQAPzcArdHHZJZe1WhJI2AZW64hzBXvUxuWooPH3eW-YGb6Vr2vSeOuHCQ',
            'client_id_new': 'd78cad36-e800-48c9-8571-1dacbd1b217c',
            'client_secret_new': 'VNZav8LJmsA3xKpoGMaZss3aDHuFS7da'
        }
        
        self.connection = None
        self.cursor = None
        
    def connect_snowflake(self) -> bool:
        """Establish connection to Snowflake"""
        try:
            logger.info("🔗 Connecting to Snowflake...")
            self.connection = snowflake.connector.connect(**self.snowflake_config)
            self.cursor = self.connection.cursor()
            
            # Test connection
            self.cursor.execute("SELECT CURRENT_VERSION()")
            version = self.cursor.fetchone()[0]
            logger.info(f"✅ Connected to Snowflake version: {version}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to Snowflake: {e}")
            return False
    
    def execute_sql(self, sql: str, params=None):
        """Execute SQL and return results"""
        try:
            if params:
                self.cursor.execute(sql, params)
            else:
                self.cursor.execute(sql)
            
            # Get column names
            columns = [desc[0] for desc in self.cursor.description] if self.cursor.description else []
            
            # Fetch results
            results = self.cursor.fetchall()
            
            # Convert to list of dictionaries
            return [dict(zip(columns, row)) for row in results]
            
        except Exception as e:
            logger.error(f"❌ SQL execution failed: {e}")
            logger.error(f"SQL: {sql}")
            return []
    
    def fix_memory_tables(self) -> bool:
        """Fix memory table creation issues"""
        logger.info("🔧 Fixing memory table creation...")
        
        try:
            # Ensure we're in the right context
            self.execute_sql("USE DATABASE SOPHIA_AI_CORE")
            self.execute_sql("CREATE SCHEMA IF NOT EXISTS AI_MEMORY")
            self.execute_sql("USE SCHEMA AI_MEMORY")
            
            # Drop existing tables if they exist (to recreate properly)
            self.execute_sql("DROP TABLE IF EXISTS MEMORY_RECORDS")
            self.execute_sql("DROP TABLE IF EXISTS CONVERSATION_HISTORY")
            self.execute_sql("DROP TABLE IF EXISTS MEMORY_CATEGORIES")
            
            # Create memory tables with proper Snowflake syntax
            memory_tables_sql = """
            CREATE TABLE MEMORY_RECORDS (
                MEMORY_ID VARCHAR(255) PRIMARY KEY,
                CONTENT VARCHAR(16777216) NOT NULL,
                CATEGORY VARCHAR(100) NOT NULL,
                TAGS ARRAY,
                EMBEDDING ARRAY,
                CREATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
                LAST_ACCESSED_AT TIMESTAMP_NTZ,
                IMPORTANCE_SCORE FLOAT DEFAULT 0.5,
                CONFIDENCE_SCORE FLOAT DEFAULT 1.0,
                USAGE_COUNT NUMBER DEFAULT 0,
                DEAL_ID VARCHAR(255),
                CALL_ID VARCHAR(255),
                CONTACT_ID VARCHAR(255),
                SOURCE_SYSTEM VARCHAR(100) DEFAULT 'sophia_ai',
                AUTO_DETECTED BOOLEAN DEFAULT FALSE,
                ADDITIONAL_METADATA VARIANT
            )
            """
            
            self.execute_sql(memory_tables_sql)
            logger.info("✅ Created MEMORY_RECORDS table")
            
            conversation_table_sql = """
            CREATE TABLE CONVERSATION_HISTORY (
                CONVERSATION_ID VARCHAR(255) PRIMARY KEY,
                SESSION_ID VARCHAR(255),
                USER_MESSAGE VARCHAR(16777216),
                AI_RESPONSE VARCHAR(16777216),
                CONVERSATION_SUMMARY VARCHAR(4000),
                CONVERSATION_TYPE VARCHAR(100),
                AGENT_TYPE VARCHAR(100),
                USER_ID VARCHAR(255),
                MEMORIES_RECALLED ARRAY,
                NEW_MEMORIES_CREATED ARRAY,
                MEMORY_EFFECTIVENESS_SCORE FLOAT,
                RESPONSE_TIME_MS NUMBER,
                TOKEN_COUNT NUMBER,
                COST_ESTIMATE FLOAT,
                USER_SATISFACTION_SCORE FLOAT,
                RELEVANCE_SCORE FLOAT,
                STARTED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
                COMPLETED_AT TIMESTAMP_NTZ,
                DURATION_SECONDS NUMBER,
                CONTEXT_METADATA VARIANT
            )
            """
            
            self.execute_sql(conversation_table_sql)
            logger.info("✅ Created CONVERSATION_HISTORY table")
            
            categories_table_sql = """
            CREATE TABLE MEMORY_CATEGORIES (
                CATEGORY_ID VARCHAR(100) PRIMARY KEY,
                CATEGORY_NAME VARCHAR(255) NOT NULL,
                CATEGORY_DESCRIPTION VARCHAR(1000),
                PARENT_CATEGORY_ID VARCHAR(100),
                DEFAULT_IMPORTANCE_SCORE FLOAT DEFAULT 0.5,
                AUTO_DETECTION_ENABLED BOOLEAN DEFAULT TRUE,
                RETENTION_DAYS NUMBER,
                PREFERRED_BUSINESS_TABLE VARCHAR(100),
                PREFERRED_EMBEDDING_COLUMN VARCHAR(100) DEFAULT 'ai_memory_embedding',
                CREATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
                UPDATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
                IS_ACTIVE BOOLEAN DEFAULT TRUE
            )
            """
            
            self.execute_sql(categories_table_sql)
            logger.info("✅ Created MEMORY_CATEGORIES table")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to fix memory tables: {e}")
            return False
    
    def fix_vector_tables(self) -> bool:
        """Fix vector table creation issues"""
        logger.info("🔧 Fixing vector table creation...")
        
        try:
            # Ensure we're in the right context
            self.execute_sql("USE DATABASE SOPHIA_VECTOR")
            self.execute_sql("CREATE SCHEMA IF NOT EXISTS MEMORY_VECTORS")
            self.execute_sql("USE SCHEMA MEMORY_VECTORS")
            
            # Drop existing table if it exists
            self.execute_sql("DROP TABLE IF EXISTS MEMORY_EMBEDDINGS")
            
            # Create vector table with proper Snowflake syntax
            vector_table_sql = """
            CREATE TABLE MEMORY_EMBEDDINGS (
                MEMORY_ID VARCHAR(255) PRIMARY KEY,
                CONTENT_EMBEDDING ARRAY,
                CATEGORY VARCHAR(100),
                TAGS ARRAY,
                IMPORTANCE_SCORE FLOAT,
                CREATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
                METADATA VARIANT
            )
            """
            
            self.execute_sql(vector_table_sql)
            logger.info("✅ Created MEMORY_EMBEDDINGS table")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to fix vector tables: {e}")
            return False
    
    def fix_estuary_credentials(self) -> bool:
        """Fix Estuary credential insertion with proper Snowflake syntax"""
        logger.info("🔧 Fixing Estuary credential insertion...")
        
        try:
            # Ensure we're in the right context
            self.execute_sql("USE DATABASE SOPHIA_AI_CORE")
            self.execute_sql("USE SCHEMA API_CREDENTIALS")
            
            # Check if credentials already exist and delete them
            self.execute_sql("DELETE FROM PLATFORM_CREDENTIALS WHERE PLATFORM_NAME = 'ESTUARY'")
            
            # Insert Estuary credentials using proper Snowflake syntax (no ON CONFLICT)
            credentials = [
                ('ESTUARY', 'CLIENT_ID', self.estuary_credentials['client_id'], 'Estuary Client ID for API access'),
                ('ESTUARY', 'CLIENT_SECRET', self.estuary_credentials['client_secret'], 'Estuary Client Secret for API access'),
                ('ESTUARY', 'ACCESS_TOKEN', self.estuary_credentials['access_token'], 'Estuary Access Token for API access'),
                ('ESTUARY', 'CLIENT_ID_NEW', self.estuary_credentials['client_id_new'], 'Estuary New Client ID for API access'),
                ('ESTUARY', 'CLIENT_SECRET_NEW', self.estuary_credentials['client_secret_new'], 'Estuary New Client Secret for API access')
            ]
            
            for platform, cred_type, cred_value, description in credentials:
                insert_sql = """
                INSERT INTO PLATFORM_CREDENTIALS (
                    PLATFORM_NAME,
                    CREDENTIAL_TYPE,
                    CREDENTIAL_VALUE,
                    IS_ACTIVE,
                    CREATED_AT,
                    METADATA
                ) VALUES (%s, %s, %s, TRUE, CURRENT_TIMESTAMP(), PARSE_JSON(%s))
                """
                
                metadata = f'{{"description": "{description}"}}'
                self.execute_sql(insert_sql, [platform, cred_type, cred_value, metadata])
            
            logger.info("✅ Fixed Estuary credentials insertion")
            
            # Fix API endpoints
            self.execute_sql("DELETE FROM API_ENDPOINTS WHERE PLATFORM_NAME = 'ESTUARY'")
            
            endpoints = [
                ('ESTUARY', 'LIST_WORKSPACES', 'https://api.estuary.dev/v1/workspaces', 'GET', 'List all workspaces'),
                ('ESTUARY', 'LIST_CONNECTIONS', 'https://api.estuary.dev/v1/connections', 'GET', 'List all connections'),
                ('ESTUARY', 'LIST_SOURCES', 'https://api.estuary.dev/v1/sources', 'GET', 'List all sources'),
                ('ESTUARY', 'LIST_DESTINATIONS', 'https://api.estuary.dev/v1/destinations', 'GET', 'List all destinations'),
                ('ESTUARY', 'TRIGGER_SYNC', 'https://api.estuary.dev/v1/jobs', 'POST', 'Trigger a sync job')
            ]
            
            for platform, endpoint_name, url, method, description in endpoints:
                insert_sql = """
                INSERT INTO API_ENDPOINTS (
                    PLATFORM_NAME,
                    ENDPOINT_NAME,
                    ENDPOINT_URL,
                    HTTP_METHOD,
                    DESCRIPTION,
                    IS_ACTIVE,
                    CREATED_AT
                ) VALUES (%s, %s, %s, %s, %s, TRUE, CURRENT_TIMESTAMP())
                """
                
                self.execute_sql(insert_sql, [platform, endpoint_name, url, method, description])
            
            logger.info("✅ Fixed Estuary Flow API endpoints")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to fix Estuary credentials: {e}")
            return False
    
    def validate_fixes(self) -> bool:
        """Validate that all fixes are working properly"""
        logger.info("🧪 Validating fixes...")
        
        try:
            # Test memory system
            self.execute_sql("USE DATABASE SOPHIA_AI_CORE")
            self.execute_sql("USE SCHEMA AI_MEMORY")
            
            # Insert test memory record
            test_memory_sql = """
            INSERT INTO MEMORY_RECORDS (
                MEMORY_ID, CONTENT, CATEGORY, TAGS, IMPORTANCE_SCORE, SOURCE_SYSTEM
            ) VALUES (
                %s,
                'This is a test memory for validation',
                'TEST',
                ARRAY_CONSTRUCT('test', 'validation'),
                0.8,
                'validation_system'
            )
            """
            
            test_id = f"test_memory_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self.execute_sql(test_memory_sql, [test_id])
            logger.info("✅ Successfully inserted test memory record")
            
            # Query test memory
            test_query = "SELECT COUNT(*) as count FROM MEMORY_RECORDS WHERE CATEGORY = 'TEST'"
            result = self.execute_sql(test_query)
            if result and result[0]['COUNT'] > 0:
                logger.info("✅ Memory system validation successful")
            
            # Test vector system
            self.execute_sql("USE DATABASE SOPHIA_VECTOR")
            self.execute_sql("USE SCHEMA MEMORY_VECTORS")
            
            # Insert test vector record
            test_vector_sql = """
            INSERT INTO MEMORY_EMBEDDINGS (
                MEMORY_ID, CONTENT_EMBEDDING, CATEGORY, IMPORTANCE_SCORE
            ) VALUES (
                %s,
                ARRAY_CONSTRUCT(0.1, 0.2, 0.3),
                'TEST',
                0.8
            )
            """
            
            self.execute_sql(test_vector_sql, [test_id])
            logger.info("✅ Successfully inserted test vector record")
            
            # Test API credentials
            self.execute_sql("USE DATABASE SOPHIA_AI_CORE")
            self.execute_sql("USE SCHEMA API_CREDENTIALS")
            
            credentials_test = "SELECT COUNT(*) as count FROM PLATFORM_CREDENTIALS WHERE PLATFORM_NAME = 'ESTUARY'"
            result = self.execute_sql(credentials_test)
            if result and result[0]['COUNT'] >= 5:
                logger.info("✅ Estuary credentials validation successful")
            
            endpoints_test = "SELECT COUNT(*) as count FROM API_ENDPOINTS WHERE PLATFORM_NAME = 'ESTUARY'"
            result = self.execute_sql(endpoints_test)
            if result and result[0]['COUNT'] >= 5:
                logger.info("✅ Estuary endpoints validation successful")
            
            logger.info("🎉 All fixes validated successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Validation failed: {e}")
            return False
    
    def run_fixes(self) -> bool:
        """Run all alignment fixes"""
        logger.info("🚀 Starting alignment fixes...")
        
        try:
            # 1. Connect to Snowflake
            if not self.connect_snowflake():
                return False
            
            # 2. Fix memory tables
            if not self.fix_memory_tables():
                return False
            
            # 3. Fix vector tables
            if not self.fix_vector_tables():
                return False
            
            # 4. Fix Estuary credentials
            if not self.fix_estuary_credentials():
                return False
            
            # 5. Validate fixes
            if not self.validate_fixes():
                return False
            
            logger.info("✅ All alignment fixes completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Alignment fixes failed: {e}")
            return False
        
        finally:
            if self.connection:
                self.connection.close()

def main():
    """Main execution function"""
    fixer = AlignmentIssuesFixer()
    
    success = fixer.run_fixes()
    
    if success:
        print("🎉 ALIGNMENT FIXES COMPLETED SUCCESSFULLY!")
        return 0
    else:
        print("❌ ALIGNMENT FIXES FAILED!")
        return 1

if __name__ == "__main__":
    exit(main())

