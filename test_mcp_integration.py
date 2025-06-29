#!/usr/bin/env python3
"""
MCP Services Integration Test Suite
Comprehensive testing for all MCP services
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.mcp_servers.mcp_health import health_monitor
from backend.mcp_servers.mcp_auth import mcp_auth

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def run_integration_tests():
    """Run comprehensive integration tests"""
    logger.info("🧪 Starting MCP Services Integration Tests")
    logger.info("=" * 60)
    
    # Test 1: Authentication Status
    logger.info("\n📋 Test 1: Authentication Status")
    auth_status = mcp_auth.get_service_status()
    
    for service, configured in auth_status.items():
        status_emoji = "✅" if configured else "⚠️"
        logger.info(f"   {status_emoji} {service}: {'Configured' if configured else 'Needs Configuration'}")
    
    # Test 2: Health Checks
    logger.info("\n📋 Test 2: Service Health Checks")
    system_health = await health_monitor.check_all_services()
    
    logger.info(f"   Overall Status: {system_health.overall_status}")
    logger.info(f"   Total Services: {system_health.total_services}")
    logger.info(f"   Healthy: {system_health.healthy_services}")
    logger.info(f"   Degraded: {system_health.degraded_services}")
    logger.info(f"   Unhealthy: {system_health.unhealthy_services}")
    
    for service_health in system_health.services:
        status_emoji = {"healthy": "✅", "degraded": "⚠️", "unhealthy": "❌"}[service_health.status]
        logger.info(f"   {status_emoji} {service_health.name}: {service_health.status} ({service_health.response_time_ms:.1f}ms)")
        if service_health.error_message:
            logger.info(f"      Error: {service_health.error_message}")
    
    # Test 3: Snowflake Connection Fix
    logger.info("\n📋 Test 3: Snowflake Connection Fix")
    try:
        from backend.core.snowflake_override import get_snowflake_connection_params
        params = get_snowflake_connection_params()
        
        if params['account'] == 'ZNB04675':
            logger.info("   ✅ Snowflake account: ZNB04675 (CORRECT)")
        else:
            logger.info(f"   ❌ Snowflake account: {params['account']} (WRONG)")
        
        logger.info(f"   User: {params['user']}")
        logger.info(f"   Database: {params['database']}")
        logger.info(f"   Warehouse: {params['warehouse']}")
        
    except Exception as e:
        logger.error(f"   ❌ Snowflake test failed: {e}")
    
    # Test 4: File Structure
    logger.info("\n📋 Test 4: File Structure Verification")
    
    expected_files = [
        "mcp-servers/snowflake/snowflake_mcp_server.py",
        "mcp-servers/hubspot/hubspot_mcp_server.py", 
        "mcp-servers/slack/slack_mcp_server.py",
        "mcp-servers/github/github_mcp_server.py",
        "mcp-servers/notion/notion_mcp_server.py",
        "backend/mcp_servers/mcp_auth.py",
        "backend/mcp_servers/mcp_health.py",
        "backend/core/snowflake_override.py",
        "start_mcp_services.py",
        "mcp_services_config.json"
    ]
    
    for file_path in expected_files:
        full_path = project_root / file_path
        if full_path.exists():
            logger.info(f"   ✅ {file_path}")
        else:
            logger.info(f"   ❌ {file_path} (MISSING)")
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("🎉 Integration Tests Complete!")
    
    # Calculate overall score
    configured_services = sum(auth_status.values())
    healthy_services = system_health.healthy_services
    total_services = len(auth_status)
    
    auth_score = (configured_services / total_services) * 100
    health_score = (healthy_services / total_services) * 100
    overall_score = (auth_score + health_score) / 2
    
    logger.info(f"\n📊 Test Results Summary:")
    logger.info(f"   Authentication Score: {auth_score:.1f}% ({configured_services}/{total_services} services)")
    logger.info(f"   Health Score: {health_score:.1f}% ({healthy_services}/{total_services} services)")
    logger.info(f"   Overall Score: {overall_score:.1f}%")
    
    if overall_score >= 80:
        logger.info("   🎉 EXCELLENT - Ready for production!")
    elif overall_score >= 60:
        logger.info("   ⚠️ GOOD - Some configuration needed")
    else:
        logger.info("   ❌ NEEDS WORK - Significant issues to resolve")
    
    return overall_score

if __name__ == "__main__":
    score = asyncio.run(run_integration_tests())
    sys.exit(0 if score >= 60 else 1)
