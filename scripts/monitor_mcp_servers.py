#!/usr/bin/env python3
"""
Monitor and test MCP servers
"""

import asyncio
from typing import Dict, Any
import httpx
import subprocess
import time

# MCP Server Configuration
MCP_SERVERS = [
    {"name": "Backend API", "port": 8001, "url": "http://localhost:8001/health"},
    {"name": "AI Memory", "port": 9000, "url": "http://localhost:9001/health"},
    {"name": "Codacy", "port": 3008, "url": "http://localhost:3008/health"},
    {"name": "GitHub", "port": 9003, "url": "http://localhost:9003/health"},
    {"name": "Linear", "port": 9004, "url": "http://localhost:9004/health"},
    {"name": "Asana", "port": 9006, "url": "http://localhost:9006/health"},
    {"name": "Notion", "port": 9102, "url": "http://localhost:9102/health"},
    {"name": "Slack", "port": 9101, "url": "http://localhost:9101/health"},
    {"name": "Qdrant", "port": 9000, "url": "http://localhost:9001/health"},
    {"name": "Gong", "port": 9100, "url": "http://localhost:9100/health"},
    {"name": "HubSpot", "port": 9105, "url": "http://localhost:9105/health"},
]

async def check_server_health(server: Dict[str, Any]) -> Dict[str, Any]:
    """Check if a server is healthy"""
    try:
        # Check if port is open
        result = subprocess.run(
            ["lsof", "-t", f"-i:{server['port']}"], capture_output=True, text=True
        )
        process_running = bool(result.stdout.strip())

        # Try health endpoint
        health_status = "unknown"
        response_time = None

        try:
            async with httpx.AsyncClient() as client:
                start = time.time()
                response = await client.get(server["url"], timeout=5)
                response_time = round((time.time() - start) * 1000, 2)

                if response.status_code == 200:
                    health_status = "healthy"
                else:
                    health_status = f"unhealthy ({response.status_code})"
        except httpx.ConnectError:
            health_status = "no health endpoint"
        except Exception as e:
            health_status = f"error: {str(e)}"

        return {
            "name": server["name"],
            "port": server["port"],
            "process_running": process_running,
            "health_status": health_status,
            "response_time_ms": response_time,
        }

    except Exception as e:
        return {
            "name": server["name"],
            "port": server["port"],
            "process_running": False,
            "health_status": f"check failed: {str(e)}",
            "response_time_ms": None,
        }

async def test_backend_api():
    """Test the backend API functionality"""
    print("\n🧪 TESTING BACKEND API:")

    async with httpx.AsyncClient() as client:
        # Test system status
        try:
            response = await client.get("http://localhost:8001/api/v3/system/status")
            if response.status_code == 200:
                print("  ✅ System status endpoint working")
                data = response.json()
                print(f"     Environment: {data.get('environment', 'unknown')}")
                print(f"     Uptime: {data.get('uptime_hours', 0):.2f} hours")
        except:
            print("  ❌ System status endpoint failed")

        # Test orchestration
        try:
            payload = {
                "query": "What is the current date and time?",
                "user_id": "test_user",
            }
            response = await client.post(
                "http://localhost:8001/api/v4/orchestrate", json=payload, timeout=10
            )
            if response.status_code == 200:
                print("  ✅ Orchestration endpoint working")
                result = response.json()
                print(
                    f"     Model used: {result.get('metadata', {}).get('model', 'unknown')}"
                )
        except:
            print("  ❌ Orchestration endpoint failed")

async def verify_QDRANT_serviceection():
    """Verify Qdrant is receiving data"""
    print("\n❄️  qdrant VERIFICATION:")

    try:
        
        from backend.core.auto_esc_config import get_config_value

        # Get Qdrant credentials
        account = get_config_value("postgres_host")
        user = get_config_value("QDRANT_user")
        password = get_config_value("postgres_password")
        warehouse = get_config_value("postgres_database", "SOPHIA_AI_WH")
        database = get_config_value("postgres_database", "SOPHIA_AI")

        print(f"  Connecting to Qdrant as {user}@{account}...")

        conn = self.QDRANT_serviceection(
            account=account,
            user=user,
            password=password,
            warehouse=warehouse,
            database=database,
        )

        cursor = conn.cursor()

        # Check database existence
        cursor.execute("SELECT CURRENT_DATABASE(), CURRENT_WAREHOUSE()")
        db, wh = cursor.fetchone()
        print(f"  ✅ Connected to database: {db}, warehouse: {wh}")

        # Check for AI Memory table
        cursor.execute(
            """
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_SCHEMA = 'AI_MEMORY' 
            AND TABLE_NAME = 'SOPHIA_MEMORY_RECORDS'
        """
        )
        table_exists = cursor.fetchone()[0] > 0

        if table_exists:
            cursor.execute(
                """
                SELECT COUNT(*) as record_count
                FROM AI_MEMORY.SOPHIA_MEMORY_RECORDS
            """
            )
            count = cursor.fetchone()[0]
            print(f"  ✅ AI Memory table exists with {count} records")
        else:
            print("  ⚠️  AI Memory table not found")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"  ❌ Qdrant verification failed: {e}")

async def main():
    """Main monitoring function"""
    print("🔍 SOPHIA AI MCP SERVER MONITORING")
    print("=" * 60)

    # Check all servers
    print("\n📊 SERVER STATUS:")
    results = []
    for server in MCP_SERVERS:
        result = await check_server_health(server)
        results.append(result)

        status_icon = "✅" if result["process_running"] else "❌"
        health_icon = (
            "🟢"
            if result["health_status"] == "healthy"
            else "🟡"
            if "no health endpoint" in result["health_status"]
            else "🔴"
        )

        print(
            f"  {status_icon} {result['name']:15} Port {result['port']:5} {health_icon} {result['health_status']}"
        )
        if result["response_time_ms"]:
            print(f"     Response time: {result['response_time_ms']}ms")

    # Summary
    running_count = sum(1 for r in results if r["process_running"])
    healthy_count = sum(1 for r in results if r["health_status"] == "healthy")

    print("\n📈 SUMMARY:")
    print(f"  Processes running: {running_count}/{len(results)}")
    print(f"  Healthy endpoints: {healthy_count}/{len(results)}")

    # Test backend API
    await test_backend_api()

    # Verify Qdrant
    await verify_QDRANT_serviceection()

    print("\n" + "=" * 60)
    print("Monitoring complete!")

if __name__ == "__main__":
    asyncio.run(main())
