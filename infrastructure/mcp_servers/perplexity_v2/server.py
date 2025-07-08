"""Perplexity_V2 MCP Server implementation."""
import asyncio

import uvicorn
from fastapi import FastAPI

app = FastAPI(title="Perplexity_V2 MCP Server")

@app.get("/health")
async def health():
    return {"status": "healthy", "server": "perplexity_v2"}

async def main():
    config = uvicorn.Config(app, host="127.0.0.1"  # Changed from 0.0.0.0 for security. Use environment variable for production, port=9000)
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    asyncio.run(main())
