#!/usr/bin/env python3
"""
Standardized AI Memory MCP Server for persistent development context
Built on the StandardizedMCPServer base class with Snowflake Cortex integration
"""

from __future__ import annotations

import asyncio
import json
import logging
import re
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel

# Enhanced dependencies with better error handling
try:
    import pinecone
    PINECONE_AVAILABLE = True
except ImportError:
    PINECONE_AVAILABLE = False
    pinecone = None

try:
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    AsyncOpenAI = None

# Import the standardized base class
from backend.mcp.base.standardized_mcp_server import (
    StandardizedMCPServer, MCPServerConfig, SyncPriority, HealthStatus, HealthCheckResult
)

# Import enhanced Snowflake Cortex service
from backend.utils.enhanced_snowflake_cortex_service import (
    EnhancedSnowflakeCortexService, AIProcessingConfig, CortexModel
)

# Import existing memory management components
from backend.core.comprehensive_memory_manager import ComprehensiveMemoryManager
from backend.core.contextual_memory_intelligence import ContextualMemoryIntelligence
from backend.core.hierarchical_cache import HierarchicalCache

logger = logging.getLogger(__name__)


class MemoryCategory:
    """Categories for AI memory storage."""
    
    ARCHITECTURE = "architecture"
    BUG_SOLUTION = "bug_solution"
    CODE_DECISION = "code_decision"
    WORKFLOW = "workflow"
    AI_CODING_PATTERN = "ai_coding_pattern"
    PERFORMANCE_TIP = "performance_tip"
    SECURITY_PATTERN = "security_pattern"
    
    # Business intelligence categories
    HUBSPOT_CONTACT_INSIGHT = "hubspot_contact_insight"
    HUBSPOT_DEAL_ANALYSIS = "hubspot_deal_analysis"
    HUBSPOT_SALES_PATTERN = "hubspot_sales_pattern"
    HUBSPOT_CUSTOMER_INTERACTION = "hubspot_customer_interaction"
    HUBSPOT_PIPELINE_INSIGHT = "hubspot_pipeline_insight"
    
    # Gong-specific categories
    GONG_CALL_SUMMARY = "gong_call_summary"
    GONG_CALL_INSIGHT = "gong_call_insight"
    GONG_COACHING_RECOMMENDATION = "gong_coaching_recommendation"
    GONG_SENTIMENT_ANALYSIS = "gong_sentiment_analysis"
    GONG_TOPIC_ANALYSIS = "gong_topic_analysis"


class MemoryRecord(BaseModel):
    """Enhanced model for a memory record."""
    
    id: str
    content: str
    category: str
    tags: List[str]
    embedding: Optional[List[float]] = None
    created_at: datetime = datetime.now()
    importance_score: float = 0.5  # 0-1 scale
    auto_detected: bool = False
    usage_count: int = 0
    last_accessed: Optional[datetime] = None
    
    # Enhanced metadata for business intelligence
    deal_id: Optional[str] = None
    call_id: Optional[str] = None
    contact_id: Optional[str] = None
    sentiment_score: Optional[float] = None
    confidence_score: Optional[float] = None


