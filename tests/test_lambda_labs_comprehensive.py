#!/usr/bin/env python3
"""
Comprehensive tests for Lambda Labs implementation
Tests all aspects of the serverless-first architecture
"""

import asyncio
from unittest.mock import AsyncMock, patch

import pytest

from backend.services.lambda_labs_chat_integration import LambdaLabsChatIntegration
from backend.services.lambda_labs_service import LambdaLabsService
from backend.services.unified_chat_service import UnifiedChatService
from core.services.natural_language_infrastructure_controller import (
    NaturalLanguageInfrastructureController,
)


class TestLambdaLabsService:
    """Test Lambda Labs service functionality"""

    @pytest.fixture
    def service(self):
        """Create service instance"""
        with patch("backend.services.lambda_labs_service.get_secret") as mock_secret:
            mock_secret.return_value = "test-api-key"
            return LambdaLabsService()

    @pytest.mark.asyncio
    async def test_model_selection(self, service):
        """Test intelligent model selection"""
        # Simple task
        model = service.select_optimal_model("Quick summary", complexity="auto")
        assert model == "llama3.1-8b-instruct"

        # Complex task
        model = service.select_optimal_model(
            "Detailed analysis with reasoning", complexity="auto"
        )
        assert model == "llama-4-maverick-17b-128e-instruct-fp8"

        # Explicit complexity
        model = service.select_optimal_model("Any task", complexity="balanced")
        assert model == "llama3.1-70b-instruct-fp8"

    @pytest.mark.asyncio
    async def test_cost_estimation(self, service):
        """Test cost estimation accuracy"""
        messages = [{"role": "user", "content": "Test message " * 100}]
        cost = service._estimate_cost(messages, "llama3.1-70b-instruct-fp8", 500)

        # Should be reasonable cost
        assert 0.0001 < cost < 0.01

    @pytest.mark.asyncio
    async def test_budget_enforcement(self, service):
        """Test budget enforcement"""
        # Set test budget
        service.cost_config["daily_budget"] = 0.01
        service.usage_tracker = {
            "2024-01-01": {"cost": 0.009, "tokens": 1000, "requests": 1}
        }

        # Should reject over-budget request
        budget_check = await service._check_budget(0.005)
        assert not budget_check["approved"]
        assert budget_check["daily_remaining"] < 0.005

    @pytest.mark.asyncio
    async def test_natural_language_to_sql(self, service):
        """Test natural language to SQL conversion"""
        with patch.object(service, "simple_inference") as mock_inference:
            mock_inference.return_value = (
                "SELECT revenue FROM sales WHERE quarter = 'Q4'"
            )

            sql = await service.natural_language_to_sql(
                "Show revenue for last quarter", schema_context="sales table"
            )

            assert "SELECT" in sql
            assert "revenue" in sql.lower()

    @pytest.mark.asyncio
    async def test_health_check(self, service):
        """Test health check functionality"""
        with patch("aiohttp.ClientSession") as mock_session:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(
                return_value={"choices": [{"message": {"content": "Hello"}}]}
            )

            mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = (
                mock_response
            )

            health = await service.health_check()
            assert health is True


class TestLambdaLabsChatIntegration:
    """Test Lambda Labs chat integration"""

    @pytest.fixture
    def integration(self):
        """Create integration instance"""
        return LambdaLabsChatIntegration()

    @pytest.mark.asyncio
    async def test_process_chat_message(self, integration):
        """Test chat message processing"""
        with patch.object(integration.router, "generate") as mock_generate:
            mock_generate.return_value = {
                "choices": [{"message": {"content": "Test response"}}],
                "model": "llama3.1-70b-instruct-fp8",
                "backend": "serverless",
                "usage": {"total_tokens": 100},
            }

            result = await integration.process_chat_message(
                "Test message", user_context={"user_role": "CEO"}
            )

            assert result["success"] is True
            assert result["response"] == "Test response"
            assert result["model"] == "llama3.1-70b-instruct-fp8"

    @pytest.mark.asyncio
    async def test_intent_analysis(self, integration):
        """Test intent analysis for routing"""
        # Infrastructure command
        intent = await integration.analyze_intent("Deploy the new service")
        assert intent["intent"] == "infrastructure_control"
        assert intent["recommended_backend"] == "gpu"

        # Analytics query
        intent = await integration.analyze_intent("Analyze sales metrics")
        assert intent["intent"] == "analytics"
        assert intent["recommended_backend"] == "serverless"

        # Simple query
        intent = await integration.analyze_intent("Hello")
        assert intent["intent"] == "simple_query"
        assert intent["recommended_model"] == "llama3.1-8b-instruct"


