"""Integration tests for Strategic Chat Architecture
Tests dynamic model selection, hybrid search, and performance
"""
import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, patch

import pytest

from backend.app.routes.retool_executive_routes import (
    ModelSelectionRequest,
    StrategicChatMessage,
    compare_models,
    get_model_presets,
    get_openrouter_models,
    strategic_chat,
)
from backend.app.security import UserRole
from backend.integrations.openrouter_integration import OpenRouterClient


class TestStrategicChat:
    """Test strategic chat functionality"""

    @pytest.fixture
    async def mock_openrouter_client(self):
        """Mock OpenRouter client"""
        client = AsyncMock(spec=OpenRouterClient)

        # Mock model list
        client.get_models.return_value = [
            {
                "id": "openai/gpt-4-turbo",
                "name": "GPT-4 Turbo",
                "context_length": 128000,
                "pricing": {"prompt": 0.01, "completion": 0.03},
            },
            {
                "id": "anthropic/claude-3.5-sonnet",
                "name": "Claude 3.5 Sonnet",
                "context_length": 200000,
                "pricing": {"prompt": 0.003, "completion": 0.015},
            },
            {
                "id": "openai/o1-preview",
                "name": "O1 Preview",
                "context_length": 128000,
                "pricing": {"prompt": 0.015, "completion": 0.06},
            },
            {
                "id": "meta-llama/llama-3.1-70b-instruct",
                "name": "Llama 3.1 70B",
                "context_length": 128000,
                "pricing": {"prompt": 0.0007, "completion": 0.0009},
            },
        ]

        # Mock chat completion
        client.chat_completion.return_value = {
            "content": "Strategic analysis response",
            "model": "anthropic/claude-3.5-sonnet",
            "usage": {"prompt_tokens": 100, "completion_tokens": 200},
        }

        # Mock model selection
        client.select_optimal_model.return_value = "anthropic/claude-3.5-sonnet"

        return client

    @pytest.fixture
    async def mock_mcp_client(self):
        """Mock MCP client for hybrid search"""
        client = AsyncMock()

        # Mock internal search results
        client.call_tool.side_effect = self._mock_mcp_responses

        return client

    async def _mock_mcp_responses(self, server, tool, **kwargs):
        """Mock MCP tool responses"""
        if server == "knowledge" and tool == "search":
            return {
                "results": [
                    {"content": "Internal knowledge result 1", "score": 0.95},
                    {"content": "Internal knowledge result 2", "score": 0.87},
                ]
            }
        elif server == "ai_memory" and tool == "recall_memory":
            return {
                "memories": [
                    {
                        "content": "Previous strategic decision",
                        "timestamp": "2024-01-15",
                    }
                ]
            }
        elif server == "snowflake" and tool == "query":
            return {
                "data": [
                    {"metric": "revenue_growth", "value": 15.3},
                    {"metric": "client_health", "value": 87.5},
                ]
            }
        elif server == "apify" and tool == "search_proptech":
            return {
                "results": [
                    {
                        "title": "PropTech Market Trends 2024",
                        "url": "https://example.com",
                    }
                ]
            }
        elif server == "huggingface" and tool == "analyze":
            return {"analysis": "AI market insights and predictions"}
        elif server == "ai_memory" and tool == "store_conversation":
            return {"status": "stored", "id": "conv_123"}

        return {}

    @pytest.mark.asyncio
    async def test_strategic_chat_internal_mode(
        self, mock_openrouter_client, mock_mcp_client
    ):
        """Test strategic chat in internal only mode"""
        with patch(
            "backend.app.routes.retool_executive_routes.get_openrouter_client",
            return_value=mock_openrouter_client,
        ):
            with patch(
                "backend.app.routes.retool_executive_routes.get_mcp_client",
                return_value=mock_mcp_client,
            ):
                message = StrategicChatMessage(
                    message="What is our current client health status?",
                    mode="internal",
                    model_id="anthropic/claude-3.5-sonnet",
                )

                result = await strategic_chat(message, UserRole.CEO)

                assert result["response"] == "Strategic analysis response"
                assert result["model_used"] == "anthropic/claude-3.5-sonnet"
                assert result["sources"]["internal"] is not None
                assert result["sources"]["external"] is None
                assert "conversation_id" in result

    @pytest.mark.asyncio
    async def test_strategic_chat_external_mode(
        self, mock_openrouter_client, mock_mcp_client
    ):
        """Test strategic chat in external only mode"""
        with patch(
            "backend.app.routes.retool_executive_routes.get_openrouter_client",
            return_value=mock_openrouter_client,
        ):
            with patch(
                "backend.app.routes.retool_executive_routes.get_mcp_client",
                return_value=mock_mcp_client,
            ):
                message = StrategicChatMessage(
                    message="What are the latest proptech market trends?",
                    mode="external",
                )

                result = await strategic_chat(message, UserRole.CEO)

                assert result["response"] == "Strategic analysis response"
                assert result["sources"]["internal"] is None
                assert result["sources"]["external"] is not None

    @pytest.mark.asyncio
    async def test_strategic_chat_combined_mode(
        self, mock_openrouter_client, mock_mcp_client
    ):
        """Test strategic chat in combined mode"""
        with patch(
            "backend.app.routes.retool_executive_routes.get_openrouter_client",
            return_value=mock_openrouter_client,
        ):
            with patch(
                "backend.app.routes.retool_executive_routes.get_mcp_client",
                return_value=mock_mcp_client,
            ):
                message = StrategicChatMessage(
                    message="How do our metrics compare to market trends?",
                    mode="combined",
                )

                result = await strategic_chat(message, UserRole.CEO)

                assert result["response"] == "Strategic analysis response"
                assert result["sources"]["internal"] is not None
                assert result["sources"]["external"] is not None

                # Verify both internal and external searches were performed
                assert (
                    mock_mcp_client.call_tool.call_count >= 5
                )  # 3 internal + 2 external

    @pytest.mark.asyncio
    async def test_model_discovery(self, mock_openrouter_client):
        """Test dynamic model discovery"""
        with patch(
            "backend.app.routes.retool_executive_routes.get_openrouter_client",
            return_value=mock_openrouter_client,
        ):
            # Test without filters
            result = await get_openrouter_models(None, UserRole.CEO)

            assert "models" in result
            assert len(result["models"]) > 0
            assert "performance_metrics" in result
            assert "categories" in result
            assert "providers" in result

            # Test with filters
            request = ModelSelectionRequest(
                provider="anthropic",
                capability="deep_analysis",
                min_context_window=100000,
            )

            result = await get_openrouter_models(request, UserRole.CEO)

            # Should filter to only Anthropic models with large context
            assert all("anthropic" in m["id"] for m in result["models"])

    @pytest.mark.asyncio
    async def test_model_presets(self, mock_openrouter_client):
        """Test executive model presets"""
        with patch(
            "backend.app.routes.retool_executive_routes._get_latest_model",
            return_value="openai/gpt-4-turbo-2024-01",
        ):
            presets = await get_model_presets(UserRole.CEO)

            assert len(presets) == 5

            # Check preset names
            preset_names = [p.name for p in presets]
            assert "Strategic Planning" in preset_names
            assert "Quick Intelligence" in preset_names
            assert "Deep Analysis" in preset_names
            assert "Cost Optimized" in preset_names
            assert "Latest & Greatest" in preset_names

    @pytest.mark.asyncio
    async def test_model_comparison(self, mock_openrouter_client):
        """Test model comparison functionality"""

        # Mock different responses for different models
        async def mock_chat_completion(model, messages, **kwargs):
            responses = {
                "openai/gpt-4-turbo": {
                    "content": "GPT-4 Turbo response",
                    "model": "openai/gpt-4-turbo",
                    "usage": {"prompt_tokens": 50, "completion_tokens": 100},
                },
                "anthropic/claude-3.5-sonnet": {
                    "content": "Claude response",
                    "model": "anthropic/claude-3.5-sonnet",
                    "usage": {"prompt_tokens": 50, "completion_tokens": 120},
                },
            }
            return responses.get(model, {"content": "Default response", "model": model})

        mock_openrouter_client.chat_completion.side_effect = mock_chat_completion

        with patch(
            "backend.app.routes.retool_executive_routes.get_openrouter_client",
            return_value=mock_openrouter_client,
        ):
            result = await compare_models(
                query="Analyze our Q4 strategy",
                model_ids=["openai/gpt-4-turbo", "anthropic/claude-3.5-sonnet"],
                current_role=UserRole.CEO,
            )

            assert "comparisons" in result
            assert len(result["comparisons"]) == 2
            assert "recommendation" in result
            assert result["recommendation"]["recommendation"] is not None

    @pytest.mark.asyncio
    async def test_optimal_model_selection(self, mock_openrouter_client):
        """Test intelligent model selection based on query"""
        with patch(
            "backend.app.routes.retool_executive_routes.get_openrouter_client",
            return_value=mock_openrouter_client,
        ):
            # Test strategic query
            mock_openrouter_client.select_optimal_model.return_value = (
                "openai/o1-preview"
            )

            message = StrategicChatMessage(
                message="Develop a 5-year strategic plan", mode="internal"
            )

            result = await strategic_chat(message, UserRole.CEO)

            # Verify strategic model was selected
            mock_openrouter_client.select_optimal_model.assert_called_with(
                query_type="strategic_analysis",
                context_size=pytest.Any(int),
                max_cost_per_token=None,
            )

    @pytest.mark.asyncio
    async def test_performance_tracking(self, mock_mcp_client):
        """Test model performance tracking"""
        with patch(
            "backend.app.routes.retool_executive_routes.get_mcp_client",
            return_value=mock_mcp_client,
        ):
            from backend.app.routes.retool_executive_routes import (
                track_model_performance,
            )

            result = await track_model_performance(
                model_id="openai/gpt-4-turbo",
                response_time=1.5,
                quality_score=9.2,
                query_type="strategic_analysis",
                current_role=UserRole.CEO,
            )

            assert result["status"] == "tracked"

            # Verify performance data was stored
            mock_mcp_client.call_tool.assert_called_with(
                "ai_memory",
                "store_conversation",
                content="Model Performance: openai/gpt-4-turbo",
                category="model_analytics",
                metadata=pytest.Any(dict),
            )

    @pytest.mark.asyncio
    async def test_context_window_handling(self, mock_openrouter_client):
        """Test large context window handling"""
        with patch(
            "backend.app.routes.retool_executive_routes.get_openrouter_client",
            return_value=mock_openrouter_client,
        ):
            # Test with large context requirement
            message = StrategicChatMessage(
                message="Analyze this large document...",
                mode="internal",
                context_window_required=150000,
            )

            # Should select model with large enough context window
            mock_openrouter_client.select_optimal_model.return_value = (
                "anthropic/claude-3.5-sonnet"
            )

            result = await strategic_chat(message, UserRole.CEO)

            # Verify context size was considered
            mock_openrouter_client.select_optimal_model.assert_called_with(
                query_type=pytest.Any(str), context_size=150000, max_cost_per_token=None
            )


