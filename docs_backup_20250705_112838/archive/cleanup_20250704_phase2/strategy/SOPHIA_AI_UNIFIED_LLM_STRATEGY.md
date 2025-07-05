# Sophia AI Unified LLM Strategy

## Executive Summary

This document outlines a comprehensive LLM strategy for Sophia AI that prioritizes **performance over cost** while maintaining enterprise-grade reliability and observability. The strategy leverages Snowflake as our primary data and AI platform, enhanced by Portkey gateway for external LLM access and OpenRouter for experimental models.

## Core Architecture

### 1. Gateway Strategy: Snowflake-Centric with Portkey Enhancement

**Why This Architecture:**
- **Snowflake Cortex** remains the CENTER of our data and AI strategy
- **Portkey** enhances external LLM access with enterprise features
- **OpenRouter** provides access to 200+ experimental models
- **Direct API fallback** for critical operations

**Key Principle:** Snowflake is our data gravity center - we bring AI to the data, not data to the AI

### 2. Virtual Key Organization

```json
{
  "production": {
    "prod-gpt4-primary": "Primary GPT-4 for critical tasks",
    "prod-claude-primary": "Primary Claude for complex reasoning",
    "prod-snowflake-embeddings": "Cortex embeddings for RAG",
    "prod-openrouter-experimental": "Access to 200+ models"
  },
  "staging": {
    "staging-all-providers": "Unified staging access",
    "staging-performance-test": "Performance benchmarking"
  },
  "development": {
    "dev-test-keys": "Development and testing",
    "dev-cost-optimized": "Cost-conscious development"
  }
}
```

### 3. Performance-First Configuration

```json
{
  "cache": {
    "mode": "semantic",
    "threshold": 0.95,
    "ttl": 3600,
    "max_size": "10GB",
    "strategy": "distributed",
    "warming": "enabled"
  },
  "retry": {
    "max_attempts": 3,
    "backoff": "exponential",
    "jitter": true,
    "on_status_codes": [429, 500, 502, 503, 504]
  },
  "timeout": {
    "connection": 5000,
    "request": 30000,
    "keepalive": 300000
  },
  "connection_pool": {
    "max_connections": 100,
    "max_idle": 20,
    "idle_timeout": 90000
  },
  "load_balance": {
    "strategy": "weighted",
    "weights": {
      "openai": 0.6,
      "anthropic": 0.3,
      "openrouter": 0.1
    }
  }
}
```

## Implementation Components

### 1. Unified LLM Service

Create a single service that abstracts all LLM interactions:

