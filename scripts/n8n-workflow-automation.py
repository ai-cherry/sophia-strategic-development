#!/usr/bin/env python3
"""
Sophia AI n8n Workflow Automation Script
Provides automation capabilities for n8n workflows with focus on Salesforce to HubSpot/Intercom migration.
Optimized for performance, stability, and quality without over-engineering.
"""

import asyncio
import json
import logging
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import aiohttp

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class WorkflowConfig:
    """Configuration for n8n workflow automation."""

    name: str
    webhook_url: str
    trigger_type: str
    schedule: str | None = None
    enabled: bool = True
    retry_count: int = 3
    timeout: int = 300


class N8NWorkflowAutomation:
    """n8n workflow automation manager for Sophia AI."""

    def __init__(self, base_url: str = None, api_key: str = None):
        self.base_url = base_url or os.getenv(
            "SOPHIA_API_URL", "https://sophia-ai-platform.vercel.app"
        )
        self.api_key = api_key or os.getenv("SOPHIA_API_KEY")
        self.session = None

        # Predefined workflow configurations
        self.workflows = {
            "salesforce_to_hubspot": WorkflowConfig(
                name="Salesforce to HubSpot Migration",
                webhook_url=f"{self.base_url}/api/n8n/webhook/salesforce_to_hubspot",
                trigger_type="webhook",
                schedule="0 */6 * * *",  # Every 6 hours
                enabled=True,
            ),
            "salesforce_to_intercom": WorkflowConfig(
                name="Salesforce to Intercom Migration",
                webhook_url=f"{self.base_url}/api/n8n/webhook/salesforce_to_intercom",
                trigger_type="webhook",
                schedule="0 */8 * * *",  # Every 8 hours
                enabled=True,
            ),
            "data_sync": WorkflowConfig(
                name="General Data Synchronization",
                webhook_url=f"{self.base_url}/api/n8n/webhook/data_sync",
                trigger_type="webhook",
                schedule="0 */2 * * *",  # Every 2 hours
                enabled=True,
            ),
            "lead_enrichment": WorkflowConfig(
                name="Lead Enrichment Automation",
                webhook_url=f"{self.base_url}/api/n8n/webhook/lead_enrichment",
                trigger_type="webhook",
                schedule="0 */4 * * *",  # Every 4 hours
                enabled=True,
            ),
        }

    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=300),
            headers={
                "Content-Type": "application/json",
                "User-Agent": "Sophia-AI-n8n-Automation/2.1.0",
            },
        )
        if self.api_key:
            self.session.headers.update({"Authorization": f"Bearer {self.api_key}"})
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()

    async def trigger_workflow(
        self, workflow_name: str, data: dict[str, Any]
    ) -> dict[str, Any]:
        """Trigger a specific n8n workflow."""
        try:
            if workflow_name not in self.workflows:
                raise ValueError(f"Unknown workflow: {workflow_name}")

            workflow = self.workflows[workflow_name]

            if not workflow.enabled:
                logger.warning(f"Workflow {workflow_name} is disabled")
                return {
                    "status": "skipped",
                    "reason": "workflow_disabled",
                    "workflow": workflow_name,
                }

            logger.info(f"Triggering workflow: {workflow.name}")

            # Prepare payload
            payload = {
                "workflow_type": workflow_name,
                "timestamp": datetime.utcnow().isoformat(),
                "source": "sophia-ai-automation",
                **data,
            }

            # Execute webhook request with retry logic
            for attempt in range(workflow.retry_count):
                try:
                    async with self.session.post(
                        workflow.webhook_url,
                        json=payload,
                        timeout=aiohttp.ClientTimeout(total=workflow.timeout),
                    ) as response:
                        result = await response.json()

                        if response.status == 200:
                            logger.info(
                                f"Workflow {workflow_name} completed successfully"
                            )
                            return {
                                "status": "success",
                                "workflow": workflow_name,
                                "result": result,
                                "attempt": attempt + 1,
                            }
                        else:
                            logger.warning(
                                f"Workflow {workflow_name} failed with status {response.status}"
                            )
                            if attempt == workflow.retry_count - 1:
                                return {
                                    "status": "failed",
                                    "workflow": workflow_name,
                                    "error": result.get("error", "Unknown error"),
                                    "status_code": response.status,
                                    "attempts": workflow.retry_count,
                                }

                except TimeoutError:
                    logger.warning(
                        f"Workflow {workflow_name} timed out (attempt {attempt + 1})"
                    )
                    if attempt == workflow.retry_count - 1:
                        return {
                            "status": "timeout",
                            "workflow": workflow_name,
                            "attempts": workflow.retry_count,
                        }

                except Exception as e:
                    logger.error(
                        f"Error in workflow {workflow_name} (attempt {attempt + 1}): {str(e)}"
                    )
                    if attempt == workflow.retry_count - 1:
                        return {
                            "status": "error",
                            "workflow": workflow_name,
                            "error": str(e),
                            "attempts": workflow.retry_count,
                        }

                # Wait before retry
                await asyncio.sleep(2**attempt)  # Exponential backoff

        except Exception as e:
            logger.error(f"Fatal error in workflow {workflow_name}: {str(e)}")
            return {"status": "fatal_error", "workflow": workflow_name, "error": str(e)}

    async def run_salesforce_migration(
        self, salesforce_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Run complete Salesforce migration to both HubSpot and Intercom."""
        logger.info("Starting Salesforce migration workflow")

        results = {}

        # Run HubSpot migration
        hubspot_result = await self.trigger_workflow(
            "salesforce_to_hubspot", {"salesforce_data": salesforce_data}
        )
        results["hubspot"] = hubspot_result

        # Run Intercom migration
        intercom_result = await self.trigger_workflow(
            "salesforce_to_intercom", {"salesforce_data": salesforce_data}
        )
        results["intercom"] = intercom_result

        # Determine overall status
        overall_status = "success"
        if (
            hubspot_result.get("status") != "success"
            or intercom_result.get("status") != "success"
        ):
            overall_status = "partial_failure"

        return {
            "status": overall_status,
            "migration_type": "salesforce_complete",
            "results": results,
            "timestamp": datetime.utcnow().isoformat(),
        }

    async def run_data_sync(self, sync_config: dict[str, Any]) -> dict[str, Any]:
        """Run general data synchronization workflow."""
        logger.info("Starting data synchronization workflow")

        return await self.trigger_workflow("data_sync", sync_config)

    async def run_lead_enrichment(self, leads: list[dict[str, Any]]) -> dict[str, Any]:
        """Run lead enrichment workflow."""
        logger.info(f"Starting lead enrichment for {len(leads)} leads")

        results = []
        for lead in leads:
            result = await self.trigger_workflow("lead_enrichment", {"lead_data": lead})
            results.append(result)

        # Calculate success rate
        successful = sum(1 for r in results if r.get("status") == "success")
        success_rate = (successful / len(results)) * 100 if results else 0

        return {
            "status": "completed",
            "enrichment_type": "batch_leads",
            "total_leads": len(leads),
            "successful": successful,
            "success_rate": f"{success_rate:.1f}%",
            "results": results,
            "timestamp": datetime.utcnow().isoformat(),
        }

    async def health_check(self) -> dict[str, Any]:
        """Check health of all workflow endpoints."""
        logger.info("Running workflow health check")

        health_results = {}

        for workflow_name, workflow in self.workflows.items():
            try:
                health_url = workflow.webhook_url.replace("/webhook/", "/health")
                async with self.session.get(health_url) as response:
                    if response.status == 200:
                        health_results[workflow_name] = "healthy"
                    else:
                        health_results[
                            workflow_name
                        ] = f"unhealthy (status: {response.status})"
            except Exception as e:
                health_results[workflow_name] = f"error: {str(e)}"

        overall_health = (
            "healthy"
            if all(status == "healthy" for status in health_results.values())
            else "degraded"
        )

        return {
            "overall_health": overall_health,
            "workflows": health_results,
            "timestamp": datetime.utcnow().isoformat(),
        }

    def generate_workflow_report(self, results: list[dict[str, Any]]) -> str:
        """Generate a comprehensive workflow execution report."""
        report = []
        report.append("# Sophia AI n8n Workflow Execution Report")
        report.append(f"Generated: {datetime.utcnow().isoformat()}")
        report.append("")

        # Summary statistics
        total_workflows = len(results)
        successful = sum(1 for r in results if r.get("status") == "success")
        failed = total_workflows - successful

        report.append("## Summary")
        report.append(f"- Total Workflows: {total_workflows}")
        report.append(f"- Successful: {successful}")
        report.append(f"- Failed: {failed}")
        report.append(
            f"- Success Rate: {(successful/total_workflows)*100:.1f}%"
            if total_workflows > 0
            else "- Success Rate: N/A"
        )
        report.append("")

        # Detailed results
        report.append("## Detailed Results")
        for i, result in enumerate(results, 1):
            workflow_name = result.get("workflow", "Unknown")
            status = result.get("status", "Unknown")
            report.append(f"### {i}. {workflow_name}")
            report.append(f"- Status: {status}")
            if "error" in result:
                report.append(f"- Error: {result['error']}")
            if "attempts" in result:
                report.append(f"- Attempts: {result['attempts']}")
            report.append("")

        return "\n".join(report)


# CLI interface for the automation script
async def main():
    """Main CLI interface for n8n workflow automation."""
    import argparse

    parser = argparse.ArgumentParser(description="Sophia AI n8n Workflow Automation")
    parser.add_argument(
        "--workflow",
        choices=[
            "salesforce_migration",
            "data_sync",
            "lead_enrichment",
            "health_check",
        ],
        required=True,
        help="Workflow to execute",
    )
    parser.add_argument("--data-file", help="JSON file containing input data")
    parser.add_argument("--output-file", help="File to save results")
    parser.add_argument("--base-url", help="Base URL for Sophia AI API")
    parser.add_argument("--api-key", help="API key for authentication")

    args = parser.parse_args()

    # Load input data if provided
    input_data = {}
    if args.data_file and Path(args.data_file).exists():
        with open(args.data_file) as f:
            input_data = json.load(f)

    # Execute workflow
    async with N8NWorkflowAutomation(
        base_url=args.base_url, api_key=args.api_key
    ) as automation:
        if args.workflow == "salesforce_migration":
            result = await automation.run_salesforce_migration(
                input_data.get("salesforce_data", {})
            )
        elif args.workflow == "data_sync":
            result = await automation.run_data_sync(input_data)
        elif args.workflow == "lead_enrichment":
            result = await automation.run_lead_enrichment(input_data.get("leads", []))
        elif args.workflow == "health_check":
            result = await automation.health_check()
        else:
            result = {"status": "error", "error": "Unknown workflow"}

        # Output results
        print(json.dumps(result, indent=2))

        # Save to file if requested
        if args.output_file:
            with open(args.output_file, "w") as f:
                json.dump(result, f, indent=2)
            print(f"Results saved to {args.output_file}")


if __name__ == "__main__":
    asyncio.run(main())
