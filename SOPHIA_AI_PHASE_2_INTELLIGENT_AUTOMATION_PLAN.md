# SOPHIA AI PHASE 2: INTELLIGENT AUTOMATION & GOVERNANCE
**Date:** July 10, 2025  
**Status:** Ready for Implementation  
**Dependencies:** Phase 1 Complete ✅

## Executive Summary

Phase 2 transforms Sophia AI from a reactive system to a proactive, self-managing platform through:
- n8n workflow automation for business process orchestration
- Advanced MCP features enabling multi-agent coordination
- UV-powered dependency governance for lightning-fast builds
- High-performance LLM routing via Portkey + OpenRouter
- Intelligent request routing with context awareness

## 🎯 Phase 2 Objectives

1. **Automated Workflow Intelligence** - n8n orchestrates complex business processes
2. **Multi-Agent Coordination** - MCPs work together seamlessly
3. **Zero-Friction Development** - UV eliminates dependency pain
4. **SOTA Model Access** - Always use the best available AI models
5. **Context-Aware Routing** - Requests go to optimal endpoints

## 🏗️ Architecture Enhancements

### 1. n8n Workflow Engine Integration

```typescript
// backend/services/n8n_integration_service.py
class N8NIntegrationService:
    """Bridges Sophia AI with n8n workflow automation"""
    
    def __init__(self):
        self.n8n_url = get_config_value("n8n_webhook_url")
        self.workflows = self._load_workflow_definitions()
        
    async def trigger_workflow(
        self,
        workflow_id: str,
        trigger_data: dict,
        context: dict
    ) -> WorkflowResult:
        """Trigger n8n workflow with context"""
        
        # Enrich with Sophia context
        payload = {
            "workflow_id": workflow_id,
            "trigger_data": trigger_data,
            "sophia_context": {
                "user_id": context.get("user_id"),
                "session_id": context.get("session_id"),
                "capabilities": await self._get_available_capabilities(),
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        
        # Send to n8n
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.n8n_url}/webhook/{workflow_id}",
                json=payload
            )
            
        return WorkflowResult.from_response(response)
    
    async def register_workflow_templates(self):
        """Register Sophia-specific workflow templates"""
        
        templates = [
            {
                "name": "Daily Business Intelligence Report",
                "triggers": ["schedule", "manual", "event"],
                "nodes": ["snowflake_query", "ai_analysis", "slack_notify"]
            },
            {
                "name": "Customer Health Alert",
                "triggers": ["gong_call_sentiment", "hubspot_deal_change"],
                "nodes": ["analyze_signals", "create_task", "notify_team"]
            },
            {
                "name": "Code Quality Gate",
                "triggers": ["github_pr", "manual_review"],
                "nodes": ["codacy_scan", "ai_review", "merge_decision"]
            }
        ]
        
        for template in templates:
            await self._register_template(template)
```

### 2. Advanced MCP Multi-Agent Coordination

```python
# backend/services/mcp_multi_agent_coordinator.py
class MCPMultiAgentCoordinator:
    """Coordinates multiple MCP servers for complex tasks"""
    
    def __init__(self):
        self.mcp_registry = self._load_mcp_registry()
        self.coordination_rules = self._load_coordination_rules()
        
    async def execute_multi_agent_task(
        self,
        task_definition: MultiAgentTask
    ) -> MultiAgentResult:
        """Execute task across multiple MCP servers"""
        
        # 1. Analyze task requirements
        required_capabilities = self._analyze_requirements(task_definition)
        
        # 2. Select optimal agent combination
        agent_plan = self._create_execution_plan(
            required_capabilities,
            self.mcp_registry
        )
        
        # 3. Execute with dependency management
        results = {}
        for step in agent_plan.execution_steps:
            if step.dependencies:
                # Wait for dependencies
                await self._await_dependencies(step.dependencies, results)
                
            # Execute step
            agent_result = await self._execute_agent_step(
                step,
                context=results
            )
            results[step.id] = agent_result
            
        # 4. Synthesize results
        return self._synthesize_results(results, task_definition)
    
    def _create_execution_plan(
        self,
        capabilities: list[str],
        registry: dict
    ) -> AgentExecutionPlan:
        """Create optimal execution plan"""
        
        # Use graph theory to optimize agent selection
        capability_graph = self._build_capability_graph(registry)
        optimal_path = self._find_optimal_coverage(
            capability_graph,
            capabilities
        )
        
        return AgentExecutionPlan(
            agents=optimal_path.agents,
            execution_steps=optimal_path.steps,
            estimated_duration=optimal_path.duration
        )
```

