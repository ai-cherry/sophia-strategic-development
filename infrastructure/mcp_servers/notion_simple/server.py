"""Simplified Notion MCP Server for Foundational Knowledge."""

import asyncio
import logging
import os
from typing import Any

import uvicorn
from fastapi import FastAPI, HTTPException
from notion_client import AsyncClient
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment configuration
NOTION_API_KEY = os.getenv(
    "NOTION_API_KEY", "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"
)
EMPLOYEES_DB_ID = get_config_value("employees_db_id", "")
CUSTOMERS_DB_ID = get_config_value("customers_db_id", "")
COMPETITORS_DB_ID = get_config_value("competitors_db_id", "")
PRODUCTS_DB_ID = get_config_value("products_db_id", "")

# Initialize Notion client
notion = AsyncClient(auth=NOTION_API_KEY)

# FastAPI app
app = FastAPI(
    title="Notion Foundational Knowledge MCP",
    description="Simple MCP server for querying foundational knowledge in Notion",
    version="1.0.0",
)


# Request/Response models
class SearchRequest(BaseModel):
    query: str
    entity_type: str | None = None
    limit: int = 10


class EmployeeLookup(BaseModel):
    email: str


class CustomerLookup(BaseModel):
    name: str


# Helper functions
def extract_text_from_property(prop: Any) -> str:
    """Extract text from various Notion property types."""
    if not prop:
        return ""

    prop_type = prop.get("type", "")

    if prop_type == "title" and prop.get("title"):
        return prop["title"][0].get("text", {}).get("content", "")
    elif prop_type == "rich_text" and prop.get("rich_text"):
        return prop["rich_text"][0].get("text", {}).get("content", "")
    elif prop_type == "email":
        return prop.get("email", "")
    elif prop_type == "select":
        return prop.get("select", {}).get("name", "")
    elif prop_type == "number":
        return str(prop.get("number", ""))
    elif prop_type == "url":
        return prop.get("url", "")
    elif prop_type == "date":
        date_obj = prop.get("date", {})
        return date_obj.get("start", "") if date_obj else ""

    return ""


def format_employee(page: dict) -> dict:
    """Format employee page data for response."""
    props = page.get("properties", {})
    return {
        "id": page["id"],
        "name": extract_text_from_property(props.get("Full Name")),
        "email": extract_text_from_property(props.get("Email")),
        "job_title": extract_text_from_property(props.get("Job Title")),
        "department": extract_text_from_property(props.get("Department")),
        "slack_id": extract_text_from_property(props.get("Slack ID")),
        "gong_id": extract_text_from_property(props.get("Gong ID")),
        "status": extract_text_from_property(props.get("Status")),
        "manager_email": extract_text_from_property(props.get("Manager Email")),
        "location": extract_text_from_property(props.get("Location")),
    }


def format_customer(page: dict) -> dict:
    """Format customer page data for response."""
    props = page.get("properties", {})
    return {
        "id": page["id"],
        "company_name": extract_text_from_property(props.get("Company Name")),
        "industry": extract_text_from_property(props.get("Industry")),
        "status": extract_text_from_property(props.get("Status")),
        "health_score": extract_text_from_property(props.get("Health Score")),
        "annual_revenue": extract_text_from_property(props.get("Annual Revenue")),
        "website": extract_text_from_property(props.get("Website")),
        "crm_id": extract_text_from_property(props.get("CRM ID")),
        "notes": extract_text_from_property(props.get("Notes")),
    }


def format_competitor(page: dict) -> dict:
    """Format competitor page data for response."""
    props = page.get("properties", {})
    return {
        "id": page["id"],
        "company_name": extract_text_from_property(props.get("Company Name")),
        "competitor_type": extract_text_from_property(props.get("Competitor Type")),
        "threat_level": extract_text_from_property(props.get("Threat Level")),
        "website": extract_text_from_property(props.get("Website")),
        "key_strengths": extract_text_from_property(props.get("Key Strengths")),
        "key_weaknesses": extract_text_from_property(props.get("Key Weaknesses")),
        "win_loss_notes": extract_text_from_property(props.get("Win/Loss Notes")),
    }


def format_product(page: dict) -> dict:
    """Format product page data for response."""
    props = page.get("properties", {})
    return {
        "id": page["id"],
        "product_name": extract_text_from_property(props.get("Product Name")),
        "product_code": extract_text_from_property(props.get("Product Code")),
        "category": extract_text_from_property(props.get("Category")),
        "status": extract_text_from_property(props.get("Status")),
        "description": extract_text_from_property(props.get("Description")),
        "key_features": extract_text_from_property(props.get("Key Features")),
        "pricing": extract_text_from_property(props.get("Pricing")),
    }


# API endpoints
@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "server": "notion_simple",
        "databases": {
            "employees": bool(EMPLOYEES_DB_ID),
            "customers": bool(CUSTOMERS_DB_ID),
            "competitors": bool(COMPETITORS_DB_ID),
            "products": bool(PRODUCTS_DB_ID),
        },
    }


