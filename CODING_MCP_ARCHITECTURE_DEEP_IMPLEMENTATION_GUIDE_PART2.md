# 🚀 CODING MCP ARCHITECTURE - DEEP IMPLEMENTATION GUIDE (PART 2)
**Continuation of Complete Implementation, Testing, and Deployment**

---

## 🏗️ ARCHITECTURE CONSOLIDATION PLAN (CONTINUED)

### **Phase 2: MCP Server Integration (Continued)**

#### **2.1 Complete Coding MCP Server Orchestrator**

```python
# backend/services/coding_mcp_orchestrator.py (continued)
        
        # Initialize Portkey gateway
        self.portkey_gateway = PortkeyGateway(
            config={
                "models": {
                    "claude-3-5-sonnet": {
                        "provider": "anthropic",
                        "cost_per_1k_tokens": 0.015,
                        "context_window": 200000,
                        "strengths": ["code_generation", "architecture", "complex_reasoning"]
                    },
                    "gpt-4o": {
                        "provider": "openai",
                        "cost_per_1k_tokens": 0.03,
                        "context_window": 128000,
                        "strengths": ["debugging", "refactoring", "documentation"]
                    },
                    "deepseek-v3": {
                        "provider": "deepseek",
                        "cost_per_1k_tokens": 0.001,
                        "context_window": 32000,
                        "strengths": ["code_completion", "syntax_correction"]
                    }
                },
                "routing": {
                    "task_routing": {
                        "generate": ["claude-3-5-sonnet", "gpt-4o"],
                        "refactor": ["gpt-4o", "claude-3-5-sonnet"],
                        "debug": ["gpt-4o", "deepseek-v3"],
                        "review": ["claude-3-5-sonnet"],
                        "document": ["gpt-4o"],
                        "test": ["claude-3-5-sonnet", "gpt-4o"],
                        "deploy": ["gpt-4o"]
                    },
                    "complexity_routing": {
                        "simple": ["deepseek-v3", "gpt-4o"],
                        "moderate": ["gpt-4o"],
                        "complex": ["claude-3-5-sonnet"],
                        "architecture": ["claude-3-5-sonnet"]
                    }
                }
            }
        )
        
        # Initialize MCP clients
        for name, client in self.mcp_clients.items():
            try:
                await client.connect()
                logger.info(f"✅ Connected to {name} MCP server")
            except Exception as e:
                logger.warning(f"⚠️ Failed to connect to {name}: {e}")
                
        logger.info("🎉 Coding MCP Orchestrator initialized")
        
    async def process_request(self, request: CodingRequest) -> CodingResponse:
        """Process a coding request through the orchestrated MCP servers"""
        logger.info(f"📝 Processing {request.task.value} request: {request.description[:100]}...")
        
        try:
            # Step 1: Retrieve context from memory
            context = await self._retrieve_context(request)
            
            # Step 2: Analyze with appropriate MCP servers
            analysis = await self._analyze_request(request, context)
            
            # Step 3: Generate/process code
            result = await self._execute_task(request, context, analysis)
            
            # Step 4: Validate and enhance result
            validated_result = await self._validate_result(result, request)
            
            # Step 5: Store in memory for future reference
            await self._store_result(request, validated_result)
            
            return validated_result
            
        except Exception as e:
            logger.error(f"❌ Failed to process request: {e}")
            return CodingResponse(
                success=False,
                errors=[str(e)]
            )
            
    async def _retrieve_context(self, request: CodingRequest) -> Dict[str, Any]:
        """Retrieve relevant context from memory"""
        context = {
            "related_code": [],
            "patterns": [],
            "previous_decisions": [],
            "project_structure": None
        }
        
        try:
            # Generate embedding for the request
            embedding = await self._generate_embedding(request.description)
            
            # Search for related code
            code_results = await self.memory_service.search(
                query_vector=embedding,
                collection=MemoryCollection.CODE,
                limit=5,
                metadata_filter={"project": request.context.get("project")} if request.context else None
            )
            context["related_code"] = [r.content for r in code_results]
            
            # Search for patterns
            pattern_results = await self.memory_service.search(
                query_vector=embedding,
                collection=MemoryCollection.KNOWLEDGE,
                limit=3,
                metadata_filter={"type": "pattern"}
            )
            context["patterns"] = [r.content for r in pattern_results]
            
            # Get project structure from GitHub if available
            if "github" in self.mcp_clients and request.context and request.context.get("repository"):
                try:
                    structure = await self.mcp_clients["github"].call_tool(
                        "get_repository_structure",
                        {"repository": request.context["repository"]}
                    )
                    context["project_structure"] = structure
                except Exception as e:
                    logger.warning(f"Failed to get project structure: {e}")
                    
        except Exception as e:
            logger.error(f"Failed to retrieve context: {e}")
            
        return context
        
    async def _analyze_request(self, request: CodingRequest, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the request using appropriate MCP servers"""
        analysis = {
            "complexity": "moderate",
            "requirements": [],
            "constraints": [],
            "suggestions": []
        }
        
        # Determine complexity
        prompt = f"""
        Analyze this coding request and determine its complexity:
        
        Task: {request.task.value}
        Description: {request.description}
        Context: {json.dumps(context.get("patterns", [])[:2])}
        
        Classify as: simple, moderate, complex, or architecture
        Provide brief reasoning.
        """
        
        complexity_result = await self.portkey_gateway.route_and_complete(
            prompt=prompt,
            task=TaskType.ANALYSIS,
            complexity=TaskComplexity.SIMPLE,
            max_tokens=200
        )
        
        # Parse complexity (simplified for example)
        if "simple" in complexity_result.lower():
            analysis["complexity"] = "simple"
        elif "complex" in complexity_result.lower():
            analysis["complexity"] = "complex"
        elif "architecture" in complexity_result.lower():
            analysis["complexity"] = "architecture"
            
        # Get code quality requirements from Codacy if available
        if "codacy" in self.mcp_clients and request.files:
            try:
                for file in request.files[:3]:  # Limit to 3 files
                    quality_check = await self.mcp_clients["codacy"].call_tool(
                        "analyze_file",
                        {"file_path": file}
                    )
                    if quality_check.get("issues"):
                        analysis["constraints"].extend(quality_check["issues"])
            except Exception as e:
                logger.warning(f"Codacy analysis failed: {e}")
                
        return analysis
        
    async def _execute_task(
        self,
        request: CodingRequest,
        context: Dict[str, Any],
        analysis: Dict[str, Any]
    ) -> CodingResponse:
        """Execute the actual coding task"""
        
        # Build comprehensive prompt
        prompt = self._build_task_prompt(request, context, analysis)
        
        # Route to appropriate model based on task and complexity
        result_text = ""
        async for chunk in self.portkey_gateway.route_and_complete(
            prompt=prompt,
            task=self._map_coding_task_to_task_type(request.task),
            complexity=self._map_complexity(analysis["complexity"]),
            max_tokens=4000,
            temperature=0.3  # Lower temperature for code generation
        ):
            result_text += chunk
            
        # Parse the result
        response = self._parse_llm_response(result_text)
        
        # Execute task-specific operations
        if request.task == CodingTask.DEPLOY and "lambda_labs" in self.mcp_clients:
            try:
                deploy_result = await self.mcp_clients["lambda_labs"].call_tool(
                    "deploy_code",
                    {
                        "code": response.code,
                        "service": request.context.get("service", "test-service"),
                        "environment": request.context.get("environment", "development")
                    }
                )
                response.artifacts = {"deployment": deploy_result}
            except Exception as e:
                response.errors = response.errors or []
                response.errors.append(f"Deployment failed: {e}")
                
        return response
        
    async def _validate_result(
        self,
        result: CodingResponse,
        request: CodingRequest
    ) -> CodingResponse:
        """Validate and enhance the result"""
        
        # Run Codacy analysis on generated code
        if result.code and "codacy" in self.mcp_clients:
            try:
                analysis = await self.mcp_clients["codacy"].call_tool(
                    "analyze_code",
                    {"code": result.code, "language": request.context.get("language", "python")}
                )
                
                if analysis.get("score", 0) < 8.0:
                    # Try to improve the code
                    improvement_prompt = f"""
                    The following code has quality issues:
                    
                    Code:
                    ```
                    {result.code}
                    ```
                    
                    Issues:
                    {json.dumps(analysis.get("issues", []))}
                    
                    Please provide an improved version that addresses these issues.
                    """
                    
                    improved_code = ""
                    async for chunk in self.portkey_gateway.route_and_complete(
                        prompt=improvement_prompt,
                        task=TaskType.CODE_GENERATION,
                        complexity=TaskComplexity.MODERATE,
                        max_tokens=4000,
                        temperature=0.2
                    ):
                        improved_code += chunk
                        
                    # Update result with improved code
                    result.code = self._extract_code_from_response(improved_code)
                    result.analysis = analysis
                    
            except Exception as e:
                logger.warning(f"Code validation failed: {e}")
                
        return result
        
    async def _store_result(self, request: CodingRequest, result: CodingResponse) -> None:
        """Store the result in memory for future reference"""
        if not result.success or not result.code:
            return
            
        try:
            # Generate embedding for the code
            embedding = await self._generate_embedding(f"{request.description}\n{result.code}")
            
            # Store in code collection
            await self.memory_service.store(
                content=result.code,
                vector=embedding,
                metadata={
                    "task": request.task.value,
                    "description": request.description,
                    "language": request.context.get("language", "python"),
                    "project": request.context.get("project"),
                    "quality_score": result.analysis.get("score") if result.analysis else None,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                },
                collection=MemoryCollection.CODE
            )
            
            # Store patterns if this was a complex task
            if request.task in [CodingTask.GENERATE, CodingTask.REFACTOR] and len(result.code) > 500:
                pattern_summary = f"Pattern: {request.task.value} - {request.description[:100]}"
                await self.memory_service.store(
                    content=pattern_summary,
                    vector=embedding,
                    metadata={
                        "type": "pattern",
                        "task": request.task.value,
                        "code_snippet": result.code[:500]
                    },
                    collection=MemoryCollection.KNOWLEDGE
                )
                
        except Exception as e:
            logger.error(f"Failed to store result: {e}")
            
    # Helper methods
    
    async def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding using Lambda Labs GPU or fallback"""
        # Simplified - in reality would call Lambda Labs inference service
        # or use local embedding model
        import hashlib
        import numpy as np
        
        # Mock embedding generation
        hash_object = hashlib.md5(text.encode())
        hash_hex = hash_object.hexdigest()
        
        # Convert to vector (simplified)
        embedding = []
        for i in range(0, len(hash_hex), 2):
            value = int(hash_hex[i:i+2], 16) / 255.0
            embedding.append(value)
            
        # Pad to 768 dimensions
        while len(embedding) < 768:
            embedding.extend(embedding[:min(768 - len(embedding), len(embedding))])
            
        return embedding[:768]
        
    def _build_task_prompt(
        self,
        request: CodingRequest,
        context: Dict[str, Any],
        analysis: Dict[str, Any]
    ) -> str:
        """Build comprehensive prompt for the task"""
        
        prompt_parts = [
            f"Task: {request.task.value}",
            f"Description: {request.description}",
            ""
        ]
        
        if context.get("related_code"):
            prompt_parts.extend([
                "Related Code Examples:",
                "```",
                "\n---\n".join(context["related_code"][:2]),
                "```",
                ""
            ])
            
        if context.get("patterns"):
            prompt_parts.extend([
                "Relevant Patterns:",
                "\n".join(f"- {p}" for p in context["patterns"]),
                ""
            ])
            
        if request.requirements:
            prompt_parts.extend([
                "Requirements:",
                json.dumps(request.requirements, indent=2),
                ""
            ])
            
        if analysis.get("constraints"):
            prompt_parts.extend([
                "Quality Constraints:",
                "\n".join(f"- {c}" for c in analysis["constraints"][:5]),
                ""
            ])
            
        # Task-specific instructions
        task_instructions = {
            CodingTask.GENERATE: "Generate clean, well-documented code that follows best practices.",
            CodingTask.REFACTOR: "Refactor the code to improve quality, readability, and performance.",
            CodingTask.DEBUG: "Identify and fix the issues in the code. Explain the problems and solutions.",
            CodingTask.REVIEW: "Review the code and provide detailed feedback on quality, security, and improvements.",
            CodingTask.DOCUMENT: "Add comprehensive documentation including docstrings, comments, and usage examples.",
            CodingTask.TEST: "Write comprehensive tests including unit tests and edge cases.",
            CodingTask.DEPLOY: "Prepare the code for deployment with proper configuration and error handling."
        }
        
        prompt_parts.extend([
            "Instructions:",
            task_instructions.get(request.task, "Complete the requested task."),
            "",
            "Provide the result in a clear format with code blocks where appropriate."
        ])
        
        return "\n".join(prompt_parts)
        
    def _map_coding_task_to_task_type(self, coding_task: CodingTask) -> TaskType:
        """Map coding task to general task type"""
        mapping = {
            CodingTask.GENERATE: TaskType.CODE_GENERATION,
            CodingTask.REFACTOR: TaskType.CODE_MODIFICATION,
            CodingTask.DEBUG: TaskType.DEBUGGING,
            CodingTask.REVIEW: TaskType.ANALYSIS,
            CodingTask.DOCUMENT: TaskType.DOCUMENTATION,
            CodingTask.TEST: TaskType.CODE_GENERATION,
            CodingTask.DEPLOY: TaskType.DEPLOYMENT
        }
        return mapping.get(coding_task, TaskType.GENERAL)
        
    def _map_complexity(self, complexity: str) -> TaskComplexity:
        """Map string complexity to enum"""
        mapping = {
            "simple": TaskComplexity.SIMPLE,
            "moderate": TaskComplexity.MODERATE,
            "complex": TaskComplexity.COMPLEX,
            "architecture": TaskComplexity.ARCHITECTURE
        }
        return mapping.get(complexity, TaskComplexity.MODERATE)
        
    def _parse_llm_response(self, response_text: str) -> CodingResponse:
        """Parse LLM response into structured format"""
        
        # Extract code blocks
        import re
        code_pattern = r"```(?:\w+)?\n(.*?)```"
        code_matches = re.findall(code_pattern, response_text, re.DOTALL)
        
        code = "\n\n".join(code_matches) if code_matches else None
        
        # Extract other sections (simplified)
        response = CodingResponse(
            success=bool(code),
            code=code,
            analysis={
                "explanation": response_text.split("```")[0].strip() if "```" in response_text else response_text
            }
        )
        
        # Look for specific sections
        if "ERROR:" in response_text or "Error:" in response_text:
            response.errors = [line.strip() for line in response_text.split("\n") if "error" in line.lower()]
            
        if "SUGGESTION:" in response_text or "Suggestion:" in response_text:
            response.suggestions = [line.strip() for line in response_text.split("\n") if "suggestion" in line.lower()]
            
        return response
        
    def _extract_code_from_response(self, response_text: str) -> str:
        """Extract clean code from response"""
        import re
        code_pattern = r"```(?:\w+)?\n(.*?)```"
        matches = re.findall(code_pattern, response_text, re.DOTALL)
        return "\n\n".join(matches) if matches else response_text


