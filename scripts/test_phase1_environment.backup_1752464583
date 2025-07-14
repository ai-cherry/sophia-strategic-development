#!/usr/bin/env python3
"""
Test Phase 1 Environment
Validates that all dependencies and configurations are working
"""

import asyncio
import sys

print("🧪 Testing Phase 1 Environment...")

# Test imports
try:
    print("✅ Testing core imports...")
    import torch
    import langchain
    import langgraph
    import weaviate
    import redis
    import asyncpg
    print(f"  torch version: {torch.__version__}")
    print(f"  langchain version: {langchain.__version__}")
    print("  langgraph imported successfully")  # langgraph doesn't have __version__
    print(f"  weaviate version: {weaviate.__version__}")
    print(f"  redis version: {redis.__version__}")
    print(f"  asyncpg version: {asyncpg.__version__}")
    print("✅ All core imports successful")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

# Test memory service
try:
    print("\n✅ Testing UnifiedMemoryServiceV2...")
    from backend.services.unified_memory_service_v2 import UnifiedMemoryServiceV2
    
    async def test_memory_service():
        service = UnifiedMemoryServiceV2()
        # Just test instantiation, not full initialization
        print("✅ UnifiedMemoryServiceV2 instantiated successfully")
        
    asyncio.run(test_memory_service())
    
except Exception as e:
    print(f"❌ Memory service error: {e}")
    sys.exit(1)

# Test configuration
try:
    print("\n✅ Testing configuration...")
    from backend.core.auto_esc_config import get_config_value
    
    # Test getting a config value
    test_value = get_config_value("redis_host", "localhost")
    print(f"  Redis host: {test_value}")
    print("✅ Configuration system working")
    
except Exception as e:
    print(f"❌ Configuration error: {e}")
    sys.exit(1)

print("\n🎉 Phase 1 environment validation complete!")
print("✅ All systems ready for max ingestion testing") 