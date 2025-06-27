"""
CoStar API Routes for Sophia AI

FastAPI routes for CoStar real estate market data management.
Provides endpoints for data upload, market browsing, and analytics.
"""

from __future__ import annotations

import logging
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, File, HTTPException, UploadFile, status, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import os
import httpx

from backend.mcp_servers.costar_mcp_server import costar_server

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/costar", tags=["costar"])


class CoStarUploadResponse(BaseModel):
    """Response model for file upload operations."""

    status: str
    message: str
    import_id: Optional[int] = None
    records_processed: int = 0
    records_imported: int = 0
    records_failed: int = 0
    processing_time_seconds: float = 0.0
    errors: List[str] = []


class CoStarMarketResponse(BaseModel):
    """Response model for market data operations."""

    status: str
    markets: List[Dict[str, Any]] = []
    data: List[Dict[str, Any]] = []
    total_count: int = 0


class CoStarImportHistoryResponse(BaseModel):
    """Response model for import history."""

    status: str
    imports: List[Dict[str, Any]] = []
    total_count: int = 0


class CoStarInitializeResponse(BaseModel):
    """Response model for database initialization."""

    status: str
    message: str
    tables_created: List[str] = []


@router.post("/initialize", response_model=CoStarInitializeResponse)
async def initialize_costar_database():
    """
    Initialize CoStar database tables and setup.

    This endpoint ensures all required database tables exist and are properly configured.
    """
    try:
        # Initialize the MCP server (which handles database setup)
        await costar_server.initialize()

        return CoStarInitializeResponse(
            status="success",
            message="CoStar database initialized successfully",
            tables_created=[
                "costar_markets",
                "costar_market_data",
                "costar_import_log",
                "costar_market_insights",
                "costar_market_comparisons",
            ],
        )

    except Exception as e:
        logger.error(f"Failed to initialize CoStar database: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database initialization failed: {str(e)}",
        )


@router.get("/markets", response_model=CoStarMarketResponse)
async def get_markets():
    """
    Get all available metro areas/markets with record counts.

    Returns a list of all markets in the database along with the number
    of data records available for each market.
    """
    try:
        await costar_server.initialize()
        markets = await costar_server.get_markets()

        return CoStarMarketResponse(
            status="success", markets=markets, total_count=len(markets)
        )

    except Exception as e:
        logger.error(f"Failed to fetch markets: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch markets: {str(e)}",
        )


@router.get("/market/{metro_area}", response_model=CoStarMarketResponse)
async def get_market_data(metro_area: str, limit: int = 100):
    """
    Get market data for a specific metro area.

    Args:
        metro_area: Name of the metropolitan area (e.g., "San Francisco, CA")
        limit: Maximum number of records to return (default: 100)

    Returns market data including vacancy rates, rent prices, inventory, etc.
    """
    try:
        await costar_server.initialize()

        # Decode URL-encoded metro area name
        metro_area = metro_area.replace("%20", " ").replace("%2C", ",")

        market_data = await costar_server.get_market_data(metro_area, limit)

        if not market_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No data found for market: {metro_area}",
            )

        return CoStarMarketResponse(
            status="success", data=market_data, total_count=len(market_data)
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch market data for {metro_area}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch market data: {str(e)}",
        )


@router.post("/upload", response_model=CoStarUploadResponse)
async def upload_costar_data(file: UploadFile = File(...)):
    """
    Upload and process CoStar data file.

    Accepts CSV, Excel (.xlsx, .xls) files containing CoStar market data.
    The file will be processed and imported into the database.

    Args:
        file: CoStar data file (CSV or Excel format)

    Returns processing results including number of records imported.
    """
    try:
        # Validate file type
        allowed_extensions = {".csv", ".xlsx", ".xls"}
        file_extension = Path(file.filename).suffix.lower()

        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file type: {file_extension}. Allowed types: {', '.join(allowed_extensions)}",
            )

        # Validate file size (50MB limit)
        max_size = 50 * 1024 * 1024  # 50MB
        file_content = await file.read()

        if len(file_content) > max_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File too large: {len(file_content)} bytes. Maximum size: {max_size} bytes",
            )

        # Save file to temporary location for processing
        with tempfile.NamedTemporaryFile(
            suffix=file_extension, delete=False
        ) as temp_file:
            temp_file.write(file_content)
            temp_file_path = Path(temp_file.name)

        try:
            # Initialize server and process file
            await costar_server.initialize()
            result = await costar_server.process_file(temp_file_path)

            return CoStarUploadResponse(
                status=result.import_status,
                message=f"File processed successfully. Imported {result.records_imported} records.",
                import_id=result.import_id,
                records_processed=result.records_processed,
                records_imported=result.records_imported,
                records_failed=result.records_failed,
                processing_time_seconds=result.processing_time_seconds,
                errors=[result.error_message] if result.error_message else [],
            )

        finally:
            # Clean up temporary file
            if temp_file_path.exists():
                temp_file_path.unlink()

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to upload CoStar data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"File upload failed: {str(e)}",
        )


@router.get("/import-status", response_model=CoStarImportHistoryResponse)
async def get_import_history(limit: int = 50):
    """
    Get import history and status of all CoStar data uploads.

    Args:
        limit: Maximum number of import records to return (default: 50)

    Returns a list of all import operations with their status and results.
    """
    try:
        await costar_server.initialize()
        imports = await costar_server.get_import_history(limit)

        return CoStarImportHistoryResponse(
            status="success", imports=imports, total_count=len(imports)
        )

    except Exception as e:
        logger.error(f"Failed to fetch import history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch import history: {str(e)}",
        )


