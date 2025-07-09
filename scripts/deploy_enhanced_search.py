#!/usr/bin/env python3
"""
Enhanced Search Deployment Script
Validates and tests the enhanced search implementation
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from typing import Any

import aiohttp
import requests

from backend.services.enhanced_search_service import (
    EnhancedSearchService,
    SearchProvider,
    SearchRequest,
    SearchTier,
)
from backend.services.unified_chat_service import UnifiedChatService

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class EnhancedSearchDeploymentValidator:
    """Validates enhanced search deployment"""

    def __init__(self):
        self.search_service = EnhancedSearchService()
        self.chat_service = UnifiedChatService()
        self.test_results = []
        self.base_url = "http://localhost:8000"

    async def run_validation(self) -> dict[str, Any]:
        """Run comprehensive validation of enhanced search system"""

        logger.info("🚀 Starting Enhanced Search Deployment Validation")

        validation_results = {
            "timestamp": datetime.utcnow().isoformat(),
            "overall_status": "unknown",
            "test_results": [],
            "performance_metrics": {},
            "provider_status": {},
            "api_endpoints": {},
            "recommendations": [],
        }

        try:
            # 1. Test core service initialization
            logger.info("1️⃣ Testing core service initialization...")
            init_result = await self.test_service_initialization()
            validation_results["test_results"].append(init_result)

            # 2. Test search tiers
            logger.info("2️⃣ Testing search tiers...")
            tier_results = await self.test_search_tiers()
            validation_results["test_results"].extend(tier_results)

            # 3. Test search providers
            logger.info("3️⃣ Testing search providers...")
            provider_results = await self.test_search_providers()
            validation_results["test_results"].extend(provider_results)
            validation_results["provider_status"] = await self.get_provider_status()

            # 4. Test semantic caching
            logger.info("4️⃣ Testing semantic caching...")
            cache_result = await self.test_semantic_caching()
            validation_results["test_results"].append(cache_result)

            # 5. Test API endpoints
            logger.info("5️⃣ Testing API endpoints...")
            api_results = await self.test_api_endpoints()
            validation_results["test_results"].extend(api_results)
            validation_results["api_endpoints"] = await self.get_api_status()

            # 6. Test real-time streaming
            logger.info("6️⃣ Testing real-time streaming...")
            streaming_result = await self.test_streaming()
            validation_results["test_results"].append(streaming_result)

            # 7. Test intelligent routing
            logger.info("7️⃣ Testing intelligent routing...")
            routing_result = await self.test_intelligent_routing()
            validation_results["test_results"].append(routing_result)

            # 8. Performance benchmarks
            logger.info("8️⃣ Running performance benchmarks...")
            performance_results = await self.run_performance_benchmarks()
            validation_results["performance_metrics"] = performance_results

            # 9. Calculate overall status
            validation_results["overall_status"] = self.calculate_overall_status(
                validation_results["test_results"]
            )

            # 10. Generate recommendations
            validation_results["recommendations"] = self.generate_recommendations(
                validation_results
            )

            logger.info(
                f"✅ Validation complete! Overall status: {validation_results['overall_status']}"
            )
            return validation_results

        except Exception as e:
            logger.error(f"❌ Validation failed: {e}")
            validation_results["overall_status"] = "failed"
            validation_results["error"] = str(e)
            return validation_results

    async def test_service_initialization(self) -> dict[str, Any]:
        """Test service initialization"""
        try:
            # Test service instantiation
            service = EnhancedSearchService()

            # Test cache initialization
            cache_initialized = service.semantic_cache is not None

            # Test browser service initialization
            browser_service = service.browser_service

            return {
                "test_name": "Service Initialization",
                "status": "passed",
                "details": {
                    "service_created": True,
                    "cache_initialized": cache_initialized,
                    "browser_service_ready": browser_service is not None,
                },
            }
        except Exception as e:
            return {
                "test_name": "Service Initialization",
                "status": "failed",
                "error": str(e),
            }

    async def test_search_tiers(self) -> list[dict[str, Any]]:
        """Test all search tiers"""
        results = []
        test_queries = [
            "What is artificial intelligence?",
            "How does machine learning work?",
            "Analyze the impact of AI on business",
        ]

        for tier in [SearchTier.TIER_1, SearchTier.TIER_2, SearchTier.TIER_3]:
            try:
                start_time = time.time()

                # Test with first query
                search_request = SearchRequest(
                    query=test_queries[0],
                    tier=tier,
                    max_results=5,
                    user_id="test_user",
                    session_id="test_session",
                )

                result_count = 0
                async for result in self.search_service.search(search_request):
                    result_count += 1
                    if result_count >= 5:  # Limit for testing
                        break

                processing_time = time.time() - start_time

                # Check tier performance targets
                tier_limits = {
                    SearchTier.TIER_1: 2.0,  # <2s
                    SearchTier.TIER_2: 30.0,  # <30s
                    SearchTier.TIER_3: 300.0,  # <5min
                }

                performance_ok = processing_time < tier_limits[tier]

                results.append(
                    {
                        "test_name": f"Search Tier {tier.value}",
                        "status": "passed"
                        if result_count > 0 and performance_ok
                        else "failed",
                        "details": {
                            "results_returned": result_count,
                            "processing_time": processing_time,
                            "performance_target": tier_limits[tier],
                            "performance_ok": performance_ok,
                        },
                    }
                )

            except Exception as e:
                results.append(
                    {
                        "test_name": f"Search Tier {tier.value}",
                        "status": "failed",
                        "error": str(e),
                    }
                )

        return results

    async def test_search_providers(self) -> list[dict[str, Any]]:
        """Test all search providers"""
        results = []
        test_query = "Python programming language"

        for provider in [
            SearchProvider.INTERNAL,
            SearchProvider.BRAVE,
            SearchProvider.SEARXNG,
        ]:
            try:
                search_request = SearchRequest(
                    query=test_query,
                    tier=SearchTier.TIER_1,
                    providers=[provider],
                    max_results=3,
                    user_id="test_user",
                    session_id="test_session",
                )

                result_count = 0
                provider_results = []
                async for result in self.search_service.search(search_request):
                    if result.get("type") == "result":
                        result_count += 1
                        provider_results.append(result)

                results.append(
                    {
                        "test_name": f"Provider {provider.value}",
                        "status": "passed" if result_count > 0 else "warning",
                        "details": {
                            "results_returned": result_count,
                            "provider_available": result_count > 0,
                            "sample_result": provider_results[0]
                            if provider_results
                            else None,
                        },
                    }
                )

            except Exception as e:
                results.append(
                    {
                        "test_name": f"Provider {provider.value}",
                        "status": "failed",
                        "error": str(e),
                    }
                )

        return results

    async def test_semantic_caching(self) -> dict[str, Any]:
        """Test semantic caching system"""
        try:
            # Test cache with similar queries
            queries = [
                "What is machine learning?",
                "What is ML?",
                "Explain machine learning",
            ]

            search_request = SearchRequest(
                query=queries[0],
                tier=SearchTier.TIER_1,
                max_results=3,
                user_id="cache_test",
                session_id="cache_session",
            )

            # First search - should cache
            result_count_1 = 0
            async for result in self.search_service.search(search_request):
                result_count_1 += 1
                if result_count_1 >= 3:
                    break

            # Second search with similar query - should hit cache
            search_request.query = queries[1]
            result_count_2 = 0
            cache_hit = False
            async for result in self.search_service.search(search_request):
                if result.get("type") == "cache_hit":
                    cache_hit = True
                result_count_2 += 1
                if result_count_2 >= 3:
                    break

            return {
                "test_name": "Semantic Caching",
                "status": "passed" if cache_hit else "warning",
                "details": {
                    "first_search_results": result_count_1,
                    "second_search_results": result_count_2,
                    "cache_hit_detected": cache_hit,
                },
            }

        except Exception as e:
            return {
                "test_name": "Semantic Caching",
                "status": "failed",
                "error": str(e),
            }

    async def test_api_endpoints(self) -> list[dict[str, Any]]:
        """Test API endpoints"""
        results = []
        endpoints = [
            ("GET", "/api/v1/search/providers", {}),
            ("GET", "/api/v1/search/health", {}),
            (
                "POST",
                "/api/v1/search/search",
                {"query": "test query", "tier": "tier_1", "max_results": 3},
            ),
            (
                "GET",
                "/api/v1/search/search/intelligent",
                {"query": "test intelligent search"},
            ),
        ]

        for method, endpoint, data in endpoints:
            try:
                if method == "GET":
                    response = requests.get(
                        f"{self.base_url}{endpoint}", params=data, timeout=10
                    )
                else:
                    response = requests.post(
                        f"{self.base_url}{endpoint}", json=data, timeout=10
                    )

                success = response.status_code == 200
                response_data = response.json() if success else None

                results.append(
                    {
                        "test_name": f"API {method} {endpoint}",
                        "status": "passed" if success else "failed",
                        "details": {
                            "status_code": response.status_code,
                            "response_time": response.elapsed.total_seconds(),
                            "response_size": len(response.content),
                            "has_data": response_data is not None,
                        },
                    }
                )

            except Exception as e:
                results.append(
                    {
                        "test_name": f"API {method} {endpoint}",
                        "status": "failed",
                        "error": str(e),
                    }
                )

        return results

    async def test_streaming(self) -> dict[str, Any]:
        """Test real-time streaming"""
        try:
            # Test streaming endpoint
            stream_url = f"{self.base_url}/api/v1/search/search/stream"
            params = {"query": "streaming test", "tier": "tier_1", "max_results": 3}

            async with aiohttp.ClientSession() as session:
                async with session.get(stream_url, params=params) as response:
                    if response.status == 200:
                        chunks_received = 0
                        async for chunk in response.content.iter_chunked(1024):
                            chunks_received += 1
                            if chunks_received >= 5:  # Limit for testing
                                break

                        return {
                            "test_name": "Real-time Streaming",
                            "status": "passed",
                            "details": {
                                "stream_established": True,
                                "chunks_received": chunks_received,
                                "content_type": response.headers.get(
                                    "content-type", ""
                                ),
                            },
                        }
                    else:
                        return {
                            "test_name": "Real-time Streaming",
                            "status": "failed",
                            "details": {
                                "status_code": response.status,
                                "stream_established": False,
                            },
                        }

        except Exception as e:
            return {
                "test_name": "Real-time Streaming",
                "status": "failed",
                "error": str(e),
            }

    async def test_intelligent_routing(self) -> dict[str, Any]:
        """Test intelligent search routing"""
        try:
            test_cases = [
                ("What is Python?", SearchTier.TIER_1),
                ("Explain machine learning algorithms", SearchTier.TIER_2),
                (
                    "Analyze the comprehensive impact of AI on business",
                    SearchTier.TIER_3,
                ),
            ]

            correct_routing = 0
            for query, expected_tier in test_cases:
                selected_tier = await self.chat_service.intelligent_search_routing(
                    query
                )
                if selected_tier == expected_tier:
                    correct_routing += 1

            accuracy = correct_routing / len(test_cases)

            return {
                "test_name": "Intelligent Routing",
                "status": "passed" if accuracy >= 0.6 else "warning",
                "details": {
                    "test_cases": len(test_cases),
                    "correct_routing": correct_routing,
                    "accuracy": accuracy,
                },
            }

        except Exception as e:
            return {
                "test_name": "Intelligent Routing",
                "status": "failed",
                "error": str(e),
            }

    async def run_performance_benchmarks(self) -> dict[str, Any]:
        """Run performance benchmarks"""
        try:
            benchmarks = {}

            # Tier 1 performance
            start_time = time.time()
            search_request = SearchRequest(
                query="performance test", tier=SearchTier.TIER_1, max_results=5
            )

            result_count = 0
            async for result in self.search_service.search(search_request):
                result_count += 1
                if result_count >= 5:
                    break

            tier1_time = time.time() - start_time
            benchmarks["tier_1_performance"] = {
                "target": "< 2s",
                "actual": tier1_time,
                "passed": tier1_time < 2.0,
            }

            # Cache performance
            start_time = time.time()
            # Second identical search should hit cache
            result_count = 0
            async for result in self.search_service.search(search_request):
                result_count += 1
                if result_count >= 5:
                    break

            cache_time = time.time() - start_time
            benchmarks["cache_performance"] = {
                "target": "< 0.5s",
                "actual": cache_time,
                "passed": cache_time < 0.5,
            }

            return benchmarks

        except Exception as e:
            return {"error": str(e)}

    async def get_provider_status(self) -> dict[str, Any]:
        """Get status of all providers"""
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/search/providers", timeout=10
            )
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}

    async def get_api_status(self) -> dict[str, Any]:
        """Get API health status"""
        try:
            response = requests.get(f"{self.base_url}/api/v1/search/health", timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}

    def calculate_overall_status(self, test_results: list[dict[str, Any]]) -> str:
        """Calculate overall validation status"""
        if not test_results:
            return "unknown"

        passed = sum(1 for result in test_results if result["status"] == "passed")
        failed = sum(1 for result in test_results if result["status"] == "failed")
        warnings = sum(1 for result in test_results if result["status"] == "warning")

        total = len(test_results)
        pass_rate = passed / total

        if pass_rate >= 0.9:
            return "excellent"
        elif pass_rate >= 0.7:
            return "good"
        elif pass_rate >= 0.5:
            return "acceptable"
        else:
            return "needs_improvement"

    def generate_recommendations(self, validation_results: dict[str, Any]) -> list[str]:
        """Generate recommendations based on validation results"""
        recommendations = []

        # Check failed tests
        failed_tests = [
            r for r in validation_results["test_results"] if r["status"] == "failed"
        ]
        if failed_tests:
            recommendations.append(f"🔧 Fix {len(failed_tests)} failed tests")

        # Check performance
        performance = validation_results.get("performance_metrics", {})
        if "tier_1_performance" in performance:
            if not performance["tier_1_performance"].get("passed", True):
                recommendations.append("⚡ Optimize Tier 1 search performance")

        # Check providers
        provider_results = [
            r
            for r in validation_results["test_results"]
            if r["test_name"].startswith("Provider")
        ]
        failed_providers = [r for r in provider_results if r["status"] == "failed"]
        if failed_providers:
            recommendations.append(
                f"🔌 Configure {len(failed_providers)} search providers"
            )

        # Check API endpoints
        api_results = [
            r
            for r in validation_results["test_results"]
            if r["test_name"].startswith("API")
        ]
        failed_apis = [r for r in api_results if r["status"] == "failed"]
        if failed_apis:
            recommendations.append(f"🌐 Fix {len(failed_apis)} API endpoints")

        if not recommendations:
            recommendations.append("✅ All systems operational - ready for production!")

        return recommendations

    async def cleanup(self):
        """Clean up resources"""
        try:
            await self.search_service.cleanup()
            logger.info("✅ Cleanup completed")
        except Exception as e:
            logger.error(f"❌ Cleanup failed: {e}")


async def main():
    """Main deployment validation function"""
    validator = EnhancedSearchDeploymentValidator()

    try:
        # Run validation
        results = await validator.run_validation()

        # Generate report
        report = f"""