### 3. UV Dependency Governance Implementation

```toml
# pyproject.toml - Following UV Governance Playbook
[project]
name = "sophia-ai"
version = "1.5.0"
requires-python = ">=3.12"

[tool.uv.dependency-groups]
# Core platform dependencies
core = [
    "fastapi==0.111.0",
    "httpx==0.27.0",
    "snowflake-connector-python==3.10.0",
    "redis==5.0.4",
    "asyncpg==0.29.0"
]

# MCP server specific
mcp-servers = [
    "anthropic-mcp-python-sdk==1.2.4",
    "mcp-base==0.5.0"
]

# AI and ML
ai-enhanced = [
    "openai==1.30.0",
    "anthropic==0.25.6",
    "langchain==0.2.0",
    "langsmith==0.1.0"
]

# Workflow automation
automation = [
    "n8n-python-client==0.2.0",
    "temporal-sdk==1.5.0"
]

# Development tools
dev = [
    "pytest==8.2.2",
    "pytest-asyncio==0.23.0",
    "ruff==0.4.4",
    "mypy==1.10.0",
    "black==24.4.0"
]

[tool.uv.transitive-overrides]
# Security fixes
urllib3 = "==2.2.2"  # CVE-2024-XXXXX fix

[tool.uv]
compile = true  # Compile Python files for performance
```

```python
# scripts/uv_dependency_audit.py
"""UV Dependency Audit Tool - Part of Governance"""
import subprocess
import json
from datetime import datetime

class UVDependencyAuditor:
    def __init__(self):
        self.report_path = "dependency_audit_report.json"
        
    def run_audit(self):
        """Run comprehensive dependency audit"""
        
        results = {
            "timestamp": datetime.utcnow().isoformat(),
            "checks": {}
        }
        
        # 1. Check lock file integrity
        results["checks"]["lock_integrity"] = self._check_lock_integrity()
        
        # 2. Security vulnerabilities
        results["checks"]["vulnerabilities"] = self._run_security_scan()
        
        # 3. License compliance
        results["checks"]["licenses"] = self._check_licenses()
        
        # 4. Unused dependencies
        results["checks"]["unused"] = self._find_unused_deps()
        
        # 5. Version drift
        results["checks"]["drift"] = self._check_version_drift()
        
        # Generate report
        self._generate_report(results)
        
    def _run_security_scan(self):
        """Run uv audit for security issues"""
        result = subprocess.run(
            ["uv", "audit", "--format", "json"],
            capture_output=True,
            text=True
        )
        
        vulnerabilities = json.loads(result.stdout)
        
        # Categorize by severity
        return {
            "critical": [v for v in vulnerabilities if v["severity"] == "CRITICAL"],
            "high": [v for v in vulnerabilities if v["severity"] == "HIGH"],
            "medium": [v for v in vulnerabilities if v["severity"] == "MEDIUM"],
            "low": [v for v in vulnerabilities if v["severity"] == "LOW"]
        }
```

### 4. High-Performance LLM Strategy Implementation

