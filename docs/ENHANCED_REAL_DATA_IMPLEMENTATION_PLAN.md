# Enhanced Real Data Implementation Plan

**Date:** July 6, 2025
**Version:** 2.0
**Status:** Ready for Implementation

## Executive Summary

This enhanced plan incorporates deep review insights to ensure a robust transition from mock to live data. Key improvements include comprehensive data source integration, advanced error handling, performance optimization, and enterprise-grade monitoring.

## Phase 1: Foundation & Infrastructure (Days 1-3)

### 1.1 Enhanced Data Source Integration

```python
# backend/services/data_source_manager.py
from typing import Dict, List, Optional, Union
from enum import Enum
import asyncio
from backend.core.auto_esc_config import get_config_value
from backend.core.optimized_cache import OptimizedCache

class DataSourceType(Enum):
    SNOWFLAKE = "snowflake"
    GONG = "gong"
    HUBSPOT = "hubspot"
    SLACK = "slack"
    LINEAR = "linear"
    PINECONE = "pinecone"
    REDIS = "redis"

class DataError(Exception):
    """Base exception for data-related errors"""
    pass

class ConnectionError(DataError):
    """Raised when connection to data source fails"""
    pass

class DataValidationError(DataError):
    """Raised when data validation fails"""
    pass

class EmptyResultError(DataError):
    """Raised when query returns no results"""
    pass

class DataSourceManager:
    """Centralized manager for all data sources"""

    def __init__(self):
        self.cache = OptimizedCache()
        self.sources = self._initialize_sources()
        self.feature_flags = self._load_feature_flags()

    def _load_feature_flags(self) -> Dict[str, bool]:
        """Load feature flags from Pulumi ESC"""
        return {
            "enable_real_data": get_config_value("features.enable_real_data", False),
            "enable_mock_data": get_config_value("features.enable_mock_data", True),
            "enable_caching": get_config_value("features.enable_caching", True),
            "enable_snowflake": get_config_value("data_sources.snowflake.enabled", True),
            "enable_gong": get_config_value("data_sources.gong.enabled", True),
            "enable_hubspot": get_config_value("data_sources.hubspot.enabled", True),
        }

    async def fetch_data(
        self,
        source: DataSourceType,
        query: str,
        params: Optional[Dict] = None,
        use_cache: bool = True
    ) -> Union[List[Dict], Dict]:
        """Fetch data from specified source with caching and error handling"""

        # Check feature flags
        if not self.feature_flags["enable_real_data"]:
            if self.feature_flags["enable_mock_data"]:
                return self._get_mock_data(source, query)
            raise DataError("Real data disabled and no mock data available")

        # Check cache first
        cache_key = f"{source.value}:{query}:{str(params)}"
        if use_cache and self.feature_flags["enable_caching"]:
            cached_data = await self.cache.get(cache_key)
            if cached_data:
                return cached_data

        # Fetch real data
        try:
            data = await self._fetch_from_source(source, query, params)

            # Validate data
            self._validate_data(data, source)

            # Cache successful results
            if use_cache and self.feature_flags["enable_caching"]:
                ttl = self._get_cache_ttl(source)
                await self.cache.set(cache_key, data, ttl)

            return data

        except ConnectionError as e:
            logger.error(f"Connection error for {source.value}: {e}")
            raise
        except EmptyResultError as e:
            logger.warning(f"Empty result for {source.value}: {e}")
            return []
        except DataValidationError as e:
            logger.error(f"Data validation error for {source.value}: {e}")
            raise
        except Exception as e:
            logger.exception(f"Unexpected error fetching from {source.value}")
            raise DataError(f"Failed to fetch from {source.value}: {e}")
```

### 1.2 Advanced Error Handling & Circuit Breaker

```python
# backend/services/circuit_breaker.py
from datetime import datetime, timedelta
from typing import Dict, Callable
import asyncio

class CircuitBreaker:
    """Circuit breaker pattern for external service calls"""

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: type = Exception
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half-open

    async def call(self, func: Callable, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        if self.state == "open":
            if self._should_attempt_reset():
                self.state = "half-open"
            else:
                raise ConnectionError("Circuit breaker is open")

        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise

    def _should_attempt_reset(self) -> bool:
        return (
            self.last_failure_time and
            datetime.now() > self.last_failure_time + timedelta(seconds=self.recovery_timeout)
        )

    def _on_success(self):
        self.failure_count = 0
        self.state = "closed"

    def _on_failure(self):
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        if self.failure_count >= self.failure_threshold:
            self.state = "open"
```