# Singleton instance
_orchestrator_instance: Optional[CodingMCPOrchestrator] = None

async def get_coding_orchestrator() -> CodingMCPOrchestrator:
    """Get or create singleton instance of coding orchestrator"""
    global _orchestrator_instance
    
    if _orchestrator_instance is None:
        _orchestrator_instance = CodingMCPOrchestrator()
        await _orchestrator_instance.initialize()
        
    return _orchestrator_instance
```

---

## 🧪 COMPREHENSIVE TESTING STRATEGY

### **Unit Tests**

#### **Test Unified Memory Service**

```python
# tests/test_unified_memory_service.py
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timezone

from backend.services.sophia_unified_memory_service import (
    SophiaUnifiedMemoryService,
    MemoryCollection,
    MemoryEntry,
    get_unified_memory_service
)

@pytest.fixture
async def memory_service():
    """Create memory service instance for testing"""
    service = SophiaUnifiedMemoryService()
    
    # Mock dependencies
    service.qdrant_pool = AsyncMock()
    service.redis_manager = AsyncMock()
    service.mem0_client = Mock()
    
    service.initialized = True
    return service

@pytest.mark.asyncio
async def test_store_entry(memory_service):
    """Test storing an entry in memory"""
    # Prepare test data
    content = "Test code snippet"
    vector = [0.1] * 768
    metadata = {"language": "python", "project": "test"}
    
    # Mock Qdrant client
    mock_client = AsyncMock()
    memory_service.qdrant_pool.get_connection.return_value.__aenter__.return_value = mock_client
    
    # Execute
    entry = await memory_service.store(
        content=content,
        vector=vector,
        metadata=metadata,
        collection=MemoryCollection.CODE
    )
    
    # Assert
    assert entry.content == content
    assert entry.collection == MemoryCollection.CODE
    assert "timestamp" in entry.metadata
    assert mock_client.upsert.called
    
