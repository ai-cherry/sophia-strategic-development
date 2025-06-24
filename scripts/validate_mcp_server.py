#!/usr/bin/env python3
"""
MCP Server Validation Script
Validates MCP server health, configuration, and integration
"""

import argparse
import asyncio
import json
import logging
import sys
import time
import aiohttp
from pathlib import Path
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MCPServerValidator:
    """Validates MCP server functionality and integration"""
    
    def __init__(self, server_name: str, config_file: str = "cursor_mcp_config.json"):
        self.server_name = server_name
        self.config_file = Path(config_file)
        self.config = self._load_config()
        self.server_config = self._get_server_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load MCP configuration"""
        if not self.config_file.exists():
            raise FileNotFoundError(f"MCP config file not found: {self.config_file}")
        
        with open(self.config_file, 'r') as f:
            return json.load(f)
    
    def _get_server_config(self) -> Dict[str, Any]:
        """Get specific server configuration"""
        servers = self.config.get('mcpServers', {})
        if self.server_name not in servers:
            raise ValueError(f"Server {self.server_name} not found in configuration")
        
        return servers[self.server_name]
    
    async def validate_health_check(self) -> Dict[str, Any]:
        """Validate server health check"""
        logger.info(f"🔍 Validating health check for {self.server_name}")
        
        base_url = self.server_config.get('baseUrl')
        if not base_url:
            return {"status": "error", "message": "No baseUrl configured"}
        
        health_url = f"{base_url}/health"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(health_url, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "status": "healthy",
                            "response_time": response.headers.get('X-Response-Time', 'unknown'),
                            "data": data
                        }
                    else:
                        return {
                            "status": "unhealthy",
                            "status_code": response.status,
                            "message": await response.text()
                        }
        except asyncio.TimeoutError:
            return {"status": "timeout", "message": "Health check timed out"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def validate_capabilities(self) -> Dict[str, Any]:
        """Validate server capabilities"""
        logger.info(f"🔧 Validating capabilities for {self.server_name}")
        
        capabilities = self.server_config.get('capabilities', [])
        if not capabilities:
            return {"status": "warning", "message": "No capabilities defined"}
        
        # Test each capability
        capability_results = {}
        for capability in capabilities:
            capability_results[capability] = await self._test_capability(capability)
        
        return {
            "status": "tested",
            "capabilities": capability_results,
            "total_capabilities": len(capabilities)
        }
    
    async def _test_capability(self, capability: str) -> Dict[str, Any]:
        """Test a specific capability"""
        base_url = self.server_config.get('baseUrl')
        if not base_url:
            return {"status": "error", "message": "No baseUrl configured"}
        
        # Map capabilities to test endpoints
        capability_endpoints = {
            'conversation_storage': '/ai_memory/store',
            'context_recall': '/ai_memory/recall',
            'code_analysis': '/codacy/analyze',
            'security_scanning': '/codacy/security_scan',
            'schema_management': '/snowflake_admin/execute_admin_task',
            'project_management': '/asana/get_tasks',
            'knowledge_search': '/notion/search'
        }
        
        endpoint = capability_endpoints.get(capability)
        if not endpoint:
            return {"status": "unknown", "message": f"No test endpoint for {capability}"}
        
        test_url = f"{base_url}{endpoint}"
        
        try:
            async with aiohttp.ClientSession() as session:
                # Use HEAD request for testing availability
                async with session.head(test_url, timeout=5) as response:
                    return {
                        "status": "available" if response.status < 500 else "error",
                        "status_code": response.status
                    }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def validate_integration(self) -> Dict[str, Any]:
        """Validate integration with other components"""
        logger.info(f"🔗 Validating integration for {self.server_name}")
        
        integration_results = {}
        
        # Check auto-triggers
        auto_triggers = self.server_config.get('autoTriggers', {})
        integration_results['auto_triggers'] = {
            "configured": len(auto_triggers) > 0,
            "triggers": list(auto_triggers.keys())
        }
        
        # Check GitHub integration
        github_config = self.server_config.get('github', {})
        integration_results['github'] = {
            "enabled": github_config.get('enabled', False),
            "context_aware": github_config.get('contextAware', False),
            "auto_sync": github_config.get('autoSync', False)
        }
        
        # Check security configuration
        security_config = self.config.get('security', {})
        integration_results['security'] = {
            "configured": len(security_config) > 0,
            "features": list(security_config.keys())
        }
        
        return integration_results
    
    async def performance_test(self, duration: int = 60, concurrent_requests: int = 10) -> Dict[str, Any]:
        """Run performance test on MCP server"""
        logger.info(f"⚡ Running performance test for {self.server_name}")
        
        base_url = self.server_config.get('baseUrl')
        if not base_url:
            return {"status": "error", "message": "No baseUrl configured"}
        
        health_url = f"{base_url}/health"
        
        # Performance metrics
        response_times = []
        error_count = 0
        success_count = 0
        
        start_time = time.time()
        end_time = start_time + duration
        
        async def make_request(session):
            nonlocal error_count, success_count
            try:
                request_start = time.time()
                async with session.get(health_url, timeout=5) as response:
                    request_time = time.time() - request_start
                    response_times.append(request_time)
                    
                    if response.status == 200:
                        success_count += 1
                    else:
                        error_count += 1
            except Exception:
                error_count += 1
        
        async with aiohttp.ClientSession() as session:
            while time.time() < end_time:
                # Create concurrent requests
                tasks = [make_request(session) for _ in range(concurrent_requests)]
                await asyncio.gather(*tasks, return_exceptions=True)
                
                # Small delay between batches
                await asyncio.sleep(0.1)
        
        # Calculate metrics
        total_requests = success_count + error_count
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        max_response_time = max(response_times) if response_times else 0
        min_response_time = min(response_times) if response_times else 0
        
        return {
            "duration": duration,
            "total_requests": total_requests,
            "success_count": success_count,
            "error_count": error_count,
            "success_rate": success_count / total_requests if total_requests > 0 else 0,
            "avg_response_time": avg_response_time,
            "max_response_time": max_response_time,
            "min_response_time": min_response_time,
            "requests_per_second": total_requests / duration
        }
    
    async def comprehensive_validation(self, include_performance: bool = False) -> Dict[str, Any]:
        """Run comprehensive validation"""
        logger.info(f"🔍 Running comprehensive validation for {self.server_name}")
        
        results = {
            "server_name": self.server_name,
            "timestamp": time.time(),
            "validation_results": {}
        }
        
        # Health check
        results["validation_results"]["health"] = await self.validate_health_check()
        
        # Capabilities
        results["validation_results"]["capabilities"] = await self.validate_capabilities()
        
        # Integration
        results["validation_results"]["integration"] = await self.validate_integration()
        
        # Performance test (optional)
        if include_performance:
            results["validation_results"]["performance"] = await self.performance_test()
        
        # Overall status
        health_status = results["validation_results"]["health"]["status"]
        overall_status = "healthy" if health_status == "healthy" else "issues_detected"
        results["overall_status"] = overall_status
        
        return results


async def main():
    """Main validation function"""
    parser = argparse.ArgumentParser(description="MCP Server Validation")
    parser.add_argument("--server", required=True, help="MCP server name to validate")
    parser.add_argument("--config", default="cursor_mcp_config.json", help="MCP configuration file")
    parser.add_argument("--health-check", action="store_true", help="Run health check")
    parser.add_argument("--integration-test", action="store_true", help="Run integration test")
    parser.add_argument("--performance-test", action="store_true", help="Run performance test")
    parser.add_argument("--duration", type=int, default=60, help="Performance test duration")
    parser.add_argument("--concurrent-requests", type=int, default=10, help="Concurrent requests")
    parser.add_argument("--output", help="Output file for results")
    
    args = parser.parse_args()
    
    try:
        validator = MCPServerValidator(args.server, args.config)
        
        if args.health_check or args.integration_test or args.performance_test:
            # Run specific tests
            results = {"server_name": args.server, "tests": {}}
            
            if args.health_check:
                results["tests"]["health"] = await validator.validate_health_check()
            
            if args.integration_test:
                results["tests"]["integration"] = await validator.validate_integration()
            
            if args.performance_test:
                results["tests"]["performance"] = await validator.performance_test(
                    args.duration, args.concurrent_requests
                )
        else:
            # Run comprehensive validation
            results = await validator.comprehensive_validation(include_performance=args.performance_test)
        
        # Output results
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2)
            logger.info(f"📊 Results saved to {args.output}")
        
        # Print summary
        print(f"✅ Validation complete for {args.server}")
        if "overall_status" in results:
            print(f"📊 Overall Status: {results['overall_status']}")
        
        # Exit with appropriate code
        if "overall_status" in results and results["overall_status"] != "healthy":
            return 1
        
        return 0
        
    except Exception as e:
        logger.error(f"❌ Validation failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main())) 