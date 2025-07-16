# 🚀 CODING MCP ARCHITECTURE - DEEP IMPLEMENTATION GUIDE (PART 3)
**Complete Testing, Deployment, Monitoring, and Usage Guide**

---

## 🧪 END-TO-END TESTING STRATEGY

### **Complete E2E Test Suite**

```python
# tests/e2e/test_complete_coding_workflow.py
import pytest
import asyncio
import os
from typing import Dict, Any

from backend.services.sophia_unified_memory_service import get_unified_memory_service
from backend.services.coding_mcp_orchestrator import get_coding_orchestrator, CodingRequest, CodingTask
from backend.services.portkey_gateway import PortkeyGateway

class TestCodingWorkflowE2E:
    """End-to-end tests for the complete coding workflow"""
    
    @pytest.fixture(autouse=True)
    async def setup(self):
        """Setup test environment"""
        # Set test environment
        os.environ["ENVIRONMENT"] = "test"
        os.environ["PULUMI_ORG"] = "test-org"
        
        # Initialize services
        self.memory_service = await get_unified_memory_service()
        self.orchestrator = await get_coding_orchestrator()
        
        yield
        
        # Cleanup
        await self.memory_service.cleanup()
        
    @pytest.mark.asyncio
    async def test_complete_feature_development_workflow(self):
        """Test complete feature development from request to deployment"""
        
        # Step 1: Generate initial code
        generate_request = CodingRequest(
            task=CodingTask.GENERATE,
            description="Create a user profile API with CRUD operations",
            context={
                "project": "test-api",
                "language": "python",
                "framework": "fastapi"
            },
            requirements={
                "database": "PostgreSQL",
                "authentication": "JWT",
                "validation": "Pydantic"
            }
        )
        
        generate_response = await self.orchestrator.process_request(generate_request)
        assert generate_response.success
        assert "class UserProfile" in generate_response.code
        assert "router" in generate_response.code
        
        # Step 2: Add tests
        test_request = CodingRequest(
            task=CodingTask.TEST,
            description="Write comprehensive tests for the user profile API",
            context={
                "project": "test-api",
                "code": generate_response.code
            }
        )
        
        test_response = await self.orchestrator.process_request(test_request)
        assert test_response.success
        assert "test_" in test_response.code
        assert "pytest" in test_response.code
        
        # Step 3: Code review
        review_request = CodingRequest(
            task=CodingTask.REVIEW,
            description="Review the user profile API for security and performance",
            context={
                "code": generate_response.code,
                "tests": test_response.code
            }
        )
        
        review_response = await self.orchestrator.process_request(review_request)
        assert review_response.success
        assert review_response.analysis is not None
        
        # Step 4: Refactor based on review
        if review_response.suggestions:
            refactor_request = CodingRequest(
                task=CodingTask.REFACTOR,
                description="Improve code based on review suggestions",
                context={
                    "code": generate_response.code,
                    "suggestions": review_response.suggestions
                }
            )
            
            refactor_response = await self.orchestrator.process_request(refactor_request)
            assert refactor_response.success
            
        # Step 5: Verify memory persistence
        embedding = await self.orchestrator._generate_embedding("user profile API CRUD")
        search_results = await self.memory_service.search(
            query_vector=embedding,
            collection=MemoryCollection.CODE,
            limit=5
        )
        
        assert len(search_results) > 0
        assert any("UserProfile" in result.content for result in search_results)
        
    @pytest.mark.asyncio
    async def test_debugging_workflow_with_context(self):
        """Test debugging workflow with historical context"""
        
        # Simulate a bug report
        debug_request = CodingRequest(
            task=CodingTask.DEBUG,
            description="Fix authentication error: JWT token validation failing",
            context={
                "error": "InvalidTokenError: Token signature verification failed",
                "code": """
                def verify_token(token: str) -> dict:
                    try:
                        payload = jwt.decode(token, SECRET_KEY, algorithm="HS256")
                        return payload
                    except jwt.InvalidTokenError:
                        raise HTTPException(status_code=401, detail="Invalid token")
                """
            }
        )
        
        debug_response = await self.orchestrator.process_request(debug_request)
        
        assert debug_response.success
        assert "verify=True" in debug_response.code or "options=" in debug_response.code
        assert debug_response.analysis.get("explanation") is not None
        
    @pytest.mark.asyncio
    async def test_multi_file_refactoring(self):
        """Test refactoring across multiple files"""
        
        files = {
            "models.py": "class User: pass",
            "api.py": "def get_user(): pass",
            "utils.py": "def validate_user(): pass"
        }
        
        refactor_request = CodingRequest(
            task=CodingTask.REFACTOR,
            description="Add type hints and documentation to all files",
            context={"files": files},
            files=list(files.keys())
        )
        
        response = await self.orchestrator.process_request(refactor_request)
        
        assert response.success
        assert "-> " in response.code  # Type hints
        assert '"""' in response.code  # Docstrings

# Performance Tests
class TestPerformance:
    """Performance and stress tests"""
    
    @pytest.mark.asyncio
    async def test_concurrent_requests(self):
        """Test handling multiple concurrent coding requests"""
        
        requests = [
            CodingRequest(
                task=CodingTask.GENERATE,
                description=f"Create function {i}",
                context={"index": i}
            )
            for i in range(10)
        ]
        
        # Process concurrently
        start_time = asyncio.get_event_loop().time()
        responses = await asyncio.gather(*[
            self.orchestrator.process_request(req) for req in requests
        ])
        elapsed = asyncio.get_event_loop().time() - start_time
        
        # All should succeed
        assert all(r.success for r in responses)
        
        # Should complete in reasonable time (less than sequential)
        assert elapsed < len(requests) * 2  # 2 seconds per request max
        
    @pytest.mark.asyncio
    async def test_memory_performance(self):
        """Test memory search performance with large dataset"""
        
        # Generate and store 1000 code snippets
        for i in range(1000):
            embedding = [float(i % 768) / 768] * 768
            await self.memory_service.store(
                content=f"Code snippet {i}",
                vector=embedding,
                metadata={"index": i},
                collection=MemoryCollection.CODE
            )
            
        # Search performance test
        start_time = asyncio.get_event_loop().time()
        results = await self.memory_service.search(
            query_vector=[0.5] * 768,
            collection=MemoryCollection.CODE,
            limit=100
        )
        search_time = asyncio.get_event_loop().time() - start_time
        
        assert len(results) <= 100
        assert search_time < 0.5  # Should complete in under 500ms
```

