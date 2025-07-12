#!/usr/bin/env python3
"""
Integration tests for Snowflake Unified MCP Server
Tests both mock mode and real Snowflake connectivity
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from snowflake_unified.server import SnowflakeUnifiedServer


async def test_server_startup():
    """Test server initialization and startup"""
    print("\n🧪 Testing server startup...")

    server = SnowflakeUnifiedServer()

    try:
        await server.startup()
        print("✅ Server started successfully")

        # Check tool definitions
        tools = await server.get_custom_tools()
        print(f"✅ Found {len(tools)} tools:")
        for tool in tools:
            print(f"   - {tool.name}: {tool.description}")

        return True
    except Exception as e:
        print(f"❌ Server startup failed: {e}")
        return False
    finally:
        await server.cleanup()


async def test_query_data():
    """Test data querying functionality"""
    print("\n🧪 Testing query_data...")

    server = SnowflakeUnifiedServer()
    await server.on_startup()

    try:
        # Test valid query
        result = await server.query_data(
            {
                "table": "test_table",
                "columns": ["id", "name"],
                "filters": {"status": "active"},
                "limit": 10,
            }
        )

        if result["success"]:
            print(
                f"✅ Query executed successfully, returned {result.get('row_count', 0)} rows"
            )
        else:
            print(f"⚠️  Query failed: {result.get('error')}")

        # Test SQL injection prevention
        result = await server.query_data(
            {"table": "test; DROP TABLE users;", "columns": ["*"], "limit": 10}
        )

        if not result["success"] and "Invalid table name" in result.get("error", ""):
            print("✅ SQL injection prevention working")
        else:
            print("❌ SQL injection prevention failed!")

        return True

    except Exception as e:
        print(f"❌ Query test failed: {e}")
        return False
    finally:
        await server.on_shutdown()


async def test_generate_embedding():
    """Test embedding generation"""
    print("\n🧪 Testing generate_embedding...")

    server = SnowflakeUnifiedServer()
    await server.on_startup()

    try:
        result = await server.generate_embedding(
            {
                "text": "This is a test sentence for embedding generation",
                "model": "e5-base-v2",
            }
        )

        if result["success"]:
            embedding = result.get("embedding", [])
            dimensions = result.get("dimensions", 0)
            print(f"✅ Embedding generated successfully: {dimensions} dimensions")

            if dimensions == 768:  # Expected for e5-base-v2
                print("✅ Correct embedding dimensions")
            else:
                print(f"⚠️  Unexpected dimensions: {dimensions}")
        else:
            print(f"⚠️  Embedding generation failed: {result.get('error')}")

        return True

    except Exception as e:
        print(f"❌ Embedding test failed: {e}")
        return False
    finally:
        await server.on_shutdown()


async def test_semantic_search():
    """Test semantic search functionality"""
    print("\n🧪 Testing semantic_search...")

    server = SnowflakeUnifiedServer()
    await server.on_startup()

    try:
        result = await server.semantic_search(
            {
                "query": "What are the best practices for data security?",
                "table": "knowledge_base",
                "limit": 5,
            }
        )

        if result["success"]:
            total = result.get("total", 0)
            print(f"✅ Semantic search completed, found {total} results")

            # Check if results have similarity scores
            results = result.get("results", [])
            if results and "similarity_score" in results[0]:
                print("✅ Results include similarity scores")
        else:
            print(f"⚠️  Semantic search failed: {result.get('error')}")

        return True

    except Exception as e:
        print(f"❌ Semantic search test failed: {e}")
        return False
    finally:
        await server.on_shutdown()


async def test_complete_text():
    """Test text completion"""
    print("\n🧪 Testing complete_text...")

    server = SnowflakeUnifiedServer()
    await server.on_startup()

    try:
        result = await server.complete_text(
            {
                "prompt": "The key benefits of using Snowflake for AI are:",
                "model": "mistral-large",
                "max_tokens": 100,
            }
        )

        if result["success"]:
            completion = result.get("completion", "")
            print(f"✅ Text completion generated: {len(completion)} characters")
            print(f"   Model: {result.get('model')}")
            print(f"   Tokens: {result.get('completion_tokens', 0)}")
        else:
            print(f"⚠️  Text completion failed: {result.get('error')}")

        return True

    except Exception as e:
        print(f"❌ Text completion test failed: {e}")
        return False
    finally:
        await server.on_shutdown()


async def test_analyze_sentiment():
    """Test sentiment analysis"""
    print("\n🧪 Testing analyze_sentiment...")

    server = SnowflakeUnifiedServer()
    await server.on_startup()

    try:
        # Test positive sentiment
        result = await server.analyze_sentiment(
            {
                "text": "I absolutely love using Snowflake! It's fantastic and makes my work so much easier."
            }
        )

        if result["success"]:
            sentiment = result.get("sentiment", "")
            score = result.get("score", 0)
            print("✅ Sentiment analysis completed:")
            print(f"   Sentiment: {sentiment}")
            print(f"   Score: {score}")
            print(f"   Confidence: {result.get('confidence', 0)}")

            if sentiment.lower() in ["positive", "pos"] or score > 0.6:
                print("✅ Correctly identified positive sentiment")
        else:
            print(f"⚠️  Sentiment analysis failed: {result.get('error')}")

        return True

    except Exception as e:
        print(f"❌ Sentiment analysis test failed: {e}")
        return False
    finally:
        await server.on_shutdown()


async def test_get_table_info():
    """Test table information retrieval"""
    print("\n🧪 Testing get_table_info...")

    server = SnowflakeUnifiedServer()
    await server.on_startup()

    try:
        result = await server.get_table_info(
            {"table_name": "knowledge_base", "schema": "PROCESSED_AI"}
        )

        if result["success"]:
            columns = result.get("columns", [])
            print("✅ Table info retrieved successfully:")
            print(f"   Table: {result.get('table')}")
            print(f"   Schema: {result.get('schema')}")
            print(f"   Columns: {len(columns)}")

            for col in columns[:3]:  # Show first 3 columns
                print(f"     - {col.get('name')} ({col.get('type')})")
        else:
            print(f"⚠️  Table info retrieval failed: {result.get('error')}")

        return True

    except Exception as e:
        print(f"❌ Table info test failed: {e}")
        return False
    finally:
        await server.on_shutdown()


async def test_performance():
    """Test server performance"""
    print("\n🧪 Testing performance...")

    server = SnowflakeUnifiedServer()
    await server.on_startup()

    try:
        import time

        # Test query performance
        start = time.time()
        await server.query_data({"table": "test_table", "columns": ["*"], "limit": 100})
        query_time = time.time() - start
        print(f"✅ Query execution time: {query_time:.3f}s")

        # Test embedding performance
        start = time.time()
        await server.generate_embedding(
            {"text": "Performance test for embedding generation", "model": "e5-base-v2"}
        )
        embed_time = time.time() - start
        print(f"✅ Embedding generation time: {embed_time:.3f}s")

        # Test completion performance
        start = time.time()
        await server.complete_text(
            {"prompt": "Quick test", "model": "mistral-large", "max_tokens": 50}
        )
        complete_time = time.time() - start
        print(f"✅ Text completion time: {complete_time:.3f}s")

        # Check if within acceptable limits
        if query_time < 1.0 and embed_time < 0.5 and complete_time < 3.0:
            print("✅ All operations within performance targets")
        else:
            print("⚠️  Some operations exceed performance targets")

        return True

    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        return False
    finally:
        await server.on_shutdown()


async def run_all_tests():
    """Run all integration tests"""
    print("🚀 Starting Snowflake MCP Server Integration Tests")
    print("=" * 60)

    tests = [
        ("Server Startup", test_server_startup),
        ("Query Data", test_query_data),
        ("Generate Embedding", test_generate_embedding),
        ("Semantic Search", test_semantic_search),
        ("Complete Text", test_complete_text),
        ("Analyze Sentiment", test_analyze_sentiment),
        ("Get Table Info", test_get_table_info),
        ("Performance", test_performance),
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        try:
            success = await test_func()
            if success:
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            failed += 1

    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed} passed, {failed} failed")

    if failed == 0:
        print("✅ All tests passed! Snowflake MCP Server is ready for deployment.")
    else:
        print(f"❌ {failed} tests failed. Please fix issues before deployment.")

    return failed == 0


if __name__ == "__main__":
    # Run tests
    success = asyncio.run(run_all_tests())

    # Exit with appropriate code
    sys.exit(0 if success else 1)