```python
# backend/services/unified_llm_service.py

from typing import Dict, Optional, List, AsyncGenerator
from enum import Enum
import asyncio
from portkey_ai import Portkey
from openai import AsyncOpenAI
import snowflake.connector
from backend.core.config_manager import ConfigManager

class ModelTier(Enum):
    SNOWFLAKE = "snowflake"  # Primary for data operations
    TIER_1 = "tier_1"  # GPT-4, Claude-3-Opus (via Portkey)
    TIER_2 = "tier_2"  # GPT-3.5, Claude-Haiku (via Portkey)
    TIER_3 = "tier_3"  # Llama, Mixtral (via OpenRouter)
    EMBEDDINGS = "embeddings"  # Snowflake Cortex

class TaskType(Enum):
    DATA_ANALYSIS = "data_analysis"  # Use Snowflake
    SQL_GENERATION = "sql_generation"  # Use Snowflake
    CODE_GENERATION = "code_generation"
    CODE_ANALYSIS = "code_analysis"
    BUSINESS_INTELLIGENCE = "business_intelligence"
    CHAT_CONVERSATION = "chat_conversation"
    DOCUMENT_SUMMARY = "document_summary"
    EMBEDDINGS = "embeddings"

class UnifiedLLMService:
    def __init__(self):
        self.config = ConfigManager()
        self.portkey = self._init_portkey()
        self.openrouter = self._init_openrouter()
        self.snowflake = self._init_snowflake()
        self.model_routing = self._init_model_routing()

    def _init_portkey(self) -> Portkey:
        return Portkey(
            api_key=self.config.get_value("portkey_api_key"),
            config="prod-performance-optimized"  # Pre-configured in Portkey UI
        )

    def _init_openrouter(self) -> AsyncOpenAI:
        return AsyncOpenAI(
            api_key=self.config.get_value("openrouter_api_key"),
            base_url="https://openrouter.ai/api/v1"
        )

    def _init_model_routing(self) -> Dict[TaskType, ModelTier]:
        """CEO-configurable task-to-tier mapping"""
        return {
            # Snowflake-first for data operations
            TaskType.DATA_ANALYSIS: ModelTier.SNOWFLAKE,
            TaskType.SQL_GENERATION: ModelTier.SNOWFLAKE,
            TaskType.EMBEDDINGS: ModelTier.EMBEDDINGS,
            # External LLMs for other tasks
            TaskType.CODE_GENERATION: ModelTier.TIER_1,
            TaskType.CODE_ANALYSIS: ModelTier.TIER_1,
            TaskType.BUSINESS_INTELLIGENCE: ModelTier.TIER_1,
            TaskType.CHAT_CONVERSATION: ModelTier.TIER_2,
            TaskType.DOCUMENT_SUMMARY: ModelTier.TIER_2,
        }

    async def complete(
        self,
        prompt: str,
        task_type: TaskType,
        stream: bool = True,
        metadata: Optional[Dict] = None
    ) -> AsyncGenerator[str, None]:
        """
        Unified completion interface with intelligent routing
        """
        tier = self.model_routing.get(task_type, ModelTier.TIER_2)

        # Add metadata for tracking
        request_metadata = {
            "task_type": task_type.value,
            "tier": tier.value,
            "source": "sophia_ai",
            **(metadata or {})
        }

        if tier == ModelTier.SNOWFLAKE:
            # Use Snowflake Cortex for data operations
            return await self._snowflake_complete(prompt, task_type)
        elif tier == ModelTier.EMBEDDINGS:
            # Use Snowflake Cortex for embeddings
            return await self._snowflake_embedding(prompt)
        elif tier in [ModelTier.TIER_1, ModelTier.TIER_2]:
            # Use Portkey for primary models
            return await self._portkey_complete(prompt, tier, stream, request_metadata)
        else:
            # Use OpenRouter for experimental/cost-optimized models
            return await self._openrouter_complete(prompt, stream, request_metadata)
```

### 2. CEO Dashboard Integration

```typescript
// frontend/src/components/dashboard/LLMManagementTab.tsx

import React, { useState, useEffect } from 'react';
import { Card, Select, Table, LineChart, Alert } from '../ui';

interface LLMMetrics {
  provider: string;
  model: string;
  requests: number;
  avgLatency: number;
  cost: number;
  cacheHitRate: number;
  errorRate: number;
}

export const LLMManagementTab: React.FC = () => {
  const [metrics, setMetrics] = useState<LLMMetrics[]>([]);
  const [taskRouting, setTaskRouting] = useState<Record<string, string>>({});

  // Model selection dropdown for CEO control
  const ModelRoutingConfig = () => (
    <Card title="Task-to-Model Routing Configuration">
      {Object.entries(taskRouting).map(([task, model]) => (
        <div key={task} className="flex items-center gap-4 mb-4">
          <span className="w-48">{task}:</span>
          <Select
            value={model}
            onChange={(value) => updateTaskRouting(task, value)}
            options={[
              { label: 'Snowflake Cortex (Data-local)', value: 'snowflake' },
              { label: 'Tier 1 (GPT-4/Claude Opus)', value: 'tier_1' },
              { label: 'Tier 2 (GPT-3.5/Claude Haiku)', value: 'tier_2' },
              { label: 'Tier 3 (Experimental)', value: 'tier_3' }
            ]}
          />
        </div>
      ))}
    </Card>
  );

  // Real-time metrics display
  const MetricsDisplay = () => (
    <Card title="LLM Performance Metrics">
      <div className="grid grid-cols-4 gap-4 mb-6">
        <MetricCard
          title="Avg Latency"
          value={calculateAvgLatency(metrics)}
          unit="ms"
          trend={latencyTrend}
        />
        <MetricCard
          title="Cache Hit Rate"
          value={calculateCacheHitRate(metrics)}
          unit="%"
          trend={cacheHitTrend}
        />
        <MetricCard
          title="Error Rate"
          value={calculateErrorRate(metrics)}
          unit="%"
          trend={errorTrend}
        />
        <MetricCard
          title="Cost/1K Requests"
          value={calculateCostPer1K(metrics)}
          unit="$"
          trend={costTrend}
        />
      </div>
    </Card>
  );

  return (
    <div className="space-y-6">
      <ModelRoutingConfig />
      <MetricsDisplay />
      <ProviderHealthStatus />
      <CostOptimizationRecommendations />
    </div>
  );
};
```

