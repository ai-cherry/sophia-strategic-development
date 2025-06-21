"""Hugging Face Agent for Sophia AI.

Handles interaction with the Hugging Face ecosystem via the HuggingFaceIntegration.
"""

import logging
import re

from backend.agents.core.base_agent import AgentConfig, BaseAgent, Task, TaskResult
from backend.integrations.huggingface_integration import HuggingFaceIntegration

logger = logging.getLogger(__name__)


class HuggingFaceAgent(BaseAgent):
    """An agent that specializes in using the Hugging Face Hub to find models,.

            datasets, papers, and run Spaces.
    """

    def __init__(self, config: AgentConfig, hf_integration: HuggingFaceIntegration):
        super().__init__(config)
        self.hf_integration = hf_integration

    async def execute_task(self, task: Task) -> TaskResult:
        """Executes a task by interpreting the natural language command and calling.

                        the appropriate method on the HuggingFaceIntegration.

                        Args:
                            task: The task to execute.

                        Returns:
                            A TaskResult with the status and formatted output.
        """
        command = task.command.lower()

        try:
            if "search" in command and "model" in command:
                query = self._extract_query(command, "model")
                models = await self.hf_integration.search_models(query)
                output = self._format_model_results(models)
                return TaskResult(status="success", output=output)

            elif "paper" in command or "arxiv" in command:
                paper_id = self._extract_paper_id(command)
                if not paper_id:
                    return TaskResult(
                        status="error",
                        output="Could not find a valid paper ID (e.g., '2404.19756') in the command.",
                    )

                details = await self.hf_integration.get_paper_details(paper_id)
                output = self._format_paper_results(details)
                return TaskResult(status="success", output=output)

            # Add more command interpretations here (e.g., for running spaces)

            else:
                return TaskResult(
                    status="error",
                    output=f"Unknown Hugging Face command: {task.command}",
                )

        except Exception as e:
            logger.error(
                f"Error executing Hugging Face task '{task.command}': {e}",
                exc_info=True,
            )
            return TaskResult(status="error", output={"error": str(e)})

    def _extract_query(self, command: str, keyword: str) -> str:
        """A simple helper to extract the search query from a command."""

        try:
            # e.g., "search for models about text generation" -> "text generation"
            return command.split("about")[-1].strip()
        except Exception:
            return command  # fallback

    def _extract_paper_id(self, command: str) -> str:
        """Finds an arXiv-style ID in the command string."""match = re.search(r"\d{4}\.\d{5}", command).

        return match.group(0) if match else None

    def _format_model_results(self, models: list) -> str:
        """Formats a list of models into a readable string."""if not models or "error" in models[0]:.

            return "Could not find any matching models."

        lines = ["Found the following models on Hugging Face:"]
        for model in models[:5]:  # show top 5
            lines.append(
                f"- **{model.get('id')}**: {model.get('pipeline_tag', 'N/A')} | Downloads: {model.get('downloads', 0)}"
            )
        return "\n".join(lines)

    def _format_paper_results(self, paper: dict) -> str:
        """Formats paper details into a readable string."""
        if not paper or paper.get("error"):
            return "Could not retrieve details for that paper."

        lines = [
            f"**{paper.get('title')}**",
            f"Authors: {', '.join(paper.get('authors', []))}",
            f"Published: {paper.get('published', 'N/A')}",
            f"URL: {paper.get('url')}",
            "\n**Abstract:**",
            paper.get("summary", "No abstract available."),
        ]
        return "\n".join(lines)