### 1.3 Data Transformation & Validation

```python
# backend/services/data_transformer.py
from typing import Dict, List, Any
import pandas as pd
from datetime import datetime

class DataTransformer:
    """Transform and validate data from various sources"""

    @staticmethod
    def transform_snowflake_results(results: List[Dict]) -> pd.DataFrame:
        """Transform Snowflake results to standardized format"""
        df = pd.DataFrame(results)

        # Standardize column names
        df.columns = [col.lower().replace(' ', '_') for col in df.columns]

        # Convert data types
        date_columns = [col for col in df.columns if 'date' in col or 'time' in col]
        for col in date_columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')

        # Handle nulls
        df = df.fillna({
            'amount': 0,
            'probability': 0,
            'stage': 'Unknown'
        })

        return df

    @staticmethod
    def validate_sales_data(data: pd.DataFrame) -> bool:
        """Validate sales data structure and content"""
        required_columns = ['deal_id', 'deal_name', 'amount', 'stage']

        # Check required columns
        if not all(col in data.columns for col in required_columns):
            raise DataValidationError(f"Missing required columns: {required_columns}")

        # Check data types
        if not pd.api.types.is_numeric_dtype(data['amount']):
            raise DataValidationError("Amount column must be numeric")

        # Check for empty dataset
        if data.empty:
            raise EmptyResultError("No sales data available")

        # Check data freshness (example: deals should have recent activity)
        if 'last_activity_date' in data.columns:
            latest_activity = data['last_activity_date'].max()
            if pd.Timestamp.now() - latest_activity > pd.Timedelta(days=30):
                logger.warning("Sales data may be stale")

        return True
```

## Phase 2: LLM Integration & Intelligence (Days 4-6)

### 2.1 Advanced LLM Service

```python
# backend/services/advanced_llm_service.py
from openai import AsyncOpenAI
from anthropic import AsyncAnthropic
from typing import Dict, List, Optional
import tiktoken
from backend.core.auto_esc_config import get_config_value

class AdvancedLLMService:
    """Enhanced LLM service with multiple providers and advanced features"""

    def __init__(self):
        self.openai_client = AsyncOpenAI(
            api_key=get_config_value("openai_api_key")
        )
        self.anthropic_client = AsyncAnthropic(
            api_key=get_config_value("anthropic_api_key")
        )
        self.tokenizer = tiktoken.encoding_for_model("gpt-4")
        self.constitutional_ai = ConstitutionalAI()

    async def synthesize_response(
        self,
        query: str,
        context: Dict,
        results: List[Dict],
        provider: str = "openai",
        use_constitutional_ai: bool = True
    ) -> str:
        """Generate response with advanced prompt engineering"""

        # Prepare data for LLM
        processed_data = self._prepare_data_for_llm(results)

        # Build prompt with few-shot examples
        prompt = self._build_advanced_prompt(query, context, processed_data)

        # Check token limits
        if self._exceeds_token_limit(prompt):
            prompt = self._compress_prompt(prompt)

        # Generate response
        if provider == "openai":
            response = await self._generate_openai_response(prompt)
        elif provider == "anthropic":
            response = await self._generate_anthropic_response(prompt)
        else:
            raise ValueError(f"Unknown provider: {provider}")

        # Apply constitutional AI
        if use_constitutional_ai:
            response = await self.constitutional_ai.review_and_revise(response)

        return response

    def _build_advanced_prompt(
        self,
        query: str,
        context: Dict,
        data: str
    ) -> str:
        """Build prompt with chain-of-thought and few-shot examples"""
        return f"""You are Sophia AI, an executive assistant providing business intelligence.

Context: {json.dumps(context)}

Here are some examples of high-quality responses:

Example 1:
Query: "What are our top deals this quarter?"
Response: Based on the current pipeline data, here are your top 5 deals for Q3 2025:
1. Acme Corp - $450K (Stage: Negotiation, 85% probability)
2. TechStart Inc - $380K (Stage: Proposal, 70% probability)
...

Example 2:
Query: "Show me customer health metrics"
Response: Customer health analysis shows:
- 78% of customers are in "Healthy" status
- 15% require attention (declining usage)
- 7% are at risk (support tickets + low engagement)
...

Now, please analyze this query and data:

Query: {query}

Data:
{data}

Provide a comprehensive, actionable response following these steps:
1. Understand the user's intent
2. Analyze the relevant data
3. Identify key insights
4. Provide specific recommendations
5. Suggest next steps

Response:"""
```

