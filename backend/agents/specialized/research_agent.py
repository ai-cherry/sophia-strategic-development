"""Specialized Research Agent for Sophia AI."""

import json
import logging

from agno import Agent, state

from backend.agents.core.base_agent import AgentConfig, BaseAgent, Task, TaskResult
from backend.integrations.portkey_client import PortkeyClient
from backend.mcp.mcp_client import MCPClient

logger = logging.getLogger(__name__)


class ResearchAgent(Agent, BaseAgent):
    """An agent specialized in conducting web research on a given topic.
    It breaks down a topic, executes web searches, and synthesizes the results.
    """

    def __init__(self, config: AgentConfig):
        Agent.__init__(self)
        BaseAgent.__init__(self, config)
        self.mcp_client = MCPClient(
            "http://localhost:8090"
        )  # Assumes gateway is running
        self.portkey_client = PortkeyClient()
        self.research_data = {}

    async def initialize(self):
        await self.mcp_client.connect()

    @state(initial=True)
    async def deconstruct_topic(self, topic: str):
        """Breaks a broad topic into specific, searchable queries using an LLM."""
        logger.info(f"[State: DECONSTRUCT_TOPIC] for topic: {topic}")
        self.research_data = {"original_topic": topic}

        system_prompt = """You are a master research analyst. Your task is to take a high-level research topic and break it down into a series of 3-5 specific, effective Google search queries. Return ONLY a JSON-formatted list of strings.

Example Topic: "The impact of AI on the property management industry"
Example Output:
[
    "AI applications in property management tenant screening",
    "automation in multifamily rent collection using AI",
    "predictive maintenance AI for apartment buildings",
    "top AI-powered property management software 2024",
    "future of AI in real estate market analysis"
]
"""

        llm_response = await self.portkey_client.llm_call(
            prompt=f"Research Topic: {topic}", system_prompt=system_prompt
        )

        try:
            # Extract and parse the JSON list from the LLM response
            content = (
                llm_response.get("choices", [{}])[0]
                .get("message", {})
                .get("content", "[]")
            )
            queries = json.loads(content)
            if not isinstance(queries, list) or not all(
                isinstance(q, str) for q in queries
            ):
                raise ValueError("LLM did not return a valid list of strings.")
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(
                f"Failed to parse LLM response into search queries: {e}. Falling back to simple query."
            )
            queries = [topic]  # Fallback to using the original topic as the query

        self.research_data["search_queries"] = queries
        logger.info(f"Generated search queries via LLM: {queries}")
        return self.execute_search

    @state
    async def execute_search(self):
        """Calls the Apify MCP server to perform web searches."""
        queries = self.research_data.get("search_queries", [])
        logger.info(f"[State: EXECUTE_SEARCH] for {len(queries)} queries.")

        search_result = await self.mcp_client.call_tool(
            "apify",
            "google_search_and_scrape",
            search_queries=queries,
            num_results=3,  # Get top 3 results for each query
        )

        self.research_data["scraped_content"] = search_result.get("data", [])
        return self.synthesize_findings

    @state
    async def synthesize_findings(self):
        """Summarizes all the scraped content into a single brief."""
        logger.info("[State: SYNTHESIZE_FINDINGS]")

        # In a real implementation, we would pass all the scraped text to an LLM
        # with a prompt like "Summarize the following research into a coherent brief..."

        # For now, we'll just concatenate the results.
        all_text = "\n\n---\n\n".join(
            str(item) for item in self.research_data.get("scraped_content", [])
        )

        summary = f"**Research Brief on: {self.research_data['original_topic']}**\n\n"
        summary += f"This is a synthesized summary from {len(self.research_data.get('scraped_content', []))} web pages.\n\n"
        summary += all_text

        self.research_data["final_brief"] = summary
        return self.done

    @state(terminal=True)
    def done(self):
        """Terminal state, returns the final research brief."""
        logger.info("[State: DONE]")
        return TaskResult(
            status="success",
            output=self.research_data.get("final_brief", "No brief generated."),
        )

    async def execute_task(self, task: Task) -> TaskResult:
        """Runs the research state machine."""
        topic = task.command
        try:
            await self.initialize()
            final_result = await self.start(
                self.deconstruct_topic, kwargs={"topic": topic}
            )
            return final_result
        except Exception as e:
            logger.error(
                f"Error executing research task for topic '{topic}': {e}", exc_info=True
            )
            return TaskResult(status="error", output={"error": str(e)})
        finally:
            await self.mcp_client.close()
