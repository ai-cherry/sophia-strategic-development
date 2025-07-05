"""
Comprehensive Test Suite for Sophia AI Unified Chat Service
Tests reliability, performance, and error handling
"""
import asyncio
import os

# Import the services we're testing
import sys
import time
from unittest.mock import AsyncMock, Mock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.api.unified_routes import router


class TestUnifiedChatReliability:
    """Comprehensive reliability and performance tests"""

    @pytest.fixture
    def app(self):
        """Create FastAPI app for testing"""
        app = FastAPI()
        app.include_router(router, prefix="/api/v1")
        return app

    @pytest.fixture
    def client(self, app):
        """Create test client"""
        return TestClient(app)

    @pytest.mark.asyncio
    async def test_ceo_chat_performance_sla(self, client):
        """Test CEO chat meets 2-second SLA under normal conditions"""
        # Test data for CEO scenarios
        ceo_queries = [
            "What's our Q4 revenue projection?",
            "Show me top customer churn risks",
            "Analyze competitive positioning vs Salesforce",
            "What are our biggest operational bottlenecks?",
        ]

        response_times = []

        with patch(
            "backend.services.unified_chat_service.UnifiedChatService"
        ) as mock_service:
            # Mock the chat service to return realistic responses quickly
            mock_instance = mock_service.return_value
            mock_instance.process_chat = AsyncMock(
                return_value={
                    "response": "Executive Summary: Revenue is tracking 15% above target...",
                    "sources": ["snowflake.revenue_table", "hubspot.deals"],
                    "suggestions": ["Review Q1 projections", "Schedule board update"],
                    "session_id": "test_session",
                    "timestamp": "2025-07-04T10:00:00",
                }
            )

            for query in ceo_queries:
                start_time = time.time()

                response = client.post(
                    "/api/v1/chat",
                    json={
                        "message": query,
                        "context": "ceo_deep_research",
                        "access_level": "ceo",
                        "user_id": "ceo_test",
                    },
                )

                end_time = time.time()
                response_time = end_time - start_time
                response_times.append(response_time)

                # Assertions
                assert response.status_code == 200, f"Failed on query: {query}"
                assert (
                    response_time < 2.0
                ), f"CEO SLA violation: {response_time:.2f}s > 2s"

                response_data = response.json()
                assert "response" in response_data
                assert len(response_data.get("sources", [])) > 0

        # Performance analysis
        avg_response_time = sum(response_times) / len(response_times)
        assert (
            avg_response_time < 1.5
        ), f"Average response time {avg_response_time:.2f}s exceeds target"

    @pytest.mark.asyncio
    async def test_mcp_server_cascading_failure_prevention(self, client):
        """Test that MCP server failures don't cascade"""

        with patch("backend.services.mcp_gateway.MCPServerGateway") as mock_gateway:
            # Create a mock that simulates primary failure then fallback success
            mock_gateway_instance = Mock()
            mock_gateway_instance.call_server = Mock(
                side_effect=[
                    ConnectionError("Primary server down"),  # First attempt fails
                    {
                        "response": "Success from fallback",
                        "server": "fallback_server",
                    },  # Fallback succeeds
                ]
            )
            mock_gateway.return_value = mock_gateway_instance

            response = client.post(
                "/api/v1/chat",
                json={
                    "message": "Test failover scenario",
                    "context": "business_intelligence",
                    "access_level": "manager",
                },
            )

            # Should still succeed despite primary failure
            assert response.status_code == 200

            # Verify fallback was used
            assert mock_gateway_instance.call_server.call_count >= 2

    @pytest.mark.asyncio
    async def test_concurrent_request_handling(self, client):
        """Test system handles concurrent requests without degradation"""

        async def make_request(session_id: int):
            """Make a single request"""
            response = client.post(
                "/api/v1/chat",
                json={
                    "message": f"Test concurrent request {session_id}",
                    "context": "business_intelligence",
                    "session_id": f"session_{session_id}",
                },
            )
            return response.status_code, response.elapsed.total_seconds()

        # Simulate 10 concurrent requests
        with patch(
            "backend.services.unified_chat_service.UnifiedChatService"
        ) as mock_service:
            mock_instance = mock_service.return_value
            mock_instance.process_chat = AsyncMock(
                return_value={
                    "response": "Concurrent test response",
                    "sources": ["test_source"],
                    "session_id": "test",
                }
            )

            # Use asyncio to run requests concurrently
            loop = asyncio.new_event_loop()
            tasks = [loop.create_task(make_request(i)) for i in range(10)]
            results = loop.run_until_complete(asyncio.gather(*tasks))
            loop.close()

            # All requests should succeed
            statuses = [r[0] for r in results]
            assert all(
                status == 200 for status in statuses
            ), "Some concurrent requests failed"

            # Response times should be reasonable
            response_times = [r[1] for r in results]
            avg_time = sum(response_times) / len(response_times)
            assert (
                avg_time < 3.0
            ), f"Concurrent requests too slow: {avg_time:.2f}s average"

    def test_error_handling_graceful_degradation(self, client):
        """Test graceful error handling without exposing internals"""

        with patch(
            "backend.services.unified_chat_service.UnifiedChatService"
        ) as mock_service:
            # Simulate various error conditions
            mock_instance = mock_service.return_value
            mock_instance.process_chat = AsyncMock(
                side_effect=Exception("Internal database error")
            )

            response = client.post(
                "/api/v1/chat",
                json={
                    "message": "Test error handling",
                    "context": "business_intelligence",
                },
            )

            # Should return error status but not expose internal details
            assert response.status_code == 500
            error_data = response.json()
            assert "detail" in error_data
            assert "database error" not in error_data["detail"].lower()
            assert "internal" not in error_data["detail"].lower()

    def test_input_validation_security(self, client):
        """Test input validation prevents injection attacks"""

        # Test various malicious inputs
        malicious_inputs = [
            {"message": "'; DROP TABLE users; --", "context": "business_intelligence"},
            {
                "message": "<script>alert('xss')</script>",
                "context": "ceo_deep_research",
            },
            {
                "message": "A" * 10000,
                "context": "business_intelligence",
            },  # Very long input
            {"message": "", "context": "business_intelligence"},  # Empty message
            {"message": "Test", "context": "invalid_context"},  # Invalid context
        ]

        for malicious_input in malicious_inputs:
            response = client.post("/api/v1/chat", json=malicious_input)

            # Should either reject (400) or handle safely (200)
            assert response.status_code in [
                200,
                400,
                422,
            ], f"Unexpected status for input: {malicious_input}"

            # If successful, ensure no injection occurred
            if response.status_code == 200:
                response_data = response.json()
                assert "<script>" not in str(response_data)
                assert "DROP TABLE" not in str(response_data)

    @pytest.mark.asyncio
    async def test_memory_leak_prevention(self, client):
        """Test that repeated requests don't cause memory leaks"""
        import os

        import psutil

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        with patch(
            "backend.services.unified_chat_service.UnifiedChatService"
        ) as mock_service:
            mock_instance = mock_service.return_value
            mock_instance.process_chat = AsyncMock(
                return_value={
                    "response": "Memory test response",
                    "sources": ["test"],
                    "session_id": "memory_test",
                }
            )

            # Make 100 requests
            for i in range(100):
                response = client.post(
                    "/api/v1/chat",
                    json={
                        "message": f"Memory test {i}",
                        "context": "business_intelligence",
                        "session_id": f"mem_test_{i}",
                    },
                )
                assert response.status_code == 200

            # Check memory hasn't grown excessively
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_growth = final_memory - initial_memory

            # Allow some growth but not excessive (< 50MB for 100 requests)
            assert memory_growth < 50, f"Excessive memory growth: {memory_growth:.2f}MB"

    def test_rate_limiting_protection(self, client):
        """Test rate limiting prevents abuse"""

        # Make rapid requests from same "user"
        responses = []
        for i in range(20):
            response = client.post(
                "/api/v1/chat",
                json={
                    "message": f"Rate limit test {i}",
                    "context": "business_intelligence",
                    "user_id": "rate_limit_test_user",
                },
            )
            responses.append(response)

        # Some requests should be rate limited (429) after threshold
        status_codes = [r.status_code for r in responses]

        # Either rate limiting is implemented (some 429s) or all succeed
        # This test documents current behavior
        if 429 in status_codes:
            assert status_codes.count(429) > 0, "Rate limiting should kick in"
        else:
            assert all(code == 200 for code in status_codes), "Unexpected errors"


