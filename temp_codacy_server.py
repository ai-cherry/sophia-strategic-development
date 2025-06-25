import asyncio
from datetime import datetime
from aiohttp import web
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Codacy")


async def health_handler(request):
    return web.json_response(
        {
            "status": "healthy",
            "server": "Codacy",
            "port": 3008,
            "timestamp": datetime.now().isoformat(),
        }
    )


async def tools_handler(request):
    return web.json_response(
        {
            "tools": [
                {"name": "health_check", "description": "Check server health"},
                {"name": "status", "description": "Get server status"},
            ]
        }
    )


async def init_app():
    app = web.Application()
    app.router.add_get("/health", health_handler)
    app.router.add_get("/tools", tools_handler)
    return app


if __name__ == "__main__":
    app = asyncio.run(init_app())
    web.run_app(app, host="0.0.0.0", port=3008)
