"""
Phase 2 Integration Tests

Comprehensive test suite for Phase 2 enhancements including:
- Enhanced LangGraph orchestration
- Unified chat service
- Cost engineering and model routing
- Enhanced Snowflake Cortex integration
- End-to-end workflow testing
"""

import asyncio
import json
import uuid
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.services.cost_engineering_service import (
    CostOptimizationStrategy,
    ModelTier,
    TaskRequest,
    cost_engineering_service,
)
from backend.services.enhanced_snowflake_cortex_service import (
    AIFunctionType,
    CortexSearchConfig,
    CortexSearchMode,
    DataPipelineConfig,
    DataProcessingMode,
    enhanced_cortex_service,
)
from backend.services.sophia_universal_chat_service import (
    ChatMessageType,
    IntentType,
    universal_chat_service,
)

# Import Phase 2 components
from backend.workflows.enhanced_langgraph_orchestration import (
    HumanCheckpoint,
    TaskComplexity,
    WorkflowStatus,
    enhanced_orchestrator,
)


class TestEnhancedLangGraphOrchestration:
    """Test suite for enhanced LangGraph orchestration"""

    @pytest.fixture
    async def orchestrator(self):
        """Initialize orchestrator for testing"""
        # Mock the services to avoid actual connections
        with (
            patch(
                "backend.workflows.enhanced_langgraph_orchestration.SnowflakeCortexService"
            ) as mock_cortex,
            patch(
                "backend.workflows.enhanced_langgraph_orchestration.EnhancedAiMemoryMCPServer"
            ) as mock_memory,
        ):

            mock_cortex_instance = AsyncMock()
            mock_cortex.return_value = mock_cortex_instance

            mock_memory_instance = AsyncMock()
            mock_memory.return_value = mock_memory_instance

            await enhanced_orchestrator.initialize()
            yield enhanced_orchestrator

    @pytest.mark.asyncio
    async def test_workflow_creation_from_natural_language(self, orchestrator):
        """Test creating workflows from natural language"""
        user_request = (
            "Create a workflow to analyze customer feedback and generate insights"
        )
        user_id = "test_user_123"
        session_id = "test_session_456"

        # Mock Cortex response
        with patch.object(
            orchestrator.cortex_service, "complete_text_with_cortex"
        ) as mock_cortex:
            mock_cortex.return_value = json.dumps(
                {
                    "type": "data_analysis",
                    "required_data_sources": ["customer_feedback"],
                    "processing_steps": ["sentiment_analysis", "topic_extraction"],
                    "human_approval_points": ["final_review"],
                    "expected_outputs": ["insights_report"],
                }
            )

            workflow_id = await orchestrator.create_workflow_from_natural_language(
                user_request=user_request, user_id=user_id, session_id=session_id
            )

            assert workflow_id is not None
            assert workflow_id in orchestrator.active_workflows

            workflow_state = orchestrator.active_workflows[workflow_id]
            assert workflow_state["user_id"] == user_id
            assert workflow_state["session_id"] == session_id
            assert workflow_state["user_request"] == user_request
            assert workflow_state["status"] == WorkflowStatus.PENDING

    @pytest.mark.asyncio
    async def test_parallel_task_execution(self, orchestrator):
        """Test parallel task execution (Map-Reduce pattern)"""
        from backend.workflows.enhanced_langgraph_orchestration import ParallelTask

        # Create test workflow
        workflow_id = str(uuid.uuid4())
        orchestrator.active_workflows[workflow_id] = {
            "workflow_id": workflow_id,
            "user_id": "test_user",
            "parallel_results": {},
            "parallel_errors": {},
            "node_timings": {},
        }

        # Define parallel tasks
        tasks = [
            ParallelTask(
                task_id="task_1",
                task_name="Data Collection",
                task_function="hubspot_data",
                timeout_minutes=5,
            ),
            ParallelTask(
                task_id="task_2",
                task_name="Call Analysis",
                task_function="gong_data",
                timeout_minutes=5,
            ),
        ]

        # Mock task execution
        with patch.object(orchestrator, "_execute_single_task") as mock_execute:
            mock_execute.side_effect = [
                {"source": "hubspot", "data": "test_data_1"},
                {"source": "gong", "data": "test_data_2"},
            ]

            result = await orchestrator.execute_parallel_tasks(workflow_id, tasks)

            assert "successful_results" in result
            assert len(result["successful_results"]) == 2
            assert "task_1" in result["successful_results"]
            assert "task_2" in result["successful_results"]

    @pytest.mark.asyncio
    async def test_human_checkpoint_creation(self, orchestrator):
        """Test human-in-the-loop checkpoint creation"""
        workflow_id = str(uuid.uuid4())
        orchestrator.active_workflows[workflow_id] = {
            "workflow_id": workflow_id,
            "user_id": "test_user",
            "status": WorkflowStatus.RUNNING,
            "pending_checkpoints": [],
        }

        checkpoint = HumanCheckpoint(
            checkpoint_id=str(uuid.uuid4()),
            title="Review Analysis Results",
            description="Please review the generated insights before proceeding",
            required_approval=True,
            timeout_minutes=30,
            context_data={"analysis_results": "test_results"},
        )

        # Mock Cortex for prompt generation
        with patch.object(
            orchestrator.cortex_service, "complete_text_with_cortex"
        ) as mock_cortex:
            mock_cortex.return_value = (
                "Please review the analysis results and approve to continue."
            )

            checkpoint_id = await orchestrator.create_human_checkpoint(
                workflow_id, checkpoint
            )

            assert checkpoint_id == checkpoint.checkpoint_id
            assert checkpoint_id in orchestrator.pending_approvals

            workflow_state = orchestrator.active_workflows[workflow_id]
            assert workflow_state["status"] == WorkflowStatus.WAITING_HUMAN
            assert len(workflow_state["pending_checkpoints"]) == 1

    @pytest.mark.asyncio
    async def test_human_response_handling(self, orchestrator):
        """Test handling human responses to checkpoints"""
        workflow_id = str(uuid.uuid4())
        checkpoint_id = str(uuid.uuid4())

        # Set up workflow and checkpoint
        orchestrator.active_workflows[workflow_id] = {
            "workflow_id": workflow_id,
            "user_id": "test_user",
            "pending_checkpoints": [
                HumanCheckpoint(
                    checkpoint_id=checkpoint_id,
                    title="Test Checkpoint",
                    description="Test description",
                )
            ],
            "checkpoint_responses": {},
            "human_feedback": [],
        }

        orchestrator.pending_approvals[checkpoint_id] = HumanCheckpoint(
            checkpoint_id=checkpoint_id,
            title="Test Checkpoint",
            description="Test description",
        )

        # Mock event processing
        with patch.object(orchestrator, "_process_event"):
            approved = await orchestrator.handle_human_response(
                checkpoint_id=checkpoint_id,
                response={"approved": True, "feedback": "Looks good!"},
                user_id="test_user",
            )

            assert approved is True
            assert checkpoint_id not in orchestrator.pending_approvals

            workflow_state = orchestrator.active_workflows[workflow_id]
            assert checkpoint_id in workflow_state["checkpoint_responses"]
            assert len(workflow_state["human_feedback"]) == 1

    @pytest.mark.asyncio
    async def test_workflow_status_retrieval(self, orchestrator):
        """Test workflow status retrieval"""
        workflow_id = str(uuid.uuid4())
        orchestrator.active_workflows[workflow_id] = {
            "workflow_id": workflow_id,
            "status": WorkflowStatus.RUNNING,
            "current_node": "analysis",
            "completed_nodes": ["data_collection"],
            "next_nodes": ["human_review"],
            "failed_nodes": [],
            "pending_checkpoints": [],
            "execution_metrics": {"total_time": 1500},
            "updated_at": datetime.now(),
        }

        status = await orchestrator.get_workflow_status(workflow_id)

        assert status["workflow_id"] == workflow_id
        assert status["status"] == "running"
        assert status["current_node"] == "analysis"
        assert status["progress"]["completed_nodes"] == 1
        assert status["progress"]["total_nodes"] == 2


