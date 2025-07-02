#!/usr/bin/env python3
"""
Test startup script to debug import and MCP configuration issues
"""

import sys
import os
import traceback
from pathlib import Path

def test_imports():
    """Test critical imports"""
    print("🔍 Testing critical imports...")
    
    try:
        # Test basic backend imports
        print("  ✓ Testing backend imports...")
        from backend.core.auto_esc_config import get_config_value
        print("    ✓ auto_esc_config imported successfully")
        
        # Test MCP server imports
        print("  ✓ Testing MCP server imports...")
        from backend.mcp_servers.enhanced_ai_memory_mcp_server import EnhancedAiMemoryMCPServer
        print("    ✓ EnhancedAiMemoryMCPServer imported successfully")
        
        # Test service imports
        print("  ✓ Testing service imports...")
        from backend.services.mcp_orchestration_service import get_orchestration_service
        print("    ✓ MCP orchestration service imported successfully")
        
        return True
        
    except Exception as e:
        print(f"    ❌ Import failed: {e}")
        traceback.print_exc()
        return False

def test_mcp_configuration():
    """Test MCP configuration loading"""
    print("\n🔧 Testing MCP configuration...")
    
    try:
        from backend.services.mcp_orchestration_service import get_orchestration_service
        
        # Get the service (this will create it if needed)
        service = get_orchestration_service()
        print(f"    ✓ MCP orchestration service created: {len(service.servers)} servers configured")
        
        # Test server status
        for name, server in service.servers.items():
            print(f"    📡 Server {name}: port {server.port}, status {server.status}")
            
        return True
        
    except Exception as e:
        print(f"    ❌ MCP configuration failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("🧪 Sophia AI Startup Diagnostic Test")
    print("=" * 50)
    
    # Test environment
    print(f"Python version: {sys.version}")
    print(f"Working directory: {os.getcwd()}")
    
    # Run tests
    tests = [
        ("Import Test", test_imports),
        ("MCP Configuration Test", test_mcp_configuration), 
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n📊 Test Results Summary")
    print("=" * 30)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 All tests passed! The application should start successfully.")
        return 0
    else:
        print(f"\n⚠️  {len(results) - passed} test(s) failed. Please fix the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 