### **Integration Test Harness**

```python
# tests/integration/test_harness.py
"""
Comprehensive test harness for integration testing
"""

import asyncio
import json
from typing import Dict, Any, List
import docker
import pytest
from testcontainers.compose import DockerCompose

class IntegrationTestHarness:
    """Test harness for integration testing with real services"""
    
    def __init__(self):
        self.compose = DockerCompose(
            "tests/integration/docker-compose.test.yml",
            pull=True
        )
        self.services_healthy = False
        
    async def setup(self):
        """Start all required services"""
        # Start services
        with self.compose:
            # Wait for services to be healthy
            await self._wait_for_services()
            self.services_healthy = True
            
    async def _wait_for_services(self):
        """Wait for all services to be healthy"""
        services = {
            "qdrant": {"port": 6333, "endpoint": "/healthz"},
            "redis": {"port": 6379, "command": "redis-cli ping"},
            "postgres": {"port": 5432, "command": "pg_isready"},
            "mcp-servers": {"ports": [9000, 3008, 9001, 9020]}
        }
        
        max_retries = 30
        for service, config in services.items():
            for retry in range(max_retries):
                if await self._check_service_health(service, config):
                    break
                await asyncio.sleep(2)
            else:
                raise Exception(f"Service {service} failed to start")
                
    async def _check_service_health(self, service: str, config: Dict) -> bool:
        """Check if a service is healthy"""
        try:
            if "endpoint" in config:
                # HTTP health check
                import aiohttp
                async with aiohttp.ClientSession() as session:
                    url = f"http://localhost:{config['port']}{config['endpoint']}"
                    async with session.get(url) as response:
                        return response.status == 200
            elif "command" in config:
                # Command health check
                import subprocess
                result = subprocess.run(
                    config["command"].split(),
                    capture_output=True
                )
                return result.returncode == 0
            elif "ports" in config:
                # Check multiple ports
                import socket
                for port in config["ports"]:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    result = sock.connect_ex(("localhost", port))
                    sock.close()
                    if result != 0:
                        return False
                return True
        except Exception:
            return False
            
    async def cleanup(self):
        """Clean up test environment"""
        if self.services_healthy:
            # Clear test data
            await self._clear_test_data()
            
    async def _clear_test_data(self):
        """Clear all test data from services"""
        # Clear Qdrant collections
        from qdrant_client import QdrantClient
        client = QdrantClient(host="localhost", port=6333)
        collections = await client.get_collections()
        for collection in collections.collections:
            if collection.name.startswith("test_"):
                await client.delete_collection(collection.name)
                
        # Clear Redis
        import redis
        r = redis.Redis(host="localhost", port=6379)
        r.flushdb()

# Docker Compose for testing
"""
# tests/integration/docker-compose.test.yml
version: '3.8'

services:
  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
    volumes:
      - ./qdrant_test_data:/qdrant/storage
    environment:
      - QDRANT__SERVICE__HTTP_PORT=6333
      
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    command: redis-server --appendonly yes
    
  postgres:
    image: postgres:15-alpine
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_USER=test
      - POSTGRES_PASSWORD=test
      - POSTGRES_DB=sophia_test
      
  mcp-ai-memory:
    build:
      context: ../../mcp-servers/ai-memory
    ports:
      - "9000:9000"
    environment:
      - QDRANT_HOST=qdrant
      - QDRANT_PORT=6333
      
  mcp-codacy:
    build:
      context: ../../mcp-servers/codacy
    ports:
      - "3008:3008"
    environment:
      - CODACY_API_TOKEN=test_token
"""
```

