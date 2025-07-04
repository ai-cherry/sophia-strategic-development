# PHASE 1: FOUNDATION ENHANCEMENT - DETAILED IMPLEMENTATION PLAN

## Overview
**Duration**: 4 weeks
**Focus**: Memory & Learning Layer + Intelligent Orchestration
**Goal**: Enhance Sophia AI with persistent memory, prompt optimization, and advanced orchestration

## Week 1-2: Memory & Learning Layer

### Day 1-2: Mem0 Deployment

#### 1. Create Kubernetes Deployment
```yaml
# infrastructure/kubernetes/mem0/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mem0-persistent-server
  namespace: sophia-memory
spec:
  replicas: 1
  selector:
    matchLabels:
      app: mem0-server
  template:
    metadata:
      labels:
        app: mem0-server
    spec:
      containers:
      - name: mem0
        image: mem0ai/mem0:latest
        ports:
        - containerPort: 8080
        env:
        - name: PINECONE_API_KEY
          valueFrom:
            secretKeyRef:
              name: sophia-secrets
              key: pinecone-api-key
        - name: POSTGRES_URL
          value: "postgresql://mem0:mem0pass@postgres-mem0:5432/mem0db"
        - name: REDIS_URL
          value: "redis://redis-mem0:6379"
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
```

#### 2. Create Integration Service
```python
# backend/services/mem0_integration_service.py
from typing import List, Dict, Any
import mem0
from backend.core.config_manager import get_config_value

class Mem0IntegrationService:
    def __init__(self):
        self.mem0_client = mem0.Client(
            api_key=get_config_value("mem0_api_key"),
            base_url="http://mem0-server:8080"
        )

    async def store_conversation_memory(
        self,
        user_id: str,
        conversation: List[Dict[str, str]],
        metadata: Dict[str, Any]
    ) -> str:
        """Store conversation with learning metadata"""
        memory = await self.mem0_client.add(
            messages=conversation,
            user_id=user_id,
            metadata={
                **metadata,
                "source": "sophia_ai",
                "timestamp": datetime.now().isoformat()
            }
        )
        return memory.id
```

### Day 3-4: Snowflake Schema Enhancement

#### 1. Execute Schema Updates
```sql
-- backend/snowflake_setup/mem0_integration.sql
USE SCHEMA SOPHIA_AI_MEMORY;

-- Enhance memory records with Mem0 integration
ALTER TABLE MEMORY_RECORDS
ADD COLUMN IF NOT EXISTS mem0_memory_id VARCHAR(255),
ADD COLUMN IF NOT EXISTS learning_score FLOAT DEFAULT 0.0,
ADD COLUMN IF NOT EXISTS feedback_count INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS last_reinforced TIMESTAMP_NTZ;

-- Create learning analytics table
CREATE TABLE IF NOT EXISTS MEMORY_LEARNING_ANALYTICS (
    analytics_id VARCHAR(255) PRIMARY KEY,
    memory_id VARCHAR(255) REFERENCES MEMORY_RECORDS(memory_id),
    learning_type VARCHAR(50),
    feedback_score FLOAT,
    learning_outcome TEXT,
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    metadata VARIANT
);

-- Create RLHF feedback table
CREATE TABLE IF NOT EXISTS RLHF_FEEDBACK (
    feedback_id VARCHAR(255) PRIMARY KEY,
    memory_id VARCHAR(255) REFERENCES MEMORY_RECORDS(memory_id),
    user_id VARCHAR(100),
    feedback_type VARCHAR(50), -- 'positive', 'negative', 'correction'
    feedback_text TEXT,
    applied BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);
```

### Day 5-6: AI Memory MCP Enhancement