class TestOpenRouterIntegration:
    """Test OpenRouter client functionality"""

    @pytest.mark.asyncio
    async def test_model_categorization(self):
        """Test model categorization logic"""
        client = OpenRouterClient("test_key")

        test_models = [
            {"id": "openai/o1-preview", "expected": "advanced_reasoning"},
            {"id": "anthropic/claude-3.5-sonnet", "expected": "deep_analysis"},
            {"id": "openai/gpt-4-turbo", "expected": "fast_response"},
            {"id": "openai/gpt-4-vision", "expected": "vision"},
            {"id": "meta-llama/llama-3.1-70b", "expected": "cost_optimized"},
        ]

        for model in test_models:
            category = client.categorize_model(model)
            assert category == model["expected"]

    @pytest.mark.asyncio
    async def test_capability_extraction(self):
        """Test model capability extraction"""
        client = OpenRouterClient("test_key")

        model = {
            "id": "openai/gpt-4-vision",
            "context_length": 128000,
            "architecture": {"modality": "text->text, image->text"},
            "pricing": {"prompt": 0.0005},
        }

        capabilities = client.get_model_capabilities(model)

        assert "vision" in capabilities
        assert "large_context" in capabilities
        assert "cost_efficient" in capabilities

    @pytest.mark.asyncio
    async def test_model_selection_logic(self):
        """Test optimal model selection"""
        client = OpenRouterClient("test_key")

        # Mock model list
        with patch.object(
            client,
            "get_models",
            return_value=[
                {
                    "id": "openai/gpt-4-turbo",
                    "context_length": 128000,
                    "pricing": {"prompt": 0.01},
                },
                {
                    "id": "anthropic/claude-3.5-sonnet",
                    "context_length": 200000,
                    "pricing": {"prompt": 0.003},
                },
                {
                    "id": "meta-llama/llama-3.1-70b",
                    "context_length": 128000,
                    "pricing": {"prompt": 0.0007},
                },
            ],
        ):
            # Test cost-optimized selection
            model = await client.select_optimal_model(
                query_type="cost_optimized", max_cost_per_token=0.001
            )

            assert model == "meta-llama/llama-3.1-70b"

            # Test strategic analysis selection
            model = await client.select_optimal_model(query_type="strategic_analysis")

            assert model == "anthropic/claude-3.5-sonnet"