---

## 🚀 DEPLOYMENT STRATEGY

### **Production Deployment Pipeline**

```yaml
# .github/workflows/deploy-coding-architecture.yml
name: Deploy Coding Architecture

on:
  push:
    branches: [main]
    paths:
      - 'backend/services/sophia_unified_memory_service.py'
      - 'backend/services/coding_mcp_orchestrator.py'
      - 'backend/core/auto_esc_config_fixed.py'
      - 'mcp-servers/**'
      - 'k8s/coding-services/**'

env:
  REGISTRY: docker.io
  DOCKER_HUB_USERNAME: scoobyjava15

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          
      - name: Install dependencies
        run: |
          pip install uv
          uv sync
          
      - name: Run unit tests
        run: |
          uv run pytest tests/unit -v --cov=backend/services --cov-report=xml
          
      - name: Run integration tests
        run: |
          docker-compose -f tests/integration/docker-compose.test.yml up -d
          uv run pytest tests/integration -v
          docker-compose -f tests/integration/docker-compose.test.yml down
          
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml

  build-and-push:
    needs: test
    runs-on: ubuntu-latest
    strategy:
      matrix:
        service:
          - name: unified-memory
            context: backend
            dockerfile: Dockerfile.memory
          - name: coding-orchestrator
            context: backend
            dockerfile: Dockerfile.orchestrator
          - name: mcp-ai-memory
            context: mcp-servers/ai-memory
          - name: mcp-codacy
            context: mcp-servers/codacy
            
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3
        
      - name: Log in to Docker Hub
        uses: docker/login-action@v3
        with:
          username: ${{ env.DOCKER_HUB_USERNAME }}
          password: ${{ secrets.DOCKER_HUB_ACCESS_TOKEN }}
          
      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: ${{ matrix.service.context }}
          file: ${{ matrix.service.context }}/${{ matrix.service.dockerfile || 'Dockerfile' }}
          push: true
          tags: |
            ${{ env.DOCKER_HUB_USERNAME }}/sophia-${{ matrix.service.name }}:latest
            ${{ env.DOCKER_HUB_USERNAME }}/sophia-${{ matrix.service.name }}:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  deploy-to-k8s:
    needs: build-and-push
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Install kubectl
        uses: azure/setup-kubectl@v3
        
      - name: Configure kubectl
        run: |
          mkdir -p ~/.kube
          echo "${{ secrets.KUBECONFIG }}" | base64 -d > ~/.kube/config
          
      - name: Update image tags
        run: |
          cd k8s/coding-services
          find . -name "*.yaml" -exec sed -i "s|:latest|:${{ github.sha }}|g" {} \;
          
      - name: Deploy to production
        run: |
          kubectl apply -k k8s/coding-services/overlays/production
          
      - name: Wait for rollout
        run: |
          kubectl rollout status deployment/unified-memory -n sophia-ai-prod
          kubectl rollout status deployment/coding-orchestrator -n sophia-ai-prod
          kubectl rollout status deployment/mcp-ai-memory -n mcp-servers
          kubectl rollout status deployment/mcp-codacy -n mcp-servers
          
      - name: Run smoke tests
        run: |
          kubectl run smoke-test --image=curlimages/curl:latest --rm -it --restart=Never -- \
            curl -f http://unified-memory-service.sophia-ai-prod:8000/health
```

