"""
Enhanced LangGraph Patterns for Sophia AI
Integrates with Mem0 for learning and advanced orchestration
"""

import logging
from datetime import datetime
from enum import Enum
from typing import Any, Optional, TypedDict

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langgraph.checkpoint import MemorySaver
from langgraph.graph import END, StateGraph

from backend.services.mem0_integration_service import get_mem0_service
from backend.services.snowflake_cortex_service import SnowflakeCortexService
from backend.services.unified_llm_service import get_unified_llm_service

logger = logging.getLogger(__name__)


class WorkflowType(str, Enum):
    """Types of workflows available"""

    BUSINESS_INTELLIGENCE = "business_intelligence"
    SALES_COACHING = "sales_coaching"
    TECHNICAL_ANALYSIS = "technical_analysis"
    CUSTOMER_SUPPORT = "customer_support"
    EXECUTIVE_BRIEFING = "executive_briefing"


class EnhancedWorkflowState(TypedDict):
    """Enhanced state for workflows with learning capabilities"""

    # Core workflow state
    messages: list[BaseMessage]
    current_step: str
    workflow_type: WorkflowType
    user_id: str
    session_id: str

    # Learning and memory
    memories: list[dict[str, Any]]
    memory_context: str
    learning_feedback: Optional[dict[str, Any]]

    # Business context
    business_data: Optional[dict[str, Any]]
    analysis_results: Optional[dict[str, Any]]
    recommendations: Optional[list[str]]

    # Metadata
    started_at: datetime
    completed_at: Optional[datetime]
    performance_metrics: dict[str, float]


