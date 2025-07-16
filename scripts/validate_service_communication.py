#!/usr/bin/env python3
"""
Inter-Service Communication Validator
Tests communication between all MCP services and reports success rates
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.core.service_discovery import service_discovery
import logging

logger = logging.getLogger(__name__)

async def validate_all_communications():
    """Test communication between all services"""
    services = service_discovery.list_services()
    results = {
        "timestamp": datetime.now().isoformat(),
        "total_services": len(services),
        "healthy_services": 0,
        "success_rate": 0,
        "service_results": {}
    }
    
    for service in services:
        health_status = await service_discovery.check_service_health(service)
        results["service_results"][service] = {
            "healthy": health_status,
            "url": service_discovery.get_service_url(service)
        }
        
        if health_status:
            results["healthy_services"] += 1
    
    results["success_rate"] = (results["healthy_services"] / results["total_services"] * 100) if results["total_services"] > 0 else 0
    
    print("✅ Communication validation complete:")
    print(f"   Healthy services: {results['healthy_services']}/{results['total_services']}")
    print(f"   Success rate: {results['success_rate']:.1f}%")
    
    return results

if __name__ == "__main__":
    asyncio.run(validate_all_communications())