### **Kubernetes Manifests**

```yaml
# k8s/coding-services/base/unified-memory-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: unified-memory
  labels:
    app: unified-memory
    component: memory
    tier: backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: unified-memory
  template:
    metadata:
      labels:
        app: unified-memory
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "8000"
        prometheus.io/path: "/metrics"
    spec:
      containers:
      - name: unified-memory
        image: scoobyjava15/sophia-unified-memory:latest
        ports:
        - containerPort: 8000
          name: http
        - containerPort: 9090
          name: metrics
        env:
        - name: ENVIRONMENT
          value: "prod"
        - name: PULUMI_ORG
          value: "scoobyjava-org"
        - name: QDRANT_URL
          valueFrom:
            secretKeyRef:
              name: qdrant-secrets
              key: url
        - name: QDRANT_API_KEY
          valueFrom:
            secretKeyRef:
              name: qdrant-secrets
              key: api-key
        - name: REDIS_HOST
          value: "redis-service"
        - name: REDIS_PASSWORD
          valueFrom:
            secretKeyRef:
              name: redis-secrets
              key: password
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
        volumeMounts:
        - name: cache
          mountPath: /app/cache
      volumes:
      - name: cache
        emptyDir:
          sizeLimit: 1Gi
---
apiVersion: v1
kind: Service
metadata:
  name: unified-memory-service
spec:
  selector:
    app: unified-memory
  ports:
  - port: 8000
    targetPort: 8000
    name: http
  type: ClusterIP
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: unified-memory-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: unified-memory
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  - type: Pods
    pods:
      metric:
        name: memory_operations_per_second
      target:
        type: AverageValue
        averageValue: "100"
```

### **Production Monitoring**

