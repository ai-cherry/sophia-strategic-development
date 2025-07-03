#!/usr/bin/env python3
"""
UNIFIED CHAT SYSTEM TEST - COMPREHENSIVE TESTING

This script tests the unified chat interface and backend service
to ensure everything is working correctly.
"""

import asyncio
import json
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("unified_chat_test")

async def test_environment_setup():
    """Test environment setup and configuration"""
    logger.info("🔧 Testing environment setup...")
    
    # Check SOPHIA_AI_TOKEN
    token = os.getenv("SOPHIA_AI_TOKEN")
    if not token:
        logger.warning("Setting SOPHIA_AI_TOKEN environment variable")
        os.environ["SOPHIA_AI_TOKEN"] = "test_token_12345"
    
    # Check if we're in the correct directory
    if not Path("backend").exists():
        logger.error("❌ Backend directory not found. Run from project root.")
        return False
    
    logger.info("✅ Environment setup complete")
    return True

async def test_enhanced_chat_service():
    """Test the enhanced universal chat service"""
    logger.info("🧪 Testing Enhanced Unified Chat Service...")
    
    try:
        from backend.services.enhanced_universal_chat_service import (
            EnhancedUnifiedChatService,
            universal_chat_service
        )
        
        # Initialize the service
        await universal_chat_service.initialize()
        
        # Test basic message processing
        response = await universal_chat_service.process_chat_message(
            message="Hello, can you help me understand the Sophia AI platform?",
            user_id="test_user",
            session_id="test_session_123"
        )
        
        logger.info(f"✅ Chat service response: {response.content[:100]}...")
        logger.info(f"✅ Response metadata: {response.metadata}")
        
        # Test health status
        health = universal_chat_service.get_health_status()
        logger.info(f"✅ Service health: {health['status']}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Enhanced chat service test failed: {e}")
        return False

async def main():
    """Run all tests"""
    logger.info("🚀 Starting Unified Chat System Tests")
    logger.info("=" * 60)
    
    test_results = {}
    
    # Run tests
    tests = [
        ("Environment Setup", test_environment_setup),
        ("Enhanced Chat Service", test_enhanced_chat_service),
    ]
    
    for test_name, test_func in tests:
        logger.info(f"\n🧪 Running {test_name} test...")
        try:
            result = await test_func()
            test_results[test_name] = result
            if result:
                logger.info(f"✅ {test_name} test PASSED")
            else:
                logger.error(f"❌ {test_name} test FAILED")
        except Exception as e:
            logger.error(f"💥 {test_name} test CRASHED: {e}")
            test_results[test_name] = False
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("📊 TEST SUMMARY")
    logger.info("=" * 60)
    
    passed = sum(1 for result in test_results.values() if result)
    total = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{test_name:.<30} {status}")
    
    logger.info("-" * 60)
    logger.info(f"Overall Result: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 ALL TESTS PASSED! Unified Chat System is ready!")
        return True
    else:
        logger.error(f"💥 {total - passed} tests failed. System needs attention.")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
