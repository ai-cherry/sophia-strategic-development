#!/usr/bin/env python3
"""
Snowflake Gong Setup Deployment Script

Executes Manus AI's finalized Snowflake DDL for Gong data pipeline including:
- RAW_AIRBYTE target tables with VARIANT columns
- STG_TRANSFORMED Gong tables with AI memory columns  
- PII policies and security
- Transformation/embedding stored procedures
- Automated scheduling tasks

Usage:
    python backend/scripts/deploy_gong_snowflake_setup.py --env dev
    python backend/scripts/deploy_gong_snowflake_setup.py --env dev --dry-run
    python backend/scripts/deploy_gong_snowflake_setup.py --env prod --execute-all
"""

import asyncio
import json
import logging
import sys
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import argparse

import snowflake.connector
from backend.core.auto_esc_config import get_config_value
from backend.utils.snowflake_cortex_service import SnowflakeCortexService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DeploymentEnvironment(Enum):
    """Deployment environments"""
    DEV = "dev"
    STAGING = "staging"
    PROD = "prod"


@dataclass
class SnowflakeDeploymentConfig:
    """Snowflake deployment configuration"""
    account: str
    user: str
    password: str
    warehouse: str
    database: str
    role: str
    
    # Environment-specific settings
    raw_schema: str = "RAW_AIRBYTE"
    stg_schema: str = "STG_TRANSFORMED"
    ops_schema: str = "OPS_MONITORING"
    ai_memory_schema: str = "AI_MEMORY"