```yaml
# k8s/coding-services/monitoring/prometheus-rules.yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: coding-architecture-alerts
  labels:
    prometheus: kube-prometheus
spec:
  groups:
  - name: memory_service_alerts
    interval: 30s
    rules:
    - alert: HighMemoryLatency
      expr: |
        histogram_quantile(0.95, 
          rate(memory_operation_latency_seconds_bucket[5m])
        ) > 0.5
      for: 5m
      labels:
        severity: warning
        component: memory
      annotations:
        summary: High memory operation latency
        description: "95th percentile latency is {{ $value }}s"
        
    - alert: CircuitBreakerOpen
      expr: |
        sum by (service) (
          sophia_circuit_breaker_status{state="open"}
        ) > 0
      for: 2m
      labels:
        severity: critical
        component: memory
      annotations:
        summary: Circuit breaker open for {{ $labels.service }}
        description: "Service {{ $labels.service }} circuit breaker is open"
        
    - alert: LowCacheHitRate
      expr: |
        rate(cache_hits_total[5m]) / 
        (rate(cache_hits_total[5m]) + rate(cache_misses_total[5m])) < 0.8
      for: 10m
      labels:
        severity: warning
        component: cache
      annotations:
        summary: Low cache hit rate
        description: "Cache hit rate is {{ $value | humanizePercentage }}"
        
  - name: orchestrator_alerts
    interval: 30s
    rules:
    - alert: HighCodingRequestFailureRate
      expr: |
        rate(coding_requests_total{status="error"}[5m]) / 
        rate(coding_requests_total[5m]) > 0.1
      for: 5m
      labels:
        severity: critical
        component: orchestrator
      annotations:
        summary: High coding request failure rate
        description: "Failure rate is {{ $value | humanizePercentage }}"
        
    - alert: SlowCodeGeneration
      expr: |
        histogram_quantile(0.95,
          rate(code_generation_duration_seconds_bucket[5m])
        ) > 30
      for: 5m
      labels:
        severity: warning
        component: orchestrator
      annotations:
        summary: Slow code generation
        description: "95th percentile generation time is {{ $value }}s"
```

---

## 💻 USAGE EXAMPLES

### **Natural Language Interface**

```python
# backend/api/coding_assistant.py
"""
Natural language interface for coding assistance
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from backend.services.coding_mcp_orchestrator import (
    get_coding_orchestrator,
    CodingRequest,
    CodingTask
)

router = APIRouter(prefix="/api/coding", tags=["coding"])

class NaturalLanguageRequest(BaseModel):
    """Natural language coding request"""
    message: str
    context: Optional[Dict[str, Any]] = None
    files: Optional[List[str]] = None

class CodingAssistantResponse(BaseModel):
    """Response from coding assistant"""
    success: bool
    code: Optional[str] = None
    explanation: Optional[str] = None
    suggestions: Optional[List[str]] = None
    artifacts: Optional[Dict[str, Any]] = None

@router.post("/assist", response_model=CodingAssistantResponse)
async def natural_language_coding(request: NaturalLanguageRequest):
    """
    Process natural language coding requests
    
    Examples:
    - "Create a REST API for user management"
    - "Fix the authentication bug in login.py"
    - "Refactor this function to improve performance"
    - "Add comprehensive tests for the payment module"
    """
    
    # Parse natural language to determine task
    task_mapping = {
        "create": CodingTask.GENERATE,
        "generate": CodingTask.GENERATE,
        "write": CodingTask.GENERATE,
        "fix": CodingTask.DEBUG,
        "debug": CodingTask.DEBUG,
        "solve": CodingTask.DEBUG,
        "refactor": CodingTask.REFACTOR,
        "improve": CodingTask.REFACTOR,
        "optimize": CodingTask.REFACTOR,
        "review": CodingTask.REVIEW,
        "analyze": CodingTask.REVIEW,
        "document": CodingTask.DOCUMENT,
        "test": CodingTask.TEST,
        "deploy": CodingTask.DEPLOY
    }
    
    # Simple task detection (in production, use NLP)
    message_lower = request.message.lower()
    detected_task = CodingTask.GENERATE  # default
    
    for keyword, task in task_mapping.items():
        if keyword in message_lower:
            detected_task = task
            break
            
    # Create coding request
    coding_request = CodingRequest(
        task=detected_task,
        description=request.message,
        context=request.context,
        files=request.files
    )
    
    # Process through orchestrator
    orchestrator = await get_coding_orchestrator()
    response = await orchestrator.process_request(coding_request)
    
    if not response.success:
        raise HTTPException(
            status_code=500,
            detail=f"Coding request failed: {response.errors}"
        )
        
    return CodingAssistantResponse(
        success=response.success,
        code=response.code,
        explanation=response.analysis.get("explanation") if response.analysis else None,
        suggestions=response.suggestions,
        artifacts=response.artifacts
    )

# WebSocket for streaming responses
from fastapi import WebSocket
import json

@router.websocket("/assist/stream")
async def coding_assistant_stream(websocket: WebSocket):
    """
    WebSocket endpoint for streaming coding responses
    """
    await websocket.accept()
    
    try:
        while True:
            # Receive request
            data = await websocket.receive_text()
            request_data = json.loads(data)
            
            # Create request
            request = NaturalLanguageRequest(**request_data)
            coding_request = CodingRequest(
                task=_detect_task(request.message),
                description=request.message,
                context=request.context,
                files=request.files
            )
            
            # Stream response
            orchestrator = await get_coding_orchestrator()
            
            # Send chunks as they're generated
            async for chunk in orchestrator.process_request_stream(coding_request):
                await websocket.send_json({
                    "type": "chunk",
                    "content": chunk
                })
                
            # Send completion
            await websocket.send_json({
                "type": "complete",
                "status": "success"
            })
            
    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "message": str(e)
        })
    finally:
        await websocket.close()
```

