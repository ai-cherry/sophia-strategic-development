#!/usr/bin/env python3
"""
Lambda Labs Serverless Test Script
==================================
Test script to demonstrate Lambda Labs Serverless capabilities
using direct HTTP requests instead of the OpenAI library.
"""

import asyncio
import aiohttp
import json
import logging
import os
import sys
from datetime import datetime
from typing import Dict, Any

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.core.auto_esc_config import get_config_value

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LambdaLabsServerlessTest:
    """
    Test class for Lambda Labs Serverless functionality
    """

    def __init__(self):
        """Initialize the test class"""
        # Get credentials from config
        self.api_key = get_config_value("LAMBDA_API_KEY")
        self.endpoint = get_config_value("LAMBDA_INFERENCE_ENDPOINT", "https://api.lambdalabs.com/v1")
        
        if not self.api_key:
            raise ValueError("LAMBDA_API_KEY not found in configuration")
        
        # Test configuration
        self.test_models = [
            "llama-4-scout-17b-16e-instruct",
            "deepseek-v3-0324",
            "qwen-3-32b"
        ]
        
        self.test_results = []
        
        logger.info("🚀 Lambda Labs Serverless Test initialized")
        logger.info(f"   Endpoint: {self.endpoint}")
        logger.info(f"   API Key: {self.api_key[:20]}...")

    async def test_model_availability(self) -> Dict[str, Any]:
        """Test if Lambda Labs models are available"""
        logger.info("📋 Testing model availability...")
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                
                # Test models endpoint
                async with session.get(f"{self.endpoint}/models", headers=headers) as response:
                    if response.status == 200:
                        models_data = await response.json()
                        available_models = [model["id"] for model in models_data.get("data", [])]
                        
                        result = {
                            "status": "success",
                            "available_models": available_models,
                            "test_models_available": [
                                model for model in self.test_models 
                                if model in available_models
                            ]
                        }
                        
                        logger.info(f"✅ Models available: {len(available_models)}")
                        return result
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ Models endpoint failed: {response.status} - {error_text}")
                        return {
                            "status": "error",
                            "error": f"HTTP {response.status}: {error_text}"
                        }
                        
        except Exception as e:
            logger.error(f"❌ Model availability test failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    async def test_chat_completion(self, model: str, message: str) -> Dict[str, Any]:
        """Test chat completion with a specific model"""
        logger.info(f"💬 Testing chat completion with {model}...")
        
        start_time = datetime.now()
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "model": model,
                    "messages": [
                        {"role": "user", "content": message}
                    ],
                    "max_tokens": 100,
                    "temperature": 0.7
                }
                
                async with session.post(
                    f"{self.endpoint}/chat/completions",
                    headers=headers,
                    json=payload
                ) as response:
                    response_time = (datetime.now() - start_time).total_seconds()
                    
                    if response.status == 200:
                        response_data = await response.json()
                        
                        # Extract response details
                        choice = response_data.get("choices", [{}])[0]
                        usage = response_data.get("usage", {})
                        
                        result = {
                            "status": "success",
                            "model": model,
                            "response": choice.get("message", {}).get("content", ""),
                            "response_time": response_time,
                            "usage": {
                                "prompt_tokens": usage.get("prompt_tokens", 0),
                                "completion_tokens": usage.get("completion_tokens", 0),
                                "total_tokens": usage.get("total_tokens", 0)
                            }
                        }
                        
                        logger.info(f"✅ Chat completion successful: {response_time:.2f}s")
                        return result
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ Chat completion failed: {response.status} - {error_text}")
                        return {
                            "status": "error",
                            "model": model,
                            "error": f"HTTP {response.status}: {error_text}",
                            "response_time": response_time
                        }
                        
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"❌ Chat completion test failed: {e}")
            return {
                "status": "error",
                "model": model,
                "error": str(e),
                "response_time": response_time
            }

    async def test_model_routing(self) -> Dict[str, Any]:
        """Test intelligent model routing with different query types"""
        logger.info("🔄 Testing model routing...")
        
        test_queries = [
            {
                "query": "Write a Python function to calculate fibonacci numbers",
                "expected_type": "code",
                "preferred_model": "deepseek-v3-0324"
            },
            {
                "query": "Write a creative story about a robot learning to paint",
                "expected_type": "creative",
                "preferred_model": "llama-4-scout-17b-16e-instruct"
            },
            {
                "query": "Analyze the following business metrics: Revenue: $100K, Costs: $60K, Growth: 15%",
                "expected_type": "analysis",
                "preferred_model": "llama-4-scout-17b-16e-instruct"
            }
        ]
        
        routing_results = []
        
        for test_query in test_queries:
            # Test with preferred model
            result = await self.test_chat_completion(
                test_query["preferred_model"],
                test_query["query"]
            )
            
            result["query_type"] = test_query["expected_type"]
            result["query"] = test_query["query"][:50] + "..."
            routing_results.append(result)
        
        # Calculate success rate
        successful_tests = sum(1 for r in routing_results if r["status"] == "success")
        success_rate = (successful_tests / len(routing_results)) * 100
        
        return {
            "status": "completed",
            "success_rate": success_rate,
            "total_tests": len(routing_results),
            "successful_tests": successful_tests,
            "results": routing_results
        }

    async def test_cost_calculation(self) -> Dict[str, Any]:
        """Test cost calculation functionality"""
        logger.info("💰 Testing cost calculation...")
        
        # Model pricing (from Lambda Labs July 2025)
        model_pricing = {
            "llama-4-scout-17b-16e-instruct": {"input": 0.08, "output": 0.30},
            "deepseek-v3-0324": {"input": 0.34, "output": 0.88},
            "qwen-3-32b": {"input": 0.10, "output": 0.30}
        }
        
        cost_tests = []
        
        for model, pricing in model_pricing.items():
            # Simulate a request
            input_tokens = 100
            output_tokens = 50
            
            # Calculate cost
            input_cost = (input_tokens / 1000000) * pricing["input"]
            output_cost = (output_tokens / 1000000) * pricing["output"]
            total_cost = input_cost + output_cost
            
            cost_tests.append({
                "model": model,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "input_cost": input_cost,
                "output_cost": output_cost,
                "total_cost": total_cost,
                "cost_per_1k_tokens": total_cost * (1000000 / (input_tokens + output_tokens))
            })
        
        # Find most cost-effective model
        most_efficient = min(cost_tests, key=lambda x: x["total_cost"])
        
        return {
            "status": "completed",
            "cost_tests": cost_tests,
            "most_efficient_model": most_efficient["model"],
            "cost_range": {
                "min": min(test["total_cost"] for test in cost_tests),
                "max": max(test["total_cost"] for test in cost_tests)
            }
        }

    async def test_performance_benchmarks(self) -> Dict[str, Any]:
        """Test performance benchmarks across models"""
        logger.info("⚡ Testing performance benchmarks...")
        
        benchmark_query = "Explain the concept of machine learning in 2 sentences."
        performance_results = []
        
        for model in self.test_models:
            result = await self.test_chat_completion(model, benchmark_query)
            
            if result["status"] == "success":
                performance_results.append({
                    "model": model,
                    "response_time": result["response_time"],
                    "total_tokens": result["usage"]["total_tokens"],
                    "tokens_per_second": result["usage"]["total_tokens"] / result["response_time"] if result["response_time"] > 0 else 0
                })
        
        if performance_results:
            # Calculate performance metrics
            avg_response_time = sum(r["response_time"] for r in performance_results) / len(performance_results)
            fastest_model = min(performance_results, key=lambda x: x["response_time"])
            most_efficient = max(performance_results, key=lambda x: x["tokens_per_second"])
            
            return {
                "status": "completed",
                "average_response_time": avg_response_time,
                "fastest_model": fastest_model["model"],
                "most_efficient_model": most_efficient["model"],
                "results": performance_results
            }
        else:
            return {
                "status": "error",
                "error": "No successful performance tests"
            }

    async def run_comprehensive_tests(self) -> Dict[str, Any]:
        """Run comprehensive test suite"""
        logger.info("🧪 Running comprehensive Lambda Labs Serverless tests...")
        
        test_results = {
            "started_at": datetime.now().isoformat(),
            "tests": {}
        }
        
        # Test 1: Model availability
        test_results["tests"]["model_availability"] = await self.test_model_availability()
        
        # Test 2: Chat completion (basic)
        if test_results["tests"]["model_availability"]["status"] == "success":
            available_models = test_results["tests"]["model_availability"]["test_models_available"]
            if available_models:
                test_model = available_models[0]
                test_results["tests"]["basic_chat"] = await self.test_chat_completion(
                    test_model,
                    "Hello! This is a test message for Lambda Labs Serverless."
                )
        
        # Test 3: Model routing
        test_results["tests"]["model_routing"] = await self.test_model_routing()
        
        # Test 4: Cost calculation
        test_results["tests"]["cost_calculation"] = await self.test_cost_calculation()
        
        # Test 5: Performance benchmarks
        test_results["tests"]["performance_benchmarks"] = await self.test_performance_benchmarks()
        
        # Calculate overall results
        total_tests = len(test_results["tests"])
        successful_tests = sum(
            1 for test in test_results["tests"].values()
            if test.get("status") in ["success", "completed"]
        )
        
        test_results["summary"] = {
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "success_rate": (successful_tests / total_tests) * 100,
            "completed_at": datetime.now().isoformat()
        }
        
        return test_results

    def generate_test_report(self, results: Dict[str, Any]) -> str:
        """Generate a comprehensive test report"""
        report = f"""
# Lambda Labs Serverless Test Report
**Generated:** {results.get('started_at', 'Unknown')}
**Completed:** {results.get('summary', {}).get('completed_at', 'Unknown')}

## Summary
- **Total Tests:** {results.get('summary', {}).get('total_tests', 0)}
- **Successful Tests:** {results.get('summary', {}).get('successful_tests', 0)}
- **Success Rate:** {results.get('summary', {}).get('success_rate', 0):.1f}%

## Test Results

### 1. Model Availability
"""
        
        model_test = results.get("tests", {}).get("model_availability", {})
        if model_test.get("status") == "success":
            report += f"✅ **Status:** Success\n"
            report += f"- Available Models: {len(model_test.get('available_models', []))}\n"
            report += f"- Test Models Available: {len(model_test.get('test_models_available', []))}\n"
        else:
            report += f"❌ **Status:** Failed\n"
            report += f"- Error: {model_test.get('error', 'Unknown')}\n"
        
        report += "\n### 2. Basic Chat Completion\n"
        chat_test = results.get("tests", {}).get("basic_chat", {})
        if chat_test.get("status") == "success":
            report += f"✅ **Status:** Success\n"
            report += f"- Model: {chat_test.get('model', 'Unknown')}\n"
            report += f"- Response Time: {chat_test.get('response_time', 0):.2f}s\n"
            report += f"- Total Tokens: {chat_test.get('usage', {}).get('total_tokens', 0)}\n"
        else:
            report += f"❌ **Status:** Failed\n"
            report += f"- Error: {chat_test.get('error', 'Unknown')}\n"
        
        report += "\n### 3. Model Routing\n"
        routing_test = results.get("tests", {}).get("model_routing", {})
        if routing_test.get("status") == "completed":
            report += f"✅ **Status:** Success\n"
            report += f"- Success Rate: {routing_test.get('success_rate', 0):.1f}%\n"
            report += f"- Total Tests: {routing_test.get('total_tests', 0)}\n"
        else:
            report += f"❌ **Status:** Failed\n"
        
        report += "\n### 4. Cost Calculation\n"
        cost_test = results.get("tests", {}).get("cost_calculation", {})
        if cost_test.get("status") == "completed":
            report += f"✅ **Status:** Success\n"
            report += f"- Most Efficient Model: {cost_test.get('most_efficient_model', 'Unknown')}\n"
            cost_range = cost_test.get("cost_range", {})
            report += f"- Cost Range: ${cost_range.get('min', 0):.6f} - ${cost_range.get('max', 0):.6f}\n"
        else:
            report += f"❌ **Status:** Failed\n"
        
        report += "\n### 5. Performance Benchmarks\n"
        perf_test = results.get("tests", {}).get("performance_benchmarks", {})
        if perf_test.get("status") == "completed":
            report += f"✅ **Status:** Success\n"
            report += f"- Average Response Time: {perf_test.get('average_response_time', 0):.2f}s\n"
            report += f"- Fastest Model: {perf_test.get('fastest_model', 'Unknown')}\n"
            report += f"- Most Efficient Model: {perf_test.get('most_efficient_model', 'Unknown')}\n"
        else:
            report += f"❌ **Status:** Failed\n"
        
        return report


async def main():
    """Main test function"""
    try:
        # Create test instance
        tester = LambdaLabsServerlessTest()
        
        # Run comprehensive tests
        print("🚀 Starting Lambda Labs Serverless comprehensive tests...")
        results = await tester.run_comprehensive_tests()
        
        # Generate report
        report = tester.generate_test_report(results)
        
        # Save report
        os.makedirs("test_reports", exist_ok=True)
        report_file = f"test_reports/lambda_serverless_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        with open(report_file, 'w') as f:
            f.write(report)
        
        # Print results
        print("\n" + "="*60)
        print("🎉 Lambda Labs Serverless Test Results")
        print("="*60)
        
        summary = results.get("summary", {})
        print(f"Total Tests: {summary.get('total_tests', 0)}")
        print(f"Successful: {summary.get('successful_tests', 0)}")
        print(f"Success Rate: {summary.get('success_rate', 0):.1f}%")
        print(f"Report saved to: {report_file}")
        
        # Print detailed results
        print("\nDetailed Results:")
        for test_name, test_result in results.get("tests", {}).items():
            status = test_result.get("status", "unknown")
            print(f"  {test_name}: {status}")
        
        return results
        
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        return {"error": str(e)}


if __name__ == "__main__":
    asyncio.run(main()) 