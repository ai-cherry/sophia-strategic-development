"""
Sophia Universal Chat Service - Phase 2 Enhancement

This service provides a comprehensive natural language interface for:
- Workflow orchestration and management
- Agent creation and configuration
- Human-in-the-loop interactions
- Real-time chat with AI agents
- Dynamic workflow modification
- Approval and decision management

Key Features:
- Natural language workflow creation
- Real-time workflow status updates
- Human approval checkpoint management
- Agent creation through conversation
- Intelligent intent recognition
- Context-aware responses
- Multi-modal interaction support
"""

import asyncio
import json
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from backend.workflows.enhanced_langgraph_orchestration import (
    enhanced_orchestrator,
    EnhancedWorkflowState,
    HumanCheckpoint,
    WorkflowEvent,
    EventType,
    WorkflowStatus
)
from backend.utils.snowflake_cortex_service import SnowflakeCortexService
from backend.mcp_servers.enhanced_ai_memory_mcp_server import EnhancedAiMemoryMCPServer
from backend.security.audit_logger import AuditLogger
from backend.core.enhanced_cache_manager import EnhancedCacheManager
from backend.agents.specialized.sales_coach_agent import SalesCoachAgent

logger = logging.getLogger(__name__)


class ChatMessageType(Enum):
    """Types of chat messages"""
    USER_MESSAGE = "user_message"
    SYSTEM_MESSAGE = "system_message"
    WORKFLOW_UPDATE = "workflow_update"
    APPROVAL_REQUEST = "approval_request"
    AGENT_RESPONSE = "agent_response"
    ERROR_MESSAGE = "error_message"
    STATUS_UPDATE = "status_update"


class IntentType(Enum):
    """Types of user intents"""
    CREATE_WORKFLOW = "create_workflow"
    MODIFY_WORKFLOW = "modify_workflow"
    CHECK_STATUS = "check_status"
    APPROVE_CHECKPOINT = "approve_checkpoint"
    REJECT_CHECKPOINT = "reject_checkpoint"
    CREATE_AGENT = "create_agent"
    GENERAL_QUESTION = "general_question"
    DATA_ANALYSIS = "data_analysis"
    WORKFLOW_HELP = "workflow_help"


@dataclass
class ChatMessage:
    """Chat message structure"""
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str = ""
    user_id: str = ""
    message_type: ChatMessageType = ChatMessageType.USER_MESSAGE
    content: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    workflow_id: Optional[str] = None
    checkpoint_id: Optional[str] = None
    intent: Optional[IntentType] = None
    confidence: float = 0.0


@dataclass
class ChatSession:
    """Chat session management"""
    session_id: str
    user_id: str
    created_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    active_workflows: List[str] = field(default_factory=list)
    pending_approvals: List[str] = field(default_factory=list)
    context_history: List[ChatMessage] = field(default_factory=list)
    user_preferences: Dict[str, Any] = field(default_factory=dict)
    session_metadata: Dict[str, Any] = field(default_factory=dict)


