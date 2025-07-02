# 🏗️ SOPHIA AI ARCHITECTURE PATTERNS & CODING STANDARDS
**Definitive Guide to Sophia AI System Architecture and Development Standards**

---

## 📋 **ARCHITECTURE OVERVIEW**

### **System Philosophy**
Sophia AI follows a **microservices-oriented, agent-centric architecture** with the following core principles:

1. **Infrastructure as Code (IaC)**: All infrastructure managed via Pulumi ESC
2. **Production-First**: Direct production deployment, no sandbox environments
3. **MCP-Driven Integration**: Model Context Protocol for all external services
4. **Agent Specialization**: Domain-specific AI agents for business functions
5. **Centralized Intelligence**: Unified data lake with semantic search capabilities
6. **Security-First**: SOC2 compliant with comprehensive audit trails

### **High-Level Architecture**
```
┌─────────────────────────────────────────────────────────────────┐
│                    SOPHIA AI ECOSYSTEM                          │
├─────────────────────────────────────────────────────────────────┤
│  Frontend Layer (React)                                        │
│  ├── CEO Dashboard        ├── Knowledge Dashboard              │
│  ├── Project Dashboard    └── Conversational Interface         │
├─────────────────────────────────────────────────────────────────┤
│  API Gateway Layer (FastAPI)                                   │
│  ├── Authentication       ├── Rate Limiting                    │
│  ├── Request Routing      └── Response Caching                 │
├─────────────────────────────────────────────────────────────────┤
│  Agent Orchestration Layer                                     │
│  ├── Enhanced Agents      ├── Specialized Agents              │
│  ├── Infrastructure Agents└── LangGraph Workflows             │
├─────────────────────────────────────────────────────────────────┤
│  MCP Server Network                                            │
│  ├── AI Memory (9000)     ├── Snowflake Admin (9012)          │
│  ├── Gong Intelligence    ├── HubSpot CRM                     │
│  ├── Slack Integration    └── Linear Projects                  │
├─────────────────────────────────────────────────────────────────┤
│  Data & Intelligence Layer                                     │
│  ├── Snowflake (Structured)├── Pinecone (Vectors)             │
│  ├── Semantic Search      └── Memory Management               │
├─────────────────────────────────────────────────────────────────┤
│  External Integrations                                         │
│  ├── Gong (Sales)         ├── HubSpot (CRM)                   │
│  ├── Slack (Comms)        ├── Linear (Projects)               │
│  ├── GitHub (Code)        └── OpenRouter (LLMs)               │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🏛️ **CORE ARCHITECTURAL PATTERNS**

### **1. Agent Architecture Pattern**

#### **Base Agent Hierarchy**
```python
# Standard inheritance pattern for all agents
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import logging
import time

class BaseAgent(ABC):
    """Base class for all Sophia AI agents"""
    
    def __init__(self, agent_name: str, agent_type: str, capabilities: List[str]):
        self.agent_name = agent_name
        self.agent_type = agent_type
        self.capabilities = capabilities
        self.logger = logging.getLogger(f"sophia.agents.{agent_name}")
        self.created_at = time.time()
        
        # Performance tracking
        self._instantiation_time = time.perf_counter() - self.created_at
        if self._instantiation_time > 3e-6:  # 3 microseconds
            self.logger.warning(f"Agent instantiation took {self._instantiation_time*1e6:.2f}μs (target: <3μs)")
    
    @abstractmethod
    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming requests - must be implemented by subclasses"""
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Health check endpoint - must be implemented by subclasses"""
        pass
    
    def get_capabilities(self) -> List[str]:
        """Return agent capabilities"""
        return self.capabilities
    
    def get_metadata(self) -> Dict[str, Any]:
        """Return agent metadata"""
        return {
            "name": self.agent_name,
            "type": self.agent_type,
            "capabilities": self.capabilities,
            "instantiation_time_us": self._instantiation_time * 1e6,
            "created_at": self.created_at
        }

class EnhancedAgent(BaseAgent):
    """Enhanced agents for core business intelligence"""
    
    def __init__(self, agent_name: str, capabilities: List[str]):
        super().__init__(agent_name, "enhanced", capabilities)
        # Enhanced agents have access to memory service
        self._memory_service = None
    
    @property
    def memory_service(self):
        if self._memory_service is None:
            from backend.services.comprehensive_memory_service import ComprehensiveMemoryService
            self._memory_service = ComprehensiveMemoryService()
        return self._memory_service

class SpecializedAgent(BaseAgent):
    """Specialized agents for domain-specific tasks"""
    
    def __init__(self, agent_name: str, domain: str, capabilities: List[str]):
        super().__init__(agent_name, "specialized", capabilities)
        self.domain = domain
```

#### **Agent Implementation Example**
```python
# Example: Sales Intelligence Agent
from backend.agents.enhanced.base_agent import EnhancedAgent

