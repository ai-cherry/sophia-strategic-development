"""
Master Data Workflow Runner
This script provides a command-line interface to trigger the various data
transformation and vectorization workflows within the Sophia AI system.
"""
import asyncio
import logging
import argparse

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from backend.workflows.langgraph_workflow import WorkflowTemplates, workflow_manager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def run_workflow(workflow_name: str):
    """
    Selects and runs the specified data processing workflow.
    
    Args:
        workflow_name: The name of the workflow to run ('gong' or 'slack').
    """
    logger.info(f"--- Triggering '{workflow_name}' Data Workflow ---")
    
    if workflow_name == 'gong':
        workflow = WorkflowTemplates.create_gong_transformation_workflow()
    elif workflow_name == 'slack':
        logger.warning("SlackTransformationWorkflow is not fully implemented yet.")
        # workflow = WorkflowTemplates.create_slack_transformation_workflow()
        print("Slack workflow placeholder triggered. No actions will be taken.")
        return
    else:
        logger.error(f"Unknown workflow: '{workflow_name}'. Please choose 'gong' or 'slack'.")
        return

    initial_context = {"trigger_method": "manual_script"}
    final_state = await workflow_manager.execute_workflow(workflow, initial_context)
    
    logger.info(f"--- Workflow '{workflow.workflow_id}' Finished ---")
    logger.info(f"Final Status: {final_state.status.value}")
    if final_state.errors:
        logger.error("Workflow completed with errors:")
        for error in final_state.errors:
            logger.error(f"  - Step '{error['step']}': {error['error']}")

def main():
    """Main function to parse arguments and run the selected workflow."""
    parser = argparse.ArgumentParser(
        description="Run data transformation and vectorization workflows for Sophia AI."
    )
    parser.add_argument(
        "workflow",
        type=str,
        choices=['gong', 'slack'],
        help="The name of the workflow to run ('gong' or 'slack')."
    )
    
    args = parser.parse_args()
    
    asyncio.run(run_workflow(args.workflow))

if __name__ == "__main__":
    main() 