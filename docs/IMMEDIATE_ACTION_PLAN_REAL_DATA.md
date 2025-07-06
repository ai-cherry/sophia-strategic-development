# Immediate Action Plan: Enable Real Data in Sophia AI

**Date:** July 6, 2025
**Priority:** CRITICAL
**Timeline:** 1-2 weeks

## Executive Summary

The primary issue preventing live data in the Vercel deployment is that the backend services are intentionally returning mock/simulated data. This document provides an immediate action plan to enable real data flow.

## Root Cause Analysis

### Current State
1. **Frontend (Vercel):** ✅ Working correctly, properly configured
2. **Backend API:** ✅ Running and accessible
3. **Data Services:** ❌ Returning mock/empty data
4. **LLM Service:** ❌ Using placeholder implementation
5. **Snowflake Cortex:** ❌ Using simulation fallback

### Specific Issues
```python
# backend/services/unified_intelligence_service.py
def _handle_sales_query(self, query: str) -> Dict:
    # ISSUE: Hardcoded empty results
    return {"type": "sales", "results": [], "insights": []}

# backend/services/enhanced_unified_intelligence_service.py
def _execute_snowflake_intelligence(self, query: str) -> Dict:
    # ISSUE: Falls back to simulation
    return self._simulate_snowflake_response(query)
```

## Immediate Action Plan

### Phase 1: Enable Real Data Sources (Days 1-3)

#### 1.1 Fix Snowflake Connection
```python
# backend/services/snowflake_cortex_service.py
class SnowflakeCortexService:
    def __init__(self):
        # Ensure real connection using Pulumi ESC
        self.conn = self._get_snowflake_connection()

    def _get_snowflake_connection(self):
        from backend.core.auto_esc_config import get_config_value

        return snowflake.connector.connect(
            user=get_config_value("snowflake_user"),
            password=get_config_value("snowflake_password"),
            account=get_config_value("snowflake_account"),
            warehouse=get_config_value("snowflake_warehouse"),
            database=get_config_value("snowflake_database"),
            schema=get_config_value("snowflake_schema")
        )
```

#### 1.2 Implement Real Query Methods
```python
# backend/services/unified_intelligence_service.py
def _handle_sales_query(self, query: str) -> Dict:
    """Fetch real sales data from Snowflake"""
    try:
        # Query actual sales data
        sql = """
        SELECT
            deal_id,
            deal_name,
            amount,
            stage,
            close_date,
            probability
        FROM ENRICHED_HUBSPOT_DEALS
        WHERE is_closed = FALSE
        ORDER BY amount DESC
        LIMIT 10
        """

        results = self.snowflake_service.execute_query(sql)

        # Generate real insights
        insights = self._generate_sales_insights(results)

        return {
            "type": "sales",
            "results": results,
            "insights": insights
        }
    except Exception as e:
        logger.error(f"Sales query failed: {e}")
        return {
            "type": "sales",
            "results": [],
            "insights": [],
            "error": "Unable to fetch sales data"
        }
```

#### 1.3 Enable Gong Integration
```python
# backend/integrations/gong_integration.py
class EnhancedGongIntegration:
    def get_recent_calls(self, limit: int = 10) -> List[Dict]:
        """Fetch real call data from Gong"""
        headers = {
            "Authorization": f"Bearer {get_config_value('gong_access_key')}"
        }

        response = requests.get(
            f"{self.base_url}/v2/calls",
            headers=headers,
            params={"limit": limit}
        )

        if response.status_code == 200:
            return response.json()["calls"]
        else:
            logger.error(f"Gong API error: {response.status_code}")
            return []
```

### Phase 2: Implement LLM Service (Days 4-5)

#### 2.1 Create Real LLM Service
```python
# backend/services/llm_service.py
from openai import AsyncOpenAI
from backend.core.auto_esc_config import get_config_value

class LLMService:
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=get_config_value("openai_api_key")
        )

    async def synthesize_response(
        self,
        query: str,
        context: Dict,
        results: List[Dict]
    ) -> str:
        """Generate comprehensive response using GPT-4"""

        messages = [
            {
                "role": "system",
                "content": "You are Sophia AI, an executive assistant providing business intelligence insights."
            },
            {
                "role": "user",
                "content": f"""
                Query: {query}

                Context: {json.dumps(context)}

                Data Results: {json.dumps(results[:5])}  # Limit for token management

                Please provide a comprehensive, actionable response.
                """
            }
        ]

        response = await self.client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=0.7,
            max_tokens=1000
        )

        return response.choices[0].message.content
```

#### 2.2 Update Intelligence Service
```python
# backend/services/unified_intelligence_service.py
def __init__(self, config: Optional[Dict] = None):
    super().__init__(config)
    # Use real LLM service instead of placeholder
    self.llm_service = LLMService()
```

### Phase 3: Deploy Snowflake Cortex Functions (Days 6-7)