class GongSnowflakeDeployer:
    """
    Deploys complete Gong data pipeline infrastructure to Snowflake
    
    Capabilities:
    - Execute Manus AI's finalized DDL for all schemas
    - Create RAW_AIRBYTE tables with proper VARIANT columns
    - Set up STG_TRANSFORMED tables with AI Memory integration
    - Configure PII policies and security
    - Deploy transformation and embedding procedures
    - Set up automated scheduling tasks
    - Idempotent deployment (safe to re-run)
    """

    def __init__(self, env: DeploymentEnvironment, dry_run: bool = False):
        self.env = env
        self.dry_run = dry_run
        self.connection: Optional[snowflake.connector.SnowflakeConnection] = None
        
        # Load environment-specific configuration
        self.config = self._load_config()
        
        # Track deployment progress
        self.deployment_log: List[Dict[str, Any]] = []

    def _load_config(self) -> SnowflakeDeploymentConfig:
        """Load configuration based on environment"""
        if self.env == DeploymentEnvironment.DEV:
            return SnowflakeDeploymentConfig(
                account=get_config_value("snowflake_account"),
                user=get_config_value("snowflake_user"),
                password=get_config_value("snowflake_password"),
                warehouse="WH_SOPHIA_ETL_TRANSFORM",
                database="SOPHIA_AI_DEV",
                role="ROLE_SOPHIA_AIRBYTE_INGEST"
            )
        elif self.env == DeploymentEnvironment.PROD:
            return SnowflakeDeploymentConfig(
                account=get_config_value("snowflake_account"),
                user=get_config_value("snowflake_user"),
                password=get_config_value("snowflake_password"),
                warehouse="WH_SOPHIA_PRODUCTION",
                database="SOPHIA_AI_PROD",
                role="ROLE_SOPHIA_PRODUCTION"
            )
        else:
            raise ValueError(f"Unsupported environment: {self.env}")

    async def deploy_complete_pipeline(self) -> Dict[str, Any]:
        """Deploy the complete Gong data pipeline to Snowflake"""
        try:
            logger.info(f"🚀 Starting Gong Snowflake deployment for {self.env.value.upper()} environment")
            
            if self.dry_run:
                logger.info("🔍 DRY RUN MODE - No changes will be made")
            
            # Initialize connection
            await self._initialize_connection()
            
            # Step 1: Create schemas and basic infrastructure
            await self._create_schemas()
            
            # Step 2: Create RAW_AIRBYTE tables for Airbyte ingestion
            await self._create_raw_airbyte_tables()
            
            # Step 3: Create STG_TRANSFORMED tables with AI Memory columns
            await self._create_stg_transformed_tables()
            
            # Step 4: Create AI_MEMORY tables and procedures
            await self._create_ai_memory_infrastructure()
            
            # Step 5: Create transformation stored procedures
            await self._create_transformation_procedures()
            
            # Step 6: Create AI embedding procedures
            await self._create_ai_embedding_procedures()
            
            # Step 7: Set up PII policies and security
            await self._create_pii_policies()
            
            # Step 8: Create automated tasks and scheduling
            await self._create_automated_tasks()
            
            # Step 9: Create monitoring and operational tables
            await self._create_ops_monitoring_tables()
            
            # Step 10: Grant necessary permissions
            await self._grant_permissions()
            
            deployment_summary = {
                "success": True,
                "environment": self.env.value,
                "dry_run": self.dry_run,
                "deployment_timestamp": datetime.utcnow().isoformat(),
                "steps_completed": len(self.deployment_log),
                "deployment_log": self.deployment_log,
                "next_steps": [
                    "Configure Airbyte Gong source connector",
                    "Test data ingestion to RAW_AIRBYTE tables",
                    "Verify transformation procedures execute correctly",
                    "Test AI Memory integration",
                    "Activate automated tasks"
                ]
            }
            
            logger.info("✅ Gong Snowflake deployment completed successfully")
            return deployment_summary
            
        except Exception as e:
            logger.error(f"❌ Deployment failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "environment": self.env.value,
                "deployment_log": self.deployment_log
            }
        finally:
            await self._cleanup()

    async def _initialize_connection(self) -> None:
        """Initialize Snowflake connection"""
        try:
            self.connection = snowflake.connector.connect(
                account=self.config.account,
                user=self.config.user,
                password=self.config.password,
                warehouse=self.config.warehouse,
                database=self.config.database,
                role=self.config.role
            )
            
            await self._log_step("connection", "Snowflake connection established", True)
            
        except Exception as e:
            await self._log_step("connection", f"Failed to connect: {e}", False)
            raise

    async def _create_schemas(self) -> None:
        """Create all required schemas"""
        schemas = [
            self.config.raw_schema,
            self.config.stg_schema,
            self.config.ops_schema,
            self.config.ai_memory_schema
        ]
        
        for schema in schemas:
            sql = f"""
            CREATE SCHEMA IF NOT EXISTS {self.config.database}.{schema}
            COMMENT = 'Schema for Gong data pipeline - Environment: {self.env.value}';
            """
            await self._execute_sql(f"create_schema_{schema}", sql)

    async def _create_raw_airbyte_tables(self) -> None:
        """Create RAW_AIRBYTE tables for Airbyte ingestion"""
        
        # RAW_GONG_CALLS_RAW table
        calls_sql = f"""
        CREATE TABLE IF NOT EXISTS {self.config.database}.{self.config.raw_schema}.RAW_GONG_CALLS_RAW (
            _AIRBYTE_AB_ID VARCHAR(64) PRIMARY KEY,
            _AIRBYTE_EMITTED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
            _AIRBYTE_NORMALIZED_AT TIMESTAMP_LTZ,
            _AIRBYTE_RAW_GONG_CALLS_HASHID VARCHAR(64),
            _AIRBYTE_DATA VARIANT NOT NULL,
            
            -- Extraction helper columns (for quick access)
            CALL_ID VARCHAR(255) AS (_AIRBYTE_DATA:id::VARCHAR),
            CALL_STARTED_AT TIMESTAMP_LTZ AS (_AIRBYTE_DATA:started::TIMESTAMP_LTZ),
            
            -- Processing tracking
            PROCESSED BOOLEAN DEFAULT FALSE,
            PROCESSED_AT TIMESTAMP_LTZ,
            PROCESSING_ERROR VARCHAR(16777216),
            
            -- Metadata
            INGESTED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
            CORRELATION_ID VARCHAR(255)
        )
        COMMENT = 'Raw Gong calls data from Airbyte ingestion';
        """
        await self._execute_sql("create_raw_calls", calls_sql)
        
        # RAW_GONG_TRANSCRIPTS_RAW table
        transcripts_sql = f"""
        CREATE TABLE IF NOT EXISTS {self.config.database}.{self.config.raw_schema}.RAW_GONG_TRANSCRIPTS_RAW (
            _AIRBYTE_AB_ID VARCHAR(64) PRIMARY KEY,
            _AIRBYTE_EMITTED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
            _AIRBYTE_NORMALIZED_AT TIMESTAMP_LTZ,
            _AIRBYTE_RAW_GONG_TRANSCRIPTS_HASHID VARCHAR(64),
            _AIRBYTE_DATA VARIANT NOT NULL,
            
            -- Extraction helper columns
            CALL_ID VARCHAR(255) AS (_AIRBYTE_DATA:callId::VARCHAR),
            
            -- Processing tracking
            PROCESSED BOOLEAN DEFAULT FALSE,
            PROCESSED_AT TIMESTAMP_LTZ,
            PROCESSING_ERROR VARCHAR(16777216),
            
            -- Metadata
            INGESTED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
            CORRELATION_ID VARCHAR(255)
        )
        COMMENT = 'Raw Gong call transcripts data from Airbyte ingestion';
        """
        await self._execute_sql("create_raw_transcripts", transcripts_sql)

    async def _create_stg_transformed_tables(self) -> None:
        """Create STG_TRANSFORMED tables with AI Memory columns"""
        
        # STG_GONG_CALLS table with AI Memory integration
        stg_calls_sql = f"""
        CREATE TABLE IF NOT EXISTS {self.config.database}.{self.config.stg_schema}.STG_GONG_CALLS (
            CALL_ID VARCHAR(255) PRIMARY KEY,
            CALL_TITLE VARCHAR(500),
            CALL_DATETIME_UTC TIMESTAMP_LTZ,
            CALL_DURATION_SECONDS NUMBER,
            CALL_DIRECTION VARCHAR(50),
            CALL_SYSTEM VARCHAR(100),
            CALL_SCOPE VARCHAR(100),
            CALL_MEDIA VARCHAR(50),
            CALL_LANGUAGE VARCHAR(10),
            CALL_URL VARCHAR(1000),
            
            -- Primary user/owner
            PRIMARY_USER_ID VARCHAR(255),
            PRIMARY_USER_EMAIL VARCHAR(255),
            PRIMARY_USER_NAME VARCHAR(255),
            
            -- CRM Integration fields
            HUBSPOT_DEAL_ID VARCHAR(255),
            HUBSPOT_CONTACT_ID VARCHAR(255),
            HUBSPOT_COMPANY_ID VARCHAR(255),
            CRM_OPPORTUNITY_ID VARCHAR(255),
            CRM_ACCOUNT_ID VARCHAR(255),
            
            -- Business context
            DEAL_STAGE VARCHAR(100),
            DEAL_VALUE NUMBER(15,2),
            ACCOUNT_NAME VARCHAR(500),
            CONTACT_NAME VARCHAR(500),
            
            -- Call quality metrics
            TALK_RATIO FLOAT,
            LONGEST_MONOLOGUE_SECONDS NUMBER,
            INTERACTIVITY_SCORE FLOAT,
            QUESTIONS_ASKED_COUNT NUMBER,
            
            -- AI-generated insights (Cortex)
            SENTIMENT_SCORE FLOAT,
            CALL_SUMMARY VARCHAR(16777216),
            KEY_TOPICS VARIANT,
            RISK_INDICATORS VARIANT,
            NEXT_STEPS VARIANT,
            
            -- AI Memory columns for semantic search and storage
            AI_MEMORY_EMBEDDING VECTOR(FLOAT, 768),
            AI_MEMORY_METADATA VARCHAR(16777216),
            AI_MEMORY_UPDATED_AT TIMESTAMP_NTZ,
            
            -- Metadata
            CREATED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
            UPDATED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
            PROCESSED_BY_CORTEX BOOLEAN DEFAULT FALSE,
            CORTEX_PROCESSED_AT TIMESTAMP_LTZ
        )
        COMMENT = 'Structured Gong calls with AI Memory integration';
        """
        await self._execute_sql("create_stg_calls", stg_calls_sql)
        
        # STG_GONG_CALL_TRANSCRIPTS table
        stg_transcripts_sql = f"""
        CREATE TABLE IF NOT EXISTS {self.config.database}.{self.config.stg_schema}.STG_GONG_CALL_TRANSCRIPTS (
            TRANSCRIPT_ID VARCHAR(255) PRIMARY KEY,
            CALL_ID VARCHAR(255) NOT NULL,
            SPEAKER_NAME VARCHAR(255),
            SPEAKER_EMAIL VARCHAR(255),
            SPEAKER_TYPE VARCHAR(50),
            TRANSCRIPT_TEXT VARCHAR(16777216),
            START_TIME_SECONDS NUMBER,
            END_TIME_SECONDS NUMBER,
            SEGMENT_DURATION_SECONDS NUMBER,
            WORD_COUNT NUMBER,
            
            -- AI processing results (Cortex)
            SEGMENT_SENTIMENT FLOAT,
            SEGMENT_SUMMARY VARCHAR(4000),
            EXTRACTED_ENTITIES VARIANT,
            KEY_PHRASES VARIANT,
            
            -- AI Memory columns for semantic search
            AI_MEMORY_EMBEDDING VECTOR(FLOAT, 768),
            AI_MEMORY_METADATA VARCHAR(16777216),
            AI_MEMORY_UPDATED_AT TIMESTAMP_NTZ,
            
            CREATED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
            PROCESSED_BY_CORTEX BOOLEAN DEFAULT FALSE,
            
            FOREIGN KEY (CALL_ID) REFERENCES {self.config.database}.{self.config.stg_schema}.STG_GONG_CALLS(CALL_ID)
        )
        COMMENT = 'Structured Gong call transcripts with AI Memory integration';
        """
        await self._execute_sql("create_stg_transcripts", stg_transcripts_sql)

    async def _create_ai_memory_infrastructure(self) -> None:
        """Create AI Memory infrastructure tables"""
        
        # AI_MEMORY.MEMORY_RECORDS table for cross-platform memory storage
        memory_records_sql = f"""
        CREATE TABLE IF NOT EXISTS {self.config.database}.{self.config.ai_memory_schema}.MEMORY_RECORDS (
            MEMORY_ID VARCHAR(255) PRIMARY KEY,
            CATEGORY VARCHAR(100) NOT NULL,
            CONTENT VARCHAR(16777216) NOT NULL,
            EMBEDDING VECTOR(FLOAT, 768),
            METADATA VARIANT,
            
            -- Source tracking
            SOURCE_TYPE VARCHAR(100),
            SOURCE_ID VARCHAR(255),
            SOURCE_TABLE VARCHAR(255),
            
            -- Memory management
            RELEVANCE_SCORE FLOAT DEFAULT 1.0,
            ACCESS_COUNT NUMBER DEFAULT 0,
            LAST_ACCESSED_AT TIMESTAMP_LTZ,
            
            -- Lifecycle
            CREATED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
            UPDATED_AT TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
            EXPIRES_AT TIMESTAMP_LTZ,
            IS_ACTIVE BOOLEAN DEFAULT TRUE
        )
        COMMENT = 'Central AI Memory storage for cross-platform semantic search';
        """
        await self._execute_sql("create_memory_records", memory_records_sql)

    async def _create_transformation_procedures(self) -> None:
        """Create stored procedures for data transformation"""
        
        # Transform raw Gong calls procedure
        transform_calls_proc = f"""
        CREATE OR REPLACE PROCEDURE {self.config.database}.{self.config.stg_schema}.TRANSFORM_RAW_GONG_CALLS()
        RETURNS STRING
        LANGUAGE SQL
        AS
        $$
        DECLARE
            processed_count NUMBER DEFAULT 0;
        BEGIN
            
            -- Transform raw calls to structured format
            MERGE INTO {self.config.database}.{self.config.stg_schema}.STG_GONG_CALLS AS target
            USING (
                SELECT 
                    _AIRBYTE_DATA:id::VARCHAR AS CALL_ID,
                    _AIRBYTE_DATA:title::VARCHAR AS CALL_TITLE,
                    _AIRBYTE_DATA:started::TIMESTAMP_LTZ AS CALL_DATETIME_UTC,
                    _AIRBYTE_DATA:duration::NUMBER AS CALL_DURATION_SECONDS,
                    _AIRBYTE_DATA:direction::VARCHAR AS CALL_DIRECTION,
                    _AIRBYTE_DATA:system::VARCHAR AS CALL_SYSTEM,
                    _AIRBYTE_DATA:scope::VARCHAR AS CALL_SCOPE,
                    _AIRBYTE_DATA:media::VARCHAR AS CALL_MEDIA,
                    _AIRBYTE_DATA:language::VARCHAR AS CALL_LANGUAGE,
                    _AIRBYTE_DATA:url::VARCHAR AS CALL_URL,
                    
                    -- Primary user extraction
                    _AIRBYTE_DATA:primaryUserId::VARCHAR AS PRIMARY_USER_ID,
                    _AIRBYTE_DATA:primaryUser.emailAddress::VARCHAR AS PRIMARY_USER_EMAIL,
                    _AIRBYTE_DATA:primaryUser.firstName::VARCHAR || ' ' || _AIRBYTE_DATA:primaryUser.lastName::VARCHAR AS PRIMARY_USER_NAME,
                    
                    -- CRM data extraction
                    _AIRBYTE_DATA:customData.hubspotDealId::VARCHAR AS HUBSPOT_DEAL_ID,
                    _AIRBYTE_DATA:customData.hubspotContactId::VARCHAR AS HUBSPOT_CONTACT_ID,
                    _AIRBYTE_DATA:customData.hubspotCompanyId::VARCHAR AS HUBSPOT_COMPANY_ID,
                    
                    -- Business context
                    _AIRBYTE_DATA:customData.dealStage::VARCHAR AS DEAL_STAGE,
                    _AIRBYTE_DATA:customData.dealValue::NUMBER AS DEAL_VALUE,
                    _AIRBYTE_DATA:customData.accountName::VARCHAR AS ACCOUNT_NAME,
                    _AIRBYTE_DATA:customData.contactName::VARCHAR AS CONTACT_NAME,
                    
                    -- Call metrics
                    _AIRBYTE_DATA:analytics.talkRatio::FLOAT AS TALK_RATIO,
                    _AIRBYTE_DATA:analytics.longestMonologue::NUMBER AS LONGEST_MONOLOGUE_SECONDS,
                    _AIRBYTE_DATA:analytics.interactivity::FLOAT AS INTERACTIVITY_SCORE,
                    _AIRBYTE_DATA:analytics.questionsAsked::NUMBER AS QUESTIONS_ASKED_COUNT,
                    
                    CURRENT_TIMESTAMP() AS UPDATED_AT
                    
                FROM {self.config.database}.{self.config.raw_schema}.RAW_GONG_CALLS_RAW 
                WHERE PROCESSED = FALSE
            ) AS source
            ON target.CALL_ID = source.CALL_ID
            WHEN MATCHED THEN UPDATE SET
                CALL_TITLE = source.CALL_TITLE,
                CALL_DATETIME_UTC = source.CALL_DATETIME_UTC,
                CALL_DURATION_SECONDS = source.CALL_DURATION_SECONDS,
                HUBSPOT_DEAL_ID = source.HUBSPOT_DEAL_ID,
                DEAL_STAGE = source.DEAL_STAGE,
                DEAL_VALUE = source.DEAL_VALUE,
                TALK_RATIO = source.TALK_RATIO,
                UPDATED_AT = source.UPDATED_AT
            WHEN NOT MATCHED THEN INSERT (
                CALL_ID, CALL_TITLE, CALL_DATETIME_UTC, CALL_DURATION_SECONDS,
                CALL_DIRECTION, CALL_SYSTEM, CALL_SCOPE, CALL_MEDIA, CALL_LANGUAGE, CALL_URL,
                PRIMARY_USER_ID, PRIMARY_USER_EMAIL, PRIMARY_USER_NAME,
                HUBSPOT_DEAL_ID, HUBSPOT_CONTACT_ID, HUBSPOT_COMPANY_ID,
                DEAL_STAGE, DEAL_VALUE, ACCOUNT_NAME, CONTACT_NAME,
                TALK_RATIO, LONGEST_MONOLOGUE_SECONDS, INTERACTIVITY_SCORE, QUESTIONS_ASKED_COUNT,
                UPDATED_AT
            ) VALUES (
                source.CALL_ID, source.CALL_TITLE, source.CALL_DATETIME_UTC, source.CALL_DURATION_SECONDS,
                source.CALL_DIRECTION, source.CALL_SYSTEM, source.CALL_SCOPE, source.CALL_MEDIA, source.CALL_LANGUAGE, source.CALL_URL,
                source.PRIMARY_USER_ID, source.PRIMARY_USER_EMAIL, source.PRIMARY_USER_NAME,
                source.HUBSPOT_DEAL_ID, source.HUBSPOT_CONTACT_ID, source.HUBSPOT_COMPANY_ID,
                source.DEAL_STAGE, source.DEAL_VALUE, source.ACCOUNT_NAME, source.CONTACT_NAME,
                source.TALK_RATIO, source.LONGEST_MONOLOGUE_SECONDS, source.INTERACTIVITY_SCORE, source.QUESTIONS_ASKED_COUNT,
                source.UPDATED_AT
            );
            
            GET DIAGNOSTICS processed_count = ROW_COUNT;
            
            -- Mark raw records as processed
            UPDATE {self.config.database}.{self.config.raw_schema}.RAW_GONG_CALLS_RAW 
            SET PROCESSED = TRUE, PROCESSED_AT = CURRENT_TIMESTAMP()
            WHERE PROCESSED = FALSE;
            
            RETURN 'Processed ' || processed_count || ' Gong call records';
            
        EXCEPTION
            WHEN OTHER THEN
                RETURN 'Error processing Gong calls: ' || SQLERRM;
        END;
        $$;
        """
        await self._execute_sql("create_transform_calls_proc", transform_calls_proc)

    async def execute_manus_ai_ddl(self, ddl_file_path: str) -> Dict[str, Any]:
        """Execute Manus AI's consolidated DDL script"""
        try:
            logger.info(f"📜 Executing Manus AI DDL from: {ddl_file_path}")
            
            with open(ddl_file_path, 'r') as f:
                ddl_content = f.read()
            
            # Split DDL into individual statements
            statements = [stmt.strip() for stmt in ddl_content.split(';') if stmt.strip()]
            
            executed_count = 0
            for i, statement in enumerate(statements):
                if statement:
                    await self._execute_sql(f"manus_ddl_statement_{i+1}", statement + ';')
                    executed_count += 1
            
            result = {
                "success": True,
                "statements_executed": executed_count,
                "ddl_file": ddl_file_path
            }
            
            await self._log_step("manus_ddl_execution", f"Executed {executed_count} DDL statements", True)
            return result
            
        except Exception as e:
            await self._log_step("manus_ddl_execution", f"DDL execution failed: {e}", False)
            return {
                "success": False,
                "error": str(e),
                "ddl_file": ddl_file_path
            }

    async def _create_ai_embedding_procedures(self) -> None:
        """Create procedures for AI embedding generation"""
        
        # Generate AI embeddings procedure using Snowflake Cortex
        embedding_proc = f"""
        CREATE OR REPLACE PROCEDURE {self.config.database}.{self.config.stg_schema}.GENERATE_AI_EMBEDDINGS()
        RETURNS STRING
        LANGUAGE SQL
        AS
        $$
        DECLARE
            processed_count NUMBER DEFAULT 0;
        BEGIN
            
            -- Generate embeddings for calls without embeddings
            UPDATE {self.config.database}.{self.config.stg_schema}.STG_GONG_CALLS
            SET 
                AI_MEMORY_EMBEDDING = SNOWFLAKE.CORTEX.EMBED_TEXT('e5-base-v2', 
                    COALESCE(CALL_SUMMARY, CALL_TITLE || ' - ' || COALESCE(ACCOUNT_NAME, 'Unknown Account'))
                ),
                AI_MEMORY_METADATA = OBJECT_CONSTRUCT(
                    'call_id', CALL_ID,
                    'account_name', ACCOUNT_NAME,
                    'deal_stage', DEAL_STAGE,
                    'sentiment_score', SENTIMENT_SCORE,
                    'talk_ratio', TALK_RATIO,
                    'call_datetime', CALL_DATETIME_UTC,
                    'primary_user', PRIMARY_USER_EMAIL,
                    'embedding_generated_at', CURRENT_TIMESTAMP()
                ),
                AI_MEMORY_UPDATED_AT = CURRENT_TIMESTAMP()
            WHERE AI_MEMORY_EMBEDDING IS NULL
            AND CALL_SUMMARY IS NOT NULL;
            
            GET DIAGNOSTICS processed_count = ROW_COUNT;
            
            -- Also populate AI_MEMORY.MEMORY_RECORDS for cross-platform access
            INSERT INTO {self.config.database}.{self.config.ai_memory_schema}.MEMORY_RECORDS (
                MEMORY_ID,
                CATEGORY,
                CONTENT,
                EMBEDDING,
                METADATA,
                SOURCE_TYPE,
                SOURCE_ID,
                SOURCE_TABLE
            )
            SELECT 
                'gong_call_' || CALL_ID AS MEMORY_ID,
                'gong_call_summary' AS CATEGORY,
                CALL_SUMMARY AS CONTENT,
                AI_MEMORY_EMBEDDING AS EMBEDDING,
                AI_MEMORY_METADATA AS METADATA,
                'gong' AS SOURCE_TYPE,
                CALL_ID AS SOURCE_ID,
                'STG_GONG_CALLS' AS SOURCE_TABLE
            FROM {self.config.database}.{self.config.stg_schema}.STG_GONG_CALLS
            WHERE AI_MEMORY_EMBEDDING IS NOT NULL
            AND CALL_ID NOT IN (
                SELECT SOURCE_ID 
                FROM {self.config.database}.{self.config.ai_memory_schema}.MEMORY_RECORDS 
                WHERE SOURCE_TYPE = 'gong' AND CATEGORY = 'gong_call_summary'
            );
            
            RETURN 'Generated embeddings for ' || processed_count || ' Gong calls';
            
        EXCEPTION
            WHEN OTHER THEN
                RETURN 'Error generating embeddings: ' || SQLERRM;
        END;
        $$;
        """
        await self._execute_sql("create_embedding_proc", embedding_proc)

    async def _create_pii_policies(self) -> None:
        """Create PII masking policies"""
        
        # Email masking policy
        email_policy = f"""
        CREATE OR REPLACE MASKING POLICY {self.config.database}.{self.config.stg_schema}.MASK_EMAIL AS (val STRING) 
        RETURNS STRING ->
        CASE 
            WHEN CURRENT_ROLE() IN ('ROLE_SOPHIA_ADMIN', 'ROLE_SOPHIA_DEVELOPER') THEN val
            WHEN CURRENT_ROLE() IN ('ROLE_SOPHIA_ANALYST') THEN REGEXP_REPLACE(val, '(.{{1,3}}).*(@.*)', '\\1***\\2')
            ELSE '***@***.com'
        END;
        """
        await self._execute_sql("create_email_policy", email_policy)
        
        # Apply email policy to relevant columns
        apply_email_policy = f"""
        ALTER TABLE {self.config.database}.{self.config.stg_schema}.STG_GONG_CALLS 
        MODIFY COLUMN PRIMARY_USER_EMAIL SET MASKING POLICY {self.config.database}.{self.config.stg_schema}.MASK_EMAIL;
        """
        await self._execute_sql("apply_email_policy", apply_email_policy)

    async def _create_automated_tasks(self) -> None:
        """Create automated Snowflake tasks for data processing"""
        
        # Task to transform raw calls every 15 minutes
        transform_task = f"""
        CREATE OR REPLACE TASK {self.config.database}.{self.config.stg_schema}.TASK_TRANSFORM_GONG_CALLS
            WAREHOUSE = {self.config.warehouse}
            SCHEDULE = 'USING CRON 0,15,30,45 * * * * UTC'
            COMMENT = 'Transform raw Gong calls from Airbyte to structured format'
        AS
            CALL {self.config.database}.{self.config.stg_schema}.TRANSFORM_RAW_GONG_CALLS();
        """
        await self._execute_sql("create_transform_task", transform_task)
        
        # Task to generate AI embeddings every 30 minutes
        embedding_task = f"""
        CREATE OR REPLACE TASK {self.config.database}.{self.config.stg_schema}.TASK_GENERATE_AI_EMBEDDINGS
            WAREHOUSE = {self.config.warehouse}
            SCHEDULE = 'USING CRON 0,30 * * * * UTC'
            COMMENT = 'Generate AI embeddings for new Gong data'
        AS
            CALL {self.config.database}.{self.config.stg_schema}.GENERATE_AI_EMBEDDINGS();
        """
        await self._execute_sql("create_embedding_task", embedding_task)

    async def _create_ops_monitoring_tables(self) -> None:
        """Create operational monitoring tables"""
        
        # ETL job logs table
        etl_logs_sql = f"""
        CREATE TABLE IF NOT EXISTS {self.config.database}.{self.config.ops_schema}.ETL_JOB_LOGS (
            LOG_ID NUMBER IDENTITY PRIMARY KEY,
            JOB_ID VARCHAR(255),
            JOB_TYPE VARCHAR(100),
            STATUS VARCHAR(50),
            RECORDS_PROCESSED NUMBER,
            SUCCESS_RATE FLOAT,
            HEALTH_STATUS VARCHAR(50),
            CONNECTION_ID VARCHAR(255),
            SOURCE_TYPE VARCHAR(100),
            DESTINATION_TYPE VARCHAR(100),
            ERROR_MESSAGE VARCHAR(16777216),
            METADATA VARIANT,
            LOG_TIMESTAMP TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP()
        )
        COMMENT = 'Operational logs for ETL jobs and data pipeline monitoring';
        """
        await self._execute_sql("create_etl_logs", etl_logs_sql)

    async def _grant_permissions(self) -> None:
        """Grant necessary permissions for different roles"""
        
        # Grant permissions to Airbyte ingestion role
        airbyte_grants = f"""
        GRANT USAGE ON WAREHOUSE {self.config.warehouse} TO ROLE ROLE_SOPHIA_AIRBYTE_INGEST;
        GRANT USAGE ON DATABASE {self.config.database} TO ROLE ROLE_SOPHIA_AIRBYTE_INGEST;
        GRANT USAGE ON SCHEMA {self.config.database}.{self.config.raw_schema} TO ROLE ROLE_SOPHIA_AIRBYTE_INGEST;
        GRANT INSERT, SELECT, UPDATE ON ALL TABLES IN SCHEMA {self.config.database}.{self.config.raw_schema} TO ROLE ROLE_SOPHIA_AIRBYTE_INGEST;
        """
        await self._execute_sql("grant_airbyte_permissions", airbyte_grants)

    async def _execute_sql(self, step_name: str, sql: str) -> None:
        """Execute SQL statement with logging and error handling"""
        try:
            if self.dry_run:
                logger.info(f"[DRY RUN] {step_name}: {sql[:100]}...")
                await self._log_step(step_name, "SQL execution (dry run)", True)
                return
            
            cursor = self.connection.cursor()
            cursor.execute(sql)
            cursor.close()
            
            await self._log_step(step_name, "SQL executed successfully", True)
            
        except Exception as e:
            await self._log_step(step_name, f"SQL execution failed: {e}", False)
            raise

    async def _log_step(self, step: str, message: str, success: bool) -> None:
        """Log deployment step"""
        log_entry = {
            "step": step,
            "message": message,
            "success": success,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.deployment_log.append(log_entry)
        
        status = "✅" if success else "❌"
        logger.info(f"{status} {step}: {message}")

    async def _cleanup(self) -> None:
        """Clean up resources"""
        if self.connection:
            self.connection.close()


async def main():
    """Main function for CLI usage"""
    parser = argparse.ArgumentParser(description="Deploy Gong Snowflake Infrastructure")
    parser.add_argument("--env", choices=["dev", "staging", "prod"], 
                       default="dev", help="Deployment environment")
    parser.add_argument("--dry-run", action="store_true", 
                       help="Perform dry run without executing changes")
    parser.add_argument("--execute-all", action="store_true",
                       help="Execute all deployment steps without prompts")
    
    args = parser.parse_args()
    
    env = DeploymentEnvironment(args.env)
    deployer = GongSnowflakeDeployer(env, args.dry_run)
    
    try:
        result = await deployer.deploy_complete_pipeline()
        print(json.dumps(result, indent=2))
        
        if result["success"]:
            sys.exit(0)
        else:
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Deployment failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
