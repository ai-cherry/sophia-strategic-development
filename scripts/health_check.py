#!/usr/bin/env python3
"""
Health check script for Sophia AI infrastructure
Validates all services are running and responsive
"""

import argparse
import requests
import asyncio
import aiohttp
import json
import sys
from typing import List, Dict, Tuple
from datetime import datetime

class HealthChecker:
    """Performs comprehensive health checks on Sophia AI infrastructure"""
    
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.results = []
        
    async def check_endpoint(self, session: aiohttp.ClientSession, url: str) -> Tuple[str, bool, str]:
        """Check a single endpoint"""
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=self.timeout)) as response:
                if response.status == 200:
                    return (url, True, "OK")
                else:
                    return (url, False, f"HTTP {response.status}")
        except asyncio.TimeoutError:
            return (url, False, "Timeout")
        except Exception as e:
            return (url, False, str(e))
    
    async def check_all_endpoints(self, endpoints: List[str]) -> Dict[str, Dict]:
        """Check all endpoints concurrently"""
        async with aiohttp.ClientSession() as session:
            tasks = [self.check_endpoint(session, url) for url in endpoints]
            results = await asyncio.gather(*tasks)
            
            return {
                url: {"healthy": healthy, "message": message}
                for url, healthy, message in results
            }
    
    def check_qdrant_health(self, endpoint: str) -> Dict:
        """Specific health check for Qdrant"""
        try:
            # Check Qdrant telemetry endpoint
            response = requests.get(f"{endpoint}/telemetry", timeout=self.timeout)
            if response.status_code == 200:
                data = response.json()
                return {
                    "healthy": True,
                    "version": data.get("version", "unknown"),
                    "collections": len(data.get("collections", [])),
                    "points_count": data.get("points_count", 0)
                }
            else:
                return {"healthy": False, "error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"healthy": False, "error": str(e)}
    
    def check_redis_health(self, host: str, port: int = 6379) -> Dict:
        """Check Redis connectivity"""
        try:
            import redis
            r = redis.Redis(host=host, port=port, socket_timeout=5)
            r.ping()
            info = r.info()
            return {
                "healthy": True,
                "version": info.get("redis_version", "unknown") if info else "unknown",
                "used_memory": info.get("used_memory_human", "unknown") if info else "unknown",
                "connected_clients": info.get("connected_clients", 0) if info else 0
            }
        except Exception as e:
            return {"healthy": False, "error": str(e)}
    
    def check_postgres_health(self, host: str, port: int = 5432) -> Dict:
        """Check PostgreSQL connectivity"""
        try:
            import psycopg2
            conn = psycopg2.connect(
                host=host,
                port=port,
                database="sophia_memory",
                user="sophia",
                password="sophia_secure_pass",
                connect_timeout=5
            )
            cursor = conn.cursor()
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            
            # Check pgvector extension
            cursor.execute("SELECT extversion FROM pg_extension WHERE extname = 'vector';")
            pgvector_version = cursor.fetchone()
            
            conn.close()
            return {
                "healthy": True,
                "version": version.split()[1] if version else "unknown",
                "pgvector": pgvector_version[0] if pgvector_version else "not installed"
            }
        except Exception as e:
            return {"healthy": False, "error": str(e)}
    
    def generate_report(self, results: Dict) -> str:
        """Generate a formatted health report"""
        report = []
        report.append("\n🏥 SOPHIA AI INFRASTRUCTURE HEALTH REPORT")
        report.append(f"📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("=" * 60)
        
        # Overall health
        all_healthy = all(r.get("healthy", False) for r in results.values() if isinstance(r, dict))
        report.append(f"\n🔍 Overall Status: {'✅ HEALTHY' if all_healthy else '❌ UNHEALTHY'}")
        
        # Individual services
        report.append("\n📊 Service Details:")
        for service, status in results.items():
            if isinstance(status, dict):
                health_icon = "✅" if status.get("healthy", False) else "❌"
                report.append(f"\n{health_icon} {service}:")
                for key, value in status.items():
                    if key != "healthy":
                        report.append(f"   • {key}: {value}")
        
        return "\n".join(report)

def main():
    parser = argparse.ArgumentParser(description="Health check for Sophia AI")
    parser.add_argument("--endpoints", nargs="+", help="HTTP endpoints to check")
    parser.add_argument("--qdrant", help="Qdrant endpoint")
    parser.add_argument("--redis", help="Redis host")
    parser.add_argument("--postgres", help="PostgreSQL host")
    parser.add_argument("--timeout", type=int, default=30, help="Timeout in seconds")
    parser.add_argument("--output", choices=["text", "json"], default="text")
    
    args = parser.parse_args()
    
    checker = HealthChecker(timeout=args.timeout)
    results = {}
    
    # Check HTTP endpoints
    if args.endpoints:
        print("🔍 Checking HTTP endpoints...")
        loop = asyncio.get_event_loop()
        endpoint_results = loop.run_until_complete(
            checker.check_all_endpoints(args.endpoints)
        )
        results.update(endpoint_results)
    
    # Check Qdrant
    if args.qdrant:
        print("🔍 Checking Qdrant...")
        results["Qdrant"] = checker.check_qdrant_health(args.qdrant)
    
    # Check Redis
    if args.redis:
        print("🔍 Checking Redis...")
        results["Redis"] = checker.check_redis_health(args.redis)
    
    # Check PostgreSQL
    if args.postgres:
        print("🔍 Checking PostgreSQL...")
        results["PostgreSQL"] = checker.check_postgres_health(args.postgres)
    
    # Output results
    if args.output == "json":
        print(json.dumps(results, indent=2))
    else:
        print(checker.generate_report(results))
    
    # Exit with appropriate code
    all_healthy = all(
        r.get("healthy", False) if isinstance(r, dict) else r
        for r in results.values()
    )
    sys.exit(0 if all_healthy else 1)

if __name__ == "__main__":
    main()