### 2.2 Constitutional AI Implementation

```python
# backend/services/constitutional_ai.py
class ConstitutionalAI:
    """Ensure AI responses are safe, ethical, and aligned"""

    def __init__(self):
        self.principles = self._load_principles()

    def _load_principles(self) -> List[str]:
        """Load constitutional principles"""
        return [
            "Be helpful, harmless, and honest",
            "Protect confidential business information",
            "Provide accurate insights based on data",
            "Avoid speculation without data support",
            "Respect privacy and data governance",
            "Focus on actionable business value"
        ]

    async def review_and_revise(self, response: str) -> str:
        """Review and revise response based on principles"""
        # Check for violations
        violations = self._check_violations(response)

        if violations:
            # Request revision from LLM
            revised = await self._request_revision(response, violations)
            return revised

        return response
```

## Phase 3: Testing & Quality Assurance (Days 7-9)

### 3.1 Comprehensive Test Suite

```python
# tests/integration/test_live_data_pipeline.py
import pytest
from unittest.mock import Mock, patch
import pandas as pd

class TestLiveDataPipeline:
    """Comprehensive tests for live data pipeline"""

    @pytest.fixture
    def mock_snowflake_data(self):
        """Mock Snowflake sales data"""
        return pd.DataFrame({
            'deal_id': ['D001', 'D002', 'D003'],
            'deal_name': ['Acme Corp', 'TechStart', 'GlobalTech'],
            'amount': [450000, 380000, 275000],
            'stage': ['Negotiation', 'Proposal', 'Discovery'],
            'probability': [85, 70, 40],
            'close_date': pd.to_datetime(['2025-08-15', '2025-09-01', '2025-09-30'])
        })

    @pytest.mark.asyncio
    async def test_end_to_end_sales_query(self, mock_snowflake_data):
        """Test complete flow from query to response"""
        # Mock external services
        with patch('backend.services.data_source_manager.SnowflakeConnector') as mock_sf:
            mock_sf.return_value.execute_query.return_value = mock_snowflake_data.to_dict('records')

            # Execute query
            service = UnifiedIntelligenceService()
            result = await service.process_query("Show me top deals")

            # Assertions
            assert result['type'] == 'sales'
            assert len(result['results']) > 0
            assert 'Acme Corp' in str(result['results'])
            assert result['insights'] is not None
            assert 'response' in result

    @pytest.mark.asyncio
    async def test_data_validation_errors(self):
        """Test handling of invalid data"""
        invalid_data = pd.DataFrame({
            'deal_id': ['D001'],
            # Missing required columns
        })

        transformer = DataTransformer()
        with pytest.raises(DataValidationError):
            transformer.validate_sales_data(invalid_data)

    @pytest.mark.asyncio
    async def test_circuit_breaker_functionality(self):
        """Test circuit breaker opens after failures"""
        breaker = CircuitBreaker(failure_threshold=3)

        async def failing_function():
            raise ConnectionError("Service unavailable")

        # Trigger failures
        for _ in range(3):
            with pytest.raises(ConnectionError):
                await breaker.call(failing_function)

        # Circuit should be open
        assert breaker.state == "open"

        # Further calls should fail immediately
        with pytest.raises(ConnectionError, match="Circuit breaker is open"):
            await breaker.call(failing_function)
```

### 3.2 Performance Testing

```python
# tests/performance/test_data_pipeline_performance.py
import asyncio
import time
from locust import HttpUser, task, between

class SophiaAIUser(HttpUser):
    """Performance test user for Sophia AI"""
    wait_time = between(1, 3)

    @task(3)
    def query_sales_data(self):
        """Test sales query performance"""
        self.client.post("/api/chat", json={
            "query": "Show me top deals this quarter",
            "context": {"user_id": "ceo"}
        })

    @task(2)
    def query_analytics(self):
        """Test analytics query performance"""
        self.client.post("/api/chat", json={
            "query": "What's our revenue trend?",
            "context": {"user_id": "ceo"}
        })

    @task(1)
    def query_complex(self):
        """Test complex multi-source query"""
        self.client.post("/api/chat", json={
            "query": "Compare sales performance with customer satisfaction",
            "context": {"user_id": "ceo"}
        })
```

