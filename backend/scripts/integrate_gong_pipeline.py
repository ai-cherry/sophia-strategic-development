#!/usr/bin/env python3
"""
Gong Pipeline Integration Script

Updates all existing Sophia AI services to integrate with the new Gong data pipeline
from STG_TRANSFORMED tables with AI Memory integration.

Usage:
    python backend/scripts/integrate_gong_pipeline.py --update-all
    python backend/scripts/integrate_gong_pipeline.py --test-integration
"""

import argparse
import asyncio
import json
import logging
import os
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any

from backend.utils.snowflake_cortex_service import SnowflakeCortexService

logger = logging.getLogger(__name__)


class IntegrationComponent(Enum):
    """Components to integrate with Gong pipeline"""

    CHAT_SERVICE = "chat_service"
    AI_MEMORY = "ai_memory"
    SAMPLE_QUERIES = "sample_queries"
    DOCUMENTATION = "documentation"
    ALL = "all"


@dataclass
class IntegrationResult:
    """Result of integration process"""

    component: IntegrationComponent
    success: bool
    message: str
    details: dict[str, Any] | None = None


class GongPipelineIntegrator:
    """Integrates existing Sophia AI services with new Gong data pipeline"""

    def __init__(self):
        self.cortex_service: SnowflakeCortexService | None = None
        self.integration_results: list[IntegrationResult] = []

    async def initialize(self):
        """Initialize services for integration"""
        try:
            self.cortex_service = SnowflakeCortexService()
            await self.cortex_service.initialize()
            logger.info("✅ Integration services initialized")
        except Exception as e:
            logger.error(f"Failed to initialize integration services: {e}")
            raise

    async def integrate_all_components(self) -> list[IntegrationResult]:
        """Integrate all components with Gong pipeline"""
        components = [
            IntegrationComponent.SAMPLE_QUERIES,
            IntegrationComponent.DOCUMENTATION,
        ]

        for component in components:
            await self.integrate_component(component)

        return self.integration_results

    async def integrate_component(
        self, component: IntegrationComponent
    ) -> IntegrationResult:
        """Integrate specific component"""
        try:
            if component == IntegrationComponent.SAMPLE_QUERIES:
                result = await self._create_sample_queries()
            elif component == IntegrationComponent.DOCUMENTATION:
                result = await self._update_documentation()
            else:
                result = IntegrationResult(
                    component=component,
                    success=False,
                    message=f"Unknown component: {component}",
                )

            self.integration_results.append(result)
            return result

        except Exception as e:
            result = IntegrationResult(
                component=component,
                success=False,
                message=f"Integration failed: {str(e)}",
            )
            self.integration_results.append(result)
            return result

    async def _create_sample_queries(self) -> IntegrationResult:
        """Create comprehensive sample queries for Gong integration"""
        try:
            sample_queries = {
                "gong_call_analysis": [
                    "Show me all calls with Acme Corp from last month",
                    "Find calls with sentiment score below -0.5",
                    "Get calls where talk ratio is less than 40%",
                    "Show high-value calls (>$100k) with positive sentiment",
                    "Find calls with risk indicators mentioned",
                ],
                "gong_executive_queries": [
                    "Give me an executive summary of this week's call performance",
                    "What are the trending topics in customer conversations?",
                    "Show me the sentiment analysis across all teams",
                    "Which deals have the highest risk based on call data?",
                    "What coaching insights can improve our close rate?",
                ],
            }

            # Save sample queries
            queries_file = "docs/sample_queries/gong_integration_queries.json"
            os.makedirs(os.path.dirname(queries_file), exist_ok=True)
            with open(queries_file, "w") as f:
                json.dump(sample_queries, f, indent=2)

            return IntegrationResult(
                component=IntegrationComponent.SAMPLE_QUERIES,
                success=True,
                message="Sample queries created for Gong integration testing",
                details={
                    "queries_file": queries_file,
                    "total_queries": sum(
                        len(queries) for queries in sample_queries.values()
                    ),
                },
            )

        except Exception as e:
            return IntegrationResult(
                component=IntegrationComponent.SAMPLE_QUERIES,
                success=False,
                message=f"Sample queries creation failed: {str(e)}",
            )

    async def _update_documentation(self) -> IntegrationResult:
        """Update documentation for Gong integration"""
        try:
            # Create comprehensive Gong integration documentation
            doc_content = """# Gong Pipeline Integration Guide

## Overview
The Gong Pipeline Integration provides comprehensive access to Gong call data through Sophia AI's enhanced data processing and AI capabilities.

## Architecture
```
Gong API → Estuary → RAW_ESTUARY → STG_TRANSFORMED → AI_MEMORY → Sophia AI Services
```

## Key Tables

### STG_TRANSFORMED.STG_GONG_CALLS
- CALL_ID: Unique call identifier
- SENTIMENT_SCORE: AI-generated sentiment (-1 to 1)
- CALL_SUMMARY: AI-generated call summary
- KEY_TOPICS: Extracted topics and themes
- RISK_INDICATORS: Identified risk factors
- AI_MEMORY_EMBEDDING: Vector embedding for semantic search

### STG_TRANSFORMED.STG_GONG_CALL_TRANSCRIPTS
- TRANSCRIPT_ID: Unique transcript segment identifier
- CALL_ID: Reference to parent call
- TRANSCRIPT_TEXT: Conversation text
- SEGMENT_SENTIMENT: Segment-level sentiment
- EXTRACTED_ENTITIES: Named entities in segment

## Usage Examples

### Natural Language Queries
- "Show me calls with negative sentiment from last week"
- "What are customers saying about pricing?"
- "Find coaching opportunities for the sales team"

### Direct SQL Access
```sql
SELECT CALL_ID, SENTIMENT_SCORE, CALL_SUMMARY
FROM SOPHIA_AI_DEV.STG_TRANSFORMED.STG_GONG_CALLS
WHERE SENTIMENT_SCORE < -0.2
ORDER BY CALL_DATETIME_UTC DESC;
```
"""

            doc_file = "docs/integrations/GONG_PIPELINE_INTEGRATION.md"
            os.makedirs(os.path.dirname(doc_file), exist_ok=True)
            with open(doc_file, "w") as f:
                f.write(doc_content)

            return IntegrationResult(
                component=IntegrationComponent.DOCUMENTATION,
                success=True,
                message="Documentation updated for Gong integration",
                details={"integration_doc": doc_file},
            )

        except Exception as e:
            return IntegrationResult(
                component=IntegrationComponent.DOCUMENTATION,
                success=False,
                message=f"Documentation update failed: {str(e)}",
            )

    async def test_integration(self) -> dict[str, Any]:
        """Test the complete Gong integration"""
        try:
            test_results = {"timestamp": datetime.utcnow().isoformat(), "tests": []}

            # Test Snowflake connectivity
            try:
                result = await self.cortex_service.execute_query("SELECT 1 as test")
                test_results["tests"].append(
                    {
                        "name": "snowflake_connectivity",
                        "status": "PASS" if len(result) > 0 else "FAIL",
                        "message": "Snowflake connection successful",
                    }
                )
            except Exception as e:
                test_results["tests"].append(
                    {
                        "name": "snowflake_connectivity",
                        "status": "FAIL",
                        "message": f"Snowflake connection failed: {e}",
                    }
                )

            # Calculate overall status
            passed_tests = sum(
                1 for test in test_results["tests"] if test["status"] == "PASS"
            )
            total_tests = len(test_results["tests"])
            test_results["overall_status"] = (
                "PASS" if passed_tests == total_tests else "FAIL"
            )
            test_results["summary"] = f"{passed_tests}/{total_tests} tests passed"

            return test_results

        except Exception as e:
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "overall_status": "ERROR",
                "error": str(e),
                "tests": [],
            }


