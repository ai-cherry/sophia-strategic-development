"""Linear_V2 MCP Server implementation."""

import asyncio

import uvicorn
from fastapi import FastAPI

app = FastAPI(title="Linear_V2 MCP Server")


@app.get("/health")
async def health():
    return {"status": "healthy", "server": "linear_v2"}


async def main():
    config = uvicorn.Config(
        app,
        host="127.0.0.1",  # Changed for security. Use ENV variable in production
        port=9000,
        log_level="info",
    )
    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":
    asyncio.run(main())