@pytest.mark.asyncio
async def test_search_with_cache_hit(memory_service):
    """Test search with Redis cache hit"""
    # Setup cache hit
    cached_data = [{
        "id": "test123",
        "content": "Cached result",
        "metadata": {"cached": True},
        "collection": "sophia_code",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "score": 0.95
    }]
    
    memory_service.redis_manager.get_async.return_value = json.dumps(cached_data)
    
    # Execute search
    results = await memory_service.search(
        query_vector=[0.1] * 768,
        collection=MemoryCollection.CODE,
        limit=10
    )
    
    # Assert cache was used
    assert len(results) == 1
    assert results[0].content == "Cached result"
    assert memory_service.redis_manager.get_async.called
    assert not memory_service.qdrant_pool.get_connection.called

@pytest.mark.asyncio
async def test_circuit_breaker_opens_after_failures(memory_service):
    """Test circuit breaker opens after 3 failures"""
    # Simulate Qdrant failures
    memory_service.qdrant_pool.get_connection.side_effect = Exception("Connection failed")
    
    # Attempt 3 stores
    for i in range(3):
        with pytest.raises(Exception):
            await memory_service.store(
                content=f"Test {i}",
                vector=[0.1] * 768,
                metadata={},
                collection=MemoryCollection.CODE
            )
    
    # Check circuit breaker
    assert memory_service._circuit_breaker["qdrant"]["failures"] == 3
    assert memory_service._circuit_breaker["qdrant"]["is_open"] == True
    
