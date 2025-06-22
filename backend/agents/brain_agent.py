"""Brain Agent for Sophia AI.

The central reasoning and planning agent for the Sophia AI system.
"""

import json
import logging

from backend.agents.core.base_agent import AgentConfig, BaseAgent, Task, TaskResult
from backend.integrations.portkey_client import PortkeyClient
from backend.integrations.snowflake_integration import snowflake_integration

logger = logging.getLogger(__name__)


class BrainAgent(BaseAgent):
    """The BrainAgent is the master orchestrator. It takes complex, open-ended.

            tasks and breaks them down into a sequence of steps. It uses other agents
            and integrations as tools to accomplish these steps. Its primary tool for
            reasoning and planning is the Portkey LLM Gateway.
    """

    def __init__(self, config: AgentConfig, portkey_client: PortkeyClient):
        super().__init__(config)
        self.portkey = portkey_client
        self.tools = {"snowflake": snowflake_integration}

    async def execute_task(self, task: Task) -> TaskResult:
        """Executes a complex task by using an LLM to generate a plan and then.

                        executing that plan.

                        Args:
                            task: The high-level task to execute.

                        Returns:
                            A TaskResult with the final, synthesized answer.
        """
        logger.info(f"BrainAgent received task: {task.command}")

        # Check if this is a direct tool call to the brain, e.g., for code generation
        if task.command == "generate_code":
            return await self.generate_code(task.parameters.get("prompt", ""))

        try:
            # 1. Generate a plan (which may include a SQL query)
            system_prompt = self._create_planning_prompt()
            plan_request = f"Based on the available tools, create a step-by-step plan to answer the following user request. Prioritize using the snowflake.query tool if the request involves specific data, metrics, or analytics. User request: '{task.command}'"

            plan_response = await self.portkey.llm_call(
                plan_request, system_prompt=system_prompt
            )
            plan_str = (
                plan_response.get("choices", [{}])[0]
                .get("message", {})
                .get("content", "")
            )
            logger.info(f"BrainAgent generated plan:\n{plan_str}")

            # 2. Execute the plan
            # This is a simplified execution loop. A real one would handle dependencies.
            try:
                # Naive assumption: plan is a JSON object with a 'tool' and 'parameters'
                plan = json.loads(plan_str.strip())
                if plan.get("tool") == "snowflake.query":
                    sql_query = plan["parameters"]["sql"]
                    logger.info(f"BrainAgent is executing SQL: {sql_query}")

                    # Execute query using the Snowflake integration
                    query_results = await self.tools["snowflake"].execute_query(
                        sql_query
                    )

                    # 3. Summarize the results
                    summary_prompt = f"""You are Sophia, an AI data analyst for Pay Ready.

                    You have just executed the SQL query: '{sql_query}'
                    And received the following data: {json.dumps(query_results, indent=2)}

                    Based on this data, provide a clear, natural language answer to the original user request: '{task.command}'
                    """
                    summary_response = await self.portkey.llm_call(summary_prompt)

                    final_answer = (
                        summary_response.get("choices", [{}])[0]
                        .get("message", {})
                        .get("content", "")
                    )
                    return TaskResult(status="success", output=final_answer)

            except (json.JSONDecodeError, KeyError):
                logger.warning(
                    "Could not parse a structured plan. Falling back to direct answer."
                )
                # Fallback if the plan isn't structured as expected
                pass

            except Exception as e:
                logger.error(
                    f"Error executing brain task '{task.command}': {e}", exc_info=True
                )
                return TaskResult(status="error", output={"error": str(e)})

        except Exception as e:
            logger.error(
                f"Error executing brain task '{task.command}': {e}", exc_info=True
            )
            return TaskResult(status="error", output={"error": str(e)})

    async def generate_code(self, prompt: str) -> TaskResult:
        """Uses the LLM via Portkey to generate a block of code based on a prompt.

        Args:
            prompt: A detailed prompt describing the desired code.

        Returns:
            A TaskResult containing the generated code.
        """
        logger.info("BrainAgent received code generation request.")

        system_prompt = """You are an expert Python and Pulumi developer.

        Your sole task is to generate clean, correct, and readable code based on the user's prompt.
        Do NOT add any explanatory text, conversational filler, or markdown code blocks (```python ... ```).
        Your output must be ONLY the raw code itself.
        """
        try:
            code_response = await self.portkey.llm_call(
                prompt, system_prompt=system_prompt
            )
            generated_code = (
                code_response.get("choices", [{}])[0]
                .get("message", {})
                .get("content", "")
            )

            # Clean up the response to ensure it's just code
            if "```python" in generated_code:
                generated_code = generated_code.split("```python\n")[1].split("```")[0]
            elif "```" in generated_code:
                generated_code = generated_code.replace("```", "")

            return TaskResult(status="success", output=generated_code.strip())
        except Exception as e:
            logger.error(f"Error during code generation: {e}", exc_info=True)
            return TaskResult(status="error", output={"error": str(e)})

    def _create_planning_prompt(self) -> str:
        """Creates the system prompt for the planning LLM call."""
        # This would be expanded to include details about all available tools.
        prompt = """You are a master planner and orchestrator AI.
        Your job is to take a user's request and create a JSON object that represents the single best tool call to answer the request.

        Available Tools:
        - snowflake.query(sql: str): Executes a SQL query against the Pay Ready data warehouse. Use this for any questions about specific data, metrics, revenue, clients, etc.

        Based on the user's request, provide a JSON object with two keys: "tool" and "parameters".
        Example Request: "What were our top 5 clients by revenue last quarter?"
        Example JSON Output:
        {
            "tool": "snowflake.query",
            "parameters": {
                "sql": "SELECT client_name, SUM(revenue) as total_revenue FROM deals WHERE quarter = 'Q3-2024' GROUP BY client_name ORDER BY total_revenue DESC LIMIT 5"
            }
        }
        """
        return prompt
