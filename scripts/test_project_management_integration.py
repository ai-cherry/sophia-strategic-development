#!/usr/bin/env python3
"""
Test Project Management Integration
Validates MCP servers, API routes, and frontend integration
"""

import asyncio
import httpx
import json
from datetime import datetime
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def test_mcp_servers():
    """Test MCP server connectivity"""
    servers = {
        "linear": "http://localhost:9004",
        "asana": "http://localhost:9007",
        "notion": "http://localhost:9008"
    }
    
    results = {}
    
    async with httpx.AsyncClient() as client:
        for name, url in servers.items():
            try:
                response = await client.get(f"{url}/health", timeout=5.0)
                results[name] = {
                    "status": "healthy" if response.status_code == 200 else "unhealthy",
                    "response_time": response.elapsed.total_seconds(),
                    "port": url.split(':')[-1],
                    "status_code": response.status_code
                }
            except Exception as e:
                results[name] = {
                    "status": "error",
                    "error": str(e),
                    "port": url.split(':')[-1]
                }
    
    return results

async def test_api_routes():
    """Test backend API routes"""
    backend_url = "http://localhost:8000"
    routes = [
        "/api/v4/mcp/linear/projects",
        "/api/v4/mcp/asana/projects", 
        "/api/v4/mcp/notion/projects",
        "/api/v4/mcp/unified/dashboard",
        "/api/v4/mcp/health"
    ]
    
    results = {}
    
    async with httpx.AsyncClient() as client:
        for route in routes:
            try:
                response = await client.get(f"{backend_url}{route}", timeout=10.0)
                results[route] = {
                    "status": response.status_code,
                    "response_time": response.elapsed.total_seconds(),
                    "data_size": len(response.text),
                    "success": response.status_code == 200
                }
                
                # Try to parse JSON response
                try:
                    data = response.json()
                    results[route]["data_keys"] = list(data.keys()) if isinstance(data, dict) else "non-dict"
                except:
                    results[route]["data_keys"] = "non-json"
                    
            except Exception as e:
                results[route] = {
                    "status": "error",
                    "error": str(e),
                    "success": False
                }
    
    return results

async def test_task_creation():
    """Test task creation endpoint"""
    backend_url = "http://localhost:8000"
    
    task_data = {
        "title": "Test Task from Integration Test",
        "description": "This is a test task created by the integration test script",
        "priority": "medium",
        "platform": "linear"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{backend_url}/api/v4/mcp/tasks/create",
                json=task_data,
                timeout=10.0
            )
            
            return {
                "status": response.status_code,
                "response_time": response.elapsed.total_seconds(),
                "success": response.status_code == 200,
                "data": response.json() if response.status_code == 200 else response.text
            }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "success": False
        }

async def test_system_health():
    """Test overall system health"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/system/status", timeout=5.0)
            data = response.json()
            
            return {
                "status": response.status_code,
                "system_status": data.get("status", "unknown"),
                "version": data.get("version", "unknown"),
                "uptime": data.get("uptime_seconds", 0),
                "mcp_servers": data.get("mcp_servers", {}),
                "success": response.status_code == 200
            }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "success": False
        }

async def test_frontend_connectivity():
    """Test frontend connectivity"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:5173", timeout=5.0)
            
            return {
                "status": response.status_code,
                "response_time": response.elapsed.total_seconds(),
                "success": response.status_code == 200,
                "content_size": len(response.text)
            }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "success": False
        }

def print_section(title, emoji="🧪"):
    """Print a formatted section header"""
    print(f"\n{emoji} {title}")
    print("=" * (len(title) + 4))

def print_result(name, result, indent="   "):
    """Print a formatted result"""
    if result.get("success", result.get("status") == "healthy"):
        status_icon = "✅"
        status_text = result.get("status", "success")
    else:
        status_icon = "❌"
        status_text = result.get("status", "error")
    
    print(f"{indent}{status_icon} {name}: {status_text}")
    
    if "response_time" in result:
        print(f"{indent}   Response time: {result['response_time']:.3f}s")
    
    if "port" in result:
        print(f"{indent}   Port: {result['port']}")
    
    if "error" in result:
        print(f"{indent}   Error: {result['error']}")
    
    if "data_keys" in result:
        print(f"{indent}   Data keys: {result['data_keys']}")