@pytest.mark.asyncio
async def test_health_check(memory_service):
    """Test comprehensive health check"""
    # Mock health responses
    memory_service.qdrant_pool.health_check.return_value = {
        "healthy": True,
        "pool_size": 10,
        "in_use": 2
    }
    memory_service.redis_manager.health_check.return_value = True
    
    # Execute health check
    status = await memory_service.get_health_status()
    
    # Assert
    assert status["healthy"] == True
    assert status["components"]["qdrant"]["healthy"] == True
    assert status["components"]["redis"]["healthy"] == True
    assert "mem0" in status["components"]

@pytest.mark.asyncio
async def test_singleton_pattern():
    """Test singleton pattern works correctly"""
    with patch('backend.services.sophia_unified_memory_service.SophiaUnifiedMemoryService') as MockService:
        mock_instance = AsyncMock()
        MockService.return_value = mock_instance
        
        # Get instance multiple times
        instance1 = await get_unified_memory_service()
        instance2 = await get_unified_memory_service()
        
        # Should be same instance
        assert instance1 is instance2
        # Should only initialize once
        assert MockService.call_count == 1
```

#### **Test Configuration Fix**

```python
# tests/test_auto_esc_config_fixed.py
import pytest
from unittest.mock import patch, MagicMock
import os
import json

