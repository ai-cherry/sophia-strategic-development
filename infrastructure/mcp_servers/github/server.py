"""Github MCP Server implementation."""
import asyncio
from fastapi import FastAPI
import uvicorn

app = FastAPI(title="Github MCP Server")

@app.get("/health")
async def health():
    return {"status": "healthy", "server": "github"}

async def main():
    config = uvicorn.Config(app, host="0.0.0.0", port=9000)
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    asyncio.run(main())