class TestUnifiedChatService:
    """Test suite for universal chat service"""

    @pytest.fixture
    async def chat_service(self):
        """Initialize chat service for testing"""
        with (
            patch(
                "backend.services.sophia_universal_chat_service.SnowflakeCortexService"
            ) as mock_cortex,
            patch(
                "backend.services.sophia_universal_chat_service.EnhancedAiMemoryMCPServer"
            ) as mock_memory,
        ):

            mock_cortex_instance = AsyncMock()
            mock_cortex.return_value = mock_cortex_instance

            mock_memory_instance = AsyncMock()
            mock_memory.return_value = mock_memory_instance

            await universal_chat_service.initialize()
            yield universal_chat_service

    @pytest.mark.asyncio
    async def test_intent_recognition(self, chat_service):
        """Test intent recognition from user messages"""
        test_cases = [
            ("Create a workflow to analyze sales data", IntentType.CREATE_WORKFLOW),
            ("What's the status of my workflow?", IntentType.CHECK_STATUS),
            ("I approve the analysis", IntentType.APPROVE_CHECKPOINT),
            ("Create an AI agent for customer support", IntentType.CREATE_AGENT),
            ("Analyze our Q4 performance", IntentType.DATA_ANALYSIS),
            ("How do workflows work?", IntentType.WORKFLOW_HELP),
        ]

        for message, expected_intent in test_cases:
            with patch.object(
                chat_service.cortex_service, "complete_text_with_cortex"
            ) as mock_cortex:
                mock_cortex.return_value = json.dumps(
                    {
                        "intent": expected_intent.value,
                        "confidence": 0.9,
                        "reasoning": "Test reasoning",
                    }
                )

                intent, confidence = await chat_service._recognize_intent(message, [])

                assert intent == expected_intent
                assert confidence == 0.9

    @pytest.mark.asyncio
    async def test_workflow_creation_via_chat(self, chat_service):
        """Test workflow creation through chat interface"""
        user_id = "test_user"
        session_id = "test_session"
        message = "Create a workflow to analyze customer feedback"

        # Mock orchestrator workflow creation
        with (
            patch.object(
                chat_service.orchestrator, "create_workflow_from_natural_language"
            ) as mock_create,
            patch.object(
                chat_service.orchestrator, "get_workflow_status"
            ) as mock_status,
        ):

            mock_create.return_value = "workflow_123"
            mock_status.return_value = {
                "status": "pending",
                "current_node": "start",
                "workflow_id": "workflow_123",
            }

            response = await chat_service.process_message(
                user_id=user_id, session_id=session_id, message_content=message
            )

            assert response.message_type == ChatMessageType.SYSTEM_MESSAGE
            assert "workflow_123" in response.content
            assert response.workflow_id == "workflow_123"
            assert "✅" in response.content  # Success indicator

    @pytest.mark.asyncio
    async def test_approval_handling_via_chat(self, chat_service):
        """Test approval handling through chat interface"""
        user_id = "test_user"
        session_id = "test_session"

        # Mock pending approvals
        with (
            patch.object(
                chat_service.orchestrator, "get_pending_approvals"
            ) as mock_pending,
            patch.object(
                chat_service.orchestrator, "handle_human_response"
            ) as mock_handle,
        ):

            mock_pending.return_value = [
                {
                    "checkpoint_id": "checkpoint_123",
                    "title": "Review Analysis",
                    "description": "Please review the analysis results",
                }
            ]
            mock_handle.return_value = True

            response = await chat_service.process_message(
                user_id=user_id,
                session_id=session_id,
                message_content="I approve the analysis",
            )

            assert response.message_type == ChatMessageType.SYSTEM_MESSAGE
            assert "✅ Approved!" in response.content

    @pytest.mark.asyncio
    async def test_session_management(self, chat_service):
        """Test chat session management"""
        user_id = "test_user"
        session_id = "test_session"

        # Create session through message processing
        await chat_service.process_message(
            user_id=user_id, session_id=session_id, message_content="Hello"
        )

        assert session_id in chat_service.active_sessions
        session = chat_service.active_sessions[session_id]
        assert session.user_id == user_id
        assert len(session.context_history) >= 1

        # Test session history retrieval
        history = await chat_service.get_session_history(session_id, limit=10)
        assert len(history) >= 1
        assert history[0].user_id == user_id