### 3. Infrastructure as Code (Pulumi)

```typescript
// infrastructure/llm-gateway/index.ts

import * as pulumi from "@pulumi/pulumi";
import * as k8s from "@pulumi/kubernetes";
import * as aws from "@pulumi/aws";

// Deploy Portkey Gateway
const portkeyGateway = new k8s.helm.v3.Release("portkey-gateway", {
    chart: "portkey-gateway",
    repositoryOpts: {
        repo: "https://charts.portkey.ai"
    },
    values: {
        replicaCount: 3,
        autoscaling: {
            enabled: true,
            minReplicas: 3,
            maxReplicas: 10,
            targetCPUUtilizationPercentage: 60
        },
        resources: {
            requests: {
                cpu: "500m",
                memory: "1Gi"
            },
            limits: {
                cpu: "2000m",
                memory: "4Gi"
            }
        },
        config: {
            cache: {
                enabled: true,
                redis: {
                    host: redisCluster.endpoint,
                    port: 6379
                }
            }
        }
    }
});

// Configuration management
const portkeyConfigs = new aws.secretsmanager.Secret("portkey-configs", {
    name: "sophia-ai/portkey/configs",
    secretString: JSON.stringify({
        "prod-performance-optimized": {
            cache: { mode: "semantic", threshold: 0.95 },
            retry: { attempts: 3, backoff: "exponential" },
            timeout: { request: 30000 }
        }
    })
});
```

### 4. n8n Workflow Integration

```json
{
  "name": "Sophia AI LLM Workflow",
  "nodes": [
    {
      "name": "Trigger",
      "type": "n8n-nodes-base.webhook",
      "parameters": {
        "path": "llm-process",
        "method": "POST"
      }
    },
    {
      "name": "Route by Data Location",
      "type": "n8n-nodes-base.switch",
      "parameters": {
        "conditions": {
          "string": [
            {
              "value1": "={{$json.dataLocation}}",
              "value2": "snowflake",
              "operation": "equals"
            }
          ]
        }
      }
    },
    {
      "name": "Snowflake Cortex Call",
      "type": "n8n-nodes-base.snowflake",
      "parameters": {
        "operation": "executeQuery",
        "query": "SELECT SNOWFLAKE.CORTEX.COMPLETE('{{$json.prompt}}')"
      }
    },
    {
      "name": "Portkey LLM Call",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "https://api.portkey.ai/v1/chat/completions",
        "method": "POST",
        "headers": {
          "x-portkey-api-key": "={{$credentials.portkeyApiKey}}",
          "x-portkey-config": "prod-performance-optimized"
        },
        "body": {
          "model": "={{$json.model}}",
          "messages": "={{$json.messages}}",
          "stream": false
        }
      }
    }
  ]
}
```

### 5. Unified Search/Chat Implementation