class ConversationAnalyzer:
    """Analyzes conversations to auto-detect important content"""
    
    def __init__(self):
        self.importance_patterns = {
            "architecture": [
                r"decided to use", r"architecture decision", r"design pattern",
                r"microservices", r"database schema", r"api design", r"system design"
            ],
            "bug_solution": [
                r"fixed the bug", r"solution was", r"error was caused by",
                r"debugging showed", r"issue resolved", r"problem solved"
            ],
            "code_decision": [
                r"chose to implement", r"decided to refactor", r"code structure",
                r"implementation approach", r"coding standard"
            ],
            "security_pattern": [
                r"security vulnerability", r"authentication", r"authorization",
                r"encryption", r"security best practice", r"secure coding"
            ],
            "performance_tip": [
                r"performance optimization", r"faster approach", r"bottleneck",
                r"cache strategy", r"query optimization"
            ]
        }
        
        self.high_importance_keywords = [
            "critical", "important", "remember", "decision", "solution",
            "pattern", "best practice", "lesson learned", "mistake",
            "breakthrough", "optimization", "security", "performance"
        ]
    
    def analyze_conversation(self, content: str) -> Dict[str, Any]:
        """Analyze conversation content for importance and categorization"""
        content_lower = content.lower()
        
        # Calculate importance score
        importance_score = self._calculate_importance(content_lower)
        
        # Detect category
        category = self._detect_category(content_lower)
        
        # Extract tags
        tags = self._extract_tags(content_lower)
        
        # Check if auto-storage worthy
        should_auto_store = importance_score > 0.6
        
        return {
            "importance_score": importance_score,
            "category": category,
            "tags": tags,
            "should_auto_store": should_auto_store,
            "analysis_reason": self._get_analysis_reason(content_lower, importance_score)
        }
    
    def _calculate_importance(self, content: str) -> float:
        """Calculate importance score based on content analysis"""
        score = 0.3  # Base score
        
        # High importance keywords
        for keyword in self.high_importance_keywords:
            if keyword in content:
                score += 0.1
        
        # Pattern matching
        for category, patterns in self.importance_patterns.items():
            for pattern in patterns:
                if re.search(pattern, content):
                    score += 0.15
        
        # Length consideration
        if len(content) > 500:
            score += 0.1
        if len(content) > 1000:
            score += 0.1
        
        # Code snippets increase importance
        if "```" in content or "def " in content or "class " in content:
            score += 0.2
        
        return min(score, 1.0)
    
    def _detect_category(self, content: str) -> str:
        """Detect the most likely category for the content"""
        category_scores = {}
        
        for category, patterns in self.importance_patterns.items():
            score = 0
            for pattern in patterns:
                if re.search(pattern, content):
                    score += 1
            category_scores[category] = score
        
        if category_scores:
            best_category = max(category_scores, key=category_scores.get)
            if category_scores[best_category] > 0:
                return best_category
        
        return MemoryCategory.CODE_DECISION
    
    def _extract_tags(self, content: str) -> List[str]:
        """Extract relevant tags from content"""
        tags = []
        
        # Technology tags
        tech_patterns = {
            "python": r"\bpython\b", "javascript": r"\b(javascript|js)\b",
            "typescript": r"\btypescript\b", "react": r"\breact\b",
            "fastapi": r"\bfastapi\b", "docker": r"\bdocker\b",
            "kubernetes": r"\bkubernetes\b", "redis": r"\bredis\b",
            "postgresql": r"\b(postgresql|postgres)\b", "openai": r"\bopenai\b",
            "pinecone": r"\bpinecone\b", "mcp": r"\bmcp\b", "cursor": r"\bcursor\b"
        }
        
        for tag, pattern in tech_patterns.items():
            if re.search(pattern, content):
                tags.append(tag)
        
        # Context tags
        if "error" in content or "bug" in content:
            tags.append("debugging")
        if "performance" in content or "slow" in content:
            tags.append("performance")
        if "security" in content:
            tags.append("security")
        if "api" in content:
            tags.append("api")
        if "database" in content:
            tags.append("database")
        
        return tags
    
    def _get_analysis_reason(self, content: str, score: float) -> str:
        """Get human-readable reason for the analysis"""
        reasons = []
        
        if score > 0.8:
            reasons.append("High importance keywords detected")
        if "```" in content:
            reasons.append("Contains code snippets")
        if any(pattern in content for patterns in self.importance_patterns.values() for pattern in patterns):
            reasons.append("Matches important patterns")
        if len(content) > 1000:
            reasons.append("Detailed conversation")
        
        return "; ".join(reasons) if reasons else "Standard content analysis"