class SophiaUniversalChatService:
    """
    Universal chat service for natural language interaction with Sophia AI
    
    Provides comprehensive natural language interface for:
    - Workflow creation and management
    - Agent interaction and creation
    - Human-in-the-loop operations
    - Real-time status updates
    """
    
    def __init__(self):
        self.cortex_service: Optional[SnowflakeCortexService] = None
        self.ai_memory: Optional[EnhancedAiMemoryMCPServer] = None
        self.audit_logger = AuditLogger()
        self.cache_manager = EnhancedCacheManager()
        
        # Session management
        self.active_sessions: Dict[str, ChatSession] = {}
        self.session_timeouts: Dict[str, datetime] = {}
        
        # Intent recognition cache
        self.intent_cache: Dict[str, IntentType] = {}
        
        # Workflow integration
        self.orchestrator = enhanced_orchestrator
        
        self.initialized = False
    
    async def initialize(self) -> None:
        """Initialize the universal chat service"""
        if self.initialized:
            return
        
        try:
            # Initialize services
            self.cortex_service = SnowflakeCortexService()
            self.ai_memory = EnhancedAiMemoryMCPServer()
            await self.ai_memory.initialize()
            
            # Initialize orchestrator
            await self.orchestrator.initialize()
            
            # Start background tasks
            asyncio.create_task(self._session_cleanup_task())
            asyncio.create_task(self._workflow_monitoring_task())
            
            self.initialized = True
            logger.info("✅ Sophia Universal Chat Service initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize Sophia Universal Chat Service: {e}")
            raise
    
    async def process_message(
        self, 
        user_id: str, 
        session_id: str, 
        message_content: str,
        message_metadata: Optional[Dict[str, Any]] = None
    ) -> ChatMessage:
        """
        Process incoming chat message and generate response
        
        Args:
            user_id: User identifier
            session_id: Session identifier
            message_content: Message content
            message_metadata: Optional metadata
            
        Returns:
            Response message
        """
        if not self.initialized:
            await self.initialize()
        
        try:
            # Get or create session
            session = await self._get_or_create_session(user_id, session_id)
            
            # Create user message
            user_message = ChatMessage(
                session_id=session_id,
                user_id=user_id,
                message_type=ChatMessageType.USER_MESSAGE,
                content=message_content,
                metadata=message_metadata or {}
            )
            
            # Add to session history
            session.context_history.append(user_message)
            session.last_activity = datetime.now()
            
            # Recognize intent
            intent, confidence = await self._recognize_intent(
                message_content, session.context_history
            )
            user_message.intent = intent
            user_message.confidence = confidence
            
            # Process based on intent
            response = await self._process_intent(user_message, session)
            
            # Add response to session history
            session.context_history.append(response)
            
            # Log interaction
            await self.audit_logger.log_chat_interaction(
                user_id=user_id,
                session_id=session_id,
                message_type="user_message",
                content=message_content,
                intent=intent.value if intent else "unknown",
                response_content=response.content
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return ChatMessage(
                session_id=session_id,
                user_id=user_id,
                message_type=ChatMessageType.ERROR_MESSAGE,
                content=f"I encountered an error processing your message: {str(e)}. Please try again.",
                metadata={"error": str(e)}
            )
    
    async def _recognize_intent(
        self, 
        message_content: str, 
        context_history: List[ChatMessage]
    ) -> tuple[Optional[IntentType], float]:
        """
        Recognize user intent from message content and context
        
        Args:
            message_content: Current message content
            context_history: Previous conversation context
            
        Returns:
            Tuple of (intent, confidence_score)
        """
        # Check cache first
        cache_key = f"intent_{hash(message_content)}"
        cached_intent = self.intent_cache.get(cache_key)
        if cached_intent:
            return cached_intent, 0.9
        
        # Build context for intent recognition
        recent_context = []
        for msg in context_history[-5:]:  # Last 5 messages
            recent_context.append(f"{msg.message_type.value}: {msg.content}")
        
        context_str = "\n".join(recent_context) if recent_context else "No previous context"
        
        # Use Cortex for intent recognition
        async with self.cortex_service as cortex:
            intent_prompt = f"""
            Analyze this user message and determine the intent:
            
            Current Message: {message_content}
            
            Recent Context:
            {context_str}
            
            Possible Intents:
            1. create_workflow - User wants to create a new workflow
            2. modify_workflow - User wants to modify an existing workflow
            3. check_status - User wants to check workflow or system status
            4. approve_checkpoint - User wants to approve a pending checkpoint
            5. reject_checkpoint - User wants to reject a pending checkpoint
            6. create_agent - User wants to create a new AI agent
            7. general_question - User has a general question
            8. data_analysis - User wants data analysis or insights
            9. workflow_help - User needs help with workflows
            
            Return JSON with:
            {{
                "intent": "intent_name",
                "confidence": 0.0-1.0,
                "reasoning": "explanation"
            }}
            """
            
            intent_result = await cortex.complete_text_with_cortex(
                prompt=intent_prompt,
                max_tokens=200
            )
        
        try:
            intent_data = json.loads(intent_result)
            intent_name = intent_data.get("intent", "general_question")
            confidence = float(intent_data.get("confidence", 0.5))
            
            # Map to enum
            intent_mapping = {
                "create_workflow": IntentType.CREATE_WORKFLOW,
                "modify_workflow": IntentType.MODIFY_WORKFLOW,
                "check_status": IntentType.CHECK_STATUS,
                "approve_checkpoint": IntentType.APPROVE_CHECKPOINT,
                "reject_checkpoint": IntentType.REJECT_CHECKPOINT,
                "create_agent": IntentType.CREATE_AGENT,
                "general_question": IntentType.GENERAL_QUESTION,
                "data_analysis": IntentType.DATA_ANALYSIS,
                "workflow_help": IntentType.WORKFLOW_HELP
            }
            
            intent = intent_mapping.get(intent_name, IntentType.GENERAL_QUESTION)
            
            # Cache result
            if confidence > 0.7:
                self.intent_cache[cache_key] = intent
            
            return intent, confidence
            
        except (json.JSONDecodeError, ValueError):
            # Fallback to keyword-based intent recognition
            return self._fallback_intent_recognition(message_content), 0.3
    
    def _fallback_intent_recognition(self, message_content: str) -> IntentType:
        """Fallback intent recognition using keywords"""
        content_lower = message_content.lower()
        
        # Keyword mapping
        if any(word in content_lower for word in ["create", "new", "build", "make", "workflow"]):
            if "agent" in content_lower:
                return IntentType.CREATE_AGENT
            else:
                return IntentType.CREATE_WORKFLOW
        elif any(word in content_lower for word in ["status", "check", "progress", "how is"]):
            return IntentType.CHECK_STATUS
        elif any(word in content_lower for word in ["approve", "yes", "accept", "confirm"]):
            return IntentType.APPROVE_CHECKPOINT
        elif any(word in content_lower for word in ["reject", "no", "deny", "cancel"]):
            return IntentType.REJECT_CHECKPOINT
        elif any(word in content_lower for word in ["modify", "change", "update", "edit"]):
            return IntentType.MODIFY_WORKFLOW
        elif any(word in content_lower for word in ["analyze", "analysis", "data", "insights"]):
            return IntentType.DATA_ANALYSIS
        elif any(word in content_lower for word in ["help", "how", "what", "explain"]):
            return IntentType.WORKFLOW_HELP
        else:
            return IntentType.GENERAL_QUESTION
    
    async def _process_intent(
        self, 
        user_message: ChatMessage, 
        session: ChatSession
    ) -> ChatMessage:
        """
        Process user message based on recognized intent
        
        Args:
            user_message: User message with recognized intent
            session: Chat session
            
        Returns:
            Response message
        """
        intent = user_message.intent
        
        if intent == IntentType.CREATE_WORKFLOW:
            return await self._handle_create_workflow(user_message, session)
        elif intent == IntentType.MODIFY_WORKFLOW:
            return await self._handle_modify_workflow(user_message, session)
        elif intent == IntentType.CHECK_STATUS:
            return await self._handle_check_status(user_message, session)
        elif intent == IntentType.APPROVE_CHECKPOINT:
            return await self._handle_approve_checkpoint(user_message, session)
        elif intent == IntentType.REJECT_CHECKPOINT:
            return await self._handle_reject_checkpoint(user_message, session)
        elif intent == IntentType.CREATE_AGENT:
            return await self._handle_create_agent(user_message, session)
        elif intent == IntentType.DATA_ANALYSIS:
            return await self._handle_data_analysis(user_message, session)
        elif intent == IntentType.WORKFLOW_HELP:
            return await self._handle_workflow_help(user_message, session)
        else:
            return await self._handle_general_question(user_message, session)
    
    async def _handle_create_workflow(
        self, 
        user_message: ChatMessage, 
        session: ChatSession
    ) -> ChatMessage:
        """Handle workflow creation request"""
        try:
            # Create workflow using orchestrator
            workflow_id = await self.orchestrator.create_workflow_from_natural_language(
                user_request=user_message.content,
                user_id=user_message.user_id,
                session_id=user_message.session_id
            )
            
            # Add to session
            session.active_workflows.append(workflow_id)
            
            # Get workflow status for response
            workflow_status = await self.orchestrator.get_workflow_status(workflow_id)
            
            response_content = f"""
            ✅ I've created a new workflow for you!
            
            **Workflow ID:** {workflow_id}
            **Status:** {workflow_status['status']}
            **Current Step:** {workflow_status['current_node']}
            
            Your workflow is now running. I'll keep you updated on its progress and let you know if any approvals are needed.
            
            You can check the status anytime by asking "What's the status of my workflow?"
            """
            
            return ChatMessage(
                session_id=user_message.session_id,
                user_id=user_message.user_id,
                message_type=ChatMessageType.SYSTEM_MESSAGE,
                content=response_content,
                workflow_id=workflow_id,
                metadata={
                    "workflow_created": True,
                    "workflow_id": workflow_id,
                    "workflow_status": workflow_status
                }
            )
            
        except Exception as e:
            logger.error(f"Error creating workflow: {e}")
            return ChatMessage(
                session_id=user_message.session_id,
                user_id=user_message.user_id,
                message_type=ChatMessageType.ERROR_MESSAGE,
                content=f"I encountered an error creating your workflow: {str(e)}. Please try again with more specific details.",
                metadata={"error": str(e)}
            )
    
    async def _handle_check_status(
        self, 
        user_message: ChatMessage, 
        session: ChatSession
    ) -> ChatMessage:
        """Handle status check request"""
        try:
            # Get status of all active workflows
            workflow_statuses = []
            for workflow_id in session.active_workflows:
                status = await self.orchestrator.get_workflow_status(workflow_id)
                workflow_statuses.append(status)
            
            # Get pending approvals
            pending_approvals = await self.orchestrator.get_pending_approvals(user_message.user_id)
            
            # Build status response
            if not workflow_statuses and not pending_approvals:
                response_content = "You don't have any active workflows or pending approvals at the moment."
            else:
                response_parts = []
                
                if workflow_statuses:
                    response_parts.append("**Active Workflows:**")
                    for status in workflow_statuses:
                        progress = status['progress']
                        response_parts.append(
                            f"• {status['workflow_id'][:8]}... - {status['status']} "
                            f"({progress['completed_nodes']}/{progress['total_nodes']} steps completed)"
                        )
                
                if pending_approvals:
                    response_parts.append("\n**Pending Approvals:**")
                    for approval in pending_approvals:
                        response_parts.append(f"• {approval['title']}: {approval['description']}")
                
                response_content = "\n".join(response_parts)
            
            return ChatMessage(
                session_id=user_message.session_id,
                user_id=user_message.user_id,
                message_type=ChatMessageType.STATUS_UPDATE,
                content=response_content,
                metadata={
                    "workflow_statuses": workflow_statuses,
                    "pending_approvals": pending_approvals
                }
            )
            
        except Exception as e:
            logger.error(f"Error checking status: {e}")
            return ChatMessage(
                session_id=user_message.session_id,
                user_id=user_message.user_id,
                message_type=ChatMessageType.ERROR_MESSAGE,
                content=f"I encountered an error checking your status: {str(e)}",
                metadata={"error": str(e)}
            )
    
    async def _handle_approve_checkpoint(
        self, 
        user_message: ChatMessage, 
        session: ChatSession
    ) -> ChatMessage:
        """Handle checkpoint approval"""
        try:
            # Get pending approvals for user
            pending_approvals = await self.orchestrator.get_pending_approvals(user_message.user_id)
            
            if not pending_approvals:
                return ChatMessage(
                    session_id=user_message.session_id,
                    user_id=user_message.user_id,
                    message_type=ChatMessageType.SYSTEM_MESSAGE,
                    content="You don't have any pending approvals at the moment."
                )
            
            # If only one approval, approve it
            if len(pending_approvals) == 1:
                checkpoint_id = pending_approvals[0]["checkpoint_id"]
                
                # Process approval
                approved = await self.orchestrator.handle_human_response(
                    checkpoint_id=checkpoint_id,
                    response={"approved": True, "feedback": user_message.content},
                    user_id=user_message.user_id
                )
                
                response_content = f"✅ Approved! I've processed your approval for '{pending_approvals[0]['title']}'. The workflow will continue."
                
            else:
                # Multiple approvals - ask for clarification
                approval_list = "\n".join([
                    f"{i+1}. {approval['title']}" 
                    for i, approval in enumerate(pending_approvals)
                ])
                
                response_content = f"""
                You have multiple pending approvals. Which one would you like to approve?
                
                {approval_list}
                
                Please specify by number or title.
                """
            
            return ChatMessage(
                session_id=user_message.session_id,
                user_id=user_message.user_id,
                message_type=ChatMessageType.SYSTEM_MESSAGE,
                content=response_content,
                metadata={"pending_approvals": pending_approvals}
            )
            
        except Exception as e:
            logger.error(f"Error handling approval: {e}")
            return ChatMessage(
                session_id=user_message.session_id,
                user_id=user_message.user_id,
                message_type=ChatMessageType.ERROR_MESSAGE,
                content=f"I encountered an error processing your approval: {str(e)}",
                metadata={"error": str(e)}
            )
    
    async def _handle_reject_checkpoint(
        self, 
        user_message: ChatMessage, 
        session: ChatSession
    ) -> ChatMessage:
        """Handle checkpoint rejection"""
        try:
            # Similar logic to approval but with rejection
            pending_approvals = await self.orchestrator.get_pending_approvals(user_message.user_id)
            
            if not pending_approvals:
                return ChatMessage(
                    session_id=user_message.session_id,
                    user_id=user_message.user_id,
                    message_type=ChatMessageType.SYSTEM_MESSAGE,
                    content="You don't have any pending approvals to reject."
                )
            
            if len(pending_approvals) == 1:
                checkpoint_id = pending_approvals[0]["checkpoint_id"]
                
                # Process rejection
                approved = await self.orchestrator.handle_human_response(
                    checkpoint_id=checkpoint_id,
                    response={"approved": False, "feedback": user_message.content},
                    user_id=user_message.user_id
                )
                
                response_content = f"❌ Rejected. I've processed your rejection for '{pending_approvals[0]['title']}'. The workflow will be adjusted accordingly."
                
            else:
                # Multiple approvals - ask for clarification
                approval_list = "\n".join([
                    f"{i+1}. {approval['title']}" 
                    for i, approval in enumerate(pending_approvals)
                ])
                
                response_content = f"""
                You have multiple pending approvals. Which one would you like to reject?
                
                {approval_list}
                
                Please specify by number or title.
                """
            
            return ChatMessage(
                session_id=user_message.session_id,
                user_id=user_message.user_id,
                message_type=ChatMessageType.SYSTEM_MESSAGE,
                content=response_content,
                metadata={"pending_approvals": pending_approvals}
            )
            
        except Exception as e:
            logger.error(f"Error handling rejection: {e}")
            return ChatMessage(
                session_id=user_message.session_id,
                user_id=user_message.user_id,
                message_type=ChatMessageType.ERROR_MESSAGE,
                content=f"I encountered an error processing your rejection: {str(e)}",
                metadata={"error": str(e)}
            )
    
    async def _handle_create_agent(
        self, 
        user_message: ChatMessage, 
        session: ChatSession
    ) -> ChatMessage:
        """Handle agent creation request"""
        try:
            # Use Cortex to analyze agent requirements
            async with self.cortex_service as cortex:
                agent_analysis = await cortex.complete_text_with_cortex(
                    prompt=f"""
                    Analyze this agent creation request and extract requirements:
                    
                    User Request: {user_message.content}
                    
                    Extract:
                    1. Agent name and purpose
                    2. Required capabilities
                    3. Data sources needed
                    4. Integration requirements
                    5. Suggested configuration
                    
                    Return as JSON with clear structure.
                    """,
                    max_tokens=400
                )
            
            # Create workflow for agent creation
            workflow_id = await self.orchestrator.create_workflow_from_natural_language(
                user_request=f"Create AI agent: {user_message.content}",
                user_id=user_message.user_id,
                session_id=user_message.session_id
            )
            
            session.active_workflows.append(workflow_id)
            
            response_content = f"""
            🤖 I'll help you create a new AI agent!
            
            I've analyzed your request and started the agent creation workflow (ID: {workflow_id[:8]}...).
            
            Based on your description, I'll:
            1. Define the agent's capabilities and purpose
            2. Configure required data sources and integrations
            3. Set up the agent's knowledge base
            4. Create tests to validate functionality
            5. Deploy the agent for use
            
            I'll need your approval at key steps to ensure the agent meets your needs.
            """
            
            return ChatMessage(
                session_id=user_message.session_id,
                user_id=user_message.user_id,
                message_type=ChatMessageType.SYSTEM_MESSAGE,
                content=response_content,
                workflow_id=workflow_id,
                metadata={
                    "agent_creation": True,
                    "workflow_id": workflow_id,
                    "agent_analysis": agent_analysis
                }
            )
            
        except Exception as e:
            logger.error(f"Error creating agent: {e}")
            return ChatMessage(
                session_id=user_message.session_id,
                user_id=user_message.user_id,
                message_type=ChatMessageType.ERROR_MESSAGE,
                content=f"I encountered an error setting up agent creation: {str(e)}",
                metadata={"error": str(e)}
            )
    
    async def _handle_data_analysis(
        self, 
        user_message: ChatMessage, 
        session: ChatSession
    ) -> ChatMessage:
        """Handle data analysis request"""
        try:
            # Create workflow for data analysis
            workflow_id = await self.orchestrator.create_workflow_from_natural_language(
                user_request=f"Data analysis: {user_message.content}",
                user_id=user_message.user_id,
                session_id=user_message.session_id
            )
            
            session.active_workflows.append(workflow_id)
            
            response_content = f"""
            📊 I'll analyze your data for you!
            
            I've started a data analysis workflow (ID: {workflow_id[:8]}...) to process your request.
            
            I'll:
            1. Identify the relevant data sources
            2. Extract and prepare the data
            3. Perform the requested analysis
            4. Generate insights and visualizations
            5. Provide actionable recommendations
            
            I'll keep you updated on the progress and share the results when ready.
            """
            
            return ChatMessage(
                session_id=user_message.session_id,
                user_id=user_message.user_id,
                message_type=ChatMessageType.SYSTEM_MESSAGE,
                content=response_content,
                workflow_id=workflow_id,
                metadata={
                    "data_analysis": True,
                    "workflow_id": workflow_id
                }
            )
            
        except Exception as e:
            logger.error(f"Error handling data analysis: {e}")
            return ChatMessage(
                session_id=user_message.session_id,
                user_id=user_message.user_id,
                message_type=ChatMessageType.ERROR_MESSAGE,
                content=f"I encountered an error setting up data analysis: {str(e)}",
                metadata={"error": str(e)}
            )
    
    async def _handle_workflow_help(
        self, 
        user_message: ChatMessage, 
        session: ChatSession
    ) -> ChatMessage:
        """Handle workflow help request"""
        help_content = """
        🔧 **Sophia AI Workflow Help**
        
        I can help you with various tasks through natural language:
        
        **Creating Workflows:**
        - "Create a workflow to analyze our Q4 sales data"
        - "Build a process to onboard new customers"
        - "Set up automated deal analysis"
        
        **Managing Workflows:**
        - "What's the status of my workflows?"
        - "Modify the customer analysis workflow"
        - "Cancel the data processing workflow"
        
        **Approvals & Decisions:**
        - "Approve the pending analysis"
        - "Reject the proposed changes"
        - "I need to review the recommendations"
        
        **Creating AI Agents:**
        - "Create an agent to monitor customer sentiment"
        - "Build a sales coaching agent"
        - "Set up an automated reporting agent"
        
        **Data Analysis:**
        - "Analyze our customer churn data"
        - "Generate insights from call recordings"
        - "Compare this quarter's performance"
        
        Just describe what you want to do in natural language, and I'll handle the rest!
        """
        
        return ChatMessage(
            session_id=user_message.session_id,
            user_id=user_message.user_id,
            message_type=ChatMessageType.SYSTEM_MESSAGE,
            content=help_content,
            metadata={"help_provided": True}
        )
    
    async def _handle_general_question(
        self, 
        user_message: ChatMessage, 
        session: ChatSession
    ) -> ChatMessage:
        """Handle general questions"""
        try:
            # Use Cortex to generate response
            async with self.cortex_service as cortex:
                # Build context from session history
                context_messages = []
                for msg in session.context_history[-5:]:
                    context_messages.append(f"{msg.message_type.value}: {msg.content}")
                
                context_str = "\n".join(context_messages) if context_messages else "No previous context"
                
                response_prompt = f"""
                You are Sophia AI, an intelligent assistant for workflow orchestration and AI agent management.
                
                User Question: {user_message.content}
                
                Recent Conversation Context:
                {context_str}
                
                Provide a helpful, informative response. If the question relates to workflows, agents, or data analysis, 
                offer to help create or manage those resources.
                
                Keep the response conversational and helpful.
                """
                
                ai_response = await cortex.complete_text_with_cortex(
                    prompt=response_prompt,
                    max_tokens=300
                )
            
            return ChatMessage(
                session_id=user_message.session_id,
                user_id=user_message.user_id,
                message_type=ChatMessageType.AGENT_RESPONSE,
                content=ai_response,
                metadata={"ai_generated": True}
            )
            
        except Exception as e:
            logger.error(f"Error handling general question: {e}")
            return ChatMessage(
                session_id=user_message.session_id,
                user_id=user_message.user_id,
                message_type=ChatMessageType.SYSTEM_MESSAGE,
                content="I'm here to help with workflows, AI agents, and data analysis. What would you like to work on?",
                metadata={"fallback_response": True}
            )
    
    async def _handle_modify_workflow(
        self, 
        user_message: ChatMessage, 
        session: ChatSession
    ) -> ChatMessage:
        """Handle workflow modification request"""
        try:
            # Check if user has active workflows
            if not session.active_workflows:
                return ChatMessage(
                    session_id=user_message.session_id,
                    user_id=user_message.user_id,
                    message_type=ChatMessageType.SYSTEM_MESSAGE,
                    content="You don't have any active workflows to modify. Would you like to create a new workflow instead?"
                )
            
            # If only one workflow, modify it
            if len(session.active_workflows) == 1:
                workflow_id = session.active_workflows[0]
                
                # Create modification event
                event = WorkflowEvent(
                    event_type=EventType.USER_INPUT,
                    source_node="user_modification",
                    data={"user_input": user_message.content, "modification_request": True}
                )
                
                # Process the modification
                await self.orchestrator._process_event(workflow_id, event)
                
                response_content = f"✅ I've processed your modification request for workflow {workflow_id[:8]}... The workflow will be updated accordingly."
                
            else:
                # Multiple workflows - ask for clarification
                workflow_list = []
                for i, workflow_id in enumerate(session.active_workflows):
                    status = await self.orchestrator.get_workflow_status(workflow_id)
                    workflow_list.append(f"{i+1}. {workflow_id[:8]}... - {status['status']}")
                
                response_content = f"""
                You have multiple active workflows. Which one would you like to modify?
                
                {chr(10).join(workflow_list)}
                
                Please specify by number or workflow ID.
                """
            
            return ChatMessage(
                session_id=user_message.session_id,
                user_id=user_message.user_id,
                message_type=ChatMessageType.SYSTEM_MESSAGE,
                content=response_content,
                metadata={"modification_request": True}
            )
            
        except Exception as e:
            logger.error(f"Error modifying workflow: {e}")
            return ChatMessage(
                session_id=user_message.session_id,
                user_id=user_message.user_id,
                message_type=ChatMessageType.ERROR_MESSAGE,
                content=f"I encountered an error modifying your workflow: {str(e)}",
                metadata={"error": str(e)}
            )
    
    async def _get_or_create_session(self, user_id: str, session_id: str) -> ChatSession:
        """Get existing session or create new one"""
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            session.last_activity = datetime.now()
            return session
        
        # Create new session
        session = ChatSession(
            session_id=session_id,
            user_id=user_id
        )
        
        self.active_sessions[session_id] = session
        self.session_timeouts[session_id] = datetime.now() + timedelta(hours=24)
        
        return session
    
    async def _session_cleanup_task(self) -> None:
        """Background task to clean up expired sessions"""
        while True:
            try:
                current_time = datetime.now()
                expired_sessions = [
                    session_id for session_id, timeout_time in self.session_timeouts.items()
                    if current_time > timeout_time
                ]
                
                for session_id in expired_sessions:
                    if session_id in self.active_sessions:
                        del self.active_sessions[session_id]
                    if session_id in self.session_timeouts:
                        del self.session_timeouts[session_id]
                
                # Sleep for 1 hour before next cleanup
                await asyncio.sleep(3600)
                
            except Exception as e:
                logger.error(f"Error in session cleanup: {e}")
                await asyncio.sleep(300)  # Sleep 5 minutes on error
    
    async def _workflow_monitoring_task(self) -> None:
        """Background task to monitor workflow status and send updates"""
        while True:
            try:
                # Check all active workflows for status changes
                for session in self.active_sessions.values():
                    for workflow_id in session.active_workflows[:]:  # Copy list to avoid modification during iteration
                        try:
                            status = await self.orchestrator.get_workflow_status(workflow_id)
                            
                            # Check for completion or failure
                            if status['status'] in ['completed', 'failed', 'cancelled']:
                                # Send notification to user
                                notification = ChatMessage(
                                    session_id=session.session_id,
                                    user_id=session.user_id,
                                    message_type=ChatMessageType.WORKFLOW_UPDATE,
                                    content=f"Workflow {workflow_id[:8]}... has {status['status']}.",
                                    workflow_id=workflow_id,
                                    metadata={"workflow_status": status}
                                )
                                
                                # Add to session history
                                session.context_history.append(notification)
                                
                                # Remove from active workflows if completed/failed/cancelled
                                session.active_workflows.remove(workflow_id)
                            
                            # Check for new pending approvals
                            if status.get('pending_checkpoints'):
                                for checkpoint in status['pending_checkpoints']:
                                    if checkpoint['checkpoint_id'] not in session.pending_approvals:
                                        session.pending_approvals.append(checkpoint['checkpoint_id'])
                                        
                                        # Send approval request
                                        approval_request = ChatMessage(
                                            session_id=session.session_id,
                                            user_id=session.user_id,
                                            message_type=ChatMessageType.APPROVAL_REQUEST,
                                            content=f"🔔 Approval needed: {checkpoint['title']}\n\n{checkpoint['natural_language_prompt']}",
                                            workflow_id=workflow_id,
                                            checkpoint_id=checkpoint['checkpoint_id'],
                                            metadata={"checkpoint": checkpoint}
                                        )
                                        
                                        session.context_history.append(approval_request)
                        
                        except Exception as e:
                            logger.error(f"Error monitoring workflow {workflow_id}: {e}")
                
                # Sleep for 30 seconds before next check
                await asyncio.sleep(30)
                
            except Exception as e:
                logger.error(f"Error in workflow monitoring: {e}")
                await asyncio.sleep(60)  # Sleep 1 minute on error
    
    async def get_session_history(self, session_id: str, limit: int = 50) -> List[ChatMessage]:
        """Get chat history for a session"""
        session = self.active_sessions.get(session_id)
        if not session:
            return []
        
        return session.context_history[-limit:]
    
    async def get_active_workflows(self, user_id: str) -> List[Dict[str, Any]]:
        """Get active workflows for a user"""
        workflows = []
        
        for session in self.active_sessions.values():
            if session.user_id == user_id:
                for workflow_id in session.active_workflows:
                    status = await self.orchestrator.get_workflow_status(workflow_id)
                    workflows.append(status)
        
        return workflows
    
    async def get_pending_approvals_for_user(self, user_id: str) -> List[Dict[str, Any]]:
        """Get pending approvals for a user"""
        return await self.orchestrator.get_pending_approvals(user_id)


# Global instance
universal_chat_service = SophiaUniversalChatService()

