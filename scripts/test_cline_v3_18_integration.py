#!/usr/bin/env python3
"""Test script for Cline v3.18 integration."""

import asyncio
import sys
import os
import json
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from backend.mcp.base.standardized_mcp_server import StandardizedMCPServer
from mcp_servers.ai_memory.enhanced_ai_memory_server import EnhancedAIMemoryServer
from mcp_servers.codacy.enhanced_codacy_server import EnhancedCodacyServer
from gemini_cli_integration.gemini_cli_provider import GeminiCLIProvider

async def test_gemini_cli():
    """Test Gemini CLI integration."""
    print("\n=== Testing Gemini CLI Integration ===")
    
    # Check if Gemini CLI is available
    result = os.system("which gemini > /dev/null 2>&1")
    if result != 0:
        print("❌ Gemini CLI not found. Please install: npm install -g @google/generative-ai-cli")
        return False
    
    print("✅ Gemini CLI found")
    
    # Test provider
    provider = GeminiCLIProvider()
    test_prompt = "Hello, this is a test"
    
    try:
        response = await provider.generate(test_prompt)
        print(f"✅ Gemini CLI response: {response[:100]}...")
        return True
    except Exception as e:
        print(f"❌ Gemini CLI error: {e}")
        return False

async def test_ai_memory_server():
    """Test enhanced AI Memory server."""
    print("\n=== Testing Enhanced AI Memory Server ===")
    
    try:
        server = EnhancedAIMemoryServer()
        
        # Test auto-discovery
        print("Testing auto-discovery...")
        await server.auto_discover_and_store({
            "type": "architecture_decision",
            "content": "Using microservices for scalability",
            "context": "system_design"
        })
        print("✅ Auto-discovery working")
        
        # Test smart recall
        print("Testing smart recall...")
        results = await server.smart_recall("microservices architecture")
        print(f"✅ Smart recall found {len(results)} results")
        
        # Test WebFetch integration
        print("Testing WebFetch integration...")
        content = await server.fetch_and_store("https://example.com")
        print("✅ WebFetch integration working")
        
        return True
        
    except Exception as e:
        print(f"❌ AI Memory server error: {e}")
        return False

async def test_codacy_server():
    """Test enhanced Codacy server."""
    print("\n=== Testing Enhanced Codacy Server ===")
    
    try:
        server = EnhancedCodacyServer()
        
        # Test real-time analysis
        print("Testing real-time analysis...")
        test_code = """
def calculate_sum(a, b):
    return a + b
"""
        analysis = await server.analyze_code_realtime(test_code)
        print(f"✅ Real-time analysis: {analysis['summary']}")
        
        # Test security scanning
        print("Testing security scanning...")
        security_results = await server.security_scan(test_code)
        print(f"✅ Security scan complete: {len(security_results)} issues found")
        
        return True
        
    except Exception as e:
        print(f"❌ Codacy server error: {e}")
        return False

async def test_standardized_server():
    """Test StandardizedMCPServer v3.18 features."""
    print("\n=== Testing StandardizedMCPServer v3.18 Features ===")
    
    try:
        # Test WebFetch
        print("Testing WebFetch...")
        server = StandardizedMCPServer()
        content = await server.webfetch("https://example.com")
        print("✅ WebFetch working")
        
        # Test self-knowledge
        print("Testing self-knowledge...")
        capabilities = await server.get_capabilities()
        print(f"✅ Self-knowledge: {len(capabilities)} capabilities")
        
        # Test model routing
        print("Testing model routing...")
        model = await server.route_to_model("Complex reasoning task", context_size=50000)
        print(f"✅ Model routing selected: {model}")
        
        return True
        
    except Exception as e:
        print(f"❌ StandardizedMCPServer error: {e}")
        return False

async def main():
    """Run all tests."""
    print("🚀 Cline v3.18 Integration Test Suite")
    print("=====================================")
    
    results = {
        "Gemini CLI": await test_gemini_cli(),
        "AI Memory Server": await test_ai_memory_server(),
        "Codacy Server": await test_codacy_server(),
        "Standardized Server": await test_standardized_server()
    }
    
    print("\n=== Test Results ===")
    passed = 0
    for test, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test}: {status}")
        if result:
            passed += 1
    
    print(f"\nTotal: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 All tests passed! Cline v3.18 integration is ready.")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
    
    return passed == len(results)

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