```python
# backend/services/portkey_gateway_service.py
class PortkeyGatewayService:
    """High-performance LLM gateway following strategy playbook"""
    
    def __init__(self):
        self.policy_engine = HighPerformanceRoutingPolicy()
        self.openrouter_client = OpenRouterClient()
        self.metrics_collector = LLMMetricsCollector()
        
    async def invoke_llm(
        self,
        prompt: str,
        context: dict,
        preferences: dict = None
    ) -> LLMResponse:
        """Route LLM request through high-performance gateway"""
        
        # 1. Enrich request with tracing
        request_id = str(uuid.uuid4())
        span_context = self._create_span_context(request_id)
        
        # 2. Evaluate routing policy
        routing_decision = await self.policy_engine.evaluate(
            prompt=prompt,
            context=context,
            preferences=preferences or {}
        )
        
        # 3. Execute with streaming
        start_time = time.time()
        
        try:
            if routing_decision.streaming_enabled:
                response = await self._stream_response(
                    routing_decision.selected_model,
                    prompt,
                    span_context
                )
            else:
                response = await self._batch_response(
                    routing_decision.selected_model,
                    prompt,
                    span_context
                )
                
            # 4. Collect metrics
            self.metrics_collector.record_request(
                model=routing_decision.selected_model,
                latency=time.time() - start_time,
                tokens=response.token_count,
                success=True
            )
            
            return response
            
        except Exception as e:
            # Automatic failover
            return await self._handle_failover(
                routing_decision,
                prompt,
                e
            )
    
    async def _stream_response(
        self,
        model: str,
        prompt: str,
        context: dict
    ) -> LLMResponse:
        """Stream response with backpressure handling"""
        
        chunks = []
        first_token_time = None
        
        async for chunk in self.openrouter_client.stream(
            model=model,
            prompt=prompt,
            max_tokens=2000,
            temperature=0.7
        ):
            if first_token_time is None:
                first_token_time = time.time()
                
            chunks.append(chunk)
            
            # Yield to caller for immediate rendering
            if hasattr(context, "stream_callback"):
                await context.stream_callback(chunk)
                
        return LLMResponse(
            content="".join(chunks),
            model=model,
            first_token_latency=first_token_time,
            streaming=True
        )
```

```python
# backend/services/high_performance_routing_policy.py
class HighPerformanceRoutingPolicy:
    """
    Model scoring based on:
    - Freshness: 40 points (release < 90 days)
    - Latency: 25 points (p95 < 800ms)
    - Quality: 25 points (benchmark scores)
    - Cost: 10 points (only penalize if > $0.01/1k tokens)
    """
    
    def __init__(self):
        self.model_catalog = self._load_model_catalog()
        self.performance_history = self._load_performance_history()
        
    async def evaluate(
        self,
        prompt: str,
        context: dict,
        preferences: dict
    ) -> RoutingDecision:
        """Evaluate and select optimal model"""
        
        # 1. Get available models
        available_models = await self._get_available_models()
        
        # 2. Score each model
        scores = {}
        for model in available_models:
            scores[model.id] = self._calculate_score(
                model,
                prompt_length=len(prompt),
                context=context
            )
            
        # 3. Apply preferences (if any)
        if preferences.get("prefer_fast"):
            # Boost latency weight
            scores = self._adjust_for_speed_preference(scores)
            
        # 4. Select highest scoring model
        best_model = max(scores, key=scores.get)
        
        return RoutingDecision(
            selected_model=best_model,
            score=scores[best_model],
            alternatives=self._get_alternatives(scores, best_model),
            streaming_enabled=self._should_stream(prompt_length=len(prompt)),
            reasoning=self._explain_decision(best_model, scores)
        )
    
    def _calculate_score(self, model: Model, prompt_length: int, context: dict) -> float:
        """Calculate model score based on policy"""
        
        score = 0.0
        
        # Freshness (40 points)
        days_old = (datetime.utcnow() - model.release_date).days
        if days_old < 90:
            score += 40
        elif days_old < 180:
            score += 20
        else:
            score += 5
            
        # Latency (25 points)
        p95_latency = self.performance_history.get_p95_latency(model.id)
        if p95_latency < 800:
            score += 25
        elif p95_latency < 1500:
            score += 15
        else:
            score += 5
            
        # Quality (25 points)
        quality_percentile = model.benchmark_scores.get("sophia_eval", 0)
        score += quality_percentile * 0.25
        
        # Cost (10 points) - only penalize expensive models
        cost_per_1k = model.pricing.get("per_1k_tokens", 0)
        if cost_per_1k <= 0.01:
            score += 10
        else:
            # Linear penalty for expensive models
            score += max(0, 10 - (cost_per_1k - 0.01) * 100)
            
        return score
```

