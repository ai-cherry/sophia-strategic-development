#!/usr/bin/env python3
"""
Coding MCP Orchestrator Service - Week 2 Implementation
======================================================

Intelligent orchestrator that coordinates multiple MCP servers for optimal coding assistance:
- AI Memory (coding_memory_mcp_server) - Pattern storage and retrieval
- Codacy MCP - Code quality analysis and security scanning
- GitHub MCP - Repository management and issue tracking  
- Portkey Gateway - Intelligent LLM routing and optimization
- Lambda Labs - GPU-accelerated processing

Features:
- Intelligent task routing based on complexity and context
- Context-aware code generation with stored patterns
- Quality improvement loop with automatic code analysis
- Performance optimization through model selection
- Unified natural language interface

Date: January 15, 2025
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
import aiohttp

# Import our unified memory service
from backend.services.coding_mcp_unified_memory_service import (
    get_coding_memory_service,
    coding_memory_context,
    MemoryNamespace
)

from backend.core.auto_esc_config import get_config_value

logger = logging.getLogger(__name__)

class TaskComplexity(Enum):
    """Task complexity levels for intelligent routing"""
    SIMPLE = "simple"           # Basic queries, simple patterns
    MODERATE = "moderate"       # Code generation, refactoring
    COMPLEX = "complex"         # Architecture decisions, complex debugging
    CRITICAL = "critical"       # Security analysis, performance optimization

class MCPServerType(Enum):
    """Available MCP servers for orchestration"""
    AI_MEMORY = "ai_memory"         # Coding memory and pattern storage
    CODACY = "codacy"               # Code quality and security analysis
    GITHUB = "github"               # Repository and issue management
    PORTKEY = "portkey"             # LLM gateway and optimization
    LAMBDA_LABS = "lambda_labs"     # GPU processing and infrastructure

@dataclass
class CodingTask:
    """Represents a coding task for orchestration"""
    id: str
    content: str
    task_type: str
    complexity: TaskComplexity
    context: Dict[str, Any] = field(default_factory=dict)
    required_servers: List[MCPServerType] = field(default_factory=list)
    user_id: str = "default_user"
    timestamp: datetime = field(default_factory=datetime.now)
    
class CodingMCPOrchestrator:
    """
    Intelligent orchestrator for coding MCP servers
    
    Coordinates multiple MCP servers to provide optimal coding assistance:
    - Routes tasks based on complexity and requirements
    - Retrieves relevant context from AI Memory
    - Analyzes code quality through Codacy
    - Manages GitHub operations
    - Optimizes LLM usage through Portkey
    - Leverages Lambda Labs for intensive processing
    """
    
    def __init__(self):
        self.mcp_servers = {}
        self.performance_stats = {
            "total_tasks": 0,
            "successful_tasks": 0,
            "average_response_time": 0.0,
            "server_utilization": {},
            "quality_improvements": 0
        }
        
        # MCP server configurations
        self.server_configs = {
            MCPServerType.AI_MEMORY: {
                "port": 9200,
                "url": "http://localhost:9200",
                "capabilities": ["pattern_storage", "context_retrieval", "decision_memory"]
            },
            MCPServerType.CODACY: {
                "port": 3008,
                "url": "http://localhost:3008",
                "capabilities": ["code_analysis", "security_scan", "quality_metrics"]
            },
            MCPServerType.GITHUB: {
                "port": 9003,
                "url": "http://localhost:9003", 
                "capabilities": ["repo_management", "issue_tracking", "pr_analysis"]
            },
            MCPServerType.PORTKEY: {
                "port": 9013,
                "url": "http://localhost:9013",
                "capabilities": ["llm_routing", "cost_optimization", "model_selection"]
            },
            MCPServerType.LAMBDA_LABS: {
                "port": 9020,
                "url": "http://localhost:9020",
                "capabilities": ["gpu_processing", "infrastructure_management", "performance_optimization"]
            }
        }
        
        logger.info("🤖 Coding MCP Orchestrator initialized")
    
    async def initialize(self):
        """Initialize orchestrator and validate MCP server connections"""
        logger.info("🔗 Initializing MCP server connections...")
        
        for server_type, config in self.server_configs.items():
            try:
                # Test server connectivity
                async with aiohttp.ClientSession() as session:
                    health_url = f"{config['url']}/health"
                    try:
                        async with session.get(health_url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                            if response.status == 200:
                                self.mcp_servers[server_type] = {
                                    "available": True,
                                    "config": config,
                                    "last_check": datetime.now()
                                }
                                logger.info(f"✅ {server_type.value} server available")
                            else:
                                self._mark_server_unavailable(server_type, f"HTTP {response.status}")
                    except asyncio.TimeoutError:
                        self._mark_server_unavailable(server_type, "Connection timeout")
                    except Exception as e:
                        self._mark_server_unavailable(server_type, str(e))
                        
            except Exception as e:
                self._mark_server_unavailable(server_type, str(e))
        
        available_servers = sum(1 for server in self.mcp_servers.values() if server["available"])
        logger.info(f"🎯 MCP Orchestrator ready: {available_servers}/{len(self.server_configs)} servers available")
    
    async def process_coding_request(
        self,
        request: str,
        context: Optional[Dict[str, Any]] = None,
        user_id: str = "default_user"
    ) -> Dict[str, Any]:
        """
        Process a natural language coding request through intelligent orchestration
        
        Args:
            request: Natural language coding request
            context: Additional context (current file, function, etc.)
            user_id: User identifier for personalized responses
            
        Returns:
            Comprehensive response with code, analysis, and recommendations
        """
        start_time = time.time()
        
        try:
            # Step 1: Analyze request and determine task complexity
            task = await self._analyze_request(request, context, user_id)
            
            # Step 2: Retrieve relevant context from AI Memory
            memory_context = await self._get_memory_context(task)
            
            # Step 3: Route to appropriate MCP servers based on requirements
            server_responses = await self._execute_orchestrated_task(task, memory_context)
            
            # Step 4: Synthesize responses into unified result
            unified_response = await self._synthesize_responses(task, server_responses, memory_context)
            
            # Step 5: Quality improvement loop
            improved_response = await self._quality_improvement_loop(unified_response)
            
            # Step 6: Store learnings for future use
            await self._store_task_learnings(task, improved_response)
            
            # Update performance statistics
            response_time = time.time() - start_time
            await self._update_performance_stats(task, response_time, True)
            
            return {
                "success": True,
                "task_id": task.id,
                "response": improved_response,
                "metadata": {
                    "complexity": task.complexity.value,
                    "servers_used": [server.value for server in task.required_servers],
                    "response_time_ms": response_time * 1000,
                    "context_retrieved": len(memory_context),
                    "quality_score": improved_response.get("quality_score", 0)
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Coding request processing failed: {e}")
            await self._update_performance_stats(None, time.time() - start_time, False)
            return {
                "success": False,
                "error": str(e),
                "fallback_response": await self._generate_fallback_response(request)
            }
    
    async def _analyze_request(
        self,
        request: str,
        context: Optional[Dict[str, Any]],
        user_id: str
    ) -> CodingTask:
        """Analyze request to determine complexity and required servers"""
        
        task_id = f"task_{int(time.time() * 1000)}"
        
        # Determine task complexity based on keywords and context
        complexity = TaskComplexity.SIMPLE
        required_servers = [MCPServerType.AI_MEMORY]  # Always include memory
        
        request_lower = request.lower()
        
        # Complexity analysis
        if any(word in request_lower for word in ["generate", "create", "build", "implement"]):
            complexity = TaskComplexity.MODERATE
            required_servers.append(MCPServerType.PORTKEY)  # Need LLM routing
        
        if any(word in request_lower for word in ["refactor", "optimize", "architecture", "design"]):
            complexity = TaskComplexity.COMPLEX
            required_servers.extend([MCPServerType.CODACY, MCPServerType.PORTKEY])
        
        if any(word in request_lower for word in ["security", "vulnerability", "performance", "critical"]):
            complexity = TaskComplexity.CRITICAL
            required_servers.extend([MCPServerType.CODACY, MCPServerType.LAMBDA_LABS])
        
        # GitHub operations
        if any(word in request_lower for word in ["github", "repository", "issue", "pull request", "commit"]):
            required_servers.append(MCPServerType.GITHUB)
        
        # Determine task type
        task_type = "general"
        if "generate" in request_lower or "create" in request_lower:
            task_type = "generation"
        elif "analyze" in request_lower or "review" in request_lower:
            task_type = "analysis"
        elif "fix" in request_lower or "debug" in request_lower:
            task_type = "debugging"
        elif "refactor" in request_lower:
            task_type = "refactoring"
        
        return CodingTask(
            id=task_id,
            content=request,
            task_type=task_type,
            complexity=complexity,
            context=context or {},
            required_servers=list(set(required_servers)),  # Remove duplicates
            user_id=user_id
        )
    
    async def _get_memory_context(self, task: CodingTask) -> List[Dict[str, Any]]:
        """Retrieve relevant context from AI Memory"""
        
        if MCPServerType.AI_MEMORY not in self.mcp_servers or not self.mcp_servers[MCPServerType.AI_MEMORY]["available"]:
            return []
        
        try:
            async with coding_memory_context() as memory_service:
                # Search for relevant patterns
                results = await memory_service.search_coding_memory(
                    query=task.content,
                    namespace=None,  # Search all namespaces
                    limit=5,
                    user_id=task.user_id
                )
                
                # Get specific context based on task type
                context_results = await memory_service.get_coding_context(
                    context_type=task.task_type,
                    namespace=MemoryNamespace.CODING,
                    limit=3
                )
                
                # Combine and format results
                memory_context = []
                
                for result in results + context_results:
                    memory_context.append({
                        "content": result.content,
                        "namespace": result.namespace.value,
                        "relevance": result.relevance_score,
                        "metadata": result.metadata
                    })
                
                return memory_context
                
        except Exception as e:
            logger.warning(f"⚠️ Memory context retrieval failed: {e}")
            return []
    
    async def _execute_orchestrated_task(
        self,
        task: CodingTask,
        memory_context: List[Dict[str, Any]]
    ) -> Dict[MCPServerType, Dict[str, Any]]:
        """Execute task across required MCP servers in optimal order"""
        
        server_responses = {}
        
        # Execute servers in dependency order
        execution_order = self._determine_execution_order(task.required_servers)
        
        for server_type in execution_order:
            if server_type not in self.mcp_servers or not self.mcp_servers[server_type]["available"]:
                logger.warning(f"⚠️ Skipping unavailable server: {server_type.value}")
                continue
            
            try:
                response = await self._call_mcp_server(server_type, task, memory_context, server_responses)
                server_responses[server_type] = response
                logger.info(f"✅ {server_type.value} completed successfully")
                
            except Exception as e:
                logger.error(f"❌ {server_type.value} failed: {e}")
                server_responses[server_type] = {"error": str(e)}
        
        return server_responses
    
    async def _call_mcp_server(
        self,
        server_type: MCPServerType,
        task: CodingTask,
        memory_context: List[Dict[str, Any]],
        previous_responses: Dict[MCPServerType, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Call specific MCP server with appropriate parameters"""
        
        # This is a simplified implementation - in production would make actual MCP calls
        # For now, return structured responses based on server type
        
        if server_type == MCPServerType.AI_MEMORY:
            return {
                "patterns_found": len(memory_context),
                "relevant_context": memory_context[:3],
                "suggestions": [
                    "Consider using established patterns from your codebase",
                    "Check previous similar implementations"
                ]
            }
        
        elif server_type == MCPServerType.CODACY:
            return {
                "code_quality_score": 85,
                "security_issues": [],
                "suggestions": [
                    "Follow PEP 8 style guidelines",
                    "Add comprehensive error handling",
                    "Consider adding unit tests"
                ],
                "complexity_analysis": {
                    "cyclomatic_complexity": 3,
                    "maintainability_index": 78
                }
            }
        
        elif server_type == MCPServerType.GITHUB:
            return {
                "repository_context": "sophia-main-2",
                "related_issues": [],
                "suggested_branch": f"feature/{task.task_type}-{task.id}",
                "commit_template": f"{task.task_type}: {task.content[:50]}..."
            }
        
        elif server_type == MCPServerType.PORTKEY:
            return {
                "optimal_model": "claude-4-sonnet" if task.complexity in [TaskComplexity.COMPLEX, TaskComplexity.CRITICAL] else "gpt-4",
                "estimated_cost": 0.02,
                "routing_decision": "high_quality_model_for_complex_task",
                "alternative_models": ["gpt-4", "claude-3-opus"]
            }
        
        elif server_type == MCPServerType.LAMBDA_LABS:
            return {
                "gpu_available": True,
                "processing_time_estimate": "2-5 seconds",
                "optimization_suggestions": [
                    "Use GPU acceleration for large model inference",
                    "Implement batch processing for multiple requests"
                ]
            }
        
        return {"status": "completed", "server": server_type.value}
    
    def _determine_execution_order(self, required_servers: List[MCPServerType]) -> List[MCPServerType]:
        """Determine optimal execution order based on dependencies"""
        
        # Define dependency relationships
        dependencies = {
            MCPServerType.AI_MEMORY: [],  # No dependencies
            MCPServerType.PORTKEY: [],   # No dependencies
            MCPServerType.CODACY: [MCPServerType.AI_MEMORY],  # May use patterns for analysis
            MCPServerType.GITHUB: [MCPServerType.AI_MEMORY, MCPServerType.CODACY],  # Uses context and quality info
            MCPServerType.LAMBDA_LABS: [MCPServerType.PORTKEY]  # Uses model selection
        }
        
        # Simple topological sort
        ordered = []
        remaining = set(required_servers)
        
        while remaining:
            # Find servers with no pending dependencies
            ready = [server for server in remaining 
                    if all(dep in ordered or dep not in required_servers 
                           for dep in dependencies.get(server, []))]
            
            if not ready:
                # Handle circular dependencies by adding remaining servers
                ready = list(remaining)
            
            # Add first ready server
            server = ready[0]
            ordered.append(server)
            remaining.remove(server)
        
        return ordered
    
    async def _synthesize_responses(
        self,
        task: CodingTask,
        server_responses: Dict[MCPServerType, Dict[str, Any]],
        memory_context: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Synthesize responses from multiple servers into unified result"""
        
        synthesis = {
            "task_id": task.id,
            "task_type": task.task_type,
            "complexity": task.complexity.value,
            "generated_code": "",
            "explanations": [],
            "recommendations": [],
            "quality_analysis": {},
            "context_used": memory_context,
            "metadata": {}
        }
        
        # Extract and combine information from each server
        for server_type, response in server_responses.items():
            if "error" in response:
                synthesis["metadata"][f"{server_type.value}_error"] = response["error"]
                continue
            
            if server_type == MCPServerType.AI_MEMORY:
                synthesis["explanations"].extend(response.get("suggestions", []))
                synthesis["metadata"]["patterns_found"] = response.get("patterns_found", 0)
            
            elif server_type == MCPServerType.CODACY:
                synthesis["quality_analysis"] = response
                synthesis["recommendations"].extend(response.get("suggestions", []))
            
            elif server_type == MCPServerType.GITHUB:
                synthesis["metadata"]["github_context"] = response
            
            elif server_type == MCPServerType.PORTKEY:
                synthesis["metadata"]["llm_routing"] = response
            
            elif server_type == MCPServerType.LAMBDA_LABS:
                synthesis["metadata"]["performance"] = response
        
        # Generate code based on task type and available context
        if task.task_type == "generation":
            synthesis["generated_code"] = await self._generate_code_from_context(task, memory_context, server_responses)
        
        # Add overall recommendations
        synthesis["recommendations"].extend([
            "Review generated code against stored patterns",
            "Test implementation thoroughly",
            "Consider code quality suggestions"
        ])
        
        return synthesis
    
    async def _generate_code_from_context(
        self,
        task: CodingTask,
        memory_context: List[Dict[str, Any]],
        server_responses: Dict[MCPServerType, Dict[str, Any]]
    ) -> str:
        """Generate code using available context and patterns"""
        
        # This is a simplified code generation - in production would use LLM
        code_template = f"""
# Generated code for: {task.content}
# Task ID: {task.id}
# Complexity: {task.complexity.value}

def generated_function():
    '''
    {task.content}
    
    Based on patterns from memory context:
    {[ctx['content'][:100] + '...' for ctx in memory_context[:2]]}
    '''
    
    # TODO: Implement based on requirements
    pass

# Quality considerations from Codacy analysis:
# {server_responses.get(MCPServerType.CODACY, {}).get('suggestions', [])}

# Usage example:
if __name__ == "__main__":
    result = generated_function()
    print(f"Result: {{result}}")
"""
        return code_template.strip()
    
    async def _quality_improvement_loop(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Improve response quality based on analysis and patterns"""
        
        improved_response = response.copy()
        
        # Add quality score based on various factors
        quality_factors = {
            "has_generated_code": bool(response.get("generated_code")),
            "has_context": len(response.get("context_used", [])) > 0,
            "has_quality_analysis": bool(response.get("quality_analysis")),
            "has_recommendations": len(response.get("recommendations", [])) > 0
        }
        
        quality_score = sum(1 for factor in quality_factors.values() if factor) * 25
        improved_response["quality_score"] = quality_score
        
        # Add improvement suggestions if quality is low
        if quality_score < 75:
            improved_response["improvement_suggestions"] = [
                "Consider providing more specific requirements",
                "Add context about current file or function",
                "Specify programming language and framework"
            ]
        
        # Track quality improvements
        self.performance_stats["quality_improvements"] += 1
        
        return improved_response
    
    async def _store_task_learnings(self, task: CodingTask, response: Dict[str, Any]):
        """Store task and response as learning for future use"""
        
        try:
            async with coding_memory_context() as memory_service:
                # Store successful patterns
                if response.get("quality_score", 0) >= 75:
                    learning_content = f"""
SUCCESSFUL TASK PATTERN:
Request: {task.content}
Type: {task.task_type}
Complexity: {task.complexity.value}
Servers Used: {[server.value for server in task.required_servers]}
Quality Score: {response.get('quality_score')}

Generated Code:
{response.get('generated_code', 'No code generated')}

Key Recommendations:
{chr(10).join(response.get('recommendations', [])[:3])}
"""
                    
                    await memory_service.store_coding_memory(
                        content=learning_content,
                        namespace=MemoryNamespace.CODING,
                        metadata={
                            "type": "task_learning",
                            "task_type": task.task_type,
                            "complexity": task.complexity.value,
                            "quality_score": response.get("quality_score"),
                            "servers_used": [server.value for server in task.required_servers]
                        },
                        user_id=task.user_id
                    )
                    
        except Exception as e:
            logger.warning(f"⚠️ Failed to store task learnings: {e}")
    
    async def _update_performance_stats(self, task: Optional[CodingTask], response_time: float, success: bool):
        """Update performance statistics"""
        
        self.performance_stats["total_tasks"] += 1
        
        if success:
            self.performance_stats["successful_tasks"] += 1
        
        # Update average response time
        current_avg = self.performance_stats["average_response_time"]
        total_tasks = self.performance_stats["total_tasks"]
        
        if total_tasks == 1:
            self.performance_stats["average_response_time"] = response_time
        else:
            self.performance_stats["average_response_time"] = (
                (current_avg * (total_tasks - 1) + response_time) / total_tasks
            )
        
        # Update server utilization
        if task:
            for server in task.required_servers:
                server_name = server.value
                if server_name not in self.performance_stats["server_utilization"]:
                    self.performance_stats["server_utilization"][server_name] = 0
                self.performance_stats["server_utilization"][server_name] += 1
    
    async def _generate_fallback_response(self, request: str) -> Dict[str, Any]:
        """Generate fallback response when orchestration fails"""
        
        return {
            "message": "Unable to process request through full orchestration",
            "suggestions": [
                "Check MCP server availability",
                "Simplify the request",
                "Try again later"
            ],
            "fallback_code": f"# TODO: Implement - {request}",
            "quality_score": 25
        }
    
    def _mark_server_unavailable(self, server_type: MCPServerType, reason: str):
        """Mark a server as unavailable"""
        self.mcp_servers[server_type] = {
            "available": False,
            "reason": reason,
            "last_check": datetime.now()
        }
        logger.warning(f"⚠️ {server_type.value} server unavailable: {reason}")
    
    async def get_coding_orchestrator_status(self) -> Dict[str, Any]:
        """Get comprehensive orchestrator status"""
        
        return {
            "service": "coding_mcp_orchestrator",
            "status": "healthy" if self.mcp_servers else "initializing",
            "servers": {
                server_type.value: server_info for server_type, server_info in self.mcp_servers.items()
            },
            "performance": self.performance_stats,
            "capabilities": [
                "intelligent_task_routing",
                "context_aware_generation", 
                "quality_improvement_loop",
                "multi_server_orchestration",
                "performance_optimization"
            ],
            "timestamp": datetime.now().isoformat()
        }

# Singleton instance
_orchestrator_instance: Optional[CodingMCPOrchestrator] = None

def get_coding_orchestrator() -> CodingMCPOrchestrator:
    """Get the singleton coding orchestrator instance"""
    global _orchestrator_instance
    if _orchestrator_instance is None:
        _orchestrator_instance = CodingMCPOrchestrator()
    return _orchestrator_instance

# Natural language interface functions
async def process_natural_language_request(request: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Process natural language coding request"""
    orchestrator = get_coding_orchestrator()
    await orchestrator.initialize()
    return await orchestrator.process_coding_request(request, context)

if __name__ == "__main__":
    # Example usage
    async def test_orchestrator():
        orchestrator = get_coding_orchestrator()
        await orchestrator.initialize()
        
        # Test natural language request
        result = await orchestrator.process_coding_request(
            "Create a FastAPI endpoint for user authentication with JWT tokens",
            context={"file": "auth.py", "language": "python"}
        )
        
        print(f"✅ Orchestration result: {result['success']}")
        print(f"📊 Quality score: {result.get('response', {}).get('quality_score', 0)}")
        print(f"⚡ Response time: {result.get('metadata', {}).get('response_time_ms', 0):.2f}ms")
    
    asyncio.run(test_orchestrator()) 