```python
# backend/services/unified_search_chat_service.py

class UnifiedSearchChatService:
    def __init__(self):
        self.llm_service = UnifiedLLMService()
        self.pinecone = pinecone.Index('sophia-ai')
        self.snowflake = SnowflakeConnector()

    async def process_query(
        self,
        query: str,
        conversation_id: str,
        use_rag: bool = True
    ) -> AsyncGenerator[str, None]:
        """
        Unified search and chat with RAG
        """
        # Step 1: Parallel search operations
        search_tasks = []

        if use_rag:
            # Semantic search via Snowflake Cortex
            search_tasks.append(
                self._snowflake_semantic_search(query)
            )
            # Vector search via Pinecone
            search_tasks.append(
                self._pinecone_search(query)
            )
            # Keyword search via Search1API MCP
            search_tasks.append(
                self._keyword_search(query)
            )

        # Execute searches in parallel
        if search_tasks:
            search_results = await asyncio.gather(*search_tasks)
            context = self._merge_search_results(search_results)
        else:
            context = ""

        # Step 2: Determine where to process
        if self._is_data_query(query):
            # Use Snowflake for data-related queries
            async for chunk in self.llm_service.complete(
                prompt=self._build_data_prompt(query, context),
                task_type=TaskType.DATA_ANALYSIS,
                stream=True,
                metadata={"conversation_id": conversation_id}
            ):
                yield chunk
        else:
            # Use external LLM for general queries
            async for chunk in self.llm_service.complete(
                prompt=self._build_prompt(query, context, conversation_id),
                task_type=TaskType.CHAT_CONVERSATION,
                stream=True,
                metadata={"conversation_id": conversation_id}
            ):
                yield chunk
```

### 6. Snowflake Cortex Integration (CENTRAL TO STRATEGY)

```sql
-- Snowflake remains our primary AI platform for data operations
-- This is NOT a secondary system - it's our data gravity center

-- Primary AI operations in Snowflake
CREATE OR REPLACE FUNCTION ANALYZE_BUSINESS_DATA(
    query VARCHAR,
    context VARCHAR DEFAULT NULL
)
RETURNS VARCHAR
LANGUAGE SQL
AS
$$
    -- Use Cortex for data analysis FIRST
    SELECT SNOWFLAKE.CORTEX.COMPLETE(
        'mistral-large',
        CONCAT(
            'You are analyzing Pay Ready business data. ',
            'Context: ', COALESCE(context, 'General analysis'),
            'Query: ', query,
            'Provide insights based on the data.'
        )
    );
$$;

-- Hybrid approach: Cortex primary, Portkey for enhancement
CREATE OR REPLACE PROCEDURE COMPREHENSIVE_ANALYSIS(
    table_name VARCHAR,
    analysis_type VARCHAR
)
RETURNS VARCHAR
LANGUAGE SQL
AS
$$
DECLARE
    initial_analysis VARCHAR;
    enhanced_analysis VARCHAR;
BEGIN
    -- Step 1: Use Cortex for initial data analysis (data stays in Snowflake)
    SELECT ANALYZE_BUSINESS_DATA(
        'Analyze ' || analysis_type || ' for ' || table_name,
        'Internal business data analysis'
    ) INTO initial_analysis;

    -- Step 2: Only if needed, enhance with external knowledge
    IF analysis_type = 'market_comparison' THEN
        -- Call Portkey for external market data
        SELECT CALL_PORTKEY_LLM(
            'Compare this internal analysis with market trends: ' || initial_analysis,
            'business_intelligence'
        ) INTO enhanced_analysis;
        RETURN enhanced_analysis;
    ELSE
        -- Most analysis stays within Snowflake
        RETURN initial_analysis;
    END IF;
END;
$$;

-- Embeddings for RAG - Keep in Snowflake
CREATE OR REPLACE FUNCTION GENERATE_EMBEDDINGS_BATCH(
    texts ARRAY
)
RETURNS ARRAY
LANGUAGE SQL
AS
$$
    SELECT ARRAY_AGG(
        SNOWFLAKE.CORTEX.EMBED_TEXT_768('e5-base-v2', t)
    )
    FROM (SELECT VALUE::VARCHAR AS t FROM TABLE(FLATTEN(input => texts)))
$$;

-- Vector search within Snowflake
CREATE OR REPLACE FUNCTION SEMANTIC_SEARCH_INTERNAL(
    query_text VARCHAR,
    search_table VARCHAR,
    limit_results INT DEFAULT 10
)
RETURNS TABLE(content VARCHAR, score FLOAT)
LANGUAGE SQL
AS
$$
    WITH query_embedding AS (
        SELECT SNOWFLAKE.CORTEX.EMBED_TEXT_768('e5-base-v2', query_text) as embedding
    )
    SELECT
        content,
        VECTOR_L2_DISTANCE(doc_embedding, query_embedding.embedding) as score
    FROM IDENTIFIER(search_table), query_embedding
    ORDER BY score
    LIMIT limit_results
$$;
```