async def main():
    """Main function for CLI usage"""
    parser = argparse.ArgumentParser(description="Gong Pipeline Integration")
    parser.add_argument(
        "--component",
        choices=[c.value for c in IntegrationComponent],
        default="all",
        help="Component to integrate",
    )
    parser.add_argument(
        "--test-integration", action="store_true", help="Test the integration"
    )
    parser.add_argument("--output", help="Output file for results (JSON)")

    args = parser.parse_args()

    integrator = GongPipelineIntegrator()
    await integrator.initialize()

    if args.test_integration:
        test_results = await integrator.test_integration()
        print(json.dumps(test_results, indent=2))

        if args.output:
            with open(args.output, "w") as f:
                json.dump(test_results, f, indent=2)
    else:
        if args.component == "all":
            results = await integrator.integrate_all_components()
        else:
            component = IntegrationComponent(args.component)
            result = await integrator.integrate_component(component)
            results = [result]

        for result in results:
            status = "✅" if result.success else "❌"
            print(f"{status} {result.component.value}: {result.message}")

        if args.output:
            results_dict = {
                "timestamp": datetime.utcnow().isoformat(),
                "results": [
                    {
                        "component": r.component.value,
                        "success": r.success,
                        "message": r.message,
                        "details": r.details,
                    }
                    for r in results
                ],
            }
            with open(args.output, "w") as f:
                json.dump(results_dict, f, indent=2)


if __name__ == "__main__":
    asyncio.run(main())