### 5. Intelligent Request Routing

```python
# backend/services/intelligent_request_router.py
class IntelligentRequestRouter:
    """Context-aware request routing with learning capabilities"""
    
    def __init__(self):
        self.routing_history = RoutingHistory()
        self.capability_map = self._load_capability_map()
        self.performance_tracker = PerformanceTracker()
        
    async def route_request(
        self,
        request: UnifiedRequest
    ) -> RoutingDecision:
        """Route request to optimal endpoint based on context"""
        
        # 1. Extract intent and requirements
        intent_analysis = await self._analyze_intent(request)
        
        # 2. Identify required capabilities
        required_capabilities = self._map_intent_to_capabilities(
            intent_analysis
        )
        
        # 3. Find candidate endpoints
        candidates = self._find_capable_endpoints(
            required_capabilities
        )
        
        # 4. Score candidates based on:
        #    - Current load
        #    - Historical performance
        #    - Capability match score
        #    - Cost efficiency
        scored_candidates = await self._score_candidates(
            candidates,
            request,
            intent_analysis
        )
        
        # 5. Select optimal endpoint
        selected = scored_candidates[0]
        
        # 6. Record decision for learning
        self.routing_history.record(
            request=request,
            decision=selected,
            timestamp=datetime.utcnow()
        )
        
        return RoutingDecision(
            endpoint=selected.endpoint,
            reasoning=selected.reasoning,
            confidence=selected.confidence,
            alternatives=scored_candidates[1:3]
        )
    
    async def _analyze_intent(self, request: UnifiedRequest) -> IntentAnalysis:
        """Use LLM to understand request intent"""
        
        # Use fast model for intent classification
        llm_response = await self.portkey_gateway.invoke_llm(
            prompt=f"""
            Analyze this request and identify:
            1. Primary intent (query, command, analysis, etc.)
            2. Required data sources
            3. Expected response type
            4. Complexity level
            
            Request: {request.query}
            Context: {json.dumps(request.context)}
            """,
            preferences={"prefer_fast": True}
        )
        
        return IntentAnalysis.from_llm_response(llm_response)
```

## 📋 Implementation Timeline

### Week 1: Foundation & Dependencies
- [ ] Implement UV dependency governance
- [ ] Set up dependency audit automation
- [ ] Create n8n integration service
- [ ] Deploy n8n instance on Lambda Labs

### Week 2: Workflow Automation
- [ ] Create business workflow templates
- [ ] Implement workflow trigger system
- [ ] Build n8n <-> Sophia bridge
- [ ] Test automated workflows

### Week 3: Multi-Agent Coordination
- [ ] Implement MCPMultiAgentCoordinator
- [ ] Create capability mapping system
- [ ] Build execution planning algorithm
- [ ] Test multi-agent scenarios

### Week 4: LLM Performance
- [ ] Deploy Portkey gateway service
- [ ] Implement routing policy engine
- [ ] Set up OpenRouter integration
- [ ] Create performance monitoring

### Week 5: Intelligent Routing
- [ ] Build intent analysis system
- [ ] Implement routing decision engine
- [ ] Create learning feedback loop
- [ ] Deploy to production

### Week 6: Integration & Testing
- [ ] End-to-end testing
- [ ] Performance optimization
- [ ] Documentation updates
- [ ] Team training

## 🔧 Configuration Updates

