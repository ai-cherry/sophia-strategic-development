#!/usr/bin/env python3
"""
Comprehensive Test Script for Simplified Portkey Service
Tests all aspects of the simplified LLM architecture
"""

import asyncio
import sys
import os
import json
import time
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.services.simplified_portkey_service import (
    SophiaLLM, 
    SimplifiedPortkeyService,
    TaskType,
    ModelTier,
    SimplifiedLLMRequest
)


class PortkeyTestSuite:
    """Comprehensive test suite for simplified Portkey service"""
    
    def __init__(self):
        self.results = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "errors": [],
            "performance_metrics": {}
        }
        
    def log(self, message: str, level: str = "INFO"):
        """Log test messages with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
    
    async def test_service_initialization(self) -> bool:
        """Test 1: Service initialization and configuration"""
        self.log("🧪 Test 1: Service Initialization")
        self.results["total_tests"] += 1
        
        try:
            service = SimplifiedPortkeyService()
            
            # Check virtual key configuration
            if not service.virtual_key:
                self.log("❌ Virtual key not configured", "ERROR")
                self.results["errors"].append("Virtual key missing")
                self.results["failed"] += 1
                return False
            
            # Initialize service
            success = await service.initialize()
            
            if success:
                self.log("✅ Service initialized successfully")
                self.results["passed"] += 1
                return True
            else:
                self.log("❌ Service initialization failed", "ERROR")
                self.results["failed"] += 1
                return False
                
        except Exception as e:
            self.log(f"❌ Service initialization error: {e}", "ERROR")
            self.results["errors"].append(f"Init error: {str(e)}")
            self.results["failed"] += 1
            return False
    
    async def test_health_check(self) -> bool:
        """Test 2: Health check functionality"""
        self.log("🧪 Test 2: Health Check")
        self.results["total_tests"] += 1
        
        try:
            service = await SophiaLLM._get_service()
            is_healthy = await service._health_check()
            
            if is_healthy:
                self.log("✅ Health check passed - Portkey connection OK")
                self.results["passed"] += 1
                return True
            else:
                self.log("❌ Health check failed - Portkey unreachable", "ERROR")
                self.results["failed"] += 1
                return False
                
        except Exception as e:
            self.log(f"❌ Health check error: {e}", "ERROR")
            self.results["errors"].append(f"Health check error: {str(e)}")
            self.results["failed"] += 1
            return False
    
    async def test_basic_chat(self) -> bool:
        """Test 3: Basic chat functionality"""
        self.log("🧪 Test 3: Basic Chat")
        self.results["total_tests"] += 1
        
        try:
            start_time = time.time()
            response = await SophiaLLM.chat(
                "Hello! Please respond with exactly: 'Sophia AI simplified Portkey service is working!'",
                TaskType.CHAT_GENERAL
            )
            end_time = time.time()
            
            response_time = int((end_time - start_time) * 1000)
            
            if response.success:
                self.log(f"✅ Basic chat successful (Response time: {response_time}ms)")
                self.log(f"   Model: {response.model_used}")
                self.log(f"   Tokens: {response.tokens_used}")
                self.log(f"   Cost: ${response.cost_estimate:.4f}")
                self.log(f"   Content: {response.content[:100]}...")
                
                # Store performance metrics
                self.results["performance_metrics"]["basic_chat"] = {
                    "response_time_ms": response_time,
                    "tokens_used": response.tokens_used,
                    "cost_estimate": response.cost_estimate,
                    "model_used": response.model_used
                }
                
                self.results["passed"] += 1
                return True
            else:
                self.log(f"❌ Basic chat failed: {response.error}", "ERROR")
                self.results["failed"] += 1
                return False
                
        except Exception as e:
            self.log(f"❌ Basic chat error: {e}", "ERROR")
            self.results["errors"].append(f"Basic chat error: {str(e)}")
            self.results["failed"] += 1
            return False
    
    async def test_business_analysis(self) -> bool:
        """Test 4: Business analysis (CEO insights)"""
        self.log("🧪 Test 4: Business Analysis (CEO Insights)")
        self.results["total_tests"] += 1
        
        try:
            start_time = time.time()
            response = await SophiaLLM.analyze_business(
                "Analyze current market trends in AI technology",
                {"industry": "AI", "timeframe": "Q4 2024"}
            )
            end_time = time.time()
            
            response_time = int((end_time - start_time) * 1000)
            
            if response.success:
                self.log(f"✅ Business analysis successful (Response time: {response_time}ms)")
                self.log(f"   Model: {response.model_used}")
                self.log(f"   Tokens: {response.tokens_used}")
                self.log(f"   Cost: ${response.cost_estimate:.4f}")
                self.log(f"   Task Type: {response.task_type}")
                
                # Check if premium model was used for CEO insights
                if "premium" in response.model_used.lower() or "gpt-4o" in response.model_used.lower() or "opus" in response.model_used.lower():
                    self.log("✅ Premium model correctly used for CEO insights")
                else:
                    self.log(f"⚠️ Non-premium model used: {response.model_used}", "WARNING")
                
                self.results["performance_metrics"]["business_analysis"] = {
                    "response_time_ms": response_time,
                    "tokens_used": response.tokens_used,
                    "cost_estimate": response.cost_estimate,
                    "model_used": response.model_used
                }
                
                self.results["passed"] += 1
                return True
            else:
                self.log(f"❌ Business analysis failed: {response.error}", "ERROR")
                self.results["failed"] += 1
                return False
                
        except Exception as e:
            self.log(f"❌ Business analysis error: {e}", "ERROR")
            self.results["errors"].append(f"Business analysis error: {str(e)}")
            self.results["failed"] += 1
            return False
    
    async def test_code_generation(self) -> bool:
        """Test 5: Code generation"""
        self.log("🧪 Test 5: Code Generation")
        self.results["total_tests"] += 1
        
        try:
            start_time = time.time()
            response = await SophiaLLM.generate_code(
                "Create a simple Python function that calculates factorial",
                "python"
            )
            end_time = time.time()
            
            response_time = int((end_time - start_time) * 1000)
            
            if response.success:
                self.log(f"✅ Code generation successful (Response time: {response_time}ms)")
                self.log(f"   Model: {response.model_used}")
                self.log(f"   Tokens: {response.tokens_used}")
                self.log(f"   Cost: ${response.cost_estimate:.4f}")
                self.log(f"   Task Type: {response.task_type}")
                
                # Check if code contains factorial logic
                if "factorial" in response.content.lower() or "def " in response.content:
                    self.log("✅ Generated code contains expected elements")
                else:
                    self.log("⚠️ Generated code may not contain expected elements", "WARNING")
                
                self.results["performance_metrics"]["code_generation"] = {
                    "response_time_ms": response_time,
                    "tokens_used": response.tokens_used,
                    "cost_estimate": response.cost_estimate,
                    "model_used": response.model_used
                }
                
                self.results["passed"] += 1
                return True
            else:
                self.log(f"❌ Code generation failed: {response.error}", "ERROR")
                self.results["failed"] += 1
                return False
                
        except Exception as e:
            self.log(f"❌ Code generation error: {e}", "ERROR")
            self.results["errors"].append(f"Code generation error: {str(e)}")
            self.results["failed"] += 1
            return False
    
    async def test_task_routing(self) -> bool:
        """Test 6: Intelligent task routing"""
        self.log("🧪 Test 6: Task Routing Verification")
        self.results["total_tests"] += 1
        
        try:
            # Test different task types
            task_tests = [
                (TaskType.CEO_INSIGHTS, "Analyze company performance"),
                (TaskType.CODE_GENERATION, "Write a Python script"),
                (TaskType.CHAT_GENERAL, "Hello, how are you?")
            ]
            
            routing_results = {}
            
            for task_type, message in task_tests:
                response = await SophiaLLM.chat(message, task_type)
                if response.success:
                    routing_results[task_type.value] = {
                        "model_used": response.model_used,
                        "cost_estimate": response.cost_estimate,
                        "tokens_used": response.tokens_used
                    }
                    self.log(f"   {task_type.value}: {response.model_used}")
            
            # Store routing analysis
            self.results["performance_metrics"]["task_routing"] = routing_results
            
            if len(routing_results) == len(task_tests):
                self.log("✅ Task routing working correctly")
                self.results["passed"] += 1
                return True
            else:
                self.log("❌ Some task routing tests failed", "ERROR")
                self.results["failed"] += 1
                return False
                
        except Exception as e:
            self.log(f"❌ Task routing error: {e}", "ERROR")
            self.results["errors"].append(f"Task routing error: {str(e)}")
            self.results["failed"] += 1
            return False
    
    async def test_streaming(self) -> bool:
        """Test 7: Streaming functionality"""
        self.log("🧪 Test 7: Streaming")
        self.results["total_tests"] += 1
        
        try:
            service = await SophiaLLM._get_service()
            request = SimplifiedLLMRequest(
                messages=[{"role": "user", "content": "Count from 1 to 5, each number on a new line"}],
                task_type=TaskType.CHAT_GENERAL,
                stream=True
            )
            
            chunks_received = 0
            start_time = time.time()
            
            async for chunk in service.stream_complete(request):
                chunks_received += 1
                if chunks_received <= 3:  # Log first few chunks
                    self.log(f"   Chunk {chunks_received}: {chunk[:50]}...")
            
            end_time = time.time()
            streaming_time = int((end_time - start_time) * 1000)
            
            if chunks_received > 0:
                self.log(f"✅ Streaming successful ({chunks_received} chunks in {streaming_time}ms)")
                self.results["performance_metrics"]["streaming"] = {
                    "chunks_received": chunks_received,
                    "total_time_ms": streaming_time
                }
                self.results["passed"] += 1
                return True
            else:
                self.log("❌ No streaming chunks received", "ERROR")
                self.results["failed"] += 1
                return False
                
        except Exception as e:
            self.log(f"❌ Streaming error: {e}", "ERROR")
            self.results["errors"].append(f"Streaming error: {str(e)}")
            self.results["failed"] += 1
            return False
    
    async def test_error_handling(self) -> bool:
        """Test 8: Error handling and fallbacks"""
        self.log("🧪 Test 8: Error Handling")
        self.results["total_tests"] += 1
        
        try:
            # Test with invalid/very long input
            response = await SophiaLLM.chat(
                "X" * 50000,  # Very long message to potentially trigger errors
                TaskType.CHAT_GENERAL,
                max_tokens=1  # Very low token limit
            )
            
            # Should either succeed with truncation or fail gracefully
            if response.success or (not response.success and response.error):
                self.log("✅ Error handling working correctly")
                if not response.success:
                    self.log(f"   Graceful error: {response.error}")
                self.results["passed"] += 1
                return True
            else:
                self.log("❌ Error handling failed", "ERROR")
                self.results["failed"] += 1
                return False
                
        except Exception as e:
            self.log(f"❌ Error handling test error: {e}", "ERROR")
            self.results["errors"].append(f"Error handling error: {str(e)}")
            self.results["failed"] += 1
            return False
    
    def print_summary(self):
        """Print comprehensive test summary"""
        self.log("\n" + "="*60)
        self.log("📊 SIMPLIFIED PORTKEY TEST RESULTS")
        self.log("="*60)
        
        success_rate = (self.results["passed"] / self.results["total_tests"]) * 100 if self.results["total_tests"] > 0 else 0
        
        self.log(f"Total Tests: {self.results['total_tests']}")
        self.log(f"Passed: {self.results['passed']}")
        self.log(f"Failed: {self.results['failed']}")
        self.log(f"Success Rate: {success_rate:.1f}%")
        
        if self.results["errors"]:
            self.log("\n❌ ERRORS:")
            for error in self.results["errors"]:
                self.log(f"   • {error}")
        
        if self.results["performance_metrics"]:
            self.log("\n📈 PERFORMANCE METRICS:")
            for test_name, metrics in self.results["performance_metrics"].items():
                self.log(f"   {test_name}:")
                for metric, value in metrics.items():
                    self.log(f"     - {metric}: {value}")
        
        # Overall assessment
        if success_rate >= 90:
            self.log("\n🎉 ASSESSMENT: Excellent - Ready for production!")
        elif success_rate >= 75:
            self.log("\n✅ ASSESSMENT: Good - Minor issues to address")
        elif success_rate >= 50:
            self.log("\n⚠️ ASSESSMENT: Fair - Several issues need fixing")
        else:
            self.log("\n❌ ASSESSMENT: Poor - Major issues need resolution")
        
        # Recommendations
        self.log("\n💡 RECOMMENDATIONS:")
        if self.results["failed"] > 0:
            self.log("   • Check Portkey virtual key configuration")
            self.log("   • Verify network connectivity to Portkey API")
            self.log("   • Review error messages above for specific issues")
        else:
            self.log("   • All tests passed! System is ready for migration")
            self.log("   • Consider monitoring cost savings through Portkey dashboard")
            self.log("   • Set up usage alerts for cost control")
    
    async def run_all_tests(self):
        """Run the complete test suite"""
        self.log("🚀 Starting Comprehensive Portkey Test Suite")
        self.log("="*60)
        
        tests = [
            self.test_service_initialization,
            self.test_health_check,
            self.test_basic_chat,
            self.test_business_analysis,
            self.test_code_generation,
            self.test_task_routing,
            self.test_streaming,
            self.test_error_handling
        ]
        
        for test in tests:
            try:
                await test()
                await asyncio.sleep(0.5)  # Brief pause between tests
            except Exception as e:
                self.log(f"❌ Test execution error: {e}", "ERROR")
                self.results["failed"] += 1
                self.results["errors"].append(f"Test execution error: {str(e)}")
        
        self.print_summary()
        
        # Save results to file
        results_file = project_root / "test_results_simplified_portkey.json"
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        self.log(f"\n📝 Results saved to: {results_file}")


async def main():
    """Main test execution"""
    print("🧪 Sophia AI - Simplified Portkey Service Test Suite")
    print("Testing 100% Portkey with Virtual Keys Architecture")
    print("="*70)
    
    # Check environment
    if not os.getenv("PORTKEY_VIRTUAL_KEY_PROD") and not os.getenv("PORTKEY_API_KEY"):
        print("⚠️ WARNING: No Portkey credentials found in environment")
        print("Please set PORTKEY_VIRTUAL_KEY_PROD or PORTKEY_API_KEY")
        print("This test will attempt to load from Pulumi ESC...")
    
    # Run tests
    test_suite = PortkeyTestSuite()
    await test_suite.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main()) 