import asyncio
import logging
import uuid
from typing import List, Dict, Any

from ..core.base_agent import BaseAgent, AgentConfig, AgentCapability, Task, create_agent_response
from ..core.agent_router import agent_router # Import the global router

logger = logging.getLogger(__name__)

class ExecutiveAgent(BaseAgent):
    """
    Serves as the CEO's dedicated interface for strategic intelligence and orchestration.
    """
    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.agent_router = agent_router

    async def get_capabilities(self) -> List[AgentCapability]:
        return [
            AgentCapability(
                name="strategic_synthesis_query",
                description="Performs a complex strategic analysis by synthesizing insights from multiple specialized agents.",
                input_types=["strategic_question"],
                output_types=["executive_briefing"],
                estimated_duration=300.0
            )
        ]

    async def _decompose_strategic_question(self, question: str) -> List[Task]:
        """
        Uses an LLM to decompose a high-level strategic question into a sequence of tasks for specialized agents.
        This is a placeholder for a more advanced implementation.
        """
        logger.info(f"Decomposing strategic question: {question}")
        # In a real implementation, this would involve an LLM call.
        # For now, we'll use a simple keyword-based mapping.
        tasks = []
        question_lower = question.lower()

        if "deal loss" in question_lower or "why did we lose" in question_lower:
             # Example decomposition for a deal loss analysis
             tasks.append(Task(task_id=f"task_{uuid.uuid4().hex}", task_type="analyze_gong_call", agent_id="sales_coach", task_data={"gong_call_id": "some_call_id"}))
             tasks.append(Task(task_id=f"task_{uuid.uuid4().hex}", task_type="calculate_health_score", agent_id="client_health", task_data={"client_id": "some_client_id"}))
             tasks.append(Task(task_id=f"task_{uuid.uuid4().hex}", task_type="generate_competitive_analysis", agent_id="marketing", task_data={"competitor_name": "Competitor X"}))
        
        return tasks


    async def process_task(self, task: Task) -> Dict[str, Any]:
        """
        Processes a strategic query by decomposing it, routing sub-tasks to specialized agents,
        and synthesizing the results into an executive briefing.
        """
        if task.task_type == "strategic_synthesis_query":
            strategic_question = task.task_data.get("strategic_question")
            if not strategic_question:
                return await create_agent_response(False, error="strategic_question is required.")

            # 1. Decompose the strategic question into sub-tasks
            sub_tasks = await self._decompose_strategic_question(strategic_question)
            if not sub_tasks:
                 return await create_agent_response(False, error="Could not decompose the strategic question.")

            # 2. Route sub-tasks to specialized agents and gather results
            # This is a simplified model. A real implementation would use the Redis pub/sub
            # system to dispatch tasks and wait for results asynchronously.
            results = []
            for sub_task in sub_tasks:
                handler = self.agent_router.agents[sub_task.agent_id].handler
                result = await handler(sub_task)
                results.append(result)

            # 3. Synthesize the results into a coherent narrative
            # This would involve a final LLM call to generate the briefing.
            briefing = {
                "strategic_question": strategic_question,
                "synthesis_summary": "Placeholder: Based on the analysis, the deal was lost due to a combination of high price sensitivity and a new feature launch by Competitor X.",
                "supporting_data": results
            }

            return await create_agent_response(True, data=briefing)
        else:
            return await create_agent_response(False, error=f"Unknown task type: {task.task_type}") 