### **CLI Interface**

```bash
#!/bin/bash
# scripts/sophia-code.sh
"""
Sophia AI Coding Assistant CLI
"""

# Function to call the API
sophia_code() {
    local command=$1
    shift
    local message="$@"
    
    case $command in
        "generate"|"create")
            curl -X POST http://localhost:8000/api/coding/assist \
                -H "Content-Type: application/json" \
                -d "{\"message\": \"Create $message\"}" | jq -r '.code'
            ;;
            
        "fix"|"debug")
            curl -X POST http://localhost:8000/api/coding/assist \
                -H "Content-Type: application/json" \
                -d "{\"message\": \"Fix $message\"}" | jq -r '.code'
            ;;
            
        "refactor")
            curl -X POST http://localhost:8000/api/coding/assist \
                -H "Content-Type: application/json" \
                -d "{\"message\": \"Refactor $message\"}" | jq -r '.code'
            ;;
            
        "test")
            curl -X POST http://localhost:8000/api/coding/assist \
                -H "Content-Type: application/json" \
                -d "{\"message\": \"Write tests for $message\"}" | jq -r '.code'
            ;;
            
        *)
            echo "Usage: sophia-code [generate|fix|refactor|test] <description>"
            ;;
    esac
}

# Examples:
# sophia-code generate "a FastAPI endpoint for user authentication"
# sophia-code fix "the JWT validation error in auth.py"
# sophia-code refactor "the database query in user_service.py for better performance"
# sophia-code test "the payment processing module"
```

### **Cursor AI Integration**

```json
// .cursor/settings.json
{
  "sophia.coding": {
    "enabled": true,
    "endpoint": "http://localhost:8000/api/coding",
    "mcpServers": {
      "ai_memory": {
        "port": 9000,
        "enabled": true
      },
      "codacy": {
        "port": 3008,
        "enabled": true
      }
    },
    "naturalLanguage": {
      "enabled": true,
      "shortcuts": {
        "generate": "Create $1",
        "fix": "Fix $1",
        "refactor": "Refactor $1 for better $2",
        "test": "Write tests for $1"
      }
    },
    "contextPersistence": {
      "enabled": true,
      "ttl": 3600
    }
  }
}
```

### **Usage Examples**

```python
# Example 1: Generate a complete feature
async def example_generate_feature():
    orchestrator = await get_coding_orchestrator()
    
    request = CodingRequest(
        task=CodingTask.GENERATE,
        description="Create a complete user authentication system with email verification",
        context={
            "project": "my-app",
            "framework": "fastapi",
            "database": "postgresql"
        },
        requirements={
            "security": "OAuth2 + JWT",
            "email": "SendGrid integration",
            "testing": "pytest"
        }
    )
    
    response = await orchestrator.process_request(request)
