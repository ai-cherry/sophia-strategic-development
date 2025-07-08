#!/usr/bin/env python3
"""
Snowflake V2 MCP Server - Enhanced Snowflake data management with modern features
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import Config
from .handlers.main_handler import SnowflakeHandler
from .utils.logging_config import setup_logging

# Setup logging
logger = setup_logging(__name__)


class SnowflakeV2Server:
    """Enhanced Snowflake MCP server with modern async patterns"""

    def __init__(self):
        self.config = Config()
        self.handler: SnowflakeHandler | None = None
        self.app = self._create_app()

    @asynccontextmanager
    async def lifespan(self, app: FastAPI):
        """Manage server lifecycle"""
        # Startup
        logger.info(f"Starting Snowflake V2 MCP Server on port {self.config.PORT}")
        self.handler = SnowflakeHandler(self.config)
        await self.handler.initialize()

        yield

        # Shutdown
        logger.info("Shutting down Snowflake V2 MCP Server")
        if self.handler:
            await self.handler.cleanup()

    def _create_app(self) -> FastAPI:
        """Create FastAPI application"""
        app = FastAPI(
            title="Snowflake V2 MCP Server",
            description="Enhanced Snowflake data management with AI integration",
            version="2.0.0",
            lifespan=self.lifespan,
        )

        # Add CORS middleware
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # Add routes
        self._add_routes(app)

        return app

    def _add_routes(self, app: FastAPI):
        """Add API routes"""

        @app.get("/health")
        async def health_check():
            """Health check endpoint"""
            return {
                "status": "healthy",
                "service": "snowflake_v2",
                "port": self.config.PORT,
                "version": "2.0.0",
            }

        @app.post("/api/v2/query")
        async def execute_query(request: dict):
            """Execute Snowflake query with AI enhancement"""
            if not self.handler:
                raise HTTPException(status_code=503, detail="Service not initialized")

            try:
                result = await self.handler.execute_query(request)
                return JSONResponse(content=result)
            except Exception as e:
                logger.error(f"Query execution failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @app.post("/api/v2/schema/create")
        async def create_schema(request: dict):
            """Create new schema"""
            if not self.handler:
                raise HTTPException(status_code=503, detail="Service not initialized")

            try:
                result = await self.handler.create_schema(request)
                return JSONResponse(content=result)
            except Exception as e:
                logger.error(f"Schema creation failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @app.post("/api/v2/table/create")
        async def create_table(request: dict):
            """Create new table with AI-ready columns"""
            if not self.handler:
                raise HTTPException(status_code=503, detail="Service not initialized")

            try:
                result = await self.handler.create_table(request)
                return JSONResponse(content=result)
            except Exception as e:
                logger.error(f"Table creation failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @app.post("/api/v2/data/load")
        async def load_data(request: dict):
            """Load data with automatic enrichment"""
            if not self.handler:
                raise HTTPException(status_code=503, detail="Service not initialized")

            try:
                result = await self.handler.load_data(request)
                return JSONResponse(content=result)
            except Exception as e:
                logger.error(f"Data loading failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @app.post("/api/v2/ai/embed")
        async def generate_embeddings(request: dict):
            """Generate embeddings using Snowflake Cortex"""
            if not self.handler:
                raise HTTPException(status_code=503, detail="Service not initialized")

            try:
                result = await self.handler.generate_embeddings(request)
                return JSONResponse(content=result)
            except Exception as e:
                logger.error(f"Embedding generation failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @app.post("/api/v2/ai/search")
        async def semantic_search(request: dict):
            """Perform semantic search"""
            if not self.handler:
                raise HTTPException(status_code=503, detail="Service not initialized")

            try:
                result = await self.handler.semantic_search(request)
                return JSONResponse(content=result)
            except Exception as e:
                logger.error(f"Semantic search failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @app.get("/api/v2/status")
        async def get_status():
            """Get comprehensive Snowflake status"""
            if not self.handler:
                raise HTTPException(status_code=503, detail="Service not initialized")

            try:
                result = await self.handler.get_system_status()
                return JSONResponse(content=result)
            except Exception as e:
                logger.error(f"Status check failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @app.post("/api/v2/optimize")
        async def optimize_performance(request: dict):
            """Optimize Snowflake performance"""
            if not self.handler:
                raise HTTPException(status_code=503, detail="Service not initialized")

            try:
                result = await self.handler.optimize_performance(request)
                return JSONResponse(content=result)
            except Exception as e:
                logger.error(f"Optimization failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @app.post("/api/v2/sync/schemas")
        async def sync_schemas(request: dict):
            """Synchronize schemas with codebase"""
            if not self.handler:
                raise HTTPException(status_code=503, detail="Service not initialized")

            try:
                result = await self.handler.sync_schemas(request)
                return JSONResponse(content=result)
            except Exception as e:
                logger.error(f"Schema sync failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @app.post("/api/v2/warehouse/manage")
        async def manage_warehouse(request: dict):
            """Manage Snowflake warehouses"""
            if not self.handler:
                raise HTTPException(status_code=503, detail="Service not initialized")

            try:
                result = await self.handler.manage_warehouse(request)
                return JSONResponse(content=result)
            except Exception as e:
                logger.error(f"Warehouse management failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))

    def run(self):
        """Run the server"""
        import uvicorn

        uvicorn.run(self.app, host="127.0.0.1"  # Changed from 0.0.0.0 for security. Use environment variable for production, port=self.config.PORT, log_level="info")


def main():
    """Main entry point"""
    server = SnowflakeV2Server()
    server.run()


if __name__ == "__main__":
    main()