class TestCostEngineeringService:
    """Test suite for cost engineering service"""

    @pytest.fixture
    async def cost_service(self):
        """Initialize cost engineering service for testing"""
        with (
            patch(
                "backend.services.cost_engineering_service.SnowflakeCortexService"
            ) as mock_cortex,
            patch(
                "backend.services.cost_engineering_service.EnhancedAiMemoryMCPServer"
            ) as mock_memory,
        ):

            mock_cortex_instance = AsyncMock()
            mock_cortex.return_value = mock_cortex_instance

            mock_memory_instance = AsyncMock()
            mock_memory.return_value = mock_memory_instance

            await cost_engineering_service.initialize()
            yield cost_engineering_service

    @pytest.mark.asyncio
    async def test_task_complexity_analysis(self, cost_service):
        """Test task complexity analysis"""
        test_cases = [
            ("What is 2+2?", TaskComplexity.SIMPLE),
            ("Analyze the sales performance for Q4", TaskComplexity.MODERATE),
            (
                "Perform a comprehensive market analysis with competitive intelligence",
                TaskComplexity.COMPLEX,
            ),
            (
                "Research advanced machine learning techniques for specialized domain",
                TaskComplexity.EXPERT,
            ),
        ]

        for prompt, expected_complexity in test_cases:
            task_request = TaskRequest(
                request_id=str(uuid.uuid4()),
                user_id="test_user",
                task_type="analysis",
                prompt=prompt,
            )

            with patch.object(
                cost_service.cortex_service, "complete_text_with_cortex"
            ) as mock_cortex:
                mock_cortex.return_value = expected_complexity.value.upper()

                complexity = await cost_service._analyze_task_complexity(task_request)
                assert complexity == expected_complexity

    @pytest.mark.asyncio
    async def test_model_selection_strategies(self, cost_service):
        """Test different model selection strategies"""
        task_request = TaskRequest(
            request_id=str(uuid.uuid4()),
            user_id="test_user",
            task_type="analysis",
            prompt="Analyze this data",
            required_quality=0.8,
        )

        # Test cost-first strategy
        cost_service.optimization_strategy = CostOptimizationStrategy.COST_FIRST
        model = await cost_service._select_optimal_model(
            task_request, TaskComplexity.MODERATE
        )
        model_config = cost_service.model_configs[model]
        assert model_config.tier in [ModelTier.SMALL, ModelTier.MEDIUM]

        # Test performance-first strategy
        cost_service.optimization_strategy = CostOptimizationStrategy.PERFORMANCE_FIRST
        model = await cost_service._select_optimal_model(
            task_request, TaskComplexity.COMPLEX
        )
        model_config = cost_service.model_configs[model]
        assert model_config.tier in [ModelTier.LARGE, ModelTier.PREMIUM]

    @pytest.mark.asyncio
    async def test_cost_tracking(self, cost_service):
        """Test cost tracking and metrics"""
        user_id = "test_user"

        # Simulate task processing
        await cost_service._update_metrics(
            user_id=user_id, tokens_used=100, cost=0.01, latency_ms=500, cache_hit=False
        )

        await cost_service._update_metrics(
            user_id=user_id, tokens_used=0, cost=0.0, latency_ms=50, cache_hit=True
        )

        # Check metrics
        user_metrics = cost_service.cost_metrics[user_id]
        assert user_metrics.total_tokens == 100
        assert user_metrics.total_cost == 0.01
        assert user_metrics.request_count == 2
        assert user_metrics.cache_hits == 1
        assert user_metrics.cache_misses == 1

        # Test cost report generation
        report = await cost_service.get_cost_report(user_id)
        assert report["scope"] == f"user_{user_id}"
        assert report["metrics"]["total_requests"] == 2
        assert report["metrics"]["cache_hit_rate"] == 0.5

    @pytest.mark.asyncio
    async def test_prompt_optimization(self, cost_service):
        """Test prompt optimization for cost efficiency"""
        long_prompt = (
            "This is a very long prompt with lots of redundant information " * 20
        )

        with patch.object(
            cost_service.cortex_service, "complete_text_with_cortex"
        ) as mock_cortex:
            mock_cortex.return_value = "Optimized shorter prompt with same intent"

            optimized = await cost_service._optimize_prompt(long_prompt, "mistral-7b")

            # Should be shorter than original
            assert len(optimized) < len(long_prompt)

    @pytest.mark.asyncio
    async def test_semantic_caching(self, cost_service):
        """Test semantic caching functionality"""
        task_request = TaskRequest(
            request_id=str(uuid.uuid4()),
            user_id="test_user",
            task_type="analysis",
            prompt="Analyze sales data",
        )

        # Mock cache miss first
        with (
            patch.object(cost_service.cache_manager, "get") as mock_get,
            patch.object(
                cost_service.ai_memory, "search_similar_content"
            ) as mock_search,
        ):

            mock_get.return_value = None
            mock_search.return_value = []

            result = await cost_service._check_semantic_cache(task_request)
            assert result is None

            # Mock cache hit
            mock_search.return_value = [
                {
                    "response": "Cached analysis result",
                    "model_used": "mistral-7b",
                    "quality_score": 0.9,
                }
            ]

            result = await cost_service._check_semantic_cache(task_request)
            assert result is not None
            assert result["response"] == "Cached analysis result"