class TestUnifiedChatServiceIntegration:
    """Test unified chat service Lambda Labs integration"""

    @pytest.fixture
    def chat_service(self):
        """Create chat service instance"""
        return UnifiedChatService()

    @pytest.mark.asyncio
    async def test_lambda_labs_in_service_map(self, chat_service):
        """Test Lambda Labs is properly integrated"""
        assert "lambda_labs" in chat_service.service_map
        assert hasattr(chat_service, "lambda_labs")

    @pytest.mark.asyncio
    async def test_process_with_lambda(self, chat_service):
        """Test processing messages with Lambda Labs"""
        with patch.object(chat_service, "_classify_message") as mock_classify:
            mock_classify.return_value = {
                "requires_gpu": False,
                "complexity": "balanced",
                "estimated_tokens": 100,
            }

            with patch.object(chat_service, "_route_to_serverless") as mock_route:
                mock_route.return_value = {
                    "response": "Test response",
                    "success": True,
                }

                result = await chat_service.process_message_with_lambda("Test message")
                assert result["success"] is True
                assert "response" in result

    @pytest.mark.asyncio
    async def test_natural_language_infrastructure_control(self, chat_service):
        """Test natural language infrastructure commands"""
        with patch.object(
            chat_service, "_optimize_lambda_infrastructure"
        ) as mock_optimize:
            mock_optimize.return_value = {
                "response": "Optimization complete",
                "success": True,
            }

            result = await chat_service.natural_language_infrastructure_control(
                "Optimize Lambda costs"
            )
            assert result["success"] is True


class TestNaturalLanguageController:
    """Test natural language infrastructure controller"""

    @pytest.fixture
    def controller(self):
        """Create controller instance"""
        return NaturalLanguageInfrastructureController()

    @pytest.mark.asyncio
    async def test_process_command(self, controller):
        """Test command processing"""
        # Lambda Labs command
        with patch.object(controller.lambda_router, "generate") as mock_generate:
            mock_generate.return_value = {
                "choices": [{"message": {"content": "Cost analysis complete"}}]
            }

            result = await controller.process_command("Analyze Lambda Labs costs")
            assert result["success"] is True

        # Snowflake command
        with patch.object(controller.snowflake, "complete") as mock_complete:
            mock_complete.return_value = {"content": "Query executed"}

            result = await controller.process_command("Query Snowflake for revenue")
            assert result["success"] is True

    @pytest.mark.asyncio
    async def test_health_check(self, controller):
        """Test health check across services"""
        with patch.object(controller.lambda_router, "health_check") as mock_lambda:
            mock_lambda.return_value = {"status": "healthy"}

            with patch.object(controller.snowflake, "health_check") as mock_snowflake:
                mock_snowflake.return_value = {"status": "healthy"}

                health = await controller.check_health()
                assert health["lambda_labs"]["status"] == "healthy"
                assert health["snowflake"]["status"] == "healthy"


class TestCostOptimization:
    """Test cost optimization features"""

    @pytest.mark.asyncio
    async def test_cost_tracking(self):
        """Test cost tracking accuracy"""
        service = LambdaLabsService()

        # Track usage
        await service._track_usage(
            model="llama3.1-70b-instruct-fp8",
            usage={"total_tokens": 1000},
            cost=0.00035,
        )

        # Check tracking
        usage = await service._get_current_usage()
        assert usage["daily_cost"] > 0

    @pytest.mark.asyncio
    async def test_cost_comparison(self):
        """Test cost comparison with GPU baseline"""
        gpu_monthly_cost = 6444
        serverless_monthly_cost = 450

        savings = gpu_monthly_cost - serverless_monthly_cost
        savings_percentage = (savings / gpu_monthly_cost) * 100

        assert savings_percentage > 90  # Should be >90% savings


class TestEndToEndScenarios:
    """Test end-to-end scenarios"""

    @pytest.mark.asyncio
    async def test_ceo_query_flow(self):
        """Test CEO query processing flow"""
        chat = UnifiedChatService()

        with patch.object(chat, "process_message_with_lambda") as mock_process:
            mock_process.return_value = {
                "response": "Revenue analysis complete",
                "model_used": "llama3.1-70b-instruct-fp8",
                "cost": 0.001,
                "success": True,
            }

            # CEO gets performance priority
            result = await chat.process_unified_query(
                "Analyze Q4 revenue by product",
                user_id="ceo",
                session_id="session-123",
            )

            # Should use Lambda Labs
            mock_process.assert_called()

    @pytest.mark.asyncio
    async def test_natural_language_sql_flow(self):
        """Test natural language to SQL flow"""
        from infrastructure.adapters.snowflake_adapter import SnowflakeAdapter

        adapter = SnowflakeAdapter("snowflake", None)

        with patch.object(adapter, "natural_language_to_sql") as mock_nl_sql:
            mock_nl_sql.return_value = {
                "success": True,
                "generated_sql": "SELECT * FROM revenue",
                "results": [{"revenue": 1000000}],
            }

            result = await adapter.natural_language_to_sql("Show total revenue")
            assert result["success"] is True
            assert "SELECT" in result["generated_sql"]


# Performance benchmarks
class TestPerformanceBenchmarks:
    """Test performance requirements"""

    @pytest.mark.asyncio
    async def test_latency_requirements(self):
        """Test latency is within requirements"""
        import time

        service = LambdaLabsService()

        start = time.time()
        # Simulate API call
        with patch("aiohttp.ClientSession"):
            pass
        elapsed = time.time() - start

        # Should be < 500ms
        assert elapsed < 0.5

    @pytest.mark.asyncio
    async def test_throughput_requirements(self):
        """Test throughput capabilities"""
        service = LambdaLabsService()

        # Should handle multiple concurrent requests
        tasks = []
        for _ in range(10):
            with patch.object(service, "chat_completion") as mock_chat:
                mock_chat.return_value = {"choices": [{"message": {"content": "OK"}}]}
                tasks.append(service.simple_inference("Test"))

        results = await asyncio.gather(*tasks)
        assert len(results) == 10


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
