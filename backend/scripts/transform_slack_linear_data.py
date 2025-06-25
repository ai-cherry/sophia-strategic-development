#!/usr/bin/env python3
"""
Slack & Linear Data Transformation Script
Transforms raw Airbyte data into structured format for knowledge base integration
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Optional
from dataclasses import dataclass
from enum import Enum

from backend.utils.snowflake_cortex_service import SnowflakeCortexService
from backend.core.snowflake_config_manager import SnowflakeConfigManager

logger = logging.getLogger(__name__)


class TransformationSource(Enum):
    """Data transformation sources"""

    SLACK = "slack"
    LINEAR = "linear"


@dataclass
class TransformationStats:
    """Statistics for data transformation"""

    source: str
    total_records: int = 0
    processed_records: int = 0
    failed_records: int = 0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

    @property
    def duration_seconds(self) -> float:
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0

    @property
    def success_rate(self) -> float:
        if self.total_records > 0:
            return self.processed_records / self.total_records
        return 0.0


class SlackLinearTransformationService:
    """Service for transforming Slack and Linear data"""

    def __init__(self):
        self.cortex_service = SnowflakeCortexService()
        self.config_manager = SnowflakeConfigManager()

    async def initialize(self):
        """Initialize the transformation service"""
        await self.cortex_service.initialize()
        await self.config_manager.initialize()
        logger.info("✅ Slack & Linear transformation service initialized")

    async def close(self):
        """Clean up resources"""
        await self.cortex_service.close()
        await self.config_manager.close()

    async def transform_slack_messages(self) -> TransformationStats:
        """Transform raw Slack messages to structured format"""
        stats = TransformationStats(source="slack")
        stats.start_time = datetime.now()

        try:
            logger.info("Starting Slack messages transformation")

            # Call Snowflake stored procedure
            transform_query = "CALL SLACK_DATA.TRANSFORM_RAW_SLACK_MESSAGES()"
            result = await self.cortex_service.execute_query(transform_query)

            # Parse result for statistics
            if result and len(result) > 0:
                result_message = result[0][0] if result[0] else "Success"
                logger.info(f"Slack transformation result: {result_message}")

                # Extract numbers from result message
                import re

                numbers = re.findall(r"\d+", result_message)
                if numbers:
                    stats.processed_records = int(numbers[0])

            # Log to monitoring table
            await self._log_etl_job(
                job_name="transform_slack_messages",
                status="SUCCESS",
                rows_processed=stats.processed_records,
                duration_seconds=stats.duration_seconds,
            )

        except Exception as e:
            logger.error(f"Slack messages transformation failed: {e}")
            stats.failed_records = stats.total_records
            await self._log_etl_job(
                job_name="transform_slack_messages",
                status="FAILED",
                error_message=str(e),
            )
            raise

        finally:
            stats.end_time = datetime.now()

        return stats

    async def create_slack_conversations(self) -> TransformationStats:
        """Create conversation records from Slack messages"""
        stats = TransformationStats(source="slack_conversations")
        stats.start_time = datetime.now()

        try:
            logger.info("Creating Slack conversation records")

            # Call Snowflake stored procedure
            conversation_query = "CALL SLACK_DATA.CREATE_SLACK_CONVERSATIONS()"
            result = await self.cortex_service.execute_query(conversation_query)

            if result and len(result) > 0:
                result_message = result[0][0] if result[0] else "Success"
                logger.info(f"Slack conversations result: {result_message}")

                import re

                numbers = re.findall(r"\d+", result_message)
                if numbers:
                    stats.processed_records = int(numbers[0])

            await self._log_etl_job(
                job_name="create_slack_conversations",
                status="SUCCESS",
                rows_processed=stats.processed_records,
                duration_seconds=stats.duration_seconds,
            )

        except Exception as e:
            logger.error(f"Slack conversations creation failed: {e}")
            stats.failed_records = stats.total_records
            await self._log_etl_job(
                job_name="create_slack_conversations",
                status="FAILED",
                error_message=str(e),
            )
            raise

        finally:
            stats.end_time = datetime.now()

        return stats

    async def process_slack_with_cortex(self) -> TransformationStats:
        """Process Slack conversations with Cortex AI"""
        stats = TransformationStats(source="slack_cortex")
        stats.start_time = datetime.now()

        try:
            logger.info("Processing Slack conversations with Cortex AI")

            # Call Snowflake stored procedure
            cortex_query = "CALL SLACK_DATA.PROCESS_SLACK_CONVERSATIONS_WITH_CORTEX()"
            result = await self.cortex_service.execute_query(cortex_query)

            if result and len(result) > 0:
                result_message = result[0][0] if result[0] else "Success"
                logger.info(f"Slack Cortex processing result: {result_message}")

                import re

                numbers = re.findall(r"\d+", result_message)
                if numbers:
                    stats.processed_records = int(numbers[0])

            await self._log_etl_job(
                job_name="process_slack_cortex",
                status="SUCCESS",
                rows_processed=stats.processed_records,
                duration_seconds=stats.duration_seconds,
            )

        except Exception as e:
            logger.error(f"Slack Cortex processing failed: {e}")
            stats.failed_records = stats.total_records
            await self._log_etl_job(
                job_name="process_slack_cortex", status="FAILED", error_message=str(e)
            )
            raise

        finally:
            stats.end_time = datetime.now()

        return stats

    async def extract_slack_insights(self) -> TransformationStats:
        """Extract knowledge insights from Slack conversations"""
        stats = TransformationStats(source="slack_insights")
        stats.start_time = datetime.now()

        try:
            logger.info("Extracting knowledge insights from Slack")

            # Call Snowflake stored procedure
            insights_query = "CALL SLACK_DATA.EXTRACT_SLACK_KNOWLEDGE_INSIGHTS()"
            result = await self.cortex_service.execute_query(insights_query)

            if result and len(result) > 0:
                result_message = result[0][0] if result[0] else "Success"
                logger.info(f"Slack insights extraction result: {result_message}")

                import re

                numbers = re.findall(r"\d+", result_message)
                if numbers:
                    stats.processed_records = int(numbers[0])

            await self._log_etl_job(
                job_name="extract_slack_insights",
                status="SUCCESS",
                rows_processed=stats.processed_records,
                duration_seconds=stats.duration_seconds,
            )

        except Exception as e:
            logger.error(f"Slack insights extraction failed: {e}")
            stats.failed_records = stats.total_records
            await self._log_etl_job(
                job_name="extract_slack_insights", status="FAILED", error_message=str(e)
            )
            raise

        finally:
            stats.end_time = datetime.now()

        return stats

    async def transform_linear_issues(self) -> TransformationStats:
        """Transform raw Linear issues to structured format"""
        stats = TransformationStats(source="linear_issues")
        stats.start_time = datetime.now()

        try:
            logger.info("Starting Linear issues transformation")

            # Call Snowflake stored procedure (to be created by Manus AI)
            transform_query = "CALL LINEAR_DATA.TRANSFORM_RAW_LINEAR_ISSUES()"
            result = await self.cortex_service.execute_query(transform_query)

            if result and len(result) > 0:
                result_message = result[0][0] if result[0] else "Success"
                logger.info(f"Linear transformation result: {result_message}")

                import re

                numbers = re.findall(r"\d+", result_message)
                if numbers:
                    stats.processed_records = int(numbers[0])

            await self._log_etl_job(
                job_name="transform_linear_issues",
                status="SUCCESS",
                rows_processed=stats.processed_records,
                duration_seconds=stats.duration_seconds,
            )

        except Exception as e:
            logger.error(f"Linear issues transformation failed: {e}")
            stats.failed_records = stats.total_records
            await self._log_etl_job(
                job_name="transform_linear_issues",
                status="FAILED",
                error_message=str(e),
            )
            raise

        finally:
            stats.end_time = datetime.now()

        return stats

    async def process_linear_with_cortex(self) -> TransformationStats:
        """Process Linear issues with Cortex AI"""
        stats = TransformationStats(source="linear_cortex")
        stats.start_time = datetime.now()

        try:
            logger.info("Processing Linear issues with Cortex AI")

            # Call Snowflake stored procedure (to be created by Manus AI)
            cortex_query = "CALL LINEAR_DATA.PROCESS_LINEAR_ISSUES_WITH_CORTEX()"
            result = await self.cortex_service.execute_query(cortex_query)

            if result and len(result) > 0:
                result_message = result[0][0] if result[0] else "Success"
                logger.info(f"Linear Cortex processing result: {result_message}")

                import re

                numbers = re.findall(r"\d+", result_message)
                if numbers:
                    stats.processed_records = int(numbers[0])

            await self._log_etl_job(
                job_name="process_linear_cortex",
                status="SUCCESS",
                rows_processed=stats.processed_records,
                duration_seconds=stats.duration_seconds,
            )

        except Exception as e:
            logger.error(f"Linear Cortex processing failed: {e}")
            stats.failed_records = stats.total_records
            await self._log_etl_job(
                job_name="process_linear_cortex", status="FAILED", error_message=str(e)
            )
            raise

        finally:
            stats.end_time = datetime.now()

        return stats

    async def run_full_slack_pipeline(self) -> Dict[str, TransformationStats]:
        """Run complete Slack data transformation pipeline"""
        logger.info("🚀 Starting full Slack data transformation pipeline")

        results = {}

        try:
            # Step 1: Transform raw messages
            results["messages"] = await self.transform_slack_messages()

            # Step 2: Create conversations
            results["conversations"] = await self.create_slack_conversations()

            # Step 3: Process with Cortex AI
            results["cortex"] = await self.process_slack_with_cortex()

            # Step 4: Extract insights
            results["insights"] = await self.extract_slack_insights()

            logger.info("✅ Slack transformation pipeline completed successfully")

        except Exception as e:
            logger.error(f"❌ Slack transformation pipeline failed: {e}")
            raise

        return results

    async def run_full_linear_pipeline(self) -> Dict[str, TransformationStats]:
        """Run complete Linear data transformation pipeline"""
        logger.info("🚀 Starting full Linear data transformation pipeline")

        results = {}

        try:
            # Step 1: Transform raw issues
            results["issues"] = await self.transform_linear_issues()

            # Step 2: Process with Cortex AI
            results["cortex"] = await self.process_linear_with_cortex()

            logger.info("✅ Linear transformation pipeline completed successfully")

        except Exception as e:
            logger.error(f"❌ Linear transformation pipeline failed: {e}")
            raise

        return results

    async def _log_etl_job(
        self,
        job_name: str,
        status: str,
        rows_processed: int = 0,
        duration_seconds: float = 0.0,
        error_message: Optional[str] = None,
    ):
        """Log ETL job execution to monitoring table"""
        try:
            log_query = f"""
            INSERT INTO OPS_MONITORING.ETL_JOB_LOGS (
                JOB_NAME,
                JOB_TYPE,
                STATUS,
                START_TIME,
                END_TIME,
                DURATION_SECONDS,
                ROWS_PROCESSED,
                ERROR_MESSAGE
            ) VALUES (
                '{job_name}',
                'TRANSFORMATION',
                '{status}',
                CURRENT_TIMESTAMP(),
                CURRENT_TIMESTAMP(),
                {duration_seconds},
                {rows_processed},
                {f"'{error_message}'" if error_message else "NULL"}
            )
            """

            await self.cortex_service.execute_query(log_query)

        except Exception as e:
            logger.error(f"Failed to log ETL job: {e}")


async def main():
    """Main function for command-line usage"""
    import argparse

    parser = argparse.ArgumentParser(description="Transform Slack and Linear data")
    parser.add_argument("--source", choices=["slack", "linear", "both"], default="both")
    parser.add_argument(
        "--step", choices=["all", "messages", "conversations", "cortex", "insights"]
    )
    parser.add_argument("--verbose", action="store_true")

    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    service = SlackLinearTransformationService()

    try:
        await service.initialize()

        if args.source in ["slack", "both"]:
            if args.step == "all":
                slack_results = await service.run_full_slack_pipeline()
                print(f"✅ Slack pipeline completed: {slack_results}")
            else:
                # Run specific step
                if args.step == "messages":
                    result = await service.transform_slack_messages()
                elif args.step == "conversations":
                    result = await service.create_slack_conversations()
                elif args.step == "cortex":
                    result = await service.process_slack_with_cortex()
                elif args.step == "insights":
                    result = await service.extract_slack_insights()

                print(f"✅ Slack {args.step} completed: {result}")

        if args.source in ["linear", "both"]:
            linear_results = await service.run_full_linear_pipeline()
            print(f"✅ Linear pipeline completed: {linear_results}")

    finally:
        await service.close()


if __name__ == "__main__":
    asyncio.run(main())