### 1. UV Configuration
```bash
# .github/workflows/uv-ci.yml
name: UV Dependency CI

on:
  push:
  pull_request:
  schedule:
    - cron: '0 0 * * *'  # Daily audit

jobs:
  dependency-quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Install UV
        run: curl -LsSf https://astral.sh/uv/install.sh | sh
        
      - name: Sync dependencies
        run: uv sync --strict --require-hashes
        
      - name: Security audit
        run: uv audit --format json > audit-report.json
        
      - name: License check
        run: uv run liccheck --fail
        
      - name: Upload results
        uses: actions/upload-artifact@v3
        with:
          name: dependency-reports
          path: |
            audit-report.json
            uv.lock
```

### 2. Portkey Configuration
```json
// config/portkey_config.json
{
  "gateway": {
    "url": "http://localhost:8100",
    "timeout": 30,
    "retry": {
      "max_attempts": 3,
      "backoff": "exponential"
    }
  },
  "routing_policy": {
    "weights": {
      "freshness": 40,
      "latency": 25,
      "quality": 25,
      "cost": 10
    },
    "preferences": {
      "default": "balanced",
      "fast": {
        "latency": 40,
        "freshness": 20
      },
      "quality": {
        "quality": 50,
        "freshness": 30
      }
    }
  },
  "models": {
    "allowed_providers": [
      "openai",
      "anthropic",
      "google",
      "meta",
      "mistral"
    ],
    "refresh_interval": 3600
  }
}
```

### 3. n8n Workflow Configuration
```yaml
# config/n8n_workflows.yaml
workflows:
  - id: daily-business-report
    name: Daily Business Intelligence Report
    schedule: "0 9 * * *"
    nodes:
      - type: snowflake-query
        config:
          query: |
            SELECT * FROM business_metrics
            WHERE date = CURRENT_DATE - 1
      - type: ai-analysis
        config:
          model: gpt-4
          prompt: "Analyze these metrics and create executive summary"
      - type: slack-notify
        config:
          channel: "#executive-updates"
          
  - id: customer-health-alert
    name: Customer Health Monitoring
    triggers:
      - type: webhook
        path: /customer-health
      - type: event
        source: gong
        event: low_sentiment_detected
    nodes:
      - type: gather-context
        inputs:
          - snowflake: customer_data
          - hubspot: deal_status
          - gong: recent_calls
      - type: ai-assessment
        config:
          prompt: "Assess customer health and recommend actions"
      - type: create-task
        config:
          system: linear
          priority: high
```

## 🚀 Expected Outcomes

### Technical Achievements
- **Build Speed**: 6x faster with UV (< 35s full install)
- **LLM Latency**: p95 < 2s for all requests
- **Workflow Automation**: 80% of routine tasks automated
- **Multi-Agent Success**: 95% task completion rate
- **Dependency Security**: 0 high/critical vulnerabilities

### Business Impact
- **Developer Velocity**: 40% faster feature delivery
- **Operational Efficiency**: 60% reduction in manual tasks
- **Decision Speed**: Real-time insights vs. daily reports
- **Model Performance**: Always using SOTA models
- **Cost Optimization**: 30% reduction through smart routing

## 📚 Documentation Updates Required

1. **Update System Handbook**
   - Add UV dependency governance section
   - Document LLM routing strategy
   - Include n8n workflow patterns
   - Update architecture diagrams

2. **Update .cursorrules**
   - Add UV-specific rules
   - Include Portkey usage patterns
   - Document multi-agent coordination

3. **Create Playbooks**
   - n8n workflow creation guide
   - Multi-agent task design patterns
   - LLM routing optimization guide

## ✅ Success Criteria

- [ ] UV dependency system fully operational
- [ ] 0 security vulnerabilities in dependencies
- [ ] n8n processing 100+ workflows daily
- [ ] Multi-agent tasks completing in < 30s
- [ ] LLM routing achieving target latencies
- [ ] All documentation updated and accurate

---

**Next Steps**: Review this plan, get stakeholder approval, and begin Week 1 implementation focusing on UV dependency governance as the foundation for all other improvements. 