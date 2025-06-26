#!/usr/bin/env python3
"""
Pay Ready Core SQL Data Ingestion Pipeline
Extracts data from operational Pay Ready SQL database and loads into Snowflake PAYREADY_CORE_SQL schema
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pandas as pd
import snowflake.connector
from sqlalchemy import create_engine, text
from dataclasses import dataclass

from backend.core.auto_esc_config import get_config_value
from backend.utils.snowflake_cortex_service import SnowflakeCortexService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PayReadyDataIngestionConfig:
    """Configuration for Pay Ready data ingestion"""
    source_db_connection: str
    snowflake_connection: Dict[str, str]
    batch_size: int = 1000
    max_retries: int = 3
    sync_window_hours: int = 24

class PayReadyCoreDataIngestor:
    """Ingests Pay Ready operational data into Snowflake PAYREADY_CORE_SQL schema"""
    
    def __init__(self):
        self.config = None
        self.source_engine = None
        self.snowflake_conn = None
        self.cortex_service = None
        
    async def initialize(self) -> None:
        """Initialize connections and services"""
        try:
            # Get configuration from Pulumi ESC
            self.config = PayReadyDataIngestionConfig(
                source_db_connection=await get_config_value("payready_operational_db_connection"),
                snowflake_connection={
                    "account": await get_config_value("snowflake_account"),
                    "user": await get_config_value("snowflake_user"),
                    "password": await get_config_value("snowflake_password"),
                    "database": "SOPHIA_AI_DEV",
                    "schema": "PAYREADY_CORE_SQL",
                    "warehouse": "WH_SOPHIA_AI_PROCESSING"
                }
            )
            
            # Initialize source database connection
            self.source_engine = create_engine(self.config.source_db_connection)
            
            # Initialize Snowflake connection
            self.snowflake_conn = snowflake.connector.connect(**self.config.snowflake_connection)
            
            # Initialize Cortex service for AI processing
            self.cortex_service = SnowflakeCortexService()
            await self.cortex_service.initialize()
            
            logger.info("✅ Pay Ready Core Data Ingestor initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Pay Ready ingestor: {e}")
            raise

    async def extract_payment_transactions(self, since_date: Optional[datetime] = None) -> pd.DataFrame:
        """Extract payment transactions from operational database"""
        try:
            if since_date is None:
                since_date = datetime.now() - timedelta(hours=self.config.sync_window_hours)
            
            query = """
            SELECT 
                transaction_id,
                customer_id,
                amount,
                currency,
                transaction_type,
                payment_method,
                status,
                processing_date,
                completed_date,
                failure_reason,
                property_id,
                unit_id,
                lease_id,
                invoice_id,
                processor_name,
                processor_transaction_id,
                processor_fee,
                processing_time_ms,
                risk_score,
                fraud_flags,
                compliance_status,
                aml_status,
                created_at,
                created_by,
                updated_by
            FROM payment_transactions 
            WHERE processing_date >= :since_date
            OR updated_at >= :since_date
            ORDER BY processing_date DESC
            """
            
            df = pd.read_sql_query(
                text(query), 
                self.source_engine, 
                params={"since_date": since_date}
            )
            
            logger.info(f"📊 Extracted {len(df)} payment transactions since {since_date}")
            return df
            
        except Exception as e:
            logger.error(f"❌ Failed to extract payment transactions: {e}")
            raise

    async def extract_customer_features(self, since_date: Optional[datetime] = None) -> pd.DataFrame:
        """Extract customer features from operational database"""
        try:
            if since_date is None:
                since_date = datetime.now() - timedelta(hours=self.config.sync_window_hours)
            
            query = """
            SELECT 
                feature_id,
                customer_id,
                feature_name,
                feature_category,
                is_enabled,
                configuration,
                default_configuration,
                custom_settings,
                feature_tier,
                requires_subscription,
                monthly_fee,
                activation_date,
                last_used_date,
                usage_count,
                usage_frequency,
                customer_satisfaction_impact,
                retention_impact,
                revenue_impact,
                created_at,
                enabled_by,
                disabled_by
            FROM customer_features 
            WHERE created_at >= :since_date
            OR updated_at >= :since_date
            ORDER BY created_at DESC
            """
            
            df = pd.read_sql_query(
                text(query), 
                self.source_engine, 
                params={"since_date": since_date}
            )
            
            logger.info(f"📊 Extracted {len(df)} customer features since {since_date}")
            return df
            
        except Exception as e:
            logger.error(f"❌ Failed to extract customer features: {e}")
            raise

    async def extract_business_rules(self, since_date: Optional[datetime] = None) -> pd.DataFrame:
        """Extract business rules from operational database"""
        try:
            if since_date is None:
                since_date = datetime.now() - timedelta(hours=self.config.sync_window_hours)
            
            query = """
            SELECT 
                rule_id,
                rule_name,
                rule_description,
                rule_type,
                rule_category,
                rule_expression,
                is_active,
                execution_order,
                execution_frequency,
                impact_level,
                affects_payments,
                affects_customers,
                affects_reporting,
                execution_count,
                last_executed_at,
                avg_execution_time_ms,
                success_rate,
                created_at,
                created_by,
                last_modified_by
            FROM business_rules 
            WHERE created_at >= :since_date
            OR updated_at >= :since_date
            ORDER BY execution_order
            """
            
            df = pd.read_sql_query(
                text(query), 
                self.source_engine, 
                params={"since_date": since_date}
            )
            
            logger.info(f"📊 Extracted {len(df)} business rules since {since_date}")
            return df
            
        except Exception as e:
            logger.error(f"❌ Failed to extract business rules: {e}")
            raise

    async def load_payment_transactions(self, df: pd.DataFrame) -> int:
        """Load payment transactions into Snowflake with MERGE logic"""
        try:
            if df.empty:
                logger.info("No payment transactions to load")
                return 0
            
            cursor = self.snowflake_conn.cursor()
            
            # Create temporary table
            cursor.execute("""
                CREATE OR REPLACE TEMPORARY TABLE TEMP_PAYMENT_TRANSACTIONS LIKE PAYMENT_TRANSACTIONS
            """)
            
            # Insert data into temporary table
            for _, row in df.iterrows():
                cursor.execute("""
                    INSERT INTO TEMP_PAYMENT_TRANSACTIONS (
                        TRANSACTION_ID, CUSTOMER_ID, AMOUNT, CURRENCY, TRANSACTION_TYPE,
                        PAYMENT_METHOD, STATUS, PROCESSING_DATE, COMPLETED_DATE, FAILURE_REASON,
                        PROPERTY_ID, UNIT_ID, LEASE_ID, INVOICE_ID, PROCESSOR_NAME,
                        PROCESSOR_TRANSACTION_ID, PROCESSOR_FEE, PROCESSING_TIME_MS,
                        RISK_SCORE, FRAUD_FLAGS, COMPLIANCE_STATUS, AML_STATUS,
                        CREATED_BY, UPDATED_BY
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s
                    )
                """, (
                    row['transaction_id'], row['customer_id'], row['amount'], 
                    row['currency'], row['transaction_type'], row['payment_method'],
                    row['status'], row['processing_date'], row['completed_date'],
                    row['failure_reason'], row['property_id'], row['unit_id'],
                    row['lease_id'], row['invoice_id'], row['processor_name'],
                    row['processor_transaction_id'], row['processor_fee'],
                    row['processing_time_ms'], row['risk_score'], 
                    json.dumps(row['fraud_flags']) if row['fraud_flags'] else None,
                    row['compliance_status'], row['aml_status'],
                    row['created_by'], row['updated_by']
                ))
            
            # MERGE into main table
            cursor.execute("""
                MERGE INTO PAYMENT_TRANSACTIONS AS target
                USING TEMP_PAYMENT_TRANSACTIONS AS source
                ON target.TRANSACTION_ID = source.TRANSACTION_ID
                WHEN MATCHED THEN UPDATE SET
                    AMOUNT = source.AMOUNT,
                    STATUS = source.STATUS,
                    PROCESSING_DATE = source.PROCESSING_DATE,
                    COMPLETED_DATE = source.COMPLETED_DATE,
                    FAILURE_REASON = source.FAILURE_REASON,
                    RISK_SCORE = source.RISK_SCORE,
                    FRAUD_FLAGS = source.FRAUD_FLAGS,
                    COMPLIANCE_STATUS = source.COMPLIANCE_STATUS,
                    AML_STATUS = source.AML_STATUS,
                    LAST_UPDATED = CURRENT_TIMESTAMP(),
                    UPDATED_BY = source.UPDATED_BY
                WHEN NOT MATCHED THEN INSERT (
                    TRANSACTION_ID, CUSTOMER_ID, AMOUNT, CURRENCY, TRANSACTION_TYPE,
                    PAYMENT_METHOD, STATUS, PROCESSING_DATE, COMPLETED_DATE, FAILURE_REASON,
                    PROPERTY_ID, UNIT_ID, LEASE_ID, INVOICE_ID, PROCESSOR_NAME,
                    PROCESSOR_TRANSACTION_ID, PROCESSOR_FEE, PROCESSING_TIME_MS,
                    RISK_SCORE, FRAUD_FLAGS, COMPLIANCE_STATUS, AML_STATUS,
                    CREATED_BY, UPDATED_BY
                ) VALUES (
                    source.TRANSACTION_ID, source.CUSTOMER_ID, source.AMOUNT, 
                    source.CURRENCY, source.TRANSACTION_TYPE, source.PAYMENT_METHOD,
                    source.STATUS, source.PROCESSING_DATE, source.COMPLETED_DATE,
                    source.FAILURE_REASON, source.PROPERTY_ID, source.UNIT_ID,
                    source.LEASE_ID, source.INVOICE_ID, source.PROCESSOR_NAME,
                    source.PROCESSOR_TRANSACTION_ID, source.PROCESSOR_FEE,
                    source.PROCESSING_TIME_MS, source.RISK_SCORE, source.FRAUD_FLAGS,
                    source.COMPLIANCE_STATUS, source.AML_STATUS,
                    source.CREATED_BY, source.UPDATED_BY
                )
            """)
            
            rows_affected = cursor.rowcount
            cursor.close()
            
            logger.info(f"✅ Loaded {rows_affected} payment transactions into Snowflake")
            return rows_affected
            
        except Exception as e:
            logger.error(f"❌ Failed to load payment transactions: {e}")
            raise

    async def load_customer_features(self, df: pd.DataFrame) -> int:
        """Load customer features into Snowflake with MERGE logic"""
        try:
            if df.empty:
                logger.info("No customer features to load")
                return 0
            
            cursor = self.snowflake_conn.cursor()
            
            # Create temporary table
            cursor.execute("""
                CREATE OR REPLACE TEMPORARY TABLE TEMP_CUSTOMER_FEATURES LIKE CUSTOMER_FEATURES
            """)
            
            # Insert data into temporary table
            for _, row in df.iterrows():
                cursor.execute("""
                    INSERT INTO TEMP_CUSTOMER_FEATURES (
                        FEATURE_ID, CUSTOMER_ID, FEATURE_NAME, FEATURE_CATEGORY, IS_ENABLED,
                        CONFIGURATION, DEFAULT_CONFIGURATION, CUSTOM_SETTINGS, FEATURE_TIER,
                        REQUIRES_SUBSCRIPTION, MONTHLY_FEE, ACTIVATION_DATE, LAST_USED_DATE,
                        USAGE_COUNT, USAGE_FREQUENCY, CUSTOMER_SATISFACTION_IMPACT,
                        RETENTION_IMPACT, REVENUE_IMPACT, ENABLED_BY, DISABLED_BY
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                """, (
                    row['feature_id'], row['customer_id'], row['feature_name'],
                    row['feature_category'], row['is_enabled'],
                    json.dumps(row['configuration']) if row['configuration'] else None,
                    json.dumps(row['default_configuration']) if row['default_configuration'] else None,
                    json.dumps(row['custom_settings']) if row['custom_settings'] else None,
                    row['feature_tier'], row['requires_subscription'], row['monthly_fee'],
                    row['activation_date'], row['last_used_date'], row['usage_count'],
                    row['usage_frequency'], row['customer_satisfaction_impact'],
                    row['retention_impact'], row['revenue_impact'],
                    row['enabled_by'], row['disabled_by']
                ))
            
            # MERGE into main table
            cursor.execute("""
                MERGE INTO CUSTOMER_FEATURES AS target
                USING TEMP_CUSTOMER_FEATURES AS source
                ON target.FEATURE_ID = source.FEATURE_ID
                WHEN MATCHED THEN UPDATE SET
                    IS_ENABLED = source.IS_ENABLED,
                    CONFIGURATION = source.CONFIGURATION,
                    CUSTOM_SETTINGS = source.CUSTOM_SETTINGS,
                    LAST_USED_DATE = source.LAST_USED_DATE,
                    USAGE_COUNT = source.USAGE_COUNT,
                    USAGE_FREQUENCY = source.USAGE_FREQUENCY,
                    CUSTOMER_SATISFACTION_IMPACT = source.CUSTOMER_SATISFACTION_IMPACT,
                    RETENTION_IMPACT = source.RETENTION_IMPACT,
                    REVENUE_IMPACT = source.REVENUE_IMPACT,
                    LAST_UPDATED = CURRENT_TIMESTAMP(),
                    DISABLED_BY = source.DISABLED_BY
                WHEN NOT MATCHED THEN INSERT (
                    FEATURE_ID, CUSTOMER_ID, FEATURE_NAME, FEATURE_CATEGORY, IS_ENABLED,
                    CONFIGURATION, DEFAULT_CONFIGURATION, CUSTOM_SETTINGS, FEATURE_TIER,
                    REQUIRES_SUBSCRIPTION, MONTHLY_FEE, ACTIVATION_DATE, LAST_USED_DATE,
                    USAGE_COUNT, USAGE_FREQUENCY, CUSTOMER_SATISFACTION_IMPACT,
                    RETENTION_IMPACT, REVENUE_IMPACT, ENABLED_BY, DISABLED_BY
                ) VALUES (
                    source.FEATURE_ID, source.CUSTOMER_ID, source.FEATURE_NAME,
                    source.FEATURE_CATEGORY, source.IS_ENABLED, source.CONFIGURATION,
                    source.DEFAULT_CONFIGURATION, source.CUSTOM_SETTINGS, source.FEATURE_TIER,
                    source.REQUIRES_SUBSCRIPTION, source.MONTHLY_FEE, source.ACTIVATION_DATE,
                    source.LAST_USED_DATE, source.USAGE_COUNT, source.USAGE_FREQUENCY,
                    source.CUSTOMER_SATISFACTION_IMPACT, source.RETENTION_IMPACT,
                    source.REVENUE_IMPACT, source.ENABLED_BY, source.DISABLED_BY
                )
            """)
            
            rows_affected = cursor.rowcount
            cursor.close()
            
            logger.info(f"✅ Loaded {rows_affected} customer features into Snowflake")
            return rows_affected
            
        except Exception as e:
            logger.error(f"❌ Failed to load customer features: {e}")
            raise

    async def generate_ai_embeddings(self, table_name: str, text_columns: List[str]) -> int:
        """Generate AI embeddings for text columns in specified table"""
        try:
            cursor = self.snowflake_conn.cursor()
            
            for column in text_columns:
                # Generate embeddings for records without them
                cursor.execute(f"""
                    UPDATE {table_name}
                    SET AI_MEMORY_EMBEDDING = SNOWFLAKE.CORTEX.EMBED_TEXT_768('e5-base-v2', {column}),
                        AI_MEMORY_METADATA = OBJECT_CONSTRUCT(
                            'embedding_model', 'e5-base-v2',
                            'embedding_source', '{column}',
                            'embedding_generated_at', CURRENT_TIMESTAMP()::STRING,
                            'embedding_confidence', 0.9
                        ),
                        AI_MEMORY_UPDATED_AT = CURRENT_TIMESTAMP()
                    WHERE {column} IS NOT NULL 
                    AND AI_MEMORY_EMBEDDING IS NULL
                """)
                
                rows_updated = cursor.rowcount
                logger.info(f"✅ Generated embeddings for {rows_updated} records in {table_name}.{column}")
            
            cursor.close()
            return rows_updated
            
        except Exception as e:
            logger.error(f"❌ Failed to generate embeddings for {table_name}: {e}")
            raise

    async def run_full_sync(self) -> Dict[str, int]:
        """Run full synchronization of Pay Ready core data"""
        try:
            logger.info("🚀 Starting Pay Ready Core Data full sync")
            
            results = {}
            
            # Extract and load payment transactions
            payment_df = await self.extract_payment_transactions()
            results['payment_transactions'] = await self.load_payment_transactions(payment_df)
            
            # Extract and load customer features
            features_df = await self.extract_customer_features()
            results['customer_features'] = await self.load_customer_features(features_df)
            
            # Extract and load business rules
            await self.extract_business_rules()
            # Note: Business rules loading would be implemented similarly
            
            # Generate AI embeddings
            await self.generate_ai_embeddings('PAYMENT_TRANSACTIONS', ['FAILURE_REASON'])
            await self.generate_ai_embeddings('CUSTOMER_FEATURES', ['FEATURE_NAME'])
            
            logger.info(f"✅ Pay Ready Core Data sync completed: {results}")
            return results
            
        except Exception as e:
            logger.error(f"❌ Pay Ready Core Data sync failed: {e}")
            raise

    async def run_incremental_sync(self, since_hours: int = 24) -> Dict[str, int]:
        """Run incremental synchronization for recent changes"""
        try:
            since_date = datetime.now() - timedelta(hours=since_hours)
            logger.info(f"🔄 Starting Pay Ready Core Data incremental sync since {since_date}")
            
            results = {}
            
            # Extract and load recent changes
            payment_df = await self.extract_payment_transactions(since_date)
            results['payment_transactions'] = await self.load_payment_transactions(payment_df)
            
            features_df = await self.extract_customer_features(since_date)
            results['customer_features'] = await self.load_customer_features(features_df)
            
            # Generate embeddings for new records
            await self.generate_ai_embeddings('PAYMENT_TRANSACTIONS', ['FAILURE_REASON'])
            await self.generate_ai_embeddings('CUSTOMER_FEATURES', ['FEATURE_NAME'])
            
            logger.info(f"✅ Pay Ready Core Data incremental sync completed: {results}")
            return results
            
        except Exception as e:
            logger.error(f"❌ Pay Ready Core Data incremental sync failed: {e}")
            raise

    async def close(self) -> None:
        """Clean up connections"""
        try:
            if self.snowflake_conn:
                self.snowflake_conn.close()
            if self.source_engine:
                self.source_engine.dispose()
            if self.cortex_service:
                await self.cortex_service.close()
            logger.info("✅ Pay Ready Core Data Ingestor connections closed")
        except Exception as e:
            logger.error(f"❌ Error closing connections: {e}")

async def main():
    """Main execution function"""
    ingestor = PayReadyCoreDataIngestor()
    
    try:
        await ingestor.initialize()
        
        # Run incremental sync by default
        results = await ingestor.run_incremental_sync()
        
        print("✅ Pay Ready Core Data ingestion completed successfully!")
        print(f"📊 Results: {results}")
        
    except Exception as e:
        print(f"❌ Pay Ready Core Data ingestion failed: {e}")
        return 1
    finally:
        await ingestor.close()
    
    return 0

if __name__ == "__main__":
    exit(asyncio.run(main())) 