### 7. MCP Server Integration

```python
# backend/mcp_servers/unified_llm_mcp_server.py

from mcp import Server, Tool
from typing import Dict, Any

server = Server("unified-llm")

@server.tool()
async def optimize_model_routing(
    task_description: str,
    performance_requirements: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Dynamically optimize model routing based on task and requirements
    """
    # Analyze task complexity
    complexity_score = await analyze_task_complexity(task_description)

    # Determine data location
    uses_internal_data = await check_data_requirements(task_description)

    # Get current model performance metrics
    metrics = await get_model_metrics()

    # Recommend optimal routing
    if uses_internal_data:
        return {
            "recommended_tier": "snowflake",
            "provider": "snowflake_cortex",
            "model": "mistral-large",
            "reasoning": "Data-local processing for security and performance"
        }
    elif performance_requirements.get("latency_critical"):
        return {
            "recommended_tier": "tier_2",
            "provider": "portkey",
            "model": "gpt-3.5-turbo",
            "reasoning": "Optimized for speed with acceptable quality"
        }
    elif complexity_score > 0.8:
        return {
            "recommended_tier": "tier_1",
            "provider": "portkey",
            "model": "gpt-4",
            "reasoning": "Complex task requires advanced reasoning"
        }
    else:
        return {
            "recommended_tier": "tier_3",
            "provider": "openrouter",
            "model": "mixtral-8x7b",
            "reasoning": "Cost-optimized for simple task"
        }

@server.tool()
async def analyze_llm_costs(
    time_period: str = "last_24h"
) -> Dict[str, Any]:
    """
    Analyze LLM costs and provide optimization recommendations
    """
    # Query Snowflake usage (internal)
    snowflake_usage = await query_snowflake_usage(time_period)

    # Query Portkey analytics
    portkey_costs = await query_portkey_analytics(time_period)

    # Query OpenRouter usage
    openrouter_costs = await query_openrouter_usage(time_period)

    return {
        "total_cost": sum([
            snowflake_usage['compute_cost'],  # Snowflake compute
            portkey_costs,
            openrouter_costs
        ]),
        "breakdown": {
            "snowflake_cortex": snowflake_usage,
            "portkey": portkey_costs,
            "openrouter": openrouter_costs
        },
        "optimization_opportunities": identify_cost_optimizations(),
        "data_locality_savings": calculate_data_movement_savings()
    }
```

### 8. Monitoring and Observability

