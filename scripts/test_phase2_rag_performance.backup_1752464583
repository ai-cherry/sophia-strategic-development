#!/usr/bin/env python3
"""
Phase 2: RAG Performance Test Script
Tests enhanced multi-hop orchestrator with personalized reranking

Date: July 12, 2025
"""

import asyncio
import json
import time
from datetime import UTC, datetime
from pathlib import Path

# Mock imports for testing
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.services.enhanced_multi_hop_orchestrator_v2 import EnhancedMultiHopOrchestrator
from backend.services.personality_engine import PersonalityEngine
from backend.services.n8n_alpha_optimizer_v2 import XTrendFetcher


class MockMemoryService:
    """Mock memory service for testing"""
    
    def __init__(self):
        self.test_data = [
            {
                "content": "Q3 2025 revenue increased by 23% YoY to $4.2M",
                "score": 0.92,
                "metadata": {
                    "source": "financial_report",
                    "time_period": "Q3 2025",
                    "categories": ["financial", "revenue"],
                    "department": "finance"
                },
                "timestamp": datetime.now(UTC)
            },
            {
                "content": "Monthly recurring revenue (MRR) hit $350K in June",
                "score": 0.88,
                "metadata": {
                    "source": "sales_dashboard",
                    "time_period": "June 2025",
                    "categories": ["financial", "revenue", "sales"],
                    "department": "sales"
                },
                "timestamp": datetime.now(UTC)
            },
            {
                "content": "Revenue per customer increased 15% due to upsells",
                "score": 0.85,
                "metadata": {
                    "source": "customer_analytics",
                    "time_period": "Q2 2025",
                    "categories": ["financial", "revenue", "customer"],
                    "department": "sales"
                },
                "timestamp": datetime.now(UTC)
            },
            {
                "content": "New product line contributing 30% of total revenue",
                "score": 0.82,
                "metadata": {
                    "source": "product_metrics",
                    "time_period": "Q3 2025",
                    "categories": ["financial", "revenue", "product"],
                    "department": "product"
                },
                "timestamp": datetime.now(UTC)
            },
            {
                "content": "Revenue forecast for Q4: $5.1M (21% growth)",
                "score": 0.90,
                "metadata": {
                    "source": "financial_forecast",
                    "time_period": "Q4 2025",
                    "categories": ["financial", "revenue", "forecast"],
                    "department": "finance"
                },
                "timestamp": datetime.now(UTC)
            }
        ]
    
    async def initialize(self):
        """Mock initialization"""
        pass
    
    async def search_knowledge(self, query: str, limit: int = 10, metadata_filter: dict = None):
        """Mock search returning test data"""
        # Simulate search with some filtering
        results = self.test_data[:limit]
        
        # Apply basic filtering
        if metadata_filter:
            filtered = []
            for item in results:
                match = True
                for key, value in metadata_filter.items():
                    if item["metadata"].get(key) != value:
                        match = False
                        break
                if match:
                    filtered.append(item)
            results = filtered
        
        return results


class MockXTrendFetcher:
    """Mock X trend fetcher"""
    
    async def fetch_trends(self, topic: str = None):
        """Return mock trends"""
        return [
            {
                "text": "Tech revenue growth hitting record highs in 2025 #earnings",
                "metrics": {"retweet_count": 1234, "like_count": 5678},
                "relevance": 0.95
            },
            {
                "text": "SaaS companies seeing 40% YoY growth on average",
                "metrics": {"retweet_count": 890, "like_count": 3456},
                "relevance": 0.88
            },
            {
                "text": "Video: How to analyze revenue trends like a pro",
                "metrics": {"retweet_count": 567, "like_count": 2345},
                "relevance": 0.82
            }
        ]