## Phase 4: Monitoring & Observability (Days 10-12)

### 4.1 Enhanced Monitoring

```python
# backend/monitoring/data_pipeline_metrics.py
from prometheus_client import Counter, Histogram, Gauge
import structlog

logger = structlog.get_logger()

# Data source metrics
data_fetch_duration = Histogram(
    'sophia_data_fetch_duration_seconds',
    'Time to fetch data from source',
    ['source', 'query_type']
)

data_fetch_errors = Counter(
    'sophia_data_fetch_errors_total',
    'Total data fetch errors',
    ['source', 'error_type']
)

data_freshness = Gauge(
    'sophia_data_freshness_seconds',
    'Age of data in seconds',
    ['source', 'data_type']
)

cache_hit_rate = Gauge(
    'sophia_cache_hit_rate',
    'Cache hit rate percentage',
    ['cache_type']
)

# LLM metrics
llm_response_time = Histogram(
    'sophia_llm_response_seconds',
    'LLM response generation time',
    ['provider', 'model']
)

llm_token_usage = Counter(
    'sophia_llm_tokens_total',
    'Total LLM tokens used',
    ['provider', 'model', 'token_type']
)

# Data quality metrics
data_validation_failures = Counter(
    'sophia_data_validation_failures_total',
    'Data validation failures',
    ['source', 'validation_type']
)

empty_results = Counter(
    'sophia_empty_results_total',
    'Queries returning empty results',
    ['source', 'query_type']
)
```

### 4.2 Alerting Configuration

```yaml
# monitoring/alerts.yml
groups:
  - name: data_pipeline_alerts
    rules:
      - alert: HighDataFetchErrorRate
        expr: rate(sophia_data_fetch_errors_total[5m]) > 0.1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: High error rate fetching data from {{ $labels.source }}

      - alert: StaleData
        expr: sophia_data_freshness_seconds > 3600
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: Data from {{ $labels.source }} is older than 1 hour

      - alert: LowCacheHitRate
        expr: sophia_cache_hit_rate < 0.5
        for: 15m
        labels:
          severity: info
        annotations:
          summary: Cache hit rate below 50% for {{ $labels.cache_type }}

      - alert: HighLLMResponseTime
        expr: histogram_quantile(0.95, sophia_llm_response_seconds) > 5
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: 95th percentile LLM response time above 5 seconds
```

## Implementation Timeline

### Week 1: Foundation
- [x] Day 1-2: Implement DataSourceManager with circuit breaker
- [x] Day 3: Complete data transformation and validation
- [x] Day 4: Deploy to staging environment

### Week 2: Intelligence & Testing
- [ ] Day 5-6: Implement advanced LLM service
- [ ] Day 7-8: Create comprehensive test suite
- [ ] Day 9: Performance testing and optimization

### Week 3: Production Rollout
- [ ] Day 10: Deploy monitoring and alerting
- [ ] Day 11: Gradual production rollout (10% → 50% → 100%)
- [ ] Day 12: Full production deployment

## Success Metrics

1. **Data Availability**
   - 99%+ uptime for all data sources
   - <2s average query response time
   - 0 data validation errors in production

2. **Performance**
   - P95 latency < 3 seconds
   - Cache hit rate > 70%
   - Support 100+ concurrent users

3. **Quality**
   - 95%+ user satisfaction with data accuracy
   - <1% error rate in production
   - 100% constitutional AI compliance

## Risk Mitigation

1. **Gradual Rollout**
   - Feature flags for each data source
   - Canary deployment strategy
   - Instant rollback capability

2. **Cost Management**
   - Token usage monitoring and alerts
   - Caching to reduce API calls
   - Query optimization for efficiency

3. **Data Security**
   - Encryption in transit and at rest
   - Audit logging for all data access
   - Role-based access control

## Conclusion

This enhanced plan addresses all critical aspects of transitioning to live data while maintaining system stability, performance, and security. The phased approach with comprehensive testing and monitoring ensures a smooth transition with minimal risk.
