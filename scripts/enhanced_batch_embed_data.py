#!/usr/bin/env python3
"""
Enhanced Batch Embedding Data Script
Generates embeddings for all schemas including new PAYREADY_CORE_SQL, NETSUITE_DATA, 
PROPERTY_ASSETS, AI_WEB_RESEARCH, and CEO_INTELLIGENCE schemas
"""

import asyncio
import logging
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass

from backend.core.auto_esc_config import get_config_value
from backend.utils.snowflake_cortex_service import SnowflakeCortexService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class EmbeddingConfig:
    """Configuration for embedding generation"""
    table_name: str
    schema_name: str
    text_columns: List[str]
    id_column: str
    embedding_column: str = "AI_MEMORY_EMBEDDING"
    metadata_column: str = "AI_MEMORY_METADATA"
    updated_column: str = "AI_MEMORY_UPDATED_AT"
    batch_size: int = 100
    model: str = "e5-base-v2"
    security_level: str = "STANDARD"  # STANDARD, CONFIDENTIAL, CEO_ONLY

class EnhancedBatchEmbeddingProcessor:
    """Enhanced processor for generating embeddings across all schemas"""
    
    def __init__(self):
        self.cortex_service = None
        self.snowflake_conn = None
        
        # Define embedding configurations for all schemas
        self.embedding_configs = [
            # HUBSPOT_DATA schema
            EmbeddingConfig(
                table_name="STG_HUBSPOT_DEALS",
                schema_name="HUBSPOT_DATA",
                text_columns=["DEAL_NAME", "DEAL_DESCRIPTION"],
                id_column="DEAL_ID"
            ),
            EmbeddingConfig(
                table_name="STG_HUBSPOT_CONTACTS",
                schema_name="HUBSPOT_DATA", 
                text_columns=["FULL_NAME", "JOB_TITLE", "COMPANY_NAME"],
                id_column="CONTACT_ID"
            ),
            
            # GONG_DATA schema
            EmbeddingConfig(
                table_name="STG_GONG_CALLS",
                schema_name="GONG_DATA",
                text_columns=["CALL_TITLE", "CALL_SUMMARY"],
                id_column="CALL_ID"
            ),
            EmbeddingConfig(
                table_name="STG_GONG_CALL_TRANSCRIPTS",
                schema_name="GONG_DATA",
                text_columns=["TRANSCRIPT_TEXT", "SEGMENT_SUMMARY"],
                id_column="TRANSCRIPT_ID"
            ),
            
            # SLACK_DATA schema
            EmbeddingConfig(
                table_name="STG_SLACK_MESSAGES",
                schema_name="SLACK_DATA",
                text_columns=["MESSAGE_TEXT", "EXTRACTED_TOPICS"],
                id_column="MESSAGE_ID"
            ),
            EmbeddingConfig(
                table_name="SLACK_KNOWLEDGE_INSIGHTS",
                schema_name="SLACK_DATA",
                text_columns=["INSIGHT_TITLE", "INSIGHT_DESCRIPTION", "INSIGHT_SUMMARY"],
                id_column="INSIGHT_ID"
            ),
            
            # FOUNDATIONAL_KNOWLEDGE schema
            EmbeddingConfig(
                table_name="EMPLOYEES",
                schema_name="FOUNDATIONAL_KNOWLEDGE",
                text_columns=["FULL_NAME", "JOB_TITLE", "DEPARTMENT", "EXPERTISE_SUMMARY"],
                id_column="EMPLOYEE_ID"
            ),
            EmbeddingConfig(
                table_name="CUSTOMERS",
                schema_name="FOUNDATIONAL_KNOWLEDGE",
                text_columns=["COMPANY_NAME", "INDUSTRY", "BUSINESS_DESCRIPTION"],
                id_column="CUSTOMER_ID"
            ),
            EmbeddingConfig(
                table_name="BUSINESS_DOCUMENTS",
                schema_name="FOUNDATIONAL_KNOWLEDGE",
                text_columns=["DOCUMENT_TITLE", "DOCUMENT_SUMMARY", "DOCUMENT_CONTENT"],
                id_column="DOCUMENT_ID"
            ),
            
            # PAYREADY_CORE_SQL schema (NEW)
            EmbeddingConfig(
                table_name="PAYMENT_TRANSACTIONS",
                schema_name="PAYREADY_CORE_SQL",
                text_columns=["FAILURE_REASON", "TRANSACTION_TYPE"],
                id_column="TRANSACTION_ID"
            ),
            EmbeddingConfig(
                table_name="CUSTOMER_FEATURES",
                schema_name="PAYREADY_CORE_SQL",
                text_columns=["FEATURE_NAME", "FEATURE_DESCRIPTION"],
                id_column="FEATURE_ID"
            ),
            EmbeddingConfig(
                table_name="BUSINESS_RULES",
                schema_name="PAYREADY_CORE_SQL",
                text_columns=["RULE_NAME", "RULE_DESCRIPTION", "RULE_EXPRESSION"],
                id_column="RULE_ID"
            ),
            
            # NETSUITE_DATA schema (NEW)
            EmbeddingConfig(
                table_name="GENERAL_LEDGER",
                schema_name="NETSUITE_DATA",
                text_columns=["ACCOUNT_NAME", "DESCRIPTION", "MEMO"],
                id_column="ENTRY_ID"
            ),
            EmbeddingConfig(
                table_name="PURCHASE_ORDERS",
                schema_name="NETSUITE_DATA",
                text_columns=["PO_NUMBER", "VENDOR_NAME"],
                id_column="PO_ID"
            ),
            EmbeddingConfig(
                table_name="EXPENSE_REPORTS",
                schema_name="NETSUITE_DATA",
                text_columns=["EXPENSE_CATEGORY", "EXPENSE_DESCRIPTION"],
                id_column="EXPENSE_ID"
            ),
            
            # PROPERTY_ASSETS schema (NEW)
            EmbeddingConfig(
                table_name="PROPERTIES",
                schema_name="PROPERTY_ASSETS",
                text_columns=["PROPERTY_NAME", "ADDRESS", "PROPERTY_TYPE"],
                id_column="PROPERTY_ID"
            ),
            EmbeddingConfig(
                table_name="PROPERTY_UNITS",
                schema_name="PROPERTY_ASSETS",
                text_columns=["UNIT_NUMBER", "UNIT_TYPE"],
                id_column="UNIT_ID"
            ),
            EmbeddingConfig(
                table_name="PROPERTY_CONTACTS",
                schema_name="PROPERTY_ASSETS",
                text_columns=["FIRST_NAME", "LAST_NAME", "COMPANY_NAME", "ROLE"],
                id_column="CONTACT_ID"
            ),
            
            # AI_WEB_RESEARCH schema (NEW)
            EmbeddingConfig(
                table_name="INDUSTRY_TRENDS",
                schema_name="AI_WEB_RESEARCH",
                text_columns=["TREND_TITLE", "TREND_DESCRIPTION", "KEY_INSIGHTS"],
                id_column="TREND_ID"
            ),
            EmbeddingConfig(
                table_name="COMPETITOR_INTELLIGENCE",
                schema_name="AI_WEB_RESEARCH",
                text_columns=["COMPETITOR_NAME", "INTELLIGENCE_SUMMARY", "DETAILED_ANALYSIS"],
                id_column="INTELLIGENCE_ID"
            ),
            EmbeddingConfig(
                table_name="PARTNERSHIP_OPPORTUNITIES",
                schema_name="AI_WEB_RESEARCH",
                text_columns=["PARTNER_NAME", "OPPORTUNITY_DESCRIPTION"],
                id_column="OPPORTUNITY_ID"
            ),
            
            # CEO_INTELLIGENCE schema (NEW - CONFIDENTIAL)
            EmbeddingConfig(
                table_name="STRATEGIC_PLANS",
                schema_name="CEO_INTELLIGENCE",
                text_columns=["PLAN_TITLE", "EXECUTIVE_SUMMARY", "STRATEGIC_RATIONALE"],
                id_column="PLAN_ID",
                security_level="CEO_ONLY"
            ),
            EmbeddingConfig(
                table_name="BOARD_MATERIALS",
                schema_name="CEO_INTELLIGENCE",
                text_columns=["MATERIAL_TITLE", "MATERIAL_CONTENT"],
                id_column="MATERIAL_ID",
                security_level="CEO_ONLY"
            ),
            EmbeddingConfig(
                table_name="COMPETITIVE_INTELLIGENCE",
                schema_name="CEO_INTELLIGENCE",
                text_columns=["INTELLIGENCE_TITLE", "DETAILED_ANALYSIS", "STRATEGIC_IMPLICATIONS"],
                id_column="INTELLIGENCE_ID",
                security_level="CEO_ONLY"
            ),
            EmbeddingConfig(
                table_name="MA_OPPORTUNITIES",
                schema_name="CEO_INTELLIGENCE",
                text_columns=["TARGET_COMPANY_NAME", "STRATEGIC_RATIONALE", "DUE_DILIGENCE_SUMMARY"],
                id_column="OPPORTUNITY_ID",
                security_level="CEO_ONLY"
            ),
            EmbeddingConfig(
                table_name="INVESTOR_RELATIONS",
                schema_name="CEO_INTELLIGENCE",
                text_columns=["INVESTOR_NAME", "COMMUNICATION_SUBJECT", "COMMUNICATION_CONTENT"],
                id_column="COMMUNICATION_ID",
                security_level="CEO_ONLY"
            ),
            EmbeddingConfig(
                table_name="EXECUTIVE_DECISIONS",
                schema_name="CEO_INTELLIGENCE",
                text_columns=["DECISION_TITLE", "DECISION_SUMMARY", "RATIONALE"],
                id_column="DECISION_ID",
                security_level="CEO_ONLY"
            )
        ]
        
    async def initialize(self) -> None:
        """Initialize the embedding processor"""
        try:
            self.cortex_service = SnowflakeCortexService()
            await self.cortex_service.initialize()
            
            # Get direct Snowflake connection for batch operations
            self.snowflake_conn = await self._get_snowflake_connection()
            
            logger.info("✅ Enhanced Batch Embedding Processor initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize embedding processor: {e}")
            raise

    async def _get_snowflake_connection(self):
        """Get direct Snowflake connection"""
        import snowflake.connector
        
        connection = snowflake.connector.connect(
            account=await get_config_value("snowflake_account"),
            user=await get_config_value("snowflake_user"),
            password=await get_config_value("snowflake_password"),
            database="SOPHIA_AI_DEV",
            warehouse="WH_SOPHIA_AI_PROCESSING",
            role="ACCOUNTADMIN"
        )
        
        return connection

    async def _check_table_exists(self, schema_name: str, table_name: str) -> bool:
        """Check if table exists in the specified schema"""
        try:
            cursor = self.snowflake_conn.cursor()
            cursor.execute(f"""
                SELECT COUNT(*) 
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_SCHEMA = '{schema_name}' 
                AND TABLE_NAME = '{table_name}'
            """)
            
            result = cursor.fetchone()
            exists = result[0] > 0
            cursor.close()
            
            return exists
            
        except Exception as e:
            logger.warning(f"⚠️ Could not check if table {schema_name}.{table_name} exists: {e}")
            return False

    async def _get_records_needing_embeddings(self, config: EmbeddingConfig) -> List[Dict[str, Any]]:
        """Get records that need embeddings generated"""
        try:
            cursor = self.snowflake_conn.cursor()
            
            # Build text concatenation for multiple columns
            text_concat = " || ' ' || ".join([f"COALESCE({col}, '')" for col in config.text_columns])
            
            cursor.execute(f"""
                SELECT 
                    {config.id_column},
                    {text_concat} AS COMBINED_TEXT
                FROM {config.schema_name}.{config.table_name}
                WHERE {config.embedding_column} IS NULL
                AND ({" OR ".join([f"{col} IS NOT NULL" for col in config.text_columns])})
                LIMIT {config.batch_size}
            """)
            
            records = []
            for row in cursor.fetchall():
                records.append({
                    'id': row[0],
                    'text': row[1]
                })
            
            cursor.close()
            return records
            
        except Exception as e:
            logger.error(f"❌ Failed to get records needing embeddings for {config.table_name}: {e}")
            return []

    async def _generate_embeddings_batch(self, config: EmbeddingConfig, records: List[Dict[str, Any]]) -> int:
        """Generate embeddings for a batch of records"""
        try:
            cursor = self.snowflake_conn.cursor()
            updated_count = 0
            
            for record in records:
                try:
                    # Generate embedding using Snowflake Cortex
                    cursor.execute(f"""
                        UPDATE {config.schema_name}.{config.table_name}
                        SET 
                            {config.embedding_column} = SNOWFLAKE.CORTEX.EMBED_TEXT_768('{config.model}', %s),
                            {config.metadata_column} = OBJECT_CONSTRUCT(
                                'embedding_model', '{config.model}',
                                'embedding_source', %s,
                                'embedding_generated_at', CURRENT_TIMESTAMP()::STRING,
                                'embedding_confidence', 0.9,
                                'security_level', '{config.security_level}',
                                'text_length', LENGTH(%s)
                            ),
                            {config.updated_column} = CURRENT_TIMESTAMP()
                        WHERE {config.id_column} = %s
                    """, (
                        record['text'],
                        ', '.join(config.text_columns),
                        record['text'],
                        record['id']
                    ))
                    
                    updated_count += cursor.rowcount
                    
                except Exception as e:
                    logger.warning(f"⚠️ Failed to generate embedding for record {record['id']}: {e}")
                    continue
            
            cursor.close()
            return updated_count
            
        except Exception as e:
            logger.error(f"❌ Failed to generate embeddings batch for {config.table_name}: {e}")
            return 0

    async def _apply_cortex_sentiment_analysis(self, config: EmbeddingConfig) -> int:
        """Apply Cortex sentiment analysis to text columns"""
        try:
            cursor = self.snowflake_conn.cursor()
            
            # Only apply sentiment to specific schemas and tables
            sentiment_applicable = [
                ("GONG_DATA", "STG_GONG_CALLS"),
                ("GONG_DATA", "STG_GONG_CALL_TRANSCRIPTS"),
                ("SLACK_DATA", "STG_SLACK_MESSAGES"),
                ("AI_WEB_RESEARCH", "INDUSTRY_TRENDS"),
                ("AI_WEB_RESEARCH", "COMPETITOR_INTELLIGENCE"),
                ("CEO_INTELLIGENCE", "COMPETITIVE_INTELLIGENCE")
            ]
            
            if (config.schema_name, config.table_name) not in sentiment_applicable:
                return 0
            
            # Apply sentiment analysis to primary text column
            primary_text_column = config.text_columns[0]
            
            cursor.execute(f"""
                UPDATE {config.schema_name}.{config.table_name}
                SET 
                    SENTIMENT_SCORE = SNOWFLAKE.CORTEX.SENTIMENT({primary_text_column}),
                    {config.metadata_column} = OBJECT_INSERT(
                        COALESCE({config.metadata_column}, OBJECT_CONSTRUCT()),
                        'sentiment_analyzed_at', CURRENT_TIMESTAMP()::STRING
                    )
                WHERE {primary_text_column} IS NOT NULL
                AND SENTIMENT_SCORE IS NULL
            """)
            
            updated_count = cursor.rowcount
            cursor.close()
            
            return updated_count
            
        except Exception as e:
            logger.warning(f"⚠️ Could not apply sentiment analysis to {config.table_name}: {e}")
            return 0

    async def _apply_cortex_summarization(self, config: EmbeddingConfig) -> int:
        """Apply Cortex summarization to long text columns"""
        try:
            cursor = self.snowflake_conn.cursor()
            
            # Only apply summarization to specific schemas and tables with long content
            summarization_applicable = [
                ("GONG_DATA", "STG_GONG_CALL_TRANSCRIPTS"),
                ("FOUNDATIONAL_KNOWLEDGE", "BUSINESS_DOCUMENTS"),
                ("CEO_INTELLIGENCE", "STRATEGIC_PLANS"),
                ("CEO_INTELLIGENCE", "BOARD_MATERIALS"),
                ("CEO_INTELLIGENCE", "COMPETITIVE_INTELLIGENCE"),
                ("AI_WEB_RESEARCH", "INDUSTRY_TRENDS")
            ]
            
            if (config.schema_name, config.table_name) not in summarization_applicable:
                return 0
            
            # Find the longest text column for summarization
            primary_text_column = config.text_columns[0]
            if len(config.text_columns) > 1:
                # Use the column most likely to contain long content
                long_content_columns = ['CONTENT', 'DESCRIPTION', 'ANALYSIS', 'SUMMARY', 'TEXT']
                for col in config.text_columns:
                    if any(keyword in col.upper() for keyword in long_content_columns):
                        primary_text_column = col
                        break
            
            cursor.execute(f"""
                UPDATE {config.schema_name}.{config.table_name}
                SET 
                    AI_GENERATED_SUMMARY = SNOWFLAKE.CORTEX.SUMMARIZE({primary_text_column}),
                    {config.metadata_column} = OBJECT_INSERT(
                        COALESCE({config.metadata_column}, OBJECT_CONSTRUCT()),
                        'summarized_at', CURRENT_TIMESTAMP()::STRING
                    )
                WHERE {primary_text_column} IS NOT NULL
                AND LENGTH({primary_text_column}) > 500
                AND AI_GENERATED_SUMMARY IS NULL
            """)
            
            updated_count = cursor.rowcount
            cursor.close()
            
            return updated_count
            
        except Exception as e:
            logger.warning(f"⚠️ Could not apply summarization to {config.table_name}: {e}")
            return 0

    async def process_schema_embeddings(self, schema_name: str) -> Dict[str, int]:
        """Process embeddings for all tables in a specific schema"""
        try:
            logger.info(f"🔄 Processing embeddings for schema: {schema_name}")
            
            schema_configs = [config for config in self.embedding_configs if config.schema_name == schema_name]
            results = {}
            
            for config in schema_configs:
                # Check if table exists
                if not await self._check_table_exists(config.schema_name, config.table_name):
                    logger.warning(f"⚠️ Table {config.schema_name}.{config.table_name} does not exist, skipping")
                    continue
                
                logger.info(f"📊 Processing {config.schema_name}.{config.table_name}")
                
                # Get records needing embeddings
                records = await self._get_records_needing_embeddings(config)
                
                if not records:
                    logger.info(f"✅ No records need embeddings in {config.table_name}")
                    results[config.table_name] = 0
                    continue
                
                # Generate embeddings
                embedding_count = await self._generate_embeddings_batch(config, records)
                
                # Apply sentiment analysis
                sentiment_count = await self._apply_cortex_sentiment_analysis(config)
                
                # Apply summarization
                summary_count = await self._apply_cortex_summarization(config)
                
                results[config.table_name] = {
                    'embeddings': embedding_count,
                    'sentiment_analysis': sentiment_count,
                    'summarization': summary_count
                }
                
                logger.info(f"✅ Processed {config.table_name}: {embedding_count} embeddings, {sentiment_count} sentiment, {summary_count} summaries")
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Failed to process schema {schema_name}: {e}")
            return {}

    async def process_all_embeddings(self) -> Dict[str, Dict[str, int]]:
        """Process embeddings for all schemas"""
        try:
            logger.info("🚀 Starting comprehensive embedding processing for all schemas")
            
            all_results = {}
            
            # Process each schema
            schemas = list(set(config.schema_name for config in self.embedding_configs))
            
            for schema in schemas:
                schema_results = await self.process_schema_embeddings(schema)
                all_results[schema] = schema_results
            
            logger.info(f"✅ Comprehensive embedding processing completed: {all_results}")
            return all_results
            
        except Exception as e:
            logger.error(f"❌ Comprehensive embedding processing failed: {e}")
            raise

    async def generate_schema_statistics(self) -> Dict[str, Any]:
        """Generate statistics about embedding coverage across schemas"""
        try:
            cursor = self.snowflake_conn.cursor()
            stats = {}
            
            for config in self.embedding_configs:
                if not await self._check_table_exists(config.schema_name, config.table_name):
                    continue
                
                cursor.execute(f"""
                    SELECT 
                        COUNT(*) AS total_records,
                        COUNT({config.embedding_column}) AS records_with_embeddings,
                        COUNT(CASE WHEN {config.embedding_column} IS NULL THEN 1 END) AS records_without_embeddings,
                        ROUND(COUNT({config.embedding_column}) * 100.0 / COUNT(*), 2) AS embedding_coverage_percent
                    FROM {config.schema_name}.{config.table_name}
                """)
                
                result = cursor.fetchone()
                stats[f"{config.schema_name}.{config.table_name}"] = {
                    'total_records': result[0],
                    'records_with_embeddings': result[1],
                    'records_without_embeddings': result[2],
                    'embedding_coverage_percent': result[3],
                    'security_level': config.security_level
                }
            
            cursor.close()
            return stats
            
        except Exception as e:
            logger.error(f"❌ Failed to generate schema statistics: {e}")
            return {}

    async def close(self) -> None:
        """Clean up connections"""
        try:
            if self.snowflake_conn:
                self.snowflake_conn.close()
            if self.cortex_service:
                await self.cortex_service.close()
            logger.info("✅ Enhanced Batch Embedding Processor connections closed")
        except Exception as e:
            logger.error(f"❌ Error closing connections: {e}")

async def main():
    """Main execution function"""
    processor = EnhancedBatchEmbeddingProcessor()
    
    try:
        await processor.initialize()
        
        # Generate statistics before processing
        print("📊 Embedding Coverage Statistics (Before):")
        before_stats = await processor.generate_schema_statistics()
        for table, stats in before_stats.items():
            print(f"  {table}: {stats['embedding_coverage_percent']}% coverage ({stats['records_with_embeddings']}/{stats['total_records']} records)")
        
        # Process all embeddings
        results = await processor.process_all_embeddings()
        
        # Generate statistics after processing
        print("\n📊 Embedding Coverage Statistics (After):")
        after_stats = await processor.generate_schema_statistics()
        for table, stats in after_stats.items():
            print(f"  {table}: {stats['embedding_coverage_percent']}% coverage ({stats['records_with_embeddings']}/{stats['total_records']} records)")
        
        print(f"\n✅ Enhanced batch embedding processing completed successfully!")
        print(f"📈 Processing results: {json.dumps(results, indent=2)}")
        
    except Exception as e:
        print(f"❌ Enhanced batch embedding processing failed: {e}")
        return 1
    finally:
        await processor.close()
    
    return 0

if __name__ == "__main__":
    exit(asyncio.run(main())) 