#### 1. Update AI Memory MCP Server
```python
# mcp-servers/ai_memory/enhanced_mem0_integration.py
class EnhancedAIMemoryWithMem0(StandardizedMCPServer):
    def __init__(self):
        super().__init__("ai_memory_mem0", 9000)
        self.mem0_service = Mem0IntegrationService()

    @mcp_tool(
        name="store_with_learning",
        description="Store memory with learning capabilities"
    )
    async def store_with_learning(
        self,
        content: str,
        category: str,
        user_id: str,
        conversation_context: List[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        # Store in Snowflake
        memory_id = await self.store_memory(content, category)

        # Store in Mem0 for learning
        if conversation_context:
            mem0_id = await self.mem0_service.store_conversation_memory(
                user_id=user_id,
                conversation=conversation_context,
                metadata={"memory_id": memory_id, "category": category}
            )

            # Update Snowflake with Mem0 ID
            await self.update_memory_with_mem0(memory_id, mem0_id)

        return {
            "memory_id": memory_id,
            "mem0_id": mem0_id,
            "learning_enabled": True
        }
```

### Day 7-8: RLHF Feedback Collection

#### 1. Create Feedback API
```python
# backend/api/rlhf_feedback_routes.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/rlhf")

class FeedbackRequest(BaseModel):
    memory_id: str
    user_id: str
    feedback_type: str
    feedback_text: str = None

@router.post("/feedback")
async def submit_feedback(request: FeedbackRequest):
    """Submit RLHF feedback for a memory"""
    feedback_id = await store_rlhf_feedback(
        memory_id=request.memory_id,
        user_id=request.user_id,
        feedback_type=request.feedback_type,
        feedback_text=request.feedback_text
    )

    # Trigger learning update
    await trigger_learning_update(request.memory_id)

    return {"feedback_id": feedback_id, "status": "accepted"}
```

### Day 9-10: Learning Analytics Dashboard

#### 1. Create Analytics Component
```typescript
// frontend/src/components/MemoryLearningAnalytics.tsx
import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip } from 'recharts';

export const MemoryLearningAnalytics: React.FC = () => {
    const [learningData, setLearningData] = useState([]);

    useEffect(() => {
        fetchLearningAnalytics();
    }, []);

    return (
        <div className="learning-analytics">
            <h2>Memory Learning Progress</h2>
            <LineChart width={600} height={300} data={learningData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey="learning_score" stroke="#8884d8" />
                <Line type="monotone" dataKey="feedback_count" stroke="#82ca9d" />
            </LineChart>
        </div>
    );
};
```

## Week 3-4: Intelligent Orchestration

### Day 11-12: Prompt Optimizer MCP Deployment

#### 1. Clone and Configure
```bash
# scripts/deploy_prompt_optimizer.sh
#!/bin/bash

# Clone the prompt optimizer
cd external/
git clone https://github.com/Bubobot-Team/mcp-prompt-optimizer.git

# Create wrapper service
cat > mcp-servers/prompt_optimizer/prompt_optimizer_wrapper.py << 'EOF'
from backend.mcp_servers.base.standardized_mcp_server import StandardizedMCPServer
import sys
sys.path.append('../external/mcp-prompt-optimizer')
from prompt_optimizer import PromptOptimizer

class PromptOptimizerMCPServer(StandardizedMCPServer):
    def __init__(self):
        super().__init__("prompt_optimizer", 9025)
        self.optimizer = PromptOptimizer()

    @mcp_tool(
        name="optimize_prompt",
        description="Optimize prompt using Tree of Thoughts"
    )
    async def optimize_prompt(
        self,
        prompt: str,
        strategy: str = "tree_of_thoughts"
    ) -> str:
        return await self.optimizer.optimize(prompt, strategy)
EOF
```

#### 2. Integrate with SmartAIService
```python
# backend/services/smart_ai_service_enhanced.py
class EnhancedSmartAIService(SmartAIService):
    def __init__(self):
        super().__init__()
        self.prompt_optimizer = PromptOptimizerClient()

    async def generate_response(self, request: LLMRequest) -> LLMResponse:
        # Optimize prompt before sending
        if request.optimize_prompt:
            optimized_prompt = await self.prompt_optimizer.optimize(
                prompt=request.messages[-1]["content"],
                strategy="tree_of_thoughts"
            )
            request.messages[-1]["content"] = optimized_prompt

        # Continue with standard flow
        return await super().generate_response(request)
```

### Day 13-14: LangGraph Advanced Patterns

