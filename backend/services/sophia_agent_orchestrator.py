"""
Sophia AI Agent Orchestrator
Implements Claude-Code-Development-Kit multi-agent workflow patterns
with Portkey gateway and OpenRouter model selection
"""

import asyncio
import json
import time
from collections.abc import AsyncGenerator
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any

from backend.core.auto_esc_config import get_config_value
from backend.services.unified_llm_service import UnifiedLLMService, TaskType
from backend.utils.custom_logger import logger


class AgentType(Enum):
    """Agent types for specialized task handling"""
    SOPHIA_INTELLIGENCE = "sophia_intelligence"
    BUSINESS_INTELLIGENCE = "business_intelligence"
    CODE_DEVELOPMENT = "code_development"
    INFRASTRUCTURE = "infrastructure"
    INTEGRATION = "integration"
    RESEARCH = "research"


class WorkflowStage(Enum):
    """Workflow stages for agent handoffs"""
    INTENT_CLASSIFICATION = "intent_classification"
    CONTEXT_RETRIEVAL = "context_retrieval"
    TASK_EXECUTION = "task_execution"
    QUALITY_VALIDATION = "quality_validation"
    RESPONSE_SYNTHESIS = "response_synthesis"


@dataclass
class AgentHandoff:
    """Agent handoff configuration"""
    from_agent: AgentType
    to_agent: AgentType
    stage: WorkflowStage
    condition: str
    data_transfer: dict[str, Any]


@dataclass
class WorkflowResult:
    """Result from agent workflow execution"""
    success: bool
    result: Any
    metadata: dict[str, Any]
    execution_time: float
    agent_chain: list[str]
    token_usage: dict[str, int]