class StandardizedAiMemoryMCPServer(StandardizedMCPServer):
    """
    Standardized AI Memory MCP Server with enhanced Snowflake Cortex integration
    Built on the StandardizedMCPServer base class for consistency and monitoring
    """
    
    def __init__(self, config: Optional[MCPServerConfig] = None):
        # Default configuration for AI Memory server
        if config is None:
            config = MCPServerConfig(
                server_name="ai_memory",
                port=9000,
                sync_priority=SyncPriority.HIGH,
                sync_interval_minutes=5,
                enable_metrics=True,
                health_check_interval_seconds=30,
                max_concurrent_requests=50,
                request_timeout_seconds=30
            )
        
        super().__init__(config)
        
        # AI Memory specific components
        self.memory_manager = ComprehensiveMemoryManager()
        self.memory_intelligence = ContextualMemoryIntelligence(self.memory_manager)
        self.cache = HierarchicalCache()
        self.conversation_analyzer = ConversationAnalyzer()
        
        # AI services
        self.openai_client: Optional[Any] = None
        self.pinecone_index: Optional[Any] = None
        self.cortex_service: Optional[EnhancedSnowflakeCortexService] = None
        
        # State tracking
        self.preloaded_knowledge = False
    
    async def initialize_server(self) -> None:
        """Initialize AI Memory server with all services"""
        logger.info("Initializing AI Memory MCP Server with Snowflake Cortex...")
        
        # Initialize AI services
        await self._initialize_openai()
        await self._initialize_pinecone()
        await self._initialize_snowflake_cortex()
        
        # Pre-load helpful AI coding knowledge
        await self._preload_ai_coding_knowledge()
        
        logger.info("AI Memory MCP Server initialized successfully")
    
    async def cleanup_server(self) -> None:
        """Cleanup AI Memory server resources"""
        if self.openai_client:
            await self.openai_client.close()
        
        # Clean up cache
        await self.cache.clear()
        
        logger.info("AI Memory MCP Server cleaned up successfully")
    
    async def _initialize_openai(self):
        """Initialize OpenAI client with proper configuration"""
        from backend.core.auto_esc_config import config
        
        openai_api_key = config.get("openai_api_key")
        
        if not openai_api_key or openai_api_key in ["fallback-key", "sk-development-key-fallback"]:
            logger.warning("No valid OpenAI API key found. Semantic search will be limited.")
            return
        
        if not OPENAI_AVAILABLE:
            logger.warning("OpenAI library not available. Install with: pip install openai")
            return
        
        try:
            self.openai_client = AsyncOpenAI(
                api_key=openai_api_key,
                timeout=30.0,
                max_retries=3
            )
            
            # Test the connection
            await self.openai_client.embeddings.create(
                input="test connection",
                model="text-embedding-3-small"
            )
            
            logger.info("✅ OpenAI client initialized and tested successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            self.openai_client = None
    
    async def _initialize_pinecone(self):
        """Initialize Pinecone with proper configuration"""
        from backend.core.auto_esc_config import config
        
        pinecone_api_key = config.get("pinecone_api_key")
        pinecone_environment = config.get("pinecone_environment", "us-east1-gcp")
        
        if not pinecone_api_key or pinecone_api_key in ["dev-pinecone-key", "fallback-key"]:
            logger.warning("No valid Pinecone API key found. Vector search will be limited.")
            return
        
        if not PINECONE_AVAILABLE:
            logger.warning("Pinecone library not available. Install with: pip install pinecone-client")
            return
        
        try:
            pinecone.init(api_key=pinecone_api_key, environment=pinecone_environment)
            
            index_name = "sophia-ai-memory"
            
            # Check if index exists, create if not
            if index_name not in pinecone.list_indexes():
                logger.info(f"Creating Pinecone index: {index_name}")
                pinecone.create_index(
                    name=index_name,
                    dimension=1536,  # text-embedding-3-small dimension
                    metric="cosine",
                    pods=1,
                    replicas=1,
                    pod_type="p1.x1"
                )
            
            self.pinecone_index = pinecone.Index(index_name)
            
            # Test the connection
            stats = self.pinecone_index.describe_index_stats()
            logger.info(f"✅ Pinecone initialized successfully. Vectors: {stats.total_vector_count}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Pinecone: {e}")
            self.pinecone_index = None
    
    async def _initialize_snowflake_cortex(self):
        """Initialize Enhanced Snowflake Cortex service"""
        try:
            config = AIProcessingConfig(
                embedding_model=CortexModel.E5_BASE_V2,
                llm_model=CortexModel.LLAMA3_70B,
                enable_caching=True,
                cache_ttl_minutes=60
            )
            
            self.cortex_service = EnhancedSnowflakeCortexService(config)
            logger.info("✅ Enhanced Snowflake Cortex service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Snowflake Cortex service: {e}")
            self.cortex_service = None
    
    async def _preload_ai_coding_knowledge(self):
        """Pre-load helpful AI coding knowledge for developers"""
        if self.preloaded_knowledge:
            return
        
        knowledge_base = [
            {
                "content": "When using Cursor IDE with MCP servers, use @server_name commands to interact with specific tools. For example: @ai_memory store this conversation, @codacy analyze this code, @asana create task. This provides intelligent, context-aware development assistance.",
                "category": MemoryCategory.AI_CODING_PATTERN,
                "tags": ["cursor", "mcp", "ai_assistance", "development_workflow"],
                "importance_score": 0.9
            },
            {
                "content": "For Python async development, always use 'async def' for I/O operations and 'await' for async calls. Common pattern: async with aiohttp.ClientSession() as session: async with session.get(url) as response: data = await response.json(). Avoid blocking calls in async functions.",
                "category": MemoryCategory.AI_CODING_PATTERN,
                "tags": ["python", "async", "aiohttp", "best_practices"],
                "importance_score": 0.8
            },
            {
                "content": "Redis connection pattern for Python 3.11+: Use 'import redis.asyncio as redis_client' then 'redis_client.from_url()'. Avoid 'redis_client' package due to Python 3.11 TimeoutError compatibility issues.",
                "category": MemoryCategory.BUG_SOLUTION,
                "tags": ["python", "redis", "python311", "compatibility"],
                "importance_score": 0.9
            },
            # Add more knowledge base entries...
        ]
        
        for knowledge in knowledge_base:
            try:
                await self.store_memory(
                    content=knowledge["content"],
                    category=knowledge["category"],
                    tags=knowledge["tags"],
                    importance_score=knowledge["importance_score"],
                    auto_detected=False
                )
            except Exception as e:
                logger.error(f"Failed to preload knowledge: {e}")
        
        self.preloaded_knowledge = True
        logger.info("AI coding knowledge preloaded successfully")
    
    async def sync_data(self) -> Dict[str, Any]:
        """Sync memory data with external systems"""
        try:
            sync_results = {
                "memories_synced": 0,
                "embeddings_updated": 0,
                "cortex_insights_generated": 0
            }
            
            # Sync with Snowflake Cortex
            if self.cortex_service:
                # Generate AI insights for recent memories
                recent_memories = await self.recall_memory("", limit=10)
                for memory in recent_memories:
                    try:
                        insights = await self.cortex_service.generate_ai_insights(
                            content=memory.get("content", ""),
                            context="memory_analysis"
                        )
                        sync_results["cortex_insights_generated"] += 1
                    except Exception as e:
                        logger.error(f"Failed to generate Cortex insights: {e}")
            
            # Update embeddings for memories without them
            memories_updated = await self._update_missing_embeddings()
            sync_results["embeddings_updated"] = memories_updated
            
            return sync_results
            
        except Exception as e:
            logger.error(f"Failed to sync memory data: {e}")
            raise
    
    async def _update_missing_embeddings(self) -> int:
        """Update embeddings for memories that don't have them"""
        try:
            updated_count = 0
            # Implementation would check for memories without embeddings
            # and generate them using OpenAI or Cortex
            return updated_count
        except Exception as e:
            logger.error(f"Failed to update missing embeddings: {e}")
            return 0
    
    async def perform_health_checks(self) -> List[HealthCheckResult]:
        """Perform comprehensive health checks for AI Memory server"""
        health_checks = []
        
        # Check OpenAI connection
        openai_status = HealthStatus.HEALTHY if self.openai_client else HealthStatus.UNHEALTHY
        health_checks.append(HealthCheckResult(
            component="openai_client",
            status=openai_status,
            response_time_ms=0.0,
            details="OpenAI client availability"
        ))
        
        # Check Pinecone connection
        pinecone_status = HealthStatus.HEALTHY if self.pinecone_index else HealthStatus.UNHEALTHY
        health_checks.append(HealthCheckResult(
            component="pinecone_index",
            status=pinecone_status,
            response_time_ms=0.0,
            details="Pinecone index availability"
        ))
        
        # Check Cortex service
        cortex_status = HealthStatus.HEALTHY if self.cortex_service else HealthStatus.UNHEALTHY
        health_checks.append(HealthCheckResult(
            component="cortex_service",
            status=cortex_status,
            response_time_ms=0.0,
            details="Snowflake Cortex service availability"
        ))
        
        # Check memory manager
        try:
            # Test memory manager functionality
            await asyncio.wait_for(
                self.memory_manager.get_memory_stats(),
                timeout=5.0
            )
            memory_status = HealthStatus.HEALTHY
        except Exception:
            memory_status = HealthStatus.UNHEALTHY
        
        health_checks.append(HealthCheckResult(
            component="memory_manager",
            status=memory_status,
            response_time_ms=0.0,
            details="Memory manager functionality"
        ))
        
        return health_checks
    
    def get_mcp_tools(self) -> List[Dict[str, Any]]:
        """Get MCP tools for AI Memory server"""
        return [
            {
                "name": "store_memory",
                "description": "Store a memory with content, category, and tags",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "content": {"type": "string", "description": "Memory content"},
                        "category": {"type": "string", "description": "Memory category"},
                        "tags": {"type": "array", "items": {"type": "string"}, "description": "Memory tags"},
                        "importance_score": {"type": "number", "minimum": 0, "maximum": 1, "description": "Importance score"},
                        "auto_detected": {"type": "boolean", "description": "Whether auto-detected"}
                    },
                    "required": ["content", "category", "tags"]
                }
            },
            {
                "name": "recall_memory",
                "description": "Recall memories using semantic search",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"},
                        "category": {"type": "string", "description": "Optional category filter"},
                        "limit": {"type": "integer", "minimum": 1, "maximum": 20, "description": "Max results"}
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "auto_store_conversation",
                "description": "Automatically analyze and store conversation if important",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "content": {"type": "string", "description": "Conversation content"},
                        "participants": {"type": "array", "items": {"type": "string"}, "description": "Participants"}
                    },
                    "required": ["content"]
                }
            },
            {
                "name": "get_ai_coding_tips",
                "description": "Get AI coding tips for a specific topic",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "topic": {"type": "string", "description": "Optional topic filter"}
                    }
                }
            }
        ]
    
    async def execute_mcp_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute MCP tool requests"""
        try:
            if tool_name == "store_memory":
                return await self.store_memory(
                    content=parameters["content"],
                    category=parameters["category"],
                    tags=parameters["tags"],
                    importance_score=parameters.get("importance_score", 0.5),
                    auto_detected=parameters.get("auto_detected", False)
                )
            
            elif tool_name == "recall_memory":
                return {"memories": await self.recall_memory(
                    query=parameters["query"],
                    category=parameters.get("category"),
                    limit=parameters.get("limit", 5)
                )}
            
            elif tool_name == "auto_store_conversation":
                return await self.auto_store_conversation(
                    content=parameters["content"],
                    participants=parameters.get("participants")
                )
            
            elif tool_name == "get_ai_coding_tips":
                return await self.get_ai_coding_tips(
                    topic=parameters.get("topic")
                )
            
            else:
                raise ValueError(f"Unknown tool: {tool_name}")
                
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}")
            return {"error": str(e), "success": False}
    
    # Core memory management methods
    async def get_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using available services"""
        try:
            # Try Snowflake Cortex first
            if self.cortex_service:
                result = await self.cortex_service.generate_embedding(text)
                return result.embedding
            
            # Fallback to OpenAI
            if self.openai_client:
                response = await self.openai_client.embeddings.create(
                    input=text,
                    model="text-embedding-3-small"
                )
                return response.data[0].embedding
            
            # No embedding service available
            logger.warning("No embedding service available")
            return []
            
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            return []
    
    async def store_memory(
        self,
        content: str,
        category: str,
        tags: List[str],
        importance_score: float = 0.5,
        auto_detected: bool = False
    ) -> Dict[str, Any]:
        """Store a memory with enhanced features"""
        try:
            # Generate embedding
            embedding = await self.get_embedding(content)
            
            # Create memory record
            memory_id = f"mem_{int(datetime.now().timestamp())}"
            memory = MemoryRecord(
                id=memory_id,
                content=content,
                category=category,
                tags=tags,
                embedding=embedding,
                importance_score=importance_score,
                auto_detected=auto_detected
            )
            
            # Store in memory manager
            await self.memory_manager.store_memory(memory.dict())
            
            # Store in Pinecone if available
            if self.pinecone_index and embedding:
                metadata = {
                    "category": category,
                    "tags": ",".join(tags),
                    "importance_score": importance_score,
                    "auto_detected": auto_detected,
                    "created_at": memory.created_at.isoformat()
                }
                
                self.pinecone_index.upsert([(memory_id, embedding, metadata)])
            
            # Record metrics
            self.metrics_collector.record_ai_processing_metrics(
                "store_memory", 1.0, importance_score
            )
            
            return {
                "success": True,
                "memory_id": memory_id,
                "category": category,
                "importance_score": importance_score,
                "embedding_generated": bool(embedding)
            }
            
        except Exception as e:
            logger.error(f"Failed to store memory: {e}")
            return {"success": False, "error": str(e)}
    
    async def recall_memory(
        self,
        query: str,
        category: Optional[str] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Recall memories using semantic search"""
        try:
            results = []
            
            # Try Pinecone vector search first
            if self.pinecone_index and query:
                query_embedding = await self.get_embedding(query)
                
                if query_embedding:
                    filter_dict = {}
                    if category:
                        filter_dict["category"] = {"$eq": category}
                    
                    search_results = self.pinecone_index.query(
                        vector=query_embedding,
                        filter=filter_dict,
                        top_k=limit,
                        include_metadata=True
                    )
                    
                    for match in search_results.matches:
                        # Get full memory content
                        memory_content = await self.memory_manager.get_memory(match.id)
                        if memory_content:
                            results.append({
                                "id": match.id,
                                "content": memory_content.get("content", ""),
                                "category": match.metadata.get("category", ""),
                                "tags": match.metadata.get("tags", "").split(","),
                                "similarity_score": float(match.score),
                                "importance_score": match.metadata.get("importance_score", 0.5)
                            })
            
            # Fallback to traditional search
            if not results:
                fallback_results = await self.memory_manager.search_memories(
                    query=query,
                    category=category,
                    limit=limit
                )
                results = fallback_results
            
            # Update usage counts
            for result in results:
                await self._update_usage_count(result["id"])
            
            # Record metrics
            self.metrics_collector.record_ai_processing_metrics(
                "recall_memory", 1.0, len(results) / limit if limit > 0 else 0
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to recall memory: {e}")
            return []
    
    async def auto_store_conversation(
        self,
        content: str,
        participants: List[str] = None
    ) -> Dict[str, Any]:
        """Automatically analyze and store conversation if important"""
        try:
            # Analyze conversation
            analysis = self.conversation_analyzer.analyze_conversation(content)
            
            if analysis["should_auto_store"]:
                # Store the memory
                result = await self.store_memory(
                    content=content,
                    category=analysis["category"],
                    tags=analysis["tags"],
                    importance_score=analysis["importance_score"],
                    auto_detected=True
                )
                
                return {
                    "stored": True,
                    "analysis": analysis,
                    "storage_result": result
                }
            else:
                return {
                    "stored": False,
                    "analysis": analysis,
                    "reason": "Importance score below threshold"
                }
                
        except Exception as e:
            logger.error(f"Failed to auto-store conversation: {e}")
            return {"stored": False, "error": str(e)}
    
    async def get_ai_coding_tips(self, topic: Optional[str] = None) -> Dict[str, Any]:
        """Get AI coding tips for a specific topic"""
        try:
            query = topic if topic else "ai coding patterns best practices"
            
            tips = await self.recall_memory(
                query=query,
                category=MemoryCategory.AI_CODING_PATTERN,
                limit=5
            )
            
            return {
                "topic": topic,
                "tips": tips,
                "total_found": len(tips)
            }
            
        except Exception as e:
            logger.error(f"Failed to get AI coding tips: {e}")
            return {"error": str(e), "tips": []}
    
    async def _update_usage_count(self, memory_id: str):
        """Update usage count for a memory"""
        try:
            await self.memory_manager.update_usage_count(memory_id)
        except Exception as e:
            logger.error(f"Failed to update usage count for {memory_id}: {e}")


# Main function for standalone execution
async def main() -> None:
    """Main function to run the AI Memory MCP Server"""
    config = MCPServerConfig(
        server_name="ai_memory",
        port=9000,
        sync_priority=SyncPriority.HIGH,
        sync_interval_minutes=5,
        enable_metrics=True
    )
    
    server = StandardizedAiMemoryMCPServer(config)
    await server.start()


if __name__ == "__main__":
    asyncio.run(main()) 