@router.get("/health")
async def health_check():
    """
    Health check endpoint for CoStar service.

    Returns the health status of the CoStar MCP server and database connection.
    """
    try:
        await costar_server.initialize()

        # Test database connection
        markets = await costar_server.get_markets()

        return {
            "status": "healthy",
            "service": "CoStar MCP Server",
            "database_connected": True,
            "markets_available": len(markets),
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"CoStar health check failed: {e}")
        return {
            "status": "unhealthy",
            "service": "CoStar MCP Server",
            "database_connected": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
        }


@router.get("/formats")
async def get_supported_formats():
    """
    Get information about supported CoStar data formats and column mappings.

    Returns details about expected file formats, column names, and data types.
    """
    return {
        "status": "success",
        "supported_formats": [
            {
                "format": "CSV",
                "extension": ".csv",
                "description": "Comma-separated values file",
            },
            {
                "format": "Excel",
                "extensions": [".xlsx", ".xls"],
                "description": "Microsoft Excel spreadsheet",
            },
        ],
        "expected_columns": {
            "required": ["metro_area", "market_date"],
            "optional": [
                "property_type",
                "submarket",
                "total_inventory",
                "vacancy_rate",
                "asking_rent_psf",
                "effective_rent_psf",
                "net_absorption",
                "construction_deliveries",
                "under_construction",
                "construction_starts",
                "cap_rate",
                "price_per_sf",
                "quarter",
            ],
        },
        "column_aliases": {
            "metro_area": ["market", "metro", "msa", "metropolitan_area"],
            "property_type": ["prop_type", "type", "asset_type"],
            "vacancy_rate": ["vacancy", "vac_rate", "vacant_pct"],
            "asking_rent_psf": ["asking_rent", "rent_psf", "rent"],
            "total_inventory": ["inventory", "total_sf", "total_space"],
            "market_date": ["date", "period", "quarter_date"],
        },
        "data_types": {
            "metro_area": "string",
            "property_type": "string",
            "vacancy_rate": "percentage (0-100)",
            "asking_rent_psf": "currency (dollars)",
            "total_inventory": "integer (square feet)",
            "market_date": "date (YYYY-MM-DD or MM/DD/YYYY)",
        },
        "limits": {"max_file_size_mb": 50, "max_records_per_file": 100000},
    }


@router.get("/analytics/summary/{metro_area}")
async def get_market_analytics_summary(metro_area: str):
    """
    Get analytics summary for a specific market.

    Provides key metrics, trends, and insights for the specified metro area.
    """
    try:
        await costar_server.initialize()

        # Decode metro area name
        metro_area = metro_area.replace("%20", " ").replace("%2C", ",")

        # Get recent market data
        market_data = await costar_server.get_market_data(metro_area, limit=50)

        if not market_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No data found for market: {metro_area}",
            )

        # Calculate summary statistics
        property_types = list(
            set(
                record.get("property_type")
                for record in market_data
                if record.get("property_type")
            )
        )
        latest_data = market_data[0] if market_data else {}

        # Calculate averages (simplified for demo)
        avg_vacancy = (
            sum(record.get("vacancy_rate", 0) or 0 for record in market_data)
            / len(market_data)
            if market_data
            else 0
        )
        avg_rent = (
            sum(record.get("asking_rent_psf", 0) or 0 for record in market_data)
            / len(market_data)
            if market_data
            else 0
        )

        return {
            "status": "success",
            "market": metro_area,
            "summary": {
                "total_records": len(market_data),
                "property_types": property_types,
                "latest_date": latest_data.get("market_date"),
                "average_vacancy_rate": round(avg_vacancy, 2),
                "average_asking_rent_psf": round(avg_rent, 2),
                "data_quality": "good" if len(market_data) > 10 else "limited",
            },
            "latest_metrics": {
                "vacancy_rate": latest_data.get("vacancy_rate"),
                "asking_rent_psf": latest_data.get("asking_rent_psf"),
                "total_inventory": latest_data.get("total_inventory"),
                "under_construction": latest_data.get("under_construction"),
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate market analytics for {metro_area}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate analytics: {str(e)}",
        )


@router.post("/api/v1/chat")
async def chat_endpoint(request: Request):
    data = await request.json()
    message = data.get("message", "")
    context = data.get("context", [])
    user_id = data.get("user_id", "anonymous")
    # Optionally, retrieve persistent context from AI Memory MCP
    llm_endpoint = os.getenv(
        "LLM_GATEWAY_ENDPOINT", "https://llm-gateway.sophia-intel.ai/v1/completions"
    )
    api_key = os.getenv("LLM_GATEWAY_API_KEY")
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {"prompt": message, "context": context, "user_id": user_id}
    async with httpx.AsyncClient(timeout=30) as client:
        try:
            response = await client.post(llm_endpoint, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            # Optionally, trigger agent actions based on LLM output
            return JSONResponse(
                {
                    "message": data.get("completion", ""),
                    "action_summary": data.get("action_summary"),
                    "confidence": data.get("confidence"),
                    "risk": data.get("risk"),
                }
            )
        except Exception as e:
            return JSONResponse({"message": f"[LLM error: {e}]"}, status_code=500)
