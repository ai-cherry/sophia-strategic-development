#!/usr/bin/env python3
"""
Sophia AI Performance Validation Script
Validates research-backed performance targets:
- Sub-200ms API response times
- 220+ N8N workflow executions/second
- Sub-100ms Estuary Flow data latency
"""

import asyncio
import aiohttp
import time
import os
import json
from typing import Dict, List

class PerformanceValidator:
    def __init__(self):
        self.lambda_ip = os.getenv('LAMBDA_LABS_INSTANCE_IP', 'localhost')
        self.targets = {
            'api_response_time_ms': 200,
            'n8n_throughput_per_second': 220,
            'estuary_latency_ms': 100,
            'availability_percent': 99.9
        }
        
    async def test_api_response_times(self) -> Dict[str, float]:
        """Test API response times with concurrent requests"""
        print("🔍 Testing API response times...")
        
        async with aiohttp.ClientSession() as session:
            start_time = time.time()
            tasks = []
            
            # Send 100 concurrent requests
            for i in range(100):
                task = session.get(f"http://{self.lambda_ip}:8000/api/health")
                tasks.append(task)
            
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            end_time = time.time()
            
            # Calculate metrics
            successful_responses = [r for r in responses if not isinstance(r, Exception)]
            success_rate = len(successful_responses) / len(responses) * 100
            avg_response_time = ((end_time - start_time) * 1000) / len(successful_responses)
            
            return {
                'avg_response_time_ms': avg_response_time,
                'success_rate_percent': success_rate,
                'total_requests': len(responses),
                'successful_requests': len(successful_responses)
            }
    
    async def test_n8n_throughput(self) -> Dict[str, float]:
        """Test N8N workflow execution throughput"""
        print("⚡ Testing N8N workflow throughput...")
        
        async with aiohttp.ClientSession() as session:
            start_time = time.time()
            tasks = []
            
            # Send 220 workflow execution requests
            for i in range(220):
                task = session.post(
                    f"http://{self.lambda_ip}:5678/webhook/performance-test",
                    json={"test_id": f"perf_test_{i}", "timestamp": start_time}
                )
                tasks.append(task)
            
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            end_time = time.time()
            
            successful_responses = [r for r in responses if not isinstance(r, Exception)]
            duration = end_time - start_time
            throughput = len(successful_responses) / duration
            
            return {
                'throughput_per_second': throughput,
                'duration_seconds': duration,
                'successful_executions': len(successful_responses),
                'total_executions': len(responses)
            }
    
    async def test_estuary_latency(self) -> Dict[str, float]:
        """Test Estuary Flow end-to-end latency"""
        print("🌊 Testing Estuary Flow latency...")
        
        async with aiohttp.ClientSession() as session:
            test_start = time.time()
            
            # Insert test data into PostgreSQL
            await session.post(
                f"http://{self.lambda_ip}:8000/api/test/insert",
                json={
                    "message": "estuary_latency_test",
                    "timestamp": test_start,
                    "test_id": f"latency_{int(test_start)}"
                }
            )
            
            # Poll for data in vector database (should appear within 100ms)
            max_wait_time = 5.0  # 5 second timeout
            poll_interval = 0.01  # 10ms polling
            
            while (time.time() - test_start) < max_wait_time:
                response = await session.get(
                    f"http://{self.lambda_ip}:8000/api/vectors/search",
                    params={"query": f"latency_{int(test_start)}"}
                )
                
                if response.status == 200:
                    data = await response.json()
                    if data.get('results'):
                        latency = (time.time() - test_start) * 1000
                        return {
                            'latency_ms': latency,
                            'success': True,
                            'data_found': True
                        }
                
                await asyncio.sleep(poll_interval)
            
            # Timeout case
            return {
                'latency_ms': max_wait_time * 1000,
                'success': False,
                'data_found': False
            }
    
    async def validate_all_targets(self) -> Dict[str, Dict]:
        """Run all performance validations"""
        print("🚀 Starting comprehensive performance validation...")
        print(f"Target metrics: {self.targets}")
        
        results = {}
        
        # Test API response times
        api_results = await self.test_api_response_times()
        results['api_performance'] = api_results
        api_passed = api_results['avg_response_time_ms'] < self.targets['api_response_time_ms']
        
        # Test N8N throughput
        n8n_results = await self.test_n8n_throughput()
        results['n8n_performance'] = n8n_results
        n8n_passed = n8n_results['throughput_per_second'] >= self.targets['n8n_throughput_per_second']
        
        # Test Estuary latency
        estuary_results = await self.test_estuary_latency()
        results['estuary_performance'] = estuary_results
        estuary_passed = (estuary_results['latency_ms'] < self.targets['estuary_latency_ms'] 
                         and estuary_results['success'])
        
        # Overall assessment
        results['validation_summary'] = {
            'api_response_passed': api_passed,
            'n8n_throughput_passed': n8n_passed,
            'estuary_latency_passed': estuary_passed,
            'overall_passed': api_passed and n8n_passed and estuary_passed
        }
        
        # Print results
        print("\n📊 Performance Validation Results:")
        print(f"  {'✅' if api_passed else '❌'} API Response Time: {api_results['avg_response_time_ms']:.2f}ms (target: <{self.targets['api_response_time_ms']}ms)")
        print(f"  {'✅' if n8n_passed else '❌'} N8N Throughput: {n8n_results['throughput_per_second']:.2f}/s (target: >{self.targets['n8n_throughput_per_second']}/s)")
        print(f"  {'✅' if estuary_passed else '❌'} Estuary Latency: {estuary_results['latency_ms']:.2f}ms (target: <{self.targets['estuary_latency_ms']}ms)")
        print(f"  {'🎉' if results['validation_summary']['overall_passed'] else '⚠️'} Overall: {'PASSED' if results['validation_summary']['overall_passed'] else 'FAILED'}")
        
        return results

async def main():
    validator = PerformanceValidator()
    results = await validator.validate_all_targets()
    
    # Save results to file
    with open('performance_validation_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    return 0 if results['validation_summary']['overall_passed'] else 1

if __name__ == "__main__":
    import sys
    sys.exit(asyncio.run(main()))
