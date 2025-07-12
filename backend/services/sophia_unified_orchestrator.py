"""
Sophia Unified Orchestrator - Multi-Hop Reasoning Engine
Because single-shot prompts are for amateurs
"""

from typing import Dict, Any
from enum import Enum
import json
from datetime import datetime
from langgraph.graph import StateGraph, END

from backend.services.unified_memory_service_v2 import UnifiedMemoryServiceV2
from backend.services.portkey_gateway import PortkeyGateway
from backend.services.mcp_orchestration_service import MCPOrchestrationService


class IntentComplexity(Enum):
    SIMPLE = "simple"  # Single MCP call
    MODERATE = "moderate"  # 2-3 MCP calls
    COMPLEX = "complex"  # Multi-hop reasoning required
    NUCLEAR = "nuclear"  # CEO asking about everything


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
        graph = StateGraph(Dict[str, Any])

        # Add nodes for multi-hop reasoning
        graph.add_node("analyze_intent", self.analyze_intent)
        graph.add_node("decompose", self.decompose_intent)
        graph.add_node("execute_mcp", self.execute_mcp_chain)
        graph.add_node("fuse", self.fuse_results)
        graph.add_node("critique", self.self_critique)
        graph.add_node("enhance", self.enhance_with_memory)

        # Add conditional edges based on complexity
        graph.add_edge("analyze_intent", "decompose")
        graph.add_conditional_edges(
            "decompose",
            self.should_execute_directly,
            {True: "execute_mcp", False: "decompose"},
        )

        graph.add_edge("execute_mcp", "fuse")
        graph.add_edge("fuse", "critique")

        # Self-critique loop
        graph.add_conditional_edges(
            "critique",
            self.critique_quality,
            {
                "good": "enhance",
                "bad": "execute_mcp",  # Re-execute with better params
                "terrible": "decompose",  # Start over, you failed
            },
        )

        graph.add_edge("enhance", END)

        return graph

    async def analyze_intent(self, state: Dict[str, Any]) -> Dict[str, Any]:
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

    async def decompose_intent(self, state: Dict[str, Any]) -> Dict[str, Any]:
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

    async def execute_mcp_chain(self, state: Dict[str, Any]) -> Dict[str, Any]:
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

    async def fuse_results(self, state: Dict[str, Any]) -> Dict[str, Any]:
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

    async def self_critique(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Critique the synthesized response and determine quality"""
        response = state["synthesized_response"]
        query = state["query"]
        errors = state.get("execution_errors", [])

        critique_prompt = f"""Critique this response brutally. No sugarcoating.
        
        Query: {query}
        Response: {response}
        Errors: {errors}
        
        Rate quality: good/bad/terrible
        - good: Answers the question completely
        - bad: Missing info but salvageable  
        - terrible: Total failure, start over
        
        Provide specific issues if not good.
        """

        critique = await self.portkey.completions.create(
            model="claude-3-5-sonnet-20240620",
            messages=[{"role": "user", "content": critique_prompt}],
            temperature=0.2,
        )

        critique_result = json.loads(critique.choices[0].message.content)
        state["quality"] = critique_result["quality"]
        state["critique_notes"] = critique_result.get("issues", [])
        state["iteration_count"] = state.get("iteration_count", 0) + 1

        # Prevent infinite loops
        if state["iteration_count"] > 3:
            state["quality"] = "good"  # Force exit after 3 tries
            state["critique_notes"].append("Max iterations reached - shipping as is")

        return state

    async def enhance_with_memory(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance response with personalized context from memory"""
        response = state["synthesized_response"]
        user_id = state.get("user_id", "ceo_user")

        # Fetch user profile and relevant memories
        profile = await self.memory.get_user_profile(user_id)
        relevant_memories = await self.memory.search_knowledge(
            query=state["query"], limit=5, metadata_filter={"user_id": user_id}
        )

        # Enhance with personalization
        enhance_prompt = f"""Enhance this response with user context.
        
        Response: {response}
        
        User profile: {json.dumps(profile)}
        Relevant memories: {json.dumps([m['content'] for m in relevant_memories])}
        
        Make it personal and relevant to their history/preferences.
        Keep the snark level appropriate to their tolerance.
        """

        enhanced = await self.portkey.completions.create(
            model="claude-3-5-sonnet-20240620",
            messages=[{"role": "user", "content": enhance_prompt}],
            temperature=0.6,
        )

        state["final_response"] = enhanced.choices[0].message.content
        state["personalization_applied"] = True

        # Store interaction in memory for future personalization
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

        return state

    async def route_simple_query(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Fast path for simple queries"""
        query = state["query"]

        # Direct MCP call
        result = await self.mcp_orchestrator.route_query(query)

        state["final_response"] = result["response"]
        state["routing_path"] = "simple"

        return state

    def _route_by_complexity(self, state: Dict[str, Any]) -> str:
        """Route based on complexity analysis"""
        return state["complexity"]

    def _check_quality(self, state: Dict[str, Any]) -> str:
        """Check critique quality for routing"""
        return state["quality"]

    def should_execute_directly(self, state: Dict[str, Any]) -> bool:
        """Determine if we should execute directly or decompose further"""
        # If we have sub-tasks, execute; otherwise decompose more
        return len(state.get("sub_tasks", [])) > 0

    def critique_quality(self, state: Dict[str, Any]) -> str:
        """Return the quality assessment from critique"""
        return state.get("quality", "good")

    async def orchestrate(
        self, query: str, user_id: str = "ceo_user"
    ) -> Dict[str, Any]:
        """Main orchestration entry point"""
        initial_state = {
            "query": query,
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat(),
            "mcp_results": {},
            "iteration_count": 0,
        }

        # Run the graph
        result = await self.compiled_graph.ainvoke(initial_state)

        return {
            "response": result.get(
                "final_response",
                result.get("synthesized_response", "Failed to generate response"),
            ),
            "metadata": {
                "complexity": result.get("complexity", IntentComplexity.SIMPLE).value,
                "routing_path": result.get("routing_path", "complex"),
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
