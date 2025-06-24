"""
Comprehensive Unit Tests for Gong Snowflake Integration

Tests cover:
- ETL script functionality
- Snowflake connector operations
- Agent hybrid logic
- Error handling and fallbacks
- Configuration management
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from datetime import datetime, timedelta
import json
import uuid

# Import modules under test
from backend.etl.gong.ingest_gong_data import (
    GongAPIClient,
    SnowflakeGongLoader,
    GongDataIngestionOrchestrator,
    SyncMode,
    IngestionState
)
from backend.utils.snowflake_gong_connector import (
    SnowflakeGongConnector,
    get_gong_connector
)
from backend.utils.snowflake_cortex_service import (
    analyze_gong_call_sentiment,
    summarize_gong_call_with_context,
    find_similar_gong_calls,
    get_gong_coaching_insights
)
from backend.agents.specialized.sales_coach_agent import (
    SalesCoachAgent,
    CoachingInsight
)
from backend.agents.specialized.call_analysis_agent import (
    CallAnalysisAgent,
    CallPriority
)


class TestGongAPIClient:
    """Test Gong API client functionality"""
    
    @pytest.fixture
    def api_client(self):
        with patch('backend.core.auto_esc_config.config') as mock_config:
            mock_config.get.side_effect = lambda key, default=None: {
                'gong_access_key': 'test_key',
                'gong_access_key_secret': 'test_secret'
            }.get(key, default)
            return GongAPIClient()
    
    @pytest.mark.asyncio
    async def test_api_client_initialization(self, api_client):
        """Test API client initialization with credentials"""
        assert api_client.access_key == 'test_key'
        assert api_client.access_key_secret == 'test_secret'
        assert api_client.base_url == "https://api.gong.io/v2"
        assert api_client.rate_limit_delay == 1.0
    
    @pytest.mark.asyncio
    async def test_get_calls_success(self, api_client):
        """Test successful calls retrieval"""
        mock_response_data = {
            "calls": [
                {
                    "id": "call_123",
                    "title": "Demo Call",
                    "started": "2024-01-15T14:30:00Z",
                    "duration": 1800
                }
            ],
            "records": {"totalRecords": 1}
        }
        
        with patch('aiohttp.ClientSession') as mock_session:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json.return_value = mock_response_data
            mock_response.raise_for_status.return_value = None
            
            mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = mock_response
            
            async with api_client as client:
                result = await client.get_calls(
                    from_date=datetime(2024, 1, 1),
                    to_date=datetime(2024, 1, 31)
                )
                
                assert result == mock_response_data
                assert len(result["calls"]) == 1
                assert result["calls"][0]["id"] == "call_123"
    
    @pytest.mark.asyncio
    async def test_get_calls_rate_limit_handling(self, api_client):
        """Test rate limit handling with retry"""
        with patch('aiohttp.ClientSession') as mock_session, \
             patch('asyncio.sleep') as mock_sleep:
            
            # First response: rate limited
            mock_rate_limited_response = AsyncMock()
            mock_rate_limited_response.status = 429
            mock_rate_limited_response.headers.get.return_value = "60"
            
            # Second response: success
            mock_success_response = AsyncMock()
            mock_success_response.status = 200
            mock_success_response.json.return_value = {"calls": []}
            mock_success_response.raise_for_status.return_value = None
            
            mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.side_effect = [
                mock_rate_limited_response,
                mock_success_response
            ]
            
            async with api_client as client:
                result = await client.get_calls(
                    from_date=datetime(2024, 1, 1),
                    to_date=datetime(2024, 1, 31)
                )
                
                # Verify rate limit sleep was called
                mock_sleep.assert_called()
                assert result == {"calls": []}
    
    @pytest.mark.asyncio
    async def test_get_call_transcript_not_found(self, api_client):
        """Test transcript retrieval when not found"""
        with patch('aiohttp.ClientSession') as mock_session:
            mock_response = AsyncMock()
            mock_response.status = 404
            
            mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = mock_response
            
            async with api_client as client:
                result = await client.get_call_transcript("call_123")
                
                assert result["call_id"] == "call_123"
                assert result["transcript"] is None


class TestSnowflakeGongLoader:
    """Test Snowflake Gong loader functionality"""
    
    @pytest.fixture
    def snowflake_loader(self):
        with patch('backend.core.auto_esc_config.config') as mock_config:
            mock_config.get.side_effect = lambda key, default=None: {
                'snowflake_database': 'TEST_DB',
                'snowflake_schema': 'TEST_SCHEMA',
                'snowflake_warehouse': 'TEST_WH',
                'snowflake_user': 'test_user',
                'snowflake_password': 'test_pass',
                'snowflake_account': 'test_account'
            }.get(key, default)
            return SnowflakeGongLoader()
    
    @pytest.mark.asyncio
    async def test_loader_initialization(self, snowflake_loader):
        """Test Snowflake loader initialization"""
        with patch('snowflake.connector.connect') as mock_connect:
            mock_connection = Mock()
            mock_cursor = Mock()
            mock_connection.cursor.return_value = mock_cursor
            mock_connect.return_value = mock_connection
            
            await snowflake_loader.initialize()
            
            mock_connect.assert_called_once()
            assert snowflake_loader.connection == mock_connection
            assert snowflake_loader.database == 'TEST_DB'
            assert snowflake_loader.schema == 'TEST_SCHEMA'
    
    @pytest.mark.asyncio
    async def test_load_raw_calls(self, snowflake_loader):
        """Test loading raw call data"""
        calls_data = [
            {"id": "call_123", "title": "Test Call", "duration": 1800},
            {"id": "call_456", "title": "Demo Call", "duration": 2400}
        ]
        
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        snowflake_loader.connection = mock_connection
        
        with patch.object(snowflake_loader, '_ensure_raw_calls_table', return_value=None):
            result = await snowflake_loader.load_raw_calls(calls_data)
            
            assert result == 2
            mock_cursor.executemany.assert_called_once()
            mock_connection.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_last_sync_state_no_previous(self, snowflake_loader):
        """Test getting sync state when no previous state exists"""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = None
        mock_connection.cursor.return_value = mock_cursor
        snowflake_loader.connection = mock_connection
        
        state = await snowflake_loader.get_last_sync_state()
        
        assert isinstance(state, IngestionState)
        assert state.sync_mode == SyncMode.INCREMENTAL
        assert state.total_calls_processed == 0
        assert isinstance(state.last_sync_timestamp, datetime)


class TestSnowflakeGongConnector:
    """Test Snowflake Gong connector functionality"""
    
    @pytest.fixture
    def gong_connector(self):
        with patch('backend.core.auto_esc_config.config') as mock_config:
            mock_config.get.side_effect = lambda key, default=None: {
                'snowflake_database': 'TEST_DB',
                'snowflake_warehouse': 'TEST_WH'
            }.get(key, default)
            return SnowflakeGongConnector()
    
    @pytest.mark.asyncio
    async def test_get_calls_for_coaching(self, gong_connector):
        """Test getting calls that need coaching attention"""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_cursor.description = [
            ('CALL_ID',), ('CALL_TITLE',), ('SENTIMENT_SCORE',), ('COACHING_PRIORITY',)
        ]
        mock_cursor.fetchall.return_value = [
            ('call_123', 'Low Sentiment Call', 0.2, 'High Priority')
        ]
        mock_connection.cursor.return_value = mock_cursor
        gong_connector.connection = mock_connection
        gong_connector.initialized = True
        
        result = await gong_connector.get_calls_for_coaching(
            sales_rep="John Smith",
            date_range_days=7
        )
        
        assert len(result) == 1
        assert result[0]['CALL_ID'] == 'call_123'
        assert result[0]['SENTIMENT_SCORE'] == 0.2
        mock_cursor.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_call_analysis_data_not_found(self, gong_connector):
        """Test getting call analysis data when call not found"""
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = None
        mock_connection.cursor.return_value = mock_cursor
        gong_connector.connection = mock_connection
        gong_connector.initialized = True
        
        result = await gong_connector.get_call_analysis_data("nonexistent_call")
        
        assert result is None


class TestSnowflakeCortexService:
    """Test Snowflake Cortex service functionality"""
    
    @pytest.mark.asyncio
    async def test_analyze_gong_call_sentiment(self):
        """Test Gong call sentiment analysis"""
        with patch('backend.utils.snowflake_cortex_service.get_cortex_service') as mock_service:
            mock_cortex = AsyncMock()
            mock_cursor = Mock()
            mock_cursor.fetchone.return_value = (
                'call_123', 'Test Call', datetime.now(), 'John Smith', 'deal_456',
                0.7, 0.8, 5, 'positive segments', 'negative segments'
            )
            mock_cortex.connection.cursor.return_value = mock_cursor
            mock_service.return_value = mock_cortex
            
            result = await analyze_gong_call_sentiment('call_123')
            
            assert result['call_id'] == 'call_123'
            assert result['call_sentiment_score'] == 0.7
            assert result['ai_service'] == 'snowflake_cortex'
    
    @pytest.mark.asyncio
    async def test_find_similar_gong_calls(self):
        """Test finding similar Gong calls using vector search"""
        with patch('backend.utils.snowflake_cortex_service.get_cortex_service') as mock_service:
            mock_cortex = AsyncMock()
            mock_cursor = Mock()
            mock_cursor.fetchall.return_value = [
                ('call_123', 'Similar Call', 'John Smith', datetime.now(), 0.8, 
                 'Test Deal', 'Qualification', 50000, 'Test Company', 0.95, 0.85, 3, 'relevant content')
            ]
            mock_cortex.connection.cursor.return_value = mock_cursor
            mock_service.return_value = mock_cortex
            
            result = await find_similar_gong_calls(
                query_text="pricing discussion",
                top_k=5,
                similarity_threshold=0.7
            )
            
            assert len(result) == 1
            assert result[0]['call_id'] == 'call_123'
            assert result[0]['max_similarity'] == 0.95


class TestSalesCoachAgent:
    """Test Sales Coach Agent functionality"""
    
    @pytest.fixture
    def sales_coach_agent(self):
        return SalesCoachAgent()
    
    @pytest.mark.asyncio
    async def test_agent_initialization(self, sales_coach_agent):
        """Test agent initialization"""
        with patch('backend.core.auto_esc_config.config') as mock_config:
            mock_config.get.return_value = 'test_key'
            
            await sales_coach_agent.initialize()
            
            assert sales_coach_agent.agent_type == "sales_coach"
            assert sales_coach_agent.snowflake_enabled is True
    
    @pytest.mark.asyncio
    async def test_analyze_call_performance_snowflake_success(self, sales_coach_agent):
        """Test call performance analysis using Snowflake"""
        sales_coach_agent.snowflake_enabled = True
        
        # Mock Snowflake functions
        with patch('backend.agents.specialized.sales_coach_agent.analyze_gong_call_sentiment') as mock_sentiment, \
             patch('backend.agents.specialized.sales_coach_agent.summarize_gong_call_with_context') as mock_summary, \
             patch('backend.agents.specialized.sales_coach_agent.get_gong_connector') as mock_connector:
            
            mock_sentiment.return_value = {
                'call_sentiment_score': 0.8,
                'sentiment_category': 'Positive'
            }
            mock_summary.return_value = {
                'ai_summary': 'Great call with positive outcome'
            }
            
            mock_conn = AsyncMock()
            mock_conn.get_call_analysis_data.return_value = {
                'CALL_ID': 'call_123',
                'TALK_RATIO': 0.6,
                'SENTIMENT_SCORE': 0.8
            }
            mock_connector.return_value = mock_conn
            
            task = {"task_type": "analyze_call", "call_id": "call_123"}
            result = await sales_coach_agent.process_task(task)
            
            assert result['success'] is True
            assert result['data_source'] == 'snowflake_cortex'
            assert result['ai_enhanced'] is True
            assert result['call_id'] == 'call_123'
    
    @pytest.mark.asyncio
    async def test_analyze_call_performance_fallback(self, sales_coach_agent):
        """Test call performance analysis fallback to traditional method"""
        sales_coach_agent.snowflake_enabled = True
        sales_coach_agent.traditional_gong_client = Mock()
        
        # Mock Snowflake failure
        with patch('backend.agents.specialized.sales_coach_agent.analyze_gong_call_sentiment') as mock_sentiment:
            mock_sentiment.side_effect = Exception("Snowflake connection failed")
            
            task = {"task_type": "analyze_call", "call_id": "call_123"}
            result = await sales_coach_agent.process_task(task)
            
            assert result['success'] is True
            assert result['data_source'] == 'traditional_gong'
            assert result['ai_enhanced'] is False
    
    @pytest.mark.asyncio
    async def test_generate_rep_coaching(self, sales_coach_agent):
        """Test rep coaching generation"""
        sales_coach_agent.snowflake_enabled = True
        
        with patch('backend.agents.specialized.sales_coach_agent.get_gong_coaching_insights') as mock_insights, \
             patch('backend.agents.specialized.sales_coach_agent.get_gong_connector') as mock_connector:
            
            mock_insights.return_value = {
                'sales_rep': 'John Smith',
                'avg_sentiment': 0.6,
                'avg_talk_ratio': 0.5,
                'ai_coaching_recommendations': 'Focus on discovery questions'
            }
            
            mock_conn = AsyncMock()
            mock_conn.get_calls_for_coaching.return_value = []
            mock_conn.get_sales_rep_performance.return_value = {
                'performance_category': 'Good'
            }
            mock_connector.return_value = mock_conn
            
            task = {"task_type": "coach_rep", "sales_rep": "John Smith"}
            result = await sales_coach_agent.process_task(task)
            
            assert result['success'] is True
            assert result['sales_rep'] == 'John Smith'
            assert 'coaching_plan' in result
    
    @pytest.mark.asyncio
    async def test_real_time_coaching(self, sales_coach_agent):
        """Test real-time coaching suggestions"""
        call_data = {
            "sentiment_score": 0.2,  # Low sentiment
            "talk_ratio": 0.9,       # High talk ratio
            "duration_seconds": 1800
        }
        
        task = {
            "task_type": "real_time_coaching",
            "call_data": call_data,
            "context": {"deal_stage": "Qualification"}
        }
        
        result = await sales_coach_agent.process_task(task)
        
        assert result['success'] is True
        assert len(result['coaching_suggestions']) >= 2  # Should have sentiment and talk ratio suggestions
        
        # Check for sentiment coaching
        sentiment_suggestions = [s for s in result['coaching_suggestions'] if s['type'] == 'sentiment']
        assert len(sentiment_suggestions) == 1
        assert sentiment_suggestions[0]['priority'] == 'high'
        
        # Check for talk ratio coaching
        talk_ratio_suggestions = [s for s in result['coaching_suggestions'] if s['type'] == 'talk_ratio']
        assert len(talk_ratio_suggestions) == 1


class TestCallAnalysisAgent:
    """Test Call Analysis Agent functionality"""
    
    @pytest.fixture
    def call_analysis_agent(self):
        return CallAnalysisAgent()
    
    @pytest.mark.asyncio
    async def test_agent_initialization(self, call_analysis_agent):
        """Test agent initialization"""
        with patch('backend.core.auto_esc_config.config') as mock_config:
            mock_config.get.return_value = 'test_key'
            
            await call_analysis_agent.initialize()
            
            assert call_analysis_agent.agent_type == "call_analysis"
            assert call_analysis_agent.snowflake_enabled is True
    
    @pytest.mark.asyncio
    async def test_analyze_individual_call(self, call_analysis_agent):
        """Test individual call analysis"""
        call_analysis_agent.snowflake_enabled = True
        
        with patch('backend.agents.specialized.call_analysis_agent.get_gong_connector') as mock_connector, \
             patch('backend.agents.specialized.call_analysis_agent.analyze_gong_call_sentiment') as mock_sentiment, \
             patch('backend.agents.specialized.call_analysis_agent.summarize_gong_call_with_context') as mock_summary:
            
            # Mock call details
            mock_conn = AsyncMock()
            mock_conn.get_call_analysis_data.return_value = {
                'CALL_ID': 'call_123',
                'CALL_TITLE': 'Test Call',
                'SENTIMENT_SCORE': 0.7,
                'TALK_RATIO': 0.6,
                'DEAL_AMOUNT': 50000
            }
            mock_connector.return_value = mock_conn
            
            # Mock AI analysis
            mock_sentiment.return_value = {
                'call_sentiment_score': 0.7,
                'sentiment_category': 'Positive'
            }
            mock_summary.return_value = {
                'ai_summary': 'Successful discovery call'
            }
            
            task = {"task_type": "analyze_call", "call_id": "call_123"}
            result = await call_analysis_agent.process_task(task)
            
            assert result['success'] is True
            assert result['call_analysis']['call_id'] == 'call_123'
            assert result['call_analysis']['ai_enhanced'] is True
            assert result['call_analysis']['overall_score'] > 0
    
    @pytest.mark.asyncio
    async def test_batch_call_analysis(self, call_analysis_agent):
        """Test batch call analysis"""
        call_analysis_agent.snowflake_enabled = True
        
        with patch('backend.agents.specialized.call_analysis_agent.get_gong_connector') as mock_connector:
            mock_conn = AsyncMock()
            mock_conn.get_calls_for_coaching.return_value = [
                {'CALL_ID': 'call_123'},
                {'CALL_ID': 'call_456'}
            ]
            mock_connector.return_value = mock_conn
            
            # Mock individual analysis results
            with patch.object(call_analysis_agent, '_analyze_individual_call') as mock_analyze:
                mock_analyze.return_value = {
                    'success': True,
                    'call_analysis': {
                        'overall_score': 75.0,
                        'priority': 'medium',
                        'sentiment_analysis': {'call_sentiment_score': 0.6}
                    }
                }
                
                task = {
                    "task_type": "batch_analysis",
                    "sales_rep": "John Smith",
                    "limit": 10
                }
                result = await call_analysis_agent.process_task(task)
                
                assert result['success'] is True
                assert result['batch_size'] == 2
                assert result['successful_analyses'] == 2
                assert 'batch_insights' in result
    
    def test_calculate_call_score(self, call_analysis_agent):
        """Test call score calculation"""
        call_details = {
            'TALK_RATIO': 0.5,
            'INTERACTIVITY_SCORE': 0.8,
            'CALL_DURATION_SECONDS': 1800
        }
        sentiment_analysis = {
            'call_sentiment_score': 0.7
        }
        
        score = asyncio.run(call_analysis_agent._calculate_call_score(call_details, sentiment_analysis))
        
        assert 0 <= score <= 100
        assert isinstance(score, float)
    
    def test_determine_call_priority(self, call_analysis_agent):
        """Test call priority determination"""
        # Test critical priority
        priority = call_analysis_agent._determine_call_priority(
            overall_score=25.0,
            sentiment_analysis={'call_sentiment_score': -0.6}
        )
        assert priority == CallPriority.CRITICAL
        
        # Test high priority
        priority = call_analysis_agent._determine_call_priority(
            overall_score=45.0,
            sentiment_analysis={'call_sentiment_score': -0.2}
        )
        assert priority == CallPriority.HIGH
        
        # Test low priority
        priority = call_analysis_agent._determine_call_priority(
            overall_score=85.0,
            sentiment_analysis={'call_sentiment_score': 0.8}
        )
        assert priority == CallPriority.LOW


class TestIntegrationScenarios:
    """Test end-to-end integration scenarios"""
    
    @pytest.mark.asyncio
    async def test_full_etl_to_agent_workflow(self):
        """Test complete workflow from ETL to agent processing"""
        # This would be an integration test that:
        # 1. Ingests sample Gong data
        # 2. Transforms it in Snowflake
        # 3. Processes with Cortex AI
        # 4. Retrieves via agents
        
        # Mock the entire pipeline
        with patch('backend.etl.gong.ingest_gong_data.GongAPIClient') as mock_gong_client, \
             patch('backend.etl.gong.ingest_gong_data.SnowflakeGongLoader') as mock_loader, \
             patch('backend.agents.specialized.sales_coach_agent.get_gong_connector') as mock_connector:
            
            # Mock ETL process
            mock_gong = AsyncMock()
            mock_gong.get_calls.return_value = {
                "calls": [{"id": "call_123", "title": "Test Call"}]
            }
            mock_gong_client.return_value.__aenter__.return_value = mock_gong
            
            mock_sf_loader = AsyncMock()
            mock_sf_loader.load_raw_calls.return_value = 1
            mock_loader.return_value = mock_sf_loader
            
            # Mock agent processing
            mock_conn = AsyncMock()
            mock_conn.get_call_analysis_data.return_value = {
                'CALL_ID': 'call_123',
                'SENTIMENT_SCORE': 0.8
            }
            mock_connector.return_value = mock_conn
            
            # Test orchestrator
            orchestrator = GongDataIngestionOrchestrator()
            etl_result = await orchestrator.run_ingestion(
                from_date=datetime.now() - timedelta(days=1),
                to_date=datetime.now(),
                include_transcripts=False
            )
            
            assert etl_result['success'] is True
            assert etl_result['calls_processed'] >= 0
    
    @pytest.mark.asyncio
    async def test_agent_error_handling_and_fallback(self):
        """Test agent error handling and fallback mechanisms"""
        sales_coach = SalesCoachAgent()
        sales_coach.snowflake_enabled = True
        sales_coach.traditional_gong_client = Mock()
        
        # Test Snowflake failure with successful fallback
        with patch('backend.agents.specialized.sales_coach_agent.analyze_gong_call_sentiment') as mock_sentiment:
            mock_sentiment.side_effect = Exception("Snowflake unavailable")
            
            task = {"task_type": "analyze_call", "call_id": "call_123"}
            result = await sales_coach.process_task(task)
            
            # Should fall back to traditional method
            assert result['success'] is True
            assert result['data_source'] == 'traditional_gong'
            assert result['ai_enhanced'] is False
    
    @pytest.mark.asyncio
    async def test_configuration_validation(self):
        """Test configuration validation and error handling"""
        # Test missing Gong credentials
        with patch('backend.core.auto_esc_config.config') as mock_config:
            mock_config.get.return_value = None
            
            with pytest.raises(ValueError, match="Gong API credentials not found"):
                client = GongAPIClient()
                async with client:
                    pass
        
        # Test missing Snowflake credentials
        with patch('backend.core.auto_esc_config.config') as mock_config:
            mock_config.get.return_value = None
            
            loader = SnowflakeGongLoader()
            with pytest.raises(Exception):  # Should fail on Snowflake connection
                await loader.initialize()


class TestPerformanceAndScaling:
    """Test performance and scaling considerations"""
    
    @pytest.mark.asyncio
    async def test_batch_processing_performance(self):
        """Test batch processing performance"""
        # Test that batch processing handles large datasets efficiently
        call_analysis_agent = CallAnalysisAgent()
        
        # Mock large batch of calls
        large_call_list = [f"call_{i}" for i in range(100)]
        
        with patch('backend.agents.specialized.call_analysis_agent.get_gong_connector') as mock_connector:
            mock_conn = AsyncMock()
            mock_conn.get_calls_for_coaching.return_value = [
                {'CALL_ID': call_id} for call_id in large_call_list
            ]
            mock_connector.return_value = mock_conn
            
            # Mock individual analysis to be fast
            with patch.object(call_analysis_agent, '_analyze_individual_call') as mock_analyze:
                mock_analyze.return_value = {
                    'success': True,
                    'call_analysis': {'overall_score': 75.0, 'priority': 'medium', 'sentiment_analysis': {'call_sentiment_score': 0.6}}
                }
                
                task = {
                    "task_type": "batch_analysis",
                    "sales_rep": "John Smith",
                    "limit": 100
                }
                
                start_time = datetime.now()
                result = await call_analysis_agent.process_task(task)
                end_time = datetime.now()
                
                # Should complete in reasonable time (less than 10 seconds for 100 calls)
                processing_time = (end_time - start_time).total_seconds()
                assert processing_time < 10.0
                assert result['success'] is True
    
    @pytest.mark.asyncio
    async def test_connection_pooling_and_resource_management(self):
        """Test connection pooling and resource management"""
        connector = SnowflakeGongConnector()
        
        # Test that multiple operations reuse connection
        with patch('snowflake.connector.connect') as mock_connect:
            mock_connection = Mock()
            mock_connect.return_value = mock_connection
            
            await connector.initialize()
            
            # Multiple operations should reuse the same connection
            assert connector.connection == mock_connection
            assert connector.initialized is True
            
            # Test connection cleanup
            await connector.close()
            assert connector.initialized is False


# Test fixtures for common mock data
@pytest.fixture
def sample_call_data():
    """Sample call data for testing"""
    return {
        "id": "call_123",
        "title": "Discovery Call - Acme Corp",
        "started": "2024-01-15T14:30:00Z",
        "duration": 1800,
        "direction": "Outbound",
        "primaryUserId": "user_456",
        "customData": {
            "hubspotDealId": "deal_789",
            "hubspotContactId": "contact_123",
            "dealStage": "Qualification",
            "dealValue": 50000
        },
        "analytics": {
            "talkRatio": 0.6,
            "interactivity": 0.8,
            "questionsAsked": 5
        }
    }

@pytest.fixture
def sample_transcript_data():
    """Sample transcript data for testing"""
    return {
        "call_id": "call_123",
        "transcript": {
            "segments": [
                {
                    "speakerName": "John Smith",
                    "speakerEmail": "john@company.com",
                    "text": "Thanks for taking the time to meet with us today.",
                    "startTime": 0,
                    "endTime": 3
                },
                {
                    "speakerName": "Jane Doe",
                    "speakerEmail": "jane@prospect.com",
                    "text": "Happy to be here. I'm excited to learn more about your solution.",
                    "startTime": 3,
                    "endTime": 8
                }
            ]
        }
    }

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 