from backend.core.auto_esc_config_fixed import get_config_value, _load_esc_environment

def test_get_config_value_from_env():
    """Test getting config value from environment variable"""
    with patch.dict(os.environ, {"TEST_KEY": "test_value"}):
        value = get_config_value("TEST_KEY")
        assert value == "test_value"

def test_get_config_value_prevents_recursion():
    """Test recursion prevention"""
    # This should not cause stack overflow
    with patch('backend.core.auto_esc_config_fixed._load_esc_environment') as mock_load:
        mock_load.side_effect = lambda: get_config_value("RECURSIVE_KEY")
        
        # Should return None instead of recursing infinitely
        value = get_config_value("TEST_KEY")
        assert value is None

@patch('subprocess.run')
def test_load_esc_environment_success(mock_run):
    """Test successful ESC environment loading"""
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = json.dumps({"KEY1": "value1", "KEY2": "value2"})
    mock_run.return_value = mock_result
    
    result = _load_esc_environment()
    
    assert result == {"KEY1": "value1", "KEY2": "value2"}
    mock_run.assert_called_once()

def test_config_caching():
    """Test configuration values are cached"""
    with patch.dict(os.environ, {"CACHED_KEY": "cached_value"}):
        # First call
        value1 = get_config_value("CACHED_KEY")
        
        # Remove from environment
        del os.environ["CACHED_KEY"]
        
        # Should still get cached value
        value2 = get_config_value("CACHED_KEY")
        
        assert value1 == value2 == "cached_value"
