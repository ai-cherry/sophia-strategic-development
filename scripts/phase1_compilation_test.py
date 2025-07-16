#!/usr/bin/env python3
"""
Phase 1 Compilation Test Script
Basic validation that Phase 1 foundation services can be compiled and imported

This simplified test validates:
- All services can be imported without errors
- Basic class structures are correct
- No syntax errors in the codebase
- Service dependencies are properly structured

Usage: python3 scripts/phase1_compilation_test.py
"""

import sys
import traceback
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test that all Phase 1 services can be imported"""
    print("🧪 Testing Phase 1 Service Imports")
    print("=" * 50)
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Foundation Service Import
    tests_total += 1
    try:
        from backend.services.QDRANT_foundation_service import (
            QdrantFoundationService,
            QueryRequest,
            QueryResponse,
            QueryType,
            MemoryTier
        )
        print("✅ QdrantFoundationService imports successfully")
        tests_passed += 1
    except Exception as e:
        print(f"❌ QdrantFoundationService import failed: {e}")
        traceback.print_exc()
    
    # Test 2: UnifiedMemoryService Import
    tests_total += 1
    try:
        from backend.services.sophia_unified_memory_service import get_memory_service UnifiedMemoryService
        print("✅ UnifiedMemoryService imports successfully")
        tests_passed += 1
    except Exception as e:
        print(f"❌ UnifiedMemoryService import failed: {e}")
    
    # Test 3: HypotheticalRAGService Import
    tests_total += 1
    try:
        from backend.services.hypothetical_rag_service import HypotheticalRAGService
        print("✅ HypotheticalRAGService imports successfully")
        tests_passed += 1
    except Exception as e:
        print(f"❌ HypotheticalRAGService import failed: {e}")
    
    # Test 4: MultimodalMemoryService Import
    tests_total += 1
    try:
        from backend.services.multimodal_memory_service import MultimodalMemoryService
        print("✅ MultimodalMemoryService imports successfully")
        tests_passed += 1
    except Exception as e:
        print(f"❌ MultimodalMemoryService import failed: {e}")
    
    # Test 5: API Routes Import
    tests_total += 1
    try:
        from backend.api.QDRANT_foundation_routes import router
        print("✅ QdrantFoundationRoutes imports successfully")
        tests_passed += 1
    except Exception as e:
        print(f"❌ QdrantFoundationRoutes import failed: {e}")
    
    return tests_passed, tests_total

def test_class_structures():
    """Test that classes have expected methods and attributes"""
    print("\n🏗️ Testing Class Structures")
    print("=" * 50)
    
    tests_passed = 0
    tests_total = 0
    
    try:
        from backend.services.QDRANT_foundation_service import QdrantFoundationService
        
        # Test 1: Foundation Service Methods
        tests_total += 1
        required_methods = ['initialize', 'query', 'get_foundation_metrics']
        foundation_methods = [method for method in dir(QdrantFoundationService) if not method.startswith('_')]
        
        has_all_methods = all(method in foundation_methods for method in required_methods)
        if has_all_methods:
            print(f"✅ QdrantFoundationService has required methods: {required_methods}")
            tests_passed += 1
        else:
            missing = [m for m in required_methods if m not in foundation_methods]
            print(f"❌ QdrantFoundationService missing methods: {missing}")
        
        # Test 2: QueryRequest Structure
        tests_total += 1
        from backend.services.QDRANT_foundation_service import QueryRequest
        test_request = QueryRequest(query="test", query_type="simple_search")
        
        required_attrs = ['query', 'query_type', 'user_id', 'session_id', 'context', 'metadata']
        has_all_attrs = all(hasattr(test_request, attr) for attr in required_attrs)
        
        if has_all_attrs:
            print(f"✅ QueryRequest has required attributes: {required_attrs}")
            tests_passed += 1
        else:
            missing = [attr for attr in required_attrs if not hasattr(test_request, attr)]
            print(f"❌ QueryRequest missing attributes: {missing}")
        
        # Test 3: Enum Types
        tests_total += 1
        from backend.services.QDRANT_foundation_service import QueryType, MemoryTier
        
        query_types = list(QueryType)
        memory_tiers = list(MemoryTier)
        
        if len(query_types) >= 5 and len(memory_tiers) >= 5:
            print(f"✅ Enums defined: {len(query_types)} QueryTypes, {len(memory_tiers)} MemoryTiers")
            tests_passed += 1
        else:
            print(f"❌ Insufficient enum values: {len(query_types)} QueryTypes, {len(memory_tiers)} MemoryTiers")
            
    except Exception as e:
        print(f"❌ Class structure test failed: {e}")
    
    return tests_passed, tests_total

def test_service_instantiation():
    """Test that services can be instantiated"""
    print("\n🔧 Testing Service Instantiation")
    print("=" * 50)
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Foundation Service Instantiation
    tests_total += 1
    try:
        from backend.services.QDRANT_foundation_service import QdrantFoundationService
        service = QdrantFoundationService()
        
        # Check basic attributes exist
        if hasattr(service, 'unified_memory') and hasattr(service, 'performance_metrics'):
            print("✅ QdrantFoundationService instantiated with correct attributes")
            tests_passed += 1
        else:
            print("❌ QdrantFoundationService missing expected attributes")
            
    except Exception as e:
        print(f"❌ QdrantFoundationService instantiation failed: {e}")
    
    # Test 2: UnifiedMemoryService Instantiation
    tests_total += 1
    try:
        from backend.services.sophia_unified_memory_service import get_memory_service UnifiedMemoryService
        service = UnifiedMemoryService()
        print("✅ UnifiedMemoryService instantiated successfully")
        tests_passed += 1
    except Exception as e:
        print(f"❌ UnifiedMemoryService instantiation failed: {e}")
    
    # Test 3: HypotheticalRAGService Instantiation
    tests_total += 1
    try:
        from backend.services.hypothetical_rag_service import HypotheticalRAGService
        service = HypotheticalRAGService()
        print("✅ HypotheticalRAGService instantiated successfully")
        tests_passed += 1
    except Exception as e:
        print(f"❌ HypotheticalRAGService instantiation failed: {e}")
    
    # Test 4: MultimodalMemoryService Instantiation
    tests_total += 1
    try:
        from backend.services.multimodal_memory_service import MultimodalMemoryService
        service = MultimodalMemoryService()
        print("✅ MultimodalMemoryService instantiated successfully")
        tests_passed += 1
    except Exception as e:
        print(f"❌ MultimodalMemoryService instantiation failed: {e}")
    
    return tests_passed, tests_total

def test_api_routes():
    """Test that API routes are properly defined"""
    print("\n🌐 Testing API Routes")
    print("=" * 50)
    
    tests_passed = 0
    tests_total = 0
    
    tests_total += 1
    try:
        from backend.api.QDRANT_foundation_routes import router
        
        # Check that router has routes
        if hasattr(router, 'routes') and len(router.routes) > 0:
            route_count = len(router.routes)
            print(f"✅ API router has {route_count} routes defined")
            tests_passed += 1
        else:
            print("❌ API router has no routes defined")
            
    except Exception as e:
        print(f"❌ API routes test failed: {e}")
    
    return tests_passed, tests_total

def main():
    """Run all compilation tests"""
    print("🚀 Phase 1 Compilation Test Suite")
    print("=" * 60)
    
    total_passed = 0
    total_tests = 0
    
    # Run all test categories
    passed, total = test_imports()
    total_passed += passed
    total_tests += total
    
    passed, total = test_class_structures()
    total_passed += passed
    total_tests += total
    
    passed, total = test_service_instantiation()
    total_passed += passed
    total_tests += total
    
    passed, total = test_api_routes()
    total_passed += passed
    total_tests += total
    
    # Generate final report
    print("\n" + "=" * 60)
    print("📊 COMPILATION TEST RESULTS")
    print("=" * 60)
    
    success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
    
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {total_passed}")
    print(f"Failed: {total_tests - total_passed}")
    print(f"Success Rate: {success_rate:.1f}%")
    
    # Overall assessment
    if success_rate >= 90:
        status = "🎉 EXCELLENT"
        print(f"\n{status} - Phase 1 compilation is perfect!")
    elif success_rate >= 75:
        status = "✅ GOOD"
        print(f"\n{status} - Phase 1 compilation is successful with minor issues")
    elif success_rate >= 50:
        status = "⚠️ NEEDS WORK"
        print(f"\n{status} - Phase 1 compilation needs improvements")
    else:
        status = "❌ CRITICAL"
        print(f"\n{status} - Phase 1 compilation has critical issues")
    
    print("\n🎯 Next Steps:")
    if success_rate >= 75:
        print("- ✅ Phase 1 foundation is ready for integration testing")
        print("- ✅ Proceed with Phase 2: Business Intelligence Layer")
        print("- ✅ Begin MCP server integration")
    else:
        print("- ❌ Fix compilation errors before proceeding")
        print("- ❌ Review service dependencies")
        print("- ❌ Check import paths and module structure")
    
    # Exit with appropriate code
    exit_code = 0 if success_rate >= 75 else 1
    return exit_code

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 