#### 3.1 Create Cortex Functions
```sql
-- backend/snowflake_setup/cortex_functions.sql

-- Sentiment Analysis Function
CREATE OR REPLACE FUNCTION ANALYZE_SENTIMENT(text VARCHAR)
RETURNS VARIANT
LANGUAGE PYTHON
RUNTIME_VERSION = '3.8'
HANDLER = 'analyze_sentiment'
AS $$
def analyze_sentiment(text):
    # Snowflake Cortex AI implementation
    return SNOWFLAKE.CORTEX.SENTIMENT(text)
$$;

-- Entity Extraction Function
CREATE OR REPLACE FUNCTION EXTRACT_ENTITIES(text VARCHAR)
RETURNS VARIANT
LANGUAGE PYTHON
RUNTIME_VERSION = '3.8'
HANDLER = 'extract_entities'
AS $$
def extract_entities(text):
    return SNOWFLAKE.CORTEX.EXTRACT_ENTITIES(text)
$$;

-- Embedding Generation Function
CREATE OR REPLACE FUNCTION GENERATE_EMBEDDING(text VARCHAR)
RETURNS ARRAY
LANGUAGE PYTHON
RUNTIME_VERSION = '3.8'
HANDLER = 'generate_embedding'
AS $$
def generate_embedding(text):
    return SNOWFLAKE.CORTEX.EMBED_TEXT(text, 'e5-base-v2')
$$;
```

#### 3.2 Remove Simulation Fallback
```python
# backend/services/enhanced_unified_intelligence_service.py
def _execute_snowflake_intelligence(self, query: str) -> Dict:
    """Execute real Snowflake Cortex AI analysis"""
    try:
        # Remove simulation, use real Cortex
        sql = f"""
        SELECT
            ANALYZE_SENTIMENT('{query}') as sentiment,
            EXTRACT_ENTITIES('{query}') as entities,
            GENERATE_EMBEDDING('{query}') as embedding
        """

        result = self.snowflake_service.execute_query(sql)

        return {
            "sentiment": result[0]["sentiment"],
            "entities": result[0]["entities"],
            "embedding": result[0]["embedding"],
            "analysis": self._process_cortex_results(result)
        }
    except Exception as e:
        logger.error(f"Cortex execution failed: {e}")
        # Return error, not simulation
        return {"error": str(e)}
```

### Phase 4: Configuration & Testing (Days 8-10)

#### 4.1 Update Pulumi ESC Configuration
```yaml
# pulumi/environments/sophia-ai-production.yaml
values:
  sophia:
    features:
      enable_mock_data: false  # CRITICAL CHANGE
      enable_real_data: true
      llm_provider: "openai"
      llm_model: "gpt-4"

    data_sources:
      snowflake:
        enabled: true
        real_time: true
      gong:
        enabled: true
        sync_interval: 300
      hubspot:
        enabled: true
        webhook_enabled: true
```

#### 4.2 Create Integration Tests
```python
# tests/integration/test_real_data_flow.py
import pytest
from backend.services.unified_intelligence_service import UnifiedIntelligenceService

@pytest.mark.integration
class TestRealDataFlow:
    def test_sales_query_returns_real_data(self):
        service = UnifiedIntelligenceService()
        result = service.process_query("Show me top deals")

        assert result["results"] != []
        assert result["results"][0].get("deal_id") is not None
        assert result["insights"] != []

    def test_snowflake_cortex_active(self):
        service = EnhancedUnifiedIntelligenceService()
        result = service._execute_snowflake_intelligence("test query")

        assert "error" not in result
        assert "simulation" not in str(result).lower()
        assert result.get("sentiment") is not None
```

## Deployment Checklist

### Pre-Deployment
- [ ] Verify all Snowflake credentials in Pulumi ESC
- [ ] Confirm Gong API access token is valid
- [ ] Test HubSpot integration connectivity
- [ ] Ensure OpenAI API key has sufficient credits
- [ ] Deploy Snowflake Cortex functions

### Deployment Steps
1. [ ] Deploy backend changes to staging
2. [ ] Run integration tests on staging
3. [ ] Verify real data flow in staging
4. [ ] Deploy to production with feature flag
5. [ ] Gradually enable for users

### Post-Deployment
- [ ] Monitor API response times
- [ ] Check error rates in logs
- [ ] Verify data freshness
- [ ] Confirm cost within budget
- [ ] Gather user feedback

## Success Criteria

1. **Data Availability**
   - Sales queries return actual HubSpot deals
   - Call analysis shows real Gong transcripts
   - Analytics reflect current business metrics

2. **Performance**
   - API response time < 2 seconds
   - Snowflake query time < 500ms
   - LLM synthesis < 3 seconds

3. **Quality**
   - No mock data indicators in responses
   - Accurate business insights
   - Relevant recommendations

## Risk Mitigation

1. **Gradual Rollout**
   - Use feature flags to control activation
   - Start with read-only queries
   - Monitor closely during initial phase

2. **Fallback Strategy**
   - Keep mock data as fallback option
   - Implement circuit breakers
   - Clear error messages when data unavailable

3. **Cost Management**
   - Set up usage alerts
   - Implement caching layer
   - Optimize query patterns

## Conclusion

This immediate action plan transforms Sophia AI from a mock data demonstration to a production-ready business intelligence platform. By systematically enabling each data source and service, we ensure a reliable transition to real-time, actionable insights for Pay Ready's CEO.