@app.post("/search")
async def search(request: SearchRequest):
    """Search across foundational knowledge databases."""
    databases = {
        "employees": (EMPLOYEES_DB_ID, format_employee),
        "customers": (CUSTOMERS_DB_ID, format_customer),
        "competitors": (COMPETITORS_DB_ID, format_competitor),
        "products": (PRODUCTS_DB_ID, format_product),
    }

    results = []
    errors = []

    for db_type, (db_id, formatter) in databases.items():
        # Skip if specific type requested and doesn't match
        if request.entity_type and request.entity_type != db_type:
            continue

        # Skip if database ID not configured
        if not db_id:
            continue

        try:
            # Build filter based on database type
            if db_type == "employees":
                filter_obj = {
                    "or": [
                        {"property": "Full Name", "title": {"contains": request.query}},
                        {"property": "Email", "email": {"contains": request.query}},
                        {
                            "property": "Job Title",
                            "rich_text": {"contains": request.query},
                        },
                    ]
                }
            elif db_type == "customers":
                filter_obj = {
                    "or": [
                        {
                            "property": "Company Name",
                            "title": {"contains": request.query},
                        },
                        {"property": "Notes", "rich_text": {"contains": request.query}},
                    ]
                }
            elif db_type == "competitors":
                filter_obj = {
                    "property": "Company Name",
                    "title": {"contains": request.query},
                }
            else:  # products
                filter_obj = {
                    "or": [
                        {
                            "property": "Product Name",
                            "title": {"contains": request.query},
                        },
                        {
                            "property": "Description",
                            "rich_text": {"contains": request.query},
                        },
                    ]
                }

            # Query Notion
            response = await notion.databases.query(
                database_id=db_id, filter=filter_obj, page_size=request.limit
            )

            # Format results
            for page in response.get("results", []):
                formatted = formatter(page)
                formatted["entity_type"] = db_type
                results.append(formatted)

        except Exception as e:
            errors.append(f"Error searching {db_type}: {str(e)}")
            logger.error(f"Search error in {db_type}: {e}")

    return {
        "query": request.query,
        "results": results[: request.limit],
        "count": len(results),
        "errors": errors,
    }


@app.post("/employees/lookup")
async def lookup_employee(request: EmployeeLookup):
    """Look up employee by email."""
    if not EMPLOYEES_DB_ID:
        raise HTTPException(status_code=503, detail="Employees database not configured")

    try:
        response = await notion.databases.query(
            database_id=EMPLOYEES_DB_ID,
            filter={"property": "Email", "email": {"equals": request.email}},
        )

        if response["results"]:
            return format_employee(response["results"][0])
        else:
            return {"error": f"No employee found with email: {request.email}"}

    except Exception as e:
        logger.error(f"Employee lookup error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/customers/lookup")
async def lookup_customer(request: CustomerLookup):
    """Look up customer by name."""
    if not CUSTOMERS_DB_ID:
        raise HTTPException(status_code=503, detail="Customers database not configured")

    try:
        response = await notion.databases.query(
            database_id=CUSTOMERS_DB_ID,
            filter={"property": "Company Name", "title": {"contains": request.name}},
        )

        if response["results"]:
            return format_customer(response["results"][0])
        else:
            return {"error": f"No customer found with name: {request.name}"}

    except Exception as e:
        logger.error(f"Customer lookup error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/employees")
async def list_employees(limit: int = 20):
    """List all employees."""
    if not EMPLOYEES_DB_ID:
        raise HTTPException(status_code=503, detail="Employees database not configured")

    try:
        response = await notion.databases.query(
            database_id=EMPLOYEES_DB_ID, page_size=limit
        )

        employees = [format_employee(page) for page in response.get("results", [])]
        return {"employees": employees, "count": len(employees)}

    except Exception as e:
        logger.error(f"List employees error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/customers")
async def list_customers(limit: int = 20):
    """List all customers."""
    if not CUSTOMERS_DB_ID:
        raise HTTPException(status_code=503, detail="Customers database not configured")

    try:
        response = await notion.databases.query(
            database_id=CUSTOMERS_DB_ID, page_size=limit
        )

        customers = [format_customer(page) for page in response.get("results", [])]
        return {"customers": customers, "count": len(customers)}

    except Exception as e:
        logger.error(f"List customers error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/sync/status")
async def sync_status():
    """Get sync status for Sophia AI integration."""
    return {
        "status": "ready",
        "databases": {
            "employees": {"configured": bool(EMPLOYEES_DB_ID), "id": EMPLOYEES_DB_ID},
            "customers": {"configured": bool(CUSTOMERS_DB_ID), "id": CUSTOMERS_DB_ID},
            "competitors": {
                "configured": bool(COMPETITORS_DB_ID),
                "id": COMPETITORS_DB_ID,
            },
            "products": {"configured": bool(PRODUCTS_DB_ID), "id": PRODUCTS_DB_ID},
        },
        "notion_connected": True,
        "last_sync": None,  # Would track this in production
    }


# Main entry point
async def main():
    """Run the server."""
    config = uvicorn.Config(
        app,
        host="127.0.0.1",  # Changed from 0.0.0.0 for security. Use environment variable for production,
        port=int(get_config_value("notion_mcp_port", "9003")),
        log_level=get_config_value("log_level", "info").lower(),
    )
    server = uvicorn.Server(config)

    logger.info(f"🚀 Starting Notion Simple MCP Server on port {config.port}")
    logger.info("📊 Configured databases:")
    logger.info(f"   Employees: {'✅' if EMPLOYEES_DB_ID else '❌'}")
    logger.info(f"   Customers: {'✅' if CUSTOMERS_DB_ID else '❌'}")
    logger.info(f"   Competitors: {'✅' if COMPETITORS_DB_ID else '❌'}")
    logger.info(f"   Products: {'✅' if PRODUCTS_DB_ID else '❌'}")

    await server.serve()


if __name__ == "__main__":
    asyncio.run(main())