```

### **Integration Tests**

#### **Test MCP Orchestration**

```python
# tests/integration/test_coding_mcp_orchestration.py
import pytest
import asyncio
from unittest.mock import AsyncMock, Mock

from backend.services.coding_mcp_orchestrator import (
    CodingMCPOrchestrator,
    CodingRequest,
    CodingTask,
    get_coding_orchestrator
)

@pytest.fixture
async def orchestrator():
    """Create orchestrator with mocked dependencies"""
    orch = CodingMCPOrchestrator()
    
    # Mock memory service
    orch.memory_service = AsyncMock()
    orch.memory_service.search.return_value = []
    orch.memory_service.store.return_value = Mock()
    
    # Mock Portkey gateway
    orch.portkey_gateway = AsyncMock()
    
    # Mock MCP clients
    for name in orch.mcp_clients:
        orch.mcp_clients[name] = AsyncMock()
        orch.mcp_clients[name].connect.return_value = None
        orch.mcp_clients[name].call_tool.return_value = {}
    
    return orch

@pytest.mark.asyncio
async def test_code_generation_workflow(orchestrator):
    """Test complete code generation workflow"""
    # Prepare request
    request = CodingRequest(
        task=CodingTask.GENERATE,
        description="Create a FastAPI endpoint for user authentication",
        context={"project": "test-api", "language": "python"},
        requirements={
            "auth_type": "JWT",
            "database": "PostgreSQL"
        }
    )
    
    # Mock LLM response
    async def mock_llm_response(*args, **kwargs):
        yield """Here's the authentication endpoint:

```python
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
import jwt

router = APIRouter()

@router.post("/auth/login")
async def login(username: str, password: str):
    # Authentication logic here
    user = await authenticate_user(username, password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_jwt_token(user.id)
    return {"access_token": token, "token_type": "bearer"}
```

This implements JWT authentication with FastAPI."""
    
    orchestrator.portkey_gateway.route_and_complete = mock_llm_response
    
    # Mock Codacy response
    orchestrator.mcp_clients["codacy"].call_tool.return_value = {
        "score": 9.2,
        "issues": []
    }
    
    # Execute
    response = await orchestrator.process_request(request)
    
    # Assert
    assert response.success == True
    assert "fastapi" in response.code.lower()
    assert "jwt" in response.code.lower()
    assert response.analysis is not None
    
    # Verify memory storage was called
    assert orchestrator.memory_service.store.called

@pytest.mark.asyncio
async def test_refactoring_with_quality_improvement(orchestrator):
    """Test refactoring with Codacy quality improvement"""
    request = CodingRequest(
        task=CodingTask.REFACTOR,
        description="Refactor this function to improve quality",
        context={"language": "python"},
        files=["messy_code.py"]
    )
    
    # Mock initial code analysis - low quality
    orchestrator.mcp_clients["codacy"].call_tool.side_effect = [
        {"score": 6.5, "issues": ["Complex function", "No error handling"]},
        {"score": 8.7, "issues": []}  # After improvement
    ]
    
    # Mock LLM responses
    response_count = 0
    async def mock_llm_responses(*args, **kwargs):
        nonlocal response_count
        response_count += 1
        
        if response_count == 1:
            # Complexity analysis
            yield "moderate complexity due to nested conditions"
        elif response_count == 2:
            # Initial refactoring
            yield """```python
def process_data(data):
    result = []
    for item in data:
        if item > 0:
            result.append(item * 2)
    return result
```"""
        else:
            # Improved version
            yield """```python
def process_data(data: List[float]) -> List[float]:
    \"\"\"Process data by doubling positive values.
    
    Args:
        data: List of numeric values
        
    Returns:
        List of processed values
        
    Raises:
        ValueError: If data is None or empty
    \"\"\"
    if not data:
        raise ValueError("Data cannot be None or empty")
        
    try:
        return [item * 2 for item in data if item > 0]
    except Exception as e:
        logger.error(f"Error processing data: {e}")
        raise
```"""
    
    orchestrator.portkey_gateway.route_and_complete = mock_llm_responses
    
    # Execute
    response = await orchestrator.process_request(request)
    
    # Assert improvements were made
    assert response.success == True
    assert "raise ValueError" in response.code  # Has error handling
    assert "\"\"\"" in response.code  # Has docstring
    assert response.analysis["score"] == 8.7  # Improved score

@pytest.mark.asyncio
async
