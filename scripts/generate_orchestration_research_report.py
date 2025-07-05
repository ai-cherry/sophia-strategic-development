#!/usr/bin/env python3
"""
Generate orchestration research report for Sophia AI platform.
Usage: python scripts/generate_orchestration_research_report.py
"""

import asyncio
import json

from backend.agents.research.orchestration_research_agent import (
    OrchestrationResearchAgent,
)


async def main():
    agent = OrchestrationResearchAgent()
    print("Starting deep research on orchestration patterns...")
    report = await agent.research_sophia_orchestration_specifics()
    output_path = "reports/orchestration_research_report.json"

    # Ensure reports directory exists
    import os

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w") as f:
        json.dump(
            {
                "research_results": report.research_results,
                "key_patterns": report.key_patterns,
                "implementation_recommendations": report.implementation_recommendations,
                "architecture_insights": report.architecture_insights,
            },
            f,
            indent=2,
        )

    print(f"Orchestration research report saved to {output_path}")


if __name__ == "__main__":
    asyncio.run(main())
