"""
Tests for strategic plan execution.
"""

import sys
from pathlib import Path

import pytest

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from execute_strategic_plan import StrategicPlanExecutor


class TestStrategicPlanExecution:
    """Test strategic plan execution."""

    def test_executor_initialization(self):
        """Test that executor initializes correctly."""
        executor = StrategicPlanExecutor()
        assert executor.base_dir.exists()
        assert "execution_start" in executor.results
        assert executor.results["deployment_status"] == "pending"

    def test_results_structure(self):
        """Test that results have correct structure."""
        executor = StrategicPlanExecutor()
        required_keys = [
            "execution_start",
            "phases_completed",
            "issues_fixed",
            "improvements_made",
            "tests_passed",
            "deployment_status",
        ]

        for key in required_keys:
            assert key in executor.results

    @pytest.mark.asyncio
    async def test_phase_1_execution(self):
        """Test Phase 1 execution."""
        executor = StrategicPlanExecutor()
        await executor.phase_1_critical_fixes()
        assert "phase_1_critical_fixes" in executor.results["phases_completed"]