#### 1. Implement Conditional Edges
```python
# backend/workflows/advanced_langgraph_patterns.py
from langgraph.graph import StateGraph, END

class AdvancedWorkflowOrchestrator:
    def create_conditional_workflow(self):
        workflow = StateGraph(WorkflowState)

        # Add nodes
        workflow.add_node("analyze", self.analyze_node)
        workflow.add_node("human_review", self.human_review_node)
        workflow.add_node("auto_process", self.auto_process_node)
        workflow.add_node("consolidate", self.consolidate_node)

        # Add conditional routing
        workflow.add_conditional_edges(
            "analyze",
            self.needs_human_review,
            {
                True: "human_review",
                False: "auto_process"
            }
        )

        # Add edges
        workflow.add_edge("human_review", "consolidate")
        workflow.add_edge("auto_process", "consolidate")
        workflow.add_edge("consolidate", END)

        return workflow.compile()
```

### Day 15-16: Unified MCP Gateway

#### 1. Create Gateway Service
```python
# backend/services/unified_mcp_gateway.py
class UnifiedMCPGateway:
    def __init__(self):
        self.servers = self._load_server_registry()
        self.router = CapabilityBasedRouter()
        self.health_monitor = HealthMonitor()

    async def route_request(
        self,
        capability: str,
        request: Dict[str, Any]
    ) -> Dict[str, Any]:
        # Find servers with capability
        capable_servers = self.router.find_capable_servers(capability)

        # Select healthy server
        server = await self.health_monitor.select_healthy(capable_servers)

        # Route request
        return await self._forward_to_server(server, request)
```

### Day 17-18: Integration Testing

#### 1. Create Test Suite
```python
# tests/test_phase1_integration.py
import pytest

class TestPhase1Integration:
    @pytest.mark.asyncio
    async def test_mem0_storage_and_recall(self):
        # Test Mem0 integration
        memory_id = await store_with_learning(
            content="Test memory",
            category="test",
            user_id="test_user"
        )

        recalled = await recall_with_context("test query", "test_user")
        assert len(recalled) > 0

    @pytest.mark.asyncio
    async def test_prompt_optimization(self):
        # Test prompt optimizer
        original = "Analyze this data"
        optimized = await optimize_prompt(original)
        assert len(optimized) > len(original)
        assert "step by step" in optimized.lower()
```

### Day 19-20: Documentation and Deployment

#### 1. Update Documentation
```markdown
# docs/PHASE_1_DEPLOYMENT_GUIDE.md

## Phase 1 Deployment Guide

### Prerequisites
- Kubernetes cluster access
- Pulumi ESC configured
- PostgreSQL for Mem0
- Redis for caching

### Deployment Steps

1. Deploy Mem0 Server
```bash
kubectl apply -f infrastructure/kubernetes/mem0/
```

2. Update Snowflake Schema
```bash
python scripts/apply_mem0_schema.py
```

3. Deploy Enhanced MCP Servers
```bash
python scripts/deploy_enhanced_mcp_servers.py
```

4. Verify Integration
```bash
python scripts/verify_phase1_deployment.py
```
```

## Success Criteria

### Technical Metrics
- [ ] Mem0 server operational
- [ ] Cross-session memory recall > 95% accuracy
- [ ] Prompt optimization reducing tokens by > 20%
- [ ] LangGraph workflows with conditional routing
- [ ] Unified gateway routing to all MCP servers

### Business Metrics
- [ ] CEO can ask follow-up questions referencing past conversations
- [ ] LLM responses 50% faster with optimization
- [ ] Automated workflow creation via natural language
- [ ] Real-time learning from user feedback

## Risk Mitigation

### Potential Issues
1. **Mem0 Integration Complexity**
   - Mitigation: Start with simple key-value storage
   - Fallback: Use existing AI Memory MCP

2. **Performance Impact**
   - Mitigation: Async processing for learning
   - Monitoring: Track latency metrics

3. **Schema Migration**
   - Mitigation: Non-breaking changes only
   - Rollback: Prepared rollback scripts

## Next Steps

After successful Phase 1 completion:
1. Begin Phase 2: Data Pipeline Automation
2. Measure performance improvements
3. Collect user feedback
4. Iterate on learning algorithms