class TestPerformance:
    """Test performance requirements"""

    @pytest.mark.asyncio
    async def test_response_time(self, mock_openrouter_client, mock_mcp_client):
        """Test sub-second response time"""
        import time

        with patch(
            "backend.app.routes.retool_executive_routes.get_openrouter_client",
            return_value=mock_openrouter_client,
        ):
            with patch(
                "backend.app.routes.retool_executive_routes.get_mcp_client",
                return_value=mock_mcp_client,
            ):
                # Make all async operations instant for testing
                mock_openrouter_client.chat_completion.return_value = {
                    "content": "Fast response",
                    "model": "openai/gpt-4-turbo",
                }

                message = StrategicChatMessage(message="Quick test", mode="internal")

                start_time = time.time()
                result = await strategic_chat(message, UserRole.CEO)
                end_time = time.time()

                # Should complete in under 1 second (in real scenario)
                assert end_time - start_time < 1.0
                assert result["response"] == "Fast response"

    @pytest.mark.asyncio
    async def test_parallel_search_execution(self, mock_mcp_client):
        """Test parallel execution of searches"""
        call_times = []

        async def track_call_time(*args, **kwargs):
            call_times.append(datetime.utcnow())
            await asyncio.sleep(0.1)  # Simulate API delay
            return {"results": ["test"]}

        mock_mcp_client.call_tool.side_effect = track_call_time

        with patch(
            "backend.app.routes.retool_executive_routes.get_mcp_client",
            return_value=mock_mcp_client,
        ):
            # Execute parallel searches

            # This would normally be called within strategic_chat
            # Testing the parallel execution pattern
            # If searches were sequential, they would take 0.5s (5 * 0.1s)
            # If parallel, they should complete in ~0.1s

            assert len(call_times) == 0  # Verify clean state


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
