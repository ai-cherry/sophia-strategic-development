"""Infrastructure as Code (IaC) Manager Agent for Sophia AI.

Handles the generation and deployment of infrastructure configurations via natural language.
"""

import asyncio
import json
import logging

from backend.agents.core.agent_router import agent_router  # To call other agents
from backend.agents.core.base_agent import AgentConfig, BaseAgent, Task, TaskResult
from backend.agents.tools.filesystem_tools import filesystem_tools
from backend.integrations.portkey_client import PortkeyClient

logger = logging.getLogger(__name__)


class IaCManagerAgent(BaseAgent):
    """An agent that specializes in managing the project's Infrastructure as Code.

            It can understand requests to create or modify infrastructure, generate the
            necessary Pulumi code, and orchestrate its deployment.
    """

    def __init__(self, config: AgentConfig, portkey_client: PortkeyClient):
        super().__init__(config)
        self.portkey = portkey_client
        # The agent's toolbox maps plan steps to actual, runnable functions.
        self.toolbox = {
            "filesystem.read": filesystem_tools.read_file,
            "filesystem.write": filesystem_tools.write_to_file,
            "brain.generate_code": self.call_brain_for_code,
            "pulumi.deploy": self.call_pulumi_agent,
        }

    async def execute_task(self, task: Task) -> TaskResult:
        """Executes an IaC management task by generating and then executing a plan."""

        logger.info(f"IaCManagerAgent received task: {task.command}")

        # 1. Generate the plan
        system_prompt = self._create_iac_planning_prompt(task.command)
        plan_response = await self.portkey.llm_call(system_prompt)
        plan_str = (
            plan_response.get("choices", [{}])[0].get("message", {}).get("content", "")
        )

        try:
            plan = json.loads(plan_str.strip())
            logger.info(f"--- IaC Management Plan ---\n{json.dumps(plan, indent=2)}")
        except json.JSONDecodeError:
            return TaskResult(
                status="error", output=f"Failed to parse LLM plan as JSON: {plan_str}"
            )

        # 2. Execute the plan
        execution_context = {}
        execution_log = []
        for step in plan:
            tool_name = step.get("tool")
            params = step.get("parameters", {})

            if tool_name not in self.toolbox:
                msg = f"Plan contains unknown tool: {tool_name}"
                logger.error(msg)
                execution_log.append(f"ERROR: {msg}")
                break

            # Substitute parameters from context (e.g., use output of step 1 in step 2)
            for key, value in params.items():
                if isinstance(value, str) and value.startswith("$"):
                    ref_key = value[1:]
                    if ref_key in execution_context:
                        params[key] = execution_context[ref_key]
                    else:
                        msg = f"Could not find referenced context variable '{ref_key}' for step '{step.get('step')}'"
                        logger.error(msg)
                        execution_log.append(f"ERROR: {msg}")
                        return TaskResult(
                            status="error", output={"execution_log": execution_log}
                        )

            # Execute the tool
            logger.info(
                f"Executing step {step.get('step')}: {tool_name} with params: {params}"
            )
            tool_function = self.toolbox[tool_name]

            try:
                # Await if the function is a coroutine
                if asyncio.iscoroutinefunction(tool_function):
                    result = await tool_function(**params)
                else:  # Handle synchronous tools like those in filesystem_tools
                    result = tool_function(**params)

                execution_log.append(f"Step {step.get('step')} ({tool_name}): SUCCESS")

                # Store output in context if requested
                if step.get("output_variable"):
                    execution_context[step.get("output_variable")] = result

            except Exception as e:
                msg = f"Step {step.get('step')} ({tool_name}) FAILED: {e}"
                logger.error(msg, exc_info=True)
                execution_log.append(f"ERROR: {msg}")
                return TaskResult(
                    status="error", output={"execution_log": execution_log}
                )

        return TaskResult(status="success", output={"execution_log": execution_log})

    async def call_brain_for_code(self, prompt: str) -> str:
        """Helper to call the BrainAgent's code generation tool."""brain_task = Task(command="generate_code", parameters={"prompt": prompt}).

        result = await agent_router.route_command_to_agent("brain_agent", brain_task)
        if result and result.status == "success":
            return result.output
        return f"Error: Could not generate code. {result.output}"

    async def call_pulumi_agent(self, stack: str, operation: str = "deploy") -> str:
        """Helper to call the PulumiAgent."""pulumi_task = Task(command=f"{operation} stack {stack}", parameters={}).

        result = await agent_router.route_command_to_agent("pulumi_agent", pulumi_task)
        return result.output if result else "Error: Pulumi agent call failed."

    def _create_iac_planning_prompt(self, command: str) -> str:
        """Creates the prompt for the LLM to generate an IaC plan."""return f"""You are an expert Site Reliability Engineer (SRE) and Pulumi developer.

        Your task is to take a natural language request and convert it into a concrete,
        step-by-step plan for modifying our Infrastructure as Code.

        Available Tools:
        - filesystem.read(file_path: str): Reads a file from the codebase.
        - filesystem.write(file_path: str, content: str): Writes content to a file.
        - pulumi_agent.deploy(stack: str): Triggers a deployment of a Pulumi stack.
        - brain.generate_code(prompt: str): Uses an LLM to generate Python code.

        User Request: "{command}"

        Based on the request, generate a JSON plan outlining the steps to take.
        For example, for "create a new Airbyte connection for HubSpot", the plan might be:
        [
            {{"step": 1, "tool": "filesystem.read", "parameters": {{"file_path": "infrastructure/airbyte.py"}}}},
            {{"step": 2, "tool": "brain.generate_code", "parameters": {{"prompt": "Based on the content of infrastructure/airbyte.py, generate a new Pulumi component for an Airbyte connection named 'hubspot_contacts'..."}}}},
            {{"step": 3, "tool": "filesystem.write", "parameters": {{"file_path": "infrastructure/airbyte.py", "content": "$step2_output"}}}},
            {{"step": 4, "tool": "pulumi_agent.deploy", "parameters": {{"stack": "dev"}}}}
        ]
        """