class SalesIntelligenceAgent(EnhancedAgent):
    def __init__(self):
        super().__init__(
            agent_name="sales_intelligence",
            capabilities=["call_analysis", "pipeline_insights", "competitive_analysis"]
        )
    
    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        try:
            request_type = request.get("type")
            
            if request_type == "analyze_calls":
                return await self._analyze_recent_calls(request.get("filters", {}))
            elif request_type == "pipeline_insights":
                return await self._generate_pipeline_insights(request.get("timeframe", "week"))
            else:
                raise ValueError(f"Unknown request type: {request_type}")
                
        except Exception as e:
            self.logger.error(f"Request processing failed: {e}")
            return {
                "status": "error",
                "message": str(e),
                "agent": self.agent_name
            }
    
    async def _analyze_recent_calls(self, filters: Dict) -> Dict[str, Any]:
        # Use semantic search to find relevant calls
        query = f"sales calls from last {filters.get('days', 7)} days"
        results = await self.memory_service.semantic_search(
            query=query,
            top_k=50,
            filters={"source": "gong_calls"}
        )
        
        # Process and analyze results
        analysis = await self._process_call_analysis(results)
        
        return {
            "status": "success",
            "data": analysis,
            "metadata": {
                "calls_analyzed": len(results),
                "agent": self.agent_name
            }
        }
    
    async def health_check(self) -> Dict[str, Any]:
        try:
            # Test memory service connection
            await self.memory_service.health_check()
            
            # Test data availability
            test_query = await self.memory_service.semantic_search(
                query="test query",
                top_k=1,
                filters={"source": "gong_calls"}
            )
            
            return {
                "status": "healthy",
                "agent": self.agent_name,
                "dependencies": {
                    "memory_service": "connected",
                    "data_availability": "confirmed" if test_query else "limited"
                }
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "agent": self.agent_name,
                "error": str(e)
            }
```

### **2. MCP Server Architecture Pattern**

#### **Standardized MCP Server Base**
```python
# Base class for all MCP servers
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import asyncio
import logging
from datetime import datetime

class StandardizedMCPServer(ABC):
    """Base class for all Sophia AI MCP servers"""
    
    def __init__(self, server_name: str, port: int, tools: List[str]):
        self.server_name = server_name
        self.port = port
        self.tools = tools
        self.logger = logging.getLogger(f"sophia.mcp.{server_name}")
        self.started_at = None
        self.health_status = "initializing"
    
    async def start_server(self):
        """Start the MCP server"""
        try:
            await self._initialize_server()
            self.started_at = datetime.utcnow()
            self.health_status = "healthy"
            self.logger.info(f"MCP server {self.server_name} started on port {self.port}")
        except Exception as e:
            self.health_status = "unhealthy"
            self.logger.error(f"Failed to start MCP server: {e}")
            raise
    
    @abstractmethod
    async def _initialize_server(self):
        """Initialize server-specific resources"""
        pass
    
    @abstractmethod
    async def handle_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming tool calls"""
        pass
    
    async def health_check(self) -> Dict[str, Any]:
        """Standard health check endpoint"""
        return {
            "server_name": self.server_name,
            "port": self.port,
            "status": self.health_status,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "tools": self.tools,
            "uptime_seconds": (datetime.utcnow() - self.started_at).total_seconds() if self.started_at else 0
        }
    
    def get_tool_schema(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get schema for a specific tool"""
        if tool_name not in self.tools:
            return None
        return self._get_tool_schema_impl(tool_name)
    
    @abstractmethod
    def _get_tool_schema_impl(self, tool_name: str) -> Dict[str, Any]:
        """Implementation-specific tool schema"""
        pass
```

#### **MCP Server Implementation Example**
```python
# Example: Gong Intelligence MCP Server
from backend.mcp.base.standardized_mcp_server import StandardizedMCPServer

class GongIntelligenceMCPServer(StandardizedMCPServer):
    def __init__(self):
        super().__init__(
            server_name="gong_intelligence",
            port=9001,
            tools=["get_recent_calls", "analyze_call_sentiment", "get_talking_points"]
        )
        self._gong_client = None
    
    async def _initialize_server(self):
        """Initialize Gong API client"""
        from backend.integrations.gong_client import GongClient
        self._gong_client = GongClient()
        await self._gong_client.authenticate()
    
    async def handle_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        try:
            if tool_name == "get_recent_calls":
                return await self._get_recent_calls(arguments)
            elif tool_name == "analyze_call_sentiment":
                return await self._analyze_call_sentiment(arguments)
            elif tool_name == "get_talking_points":
                return await self._get_talking_points(arguments)
            else:
                raise ValueError(f"Unknown tool: {tool_name}")
                
        except Exception as e:
            self.logger.error(f"Tool call failed: {e}")
            return {
                "status": "error",
                "message": str(e),
                "tool": tool_name
            }
    
    def _get_tool_schema_impl(self, tool_name: str) -> Dict[str, Any]:
        schemas = {
            "get_recent_calls": {
                "description": "Retrieve recent sales calls from Gong",
                "parameters": {
                    "days": {"type": "integer", "description": "Number of days to look back"},
                    "filters": {"type": "object", "description": "Additional filters"}
                }
            },
            "analyze_call_sentiment": {
                "description": "Analyze sentiment of specific calls",
                "parameters": {
                    "call_ids": {"type": "array", "description": "List of call IDs to analyze"}
                }
            }
        }
        return schemas.get(tool_name, {})