🚀 ENHANCED SEARCH DEPLOYMENT VALIDATION REPORT
===============================================

Overall Status: {results['overall_status'].upper()}
Timestamp: {results['timestamp']}

📊 TEST RESULTS SUMMARY:
{'-' * 50}
"""

        for test_result in results["test_results"]:
            status_emoji = {"passed": "✅", "failed": "❌", "warning": "⚠️"}.get(
                test_result["status"], "❓"
            )

            report += f"{status_emoji} {test_result['test_name']}: {test_result['status'].upper()}\n"

            if test_result["status"] == "failed" and "error" in test_result:
                report += f"   Error: {test_result['error']}\n"

        # Performance metrics
        if results.get("performance_metrics"):
            report += f"\n⚡ PERFORMANCE METRICS:\n{'-' * 50}\n"
            for metric, data in results["performance_metrics"].items():
                if isinstance(data, dict) and "target" in data:
                    status = "✅" if data.get("passed", False) else "❌"
                    report += f"{status} {metric}: {data['actual']:.2f}s (target: {data['target']})\n"

        # Recommendations
        if results.get("recommendations"):
            report += f"\n💡 RECOMMENDATIONS:\n{'-' * 50}\n"
            for rec in results["recommendations"]:
                report += f"• {rec}\n"

        # Provider status
        if results.get("provider_status"):
            report += f"\n🔌 PROVIDER STATUS:\n{'-' * 50}\n"
            providers = results["provider_status"].get("providers", [])
            for provider in providers:
                report += f"• {provider.get('display_name', 'Unknown')}: Available\n"

        print(report)

        # Save detailed results
        with open("enhanced_search_validation_results.json", "w") as f:
            json.dump(results, f, indent=2)

        logger.info(
            "📄 Detailed results saved to enhanced_search_validation_results.json"
        )

        # Exit with appropriate code
        if results["overall_status"] in ["excellent", "good"]:
            exit(0)
        else:
            exit(1)

    except Exception as e:
        logger.error(f"❌ Validation failed: {e}")
        exit(1)
    finally:
        await validator.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
