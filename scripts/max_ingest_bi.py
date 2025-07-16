"""
Sophia AI - Maximize Business Intelligence Data Ingestion

This script orchestrates the complete data ingestion pipeline for all
critical business intelligence sources using Estuary Flow. It's the
first step in achieving maximum data awareness for the Sophia AI platform.

Phase 1: Kick off all data flows.
Future Phases: Verify ingestion, trigger embeddings, and load to vector store.

Date: July 12, 2025
"""

import backend.utils.path_utils  # noqa: F401, must be before other imports

import asyncio
import logging
import sys
from pathlib import Path

# Add project root to path for consistent imports
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from infrastructure.etl.estuary_flow_orchestrator import EstuaryFlowOrchestrator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s",
)
logger = logging.getLogger(__name__)

async def run_max_ingestion():
    """
    Initializes and runs the complete data ingestion pipeline for all 7 services.
    """
    logger.info("--- Starting Phase 1: Max Data Pull ---")
    logger.info(
        "Initializing Estuary Flow orchestrator to set up all 7 data pipelines."
    )

    try:
        async with EstuaryFlowOrchestrator() as orchestrator:
            results = await orchestrator.setup_complete_pipeline()
            logger.info("Successfully triggered pipeline setup for all services.")
            logger.info("Pipeline setup results:")
            for key, value in results.items():
                flow_id = value.get("id", "N/A")
                logger.info(f"  - {key}: {flow_id}")
        logger.info("--- Phase 1: Max Data Pull initiated successfully. ---")
        logger.info(
            "Estuary flows are now being created and started in the background."
        )
        logger.info(
            "Monitor the Estuary dashboard and PostgreSQL staging database to see the data flowing in."
        )

    except Exception as e:
        logger.exception(f"An error occurred during the max data pull process: {e}")
        logger.error("--- Phase 1: Max Data Pull FAILED. ---")

async def main():
    """Main entry point for the script."""
    await run_max_ingestion()

if __name__ == "__main__":
    asyncio.run(main())