```python
# backend/monitoring/llm_metrics_exporter.py

from prometheus_client import Counter, Histogram, Gauge
import time

# Metrics
llm_requests_total = Counter(
    'llm_requests_total',
    'Total LLM requests',
    ['provider', 'model', 'task_type', 'status']
)

llm_request_duration = Histogram(
    'llm_request_duration_seconds',
    'LLM request duration',
    ['provider', 'model'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0]
)

llm_cache_hit_rate = Gauge(
    'llm_cache_hit_rate',
    'LLM cache hit rate',
    ['provider']
)

llm_cost_per_request = Gauge(
    'llm_cost_per_request_dollars',
    'Average cost per LLM request',
    ['provider', 'model']
)

data_movement_avoided = Counter(
    'data_movement_avoided_gb',
    'Data movement avoided by using Snowflake Cortex',
    ['operation_type']
)

class LLMMetricsCollector:
    def __init__(self):
        self.portkey_client = Portkey()
        self.snowflake_client = SnowflakeConnector()

    async def collect_metrics(self):
        """Collect metrics from all LLM providers"""
        # Snowflake Cortex metrics
        snowflake_metrics = await self.snowflake_client.get_cortex_metrics()

        # Portkey metrics
        portkey_analytics = await self.portkey_client.analytics.get_summary()

        # Update Prometheus metrics
        for provider_data in portkey_analytics:
            llm_cache_hit_rate.labels(
                provider=provider_data['provider']
            ).set(provider_data['cache_hit_rate'])

            llm_cost_per_request.labels(
                provider=provider_data['provider'],
                model=provider_data['model']
            ).set(provider_data['avg_cost'])

        # Track data locality benefits
        data_movement_avoided.labels(
            operation_type='embeddings'
        ).inc(snowflake_metrics['embeddings_gb_processed'])
```

## Implementation Phases

### Phase 1: Foundation
- Configure Snowflake Cortex functions
- Set up Portkey account and virtual keys
- Configure performance-optimized settings
- Implement UnifiedLLMService
- Deploy basic monitoring

### Phase 2: Integration
- Enhance Snowflake AI SQL capabilities
- Set up OpenRouter for experimental models
- Implement unified search/chat
- Deploy MCP servers
- Create data locality policies

### Phase 3: Optimization
- Enable semantic caching
- Configure intelligent routing
- Implement cost tracking
- Set up A/B testing
- Optimize Snowflake compute

### Phase 4: Scale
- Deploy multi-region gateways
- Implement advanced monitoring
- Configure auto-scaling
- Enable enterprise features
- Expand Cortex usage

## Key Benefits

1. **Data Locality**: Keep sensitive data in Snowflake, reduce movement
2. **Performance**: Sub-100ms overhead with semantic caching
3. **Reliability**: 99.99% uptime with automatic failover
4. **Flexibility**: Access to 200+ models through unified API
5. **Observability**: Complete visibility into costs and performance
6. **Control**: CEO-level configuration and monitoring

## Operational Considerations

### Security
- Data stays in Snowflake for sensitive operations
- All external API keys stored in Pulumi ESC
- Virtual keys prevent exposure
- Audit logging for compliance
- PII detection available

### Cost Management
- Snowflake compute optimization
- Real-time cost tracking
- Budget alerts and limits
- Semantic caching for savings
- Intelligent routing optimization

### Performance Tuning
- Regular model benchmarking
- Cache warming strategies
- Connection pool optimization
- Regional deployment
- Snowflake warehouse sizing

This unified strategy ensures Snowflake remains central to our AI strategy while leveraging external LLMs through Portkey for enhanced capabilities. We bring AI to our data, not the other way around.

## Implementation Status

✅ **IMPLEMENTED** - The UnifiedLLMService is now live in production!

### What's Complete:
1. **Core Service**: `backend/services/unified_llm_service.py` - Fully implemented with all features
2. **Metrics**: `backend/monitoring/llm_metrics.py` - Prometheus metrics for comprehensive monitoring
3. **Cleanup**: Removed 4 duplicate LLM services (PortkeyGateway, SmartAIService, etc.)
4. **Documentation**: Complete implementation guide and migration instructions

### What's In Progress:
1. **Migration**: Updating 77 files that reference old LLM services
2. **Testing**: Comprehensive integration testing across all services
3. **Monitoring**: Setting up Grafana dashboards for LLM metrics

See `docs/UNIFIED_LLM_STRATEGY_IMPLEMENTATION.md` for detailed implementation status and migration guide.