class SophiaAgentOrchestrator:
    """
    Multi-agent workflow orchestrator with intelligent routing
    Implements Claude-Code-Development-Kit patterns for agent coordination
    """

    def __init__(self):
        self.llm_service = UnifiedLLMService()
        self.documentation_loader = None  # Will be initialized
        self.agent_workflows = self._init_agent_workflows()
        self.mcp_servers = self._init_mcp_servers()
        self.performance_metrics = {}
        
    async def initialize(self):
        """Initialize the orchestrator and all dependencies"""
        await self.llm_service.initialize()
        self.documentation_loader = await self._init_documentation_loader()
        logger.info("✅ SophiaAgentOrchestrator initialized successfully")

    def _init_agent_workflows(self) -> dict[str, list[AgentHandoff]]:
        """Initialize agent workflow patterns following Claude-Code-Development-Kit"""
        return {
            # Code Development Workflow
            "code_development": [
                AgentHandoff(
                    from_agent=AgentType.SOPHIA_INTELLIGENCE,
                    to_agent=AgentType.CODE_DEVELOPMENT,
                    stage=WorkflowStage.INTENT_CLASSIFICATION,
                    condition="task_type == 'code_generation'",
                    data_transfer={"context": "foundation_tier", "complexity": "moderate"}
                ),
                AgentHandoff(
                    from_agent=AgentType.CODE_DEVELOPMENT,
                    to_agent=AgentType.INTEGRATION,
                    stage=WorkflowStage.QUALITY_VALIDATION,
                    condition="requires_quality_check",
                    data_transfer={"code": "generated_code", "tests": "test_cases"}
                )
            ],
            
            # Business Intelligence Workflow
            "business_intelligence": [
                AgentHandoff(
                    from_agent=AgentType.SOPHIA_INTELLIGENCE,
                    to_agent=AgentType.RESEARCH,
                    stage=WorkflowStage.CONTEXT_RETRIEVAL,
                    condition="requires_external_data",
                    data_transfer={"query": "research_query", "sources": "data_sources"}
                ),
                AgentHandoff(
                    from_agent=AgentType.RESEARCH,
                    to_agent=AgentType.BUSINESS_INTELLIGENCE,
                    stage=WorkflowStage.TASK_EXECUTION,
                    condition="data_collected",
                    data_transfer={"data": "research_data", "insights": "key_insights"}
                )
            ],
            
            # Infrastructure Management Workflow
            "infrastructure": [
                AgentHandoff(
                    from_agent=AgentType.SOPHIA_INTELLIGENCE,
                    to_agent=AgentType.INFRASTRUCTURE,
                    stage=WorkflowStage.INTENT_CLASSIFICATION,
                    condition="task_type == 'infrastructure_management'",
                    data_transfer={"scope": "infrastructure_scope", "risk_level": "high"}
                ),
                AgentHandoff(
                    from_agent=AgentType.INFRASTRUCTURE,
                    to_agent=AgentType.INTEGRATION,
                    stage=WorkflowStage.QUALITY_VALIDATION,
                    condition="requires_validation",
                    data_transfer={"changes": "infrastructure_changes", "tests": "validation_tests"}
                )
            ],
            
            # Research and Analysis Workflow
            "research_analysis": [
                AgentHandoff(
                    from_agent=AgentType.SOPHIA_INTELLIGENCE,
                    to_agent=AgentType.RESEARCH,
                    stage=WorkflowStage.CONTEXT_RETRIEVAL,
                    condition="requires_comprehensive_research",
                    data_transfer={"query": "research_scope", "depth": "comprehensive"}
                ),
                AgentHandoff(
                    from_agent=AgentType.RESEARCH,
                    to_agent=AgentType.BUSINESS_INTELLIGENCE,
                    stage=WorkflowStage.RESPONSE_SYNTHESIS,
                    condition="analysis_required",
                    data_transfer={"raw_data": "research_results", "context": "business_context"}
                )
            ]
        }

    def _init_mcp_servers(self) -> dict[str, dict[str, Any]]:
        """Initialize MCP server configuration for agent routing"""
        return {
            # Core Intelligence Servers
            "ai_memory": {
                "port": 9000,
                "agent_type": AgentType.SOPHIA_INTELLIGENCE,
                "capabilities": ["memory_storage", "context_retrieval", "pattern_matching"]
            },
            "codacy": {
                "port": 3008,
                "agent_type": AgentType.CODE_DEVELOPMENT,
                "capabilities": ["code_quality", "security_analysis", "refactoring"]
            },
            "github": {
                "port": 9003,
                "agent_type": AgentType.CODE_DEVELOPMENT,
                "capabilities": ["repository_management", "pr_creation", "code_review"]
            },
            
            # Business Intelligence Servers
            "hubspot": {
                "port": 9006,
                "agent_type": AgentType.BUSINESS_INTELLIGENCE,
                "capabilities": ["crm_data", "sales_analytics", "customer_insights"]
            },
            "gong": {
                "port": 9007,
                "agent_type": AgentType.BUSINESS_INTELLIGENCE,
                "capabilities": ["call_analysis", "conversation_intelligence", "sales_coaching"]
            },
            "slack": {
                "port": 9005,
                "agent_type": AgentType.INTEGRATION,
                "capabilities": ["team_communication", "notification_management", "workflow_integration"]
            },
            
            # Infrastructure Servers
            "lambda_labs": {
                "port": 9012,
                "agent_type": AgentType.INFRASTRUCTURE,
                "capabilities": ["gpu_management", "instance_scaling", "resource_optimization"]
            },
            "pulumi": {
                "port": 9011,
                "agent_type": AgentType.INFRASTRUCTURE,
                "capabilities": ["infrastructure_as_code", "deployment_management", "configuration_management"]
            },
            
            # Research and Integration Servers
            "portkey_admin": {
                "port": 9013,
                "agent_type": AgentType.RESEARCH,
                "capabilities": ["llm_routing", "model_optimization", "cost_management"]
            },
            "openrouter_search": {
                "port": 9014,
                "agent_type": AgentType.RESEARCH,
                "capabilities": ["model_selection", "performance_optimization", "cost_analysis"]
            }
        }

    async def execute_workflow(
        self,
        user_input: str,
        workflow_type: str,
        context: dict[str, Any] | None = None,
        parallel_execution: bool = True
    ) -> WorkflowResult:
        """
        Execute multi-agent workflow with intelligent routing
        
        Args:
            user_input: User's request
            workflow_type: Type of workflow to execute
            context: Additional context for the workflow
            parallel_execution: Whether to enable parallel agent execution
            
        Returns:
            WorkflowResult with execution details and results
        """
        start_time = time.time()
        agent_chain = []
        token_usage = {"total": 0, "by_agent": {}}
        
        try:
            # Step 1: Intent Classification using Sophia Intelligence
            intent_result = await self._classify_intent(user_input)
            agent_chain.append("sophia_intelligence")
            
            # Step 2: Load appropriate documentation context
            documentation_context = await self._load_documentation_context(
                intent_result["complexity"], 
                intent_result["task_type"]
            )
            
            # Step 3: Execute workflow based on classification
            if workflow_type not in self.agent_workflows:
                raise ValueError(f"Unknown workflow type: {workflow_type}")
                
            workflow_result = await self._execute_agent_chain(
                self.agent_workflows[workflow_type],
                user_input,
                {
                    "intent": intent_result,
                    "documentation": documentation_context,
                    **(context or {})
                },
                parallel_execution
            )
            
            agent_chain.extend(workflow_result["agent_chain"])
            token_usage["total"] += workflow_result["token_usage"]
            
            # Step 4: Response Synthesis
            final_result = await self._synthesize_response(
                workflow_result["results"],
                intent_result,
                user_input
            )
            
            execution_time = time.time() - start_time
            
            # Track performance metrics
            self._update_performance_metrics(
                workflow_type, execution_time, token_usage["total"], True
            )
            
            return WorkflowResult(
                success=True,
                result=final_result,
                metadata={
                    "workflow_type": workflow_type,
                    "intent": intent_result,
                    "execution_mode": "parallel" if parallel_execution else "sequential"
                },
                execution_time=execution_time,
                agent_chain=agent_chain,
                token_usage=token_usage
            )
            
        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            execution_time = time.time() - start_time
            
            self._update_performance_metrics(
                workflow_type, execution_time, token_usage["total"], False
            )
            
            return WorkflowResult(
                success=False,
                result=f"Error: {str(e)}",
                metadata={"error": str(e), "workflow_type": workflow_type},
                execution_time=execution_time,
                agent_chain=agent_chain,
                token_usage=token_usage
            )

    async def _classify_intent(self, user_input: str) -> dict[str, Any]:
        """Classify user intent using Snowflake Cortex"""
        classification_prompt = f"""
        Classify this user request for the Sophia AI system:
        
        Request: {user_input}
        
        Classify:
        1. Task complexity: simple, moderate, complex, architecture
        2. Task type: code_generation, business_intelligence, infrastructure, research, integration
        3. Required agents: List of agent types needed
        4. Parallel execution: Whether tasks can be executed in parallel
        
        Return JSON format.
        """
        
        result = ""
        async for chunk in self.llm_service.complete(
            classification_prompt,
            TaskType.BUSINESS_INTELLIGENCE,
            stream=False
        ):
            result += chunk
            
        try:
            return json.loads(result)
        except json.JSONDecodeError:
            # Fallback classification
            return {
                "task_complexity": "moderate",
                "task_type": "code_generation",
                "required_agents": ["sophia_intelligence", "code_development"],
                "parallel_execution": True
            }

    async def _load_documentation_context(
        self, complexity: str, task_type: str
    ) -> dict[str, Any]:
        """Load appropriate documentation context based on task complexity"""
        if not self.documentation_loader:
            return {}
            
        # Implement 3-tier documentation loading
        tiers_to_load = []
        
        if complexity in ["architecture", "complex"]:
            tiers_to_load = [1, 2, 3]  # Foundation + Component + Feature
        elif complexity == "moderate":
            tiers_to_load = [2, 3]  # Component + Feature
        else:
            tiers_to_load = [3]  # Feature only
            
        context = {}
        for tier in tiers_to_load:
            tier_context = await self.documentation_loader.load_tier(tier, task_type)
            context[f"tier_{tier}"] = tier_context
            
        return context

    async def _execute_agent_chain(
        self,
        workflow: list[AgentHandoff],
        user_input: str,
        context: dict[str, Any],
        parallel_execution: bool
    ) -> dict[str, Any]:
        """Execute agent chain with handoffs"""
        results = {}
        agent_chain = []
        token_usage = 0
        
        if parallel_execution:
            # Execute compatible agents in parallel
            parallel_tasks = []
            sequential_tasks = []
            
            for handoff in workflow:
                if handoff.condition == "requires_previous_result":
                    sequential_tasks.append(handoff)
                else:
                    parallel_tasks.append(handoff)
            
            # Execute parallel tasks
            if parallel_tasks:
                parallel_results = await asyncio.gather(*[
                    self._execute_agent_task(handoff, user_input, context)
                    for handoff in parallel_tasks
                ])
                
                for i, result in enumerate(parallel_results):
                    agent_name = parallel_tasks[i].to_agent.value
                    results[agent_name] = result
                    agent_chain.append(agent_name)
                    token_usage += result.get("token_usage", 0)
            
            # Execute sequential tasks
            for handoff in sequential_tasks:
                result = await self._execute_agent_task(handoff, user_input, {**context, **results})
                agent_name = handoff.to_agent.value
                results[agent_name] = result
                agent_chain.append(agent_name)
                token_usage += result.get("token_usage", 0)
        else:
            # Sequential execution
            for handoff in workflow:
                result = await self._execute_agent_task(handoff, user_input, {**context, **results})
                agent_name = handoff.to_agent.value
                results[agent_name] = result
                agent_chain.append(agent_name)
                token_usage += result.get("token_usage", 0)
        
        return {
            "results": results,
            "agent_chain": agent_chain,
            "token_usage": token_usage
        }

    async def _execute_agent_task(
        self, handoff: AgentHandoff, user_input: str, context: dict[str, Any]
    ) -> dict[str, Any]:
        """Execute individual agent task"""
        agent_type = handoff.to_agent
        
        # Route to appropriate MCP server or LLM service
        if agent_type == AgentType.SOPHIA_INTELLIGENCE:
            return await self._execute_sophia_intelligence_task(user_input, context)
        elif agent_type == AgentType.CODE_DEVELOPMENT:
            return await self._execute_code_development_task(user_input, context)
        elif agent_type == AgentType.BUSINESS_INTELLIGENCE:
            return await self._execute_business_intelligence_task(user_input, context)
        elif agent_type == AgentType.INFRASTRUCTURE:
            return await self._execute_infrastructure_task(user_input, context)
        elif agent_type == AgentType.RESEARCH:
            return await self._execute_research_task(user_input, context)
        else:
            return await self._execute_integration_task(user_input, context)

    async def _execute_sophia_intelligence_task(
        self, user_input: str, context: dict[str, Any]
    ) -> dict[str, Any]:
        """Execute Sophia Intelligence agent task"""
        prompt = f"""
        As Sophia AI's central intelligence, analyze this request:
        
        User Input: {user_input}
        Context: {json.dumps(context, indent=2)}
        
        Provide:
        1. Detailed analysis
        2. Recommended approach
        3. Next steps
        4. Required resources
        """
        
        result = ""
        async for chunk in self.llm_service.complete(
            prompt,
            TaskType.BUSINESS_INTELLIGENCE,
            stream=False
        ):
            result += chunk
            
        return {
            "agent": "sophia_intelligence",
            "result": result,
            "token_usage": len(prompt.split()) + len(result.split()),
            "timestamp": datetime.utcnow().isoformat()
        }

    async def _execute_code_development_task(
        self, user_input: str, context: dict[str, Any]
    ) -> dict[str, Any]:
        """Execute Code Development agent task"""
        prompt = f"""
        As a code development specialist, handle this request:
        
        Request: {user_input}
        Context: {json.dumps(context, indent=2)}
        
        Generate:
        1. Code implementation
        2. Tests
        3. Documentation
        4. Integration patterns
        """
        
        result = ""
        async for chunk in self.llm_service.complete(
            prompt,
            TaskType.CODE_GENERATION,
            stream=False
        ):
            result += chunk
            
        return {
            "agent": "code_development",
            "result": result,
            "token_usage": len(prompt.split()) + len(result.split()),
            "timestamp": datetime.utcnow().isoformat()
        }

    async def _execute_business_intelligence_task(
        self, user_input: str, context: dict[str, Any]
    ) -> dict[str, Any]:
        """Execute Business Intelligence agent task"""
        prompt = f"""
        As a business intelligence specialist, analyze:
        
        Request: {user_input}
        Context: {json.dumps(context, indent=2)}
        
        Provide:
        1. Business insights
        2. Data analysis
        3. Recommendations
        4. Metrics and KPIs
        """
        
        result = ""
        async for chunk in self.llm_service.complete(
            prompt,
            TaskType.BUSINESS_INTELLIGENCE,
            stream=False
        ):
            result += chunk
            
        return {
            "agent": "business_intelligence",
            "result": result,
            "token_usage": len(prompt.split()) + len(result.split()),
            "timestamp": datetime.utcnow().isoformat()
        }

    async def _execute_infrastructure_task(
        self, user_input: str, context: dict[str, Any]
    ) -> dict[str, Any]:
        """Execute Infrastructure agent task"""
        prompt = f"""
        As an infrastructure specialist, handle:
        
        Request: {user_input}
        Context: {json.dumps(context, indent=2)}
        
        Provide:
        1. Infrastructure analysis
        2. Deployment strategy
        3. Security considerations
        4. Monitoring setup
        """
        
        result = ""
        async for chunk in self.llm_service.complete(
            prompt,
            TaskType.DATA_ANALYSIS,
            stream=False
        ):
            result += chunk
            
        return {
            "agent": "infrastructure",
            "result": result,
            "token_usage": len(prompt.split()) + len(result.split()),
            "timestamp": datetime.utcnow().isoformat()
        }

    async def _execute_research_task(
        self, user_input: str, context: dict[str, Any]
    ) -> dict[str, Any]:
        """Execute Research agent task"""
        prompt = f"""
        As a research specialist, investigate:
        
        Request: {user_input}
        Context: {json.dumps(context, indent=2)}
        
        Provide:
        1. Research findings
        2. Market analysis
        3. Competitive landscape
        4. Recommendations
        """
        
        result = ""
        async for chunk in self.llm_service.complete(
            prompt,
            TaskType.DOCUMENT_SUMMARY,
            stream=False
        ):
            result += chunk
            
        return {
            "agent": "research",
            "result": result,
            "token_usage": len(prompt.split()) + len(result.split()),
            "timestamp": datetime.utcnow().isoformat()
        }

    async def _execute_integration_task(
        self, user_input: str, context: dict[str, Any]
    ) -> dict[str, Any]:
        """Execute Integration agent task"""
        prompt = f"""
        As an integration specialist, handle:
        
        Request: {user_input}
        Context: {json.dumps(context, indent=2)}
        
        Provide:
        1. Integration strategy
        2. API connections
        3. Data flow design
        4. Error handling
        """
        
        result = ""
        async for chunk in self.llm_service.complete(
            prompt,
            TaskType.CODE_GENERATION,
            stream=False
        ):
            result += chunk
            
        return {
            "agent": "integration",
            "result": result,
            "token_usage": len(prompt.split()) + len(result.split()),
            "timestamp": datetime.utcnow().isoformat()
        }

    async def _synthesize_response(
        self, results: dict[str, Any], intent: dict[str, Any], user_input: str
    ) -> str:
        """Synthesize final response from agent results"""
        synthesis_prompt = f"""
        Synthesize a comprehensive response from these agent results:
        
        Original Request: {user_input}
        Intent: {json.dumps(intent, indent=2)}
        Agent Results: {json.dumps(results, indent=2)}
        
        Create a unified, actionable response that addresses the user's request.
        """
        
        result = ""
        async for chunk in self.llm_service.complete(
            synthesis_prompt,
            TaskType.CHAT_CONVERSATION,
            stream=False
        ):
            result += chunk
            
        return result

    async def _init_documentation_loader(self):
        """Initialize documentation loader service"""
        try:
            from backend.services.documentation_loader_service import DocumentationLoaderService
            loader = DocumentationLoaderService()
            await loader.initialize()
            return loader
        except ImportError:
            logger.warning("DocumentationLoaderService not available")
            return None

    def _update_performance_metrics(
        self, workflow_type: str, execution_time: float, token_usage: int, success: bool
    ):
        """Update performance metrics for monitoring"""
        if workflow_type not in self.performance_metrics:
            self.performance_metrics[workflow_type] = {
                "total_executions": 0,
                "successful_executions": 0,
                "average_execution_time": 0,
                "total_token_usage": 0
            }
        
        metrics = self.performance_metrics[workflow_type]
        metrics["total_executions"] += 1
        
        if success:
            metrics["successful_executions"] += 1
            
        # Update running averages
        metrics["average_execution_time"] = (
            (metrics["average_execution_time"] * (metrics["total_executions"] - 1) + execution_time)
            / metrics["total_executions"]
        )
        
        metrics["total_token_usage"] += token_usage

    async def get_performance_metrics(self) -> dict[str, Any]:
        """Get orchestrator performance metrics"""
        return {
            "orchestrator_status": "active",
            "workflow_metrics": self.performance_metrics,
            "available_workflows": list(self.agent_workflows.keys()),
            "mcp_servers": len(self.mcp_servers),
            "llm_service_status": self.llm_service.initialized
        }

    async def health_check(self) -> dict[str, Any]:
        """Health check for the orchestrator"""
        return {
            "service": "sophia_agent_orchestrator",
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "capabilities": [
                "Multi-agent workflow orchestration",
                "Parallel agent execution",
                "Intelligent documentation loading",
                "Performance monitoring",
                "Claude-Code-Development-Kit patterns"
            ],
            "metrics": await self.get_performance_metrics()
        }


# Global orchestrator instance
_orchestrator_instance = None


async def get_sophia_agent_orchestrator() -> SophiaAgentOrchestrator:
    """Get singleton orchestrator instance"""
    global _orchestrator_instance
    if _orchestrator_instance is None:
        _orchestrator_instance = SophiaAgentOrchestrator()
        await _orchestrator_instance.initialize()
    return _orchestrator_instance