class TestEnhancedSnowflakeCortexService:
    """Test suite for enhanced Snowflake Cortex service"""

    @pytest.fixture
    async def cortex_service(self):
        """Initialize enhanced Cortex service for testing"""
        with patch(
            "backend.services.enhanced_snowflake_cortex_service.snowflake.connector.connect"
        ) as mock_connect:
            mock_connection = MagicMock()
            mock_cursor = MagicMock()
            mock_connection.cursor.return_value = mock_cursor
            mock_connect.return_value = mock_connection

            await enhanced_cortex_service.initialize()
            yield enhanced_cortex_service

    @pytest.mark.asyncio
    async def test_advanced_cortex_search(self, cortex_service):
        """Test advanced Cortex Search functionality"""
        search_config = CortexSearchConfig(
            search_mode=CortexSearchMode.HYBRID, max_results=5, similarity_threshold=0.8
        )

        # Mock database results
        mock_results = [
            {
                "content": "Test content 1",
                "similarity_score": 0.9,
                "metadata": {"source": "test"},
            },
            {
                "content": "Test content 2",
                "similarity_score": 0.85,
                "metadata": {"source": "test"},
            },
        ]

        with patch.object(cortex_service, "_get_connection") as mock_conn:
            mock_connection = AsyncMock()
            mock_cursor = MagicMock()
            mock_cursor.fetchall.return_value = mock_results
            mock_connection.cursor.return_value = mock_cursor
            mock_conn.return_value = mock_connection

            result = await cortex_service.advanced_cortex_search(
                query="test query", search_service="test_service", config=search_config
            )

            assert "results" in result
            assert "metadata" in result
            assert len(result["results"]) == 2
            assert result["metadata"]["search_mode"] == "hybrid"

    @pytest.mark.asyncio
    async def test_data_pipeline_creation(self, cortex_service):
        """Test data pipeline creation and execution"""
        pipeline_config = DataPipelineConfig(
            pipeline_id="test_pipeline",
            source_tables=["source_table_1"],
            target_table="target_table",
            processing_mode=DataProcessingMode.BATCH,
            ai_functions=[
                AIFunctionType.SENTIMENT_ANALYSIS,
                AIFunctionType.SUMMARIZATION,
            ],
            batch_size=100,
        )

        execution_id = await cortex_service.create_data_pipeline(pipeline_config)

        assert execution_id is not None
        assert execution_id in cortex_service.active_pipelines
        assert cortex_service.active_pipelines[execution_id] == pipeline_config

    @pytest.mark.asyncio
    async def test_ai_function_processing(self, cortex_service):
        """Test AI function processing on data"""
        test_row = {
            "id": 1,
            "content": "This is a great product! I love it.",
            "customer_name": "John Doe",
        }

        # Test sentiment analysis
        with patch.object(cortex_service, "_get_connection") as mock_conn:
            mock_connection = AsyncMock()
            mock_cursor = MagicMock()
            mock_cursor.fetchone.return_value = [
                '{"sentiment": 0.8, "classification": "positive", "confidence": 0.9}'
            ]
            mock_connection.cursor.return_value = mock_cursor
            mock_conn.return_value = mock_connection

            result = await cortex_service._apply_sentiment_analysis(
                test_row, "test_execution"
            )

            assert result.function_type == AIFunctionType.SENTIMENT_ANALYSIS
            assert "sentiment_score" in result.output_data
            assert result.output_data["sentiment_classification"] == "positive"

    @pytest.mark.asyncio
    async def test_data_quality_analysis(self, cortex_service):
        """Test data quality analysis"""
        mock_schema = [
            {"name": "id", "type": "NUMBER"},
            {"name": "content", "type": "VARCHAR"},
            {"name": "created_at", "type": "TIMESTAMP"},
        ]

        mock_quality_stats = [
            {
                "total_rows": 1000,
                "non_null_rows": 1000,
                "null_rows": 0,
                "null_percentage": 0.0,
            },
            {
                "total_rows": 1000,
                "non_null_rows": 950,
                "null_rows": 50,
                "null_percentage": 5.0,
            },
            {
                "total_rows": 1000,
                "non_null_rows": 1000,
                "null_rows": 0,
                "null_percentage": 0.0,
            },
        ]

        with patch.object(cortex_service, "_get_connection") as mock_conn:
            mock_connection = AsyncMock()
            mock_cursor = MagicMock()

            # Mock schema query
            mock_cursor.fetchall.side_effect = [mock_schema]
            # Mock quality stats queries
            mock_cursor.fetchone.side_effect = mock_quality_stats

            mock_connection.cursor.return_value = mock_cursor
            mock_conn.return_value = mock_connection

            result = await cortex_service.analyze_data_quality("test_table")

            assert "overall_quality_score" in result
            assert "column_quality" in result
            assert len(result["column_quality"]) == 3
            assert result["column_quality"][1]["null_percentage"] == 5.0

    @pytest.mark.asyncio
    async def test_pipeline_status_monitoring(self, cortex_service):
        """Test pipeline status monitoring"""
        execution_id = "test_execution"
        pipeline_config = DataPipelineConfig(
            pipeline_id="test_pipeline",
            source_tables=["source_table"],
            target_table="target_table",
            processing_mode=DataProcessingMode.BATCH,
            ai_functions=[AIFunctionType.SENTIMENT_ANALYSIS],
        )

        # Set up pipeline
        cortex_service.active_pipelines[execution_id] = pipeline_config
        cortex_service.pipeline_results[execution_id] = [
            MagicMock(cost=0.01, quality_score=0.9, processing_time_ms=500),
            MagicMock(cost=0.02, quality_score=0.85, processing_time_ms=600),
        ]

        status = await cortex_service.get_pipeline_status(execution_id)

        assert status["execution_id"] == execution_id
        assert status["pipeline_id"] == "test_pipeline"
        assert status["metrics"]["total_operations"] == 2
        assert status["metrics"]["total_cost"] == 0.03
        assert status["metrics"]["avg_quality_score"] == 0.875


