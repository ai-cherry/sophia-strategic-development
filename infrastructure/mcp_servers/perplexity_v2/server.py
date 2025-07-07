"""Perplexity_V2 MCP Server implementation."""
import asyncio
from fastapi import FastAPI
import uvicorn

app = FastAPI(title="Perplexity_V2 MCP Server")

@app.get("/health")
async def health():
    return {"status": "healthy", "server": "perplexity_v2"}

async def main():
    config = uvicorn.Config(app, host="0.0.0.0", port=9000)
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    asyncio.run(main())