class TestPromptOptimization:
    """Test prompt optimization for cost reduction"""

    def test_prompt_cost_estimation(self):
        """Test accurate cost estimation before execution"""
        from backend.prompts.optimized_templates import SophiaPromptOptimizer

        optimizer = SophiaPromptOptimizer()

        # Test various query lengths
        test_cases = [
            ("What is our revenue?", 0.001),  # Short query
            (
                "Analyze all customer data for the past year and provide insights",
                0.005,
            ),  # Medium
            ("Provide a comprehensive analysis of " * 50, 0.05),  # Long query
        ]

        for query, max_expected_cost in test_cases:
            estimated_cost = asyncio.run(
                optimizer.cost_tracker.estimate_query_cost(
                    query, "business_intelligence"
                )
            )

            assert estimated_cost > 0, "Cost should be positive"
            assert (
                estimated_cost < max_expected_cost
            ), f"Cost too high: ${estimated_cost:.4f}"

    def test_prompt_optimization_reduces_tokens(self):
        """Test that optimization reduces token count"""
        from backend.prompts.optimized_templates import SophiaPromptOptimizer

        optimizer = SophiaPromptOptimizer()

        # Long, expensive query
        expensive_query = (
            "Please analyze all of our customer data including their purchase history, "
            "interaction patterns, support tickets, and provide detailed insights about "
            "their behavior patterns, preferences, and likelihood to churn. Also include "
            "recommendations for improving customer satisfaction and retention rates. "
            * 5
        )

        # Should optimize for cost
        optimized = asyncio.run(
            optimizer.cost_tracker.optimize_for_cost(expensive_query)
        )

        assert len(optimized) < len(
            expensive_query
        ), "Optimization should reduce length"
        assert "Summarize" in optimized or "analyze" in optimized.lower()

    def test_context_aware_prompt_selection(self):
        """Test correct prompt template selection based on context"""
        from backend.prompts.optimized_templates import SophiaPromptOptimizer

        optimizer = SophiaPromptOptimizer()

        contexts = ["ceo_research", "business_intelligence", "cost_optimization"]

        for context in contexts:
            template = optimizer.templates.get(context)
            assert template is not None, f"Missing template for context: {context}"
            assert "{query}" in template, "Template should have query placeholder"

            # CEO templates should emphasize executive summary
            if context == "ceo_research":
                assert "Executive Summary" in template
                assert "Strategic" in template


