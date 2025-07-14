"""
🤖 ADVANCED MCP ORCHESTRATION ENGINE
Intelligent agent routing and multi-agent collaboration leveraging Phase 2.1 memory intelligence

Created: July 14, 2025
Phase: 2.2 - AI Agent Orchestration Mastery
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import uuid
from collections import defaultdict, deque

from ..services.advanced_hybrid_search_service import AdvancedHybridSearchService, SearchContext, BusinessInsights
from ..services.adaptive_memory_system import AdaptiveMemorySystem, UserFeedback, FeedbackType
from ..services.payready_business_intelligence import PayReadyBusinessIntelligence, BusinessContext, BusinessIntelligenceLayer
from ..core.truthful_config import get_real_qdrant_config

logger = logging.getLogger(__name__)

class TaskPriority(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class TaskComplexity(Enum):
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    ENTERPRISE = "enterprise"

class AgentCapability(Enum):
    CUSTOMER_INTELLIGENCE = "customer_intelligence"
    SALES_OPTIMIZATION = "sales_optimization"
    MARKET_RESEARCH = "market_research"
    FINANCIAL_ANALYSIS = "financial_analysis"
    WORKFLOW_AUTOMATION = "workflow_automation"
    DATA_ANALYSIS = "data_analysis"
    CONTENT_GENERATION = "content_generation"
    INTEGRATION_MANAGEMENT = "integration_management"

class OrchestrationStrategy(Enum):
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    PIPELINE = "pipeline"
    ADAPTIVE = "adaptive"

@dataclass
class BusinessTask:
    """Business task for agent orchestration"""
    id: str
    title: str
    description: str
    business_domain: str
    priority: TaskPriority
    complexity: TaskComplexity
    required_capabilities: List[AgentCapability]
    context: BusinessContext
    deadline: Optional[datetime] = None
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class SubTask:
    """Sub-task for decomposed business tasks"""
    id: str
    parent_task_id: str
    title: str
    description: str
    required_capability: AgentCapability
    priority: TaskPriority
    estimated_duration: int  # minutes
    context: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)

@dataclass
class MCPAgent:
    """MCP Agent definition"""
    id: str
    name: str
    capabilities: List[AgentCapability]
    endpoint: str
    port: int
    health_status: str = "unknown"
    current_load: float = 0.0
    performance_score: float = 0.8
    specialization_score: Dict[AgentCapability, float] = field(default_factory=dict)
    last_health_check: Optional[datetime] = None
    total_tasks_completed: int = 0
    average_completion_time: float = 0.0

@dataclass
class TaskExecution:
    """Task execution tracking"""
    task_id: str
    agent_id: str
    status: str  # pending, running, completed, failed
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    performance_metrics: Dict[str, Any] = field(default_factory=dict)

@dataclass
class OrchestrationResult:
    """Result of task orchestration"""
    task_id: str
    status: str
    results: Dict[str, Any]
    agent_executions: List[TaskExecution]
    total_duration: float
    business_impact: str
    confidence_score: float
    recommendations: List[str]
    created_at: datetime = field(default_factory=datetime.now)

class AdvancedMCPOrchestrationEngine:
    """
    Advanced MCP orchestration engine with:
    - Intelligent agent routing using business intelligence
    - Context-aware task decomposition leveraging memory insights
    - Multi-agent collaboration with performance optimization
    - Real-time learning and adaptation
    """
    
    def __init__(self, hybrid_search: AdvancedHybridSearchService, 
                 adaptive_memory: AdaptiveMemorySystem,
                 business_intelligence: PayReadyBusinessIntelligence):
        self.hybrid_search = hybrid_search
        self.adaptive_memory = adaptive_memory
        self.business_intelligence = business_intelligence
        
        # Agent registry and management
        self.agent_registry: Dict[str, MCPAgent] = {}
        self.agent_capabilities: Dict[AgentCapability, List[str]] = defaultdict(list)
        
        # Task management
        self.active_tasks: Dict[str, BusinessTask] = {}
        self.task_queue: deque = deque()
        self.execution_history: List[TaskExecution] = []
        
        # Orchestration intelligence
        self.orchestration_patterns: Dict[str, Any] = {}
        self.performance_analytics: Dict[str, Any] = {}
        self.learning_insights: List[Dict[str, Any]] = []
        
        # Configuration
        self.max_concurrent_tasks = 10
        self.max_agent_load = 0.8
        self.performance_threshold = 0.7
        
        self.logger = logging.getLogger(__name__)
        
    async def initialize(self):
        """Initialize the advanced MCP orchestration engine"""
        try:
            # Initialize agent registry
            await self._initialize_agent_registry()
            
            # Start health monitoring
            asyncio.create_task(self._continuous_health_monitoring())
            
            # Start performance analytics
            asyncio.create_task(self._continuous_performance_analytics())
            
            # Start orchestration optimization
            asyncio.create_task(self._continuous_orchestration_optimization())
            
            self.logger.info("✅ Advanced MCP Orchestration Engine initialized successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Advanced MCP Orchestration Engine: {e}")
            raise

    async def orchestrate_business_task(self, task: BusinessTask) -> OrchestrationResult:
        """
        Main orchestration method that leverages Phase 2.1 intelligence
        """
        try:
            self.logger.info(f"🎯 Orchestrating business task: {task.title}")
            
            # 1. Task analysis and decomposition using business intelligence
            subtasks = await self._decompose_business_task(task)
            
            # 2. Agent selection using performance analytics and memory insights
            selected_agents = await self._select_optimal_agents(subtasks, task)
            
            # 3. Context enrichment using hybrid search and business intelligence
            enriched_context = await self._enrich_with_intelligence_context(task, subtasks)
            
            # 4. Orchestration strategy selection
            strategy = await self._select_orchestration_strategy(task, subtasks, selected_agents)
            
            # 5. Coordinated execution with real-time monitoring
            execution_results = await self._execute_coordinated_agents(
                selected_agents, subtasks, enriched_context, strategy
            )
            
            # 6. Result synthesis and quality validation
            final_result = await self._synthesize_and_validate_results(
                task, execution_results, enriched_context
            )
            
            # 7. Learning and optimization
            await self._learn_from_orchestration(task, execution_results, final_result)
            
            self.logger.info(f"✅ Task orchestration completed: {task.title}")
            return final_result
            
        except Exception as e:
            self.logger.error(f"❌ Task orchestration failed for {task.title}: {e}")
            raise

    async def _decompose_business_task(self, task: BusinessTask) -> List[SubTask]:
        """
        Decompose business task using business intelligence insights
        """
        try:
            # Use business intelligence to understand task domain
            business_insights = await self.business_intelligence.intelligent_business_search(
                task.description,
                task.context
            )
            
            # Use hybrid search to find similar task patterns
            search_context = SearchContext(
                user_id=task.context.user_role,
                session_id=f"orchestration_{task.id}",
                business_domain=task.business_domain
            )
            
            similar_tasks = await self.hybrid_search.hybrid_search(
                f"task decomposition {task.description}",
                search_context
            )
            
            # Analyze task complexity and required capabilities
            subtasks = []
            
            if task.complexity == TaskComplexity.SIMPLE:
                # Single subtask for simple tasks
                subtasks.append(SubTask(
                    id=f"{task.id}_main",
                    parent_task_id=task.id,
                    title=task.title,
                    description=task.description,
                    required_capability=task.required_capabilities[0] if task.required_capabilities else AgentCapability.DATA_ANALYSIS,
                    priority=task.priority,
                    estimated_duration=15
                ))
            
            elif task.complexity == TaskComplexity.MODERATE:
                # 2-3 subtasks for moderate complexity
                if AgentCapability.CUSTOMER_INTELLIGENCE in task.required_capabilities:
                    subtasks.extend([
                        SubTask(
                            id=f"{task.id}_analysis",
                            parent_task_id=task.id,
                            title=f"Customer Analysis - {task.title}",
                            description=f"Analyze customer data for {task.description}",
                            required_capability=AgentCapability.CUSTOMER_INTELLIGENCE,
                            priority=task.priority,
                            estimated_duration=20
                        ),
                        SubTask(
                            id=f"{task.id}_insights",
                            parent_task_id=task.id,
                            title=f"Business Insights - {task.title}",
                            description=f"Generate business insights for {task.description}",
                            required_capability=AgentCapability.DATA_ANALYSIS,
                            priority=task.priority,
                            estimated_duration=15,
                            dependencies=[f"{task.id}_analysis"]
                        )
                    ])
                
                elif AgentCapability.SALES_OPTIMIZATION in task.required_capabilities:
                    subtasks.extend([
                        SubTask(
                            id=f"{task.id}_sales_analysis",
                            parent_task_id=task.id,
                            title=f"Sales Analysis - {task.title}",
                            description=f"Analyze sales performance for {task.description}",
                            required_capability=AgentCapability.SALES_OPTIMIZATION,
                            priority=task.priority,
                            estimated_duration=25
                        ),
                        SubTask(
                            id=f"{task.id}_recommendations",
                            parent_task_id=task.id,
                            title=f"Sales Recommendations - {task.title}",
                            description=f"Generate sales recommendations for {task.description}",
                            required_capability=AgentCapability.DATA_ANALYSIS,
                            priority=task.priority,
                            estimated_duration=15,
                            dependencies=[f"{task.id}_sales_analysis"]
                        )
                    ])
            
            elif task.complexity in [TaskComplexity.COMPLEX, TaskComplexity.ENTERPRISE]:
                # 4+ subtasks for complex tasks
                subtasks.extend([
                    SubTask(
                        id=f"{task.id}_research",
                        parent_task_id=task.id,
                        title=f"Research Phase - {task.title}",
                        description=f"Research and data gathering for {task.description}",
                        required_capability=AgentCapability.MARKET_RESEARCH,
                        priority=task.priority,
                        estimated_duration=30
                    ),
                    SubTask(
                        id=f"{task.id}_analysis",
                        parent_task_id=task.id,
                        title=f"Analysis Phase - {task.title}",
                        description=f"Data analysis and processing for {task.description}",
                        required_capability=AgentCapability.DATA_ANALYSIS,
                        priority=task.priority,
                        estimated_duration=25,
                        dependencies=[f"{task.id}_research"]
                    ),
                    SubTask(
                        id=f"{task.id}_intelligence",
                        parent_task_id=task.id,
                        title=f"Intelligence Phase - {task.title}",
                        description=f"Business intelligence generation for {task.description}",
                        required_capability=AgentCapability.CUSTOMER_INTELLIGENCE,
                        priority=task.priority,
                        estimated_duration=20,
                        dependencies=[f"{task.id}_analysis"]
                    ),
                    SubTask(
                        id=f"{task.id}_synthesis",
                        parent_task_id=task.id,
                        title=f"Synthesis Phase - {task.title}",
                        description=f"Result synthesis and recommendations for {task.description}",
                        required_capability=AgentCapability.CONTENT_GENERATION,
                        priority=task.priority,
                        estimated_duration=15,
                        dependencies=[f"{task.id}_intelligence"]
                    )
                ])
            
            # Enhance subtasks with business intelligence insights
            for subtask in subtasks:
                subtask.context = {
                    "business_insights": [insight.content for insight in business_insights.primary_insights[:3]],
                    "similar_patterns": [result.content for result in similar_tasks[:2]],
                    "business_domain": task.business_domain,
                    "priority_context": task.priority.value
                }
            
            self.logger.info(f"🔧 Decomposed task {task.title} into {len(subtasks)} subtasks")
            return subtasks
            
        except Exception as e:
            self.logger.error(f"❌ Task decomposition failed: {e}")
            return []

    async def _select_optimal_agents(self, subtasks: List[SubTask], task: BusinessTask) -> Dict[str, str]:
        """
        Select optimal agents using performance analytics and memory insights
        """
        try:
            agent_assignments = {}
            
            for subtask in subtasks:
                # Get agents with required capability
                capable_agents = self.agent_capabilities.get(subtask.required_capability, [])
                
                if not capable_agents:
                    self.logger.warning(f"No agents found for capability: {subtask.required_capability}")
                    continue
                
                # Score agents based on multiple factors
                agent_scores = {}
                
                for agent_id in capable_agents:
                    agent = self.agent_registry.get(agent_id)
                    if not agent:
                        continue
                    
                    # Base performance score
                    score = agent.performance_score
                    
                    # Specialization bonus
                    specialization = agent.specialization_score.get(subtask.required_capability, 0.5)
                    score += specialization * 0.3
                    
                    # Load penalty
                    load_penalty = agent.current_load * 0.4
                    score -= load_penalty
                    
                    # Health bonus
                    if agent.health_status == "healthy":
                        score += 0.2
                    elif agent.health_status == "degraded":
                        score -= 0.1
                    elif agent.health_status == "unhealthy":
                        score -= 0.5
                    
                    # Priority boost for critical tasks
                    if task.priority == TaskPriority.CRITICAL:
                        score += 0.15
                    
                    # Historical performance with similar tasks
                    historical_performance = await self._get_agent_historical_performance(
                        agent_id, subtask.required_capability
                    )
                    score += historical_performance * 0.2
                    
                    agent_scores[agent_id] = score
                
                # Select best agent
                if agent_scores:
                    best_agent = max(agent_scores, key=agent_scores.get)
                    agent_assignments[subtask.id] = best_agent
                    
                    # Update agent load
                    if best_agent in self.agent_registry:
                        estimated_load = subtask.estimated_duration / 60.0  # Convert to hours
                        self.agent_registry[best_agent].current_load += estimated_load
            
            self.logger.info(f"🎯 Selected {len(agent_assignments)} agents for task execution")
            return agent_assignments
            
        except Exception as e:
            self.logger.error(f"❌ Agent selection failed: {e}")
            return {}

    async def _enrich_with_intelligence_context(self, task: BusinessTask, subtasks: List[SubTask]) -> Dict[str, Any]:
        """
        Enrich task context using hybrid search and business intelligence
        """
        try:
            enriched_context = {
                "task_context": task.metadata,
                "business_intelligence": {},
                "memory_insights": {},
                "performance_context": {}
            }
            
            # Get business intelligence for task domain
            if task.business_domain == "customer_management":
                customer_insights = await self.business_intelligence._search_customer_intelligence(
                    task.description, task.context
                )
                enriched_context["business_intelligence"]["customer"] = {
                    "insights": [insight.content for insight in customer_insights.primary_insights[:5]],
                    "recommendations": customer_insights.actionable_recommendations,
                    "confidence": customer_insights.confidence_score
                }
            
            elif task.business_domain == "sales":
                sales_insights = await self.business_intelligence._search_sales_intelligence(
                    task.description, task.context
                )
                enriched_context["business_intelligence"]["sales"] = {
                    "insights": [insight.content for insight in sales_insights.primary_insights[:5]],
                    "recommendations": sales_insights.actionable_recommendations,
                    "confidence": sales_insights.confidence_score
                }
            
            elif task.business_domain == "market_intelligence":
                market_insights = await self.business_intelligence._search_market_intelligence(
                    task.description, task.context
                )
                enriched_context["business_intelligence"]["market"] = {
                    "insights": [insight.content for insight in market_insights.primary_insights[:5]],
                    "recommendations": market_insights.actionable_recommendations,
                    "confidence": market_insights.confidence_score
                }
            
            # Get memory insights using hybrid search
            search_context = SearchContext(
                user_id=task.context.user_role,
                session_id=f"orchestration_{task.id}",
                business_domain=task.business_domain
            )
            
            memory_results = await self.hybrid_search.hybrid_search(
                f"task execution patterns {task.description}",
                search_context
            )
            
            enriched_context["memory_insights"] = {
                "similar_tasks": [result.content for result in memory_results[:3]],
                "execution_patterns": [result.relevance_explanation for result in memory_results[:3]],
                "confidence_scores": [result.confidence for result in memory_results[:3]]
            }
            
            # Get performance context
            enriched_context["performance_context"] = {
                "task_complexity": task.complexity.value,
                "priority_level": task.priority.value,
                "estimated_duration": sum(subtask.estimated_duration for subtask in subtasks),
                "required_capabilities": [cap.value for cap in task.required_capabilities]
            }
            
            return enriched_context
            
        except Exception as e:
            self.logger.error(f"❌ Context enrichment failed: {e}")
            return {"error": str(e)}

    async def _select_orchestration_strategy(self, task: BusinessTask, subtasks: List[SubTask], 
                                           agent_assignments: Dict[str, str]) -> OrchestrationStrategy:
        """
        Select optimal orchestration strategy based on task characteristics
        """
        try:
            # Analyze task dependencies
            has_dependencies = any(subtask.dependencies for subtask in subtasks)
            
            # Analyze agent availability
            agent_availability = len(set(agent_assignments.values()))
            
            # Analyze task priority and complexity
            if task.priority == TaskPriority.CRITICAL:
                if has_dependencies:
                    return OrchestrationStrategy.PIPELINE
                else:
                    return OrchestrationStrategy.PARALLEL
            
            elif task.complexity == TaskComplexity.ENTERPRISE:
                return OrchestrationStrategy.ADAPTIVE
            
            elif has_dependencies:
                return OrchestrationStrategy.SEQUENTIAL
            
            elif agent_availability >= len(subtasks):
                return OrchestrationStrategy.PARALLEL
            
            else:
                return OrchestrationStrategy.SEQUENTIAL
                
        except Exception as e:
            self.logger.error(f"❌ Strategy selection failed: {e}")
            return OrchestrationStrategy.SEQUENTIAL

    async def _execute_coordinated_agents(self, agent_assignments: Dict[str, str], 
                                        subtasks: List[SubTask], enriched_context: Dict[str, Any],
                                        strategy: OrchestrationStrategy) -> List[TaskExecution]:
        """
        Execute agents using selected orchestration strategy
        """
        try:
            executions = []
            
            if strategy == OrchestrationStrategy.PARALLEL:
                # Execute all subtasks in parallel
                execution_tasks = []
                for subtask in subtasks:
                    if subtask.id in agent_assignments:
                        agent_id = agent_assignments[subtask.id]
                        task_coro = self._execute_agent_task(agent_id, subtask, enriched_context)
                        execution_tasks.append(task_coro)
                
                results = await asyncio.gather(*execution_tasks, return_exceptions=True)
                executions.extend([r for r in results if isinstance(r, TaskExecution)])
            
            elif strategy == OrchestrationStrategy.SEQUENTIAL:
                # Execute subtasks sequentially
                for subtask in subtasks:
                    if subtask.id in agent_assignments:
                        agent_id = agent_assignments[subtask.id]
                        execution = await self._execute_agent_task(agent_id, subtask, enriched_context)
                        executions.append(execution)
            
            elif strategy == OrchestrationStrategy.PIPELINE:
                # Execute with dependency management
                completed_tasks = set()
                remaining_tasks = subtasks.copy()
                
                while remaining_tasks:
                    # Find tasks with satisfied dependencies
                    ready_tasks = [
                        task for task in remaining_tasks 
                        if all(dep in completed_tasks for dep in task.dependencies)
                    ]
                    
                    if not ready_tasks:
                        break  # Avoid infinite loop
                    
                    # Execute ready tasks in parallel
                    execution_tasks = []
                    for subtask in ready_tasks:
                        if subtask.id in agent_assignments:
                            agent_id = agent_assignments[subtask.id]
                            task_coro = self._execute_agent_task(agent_id, subtask, enriched_context)
                            execution_tasks.append(task_coro)
                    
                    results = await asyncio.gather(*execution_tasks, return_exceptions=True)
                    batch_executions = [r for r in results if isinstance(r, TaskExecution)]
                    executions.extend(batch_executions)
                    
                    # Update completed tasks
                    for execution in batch_executions:
                        if execution.status == "completed":
                            completed_tasks.add(execution.task_id)
                    
                    # Remove completed tasks from remaining
                    remaining_tasks = [t for t in remaining_tasks if t.id not in completed_tasks]
            
            elif strategy == OrchestrationStrategy.ADAPTIVE:
                # Adaptive execution based on real-time performance
                executions = await self._execute_adaptive_orchestration(
                    agent_assignments, subtasks, enriched_context
                )
            
            return executions
            
        except Exception as e:
            self.logger.error(f"❌ Coordinated execution failed: {e}")
            return []

    async def _execute_agent_task(self, agent_id: str, subtask: SubTask, 
                                 enriched_context: Dict[str, Any]) -> TaskExecution:
        """
        Execute a single agent task with monitoring
        """
        try:
            execution = TaskExecution(
                task_id=subtask.id,
                agent_id=agent_id,
                status="pending",
                start_time=datetime.now()
            )
            
            # Simulate agent execution (would integrate with actual MCP servers)
            execution.status = "running"
            
            # Simulate processing time based on task complexity
            processing_time = subtask.estimated_duration / 60.0  # Convert to hours for simulation
            await asyncio.sleep(min(processing_time, 0.1))  # Cap at 0.1s for demo
            
            # Generate simulated results based on capability
            if subtask.required_capability == AgentCapability.CUSTOMER_INTELLIGENCE:
                result = {
                    "customer_analysis": "Customer health analysis completed",
                    "insights": enriched_context.get("business_intelligence", {}).get("customer", {}).get("insights", []),
                    "recommendations": ["Improve customer engagement", "Focus on retention"],
                    "confidence": 0.85
                }
            elif subtask.required_capability == AgentCapability.SALES_OPTIMIZATION:
                result = {
                    "sales_analysis": "Sales performance analysis completed",
                    "insights": enriched_context.get("business_intelligence", {}).get("sales", {}).get("insights", []),
                    "recommendations": ["Optimize sales funnel", "Improve conversion rates"],
                    "confidence": 0.82
                }
            elif subtask.required_capability == AgentCapability.MARKET_RESEARCH:
                result = {
                    "market_analysis": "Market research completed",
                    "insights": enriched_context.get("business_intelligence", {}).get("market", {}).get("insights", []),
                    "recommendations": ["Expand market presence", "Monitor competitors"],
                    "confidence": 0.78
                }
            else:
                result = {
                    "analysis": f"Task {subtask.title} completed",
                    "insights": ["General analysis completed"],
                    "recommendations": ["Continue monitoring"],
                    "confidence": 0.75
                }
            
            execution.status = "completed"
            execution.end_time = datetime.now()
            execution.result = result
            execution.performance_metrics = {
                "duration_minutes": subtask.estimated_duration,
                "quality_score": result.get("confidence", 0.75),
                "efficiency_score": 0.8
            }
            
            # Update agent performance
            if agent_id in self.agent_registry:
                agent = self.agent_registry[agent_id]
                agent.total_tasks_completed += 1
                agent.current_load = max(0, agent.current_load - (subtask.estimated_duration / 60.0))
            
            return execution
            
        except Exception as e:
            execution.status = "failed"
            execution.error = str(e)
            execution.end_time = datetime.now()
            self.logger.error(f"❌ Agent task execution failed: {e}")
            return execution

    async def _synthesize_and_validate_results(self, task: BusinessTask, 
                                             executions: List[TaskExecution],
                                             enriched_context: Dict[str, Any]) -> OrchestrationResult:
        """
        Synthesize results and validate quality
        """
        try:
            # Collect all results
            all_results = {}
            successful_executions = [e for e in executions if e.status == "completed"]
            
            for execution in successful_executions:
                all_results[execution.task_id] = execution.result
            
            # Synthesize insights
            synthesized_insights = []
            synthesized_recommendations = []
            
            for execution in successful_executions:
                if execution.result:
                    insights = execution.result.get("insights", [])
                    recommendations = execution.result.get("recommendations", [])
                    
                    synthesized_insights.extend(insights)
                    synthesized_recommendations.extend(recommendations)
            
            # Calculate overall confidence
            confidence_scores = [
                execution.result.get("confidence", 0.5) 
                for execution in successful_executions 
                if execution.result
            ]
            overall_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.5
            
            # Calculate total duration
            total_duration = sum(
                (execution.end_time - execution.start_time).total_seconds()
                for execution in executions
                if execution.start_time and execution.end_time
            ) / 60.0  # Convert to minutes
            
            # Determine business impact
            business_impact = self._assess_business_impact(task, all_results, overall_confidence)
            
            # Generate final recommendations
            final_recommendations = list(set(synthesized_recommendations))[:5]  # Top 5 unique
            
            result = OrchestrationResult(
                task_id=task.id,
                status="completed" if len(successful_executions) > 0 else "failed",
                results={
                    "synthesized_insights": synthesized_insights[:10],  # Top 10
                    "business_recommendations": final_recommendations,
                    "detailed_results": all_results,
                    "execution_summary": {
                        "total_subtasks": len(executions),
                        "successful_subtasks": len(successful_executions),
                        "failed_subtasks": len(executions) - len(successful_executions)
                    }
                },
                agent_executions=executions,
                total_duration=total_duration,
                business_impact=business_impact,
                confidence_score=overall_confidence,
                recommendations=final_recommendations
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Result synthesis failed: {e}")
            return OrchestrationResult(
                task_id=task.id,
                status="failed",
                results={"error": str(e)},
                agent_executions=executions,
                total_duration=0,
                business_impact="Unable to assess due to error",
                confidence_score=0.0,
                recommendations=["Review and retry task execution"]
            )

    async def _learn_from_orchestration(self, task: BusinessTask, executions: List[TaskExecution], 
                                      result: OrchestrationResult):
        """
        Learn from orchestration execution for future optimization
        """
        try:
            # Store orchestration pattern
            pattern_key = f"{task.business_domain}_{task.complexity.value}_{task.priority.value}"
            
            if pattern_key not in self.orchestration_patterns:
                self.orchestration_patterns[pattern_key] = {
                    "successful_executions": 0,
                    "total_executions": 0,
                    "average_duration": 0,
                    "average_confidence": 0,
                    "best_agents": defaultdict(int),
                    "common_issues": []
                }
            
            pattern = self.orchestration_patterns[pattern_key]
            pattern["total_executions"] += 1
            
            if result.status == "completed":
                pattern["successful_executions"] += 1
                
                # Update averages
                pattern["average_duration"] = (
                    pattern["average_duration"] * (pattern["successful_executions"] - 1) + 
                    result.total_duration
                ) / pattern["successful_executions"]
                
                pattern["average_confidence"] = (
                    pattern["average_confidence"] * (pattern["successful_executions"] - 1) + 
                    result.confidence_score
                ) / pattern["successful_executions"]
                
                # Track best performing agents
                for execution in executions:
                    if execution.status == "completed":
                        pattern["best_agents"][execution.agent_id] += 1
            
            # Update agent performance scores
            for execution in executions:
                if execution.agent_id in self.agent_registry:
                    agent = self.agent_registry[execution.agent_id]
                    
                    if execution.status == "completed":
                        # Boost performance score for successful tasks
                        quality_score = execution.performance_metrics.get("quality_score", 0.75)
                        agent.performance_score = (agent.performance_score * 0.9) + (quality_score * 0.1)
                    else:
                        # Slight penalty for failed tasks
                        agent.performance_score = max(0.1, agent.performance_score * 0.95)
            
            # Store learning insights
            learning_insight = {
                "task_pattern": pattern_key,
                "execution_time": datetime.now().isoformat(),
                "success_rate": pattern["successful_executions"] / pattern["total_executions"],
                "performance_insights": {
                    "duration": result.total_duration,
                    "confidence": result.confidence_score,
                    "business_impact": result.business_impact
                },
                "optimization_opportunities": await self._identify_optimization_opportunities(
                    task, executions, result
                )
            }
            
            self.learning_insights.append(learning_insight)
            
            # Keep only recent insights
            if len(self.learning_insights) > 1000:
                self.learning_insights = self.learning_insights[-1000:]
            
            self.logger.info(f"📚 Learning completed for task: {task.title}")
            
        except Exception as e:
            self.logger.error(f"❌ Learning from orchestration failed: {e}")

    # Helper methods
    async def _initialize_agent_registry(self):
        """Initialize agent registry with available MCP servers"""
        try:
            # Sample agent registry (would be populated from actual MCP server discovery)
            sample_agents = [
                MCPAgent(
                    id="customer_intelligence_agent",
                    name="Customer Intelligence Agent",
                    capabilities=[AgentCapability.CUSTOMER_INTELLIGENCE, AgentCapability.DATA_ANALYSIS],
                    endpoint="localhost",
                    port=9006,
                    health_status="healthy",
                    performance_score=0.85,
                    specialization_score={
                        AgentCapability.CUSTOMER_INTELLIGENCE: 0.9,
                        AgentCapability.DATA_ANALYSIS: 0.7
                    }
                ),
                MCPAgent(
                    id="sales_optimization_agent",
                    name="Sales Optimization Agent",
                    capabilities=[AgentCapability.SALES_OPTIMIZATION, AgentCapability.DATA_ANALYSIS],
                    endpoint="localhost",
                    port=9007,
                    health_status="healthy",
                    performance_score=0.82,
                    specialization_score={
                        AgentCapability.SALES_OPTIMIZATION: 0.88,
                        AgentCapability.DATA_ANALYSIS: 0.75
                    }
                ),
                MCPAgent(
                    id="market_research_agent",
                    name="Market Research Agent",
                    capabilities=[AgentCapability.MARKET_RESEARCH, AgentCapability.DATA_ANALYSIS],
                    endpoint="localhost",
                    port=9008,
                    health_status="healthy",
                    performance_score=0.78,
                    specialization_score={
                        AgentCapability.MARKET_RESEARCH: 0.85,
                        AgentCapability.DATA_ANALYSIS: 0.72
                    }
                ),
                MCPAgent(
                    id="financial_analysis_agent",
                    name="Financial Analysis Agent",
                    capabilities=[AgentCapability.FINANCIAL_ANALYSIS, AgentCapability.DATA_ANALYSIS],
                    endpoint="localhost",
                    port=9009,
                    health_status="healthy",
                    performance_score=0.80,
                    specialization_score={
                        AgentCapability.FINANCIAL_ANALYSIS: 0.87,
                        AgentCapability.DATA_ANALYSIS: 0.78
                    }
                ),
                MCPAgent(
                    id="workflow_automation_agent",
                    name="Workflow Automation Agent",
                    capabilities=[AgentCapability.WORKFLOW_AUTOMATION, AgentCapability.INTEGRATION_MANAGEMENT],
                    endpoint="localhost",
                    port=9010,
                    health_status="healthy",
                    performance_score=0.83,
                    specialization_score={
                        AgentCapability.WORKFLOW_AUTOMATION: 0.89,
                        AgentCapability.INTEGRATION_MANAGEMENT: 0.76
                    }
                )
            ]
            
            # Register agents
            for agent in sample_agents:
                self.agent_registry[agent.id] = agent
                
                # Build capability index
                for capability in agent.capabilities:
                    self.agent_capabilities[capability].append(agent.id)
            
            self.logger.info(f"✅ Initialized {len(sample_agents)} agents in registry")
            
        except Exception as e:
            self.logger.error(f"❌ Agent registry initialization failed: {e}")

    async def _get_agent_historical_performance(self, agent_id: str, capability: AgentCapability) -> float:
        """Get agent's historical performance for specific capability"""
        # Simulate historical performance lookup
        base_performance = 0.75
        
        if agent_id in self.agent_registry:
            agent = self.agent_registry[agent_id]
            specialization = agent.specialization_score.get(capability, 0.5)
            return min(1.0, base_performance + specialization * 0.2)
        
        return base_performance

    def _assess_business_impact(self, task: BusinessTask, results: Dict[str, Any], confidence: float) -> str:
        """Assess business impact of task completion"""
        if confidence >= 0.8:
            if task.priority == TaskPriority.CRITICAL:
                return "High business impact - Critical task completed with high confidence"
            elif task.complexity == TaskComplexity.ENTERPRISE:
                return "Significant business impact - Enterprise task completed successfully"
            else:
                return "Positive business impact - Task completed with good quality"
        elif confidence >= 0.6:
            return "Moderate business impact - Task completed with acceptable quality"
        else:
            return "Limited business impact - Task completed but quality concerns"

    async def _identify_optimization_opportunities(self, task: BusinessTask, 
                                                 executions: List[TaskExecution],
                                                 result: OrchestrationResult) -> List[str]:
        """Identify optimization opportunities for future tasks"""
        opportunities = []
        
        # Analyze execution times
        slow_executions = [e for e in executions if e.performance_metrics.get("duration_minutes", 0) > 30]
        if slow_executions:
            opportunities.append("Consider agent optimization for long-running tasks")
        
        # Analyze failure rates
        failed_executions = [e for e in executions if e.status == "failed"]
        if failed_executions:
            opportunities.append("Investigate and address task execution failures")
        
        # Analyze confidence scores
        if result.confidence_score < 0.7:
            opportunities.append("Improve task decomposition and agent selection for better results")
        
        # Analyze business impact
        if "Limited" in result.business_impact:
            opportunities.append("Enhance business context enrichment for better impact")
        
        return opportunities

    async def _continuous_health_monitoring(self):
        """Continuous health monitoring of agents"""
        while True:
            try:
                await asyncio.sleep(60)  # Check every minute
                
                for agent_id, agent in self.agent_registry.items():
                    # Simulate health check (would ping actual MCP servers)
                    try:
                        # Simulated health check
                        agent.health_status = "healthy"
                        agent.last_health_check = datetime.now()
                    except Exception as e:
                        agent.health_status = "unhealthy"
                        self.logger.warning(f"Agent {agent_id} health check failed: {e}")
                
            except Exception as e:
                self.logger.error(f"❌ Health monitoring error: {e}")

    async def _continuous_performance_analytics(self):
        """Continuous performance analytics and optimization"""
        while True:
            try:
                await asyncio.sleep(300)  # Analyze every 5 minutes
                
                # Analyze orchestration patterns
                await self._analyze_orchestration_patterns()
                
                # Update agent performance scores
                await self._update_agent_performance_scores()
                
                # Generate optimization recommendations
                await self._generate_optimization_recommendations()
                
            except Exception as e:
                self.logger.error(f"❌ Performance analytics error: {e}")

    async def _continuous_orchestration_optimization(self):
        """Continuous orchestration optimization based on learning"""
        while True:
            try:
                await asyncio.sleep(900)  # Optimize every 15 minutes
                
                # Optimize agent assignments based on performance
                await self._optimize_agent_assignments()
                
                # Optimize orchestration strategies
                await self._optimize_orchestration_strategies()
                
                # Clean up old data
                await self._cleanup_old_data()
                
            except Exception as e:
                self.logger.error(f"❌ Orchestration optimization error: {e}")

    async def _analyze_orchestration_patterns(self):
        """Analyze orchestration patterns for insights"""
        # This would analyze patterns and generate insights
        pass

    async def _update_agent_performance_scores(self):
        """Update agent performance scores based on recent performance"""
        # This would update performance scores based on recent executions
        pass

    async def _generate_optimization_recommendations(self):
        """Generate optimization recommendations"""
        # This would generate specific optimization recommendations
        pass

    async def _optimize_agent_assignments(self):
        """Optimize agent assignments based on performance data"""
        # This would optimize future agent assignments
        pass

    async def _optimize_orchestration_strategies(self):
        """Optimize orchestration strategies based on learning"""
        # This would optimize strategy selection
        pass

    async def _cleanup_old_data(self):
        """Clean up old orchestration data"""
        # Clean up old execution history
        cutoff_time = datetime.now() - timedelta(days=7)
        self.execution_history = [
            execution for execution in self.execution_history
            if execution.start_time and execution.start_time > cutoff_time
        ]

    async def _execute_adaptive_orchestration(self, agent_assignments: Dict[str, str], 
                                            subtasks: List[SubTask], 
                                            enriched_context: Dict[str, Any]) -> List[TaskExecution]:
        """Execute adaptive orchestration strategy"""
        # This would implement adaptive orchestration based on real-time conditions
        # For now, fall back to parallel execution
        return await self._execute_coordinated_agents(
            agent_assignments, subtasks, enriched_context, OrchestrationStrategy.PARALLEL
        ) 