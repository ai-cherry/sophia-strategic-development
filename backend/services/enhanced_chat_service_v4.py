"""
Enhanced Chat Service v4 - July 2025
GPU-accelerated, personality-driven, RAG-powered chat
"""

import asyncio
import json
from typing import Dict, List, Optional, AsyncGenerator
from datetime import datetime
import uuid

from langchain.memory import ConversationBufferWindowMemory
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from backend.services.unified_memory_service_v2 import UnifiedMemoryServiceV2
from backend.services.personality_engine import PersonalityEngine, PersonalityMode
from backend.services.unified_llm_service import UnifiedLLMService
import structlog

logger = structlog.get_logger()


class ChatState:
    """State management for chat conversations"""

    def __init__(self):
        self.messages: List[Dict] = []
        self.context: Dict = {}
        self.memory_results: List[Dict] = []
        self.user_id: str = ""
        self.session_id: str = ""
        self.personality_mode: str = PersonalityMode.SASSY.value


class EnhancedChatServiceV4:
    """
    Enhanced chat service with GPU memory, personality, and advanced orchestration
    """

    def __init__(self):
        self.memory_service = UnifiedMemoryServiceV2()
        self.personality_engine = PersonalityEngine()
        self.llm_service = UnifiedLLMService()
        self.conversation_memory = ConversationBufferWindowMemory(k=10)
        self.checkpointer = MemorySaver()
        self._setup_workflow()

    def _setup_workflow(self):
        """Setup LangGraph workflow for chat orchestration"""

        # Define the graph
        workflow = StateGraph(ChatState)

        # Add nodes
        workflow.add_node("retrieve_memory", self._retrieve_memory_node)
        workflow.add_node("analyze_intent", self._analyze_intent_node)
        workflow.add_node("generate_response", self._generate_response_node)
        workflow.add_node("apply_personality", self._apply_personality_node)
        workflow.add_node("store_memory", self._store_memory_node)

        # Add edges
        workflow.set_entry_point("retrieve_memory")
        workflow.add_edge("retrieve_memory", "analyze_intent")
        workflow.add_edge("analyze_intent", "generate_response")
        workflow.add_edge("generate_response", "apply_personality")
        workflow.add_edge("apply_personality", "store_memory")
        workflow.add_edge("store_memory", END)

        # Compile
        self.workflow = workflow.compile(checkpointer=self.checkpointer)

    async def _retrieve_memory_node(self, state: ChatState) -> ChatState:
        """Retrieve relevant memories using GPU-accelerated search"""

        query = state.messages[-1]["content"]

        # Search knowledge base
        results = await self.memory_service.search_knowledge(
            query=query,
            limit=5,
            metadata_filter={"user_id": state.user_id} if state.user_id else None,
        )

        state.memory_results = results

        logger.info(
            "memory_retrieved",
            query=query,
            results_count=len(results),
            latency_ms=results[0].get("search_latency_ms", 0) if results else 0,
        )

        return state

    async def _analyze_intent_node(self, state: ChatState) -> ChatState:
        """Analyze user intent and context"""

        # Extract intent using LLM
        intent_prompt = f"""
        Analyze the user's message and determine their intent.
        
        User message: {state.messages[-1]["content"]}
        
        Previous context: {json.dumps(state.memory_results[:2], indent=2)}
        
        Possible intents:
        - technical_help: User needs help with code/deployment
        - status_check: User wants to know system status
        - architecture_question: User asking about system design
        - general_chat: Casual conversation
        - frustration: User is frustrated with errors
        
        Return the intent and any key entities.
        """

        intent_response = await self.llm_service.generate(
            prompt=intent_prompt, temperature=0.3
        )

        state.context["intent"] = intent_response
        state.context["technical"] = "technical" in intent_response.lower()
        state.context["failure"] = "error" in state.messages[-1]["content"].lower()

        return state

    async def _generate_response_node(self, state: ChatState) -> ChatState:
        """Generate response using RAG and context"""

        # Build context from memory results
        memory_context = "\n".join(
            [f"- {result['content'][:200]}..." for result in state.memory_results[:3]]
        )

        # Generate response
        response_prompt = f"""
        You are Sophia AI, an advanced deployment and infrastructure assistant.
        
        User message: {state.messages[-1]["content"]}
        
        Relevant context from memory:
        {memory_context}
        
        User intent: {state.context.get('intent', 'unknown')}
        
        Provide a helpful, accurate response. Include specific technical details
        and actionable steps when appropriate.
        """

        response = await self.llm_service.generate(
            prompt=response_prompt, temperature=0.7, max_tokens=1000
        )

        state.context["raw_response"] = response

        return state

    async def _apply_personality_node(self, state: ChatState) -> ChatState:
        """Apply personality adjustments to response"""

        # Analyze user sentiment
        sentiment = self.personality_engine.analyze_sentiment(
            state.messages[-1]["content"]
        )

        # Adjust response with personality
        adjusted_response = self.personality_engine.adjust_response(
            state.context["raw_response"], state.context
        )

        state.context["final_response"] = adjusted_response
        state.context["personality_mode"] = sentiment["mode"]

        return state

    async def _store_memory_node(self, state: ChatState) -> ChatState:
        """Store conversation in GPU-accelerated memory"""

        # Store the interaction
        memory_id = await self.memory_service.add_knowledge(
            content=f"User: {state.messages[-1]['content']}\nAssistant: {state.context['final_response']}",
            source="chat",
            metadata={
                "user_id": state.user_id,
                "session_id": state.session_id,
                "intent": state.context.get("intent", "unknown"),
                "personality_mode": state.context.get("personality_mode", "sassy"),
                "timestamp": datetime.utcnow().isoformat(),
            },
        )

        logger.info("memory_stored", memory_id=memory_id, user_id=state.user_id)

        return state

    async def chat(
        self,
        message: str,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        stream: bool = False,
    ) -> AsyncGenerator[str, None]:
        """
        Main chat interface with streaming support
        """

        # Initialize state
        state = ChatState()
        state.messages = [{"role": "user", "content": message}]
        state.user_id = user_id or "anonymous"
        state.session_id = session_id or str(uuid.uuid4())

        # Run workflow
        config = {"configurable": {"thread_id": state.session_id}}
        result = await self.workflow.ainvoke(state, config)

        response = result.context["final_response"]

        if stream:
            # Stream response character by character for effect
            for char in response:
                yield char
                await asyncio.sleep(0.01)
        else:
            yield response

    async def get_chat_history(
        self, user_id: str, session_id: Optional[str] = None, limit: int = 10
    ) -> List[Dict]:
        """Get chat history from memory"""

        filter_params = {"user_id": user_id}
        if session_id:
            filter_params["session_id"] = session_id

        results = await self.memory_service.search_knowledge(
            query="", limit=limit, metadata_filter=filter_params
        )

        return results

    async def health_check(self) -> Dict:
        """Health check for the service"""

        try:
            # Test memory service
            memory_health = await self.memory_service.health_check()

            # Test LLM service
            llm_test = await self.llm_service.generate(
                prompt="Say 'operational'", max_tokens=10
            )

            return {
                "status": "healthy",
                "memory_service": memory_health,
                "llm_service": "operational" in llm_test.lower(),
                "personality_engine": self.personality_engine.current_mode.value,
                "workflow": "compiled" if self.workflow else "not compiled",
            }
        except Exception as e:
            logger.error("health_check_failed", error=str(e))
            return {"status": "unhealthy", "error": str(e)}
