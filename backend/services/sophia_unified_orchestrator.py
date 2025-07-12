"""
Sophia Unified Orchestrator - Multi-Hop Reasoning Engine
Because single-shot prompts are for amateurs
"""

import sys
from pathlib import Path

# Add project root to path for consistent imports
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

import logging
from typing import Dict, Any, List
from enum import Enum
import json
from datetime import datetime
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, END

import backend.utils.path_utils  # noqa: F401
from backend.services.unified_memory_service_v2 import UnifiedMemoryServiceV2
from backend.services.portkey_gateway import PortkeyGateway
from backend.services.mcp_orchestration_service import MCPOrchestrationService

logger = logging.getLogger(__name__)


class IntentComplexity(Enum):
    SIMPLE = "simple"  # Single MCP call
    MODERATE = "moderate"  # 2-3 MCP calls
    COMPLEX = "complex"  # Multi-hop reasoning required
    NUCLEAR = "nuclear"  # CEO asking about everything


class OrchestratorState(TypedDict):
    """The state of the reasoning graph."""

    query: str
    user_id: str
    complexity: IntentComplexity
    required_servers: List[str]
    sub_tasks: List[Dict[str, Any]]
    task_dependencies: Dict[str, List[str]]
    mcp_results: Dict[str, Any]
    synthesized_response: str
    synthesis_metadata: Dict[str, Any]
    quality: str
    critique_notes: List[str]
    iteration_count: int
    final_response: str
    personalization_applied: bool
    execution_errors: List[str]
    snark: str
    current_task_index: int
    routing_path: str