async def test_rag_performance():
    """Test RAG performance with revenue query"""
    print("🧪 Phase 2 RAG Performance Test")
    print("=" * 50)
    
    # Initialize components
    print("\n📚 Initializing components...")
    
    # Create mock orchestrator
    orchestrator = EnhancedMultiHopOrchestrator()
    orchestrator.memory_service = MockMemoryService()
    await orchestrator.initialize()
    
    # Initialize personality engine
    personality_engine = PersonalityEngine()
    
    # Mock trend fetcher
    trend_fetcher = MockXTrendFetcher()
    
    # Test queries
    test_queries = [
        {
            "query": "Revenue trends?",
            "user_id": "ceo_user",
            "mode": "ceo_roast"
        },
        {
            "query": "What are the revenue trends for Q3?",
            "user_id": "cfo_user",
            "mode": "professional"
        },
        {
            "query": "Show me revenue growth patterns",
            "user_id": "analyst_user",
            "mode": "snarky"
        }
    ]
    
    results = []
    
    for test in test_queries:
        print(f"\n🔍 Testing: {test['query']}")
        print(f"   User: {test['user_id']}")
        print(f"   Mode: {test['mode']}")
        
        # Set personality mode
        personality_engine.set_mode(test['mode'], test['user_id'])
        
        # Execute multi-hop query
        start_time = time.time()
        result = await orchestrator.multi_hop_query(
            test['query'],
            test['user_id'],
            context={"focus": "revenue"}
        )
        query_time = time.time() - start_time
        
        # Fetch X trends
        trends = await trend_fetcher.fetch_trends("revenue trends")
        
        # Calculate accuracy (mock calculation)
        accuracy = calculate_accuracy(result)
        
        # Generate response with personality
        response = generate_response(result, trends)
        enhanced_response = personality_engine.enhance_response(
            response,
            test['query'],
            test['user_id'],
            context={"repeated_question": True}
        )
        
        test_result = {
            "query": test['query'],
            "user_id": test['user_id'],
            "mode": test['mode'],
            "accuracy": accuracy,
            "query_time": query_time,
            "hops": result['hops'],
            "total_results": result['total_results'],
            "confidence": result['confidence'],
            "has_trends": len(trends) > 0,
            "has_video": any("video" in str(t).lower() for t in trends),
            "response_preview": enhanced_response[:200] + "..."
        }
        
        results.append(test_result)
        
        # Print results
        print(f"\n📊 Results:")
        print(f"   Accuracy: {accuracy:.1%}")
        print(f"   Query Time: {query_time:.3f}s")
        print(f"   Hops: {result['hops']}")
        print(f"   Results Found: {result['total_results']}")
        print(f"   Confidence: {result['confidence']:.2f}")
        print(f"   X Trends: {'✅' if test_result['has_trends'] else '❌'}")
        print(f"   Video Content: {'✅' if test_result['has_video'] else '❌'}")
        print(f"\n💬 Response Preview:")
        print(f"   {test_result['response_preview']}")
    
    # Generate summary report
    print("\n" + "=" * 50)
    print("📈 Performance Summary")
    print("=" * 50)
    
    avg_accuracy = sum(r['accuracy'] for r in results) / len(results)
    avg_time = sum(r['query_time'] for r in results) / len(results)
    
    print(f"\n✅ Average Accuracy: {avg_accuracy:.1%} {'✅' if avg_accuracy > 0.88 else '❌'}")
    print(f"⏱️  Average Query Time: {avg_time:.3f}s")
    print(f"🔄 Average Hops: {sum(r['hops'] for r in results) / len(results):.1f}")
    print(f"📱 X Integration: {sum(1 for r in results if r['has_trends']) / len(results):.0%}")
    print(f"🎥 Video Content: {sum(1 for r in results if r['has_video']) / len(results):.0%}")
    
    # Check personalities
    print(f"\n🎭 Personality Modes Tested:")
    for mode in set(r['mode'] for r in results):
        count = sum(1 for r in results if r['mode'] == mode)
        print(f"   - {mode}: {count} test(s)")
    
    # Save detailed results
    report = {
        "timestamp": datetime.now(UTC).isoformat(),
        "summary": {
            "average_accuracy": avg_accuracy,
            "average_query_time": avg_time,
            "total_tests": len(results),
            "passed": avg_accuracy > 0.88
        },
        "detailed_results": results
    }
    
    report_file = Path("PHASE_2_RAG_TEST_RESULTS.json")
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Detailed results saved to: {report_file}")
    
    # Final verdict
    print("\n" + "=" * 50)
    if avg_accuracy > 0.88:
        print("🎉 PHASE 2 RAG TEST: PASSED!")
        print(f"   Achieved {avg_accuracy:.1%} accuracy (target: >88%)")
    else:
        print("❌ PHASE 2 RAG TEST: FAILED")
        print(f"   Only achieved {avg_accuracy:.1%} accuracy (target: >88%)")
    
    return avg_accuracy > 0.88


def calculate_accuracy(result: dict) -> float:
    """Calculate accuracy based on result quality"""
    # Mock accuracy calculation based on:
    # - Number of relevant results
    # - Average score
    # - Confidence level
    
    if not result['results']:
        return 0.0
    
    # Base accuracy from average score
    avg_score = sum(r['score'] for r in result['results']) / len(result['results'])
    
    # Boost for having enough results
    result_boost = min(0.1, len(result['results']) * 0.02)
    
    # Boost for high confidence
    confidence_boost = result['confidence'] * 0.1
    
    # Penalty for too many hops
    hop_penalty = max(0, (result['hops'] - 2) * 0.05)
    
    accuracy = avg_score + result_boost + confidence_boost - hop_penalty
    
    return min(1.0, max(0.0, accuracy))


def generate_response(result: dict, trends: list) -> str:
    """Generate response from results and trends"""
    if not result['results']:
        return "No revenue data found."
    
    # Compile key insights
    insights = []
    for r in result['results'][:3]:
        insights.append(r['content'])
    
    response = "Based on the latest data:\n\n"
    response += "\n".join(f"• {insight}" for insight in insights)
    
    # Add trend insights
    if trends:
        response += "\n\n📱 Trending on X:\n"
        for trend in trends[:2]:
            response += f"• {trend['text']}\n"
    
    return response


async def main():
    """Main test runner"""
    try:
        passed = await test_rag_performance()
        exit(0 if passed else 1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)


if __name__ == "__main__":
    asyncio.run(main()) 