from __future__ import annotations

import logging
import operator
from collections.abc import Sequence
from typing import Annotated, TypedDict

from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages

from backend.orchestration.langgraph_mcp_orchestrator import (
    LangGraphMCPOrchestrator as ToolOrchestrator,
)
from backend.workflows.langgraph_agent_orchestration import (
    LangGraphWorkflowOrchestrator as DealAnalysisOrchestrator,
)

logger = logging.getLogger(__name__)


class SupervisorState(TypedDict):
    messages: Annotated[Sequence[dict], operator.add]


class SupervisorAgent:
    """
    A meta-orchestrator that routes tasks to specialized LangGraph workflows.
    """

    def __init__(self):
        self.deal_analysis_orchestrator = DealAnalysisOrchestrator()
        self.tool_orchestrator = ToolOrchestrator()

        workflow = StateGraph(SupervisorState)
        workflow.add_node("supervisor", self.supervisor_node)

        # Define the routing logic
        workflow.add_conditional_edges(
            "supervisor",
            self.route_to_specialist,
            {
                "deal_analysis": "deal_analysis_orchestrator",
                "tool_use": "tool_orchestrator",
                "end": END,
            },
        )

        # Add the specialist nodes
        workflow.add_node("deal_analysis_orchestrator", self.run_deal_analysis)
        workflow.add_node("tool_orchestrator", self.run_tool_orchestrator)

        # Connect specialist nodes back to the supervisor or end
        workflow.add_edge("deal_analysis_orchestrator", END)  # Simplified for now
        workflow.add_edge("tool_orchestrator", END)  # Simplified for now

        workflow.set_entry_point("supervisor")
        self.graph = workflow.compile()
        logger.info("✅ SupervisorAgent workflow compiled.")

    def route_to_specialist(self, state: SupervisorState):
        """Routing function to decide which specialist to use."""
        last_message = state["messages"][-1]
        content = last_message.get("content", "").lower()

        if "deal" in content or "gong" in content or "sales" in content:
            logger.info("Routing to Deal Analysis Orchestrator")
            return "deal_analysis"
        elif "tool" in content or "mcp" in content or "remember" in content:
            logger.info("Routing to Tool Orchestrator")
            return "tool_use"
        else:
            logger.info("No specific specialist found. Ending conversation.")
            return "end"

    async def run_deal_analysis(self, state: SupervisorState):
        """Node to run the deal analysis workflow."""
        last_message = state["messages"][-1]
        deal_id = "some_deal_id"  # Placeholder: In a real scenario, this would be extracted from the message
        result = await self.deal_analysis_orchestrator.analyze_deal(deal_id=deal_id)
        return {
            "messages": add_messages([{"role": "assistant", "content": str(result)}])
        }

    async def run_tool_orchestrator(self, state: SupervisorState):
        """Node to run the tool orchestrator."""
        last_message = state["messages"][-1]
        request = {"message": last_message.get("content"), "context": "mcp_tool_use"}
        result = await self.tool_orchestrator.route_request(request)
        return {
            "messages": add_messages([{"role": "assistant", "content": str(result)}])
        }

    async def supervisor_node(self, state: SupervisorState):
        # This node can be enhanced to provide more sophisticated routing logic
        # or to synthesize results from multiple specialists.
        # For now, it's a pass-through to the routing function.
        return state

    async def invoke(self, query: str):
        """Invoke the supervisor with a user query."""
        initial_state: SupervisorState = {
            "messages": [{"role": "user", "content": query}]
        }
        async for event in self.graph.astream(initial_state):
            for v in event.values():
                print(v)
        return "Workflow finished."


async def main():
    """Main function to test the supervisor."""
    supervisor = SupervisorAgent()
    # Example queries
    await supervisor.invoke("Analyze the latest deal for ACME Corp.")
    await supervisor.invoke("Please remember to use the codacy tool to check my code.")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
