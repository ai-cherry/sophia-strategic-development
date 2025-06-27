#!/usr/bin/env python3
"""
NetSuite Estuary Integration Setup
Configures Estuary source for NetSuite and creates transformation procedures for NETSUITE_DATA schema
"""

import asyncio
import logging
from typing import Dict, Any
from dataclasses import dataclass

from backend.core.auto_esc_config import get_config_value
from backend.etl.estuary.estuary_configuration_manager import EstuaryConfigurationManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class NetSuiteSourceConfig:
    """NetSuite source configuration for Estuary"""
    realm: str
    consumer_key: str
    consumer_secret: str
    token_id: str
    token_secret: str
    start_date: str = "2024-01-01T00:00:00Z"

class EstuaryNetSuiteOrchestrator:
    """Orchestrates NetSuite data ingestion via Estuary"""
    
    def __init__(self):
        self.config_manager = EstuaryConfigurationManager()
        self.netsuite_config = None
        
    async def initialize(self) -> None:
        """Initialize NetSuite Estuary orchestrator"""
        try:
            await self.config_manager.initialize()
            
            # Get NetSuite configuration from Pulumi ESC
            self.netsuite_config = NetSuiteSourceConfig(
                realm=await get_config_value("netsuite_realm"),
                consumer_key=await get_config_value("netsuite_consumer_key"),
                consumer_secret=await get_config_value("netsuite_consumer_secret"),
                token_id=await get_config_value("netsuite_token_id"),
                token_secret=await get_config_value("netsuite_token_secret")
            )
            
            logger.info("✅ NetSuite Estuary orchestrator initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize NetSuite orchestrator: {e}")
            raise

    async def _create_netsuite_source(self) -> Dict[str, Any]:
        """Create NetSuite source configuration"""
        try:
            source_config = {
                "sourceDefinitionId": "4eb22946-2a79-4d20-a3c9-8466b70b7b9e",  # NetSuite source ID
                "connectionConfiguration": {
                    "realm": self.netsuite_config.realm,
                    "consumer_key": self.netsuite_config.consumer_key,
                    "consumer_secret": self.netsuite_config.consumer_secret,
                    "token_id": self.netsuite_config.token_id,
                    "token_secret": self.netsuite_config.token_secret,
                    "start_date": self.netsuite_config.start_date,
                    "window_in_days": 30
                },
                "name": "NetSuite-PayReady-Source"
            }
            
            source_response = await self.config_manager.create_source(source_config)
            logger.info(f"✅ Created NetSuite source: {source_response['sourceId']}")
            return source_response
            
        except Exception as e:
            logger.error(f"❌ Failed to create NetSuite source: {e}")
            raise

    async def _create_snowflake_destination(self) -> Dict[str, Any]:
        """Create or get Snowflake destination for NetSuite data"""
        try:
            # Use existing Snowflake destination or create new one
            destination_config = {
                "destinationDefinitionId": "424892c4-daac-4491-b35d-c6688ba547ba",  # Snowflake destination ID
                "connectionConfiguration": {
                    "host": await get_config_value("snowflake_account") + ".snowflakecomputing.com",
                    "role": "ACCOUNTADMIN",
                    "warehouse": "WH_SOPHIA_AI_PROCESSING",
                    "database": "SOPHIA_AI_DEV",
                    "schema": "RAW_ESTUARY",
                    "username": await get_config_value("snowflake_user"),
                    "password": await get_config_value("snowflake_password"),
                    "jdbc_url_params": "",
                    "raw_data_schema": "RAW_ESTUARY",
                    "loading_method": {
                        "method": "Standard"
                    }
                },
                "name": "Snowflake-NetSuite-Destination"
            }
            
            destination_response = await self.config_manager.create_destination(destination_config)
            logger.info(f"✅ Created Snowflake destination for NetSuite: {destination_response['destinationId']}")
            return destination_response
            
        except Exception as e:
            logger.error(f"❌ Failed to create Snowflake destination: {e}")
            raise

    async def _create_netsuite_connection(self, source_id: str, destination_id: str) -> Dict[str, Any]:
        """Create connection between NetSuite source and Snowflake destination"""
        try:
            # Define NetSuite streams to sync
            streams_config = [
                {
                    "stream": {
                        "name": "accounts",
                        "json_schema": {},
                        "supported_sync_modes": ["full_refresh", "incremental"]
                    },
                    "config": {
                        "sync_mode": "incremental",
                        "destination_sync_mode": "append_dedup",
                        "cursor_field": ["lastModifiedDate"],
                        "primary_key": [["internalId"]]
                    }
                },
                {
                    "stream": {
                        "name": "transactions",
                        "json_schema": {},
                        "supported_sync_modes": ["full_refresh", "incremental"]
                    },
                    "config": {
                        "sync_mode": "incremental",
                        "destination_sync_mode": "append_dedup",
                        "cursor_field": ["lastModifiedDate"],
                        "primary_key": [["internalId"]]
                    }
                },
                {
                    "stream": {
                        "name": "purchase_orders",
                        "json_schema": {},
                        "supported_sync_modes": ["full_refresh", "incremental"]
                    },
                    "config": {
                        "sync_mode": "incremental",
                        "destination_sync_mode": "append_dedup",
                        "cursor_field": ["lastModifiedDate"],
                        "primary_key": [["internalId"]]
                    }
                },
                {
                    "stream": {
                        "name": "expense_reports",
                        "json_schema": {},
                        "supported_sync_modes": ["full_refresh", "incremental"]
                    },
                    "config": {
                        "sync_mode": "incremental",
                        "destination_sync_mode": "append_dedup",
                        "cursor_field": ["lastModifiedDate"],
                        "primary_key": [["internalId"]]
                    }
                },
                {
                    "stream": {
                        "name": "vendors",
                        "json_schema": {},
                        "supported_sync_modes": ["full_refresh", "incremental"]
                    },
                    "config": {
                        "sync_mode": "incremental",
                        "destination_sync_mode": "append_dedup",
                        "cursor_field": ["lastModifiedDate"],
                        "primary_key": [["internalId"]]
                    }
                }
            ]
            
            connection_config = {
                "sourceId": source_id,
                "destinationId": destination_id,
                "syncCatalog": {
                    "streams": streams_config
                },
                "schedule": {
                    "scheduleType": "cron",
                    "cronExpression": "0 */6 * * *"  # Every 6 hours
                },
                "name": "NetSuite-to-Snowflake-Connection",
                "namespaceDefinition": "source",
                "namespaceFormat": "${SOURCE_NAMESPACE}",
                "prefix": "netsuite_"
            }
            
            connection_response = await self.config_manager.create_connection(connection_config)
            logger.info(f"✅ Created NetSuite connection: {connection_response['connectionId']}")
            return connection_response
            
        except Exception as e:
            logger.error(f"❌ Failed to create NetSuite connection: {e}")
            raise

    async def create_transformation_procedures(self) -> None:
        """Create Snowflake stored procedures for NetSuite data transformation"""
        try:
            snowflake_conn = await self.config_manager._get_snowflake_connection()
            cursor = snowflake_conn.cursor()
            
            # Procedure to transform NetSuite accounts to general ledger
            cursor.execute("""
                CREATE OR REPLACE PROCEDURE TRANSFORM_NETSUITE_ACCOUNTS()
                RETURNS STRING
                LANGUAGE SQL
                AS
                $$
                DECLARE
                    processed_count NUMBER DEFAULT 0;
                BEGIN
                    
                    -- Transform raw NetSuite accounts to GENERAL_LEDGER
                    INSERT INTO NETSUITE_DATA.GENERAL_LEDGER (
                        ENTRY_ID,
                        ACCOUNT_ID,
                        ACCOUNT_NAME,
                        ACCOUNT_TYPE,
                        DEBIT_AMOUNT,
                        CREDIT_AMOUNT,
                        NET_AMOUNT,
                        TRANSACTION_DATE,
                        POSTING_DATE,
                        TRANSACTION_TYPE,
                        REFERENCE_NUMBER,
                        DESCRIPTION,
                        MEMO,
                        DEPARTMENT,
                        CLASS,
                        LOCATION,
                        IS_RECONCILED,
                        NETSUITE_CREATED_DATE,
                        NETSUITE_MODIFIED_DATE,
                        AI_MEMORY_METADATA
                    )
                    SELECT 
                        _ESTUARY_DATA:internalId::VARCHAR AS ENTRY_ID,
                        _ESTUARY_DATA:accountNumber::VARCHAR AS ACCOUNT_ID,
                        _ESTUARY_DATA:acctName::VARCHAR AS ACCOUNT_NAME,
                        _ESTUARY_DATA:acctType:value::VARCHAR AS ACCOUNT_TYPE,
                        CASE WHEN _ESTUARY_DATA:balance::FLOAT > 0 THEN _ESTUARY_DATA:balance::FLOAT ELSE 0 END AS DEBIT_AMOUNT,
                        CASE WHEN _ESTUARY_DATA:balance::FLOAT < 0 THEN ABS(_ESTUARY_DATA:balance::FLOAT) ELSE 0 END AS CREDIT_AMOUNT,
                        _ESTUARY_DATA:balance::FLOAT AS NET_AMOUNT,
                        _ESTUARY_DATA:lastModifiedDate::TIMESTAMP_LTZ AS TRANSACTION_DATE,
                        _ESTUARY_DATA:lastModifiedDate::TIMESTAMP_LTZ AS POSTING_DATE,
                        'BALANCE_ENTRY' AS TRANSACTION_TYPE,
                        _ESTUARY_DATA:internalId::VARCHAR AS REFERENCE_NUMBER,
                        _ESTUARY_DATA:description::VARCHAR AS DESCRIPTION,
                        _ESTUARY_DATA:memo::VARCHAR AS MEMO,
                        _ESTUARY_DATA:department:name::VARCHAR AS DEPARTMENT,
                        _ESTUARY_DATA:class:name::VARCHAR AS CLASS,
                        _ESTUARY_DATA:location:name::VARCHAR AS LOCATION,
                        FALSE AS IS_RECONCILED,
                        _ESTUARY_DATA:dateCreated::TIMESTAMP_LTZ AS NETSUITE_CREATED_DATE,
                        _ESTUARY_DATA:lastModifiedDate::TIMESTAMP_LTZ AS NETSUITE_MODIFIED_DATE,
                        OBJECT_CONSTRUCT(
                            'source_table', 'RAW_NETSUITE_ACCOUNTS',
                            'transformation_date', CURRENT_TIMESTAMP()::STRING,
                            'netsuite_internal_id', _ESTUARY_DATA:internalId::VARCHAR
                        ) AS AI_MEMORY_METADATA
                    FROM RAW_ESTUARY._ESTUARY_RAW_NETSUITE_ACCOUNTS
                    WHERE _ESTUARY_DATA:internalId IS NOT NULL
                    AND NOT EXISTS (
                        SELECT 1 FROM NETSUITE_DATA.GENERAL_LEDGER 
                        WHERE ENTRY_ID = _ESTUARY_DATA:internalId::VARCHAR
                    );
                    
                    GET DIAGNOSTICS processed_count = ROW_COUNT;
                    
                    RETURN 'Processed ' || processed_count || ' NetSuite accounts to general ledger';
                    
                EXCEPTION
                    WHEN OTHER THEN
                        RETURN 'Error transforming NetSuite accounts: ' || SQLERRM;
                END;
                $$;
            """)
            
            # Procedure to transform NetSuite purchase orders
            cursor.execute("""
                CREATE OR REPLACE PROCEDURE TRANSFORM_NETSUITE_PURCHASE_ORDERS()
                RETURNS STRING
                LANGUAGE SQL
                AS
                $$
                DECLARE
                    processed_count NUMBER DEFAULT 0;
                BEGIN
                    
                    -- Transform raw NetSuite purchase orders
                    INSERT INTO NETSUITE_DATA.PURCHASE_ORDERS (
                        PO_ID,
                        PO_NUMBER,
                        VENDOR_ID,
                        VENDOR_NAME,
                        ORDER_DATE,
                        EXPECTED_DELIVERY_DATE,
                        STATUS,
                        SUBTOTAL_AMOUNT,
                        TAX_AMOUNT,
                        TOTAL_AMOUNT,
                        CURRENCY,
                        REQUESTED_BY,
                        APPROVED_BY,
                        APPROVAL_STATUS,
                        DEPARTMENT,
                        AI_MEMORY_METADATA
                    )
                    SELECT 
                        _ESTUARY_DATA:internalId::VARCHAR AS PO_ID,
                        _ESTUARY_DATA:tranId::VARCHAR AS PO_NUMBER,
                        _ESTUARY_DATA:entity:internalId::VARCHAR AS VENDOR_ID,
                        _ESTUARY_DATA:entity:entityId::VARCHAR AS VENDOR_NAME,
                        _ESTUARY_DATA:tranDate::DATE AS ORDER_DATE,
                        _ESTUARY_DATA:dueDate::DATE AS EXPECTED_DELIVERY_DATE,
                        _ESTUARY_DATA:status:name::VARCHAR AS STATUS,
                        _ESTUARY_DATA:subTotal::FLOAT AS SUBTOTAL_AMOUNT,
                        _ESTUARY_DATA:taxTotal::FLOAT AS TAX_AMOUNT,
                        _ESTUARY_DATA:total::FLOAT AS TOTAL_AMOUNT,
                        _ESTUARY_DATA:currency:name::VARCHAR AS CURRENCY,
                        _ESTUARY_DATA:createdBy:name::VARCHAR AS REQUESTED_BY,
                        _ESTUARY_DATA:approvedBy:name::VARCHAR AS APPROVED_BY,
                        CASE 
                            WHEN _ESTUARY_DATA:approvedBy IS NOT NULL THEN 'APPROVED'
                            ELSE 'PENDING'
                        END AS APPROVAL_STATUS,
                        _ESTUARY_DATA:department:name::VARCHAR AS DEPARTMENT,
                        OBJECT_CONSTRUCT(
                            'source_table', 'RAW_NETSUITE_PURCHASE_ORDERS',
                            'transformation_date', CURRENT_TIMESTAMP()::STRING,
                            'netsuite_internal_id', _ESTUARY_DATA:internalId::VARCHAR,
                            'original_status', _ESTUARY_DATA:status:name::VARCHAR
                        ) AS AI_MEMORY_METADATA
                    FROM RAW_ESTUARY._ESTUARY_RAW_NETSUITE_PURCHASE_ORDERS
                    WHERE _ESTUARY_DATA:internalId IS NOT NULL
                    AND NOT EXISTS (
                        SELECT 1 FROM NETSUITE_DATA.PURCHASE_ORDERS 
                        WHERE PO_ID = _ESTUARY_DATA:internalId::VARCHAR
                    );
                    
                    GET DIAGNOSTICS processed_count = ROW_COUNT;
                    
                    RETURN 'Processed ' || processed_count || ' NetSuite purchase orders';
                    
                EXCEPTION
                    WHEN OTHER THEN
                        RETURN 'Error transforming NetSuite purchase orders: ' || SQLERRM;
                END;
                $$;
            """)
            
            # Procedure to transform NetSuite expense reports
            cursor.execute("""
                CREATE OR REPLACE PROCEDURE TRANSFORM_NETSUITE_EXPENSE_REPORTS()
                RETURNS STRING
                LANGUAGE SQL
                AS
                $$
                DECLARE
                    processed_count NUMBER DEFAULT 0;
                BEGIN
                    
                    -- Transform raw NetSuite expense reports
                    INSERT INTO NETSUITE_DATA.EXPENSE_REPORTS (
                        EXPENSE_ID,
                        EXPENSE_REPORT_ID,
                        EMPLOYEE_ID,
                        EXPENSE_DATE,
                        EXPENSE_CATEGORY,
                        EXPENSE_DESCRIPTION,
                        AMOUNT,
                        CURRENCY,
                        DEPARTMENT,
                        PROJECT_ID,
                        CLIENT_ID,
                        IS_BILLABLE,
                        SUBMITTED_DATE,
                        APPROVED_DATE,
                        APPROVED_BY,
                        RECEIPT_ATTACHED
                    )
                    SELECT 
                        _ESTUARY_DATA:internalId::VARCHAR AS EXPENSE_ID,
                        _ESTUARY_DATA:parentExpenseReport:internalId::VARCHAR AS EXPENSE_REPORT_ID,
                        _ESTUARY_DATA:employee:internalId::VARCHAR AS EMPLOYEE_ID,
                        _ESTUARY_DATA:expenseDate::DATE AS EXPENSE_DATE,
                        _ESTUARY_DATA:category:name::VARCHAR AS EXPENSE_CATEGORY,
                        _ESTUARY_DATA:memo::VARCHAR AS EXPENSE_DESCRIPTION,
                        _ESTUARY_DATA:amount::FLOAT AS AMOUNT,
                        _ESTUARY_DATA:currency:name::VARCHAR AS CURRENCY,
                        _ESTUARY_DATA:department:name::VARCHAR AS DEPARTMENT,
                        _ESTUARY_DATA:customer:internalId::VARCHAR AS PROJECT_ID,
                        _ESTUARY_DATA:customer:internalId::VARCHAR AS CLIENT_ID,
                        _ESTUARY_DATA:isBillable::BOOLEAN AS IS_BILLABLE,
                        _ESTUARY_DATA:dateCreated::DATE AS SUBMITTED_DATE,
                        _ESTUARY_DATA:approvedDate::DATE AS APPROVED_DATE,
                        _ESTUARY_DATA:approvedBy:name::VARCHAR AS APPROVED_BY,
                        CASE WHEN _ESTUARY_DATA:receipt IS NOT NULL THEN TRUE ELSE FALSE END AS RECEIPT_ATTACHED
                    FROM RAW_ESTUARY._ESTUARY_RAW_NETSUITE_EXPENSE_REPORTS
                    WHERE _ESTUARY_DATA:internalId IS NOT NULL
                    AND NOT EXISTS (
                        SELECT 1 FROM NETSUITE_DATA.EXPENSE_REPORTS 
                        WHERE EXPENSE_ID = _ESTUARY_DATA:internalId::VARCHAR
                    );
                    
                    GET DIAGNOSTICS processed_count = ROW_COUNT;
                    
                    RETURN 'Processed ' || processed_count || ' NetSuite expense reports';
                    
                EXCEPTION
                    WHEN OTHER THEN
                        RETURN 'Error transforming NetSuite expense reports: ' || SQLERRM;
                END;
                $$;
            """)
            
            # Create task to run transformations automatically
            cursor.execute("""
                CREATE OR REPLACE TASK TASK_TRANSFORM_NETSUITE_DATA
                    WAREHOUSE = WH_SOPHIA_AI_PROCESSING
                    SCHEDULE = 'USING CRON 0 */6 * * * UTC'
                    COMMENT = 'Transform NetSuite raw data to structured schema every 6 hours'
                AS
                BEGIN
                    CALL TRANSFORM_NETSUITE_ACCOUNTS();
                    CALL TRANSFORM_NETSUITE_PURCHASE_ORDERS();
                    CALL TRANSFORM_NETSUITE_EXPENSE_REPORTS();
                END;
            """)
            
            # Resume the task
            cursor.execute("ALTER TASK TASK_TRANSFORM_NETSUITE_DATA RESUME;")
            
            cursor.close()
            snowflake_conn.close()
            
            logger.info("✅ Created NetSuite transformation procedures and tasks")
            
        except Exception as e:
            logger.error(f"❌ Failed to create NetSuite transformation procedures: {e}")
            raise

    async def setup_complete_netsuite_pipeline(self) -> Dict[str, str]:
        """Set up complete NetSuite data pipeline"""
        try:
            logger.info("🚀 Setting up complete NetSuite data pipeline")
            
            # Create NetSuite source
            source_response = await self._create_netsuite_source()
            source_id = source_response['sourceId']
            
            # Create Snowflake destination
            destination_response = await self._create_snowflake_destination()
            destination_id = destination_response['destinationId']
            
            # Create connection
            connection_response = await self._create_netsuite_connection(source_id, destination_id)
            connection_id = connection_response['connectionId']
            
            # Create transformation procedures
            await self.create_transformation_procedures()
            
            # Trigger initial sync
            await self.config_manager.trigger_sync(connection_id)
            
            pipeline_info = {
                'source_id': source_id,
                'destination_id': destination_id,
                'connection_id': connection_id,
                'status': 'configured'
            }
            
            logger.info(f"✅ NetSuite pipeline setup completed: {pipeline_info}")
            return pipeline_info
            
        except Exception as e:
            logger.error(f"❌ NetSuite pipeline setup failed: {e}")
            raise

async def main():
    """Main execution function"""
    orchestrator = EstuaryNetSuiteOrchestrator()
    
    try:
        await orchestrator.initialize()
        pipeline_info = await orchestrator.setup_complete_netsuite_pipeline()
        
        print("✅ NetSuite Estuary pipeline setup completed successfully!")
        print(f"📊 Pipeline info: {pipeline_info}")
        
    except Exception as e:
        print(f"❌ NetSuite pipeline setup failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(asyncio.run(main())) 