async def main():
    """Run comprehensive test suite"""
    print("🚀 Testing Project Management Integration")
    print("=" * 60)
    print(f"Test started at: {datetime.now().isoformat()}")
    
    # Test MCP servers
    print_section("MCP Server Connectivity", "🔗")
    mcp_results = await test_mcp_servers()
    
    for server, result in mcp_results.items():
        print_result(f"{server.upper()} MCP Server", result)
    
    # Test API routes
    print_section("Backend API Routes", "🌐")
    api_results = await test_api_routes()
    
    for route, result in api_results.items():
        print_result(route, result)
    
    # Test task creation
    print_section("Task Creation", "📝")
    task_result = await test_task_creation()
    print_result("Task Creation", task_result)
    
    if task_result.get("success") and "data" in task_result:
        print(f"   Created task: {task_result['data']}")
    
    # Test system health
    print_section("System Health", "💊")
    health_result = await test_system_health()
    print_result("System Health", health_result)
    
    if health_result.get("success"):
        print(f"   System Status: {health_result['system_status']}")
        print(f"   Version: {health_result['version']}")
        print(f"   Uptime: {health_result['uptime']:.1f}s")
        
        mcp_servers = health_result.get('mcp_servers', {})
        print(f"   MCP Servers: {len(mcp_servers)} detected")
        for server, info in mcp_servers.items():
            print(f"      - {server}: {info['status']} (port {info['port']})")
    
    # Test frontend connectivity
    print_section("Frontend Connectivity", "🎨")
    frontend_result = await test_frontend_connectivity()
    print_result("Frontend Server", frontend_result)
    
    # Generate comprehensive report
    report = {
        "timestamp": datetime.now().isoformat(),
        "test_results": {
            "mcp_servers": mcp_results,
            "api_routes": api_results,
            "task_creation": task_result,
            "system_health": health_result,
            "frontend": frontend_result
        },
        "summary": {
            "mcp_healthy": sum(1 for r in mcp_results.values() if r.get("status") == "healthy"),
            "mcp_total": len(mcp_results),
            "api_working": sum(1 for r in api_results.values() if r.get("success", False)),
            "api_total": len(api_results),
            "task_creation_working": task_result.get("success", False),
            "system_healthy": health_result.get("success", False),
            "frontend_accessible": frontend_result.get("success", False)
        }
    }
    
    # Calculate overall status
    critical_tests = [
        report["summary"]["mcp_healthy"] >= 2,  # At least 2 MCP servers healthy
        report["summary"]["api_working"] >= 3,  # At least 3 API routes working
        report["summary"]["system_healthy"],     # System health check passes
    ]
    
    overall_status = "PASS" if all(critical_tests) else "FAIL"
    report["summary"]["overall_status"] = overall_status
    
    # Save detailed report
    report_file = f"project_management_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, "w") as f:
        json.dump(report, f, indent=2)
    
    # Print summary
    print_section("Test Summary", "📊")
    print(f"   MCP Servers Healthy: {report['summary']['mcp_healthy']}/{report['summary']['mcp_total']}")
    print(f"   API Routes Working: {report['summary']['api_working']}/{report['summary']['api_total']}")
    print(f"   Task Creation: {'✅ Working' if report['summary']['task_creation_working'] else '❌ Failed'}")
    print(f"   System Health: {'✅ Healthy' if report['summary']['system_healthy'] else '❌ Unhealthy'}")
    print(f"   Frontend Access: {'✅ Accessible' if report['summary']['frontend_accessible'] else '❌ Not Accessible'}")
    print(f"   Overall Status: {'✅ PASS' if overall_status == 'PASS' else '❌ FAIL'}")
    
    print(f"\n📋 Detailed report saved to: {report_file}")
    
    # Return exit code
    return 0 if overall_status == "PASS" else 1

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test failed with error: {e}")
        sys.exit(1) 