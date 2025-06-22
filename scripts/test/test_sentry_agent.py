"""
Test script for SentryAgent MCP integration.

Instructions:
- Fill in your real Sentry project_slug and issue_id below.
- Run with: python scripts/test/test_sentry_agent.py
"""
import asyncio
import logging
from backend.core.auto_esc_config import config
from backend.agents.specialized.sentry_agent import SentryAgent
from backend.agents.core.base_agent import AgentConfig, Task
from datetime import datetime

logging.basicConfig(level=logging.INFO)

# TODO: Fill in your real Sentry project_slug and issue_id here
PROJECT_SLUG = "your_project_slug"
ISSUE_ID = "your_issue_id"

async def main():
    if PROJECT_SLUG == "your_project_slug" or ISSUE_ID == "your_issue_id":
        print("Please set PROJECT_SLUG and ISSUE_ID to real values before running the test.")
        return

    agent_config = AgentConfig(
        agent_id="test_sentry_agent",
        agent_type="error_monitoring",
        specialization="sentry"
    )
    agent = SentryAgent(agent_config)
    task = Task(
        task_id="test1",
        task_type="fetch_sentry_issue_context",
        agent_id="test_sentry_agent",
        task_data={"project_slug": PROJECT_SLUG, "issue_id": ISSUE_ID},
        status=None,
        created_at=datetime.utcnow(),
        started_at=None,
        completed_at=None,
        result=None,
        error_message=None,
        priority=None,
    )
    print(f"Testing SentryAgent with project_slug='{PROJECT_SLUG}' and issue_id='{ISSUE_ID}'...")
    try:
        result = await agent.process_task(task)
        print("\n=== SentryAgent Result ===")
        print(result)
    except Exception as e:
        print(f"Error during SentryAgent test: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 