class LearningOrchestrator:
    """
    Advanced orchestrator with learning capabilities
    Integrates Mem0 for persistent memory and RLHF
    """

    def __init__(self):
        self.mem0_service = get_mem0_service()
        self.ai_service = await get_unified_llm_service()
        self.cortex_service = SnowflakeCortexService()
        self.checkpointer = MemorySaver()

    async def create_learning_workflow(
        self, workflow_type: WorkflowType, user_id: str, session_id: str
    ) -> StateGraph:
        """
        Create a workflow with learning capabilities

        Args:
            workflow_type: Type of workflow to create
            user_id: User identifier
            session_id: Session identifier

        Returns:
            Configured StateGraph
        """
        workflow = StateGraph(EnhancedWorkflowState)

        # Add nodes based on workflow type
        workflow.add_node("recall_memories", self.recall_memories_node)
        workflow.add_node("analyze_context", self.analyze_context_node)

        if workflow_type == WorkflowType.BUSINESS_INTELLIGENCE:
            workflow.add_node("gather_business_data", self.gather_business_data_node)
            workflow.add_node("perform_analysis", self.perform_business_analysis_node)
            workflow.add_node("generate_insights", self.generate_business_insights_node)

        elif workflow_type == WorkflowType.SALES_COACHING:
            workflow.add_node("analyze_call", self.analyze_sales_call_node)
            workflow.add_node("identify_patterns", self.identify_sales_patterns_node)
            workflow.add_node("generate_coaching", self.generate_coaching_advice_node)

        # Common final nodes
        workflow.add_node("synthesize_response", self.synthesize_response_node)
        workflow.add_node("store_learning", self.store_learning_node)

        # Define edges
        workflow.set_entry_point("recall_memories")
        workflow.add_edge("recall_memories", "analyze_context")

        # Conditional routing based on workflow type
        workflow.add_conditional_edges(
            "analyze_context",
            self.route_by_workflow_type,
            {
                WorkflowType.BUSINESS_INTELLIGENCE: "gather_business_data",
                WorkflowType.SALES_COACHING: "analyze_call",
                "default": "synthesize_response",
            },
        )

        # Connect workflow-specific nodes
        if workflow_type == WorkflowType.BUSINESS_INTELLIGENCE:
            workflow.add_edge("gather_business_data", "perform_analysis")
            workflow.add_edge("perform_analysis", "generate_insights")
            workflow.add_edge("generate_insights", "synthesize_response")

        elif workflow_type == WorkflowType.SALES_COACHING:
            workflow.add_edge("analyze_call", "identify_patterns")
            workflow.add_edge("identify_patterns", "generate_coaching")
            workflow.add_edge("generate_coaching", "synthesize_response")

        # Final edge
        workflow.add_edge("synthesize_response", "store_learning")
        workflow.add_edge("store_learning", END)

        return workflow.compile(checkpointer=self.checkpointer)

    async def recall_memories_node(
        self, state: EnhancedWorkflowState
    ) -> dict[str, Any]:
        """Recall relevant memories for the user"""
        logger.info(f"Recalling memories for user {state['user_id']}")

        # Get the latest message as context
        latest_message = state["messages"][-1].content if state["messages"] else ""

        # Recall memories
        memories = await self.mem0_service.recall_memories(
            user_id=state["user_id"],
            query=latest_message,
            limit=5,
            filters={"workflow_type": state["workflow_type"]},
        )

        # Build memory context
        memory_context = "Previous relevant interactions:\n"
        for memory in memories:
            memory_context += f"- {memory.get('content', '')}\n"

        return {
            "memories": memories,
            "memory_context": memory_context,
            "current_step": "memories_recalled",
        }

    async def analyze_context_node(
        self, state: EnhancedWorkflowState
    ) -> dict[str, Any]:
        """Analyze context and determine next steps"""
        logger.info("Analyzing context")

        # Use AI to analyze context with memories
        prompt = f"""
        Analyze the following context and determine the best approach:

        User Message: {state['messages'][-1].content if state['messages'] else ''}

        {state.get('memory_context', '')}

        Workflow Type: {state['workflow_type']}

        Provide a brief analysis of what the user needs.
        """

        analysis = await self.ai_service.generate(prompt=prompt, task_type="analysis")

        return {
            "analysis_results": {"context_analysis": analysis},
            "current_step": "context_analyzed",
        }

    async def gather_business_data_node(
        self, state: EnhancedWorkflowState
    ) -> dict[str, Any]:
        """Gather relevant business data from Snowflake"""
        logger.info("Gathering business data")

        # Extract entities and timeframe from the message
        message = state["messages"][-1].content if state["messages"] else ""

        # Use Cortex to understand what data is needed
        data_query = f"""
        Based on this request: "{message}"

        Generate a SQL query to get relevant business data.
        Focus on: revenue, customer metrics, or operational KPIs.
        """

        # For demo, return sample data structure
        business_data = {
            "revenue_trend": "increasing",
            "customer_satisfaction": 4.5,
            "operational_efficiency": 0.85,
            "key_metrics": {"mrr": 150000, "churn_rate": 0.05, "nps": 72},
        }

        return {"business_data": business_data, "current_step": "data_gathered"}

    async def perform_business_analysis_node(
        self, state: EnhancedWorkflowState
    ) -> dict[str, Any]:
        """Perform business analysis on gathered data"""
        logger.info("Performing business analysis")

        analysis_prompt = f"""
        Perform a business analysis based on:

        Request: {state['messages'][-1].content if state['messages'] else ''}

        Business Data: {state.get('business_data', {})}

        Previous Context: {state.get('memory_context', '')}

        Provide actionable insights and trends.
        """

        analysis = await self.ai_service.generate(
            prompt=analysis_prompt, task_type="business_analysis"
        )

        return {
            "analysis_results": {
                **state.get("analysis_results", {}),
                "business_analysis": analysis,
            },
            "current_step": "analysis_complete",
        }

    async def generate_business_insights_node(
        self, state: EnhancedWorkflowState
    ) -> dict[str, Any]:
        """Generate actionable business insights"""
        logger.info("Generating business insights")

        insights_prompt = f"""
        Based on the analysis: {state.get('analysis_results', {}).get('business_analysis', '')}

        Generate 3-5 actionable recommendations for the CEO.
        Focus on immediate actions and strategic initiatives.
        """

        insights = await self.ai_service.generate(
            prompt=insights_prompt, task_type="recommendations"
        )

        recommendations = insights.split("\n")
        recommendations = [r.strip() for r in recommendations if r.strip()]

        return {
            "recommendations": recommendations,
            "current_step": "insights_generated",
        }

    async def analyze_sales_call_node(
        self, state: EnhancedWorkflowState
    ) -> dict[str, Any]:
        """Analyze sales call for coaching"""
        logger.info("Analyzing sales call")

        # Placeholder for call analysis
        call_analysis = {
            "sentiment": "positive",
            "key_topics": ["pricing", "features", "timeline"],
            "objections": ["budget concerns"],
            "opportunities": ["upsell potential"],
        }

        return {
            "analysis_results": {
                **state.get("analysis_results", {}),
                "call_analysis": call_analysis,
            },
            "current_step": "call_analyzed",
        }

    async def identify_sales_patterns_node(
        self, state: EnhancedWorkflowState
    ) -> dict[str, Any]:
        """Identify patterns in sales performance"""
        logger.info("Identifying sales patterns")

        # Use memories to identify patterns
        patterns = {
            "common_objections": ["pricing", "integration"],
            "successful_tactics": ["ROI demonstration", "case studies"],
            "improvement_areas": ["discovery questions", "closing techniques"],
        }

        return {
            "analysis_results": {
                **state.get("analysis_results", {}),
                "sales_patterns": patterns,
            },
            "current_step": "patterns_identified",
        }

    async def generate_coaching_advice_node(
        self, state: EnhancedWorkflowState
    ) -> dict[str, Any]:
        """Generate personalized coaching advice"""
        logger.info("Generating coaching advice")

        coaching_prompt = f"""
        Based on the sales analysis:
        {state.get('analysis_results', {})}

        Previous coaching context:
        {state.get('memory_context', '')}

        Generate personalized coaching advice focusing on:
        1. What went well
        2. Areas for improvement
        3. Specific techniques to practice
        """

        coaching = await self.ai_service.generate(
            prompt=coaching_prompt, task_type="coaching"
        )

        recommendations = [
            "Practice discovery questions",
            "Use more customer success stories",
            "Focus on value over features",
        ]

        return {
            "recommendations": recommendations,
            "analysis_results": {
                **state.get("analysis_results", {}),
                "coaching_advice": coaching,
            },
            "current_step": "coaching_generated",
        }

    async def synthesize_response_node(
        self, state: EnhancedWorkflowState
    ) -> dict[str, Any]:
        """Synthesize final response"""
        logger.info("Synthesizing response")

        # Build comprehensive response
        response_parts = []

        if state.get("analysis_results"):
            for key, value in state["analysis_results"].items():
                response_parts.append(f"{key.replace('_', ' ').title()}:\n{value}\n")

        if state.get("recommendations"):
            response_parts.append("\nRecommendations:")
            for rec in state["recommendations"]:
                response_parts.append(f"• {rec}")

        final_response = "\n".join(response_parts)

        # Add as AI message
        state["messages"].append(AIMessage(content=final_response))

        return {"current_step": "response_synthesized", "completed_at": datetime.now()}

    async def store_learning_node(self, state: EnhancedWorkflowState) -> dict[str, Any]:
        """Store conversation and learning in Mem0"""
        logger.info("Storing learning outcomes")

        # Extract conversation for storage
        conversation = [
            {
                "role": "user" if isinstance(msg, HumanMessage) else "assistant",
                "content": msg.content,
            }
            for msg in state["messages"]
        ]

        # Store in Mem0
        memory_id = await self.mem0_service.store_conversation_memory(
            user_id=state["user_id"],
            conversation=conversation,
            metadata={
                "session_id": state["session_id"],
                "workflow_type": state["workflow_type"],
                "category": "workflow_completion",
                "analysis_results": state.get("analysis_results"),
                "recommendations": state.get("recommendations"),
            },
        )

        # Calculate performance metrics
        if state.get("started_at") and state.get("completed_at"):
            duration = (state["completed_at"] - state["started_at"]).total_seconds()
        else:
            duration = 0

        return {
            "performance_metrics": {
                "duration_seconds": duration,
                "memories_used": len(state.get("memories", [])),
                "memory_id": memory_id,
            },
            "current_step": "learning_stored",
        }

    def route_by_workflow_type(self, state: EnhancedWorkflowState) -> str:
        """Route based on workflow type"""
        workflow_type = state.get("workflow_type")

        if workflow_type == WorkflowType.BUSINESS_INTELLIGENCE:
            return WorkflowType.BUSINESS_INTELLIGENCE
        elif workflow_type == WorkflowType.SALES_COACHING:
            return WorkflowType.SALES_COACHING
        else:
            return "default"


# Example usage function
async def run_learning_workflow(
    user_query: str,
    workflow_type: WorkflowType,
    user_id: str = "ceo",
    session_id: Optional[str] = None,
) -> dict[str, Any]:
    """
    Run a learning-enabled workflow

    Args:
        user_query: User's question or request
        workflow_type: Type of workflow to run
        user_id: User identifier
        session_id: Session identifier

    Returns:
        Workflow results
    """
    if not session_id:
        session_id = f"session_{datetime.now().timestamp()}"

    orchestrator = LearningOrchestrator()

    # Create workflow
    workflow = await orchestrator.create_learning_workflow(
        workflow_type=workflow_type, user_id=user_id, session_id=session_id
    )

    # Initialize state
    initial_state = {
        "messages": [HumanMessage(content=user_query)],
        "current_step": "initialized",
        "workflow_type": workflow_type,
        "user_id": user_id,
        "session_id": session_id,
        "started_at": datetime.now(),
        "memories": [],
        "memory_context": "",
        "performance_metrics": {},
    }

    # Run workflow
    result = await workflow.ainvoke(
        initial_state, config={"configurable": {"thread_id": session_id}}
    )

    return result
