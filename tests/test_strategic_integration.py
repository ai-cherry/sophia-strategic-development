"""
Strategic Integration Test Suite
Comprehensive testing for all five components
"""
import asyncio
import pytest
from backend.services.router_service import RouterService
from backend.services.unified_mcp_router import UnifiedMCPRouter
from backend.services.n8n_orchestrator import IntelligentN8NOrchestrator
from backend.services.agent_factory import LangGraphAgentFactory

class TestStrategicIntegration:
    
    @pytest.mark.asyncio
    async def test_router_performance(self):
        """Test router meets performance targets"""
        router = RouterService()
        
        start_time = asyncio.get_event_loop().time()
        result = await router.route_and_execute("Test query", {"complexity": "medium"})
        end_time = asyncio.get_event_loop().time()
        
        latency_ms = (end_time - start_time) * 1000
        assert latency_ms < 180, f"Router latency {latency_ms}ms exceeds 180ms target"
        assert result["routing_decision"].confidence > 0.8
        
    @pytest.mark.asyncio
    async def test_mcp_consolidation(self):
        """Test MCP server consolidation"""
        mcp_router = UnifiedMCPRouter()
        
        # Test routing to different capabilities
        result1 = await mcp_router.route_request("PROJECT_MANAGEMENT", {"action": "list_issues"})
        result2 = await mcp_router.route_request("CRM", {"action": "get_deals"})
        
        assert result1["routed_to"] in ["linear", "asana", "github"]
        assert result2["routed_to"] in ["hubspot"]
        
    @pytest.mark.asyncio
    async def test_n8n_workflow_creation(self):
        """Test N8N workflow creation from NLP"""
        orchestrator = IntelligentN8NOrchestrator()
        
        result = await orchestrator.create_workflow_from_nlp(
            "Create daily revenue report and send to Slack"
        )
        
        assert result["deployment_status"] == "success"
        assert "workflow_id" in result
        assert result["workflow_url"].startswith("https://")
        
    @pytest.mark.asyncio
    async def test_agent_factory(self):
        """Test agent creation and deployment"""
        factory = LangGraphAgentFactory()
        
        result = await factory.create_agent_from_description(
            "Monitor customer health and alert on issues"
        )
        
        assert result["deployment_status"] == "success"
        assert result["test_results"]["success"] == True
        assert "agent_id" in result
        
    @pytest.mark.asyncio
    async def test_end_to_end_integration(self):
        """Test complete integration flow"""
        # Test user request → router → MCP → workflow → agent
        router = RouterService()
        mcp_router = UnifiedMCPRouter()
        orchestrator = IntelligentN8NOrchestrator()
        
        # Simulate user request
        user_query = "Analyze recent deals for fraud patterns and create alerts"
        
        # Route through intelligent router
        router_result = await router.route_and_execute(user_query)
        assert router_result["model_used"] in ["claude-4-sonnet", "grok-4"]
        
        # Route through MCP consolidation
        mcp_result = await mcp_router.route_request("CRM", {"action": "fraud_analysis"})
        assert mcp_result["capability"] == "CRM"
        
        # Create workflow for automation
        workflow_result = await orchestrator.create_workflow_from_nlp(
            "Automate fraud detection alerts"
        )
        assert workflow_result["deployment_status"] == "success"
        
        print("✅ End-to-end integration test passed!")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