class SophiaUnifiedOrchestrator:
    """
    Multi-hop reasoning orchestrator that breaks down complex queries
    into sub-tasks, executes them across MCP servers, and synthesizes
    results with self-critique loops. No more one-shot bullshit.
    """

    def __init__(self):
        self.memory = UnifiedMemoryServiceV2()
        self.portkey = PortkeyGateway()
        self.mcp_orchestrator = MCPOrchestrationService()

        # Build the multi-hop graph
        self.graph = self._build_reasoning_graph()
        self.compiled_graph = self.graph.compile()

    def _build_reasoning_graph(self) -> StateGraph:
        """Build the LangGraph for multi-hop reasoning"""
        graph = StateGraph(OrchestratorState)

        # Add nodes for multi-hop reasoning
        graph.add_node("analyze_intent", self.analyze_intent)
        graph.add_node("decompose", self.decompose_intent)
        graph.add_node("execute_mcp", self.execute_mcp_chain)
        graph.add_node("fuse", self.fuse_results)
        graph.add_node("critique", self.self_critique)
        graph.add_node("enhance_with_rag", self.enhance_with_rag)
        graph.add_node("enhance_with_memory", self.enhance_with_memory)

        # Define graph flow
        graph.set_entry_point("analyze_intent")
        graph.add_edge("analyze_intent", "decompose")
        graph.add_conditional_edges(
            "decompose",
            self.should_execute_directly,
            {True: "execute_mcp", False: "decompose"},
        )

        graph.add_edge("execute_mcp", "fuse")
        graph.add_edge("fuse", "critique")

        # Self-critique and enhancement loop
        graph.add_conditional_edges(
            "critique",
            self.critique_quality,
            {
                "perfect": "enhance_with_memory",
                "needs_data": "enhance_with_rag",
                "needs_refining": "fuse",
                "total_failure": "decompose",
            },
        )

        graph.add_edge("enhance_with_rag", "fuse")  # Re-fuse after getting more data
        graph.add_edge("enhance_with_memory", END)

        return graph

    async def analyze_intent(self, state: OrchestratorState) -> OrchestratorState:
        """Analyze query complexity and intent"""
        query = state["query"]

        # Use Portkey to analyze complexity
        analysis_prompt = f"""Analyze this query and determine:
        1. Complexity: simple/moderate/complex/nuclear
        2. Required MCP servers
        3. Sub-tasks needed
        
        Query: {query}
        
        Be brutal - if it's a dumb question, say so.
        """

        response = await self.portkey.completions.create(
            model="claude-3-5-sonnet-20240620",
            messages=[{"role": "user", "content": analysis_prompt}],
            temperature=0.3,
        )

        # Parse response and determine complexity
        analysis = json.loads(response.choices[0].message.content)

        state["complexity"] = IntentComplexity(analysis["complexity"])
        state["required_servers"] = analysis["required_servers"]
        state["sub_tasks"] = analysis.get("sub_tasks", [])
        state["snark"] = analysis.get("snark_comment", "")

        return state

    async def decompose_intent(self, state: OrchestratorState) -> OrchestratorState:
        """Break complex queries into sub-tasks"""
        query = state["query"]
        complexity = state["complexity"]

        if complexity == IntentComplexity.NUCLEAR:
            # CEO wants everything? Give them everything
            decompose_prompt = f"""The CEO is asking a nuclear-level query. Break it down into EVERY possible sub-task.
            
            Query: {query}
            
            Create a dependency graph of sub-tasks. Be exhaustive - miss nothing.
            Format: {{"tasks": [...], "dependencies": {{...}}}}
            """
        else:
            decompose_prompt = f"""Decompose this {complexity.value} query into sub-tasks.
            
            Query: {query}
            Required servers: {state['required_servers']}
            
            Create executable sub-tasks with clear dependencies.
            """

        response = await self.portkey.completions.create(
            model="claude-3-5-sonnet-20240620",
            messages=[{"role": "user", "content": decompose_prompt}],
            temperature=0.4,
        )

        decomposition = json.loads(response.choices[0].message.content)
        state["sub_tasks"] = decomposition["tasks"]
        state["task_dependencies"] = decomposition.get("dependencies", {})
        state["current_task_index"] = 0

        return state

    async def execute_mcp_chain(self, state: OrchestratorState) -> OrchestratorState:
        """Execute MCP calls in dependency order"""
        sub_tasks = state["sub_tasks"]
        dependencies = state.get("task_dependencies", {})
        results = state.get("mcp_results", {})

        # Execute tasks respecting dependencies
        for i, task in enumerate(sub_tasks):
            task_id = task.get("id", f"task_{i}")

            # Check dependencies
            deps = dependencies.get(task_id, [])
            if not all(dep in results for dep in deps):
                continue  # Skip if dependencies not met

            # Route to appropriate MCP server
            server = task["server"]
            tool = task["tool"]
            args = task.get("args", {})

            # Inject context from previous results
            for dep in deps:
                if dep in results:
                    args[f"context_{dep}"] = results[dep]

            try:
                result = await self.mcp_orchestrator.invoke_tool(
                    server=server, tool=tool, arguments=args
                )
                results[task_id] = result
            except Exception as e:
                results[task_id] = {"error": str(e), "failed": True}
                state["execution_errors"] = state.get("execution_errors", []) + [str(e)]

        state["mcp_results"] = results
        return state

    async def fuse_results(self, state: OrchestratorState) -> OrchestratorState:
        """Synthesize results from multiple MCP calls"""
        results = state["mcp_results"]
        query = state["query"]

        # Create synthesis prompt
        synthesis_prompt = f"""Synthesize these results into a coherent response.
        
        Original query: {query}
        
        Results from MCP servers:
        {json.dumps(results, indent=2)}
        
        Requirements:
        1. Combine insights intelligently
        2. Highlight key findings
        3. Flag any contradictions
        4. Be concise but complete
        5. Add snark if the data shows something stupid
        """

        response = await self.portkey.completions.create(
            model="claude-3-5-sonnet-20240620",
            messages=[{"role": "user", "content": synthesis_prompt}],
            temperature=0.5,
        )

        state["synthesized_response"] = response.choices[0].message.content
        state["synthesis_metadata"] = {
            "sources": list(results.keys()),
            "timestamp": datetime.utcnow().isoformat(),
            "model": "claude-3-5-sonnet",
        }

        return state

    async def self_critique(self, state: OrchestratorState) -> OrchestratorState:
        """Critique the synthesized response and determine quality"""
        response = state["synthesized_response"]
        query = state["query"]
        errors = state.get("execution_errors", [])

        critique_prompt = f"""Critique this synthesized response with extreme prejudice.

        Original Query: {query}
        Synthesized Response: {response}
        Execution Errors: {errors}

        Rate the quality on this scale:
        - perfect: The answer is complete, accurate, and requires no changes.
        - needs_data: The answer is good but incomplete. It needs more information from a knowledge source (RAG).
        - needs_refining: The components are all here, but the synthesis is weak or poorly worded. Re-running synthesis might fix it.
        - total_failure: The entire approach was wrong. Decompose the problem again from scratch.

        Provide your reasoning in 'critique_notes'.
        Output JSON: {{"quality": "...", "critique_notes": "..."}}
        """

        critique_response = await self.portkey.completions.create(
            model="claude-3-5-sonnet-20240620",
            messages=[{"role": "user", "content": critique_prompt}],
            temperature=0.1,
            response_format={"type": "json_object"},
        )

        critique_result = json.loads(critique_response.choices[0].message.content)
        state["quality"] = critique_result["quality"]
        state["critique_notes"] = critique_result.get("critique_notes", [])
        state["iteration_count"] = state.get("iteration_count", 0) + 1

        # Prevent infinite loops of pure failure
        if state["iteration_count"] > 3:
            state["quality"] = "perfect"  # Force exit
            state["critique_notes"].append("Max iterations reached. Shipping as is.")

        return state

    async def enhance_with_rag(self, state: OrchestratorState) -> OrchestratorState:
        """
        Enhance the context with a targeted RAG query to fill in missing information.
        """
        critique_notes = state.get("critique_notes", "Missing general context.")
        logger.info(f"Enhancing with RAG based on critique: {critique_notes}")

        rag_query = f"Find information to address the following critique of an AI-generated answer: {critique_notes}"

        rag_results = await self.memory.search_knowledge(
            query=rag_query,
            limit=3,
        )

        # Add RAG results to the state to be re-fused
        existing_results = state.get("mcp_results", {})
        existing_results["rag_enhancement"] = {
            "source": "weaviate_rag",
            "results": [res.get("content") for res in rag_results],
        }
        state["mcp_results"] = existing_results
        state["execution_errors"] = []  # Clear previous errors before re-fusing

        logger.info("RAG enhancement complete. Returning to fuse results.")
        return state

    async def enhance_with_memory(self, state: OrchestratorState) -> OrchestratorState:
        """Enhance response with personalized context using Weaviate v1.26 agents."""
        response = state["synthesized_response"]
        user_id = state.get("user_id", "ceo_user")

        # Weaviate v1.26+ allows for personalization agents in the search itself
        logger.info(
            f"Enhancing final response with personalized memory for user: {user_id}"
        )
        personalized_results = await self.memory.search_knowledge_personalized(
            query=state["query"],
            user_id=user_id,
            limit=5,
        )

        enhance_prompt = f"""Rewrite this response to be hyper-personalized for the user based on their context.

        Generic Response: {response}

        User's Personal Context & Memories:
        {json.dumps([res.get('content') for res in personalized_results], indent=2)}

        Make it personal, relevant, and adopt the user's preferred tone (e.g., CEO snark).
        """

        enhanced_response = await self.portkey.completions.create(
            model="claude-3-5-sonnet-20240620",
            messages=[{"role": "user", "content": enhance_prompt}],
            temperature=0.6,
        )

        state["final_response"] = enhanced_response.choices[0].message.content
        state["personalization_applied"] = True

        # Store the final, personalized interaction in memory
        await self.memory.add_knowledge(
            content=f"Q: {state['query']}\nA: {state['final_response']}",
            source="chat_interaction",
            metadata={
                "user_id": user_id,
                "complexity": state["complexity"].value,
                "quality": state["quality"],
                "timestamp": datetime.utcnow().isoformat(),
            },
        )

        state["routing_path"] = "simple"

        return state

    async def route_simple_query(self, state: OrchestratorState) -> OrchestratorState:
        """Fast path for simple queries"""
        query = state["query"]

        # Direct MCP call
        result = await self.mcp_orchestrator.route_query(query)

        state["final_response"] = result["response"]
        state["routing_path"] = "simple"

        return state

    def _route_by_complexity(self, state: OrchestratorState) -> str:
        """Route based on complexity analysis"""
        return state["complexity"].value

    def _check_quality(self, state: OrchestratorState) -> str:
        """Check critique quality for routing"""
        return state["quality"]

    def should_execute_directly(self, state: OrchestratorState) -> bool:
        """Determine if we should execute directly or decompose further"""
        # If we have sub-tasks, execute; otherwise decompose more
        return len(state.get("sub_tasks", [])) > 0

    def critique_quality(self, state: OrchestratorState) -> str:
        """Return the quality assessment from critique for routing"""
        return state.get("quality", "perfect")

    async def orchestrate(
        self, query: str, user_id: str = "ceo_user"
    ) -> Dict[str, Any]:
        """Main orchestration entry point"""
        initial_state: OrchestratorState = {
            "query": query,
            "user_id": user_id,
            "complexity": IntentComplexity.SIMPLE,
            "required_servers": [],
            "sub_tasks": [],
            "task_dependencies": {},
            "mcp_results": {},
            "synthesized_response": "",
            "synthesis_metadata": {},
            "quality": "",
            "critique_notes": [],
            "iteration_count": 0,
            "final_response": "",
            "personalization_applied": False,
            "execution_errors": [],
            "snark": "",
            "current_task_index": 0,
            "routing_path": "",
        }

        # Run the graph
        result = await self.compiled_graph.ainvoke(initial_state)

        final_response = result.get(
            "final_response", result.get("synthesized_response")
        )
        if not final_response:
            final_response = "Execution failed. Could not generate a response."
            if result.get("execution_errors"):
                final_response += f"\nErrors: {result.get('execution_errors')}"

        return {
            "response": final_response,
            "metadata": {
                "complexity": result.get("complexity", IntentComplexity.SIMPLE).value,
                "confidence_score": 0.95
                if result.get("quality") == "perfect"
                else 0.7,  # Example score
                "reasoning_trace": "->".join(
                    self.compiled_graph.get_graph().nodes
                ),  # Simplified trace
                "iterations": result.get("iteration_count", 1),
                "sources": result.get("synthesis_metadata", {}).get("sources", []),
                "personalized": result.get("personalization_applied", False),
                "critique_notes": result.get("critique_notes", []),
            },
            "debug": {
                "sub_tasks": result.get("sub_tasks", []),
                "mcp_results": result.get("mcp_results", {}),
                "quality": result.get("quality", "unknown"),
            },
        }
