# Phase 3: Do Later Tasks - Implementation Plan

## Overview

These are the strategic enhancements identified for future implementation to further optimize the UnifiedLLMService and reduce costs.

## 1. Evaluate Portkey Virtual Keys for Better Cost Tracking

### What Are Virtual Keys?
Portkey Virtual Keys allow you to create sub-keys for different projects, teams, or environments while using a single Portkey account. Each virtual key can have its own:
- Cost tracking
- Rate limits
- Model access
- Usage analytics

### Implementation Plan

#### Step 1: Create Virtual Keys Structure
```python
# backend/services/portkey_virtual_keys.py
VIRTUAL_KEYS = {
    "departments": {
        "engineering": "vk_eng_xxx",
        "sales": "vk_sales_xxx",
        "marketing": "vk_mkt_xxx",
        "executive": "vk_exec_xxx"
    },
    "environments": {
        "production": "vk_prod_xxx",
        "staging": "vk_stg_xxx",
        "development": "vk_dev_xxx"
    },
    "task_types": {
        "chat": "vk_chat_xxx",
        "analysis": "vk_analysis_xxx",
        "generation": "vk_gen_xxx"
    }
}
```

#### Step 2: Update UnifiedLLMService
- Add virtual key selection based on context
- Track costs per department/project
- Generate detailed cost reports

### Benefits
- **Granular Cost Tracking**: Know exactly how much each department spends
- **Budget Controls**: Set limits per virtual key
- **Better Analytics**: Understand usage patterns by team
- **Chargeback Capability**: Bill departments for their AI usage

### Estimated Implementation: 4-6 hours

## 2. Consider SonarQube MCP Integration

### What This Means
Create an MCP (Model Context Protocol) server that integrates with SonarQube to provide AI-powered code quality insights directly in the chat interface.

### Implementation Plan

#### Step 1: Create SonarQube MCP Server
```python
# mcp-servers/sonarqube/sonarqube_mcp_server.py
class SonarQubeMCPServer(StandardizedMCPServer):
    """MCP server for SonarQube integration"""

    @mcp.tool()
    async def analyze_project(self, project_key: str) -> dict:
        """Get SonarQube analysis for a project"""

    @mcp.tool()
    async def get_code_smells(self, project_key: str, severity: str = "MAJOR") -> list:
        """Get code smells by severity"""

    @mcp.tool()
    async def get_security_hotspots(self, project_key: str) -> list:
        """Get security hotspots"""
```

#### Step 2: Natural Language Interface
Enable queries like:
- "What are the critical issues in the backend?"
- "Show me security vulnerabilities"
- "What's our technical debt score?"
- "Which files have the most code smells?"

### Benefits
- **Proactive Quality**: AI suggests fixes before code review
- **Natural Language**: No need to navigate SonarQube UI
- **Integrated Workflow**: Quality checks in the same chat interface
- **Automated Remediation**: AI can suggest and apply fixes

### Estimated Implementation: 8-10 hours

## 3. Implement Semantic Caching

### What Is Semantic Caching?
Instead of exact string matching, semantic caching uses embeddings to identify similar queries and reuse responses, even if the wording is different.

### Implementation Plan

#### Step 1: Create Semantic Cache Service
```python
# backend/services/semantic_cache_service.py
class SemanticCacheService:
    def __init__(self):
        self.embedding_model = "text-embedding-ada-002"
        self.similarity_threshold = 0.95
        self.cache_ttl = 3600  # 1 hour

    async def get_or_compute(
        self,
        query: str,
        compute_fn: Callable,
        context: dict = None
    ) -> str:
        # 1. Generate embedding for query
        # 2. Search for similar cached queries
        # 3. If match found with > threshold, return cached
        # 4. Otherwise compute and cache
```

#### Step 2: Integration Points
1. **Portkey Integration**: Use Portkey's built-in semantic caching
2. **Snowflake Integration**: Store embeddings in Snowflake
3. **Custom Implementation**: Build our own with Pinecone/Weaviate

#### Step 3: Cache Strategy
```python
CACHE_CONFIG = {
    "chat_conversation": {
        "ttl": 3600,
        "threshold": 0.95
    },
    "document_summary": {
        "ttl": 86400,  # 24 hours
        "threshold": 0.90
    },
    "sql_generation": {
        "ttl": 7200,
        "threshold": 0.98  # Higher threshold for SQL
    }
}
```

### Benefits
- **30-50% Cost Reduction**: Reuse responses for similar queries
- **Faster Responses**: Cached responses return instantly
- **Better UX**: Consistent answers for similar questions
- **Reduced API Calls**: Fewer calls to expensive models

### Implementation Options

#### Option 1: Use Portkey's Semantic Cache (Recommended)
- **Effort**: 2-3 hours
- **Cost**: Included in Portkey pricing
- **Benefits**: Zero maintenance, proven solution

#### Option 2: Build Custom Solution
- **Effort**: 16-20 hours
- **Cost**: Additional vector DB costs
- **Benefits**: Full control, custom features

## 4. Additional Optimizations to Consider

### A. Implement Request Batching
- Batch multiple small requests together
- Reduce per-request overhead
- Estimated savings: 10-15%

### B. Add Request Deduplication
- Detect identical concurrent requests
- Return same response to all
- Estimated savings: 5-10%

### C. Implement Fallback Strategies
- Graceful degradation when primary models fail
- Automatic retry with exponential backoff
- Circuit breaker patterns

### D. Add Cost Alerts
- Slack/email alerts for unusual spending
- Daily/weekly cost reports
- Budget threshold notifications

## Recommended Implementation Order

1. **Semantic Caching** (Highest ROI)
   - Use Portkey's built-in solution
   - 2-3 hours effort
   - 30-50% cost reduction

2. **Portkey Virtual Keys**
   - Better cost visibility
   - 4-6 hours effort
   - Enables chargeback

3. **Cost Alerts**
   - Prevent bill shock
   - 2-3 hours effort
   - Peace of mind

4. **SonarQube MCP Integration**
   - Nice to have
   - 8-10 hours effort
   - Improves code quality

## Quick Wins (Do This Week)

### 1. Enable Portkey Semantic Caching
```python
# In UnifiedLLMService._init_portkey()
"cache": {
    "mode": "semantic",
    "threshold": 0.95,
    "ttl": 3600,
}
```

### 2. Add Basic Cost Alerts
```python
# backend/monitoring/cost_alerts.py
async def check_daily_spend():
    if daily_cost > DAILY_BUDGET_THRESHOLD:
        await send_slack_alert(f"LLM costs exceeded budget: ${daily_cost}")
```

### 3. Create Cost Dashboard
- Use existing Grafana setup
- Add cost panels to LLM dashboard
- Set up daily email reports

## Success Metrics

- **Cost per Request**: Target < $0.01
- **Cache Hit Rate**: Target > 40%
- **Response Time**: Target < 200ms (p95)
- **Cost Reduction**: Target 40-60% overall

## Next Steps

1. Review this plan with the team
2. Prioritize based on current pain points
3. Start with semantic caching (biggest win)
4. Measure impact before moving to next item