```

### **3. Service Layer Architecture Pattern**

#### **Comprehensive Memory Service Pattern**
```python
# Central service for all data access
from typing import Dict, List, Any, Optional
import asyncio
import logging
from datetime import datetime

class ComprehensiveMemoryService:
    """Central service for all data access and memory operations"""
    
    def __init__(self):
        self.logger = logging.getLogger("sophia.services.memory")
        self._snowflake_client = None
        self._vector_client = None
        self._connection_pool = None
    
    @property
    async def snowflake_client(self):
        """Lazy-loaded Snowflake client"""
        if self._snowflake_client is None:
            self._snowflake_client = await self._create_snowflake_client()
        return self._snowflake_client
    
    @property
    async def vector_client(self):
        """Lazy-loaded vector database client"""
        if self._vector_client is None:
            self._vector_client = await self._create_vector_client()
        return self._vector_client
    
    async def semantic_search(self, query: str, top_k: int = 10, filters: Optional[Dict] = None) -> List[Dict]:
        """Perform semantic search across all data sources"""
        try:
            # Generate query embedding
            embedding = await self._generate_embedding(query)
            
            # Search vector database
            vector_results = await self._search_vectors(embedding, top_k, filters)
            
            # Enrich with structured data
            enriched_results = await self._enrich_with_structured_data(vector_results)
            
            return enriched_results
            
        except Exception as e:
            self.logger.error(f"Semantic search failed: {e}")
            raise
    
    async def execute_query(self, query: str, parameters: Optional[List] = None) -> List[Dict]:
        """Execute SQL query against Snowflake"""
        try:
            client = await self.snowflake_client
            return await client.execute_query(query, parameters)
        except Exception as e:
            self.logger.error(f"Query execution failed: {e}")
            raise
    
    async def store_memory(self, content: str, metadata: Dict[str, Any]) -> str:
        """Store new memory with vector embedding"""
        try:
            # Generate embedding
            embedding = await self._generate_embedding(content)
            
            # Store in vector database
            memory_id = await self._store_vector(content, embedding, metadata)
            
            # Store structured data if applicable
            if metadata.get("structured_data"):
                await self._store_structured_data(memory_id, metadata["structured_data"])
            
            return memory_id
            
        except Exception as e:
            self.logger.error(f"Memory storage failed: {e}")
            raise
    
    async def health_check(self) -> Dict[str, Any]:
        """Comprehensive health check"""
        try:
            # Test Snowflake connection
            snowflake_health = await self._test_snowflake_connection()
            
            # Test vector database connection
            vector_health = await self._test_vector_connection()
            
            return {
                "status": "healthy" if snowflake_health and vector_health else "degraded",
                "snowflake": "connected" if snowflake_health else "disconnected",
                "vector_db": "connected" if vector_health else "disconnected",
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
```

### **4. API Layer Architecture Pattern**

#### **FastAPI Route Organization**
```python
# Standardized API route structure
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, List, Any
import logging

# Create router with prefix and tags
router = APIRouter(prefix="/api/v1/intelligence", tags=["intelligence"])
logger = logging.getLogger("sophia.api.intelligence")

# Dependency injection for services
async def get_memory_service():
    from backend.services.comprehensive_memory_service import ComprehensiveMemoryService
    return ComprehensiveMemoryService()

async def get_agent_orchestrator():
    from backend.agents.enhanced.cortex_agent_orchestrator import CortexAgentOrchestrator
    return CortexAgentOrchestrator()

# Standard route patterns
@router.post("/query")
async def query_intelligence(
    request: Dict[str, Any],
    memory_service = Depends(get_memory_service),
    agent_orchestrator = Depends(get_agent_orchestrator)
):
    """Standard intelligence query endpoint"""
    try:
        # Validate request
        if not request.get("query"):
            raise HTTPException(status_code=400, detail="Query parameter required")
        
        # Route to appropriate agent
        agent_type = request.get("agent_type", "general")
        agent = await agent_orchestrator.get_agent(agent_type)
        
        # Process request
        result = await agent.process_request(request)
        
        return {
            "status": "success",
            "data": result,
            "metadata": {
                "agent": agent.agent_name,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Query processing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check(
    memory_service = Depends(get_memory_service),
    agent_orchestrator = Depends(get_agent_orchestrator)
):
    """Standard health check endpoint"""
    try:
        # Check all dependencies
        memory_health = await memory_service.health_check()
        agent_health = await agent_orchestrator.health_check()
        
        overall_status = "healthy" if (
            memory_health.get("status") == "healthy" and
            agent_health.get("status") == "healthy"
        ) else "degraded"
        
        return {
            "status": overall_status,
            "components": {
                "memory_service": memory_health,
                "agent_orchestrator": agent_health
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }
```

---

## 🔧 **CODING STANDARDS**

### **1. Python Code Standards**

#### **Type Hints (MANDATORY)**
```python
# CORRECT: Always use type hints
from typing import Dict, List, Optional, Union, Any
import asyncio

async def process_data(
    data: List[Dict[str, Any]], 
    filters: Optional[Dict[str, str]] = None
) -> Dict[str, Union[str, int, List]]:
    """Process data with optional filters"""
    pass

# INCORRECT: Missing type hints
async def process_data(data, filters=None):  # ❌ No type hints
    pass
```

#### **Async/Await Patterns (REQUIRED)**
```python
# CORRECT: Use async/await for I/O operations
import asyncio
import aiohttp

class DataService:
    async def fetch_external_data(self, url: str) -> Dict[str, Any]:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                return await response.json()
    
    async def process_multiple_sources(self, urls: List[str]) -> List[Dict]:
        tasks = [self.fetch_external_data(url) for url in urls]
        return await asyncio.gather(*tasks)

# INCORRECT: Blocking I/O operations
import requests

def fetch_external_data(self, url: str):  # ❌ Blocking
    response = requests.get(url)
    return response.json()
```

#### **Error Handling Standards**
```python
# CORRECT: Comprehensive error handling
import logging
from typing import Optional

class ServiceClass:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    async def risky_operation(self, data: Dict) -> Optional[Dict]:
        try:
            # Validate input
            if not data.get("required_field"):
                raise ValueError("required_field is missing")
            
            # Perform operation
            result = await self._perform_operation(data)
            return result
            
        except ValueError as e:
            # Handle validation errors
            self.logger.warning(f"Validation error: {e}")
            return None
            
        except ConnectionError as e:
            # Handle connection errors with retry
            self.logger.error(f"Connection failed: {e}")
            return await self._retry_operation(data)
            
        except Exception as e:
            # Handle unexpected errors
            self.logger.error(f"Unexpected error: {e}")
            raise  # Re-raise for upstream handling

# INCORRECT: Poor error handling
def risky_operation(self, data):
    try:
        return self._perform_operation(data)
    except:  # ❌ Bare except
        pass  # ❌ Silent failure
```

#### **Logging Standards**
```python
# CORRECT: Structured logging
import logging
import json
from datetime import datetime

class LoggingService:
    def __init__(self, service_name: str):
        self.logger = logging.getLogger(f"sophia.{service_name}")
        self.service_name = service_name
    
    def log_operation(self, operation: str, data: Dict, level: str = "info"):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "service": self.service_name,
            "operation": operation,
            "data": data
        }
        
        if level == "info":
            self.logger.info(json.dumps(log_entry))
        elif level == "error":
            self.logger.error(json.dumps(log_entry))
        elif level == "warning":
            self.logger.warning(json.dumps(log_entry))

# INCORRECT: Poor logging
def some_operation(self):
    print("Starting operation")  # ❌ Use logging, not print
    logging.info("Operation completed")  # ❌ No context
```

### **2. Performance Standards**

#### **Agent Instantiation Performance**
```python
# CORRECT: Optimized agent instantiation
import time
from typing import Optional

class PerformantAgent:
    def __init__(self, agent_name: str):
        start_time = time.perf_counter()
        
        # Minimal initialization
        self.agent_name = agent_name
        self.created_at = time.time()
        
        # Defer heavy operations
        self._heavy_resource = None
        self._model = None
        
        # Track instantiation time
        instantiation_time = time.perf_counter() - start_time
        if instantiation_time > 3e-6:  # 3 microseconds
            logging.warning(f"Slow instantiation: {instantiation_time*1e6:.2f}μs")
    
    @property
    def heavy_resource(self):
        """Lazy-load heavy resources"""
        if self._heavy_resource is None:
            self._heavy_resource = self._initialize_heavy_resource()
        return self._heavy_resource
    
    @property
    def model(self):
        """Lazy-load ML models"""
        if self._model is None:
            self._model = self._load_model()
        return self._model

# INCORRECT: Heavy initialization
class SlowAgent:
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.heavy_resource = self._initialize_heavy_resource()  # ❌ Slow
        self.model = self._load_model()  # ❌ Blocks instantiation
```

#### **Database Query Optimization**
```python
# CORRECT: Optimized database queries
class OptimizedDataService:
    async def get_recent_data(self, days: int = 7, limit: int = 100) -> List[Dict]:
        # Use parameterized queries
        query = """
        SELECT id, created_at, data
        FROM events 
        WHERE created_at >= DATEADD(day, -%s, CURRENT_TIMESTAMP())
        ORDER BY created_at DESC
        LIMIT %s
        """
        return await self.memory_service.execute_query(query, [days, limit])
    
    async def batch_insert(self, records: List[Dict]) -> None:
        # Use batch operations
        if not records:
            return
        
        # Process in chunks to avoid memory issues
        chunk_size = 1000
        for i in range(0, len(records), chunk_size):
            chunk = records[i:i + chunk_size]
            await self._insert_chunk(chunk)

# INCORRECT: Inefficient queries
class SlowDataService:
    async def get_recent_data(self):
        # ❌ No limits, no parameters
        query = "SELECT * FROM events ORDER BY created_at DESC"
        return await self.memory_service.execute_query(query)
    
    async def insert_records(self, records: List[Dict]):
        # ❌ Individual inserts
        for record in records:
            await self._insert_single(record)
```

### **3. Security Standards**

#### **Secret Management (CRITICAL)**
```python
# CORRECT: Environment variable usage
import os
from typing import Optional

class SecureService:
    def __init__(self):
        # Always use environment variables
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.db_password = os.getenv("SNOWFLAKE_PASSWORD")
        
        # Validate required secrets
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable required")
        
        # Never log secrets
        self.logger.info(f"Service initialized with API key: {'*' * len(self.api_key)}")
    
    def get_connection_string(self) -> str:
        """Build connection string from environment variables"""
        account = os.getenv("SNOWFLAKE_ACCOUNT")
        user = os.getenv("SNOWFLAKE_USER")
        password = os.getenv("SNOWFLAKE_PASSWORD")
        
        if not all([account, user, password]):
            raise ValueError("Missing required Snowflake credentials")
        
        return f"snowflake://{user}:{password}@{account}"

# INCORRECT: Hardcoded secrets
class InsecureService:
    def __init__(self):
        self.api_key = "sk-1234567890abcdef"  # ❌ Hardcoded secret
        self.db_password = "password123"      # ❌ Hardcoded password
        
        # ❌ Logging secrets
        self.logger.info(f"API key: {self.api_key}")
```

#### **Input Validation**
```python
# CORRECT: Comprehensive input validation
from typing import Dict, Any
import re

class ValidatedService:
    def validate_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and sanitize request data"""
        errors = []
        
        # Required fields
        if not request.get("query"):
            errors.append("query field is required")
        
        # Type validation
        if "limit" in request and not isinstance(request["limit"], int):
            errors.append("limit must be an integer")
        
        # Range validation
        if "limit" in request and not (1 <= request["limit"] <= 1000):
            errors.append("limit must be between 1 and 1000")
        
        # String sanitization
        if "query" in request:
            query = str(request["query"]).strip()
            if len(query) > 1000:
                errors.append("query too long (max 1000 characters)")
            request["query"] = query
        
        if errors:
            raise ValueError(f"Validation errors: {', '.join(errors)}")
        
        return request

# INCORRECT: No validation
class UnvalidatedService:
    def process_request(self, request):
        # ❌ No validation
        query = request["query"]  # Could raise KeyError
        limit = request.get("limit", 999999)  # ❌ No upper bound
        return self._execute_query(query, limit)
```

---

## 📁 **FILE ORGANIZATION STANDARDS**

### **Directory Structure Rules**
```
backend/
├── agents/                    # AI agent implementations
│   ├── enhanced/             # Core business intelligence agents
│   │   ├── __init__.py
│   │   ├── base_agent.py     # Base class for enhanced agents
│   │   ├── sales_intelligence_agent.py
│   │   └── customer_health_agent.py
│   ├── specialized/          # Domain-specific agents
│   │   ├── __init__.py
│   │   ├── base_specialized_agent.py
│   │   └── marketing_analysis_agent.py
│   └── infrastructure/       # Infrastructure management agents
├── api/                      # FastAPI route definitions
│   ├── __init__.py
│   ├── intelligence_routes.py
│   ├── health_routes.py
│   └── auth_routes.py
├── core/                     # Core utilities and configuration
│   ├── __init__.py
│   ├── config.py
│   ├── logging_config.py
│   └── security.py
├── infrastructure/           # IaC orchestration and adapters
│   ├── core/                # Core IaC components
│   ├── adapters/            # Platform-specific adapters
│   └── sophia_iac_orchestrator.py
├── mcp/                      # MCP server implementations
│   ├── base/                # Base MCP server classes
│   ├── ai_memory_mcp_server.py
│   └── snowflake_admin_mcp_server.py
├── services/                 # Business logic services
│   ├── __init__.py
│   ├── comprehensive_memory_service.py
│   ├── semantic_layer_service.py
│   └── automated_insights_service.py
└── workflows/                # LangGraph orchestration
    ├── __init__.py
    └── langgraph_agent_orchestration.py
```

### **Naming Conventions**
```python
# File naming: snake_case
sales_intelligence_agent.py
comprehensive_memory_service.py
snowflake_admin_mcp_server.py

# Class naming: PascalCase
class SalesIntelligenceAgent:
class ComprehensiveMemoryService:
class SnowflakeAdminMCPServer:

# Function/method naming: snake_case
async def process_request():
async def semantic_search():
async def health_check():

# Variable naming: snake_case
agent_name = "sales_intelligence"
memory_service = ComprehensiveMemoryService()
api_response = await client.get_data()

# Constants: UPPER_SNAKE_CASE
MAX_QUERY_LENGTH = 1000
DEFAULT_TIMEOUT = 30
SNOWFLAKE_SCHEMA = "SOPHIA_AI_CORE"
```

---

## 🔄 **INTEGRATION PATTERNS**

### **1. MCP Client Integration**
```python
# Standard MCP client usage pattern
from backend.mcp.mcp_client import MCPClient

class BusinessIntelligenceService:
    def __init__(self):
        self.mcp_client = MCPClient()
    
    async def get_sales_insights(self, timeframe: str) -> Dict[str, Any]:
        # Call Gong intelligence MCP server
        gong_data = await self.mcp_client.call_tool(
            server="gong_intelligence",
            tool="get_recent_calls",
            arguments={"timeframe": timeframe}
        )
        
        # Call HubSpot CRM MCP server
        crm_data = await self.mcp_client.call_tool(
            server="hubspot_crm",
            tool="get_pipeline_data",
            arguments={"timeframe": timeframe}
        )
        
        # Combine and analyze
        return await self._analyze_combined_data(gong_data, crm_data)
```

### **2. Database Integration Pattern**
```python
# Standard database access pattern
from backend.services.comprehensive_memory_service import ComprehensiveMemoryService

class DataAnalysisService:
    def __init__(self):
        self.memory_service = ComprehensiveMemoryService()
    
    async def analyze_customer_health(self, customer_id: str) -> Dict[str, Any]:
        # Semantic search for customer interactions
        interactions = await self.memory_service.semantic_search(
            query=f"customer interactions for {customer_id}",
            filters={"customer_id": customer_id}
        )
        
        # Structured query for metrics
        metrics_query = """
        SELECT 
            revenue_last_30_days,
            support_tickets_count,
            last_interaction_date
        FROM customer_metrics 
        WHERE customer_id = %s
        """
        metrics = await self.memory_service.execute_query(metrics_query, [customer_id])
        
        # Combine for analysis
        return await self._calculate_health_score(interactions, metrics)
```

### **3. External API Integration Pattern**
```python
# Standard external API integration
import aiohttp
import os
from typing import Dict, Any, Optional

class ExternalAPIClient:
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.api_key = os.getenv(f"{service_name.upper()}_API_KEY")
        self.base_url = os.getenv(f"{service_name.upper()}_BASE_URL")
        self.logger = logging.getLogger(f"sophia.integrations.{service_name}")
        
        if not self.api_key:
            raise ValueError(f"{service_name.upper()}_API_KEY environment variable required")
    
    async def make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make authenticated request to external API"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.request(method, url, headers=headers, json=data) as response:
                    response.raise_for_status()
                    return await response.json()
                    
        except aiohttp.ClientError as e:
            self.logger.error(f"API request failed: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            raise
```

---

## 🧪 **TESTING STANDARDS**

### **1. Unit Testing Pattern**
```python
# Standard unit test structure
import pytest
from unittest.mock import AsyncMock, MagicMock
from backend.agents.enhanced.sales_intelligence_agent import SalesIntelligenceAgent

class TestSalesIntelligenceAgent:
    @pytest.fixture
    async def agent(self):
        """Create agent instance for testing"""
        agent = SalesIntelligenceAgent()
        # Mock dependencies
        agent.memory_service = AsyncMock()
        return agent
    
    async def test_process_request_success(self, agent):
        """Test successful request processing"""
        # Arrange
        request = {
            "type": "analyze_calls",
            "filters": {"days": 7}
        }
        agent.memory_service.semantic_search.return_value = [
            {"call_id": "123", "sentiment": "positive"}
        ]
        
        # Act
        result = await agent.process_request(request)
        
        # Assert
        assert result["status"] == "success"
        assert "data" in result
        agent.memory_service.semantic_search.assert_called_once()
    
    async def test_process_request_invalid_type(self, agent):
        """Test handling of invalid request type"""
        # Arrange
        request = {"type": "invalid_type"}
        
        # Act
        result = await agent.process_request(request)
        
        # Assert
        assert result["status"] == "error"
        assert "Unknown request type" in result["message"]
    
    async def test_health_check_healthy(self, agent):
        """Test health check when all dependencies are healthy"""
        # Arrange
        agent.memory_service.health_check.return_value = {"status": "healthy"}
        agent.memory_service.semantic_search.return_value = [{"test": "data"}]
        
        # Act
        result = await agent.health_check()
        
        # Assert
        assert result["status"] == "healthy"
        assert result["dependencies"]["memory_service"] == "connected"
```

### **2. Integration Testing Pattern**
```python
# Integration test for MCP servers
import pytest
import asyncio
from backend.mcp.ai_memory_mcp_server import AIMemoryMCPServer

class TestAIMemoryMCPServerIntegration:
    @pytest.fixture
    async def mcp_server(self):
        """Create and start MCP server for testing"""
        server = AIMemoryMCPServer()
        await server.start_server()
        yield server
        # Cleanup
        await server.stop_server()
    
    async def test_semantic_search_tool(self, mcp_server):
        """Test semantic search tool integration"""
        # Arrange
        arguments = {
            "query": "recent sales calls",
            "top_k": 5
        }
        
        # Act
        result = await mcp_server.handle_tool_call("semantic_search", arguments)
        
        # Assert
        assert result["status"] == "success"
        assert isinstance(result["data"], list)
        assert len(result["data"]) <= 5
    
    async def test_health_check_endpoint(self, mcp_server):
        """Test health check endpoint"""
        # Act
        health = await mcp_server.health_check()
        
        # Assert
        assert health["status"] == "healthy"
        assert health["server_name"] == "ai_memory"
        assert "uptime_seconds" in health
```

### **3. Performance Testing Pattern**
```python
# Performance test for agent instantiation
import time
import pytest
from backend.agents.enhanced.sales_intelligence_agent import SalesIntelligenceAgent

class TestPerformance:
    def test_agent_instantiation_speed(self):
        """Test that agent instantiation is under 3 microseconds"""
        # Warm up
        for _ in range(10):
            SalesIntelligenceAgent()
        
        # Measure instantiation time
        times = []
        for _ in range(100):
            start_time = time.perf_counter()
            agent = SalesIntelligenceAgent()
            end_time = time.perf_counter()
            times.append(end_time - start_time)
        
        # Calculate statistics
        avg_time = sum(times) / len(times)
        max_time = max(times)
        
        # Assert performance requirements
        assert avg_time < 3e-6, f"Average instantiation time {avg_time*1e6:.2f}μs exceeds 3μs"
        assert max_time < 10e-6, f"Max instantiation time {max_time*1e6:.2f}μs exceeds 10μs"
    
    async def test_query_response_time(self):
        """Test that queries respond within 200ms"""
        agent = SalesIntelligenceAgent()
        request = {"type": "analyze_calls", "filters": {"days": 1}}
        
        start_time = time.perf_counter()
        result = await agent.process_request(request)
        end_time = time.perf_counter()
        
        response_time = end_time - start_time
        assert response_time < 0.2, f"Query response time {response_time:.3f}s exceeds 200ms"
```

---

## 📊 **MONITORING & OBSERVABILITY**

### **1. Logging Standards**
```python
# Structured logging implementation
import logging
import json
from datetime import datetime
from typing import Dict, Any

class StructuredLogger:
    def __init__(self, service_name: str):
        self.logger = logging.getLogger(f"sophia.{service_name}")
        self.service_name = service_name
    
    def log_event(self, event_type: str, data: Dict[str, Any], level: str = "info"):
        """Log structured event"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "service": self.service_name,
            "event_type": event_type,
            "data": data,
            "level": level
        }
        
        log_message = json.dumps(log_entry)
        
        if level == "info":
            self.logger.info(log_message)
        elif level == "warning":
            self.logger.warning(log_message)
        elif level == "error":
            self.logger.error(log_message)
        elif level == "debug":
            self.logger.debug(log_message)
    
    def log_performance(self, operation: str, duration: float, metadata: Dict = None):
        """Log performance metrics"""
        self.log_event("performance", {
            "operation": operation,
            "duration_seconds": duration,
            "metadata": metadata or {}
        })
    
    def log_error(self, error: Exception, context: Dict = None):
        """Log error with context"""
        self.log_event("error", {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context or {}
        }, level="error")
```

### **2. Health Check Standards**
```python
# Comprehensive health check implementation
from typing import Dict, List, Any
import asyncio
from datetime import datetime

class HealthCheckManager:
    def __init__(self):
        self.checks = []
        self.logger = StructuredLogger("health_check")
    
    def register_check(self, name: str, check_func, timeout: float = 5.0):
        """Register a health check"""
        self.checks.append({
            "name": name,
            "check_func": check_func,
            "timeout": timeout
        })
    
    async def run_all_checks(self) -> Dict[str, Any]:
        """Run all registered health checks"""
        results = {}
        overall_healthy = True
        
        for check in self.checks:
            try:
                # Run check with timeout
                result = await asyncio.wait_for(
                    check["check_func"](),
                    timeout=check["timeout"]
                )
                results[check["name"]] = result
                
                if result.get("status") != "healthy":
                    overall_healthy = False
                    
            except asyncio.TimeoutError:
                results[check["name"]] = {
                    "status": "timeout",
                    "error": f"Check timed out after {check['timeout']}s"
                }
                overall_healthy = False
                
            except Exception as e:
                results[check["name"]] = {
                    "status": "error",
                    "error": str(e)
                }
                overall_healthy = False
        
        return {
            "status": "healthy" if overall_healthy else "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "checks": results
        }
```

---

## 🚀 **DEPLOYMENT STANDARDS**

### **1. Environment Configuration**
```python
# Environment-specific configuration
import os
from typing import Dict, Any
from enum import Enum

class Environment(Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"

class Config:
    def __init__(self):
        self.environment = Environment(os.getenv("SOPHIA_ENVIRONMENT", "development"))
        self.debug = self.environment == Environment.DEVELOPMENT
        
        # Database configuration
        self.snowflake_account = os.getenv("SNOWFLAKE_ACCOUNT")
        self.snowflake_user = os.getenv("SNOWFLAKE_USER")
        self.snowflake_password = os.getenv("SNOWFLAKE_PASSWORD")
        
        # API configuration
        self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
        self.api_rate_limit = int(os.getenv("API_RATE_LIMIT", "1000"))
        
        # MCP server configuration
        self.mcp_base_port = int(os.getenv("MCP_BASE_PORT", "9000"))
        
        # Validate required configuration
        self._validate_config()
    
    def _validate_config(self):
        """Validate required configuration"""
        required_vars = [
            "SNOWFLAKE_ACCOUNT",
            "SNOWFLAKE_USER", 
            "SNOWFLAKE_PASSWORD",
            "OPENROUTER_API_KEY"
        ]
        
        missing = [var for var in required_vars if not os.getenv(var)]
        if missing:
            raise ValueError(f"Missing required environment variables: {missing}")
    
    def get_database_url(self) -> str:
        """Get database connection URL"""
        return f"snowflake://{self.snowflake_user}:{self.snowflake_password}@{self.snowflake_account}"
    
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.environment == Environment.PRODUCTION
```

### **2. Startup Sequence**
```python
# Application startup sequence
import asyncio
import logging
from typing import List
from backend.core.config import Config
from backend.mcp.mcp_client import MCPClient

class ApplicationStartup:
    def __init__(self):
        self.config = Config()
        self.logger = logging.getLogger("sophia.startup")
        self.startup_tasks = []
    
    async def initialize_application(self):
        """Initialize the complete Sophia AI application"""
        try:
            self.logger.info("Starting Sophia AI application initialization")
            
            # 1. Initialize configuration
            await self._initialize_config()
            
            # 2. Start MCP servers
            await self._start_mcp_servers()
            
            # 3. Initialize services
            await self._initialize_services()
            
            # 4. Initialize agents
            await self._initialize_agents()
            
            # 5. Start API server
            await self._start_api_server()
            
            # 6. Run health checks
            await self._run_startup_health_checks()
            
            self.logger.info("Sophia AI application initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Application initialization failed: {e}")
            await self._cleanup()
            raise
    
    async def _start_mcp_servers(self):
        """Start all MCP servers"""
        mcp_servers = [
            "ai_memory",
            "snowflake_admin", 
            "gong_intelligence",
            "hubspot_crm",
            "slack_integration"
        ]
        
        for server_name in mcp_servers:
            try:
                # Start server
                await self._start_mcp_server(server_name)
                self.logger.info(f"MCP server {server_name} started successfully")
            except Exception as e:
                self.logger.error(f"Failed to start MCP server {server_name}: {e}")
                raise
    
    async def _run_startup_health_checks(self):
        """Run comprehensive health checks after startup"""
        health_manager = HealthCheckManager()
        
        # Register all health checks
        health_manager.register_check("database", self._check_database_health)
        health_manager.register_check("mcp_servers", self._check_mcp_health)
        health_manager.register_check("external_apis", self._check_external_apis)
        
        # Run checks
        results = await health_manager.run_all_checks()
        
        if results["status"] != "healthy":
            raise RuntimeError(f"Startup health checks failed: {results}")
        
        self.logger.info("All startup health checks passed")
```

---

**This architecture guide provides the foundation for all Sophia AI development. Every AI coder should reference these patterns to ensure consistency, performance, and maintainability across the entire platform.**

---

*Last Updated: June 27, 2025*  
*Version: 1.0*  
*Status: Production Standard*

