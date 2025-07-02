#!/usr/bin/env python3
"""Comprehensive end-to-end testing of core infrastructure."""

import asyncio
import aiohttp
import sys

async def test_infrastructure():
    """Test all core components."""
    tests = [
        ("API Gateway", "http://localhost:8000/health"),
        ("AI Memory MCP", "http://localhost:9000/health"),
        ("Codacy MCP", "http://localhost:3008/health"),
        ("GitHub MCP", "http://localhost:9003/health"),
        ("Linear MCP", "http://localhost:9004/health"),
    ]
    
    print("=== Testing Core Infrastructure ===\n")
    
    results = []
    timeout = aiohttp.ClientTimeout(total=5)
    
    async with aiohttp.ClientSession(timeout=timeout) as session:
        for name, url in tests:
            try:
                async with session.get(url) as response:
                    success = response.status == 200
                    results.append((name, success))
                    print(f"{'✅' if success else '❌'} {name}: {'OK' if success else 'FAIL'}")
            except Exception as e:
                results.append((name, False))
                print(f"❌ {name}: {e}")
    
    successful = sum(1 for _, success in results if success)
    print(f"\n=== Test Results ===")
    print(f"Passed: {successful}/{len(tests)} tests")
    
    success_rate = successful / len(tests)
    if success_rate >= 0.8:
        print("✅ Infrastructure is stable and ready for development")
    elif success_rate >= 0.6:
        print("⚠️  Infrastructure partially operational - some issues need attention")
    else:
        print("❌ Infrastructure has critical issues - immediate attention required")
    
    return success_rate >= 0.8

if __name__ == "__main__":
    success = asyncio.run(test_infrastructure())
    sys.exit(0 if success else 1)
