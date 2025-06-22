#!/usr/bin/env python3
"""Test script for Agno integration.

Tests the Agno MCP server, Agno integration, and AG-UI components
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime
import pytest
from backend.integrations.agno_integration import agno_integration
from infrastructure.esc.agno_secrets import agno_secret_manager
from backend.agents.specialized.sentry_agent import SentryAgent
from backend.agents.specialized.call_analysis_agent import CallAnalysisAgent
from backend.agents.specialized.metrics_agent import MetricsAgent
from backend.agents.specialized.executive_agent import ExecutiveAgent
from backend.agents.specialized.sales_coach_agent import SalesCoachAgent
from backend.agents.specialized.crm_sync_agent import CRMSyncAgent
from backend.agents.specialized.insight_extraction_agent import InsightExtractionAgent
from backend.agents.specialized.project_intelligence_agent import ProjectIntelligenceAgent
from backend.agents.specialized.hr_agent import HRAgent
from backend.agents.core.base_agent import AgentConfig, Task

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(
            f"agno_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        ),
    ],
)
logger = logging.getLogger(__name__)

# Test configuration
TEST_AGENT_ID = "test_agent"
TEST_REQUEST = "What is the current status of our Gong integration? Please check the latest calls and provide a summary."

AGENTS = [
    ("SentryAgent", SentryAgent),
    ("CallAnalysisAgent", CallAnalysisAgent),
    ("MetricsAgent", MetricsAgent),
    ("ExecutiveAgent", ExecutiveAgent),
    ("SalesCoachAgent", SalesCoachAgent),
    ("CRMSyncAgent", CRMSyncAgent),
    ("InsightExtractionAgent", InsightExtractionAgent),
    ("ProjectIntelligenceAgent", ProjectIntelligenceAgent),
    ("HRAgent", HRAgent),
]

@pytest.mark.asyncio
async def test_agno_secret_loading():
    """Test Agno secret/config loading from Pulumi ESC."""
    api_key = await agno_secret_manager.get_agno_api_key()
    config = await agno_secret_manager.get_agno_config()
    assert api_key, "AGNO_API_KEY should not be empty"
    assert isinstance(config, dict), "AGNO_CONFIG should be a dict"
    print("✅ Agno secret/config loading passed.")

@pytest.mark.asyncio
async def test_agno_secret_loading_failure(monkeypatch):
    """Test Agno secret loading failure (simulate missing secret)."""
    monkeypatch.setattr(agno_secret_manager, "get_secret", lambda key: None)
    api_key = await agno_secret_manager.get_agno_api_key()
    assert api_key is None, "Should return None if secret is missing"
    print("✅ Agno secret loading failure handled.")

@pytest.mark.asyncio
async def test_agent_pooling():
    """Test pooled instantiation for all Agno agents."""
    for name, AgentClass in AGENTS:
        config = AgentConfig(agent_id=f"test_{name.lower()}", agent_type="test", specialization=name.lower())
        agent = await AgentClass.pooled(config)
        assert agent is not None, f"{name} pooled instantiation failed"
        print(f"✅ {name} pooled instantiation passed.")

@pytest.mark.asyncio
async def test_task_failure_handling():
    """Test task failure and exception handling for all Agno agents."""
    for name, AgentClass in AGENTS:
        config = AgentConfig(agent_id=f"fail_{name.lower()}", agent_type="test", specialization=name.lower())
        agent = await AgentClass.pooled(config)
        # Use an invalid task type to trigger error
        task = Task(
            task_id="fail_task",
            task_type="invalid_task_type",
            agent_id=config.agent_id,
            task_data={},
            status=None,
            created_at=datetime.utcnow(),
            started_at=None,
            completed_at=None,
            result=None,
            error_message=None,
            priority=None,
        )
        result = await agent.process_task(task)
        assert not result.get("success", True), f"{name} should fail on invalid task type"
        print(f"✅ {name} task failure handling passed.")

@pytest.mark.asyncio
async def test_edge_cases():
    """Test edge cases: rapid agent creation, concurrent tasks, missing config."""
    # Rapid agent creation
    config = AgentConfig(agent_id="rapid_test", agent_type="test", specialization="sentry")
    agents = [await SentryAgent.pooled(config) for _ in range(10)]
    assert all(agents), "Rapid agent creation failed"
    print("✅ Rapid agent creation passed.")

    # Concurrent tasks
    async def run_task(agent, i):
        task = Task(
            task_id=f"concurrent_{i}",
            task_type="invalid_task_type",
            agent_id=agent.config.agent_id,
            task_data={},
            status=None,
            created_at=datetime.utcnow(),
            started_at=None,
            completed_at=None,
            result=None,
            error_message=None,
            priority=None,
        )
        return await agent.process_task(task)
    agent = await SentryAgent.pooled(config)
    results = await asyncio.gather(*(run_task(agent, i) for i in range(5)))
    assert all(not r.get("success", True) for r in results), "Concurrent task error handling failed"
    print("✅ Concurrent task error handling passed.")

    # Missing config (simulate by passing None)
    try:
        await SentryAgent.pooled(None)
    except Exception as e:
        print(f"✅ Missing config edge case handled: {e}")


def print_test_summary():
    print("\n=== AGNO AGENT TEST SUITE COMPLETE ===\n")
    print("All core agents, pooling, config, and error handling tested.")

# Remove or comment out legacy/duplicate test functions below
# async def test_agno_integration():
#     ...
# (and any other old test functions)
