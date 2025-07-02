import asyncio
import httpx
import json
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define the services that our N8N workflows depend on.
# These are the underlying REST APIs, not the MCP gateway itself.
INTERNAL_SERVICES = {
    "Codacy REST API": "http://localhost:3008/health",
    "AI Memory REST API": "http://localhost:9001/health",
}

async def check_service(name: str, url: str, client: httpx.AsyncClient) -> dict:
    """
    Checks the health of a single service.
    """
    try:
        response = await client.get(url, timeout=10.0)
        
        if response.status_code == 200:
            return {
                "name": name,
                "status": "HEALTHY",
                "statusCode": response.status_code,
                "details": "Service is running and responsive."
            }
        else:
            return {
                "name": name,
                "status": "UNHEALTHY",
                "statusCode": response.status_code,
                "details": f"Service returned an unhealthy status: {response.text}"
            }
    except httpx.RequestError as e:
        return {
            "name": name,
            "status": "OFFLINE",
            "statusCode": None,
            "details": f"Failed to connect to the service: {str(e)}"
        }
    except Exception as e:
        return {
            "name": name,
            "status": "ERROR",
            "statusCode": None,
            "details": f"An unexpected error occurred: {str(e)}"
        }

async def main():
    """
    Main function to run health checks on all internal services.
    """
    logging.info("Starting internal service health check...")
    
    health_report = {
        "reportGeneratedAt": datetime.utcnow().isoformat() + "Z",
        "services": [],
        "summary": {
            "healthy": 0,
            "unhealthy": 0,
            "offline": 0,
            "error": 0,
            "overallStatus": "HEALTHY"
        }
    }
    
    async with httpx.AsyncClient() as client:
        tasks = [check_service(name, url, client) for name, url in INTERNAL_SERVICES.items()]
        results = await asyncio.gather(*tasks)

    unhealthy_services = []
    for result in results:
        health_report["services"].append(result)
        status = result["status"]
        if status == "HEALTHY":
            health_report["summary"]["healthy"] += 1
        elif status == "UNHEALTHY":
            health_report["summary"]["unhealthy"] += 1
            unhealthy_services.append(result)
        elif status == "OFFLINE":
            health_report["summary"]["offline"] += 1
            unhealthy_services.append(result)
        else: # ERROR
            health_report["summary"]["error"] += 1
            unhealthy_services.append(result)

    if unhealthy_services:
        health_report["summary"]["overallStatus"] = "UNHEALTHY"
        health_report["unhealthyServices"] = unhealthy_services

    # Print results as a JSON object to be captured by N8N
    print(json.dumps(health_report, indent=2))
    logging.info("Internal service health check complete.")

if __name__ == "__main__":
    asyncio.run(main())
