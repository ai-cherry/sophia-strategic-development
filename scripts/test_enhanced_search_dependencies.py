#!/usr/bin/env python3
"""
Test Enhanced Search Dependencies
Validates that all critical dependencies for the enhanced search service can be imported
"""

import sys
import logging
from typing import List, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_core_dependencies() -> List[Tuple[str, bool, str]]:
    """Test core Python dependencies"""
    results = []
    
    core_deps = [
        ("asyncio", "asyncio"),
        ("aiohttp", "aiohttp"),
        ("enum", "enum"),
        ("dataclasses", "dataclasses"),
        ("typing", "typing"),
        ("json", "json"),
        ("logging", "logging"),
        ("datetime", "datetime"),
    ]
    
    for name, module in core_deps:
        try:
            __import__(module)
            results.append((name, True, "✅ Core dependency available"))
        except ImportError as e:
            results.append((name, False, f"❌ Missing: {e}"))
    
    return results

def test_enhanced_search_dependencies() -> List[Tuple[str, bool, str]]:
    """Test enhanced search specific dependencies"""
    results = []
    
    search_deps = [
        ("Playwright", "playwright"),
        ("BeautifulSoup", "bs4"),
        ("Requests", "requests"),
        ("Redis", "redis"),
        ("SQLAlchemy", "sqlalchemy"),
    ]
    
    for name, module in search_deps:
        try:
            __import__(module)
            results.append((name, True, "✅ Search dependency available"))
        except ImportError as e:
            results.append((name, False, f"❌ Missing: {e}"))
    
    return results

def test_ai_dependencies() -> List[Tuple[str, bool, str]]:
    """Test AI/ML dependencies"""
    results = []
    
    ai_deps = [
        ("OpenAI", "openai"),
        ("Anthropic", "anthropic"),
        ("Sentence Transformers", "sentence_transformers"),
    ]
    
    for name, module in ai_deps:
        try:
            __import__(module)
            results.append((name, True, "✅ AI dependency available"))
        except ImportError as e:
            results.append((name, False, f"❌ Missing: {e}"))
    
    return results

def test_configuration_access() -> List[Tuple[str, bool, str]]:
    """Test configuration access"""
    results = []
    
    try:
        from backend.core.auto_esc_config import get_config_value
        
        # Test basic configuration access
        test_val = get_config_value("test_key", "default_value")
        if test_val == "default_value":
            results.append(("Config Access", True, "✅ Configuration system working"))
        else:
            results.append(("Config Access", True, f"✅ Configuration system working (got: {test_val})"))
            
    except ImportError as e:
        results.append(("Config Access", False, f"❌ Config import failed: {e}"))
    except Exception as e:
        results.append(("Config Access", False, f"❌ Config error: {e}"))
    
    return results

def test_enhanced_search_imports() -> List[Tuple[str, bool, str]]:
    """Test enhanced search service imports with graceful degradation"""
    results = []
    
    try:
        # Test the core enhanced search enums and classes
        import sys
        import os
        
        # Add the project root to Python path
        project_root = os.path.dirname(os.path.abspath(__file__))
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
        
        # Try to import the enhanced search service components
        try:
            from backend.services.enhanced_search_service import SearchTier
            results.append(("SearchTier Enum", True, "✅ SearchTier enum imported"))
        except ImportError as e:
            results.append(("SearchTier Enum", False, f"❌ SearchTier import failed: {e}"))
        
        try:
            from backend.services.enhanced_search_service import SearchProvider  
            results.append(("SearchProvider Enum", True, "✅ SearchProvider enum imported"))
        except ImportError as e:
            results.append(("SearchProvider Enum", False, f"❌ SearchProvider import failed: {e}"))
        
        try:
            from backend.services.enhanced_search_service import SearchRequest
            results.append(("SearchRequest Model", True, "✅ SearchRequest model imported"))
        except ImportError as e:
            results.append(("SearchRequest Model", False, f"❌ SearchRequest import failed: {e}"))
        
        # Try to import the full service (this might fail due to missing dependencies)
        try:
            from backend.services.enhanced_search_service import EnhancedSearchService
            results.append(("EnhancedSearchService", True, "✅ Full service imported"))
        except ImportError as e:
            results.append(("EnhancedSearchService", False, f"⚠️ Service import failed (expected): {e}"))
        
    except Exception as e:
        results.append(("Enhanced Search Imports", False, f"❌ Critical error: {e}"))
    
    return results

def test_mcp_compatibility() -> List[Tuple[str, bool, str]]:
    """Test MCP compatibility layer"""
    results = []
    
    try:
        from backend.core.mcp_compatibility import get_mcp_server_class
        server_class = get_mcp_server_class()
        results.append(("MCP Compatibility", True, f"✅ MCP compatibility layer working (class: {server_class.__name__})"))
    except ImportError as e:
        results.append(("MCP Compatibility", False, f"❌ MCP compatibility failed: {e}"))
    except Exception as e:
        results.append(("MCP Compatibility", False, f"❌ MCP error: {e}"))
    
    return results

def run_all_tests() -> bool:
    """Run all dependency tests"""
    logger.info("🚀 Testing Enhanced Search Dependencies")
    logger.info("=" * 60)
    
    all_results = []
    
    # Run all test categories
    test_categories = [
        ("Core Dependencies", test_core_dependencies),
        ("Enhanced Search Dependencies", test_enhanced_search_dependencies),
        ("AI Dependencies", test_ai_dependencies),
        ("Configuration Access", test_configuration_access),
        ("Enhanced Search Imports", test_enhanced_search_imports),
        ("MCP Compatibility", test_mcp_compatibility),
    ]
    
    total_tests = 0
    passed_tests = 0
    
    for category_name, test_func in test_categories:
        logger.info(f"\n📋 {category_name}")
        logger.info("-" * 40)
        
        try:
            results = test_func()
            for name, success, message in results:
                logger.info(f"  {message}")
                total_tests += 1
                if success:
                    passed_tests += 1
                    
            all_results.extend(results)
            
        except Exception as e:
            logger.error(f"  ❌ Test category failed: {e}")
            total_tests += 1
    
    # Generate summary
    logger.info("\n" + "=" * 60)
    logger.info("📊 DEPENDENCY TEST SUMMARY")
    logger.info("=" * 60)
    
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    logger.info(f"✅ Tests Passed: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
    
    # Critical dependencies check
    critical_deps = ["asyncio", "aiohttp", "Config Access", "MCP Compatibility"]
    critical_passed = 0
    
    for name, success, _ in all_results:
        if name in critical_deps and success:
            critical_passed += 1
    
    critical_rate = (critical_passed / len(critical_deps) * 100)
    logger.info(f"🎯 Critical Dependencies: {critical_passed}/{len(critical_deps)} ({critical_rate:.1f}%)")
    
    if critical_rate >= 75:
        logger.info("🎉 DEPENDENCY TEST PASSED - Enhanced search ready for deployment!")
        return True
    else:
        logger.error("❌ DEPENDENCY TEST FAILED - Critical dependencies missing")
        return False

def main():
    """Main function"""
    success = run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main()) 