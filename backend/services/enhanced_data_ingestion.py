"""
Enhanced Data Ingestion Service for Sophia AI
Implements near-real-time data ingestion with Snowpipe as recommended in architectural research
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any

from ..core.simple_config import config
from ..utils.enhanced_snowflake_cortex_service import EnhancedSnowflakeCortexService

logger = logging.getLogger(__name__)


class IngestionPriority(Enum):
    """Data ingestion priority levels"""

    REAL_TIME = "real_time"  # Sub-second ingestion (Snowpipe)
    NEAR_REAL_TIME = "near_real_time"  # Seconds (Snowpipe)
    BATCH_HOURLY = "batch_hourly"  # Hourly batch processing
    BATCH_DAILY = "batch_daily"  # Daily batch processing


class DataSource(Enum):
    """Supported data sources"""

    GITHUB = "github"
    GONG = "gong"
    HUBSPOT = "hubspot"
    ASANA = "asana"
    LINEAR = "linear"
    SLACK = "slack"
    NOTION = "notion"
    KNOWLEDGE_BASE = "knowledge_base"


@dataclass
class IngestionConfig:
    """Configuration for data source ingestion"""

    source: DataSource
    priority: IngestionPriority
    snowpipe_name: str
    stage_name: str
    table_name: str
    file_format: str
    transformation_sql: str | None = None
    auto_ingest: bool = True
    error_integration: str | None = None


class EnhancedDataIngestionService:
    """
    Enhanced data ingestion service implementing architectural research recommendations:
    - Near-real-time ingestion with Snowpipe
    - MCP operational data → Snowflake analytical storage
    - Intelligent routing based on data criticality
    """

    def __init__(self):
        self.cortex_service = EnhancedSnowflakeCortexService()

        # Data source configurations as per research recommendations
        self.ingestion_configs = {
            DataSource.GITHUB: IngestionConfig(
                source=DataSource.GITHUB,
                priority=IngestionPriority.NEAR_REAL_TIME,
                snowpipe_name="GITHUB_WEBHOOK_PIPE",
                stage_name="GITHUB_EVENTS_STAGE",
                table_name="RAW_GITHUB_EVENTS",
                file_format="JSON_FORMAT",
                transformation_sql="SELECT * FROM @GITHUB_EVENTS_STAGE",
                auto_ingest=True,
            ),
            DataSource.GONG: IngestionConfig(
                source=DataSource.GONG,
                priority=IngestionPriority.REAL_TIME,
                snowpipe_name="GONG_CALLS_PIPE",
                stage_name="GONG_DATA_STAGE",
                table_name="RAW_GONG_CALLS",
                file_format="JSON_FORMAT",
                auto_ingest=True,
            ),
            DataSource.HUBSPOT: IngestionConfig(
                source=DataSource.HUBSPOT,
                priority=IngestionPriority.NEAR_REAL_TIME,
                snowpipe_name="HUBSPOT_DEALS_PIPE",
                stage_name="HUBSPOT_DATA_STAGE",
                table_name="RAW_HUBSPOT_DEALS",
                file_format="JSON_FORMAT",
                auto_ingest=True,
            ),
            DataSource.ASANA: IngestionConfig(
                source=DataSource.ASANA,
                priority=IngestionPriority.NEAR_REAL_TIME,
                snowpipe_name="ASANA_TASKS_PIPE",
                stage_name="ASANA_DATA_STAGE",
                table_name="RAW_ASANA_TASKS",
                file_format="JSON_FORMAT",
            ),
            DataSource.LINEAR: IngestionConfig(
                source=DataSource.LINEAR,
                priority=IngestionPriority.NEAR_REAL_TIME,
                snowpipe_name="LINEAR_ISSUES_PIPE",
                stage_name="LINEAR_DATA_STAGE",
                table_name="RAW_LINEAR_ISSUES",
                file_format="JSON_FORMAT",
            ),
            DataSource.SLACK: IngestionConfig(
                source=DataSource.SLACK,
                priority=IngestionPriority.BATCH_HOURLY,
                snowpipe_name="SLACK_MESSAGES_PIPE",
                stage_name="SLACK_DATA_STAGE",
                table_name="RAW_SLACK_MESSAGES",
                file_format="JSON_FORMAT",
            ),
        }

    async def setup_snowpipe_infrastructure(self) -> dict[str, Any]:
        """
        Setup Snowpipe infrastructure for near-real-time ingestion
        Following research blueprint: "Snowpipe for near-real-time ingestion"
        """
        try:
            setup_results = {}

            for source, config in self.ingestion_configs.items():
                logger.info(f"Setting up Snowpipe infrastructure for {source.value}")

                # Create stage for data files
                stage_sql = f"""
                CREATE STAGE IF NOT EXISTS {config.stage_name}
                    URL = 's3://sophia-ai-data-ingestion/{source.value.lower()}/'
                    CREDENTIALS = (AWS_KEY_ID = '{await self._get_aws_key()}'
                                  AWS_SECRET_KEY = '{await self._get_aws_secret()}')
                    FILE_FORMAT = (TYPE = 'JSON' STRIP_OUTER_ARRAY = TRUE);
                """

                # Create Snowpipe
                pipe_sql = f"""
                CREATE PIPE IF NOT EXISTS {config.snowpipe_name}
                    AUTO_INGEST = {str(config.auto_ingest).upper()}
                    AS COPY INTO {config.table_name}
                    FROM @{config.stage_name}
                    FILE_FORMAT = {config.file_format};
                """

                # Execute setup
                await self.cortex_service.execute_query(stage_sql)
                await self.cortex_service.execute_query(pipe_sql)

                # Get pipe status
                status_sql = f"SHOW PIPES LIKE '{config.snowpipe_name}'"
                pipe_status = await self.cortex_service.execute_query(status_sql)

                setup_results[source.value] = {
                    "status": "configured",
                    "pipe_name": config.snowpipe_name,
                    "stage_name": config.stage_name,
                    "priority": config.priority.value,
                    "auto_ingest": config.auto_ingest,
                    "pipe_status": pipe_status,
                }

            logger.info("✅ Snowpipe infrastructure setup complete")
            return {
                "status": "success",
                "configured_sources": len(setup_results),
                "sources": setup_results,
                "setup_timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error setting up Snowpipe infrastructure: {e}")
            return {
                "status": "error",
                "error": str(e),
                "setup_timestamp": datetime.now().isoformat(),
            }

    async def ingest_real_time_data(
        self, source: DataSource, data: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Ingest real-time data through appropriate pipeline
        Routes to MCP for operational data, Snowpipe for analytical storage
        """
        try:
            config = self.ingestion_configs.get(source)
            if not config:
                raise ValueError(f"No ingestion config for source: {source}")

            # Determine ingestion strategy based on priority
            if config.priority in [
                IngestionPriority.REAL_TIME,
                IngestionPriority.NEAR_REAL_TIME,
            ]:
                # Use Snowpipe for real-time/near-real-time data
                result = await self._ingest_via_snowpipe(config, data)
            else:
                # Queue for batch processing
                result = await self._queue_for_batch_processing(config, data)

            return {
                "status": "success",
                "source": source.value,
                "ingestion_method": result["method"],
                "records_processed": result.get("records", 1),
                "processing_time": result.get("processing_time", 0),
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error ingesting data from {source.value}: {e}")
            return {
                "status": "error",
                "source": source.value,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    async def _ingest_via_snowpipe(
        self, config: IngestionConfig, data: dict[str, Any]
    ) -> dict[str, Any]:
        """Ingest data via Snowpipe for near-real-time processing"""
        start_time = datetime.now()

        try:
            # Stage the data file
            stage_path = f"@{config.stage_name}/{datetime.now().strftime('%Y/%m/%d')}/{datetime.now().timestamp()}.json"

            # In a real implementation, this would upload to S3 stage
            # For now, we'll simulate direct insertion
            insert_sql = f"""
            INSERT INTO {config.table_name} (raw_data, source, ingested_at)
            SELECT
                PARSE_JSON(%s) as raw_data,
                %s as source,
                CURRENT_TIMESTAMP() as ingested_at
            """

            await self.cortex_service.execute_query(
                insert_sql, params=[str(data), config.source.value]
            )

            processing_time = (datetime.now() - start_time).total_seconds()

            return {
                "method": "snowpipe",
                "records": 1,
                "processing_time": processing_time,
                "stage_path": stage_path,
            }

        except Exception as e:
            logger.error(f"Snowpipe ingestion failed: {e}")
            raise

    async def _queue_for_batch_processing(
        self, config: IngestionConfig, data: dict[str, Any]
    ) -> dict[str, Any]:
        """Queue data for batch processing"""
        try:
            # In a real implementation, this would queue to a message system
            # For now, we'll insert into a staging table
            queue_sql = """
            INSERT INTO BATCH_PROCESSING_QUEUE (source, data, priority, queued_at)
            VALUES (%s, %s, %s, CURRENT_TIMESTAMP())
            """

            await self.cortex_service.execute_query(
                queue_sql,
                params=[config.source.value, str(data), config.priority.value],
            )

            return {"method": "batch_queue", "records": 1, "processing_time": 0.1}

        except Exception as e:
            logger.error(f"Batch queueing failed: {e}")
            raise

    async def get_ingestion_metrics(self, time_range_hours: int = 24) -> dict[str, Any]:
        """Get ingestion performance metrics"""
        try:
            metrics_sql = f"""
            SELECT
                source,
                COUNT(*) as total_records,
                AVG(DATEDIFF('second', ingested_at, CURRENT_TIMESTAMP())) as avg_latency_seconds,
                MIN(ingested_at) as earliest_record,
                MAX(ingested_at) as latest_record
            FROM (
                SELECT 'GITHUB' as source, ingested_at FROM RAW_GITHUB_EVENTS
                WHERE ingested_at >= DATEADD('hour', -{time_range_hours}, CURRENT_TIMESTAMP())
                UNION ALL
                SELECT 'GONG' as source, ingested_at FROM RAW_GONG_CALLS
                WHERE ingested_at >= DATEADD('hour', -{time_range_hours}, CURRENT_TIMESTAMP())
                UNION ALL
                SELECT 'HUBSPOT' as source, ingested_at FROM RAW_HUBSPOT_DEALS
                WHERE ingested_at >= DATEADD('hour', -{time_range_hours}, CURRENT_TIMESTAMP())
            )
            GROUP BY source
            ORDER BY total_records DESC
            """

            metrics_data = await self.cortex_service.execute_query(metrics_sql)

            # Get Snowpipe status
            pipe_status_sql = "SHOW PIPES"
            pipe_status = await self.cortex_service.execute_query(pipe_status_sql)

            return {
                "time_range_hours": time_range_hours,
                "ingestion_metrics": metrics_data or [],
                "pipe_status": pipe_status or [],
                "overall_health": self._calculate_ingestion_health(metrics_data),
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error getting ingestion metrics: {e}")
            return {"error": str(e), "timestamp": datetime.now().isoformat()}

    def _calculate_ingestion_health(self, metrics_data: list[dict]) -> str:
        """Calculate overall ingestion health score"""
        if not metrics_data:
            return "unknown"

        # Simple health calculation based on recent activity
        total_records = sum(row.get("total_records", 0) for row in metrics_data)
        avg_latency = sum(
            row.get("avg_latency_seconds", 0) for row in metrics_data
        ) / len(metrics_data)

        if total_records > 100 and avg_latency < 30:
            return "healthy"
        elif total_records > 10 and avg_latency < 60:
            return "degraded"
        else:
            return "unhealthy"

    async def _get_aws_key(self) -> str:
        """Get AWS access key for S3 stage access"""
        return config.get("aws_access_key_id", "")

    async def _get_aws_secret(self) -> str:
        """Get AWS secret key for S3 stage access"""
        return config.get("aws_secret_access_key", "")


# Global service instance
enhanced_data_ingestion = EnhancedDataIngestionService()
