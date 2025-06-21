import asyncio
import json
import logging
import uuid
from typing import Any, Dict, List

import openai

from ...core.config_manager import get_secret
from ..core.agent_router import agent_router
from ..core.base_agent import AgentConfig, BaseAgent, Task, create_agent_response
from backend.agents.core.agno_performance_optimizer import AgnoPerformanceOptimizer

logger = logging.getLogger(__name__)


class ExecutiveAgent(BaseAgent):
    """Serves as the CEO's dedicated interface for strategic intelligence and orchestration. Integrated with AgnoPerformanceOptimizer."""

    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.agent_router = agent_router
        self.openai_client = None

    @classmethod
    async def pooled(cls, config: AgentConfig) -> 'ExecutiveAgent':
        """Get a pooled or new instance using AgnoPerformanceOptimizer."""
        optimizer = AgnoPerformanceOptimizer()
        await optimizer.register_agent_class('executive', cls)
        agent = await optimizer.get_or_create_agent('executive', {'config': config})
        logger.info(f"[AgnoPerformanceOptimizer] Provided ExecutiveAgent instance (pooled or new)")
        return agent

    async def _initialize_llm(self):
        if not self.openai_client:
            try:
                api_key = await get_secret("api_key", "openai")
                self.openai_client = openai.AsyncOpenAI(api_key=api_key)
                logger.info("OpenAI client initialized for ExecutiveAgent.")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")

    async def _get_deal_info_from_crm(self, deal_name: str) -> Dict[str, Any]:
        """Mocks a CRM lookup to get IDs associated with a deal."""logger.info(f"Mock CRM lookup for deal: {deal_name}").

        # In a real system, this would query your CRM (e.g., HubSpot)
        # to find the company, associated calls, etc.
        return {
            "deal_name": deal_name,
            "client_id": "client_abc_123",  # Placeholder
            "primary_competitor": "CompetitorX",  # Placeholder
            "gong_call_ids": ["gong_call_1", "gong_call_2"],  # Placeholder
        }

    async def _decompose_strategic_question(self, question: str) -> List[Task]:
        """Decomposes a high-level strategic question into a sequence of tasks."""logger.info(f"Decomposing strategic question: {question}").

        tasks = []
        question_lower = question.lower()

        # Improved decomposition for Deal Loss Analysis
        if "deal loss" in question_lower or "why did we lose" in question_lower:
            # This is still simplified. A real system might use an LLM to parse the deal name.
            deal_name = "the Acme deal"  # Placeholder
            deal_info = await self._get_deal_info_from_crm(deal_name)

            # Task for Client Health Agent
            tasks.append(
                Task(
                    task_id=f"task_{uuid.uuid4().hex}",
                    task_type="calculate_health_score",
                    agent_id="client_health",
                    task_data={"client_id": deal_info["client_id"]},
                )
            )

            # Task for Marketing Agent (competitive analysis)
            tasks.append(
                Task(
                    task_id=f"task_{uuid.uuid4().hex}",
                    task_type="generate_competitive_analysis",
                    agent_id="marketing",
                    task_data={"competitor_name": deal_info["primary_competitor"]},
                )
            )

            # Tasks for Sales Coach Agent (one for each call)
            for call_id in deal_info["gong_call_ids"]:
                tasks.append(
                    Task(
                        task_id=f"task_{uuid.uuid4().hex}",
                        task_type="analyze_gong_call",
                        agent_id="sales_coach",
                        task_data={"gong_call_id": call_id},
                    )
                )

        return tasks

    async def _synthesize_results_with_llm(
        self, question: str, results: List[Dict]
    ) -> str:
        """Uses an LLM to synthesize agent results into a narrative briefing."""if not self.openai_client:.

            await self._initialize_llm()
        if not self.openai_client:
            return "Error: LLM client not available for synthesis."

        # Create a detailed prompt with all the collected context
        prompt = f"""
        Executive Briefing Request:
        The CEO has asked the following strategic question: "{question}"

        Sophia's specialized AI agents have gathered the following intelligence:
        ---
        """for res in results:.

                            if res.get("success"):
                                prompt += f"\n**Source Agent: {res.get('agent_id', 'Unknown')}**\n"
                                prompt += f"```json\n{json.dumps(res.get('data'), indent=2)}\n```\n---"

                        prompt +=
        """
        Your Task:
        As Sophia's central intelligence, synthesize all the provided data into a concise, insightful, and actionable executive briefing.
        Structure your response with the following sections:
        1.  **Top-Line Summary:** A 2-3 sentence answer to the CEO's question.
        2.  **Key Contributing Factors:** A bulleted list of the primary reasons for the outcome.
        3.  **Supporting Evidence:** A brief summary of the key data points from the agent reports that support your analysis.
        4.  **Strategic Recommendations:** A numbered list of 2-3 actionable recommendations for the executive team.
        """try:.

                            response = await self.openai_client.chat.completions.create(
                                model="gpt-4-turbo",
                                messages=[{"role": "user", "content": prompt}],
                                temperature=0.5,
                            )
                            return response.choices[0].message.content
                        except Exception as e:
                            logger.error(f"LLM synthesis failed: {e}")
                            return f"Error during synthesis: {e}"

                    async def process_task(self, task: Task) -> Dict[str, Any]:
        """Processes a strategic query by decomposing it, routing sub-tasks, and synthesizing the results."""
        if task.task_type == "strategic_synthesis_query":
            strategic_question = task.task_data.get("strategic_question")
            if not strategic_question:
                return await create_agent_response(
                    False, error="strategic_question is required."
                )

            sub_tasks = await self._decompose_strategic_question(strategic_question)
            if not sub_tasks:
                return await create_agent_response(
                    False, error="Could not decompose the strategic question."
                )

            # Concurrently execute all sub-tasks
            task_handlers = []
            for sub_task in sub_tasks:
                handler = self.agent_router.agents[sub_task.agent_id].handler
                task_handlers.append(handler(sub_task))

            results = await asyncio.gather(*task_handlers, return_exceptions=True)

            # Synthesize the results into a coherent narrative
            final_briefing = await self._synthesize_results_with_llm(
                strategic_question, results
            )

            # Add the raw data for drill-down capabilities in the UI
            response_data = {
                "executive_briefing": final_briefing,
                "supporting_data": results,
            }

            return await create_agent_response(True, data=response_data)
        else:
            return await create_agent_response(
                False, error=f"Unknown task type: {task.task_type}"
            )
