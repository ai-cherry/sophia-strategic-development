"""
Enhanced AI Memory MCP Server for persistent development context
Now with real OpenAI embeddings, Pinecone integration, and auto-detection
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
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


class ConversationAnalyzer:
    """Analyzes conversations to auto-detect important content"""
    
    def __init__(self):
        self.importance_patterns = {
            "architecture": [
                r"decided to use",
                r"architecture decision",
                r"design pattern",
                r"microservices",
                r"database schema",
                r"api design",
                r"system design"
            ],
            "bug_solution": [
                r"fixed the bug",
                r"solution was",
                r"error was caused by",
                r"debugging showed",
                r"issue resolved",
                r"problem solved"
            ],
            "code_decision": [
                r"chose to implement",
                r"decided to refactor",
                r"code structure",
                r"implementation approach",
                r"coding standard"
            ],
            "security_pattern": [
                r"security vulnerability",
                r"authentication",
                r"authorization",
                r"encryption",
                r"security best practice",
                r"secure coding"
            ],
            "performance_tip": [
                r"performance optimization",
                r"faster approach",
                r"bottleneck",
                r"cache strategy",
                r"query optimization"
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
        
        # Length consideration (longer conversations often more important)
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
        
        # Return category with highest score, default to code_decision
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
            "python": r"\bpython\b",
            "javascript": r"\b(javascript|js)\b",
            "typescript": r"\btypescript\b",
            "react": r"\breact\b",
            "fastapi": r"\bfastapi\b",
            "docker": r"\bdocker\b",
            "kubernetes": r"\bkubernetes\b",
            "redis": r"\bredis\b",
            "postgresql": r"\b(postgresql|postgres)\b",
            "openai": r"\bopenai\b",
            "pinecone": r"\bpinecone\b",
            "mcp": r"\bmcp\b",
            "cursor": r"\bcursor\b"
        }
        
        for tag, pattern in tech_patterns.items():
            if re.search(pattern, content):
                tags.append(tag)
        
        # Add context tags
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


class EnhancedAiMemoryMCPServer:
    """Enhanced AI Memory MCP Server with real integrations and auto-detection"""

    def __init__(self) -> None:
        self.name = "ai_memory"
        self.description = "Enhanced AI Memory for persistent development context with auto-detection"
        self.memory_manager = ComprehensiveMemoryManager()
        self.memory_intelligence = ContextualMemoryIntelligence(self.memory_manager)
        self.cache = HierarchicalCache()
        self.conversation_analyzer = ConversationAnalyzer()
        self.openai_client: Optional[Any] = None
        self.pinecone_index: Optional[Any] = None
        self.initialized = False
        self.preloaded_knowledge = False

    async def initialize(self) -> None:
        """Initialize connections and prepare the server with enhanced setup"""
        if self.initialized:
            return

        logger.info("Initializing Enhanced AI Memory MCP Server...")

        # Initialize OpenAI client with enhanced error handling
        await self._initialize_openai()
        
        # Initialize Pinecone with enhanced setup
        await self._initialize_pinecone()
        
        # Pre-load helpful AI coding knowledge
        await self._preload_ai_coding_knowledge()

        self.initialized = True
        logger.info("Enhanced AI Memory MCP Server initialized successfully")

    async def _initialize_openai(self):
        """Initialize OpenAI client with proper configuration"""
        openai_api_key = os.getenv("OPENAI_API_KEY")
        
        if not openai_api_key or openai_api_key in ['fallback-key', 'sk-development-key-fallback']:
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
            test_response = await self.openai_client.embeddings.create(
                input="test connection",
                model="text-embedding-3-small"
            )
            
            logger.info("✅ OpenAI client initialized and tested successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            self.openai_client = None

    async def _initialize_pinecone(self):
        """Initialize Pinecone with proper configuration"""
        pinecone_api_key = os.getenv("PINECONE_API_KEY")
        pinecone_environment = os.getenv("PINECONE_ENVIRONMENT", "us-east1-gcp")
        
        if not pinecone_api_key or pinecone_api_key in ['dev-pinecone-key', 'fallback-key']:
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
                "content": "Redis connection pattern for Python 3.11+: Use 'import redis.asyncio as redis_client' then 'redis_client.from_url()'. Avoid 'aioredis' package due to Python 3.11 TimeoutError compatibility issues.",
                "category": MemoryCategory.BUG_SOLUTION,
                "tags": ["python", "redis", "python311", "compatibility"],
                "importance_score": 0.9
            },
            {
                "content": "FastAPI deprecation fix: Replace @app.on_event('startup') with lifespan context manager. Use 'from contextlib import asynccontextmanager' and '@asynccontextmanager async def lifespan(app): # startup code yield # shutdown code'. Then FastAPI(lifespan=lifespan).",
                "category": MemoryCategory.CODE_DECISION,
                "tags": ["fastapi", "deprecation", "lifespan", "modernization"],
                "importance_score": 0.8
            },
            {
                "content": "OpenAI embeddings best practice: Use 'text-embedding-3-small' (1536 dimensions) for most use cases, 'text-embedding-3-large' (3072 dimensions) for highest quality. Always handle rate limits with exponential backoff and batch requests when possible.",
                "category": MemoryCategory.PERFORMANCE_TIP,
                "tags": ["openai", "embeddings", "rate_limits", "optimization"],
                "importance_score": 0.8
            },
            {
                "content": "Pinecone vector database pattern: Initialize with pinecone.init(), create index with proper dimensions matching your embedding model, use upsert() for storing vectors with metadata, query() with filters for retrieval. Always include meaningful metadata for filtering.",
                "category": MemoryCategory.AI_CODING_PATTERN,
                "tags": ["pinecone", "vector_database", "embeddings", "metadata"],
                "importance_score": 0.8
            },
            {
                "content": "Docker Compose environment variable warnings fix: Create .env file with all required variables, use 'docker-compose config' to validate, ensure no WARN messages about unset variables. Use Pulumi ESC or similar for production secret management.",
                "category": MemoryCategory.BUG_SOLUTION,
                "tags": ["docker", "environment_variables", "secrets", "pulumi"],
                "importance_score": 0.7
            },
            {
                "content": "Security pattern for API keys: Never hardcode in source code, use environment variables or secret management systems (Pulumi ESC, AWS Secrets Manager), implement key rotation, use different keys for dev/staging/prod, log key usage without exposing values.",
                "category": MemoryCategory.SECURITY_PATTERN,
                "tags": ["security", "api_keys", "secrets", "environment"],
                "importance_score": 0.9
            },
            {
                "content": "MCP server health check pattern: Implement /health endpoint returning JSON with status, dependencies, and timestamp. Include circuit breaker status, database connectivity, external API availability. Use for monitoring and load balancer health checks.",
                "category": MemoryCategory.AI_CODING_PATTERN,
                "tags": ["mcp", "health_checks", "monitoring", "reliability"],
                "importance_score": 0.8
            },
            {
                "content": "Error handling best practice: Use specific exception types, implement retry logic with exponential backoff, log errors with context (correlation IDs), provide fallback mechanisms, never expose internal errors to users. Pattern: try/except with proper logging and user-friendly messages.",
                "category": MemoryCategory.AI_CODING_PATTERN,
                "tags": ["error_handling", "logging", "retry", "user_experience"],
                "importance_score": 0.8
            }
        ]
        
        logger.info("Pre-loading AI coding knowledge base...")
        
        for knowledge in knowledge_base:
            try:
                memory_id = f"preloaded_{knowledge['category']}_{len(knowledge['tags'])}"
                await self.store_memory(
                    content=knowledge["content"],
                    category=knowledge["category"],
                    tags=knowledge["tags"],
                    importance_score=knowledge["importance_score"],
                    auto_detected=False
                )
                logger.debug(f"Pre-loaded knowledge: {knowledge['category']}")
            except Exception as e:
                logger.warning(f"Failed to pre-load knowledge item: {e}")
        
        self.preloaded_knowledge = True
        logger.info("✅ AI coding knowledge base pre-loaded successfully")

    async def get_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using OpenAI with enhanced error handling"""
        if not self.openai_client:
            logger.debug("OpenAI client not available, returning empty embedding")
            return []

        try:
            response = await self.openai_client.embeddings.create(
                input=text[:8000],  # Limit input length
                model="text-embedding-3-small",
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return []

    async def store_memory(
        self, 
        content: str, 
        category: str, 
        tags: List[str],
        importance_score: float = 0.5,
        auto_detected: bool = False
    ) -> Dict[str, Any]:
        """Store a memory with enhanced categorization and embedding"""
        if not self.initialized:
            await self.initialize()

        memory_id = f"{category}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        embedding = await self.get_embedding(content)

        memory = MemoryRecord(
            id=memory_id,
            content=content,
            category=category,
            tags=tags,
            embedding=embedding,
            created_at=datetime.now(),
            importance_score=importance_score,
            auto_detected=auto_detected,
            usage_count=0
        )

        # Store in Pinecone if available
        if self.pinecone_index and embedding:
            try:
                self.pinecone_index.upsert(
                    vectors=[
                        (
                            memory_id,
                            embedding,
                            {
                                "category": category,
                                "tags": json.dumps(tags),
                                "created_at": memory.created_at.isoformat(),
                                "importance_score": importance_score,
                                "auto_detected": auto_detected,
                                "content_preview": content[:200]  # For debugging
                            },
                        )
                    ]
                )
                logger.debug(f"Stored memory in Pinecone: {memory_id}")
            except Exception as e:
                logger.error(f"Error storing in Pinecone: {e}")

        # Store in local memory manager
        await self.memory_manager.append(
            category, json.dumps(memory.model_dump(), default=str)
        )
        
        return {
            "id": memory_id, 
            "status": "stored",
            "importance_score": importance_score,
            "auto_detected": auto_detected,
            "vector_stored": bool(self.pinecone_index and embedding)
        }

    async def auto_store_conversation(self, content: str, participants: List[str] = None) -> Dict[str, Any]:
        """Automatically analyze and store important conversations"""
        analysis = self.conversation_analyzer.analyze_conversation(content)
        
        if analysis["should_auto_store"]:
            result = await self.store_memory(
                content=content,
                category=analysis["category"],
                tags=analysis["tags"] + ["auto_detected"],
                importance_score=analysis["importance_score"],
                auto_detected=True
            )
            
            result.update({
                "auto_stored": True,
                "analysis_reason": analysis["analysis_reason"],
                "detected_category": analysis["category"]
            })
            
            logger.info(f"Auto-stored conversation: {analysis['category']} (score: {analysis['importance_score']:.2f})")
            return result
        else:
            return {
                "auto_stored": False,
                "reason": "Importance score too low",
                "score": analysis["importance_score"],
                "suggested_category": analysis["category"]
            }

    async def recall_memory(
        self, query: str, category: Optional[str] = None, limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Enhanced memory recall with better ranking and usage tracking"""
        if not self.initialized:
            await self.initialize()

        embedding = await self.get_embedding(query)
        results: List[Dict[str, Any]] = []

        # Try Pinecone first for semantic search
        if self.pinecone_index and embedding:
            try:
                filter_dict = {"category": category} if category else {}
                query_response = self.pinecone_index.query(
                    vector=embedding,
                    filter=filter_dict,
                    top_k=limit * 2,  # Get more results for better filtering
                    include_metadata=True,
                )
                
                for match in query_response.matches:
                    metadata = match.metadata
                    memory_content = await self._get_memory_content(
                        metadata.get("category", "unknown"), match.id
                    )
                    
                    if memory_content:  # Only include if content found
                        results.append({
                            "id": match.id,
                            "category": metadata.get("category", "unknown"),
                            "tags": json.loads(metadata.get("tags", "[]")),
                            "created_at": metadata.get("created_at"),
                            "relevance_score": float(match.score),
                            "importance_score": metadata.get("importance_score", 0.5),
                            "auto_detected": metadata.get("auto_detected", False),
                            "content": memory_content,
                        })
                
                # Sort by combined relevance and importance
                results.sort(key=lambda x: (x["relevance_score"] * 0.7 + x["importance_score"] * 0.3), reverse=True)
                results = results[:limit]
                
                logger.debug(f"Pinecone search returned {len(results)} results")
                
            except Exception as e:
                logger.error(f"Error searching Pinecone: {e}")

        # Fallback to local search if no Pinecone results
        if not results and category:
            try:
                history = await self.memory_manager.history(category)
                for memory_json in history[-limit:]:
                    try:
                        memory = json.loads(memory_json)
                        # Simple text matching for fallback
                        if any(word.lower() in memory.get("content", "").lower() for word in query.split()):
                            results.append({
                                "id": memory.get("id", "unknown"),
                                "category": memory.get("category", "unknown"),
                                "tags": memory.get("tags", []),
                                "created_at": memory.get("created_at"),
                                "content": memory.get("content", ""),
                                "relevance_score": 0.5,  # Default score for text matching
                                "importance_score": memory.get("importance_score", 0.5),
                                "auto_detected": memory.get("auto_detected", False)
                            })
                    except json.JSONDecodeError:
                        continue
            except Exception as e:
                logger.error(f"Error in fallback search: {e}")

        # Update usage count for returned memories
        for result in results:
            await self._update_usage_count(result["id"])

        return results

    async def _get_memory_content(self, category: str, memory_id: str) -> str:
        """Retrieve full memory content by ID with caching"""
        try:
            history = await self.memory_manager.history(category)
            for memory_json in history:
                try:
                    memory = json.loads(memory_json)
                    if memory.get("id") == memory_id:
                        return memory.get("content", "")
                except json.JSONDecodeError:
                    continue
        except Exception as e:
            logger.error(f"Error retrieving memory content: {e}")
        return ""

    async def _update_usage_count(self, memory_id: str):
        """Update usage count for a memory (for future ranking improvements)"""
        # This could be implemented to track popular memories
        pass

    def get_tools(self) -> List[Dict[str, Any]]:
        """Return enhanced list of tools provided by this MCP server"""
        return [
            {
                "name": "store_conversation",
                "description": "Store development conversations for future reference with auto-analysis",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "content": {
                            "type": "string",
                            "description": "The conversation content to store",
                        },
                        "category": {
                            "type": "string",
                            "description": "Category for the memory (architecture, bug_solution, code_decision, workflow)",
                            "enum": [
                                "architecture",
                                "bug_solution", 
                                "code_decision",
                                "workflow",
                                "ai_coding_pattern",
                                "performance_tip",
                                "security_pattern"
                            ],
                        },
                        "tags": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Tags to associate with this memory",
                        },
                    },
                    "required": ["content"],
                },
            },
            {
                "name": "auto_store_conversation",
                "description": "Automatically analyze and store important conversations",
                "parameters": {
                    "type": "object", 
                    "properties": {
                        "content": {
                            "type": "string",
                            "description": "The conversation content to analyze and potentially store",
                        },
                        "participants": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Optional list of conversation participants",
                        },
                    },
                    "required": ["content"],
                },
            },
            {
                "name": "recall_memory",
                "description": "Search previous decisions and solutions with enhanced ranking",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query to find relevant memories",
                        },
                        "category": {
                            "type": "string",
                            "description": "Optional category to filter results",
                            "enum": [
                                "architecture",
                                "bug_solution",
                                "code_decision", 
                                "workflow",
                                "ai_coding_pattern",
                                "performance_tip",
                                "security_pattern"
                            ],
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results to return",
                            "default": 5,
                        },
                    },
                    "required": ["query"],
                },
            },
            {
                "name": "get_ai_coding_tips",
                "description": "Get pre-loaded AI coding tips and best practices",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "topic": {
                            "type": "string",
                            "description": "Optional topic to filter tips (python, async, redis, etc.)",
                        },
                    },
                    "required": [],
                },
            },
        ]

    async def get_ai_coding_tips(self, topic: Optional[str] = None) -> Dict[str, Any]:
        """Get pre-loaded AI coding tips filtered by topic"""
        if not self.initialized:
            await self.initialize()
            
        # Search for pre-loaded knowledge
        query = topic if topic else "ai coding pattern best practice"
        results = await self.recall_memory(query, limit=10)
        
        # Filter for pre-loaded content and high importance
        tips = [
            {
                "content": result["content"],
                "category": result["category"],
                "tags": result["tags"],
                "importance_score": result["importance_score"]
            }
            for result in results
            if result.get("importance_score", 0) > 0.7
        ]
        
        return {
            "tips": tips,
            "topic_filter": topic,
            "total_found": len(tips)
        }

    async def execute_tool(
        self, tool_name: str, parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a tool with enhanced functionality"""
        if not self.initialized:
            await self.initialize()

        if tool_name == "store_conversation":
            content = parameters.get("content", "")
            category = parameters.get("category")
            tags = parameters.get("tags", [])
            
            # Auto-analyze if no category provided
            if not category:
                analysis = self.conversation_analyzer.analyze_conversation(content)
                category = analysis["category"]
                tags.extend(analysis["tags"])
            
            return await self.store_memory(content, category, tags)
            
        elif tool_name == "auto_store_conversation":
            content = parameters.get("content", "")
            participants = parameters.get("participants", [])
            return await self.auto_store_conversation(content, participants)
            
        elif tool_name == "recall_memory":
            query = parameters.get("query", "")
            category = parameters.get("category")
            limit = parameters.get("limit", 5)
            results = await self.recall_memory(query, category, limit)
            return {"results": results}
            
        elif tool_name == "get_ai_coding_tips":
            topic = parameters.get("topic")
            return await self.get_ai_coding_tips(topic)
            
        return {"error": f"Unknown tool: {tool_name}"}

    async def health_check(self) -> Dict[str, Any]:
        """Enhanced health check with detailed status"""
        if not self.initialized:
            await self.initialize()

        # Test OpenAI if available
        openai_status = "not_configured"
        if self.openai_client:
            try:
                await self.openai_client.embeddings.create(
                    input="health check",
                    model="text-embedding-3-small"
                )
                openai_status = "healthy"
            except Exception as e:
                openai_status = f"error: {str(e)[:100]}"

        # Test Pinecone if available  
        pinecone_status = "not_configured"
        pinecone_vector_count = 0
        if self.pinecone_index:
            try:
                stats = self.pinecone_index.describe_index_stats()
                pinecone_vector_count = stats.total_vector_count
                pinecone_status = "healthy"
            except Exception as e:
                pinecone_status = f"error: {str(e)[:100]}"

        return {
            "status": "operational" if self.initialized else "initializing",
            "openai_status": openai_status,
            "pinecone_status": pinecone_status,
            "pinecone_vector_count": pinecone_vector_count,
            "memory_manager": True,
            "preloaded_knowledge": self.preloaded_knowledge,
            "conversation_analyzer": True,
            "timestamp": datetime.now().isoformat(),
        }


# Use the enhanced server
ai_memory_server = EnhancedAiMemoryMCPServer()


async def main() -> None:
    """Run the Enhanced AI Memory MCP server indefinitely"""
    await ai_memory_server.initialize()
    try:
        while True:
            await asyncio.sleep(60)
    except KeyboardInterrupt:
        logger.info("Shutting down Enhanced AI Memory MCP Server")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
