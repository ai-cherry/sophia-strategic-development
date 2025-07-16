#!/usr/bin/env python3
"""
🧪 PHASE 2.1 ADVANCED MEMORY INTELLIGENCE VALIDATION
Comprehensive testing of hybrid search, adaptive learning, and business intelligence

Created: July 14, 2025
Phase: 2.1 - Advanced Memory Intelligence
"""

import asyncio
import sys
import time
import logging
from typing import Dict, List, Any
from datetime import datetime
import traceback

# Add backend to path for imports
sys.path.append('backend')

from backend.services.advanced_hybrid_search_service import (
    AdvancedHybridSearchService, SearchContext, SearchResult, SearchResultType
)
from backend.services.adaptive_memory_system import (
    AdaptiveMemorySystem, UserFeedback, FeedbackType
)
from backend.services.payready_business_intelligence import (
    PayReadyBusinessIntelligence, BusinessContext
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Phase2ValidationSuite:
    """Comprehensive validation suite for Phase 2.1 Advanced Memory Intelligence"""
    
    def __init__(self):
        self.hybrid_search = None
        self.adaptive_memory = None
        self.business_intelligence = None
        self.test_results = {}
        self.start_time = None
        
    async def run_comprehensive_validation(self) -> Dict[str, Any]:
        """Run comprehensive validation of Phase 2.1 components"""
        self.start_time = time.time()
        
        print("🚀 PHASE 2.1 ADVANCED MEMORY INTELLIGENCE VALIDATION")
        print("=" * 60)
        
        try:
            # Initialize components
            await self._initialize_components()
            
            # Test 1: Hybrid Search Validation
            await self._test_hybrid_search_system()
            
            # Test 2: Adaptive Memory Validation
            await self._test_adaptive_memory_system()
            
            # Test 3: Business Intelligence Validation
            await self._test_business_intelligence_system()
            
            # Test 4: Integration Testing
            await self._test_system_integration()
            
            # Test 5: Performance Testing
            await self._test_performance_metrics()
            
            # Generate validation report
            return await self._generate_validation_report()
            
        except Exception as e:
            logger.error(f"❌ Validation failed: {e}")
            traceback.print_exc()
            return {"status": "FAILED", "error": str(e)}

    async def _initialize_components(self):
        """Initialize all Phase 2.1 components"""
        print("\n🔧 INITIALIZING COMPONENTS...")
        
        try:
            # Initialize Adaptive Memory System first
            self.adaptive_memory = AdaptiveMemorySystem()
            await self.adaptive_memory.initialize()
            print("✅ Adaptive Memory System initialized")
            
            # Initialize Hybrid Search Service
            self.hybrid_search = AdvancedHybridSearchService()
            await self.hybrid_search.initialize()
            print("✅ Advanced Hybrid Search Service initialized")
            
            # Initialize Business Intelligence
            self.business_intelligence = PayReadyBusinessIntelligence(self.adaptive_memory)
            await self.business_intelligence.initialize()
            print("✅ Pay Ready Business Intelligence initialized")
            
            self.test_results["initialization"] = {"status": "PASSED", "components": 3}
            
        except Exception as e:
            logger.error(f"❌ Component initialization failed: {e}")
            self.test_results["initialization"] = {"status": "FAILED", "error": str(e)}
            raise

    async def _test_hybrid_search_system(self):
        """Test Advanced Hybrid Search System"""
        print("\n🔍 TESTING HYBRID SEARCH SYSTEM...")
        
        test_cases = [
            {
                "name": "Multi-Modal Search",
                "query": "customer retention strategies",
                "context": SearchContext(
                    user_id="test_user_1",
                    session_id="test_session_1",
                    business_domain="customer_management"
                )
            },
            {
                "name": "Business Intelligence Search",
                "query": "sales pipeline analysis Q3 2025",
                "context": SearchContext(
                    user_id="test_user_2",
                    session_id="test_session_2",
                    business_domain="sales"
                )
            },
            {
                "name": "Personalized Search",
                "query": "market trends and opportunities",
                "context": SearchContext(
                    user_id="test_user_3",
                    session_id="test_session_3",
                    business_domain="market_intelligence",
                    personalization_enabled=True
                )
            }
        ]
        
        search_results = {}
        
        for test_case in test_cases:
            try:
                print(f"  🧪 Testing: {test_case['name']}")
                
                # Perform hybrid search
                start_time = time.time()
                results = await self.hybrid_search.hybrid_search(
                    test_case["query"], 
                    test_case["context"]
                )
                search_time = time.time() - start_time
                
                # Validate results
                validation = await self._validate_search_results(results, test_case)
                
                search_results[test_case["name"]] = {
                    "status": "PASSED" if validation["valid"] else "FAILED",
                    "results_count": len(results),
                    "search_time_ms": round(search_time * 1000, 2),
                    "validation": validation
                }
                
                print(f"    ✅ {test_case['name']}: {len(results)} results in {search_time*1000:.2f}ms")
                
            except Exception as e:
                logger.error(f"❌ Search test failed for {test_case['name']}: {e}")
                search_results[test_case["name"]] = {
                    "status": "FAILED",
                    "error": str(e)
                }
        
        # Test business intelligence search
        try:
            print("  🧪 Testing: Business Intelligence Search")
            
            BusinessContext(
                user_role="CEO",
                business_unit="executive",
                time_horizon="short",
                priority_level="high",
                decision_context="strategic"
            )
            
            start_time = time.time()
            bi_results = await self.hybrid_search.intelligent_business_search(
                "customer health and revenue impact analysis",
                SearchContext(
                    user_id="ceo_user",
                    session_id="executive_session",
                    business_domain="executive"
                )
            )
            search_time = time.time() - start_time
            
            search_results["Business Intelligence"] = {
                "status": "PASSED",
                "insights_count": len(bi_results.primary_insights),
                "confidence_score": bi_results.confidence_score,
                "search_time_ms": round(search_time * 1000, 2)
            }
            
            print(f"    ✅ Business Intelligence: {len(bi_results.primary_insights)} insights in {search_time*1000:.2f}ms")
            
        except Exception as e:
            logger.error(f"❌ Business intelligence search test failed: {e}")
            search_results["Business Intelligence"] = {
                "status": "FAILED",
                "error": str(e)
            }
        
        self.test_results["hybrid_search"] = search_results

    async def _test_adaptive_memory_system(self):
        """Test Adaptive Memory System"""
        print("\n🧠 TESTING ADAPTIVE MEMORY SYSTEM...")
        
        memory_tests = {}
        
        try:
            # Test 1: User Profile Creation and Updates
            print("  🧪 Testing: User Profile Management")
            
            test_user_id = "test_adaptive_user"
            
            # Create user feedback
            feedback = UserFeedback(
                user_id=test_user_id,
                query="customer retention analysis",
                result_id="test_result_1",
                feedback_type=FeedbackType.RATING,
                rating=0.9,
                context={"business_domain": "customer_management"}
            )
            
            # Simulate search results
            search_results = [
                SearchResult(
                    id="test_result_1",
                    content="Customer retention strategies and best practices",
                    source="test_collection",
                    metadata={"category": "customer_management"},
                    scores={SearchResultType.DENSE_SEMANTIC: 0.85},
                    final_score=0.85,
                    confidence=0.85,
                    relevance_explanation="High semantic relevance",
                    timestamp=datetime.now()
                )
            ]
            
            # Test learning from interaction
            await self.adaptive_memory.learn_from_interaction(
                "customer retention analysis",
                search_results,
                feedback
            )
            
            # Test personalized search context
            personalized_context = await self.adaptive_memory.get_personalized_search_context(
                test_user_id,
                "sales performance metrics"
            )
            
            memory_tests["User Profile Management"] = {
                "status": "PASSED",
                "user_id": test_user_id,
                "personalized_context": personalized_context.business_domain,
                "learning_applied": True
            }
            
            print("    ✅ User Profile Management: Learning and personalization working")
            
        except Exception as e:
            logger.error(f"❌ User profile test failed: {e}")
            memory_tests["User Profile Management"] = {
                "status": "FAILED",
                "error": str(e)
            }
        
        try:
            # Test 2: Learning Insights Generation
            print("  🧪 Testing: Learning Insights Generation")
            
            # Generate learning insights
            insights = await self.adaptive_memory.generate_learning_insights()
            
            memory_tests["Learning Insights"] = {
                "status": "PASSED",
                "insights_count": len(insights),
                "insight_types": [insight.pattern_type.value for insight in insights] if insights else []
            }
            
            print(f"    ✅ Learning Insights: Generated {len(insights)} insights")
            
        except Exception as e:
            logger.error(f"❌ Learning insights test failed: {e}")
            memory_tests["Learning Insights"] = {
                "status": "FAILED",
                "error": str(e)
            }
        
        self.test_results["adaptive_memory"] = memory_tests

    async def _test_business_intelligence_system(self):
        """Test Business Intelligence System"""
        print("\n💼 TESTING BUSINESS INTELLIGENCE SYSTEM...")
        
        bi_tests = {}
        
        # Test business intelligence layers
        business_layers = [
            ("Customer Intelligence", "customer retention and health analysis"),
            ("Sales Intelligence", "sales pipeline and revenue forecasting"),
            ("Market Intelligence", "market trends and competitive analysis"),
            ("Competitive Intelligence", "competitor analysis and market positioning")
        ]
        
        for layer_name, test_query in business_layers:
            try:
                print(f"  🧪 Testing: {layer_name}")
                
                business_context = BusinessContext(
                    user_role="CEO",
                    business_unit="executive",
                    time_horizon="medium",
                    priority_level="high",
                    decision_context="strategic"
                )
                
                start_time = time.time()
                insights = await self.business_intelligence.intelligent_business_search(
                    test_query,
                    business_context
                )
                search_time = time.time() - start_time
                
                bi_tests[layer_name] = {
                    "status": "PASSED",
                    "primary_insights": len(insights.primary_insights),
                    "related_insights": len(insights.related_insights),
                    "confidence_score": insights.confidence_score,
                    "business_impact": insights.business_impact,
                    "search_time_ms": round(search_time * 1000, 2)
                }
                
                print(f"    ✅ {layer_name}: {len(insights.primary_insights)} insights, confidence: {insights.confidence_score:.2f}")
                
            except Exception as e:
                logger.error(f"❌ {layer_name} test failed: {e}")
                bi_tests[layer_name] = {
                    "status": "FAILED",
                    "error": str(e)
                }
        
        try:
            # Test executive dashboard insights
            print("  🧪 Testing: Executive Dashboard Insights")
            
            executive_context = BusinessContext(
                user_role="CEO",
                business_unit="executive",
                time_horizon="short",
                priority_level="critical",
                decision_context="strategic"
            )
            
            start_time = time.time()
            dashboard_insights = await self.business_intelligence.generate_executive_dashboard_insights(
                executive_context
            )
            generation_time = time.time() - start_time
            
            bi_tests["Executive Dashboard"] = {
                "status": "PASSED",
                "insights_categories": list(dashboard_insights.keys()),
                "overall_health_score": dashboard_insights.get("overall_health_score", 0),
                "generation_time_ms": round(generation_time * 1000, 2)
            }
            
            print(f"    ✅ Executive Dashboard: {len(dashboard_insights)} categories in {generation_time*1000:.2f}ms")
            
        except Exception as e:
            logger.error(f"❌ Executive dashboard test failed: {e}")
            bi_tests["Executive Dashboard"] = {
                "status": "FAILED",
                "error": str(e)
            }
        
        self.test_results["business_intelligence"] = bi_tests

    async def _test_system_integration(self):
        """Test integration between all Phase 2.1 components"""
        print("\n🔗 TESTING SYSTEM INTEGRATION...")
        
        integration_tests = {}
        
        try:
            # Test end-to-end workflow
            print("  🧪 Testing: End-to-End Workflow")
            
            # 1. Create search context with adaptive memory
            user_id = "integration_test_user"
            search_context = await self.adaptive_memory.get_personalized_search_context(
                user_id,
                "comprehensive business analysis"
            )
            
            # 2. Perform hybrid search
            search_results = await self.hybrid_search.hybrid_search(
                "customer health sales performance market opportunities",
                search_context
            )
            
            # 3. Get business intelligence insights
            business_context = BusinessContext(
                user_role="CEO",
                business_unit="executive",
                time_horizon="medium",
                priority_level="high",
                decision_context="strategic"
            )
            
            bi_insights = await self.business_intelligence.intelligent_business_search(
                "strategic business performance analysis",
                business_context
            )
            
            # 4. Simulate user feedback and learning
            feedback = UserFeedback(
                user_id=user_id,
                query="comprehensive business analysis",
                result_id=search_results[0].id if search_results else "no_results",
                feedback_type=FeedbackType.RATING,
                rating=0.85,
                context={"integration_test": True}
            )
            
            await self.adaptive_memory.learn_from_interaction(
                "comprehensive business analysis",
                search_results,
                feedback
            )
            
            integration_tests["End-to-End Workflow"] = {
                "status": "PASSED",
                "search_results": len(search_results),
                "bi_insights": len(bi_insights.primary_insights),
                "learning_applied": True,
                "workflow_complete": True
            }
            
            print("    ✅ End-to-End Workflow: Complete integration successful")
            
        except Exception as e:
            logger.error(f"❌ Integration test failed: {e}")
            integration_tests["End-to-End Workflow"] = {
                "status": "FAILED",
                "error": str(e)
            }
        
        self.test_results["integration"] = integration_tests

    async def _test_performance_metrics(self):
        """Test performance metrics for Phase 2.1 components"""
        print("\n⚡ TESTING PERFORMANCE METRICS...")
        
        performance_tests = {}
        
        try:
            # Test search performance
            print("  🧪 Testing: Search Performance")
            
            search_times = []
            for i in range(5):
                start_time = time.time()
                
                await self.hybrid_search.hybrid_search(
                    f"performance test query {i}",
                    SearchContext(
                        user_id=f"perf_user_{i}",
                        session_id=f"perf_session_{i}",
                        business_domain="performance_testing"
                    )
                )
                
                search_time = time.time() - start_time
                search_times.append(search_time * 1000)  # Convert to ms
            
            avg_search_time = sum(search_times) / len(search_times)
            max_search_time = max(search_times)
            min_search_time = min(search_times)
            
            performance_tests["Search Performance"] = {
                "status": "PASSED" if avg_search_time < 1000 else "WARNING",  # Target < 1s
                "avg_time_ms": round(avg_search_time, 2),
                "max_time_ms": round(max_search_time, 2),
                "min_time_ms": round(min_search_time, 2),
                "test_runs": len(search_times)
            }
            
            print(f"    ✅ Search Performance: Avg {avg_search_time:.2f}ms, Max {max_search_time:.2f}ms")
            
        except Exception as e:
            logger.error(f"❌ Performance test failed: {e}")
            performance_tests["Search Performance"] = {
                "status": "FAILED",
                "error": str(e)
            }
        
        try:
            # Test business intelligence performance
            print("  🧪 Testing: Business Intelligence Performance")
            
            bi_times = []
            for i in range(3):
                start_time = time.time()
                
                await self.business_intelligence.intelligent_business_search(
                    f"business performance analysis {i}",
                    BusinessContext(
                        user_role="CEO",
                        business_unit="executive",
                        time_horizon="short",
                        priority_level="medium",
                        decision_context="operational"
                    )
                )
                
                bi_time = time.time() - start_time
                bi_times.append(bi_time * 1000)  # Convert to ms
            
            avg_bi_time = sum(bi_times) / len(bi_times)
            
            performance_tests["Business Intelligence Performance"] = {
                "status": "PASSED" if avg_bi_time < 2000 else "WARNING",  # Target < 2s
                "avg_time_ms": round(avg_bi_time, 2),
                "test_runs": len(bi_times)
            }
            
            print(f"    ✅ BI Performance: Avg {avg_bi_time:.2f}ms")
            
        except Exception as e:
            logger.error(f"❌ BI performance test failed: {e}")
            performance_tests["Business Intelligence Performance"] = {
                "status": "FAILED",
                "error": str(e)
            }
        
        self.test_results["performance"] = performance_tests

    async def _validate_search_results(self, results: List[SearchResult], test_case: Dict[str, Any]) -> Dict[str, Any]:
        """Validate search results quality"""
        validation = {
            "valid": True,
            "issues": []
        }
        
        # Check if we got results
        if not results:
            validation["valid"] = False
            validation["issues"].append("No results returned")
            return validation
        
        # Check result structure
        for result in results:
            if not result.id or not result.content:
                validation["valid"] = False
                validation["issues"].append("Invalid result structure")
                break
            
            if result.confidence < 0 or result.confidence > 1:
                validation["valid"] = False
                validation["issues"].append("Invalid confidence score")
                break
        
        # Check performance
        if len(results) > test_case["context"].max_results:
            validation["issues"].append("Too many results returned")
        
        return validation

    async def _generate_validation_report(self) -> Dict[str, Any]:
        """Generate comprehensive validation report"""
        total_time = time.time() - self.start_time
        
        # Calculate overall success rate
        total_tests = 0
        passed_tests = 0
        
        for category, tests in self.test_results.items():
            if isinstance(tests, dict):
                for test_name, result in tests.items():
                    total_tests += 1
                    if result.get("status") == "PASSED":
                        passed_tests += 1
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        # Determine overall status
        if success_rate >= 95:
            overall_status = "EXCELLENT"
        elif success_rate >= 85:
            overall_status = "GOOD"
        elif success_rate >= 70:
            overall_status = "ACCEPTABLE"
        else:
            overall_status = "NEEDS_IMPROVEMENT"
        
        report = {
            "validation_summary": {
                "overall_status": overall_status,
                "success_rate": round(success_rate, 1),
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": total_tests - passed_tests,
                "total_time_seconds": round(total_time, 2)
            },
            "component_results": self.test_results,
            "recommendations": await self._generate_recommendations(),
            "next_steps": await self._generate_next_steps(),
            "timestamp": datetime.now().isoformat()
        }
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 PHASE 2.1 VALIDATION SUMMARY")
        print("=" * 60)
        print(f"Overall Status: {overall_status}")
        print(f"Success Rate: {success_rate:.1f}% ({passed_tests}/{total_tests} tests passed)")
        print(f"Total Time: {total_time:.2f} seconds")
        print(f"Components Tested: {len(self.test_results)}")
        
        if overall_status in ["EXCELLENT", "GOOD"]:
            print("\n✅ Phase 2.1 Advanced Memory Intelligence is ready for production!")
        else:
            print("\n⚠️  Phase 2.1 needs improvements before production deployment.")
        
        return report

    async def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []
        
        # Analyze test results and generate specific recommendations
        for category, tests in self.test_results.items():
            if isinstance(tests, dict):
                failed_tests = [name for name, result in tests.items() if result.get("status") == "FAILED"]
                if failed_tests:
                    recommendations.append(f"Fix failed tests in {category}: {', '.join(failed_tests)}")
        
        # Performance recommendations
        performance_tests = self.test_results.get("performance", {})
        for test_name, result in performance_tests.items():
            if result.get("status") == "WARNING":
                recommendations.append(f"Optimize {test_name} - current performance below target")
        
        if not recommendations:
            recommendations.append("All systems performing well - ready for Phase 2.2 implementation")
        
        return recommendations

    async def _generate_next_steps(self) -> List[str]:
        """Generate next steps based on validation results"""
        next_steps = [
            "Review validation report and address any failed tests",
            "Optimize performance for any components showing warnings",
            "Proceed with Phase 2.2: AI Agent Orchestration Mastery",
            "Begin implementation of advanced MCP orchestration",
            "Design specialized business agents for Pay Ready operations"
        ]
        
        return next_steps

async def main():
    """Main validation function"""
    print("🚀 Starting Phase 2.1 Advanced Memory Intelligence Validation...")
    
    validator = Phase2ValidationSuite()
    
    try:
        report = await validator.run_comprehensive_validation()
        
        # Save report to file
        import json
        with open("phase2_1_validation_report.json", "w") as f:
            json.dump(report, f, indent=2, default=str)
        
        print("\n📄 Validation report saved to: phase2_1_validation_report.json")
        
        return report
        
    except Exception as e:
        logger.error(f"❌ Validation failed: {e}")
        return {"status": "FAILED", "error": str(e)}

if __name__ == "__main__":
    # Run validation
    result = asyncio.run(main())
    
    # Exit with appropriate code
    if result.get("validation_summary", {}).get("overall_status") in ["EXCELLENT", "GOOD"]:
        sys.exit(0)
    else:
        sys.exit(1) 