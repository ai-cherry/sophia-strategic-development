#!/usr/bin/env python3
"""
Test MCP Server
Simple validation server for deployment testing
"""

import sys

import uvicorn
from fastapi import FastAPI

app = FastAPI(title="Test MCP Server")


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "test-mcp-server",
        "port": getattr(app.state, "port", 9999),
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Test MCP Server is running",
        "endpoints": ["/health", "/status"],
    }


@app.get("/status")
async def status():
    """Status endpoint"""
    return {
        "server": "test-mcp-server",
        "status": "operational",
        "capabilities": ["health_check", "basic_validation"],
    }


def main():
    """Main entry point"""
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 9999

    print(f"🧪 Starting Test MCP Server on port {port}...")

    # Store port in app state for health endpoint
    app.state.port = port

    uvicorn.run(app, host="127.0.0.1", port=port, log_level="info")


if __name__ == "__main__":
    main()