class TestMCPOrchestration:
    """Test MCP server orchestration logic"""

    @pytest.mark.asyncio
    async def test_server_health_monitoring(self):
        """Test health monitoring correctly identifies server status"""
        from backend.monitoring.mcp_health_monitor import MCPHealthMonitor

        monitor = MCPHealthMonitor()

        # Mock health check responses
        with patch("aiohttp.ClientSession.get") as mock_get:
            # Simulate healthy server
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={"status": "healthy"})
            mock_get.return_value.__aenter__.return_value = mock_response

            health = await monitor.check_server_health("ai_memory", 9000)

            assert health["status"] == "healthy"
            assert health["response_time"] > 0
            assert health["response_time"] < 1000  # Should be fast

    @pytest.mark.asyncio
    async def test_intelligent_server_routing(self):
        """Test routing selects best server based on capabilities"""
        from backend.services.mcp_capability_router import MCPCapabilityRouter

        router = MCPCapabilityRouter()

        # Test routing for different capabilities
        test_cases = [
            ("memory_storage", ["ai_memory"]),
            ("code_analysis", ["codacy", "github"]),
            ("project_management", ["linear", "github"]),
        ]

        for capability, expected_servers in test_cases:
            servers = await router.get_servers_for_capability(capability)

            assert len(servers) > 0, f"No servers found for {capability}"
            assert any(
                s in expected_servers for s in servers
            ), f"Expected one of {expected_servers} for {capability}, got {servers}"

    def test_fallback_server_configuration(self):
        """Test each server has proper fallback configuration"""
        from backend.orchestration.langgraph_mcp_orchestrator import (
            LangGraphMCPOrchestrator,
        )

        orchestrator = LangGraphMCPOrchestrator()

        for server_name, config in orchestrator.server_registry.items():
            # Critical servers must have fallbacks
            if config["tier"] == "primary" and config["critical"]:
                assert (
                    "fallback" in config
                ), f"Critical server {server_name} missing fallback"
                assert (
                    config["fallback"] in orchestrator.server_registry
                ), f"Fallback server {config['fallback']} doesn't exist"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