class TestEndToEndIntegration:
    """End-to-end integration tests"""

    @pytest.mark.asyncio
    async def test_complete_workflow_via_chat(self):
        """Test complete workflow creation and execution via chat"""
        # This test would simulate a complete user journey:
        # 1. User creates workflow via chat
        # 2. Workflow executes with cost optimization
        # 3. Human approval checkpoint is reached
        # 4. User approves via chat
        # 5. Workflow completes with Cortex processing

        # Mock all services
        with (
            patch(
                "backend.services.sophia_universal_chat_service.SnowflakeCortexService"
            ),
            patch(
                "backend.services.sophia_universal_chat_service.EnhancedAiMemoryMCPServer"
            ),
            patch(
                "backend.workflows.enhanced_langgraph_orchestration.SnowflakeCortexService"
            ),
            patch(
                "backend.workflows.enhanced_langgraph_orchestration.EnhancedAiMemoryMCPServer"
            ),
            patch("backend.services.cost_engineering_service.SnowflakeCortexService"),
            patch(
                "backend.services.cost_engineering_service.EnhancedAiMemoryMCPServer"
            ),
        ):

            # Initialize services
            await universal_chat_service.initialize()
            await enhanced_orchestrator.initialize()
            await cost_engineering_service.initialize()

            user_id = "test_user"
            session_id = "test_session"

            # Step 1: Create workflow via chat
            with patch.object(
                enhanced_orchestrator.cortex_service, "complete_text_with_cortex"
            ) as mock_cortex:
                mock_cortex.return_value = json.dumps(
                    {
                        "type": "data_analysis",
                        "required_data_sources": ["sales_data"],
                        "processing_steps": ["analysis"],
                        "human_approval_points": ["review"],
                        "expected_outputs": ["report"],
                    }
                )

                response = await universal_chat_service.process_message(
                    user_id=user_id,
                    session_id=session_id,
                    message_content="Create a workflow to analyze our sales data",
                )

                assert response.message_type == ChatMessageType.SYSTEM_MESSAGE
                assert response.workflow_id is not None
                workflow_id = response.workflow_id

            # Step 2: Simulate workflow reaching approval checkpoint
            checkpoint = HumanCheckpoint(
                checkpoint_id=str(uuid.uuid4()),
                title="Review Analysis",
                description="Please review the analysis results",
            )

            with patch.object(
                enhanced_orchestrator.cortex_service, "complete_text_with_cortex"
            ) as mock_cortex:
                mock_cortex.return_value = (
                    "Please review the analysis and approve to continue."
                )

                checkpoint_id = await enhanced_orchestrator.create_human_checkpoint(
                    workflow_id, checkpoint
                )

            # Step 3: User approves via chat
            with (
                patch.object(
                    enhanced_orchestrator, "get_pending_approvals"
                ) as mock_pending,
                patch.object(
                    enhanced_orchestrator, "handle_human_response"
                ) as mock_handle,
            ):

                mock_pending.return_value = [
                    {
                        "checkpoint_id": checkpoint_id,
                        "title": "Review Analysis",
                        "description": "Please review the analysis results",
                    }
                ]
                mock_handle.return_value = True

                approval_response = await universal_chat_service.process_message(
                    user_id=user_id,
                    session_id=session_id,
                    message_content="I approve the analysis",
                )

                assert "✅ Approved!" in approval_response.content

            # Verify workflow state
            workflow_status = await enhanced_orchestrator.get_workflow_status(
                workflow_id
            )
            assert workflow_status["workflow_id"] == workflow_id

    @pytest.mark.asyncio
    async def test_cost_optimized_processing_pipeline(self):
        """Test cost-optimized processing with Cortex integration"""
        # Mock services
        with (
            patch("backend.services.cost_engineering_service.SnowflakeCortexService"),
            patch(
                "backend.services.enhanced_snowflake_cortex_service.snowflake.connector.connect"
            ),
        ):

            await cost_engineering_service.initialize()
            await enhanced_cortex_service.initialize()

            # Create a task request
            task_request = TaskRequest(
                request_id=str(uuid.uuid4()),
                user_id="test_user",
                task_type="sentiment_analysis",
                prompt="Analyze the sentiment of customer feedback",
                required_quality=0.8,
            )

            # Mock cost service processing
            with (
                patch.object(cost_engineering_service, "_execute_task") as mock_execute,
                patch.object(
                    cost_engineering_service, "_assess_response_quality"
                ) as mock_quality,
            ):

                mock_execute.return_value = ("Positive sentiment detected", 50)
                mock_quality.return_value = 0.9

                response = await cost_engineering_service.process_task(task_request)

                assert response.request_id == task_request.request_id
                assert response.tokens_used == 50
                assert response.quality_score == 0.9
                assert response.cost > 0

    @pytest.mark.asyncio
    async def test_performance_metrics_collection(self):
        """Test performance metrics collection across all services"""
        # This test would verify that performance metrics are properly
        # collected and aggregated across all Phase 2 services

        # Mock all services
        with (
            patch(
                "backend.services.sophia_universal_chat_service.SnowflakeCortexService"
            ),
            patch("backend.services.cost_engineering_service.SnowflakeCortexService"),
            patch(
                "backend.services.enhanced_snowflake_cortex_service.snowflake.connector.connect"
            ),
        ):

            await universal_chat_service.initialize()
            await cost_engineering_service.initialize()
            await enhanced_cortex_service.initialize()

            # Simulate various operations and verify metrics are collected
            user_id = "test_user"

            # Chat service metrics
            await universal_chat_service.process_message(
                user_id=user_id,
                session_id="test_session",
                message_content="Test message",
            )

            # Cost service metrics
            await cost_engineering_service._update_metrics(
                user_id=user_id,
                tokens_used=100,
                cost=0.01,
                latency_ms=500,
                cache_hit=False,
            )

            # Verify metrics are collected
            assert user_id in cost_engineering_service.cost_metrics
            user_metrics = cost_engineering_service.cost_metrics[user_id]
            assert user_metrics.total_tokens == 100
            assert user_metrics.total_cost == 0.01
            assert user_metrics.request_count == 1


# Test configuration
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])
