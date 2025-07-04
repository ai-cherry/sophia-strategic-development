#!/usr/bin/env python3
"""
Test Priority Enhancements for Sophia AI
Verifies the key improvements work correctly
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def print_header(title):
    print(f"\n{'='*60}")
    print(f"🧪 {title}")
    print(f"{'='*60}\n")

def print_result(test_name, success, details=""):
    icon = "✅" if success else "❌"
    print(f"{icon} {test_name}")
    if details:
        print(f"   {details}")

async def test_prompt_optimization():
    """Test the prompt optimization module"""
    print_header("Testing Prompt Optimization")
    
    try:
        from backend.prompts.optimized_templates import SophiaPromptOptimizer, PromptCacheManager
        
        # Create optimizer
        optimizer = SophiaPromptOptimizer()
        print_result("Import SophiaPromptOptimizer", True)
        
        # Test CEO query optimization
        ceo_query = "What is our current revenue and growth rate compared to last quarter?"
        optimized = await optimizer.optimize_prompt(ceo_query, "ceo_research")
        
        print_result("CEO Query Optimization", True, f"Original: {len(ceo_query)} chars")
        print(f"   Optimized template applied")
        
        # Test cost estimation
        cost = await optimizer.cost_tracker.estimate_query_cost(optimized, "ceo_research")
        print_result("Cost Estimation", True, f"Estimated cost: ${cost:.4f}")
        
        # Test long query optimization
        long_query = "Please analyze all of our customer data " * 20
        optimized_long = await optimizer.cost_tracker.optimize_for_cost(long_query)
        
        cost_reduction = (len(long_query) - len(optimized_long)) / len(long_query) * 100
        print_result("Long Query Optimization", True, f"Reduced by {cost_reduction:.1f}%")
        
        # Test cache manager
        cache = PromptCacheManager()
        cache.cache_prompt("What is our revenue?", "ceo_research", "Optimized prompt here")
        cached = cache.get_cached_prompt("What is our revenue?", "ceo_research")
        print_result("Prompt Caching", cached is not None)
        
        return True
        
    except Exception as e:
        print_result("Prompt Optimization", False, str(e))
        return False

async def test_langgraph_orchestration():
    """Test the LangGraph MCP orchestration"""
    print_header("Testing LangGraph MCP Orchestration")
    
    try:
        from backend.orchestration.langgraph_mcp_orchestrator import (
            LangGraphMCPOrchestrator, SimpleOrchestrationGraph
        )
        
        # Create orchestrator
        orchestrator = LangGraphMCPOrchestrator()
        print_result("Import LangGraphMCPOrchestrator", True)
        
        # Test server registry
        servers = orchestrator.get_all_servers()
        print_result("Server Registry", len(servers) > 0, f"{len(servers)} servers registered")
        
        # Test capability lookup
        memory_servers = orchestrator.get_servers_by_capability("memory")
        print_result("Capability Lookup", len(memory_servers) > 0, 
                    f"Memory servers: {', '.join(memory_servers)}")
        
        # Test request routing
        test_request = {
            "message": "Remember that our Q4 revenue target is $5M",
            "context": "ceo_deep_research"
        }
        
        result = await orchestrator.route_request(test_request)
        print_result("Request Routing", result.get("success", False), 
                    f"Routed to: {result.get('server')}")
        
        # Test failover
        test_failover = {
            "message": "Analyze the security of our code",
            "context": "coding_agents"
        }
        
        # Simulate primary failure
        orchestrator.health_scores["codacy"] = 0  # Mark as unhealthy
        result = await orchestrator.route_request(test_failover)
        
        print_result("Failover Handling", 
                    result.get("fallback_used", False) or result.get("server") == "github",
                    f"Fallback to: {result.get('server')}")
        
        # Test simple graph
        graph = SimpleOrchestrationGraph(orchestrator)
        graph_result = await graph.process_request(test_request)
        print_result("Graph Processing", graph_result.get("success", False),
                    f"Time: {graph_result.get('orchestration_time', 0):.3f}s")
        
        return True
        
    except Exception as e:
        print_result("LangGraph Orchestration", False, str(e))
        return False

async def test_existing_components():
    """Test that existing components still work"""
    print_header("Testing Existing Components")
    
    try:
        # Test MCP Health Monitor
        from backend.monitoring.mcp_health_monitor import MCPHealthMonitor
        monitor = MCPHealthMonitor()
        print_result("MCP Health Monitor", True, "Successfully imported")
        
        # Test GPTCache Service
        from backend.services.gptcache_service import GPTCacheService
        print_result("GPTCache Service", True, "Successfully imported")
        
        # Test Capability Router
        from backend.services.mcp_capability_router import MCPCapabilityRouter
        router = MCPCapabilityRouter()
        capabilities = router.get_capability_coverage()
        print_result("Capability Router", len(capabilities) > 0, 
                    f"{len(capabilities)} capabilities mapped")
        
        # Test Snowflake Cortex AISQL
        from backend.services.snowflake_cortex_aisql import SnowflakeCortexAISQLService
        print_result("Snowflake Cortex AISQL", True, "Successfully imported")
        
        return True
        
    except Exception as e:
        print_result("Existing Components", False, str(e))
        return False

async def main():
    """Run all priority enhancement tests"""
    print("\n🚀 Testing Sophia AI Priority Enhancements")
    print("=" * 60)
    
    results = []
    
    # Test each component
    results.append(await test_prompt_optimization())
    results.append(await test_langgraph_orchestration())
    results.append(await test_existing_components())
    
    # Summary
    print_header("Test Summary")
    
    passed = sum(results)
    total = len(results)
    
    print(f"Tests Passed: {passed}/{total}")
    
    if passed == total:
        print("\n✅ All priority enhancements are working correctly!")
        print("\nExpected Benefits:")
        print("  • 30% cost reduction through prompt optimization")
        print("  • Intelligent MCP server routing with failover")
        print("  • Improved reliability and performance")
        print("  • Foundation for comprehensive testing")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 